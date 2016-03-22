# Code to fetch & store long-term access token from Facebook
import json,os,requests,os,datetime,time
from models import UserDevice,User


def fetchLongTermFacebookToken(shortTermToken, userId=None):


	baseUrl = 'https://graph.facebook.com/oauth/access_token?'
	grant_type = 'fb_exchange_token'
	client_id = '979436568777408'
	client_secret = 'd5b9341b3b70e2e20cbf2ef0f4498db4'
	fb_exchange_token = shortTermToken
	redirect_uri = 'http://localhost:5000/connect-facebook'
	ampersand = '&'

	compiledUrl = baseUrl + ampersand + \
	'grant_type=' + grant_type + ampersand + \
	'client_id=' + client_id + ampersand + \
	'client_secret=' + client_secret + ampersand + \
	'fb_exchange_token=' + fb_exchange_token + ampersand + \
	'redirect_uri=' + redirect_uri

	print
	print "------ Compiled URL -----", compiledUrl
	print

	response = requests.get(compiledUrl)
	responseText = response.text
	splitResponse = responseText.split('=')
	token = splitResponse[1]
	print "----- Facebook long-term access token -----", token

	## Need to write long-term token to DB for logged-in user
