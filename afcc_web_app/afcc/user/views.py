'''
This file handles all user-related functionality
'''
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from afcc.extensions import db, limiter, login_manager
from afcc.user.models import User
from afcc.user.forms import LoginForm, SignupForm
from afcc.user.email_verify import generate_token_for_verification, confirm_token
from afcc.user.email_sender import send_confirmation_email
from afcc.decorators import email_verification_required

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, login_required, logout_user

user_bp = Blueprint('user', __name__, url_prefix='/user',
                    static_folder='static', template_folder='templates')


# The user signup route. Display the webpage when a GET request is sent.
# If a POST request is sent, that means the user submitted the form, so
# try process it.
@user_bp.route('/signup', methods=['GET', 'POST'])
# Don't allow users to try create too many accounts, as a legitimate user has no reason to
@limiter.limit('10/minute;10/day')
def create_user():
    # If user is already authenticated, no use showing this page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Create a new SignupForm object from the SignupForm class found in user/forms.py
    signup_form = SignupForm()

    # If the request is a POST request, that means that a form has been submitted.
    # Check if the validators specified in the SignupForm class all pass, and if so, continue.
    if signup_form.validate_on_submit():
        # Hash the password the user inputted, and create a new user
        # pbkdf2:sha256 is the encryption method used if none is specified.
        pw_hash = generate_password_hash(signup_form.password.data)
        new_user = User(username=signup_form.username.data,
                        password=pw_hash, email=signup_form.email.data)

        # Try adding the user to the database, and catch any potential errors
        try:
            # See if a user of the given email address already exist sexists
            user_exists = User.query.filter_by(
                email=signup_form.email.data).first()

            if user_exists is None:  # A user with the email address wasn't found
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                # Create the verification token which will be sent as a link in the email address
                verification_token = generate_token_for_verification(new_user.email)

                # The html template used to generate the email requires a confirmation url to display a link to the user
                confirmation_url = url_for('.verify_email', token=verification_token, _external=True)
                
                # Render the html, which is then content of the email.
                email_content = render_template('email/verifyemailaddress.html', confirmation_url=confirmation_url)
                send_confirmation_email(new_user.email, email_content)

                # Indicate to the user that they have created an account
                return render_template('signupsuccess.html')
            else:
                # Add a flash message and redirect the user back to the signup page. The templating
                # engine will check for any flash messages when constructing the html page, and if a message
                # is found, it will display it to the user
                flash('A user with that email address already exists')
                return redirect(url_for('.create_user'))
        except Exception as e:
            print(e)
            # TODO: Add exception logging
            flash('An error has occurred. Please try again later')
            return redirect(url_for('.create_user'))

    # If there are validation errors when the user submitted the form, display
    # them as feedback to the user
    if len(signup_form.errors) != 0:
        for error in signup_form.errors:
            for msg in signup_form.errors[error]:
                flash(msg)

    return render_template('signup.html', form=signup_form)



# Verify the user's email address when they click on a link in the email
@user_bp.route('/verify/<token>')
def verify_email(token):
    # Try confirm that the token is valid
    
    try:
        # Call the email_verify file's confirm_token function to verify that the token is still valid
        email = confirm_token(token)

        if email is False:
            flash('The token is either invalid or expired')
            return render_template('emailconfirmation.html')

        # Log the user in when they click on the link
        user = User.query.filter_by(email=email).first()
        login_user(user)

        # Check to see if the logged in user's email address has already been verified, 
        # as they don't need to verify again
        if current_user.email_verified:
            flash('Your account has already been verified')
            return render_template('emailconfirmation.html')

        # Verify the user
        else:
            current_user.email_verified = True
            db.session.add(current_user)
            db.session.commit()
            flash('Your email address has been verified. Thank you')
            return render_template('emailconfirmation.html')
            
    except:
        flash('The token is either invalid or expired')
        return render_template('emailconfirmation.html')



# Display user account details to the user, if they're logged in
@user_bp.route('/', methods=['GET'])
@login_required
@email_verification_required # The user needs to have verified their email address
def display_user_details():
    # If the user is logged in, we search the db for the record using their email address
    try:
        user = User.query.filter_by(email=current_user.email).first()

        # Remove the password before sending the user data to the client, otherwise a malicious
        # user can steal the password hash
        user.password = None
        return render_template('profile.html', data=user)
    # Something has gone seriously wrong if this exception is called. Redirect to the generic error page
    except Exception as e:
        # TODO: Add logging to log all exceptions
        flash('An error has occured when trying to access your user details')
        return redirect(url_for('display_error_page'))



@user_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10/minute;15/hour')
def log_in():
    # If user is already authenticated, no use showing this page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        try:
            # Get the user from the DB using email address
            user = User.query.filter_by(email=login_form.email.data).first()
            # Ensure that the password the user entered is correct
            if user.check_password(login_form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('The password or email address is incorrect')
                return redirect(url_for('.log_in'))
        except:
            flash('The user does not exist')
            # Redirect back to login page to provide the user with feedback
            return redirect(url_for('.log_in'))

    # If there are validation errors when the user submitted the form, display
    # them as feedback to the user
    if len(login_form.errors) != 0:
        for error in login_form.errors:
            for msg in login_form.errors[error]:
                flash(msg)
    return render_template('login.html', form=login_form)



@user_bp.route('/logout', methods=['GET'])
def log_out():
    logout_user()
    return redirect(url_for('index'))



# This route is to allow the user to request another link to verify their email,
# just in case they may not have received it
@user_bp.route('/resend_verification')
@login_required
def resend_verification():

    # Create the verification token which will be sent as a link in the email address
    verification_token = generate_token_for_verification(current_user.email)

    # The html template used to generate the email requires a confirmation url to display a link to the user
    confirmation_url = url_for('.verify_email', token=verification_token, _external=True)

    # Render the html, which is then content of the email.
    email_content = render_template('email/verifyemailaddress.html', confirmation_url=confirmation_url)
    send_confirmation_email(current_user.email, email_content)

    return render_template('verificationemailsent.html')



# This is called by the custom made decorator whenever an unverified user tries to 
# access a page that requires email verification
@user_bp.route('/email_not_verified')
def email_not_verified():  
    return render_template('verificationrequired.html')



# The login manager calls this when an unauthenticated user tries to access
# a page that requires them to be logged in. Do this to display a more
# user-friendly page, rather than the one Flask-login provides by default
@login_manager.unauthorized_handler
def unauthorized():
    return render_template('authenticationrequired.html')