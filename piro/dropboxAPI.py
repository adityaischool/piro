## PACKAGE FOR AUTHORIZING & HITTING THE DROPBOX API

import os, requests, dropbox, json, pymongo
from flask import request, session
# from models import UserDevice,User
from pprint import pprint
from piro import models, db
from models import User, UserDevice
from apiCredentials import getAPICredentials
from dataPointBuilder import createDataPoint

# Instantiate Mongo client
client = pymongo.MongoClient()
# Instantiate Mongo data point db
dataPointDb = client.dataPointDb
dataPoints = dataPointDb.dataPoints
# Instantiate Mongo Dropbox db
dropboxDb = client.dropbox
dboxUserFolders = dropboxDb.dboxUserFolders

# Instantiate Dropbox API credentials
API_KEY = getAPICredentials('dropbox')[0]
SECRET = getAPICredentials('dropbox')[1]
AUTH_CALLBACK = 'http://localhost:5000/dropbox-token'

# Instantiate dropbox variable, to be set to Dropbox API object later
dbox = ''

# Check whether or not the user has authorized access to Dropbox or not
def checkIfDropboxAuthorized():
	userId = session['userId']
	# Query UserDevice table Dropbox record for current user
	try:
		userIdQueryResults = UserDevice.query.filter_by(userid=userId, devicetype='dropbox').first()
	except Exception as e:
		print
		print "------- ERROR QUERYING DB FOR DROPBOX USERDEVICE RECORD -------", e
		print
	# Check if user has authorized Dropbox yet before trying to instantiate Dropbox API object
	if (type(userIdQueryResults) != type(None)):
		return [True, userIdQueryResults]
	else:
		print
		print "------- USERDEVICE DROPBOX RECORD FOR USER", userId, "DOES NOT YET EXIST -------"
		print
		return [False, None]

# Get Dropbox token from UserDevice table and instantiate Dropbox API object
def setDboxApiObj():
	global dbox
	dropboxCheckResponse = checkIfDropboxAuthorized()
	if dropboxCheckResponse[0]:
		try:
			userDeviceDict = dropboxCheckResponse[1].__dict__
			userToken = userDeviceDict['accesstoken']
			# Instantiate Dropbox API object
			dbox = dropbox.dropbox.Dropbox(userToken)
		except Exception as e:
			print
			print "------- ERROR INSTANTIATING DROPBOX API OBJECT -------", e
			print

# Return API key (for outside access)
def getAPIKey():
	return API_KEY

# Return API secret (for outside access)
def getSecret():
	return SECRET

# Return API OAuth callback (for outside access)
def getAuthCallback():
	return AUTH_CALLBACK

# Receive OAuth code from client, then get access token from Dropbox API
def codeFlow(code):
	userId = session['userId']
	print
	print "------- DROPBOX OAUTH CODE -------", code
	print
	baseURL = 'https://api.dropboxapi.com/1/oauth2/token'
	# Set params for Dropbox user authorzation request
	params = {'code': code,
	'grant_type': 'authorization_code',
	'client_id': API_KEY,
	'client_secret': SECRET,
	'redirect_uri': AUTH_CALLBACK}
	# Hit Dropbox API for access token
	try:
		response = requests.post(baseURL, data = params)
		decodedResponse = response.json()
		print
		print "------- DROPBOX ACCESS TOKEN RESPONSE -------"
		pprint(decodedResponse)
		print
	except Exception as e:
		print
		print "------- ERROR GETTING DROPBOX ACCESS TOKEN RESPONSE -------", e
		print
	# Update the UserDevice table in the db
	updateUserDeviceTable(decodedResponse, userId)

# Update the UserDevice table in the db
def updateUserDeviceTable(decodedResponse, userId):
	# Parse Dropbox access token response
	accessToken = decodedResponse['access_token']
	dropboxUserId = decodedResponse['uid']
	# Check if user already has a record in UserDevice - update if so, create one if not
	userIdQueryResult = UserDevice.query.filter_by(userid=userId, devicetype='dropbox').first()
	if userIdQueryResult is not None:
		# Update the user's existing record in the UserDevice table
		print
		print '------ THERE IS ALREADY A RECORD FOR THIS USER!!!! -------'
		print
		userIdQueryResult.deviceuserid = dropboxUserId
		userIdQueryResult.accesstoken = accessToken
	else:
		# Create a new db record to be inserted into the UserDevice table
		userDevice = UserDevice(userId, 'dropbox', None, dropboxUserId, accessToken, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
	# Commit the results to the UserDevice table in the db
	try:
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING DROPBOX USERID & TOKEN TO DB -------", e
		print

# Returns a list of all a user's folder names & associated paths
def getUserFolders():
	global dbox
	setDboxApiObj()
	folders = dbox.files_list_folder('', include_media_info=True)
	returnFolders = []
	tempFolder = {}
	print
	print "------- USER'S DROPBOX FOLDERS -------"
	print
	for item in folders.entries:		
		if item.__class__.__name__ == 'FolderMetadata':
			print
			print item
			print item.name
			print item.path_lower
			tempFolder = {
			'name': item.name,
			'path': item.path_lower
			}
			returnFolders.append(tempFolder)
	# Sort folders alphabetically
	sortedFolders = sorted(returnFolders, key=lambda k: k['name'].lower())
	return sortedFolders

# CHeck if given file has photo metadata associated with it
def checkIfPhoto(fileToCheck):
	try:
		if fileToCheck.is_metadata():
			if fileToCheck.get_metadata().__class__.__name__ == 'PhotoMetadata':
				return True
			else:
				return False
		else:
			return False
	except Exception as e:
		print
		print "------- ERROR GETTING FILE METADATA -------", e
		print fileToCheck
		return False

# Create & return a photo metadata object + the photo file path in Dropbox
# so the photo can be downloaded and sent to Storj
def processPhoto(photoFile):
	userId = session['userId']
	# Get photo Dropbox path
	photoPath = photoFile.path_lower
	# Create photoMetadata object to add values to later
	photoMetadataObj = {}
	# Create photo metadata object from Dropbox class for easier reference
	photoMetadata = photoFile.media_info.get_metadata()
	# Initialize & set photo metadata values
	photoName = photoFile.name
	photoDropboxId = photoFile.id.split(':')[1]
	photoDimensions = {}
	photoTimestamp = None
	photoLocation = None
	try:
		photoDimensions['width'] = photoMetadata.dimensions.width
		photoDimensions['height'] = photoMetadata.dimensions.height
	except Exception as e:
		print
		print "------- ERROR GETTING PHOTO DIMENSIONS -------", e
		print
	try:
		photoTimestamp = photoMetadata.time_taken
	except Exception as e:
		print
		print "------- ERROR GETTING PHOTO TIMESTAMP -------", e
		print
	# Check if photo has location data
	if type(photoMetadata.location) != type(None):
		photoLocation = {}
		photoLocation['lat'] = photoMetadata.location.latitude
		photoLocation['long'] = photoMetadata.location.longitude
	# Set photoMetadata object key-value pairs
	photoMetadataObj['photoName'] = photoName
	photoMetadataObj['photoPath'] = '../photos/'+photoName
	photoMetadataObj['photoDropboxId'] = photoDropboxId
	photoMetadataObj['photoDimensions'] = photoDimensions
	photoMetadataObj['photoTimestamp'] = photoTimestamp
	photoMetadataObj['photoLocation'] = photoLocation

	dataPoint = createDataPoint(userId=userId, dataPointType='photo', source='dropbox', sourceData=photoMetadataObj, timestamp=photoTimestamp, coords=photoLocation, fileName=photoName)

	return [photoPath, dataPoint]

# Save the user's selected Dropbox folders to sync
def saveUserFolderSelections(folders):
	folders = json.loads(folders)['data']
	userId = session['userId']
	print
	print "------- USER ID --------", userId
	tempFolder = {}
	print 
	print "------- USER DROPBOX FOLDERS TO SYNC -------", folders
	print
	# Check if document with userId & path exists
	# Create if it doesn't exist, or update if it does
	for folder in folders:
		userIdPathQueryResults = dboxUserFolders.find({'$and': [{'userId': userId}, {'path': folder['path']}]})
		for result in userIdPathQueryResults:
			print 
			print "------- USERID/PATH QUERY RESULT -------", result
			print
		if userIdPathQueryResults.count() == 0:
			createNewSyncedFolder(userId, folder)
		else:
			updateFolderSync(userId, folder)
	# Display updated Mongo contents
	getMongoFolderContents()

# Display Mongo contents for user
def getMongoFolderContents():
	userId = session['userId']
	print
	print "------- A LIST OF THE USER'S FOLDERS, SYNC SETTINGS, & CURSORS -------"
	for folder in dboxUserFolders.find({"userId": userId}):
		print
		print "------- Path -------", folder['path']
		print "------- Sync -------", folder['sync']
		print "------- Cursor -----", folder['cursor']
		print

# Reset user's given folder path cursor in Mongo
# If no folder path given, will reset all folder cursors, so be careful in using this!
# Useful for testing or if user wants to redownload things from a certain folder or everything
def resetUserFolderCursors(path=None):
	userId = session['userId']
	# If folder path given, reset only that folder's cursor
	if path is not None:
		print
		print '------- PATH GIVEN, RESETTING CURSOR AT PATH', path, '-------'
		print
		dboxUserFolders.update({'$and': [{'userId': userId}, {'path': path}]}, {'$set': {'cursor': ''}})
	# If no folder path given, reset cursors for all folders
	else:
		print
		print '------- PATH NOT GIVEN, RESETTING ALL CURSORS -------'
		print
		for result in dboxUserFolders.find({'userId': userId}):
			print "RESULT_------------", result
		dboxUserFolders.update({'userId': userId}, {'$set': {'cursor': ''}}, upsert=False, multi=True)	
	# Verify changes to Mongo
	getMongoFolderContents()

# Create a new folder to be synced
def createNewSyncedFolder(userId, folder):
	# Return if folder is unchecked and not yet tracked
	if folder['checked'] == 'unchecked':
		return
	else:
		tempFolder = {}
		tempFolder['userId'] = userId
		tempFolder['path'] = folder['path']
		tempFolder['sync'] = True
		tempFolder['cursor'] = ''
		dboxUserFolders.insert(tempFolder)

# Update a folder's sync setting, if changed
def updateFolderSync(userId, folder):
	if folder['checked'] == 'unchecked':
		dboxUserFolders.update({'$and': [{'userId': userId}, {'path': folder['path']}]}, {'$set': {'sync': False}})
	elif folder['checked'] == 'checked':
		dboxUserFolders.update({'$and': [{'userId': userId}, {'path': folder['path']}]}, {'$set': {'sync': True}})

# Download any new files from user's synced folders
def pollUserSelectedFolders():
	userId = session['userId']
	setDboxApiObj()
	# ######## REMOVE THIS LINE ONCE TESTING IS DONE!!!! #########
	# dataPoints.remove({'$and': [{'userId': userId}, {'source': 'dropbox'}]})
	# Get a user's selected folder paths to sync
	folderPaths = getUserSelectedFolders(userId)
	# Iterate through each 
	for folderPath in folderPaths['folders']:
		getFilesFromFolder(folderPath)

# Get and return a user's selected folder paths to sync
def getUserSelectedFolders(userId):
	folderPaths = {'folders': []}
	print "------- A LIST OF THE USER'S FOLDERS SET TO SYNC -------"
	# Get user's Dropbox folders that are set to be synced
	for folder in dboxUserFolders.find({'$and': [{'userId': userId}, {'sync': True}]}):
		print
		print "------- Path -------", folder['path']
		print "------- Sync -------", folder['sync']
		print "------- Cursor -----", folder['cursor']
		print
		folderPaths['folders'].append(folder['path'])
	return folderPaths

# Update folder objects in Mongo with latest cursors
def updateFolderCursor(userId, folderPath, cursor):
	dboxUserFolders.update({'$and': [{'userId': userId}, {'path': folderPath}]}, {'$set': {'cursor': cursor}})
	# Display updated Mongo contents
	getMongoFolderContents()

# Get the latest files from the specified folder path using the existing cursor
def existingCursorGetFilesFlow(cursor, userId, folderPath):
	files = dbox.files_list_folder_continue(cursor)
	newCursor = files.cursor
	# Now update the folder cursor
	updateFolderCursor(userId, folderPath, newCursor)
	return files

# Get all files from specified Dropbox folder if no cursor exists or if cursor has been reset to 0
def newCursorGetFilesFlow(userId, folderPath):
	files = dbox.files_list_folder(folderPath, include_media_info=True)
	cursor = files.cursor
	updateFolderCursor(userId, folderPath, cursor)
	return files

# Gets a list of all photo files in the given folder then downloads them
def getFilesFromFolder(folderPath):
	userId = session['userId']
	cursor = ''
	files = ''
	# If cursor exists, use cursor to get latest files. Otherwise, get all files from folder
	try:
		userIdPathQueryResults = dboxUserFolders.find({'$and': [{'userId': userId}, {'path': folderPath}]})
		for result in userIdPathQueryResults:
			print 
			print "------- USERID/PATH QUERY RESULT -------", result
			print
			cursor = result['cursor']
			# Cursor might have been reset to 0, so check if it's 0
			if cursor != '':
				files = existingCursorGetFilesFlow(cursor, userId, folderPath)
				# files = dbox.files_list_folder_continue(cursor)
				# newCursor = files.cursor
				# # Now update the folder cursor
				# updateFolderCursor(userId, folderPath, newCursor)
			elif cursor == '':
				files = newCursorGetFilesFlow(userId, folderPath)
	except:
		print
		print "------- CURSOR NOT FOUND!!! GETTING FRESH FOLDER DATA -------"
		print
		files = newCursorGetFilesFlow(userId, folderPath)
		# # Get all files from specified Dropbox folder if no cursor exists
		# files = dbox.files_list_folder(folderPath, include_media_info=True)
		# cursor = files.cursor
		# updateFolderCursor(userId, folderPath, cursor)
	photoData = []
	dataPointObjects = []
	# Iterate through files and check if each file is a photo.
	# If file is a photo, create a metadata object for the
	# photo and download the photo
	# First check if there are any returned entries - if not, then everything's up-to-date!
	if len(files.entries) > 0:
		for fileToCheck in files.entries:
			try:
				if checkIfPhoto(fileToCheck.media_info):
					photoData.append(processPhoto(fileToCheck))
			except Exception as e:
				print
				print "------- ERROR GETTING FILE MEDIA INFO -------", e
				print
		# Download each photo to temporary storage on web server
		for i in range(len(photoData)):
			if photoData[i][1] != None:
				downloadFile(photoData[i][0], photoData[i][1]['fileName'], photoData[i][1]['adjustedDate'])
				dataPointObjects.append(photoData[i][1])
	else:
		print
		print '------- NO NEW FILES! -------'
		print
	# Temporarily store dataPoints in Mongo
	oldCount = dataPoints.count()
	try:
		dataPoints.insert(dataPointObjects)
	except Exception as e:
		print
		print '------- ERROR WRITING DATA POINTS TO MONGO -------', e
	# Verify that everything went to Mongo successfully
	print "------- A LIST OF THE USER'S FOLDERS, SYNC SETTINGS, & CURSORS -------"
	newCount = dataPoints.count()
	print
	print "------- NUMBER OF DATA POINTS ATTEMPTED TO ADD TO DATAPOINTS DB:", len(dataPointObjects)
	print "------- SUCCESSFULLY ADDED", newCount - oldCount, 'NEW DATA POINTS TO DATAPOINTS DB -------'
	
	# TODO: SEND PHOTO META DATA TO STORJ - WILL MATCH TO PHOTO BY FILENAME

# Downloads the file at the given path to a specified folder
def downloadFile(filePath, fileName, date):
	userId = session['userId']
	downloadDirectory = 'static/staging/'+userId+'/'+date+'/'
	# Check if download directory exists; create if it does not exist
	if not os.path.exists(downloadDirectory):
		os.makedirs(downloadDirectory)
	# Download file at from specified Dropbox path to specified local path
	fileMetadata = dbox.files_download_to_file(downloadDirectory+fileName, filePath)
	
	# ADD CODE TO UPLOAD PHOTO FILES TO STORJ - WILL MATCH TO DATAPOINT BY FILENAME
	# ONCE FILES UPLOADED TO STORJ, DELETE FROM WEB SERVER
	print
	print fileMetadata

if __name__ == '__main__':
	getUserFolders()

