import requests
import json
import math

# Get the token key from the configs file
with open('configs.json') as json_file:
  configs = json.load(json_file)
  API_KEY = configs["token_key"]

def getRoute(startCoords, endCoords):
  """Get a route between two coordinates by sending a GET request to an API

  Arguments:
  startCoords {number} -- Coordinates of starting location in [longitude, latitude] form
  endCoords {number} -- Coordinates of destination in [longitude, latitude] form

  Returns:
  [JSON] -- Retrieved data about the route, in GeoJSON format.
  """

  endpointURL = "https://api.openrouteservice.org/v2/directions/driving-hgv?api_key={}&start={}&end={}" \
    .format(API_KEY, startCoords, endCoords)  
  response = requests.get(endpointURL)

  # First check if the API service was able to process the requests successfully.
  # They will return a status code of 200 if so.
  if response.status_code == 200:
    result = response.json()

    # For Debugging purposes
    print ("total length in metres: " + str(getLengthOfRoute(result)))
    print ("estimated length of trip in seconds: " + str(getDurationOfRoute(result)))
    print (convertSecondsToDHMS(getDurationOfRoute(result)))
    
    return result

  # Status code of 400 means that we sent an incorrect request/inputs, therefore provide the user with feedback.
  elif response.status_code == 400:
    # TODO: Change this to handle the error gracefully
    return "Error: request was unable to processed"
  # Handle any other of the various possible errors
  else:
    # TODO: Change this to handle the error gracefully
    return "Error: " + str(response.status_code)



def getLengthOfRoute(routeGeoJSON):
  """Get the distance between the starting location and destination. Note that distance refers to the
  total amount of metres if the route is followed exactly (i.e, it is not the straight line distance 
  between 2 points).

  Arguments:
  routeGeoJSON {JSON} -- the GeoJSON data containing data about the route

  Returns:
  [float] -- Total distance between point A and point B, in metres. -1 if an error was encountered
  """

  # Create a try/catch block to handle errors in the event that the JSON data is incorrect/changed format
  try:
    return routeGeoJSON["features"][0]["properties"]["summary"]["distance"]
  except:
    return -1



def getDurationOfRoute(routeGeoJSON):
  """Get the estimated time it will take to reach the destination from starting location

  Arguments:
  routeGeoJSON {JSON} -- the GeoJSON data containing data about the route

  Returns:
  [float] -- Duration of route in seconds. -1 if an error was encountered
  """
  # Create a try/catch block to handle errors in the event that the JSON data is incorrect/changed format
  try:
    return routeGeoJSON["features"][0]["properties"]["summary"]["duration"]
  except:
    return -1


# There are libraries that do a similar job to what this function does, but none
# were found that can format durations that exceed 24 hours
# TODO: Check if a library that provides this functionality exists
def convertSecondsToDHMS(n):
  """Format the amount of time it will take from starting location to destination into a readable format

  Arguments:
  n {number} -- The amount of seconds

  Returns:
  [string] -- The amount of time in days, HH:MM:SS format
  """

  # Get the days by using the // operator which divides and returns the floor value (rounding down to an integer)
  days = n // (60 * 60 * 24) 
  
  # Use the % operator to exclude the days and get the remaining hours
  n = n % (60 * 60 * 24) 
  # Get the amount of hours by rounding down to the nearest integer
  hours = n // (60 * 60)
  
  # Exclude the hours to get the remaining minutes
  n = n % (60 * 60)
  minutes = n // 60

  seconds = math.floor(n % 60)

  # Format string to "HH:MM:SS"
  formattedStr = str(int(hours)).zfill(2) + ":" + str(int(minutes)).zfill(2) + ":" + str(int(seconds)).zfill(2)

  # If total duration exceeds 24 hours, prepend the number of days it will take to the beginning of the string
  if days != 0:
    return str(int(days)) + " days " + formattedStr
  else:
    return formattedStr



def searchAddress(userInput):
  """Try predict what address the user will type, by calling an API and returning all possible addresses

  Arguments:
  userInput {string} -- The user's input so far

  Returns:
  [JSON] -- JSON data of all the possible addresses so far. Note that JSON data will still be returned 
  even if no addresses were found
  """

  country = "AUS" # restrict all searches to addresses in Australia only.
  
  endpointURL = "https://api.openrouteservice.org/geocode/search?api_key={}&text={}&boundary.country={}" \
    .format(API_KEY, userInput, country)
  response = requests.get(endpointURL)
  
  # Check if API service was able to process the request successfully, and if so, return the data
  if response.status_code == 200:
    return response.json() # 
  else:
    # TODO: Handle error more gracefully
    return "Error: " + response.status_code 



def convertAddressToCoords(address):
  pass



def converCoordsToAddress(coords):
  pass