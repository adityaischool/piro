# CODE TO HIT FITBIT API AND GRAB USER'S DATA

import fitbit
from pprint import pprint
from models import UserDevice,User
#import request

clientId = '227NKT'
clientSecret = 'd7a4ececd5e68a5f3f36d64e304fbe25'

def hitFitbitApis(userId, date=None):
	accesstoken = ''
	refreshtoken = ''

	# Get User's Fitbit access & refresh tokens from the UserDevice table
	try:
		first=UserDevice.query.filter_by(userid=userId).first()
		print "user id is ----",userId
		print "first row is ----"
		print first.__dict__
		fdict=first.__dict__
		accesstoken=fdict['accesstoken']
		refreshtoken=fdict['refreshtoken']
	except Exception as e:
		print "Error! --- ", e

	# Instantiate Fitbit API client object
	try:
		auth_cl=fitbit.Fitbit(clientId, clientSecret,oauth2=True,access_token=accesstoken,refresh_token=refreshtoken)
	except Exception as e:
		print "Error! --- ", e

	# Hit 'Body' endpoint of Fitbit API
	fitbitBodyData = auth_cl.body(date)
	print "-----------\n-----\n---Body Data-----\n\n\n"
	pprint(fitbitBodyData)

	# Hit 'Activities' endpoint of Fitbit API
	fitbitActivitiesData = auth_cl.activities(date)
	print "-----------\n-----\n---Activities Data-----\n\n\n"
	pprint(fitbitActivitiesData)

	# Hit 'Sleep' endpoint of Fitbit API
	fitbitSleepData = auth_cl.sleep(date)
	print "-----------\n-----\n---Sleep Data-----\n\n\n"
	pprint(fitbitSleepData)

	# Hit 'Heart' endpoint of Fitbit API
	fitbitHeartData = auth_cl.heart(date)
	print "-----------\n-----\n---Heart Rate Data-----\n\n\n"
	pprint(fitbitHeartData)

	# Hit 'BP' endpoint of Fitbit API
	fitbitBpData = auth_cl.bp(date)
	print "-----------\n-----\n---Blood Pressure Data-----\n\n\n"
	pprint(fitbitBpData)

	packagedData = {'data': [fitbitBodyData, 
	fitbitActivitiesData, 
	fitbitSleepData, 
	fitbitHeartData,
	fitbitBpData]}

	return packagedData


if __name__ == '__main__':
	hitFitbitApis('alextest', '2015-12-24')