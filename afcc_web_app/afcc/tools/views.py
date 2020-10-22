from flask import Blueprint, request, render_template, url_for
from afcc.extensions import db
from afcc.shipment.models import Shipment
from afcc.user.models import User
from flask_login import current_user

# create tools blueprint.
tools_bp = Blueprint(
    'tools', __name__, template_folder='tools-templates', static_folder='tools-static')

@tools_bp.route('/tools', methods=['GET'])
def tools():
    return render_template('tools.html')

@tools_bp.route('/tools/compare', methods=['GET'])
def compare():
    return render_template('compare.html')