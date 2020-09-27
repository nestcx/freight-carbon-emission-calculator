"""
This file is to test functionality related to user authentication and security measures
"""
import pytest
from flask import Flask, request
from afcc import create_app
from flask_login import current_user, login_user, login_required, logout_user


@pytest.fixture
def app():
  """Create a new app instance for each test"""
  app = create_app()
  app.config['WTF_CSRF_ENABLED'] = False
  yield app

@pytest.fixture
def client(app):
  """Create a test client for the app when testing"""
  return app.test_client()


def test_user_can_access_login_page(client):
  rv = client.get('/user/login')
  assert rv.status_code == 200


def test_user_should_authenticate_with_valid_username_valid_password(client):
  
  # Check that a user can't already access restricted pages if they're not logged in
  response = client.get('/user/', follow_redirects=True)
  assert response.status_code == 401

  # Login the user
  response = client.post('/user/login', data=dict(
    email='testuser@gmail.com',
    password='testuser@gmail.com'
  ), follow_redirects=False)


  assert response.status_code == 302 # Check that it redirected to login

  # Check to see if user can now access a protected page
  response = client.get('/user/')
  assert response.status_code == 200 


def test_user_should_not_authenticate_with_valid_username_invalid_password(client):
  response = client.post('/user/login', data=dict(
    email='testuser@gmail.com',
    password='wrongpassword'
  ), follow_redirects=True)
  
  # Ensure that user can't access a protected page
  response = client.get('/user/')
  assert response.status_code == 401


# def test_user_can_sign_out():
#   assert False


# def test_passwords_should_be_case_sensitive():
#   assert False

# # This test is specifically to ensure that upon signing out, users can't access stuff like user account page.
# def test_features_requiring_authentication_cant_be_accessed_by_users_that_arent_logged_in():
#   assert False


# def test_user_cant_sign_in_using_multiple_accounts_in_same_browser():
#   assert False


# def test_user_cant_inject_SQL():
#   assert False


# def test_system_allows_no_more_than_one_attempt_per_second_for_username():
#   assert False


# def test_system_allows_no_more_than_five_attempts_per_minute_for_username():
#   assert False


# def test_system_allows_no_more_than_fifteen_attempts_per_hour_for_username():
#   assert False


# def test_system_allows_no_more_than_one_attempt_per_second_for_ip_address():
#   assert False


# def test_system_allows_no_more_than_five_attemps_per_minute_for_ip_address():
#   assert False


# def test_system_allows_no_more_than_fifteen_attempts_per_hour_for_ip_adress():
#   assert False
