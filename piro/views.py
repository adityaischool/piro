from flask import render_template, request, session, redirect, jsonify, Response, escape
from flask import url_for
from piro import app, models, db
import urllib2,fitoauth
import math
import json,os,requests,os,datetime,time
from flask import Response
#from libraries.python-fitbit-master import foauth2
from libraries import pythonfitbitmaster as pythonfitbitmaster
from libraries.pythonfitbitmaster import foauth2
import fitbit
from models import User, UserDevice
from piro import hitFitbitApi
from facebookLongTermTokenFetcher import fetchLongTermFacebookToken
import md5, base64
import lastfmAPI, dropboxAPI, instagramAPI, fitbitAPI, foursquareAPI, forecastioAPI
from pprint import pprint
from apiCredentials import setAPICredentials

@app.route('/')
@app.route('/index')
def land():
	username = ''
	if 'username' in session:
		username = escape(session['username'])
		onboarded = session['onboarded']
		if onboarded:
			return redirect('/dashboard')
		else:
			return redirect('/service_authorization')
	else:
		return render_template('login.html', errors=None)

@app.route('/service_authorization')
def serviceAuthorization():
	username = escape(session['username'])
	userId = session['userId']
	return render_template('service_authorization.html', name=username)

@app.route('/dashboard')
def dashboard():
	username = escape(session['username'])
	userId = session['userId']
	return render_template('dashboard.html', name=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
	errors = {}
	if request.method=='POST':
		username = request.form['username']
		# First check if username in the User table
		# TODO: ADD LOGIC FOR PASSWORDS
		usernameQueryResults = User.query.filter_by(name=username).first()
		if (type(usernameQueryResults) != type(None)):
			usernameQueryResultsDict = usernameQueryResults.__dict__
			print
			print "------- USER DB RECORD -------", usernameQueryResultsDict
			print
			# If username in db, set session object with username and userId
			username = usernameQueryResultsDict['name']
			userId = usernameQueryResultsDict['userid']
			email = usernameQueryResultsDict['email']
			onboarded = usernameQueryResultsDict['onboarded']
			session['username'] = username
			session['userId'] = userId
			session['email'] = email
			session['onboarded'] = onboarded
			return redirect('/index')
		# If username not in db, notify user that the username does not exist - let them reenter
		else:
			errors['usernameError'] = True
			return render_template('login.html', errors=errors)

# Generates an md5 hash from the user name, email, & a random number
def generateUserId(userName, email):
	random = str(os.urandom(24))
	m = md5.new()
	m.update(userName+email+random)
	print "------- HASHED USER ID -------", m.hexdigest()
	return m.hexdigest()

# Logout handler
@app.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('email', None)
	session.pop('userId', None)
	return redirect('index')

# Route user to registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
	# userid=request.args.get("name")
	# print "userid is ----- -        ", userid
	# foauth2.fitbitoauth(userid)
	return render_template("register.html", errors=None)

# Handler for submitting user registration info
@app.route('/submit-registration', methods=['GET', 'POST'])
def submitRegistration():
	errors = {}
	if request.method=='POST':
		username = escape(request.form['username']).encode('utf-8')
		email = escape(request.form['email']).encode('utf-8')
		userId = ''
		user = ''
		onboarded = False
		# First check if username or email in the User table
		# TODO: ADD LOGIC FOR PASSWORDS LATER
		usernameQueryResults = User.query.filter_by(name=username).first()
		emailQueryResults = User.query.filter_by(email=email).first()
		# Check if username and email are in the User table yet
		# If neither are in the User table, proceed with registration
		if (type(usernameQueryResults) == type(None)) and (type(emailQueryResults) == type(None)):
			print
			print '------- USERNAME AND EMAIL DO NOT YET EXIST IN DB ------'
			print '------- WRITING USERNAME AND EMAIL TO DB -------'
			print
			# Generate unique userId
			userId = generateUserId(username, email)
			# Create User db record

			# TODO: GET USER'S ACTUAL PI MAC ADDRESSS
			user = User(userId, username, email, onboarded, '0000000000000000')
			# Add and commit newly created User db record
			db.session.add(user)
			db.session.commit()
			# Set session values
			session['username'] = username
			session['userId'] = userId
			session['email'] = email
			session['onboarded'] = onboarded
			# Finally, redirect user to index
			return redirect('/index')
		# If username exists in db already but email doesn't, notify user as such and let them try a new username
		elif (type(usernameQueryResults) == type(None)) and (type(emailQueryResults) == type(None)):
			errors['usernameError'] = True
			return render_template('register.html', errors=errors)
		# If email exists in db already but username doesn't, notify user as such and let them try a different email
		elif (type(usernameQueryResults) == type(None)) and (type(emailQueryResults) != type(None)):
			errors['emailError'] = True
			return render_template('register.html', errors=errors)
		# If both username and email exist in db already, notify user as such and give them a login button
		elif (type(usernameQueryResults) != type(None)) and (type(emailQueryResults) != type(None)):
			errors['usernameError'] = True
			errors['emailError'] = True
			return render_template('register.html', errors=errors)

# USE THIS FOR TESTING DIFFERENT API FUNCTIONALITY
@app.route('/test-api')
def testAPIButton():
	# instagramAPI.getAllNewPosts()

	# foursquareAPI.resetMostRecentItemId()
	# foursquareAPI.getUserCheckinHistory()

	# lastfmAPI.resetMostRecentPlaybackTimestamp()
	# lastfmAPI.getUserHistoricalPlays()

	# dropboxAPI.pollUserSelectedFolders()

	# fitbitAPI.resetLastFitbitSyncDate()
	# fitbitAPI.pollRecentFitbitData()

	# setAPICredentials('fitbit', '227NKT', 'd7a4ececd5e68a5f3f36d64e304fbe25')
	# setAPICredentials('foursquare', 'OZ44SB02FKZ52UFPU0BNDJIX02ARUFPRLVRKABH0RAR5YVGR', 'KYDDWZEXFQ33WAD0TU2RCFEAFFNHKHL5LQ4I3EJT1UIJ5BLN')
	# setAPICredentials('instagram', '710b8ed34bce4cc7894e7991459a4ebb', '23276b9f88c94e30b880a072041aecb3')
	# setAPICredentials('lastfm', '070094824815e5b8dc5fcfbc5a2f723f', '3afa4374733f63f58bd6e5b5962cbbb6')
	# setAPICredentials('dropbox', 'f2ysiyl8imtvz0g', '6pk00rjwh5s24cr')
	# setAPICredentials('forecastio', '2e70ea34e0ed57fe0de1452024af79ba', '')

	forecastioAPI.getWeatherAtTime('37.866795', '-122.262635', '2015-06-20T12:00:00')
	return redirect('service_authorization')

# A function to be called to poll all of user's authorized apps/services
# Set this up on a Cron??? - maybe set this up to instead update all users for a given service at once instead of all services for a given user? Would this cause rate limit issues?
def pollAllUserAuthorizedServices():
	# TODO: PUT IN LOGIC TO ONLY HIT SERVICES THAT A USER HAS AUTHORIZED
	instagramAPI.getAllNewPosts()
	foursquareAPI.getUserCheckinHistory()
	dropboxAPI.pollUserSelectedFolders()
	lastfmAPI.getUserRecentPlays()

@app.route('/connect-facebook', methods=['GET', 'POST'])
def connectFacebook():
	return render_template("connect_facebook.html")

@app.route('/get-facebook-long-term-token')
def getFacebookLongTermToken():
	shortTermToken = request.args.get('token')
	print "Facebook short-term token:", shortTermToken
	print "Fetching long-term token from Facebook..."
	tokenResponse = fetchLongTermFacebookToken(shortTermToken)

@app.route('/connect-instagram')
def connectInstagram():
	client_id = instagramAPI.getAPIKey()
	print
	print '---------- INSTAGRAM CLIENT ID ---------', client_id
	redirect_uri = instagramAPI.getAuthCallback()
	print
	print '---------- INSTAGRAM CALLBACK REDIRECT URI --------', redirect_uri
	return redirect('https://api.instagram.com/oauth/authorize/?client_id='+client_id+'&redirect_uri='+redirect_uri+'&response_type=code')

@app.route('/instagram-token')
def instagramToken():
	code = request.args.get('code')
	instagramAPI.codeFlow(code)
	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		#changeUserOnboardedStatus()
		return redirect('/connect-dropbox')

@app.route('/connect-foursquare')
def foursquareConnect():
	client_id = foursquareAPI.getAPIKey()
	redirect_uri = foursquareAPI.getAuthCallback()
	return redirect('https://foursquare.com/oauth2/authenticate?client_id='+client_id+'&response_type=code&redirect_uri='+redirect_uri)

@app.route('/foursquare-token')
def foursquareToken():
	code = request.args.get('code')
	foursquareAPI.codeFlow(code)
	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		#changeUserOnboardedStatus()
		return redirect('/connect-fitbit')

@app.route('/connect-lastfm')
def connectLastFm():
	api_key = lastfmAPI.getAPIKey()
	callback_redirect = lastfmAPI.getAuthCallback()
	return redirect('http://last.fm/api/auth/?api_key='+api_key+'&cb='+callback_redirect)
	
@app.route('/lastfm-token')
def lastfmToken():
	token = request.args.get('token')
	print "--------- TOKEN --------- ", token
	lastfmAPI.getUserName(token)
	# NEED TO TRIGGER & SHOW A CONFIRMATION OF SUCCESS THAT AUTH WAS SUCCCESSFUL
	lastfmAPI.getUserHistoricalPlays()

	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		# TODO: UNCOMMENT THIS WHEN DONE MAKING CHANGES TO SERVICE AUTH FLOW
		#changeUserOnboardedStatus()
		return redirect('/dashboard')

# Once a user is finished onboarding (i.e., they have gone through all of the service authorization options),
# change their onboarded status in the db to True
def changeUserOnboardedStatus():
	userId = session['userId']
	user = User.query.filter_by(userid=userId).first()
	user.onboarded = True
	db.session.commit()
	#userIdQueryResultsDict = userIdQueryResults.__dict__


@app.route('/connect-dropbox')
def connectDropbox():
	api_key = ''
	callback_redirect = ''
	# First check if Dropbox has already been authorized by user
	dropboxCheck = dropboxAPI.checkIfDropboxAuthorized()
	# If Dropbox already authorized, redirect to Dropbox photo folder selection page
	if dropboxCheck[0]:
		return redirect('/dropbox-photo-folder-selection')
	# If Dropbox not yet authorized, begin authorization flow
	else:
		api_key = dropboxAPI.getAPIKey()
		print
		print '---------- DROPBOX API KEY ---------', api_key
		callback_redirect = dropboxAPI.getAuthCallback()
		print
		print '---------- DROPBOX CALLBACK REDIRECT --------', callback_redirect
		print
		return redirect('https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id='+api_key+'&redirect_uri='+callback_redirect)

@app.route('/dropbox-token')
def dropboxToken():
	code = request.args.get('code')
	dropboxAPI.codeFlow(code)
	return redirect('/dropbox-photo-folder-selection')

@app.route('/dropbox-photo-folder-selection')
def dropboxPhotoFolderSelection():
	username = escape(session['username'])
	dropboxAPI.setDboxApiObj()
	folderData = dropboxAPI.getUserFolders()
	# REDIRECT TO PAGE THAT ALLOWS USER TO SELECT FOLDERS WITH PHOTOS
	return render_template('dropbox_photo_folder_selection.html', name=username, folderData=folderData)

@app.route('/dropbox-user-selected-folders', methods=['GET', 'POST'])
def dropboxUserSelectedFolders():
	# Get folders from GET request
	folders = request.args.get('paths')
	# Save user's Dropbox folder selections to Mongo
	dropboxAPI.saveUserFolderSelections(folders)
	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		# Poll selected folders and download photos
		dropboxAPI.pollUserSelectedFolders()
		return redirect('/connect-foursquare')

# Only used for determining which folders to auto-check in the Dropbox folder selection screen
@app.route('/get-dropbox-user-selected-folders')
def getDropboxUserSelectedFolders():
	userId = session['userId']
	folderPaths = dropboxAPI.getUserSelectedFolders(userId)
	print
	print '------- FOLDER PATHS TO BE AUTO-CHECKED -------', folderPaths
	print
	return jsonify(folderPaths)

@app.route('/connect-fitbit', methods=['GET', 'POST'])
def connectFitbit():
	# userId = session['userId']
	client_id = fitbitAPI.getAPIKey()
	print
	print '---------- FITBIT CLIENT ID ---------', client_id
	redirect_uri = fitbitAPI.getAuthCallback()
	print
	print '---------- FITBIT CALLBACK REDIRECT URI --------', redirect_uri
	return redirect('https://www.fitbit.com/oauth2/authorize?response_type=code&client_id='+client_id+'&redirect_uri='+redirect_uri+'&scope=activity%20heartrate%20location%20nutrition%20profile%20sleep')

@app.route('/fitbit-token')
def fitbitToken():
	code = request.args.get('code')
	fitbitAPI.codeFlow(code)

	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		return redirect('/dashboard')
		return redirect('/connect-lastfm')

# @app.route('/fitbit2', methods=['GET', 'POST'])
# def fitbithandler2():
# 	#call fitbit oauth code here
# 	#foauth2.fitbitoauth()
# 	z = fitoauth.Fitbit()
# 	auth_url = z.GetAuthorizationUri()
# 	print "AAAAuth URL",auth_url
# 	accesscode=auth_url['access_code']
# 	token = z.GetAccessToken(access_code)
# 	response = z.ApiCall(token, '/1/user/-/activities/log/steps/date/today/7d.json')
# 	print "response",response
# 	#foauth2.newauth()"""

# 	# If user has already been onboarded, return them to the service authorization page
# 	if session['onboarded']:
# 		return redirect('/service_authorization')
# 	# If user has not been fully onboarded, redirect them to the next service authorization option
# 	# If this is the last service authorization option available on the list, redirect user to the dashboard
# 	else:
# 		return redirect('/connect-lastfm')

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
	return redirect('/dashboard')
