"""
This file is to test user related functionality. Spefically CRUD operations for users
"""
import pytest

from afcc import data_conversion

# CRUD - Create related tests
def test_new_user_should_be_created_with_correct_username_and_hashed_password():
  assert False

def test_user_should_not_be_created_if_required_inputs_are_missing():
  assert False

def test_system_should_not_create_user_if_email_address_doesnt_match_address_regex():
  assert False

 def test_system_can_handle_special_characters_in_username_and_password():
   assert False


# CRUD - Read related tests
def test_user_can_get_user_account_details():
  assert False


# CRUD - Update related tests
def test_user_can_update_their_account_details():
  assert False


# CRUD - Delete related tests
def test_user_can_delete_their_account():
  assert False

  