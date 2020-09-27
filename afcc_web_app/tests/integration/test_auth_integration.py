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
  response = client.get('/user/login')
  assert response.status_code == 200


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


def test_user_should_not_authenticate_if_no_inputs_are_provided(client):
  response = client.post('/user/login', data=dict(
      email='',
      password=''
    ), follow_redirects=True)
    
  # Ensure that user can't access a protected page
  response = client.get('/user/')
  assert response.status_code == 401


def test_user_should_not_authenticate_if_nonexistant_email_address_is_entered(client):
  response = client.post('/user/login', data=dict(
      email='thisemaildoesntexist@nonexistantemail.com',
      password=''
    ), follow_redirects=True)
    
  # Ensure that user can't access a protected page
  response = client.get('/user/')
  assert response.status_code == 401


def test_user_should_not_authenticate_with_valid_username_invalid_password(client):
  response = client.post('/user/login', data=dict(
    email='testuser@gmail.com',
    password='wrongpassword'
  ), follow_redirects=True)
  
  # Ensure that user can't access a protected page
  response = client.get('/user/')
  assert response.status_code == 401


def test_user_can_sign_out(client):
  # Login the user
  response = client.post('/user/login', data=dict(
    email='testuser@gmail.com',
    password='testuser@gmail.com'
  ), follow_redirects=False)

  # Check to see if user can now access a protected page
  response = client.get('/user/')
  assert response.status_code == 200

  # Log the user out and see if they can still access the protected page
  client.get('/user/logout')
  response = client.get('/user/')
  assert response.status_code == 401


def test_user_login_attempts_are_limited_to_ten_per_minute(client):
  for i in range(0, 20):
    response = client.get('/user/login')
    # Eventually the server should respond with the status code indicating too many requests
    if response.status_code == 429:
      assert True
      return
  
  assert False


def test_user_signup_attempts_are_limited(client):
  for i in range(0, 20):
    response = client.get('/user/signup')
    # Eventually the server should respond with the status code indicating too many requests
    if response.status_code == 429:
      assert True
      return
  
  assert False


def test_user_can_update_their_account_details(app, client):
  with app.test_request_context():
    # Login the user
    client.post('/user/login', data=dict(
      email='testuser@gmail.com',
      password='testuser@gmail.com'
    ), follow_redirects=False)


    # login_user(email='testuser@gmail.com', password='testuser@gmail.com')
    print(current_user)
    assert current_user is not None
    # assert current_user.username == 'testuser@gmail.com'

    # response = client.post('/user/edit', data=dict(
    #   username='superuser'
    # ))
  # assert False


def test_user_can_update_their_password(client):
  assert False


def test_user_can_delete_their_account(client):
  assert False


def test_system_sends_verification_email(client):
  assert False

