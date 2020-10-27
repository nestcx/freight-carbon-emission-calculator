import pytest

from afcc import data_conversion

# Assert that 1000 kg is equal to 1 tonne. Test passes if conversion works as expected
def test_1000_kg_is_1_tonne():
  result = data_conversion.convert_kilogram_to_tonnes(1000)
  assert result == 1

# Test that the function correctly returns floats, not just integers
def test_500_kg_is_half_a_tonne():
  result = data_conversion.convert_kilogram_to_tonnes(500)
  assert result == 0.5

# The data_conversion_function_should throw an exception when a string is inputted
def test_data_conversion_doesnt_allow_strings():

  with pytest.raises(Exception):
    data_conversion.convert_kilogram_to_tonnes("hello")