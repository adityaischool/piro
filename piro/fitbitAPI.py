## PACKAGE FOR AUTHORIZING & HITTING THE FITBIT API

import base64, requests, pymongo, fitbitLibrary
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint

# Instantiate Mongo client
client = pymongo.MongoClient()
mongoDb = client.fitbit
lastFitbitSync = mongoDb.lastFitbitSync

API_KEY = '227NKT'
SECRET = 'd7a4ececd5e68a5f3f36d64e304fbe25'
AUTH_CALLBACK = 'http://localhost:5000/fitbit-token'

fitbit = ''

def getAPIKey():
	return API_KEY

def getSecret():
	return SECRET

def getAuthCallback():
	return AUTH_CALLBACK

def codeFlow(code):
	userId = session['userId']
	print
	print "------- FITBIT OAUTH CODE -------", code
	print
	baseURL = 'https://api.fitbit.com/oauth2/token'
	# Set params for Fitbit user authorzation request
	params = {'code': code,
	'grant_type': 'authorization_code',
	'client_id': API_KEY,
	'client_secret': SECRET,
	'redirect_uri': AUTH_CALLBACK}
	encodedAuthHeader = base64.b64encode(API_KEY+':'+SECRET)
	headers = {
	'Authorization': 'Basic ' + encodedAuthHeader
	}
	# Hit Fitbit API for access token
	try:
		response = requests.post(baseURL, data=params, headers=headers)
		decodedResponse = response.json()
		print
		print "------- FITBIT TOKEN RESPONSE -------"
		pprint(decodedResponse)
		print
	except Exception as e:
		print
		print "------- ERROR GETTING FITBIT TOKEN RESPONSE -------", e
		print
	# Update the UserDevice table in the db
	updateUserDeviceTable(decodedResponse, userId)

# Update the UserDevice table in the db
def updateUserDeviceTable(decodedResponse, userId):
	# Parse Fitbit access token response
	accessToken = decodedResponse['access_token']
	refreshToken = decodedResponse['refresh_token']
	fitbitUserId = decodedResponse['user_id']
	# Check if user already has a record in UserDevice - update if so, create one if not
	userIdQueryResult = UserDevice.query.filter_by(userid=userId, devicetype='fitbit').first()
	if userIdQueryResult is not None:
		# Update the user's existing record in the UserDevice table
		print
		print '------ THERE IS ALREADY A RECORD FOR THIS USER!!!! -------'
		print
		userIdQueryResult.deviceuserid = fitbitUserId
		userIdQueryResult.accesstoken = accessToken
		userIdQueryResult.refreshtoken = refreshToken
	else:
		# Create a new db record to be inserted into the UserDevice table
		userDevice = UserDevice(userId, 'fitbit', None, fitbitUserId, accessToken, refreshToken)
		# Add and commit newly created User db record
		db.session.add(userDevice)
	# Commit the results to the UserDevice table in the db
	try:
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING FITBIT USERID & TOKENS TO DB -------", e
		print

# Check whether or not the user has authorized access to Instagram or not
def checkIfFitbitAuthorized():
	userId = session['userId']
	# Query UserDevice table current user's Fitbit credentials
	try:
		userIdQueryResults = UserDevice.query.filter_by(userid=userId, devicetype='fitbit').first()
	except Exception as e:
		print
		print "------- ERROR QUERYING DB FOR FITBIT USERDEVICE RECORD -------", e
		print
	# Check if user has authorized Instagram yet
	if (type(userIdQueryResults) != type(None)):
		return [True, userIdQueryResults]
	else:
		print
		print "------- USERDEVICE FITBIT RECORD FOR USER", userId, "DOES NOT YET EXIST -------"
		print
		return [False, None]

# Parse the web server db query response and return the user's access token
def getTokensFromDb():
	fitbitCheckResponse = checkIfFitbitAuthorized()
	if fitbitCheckResponse[0]:
		try:
			userDeviceDict = fitbitCheckResponse[1].__dict__
			accessToken = userDeviceDict['accesstoken']
			refreshToken = userDeviceDict['refreshtoken']
			print
			print '------- USER ACCESS TOKEN -------', accessToken
			print '------- USER REFRESH TOKEN -------', refreshToken
			print
			return [accessToken, refreshToken]
		except Exception as e:
			print
			print "------- ERROR GETTING USER'S FITBIT ACCESS & REFRESH TOKENS -------", e
			print
			return [None, None]
	else:
		return [None, None]

# Get Fitbit access & refresh tokens from web server db and instantiate Fitbit API object
def setFitbitApiObj():
	global fitbit
	tokens = getTokensFromDb()
	accessToken = tokens[0]
	refreshToken = tokens[1]
	try:
		# Instantiate Fitbit API object
		fitbit = fitbitLibrary.Fitbit(API_KEY, SECRET, access_token=accessToken, refresh_token=refreshToken)
	except Exception as e:
		print
		print "------- ERROR INSTANTIATING FITBIT API OBJECT -------", e
		print

def pollRecentFitbitData():
	setFitbitApiObj()
	# Hit 'Activities' endpoint of Fitbit API
	fitbitActivitiesData = fitbit.activities('today')
	print "-----------\n-----\n---Activities Data-----\n\n\n"
	pprint(fitbitActivitiesData)
	getIntradayHeartData()


def getIntradayHeartData(date='today'):
	responseData = fitbit.intraday_time_series_heart(base_date=date, detail_level='1min')
	print
	print '------- INTRADAY HEART RATE DATA FROM', date, '-------'
	pprint(responseData)
	print

# Display Mongo contents
def getMongoFolderContents():
	userId = session['userId']
	print
	print "------- USER'S LAST FITBIT SYNC TIMESTAMP -------"
	for user in lastFitbitSync.find({}):
		print
		print "------- User ---------------", user['userId']
		print "------- lastFitbitSyncTimestamp -------", user['lastFitbitSyncTimestamp']

# Reset user's lastFitbitSyncTimestamp in Mongo - useful for testing or if user wants to redownload everything
def resetLastFitbitSyncTimestamp():
	userId = session['userId']
	lastFitbitSync.update({'userId': userId}, {'$set': {'lastFitbitSyncTimestamp': 0}})	

# Hits Mongo to find & return the timestamp of the user's last sync
def getLastFitbitSyncTimestamp():
	userId = session['userId']
	lastFitbitSyncTimestamp = 0
	# Check if user has a Foursquare record in Mongo
	userIdQueryResults = lastFitbitSync.find({'userId': userId})
	# If user doesn't yet have a record, create one for them with a lastCheckinTimestamp value of 0
	if userIdQueryResults.count() == 0:
		recentCheckinsDb.insert({
			'userId': userId,
			'lastFitbitSyncTimestamp': 0
			})
	# If user does have a record, get the lastFitbitSyncTimestamp value - this should represent the newest post we have stored on the pi box for the user
	else:
		for user in userIdQueryResults:
			lastFitbitSyncTimestamp = user['lastFitbitSyncTimestamp']
			print
			print '------- MOST RECENT FITBIT SYNC TIMESTAMP FOR USER', userId, '-------', lastFitbitSyncTimestamp
			print
	return lastFitbitSyncTimestamp