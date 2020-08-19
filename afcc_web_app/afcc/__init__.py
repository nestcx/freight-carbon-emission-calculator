from flask import Flask
from flask import render_template

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["2000 per day", "100 per hour"])

def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')

    limiter.init_app(app)

    # import blueprints.
    from afcc import maproutes, calculation

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)

    
    @app.route("/")
    def index():
        return "Hello!"

    return app