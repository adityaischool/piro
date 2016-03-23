## THIS IS A PACKAGE TO HIT THE DROPBOX API

import os, requests, dropbox
from flask import request
# from models import UserDevice,User
from pprint import pprint

API_KEY = 'f2ysiyl8imtvz0g'
SECRET = '6pk00rjwh5s24cr'
AUTH_CALLBACK = 'http://localhost:5000/dropbox-token'

# DELETE THESE TWO ONCE WE HAVE TOKENS & UIDS BEING SAVED TO WEB SERVER DB
USER_TOKEN = 'nEcQMWpx7EwAAAAAAAB90-lvGwK6WJe3drnlUBW-Le4_cB7lq_yDbcDK90H7GhJn'
USER_ID = '5540488'

# Instantiate Dropbox API object
dbox = dropbox.dropbox.Dropbox(USER_TOKEN)

def getAPIKey():
	return API_KEY

def getSecret():
	return SECRET

def getAuthCallback():
	return AUTH_CALLBACK

# Receive OAuth code from client, then get access token from Dropbox API
def codeFlow(code):
	print "------- DROPBOX OAUTH CODE -------", code

	baseURL = 'https://api.dropboxapi.com/1/oauth2/token'

	params = {'code': code,
	'grant_type': 'authorization_code',
	'client_id': API_KEY,
	'client_secret': SECRET,
	'redirect_uri': AUTH_CALLBACK}

	response = requests.post(baseURL, data = params)
	decodedResponse = response.json()
	pprint(decodedResponse)

	# token = decodedResponse['access_token']
	# userId = decodedResponse['uid']
	# NEED TO STORE DROPBOX ACCESS TOKEN IN WEB SERVER DB

# Returns a list of all a user's folder names & associated paths
def getUserFolders():
	folders = dbox.files_list_folder('', include_media_info=True)

	returnFolders = []
	tempFolder = {}

	print
	print "------- USER'S DROPBOX FOLDERS -------"
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
			# Perhaps auto-check folders with things like 'picture' or 'photo' in the name

	print

	# Sort folders alphabetically
	sortedFolders = sorted(returnFolders, key=lambda k: k['name'].lower())
	return sortedFolders

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

def saveUserFolderSelections(folders):
	pass
	# NEED LOGIC TO SAVE USER'S DROPBOX FOLDER SELECTIONS TO WEB SERVER DB

def pollUserSelectedFolders():
	pass
	# NEED LOGIC TO HIT WEB SERVER DB FOR USER-SELECTED DROPBOX FOLDERS
	# THEN CALL GETFILESFROMFOLDER FUNCTION FOR EACH DROPBOX FOLDER PATH

# Gets a list of all photo files in the given folder then downloads them
def getFilesFromFolder(folderPath):

	cursor = ''
	files = ''

	# If cursor exists, use cursor to get latest files. Otherwise, get all files from folder
	# Set cursor
	# NEED TO SET CURSORS FOR EACH FOLDER IN WEB SERVER DB AND CHECK CURSOR FROM THERE INSTEAD OF TXT FILE
	try:
		with open('Cursor.txt', 'r+') as f:
			cursor = f.read()
			files = dbox.files_list_folder_continue(cursor)
			newCursor = files.cursor
			f.seek(0)
			f.write(newCursor)
			f.close
			# NEED TO UPDATE CURSOR FOR THIS FOLDER IN WEB SERVER DB INSTEAD OF TXT FILE
	except:
		print "------- CURSOR NOT FOUND!!! GETTING FRESH FOLDER DATA -------"
		# Get all files from specified Dropbox folder if no cursor exists
		files = dbox.files_list_folder(folderPath, include_media_info=True)
		cursor = files.cursor
		with open('Cursor.txt', 'w') as f:
			f.write(cursor)
			f.close

	# REMOVE RETURN STATEMENT AFTER USER TOKEN, USER SELECTED FOLDERS, & CURSOR ITEMS SAVED TO WEB SERVER DB ARE SET UP

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
	# NEED CODE TO SEND PHOTO META DATA TO PI BOX - SEND TO SIBLING FOLDER OF PHOTO DOWNLOADS - MATCH BY FILENAME

# Downloads the file at the given path to a specified folder
def downloadFile(filePath, fileName):
	# NEED TO REPLACE THIS WITH PIRO USER ID FROM WEB SERVER (NOT DROPBOX USER ID)
	userId = 'ioa'
	downloadDirectory = 'dropboxStaging/'+userId+'/'
	# Check if download directory exists; create if it does not exist
	if not os.path.exists(downloadDirectory):
		os.makedirs(downloadDirectory)
	# Download file at from specified Dropbox path to specified local path
	fileMetadata = dbox.files_download_to_file(downloadDirectory+fileName, filePath)
	
	# ADD CODE TO UPLOAD PHOTO FILES TO PI BOX - SHOULD BE IN SIBLING FOLDER OF PHOTO METADATA - MATCH BY FILENAME
	print
	print fileMetadata

if __name__ == '__main__':
	# getUserFolders()
	getFilesFromFolder('/camera uploads')
	#getUserFolders()

