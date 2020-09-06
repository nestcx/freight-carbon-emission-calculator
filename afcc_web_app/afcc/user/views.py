'''
This file handles all user-related functionality
'''
from flask import Blueprint, request, render_template, redirect, url_for, flash
from afcc.extensions import db, limiter
from afcc.user.models import User
from afcc.user.forms import LoginForm, SignupForm

# Used for exception handling regarding DB connection and queries
from sqlalchemy import exc

# Used for exception handling unique key violations. Note that sqlalchemy wraps psycopg2's exceptions and provides its own
from psycopg2.errors import UniqueViolation

# This does not need to be installed on your local machines as it is already a dependency for Flask and therefore already installed
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import current_user, login_user, login_required, logout_user

user_bp = Blueprint('user', __name__, static_folder='static', template_folder='templates')



# curl test:
# curl -d "username=burak&password=secret&email=burak@gmail.com" -X POST http://localhost:5000/user/
@user_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit('5/second;10/day') # Don't allow users to try create too many accounts, as a legitimate user has no reason to
def create_user():
  # If user is already authenticated, no use showing this page
  if current_user.is_authenticated:
      return redirect(url_for('index'))

  signup_form = SignupForm()
  
  if signup_form.validate_on_submit():
    pw_hash = generate_password_hash(signup_form.password.data) # pbkdf2:sha256 is the encryption method used if none is specified. 
    new_user = User(username=signup_form.username.data, password=pw_hash, email=signup_form.email.data)

    # Try adding the user to the database, and catch any potential errors
    try:
      db.session.add(new_user)
      db.session.commit()
      # TODO: Return a html page indicating success
      return 'account created', 200

    # Check if a statement error occured from a user who tried to create a new account with an email address
    # that already exists in the db. Note that we're using Sqlalchemy for ORM, and it uses Psycopg2 as an adapter
    # API for Postgres databases. This means that, among other things, Sqlalchemy wraps Psycopg2's exceptions and 
    # throws it's own. However Sqlalchemy doesn't provide a specific exception for Unique key violation, therefore, 
    # we have to retrieve Psycopg2's exception if we want to see if the user attempted to create a user with an
    # email address that already exists
    except exc.StatementError as e:
      # Retrieve the exception Psycopg2 threw, and see if it is a Unique key violation
      if isinstance(e.orig, UniqueViolation):
        flash('User already exists')
        return redirect(url_for('.create_user'))
        return 'A user with this email address already exists', 409
      else:
        return 'An error occurred while trying to create your account. Please try again later', 500
    except Exception as e:
      # TODO: Redirect to the sign up page and provide the user with feedback
      return 'An error occurred while trying to create your account. Please try again later', 500

  return render_template('signup.html', form=signup_form)




# Display user account details to the user, if they're logged in
@user_bp.route('/<username>', methods=['GET'])
@login_required
def display_user_details(username):
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




@user_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('1/second;5/minute;15/hour')
def log_in():
  # If user is already authenticated, no use showing this page
  if current_user.is_authenticated:
      return redirect(url_for('index'))

  login_form = LoginForm()
  if login_form.validate_on_submit():
    user = User.query.filter_by(email=login_form.email.data).first() # Get the user from the DB using email address
    if user is not None:
      if user.check_password(login_form.password.data): # Ensure that the password the user entered is correct
        login_user(user)
        return redirect(url_for('index'))
      else:
        return 'Password is incorrect', 401
    else:
      return 'User does not exist', 401

  return render_template('login.html', form=login_form)




@user_bp.route('/logout' , methods=['GET'])
def log_out():
  logout_user()
  return redirect(url_for('index'))
