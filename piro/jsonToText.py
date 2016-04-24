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

	# dates = ['20160204', '20160106', '20130331']

	# queryResultDate = memoryDisks.find({'$and': [{'userId': userId}, {'date': '20160106'}]})

	# for result in queryResultDate:
	# 	pprint(result)

	# return
	downloadDirectory = ''

	queryResults = memoryDisks.find({'userId': userId})

	for result in queryResults:
		if result['date'] in dates:
			path1=os.path.dirname(__file__)
			dirpath=os.path.join(path1,'static','staging',str(userid),date)
			downloadDirectory = dirpath
			# downloadDirectory = 'static/staging/'+userId+'/'+result['date']+'/'

			# Check if download directory exists; create if it does not exist
			if not os.path.exists(downloadDirectory):
				os.makedirs(downloadDirectory)

			print '======== download directory:', downloadDirectory
			print 'filename =============', result['date']

			with open(downloadDirectory+result['date']+'.txt', 'w') as outfile:
   				json.dump(dumps(result), outfile)
