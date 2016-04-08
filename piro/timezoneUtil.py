from datetime import datetime, timedelta
from pytz import timezone
import requests

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

auth = Oauth1Authenticator(
    consumer_key='XWZTKVrlIf0n8Gyxmgihkg',
    consumer_secret='wHdF8zUBnWcJ_rceQbK18ZcwSeI',
    token='UP_PXflQ4LeMWMLKvrkxGzUxc_B_GMLI',
    token_secret='p1SmFEYZbkQknMGte5yqTY2OpeQ'
)
yelpClient = Client(auth)

# Generate & return a datetime object from a Unix timestamp
def createDatetimeFromTimestamp(timestamp):
	return datetime.utcfromtimestamp(timestamp)

def utcFromDatetime(datetimeObject):
	timestamp = (datetimeObject - datetime(1970, 1, 1)).total_seconds()
	return timestamp

# Generate a timezone-adjusted Unix timestamp
def getLocalizedTimestamp(locale, timestamp):
	timestamp = timestamp
	adjustedTimestamp = 0
	tz = timezone(locale)
	datetimeObject = createDatetimeFromTimestamp(timestamp)
	# localizedTimestamp = datetimeObject.astimezone(tz)
	rawOffset = timezone(locale).localize(datetimeObject).strftime('%z')
	# print
	# print '------- UTC TIMESTAMP -------', timestamp
	# print '------- UTC DATETIME -------', datetimeObject
	# print '------- LOCALE -------', locale
	# print '------- TIMEZONE OFFSET -------', rawOffset
	# Convert offset into seconds
	offsetOperator = rawOffset[0]
	offsetHours = int(rawOffset[1:3])
	offsetMinutes = int(rawOffset[3:])
	offsetTotalMinutes = (offsetHours * 60) + offsetMinutes
	offsetSeconds = offsetTotalMinutes * 60
	# print '------- OFFSET SECONDS -------', offsetSeconds
	# Determine whether or not to add or subtract offset amount
	if offsetOperator == '-':
		adjustedTimestamp = timestamp - offsetSeconds
	elif offsetOperator == '+':
		adjustedTimestamp = timestamp + offsetSeconds
	adjustedDatetimeObject = createDatetimeFromTimestamp(adjustedTimestamp)
	# print '------- ADJUSTED TIMESTAMP -------', adjustedTimestamp
	# print '------- ADJUSTED DATETIME -------', adjustedDatetimeObject
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
	# print
	# print '------- DATETIME OBJECT -------', datetimeObject
	# print '------- FORMATTED DATE -------', formattedDate 
	return formattedDate

# Subtracts 4 hours from a timestamp because we're starting
# dates at 4am instead of 12am
# Generates a date as a string in format YYYYMMDD
def adjustedDateGenerator(localizedTimestamp):
	offsetHours= 4
	offsetSeconds = offsetHours * 60 * 60
	adjustedTimestamp = localizedTimestamp - offsetSeconds
	adjustedDate = formattedDateGenerator(adjustedTimestamp)
	# print
	# print '------- ORIGINAL LOCALIZED TIMESTAMP', localizedTimestamp
	# print '------- ADJUSTED LOCALIZED TIMESTAMP', adjustedTimestamp
	# print '------- ADJUSTED DATE FOR DAY STARTING AT', offsetHours, 'AM -------', adjustedDate
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
	# print
	# print '------- TIMEZONE LOCALE FOR LAT:', latitude, "& LONG:", longitude, '-------', timezoneLocale
	return timezoneLocale

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
	response = requests.get(constructedUrl, params=params)
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
	# print '------- PLACE NAME -------', placeName
	if placeName == ', ':
		return None
	return placeName

# Use Yelp's API to find the closest business name from a pair of coordinates
# NOT CURRENTLY WORKING PROPERLY - NOT SORTING CORRECTLY AS OF 4/7/2016
def reverseGeocodeBusiness(latitude, longitude):
	params = {
	'radius_filter': '25', #Radius in meters
	'sort': '1', #Sort by distance (DOES NOT WORK)
	'limit': '5'
	}
	# Hit the Yelp API
	response = yelpClient.search_by_coordinates(latitude, longitude, params)
	print '------- RESPONSE -------'
	for business in response.businesses:
		print
		print 'name:', business.name
		print 'image_url:', business.image_url
		print 'location:', business.location.address
		print 'latitude:', business.location.coordinate.latitude
		print 'longitude:', business.location.coordinate.longitude



if __name__ == '__main__':
	# getLocalizedTimestamp('America/Los_Angeles', 1460067767)
	adjustedDateGenerator(getLocalizedTimestamp('America/Los_Angeles', 1460024566))
	# coordsToTimezoneLocale(37.8734855,-122.2597169)
	# reverseGeocode(37.8734855,-122.2597169)
	# reverseGeocodeBusiness(37.8734855,-122.2597169)