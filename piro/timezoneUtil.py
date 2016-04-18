from datetime import datetime, date, timedelta
from pytz import timezone
import requests
from pprint import pprint
from flask import session

# Generate & return a datetime object from a Unix timestamp
def createDatetimeFromTimestamp(timestamp):
	return datetime.utcfromtimestamp(timestamp)

def utcFromDatetime(datetimeObject):
	timestamp = (datetimeObject - datetime(1970, 1, 1)).total_seconds()
	return timestamp

def datetimeObjFromYYYYMMDD(yyyymmdd):
	year = int(yyyymmdd[:4])
	month = int(yyyymmdd[4:6])
	day = int(yyyymmdd[6:])

	datetimeObject = datetime(year, month, day)
	return datetimeObject

def localizedDatetimeObjFromYYYYMMDD(yyyymmdd):
	locale = timezone(session['timezone'])
	year = int(yyyymmdd[:4])
	month = int(yyyymmdd[4:6])
	day = int(yyyymmdd[6:])

	datetimeObject = datetime(year, month, day, tzinfo=locale)
	return datetimeObject

def yyyymmddFromDatetimeObj(datetimeObj):
	year = str(datetimeObj.year)
	month = datetimeObj.month
	if month < 10:
		month = "0" + str(month)
	else:
		month = str(month)
	day = datetimeObj.day
	if day < 10:
		day = "0" + str(day)
	else:
		day = str(day)
	# Concatenate
	formattedDate = year + month + day
	return formattedDate

def localizedDatetimeObjToReadableDate(localizedDatetimeObj):
	readableDate = localizedDatetimeObj.strftime('%a %b %d, %Y')
	print readableDate
	return readableDate

# Generate a timezone-adjusted Unix timestamp
def getLocalizedTimestamp(locale, timestamp):
	timestamp = timestamp
	adjustedTimestamp = 0
	tz = timezone(locale)
	datetimeObject = createDatetimeFromTimestamp(timestamp)
	rawOffset = timezone(locale).localize(datetimeObject).strftime('%z')
	# Convert offset into seconds
	offsetOperator = rawOffset[0]
	offsetHours = int(rawOffset[1:3])
	offsetMinutes = int(rawOffset[3:])
	offsetTotalMinutes = (offsetHours * 60) + offsetMinutes
	offsetSeconds = offsetTotalMinutes * 60
	# Determine whether or not to add or subtract offset amount
	if offsetOperator == '-':
		adjustedTimestamp = timestamp - offsetSeconds
	elif offsetOperator == '+':
		adjustedTimestamp = timestamp + offsetSeconds
	adjustedDatetimeObject = createDatetimeFromTimestamp(adjustedTimestamp)
	return adjustedTimestamp

# Generates a date as a string in format YYYYMMDD
def formattedDateGenerator(localizedTimestamp):
	datetimeObject = createDatetimeFromTimestamp(localizedTimestamp)
	year = str(datetimeObject.year)
	month = datetimeObject.month
	day = datetimeObject.day
	# Add a leading '0' for months 1-9
	if month < 10:
		month = '0' + str(month)
	elif month >= 10:
		month = str(month)
	# Add a leading '0' for days 1-9
	if day < 10:
		day = '0' + str(day)
	elif day >= 10:
		day = str(day)
	# Concatenate date parts
	formattedDate = year + month + day
	return formattedDate

# Subtracts 4 hours from a timestamp because we're starting
# dates at 4am instead of 12am
# Generates a date as a string in format YYYYMMDD
def adjustedDateGenerator(localizedTimestamp):
	offsetHours= 4
	offsetSeconds = offsetHours * 60 * 60
	adjustedTimestamp = localizedTimestamp - offsetSeconds
	adjustedDate = formattedDateGenerator(adjustedTimestamp)
	return adjustedDate

# Use the Geonames API to determine which time zone a pair of coordinates falls within
def coordsToTimezoneLocale(latitude, longitude):
	baseUrl = 'http://api.geonames.org/'
	endpoint = 'timezoneJSON'
	params = {
	'lat': str(latitude).encode('utf-8'),
	'lng': str(longitude).encode('utf-8'),
	'username': 'jalexander620@gmail.com'
	}
	constructedUrl = baseUrl + endpoint
	# Hit the Geonames API
	response = requests.get(constructedUrl, params=params)
	decodedResponse = response.json()
	try:
		timezoneLocale = decodedResponse['timezoneId']
	except Exception as e:
		print
		print '------- ERROR GETTING TIMEZONE LOCALE FROM GEONAMES -------', e
		return None
	return timezoneLocale

# Use the Geonames API to geocode a place name into a pair of coordinates
def geocode(placeName):
	baseUrl = 'http://api.geonames.org'
	endpoint = '/postalCodeSearchJSON'
	constructedUrl = baseUrl + endpoint
	# Remove space in given placeName argument
	splitName = placeName.split(' ')
	city = splitName[0]
	state = splitName[1]
	placeName = city + state

	params = {
	'placename': placeName,
	'maxRows': '1',
	'style': 'full',
	'username': 'jalexander620@gmail.com'
	}
	# Hit the Geonames API
	try:
		response = requests.get(constructedUrl, params=params)
	except Exception as e:
		print
		print '------- ERROR HITTING THE GEONAMES API -------', e
		print
		return None
	try:
		decodedResponse = response.json()
	except Exception as e:
		print
		print '------- ERROR DECODING GEONAMES RESPONSE -------', e
		print
		return None
	try:
		firstResult = decodedResponse['postalCodes'][0]
	except Exception as e:
		print
		print '------- ERROR GETTING PLACE NAME FROM RESPONSE -------', e
		print
		return None
	latitude = str(firstResult['lat'])
	longitude = str(firstResult['lng'])
	coords = {
	'latitude': latitude,
	'longitude': longitude
	}
	return coords

# Use the Geonames API to reverse geocode a pair of coordinates into a place name
def reverseGeocode(latitude, longitude):
	baseUrl = 'http://api.geonames.org/'
	endpoint = 'findNearbyPostalCodesJSON'
	params = {
	'lat': str(latitude).encode('utf-8'),
	'lng': str(longitude).encode('utf-8'),
	'radius': '30', #Radius in km
	'style': 'FULL',
	'username': 'jalexander620@gmail.com'
	}
	constructedUrl = baseUrl + endpoint
	# Hit the Geonames API
	try:
		response = requests.get(constructedUrl, params=params)
	except Exception as e:
		print
		print '------- ERROR HITTING THE GEONAMES API -------', e
		print
	decodedResponse = response.json()
	firstResult = decodedResponse['postalCodes'][0]
	# Try to get the city or county/local administrative region name
	try:
		city = firstResult['placeName']
	except Exception as e:
		print
		print '------- ERROR RETRIEVING CITY NAME -------', e
		try:
			city = firstResult['adminName2']
		except Exception as e:
			print
			print '------- ERROR RETRIEVING COUNTY/LOCAL ADMIN NAME -------', e
			city = ''
	# Try to get the state/administrative region name
	try:
		state = firstResult['adminCode1']
	except Exception as e:
		print
		print '------- ERROR RETRIEVING STATE/ADMIN NAME -------', e
		state = ''
	# Construct placeName
	placeName = ''
	if city != '':
		placeName += city
	placeName += ', '
	if state != '':
		placeName += state
	# Return None if neither city nor administrative name was found
	if placeName == ', ':
		return None
	return placeName

from apiCredentials import getAPICredentials
# Instantiate Foursquare API credentials
API_KEY = getAPICredentials('foursquare')[0]
SECRET = getAPICredentials('foursquare')[1]
API_VERSION = '20160324'
MODE = 'swarm'

from factual import Factual
from factual.utils import circle


# Use Foursquare's API to find the closest business name from a pair of coordinates
# NOT CURRENTLY WORKING PROPERLY - FOURSQUARE NOT GIVING ACCURATE RESULTS - MAYBE TRY GOOGLE PLACES API?
def reverseGeocodeBusiness(latitude, longitude):

	factual = Factual('SOYYrhMgNoRKMDsKSVfANUMExX5cPeeuQ5fUD6Wd', '1w2bwTf2NwRa0ljzsUYROYyrCwEXiERUuYrIJbaC')

	places = factual.table('places')

	places = places.geo(circle(latitude, longitude, 15)).filters({'$and': [{'category_ids':{'$includes_any':[20, 107, 308, 372, 424, 430]}}, {'category_ids':{'$excludes_any':[439, 440]}}]}).data()
	
	if len(places) > 0:
		sortedPlaces = sorted(places, key=lambda k: float(k['$distance']))

		for place in sortedPlaces:
			tempPlace = {}
			
			name = place['name']
			city = place['locality']
			region = place['region']

			tempPlace['name'] = name
			tempPlace['city'] = city
			tempPlace['region'] = region

			return tempPlace
	else:
		return None


	# resolve from name and geo location
	# data = factual.resolve('places', {'latitude':latitude,'longitude':longitude}).response()
	# print '------- FACTUAL RESOPONSE DATA -------', data


		



if __name__ == '__main__':
	# getLocalizedTimestamp('America/Los_Angeles', 1460067767)
	# adjustedDateGenerator(getLocalizedTimestamp('America/Los_Angeles', 1460024566))
	# coordsToTimezoneLocale(37.8734855,-122.2597169)
	# reverseGeocode(37.8734855,-122.2597169)
	reverseGeocodeBusiness(37.8734855,-122.2597169)