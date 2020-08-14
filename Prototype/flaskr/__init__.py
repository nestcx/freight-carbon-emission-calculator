from flask import Flask, render_template, request, jsonify
from . import maproutes
from . import algorithm

from flask_limiter import Limiter # Use to limit the amount of requests a user can perform in a given duration
from flask_limiter.util import get_remote_address

def create_app():
  app = Flask(__name__, instance_relative_config=True)

  limiter = Limiter(
    app,
    key_func=get_remote_address,

    # By default, limit requests to all routes to 2000 per day, and 100 per hour.
    # TODO: See if this should be increased/decreased or even remove default limits entirely
    default_limits=["2000 per day", "100 per hour"]
  )


  @app.route("/")
  def main():
    return render_template("main.html")
  
  @app.route("/dashboard")
  def dashboard():
    return render_template("dashboard.html")

  # Find the route between 2 specified coordinates or addresses
  # Returns the data in GeoJSON format
  @app.route("/route", methods=["GET"])
  def get_route():

    # Ensure that two coordinates are passed as arguments
    if "startCoords" in request.args and "endCoords" in request.args:
      start_coords = request.args.get("startCoords")
      end_coords = request.args.get("endCoords")

      # Return the GeoJSON data and a status code of 200 indicating success
      return maproutes.get_route(start_coords, end_coords), 200
    else:
      # TODO: Handle error more gracefully
      return "Need to input coordinates as request arguments"


  # This will be used for asynchronous requests.
  # Find suggestions for address/places depending on the user's input so far
  # Returns a list of possible addresses if found
  @app.route("/search/address", methods=["GET"])
  @limiter.limit("4 per second") # Throttle requests to 4 per second as per OpenRouteService's request/guidelines
  def find_coordinate_of_address():
    if "input" in request.args:
      user_input = request.args.get("input")
      # Return the JSON data and a status code of 200 indicating success
      return maproutes.search_address(user_input), 200
    else:
      # TODO: Handle error more gracefully
      return "Need to input something", 400 # 400 status code indicates that there was a client error
  


  # need to tidy up / put in it's own file with flask blueprint
  @app.route("/calculate_emissions", methods=["POST"])
  def get_emissions():
    """API endpoint for calculating emissions based on trip-specific values.

    Expected parameters in the JSON request:
    startCoords  -- decimal degrees
    endCoords    -- decimal degrees
    load_weight  -- tonnes

    The algorithm receives the following values:
    fuel_economy -- litres per 100 kilometres, float
    distance     -- kilometres, float
    load_weight  -- tonnes, float

    TODO:  conversion methods? when should the data be converted? 

    """

    # Check if request data contains JSON
    if not request.is_json:
      return jsonify({"msg": "Missing JSON in POST request"}), 400

    # Parse json into dictionary
    request_data = request.get_json()

    # TODO: put each of these input calculations into their own methods once blueprints implemented.

    # input 1:  Distance
    # Calculate trip distance
    if ('startCoords' in request_data) and ('endCoords' in request_data):
      geo_JSON_data = maproutes.getRoute(request_data['startCoords'], request_data['endCoords'])
      distance = maproutes.getLengthOfRoute(geo_JSON_data)

      # convert distance to kilometres
      distance = distance / 1000


    # input 2:  Load Weight
    if ('load_weight' in request_data):
      load_weight = request_data['load_weight']


    # input 3:  Fuel Economy
    # this value is currently hardcoded here. Will change to constant when this method has it's own file.
    fuel_economy = 47.162


    # call the algorithm function and return as json
    emissions = algorithm.calculate_emissions(fuel_economy, distance, load_weight)
    return jsonify(emissions)

    
  return app

