from flask import Flask, render_template, request
from . import maproutes

def create_app():
  app = Flask(__name__, instance_relative_config=True)

  @app.route("/")
  def main():
    return render_template("main.html")
  
  @app.route("/dashboard")
  def dashboard():
    return render_template("dashboard.html")

  # Find the route between 2 specified coordinates or addresses
  # Returns the data in GeoJSON format
  @app.route("/route", methods=["GET"])
  def getRoute():

    # Ensure that two coordinates are passed as arguments
    if "startCoords" in request.args and "endCoords" in request.args:
      startCoords = request.args.get("startCoords")
      endCoords = request.args.get("endCoords")
      return maproutes.getRoute(startCoords, endCoords)

    else:
      return "Need to input coordinates as request arguments"


  # This will be used for asynchronous requests.
  # Find suggestions for address/places depending on the user's input so far
  # Returns a list of possible addresses if found
  # Note that this function should throttle requests to minimise loads 
  @app.route("/autocomplete/address")
  def findCoordinateOfAddress():
    # Add functionality here
    print("Todo")
  
  return app

