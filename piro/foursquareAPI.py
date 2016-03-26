## PACKAGE FOR AUTHORIZING & HITTING THE FOURSQUARE/SWARM API

import md5, base64, requests, pymongo
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint

# Instantiate Mongo client
client = pymongo.MongoClient()
mongoDb = client.foursquare
recentCheckinsDb = mongoDb.foursquareRecentCheckins

API_KEY = 'OZ44SB02FKZ52UFPU0BNDJIX02ARUFPRLVRKABH0RAR5YVGR'
SECRET = 'KYDDWZEXFQ33WAD0TU2RCFEAFFNHKHL5LQ4I3EJT1UIJ5BLN'
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
		pprint(decodedResponse)
		print
	except Exception as e:
		print
		print "------- ERROR GETTING FOURSQUARE ACCESS TOKEN RESPONSE -------", e
		print
	# Parse Foursquare access token response
	token = decodedResponse['access_token']
	# Write the user's Foursquare token to the web server db
	try:
		userDevice = UserDevice(userId, 'foursquare', None, None, token, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
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
			offset += 250
		except Exception as e:
			print
			print '------- ERROR FETCHING CHECKIN DATA -------', e
			print
	# If there were any results, update the lastCheckinTimestamp in Mongo
	if len(checkinHistoryData['data']) > 0:
		# Set user's lastCheckinTimestamp to most recent checkin timestamp + 3 seconds (as not to include the last checkin in the next API call results)
		lastCheckinTimestamp = checkinHistoryData['data'][0]['timestamp'] + 3
		# Update user's lastCheckinTimestamp in Mongo
		recentCheckinsDb.update({'userId': userId}, {'$set': {'lastCheckinTimestamp': lastCheckinTimestamp}})
		# Verify Mongo update
		getMongoFolderContents()

		# TODO: ADD CODE FOR DOWNLOADING PHOTOS LOCALLY & PUSHING TO PI BOX - MAYBE GET PHOTOS USING SEPARATE ENDPOINT?
		# TODO: PUSH CHECKIN METADATA TO PI BOX
		return checkinHistoryData
	else:
		print
		print '------- NO NEW FOURSQUARE CHECKINS! -------'
		print
		return False

# Gets & processes a page of results from the user's checkin history
# Optionally takes a results limit, offset (for pagination), and an afterTimestamp,
# which filters out any checkins before the timestamp - good for ignoring checkins we've already processed
def getRecentUserCheckinPage(limit=250, offset=0, afterTimestamp=0):
	userId = session['userId']
	# Fetch user's access token from web server db
	accessToken = getAccessToken()
	baseURL = 'https://api.foursquare.com/v2'
	endpoint = '/users/self/checkins'
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
		pprint(decodedResponse)
	except Exception as e:
		print
		print "------- ERROR HITTING FOURSQUARE API -------", e
		print
	# Return the results of calling processCheckins with decodedResponse
	processedCheckins = processCheckins(decodedResponse)
	pprint(processedCheckins)
	return processedCheckins

def processCheckins(decodedResponse):
	checkinData = {'data': []}
	# Iterate through decoded response and process each post
	for checkin in decodedResponse['response']['checkins']['items']:
		tempCheckin = {}
		# Extract desired information
		checkinId = checkin['id']
		checkinType = checkin['type']
		timestamp = checkin['createdAt']
		timeZoneOffset = checkin['timeZoneOffset']
		shout = ''
		location = {}
		venueName = ''
		venueCoords = {}
		venueUrl = ''
		event = ''
		photos = []
		nearbyFriends = []
		try:
			shout = checkin['shout']
		except Exception as e:
			print
			print '------- ERROR EXTRACTING CHECKIN SHOUT -------', e
		try:
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
				photos.append(photo)
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
		tempCheckin['venueName'] = venueName
		tempCheckin['venueCoords'] = venueCoords
		tempCheckin['venueUrl'] = venueUrl
		tempCheckin['venueCoords'] = venueCoords
		tempCheckin['event'] = event
		tempCheckin['photos'] = photos
		tempCheckin['nearbyFriends'] = nearbyFriends
		# Append tempCheckin objecct to postData 'posts' key-value list
		checkinData['data'].append(tempCheckin)
	# Return the postData object
	return checkinData

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

# Parse the web server db query response and return the user's access token
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