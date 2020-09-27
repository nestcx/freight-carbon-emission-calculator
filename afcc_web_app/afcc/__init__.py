from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from afcc.config import *
from afcc.extensions import db, limiter, login_manager, mail


def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_STRING
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    # import blueprints
    from afcc import maproutes, calculation
    from afcc.user import views  # import the blueprint with user-related routes

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)
    app.register_blueprint(views.user_bp)

    @app.route('/')
    def index():
        return render_template('main.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/error')
    def display_error_page():
        return render_template('error.html')
        
    return app
