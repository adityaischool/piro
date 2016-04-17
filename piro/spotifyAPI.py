## A SIMPLE UTILITY FOR HITTING THE SPOTIFY SEARCH API

import requests
from pprint import pprint


def getSpotifyPreviewAndImgUrls(artist, track):
	baseUrl = 'https://api.spotify.com/v1'
	endpoint = '/search'
	constructedUrl = baseUrl + endpoint

	query = '"' + artist + '" "' + track + '"'

	params = {
	'q': query,
	'type': 'track'
	}

	try:
		response = requests.get(constructedUrl, params=params)
	except Exception as e:
		print
		print '------- ERROR HITTING SPOTIFY API -------', e
		print

	try:
		decodedResponse = response.json()
	except Exception as e:
		print
		print '------- ERROR DECODING SPOTIFY RESPONSE -------', e
		print '------- RAW SPOTIFY RESPONSE -------', response
		print
	# Parse Spotify's decoded response
	spotifyObj = {}
	try:
		previewUrl = decodedResponse['tracks']['items'][0]['preview_url']
		spotifyObj['previewUrl'] = previewUrl
	except Exception as e:
		print
		print '------- ERROR GETTING SPOTIFY PREVIEW URL -------', e
		print
		return None
	try:
		imgUrl = decodedResponse['tracks']['items'][0]['album']['images'][0]['url']
		spotifyObj['imgUrl'] = imgUrl
	except Exception as e:
		print
		print '------- ERROR GETTING SPOTIFY IMG URL -------', e
		print
		# Use stock Spotify logo if no image could be found/ error getting image
		spotifyObj['imgUrl'] = 'http://1.bp.blogspot.com/-wX17TM21_qQ/VkBQKAGtYXI/AAAAAAAAAp8/DAVVOavtrRQ/s1600/Spotify%2BBlack.png'

	return spotifyObj

