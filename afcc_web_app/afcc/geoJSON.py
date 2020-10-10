from flask import Blueprint
from afcc import data_conversion
from afcc.models import Postcode
from afcc.extensions import db
import requests
from afcc.config import *
from flask import jsonify

##############################################
############### FOR TESTING ONLY #############

# TODO: Remove blueprint and views once done testing the geojson data
geojson_bp = Blueprint("geojson", __name__, url_prefix="/geojson",
                         static_folder='static', template_folder='templates')

@geojson_bp.route("/", methods=["GET"])
def get_geojson_data():
  
  geojson = GeoJSON(data)

  print(geojson.get_distance())
  print(geojson.get_duration())
  print(geojson.get_duration_in_dhms())
  return data

class GeoJSON:

  def __init__(self, geoJSON_data):
    self.geojson = geoJSON_data
    
  
  def get_distance(self):
    return self.geojson['routes'][0]['summary']['distance']


  def get_duration(self):
    return self.geojson['routes'][0]['summary']['duration']


  def get_duration_in_dhms(self):
    return data_conversion.convert_seconds_to_dhms(self.geojson['routes'][0]['summary']['duration'])



class GeoJSON_Address:
  """This class is for extracting address-related data from GeoJSON data when an address
  postcode is provided.
  """

  def __init__(self, geoJSON_data, postcode=None):
    self.postcode = postcode
    self.long = geoJSON_data["features"][0]["geometry"]["coordinates"][0]
    self.lat = geoJSON_data["features"][0]["geometry"]["coordinates"][1]
    self.address_name = geoJSON_data["features"][0]["properties"]["label"]

  def get_postcode(self):
    return self.postcode

  def get_long(self):
    return self.long

  def get_lat(self):
    return self.lat

  def get_address_name(self):
    return self.address_name



class GeoJSON_Route_Matrix:
  
  def __init__(self, list_of_postcode_coords):
    print('Class GeoJSON_Route_Matrix: initialising')

    self.list_of_postcode_coords = list_of_postcode_coords

    json = {
      "locations" : self.list_of_postcode_coords,
      "metrics" : ["distance","duration"],
      "units":"km"}

    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': API_KEY,
        'Content-Type': 'application/json; charset=utf-8'
    }

    response = requests.post('https://api.openrouteservice.org/v2/matrix/driving-hgv', json=json, headers=headers)

    self.geojson_data = response.json()


  def get_geojson_data(self):
    return self.geojson_data

  def get_location_coordinates(self, n):
    # Typecast to a tuple, as it would otherwise return a list, which is an inappropriate data type
    return tuple(self.geojson_data["metadata"]["query"]["locations"][n])

  # Note that the location count is effectively the amount of rows and columns
  # that the matrix will have.
  def get_location_count(self):
    return len(self.geojson_data["metadata"]["query"]["locations"])

  def get_distance_between(self, i, j):
    """Return the distance between coordinates for location and a and b, in kms

    """
    return self.geojson_data["distances"][i][j]
  
  def get_duration_between(self, i, j):
    return self.geojson_data["durations"][i][j]