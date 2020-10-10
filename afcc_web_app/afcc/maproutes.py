import requests
import json
import math

from flask import Blueprint
from flask import request

from afcc import data_conversion
from afcc.extensions import limiter
from afcc.config import *  # Import sensitive config data

from afcc.models import Route, Postcode
from datetime import date, timedelta
from afcc.extensions import db
from afcc import data_conversion

from afcc.geoJSON import GeoJSON_Address, GeoJSON_Route_Matrix

maproutes_bp = Blueprint("maproutes", __name__, url_prefix="/maproutes",
                         static_folder='static', template_folder='templates')


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
# Throttle requests to 4 per second as per OpenRouteService's request/guidelines
@limiter.limit("4 per second")
def find_coordinate_of_address():
    if "input" in request.args:
        user_input = request.args.get("input")
        # Return the JSON data and a status code of 200 indicating success
        return search_address(user_input), 200
    else:
        # TODO: Handle error more gracefully
        # 400 status code indicates that there was a client error
        return "Need to input something", 400

###############
#  END VIEWS  #
###############

def get_route(start_coords, end_coords):
    """Get a route between two coordinates by sending a GET request to an API

    Arguments:
    start_coords {number} -- Coordinates of starting location as an array of floats in [longitude, latitude] form
    end_coords {number} -- Coordinates of destination as an array of floats in [longitude, latitude] form

    Returns:
    [JSON] -- Retrieved data about the route, in GeoJSON format.
    """
    
    # This is the amount of metres that the API service should look for a road from the point
    # of a coordinate. A larger number means that it would search a larger area when routing,
    # which means more often it will find successful route, but the algorithm might be a little
    # less accurate (though this is a non-issue in practice)
    road_search_radius = 1000
    
    endpointURL = "https://api.openrouteservice.org/v2/directions/driving-hgv"
    headers = { 
        'Authorization': API_KEY,
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Content-Type': 'application/json; charset=utf-8'}


    json = {
        "coordinates": [start_coords, end_coords],
        "instructions" : "false", # Don't want driving instructions, as we're only interested in the route distance and duration
        "radiuses" : [road_search_radius, road_search_radius]} # Must specify radius for both points
 
    response = requests.post(endpointURL, headers=headers, json=json)

    # First check if the API service was able to process the requests successfully.
    # They will return a status code of 200 if so.
    if response.status_code == 200:
        result = response.json()

        # For Debugging purposes
        # print("total length in metres: " + str(get_length_of_route(result)))
        # print("estimated length of trip in seconds: " +
        #       str(get_duration_of_route(result)))
        # print(data_conversion.convert_seconds_to_dhms(
        #     get_duration_of_route(result)))

        if get_length_of_route(result) < 0:
            return None

        return result

    # Status code wasn't 200, therefore, something went wrong in the route calculation
    else:
        return None


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


def search_address(address_input):
    """Try predict what address the user will type, by calling an API and returning all possible addresses

    Arguments:
    address_input {string} -- The user's input so far

    Returns:
    [JSON] -- JSON data of all the possible addresses so far. Note that JSON data will still be returned 
    even if no addresses were found
    """

    country = "AUS"  # restrict all searches to addresses in Australia only.

    endpointURL = "https://api.openrouteservice.org/geocode/search?api_key={}&text={}&boundary.country={}" \
        .format(API_KEY, address_input, country)
    response = requests.get(endpointURL)

    # Check if API service was able to process the request successfully, and if so, return the data
    if response.status_code == 200:
        return response.json()
    else:
        # TODO: Handle error more gracefully
        return "Error: " + response.status_code



def route_exists(postcode_a, postcode_b):
    print('route_exists(): checking if route exists between ' + postcode_a + ' and ' + postcode_b)

    route = Route.query.filter_by(
        point_a_postcode = postcode_a,
        point_b_postcode = postcode_b
        ).first()
        
    # flip point a and point b and retry to see if a route exists
    if route is None:
        route = Route.query.filter_by(
            point_a_postcode = postcode_b,
            point_b_postcode = postcode_a
        ).first()
    
    if route is None:
        print('route_exists(): Route doesn\'t exist')
        return None
    else:
        print('route_exists(): Route does exist')
        return route


def route_is_up_to_date(route):
    """Check if a route is up to date, meaning that it hasn't been more than a year since
    the route was calculated and stored in the routes table

    Arguments:
    route {object} the route object whose date will be checked

    Returns:
    [Boolean] -- True if it is up to date, otherwise false
    """

    todays_date = date.today()
    year_ago = todays_date - timedelta(days=365)
    
    if route.last_updated < year_ago:
        return False
    else:
        return True



def update_route(route):
    """Update a route in the routes table. Do so by calling the API service and updating the distance
    and duration as calculated by the API service. This is done to account for the fact that new features/
    roads/etc may be built or removed, which would alter the distance and duration of a route

    Arguments:
    route {object} the route object to update

    Returns:
    [Boolean] -- True if the route was able to be updated. Otherwise, false
    """

    coords_a = [route.point_a_long, route.point_a_lat]
    coords_b = [route.point_b_long, route.point_b_lat]
    # coords_a = str(route.point_a_long) + ',' + str(route.point_a_lat)
    # coords_b = str(route.point_b_long) + ',' + str(route.point_b_lat)


    # Call API service and retrieve the route directions again, so that the distance
    # and duration of the trip can be updated
    route_updated_GeoJSON = get_route(coords_a, coords_b)

    if route_updated_GeoJSON is not None:
        try:
            updated_length = data_conversion.metre_to_kilometre(
                get_length_of_route(route_updated_GeoJSON))
            updated_duration = get_duration_of_route(route_updated_GeoJSON)

            # Update the route object and commit to db
            route.route_distance_in_km = updated_length
            route.estimated_duration_in_seconds = updated_duration

            route.last_updated = date.today()
            db.session.commit()
            return True

        except:
            db.session.rollback()
            return False


def add_postcode_to_db(postcode):
    """Add a postcode and its coords to the postcode database. This is so that the app can avoid having
    to call the API service every time it needs to retrieve the coordinates of a postcode

    Arguments:
    postcode {int} -- The postcode that will be stored

    Returns:
    [Boolean] -- True if the postcode was able to be stored in the db, otherwise false
    """

    # Generate a GeoJSON_Address object and feed it the GeoJSON data that is retrieved from the API service
    postcode_data = GeoJSON_Address(search_address(postcode), postcode)
    
    print('add_postcode_to_db(): created postcode GeoJSON data')
    print('add_postcode_to_db(): postcode is: ' + str(postcode_data.get_postcode()))
    print('add_postcode_to_db(): postcode coords are: ' + str(postcode_data.get_long()) + ',' + str(postcode_data.get_lat()))    
    print('add_postcode_to_db(): adding postcode to db postcode table')

    try:
        new_postcode = Postcode(
            postcode = postcode_data.get_postcode(),
            long = postcode_data.get_long(),
            lat = postcode_data.get_lat()
        )

        db.session.add(new_postcode)
        db.session.commit()

        print('add_postcode_to_db(): successfully added postcode to db table')
        return True

    except:
        db.session.rollback()
        print('add_postcode_to_db(): ERROR: could not add postcode to db table')
        return False



def add_route(postcode_a, postcode_b):


    # Check if the database postcode table has a record of the postcode and its coords.
    # If not, create a new postcode record by calling the API service and retrieving
    # coordinate data of the postcode
    postcode_a_obj = Postcode.query.get(postcode_a)
    postcode_b_obj = Postcode.query.get(postcode_b)

    # If postcode a doesn't exist in the postcode db table, create it now
    if postcode_a_obj is None:
        print('add_route(): postcode ' + str(postcode_a) + ' doesn\'t exist in postcodes table')
        
        # If the postcode was able to be added to the db, continue.
        # If not, return false as we can't calculate the route without valid coordinates
        if add_postcode_to_db(postcode_a):
            postcode_a_obj = Postcode.query.get(postcode_a) # Retrive the newly created entry, as we need it for route creation
        else:
            print('add_route(): postcode ' + str(postcode_a) + ' was not able to be added to the postcodes table')
            return False

    # If postcode b doesn't exist in the postcode db table, create it now
    if postcode_b_obj is None:
        print('add_route(): postcode ' + str(postcode_b) + ' doesn\'t exist in postcodes table')

        if add_postcode_to_db(postcode_b):
            postcode_b_obj = Postcode.query.get(postcode_b) # Retrive the newly created entry, as we need it for route creation
        else:
            print('add_route(): postcode ' + str(postcode_b) + ' was not able to be added to the postcodes table')
            return False

    print('')

    print([postcode_a_obj.long, postcode_a_obj.lat], [postcode_b_obj.long, postcode_b_obj.lat])

    geoJSONData = get_route(
        [postcode_a_obj.long, postcode_a_obj.lat],
        [postcode_b_obj.long, postcode_b_obj.lat]
    )


    print(geoJSONData)

    return

    # If valid geoJSON data was returned from API service, continue
    if geoJSONData is not None:
        length_of_route = data_conversion.metre_to_kilometre(
            get_length_of_route(geoJSONData))
        duration_of_route = get_duration_of_route(geoJSONData)

        route = Route(

            point_a_postcode = postcode_a,
            point_a_region_name = postcode_a_coordinates["features"][0]["properties"]["label"],
            # ORS API returns coords as [long, lat] as opposed to the common [lat, long]
            point_a_lat = postcode_a_coordinates["features"][0]["geometry"]["coordinates"][1],
            point_a_long = postcode_a_coordinates["features"][0]["geometry"]["coordinates"][0],
            
            point_b_postcode = postcode_b,
            point_b_region_name = postcode_b_coordinates["features"][0]["properties"]["label"],
            point_b_lat = postcode_b_coordinates["features"][0]["geometry"]["coordinates"][1],
            point_b_long = postcode_b_coordinates["features"][0]["geometry"]["coordinates"][0],
            
            route_distance_in_km = length_of_route,
            estimated_duration_in_seconds = duration_of_route,
            last_updated = date.today()
        )

        db.session.add(route)
        db.session.commit()

        return True

    return False


def add_routes_matrix(set_of_postcodes):
    print('\nadd_routes_matrix(): Going to call API for matrix of route data')
    geojson_matrix = GeoJSON_Route_Matrix(set_of_postcodes)
    
    print('\n\n\n\n')
    print(geojson_matrix.get_location_count())

    return geojson_matrix
