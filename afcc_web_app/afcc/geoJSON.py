from flask import Blueprint
from afcc import data_conversion

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