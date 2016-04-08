## PACKAGE FOR AUTHORIZING & HITTING THE FITBIT API

import base64, requests, time, datetime, pymongo, fitbitLibrary
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint
from apiCredentials import getAPICredentials

# Instantiate Mongo client
client = pymongo.MongoClient()
mongoDb = client.fitbit
lastFitbitSync = mongoDb.lastFitbitSync

# Instantiate Fitbit API credentials
API_KEY = getAPICredentials('fitbit')[0]
SECRET = getAPICredentials('fitbit')[1]
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

# Check whether or not the user has authorized access to Fitbit or not
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

# Parse the UserDevice table query response and return the user's access token
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

# Get Fitbit access & refresh tokens from UserDevice table and instantiate Fitbit API object
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

# Get a user's recent Fitbit data
def pollRecentFitbitData():
	# Instantiate the Fitbit API object
	setFitbitApiObj()
	lastSyncDate = getLastFitbitSyncDate()
	if lastSyncDate == '0':
		getUserMembershipDate()
		lastSyncDate = getLastFitbitSyncDate()
	# Iterate through each day since lastSyncDate & hit Fitbit API until lastSyncDate == yesterday
	while True:
		# Check if lastSyncDate is yesterday - if so, update Mongo with current lastSyncDate & break loop
		if checkIfLastSyncDateIsYesterday(lastSyncDate):
			print
			print '------- FITBIT DATA SYNCED THROUGH YESTERDAY,', lastSyncDate,'-------'
			print
			break
		print
		print "------- SLEEPING 48 SECONDS PER FITBIT'S RATE LIMITS -------"
		print
		# time.sleep(48)
		# Otherwise, add 1 day to lastSyncDate & get data from Fitbit API
		lastSyncDate = addOneDayToLastSyncDate(lastSyncDate)
		# Hit Fitbit API endpoints with lastSyncDate
		getIntradayStepsData(date=lastSyncDate)
		getIntradayHeartData(date=lastSyncDate)
	updateLastFitbitSyncDate(lastSyncDate)

def addOneDayToLastSyncDate(lastSyncDate):
	formattedLastSyncDate = datetime.datetime.strptime(lastSyncDate, '%Y-%m-%d').date()
	updatedLastSyncDate = formattedLastSyncDate + datetime.timedelta(days=1)
	formattedLastSyncDate = datetime.datetime.strftime(updatedLastSyncDate, '%Y-%m-%d')
	return formattedLastSyncDate

def checkIfLastSyncDateIsYesterday(lastSyncDate):
	# Turn lastSyncDate into datetime date object
	formattedLastSyncDate = datetime.datetime.strptime(lastSyncDate, '%Y-%m-%d').date()
	# Instantiate 'yesterday' datetime date object
	yesterday = datetime.date.today() - datetime.timedelta(days=1)
	if formattedLastSyncDate == yesterday:
		return True
	else:
		return False

# Hit Fitbit API for a user's intraday activity data
# Date format is YYYY-MM-DD, 'today', or 'yesterday'
def getIntradayStepsData(date='yesterday'):
	lastFitbitSyncDate = getLastFitbitSyncDate()
	responseData = fitbit.intraday_time_series(resource='steps', base_date=date, detail_level='1min')
	print
	print '------- INTRADAY STEPS DATA FROM', date, '-------'
	pprint(responseData)
	print

# Hit Fitbit API for a user's intraday heart rate data
# Date format is YYYY-MM-DD, 'today', or 'yesterday'
def getIntradayHeartData(date='yesterday'):
	lastFitbitSyncDate = getLastFitbitSyncDate()
	responseData = fitbit.intraday_time_series_heart(base_date=date, detail_level='1min')
	print
	print '------- INTRADAY HEART RATE DATA FROM', date, '-------'
	pprint(responseData)
	print

# Get a user's Fitbit membership date
# Set the day before this date as the lastFitbitSyncDate when polling user's historical data
def getUserMembershipDate():
	userProfile = fitbit.user_profile_get()
	userMembershipDate = userProfile['user']['memberSince']
	formattedMembershipDate = datetime.datetime.strptime(userMembershipDate, '%Y-%m-%d').date()
	dayBeforeMembership = formattedMembershipDate - datetime.timedelta(days=1)
	formattedDayBeforeMemberShip = datetime.datetime.strftime(dayBeforeMembership, '%Y-%m-%d')
	# Now update the lastFitbitSyncDate to 1 day before the user's membership date
	updateLastFitbitSyncDate(formattedDayBeforeMemberShip)

def updateLastFitbitSyncDate(date):
	userId = session['userId']
	# Make sure there is a lastFitbitSyncDate to update
	getLastFitbitSyncDate()
	# Update the lastFitbitSyncDate to the given date
	lastFitbitSync.update({'userId': userId}, {'$set': {'lastFitbitSyncDate': date}})
	# Verify changes in Mongo
	getMongoFolderContents()

# Display Mongo contents
def getMongoFolderContents():
	userId = session['userId']
	for user in lastFitbitSync.find({}):
		print
		print "------- USER", user['userId'], "LAST FITBIT SYNC DATE", user['lastFitbitSyncDate'], "-------"

# Reset user's lastFitbitSyncDate in Mongo - useful for testing or if user wants to redownload everything
def resetLastFitbitSyncDate():
	userId = session['userId']
	lastFitbitSync.update({'userId': userId}, {'$set': {'lastFitbitSyncDate': '0'}})	

# Hits Mongo to find & return the date of the user's last sync
def getLastFitbitSyncDate():
	userId = session['userId']
	lastFitbitSyncDate = '0'
	# Check if user has a Foursquare record in Mongo
	userIdQueryResults = lastFitbitSync.find({'userId': userId})
	# If user doesn't yet have a record, create one for them with a lastFitbitSyncDate value of 0
	if userIdQueryResults.count() == 0:
		lastFitbitSync.insert({
			'userId': userId,
			'lastFitbitSyncDate': '0'
			})
	# If user does have a record, get the lastFitbitSyncDate value - this should represent the newest post we have stored on the pi box for the user
	else:
		for user in userIdQueryResults:
			lastFitbitSyncDate = user['lastFitbitSyncDate']
			print
			print '------- MOST RECENT FITBIT SYNC DATE FOR USER', userId, '-------', lastFitbitSyncDate
			print
	return lastFitbitSyncDate