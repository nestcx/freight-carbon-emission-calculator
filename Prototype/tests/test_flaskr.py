import pytest

from flaskr import algorithm

def test_sum_2_plus_2_is_4():
  result = algorithm.sum(2, 2)
  assert result == 4

def test_sum_2_plus_2_is_5():
  result = algorithm.sum(2, 2)
  assert result == 5