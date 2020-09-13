from flask import Flask
from flask import render_template

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_cors import CORS, cross_origin


limiter = Limiter(key_func=get_remote_address, default_limits=["2000 per day", "100 per hour"])

def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = b'_5#o2L"F4Q8z\n\xec]/'

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    limiter.init_app(app)

    # import blueprints.
    from afcc import maproutes, calculation, shipments

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)    
    app.register_blueprint(shipments.shipments_bp)

    
    @app.route("/")
    def index():
        return render_template("main.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")
    

    return app
