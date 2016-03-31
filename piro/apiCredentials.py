## PACKAGE FOR SETTING & GETTING API CREDENTIALS FROM APICREDENTIALS TABLE

from piro import models, db
from models import APICredentials

def getAPICredentials(apiName):
	apiNameQueryResult = APICredentials.query.filter_by(apiName=apiName).first()
	apiNameQueryResultDict = apiNameQueryResult.__dict__
	try:
		apiKeyOrClientId = apiNameQueryResultDict['apiKeyOrClientId']
	except Exception as e:
		print
		print '------- ERROR GETTING apiKeyOrClientId -------', e
		print
		apiKeyOrClientId = ''
	try:
		apiSecret = apiNameQueryResultDict['apiSecret']
	except:
		print
		print '------- ERROR GETTING apiSecret -------', e
		print
		apiSecret = ''

	return [apiKeyOrClientId, apiSecret]

def setAPICredentials(apiName, apiKeyOrClientId, apiSecret):
	apiNameQueryResult = APICredentials.query.filter_by(apiName=apiName).first()
	if apiNameQueryResult is not None:
		# Update the API's existing record in the APICredentials table
		print
		print '------ THERE IS ALREADY A RECORD FOR THE', apiName, 'API -------'
		print '------- UPDATING', apiName, 'API CREDENTIALS -------'
		print
		apiNameQueryResult.apiKeyOrClientId = apiKeyOrClientId
		apiNameQueryResult.apiSecret = apiSecret
	else:
		# Create a new db record to be inserted into the APICredentials table
		apiCredentials = APICredentials(apiName, apiKeyOrClientId, apiSecret)
		# Add and commit newly created apiCredentials db record
		db.session.add(apiCredentials)
	# Commit the results to the UserDevice table in the db
	try:
		db.session.commit()
	except Exception as e:
		print
		print "------- ERROR WRITING", apiName, "API CREDENTIALS DB -------", e
		print