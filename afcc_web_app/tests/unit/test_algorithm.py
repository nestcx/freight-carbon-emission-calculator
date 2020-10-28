from afcc import calculation

"""
Once the algorithm is developed, the outputs may vary based on predictions. This
means that we may not be able to use a test oracle to determine if the algorithm
is working correctly. Instead, we will do metamorphic testing by running multiple
tests on each function, using slightly altered input values, and see if the relationship
between changed inputs and resulting output make sense.

For example; we'll run a test to determine fuel consumption of a 100km trip of a
certain truck type, then run the same test with a slightly higher trip length of
110km, and see if the predicted fuel consumption for a 110km trip is about
10% higher to the predicted fuel consumption for a 100km trip. 

By testing the relationship between these input and output values, we can't determine if 
the algorithm is working 100%, but we can reasonably assume that it is working as intended.
"""


def test_fuel_consumption_metamorphic_relations_are_sensible():

  # First trip has a fuel economy of 8, is 100km long, and carrying 10 tonnes
  first_result = calculation.calculate_fuel_consumption(8, 100, 10, 'tonne')

  # 10km longer distance
  second_result = calculation.calculate_fuel_consumption(8, 110, 10, 'tonne')

  assert first_result['fuel_consumption'] != 0
  assert second_result['fuel_consumption'] != 0

  # First result should be lower, as the only variable that has changed is distance, and its shorter
  assert first_result['fuel_consumption'] < second_result['fuel_consumption']

  # Now see if the difference in results seems sensible. Do this by checking the difference
  # in results and seeing if there's a larger than expected difference.
  difference = second_result['fuel_consumption'] - first_result['fuel_consumption']

  # If the difference in results is under 20%, count as passed
  assert difference < (second_result['fuel_consumption'] / 5)

