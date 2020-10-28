import requests
from flask import Blueprint, jsonify
from afcc import data_conversion
from afcc.models import Postcode
from afcc.extensions import db
from afcc.config import *

"""
The classes in this file are used to serve as a wrapper for the map API response JSON data. 
This should make it easier to switch APIs in the future, as only the wrapper classes would 
need to be changed in such an event.
"""

class GeoJSON_Route:
    """This class is used to store GeoJSON data about a route between 2 points
    """

    def __init__(self, start_coords, end_coords):

        # This is the amount of metres that the API service should look for a road from the point
        # of a coordinate. A larger number means that it would search a larger area when routing,
        # which means more often it will find successful route, but the algorithm might be a little
        # less accurate (though this is a non-issue in practice due to large distances between states)
        # In this case, a radius of 5,000 metres is used because some very rural areas may not
        # have a road within a close radius of the 'centre' coordinate of the region
        road_search_radius = 5000
        
        endpointURL = "https://api.openrouteservice.org/v2/directions/driving-hgv/geojson"
        
        headers = {
            'Authorization': API_KEY,
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Content-Type': 'application/json; charset=utf-8'}
            
        json = {
            "coordinates": [start_coords, end_coords],
            "instructions": False,
            "attributes": ["avgspeed"],
            "geometry_simplify": "false",
            "radiuses": [road_search_radius, road_search_radius]}  # Must specify radius for both points

        self.response = requests.post(endpointURL, headers=headers, json=json)
        self.geojson = self.response.json()

    def get_response(self):
        return self.response

    def get_geojson_data(self):
        return self.response.json()

    def get_distance(self):
        return self.geojson['features'][0]['properties']['summary']['distance']

    def get_duration(self):
        return self.geojson['features'][0]['properties']['summary']['duration']

    def get_duration_in_dhms(self):
        return data_conversion.convert_seconds_to_dhms(self.get_duration())

    def is_valid(self):
        try:
            if self.response.status_code == 200 and self.get_distance() is not None and self.get_duration() > 0 and self.get_duration is not None:
                return True
        except:
            return False


class GeoJSON_Address:
    """This class stores all possible addresses found for an inputted address. Its used for autosuggesting
    addresses to the user, but can also be used to find data for a specific address or postcode
    """

    def __init__(self, address, postcode=None):
        self.postcode = postcode

        # restrict all searches to addresses in Australia only.
        country = "AUS"

        endpointURL = "https://api.openrouteservice.org/geocode/search?api_key={}&text={}&boundary.country={}" \
            .format(API_KEY, address, country)
        self.response = requests.get(endpointURL)

        if self.response.status_code == 200:
            self.geojson_data = self.response.json()

    def get_postcode(self):
        return self.postcode

    # get_long, get_lat and get_address_name are used for when processing data for a singular address
    # (i.e: don't use these functions if you're working on the autosuggest feature)
    def get_long(self):
        return self.geojson_data["features"][0]["geometry"]["coordinates"][0]

    def get_lat(self):
        return self.geojson_data["features"][0]["geometry"]["coordinates"][1]

    def get_address_name(self):
        return self.geojson_data["features"][0]["properties"]["label"]

    # Get the number of found addresses for the given inputted address so far
    def get_address_count(self):
        return len(self.geojson_data["features"])

    # Return the actual geojson data
    def get_geojson_data(self):
        return self.geojson_data

    # This is use to retrieve the response sent by the API service
    def get_response(self):
        return self.response

    def is_valid(self):
        try:
            return self.response.status_code == 200 and self.get_long is not None and self.get_lat is not None and self.get_address_count() > 0
        except:
            return None


class GeoJSON_Route_Matrix:
    """This class is used to store the matrices of postcodes and route distances and durations between them.
    This class is built specifically for OpenRouteService's Matrix API call
    """

    def __init__(self, list_of_postcode_coords):

        self.list_of_postcode_coords = list_of_postcode_coords

        json = {
            "locations": self.list_of_postcode_coords,
            "metrics": ["distance", "duration"],
            "units": "km"}

        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': API_KEY,
            'Content-Type': 'application/json; charset=utf-8'
        }

        response = requests.post(
            'https://api.openrouteservice.org/v2/matrix/driving-hgv', json=json, headers=headers)

        self.geojson_data = response.json()

    def get_geojson_data(self):
        return self.geojson_data

    def get_location_coordinates(self, n):
        # Typecast to a tuple, as it would otherwise return a list, which is an inappropriate data type
        return tuple(self.geojson_data["metadata"]["query"]["locations"][n])

    # Note that the location count is effectively the amount of rows and columns
    # that the matrix will have.
    def get_location_count(self):
        try:
            return len(self.geojson_data["metadata"]["query"]["locations"])
        except:
            # TODO: Add logging here
            return None

    def get_distance_between(self, i, j):
        """Return the distance between coordinates for location and a and b, in kms

        """
        return self.geojson_data["distances"][i][j]

    def get_duration_between(self, i, j):
        return self.geojson_data["durations"][i][j]

    def is_valid(self, i, j):
        try:
            return self.get_distance_between(i, j) is not None and self.get_distance_between(i, j) > 0
        except:
            return False