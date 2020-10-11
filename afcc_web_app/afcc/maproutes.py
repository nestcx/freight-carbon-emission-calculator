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
    # In this case, a radius of 5,000 metres is used because some very rural areas may not
    # have a road within a close radius of the 'centre' coordinate of the region
    road_search_radius = 5000
    
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
        
        # Some shipments just can't be processed due to incorrect data entry or
        # issues like inserting the same postcode in the 'from' and 'to' columns.
        # So try check if the data is valid, and if not, discard entirely. For some
        # errors, the API service will not include the distance as part of geoJSON data,
        # so you must try see if it exists, and if not, just return none anyway
        try:
            if result["routes"][0]["summary"]["distance"] > 0:
                return result
        except:
            return None

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
    # print('route_exists(): checking if route exists between ' + postcode_a + ' and ' + postcode_b)

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
        # print('route_exists(): Route doesn\'t exist')
        return None
    else:
        # print('route_exists(): Route does exist')
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

    # Try generate a GeoJSON_Address object and feed it the GeoJSON data that is retrieved from the API service
    # The API service may not have complete coverage of all areas and postcodes, so account for that
    # by adding a try/catch block
    try:
        postcode_data = GeoJSON_Address(search_address(postcode), postcode)
    except(Exception):
        print('add_postcode_to_db(): ERROR: could not add postcode to db table')
        return False

    print('add_postcode_to_db(): created postcode GeoJSON data')
    print('add_postcode_to_db(): postcode is: ' + str(postcode_data.get_postcode()))

    try:
        new_postcode = Postcode(
            postcode = postcode_data.get_postcode(),
            region_name = postcode_data.get_address_name(),
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



def get_postcode(postcode):
    """Try get a postcode and its coords. If a postcode doesn't exist in the DB postcode table, create it.

    Arguments:
    postcode {number} The postcode

    Returns:
    [Object] -- The postcode object if it exists, or a newly created postcode object. Return None if it wasn't able to be created.
    """
    
    # Check if the database postcode table has a record of the postcode and its coords.
    # If not, create a new postcode record by calling the API service and retrieving
    # coordinate data of the postcode
    postcode_obj = Postcode.query.get(postcode)

    if postcode_obj is None:
        print('get_postcode(): postcode ' + postcode + ' doesn\'t exist in postcodes table')
        
        if add_postcode_to_db(postcode):
            return Postcode.query.get(postcode) # Retrieve the newly created entry, as we need it for route creation
        else:
            print('get_postcode(): postcode ' + postcode + ' was not able to be added to the postcodes table')
            return None

    return postcode_obj



def add_routes_matrix(set_of_postcodes):
    print('add_routes_matrix===================================================================================')
    # Create a dictionary mapping all the postcodes to coordinates, with the key
    # being the coordinate
    dict_postcodes = dict()


    for postcode_tuple in set_of_postcodes:
        postcode_a_obj = get_postcode(postcode_tuple[0])
        postcode_b_obj = get_postcode(postcode_tuple[1])
        

        if postcode_a_obj is None:
            print('Error postcode_a_obj: ' + str(postcode_tuple[0]))
            continue

        if postcode_b_obj is None:
            print('Error postcode_b_obj: ' + str(postcode_tuple[1]))
            continue

        # Key: [long, lat], Value: Postcode object
        dict_postcodes[postcode_a_obj.long, postcode_a_obj.lat] = postcode_a_obj
        dict_postcodes[postcode_b_obj.long, postcode_b_obj.lat] = postcode_b_obj

    
    list_of_postcode_coords = list(dict_postcodes.keys())

    # Create a new geojson matrix object, passing the list of coordinates gained from
    # the dictionary as an argument
    matrix = GeoJSON_Route_Matrix(list_of_postcode_coords)

    # The matrix looks like so (note that an identical matrix is also created for duration):

    # distance      coords_1    coords_2    coords_3    coords_4    coords_5
    # coords_1      0           distance    distance    distance    distance
    # coords_2      distance    0           distance    distance    distance
    # coords_3      distance    distance    0           distance    distance
    # coords_4      distance    distance    distance    0           distance
    # coords_5      distance    distance    distance    distance    0


    # Iterate through all the rows and columns in the matrix, adding the distance
    # and duration for every single route between post codes, to the db
    
    if matrix.get_location_count() is None:
        return None

    row_and_column_count = matrix.get_location_count()
    for i in range(row_and_column_count):

        # Get the coordinates of location a, so that you can then find the postcode
        # object by searching the dictionary.
        loc_a = matrix.get_location_coordinates(i)
        loc_a_postcode_obj = dict_postcodes[loc_a]
        
        for j in range(row_and_column_count):

            # Get location b
            loc_b = matrix.get_location_coordinates(j)
            loc_b_postcode_obj = dict_postcodes[loc_b]

            # Ignore when the row and column are the same, as that essentially
            # means you're looking at distance and duration from location a to location a
            if i == j:
                continue

            # Check if route exists, as it may have been created as a previous matrix
            # was being processed
            if route_exists(loc_a_postcode_obj.postcode, loc_b_postcode_obj.postcode) is not None:
                continue

            # Check if any of the route's distances and durations were not able to be created 
            # between point A and point B by the API, and if so, continue
            if matrix.get_distance_between(i, j) is None:
                continue

            route = Route(
                point_a_postcode = loc_a_postcode_obj.postcode,
                point_a_region_name = loc_a_postcode_obj.region_name,
                # ORS API returns coords as [long, lat] as opposed to the common [lat, long]
                point_a_long = loc_a[0],
                point_a_lat = loc_a[1],

                point_b_postcode = loc_b_postcode_obj.postcode,
                point_b_region_name = loc_b_postcode_obj.region_name,
                # ORS API returns coords as [long, lat] as opposed to the common [lat, long]
                point_b_long = loc_b[0],
                point_b_lat = loc_b[1],
                
                route_distance_in_km = matrix.get_distance_between(i, j),
                estimated_duration_in_seconds = matrix.get_duration_between(i, j),
                last_updated = date.today()
            )

            try:
                db.session.add(route)
            except:
                # TODO: Add graceful error handling
                continue

    db.session.commit()

    return matrix
