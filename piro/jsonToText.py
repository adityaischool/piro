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
import os, json
from bson.json_util import dumps

# Instantiate Mongo client
client = pymongo.MongoClient()
# Instantiate Mongo memory disk db
memoryDiskDb = client.memoryDiskDb
memoryDisks = memoryDiskDb.memoryDisks

def outputTxtFromJson():
	userId = session['userId']

	dates = ['20160204', '20160106', '20130331']

	# queryResultDate = memoryDisks.find({'$and': [{'userId': userId}, {'date': '20160106'}]})

	# for result in queryResultDate:
	# 	pprint(result)

	# return

	queryResults = memoryDisks.find({'userId': userId})

	for result in queryResults:
		if result['date'] in dates:
			with open(result['date']+'.txt', 'w') as outfile:
   				json.dump(dumps(result), outfile)
