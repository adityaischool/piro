from timezoneUtil import getLocalizedTimestamp, formattedDateGenerator, adjustedDateGenerator, reverseGeocode, coordsToTimezoneLocale, utcFromDatetime
from pprint import pprint
from piro import models, db
from models import User
from datetime import datetime
from forecastioAPI import getWeatherAtTime

def createDataPoint(userId, dataPointType, source, sourceData, timestamp, location=None, fileName=None, businessName=None, businessPhotoUrl=None):
	timestamp = timestamp
	localizedTimestamp = None
	locale = None
	localizedTimestamp = None
	actualDate = None
	adjustedDate = None
	placeName = None
	businessName = businessName
	businessPhotoUrl = businessPhotoUrl
	# Check if location is given. If so, localize the timestamp using the location
	# Otherwise, localize the timestamp using the user's locale in User db table
	if location is not None and location is not {}:
		locale = coordsToTimezoneLocale(location['lat'], location['long'])
		placeName = reverseGeocode(location['lat'], location['long'])
	else:
		# Get user's locale from the User db table if data point has no location
		try:
			userIdQueryResults = User.query.filter_by(userid=userId).first()
		except Exception as e:
			print
			print "------- ERROR QUERYING USER DB TABLE FOR USER LOCALE -------", e
			print
		userDict = userIdQueryResults.__dict__
		locale = userDict['timezone']
	# Generate the localized timestamp, actual date, and adjusted date
	# print
	# print '---------- TIMESTAMP --------', timestamp
	# print type(timestamp)
	# print
	if timestamp is not None:
		if type(timestamp) == type(datetime.now()):
			# print '------- GIVEN TIMESTAMP IS A DATETIME OBJECT... CONVERTING TO UTC -------'
			timestamp = utcFromDatetime(timestamp)
		localizedTimestamp = getLocalizedTimestamp(locale, timestamp)
		actualDate = formattedDateGenerator(localizedTimestamp)
		adjustedDate = adjustedDateGenerator(localizedTimestamp)
	else:
		return None
	# Get weather 
	# Generate dataPoint object
	dataPoint = {
	'userId': userId, # The user's id on our service
	'dataPointId': source + str(localizedTimestamp), # Will use for reference in 'disks'
	'dataPointType': dataPointType, # e.g., image or checkin
	'source': source, # e.g., dropbox
	'sourceData': sourceData, # This will be the data obj we generated from the provider
	'timestamp': timestamp,
	'localizedTimestamp': localizedTimestamp,
	'actualDate': actualDate,
	'adjustedDate': adjustedDate,
	'location': location,
	'placeName': placeName,
	'businessName': businessName,
	'businessPhotoUrl': businessPhotoUrl,
	'fileName': fileName
	}
	# print
	# print '------- DATA POINT -------'
	# pprint(dataPoint)
	return dataPoint