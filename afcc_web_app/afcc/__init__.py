from flask import Flask
from flask import render_template

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

''' ##################  These are the imports for fielupload py  ################## '''
from flask import redirect
from flask import url_for
import pandas as pd
from flask import request
from flask import flash
import string

limiter = Limiter(key_func=get_remote_address, default_limits=["2000 per day", "100 per hour"])

def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')

    limiter.init_app(app)

    # import blueprints.
    from afcc import maproutes, calculation, fileupload

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)    
    app.register_blueprint(fileupload.fileupload_bp)

    
    @app.route("/")
    def index():
        return render_template("main.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")
    

    return app
