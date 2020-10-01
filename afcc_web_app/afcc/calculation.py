from flask import request
from flask import jsonify
from flask import Blueprint
from flask import render_template

from afcc import maproutes
from afcc import data_conversion


calculation_bp = Blueprint("calculation", __name__, url_prefix='/calculation', template_folder='templates', static_folder='static')


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


def calculate_fuel_consumption(truck_fuel_economy, distance, load_weight, load_weight_unit):
    """Calculate fuel consumption based on a series of trip-specific factors.

    Keyword arguments:
    truck_fuel_economy  -- fuel economy of truck given in litres per 100km (l/100km)
    distance            -- trip distance given in kilometres.
    load_weight         -- load weight in vehicle given in tonnes.
    load_weight_unit    -- load weight unit: 'kilogram', or 'tonne'.

    Returns:
    fuel_consumption       -- litres
    adjusted_fuel_economy  -- litres per 100km (l/100km)

    In future, more factors will be added to this function to further increase 
    the accuracy of the fuel consumption estimate.
    """

    # Convert load_weight to tonnes for the calculation.
    if load_weight_unit == 'kilogram':
        load_weight = data_conversion.convert_kilogram_to_tonnes(load_weight)

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


def calculate_emissions(truck_fuel_economy, distance, load_weight, load_weight_unit):
    """Calculate emissions for each gas type given a series of 
       trip-specific factors.

    This function is a wrapper for the API. It is the only function that needs
    to be called to calculate emissions. Consider this the only public function
    and the rest of the functions private.
    """

    # Fuel consumption must be calculated prior to calculation of greenhouse gas emissions.
    fuel_consumption = calculate_fuel_consumption(truck_fuel_economy, distance, load_weight, load_weight_unit)

    # The emission calculation is performed for each relevant greenhouse gas.
    calculation_data = {}
    calculation_data["carbon_dioxide_emission"] = emission_calculation(CARBON_DIOXIDE, fuel_consumption["fuel_consumption"])
    calculation_data["methane_emission"] = emission_calculation(METHANE, fuel_consumption["fuel_consumption"])
    calculation_data["nitrous_oxide_emission"] = emission_calculation(NITROUS_OXIDE, fuel_consumption["fuel_consumption"])
    calculation_data["distance"] = distance
    calculation_data["fuel_consumptionn"] = fuel_consumption["fuel_consumption"]
    calculation_data["adjusted_fuel_economy"] = fuel_consumption["adjusted_fuel_economy"]
    
    return calculation_data


