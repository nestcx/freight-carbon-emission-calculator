import requests
import json

# Get the token key from the configs file
with open('configs.json') as json_file:
  configs = json.load(json_file)
  API_KEY = configs["token_key"]

# Find the route between two coordinates by sending a GET request to OpenRouteService's API
# Returns the retrieved data in JSON format
def getRoute(startCoords, endCoords):

  endpointURL = "https://api.openrouteservice.org/v2/directions/driving-hgv?api_key={}&start={}&end={}".format(API_KEY, startCoords, endCoords)
  result = requests.get(endpointURL)

  print(result.json())
  return result.json()