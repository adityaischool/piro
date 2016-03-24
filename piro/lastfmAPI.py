## PACKAGE FOR AUTHORIZING & HITTING THE LAST.FM API

import md5, base64, requests
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint


API_KEY = '070094824815e5b8dc5fcfbc5a2f723f'
SECRET = '3afa4374733f63f58bd6e5b5962cbbb6'
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
		jsonResponse = getAuthSession.json()
		print
		print "------- AUTH SESSION RESPONSE -------"
		pprint(jsonResponse)
		print
		lastfmUsername = jsonResponse['session']['name']
		print "------- LAST.FM USERNAME -------", lastfmUsername
		print
	except Exception as e:
		print
		print "------- ERROR PARSING LAST.FM USER AUTH RESPONSE -------", e
		print
	# Now write the user's Last.fm username to the web server db
	try:
		userDevice = UserDevice(userId, 'lastfm', lastfmUsername, None, None, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING LAST.FM USERNAME TO DB -------", e
		print

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

def callAPI(page=None):
	userId = session['userId']
	userIdQueryResults = UserDevice.query.filter_by(userid=userId, devicetype='lastfm').first()
	userDeviceDict = userIdQueryResults.__dict__
	userLastfmUsername = userDeviceDict['deviceusername']
	method = "user.getrecenttracks"
	amp = "&"

	constructedURL = BASE_URL + '?' + \
	"method=" + method + amp + \
	"user=" + userLastfmUsername + amp + \
	"api_key=" + API_KEY + amp + \
	"format=json" + amp + \
	"limit=200"

	if page:
		constructedURL += ("&page=" + str(page))
		print "----- CONSTRUCTED URL -------", constructedURL

	try:
		response = requests.get(constructedURL)
		return response
	except Exception as e:
		print
		print "------- ERROR HITTING LAST.FM API -------", e

# Get a given user's recent tracks, optionally by date
def getUserRecentPlays():
	recentPlaysObject = {'plays': []}

	response = callAPI()
	# Extract track info
	for track in response.json()['recenttracks']['track']:
		processedTrack = processTrack(track)
		recentPlaysObject['plays'].append(processedTrack)

	saveToBox(recentPlaysObject)

# Get a user's complete play history
def getUserHistoricalPlays():
	historicalPlaysObject = {'plays': []}

	page = 1
	while True:
		try:
			response = callAPI(page)
			# Extract track info
			for track in response.json()['recenttracks']['track']:
				processedTrack = processTrack(track)
				historicalPlaysObject['plays'].append(processedTrack)
				page += 1

		# Break out of loop if error, or if page does not exist (reached end of historical tracks)
		except Exception as e:
			print
			print "------ ERROR -------", e
			break

	print
	print "---------- THERE WERE", page, "PAGES OF HISTORICAL TRACKS FOR THIS USER -----------"
	print

	saveToBox(historicalPlaysObject)

def processTrack(track):
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

	# print 
	# print "TRACK NAME:", trackName
	# print "TRACK ARTIST:", trackArtist
	# print "PLAYBACK TIMESTAMP:", playbackTimestamp
	# print "TRACK IMAGE URL:", imageUrl

	processedTrack = {}
	processedTrack['trackName'] = trackName
	processedTrack['trackArtist'] = trackArtist
	processedTrack['playbackTimestamp'] = playbackTimestamp
	processedTrack['imageUrl'] = imageUrl

	return processedTrack


def saveToBox(trackPlaybackObject):
	print trackPlaybackObject
	# NEED TO ADD LOGIC TO ENCRYPT & WRITE OBJECT DATA TO THE BOX
	# ALSO NEED LOGIC TO SAVE TO WEB SERVER TEMPORARILY IN CASE BOX IS UNREACHABLE (DELETE FROM WEB SERVER AFTER SUCCESSFULLY WRITING TO BOX)


if __name__ == '__main__':
	# getUserRecentPlays()
	getUserHistoricalPlays()