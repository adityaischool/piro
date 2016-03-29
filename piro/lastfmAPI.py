## PACKAGE FOR AUTHORIZING & HITTING THE LAST.FM API

import md5, base64, requests, pymongo
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint
from apiCredentials import getAPICredentials

# Instantiate Mongo client
client = pymongo.MongoClient()
mongoDb = client.lastfm
recentSongPlaysDb = mongoDb.lastfmRecentSongPlaysDb

# Instantiate Last.fm API credentials
API_KEY = getAPICredentials('lastfm')[0]
SECRET = getAPICredentials('lastfm')[1]
# Callback on Last.fm server = 'http://localhost:5000/connect-lastfm'
AUTH_CALLBACK = 'http://localhost:5000/lastfm-token'
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

def getAPIKey():
	return API_KEY

def getSecret():
	return SECRET

def getAuthCallback():
	return AUTH_CALLBACK

# Get the user's username and store in db so we can
# call other last.fm methods that do not require
# authorization (they only require a username)
def getUserName(token):
	userId = session['userId']
	# Generate md5-hashed signature per Last.fm's authorization requirements
	try:
		signature = lastfmSignatureGen(token)
		print
		print "--------- SIGNATURE -------", signature
		print
	except Exception as e:
		print
		print "------- ERROR GETTING LAST.FM AUTH SIGNATURE -------", e
		print
	# Hit Last.fm API for user authorization
	try:
		requestUrlRaw = 'http://ws.audioscrobbler.com/2.0/?method=auth.getsession&api_key='+API_KEY+'&token='+token+'&api_sig='+signature+'&format=json'
		requestUrlEncoded = requestUrlRaw.decode('utf-8').encode('utf-8')
		getAuthSession = requests.get(requestUrlEncoded)
	except Exception as e:
		print "------- ERROR AUTHORIZING USER WITH LAST.FM -------", e
	# Parse Last.fm user authorization response	
	try:
		decodedResponse = getAuthSession.json()
		print
		print "------- AUTH SESSION RESPONSE -------"
		pprint(decodedResponse)
		print
	except Exception as e:
		print
		print "------- ERROR DECODING LAST.FM USER AUTH RESPONSE -------", e
		print
	# Update the UserDevice table in the db
	updateUserDeviceTable(decodedResponse, userId)
	# If the user is not yet onboarded (i.e., it's their first time throug this process), download their history
	if not session['onboarded']:
		getUserHistoricalPlays()

# Update the UserDevice table in the db
def updateUserDeviceTable(decodedResponse, userId):
	# Parse Last.fm access token response
	lastfmUsername = decodedResponse['session']['name']
	# Check if user already has a record in UserDevice - update if so, create one if not
	userIdQueryResult = UserDevice.query.filter_by(userid=userId, devicetype='lastfm').first()
	if userIdQueryResult is not None:
		# Update the user's existing record in the UserDevice table
		print
		print '------ THERE IS ALREADY A RECORD FOR THIS USER!!!! -------'
		print
		userIdQueryResult.deviceusername = lastfmUsername
	else:
		# Create a new db record to be inserted into the UserDevice table
		userDevice = UserDevice(userId, 'lastfm', lastfmUsername, None, None, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
	# Commit the results to the UserDevice table in the db
	try:
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING LAST.FM USERNAME TO DB -------", e
		print

# Display Mongo contents
def getMongoFolderContents():
	userId = session['userId']
	print
	print "------- A LIST OF ALL USERS & THEIR LAST LAST.FM SONG PLAYBACK TIMESTAMPS -------"
	for user in recentSongPlaysDb.find({}):
		print
		print "------- User ---------------", user['userId']
		print "------- lastSongPlaybackTimestamp -------", user['lastSongPlaybackTimestamp']

# Reset user's most recent playback timestamp record in Mongo - useful for testing or if user wants to redownload their data
def resetMostRecentPlaybackTimestamp():
	userId = session['userId']
	recentSongPlaysDb.update({'userId': userId}, {'$set': {'lastSongPlaybackTimestamp': 0}})
	# Verify Mongo update
	getMongoFolderContents()	

# Hits Mongo to find & return the timestamp of the user's most recent song playback
def getLastPlaybackTimestamp():
	userId = session['userId']
	lastSongPlaybackTimestamp = 0
	# Check if user has a Last.fm record in Mongo
	userIdQueryResults = recentSongPlaysDb.find({'userId': userId})
	# If user doesn't yet have a record, create one for them with a lastCheckinTimestamp value of 0
	if userIdQueryResults.count() == 0:
		recentSongPlaysDb.insert({
			'userId': userId,
			'lastSongPlaybackTimestamp': 0
			})
	# If user does have a record, get the mostRecentItemId value - this should represent the newest post we have stored on the pi box for the user
	else:
		for user in userIdQueryResults:
			lastSongPlaybackTimestamp = user['lastSongPlaybackTimestamp']
			print
			print '------- MOST RECENT SONG PLAYBACK TIMESTAMP FOR USER', userId, '-------', lastSongPlaybackTimestamp
			print
	return lastSongPlaybackTimestamp

# Function for generating an md5-hashed signature,
# required by last.fm API for an auth session
# takes a token, provided by the last.fm auth sequence
def lastfmSignatureGen(token):
	token = token
	method = 'auth.getsession'
	# Concatenate unsigned params in alphabetical order per Last.fm's requirements
	unsignedParams = "api_key" + API_KEY + \
	"method" + method + \
	"token" + token
	# Encode unsigned params, then tack on app secret
	unsignedParams.encode('utf-8')
	unsignedParams += SECRET
	# Generate md5 hash and update with unsigned params
	m = md5.new()
	m.update(unsignedParams)
	return m.hexdigest()

# Function to call the Last.fm API
def callAPI(page=None, fromTimestamp=0):
	page = page
	userId = session['userId']
	userIdQueryResults = UserDevice.query.filter_by(userid=userId, devicetype='lastfm').first()
	userDeviceDict = userIdQueryResults.__dict__
	userLastfmUsername = userDeviceDict['deviceusername']
	method = "user.getrecenttracks"

	params = {
	'method': method,
	'user': userLastfmUsername,
	'api_key': API_KEY,
	'format': 'json',
	'limit': 200,
	}

	if page:
		params['page'] = page
	if fromTimestamp > 0:
		params['from'] = fromTimestamp

	try:
		response = requests.get(BASE_URL, params=params)
		decodedResponse = response.json()
		return decodedResponse
	except Exception as e:
		print
		print "------- ERROR HITTING LAST.FM API -------", e

# Get a user's play history starting with the most recently captured song playback timestamp, if available
def getUserHistoricalPlays():
	# resetMostRecentPlaybackTimestamp()
	historicalPlaysObject = {'data': []}
	fromTimestamp = getLastPlaybackTimestamp()
	mostRecentlyPlayedTimestamp = fromTimestamp
	page = 1
	# Go through each page of API results and process tracks until we process all new tracks
	while True:
		try:
			print
			print '------- CALLING PAGE', page, 'OF LAST.FM API WITH TIMESTAMP', fromTimestamp, '-------'
			decodedResponse = callAPI(page, fromTimestamp)
			responseTracks = decodedResponse['recenttracks']['track']
			print '------- PAGE', page, 'OF RESULTS HAS', len(responseTracks), 'TRACKS TO PROCESS -------'
			print
			# Check to make sure response has playback songs - break loop if no more songs to process
			if len(responseTracks) > 0:
				# Extract track info
				for track in responseTracks:
					processedTrack = processTrack(track)
					if processedTrack['playbackTimestamp'] > mostRecentlyPlayedTimestamp:
						mostRecentlyPlayedTimestamp = processedTrack['playbackTimestamp']
					historicalPlaysObject['data'].append(processedTrack)
			else:
				print
				print '------- NO MORE RECENT SONG PLAYBACKS! -------'
				print
				break
			# Move on to next page of results
			page += 1
		except Exception as e:
			print
			print "------ ERROR GETTING LAST.FM SONG PLAYBACK DATA -------", e
			break
	# Update Mongo with mostRecentlyPlayedTimestamp
	updateMongoMostRecentSongPlaybackTimestamp(int(mostRecentlyPlayedTimestamp)+1)
	print
	print "---------- THERE WERE", len(historicalPlaysObject['data']), "NEW SONG PLAYBACKS -----------"
	print
	# Send processed track data to pi box
	saveToBox(historicalPlaysObject)

# Function to update Mongo with mostRecentlyPlayedTimestamp
def updateMongoMostRecentSongPlaybackTimestamp(mostRecentlyPlayedTimestamp):
	userId = session['userId']
	recentSongPlaysDb.update({'userId': userId}, {'$set': {'lastSongPlaybackTimestamp': mostRecentlyPlayedTimestamp}})
	# Verify Mongo update
	getMongoFolderContents()

# Extract & bundle relevant data for given track
def processTrack(track):
	processedTrack = {}
	try:
		trackName = track['name'].encode('utf-8')
	except Exception as e:
		print "----- ERROR GETTING TRACK NAME -----", e
	try:
		trackArtist = track['artist']['#text'].encode('utf-8')
	except Exception as e:
		print "----- ERROR GETTING TRACK ARTIST -----", e
	try:
		playbackTimestamp = track['date']['uts']
	except Exception as e:
		print "----- ERROR GETTING TRACK PLAYBACK TIMESTAMP -----", e
	try:
		imageUrl = track['image'][1]['#text']
	except Exception as e:
		print "----- ERROR GETTING TRACK IMAGE URL -----", e
	# Populate processed track object
	processedTrack['trackName'] = trackName
	processedTrack['trackArtist'] = trackArtist
	processedTrack['playbackTimestamp'] = playbackTimestamp
	processedTrack['imageUrl'] = imageUrl
	# Return processed track
	return processedTrack


def saveToBox(trackPlaybackObject):
	pass
	# print trackPlaybackObject
	# NEED TO ADD LOGIC TO ENCRYPT & WRITE OBJECT DATA TO THE BOX
	# ALSO NEED LOGIC TO SAVE TO WEB SERVER TEMPORARILY IN CASE BOX IS UNREACHABLE (DELETE FROM WEB SERVER AFTER SUCCESSFULLY WRITING TO BOX)


if __name__ == '__main__':
	# getUserRecentPlays()
	getUserHistoricalPlays()