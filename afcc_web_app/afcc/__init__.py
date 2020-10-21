from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user

import os
from flask import send_from_directory

from afcc.config import *
from afcc.extensions import db, limiter, login_manager, mail

def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = b'_5#o2L"F4Q8z\n\xec]/'

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_STRING
    # Use the secret key as the salt as well. NOTE: This is temporary
    app.config['SECURITY_PASSWORD_SALT'] = SECRET_KEY

    # Email sending related configs
    app.config['MAIL_SERVER'] = 'smtp.gmail.com' # NOTE: Using Gmail we've created a new gmail account for testing
    # Use port 465 as Googlemail uses that for SMTP and SSL authentication
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    # Get the email address and password fron the configs. 
    # NOTE: A gmail account was made specifically for testing. This must be replaced by the client's credentials and done by the client
    app.config['DEFAULT_MAIL_SENDER'] = DEFAULT_SENDER_EMAIL_ADDRESS
    app.config['MAIL_PASSWORD'] = SENDER_EMAIL_APP_PASSWORD
    app.config['MAIL_USERNAME'] = DEFAULT_SENDER_EMAIL_ADDRESS # Username must be specified even though it is the same as the email address


    db.init_app(app)  # The db object is retrieved from the extensions.py file
    # The limiter object is retrieved from the extensions.py file
    limiter.init_app(app)
    # The login object is retrieved from the extensions.py file
    login_manager.init_app(app)
    # Retrieve the mail object from the extensions.py file
    mail.init_app(app)

    # import blueprints.
    from afcc import maproutes, calculation
    # import the blueprint with user-related routes
    from afcc.user import views as uviews
    from afcc.shipment import views as sviews
    from afcc.tools import views as tviews

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)
    app.register_blueprint(uviews.user_bp)
    app.register_blueprint(sviews.shipment_bp)
    app.register_blueprint(tviews.tools_bp)

    @app.route('/')
    def index():
        # If a user is logged in, redirect them to the app 'home' page, since thats where
        # they most liekly want to be
        if current_user.is_authenticated:
            return redirect(url_for('shipment.CR_shipments'))
        else:
            return render_template('index.html')

    @app.route('/error')
    def display_error_page():
        return render_template('error.html')

    @app.route('/about')
    def about():
        return render_template('about.html', title='About')

    @app.route('/help')
    def help():
        return render_template('help.html', title='Help')

    @app.route('/devplayground')
    def show_styles():
        return render_template('playground.html', title='CSS styling playground')
    

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
                                
    # Register 404 handler so that a custom 404 page can be delivered
    app.register_error_handler(404, page_not_found)

    return app

def page_not_found(e):
  return render_template('404.html'), 404


