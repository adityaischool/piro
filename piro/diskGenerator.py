## PACKAGE FOR GENERATING 'MEMORY DISKS' FROM DATA POINTS

import pymongo
from flask import request, session
from piro import models, db
from models import UserDevice,User
from pprint import pprint
from datetime import datetime
from apiCredentials import getAPICredentials
from forecastioAPI import getWeatherAtTime
from timezoneUtil import utcFromDatetime

# Instantiate Mongo client
client = pymongo.MongoClient()
# Instantiate Mongo data point db
dataPointDb = client.dataPointDb
dataPoints = dataPointDb.dataPoints
# Instantiate Mongo memory disk db
memoryDiskDb = client.memoryDiskDb
memoryDisks = memoryDiskDb.memoryDisks

def generateHistoricalDisks(userId):
	newestDiskDate = ''

	mongoQueryResults = memoryDisks.find({'userId': userId}).sort("diskId", pymongo.DESCENDING)

	for disk in mongoQueryResults:
		newestDiskDate = disk['date']
		break




# Query Mongo for all data points for a given user on a given date
def getDataPointsForUserAndDate(userId, diskDate):
	dataPointIds = []
	locations = []
	weather = None

	mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}]}).sort("localizedTimestamp", pymongo.ASCENDING)

	for result in mongoQueryResults:
		print
		print result['dataPointType']
		print result['source']
		print result['localizedTimestamp']
		try:
			print result['businessName']
		except:
			print 'no business name'
		print result['placeName']

		if result['dataPointType'] != 'song':
			dataPointIds.append(result['dataPointId'])

		if result['placeName'] != None and result['placeName'] not in locations:
			locations.append(result['placeName'])

			# TODO: ADD CODE TO GET WEATHER DATA

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

	memoryDisk = {
		'diskId': diskId, # a unique id for this 'disk' - in the format 'YYYYMMDDXXX' (will increment the 'XXX' number each time an additional 'disk' is created for the date)
		'emotions': [], # a user-defined list of no more than 2 emotions selected from the user's own defined set of emotions
		'displayStatus': 'on', # 'on', 'off', or 'snooze', defaults to 'on'
		'snoozeDate': 0, # a future unix timestamp when this 'disk' becomes 'on' again
		'locations': locations, # a list of all of the resolved locations from the data points in this 'disk'
		'date': diskDate, # date string in format YYYYMMDD for this 'disk' - actually encompasses the period 4am-3:59am
		'dataPointIds': dataPointIds, # a list of all data points, excluding songs, associated with this 'disk' - used for reference
		'name': name, # the user-assigned name for this 'disk' - defaults to mode of locations
		'themeSongs': themeSongs, # a data point id of a user-selected song from the songs played that day, defaults to either the most-played song from that day or a random song from the mode
		'weather': weather, # a weather summary object for the date & location of this 'disk', if available
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

def findThemeSongs(userId, diskDate):
	mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}, {'dataPointType': 'song'}]})

	playbackHistogram = {}

	themeSongs = []

	for result in mongoQueryResults:
		key = result['sourceData']['trackArtist']+result['sourceData']['trackName']
		playcount = playbackHistogram.get(key, 0)
		if playcount == 0:
			themeSongs.append(result['dataPointId'])
			# TODO: ADD CODE TO RESOLVE SONG ON SPOTIFY SEARCH API & GET SPOTIFY PREVIEW STREAM URL
		playbackHistogram[key] = playcount + 1

	print
	print '------- SONG PLAYBACK HISTOGRAM -------'
	for key in playbackHistogram:
		print
		print key, playbackHistogram[key]

	return themeSongs

def findLocationMode(userId, diskDate):
	mongoQueryResults = dataPoints.find({'$and': [{'userId': userId}, {'adjustedDate': diskDate}]})

	placeHistogram = {}

	locationMode = ''
	maxLocationMode = 0

	for result in mongoQueryResults:
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