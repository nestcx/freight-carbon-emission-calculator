'''
This file handles all user-related functionality
'''
from flask import Blueprint, request, render_template, redirect, url_for, flash
from afcc.extensions import db, limiter, login
from afcc.user.models import User
from afcc.user.forms import LoginForm, SignupForm
from afcc.user.email_verify import generate_token_for_verification, confirm_token
# Used for exception handling regarding DB connection and queries
from sqlalchemy import exc
# Used for exception handling unique key violations. Note that sqlalchemy wraps psycopg2's exceptions and provides its own
from psycopg2.errors import UniqueViolation

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, login_required, logout_user

user_bp = Blueprint('user', __name__, static_folder='static', template_folder='templates')

@user_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit('5/second;10/day') # Don't allow users to try create too many accounts, as a legitimate user has no reason to
def create_user():
  # If user is already authenticated, no use showing this page
  if current_user.is_authenticated:
      return redirect(url_for('index'))

  # Create a new SignupForm object from the SignupForm class found in user/forms.py
  signup_form = SignupForm()

  # If the validators specified in the class'es input field pass   
  if signup_form.validate_on_submit():
    # Hash the password the user inputted, and create a new user
    pw_hash = generate_password_hash(signup_form.password.data) # pbkdf2:sha256 is the encryption method used if none is specified. 
    new_user = User(username=signup_form.username.data, password=pw_hash, email=signup_form.email.data)

    # Try adding the user to the database, and catch any potential errors
    try:
      db.session.add(new_user)
      db.session.commit()
      # TODO: Add email verification
      # token = generate_token_for_verification(new_user.email)
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

        # Flash a message. This means that when the sign up page is being generated via the template, it will
        # check if there are any flash messages, and if so, create a new element and display those flash messages
        flash('A user with this email address already exists')
        # Redirect back to the signup page, which is the route that calls create_user (ie. the function this code is in)
        return redirect(url_for('.create_user'))
      else:
        # TODO: Add error logging here, to log all exceptions that have occured and what times
        flash('An error occurred while trying to create your account. Please try again later')
    except Exception as e:
        # TODO: Add error logging here, to log all exceptions that have occured and what times
        flash('An error occurred while trying to create your account. Please try again later')

  return render_template('signup.html', form=signup_form)


# Verify the user's email address when they click on a link in the email
################################
#TODO: Add code to this function
################################
@user_bp.route('/verify/<token>')
def verify_token(token):
  try:
    pass
  except:
    pass



# Display user account details to the user, if they're logged in
@user_bp.route('/', methods=['GET'])
@login_required
def display_user_details():
  # If the user is logged in, we search the db for the record using their email address
  try:
    user = User.query.filter_by(email=current_user.email).first()
    user.password = None
    return render_template('profile.html', data=user)
  # Something has gone seriously wrong if this exception is called. Redirect to the generic error page
  except Exception as e:
    # TODO: Add logging to log all exceptions
    flash('An error has occured when trying to access your user details')
    return redirect(url_for('display_error_page'))



@user_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('1/second;5/minute;15/hour')
def log_in():
  # If user is already authenticated, no use showing this page
  if current_user.is_authenticated:
      return redirect(url_for('index'))

  login_form = LoginForm()

  if login_form.validate_on_submit():
    try:
      user = User.query.filter_by(email=login_form.email.data).first() # Get the user from the DB using email address
    except:
      flash('The user does not exist')
      return redirect(url_for('log_in')) # Redirect back to login page to provide the user with feedback

      if user.check_password(login_form.password.data): # Ensure that the password the user entered is correct
        login_user(user)
        return redirect(url_for('index'))
      else:
        flash('The password or email address is incorrect')
        return redirect(url_for('log_in'))


  return render_template('login.html', form=login_form)



@user_bp.route('/logout' , methods=['GET'])
def log_out():
  logout_user()
  return redirect(url_for('index'))



# The login manager calls this when an unauthenticated user tries to access 
# a page that requires them to be logged in. Do this to display a more 
# user-friendly page, rather than the one Flask-login provides by default
@login.unauthorized_handler
def unauthorized():
  return render_template('authenticationrequired.html')