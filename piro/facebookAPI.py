## Script for hitting FB Graph API
## Get all of a user's past posts & current posts every day
from facepy import GraphAPI
from pprint import pprint

facebookToken = 'CAAN6ytjDEsABAA9JfZBRnLBU3X8XxrhDYcCxyZC1xnh6OpMYIGKeop33UyftqbfKZCIc8GkzDrtjxmh1iHLSaOxKIU2vXrRI8lYWew5XRMHyZA7ruYfZAwRTCczJtkXzasdMod8pQ2xDgDTsXfkJWaa9DXwSbg5BVcnGVqfRO5pF24AwJlRbGWV4gC6SuZCa8I8kFdFOJecAZDZD'

# Initialize the Graph API with a valid access token (optional,
# but will allow you to do all sorts of fun stuff).
graph = GraphAPI(facebookToken)

def getPhotos():
	# Get my latest posts
	myPhotos = graph.get('me/photos/uploaded')
	pprint(myPhotos)

def getAlbums():
	pass


if __name__ == '__main__':
	getPhotos()