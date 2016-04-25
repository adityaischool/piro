## PACKAGE FOR AUTHORIZING & HITTING THE INSTAGRAM API

import os, md5, base64, requests, pymongo
import hmac
from hashlib import sha256
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint
from apiCredentials import getAPICredentials
from dataPointBuilder import createDataPoint

# Instantiate Mongo client
client = pymongo.MongoClient()
# Instantiate Mongo data point db
dataPointDb = client.dataPointDb
dataPoints = dataPointDb.dataPoints
# Instantiate Instagram Dropbox db
instagramDb = client.instagram
recentMediaIdsDb = instagramDb.instagramRecentMediaIds

# Instantiate Instagram API credentials
API_KEY = getAPICredentials('instagram')[0]
SECRET = getAPICredentials('instagram')[1]
AUTH_CALLBACK = 'http://localhost:5000/instagram-token'
BASE_URL = ''

def getAPIKey():
	return API_KEY

def getSecret():
	return SECRET

def getAuthCallback():
	return AUTH_CALLBACK

def codeFlow(code):
	userId = session['userId']
	print
	print "------- INSTAGRAM OAUTH CODE -------", code
	print
	baseURL = 'https://api.instagram.com/oauth/access_token'
	# Set params for Instagram user authorzation request
	params = {'code': code,
	'grant_type': 'authorization_code',
	'client_id': API_KEY,
	'client_secret': SECRET,
	'redirect_uri': AUTH_CALLBACK}
	# Hit Instagram API for access token
	try:
		response = requests.post(baseURL, data = params)
		decodedResponse = response.json()
		print
		print "------- INSTAGRAM ACCESS TOKEN RESPONSE -------"
		pprint(decodedResponse)
		print
	except Exception as e:
		print
		print "------- ERROR GETTING INSTAGRAM ACCESS TOKEN RESPONSE -------", e
		print
	# Update the UserDevice table in the db
	updateUserDeviceTable(decodedResponse, userId)
	# If the user is not yet onboarded (i.e., it's their first time throug this process), download their history
	if not session['onboarded']:
		getAllNewPosts()

# Update the UserDevice table in the db
def updateUserDeviceTable(decodedResponse, userId):
	# Parse Instagram access token response
	accessToken = decodedResponse['access_token']
	instagramUserId = decodedResponse['user']['id']
	instagramUsername = decodedResponse['user']['username']
	# Check if user already has a record in UserDevice - update if so, create one if not
	userIdQueryResult = UserDevice.query.filter_by(userid=userId, devicetype='instagram').first()
	if userIdQueryResult is not None:
		# Update the user's existing record in the UserDevice table
		print
		print '------ THERE IS ALREADY A RECORD FOR THIS USER!!!! -------'
		print
		userIdQueryResult.deviceuserid = instagramUsername
		userIdQueryResult.deviceuserid = instagramUserId
		userIdQueryResult.accesstoken = accessToken
	else:
		# Create a new db record to be inserted into the UserDevice table
		userDevice = UserDevice(userId, 'instagram', instagramUsername, instagramUserId, accessToken, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
	# Commit the results to the UserDevice table in the db
	try:
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING INSTAGRAM USERNAME, USERID, & TOKEN TO DB -------", e
		print

# Check whether or not the user has authorized access to Instagram or not
def checkIfInstagramAuthorized():
	userId = session['userId']
	# Query UserDevice table current user's Instagram credentials
	try:
		userIdQueryResults = UserDevice.query.filter_by(userid=userId, devicetype='instagram').first()
	except Exception as e:
		print
		print "------- ERROR QUERYING DB FOR INSTAGRAM USERDEVICE RECORD -------", e
		print
	# Check if user has authorized Instagram yet
	if (type(userIdQueryResults) != type(None)):
		return [True, userIdQueryResults]
	else:
		print
		print "------- USERDEVICE INSTAGRAM RECORD FOR USER", userId, "DOES NOT YET EXIST -------"
		print
		return [False, None]

# Parse the UserDevice table query response and return the user's access token
def getAccessToken():
	instagramCheckResponse = checkIfInstagramAuthorized()
	if instagramCheckResponse[0]:
		try:
			userDeviceDict = instagramCheckResponse[1].__dict__
			accessToken = userDeviceDict['accesstoken']
			return accessToken
		except Exception as e:
			print
			print "------- ERROR GETTING USER'S INSTAGRAM ACCESS TOKEN -------", e
			print
			return None
	else:
		print
		print '------- NO INSTAGRAM ACCESS TOKEN IN DB -------'
		return None

# Generate and return an sha256 signature used for API calls
def generateSignature(endpoint, params):
	secret = SECRET
	params = params
	sig = endpoint
	sortedKeys = sorted(params.keys())
	# Add each key-value to raw signature
	for key in sortedKeys:
		sig += '|%s=%s' % (key, params[key])
	# Create & return sha256 hash of signature
	return hmac.new(key=bytearray(secret, 'utf-8'), msg=bytearray(sig, 'utf-8'), digestmod=sha256).hexdigest()

# Display Mongo contents
def getMongoFolderContents():
	userId = session['userId']
	print
	print "------- A LIST OF ALL USERS & THEIR MOST RECENT INSTAGRAM MEDIA IDS -------"
	for user in recentMediaIdsDb.find({}):
		print
		print "------- User ---------------", user['userId']
		print "------- mostRecentItemId -------", user['mostRecentItemId']

# Reset user's most recent item id record in Mongo - useful for testing or if user wants to redownload everything
def resetMostRecentItemId():
	userId = session['userId']
	recentMediaIdsDb.update({'userId': userId}, {'$set': {'mostRecentItemId': 0}})	

# Get all of a user's posts that have not already been retrieved in the past
def getAllNewPosts():
	print "getAllNewPosts"
	userId = session['userId']
	# ######## REMOVE THIS LINE ONCE TESTING IS DONE!!!! #########
	# dataPoints.remove({'$and': [{'userId': userId}, {'source': 'instagram'}]})
	mostRecentItemId = 0
	maxId = 0
	highestMaxId = 0
	postDataObj = ''
	postData = None
	allPostData = {'data': []}
	imageUrls = []
	# Variable for while loop
	keepProcessing = True
	# Check if user has an Instagram record in Mongo
	userIdQueryResults = recentMediaIdsDb.find({'userId': userId})
	# If user doesn't have a record, create one for them with a mostRecentItemId value of 0
	if userIdQueryResults.count() == 0:
		recentMediaIdsDb.insert({
			'userId': userId,
			'mostRecentItemId': 0
			})
	# If user does have a record, get the mostRecentItemId value - this should represent the newest post we have stored on the pi box for the user
	else:
		for user in userIdQueryResults:
			mostRecentItemId = user['mostRecentItemId']
			print
			print '------- MOST RECENT ITEM ID FOR USER', userId, '-------', mostRecentItemId
			print
	# Get all of a user's recent media since the last poll
	while keepProcessing:
		# Start with the most recent data then work backward through
		# more posts by using the returned maxId when calling the Instagram API
		print
		print '------- CURRENT MAX ID:', maxId, '-------'
		print
		print '------- MOST RECENT ITEM ID -------', mostRecentItemId
		print
		postDataObj = getUserRecentMedia(maxId)
		# If postDataObj has no results, break while loop
		if len(postDataObj['posts']) == 0:
			print
			print '------- NO MORE/NEW INSTAGRAM POSTS! -------'
			print
			break
		# Update highestMaxId with the maxId key-value from the returned postData object, only after first API call
		if maxId == 0:
			highestMaxId = postDataObj['highestMaxId']
		# Update maxId with the latest maxId
		maxId = postDataObj['minId']
		# Iterate through each post returned by getUserRecentMedia & append to allPostData object
		# Also append each post image url to the imageUrls list for downloading later
		for post in postDataObj['posts']:
			# Check if mostRecentItemId is equal to the post's itemId - if it is equal, stop getting Instagram posts by breaking for & while loops
			if post['sourceData']['itemId'] == mostRecentItemId:
				keepProcessing = False
				print
				print '------- NO MORE/NEW INSTAGRAM POSTS! -------'
				print
				break	
			allPostData['data'].append(post)
			imageUrls.append(post['sourceData']['url'])
	# Set the mostRecentItemId in Mongo to highestMaxId - this is so we know where to start next time
	recentMediaIdsDb.update({'userId': userId}, {'$set': {'mostRecentItemId': highestMaxId}})
	# Check Mongo user object update
	getMongoFolderContents()
	# Download each from the Instagram URL
	for item in allPostData['data']:
		url = item['sourceData']['url']
		date = item['adjustedDate']
		downloadFile(url, date)

	# Temporarily store dataPoints in Mongo
	oldCount = dataPoints.count()
	try:
		print '------- SKIPPING WRITING TO MONGO FOR NOW - MAKE SURE EVERYTHING LOOKS GOOD FIRST -------'
		dataPoints.insert(allPostData['data'])
	except Exception as e:
		print
		print '------- ERROR WRITING DATA POINTS TO MONGO -------', e
	# Verify that everything went to Mongo successfully
	print "------- A LIST OF THE USER'S FOLDERS, SYNC SETTINGS, & CURSORS -------"
	newCount = dataPoints.count()
	print
	print "------- NUMBER OF DATA POINTS ATTEMPTED TO ADD TO DATAPOINTS DB:", len(allPostData['data'])
	print "------- SUCCESSFULLY ADDED", newCount - oldCount, 'NEW DATA POINTS TO DATAPOINTS DB -------'
	
	# TODO: SEND PHOTO META DATA TO STORJ - WILL MATCH TO PHOTO BY FILENAME
	return allPostData

# Downloads the file at the given URL to the staging folder
def downloadFile(url, date):
	userId = session['userId']
	path1=os.path.dirname(__file__)
	dirpath=os.path.join(path1,'static','staging',str(userId),date)
	downloadDirectory = dirpath
	# downloadDirectory = 'static/staging/'+userId+'/'+date+'/'
	# Check if download directory exists; create if it does not exist
	if not os.path.exists(downloadDirectory):
		os.makedirs(downloadDirectory)
	fileName = url.split(os.sep)[-1].split('?')[0]
	# Concatenate downloadDirectory + fileName
	pathPlusFileName = downloadDirectory + os.sep+fileName
	# Download file at from specified Instagram URL to specified local path
	try:
		print
		print '------- DOWNLOADING FILE FROM URL', url, '-------'
		print
		fileData = requests.get(url).content
	except Exception as e:
		print
		print '------- ERROR DOWNLOADING FILE FROM INSTAGRAM -------', e
	# Write the downlaoded file data to local disk at specified path
	f = open(pathPlusFileName, 'wb')
	f.write(fileData)
	f.close()
	
	# TODO: ADD CODE TO UPLOAD PHOTO FILES TO STORJ - MATCH BY FILENAME
	# TODO: ONCE FILES UPLOADED TO STORJ, DELETE FROM WEB SERVER

# Gets a user's recent Instagram posts earlier than the maxId, if given
def getUserRecentMedia(maxId):
	userId = session['userId']
	# Fetch user's access token from the UserDevice table
	accessToken = getAccessToken()
	baseURL = 'https://api.instagram.com/v1'
	endpoint = '/users/self/media/recent'
	# Instantiate params
	params = {
	'access_token': accessToken,
	'count': '20'
	}
	# Add maxId parameter to parameters if given
	if maxId > 0:
		params['max_id'] = str(maxId)
	# Generate hashed signature per Instagram's security requirements
	sig = generateSignature(endpoint, params)
	# Add hashed signature to parameters
	params['sig'] = sig
	print '----- PARAMS ------', params
	# Hit Instagram API
	try:
		response = requests.get(baseURL+endpoint, params=params)
		decodedResponse = response.json()
	except Exception as e:
		print
		print "------- ERROR HITTING INSTAGRAM API -------", e
		print
	# Return the results of calling processRecentMediaResponse with decodedResponse
	return processRecentMediaResponse(decodedResponse)

# Process the Instagram API recent media response object, extracting necessary info
def processRecentMediaResponse(decodedResponse):
	userId = session['userId']
	itemIds = []
	postData = {
	'posts': [],
	'highestMaxId': 0,
	'minId': 0
	}
	print decodedResponse
	# Iterate through decoded response and process each post
	for item in decodedResponse['data']:
		tempItem = {}
		timestamp = ''
		caption = ''
		url = ''
		dimensions = {}
		mediaType = ''
		usersInPhoto = []
		tags = []
		location = None
		# Extract desired information	
		itemId = int(item['id'].split('_')[0])
		itemIds.append(itemId)
		# Set the highestMaxId value - will use this to set the mostRecentItemId value later on
		postData['highestMaxId'] = max(itemIds)
		# Add the minId key-value to postData object so we can compare against maxId in getAllNewPosts and determine if further API calls are necessary
		postData['minId'] = min(itemIds)
		try:
			timestamp = float(item['created_time'])
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM TIMESTAMP -------', e
		try:
			caption = item['caption']['text']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM CAPTION -------', e
		try:
			url = item['images']['standard_resolution']['url']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM URL -------', e
		try:
			dimensions['width'] = item['images']['standard_resolution']['width']
			dimensions['height'] = item['images']['standard_resolution']['height']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM DIMENSIONS -------', e
		try:
			mediaType = item['type']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM MEDIA TYPE -------', e
		try:
			for user in item['users_in_photo']:
				usersInPhoto.append(user['name'])
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM USERS IN PHOTO -------', e
		try:
			for tag in item['tags']:
				tags.append(tag)
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM TAGS -------', e
		try:
			item['location']['latitude']
			location = {}
			location['lat'] = item['location']['latitude']
			location['long'] = item['location']['longitude']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING ITEM LOCATION -------', e
		# Set tempItem key-values to extracted information
		tempItem['itemId'] = itemId
		tempItem['timestamp'] = timestamp
		tempItem['caption'] = caption
		tempItem['url'] = url
		tempItem['mediaType'] = mediaType
		tempItem['usersInPhoto'] = usersInPhoto
		tempItem['tags'] = tags
		tempItem['location'] = location

		fileName = url.split('/')[-1].split('?')[0]

		dataPoint = createDataPoint(userId=userId, dataPointType='photo', source='instagram', sourceData=tempItem, timestamp=timestamp, coords=location, fileName=fileName)
		# Append tempItem object to postData 'posts' key-value list
		if dataPoint != None:
			postData['posts'].append(dataPoint)
	# Sort the 'posts' key-value list by the 'itemId' key in descending order
	sortedPosts = sorted(postData['posts'], key=lambda k: k['sourceData']['itemId'], reverse=True)
	# Update the 'posts' key-value list in postData
	postData['posts'] = sortedPosts
	# Return the postData object
	return postData