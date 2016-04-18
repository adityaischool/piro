## PACKAGE FOR AUTHORIZING & HITTING THE FOURSQUARE/SWARM API

import os, md5, base64, requests, pymongo
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
# Instantiate Mongo Foursquare db
foursquareDb = client.foursquare
recentCheckinsDb = foursquareDb.foursquareRecentCheckins

# Instantiate Foursquare API credentials
API_KEY = getAPICredentials('foursquare')[0]
SECRET = getAPICredentials('foursquare')[1]
AUTH_CALLBACK = 'http://localhost:5000/foursquare-token'
# This is a special value for Foursquare's API that keeps your API calls tied to a specific version of their API
# Helps to avoid unexpected changes if they change their API - kinda nice, really!
API_VERSION = '20160324'
MODE = 'swarm'

def getAPIKey():
	return API_KEY

def getSecret():
	return SECRET

def getAuthCallback():
	return AUTH_CALLBACK

def codeFlow(code):
	userId = session['userId']
	print
	print "------- FOURSQUARE OAUTH CODE -------", code
	print
	baseURL = 'https://foursquare.com/oauth2/access_token'
	# Set params for Foursquare user authorzation request
	params = {'code': code,
	'grant_type': 'authorization_code',
	'client_id': API_KEY,
	'client_secret': SECRET,
	'redirect_uri': AUTH_CALLBACK}
	# Hit Foursquare API for access token
	try:
		response = requests.post(baseURL, data = params)
		decodedResponse = response.json()
		print
		print "------- FOURSQUARE ACCESS TOKEN RESPONSE -------"
		# pprint(decodedResponse)
		print
	except Exception as e:
		print
		print "------- ERROR GETTING FOURSQUARE ACCESS TOKEN RESPONSE -------", e
		print
	# Update the UserDevice table in the db
	updateUserDeviceTable(decodedResponse, userId)
	# If the user is not yet onboarded (i.e., it's their first time throug this process), download their history
	if not session['onboarded']:
		getUserCheckinHistory()

# Update the UserDevice table in the db
def updateUserDeviceTable(decodedResponse, userId):
	# Parse Foursquare access token response
	accessToken = decodedResponse['access_token']
	# Check if user already has a record in UserDevice - update if so, create one if not
	userIdQueryResult = UserDevice.query.filter_by(userid=userId, devicetype='foursquare').first()
	if userIdQueryResult is not None:
		# Update the user's existing record in the UserDevice table
		print
		print '------ THERE IS ALREADY A RECORD FOR THIS USER!!!! -------'
		print
		userIdQueryResult.accesstoken = accessToken
	else:
		# Create a new db record to be inserted into the UserDevice table
		userDevice = UserDevice(userId, 'foursquare', None, None, accessToken, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
	# Commit the results to the UserDevice table in the db
	try:
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING FOURSQUARE USERID & TOKEN TO DB -------", e
		print

# Display Mongo contents
def getMongoFolderContents():
	userId = session['userId']
	print
	print "------- A LIST OF ALL USERS & THEIR LAST FOURSQUARE CHECKIN TIMESTAMPS -------"
	for user in recentCheckinsDb.find({}):
		print
		print "------- User ---------------", user['userId']
		print "------- lastCheckinTimestamp -------", user['lastCheckinTimestamp']

# Reset user's lastCheckinTimestamp in Mongo - useful for testing or if user wants to redownload everything
def resetMostRecentItemId():
	userId = session['userId']
	recentCheckinsDb.update({'userId': userId}, {'$set': {'lastCheckinTimestamp': 0}})	

# Hits Mongo to find & return the timestamp of the user's most recent checkin
def getLastCheckinTimestamp():
	userId = session['userId']
	lastCheckinTimestamp = 0
	# Check if user has a Foursquare record in Mongo
	userIdQueryResults = recentCheckinsDb.find({'userId': userId})
	# If user doesn't yet have a record, create one for them with a lastCheckinTimestamp value of 0
	if userIdQueryResults.count() == 0:
		recentCheckinsDb.insert({
			'userId': userId,
			'lastCheckinTimestamp': 0
			})
	# If user does have a record, get the mostRecentItemId value - this should represent the newest post we have stored on the pi box for the user
	else:
		for user in userIdQueryResults:
			lastCheckinTimestamp = user['lastCheckinTimestamp']
			print
			print '------- MOST RECENT CHECKIN TIMESTAMP FOR USER', userId, '-------', lastCheckinTimestamp
			print
	return lastCheckinTimestamp

# Get a user's Foursquare checkin history since their last checkin
def getUserCheckinHistory():
	userId = session['userId']
	# ######## REMOVE THIS LINE ONCE TESTING IS DONE!!!! #########
	# dataPoints.remove({'$and': [{'userId': userId}, {'source': 'foursquare'}]})
	afterTimestamp = getLastCheckinTimestamp()
	offset = 0
	limit = 250
	checkinHistoryData = {'data': []}
	while True:
		try:
			pageOfCheckinData = getRecentUserCheckinPage(limit, offset, afterTimestamp)['data']
			# If no more checkins to process, break the while loop
			if len(pageOfCheckinData) == 0:
				break
			for checkin in pageOfCheckinData:
				checkinHistoryData['data'].append(checkin)
		except Exception as e:
			print
			print '------- ERROR FETCHING CHECKIN DATA -------', e
			print
		offset += 250
	# If there were any results, update the lastCheckinTimestamp in Mongo
	if len(checkinHistoryData['data']) > 0:
		# Set user's lastCheckinTimestamp to most recent checkin timestamp + 3 seconds (as not to include the last checkin in the next API call results)
		lastCheckinTimestamp = checkinHistoryData['data'][0]['timestamp'] + 3
		# Update user's lastCheckinTimestamp in Mongo
		recentCheckinsDb.update({'userId': userId}, {'$set': {'lastCheckinTimestamp': lastCheckinTimestamp}})
		# Verify Mongo update
		getMongoFolderContents()
		# Download photos
		for checkin in checkinHistoryData['data']:
			date = checkin['adjustedDate']
			if len(checkin['sourceData']['photos']) > 0:
				for photo in checkin['sourceData']['photos']:
					downloadUrl = getDownloadUrl(photo)
					downloadFile(downloadUrl, date)
		# dataPoints.remove({'source': 'foursquare'})
		# Temporarily store dataPoints in Mongo
		oldCount = dataPoints.count()
		try:
			dataPoints.insert(checkinHistoryData['data'])
		except Exception as e:
			print
			print '------- ERROR WRITING DATA POINTS TO MONGO -------', e
		# Verify that everything went to Mongo successfully
		print "------- A LIST OF THE USER'S FOLDERS, SYNC SETTINGS, & CURSORS -------"
		newCount = dataPoints.count()
		print
		print "------- NUMBER OF DATA POINTS ATTEMPTED TO ADD TO DATAPOINTS DB:", len(checkinHistoryData['data'])
		print "------- SUCCESSFULLY ADDED", newCount - oldCount, 'NEW DATA POINTS TO DATAPOINTS DB -------'
		
		# TODO: SEND CHECKIN META DATA TO STORJ - WILL MATCH TO PHOTO BY FILENAME

		return checkinHistoryData
	else:
		print
		print '------- NO NEW FOURSQUARE CHECKINS! -------'
		print
		return False

# Get the download url for the given photo object
def getDownloadUrl(photo):
	maxDimension = ''
	constructedUrl = ''
	if max([int(photo['width']), int(photo['height'])]) >= 500:
		maxDimension = '500'
	elif max([int(photo['width']), int(photo['height'])]) < 500:
		maxDimension = '300'
	constructedUrl = photo['urlPrefix'] + 'cap' + maxDimension + photo['urlSuffix']
	
	print '--------- CONSTRUCTED PHOTO URL ---------', constructedUrl
	return constructedUrl

# Downloads the file at the given URL to a specified folder
def downloadFile(url, date):
	userId = session['userId']
	downloadDirectory = 'fileStaging/'+userId+'/'+date+'/'
	# Check if download directory exists; create if it does not exist
	if not os.path.exists(downloadDirectory):
		os.makedirs(downloadDirectory)
	fileName = url.split('/')[-1]
	# Concatenate downloadDirectory + fileName
	pathPlusFileName = downloadDirectory + fileName
	# Download file at from specified Foursquare URL to specified local path
	try:
		print
		print '------- DOWNLOADING FILE FROM URL', url, '-------'
		print
		fileData = requests.get(url).content
	except Exception as e:
		print
		print '------- ERROR DOWNLOADING FILE FROM FOURSQUARE -------', e
	# Write the downlaoded file data to local disk at specified path
	f = open(pathPlusFileName, 'wb')
	f.write(fileData)
	f.close()
	
	# TODO: ADD CODE TO UPLOAD PHOTO FILES & METADATA TO STORJ - MATCH BY FILENAME
	# TODO: ONCE FILES UPLOADED TO STORJ, DELETE FROM WEB SERVER

# Gets & processes a page of results from the user's checkin history
# Optionally takes a results limit, offset (for pagination), and an afterTimestamp,
# which filters out any checkins before the timestamp - good for ignoring checkins we've already processed
def getRecentUserCheckinPage(limit=250, offset=0, afterTimestamp=0):
	userId = session['userId']
	# Fetch user's access token from UserDevice table
	accessToken = getAccessToken()
	baseURL = 'https://api.foursquare.com/v2/'
	endpoint = 'users/self/checkins'
	# Instantiate params
	params = {
	'oauth_token': accessToken,
	'v': API_VERSION,
	'm': MODE,
	'limit': limit,
	'offset': offset
	}

	# Add afterTimestamp param if given
	if afterTimestamp > 0:
		print
		print '------------ AFTER TIMESTAMP -------------', afterTimestamp
		print
		params['afterTimestamp'] = afterTimestamp
	# Hit Foursquare API
	print
	print '------------- PARAMS ----------', params
	print
	try:
		response = requests.get(baseURL+endpoint, params=params)
		decodedResponse = response.json()
		# pprint(decodedResponse)
	except Exception as e:
		print
		print "------- ERROR HITTING FOURSQUARE API -------", e
		print
	# Return the results of calling processCheckins with decodedResponse
	processedCheckins = processCheckins(decodedResponse)
	# pprint(processedCheckins)
	return processedCheckins

def processCheckins(decodedResponse):
	print
	print '------- PROCESSING DECODED RESPONSE -------'
	# pprint(decodedResponse)
	userId = session['userId']
	checkinData = {'data': []}
	# Iterate through decoded response and process each post
	for checkin in decodedResponse['response']['checkins']['items']:
		tempCheckin = {}
		# Extract desired information
		checkinId = checkin['id']
		checkinType = checkin['type']
		timestamp = checkin['createdAt']
		timeZoneOffset = checkin['timeZoneOffset']
		shout = None
		location = None
		venueName = None
		venueCoords = None
		venueUrl = None
		venueId = None
		event = None
		photos = []
		nearbyFriends = []
		try:
			shout = checkin['shout']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN SHOUT -------', e
		try:
			checkin['location']['lat']
			location = {}
			location['lat'] = checkin['location']['lat']
			location['long'] = checkin['location']['lng']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN LOCATION -------', e
		try:
			venueName = checkin['venue']['name']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN VENUE -------', e
		try:
			venueId = checkin['venue']['id']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN VENUE ID -------', e
		try:
			venuePhotoUrl = getDownloadUrl(getVenuePhoto(venueId))
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN VENUE PHOTO URL -------', e
		try:
			checkin['venue']['location']['lat']
			venueCoords = {}
			venueCoords['lat'] = checkin['venue']['location']['lat']
			venueCoords['long'] = checkin['venue']['location']['lng']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN VENUE COORDS -------', e
		try:
			venueURL = checkin['venue']['url']
		except:
			print
			print '------- ERROR EXTRACTING CHECKIN VENUE URL -------', e
		try:
			event = checkin['event']['name']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN EVENT -------', e
		try:
			for photo in checkin['photos']['items']:
				tempPhoto = {}
				photoTimestamp = photo['createdAt']
				photoHeight = photo['height']
				photoWidth = photo['width']
				photoId = photo['id']
				photoUrlPrefix = photo['prefix']
				photoUrlSuffix = photo['suffix']

				tempPhoto['timestamp'] = photoTimestamp
				tempPhoto['height'] = photoHeight
				tempPhoto['width'] = photoWidth
				tempPhoto['id'] = photoId
				tempPhoto['urlPrefix'] = photoUrlPrefix
				tempPhoto['urlSuffix'] = photoUrlSuffix

				photos.append(tempPhoto)
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN PHOTO(S) -------', e
		try:
			for friend in checkin['overlaps']['items']:
				nearbyFriends.append(friend)
		except Exception as e:
			print
			print '------- ERROR EXTRACTING NEARBY FRIENDS -------', e

		# Set tempCheckin key-values to extracted information
		tempCheckin['checkinId'] = checkinId
		tempCheckin['checkinType'] = checkinType
		tempCheckin['timestamp'] = timestamp
		tempCheckin['timeZoneOffset'] = timeZoneOffset
		tempCheckin['shout'] = shout
		tempCheckin['location'] = location
		tempCheckin['venueId'] = venueId
		tempCheckin['venueName'] = venueName
		tempCheckin['venueCoords'] = venueCoords
		tempCheckin['venueUrl'] = venueUrl
		tempCheckin['venuePhotoUrl'] = venuePhotoUrl
		tempCheckin['venueCoords'] = venueCoords
		tempCheckin['event'] = event
		tempCheckin['photos'] = photos
		tempCheckin['nearbyFriends'] = nearbyFriends

		photoNames = []
		for photo in tempCheckin['photos']:
			photoNames.append(photo['urlSuffix'].split('/')[-1])

		locationCoords = {}

		if venueCoords is not None:
			locationCoords = venueCoords
		else:
			locationCoords = location

		dataPoint = createDataPoint(userId=userId, dataPointType='checkin', source='foursquare', sourceData=tempCheckin, timestamp=timestamp, location=locationCoords, fileName=photoNames, businessName=venueName)
		# Append tempCheckin objecct to postData 'posts' key-value list
		if dataPoint != None:
			checkinData['data'].append(dataPoint)
	# Return the postData object
	return checkinData

def getVenuePhoto(venueId):
	baseUrl = 'https://api.foursquare.com/v2/'
	endpoint = 'venues/'+venueId+'/photos'
	params = {
	'v': API_VERSION,
	'm': 'foursquare',
	'client_id': API_KEY,
	'client_secret': SECRET,
	'group': 'venue'
	}

	constructedUrl = baseUrl + endpoint

	response = requests.get(constructedUrl, params=params)
	decodedResponse = response.json()
	# print
	# print '------- FOURSQUARE VENUE PHOTOS RESPONSE -------'
	# pprint(decodedResponse)

	for photo in decodedResponse['response']['photos']['items']:
		tempPhoto = {}
		source = None
		try:
			source = photo['source']['name']
		except Exception as e:
			print
			print '------- ERROR GETTING FOURSQUARE VENUE PHOTO SOURCE -------', e
			print
		# Only use Instagram-taken photos because they tend to be higher quality
		if source == 'Instagram':
			try:
				tempPhoto['height'] = photo['height']
				tempPhoto['width'] = photo['width']
				tempPhoto['id'] = photo['id']
				tempPhoto['urlPrefix'] = photo['prefix']
				tempPhoto['urlSuffix'] = photo['suffix']
				return tempPhoto
			except:
				continue
		else:
			continue
	return None

# Check whether or not the user has authorized access to Foursquare or not
def checkIfFoursquareAuthorized():
	userId = session['userId']
	# Query UserDevice table current user's Foursquare credentials
	try:
		userIdQueryResults = UserDevice.query.filter_by(userid=userId, devicetype='foursquare').first()
	except Exception as e:
		print
		print "------- ERROR QUERYING DB FOR FOURSQUARE USERDEVICE RECORD -------", e
		print
	# Check if user has authorized Foursquare yet
	if (type(userIdQueryResults) != type(None)):
		return [True, userIdQueryResults]
	else:
		print
		print "------- USERDEVICE FOURSQUARE RECORD FOR USER", userId, "DOES NOT YET EXIST -------"
		print
		return [False, None]

# Parse the UserDevice table query response and return the user's access token
def getAccessToken():
	foursquareCheckResponse = checkIfFoursquareAuthorized()
	if foursquareCheckResponse[0]:
		try:
			userDeviceDict = foursquareCheckResponse[1].__dict__
			accessToken = userDeviceDict['accesstoken']
			return accessToken
		except Exception as e:
			print
			print "------- ERROR GETTING USER'S FOURSQUARE ACCESS TOKEN -------", e
			print
			return None
	else:
		return None