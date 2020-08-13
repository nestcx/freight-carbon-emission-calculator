from flask import Flask, render_template, request
from . import maproutes

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
  
  return app

