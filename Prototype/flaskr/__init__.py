from flask import Flask, render_template
from . import mapapiconnector as mapapi # need a . when importing from the same level, for some strange reason (its called relative imports if wanting to google it)

def create_app():
  app = Flask(__name__, instance_relative_config=True)

  @app.route("/")
  def main():
    return render_template("main.html")
  
  @app.route("/dashboard")
  def dashboard():
    return render_template("dashboard.html")

  # TODO: THIS ROUTE WON'T WORK AS THE MAPAPICONNECTOR FILE HASN'T BEEN PUSHED TO THE REPO
  # Find the route between 2 specified coordinates or addresses
  # Returns the data in GeoJSON format
  @app.route("/route")
  def getRoute():
    return mapapiconnector.connectToApi()

  # This will be used for asynchronous requests.
  # Find suggestions for address/places depending on the user's input so far
  # Returns a list of possible addresses if found
  # Note that this function should throttle requests to minimise loads 
  @app.route("/autocomplete/address")
  def findCoordinateOfAddress():
    # Add functionality here
    print("Todo")
  
  return app

