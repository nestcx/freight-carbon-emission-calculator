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

# Fuel economy of x truck.
# Given in litres per 100 kilometres (l/100km)
truck_fuel_economy = 47.619


def calculate_fuel_consumption(distance, load_weight):
    """Calculate fuel consumption based on a series of trip-specific factors.

    Keyword arguments:
    distance    -- trip distance given in kilometres.
    load_weight -- load weight in vehicle given in tonnes.

    In future, more factors will be added to this function to further increase 
    the accuracy of the fuel consumption estimate.
    """

    # For every tonne of load weight, 1.1% decrease in fuel economy
    load_weight_effect = load_weight * LOAD_WEIGHT_PERCENTAGE_DECREASE
    fuel_economy = truck_fuel_economy + ((load_weight_effect / 100) * truck_fuel_economy)

    # Distance calculation
    # Fuel economy converted from l/100km to l/km, multiplied by distance in kilometres.
    fuel_consumption = (fuel_economy / 100) * distance

    return fuel_consumption



def emission_calculation(gas_type, fuel_consumption):
    """Calculate emission for specific gas type based on fuel consumption.

    Estimates of emissions from the combustion of diesel oil are made by
    multiplying a physical quantity of fuel combusted by a fuel-specific
    energy content factor and a fuel-specific emission factor.

    This is performed for each relevant greenhouse gas.

    Fuel consumption is converted from litres to kilolitres.    
    """

    return ((fuel_consumption / 1000) * ENERGY_CONTENT_FACTOR * gas_type) / 1000


def calculate_emissions(distance, load_weight):
    """Calculate emissions for each gas type given a series of 
       trip-specific factors.

    This function is a wrapper for the API. It is the only function that needs
    to be called to calculate emissions. Consider this the only public function
    and the rest of the functions private.
    """

    # Fuel consumption must be calculated prior to calculation of greenhouse gas emissions.
    fuel_consumption = calculate_fuel_consumption(distance, load_weight)

    # The emission calculation is performed for each relevant greenhouse gas.
    emissions = {}
    emissions["carbon_dioxide_emission"] = emission_calculation(CARBON_DIOXIDE, fuel_consumption)
    emissions["methane_emission"] = emission_calculation(METHANE, fuel_consumption)
    emissions["nitrous_oxide_emission"] = emission_calculation(NITROUS_OXIDE, fuel_consumption)

    return emissions


test = calculate_emissions(877, 10)
print(test)