from flask import Flask, render_template, request, jsonify, make_response
import maproutes
from . import emissioncalculator

def create_app():
  app = Flask(__name__, instance_relative_config=True)

  @app.route("/")
  def main():
    return render_template("main.html")
  
  @app.route("/dashboard")
  def dashboard():
    return render_template("dashboard.html")

  @app.route("/getemissionresult", methods = ['POST'])
  def getemissionresult():
    req=request.get_json()
    emissioncalculator.setLoadWeight(int(req('load')))
    dump=maproutes.getRoute(req('startc'), req('endc'))
    
    res=make_response(jsonify(emissioncalculator.getResult()),200)
    return res


  # Find the route between 2 specified coordinates or addresses
  # Returns the data in GeoJSON format
  @app.route("/route", methods=["GET"])
  def getRoute():

    # Ensure that two coordinates are passed as arguments
    if "startCoords" in request.args and "endCoords" in request.args:
      startCoords = request.args.get("startCoords")
      endCoords = request.args.get("endCoords")

      # Return the GeoJSON data and a status code of 200 indicating success
      return maproutes.getRoute(startCoords, endCoords), 200
    else:
      # TODO: Handle error more gracefully
      return "Need to input coordinates as request arguments"


  # This will be used for asynchronous requests.
  # Find suggestions for address/places depending on the user's input so far
  # Returns a list of possible addresses if found
  # Note that this function should throttle requests to about 5 per seconds to minimise loads and prevent abuse 
  @app.route("/search/address", methods=["GET"])

  ######################################################################
  # TODO: THROTTLE REQUESTS TO ENSURE NO MORE THAN 5 REQUESTS PER SECOND
  ######################################################################
  
  def findCoordinateOfAddress():
    if "input" in request.args:
      userInput = request.args.get("input")
      # Return the JSON data and a status code of 200 indicating success
      return maproutes.searchAddress(userInput), 200
    else:
      # TODO: Handle error more gracefully
      return "Need to input something"
  


  return app

