## PACKAGE FOR HITTING THE LAST.FM API

import md5, base64, requests
from flask import request
from models import UserDevice,User
from pprint import pprint


API_KEY = '070094824815e5b8dc5fcfbc5a2f723f'
SECRET = '3afa4374733f63f58bd6e5b5962cbbb6'
# Callback on Last.fm server = 'http://localhost:5000/connect-lastfm'
AUTH_CALLBACK = 'http://localhost:5000/lastfm-token'

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
	signature = lastfmSignatureGen(token)
	print
	print "--------- SIGNATURE -------", signature
	print

	requestUrlRaw = 'http://ws.audioscrobbler.com/2.0/?method=auth.getsession&api_key='+API_KEY+'&token='+token+'&api_sig='+signature+'&format=json'
	requestUrlEncoded = requestUrlRaw.decode('utf-8').encode('utf-8')

	getAuthSession = requests.get(requestUrlEncoded)
	jsonResponse = getAuthSession.json()
	print
	print "------- AUTH SESSION RESPONSE -------"
	pprint(jsonResponse)
	print

	lastfmUsername = jsonResponse['session']['name']
	print "------- LAST.FM USERNAME -------", lastfmUsername
	print

	# NEED TO WRITE USERNAME TO DB FOR FUTURE REFERENCE

# Function for generating an md5-hashed signature,
# required by last.fm API for an auth session
# takes a token, provided by the last.fm auth sequence
def lastfmSignatureGen(token):
	token = token
	method = 'auth.getsession'

	unsignedParams = "api_key" + API_KEY + \
	"method" + method + \
	"token" + token
	
	unsignedParams.encode('utf-8')
	unsignedParams += SECRET

	m = md5.new()
	m.update(unsignedParams)
	return m.hexdigest()

# Get a given user's recent tracks
def lastfmGetUserRecents(userId, startDate=None, endDate=None):
	userResponse = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user='+userId+'&api_key=070094824815e5b8dc5fcfbc5a2f723f&format=json')
	print
	print "------- LAST.FM USER OBJECT -------"
	pprint(userResponse.json())
	print

