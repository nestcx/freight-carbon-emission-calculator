from flask import Blueprint, request, render_template
from afcc.extensions import db
from afcc.shipment.models import Shipment

# create shipment blueprint.
shipment_bp = Blueprint('shipments', __name__)


# GET  /shipments  -  get a list of shipments
# POST /shipments  -  create multiple shipments
@shipment_bp.route('/shipments', methods=['GET', 'POST'])
def C_shipment():
    return 'not implemented'
    

# POST  /shipment  -  create a new shipment
@shipment_bp.route('/shipment', methods=['POST'])
def create_shipment():
    return 'not implemented'


# GET  /shipments/new  -  show form to create new shipment
@shipment_bp.route('/shipments/new', methods=['GET'])
def show_create_shipment_form():
    return 'not implemented'


# GET     /shipments/<shipment_id>  -  get individual shipment
# PATCH   /shipments/<shipment_id>  -  update individual shipment
# DELETE  /shipments/<shipment_id>  -  delete individual shipment
@shipment_bp.route('/shipments/<int:shipment_id>', methods=['GET', 'PATCH', 'DELETE'])
def RUD_shipment(shipment_id):
    return 'not implemented'


# GET  /shipments/<shipment_id>/edit  -  show form to edit individual shipment
@shipment_bp.route('/shipments/<int:shipment_id>/edit', methods=['GET'])
def show_edit_shipment_form(shipment_id):
    return 'not implemented'