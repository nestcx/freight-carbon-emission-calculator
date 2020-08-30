from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
# from flask_security import Security, SQLAlc

from afcc.config import *
from afcc.extensions import db, limiter


def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')


    # app.config['SECRET_KEY'] = 'super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_STRING

    db.init_app(app) # The db object is retrieved from the extensions.py file
    limiter.init_app(app) # The limiter object is retrieved from the extensions.py file

    # import blueprints
    from afcc import maproutes, calculation
    from afcc.user import views # import the blueprint with user-related routes

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)
    app.register_blueprint(views.user_bp, url_prefix='/user')
    
    
    @app.route("/")
    def index():
        return render_template("main.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    return app