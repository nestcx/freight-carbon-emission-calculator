from flask import request
from flask import jsonify
from flask import Blueprint
from flask import render_template

from afcc import maproutes
from afcc import data_conversion


calculation_bp = Blueprint("calculation", __name__, url_prefix='/calculation', template_folder='templates', static_folder='static')


###############
# BEGIN VIEWS #
###############

# API ENDPOINT #1
# - using co-ordinates

# curl test:
# curl --header "Content-Type: application/json" --request POST --data '{"loadWeight": 7.5, "startCoords":"144.910115,-37.593950", "endCoords":"145.028376,-37.723944"}' http://127.0.0.1:5000/calculation/coordinates

@calculation_bp.route("/coordinates", methods=["POST"])
def emissions():

    if not request.is_json:
        return "ERROR", 400

    request_data = request.get_json()

    if ('startCoords' not in request_data or 'endCoords' not in request_data or 'loadWeight' not in request_data):
        return "ERROR", 400


    geoJSONData = maproutes.get_route(request_data["startCoords"], request_data["endCoords"])

    length_of_route = data_conversion.metre_to_kilometre(maproutes.get_length_of_route(geoJSONData))
    duration_of_route = maproutes.get_duration_of_route(geoJSONData)

    load_weight = request_data["loadWeight"]

    fuel_economy = 18.1

    calculation_data = calculate_emissions(fuel_economy, length_of_route, load_weight)
    calculation_data["duration_of_route"] = duration_of_route

    response = {}

    response["emissions"] = {}
    response["emissions"]["carbon_dioxide_emission"] = calculation_data["carbon_dioxide_emission"]
    response["emissions"]["methane_emission"] = calculation_data["methane_emission"]
    response["emissions"]["nitrous_oxide_emission"] = calculation_data["nitrous_oxide_emission"]

    response["fuel_consumption"] = calculation_data["fuel_consumptionn"]
    response["adjusted_fuel_economy"] = calculation_data["adjusted_fuel_economy"]
    response["distance"] = data_conversion.metre_to_kilometre(length_of_route)
    response["duration"] = data_conversion.convert_seconds_to_dhms(duration_of_route)

    return jsonify(response)


# API ENDPOINT #2
# - using given addresses

# curl test:
# curl --header "Content-Type: application/json" --request POST --data '{"loadWeight": 7.5, "startAddress":"preston", "endAddress":"10 smith street collingwood"}' http://127.0.0.1:5000/calculation/address

@calculation_bp.route("/address", methods=["POST"])
def emissions_by_address():

    if not request.is_json:
        return "ERROR", 400

    request_data = request.get_json()

    if ('startAddress' not in request_data or 'endAddress' not in request_data or 'loadWeight' not in request_data):
        return "ERROR", 400


    startAddressInfo = maproutes.search_address(request_data["startAddress"])
    endAddressInfo = maproutes.search_address(request_data["endAddress"])

    startAddressValidated = startAddressInfo["features"][0]["properties"]["label"]
    endAddressValidated = endAddressInfo["features"][0]["properties"]["label"]

    startAddressCoordinates = startAddressInfo["features"][0]["geometry"]["coordinates"]
    endAddressCoordinates = endAddressInfo["features"][0]["geometry"]["coordinates"]

    #fix, this is kinda yuck
    geoJSONData = maproutes.get_route(str(startAddressCoordinates[0]) + "," + str(startAddressCoordinates[1]), str(endAddressCoordinates[0]) + "," + str(endAddressCoordinates[1]))

    length_of_route = data_conversion.metre_to_kilometre(maproutes.get_length_of_route(geoJSONData))
    duration_of_route = maproutes.get_duration_of_route(geoJSONData)

    load_weight = request_data["loadWeight"]

    fuel_economy = 18.1
    
    calculation_data = calculate_emissions(fuel_economy, length_of_route, load_weight)



    # create response with data conversion

    response = {}

    response["emissions"] = {}
    response["emissions"]["carbon_dioxide_emission"] = calculation_data["carbon_dioxide_emission"]
    response["emissions"]["methane_emission"] = calculation_data["methane_emission"]
    response["emissions"]["nitrous_oxide_emission"] = calculation_data["nitrous_oxide_emission"]

    response["fuel_consumption"] = calculation_data["fuel_consumptionn"]
    response["adjusted_fuel_economy"] = calculation_data["adjusted_fuel_economy"]
    response["distance"] = length_of_route
    response["duration"] = data_conversion.convert_seconds_to_dhms(duration_of_route)

    response["location"] = {}
    response["location"]["start_location"] = {}
    response["location"]["end_location"] = {}
    response["location"]["start_location"]["address"] = startAddressValidated
    response["location"]["start_location"]["coordinate"] = startAddressCoordinates
    response["location"]["end_location"]["address"] = endAddressValidated
    response["location"]["end_location"]["coordinate"] = endAddressCoordinates

    return response


###############
#  END VIEWS  #
###############



# Emission factor of each gas type
# Transport equipment type: Heavy vehicles conforming to Euro IV+ design standards
# Fuel combusted: Diesel oil
# Given in kg CO2-e/GJ
CARBON_DIOXIDE = 69.9
METHANE = 0.06
NITROUS_OXIDE = 0.5

# Energy content factor of diesel oil
# Transport equipment type: Heavy vehicles conforming to Euro IV+ design standards
# Given in GJ/kL
ENERGY_CONTENT_FACTOR = 38.6

LOAD_WEIGHT_PERCENTAGE_DECREASE = 1.1


def calculate_fuel_consumption(truck_fuel_economy, distance, load_weight):
    """Calculate fuel consumption based on a series of trip-specific factors.

    Keyword arguments:
    truck_fuel_economy  -- fuel economy of truck given in litres per 100km (l/100km)
    distance            -- trip distance given in kilometres.
    load_weight         -- load weight in vehicle given in tonnes.

    In future, more factors will be added to this function to further increase 
    the accuracy of the fuel consumption estimate.
    """

    # For every tonne of load weight, 1.1% decrease in fuel economy
    load_weight_effect = load_weight * LOAD_WEIGHT_PERCENTAGE_DECREASE
    fuel_economy = truck_fuel_economy + ((load_weight_effect / 100) * truck_fuel_economy)

    # Distance calculation
    # Fuel economy converted from l/100km to l/km, multiplied by distance in kilometres.
    fuel_consumption = (fuel_economy / 100) * distance

    fuel_calculation = {}
    fuel_calculation["fuel_consumption"] = fuel_consumption
    fuel_calculation["adjusted_fuel_economy"] = fuel_economy

    return fuel_calculation



def emission_calculation(gas_type, fuel_consumption):
    """Calculate emission for specific gas type based on fuel consumption.

    Estimates of emissions from the combustion of diesel oil are made by
    multiplying a physical quantity of fuel combusted by a fuel-specific
    energy content factor and a fuel-specific emission factor.

    This is performed for each relevant greenhouse gas.

    Fuel consumption is converted from litres to kilolitres.    
    """

    return ((fuel_consumption / 1000) * ENERGY_CONTENT_FACTOR * gas_type) / 1000


def calculate_emissions(truck_fuel_economy, distance, load_weight):
    """Calculate emissions for each gas type given a series of 
       trip-specific factors.

    This function is a wrapper for the API. It is the only function that needs
    to be called to calculate emissions. Consider this the only public function
    and the rest of the functions private.
    """

    # Fuel consumption must be calculated prior to calculation of greenhouse gas emissions.
    fuel_consumption = calculate_fuel_consumption(truck_fuel_economy, distance, load_weight)

    # The emission calculation is performed for each relevant greenhouse gas.
    calculation_data = {}
    calculation_data["carbon_dioxide_emission"] = emission_calculation(CARBON_DIOXIDE, fuel_consumption["fuel_consumption"])
    calculation_data["methane_emission"] = emission_calculation(METHANE, fuel_consumption["fuel_consumption"])
    calculation_data["nitrous_oxide_emission"] = emission_calculation(NITROUS_OXIDE, fuel_consumption["fuel_consumption"])
    calculation_data["distance"] = distance
    calculation_data["fuel_consumptionn"] = fuel_consumption["fuel_consumption"]
    calculation_data["adjusted_fuel_economy"] = fuel_consumption["adjusted_fuel_economy"]
    
    print(fuel_consumption)
    return calculation_data


def get_emission_calculation(start_address,end_address,item_weight,item_quantity):
    ''' Method to get the emission calculation

        Keyword Variables:
        length_of_data -- Checks the number of shipments uploaded in the excel/csv file
        emis_temp_array -- temporary array to store responses of emissions from caculation py file 

    '''

    calculation_data={}

    calculation_data['origin']=start_address
    calculation_data['destination']=end_address
    calculation_data['itemWeight']=item_weight
    calculation_data['itemQuantity']=item_quantity

    startAddressInfo = maproutes.search_address(calculation_data['origin'])
    endAddressInfo = maproutes.search_address(calculation_data['destination'])

    startAddressCoordinates = startAddressInfo["features"][0]["geometry"]["coordinates"]
    endAddressCoordinates = endAddressInfo["features"][0]["geometry"]["coordinates"]

    calculation_data['origincoords']=(startAddressCoordinates)
    calculation_data['destcoords']=(endAddressCoordinates)

    geoJSONData = maproutes.get_route(str(startAddressCoordinates[0]) + "," + str(startAddressCoordinates[1]), str(endAddressCoordinates[0]) + "," + str(endAddressCoordinates[1]))

    calculation_data['distance']=(data_conversion.metre_to_kilometre(maproutes.get_length_of_route(geoJSONData)))
    calculation_data['duration']=(maproutes.get_duration_of_route(geoJSONData))
    

    calculation_data['emission']=(calculate_emissions(18.1,calculation_data['distance'],(calculation_data['itemQuantity'])*(calculation_data['itemWeight'])))

    return calculation_data

