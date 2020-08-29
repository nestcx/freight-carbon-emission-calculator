"""
This file is to test functionality related to user authentication and security measures
"""
import pytest

from afcc import data_conversion

def test_user_should_authenticate_with_valid_username_valid_password():
  assert False


def test_user_should_not_authenticate_with_valid_username_invalid_password():
  assert False


def test_user_can_sign_out():
  assert False


# This test is specifically to ensure that upon signing out, users can't access stuff like user account page.
def test_features_requiring_authentication_cant_be_accessed_by_users_that_arent_logged_in():
  assert False


def test_user_cant_sign_in_using_multiple_accounts_in_same_browser():
  assert False


def test_user_cant_inject_SQL():
  assert False
