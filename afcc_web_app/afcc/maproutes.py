import requests
import json
import math

from flask import Blueprint
from flask import request

from afcc import data_conversion
from afcc import limiter


maproutes_bp = Blueprint("openrouteservice", __name__, url_prefix="/openrouteservice", static_folder='static', template_folder='templates')


###############
# BEGIN VIEWS #
###############

@maproutes_bp.route("/route", methods=["GET"])
def get_route():
    # Ensure that two coordinates are passed as arguments
    if "startCoords" in request.args and "endCoords" in request.args:
      start_coords = request.args.get("startCoords")
      end_coords = request.args.get("endCoords")
      print(start_coords)

      # Return the GeoJSON data and a status code of 200 indicating success
      return get_route(start_coords, end_coords), 200
    else:
      # TODO: Handle error more gracefully
      return "Need to input coordinates as request arguments"


# This will be used for asynchronous requests.
# Find suggestions for address/places depending on the user's input so far
# Returns a list of possible addresses if found
@maproutes_bp.route("/search/address", methods=["GET"])
@limiter.limit("4 per second") # Throttle requests to 4 per second as per OpenRouteService's request/guidelines
def find_coordinate_of_address():
    if "input" in request.args:
        user_input = request.args.get("input")
        # Return the JSON data and a status code of 200 indicating success
        return search_address(user_input), 200
    else:
        # TODO: Handle error more gracefully
        return "Need to input something", 400 # 400 status code indicates that there was a client error

###############
#  END VIEWS  #
###############


# Get the token key from the configs file
with open('configs.json') as json_file:
  configs = json.load(json_file)
  API_KEY = configs["token_key"]

def get_route(start_coords, end_coords):
  """Get a route between two coordinates by sending a GET request to an API

  Arguments:
  start_coords {number} -- Coordinates of starting location in [longitude, latitude] form
  end_coords {number} -- Coordinates of destination in [longitude, latitude] form

  Returns:
  [JSON] -- Retrieved data about the route, in GeoJSON format.
  """

  endpointURL = "https://api.openrouteservice.org/v2/directions/driving-hgv?api_key={}&start={}&end={}" \
    .format(API_KEY, start_coords, end_coords)  
  response = requests.get(endpointURL)

  # First check if the API service was able to process the requests successfully.
  # They will return a status code of 200 if so.
  if response.status_code == 200:
    result = response.json()

    # For Debugging purposes
    print ("total length in metres: " + str(get_length_of_route(result)))
    print ("estimated length of trip in seconds: " + str(get_duration_of_route(result)))
    print (data_conversion.convert_seconds_to_dhms(get_duration_of_route(result)))
    
    return result

  # Status code of 400 means that we sent an incorrect request/inputs, therefore provide the user with feedback.
  elif response.status_code == 400:
    # TODO: Change this to handle the error gracefully
    return "Error: request was unable to processed"
  # Handle any other of the various possible errors
  else:
    # TODO: Change this to handle the error gracefully
    return "Error: " + str(response.status_code)



def get_length_of_route(route_geojson):
  """Get the distance between the starting location and destination. Note that distance refers to the
  total amount of metres if the route is followed exactly (i.e, it is not the straight line distance 
  between 2 points).

  Arguments:
  route_geojson {JSON} -- the GeoJSON data containing data about the route

  Returns:
  [float] -- Total distance between point A and point B, in metres. -1 if an error was encountered
  """

  # Create a try/catch block to handle errors in the event that the JSON data is incorrect/changed format
  try:
    return route_geojson["features"][0]["properties"]["summary"]["distance"]
  except:
    return -1



def get_duration_of_route(route_geojson):
  """Get the estimated time it will take to reach the destination from starting location

  Arguments:
  route_geojson {JSON} -- the GeoJSON data containing data about the route

  Returns:
  [float] -- Duration of route in seconds. -1 if an error was encountered
  """
  # Create a try/catch block to handle errors in the event that the JSON data is incorrect/changed format
  try:
    return route_geojson["features"][0]["properties"]["summary"]["duration"]
  except:
    return -1



def search_address(user_input):
  """Try predict what address the user will type, by calling an API and returning all possible addresses

  Arguments:
  user_input {string} -- The user's input so far

  Returns:
  [JSON] -- JSON data of all the possible addresses so far. Note that JSON data will still be returned 
  even if no addresses were found
  """

  country = "AUS" # restrict all searches to addresses in Australia only.
  
  endpointURL = "https://api.openrouteservice.org/geocode/search?api_key={}&text={}&boundary.country={}" \
    .format(API_KEY, user_input, country)
  response = requests.get(endpointURL)
  
  # Check if API service was able to process the request successfully, and if so, return the data
  if response.status_code == 200:
    return response.json() # 
  else:
    # TODO: Handle error more gracefully
    return "Error: " + response.status_code 



def convert_address_to_coords(address):
  pass



def convert_coords_to_address(coords):
  pass