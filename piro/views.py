from flask import render_template,request,session,redirect,jsonify,Response
from flask import url_for
from piro import app
import urllib2,fitoauth
import math
import json,os,requests,os,datetime,time
from flask import Response
#from libraries.python-fitbit-master import foauth2
from libraries import pythonfitbitmaster as pythonfitbitmaster
from libraries.pythonfitbitmaster import foauth2
import fitbit
from models import UserDevice,User
from piro import hitFitbitApi
from facebookLongTermTokenFetcher import fetchLongTermFacebookToken
import md5, base64
import lastfmAPI, dropboxAPI
from pprint import pprint

@app.route('/', methods=['GET', 'POST'])
def land():
	return render_template("index.html")

@app.route('/connect-facebook', methods=['GET', 'POST'])
def connectFacebook():
	return render_template("connect_facebook.html")

@app.route('/get-facebook-long-term-token')
def getFacebookLongTermToken():
	shortTermToken = request.args.get('token')
	print "Facebook short-term token:", shortTermToken
	print "Fetching long-term token from Facebook..."
	tokenResponse = fetchLongTermFacebookToken(shortTermToken)


@app.route('/requestdata', methods=['GET', 'POST'])
def upload():
	print "requested data"
	if request.method == 'POST':
		macaddress = request.form['macaddress']
	else:
		macaddress=request.args.get("macaddress")
	print "\n requested data by mac address---",macaddress
	try:
		print "sending to parse data"
		js=parsedata(macaddress)
	except Exception as e:
		print e
		return ''
	print "returning response"
	return Response(json.dumps(js))

def parsedata(macaddress):
	userswithMac=User.query.filter_by(userpimac=macaddress).first()
	fdict=userswithMac.__dict__
	print "dict for this mac is", fdict
	userpimac=fdict['userpimac']
	userid=fdict['userid']
	print"mac address translated to this user----",userid
	js=hitFitbitApi.hitFitbitApis(userid)
	print "gonna return",js
	return js

@app.route('/connect-lastfm')
def connectLastFm():
	# api_key = '070094824815e5b8dc5fcfbc5a2f723f'
	api_key = lastfmAPI.getAPIKey()
	print
	print '---------- API KEY ---------', api_key
	callback_redirect = lastfmAPI.getAuthCallback()
	print
	print '---------- CALLBACK REDIRECT --------', callback_redirect
	return redirect('http://last.fm/api/auth/?api_key='+api_key+'&cb='+callback_redirect)
	
@app.route('/lastfm-token')
def lastfmToken():
	token = request.args.get('token')
	print "--------- TOKEN --------- ", token
	lastfmAPI.getUserName(token)
	# NEED TO TRIGGER & SHOW A CONFIRMATION OF SUCCESS FOR THE USER
	return render_template('index.html')

@app.route('/connect-dropbox')
def connectDropbox():
	api_key = dropboxAPI.getAPIKey()
	print
	print '---------- API KEY ---------', api_key
	callback_redirect = dropboxAPI.getAuthCallback()
	print
	print '---------- CALLBACK REDIRECT --------', callback_redirect
	print
	return redirect('https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id='+api_key+'&redirect_uri='+callback_redirect)

@app.route('/dropbox-token')
def dropboxToken():
	code = request.args.get('code')
	print "--------- CODE --------- ", code
	token = dropboxAPI.codeFlow(code)

	return redirect(url_for('dropbox-photo-folder-selection'))

@app.route('/dropbox-photo-folder-selection')
def dropboxPhotoFolderSelection():
	folderData = dropboxAPI.getUserFolders()
	# REDIRECT TO PAGE THAT ALLOWS USER TO SELECT FOLDERS WITH PHOTOS
	return render_template('dropbox_photo_folder_selection.html', folderData=folderData)

@app.route('/dropbox-user-selected-folders', methods=['GET', 'POST'])
def dropboxUserSelectedFolders():
	folders = request.args.get('paths')
	print "------ FOLDERS------", folders


@app.route('/register', methods=['GET', 'POST'])
def register():
	userid=request.args.get("name")
	print "userid is ----- -        ", userid
	foauth2.fitbitoauth(userid)
	return render_template("register.html")

@app.route('/getdata', methods=['GET', 'POST'])
def getdata():
	#user makes get request to our api with param userid=* and auth
	userid=request.args.get("userid")
	try:
		first=UserDevice.query.filter_by(userid=userid).first()
	except Exception as e:
		print e
		return ''
	print "user id is ----",userid
	print "first row is ----"
	print first.__dict__
	fdict=first.__dict__
	accesstoken=fdict['accesstoken']
	refreshtoken=fdict['refreshtoken']
	#aut_cl=Fitbit('994ae27440a52d1f0bb33e8d7e305929','d7a4ececd5e68a5f3f36d64e304fbe25',oauth2=True,access_token=accesstoken,refresh_token=refreshtoken)
	aut_cl=fitbit.Fitbit('227NKT','d7a4ececd5e68a5f3f36d64e304fbe25',oauth2=True,access_token=accesstoken,refresh_token=refreshtoken)
	print "-----------\n-----\n---activities-----\n\n\n"
	print aut_cl.activities(date='2015-12-24')
	return render_template("index.html")

@app.route('/connect-fitbit', methods=['GET', 'POST'])
def fitbithandler():
	#call fitbit oauth code here
	foauth2.fitbitoauth()
	"""z = fitoauth.Fitbit()
	auth_url = z.GetAuthorizationUri()
	print "AAAAuth URL",auth_url
	#accesscode=auth_url['access_code']
	token = z.GetAccessToken(access_code)
	response = z.ApiCall(token, '/1/user/-/activities/log/steps/date/today/7d.json')
	print "response",response
	#foauth2.newauth()"""
	return render_template("index.html")

@app.route('/fitbit2', methods=['GET', 'POST'])
def fitbithandler2():
	#call fitbit oauth code here
	#foauth2.fitbitoauth()
	z = fitoauth.Fitbit()
	auth_url = z.GetAuthorizationUri()
	print "AAAAuth URL",auth_url
	accesscode=auth_url['access_code']
	token = z.GetAccessToken(access_code)
	response = z.ApiCall(token, '/1/user/-/activities/log/steps/date/today/7d.json')
	print "response",response
	#foauth2.newauth()"""
	return render_template("index.html")