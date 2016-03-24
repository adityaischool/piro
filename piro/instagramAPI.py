## PACKAGE FOR AUTHORIZING & HITTING THE INSTAGRAM API


import md5, base64, requests
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint


API_KEY = '710b8ed34bce4cc7894e7991459a4ebb'
SECRET = '23276b9f88c94e30b880a072041aecb3'
# Callback on Last.fm server = 'http://localhost:5000/connect-lastfm'
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
	# Parse Instagram access token response
	token = decodedResponse['access_token']
	instagramUserId = decodedResponse['user']['id']
	instagramUsername = decodedResponse['user']['username']
	# Write the user's Instagram username, id, & token to the web server db
	try:
		userDevice = UserDevice(userId, 'instagram', instagramUsername, instagramUserId, token, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING INSTAGRAM USERID & TOKEN TO DB -------", e
		print