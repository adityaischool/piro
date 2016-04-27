from flask import render_template, request, session, redirect, jsonify, Response, escape, url_for
from piro import app, models, db
import urllib2,fitoauth,pymongo
import math, metaclient
import json, os, requests, datetime, time
from flask import Response
#from libraries.python-fitbit-master import foauth2
from libraries import pythonfitbitmaster as pythonfitbitmaster
from libraries.pythonfitbitmaster import foauth2
import fitbit
from models import User, UserDevice
# from piro import hitFitbitApi
from facebookLongTermTokenFetcher import fetchLongTermFacebookToken
import md5, base64
import lastfmAPI, dropboxAPI, instagramAPI, fitbitAPI, foursquareAPI, forecastioAPI
from pprint import pprint
from apiCredentials import setAPICredentials
import diskGenerator, jsonToText, getRandomDiskHashes
import timezoneUtil,writefile
import storjMongo

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
			timezone = usernameQueryResultsDict['timezone']
			session['username'] = username
			session['userId'] = userId
			session['email'] = email
			session['onboarded'] = onboarded
			session['timezone'] = timezone
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

@app.route('/cleardatafrommongo')
def cleardatafrommongo():
	# Instantiate Mongo client
	client = pymongo.MongoClient()
	# Instantiate Mongo data point db
	dataPointDb = client.dataPointDb
	dataPoints = dataPointDb.dataPoints
	# Instantiate Mongo Dropbox db
	dropboxDb = client.dropbox
	dboxUserFolders = dropboxDb.dboxUserFolders
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
		timezone = escape(request.form['timezone']).encode('utf-8')
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
			user = User(userId, username, email, onboarded, timezone, '0000000000000000')
			# Add and commit newly created User db record
			try:
				print "trying to add user"
				db.session.add(user)
				db.session.commit()
				print "added user"
			except Exception as e:
				print "caught exception",e
			# Set session values
			session['username'] = username
			session['userId'] = userId
			session['email'] = email
			session['onboarded'] = onboarded
			session['timezone'] = timezone
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

# An 'API' endpoint for randomly choosing <x> number of compact disks and returning their corresponding Storj hash locations
@app.route('/api/v1/getRandomDisk', methods=['GET'])
def getRandomDisk():
	userId = session['userId']
	# key = request.args.get('key')
	returnResponse = {
	'storjHashes': []
	}
	numDates = 5
	dates = getRandomDates(userId, numDates)
	for date in dates:
		storjHash = storjMongo.getDateHashes(userId, date)
		returnResponse['storjHashes'].append(storjHash)

	return jsonify(returnResponse), 200

@app.route('/getRandomDisk/<userid>', methods=['GET'])
def getRandomDisk(userid1):
	userId = userid1
	# key = request.args.get('key')
	returnResponse = {
	'storjHashes': []
	}
	numDates = 5
	dates = getRandomDates(userId, numDates)
	for date in dates:
		storjHash = storjMongo.getDateHashes(userId, date)
		returnResponse['storjHashes'].append(storjHash)

	return jsonify(returnResponse), 200

def uploadToStorj(userId, date):
	# Remove this once we're calling this function programatically for each user once all of their API data is fetched for the day
	userId = session['userId']

	endpoint = str(userId) + '-' + date
	print "endpoint",endpoint
	#print "hhuuulllasd",url_for('uploadapi')
	#uploadResponse = requests.get(url_for('uploadapi',userfolder=endpoint))
	uploadResponse=uploadapi(endpoint)
	bucketHash = uploadResponse['buckethash']
	fileHash = uploadResponse['filehash']

	storjHashObj = {
	'userId': userId,
	'date': date,
	'storjBucketHash': bucketHash,
	'storjFileHash': fileHash
	}

	response = storjMongo.writeToStorj(storjHashObj)

	print response2

def getRandomDates(userId, numDates):
	randomDates = getRandomDiskHashes.getRandomDate(userId, numDates)
	print 'RANDOMLY GENERATED DATES', randomDates
	return randomDates[0]


# USE THIS FOR TESTING DIFFERENT API FUNCTIONALITY
@app.route('/test-api')
def testAPIButton():

	

	return redirect('service_authorization')

# THIS WILL GET ALL OF THE LOGGED-IN USER'S UNSYNCED DATA FROM EACH SERVICE
@app.route('/get-all')
def getAll():
	userId = session['userId']


	setAPICredentials('fitbit', '227NKT', 'd7a4ececd5e68a5f3f36d64e304fbe25')
	setAPICredentials('foursquare', 'OZ44SB02FKZ52UFPU0BNDJIX02ARUFPRLVRKABH0RAR5YVGR', 'KYDDWZEXFQ33WAD0TU2RCFEAFFNHKHL5LQ4I3EJT1UIJ5BLN')
	setAPICredentials('instagram', '710b8ed34bce4cc7894e7991459a4ebb', '23276b9f88c94e30b880a072041aecb3')
	setAPICredentials('lastfm', '070094824815e5b8dc5fcfbc5a2f723f', '3afa4374733f63f58bd6e5b5962cbbb6')
	setAPICredentials('dropbox', 'f2ysiyl8imtvz0g', '6pk00rjwh5s24cr')
	setAPICredentials('forecastio', '2e70ea34e0ed57fe0de1452024af79ba', '')
	setAPICredentials('spotify', '3a1f5d8baa2149b48d9a8128bcc48c05', 'ce6cc2bd81324433984c3f7ab55155b0')
	try:
		# instagramAPI.resetMostRecentItemId()
		print "instagram"
		instagramAPI.resetMostRecentItemId()
		instagramAPI.getAllNewPosts()
		# foursquareAPI.resetMostRecentItemId()
		print "four square"
		foursquareAPI.resetMostRecentItemId()
		foursquareAPI.getUserCheckinHistory()
		# lastfmAPI.resetMostRecentPlaybackTimestamp()
		print "last fm"
		lastfmAPI.resetMostRecentPlaybackTimestamp()
		lastfmAPI.getUserHistoricalPlays()
		print "dropbox"
		# dropboxAPI.resetUserFolderCursors()
		dropboxAPI.resetUserFolderCursors()
		dropboxAPI.pollUserSelectedFolders()
	except Exception as e:
		print "exception",e
		return redirect('service_authorization')
	# fitbitAPI.resetLastFitbitSyncDate()
	# fitbitAPI.pollRecentFitbitData()
	# timezoneUtil.reverseGeocodeBusiness(37.880208, -122.269341)
	diskGenerator.generateHistoricalDisks(userId)

	memoryDisks = diskGenerator.getUserMemoryDisks(userId)
	diskGenerator.generateCompactDisks(userId, memoryDisks)

	# uploadToStorj(userId, '20160204')

	# diskGenerator.getDataPointsForUserAndDate(userId, '20160403')

	# return redirect('/api/v1/getRandomDisk')

	# forecastioAPI.getWeatherAtTime('37.866795', '-122.262635', '2015-06-20T12:00:00')

	jsonToText.outputTxtFromJson()
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

@app.route('/myfiles', methods=['GET', 'POST'])
def myfiles():
	# userId = session['userId']
	files=metaclient.returnfiles()
	return render_template('myfiles.html', files=files)

@app.route('/testupload', methods=['GET', 'POST'])
def test():
	# userId = session['userId']
	test=metaclient.storefiles("1","newtest")
	return render_template('myfiles.html', files=test)
@app.route('/viewfilesinbucket/<id1>', methods=['GET', 'POST'])
def viewfilesinbucket(id1):
	# userId = session['userId']
	test=metaclient.viewfilesinbucket(id1)
	return render_template('viewbucket.html', mylist=test)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
	# userId = session['userId']
	test=metaclient.getadmindata()
	return render_template('admin.html', mylist=test)

@app.route('/delete/<id1>', methods=['GET', 'POST'])
def delete(id1):
	# userId = session['userId']
	test=metaclient.deletebucket(id1)
	print "deleting",str(test)
	#return render_template('myfiles.html', mylist=test)
	return redirect('/admin')

@app.route('/testbucket', methods=['GET', 'POST'])
def testbucket():
	# userId = session['userId']
	test=metaclient.storefilesinbucket("570c997da2ae841d2ea9798e","newtest")
	return render_template('myfiles.html', files=test)

@app.route('/uploadapi/<userfolder>', methods=['GET', 'POST'])
def uploadapi2(userfolder):
	#this api will return you an object that will then go into mongo
	#userid and folder name should be separated by '-'
	#static/staging/alexjones/20191904
	uid=userfolder.split('-')[0]
	date=userfolder.split('-')[1]
	returnobj=metaclient.storefilesapi(str(uid),str(date))
	print "Object returned from upload api", returnobj
	if returnobj:
		storjMongo.writestorjtomongo(str(uid),str(date),returnobj['buckethash'],returnobj['filehash'])
	#retobj['filehash']=metahash
	#retobj['buckethash']
	return render_template('myfiles.html', files=str(returnobj))

def uploadapi(userfolder):
	#userid and folder name should be separated by '-'
	#static/staging/alexjones/20191904
	uid=userfolder.split('-')[0]
	date=userfolder.split('-')[1]
	returnobj=metaclient.storefilesapi(uid,date)
	print "api returns object", returnobj
	storjMongo.writestorjtomongo
	return returnobj

@app.route('/manageuploads', methods=['GET', 'POST'])
def manageuploads():
	#userid and folder name should be separated by '-'
	#static/staging/alexjones/20191904
	returnobj=metaclient.liststagingfiles()
	print "api returns object", returnobj
	return render_template('uploads.html', mylist=returnobj)


