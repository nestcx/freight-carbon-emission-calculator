from flask import Blueprint, request, render_template, flash, redirect, url_for
from afcc.extensions import db
from afcc.shipment.models import Shipment
from afcc.user.models import User
from flask_login import current_user
from afcc.shipment.forms import UpdateForm
from afcc.calculation import calculate_by_address

# create shipment blueprint.
shipment_bp = Blueprint(
    'shipment', __name__, template_folder='templates', static_folder='shipment-static')


# GET  /shipments  -  get a list of shipments
# POST /shipments  -  create multiple shipments
@shipment_bp.route('/shipments', methods=['GET', 'POST'])
def CR_shipments():

    # check that user is logged in.
    if not current_user.is_authenticated:
        return str("hello!")

    # try to find user's details.
    try:
        user = User.query.filter_by(email=current_user.email).first()
    except Exception:
        flash("An error has occurred.")
        return redirect(url_for('display_error_page'))

    # find all shipments that belong to the user.
    if (request.method == 'GET'):
        shipments = Shipment.query.filter_by(uid=user.uid).all()

    return render_template('shipments.html', shipments=shipments)


# POST  /shipment  -  create a new shipment
@shipment_bp.route('/shipment', methods=['POST'])
def C_shipment():
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

    # check that user is logged in.
    if not current_user.is_authenticated:
        return redirect(url_for('user.log_in'))

    # try to find user's details.
    try:
        user = User.query.filter_by(email=current_user.email).first()
    except Exception:
        flash("An error has occurred.")
        return redirect(url_for('display_error_page'))

    # GET
    if (request.method == 'GET'):

        # query shipment.
        shipment = Shipment.query.get(shipment_id)

        # if shipment does not exist, or does not belong to user, redirect to shipments list.
        # if shipment belongs to user, display shipment.
        if (shipment is None or user.uid != shipment.uid):
            return redirect(url_for('shipment.CR_shipments'))
        elif (user.uid == shipment.uid):
            return render_template('shipment.html', shipment=shipment)

    # PATCH
    if (request.method == 'PATCH'):
        None

    # DELETE
    if (request.method == 'DELETE'):
        None


# GET  /shipments/<shipment_id>/edit  -  show form to edit individual shipment
@shipment_bp.route('/shipments/<int:shipment_id>/edit', methods=['GET', 'POST'])
def show_edit_shipment_form(shipment_id):
    # query shipment
    shipment = Shipment.query.get(shipment_id)

    update_form = UpdateForm()

    # check that user is logged in.
    if not current_user.is_authenticated:
        return redirect(url_for('user.log_in'))

    # try to find user's details.
    try:
        user = User.query.filter_by(email=current_user.email).first()
    except Exception:
        flash("An error has occurred.")
        return redirect(url_for('display_error_page'))
    
    if update_form.validate_on_submit():
        # Update action goes here
        if (shipment is None or user.uid != shipment.uid):
            return redirect(url_for('shipments'))  #this should take user back to home page
        else:
            #get calculation results
            result = calculate_by_address(update_form.fromAddress.data, update_form.toAddress.data, update_form.weight.data)    

            #Update shipment details
            #shipment_id - unchanged
            #uid - unchanged
            #shipment_created - unchanged
            #shipment_name - unchanged
            #trip_distance
            shipment.trip_distance = result["distance"]
            #trip_duration
            shipment.trip_duration = result["duration"]
            #fuel_economy_adjustment
            shipment.fuel_economy_adjustment = result["adjusted_fuel_economy"]
            #carbon_dioxide_emission
            shipment.carbon_dioxide_emission = result["emissions"]["carbon_dioxide_emission"]
            #methane_emission
            shipment.methane_emission = result["emissions"]["methane_emission"]
            #nitrous_oxide_emission
            shipment.nitrous_oxide_emission = result["emissions"]["nitrous_oxide_emission"]
            #start_address
            shipment.start_address = result["location"]["start_location"]["address"]
            #start_address_coordinates
            shipment.start_address_coordinates = result["location"]["start_location"]["coordinate"]
            #end_address
            shipment.end_address = result["location"]["end_location"]["address"]
            #end_address_coordinates
            shipment.end_address = result["location"]["end_location"]["coordinate"]

            #commit changes
            db.session.commit()

            #Confirm Message
            return redirect(url_for('shipments'))

            #Redirect to Standard shipment page for user

    # if shipment does not exist, or does not belong to user, show error page
    # if shipment exists and belongs to user, show update form.
    if (shipment is None):
        return redirect(url_for('display_error_page'))
    else:
        return render_template('editShipment.html', shipment=shipment, form=update_form)
