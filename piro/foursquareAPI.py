## PACKAGE FOR AUTHORIZING & HITTING THE FOURSQUARE/SWARM API

import md5, base64, requests
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint



API_KEY = 'OZ44SB02FKZ52UFPU0BNDJIX02ARUFPRLVRKABH0RAR5YVGR'
SECRET = 'KYDDWZEXFQ33WAD0TU2RCFEAFFNHKHL5LQ4I3EJT1UIJ5BLN'
# Callback on Last.fm server = 'http://localhost:5000/connect-lastfm'
AUTH_CALLBACK = 'http://localhost:5000/foursquare-token'
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