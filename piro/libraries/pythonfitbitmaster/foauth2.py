import fitbit
import gather_keys_oauth2
#import fitoauth

def fitbitoauth():
	CLIENT_ID = '227NKT'
	CLIENT_SECRET = 'd7a4ececd5e68a5f3f36d64e304fbe25'

	server = gather_keys_oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
	server.browser_authorize()

	access_token = server.oauth.token['access_token']
	refresh_token = server.oauth.token['refresh_token']

	authd_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=access_token, refresh_token=refresh_token)

	# date in format yyyy-MM-dd
	print authd_client.activities(date='2015-12-24')
	print "inside aaaa",access_token,refresh_token


def newoauth():
	z = fitoauth.Fitbit()
	auth_url = z.GetAuthorizationUri()
	token = z.GetAccessToken(access_code)
	response = z.ApiCall(token, '/1/user/-/activities/log/steps/date/today/7d.json')
	print "response",response