"""
This file is used to retreive sensitive data from the hidden configs.json file
"""
import json

# Get sensitive data from the configs file
with open('configs.json') as json_file:
    configs = json.load(json_file)
    DB_STRING = configs["db_string"] # This is string used to connect to the AWS PostGres database
    API_KEY = configs["token_key"] # This is the API key used to access OpenRouteService's API
    SECRET_KEY = configs["secret_key"] # A secret key is required when if we want to implement session functionality in Flask
    DEFAULT_SENDER_EMAIL_ADDRESS = configs["default_sender_email"]
    SENDER_EMAIL_APP_PASSWORD = configs["email_sender_app_password"]