## PACKAGE FOR WRITING STORJ HASHES TO MONGO

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
# Instantiate Mongo compact Storj Hahses db
storjHashesDb = client.storjHashesDb
storjHashes = storjHashesDb.storjHashes


# 
def writestorjtomongo(userid,date,buckethash,filehash):
	#userId = storjHashObj['userId']
	#date = storjHashObj['date']
	#metadiskhash = storjHashObj['metadiskhash']
	print "inside write storj to mongo, writing to mongo now"
	print "userid,date,buckethash,filehash=",userid,date,buckethash,filehash
	writeobj={'userid':userid,'date':date,'buckethash':buckethash,'filehash':filehash}
	print "writeobj",writeobj
	storjHashesBefore = storjHashes.find({'userId': userid}).count()
	storjHashes.insert(writeobj)
	storjHashesAfter = storjHashes.find({'userId': userid}).count()
	response = 'Successfully inserted'

	return response

def getDateHashes(userId, date):
	queryResults = storjHashes.find({{'$and': [{'userId': userId}, {'date': date}]}})

	if queryResults.count() > 0:
		for result in queryResults:
			return result

