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
  
  def __init__(self, set_of_postcodes):
    print('Class GeoJSON_Route_Matrix: initialising')

    self.list_of_postcode_coords = []

    # OpenRouteService's Matrix API service requires a very specific format when it comes to coordinates
    # This is what the list of coordinates should look like:
    # let Rn = Route n, PCAlong = Postcode A longitude, PCAlat = Postcode A latitude, PCBlong = Postcode B longitude
    # Storte the postcodes in this format:
    # [[R1 PCAlong, R1 PCAlat], [R1 PCBlong, R1 PCBlat], 
    # [R2 PCAlong, R2 PCAlat], [R2 PCBlong, R2 PCBlat],
    # .. ,
    # [Rn PCAlong, Rn PCAlat], [Rn PCBlong, Rn PCBlat]] 

    # The operations below are all specifically to format the postcode coordinates in the required format
    for postcodes in set_of_postcodes:
      postcode_a_obj = Postcode.query.get(postcodes[0])
      postcode_b_obj = Postcode.query.get(postcodes[1])

      # self.list_of_postcode_coords.append([postcodes[0], postcodes[1]])
      self.list_of_postcode_coords.append([postcode_a_obj.long, postcode_a_obj.lat])
      self.list_of_postcode_coords.append([postcode_b_obj.long, postcode_b_obj.lat])

    print(self.list_of_postcode_coords)

    # You have to specify which indices are starting locations and ending locations
    # We've stored them in this format: [[route_1_start],[route_1_end],[route_2_start],[route_2_end]]
    # Therefore, start locations look like so [0, 2, 4, 6] , whereas end locations are like so: [1, 3, 5, 7]
    start_locations = list(range(0, len(self.list_of_postcode_coords), 2))
    end_locations = list(range(1, len(self.list_of_postcode_coords), 2))

    print(start_locations)
    print(end_locations)

    json = {
      "locations" : self.list_of_postcode_coords,
      "sources" : start_locations,
      "destinations" : end_locations,
      "metrics" : ["distance","duration"]}

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
    return self.geojson_data["metadata"]["query"]["locations"][n]

  def get_location_count(self):
    return len(self.geojson_data["metadata"]["query"]["locations"])

  def get_arr_of_distances_for_location(self, n):
    return self.geojson_data["distances"][n]
  
  def get_arr_of_durations_for_location(self, n):
    return self.geojson_data["durations"][n]