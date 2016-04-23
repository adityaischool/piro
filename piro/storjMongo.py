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



def writeToStorj(storjHashObj):
	userId = storjHashObj['userId']
	date = storjHashObj['date']

	storjHashesBefore = storjHashes.find({'userId': userId}).count()
	storjHashes.insert(storjHashObj)
	storjHashesAfter = storjHashes.find({'userId': userId}).count()

	response = 'Successfully inserted', storjHashesBefore = storjHashesAfter, 'Storj Hashes for date', date, 'into Mongo'

	return response

def getDateHashes(userId, date):
	queryResults = storjHashes.find({{'$and': [{'userId': userId}, {'date': date}]}})

	if queryResults.count() > 0:
		for result in queryResults:
			return result

