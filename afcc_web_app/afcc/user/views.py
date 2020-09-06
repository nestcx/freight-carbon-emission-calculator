'''
This file handles all user-related functionality
'''
from flask import Blueprint
from flask import request
from flask import render_template

from afcc.extensions import db, limiter
from afcc.user.models import User

# Used for exception handling regarding DB connection and queries
from sqlalchemy import exc

# Used for exception handling unique key violations. Note that sqlalchemy wraps psycopg2's exceptions and provides its own
from psycopg2.errors import UniqueViolation

# This does not need to be installed on your local machines as it is already a dependency for Flask and therefore already installed
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('user', __name__, static_folder='static', template_folder='templates')


# curl test:
# curl -d "username=burak&password=secret&email=burak@gmail.com" -X POST http://localhost:5000/user/
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
      # TODO: Return a html page indicating success
      return 'account created', 200

    # Check if a statement error occured because a user tried to create a new account with an email address
    # that already exists in the db. Note that we're using Sqlalchemy for ORM, and it uses Psycopg2 as an adapter
    # API for Postgres databases. This means that, among other things, Sqlalchemy wraps Psycopg2's exceptions and 
    # throws it's own. However Sqlalchemy doesn't provide a specific exception for Unique key violation, therefore, 
    # we have to retrieve Psycopg2's exception if we want to see if the user attempted to create a user with an
    # email address that already exists
    except exc.StatementError as e:
      # Retrieve the exception Psycopg2 threw, and see if it is a Unique key violation
      if isinstance(e.orig, UniqueViolation):
        return 'A user with this email address already exists', 409
      else:
        return 'An error occurred while trying to create your account. Please try again later', 500
    except Exception as e:
      # TODO: Redirect to the sign up page and provide the user with feedback
      return 'An error occurred while trying to create your account. Please try again later', 500
  else:
    # TODO: Redirect to the sign up page and provide the user with feedback
    return 'You need to enter username, password and email address', 400



# Display user details to the user
########################################################
# TODO: Implement Flask-security to ensure that only logged in users can view their own details
########################################################
@user_bp.route('/<username>', methods=['GET'])
def get_user(username):
  try:
    # Note that there is no need to sanitise inputs, as inputs are already parametised
    # by the db-API that SQLAlchemy calls. (As long as we don't write raw SQL ourself, of course)
    user = User.query.filter_by(username=username).first()
    if (user is not None):
      user.password = None
      return render_template('profile.html', data=user)
    else:
      return 'could not find that user in db'
  except:
    return 'an error occurred while trying to retrieve data from the database', 500



@user_bp.route('/<email>', methods=['POST'])
@limiter.limit('1/second;10/hour')
def update_user():
  pass



@user_bp.route('/login', methods=['POST'])
@limiter.limit('1/second;5/minute;15/hour')
def log_in():
  pass
