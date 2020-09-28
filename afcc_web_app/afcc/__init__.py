from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from afcc.config import *
from afcc.extensions import db, limiter, login_manager


def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = b'_5#o2L"F4Q8z\n\xec]/'

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_STRING
    # Use the secret key as the salt as well. NOTE: This is temporary
    app.config['SECURITY_PASSWORD_SALT'] = SECRET_KEY

    db.init_app(app)  # The db object is retrieved from the extensions.py file
    # The limiter object is retrieved from the extensions.py file
    limiter.init_app(app)
    # The login object is retrieved from the extensions.py file
    login_manager.init_app(app)

    # import blueprints.
    from afcc import maproutes, calculation#, shipments
    from afcc.user import views 
    

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)    
    #app.register_blueprint(shipments.shipments_bp)
    app.register_blueprint(views.user_bp)

    from afcc.shipment import views
    app.register_blueprint(views.shipment_bp)

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
