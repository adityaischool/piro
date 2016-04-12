## PACKAGE FOR GENERATING 'MEMORY DISKS' FROM DATA POINTS

import pymongo
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint
from datetime import datetime, date, timedelta
from apiCredentials import getAPICredentials
from forecastioAPI import getPlaceDateWeatherSummary
from timezoneUtil import utcFromDatetime, datetimeObjFromYYYYMMDD, localizedDatetimeObjFromYYYYMMDD, yyyymmddFromDatetimeObj, geocode, localizedDatetimeObjToReadableDate
from spotifyAPI import getSpotifyPreviewAndImgUrls

# Instantiate Mongo client
client = pymongo.MongoClient()
# Instantiate Mongo data point db
dataPointDb = client.dataPointDb
dataPoints = dataPointDb.dataPoints
# Instantiate Mongo memory disk db
memoryDiskDb = client.memoryDiskDb
memoryDisks = memoryDiskDb.memoryDisks


def generateHistoricalDisks(userId):
	# memoryDisks.remove({})

	# Iterate through existing disks in Mongo to find the newest disk date as a starting point
	newestDiskDate = ''
	mongoQueryResults = memoryDisks.find({'userId': userId}).sort("date", pymongo.DESCENDING)
	oldCount = mongoQueryResults.count()

	# for disk in mongoQueryResults:
	# 	if int(disk['date']) >= 20160401:
	# 		print
	# 		print '======== DISK FOUND WITH DATE >= 20160404'
	# 		print 'DISK DATE:',  int(disk['date'])
	# 		print 'REMOVING DISK', disk, '......'
	# 		memoryDisks.remove({'diskId': disk['diskId']})
	# newCount = mongoQueryResults.count()
	# print '------ OLD COUNT -------', oldCount
	# print '------ NEW COUNT -------', newCount
	# print '------ REMOVED', (oldCount - newCount), 'DISKS -------'
	# return


	if mongoQueryResults.count() > 0:
		print '------ MEMORY DISKS FOUND! ------'
		for disk in mongoQueryResults:
			# Convert newestDiskDate to date object for easy incrementing & comparison
			newestDiskDate = datetime.utcfromtimestamp(utcFromDatetime(datetimeObjFromYYYYMMDD(disk['date'])))
			# Increment newestDiskDate by 1 so we're not regenerating the newest disk on record)
			newestDiskDate += timedelta(1)
			break
	# If user has no disks in Mongo (i.e., they're brand new to the product), use the oldest data point as a starting date
	elif mongoQueryResults.count() == 0:
		print '------ NO MEMORY DISKS FOUND! ------'
		mongoQueryResults = dataPoints.find({'userId': userId}).limit(1)
		for dataPoint in mongoQueryResults:
			# Convert newestDiskDate to date object for easy incrementing & comparison
			newestDiskDate = datetime.utcfromtimestamp(utcFromDatetime(datetimeObjFromYYYYMMDD(dataPoint['adjustedDate'])))
			break
	# Get stop date (1 week ago) as a string formatted as YYYYMMDD for comparison to disk dates as we create them
	# This stop date is set to 7 days so we give the user a week before auto-generating disks
	stopDate = datetime.today() - timedelta(1)
	# Reset stopDate's hours, minutes, seconds, & microseconds to 0
	stopDate = datetime(stopDate.year, stopDate.month, stopDate.day, 0, 0, 0, 0)
	# Iterate through each date since the newestDiskDate & create disks for each date
	# Break loop once newestDiskDate equals stopDate
	while True:
		print
		print '------- NEWEST DISK DATE -------', newestDiskDate
		print '------- STOP DATE -------', stopDate
		print
		if newestDiskDate == stopDate:
			newCount = memoryDisks.find({'userId': userId}).count()
			print
			print '------- NEWEST DISK DATE', newestDiskDate, 'EQUALS STOP DATE', stopDate, '-------'
			print '------- BREAKING LOOP -------'
			print '------- MEMORYDISKS COLLECTION SIZE BEFORE:', oldCount
			print '------- MEMORYDISKS COLLECTION SIZE AFTER:', newCount
			print '------- ADDED', newCount - oldCount, 'NEW MEMORY DISKS -------'
			print
			break
		diskDate = yyyymmddFromDatetimeObj(newestDiskDate)
		print
		print '------- GENERATING MEMORY DISK FOR DATE', diskDate, '-------'
		# Create new disk
		newDisk = getDataPointsForUserAndDate(userId, diskDate)
		# Insert newly created disk into Mongo if a new disk was created
		if newDisk != None:
			print 'DISK CREATED!'
			memoryDisks.insert(newDisk)
		# Increment newestDiskDate
		newestDiskDate += timedelta(1)


# Query Mongo for all data points for a given user on a given date
def getDataPointsForUserAndDate(userId, diskDate):
	dataPointIds = []
	locations = []
	weather = []

	# If there is at least one photo for the given date, generate a memory disk using the datam otherwise return None
	numPhotos = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}, {'dataPointType': 'photo'}]}).count()
	print
	print 'NUM PHOTOS =====', numPhotos
	if numPhotos == 0:
		return None

	mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}]}).sort("localizedTimestamp", pymongo.ASCENDING)

	for result in mongoQueryResults:
		if result['dataPointType'] != 'song':
			dataPointIds.append(result['dataPointId'])
		# Add all unique locations to the disk's locations list
		if result['placeName'] != None and result['placeName'] not in locations:
			locations.append(result['placeName'])

	# Get daily summary of weather for each location
	for location in locations:
		latitude = ''
		longitude = ''
		rawTimestamp = ''
		timestamp = ''
		locationWeather = {
		'location': location
		}
		locationCoords = geocode(location)
		if locationCoords != None:
			latitude = locationCoords['latitude']
			longitude = locationCoords['longitude']

			rawTimestamp = utcFromDatetime(datetimeObjFromYYYYMMDD(diskDate))
			# Convert rawTimestamp to string & remove decimal
			timestamp = str(rawTimestamp).split('.')[0]
			locationWeather['weather'] = getPlaceDateWeatherSummary(latitude, longitude, timestamp)
			weather.append(locationWeather)
		else:
			locationWeather['weather'] = None

		

	themeSongs = findThemeSongs(userId, diskDate)

	newDisk = generateDisk(userId, diskDate, dataPointIds=dataPointIds, locations=locations, themeSongs=themeSongs, weather=weather)
	print
	print '------- NEWLY GENERATED DISK -------'
	pprint(newDisk)
	return newDisk


def generateDisk(userId, diskDate, dataPointIds, locations, themeSongs, weather):
	creationTimestamp = utcFromDatetime(datetime.now())
	diskId = generateDiskId(userId, diskDate)

	name = findLocationMode(userId, diskDate)
	# If no locations exist for disk, use the plain-english representation of the disk's date as its default name
	if name == None:
		readableDate = localizedDatetimeObjToReadableDate(localizedDatetimeObjFromYYYYMMDD(diskDate))
		name = readableDate

	memoryDisk = {
		'userId': userId,
		'diskId': diskId, # a unique id for this 'disk' - in the format 'YYYYMMDDXXX' (will increment the 'XXX' number each time an additional 'disk' is created for the date)
		'emotions': [], # a user-defined list of no more than 2 emotions selected from the user's own defined set of emotions
		'people': [], # a user-defined list of people in this disk
		'notes': [], # a user-defined list of notes/annotations
		'displayStatus': 'on', # 'on', 'off', or 'snooze', defaults to 'on'
		'snoozeDate': 0, # a future unix timestamp when this 'disk' becomes 'on' again
		'locations': locations, # a list of all of the resolved locations from the data points in this 'disk'
		'date': diskDate, # date string in format YYYYMMDD for this 'disk' - actually encompasses the period 4am-3:59am
		'dataPointIds': dataPointIds, # a list of all data points, excluding songs, associated with this 'disk' - used for reference
		'name': name, # the user-assigned name for this 'disk' - defaults to mode of locations
		'themeSongs': themeSongs, # a data point id of a user-selected song from the songs played that day, defaults to either the most-played song from that day or a random song from the mode
		'weather': weather, # a weather summary object for each of the locations of this 'disk', if available
		'diskUserEngagement': {
			'diskModified': False, # Boolean of whether or not a user has ever modified this 'disk'
			'diskLastModified': 0, # a unix timestamp of when this 'disk' was last modified by user
			'diskTimesModified': 0, # how many times this 'disk' has been modified by user
			'diskLastViewed': 0, # a unix timestamp of when this 'disk' was last viewed (not played)
			'diskTotalViews': 0, # how many times this 'disk' has ever been viewed
			'diskLastPlayed': 0, # a unix timestamp of the last time this 'disk' was played to completion
			'diskTotalPlays': 0, # how many times this 'disk' was played to completion
			'diskTotalSkips': 0, # how many times this 'disk' was skipped without being viewed
		},
		'creationTimestamp': creationTimestamp # a unix timestamp of when this disk was first created
	}

	return memoryDisk

# Returns a user's top-10 most-played songs for a given date, sorted by play count
def findThemeSongs(userId, diskDate):
	themeSongLimit = 20

	count = mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'dataPointType': 'song'}]}).count()
	mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}, {'dataPointType': 'song'}]})

	playbackHistogram = {}
	themeSongs = []

	for result in mongoQueryResults:
		#print result['sourceData']['trackArtist'], result['sourceData']['trackName']
		tempSong = {}
		dataPointId = result['dataPointId']
		artist = result['sourceData']['trackArtist']
		track = result['sourceData']['trackName']
		tempSong['dataPointId'] = dataPointId
		tempSong['artist'] = artist.encode('utf-8')
		tempSong['track'] = track.encode('utf-8')
		# Concatenate with a string in the middle that is highly unlikely to ever appear in a song
		# We'll split on this string later for sorting the tracks
		key = artist + '^$%&#^$%&#' + track
		playcount = playbackHistogram.get(key, 0)
		if playcount == 0:
			spotifyObj = getSpotifyPreviewAndImgUrls(artist, track)
			if spotifyObj != None:
				tempSong['spotifyPreviewUrl'] = spotifyObj['previewUrl']
				tempSong['spotifyImgUrl'] = spotifyObj['imgUrl']
				themeSongs.append(tempSong)
		playbackHistogram[key] = playcount + 1

	processedSongs = []
	for key in playbackHistogram:
		print '----------- KEY:', key.encode('utf-8')
		split = key.split('^$%&#^$%&#')
		artist = split[0].encode('utf-8')
		track = split[1].encode('utf-8')
		print '------ ARTIST:', artist
		print '------ TRACK:', track
		for song in themeSongs:
			if song['dataPointId'] not in processedSongs and song['artist'] == artist and song['track'] == track:
				song['playCount'] = playbackHistogram[key]
				processedSongs.append(song['dataPointId'])
	for song in themeSongs:
		print
		print song
	themeSongsSorted = sorted(themeSongs, key=lambda k: k['playCount'], reverse=True)[:themeSongLimit]
	return themeSongsSorted

def findLocationMode(userId, diskDate):
	mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}]})

	placeHistogram = {}

	locationMode = None
	maxLocationMode = 0

	for result in mongoQueryResults:
		key = ''
		# print result
		if result['placeName'] != None:
			key = result['placeName']
			placeCount = placeHistogram.get(key, 0)
			placeHistogram[key] = placeCount + 1
			if placeHistogram[key] > maxLocationMode:
				maxLocationMode = placeHistogram[key]
				locationMode = result['placeName']

	return locationMode

def generateDiskId(userId, diskDate):
	mongoQueryResults = memoryDisks.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}]}).sort("diskId", pymongo.DESCENDING)

	if mongoQueryResults.count() > 0:
		for disk in mongoQueryResults:
			mostRecentDiskId = disk['diskId']
			mostRecentDiskIdNumber = int(mostRecentDiskId[8:])
			incrementedDiskIdNumber = mostRecentDiskIdNumber + 1
			formattedIncremenetedDiskIdNumber = str(incrementedDiskIdNumber)
			if incrementedDiskIdNumber < 100:
				formattedIncremenetedDiskIdNumber = '0' + formattedIncremenetedDiskIdNumber
			if incrementedDiskIdNumber < 10:
				formattedIncremenetedDiskIdNumber = '0' + formattedIncremenetedDiskIdNumber
			newDiskId = diskDate + formattedIncremenetedDiskIdNumber
			print 
			print '------- MOST RECENT DISK ID -------', mostRecentDiskId
			print '------- NEWLY GENERATED DISK ID -------', newDiskId

			return newDiskId
	else:
		newDiskId = diskDate + '001'
		print 
		print '------- THIS IS THE FIRST DISK FOR THE DATE',  diskDate, '-------'
		print '------- NEWLY GENERATED DISK ID -------', newDiskId

		return newDiskId


if __name__ == '__main__':
	getDataPointsForUserAndDate(userId, '20160403')