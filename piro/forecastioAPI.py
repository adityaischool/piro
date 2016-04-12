## PACKAGE FOR HITTING THE FORECAST.IO API

import os, requests, json, pymongo
from flask import request, session
# from models import UserDevice,User
from pprint import pprint
from apiCredentials import getAPICredentials

# Instantiate Forecast.io API credentials
API_KEY = getAPICredentials('forecastio')[0]
ENDPOINT = 'https://api.forecast.io/forecast/'
COMMA = '%2C'


# TIME should be a UNIX timestamp or a string formatted as follows: [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS]
def getWeatherAtTime(latitude, longitude, timestamp):

	constructedEndpoint = ENDPOINT+API_KEY+'/'+latitude+COMMA+longitude+COMMA+timestamp
	response = requests.get(constructedEndpoint)
	decodedResponse = response.json()
	print
	pprint(decodedResponse)
	print

	tempWeather = {}
	weatherObjAtGivenTime = decodedResponse['currently']
	weatherObjForDay = decodedResponse['daily']['data'][0]
	tempWeather['moonPhaseValue'] = None
	tempWeather['moonPhaseName'] = None

	try:
		tempWeather['temp'] = weatherObjAtGivenTime['apparentTemperature']
	except Exception as e:
		print
		print '------- ERROR GETTING TEMPERATURE -------', e
		print
		tempWeather['temp'] = None
	try:
		tempWeather['precipType'] = weatherObjAtGivenTime['precipType']
	except Exception as e:
		print
		print '------- ERROR GETTING PRECIPITATION TYPE -------', e
		print
		tempWeather['precipType'] = None
	try:
		tempWeather['pressure'] = weatherObjAtGivenTime['pressure']
	except Exception as e:
		print
		print '------- ERROR GETTING PRESSURE -------', e
		print
		tempWeather['pressure'] = None
	try:
		tempWeather['summary'] = weatherObjAtGivenTime['summary']
	except Exception as e:
		print
		print '------- ERROR GETTING WEATHER SUMMARY -------', e
		print
		tempWeather['summary'] = None
	try:
		tempWeather['windSpeed'] = weatherObjAtGivenTime['windSpeed']
	except Exception as e:
		print
		print '------- ERROR GETTING WIND SPEED -------', e
		print
		tempWeather['windSpeed'] = None
	try:
		tempWeather['icon'] = weatherObjAtGivenTime['icon']
	except Exception as e:
		print
		print '------- ERROR GETTING ICON -------', e
		print
		tempWeather['icon'] = None

	pointForecastTimestamp = weatherObjAtGivenTime['time']
	try:
		sunrise = weatherObjForDay['sunriseTime']
	except Exception as e:
		print
		print '------- ERROR GETTING SUNRISE TIME -------', e
		print
		sunrise = None
	try:
		sunset = weatherObjForDay['sunsetTime']
	except Exception as e:
		print
		print '------- ERROR GETTING SUNSET TIME -------', e
		print
		sunset = None
	# Compare point forecast timestamp with sunset timestamp to determine whether or not to include moon phase in return object
	if sunset is not None:
		if pointForecastTimestamp > sunset:
			try:
				tempWeather['moonPhaseValue'] = weatherObjForDay['moonPhase']
				print
				print '------- MOON PHASE VALUE TYPE:', type(tempWeather['moonPhaseValue']), '-------'
				print
			except Exception as e:
				print
				print '------- ERROR GETTING MOON PHASE VALUE -------', e
				print
	# Determine the name of the moon phase based on the percentage value
	if tempWeather['moonPhaseValue'] is not None:
		if tempWeather['moonPhaseValue'] == 0.00:
			tempWeather['moonPhaseName'] = 'new'
		elif tempWeather['moonPhaseValue'] > 0.00 and tempWeather['moonPhaseValue'] < 0.25:
			tempWeather['moonPhaseName'] = 'waxing-crescent'
		elif tempWeather['moonPhaseValue'] == 0.25:
			tempWeather['moonPhaseName'] = 'first-quarter'
		elif tempWeather['moonPhaseValue'] > 0.25 and tempWeather['moonPhaseValue'] < 0.50:
			tempWeather['moonPhaseName'] = 'waxing-gibbous'
		elif tempWeather['moonPhaseValue'] == 0.50:
			tempWeather['moonPhaseName'] = 'full'
		elif tempWeather['moonPhaseValue'] > 0.50 and tempWeather['moonPhaseValue'] < 0.75:
			tempWeather['moonPhaseName'] = 'waning-gibbous'
		elif tempWeather['moonPhaseValue'] == 0.75:
			tempWeather['moonPhaseName'] = 'last-quarter'
		elif tempWeather['moonPhaseValue'] > 0.75:
			tempWeather['moonPhaseName'] = 'waning-crescent'

	print
	print '------- TEMP WEATHER OBJECT -------'
	pprint(tempWeather)
	print

	return tempWeather

def getPlaceDateWeatherSummary(latitude, longitude, timestamp):

	constructedEndpoint = ENDPOINT+API_KEY+'/'+latitude+COMMA+longitude+COMMA+timestamp
	# print '---------- CONSTRUCTED ENDPOINT --------'
	# print constructedEndpoint
	# print
	response = requests.get(constructedEndpoint)
	# print
	# print '----------- RESPONSE ------------', response
	# print
	decodedResponse = response.json()
	# print
	# pprint(decodedResponse)
	# print

	tempWeather = {}
	weatherObjForDay = decodedResponse['daily']['data'][0]

	try:
		tempWeather['minTemp'] = weatherObjForDay['apparentTemperatureMin']
	except Exception as e:
		print
		print '------- ERROR GETTING MIN TEMPERATURE -------', e
		print
		tempWeather['minTemp'] = None
	try:
		tempWeather['maxTemp'] = weatherObjForDay['apparentTemperatureMax']
	except Exception as e:
		print
		print '------- ERROR GETTING MAX TEMPERATURE -------', e
		print
		tempWeather['maxTemp'] = None
	try:
		tempWeather['humidity'] = weatherObjForDay['humidity']
	except Exception as e:
		print
		print '------- ERROR GETTING HUMIDITY -------', e
		print
		tempWeather['humidity'] = None
	try:
		tempWeather['precipProbability'] = weatherObjForDay['precipProbability']
	except Exception as e:
		print
		print '------- ERROR GETTING PRECIPITATION PROBABILITY -------', e
		print
		tempWeather['precipProbability'] = None
	try:
		tempWeather['precipType'] = weatherObjForDay['precipType']
	except Exception as e:
		print
		print '------- ERROR GETTING PRECIPITATION TYPE -------', e
		print
		tempWeather['precipType'] = None
	try:
		tempWeather['pressure'] = weatherObjForDay['pressure']
	except Exception as e:
		print
		print '------- ERROR GETTING PRESSURE -------', e
		print
		tempWeather['pressure'] = None
	try:
		tempWeather['cloudCover'] = weatherObjForDay['cloudCover']
	except Exception as e:
		print
		print '------- ERROR GETTING CLOUD COVER -------', e
		print
		tempWeather['cloudCover'] = None
	try:
		tempWeather['visibility'] = weatherObjForDay['visibility']
	except Exception as e:
		print
		print '------- ERROR GETTING VISIBILITY -------', e
		print
		tempWeather['visibility'] = None
	try:
		tempWeather['summary'] = weatherObjForDay['summary']
	except Exception as e:
		print
		print '------- ERROR GETTING WEATHER SUMMARY -------', e
		print
		tempWeather['summary'] = None
	try:
		tempWeather['windSpeed'] = weatherObjForDay['windSpeed']
	except Exception as e:
		print
		print '------- ERROR GETTING WIND SPEED -------', e
		print
		tempWeather['windSpeed'] = None
	try:
		tempWeather['icon'] = weatherObjForDay['icon']
	except Exception as e:
		print
		print '------- ERROR GETTING ICON -------', e
		print
		tempWeather['icon'] = None

	pointForecastTimestamp = weatherObjForDay['time']
	try:
		tempWeather['sunrise'] = weatherObjForDay['sunriseTime']
	except Exception as e:
		print
		print '------- ERROR GETTING SUNRISE TIME -------', e
		print
		tempWeather['sunrise'] = None
	try:
		tempWeather['sunset'] = weatherObjForDay['sunsetTime']
	except Exception as e:
		print
		print '------- ERROR GETTING SUNSET TIME -------', e
		print
		tempWeather['sunset'] = None
	try:
		tempWeather['moonPhaseValue'] = weatherObjForDay['moonPhase']
	except Exception as e:
		print
		print '------- ERROR GETTING MOON PHASE VALUE -------', e
		print
		tempWeather['moonPhaseValue'] = None
	# Determine the name of the moon phase based on the percentage value
	tempWeather['moonPhaseName'] = None
	if tempWeather['moonPhaseValue'] is not None:
		if tempWeather['moonPhaseValue'] == 0.00:
			tempWeather['moonPhaseName'] = 'new'
		elif tempWeather['moonPhaseValue'] > 0.00 and tempWeather['moonPhaseValue'] < 0.25:
			tempWeather['moonPhaseName'] = 'waxing-crescent'
		elif tempWeather['moonPhaseValue'] == 0.25:
			tempWeather['moonPhaseName'] = 'first-quarter'
		elif tempWeather['moonPhaseValue'] > 0.25 and tempWeather['moonPhaseValue'] < 0.50:
			tempWeather['moonPhaseName'] = 'waxing-gibbous'
		elif tempWeather['moonPhaseValue'] == 0.50:
			tempWeather['moonPhaseName'] = 'full'
		elif tempWeather['moonPhaseValue'] > 0.50 and tempWeather['moonPhaseValue'] < 0.75:
			tempWeather['moonPhaseName'] = 'waning-gibbous'
		elif tempWeather['moonPhaseValue'] == 0.75:
			tempWeather['moonPhaseName'] = 'last-quarter'
		elif tempWeather['moonPhaseValue'] > 0.75:
			tempWeather['moonPhaseName'] = 'waning-crescent'

	# print
	# print '------- TEMP WEATHER OBJECT -------'
	# pprint(tempWeather)
	# print
	return tempWeather


