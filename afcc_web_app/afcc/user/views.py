'''
This file handles all user-related functionality
'''
from flask import Blueprint
from flask import request

from afcc.extensions import db, limiter
from afcc.user.models import User

# This does not need to be installed on your local machines as it is already a dependency for Flask and therefore already installed
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('user', __name__, static_folder='static', template_folder='templates')


# curl test:
# curl -d 'username=burak&password=secret&email=burak@gmail.com' -X POST http://localhost:5000/user/
@user_bp.route('/', methods=['POST'])
@limiter.limit('1/second;5/day') # Don't allow users to try create too many accounts, as a legitimate user has no reason to
def create_user():
  data = request.form
  username = data.get('username')
  password = data.get('password')
  email = data.get('email')

  # Ensure that user has entered all required data
  if (username is not None and password is not None and email is not None):
    pw_hash = generate_password_hash(password) # pbkdf2:sha256 is the encryption method used if none is specified. 
    new_user = User(username=username, password=pw_hash, email=email)
    
    # Try adding the user to the database, and catch any potential errors
    try:
      db.session.add(new_user)
      db.session.commit()
      return 'account created', 200
    except:
      return 'An error occurred while trying to create your account. Please try again later', 500
  else:
    return 'You need to enter username, password and email address', 400


@user_bp.route('/<email>', methods=['GET'])
def get_user():

  pass


@user_bp.route('/<email>', methods=['POST'])
@limiter.limit('1/second;10/hour')
def update_user():
  pass


@user_bp.route('/login', methods=['POST'])
@limiter.limit('1/second;5/minute;15/hour')
def log_in():
  pass
