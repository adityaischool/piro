## PACKAGE FOR HITTING THE DROPBOX API

import os, requests, dropbox, json, pymongo
from flask import request, session
# from models import UserDevice,User
from pprint import pprint
from piro import models, db
from models import User, UserDevice

# Instantiate Mongo client
client = pymongo.MongoClient()
mongoDb = client.dropbox
dboxUserFolders = mongoDb.dboxUserFolders

# Dropbox app credentials
API_KEY = 'f2ysiyl8imtvz0g'
SECRET = '6pk00rjwh5s24cr'
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

# Get Dropbox token from db and instantiate Dropbox API object
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
	# Parse Dropbox access token response
	token = decodedResponse['access_token']
	dropboxUserId = decodedResponse['uid']
	# Write the user's Dropbox id & token to the web server db
	try:
		userDevice = UserDevice(userId, 'dropbox', None, dropboxUserId, token, None)
		# Add and commit newly created User db record
		db.session.add(userDevice)
		db.session.commit()
		setDboxApiObj()
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
		print "------- ERROR GETTING FILE METADATA -------", e
		print fileToCheck
		return False

# Create & return a photo metadata object + the photo file path in Dropbox
# so the photo can be downloaded and sent to pi box
def processPhoto(photoFile):
	# Get photo Dropbox path
	photoPath = photoFile.path_lower
	# Create photoMetadata object to add values to later
	photoMetadataObj = {}
	# Create photo metadata object from Dropbox class for easier reference
	photoMetadata = photoFile.media_info.get_metadata()
	# Initialize & set photo metadata values
	photoName = photoFile.name
	photoDropboxId = photoFile.id.split(':')[1]
	photoDimensions = []
	photoTimestamp = ''
	photoLocation = None
	try:
		photoDimensions.append(photoMetadata.dimensions.height)
		photoDimensions.append(photoMetadata.dimensions.width)
	except Exception as e:
		print "------- ERROR GETTING PHOTO DIMENSIONS -------", e
	try:
		photoTimestamp = photoMetadata.time_taken
	except Exception as e:
		print "------- ERROR GETTING PHOTO TIMESTAMP -------", e
	# Check if photo has location data
	if type(photoMetadata.location) != type(None):
		photoLocation = []
		photoLocation.append(photoMetadata.location.latitude)
		photoLocation.append(photoMetadata.location.longitude)
	# Set photoMetadata object key-value pairs
	photoMetadataObj['photoName'] = photoName
	photoMetadataObj['photoPath'] = '../photos/'+photoName
	photoMetadataObj['photoDropboxId'] = photoDropboxId
	photoMetadataObj['photoDimensions'] = photoDimensions
	photoMetadataObj['photoTimestamp'] = photoTimestamp
	photoMetadataObj['photoLocation'] = photoLocation
	return [photoPath, photoMetadataObj]

# Save the user's selected Dropbox folders to sync
def saveUserFolderSelections(folders):
	global dboxUserFolders
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

# Display Mongo contents
def getMongoFolderContents():
	global dboxUserFolders
	userId = session['userId']
	print
	print "------- A LIST OF THE USER'S FOLDERS, SYNC SETTINGS, & CURSORS -------"
	for folder in dboxUserFolders.find({"userId": userId}):
		print
		print "------- Path -------", folder['path']
		print "------- Sync -------", folder['sync']
		print "------- Cursor -----", folder['cursor']
		print 

# Create a new folder to be synced
def createNewSyncedFolder(userId, folder):
	global dboxUserFolders

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
	global dboxUserFolders

	if folder['checked'] == 'unchecked':
		dboxUserFolders.update({'$and': [{'userId': userId}, {'path': folder['path']}]}, {'$set': {'sync': False}})

# Download any new files from user's synced folders
def pollUserSelectedFolders():
	userId = session['userId']
	folderPaths = []
	print "------- A LIST OF THE USER'S FOLDERS SET TO SYNC -------"
	# Get user's Dropbox folders that are set to be synced
	for folder in dboxUserFolders.find({'$and': [{'userId': userId}, {'sync': True}]}):
		print
		print "------- Path -------", folder['path']
		print "------- Sync -------", folder['sync']
		print "------- Cursor -----", folder['cursor']
		print
		folderPaths.append(folder['path'])
	# Get all of the photos from synced folders
	for folderPath in folderPaths:
		getFilesFromFolder(folderPath)

# Update folder objects in Mongo with latest cursors
def updateFolderCursor(userId, folderPath, cursor):
	dboxUserFolders.update({'$and': [{'userId': userId}, {'path': folderPath}]}, {'$set': {'cursor': cursor}})
	# Display updated Mongo contents
	getMongoFolderContents()

# Gets a list of all photo files in the given folder then downloads them
def getFilesFromFolder(folderPath):
	setDboxApiObj()
	userId = session['userId']
	cursor = ''
	files = ''
	# If cursor exists, use cursor to get latest files. Otherwise, get all files from folder
	# Set cursor
	# NEED TO SET CURSORS FOR EACH FOLDER IN WEB SERVER DB AND CHECK CURSOR FROM THERE INSTEAD OF TXT FILE
	try:
		userIdPathQueryResults = dboxUserFolders.find({'$and': [{'userId': userId}, {'path': folder['path']}]})
		for result in userIdPathQueryResults:
			print 
			print "------- USERID/PATH QUERY RESULT -------", result
			print
			cursor = result['cursor']
			files = dbox.files_list_folder_continue(cursor)
			newCursor = files.cursor
			# Now update the folder cursor
			updateFolderCursor(userId, folderPath, newCursor)
	except:
		print
		print "------- CURSOR NOT FOUND!!! GETTING FRESH FOLDER DATA -------"
		print
		# Get all files from specified Dropbox folder if no cursor exists
		files = dbox.files_list_folder(folderPath, include_media_info=True)
		cursor = files.cursor
		updateFolderCursor(userId, folderPath, cursor)
	photoData = []
	# Iterate through files and check if each file is a photo.
	# If file is a photo, create a metadata object for the
	# photo and download the photo 
	for fileToCheck in files.entries:
		if checkIfPhoto(fileToCheck.media_info):
			photoData.append(processPhoto(fileToCheck))
	# Download each photo to temporary storage on web server
	for i in range(len(photoData)):
		downloadFile(photoData[i][0], photoData[i][1]['photoName'])

	# TODO: SEND PHOTO META DATA TO PI BOX - SEND TO SIBLING FOLDER OF PHOTO DOWNLOADS - MATCH BY FILENAME

# Downloads the file at the given path to a specified folder
def downloadFile(filePath, fileName):
	userId = session['userId']
	downloadDirectory = 'dropboxStaging/'+userId+'/'
	# Check if download directory exists; create if it does not exist
	if not os.path.exists(downloadDirectory):
		os.makedirs(downloadDirectory)
	# Download file at from specified Dropbox path to specified local path
	fileMetadata = dbox.files_download_to_file(downloadDirectory+fileName, filePath)
	
	# ADD CODE TO UPLOAD PHOTO FILES & METADATA TO PI BOX - SHOULD BE IN SIBLING FOLDER OF PHOTO METADATA - MATCH BY FILENAME
	# ONCE FILES UPLOADED TO PI BOX, DELETE FROM WEB SERVER
	print
	print fileMetadata

if __name__ == '__main__':
	getUserFolders()

