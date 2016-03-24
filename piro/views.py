from flask import render_template,request,session,redirect,jsonify,Response, escape
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
import lastfmAPI, dropboxAPI
from pprint import pprint

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
		# First check if username in web server db
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
		# First check if username or email in web server db
		# TODO: ADD LOGIC FOR PASSWORDS LATER
		usernameQueryResults = User.query.filter_by(name=username).first()
		emailQueryResults = User.query.filter_by(email=email).first()
		# Check if username and email are in web server db yet
		# If neither are in web server db, proceed with registration
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
		if (type(usernameQueryResults) == type(None)) and (type(emailQueryResults) == type(None)):
			errors['usernameError'] = True
			return render_template('register.html', errors=errors)
		# If email exists in db already but username doesn't, notify user as such and let them try a different email
		if (type(usernameQueryResults) == type(None)) and (type(emailQueryResults) != type(None)):
			errors['emailError'] = True
			return render_template('register.html', errors=errors)
		# If both username and email exist in db already, notify user as such and give them a login button
		if (type(usernameQueryResults) != type(None)) and (type(emailQueryResults) != type(None)):
			errors['usernameError'] = True
			errors['emailError'] = True
			return render_template('register.html', errors=errors)

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
	# NEED TO TRIGGER & SHOW A CONFIRMATION OF SUCCESS THAT AUTH WAS SUCCCESSFUL

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
		print '---------- API KEY ---------', api_key
		callback_redirect = dropboxAPI.getAuthCallback()
		print
		print '---------- CALLBACK REDIRECT --------', callback_redirect
		print
		return redirect('https://www.dropbox.com/1/oauth2/authorize?response_type=code&client_id='+api_key+'&redirect_uri='+callback_redirect)

@app.route('/dropbox-token')
def dropboxToken():
	code = request.args.get('code')
	print
	print "--------- DROPBOX CODE --------- ", code
	print
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
	# Save user's Dropbox folder selections to web server DB
	dropboxAPI.saveUserFolderSelections(folders)
	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		# Poll selected folders and download photos
		dropboxAPI.pollUserSelectedFolders()
		return redirect('/connect-fitbit')

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

	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		return redirect('/connect-lastfm')

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

	# If user has already been onboarded, return them to the service authorization page
	if session['onboarded']:
		return redirect('/service_authorization')
	# If user has not been fully onboarded, redirect them to the next service authorization option
	# If this is the last service authorization option available on the list, redirect user to the dashboard
	else:
		return redirect('/connect-lastfm')