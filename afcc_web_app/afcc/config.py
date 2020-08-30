"""
This file is used to retreive sensitive data from the hidden configs.json file
"""
import json

# Get sensitive data from the configs file
with open('configs.json') as json_file:
    configs = json.load(json_file)
    DB_STRING = configs["db_string"]
    API_KEY = configs["token_key"]

