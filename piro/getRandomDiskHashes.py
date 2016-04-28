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
import random, string

# Instantiate Mongo client
client = pymongo.MongoClient()
# Instantiate Mongo data point db
dataPointDb = client.dataPointDb
dataPoints = dataPointDb.dataPoints
# Instantiate Mongo memory disk db
memoryDiskDb = client.memoryDiskDb
memoryDisks = memoryDiskDb.memoryDisks
# Instantiate Mongo compact memory disk db
compactMemoryDiskDb = client.compactMemoryDiskDb
compactMemoryDisks = compactMemoryDiskDb.compactMemoryDisks
storjHashesDb = client.storjHashesDb
storjHashesColl = storjHashesDb.storjHashes

# Given an upper integer range and a list of indices, generate a new random int that is not alreayd in the given list of indices
def generateRandomIndex(rangeUpper, randomIndices):
	index = random.randint(0, rangeUpper)
	if index not in randomIndices:
		return index
	else:
		# Let's get recursive!
		return generateRandomIndex(rangeUpper, randomIndices)

def getRandomDiskHashes(userId):
	numHashesToReturn = 5
	randomIndices = []
	storjHashes = []
	# Hit compactMemoryDisks Mongo collection to get all of a user's compact disks
	cdResults = compactMemoryDisks.find({'userId': userId})
	# Set the upper range on random integer generation for selecting random disks
	# Need to put in code for avoiding disks that have already been chosen recently (and those which have been 'hidden' by the user)
	rangeUpper = cdResults.count() - 1
	# Generate random indices and append to randomIndices list
	for i in range(numHashesToReturn):
		index = generateRandomIndex(rangeUpper, randomIndices)
		randomIndices.append(index)
	# Iterate through the user's compact disks and get the storjHashes for those with matching indices of the randomly generated indices
	count = 0
	for result in cdResults:
		if count in randomIndices:
			storjHashes.append(result['storjHash'])
			if len(storjHashes) == numHashesToReturn:
				break
		count += 1
	print '------- RANDOMLY SELETECTED STORJ HASHES TO BE RETURNED -------'
	for storjHash in storjHashes:
		print storjHash
	return storjHashes

def getRandomDate(userId, numDates):
	print 'user id==========', userId
	numDatesToReturn = numDates
	randomIndices = []
	dates = []
	# Hit compactMemoryDisks Mongo collection to get all of a user's compact disks
	cdResults = compactMemoryDisks.find({'userId': userId})
	print "lenght of resutls=======", cdResults.count()

	# for result in cdResults:
	# 	print '------- CD RESULT:', result
	# Set the upper range on random integer generation for selecting random disks
	# Need to put in code for avoiding disks that have already been chosen recently (and those which have been 'hidden' by the user)
	rangeUpper = cdResults.count() - 1
	print "numDatesToReturn",numDatesToReturn
	print "rangeUpper, randomIndices",rangeUpper, randomIndices
	# Generate random indices and append to randomIndices list
	for i in range(numDatesToReturn):
		index = generateRandomIndex(rangeUpper, randomIndices)
		randomIndices.append(index)
	# Iterate through the user's compact disks and get the dates for those with matching indices of the randomly generated indices
	count = 0
	for result in cdResults:
		if count in randomIndices:
			dates.append(result['diskDate'])
			if len(dates) == numDates:
				break
		count += 1
	print '------- RANDOMLY SELETECTED DATES TO BE RETURNED -------'
	for date in dates:
		print date
	return dates

def getRandomDateStorjHash(userId, numDates):
	print 'user id==========', userId
	numDatesToReturn = numDates
	randomIndices = []
	dates = []
	# Hit compactMemoryDisks Mongo collection to get all of a user's compact disks
	cdResults = compactMemoryDisks.find({'userId': userId})
	print "lenght of resutls=======", cdResults.count()

	# for result in cdResults:
	# 	print '------- CD RESULT:', result
	# Set the upper range on random integer generation for selecting random disks
	# Need to put in code for avoiding disks that have already been chosen recently (and those which have been 'hidden' by the user)
	rangeUpper = cdResults.count() - 1
	print "numDatesToReturn",numDatesToReturn
	print "rangeUpper, randomIndices",rangeUpper, randomIndices
	# Generate random indices and append to randomIndices list
	for i in range(numDatesToReturn):
		index = generateRandomIndex(rangeUpper, randomIndices)
		randomIndices.append(index)
	# Iterate through the user's compact disks and get the dates for those with matching indices of the randomly generated indices
	count = 0
	for result in cdResults:
		if count in randomIndices:
			dates.append(result['diskDate'])
			if len(dates) == numDates:
				break
		count += 1
	print '------- RANDOMLY SELETECTED DATES TO BE RETURNED -------'
	for date in dates:
		print date
	return dates


def getRandomStorjHashes(userId):
	print "inside random storjhashes"
	numHashesToReturn = 5
	randomIndices = []
	storjHashes = []
	# Hit compactMemoryDisks Mongo collection to get all of a user's compact disks
	print "hitting DB for user"
	cdResults = storjHashesColl.find({'userid': userId})
	print "number of hashes found is = ",cdResults.count()
	# Set the upper range on random integer generation for selecting random disks
	# Need to put in code for avoiding disks that have already been chosen recently (and those which have been 'hidden' by the user)
	rangeUpper = cdResults.count() - 1
	#print rangeUpper
	# Generate random indices and append to randomIndices list
	for i in range(numHashesToReturn):
		index = generateRandomIndex(rangeUpper, randomIndices)
		randomIndices.append(index)
	# Iterate through the user's compact disks and get the storjHashes for those with matching indices of the randomly generated indices
	count = 0
	for result in cdResults:
		if count in randomIndices:
			tempdict={'storjBucketHash':result['buckethash'],'storjFileHash':result['filehash'],'date':result['date']}
			if tempdict['storjFileHash'] != "":
				storjHashes.append(tempdict)
			if len(storjHashes) == numHashesToReturn:
				break
		count += 1
	print '------- RANDOMLY SELETECTED STORJ HASHES TO BE RETURNED -------',storjHashes
	for storjHash in storjHashes:
		print storjHash
	return storjHashes