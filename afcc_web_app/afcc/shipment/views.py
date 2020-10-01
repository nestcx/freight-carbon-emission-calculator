from flask import Blueprint, request, render_template, flash, redirect, url_for, g
from afcc.extensions import db
from afcc.shipment.models import Shipment
from afcc.user.models import User
from flask_login import current_user
import datetime
import os
import pandas as pd
from flask import jsonify
from afcc import maproutes
from afcc import calculation
from afcc import data_conversion
import string
from afcc.shipment.forms import CreateShipmentForm
from afcc.shipment.forms import EditShipmentForm


# create shipment blueprint.
shipment_bp = Blueprint(
    'shipment', __name__, template_folder='templates', static_folder='shipment-static')


# GET  /shipments  -  get a list of shipments
@shipment_bp.route('/shipments', methods=['GET', 'POST'])
def CR_shipments():

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    # find all shipments that belong to the user.
    if (request.method == 'GET'):
        shipments = Shipment.query.filter_by(uid=user.uid).all()

    return render_template('shipments.html', shipments=shipments)


# GET  /shipments/new  -  show form to create new shipment
@shipment_bp.route('/shipments/new', methods=['GET', 'POST'])
def show_create_shipment_form():

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    # create the shipment form
    create_shipment_form = CreateShipmentForm()

    # if submitted form is valid:
    #    1. - generate shipment data
    #    2. - persist to database
    #    3. - redirect to new shipment page
    if create_shipment_form.validate_on_submit():

        # 1. - generate shipment data
        # if this fails, render form again.
        try:
            shipment_data = generate_shipment_data(
                create_shipment_form.load_weight.data,
                create_shipment_form.load_weight_unit.data,
                create_shipment_form.start_address.data,
                create_shipment_form.end_address.data
            )
        except Exception:
            flash("An error occurred while trying to generate the shipment.")
            return render_template('create_shipment_form.html', form=create_shipment_form)

        # 2. - persist to database
        try:
            shipment_id = create_shipment(
                shipment_data, 
                user.uid, 
                create_shipment_form.shipment_name.data
            )
        except Exception:
            flash("An error occurred while saving the shipment.")
            return render_template('create_shipment_form.html', form=create_shipment_form)

        # 3. - redirect to new shipment page.
        return redirect(url_for('shipment.RUD_shipment', shipment_id=shipment_id))


    # flash form errors.
    if len(create_shipment_form.errors) != 0:
        for error in create_shipment_form.errors:
            for msg in create_shipment_form.errors[error]:
                flash(msg)


    return render_template('create_shipment_form.html', form=create_shipment_form)


# GET  /shipments/<shipment_id>  -  get individual shipment
@shipment_bp.route('/shipments/<int:shipment_id>', methods=['GET'])
def RUD_shipment(shipment_id):

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    # get shipment.
    try:
        shipment = Shipment.query.get(shipment_id)
    except Exception:
        return redirect(url_for('shipment.CR_shipments'))

    # check shipment exists and belongs to user.
    result = check_user_shipment(user, shipment)
    if result is True:
        return render_template('shipment.html', shipment=shipment)
    else:
        return redirect(url_for('shipment.CR_shipments'))

    


# GET  /shipments/<shipment_id>/edit  -  show form to edit individual shipment
@shipment_bp.route('/shipments/<int:shipment_id>/edit', methods=['GET', 'POST'])
def show_edit_shipment_form(shipment_id):

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    # create edit shipment form
    edit_shipment_form = EditShipmentForm()

    # get shipment.
    try:
        shipment = Shipment.query.get(shipment_id)
    except Exception:
        return redirect(url_for('shipment.CR_shipments'))

    # check shipment exists and belongs to user.
    result = check_user_shipment(user, shipment)
    if result is False:
        return redirect(url_for('shipment.CR_shipments'))
    

    # if submitted form is valid:
    #    1. - generate new shipment data
    #    2. - update row in database
    #    3. - refresh form to show updated data
    if edit_shipment_form.validate_on_submit():
        
        # 1. - generate new shipment data
        # if this fails, render form again.
        try:
            shipment_data = generate_shipment_data(
                edit_shipment_form.load_weight.data, 
                edit_shipment_form.load_weight_unit.data,
                edit_shipment_form.start_address.data, 
                edit_shipment_form.end_address.data
            )
        except Exception:
            flash("An error occurred while trying to generate the shipment")
            return render_template('edit_shipment_form.html', form=edit_shipment_form, shipment=shipment)


        # 2. - update row in database.
        try:
            edit_shipment(shipment, shipment_data, edit_shipment_form.shipment_name.data)
        except Exception:
            flash("An error has occurred while updating the shipment.")
            return render_template('edit_shipment_form.html', form=edit_shipment_form, shipment=shipment)

        # 3. - refresh form to show updated data
        flash("Updated shipment successfully")
        return redirect(url_for('shipment.show_edit_shipment_form', shipment_id=shipment.shipment_id))

    # flash form errors
    if len(edit_shipment_form.errors) != 0:
        for error in edit_shipment_form.errors:
            for msg in edit_shipment_form.errors[error]:
                flash(msg)

    # pre-populate the form with existing shipment data.
    # NOTE: ensure population occurs AFTER the form validation.
    edit_shipment_form.shipment_name.data = shipment.shipment_name
    edit_shipment_form.start_address.data = shipment.start_address
    edit_shipment_form.end_address.data = shipment.end_address
    edit_shipment_form.load_weight.data = shipment.load_weight
    edit_shipment_form.load_weight_unit.data = shipment.load_weight_unit

    return render_template('edit_shipment_form.html', form=edit_shipment_form, shipment=shipment)


def authenticate_user():
    """ Ensure a user is logged in and has a valid account.

        Returns:
        False, redirect_url  -- if user is not logged in, if user doesn't exist 
                                in database, or if user has inactive account,
                                returns False and url to redirect to.
        True, user           -- if user is valid, return True and user object.
    """
    
    # check user is logged in.
    print(current_user.is_authenticated)

    if not current_user.is_authenticated:
        flash("Please log in.")
        return False, 'user.log_in'

    # check user exists in database.
    try:
        user = User.query.filter_by(email=current_user.email).first()
    except Exception:
        flash("An error has occurred.")
        return False, '/'

    # check user has active account.
    if user.deactivated is True:
        return False, 'user.display_user_details'

    return True, user
    

def check_user_shipment(user, shipment):
    if (shipment is None or user.uid != shipment.uid):
        return False
    elif (user.uid == shipment.uid):
        return True
        

def edit_shipment(shipment, updated, shipment_name):
    shipment.shipment_name = shipment_name
    shipment.trip_distance = updated["distance"]
    shipment.trip_duration = updated["duration"]
    shipment.load_weight = updated["load_weight"]
    shipment.load_weight_unit = updated["load_weight_unit"]
    shipment.fuel_economy_adjustment = updated["adjusted_fuel_economy"]
    shipment.carbon_dioxide_emission = updated["emissions"]["carbon_dioxide_emission"]
    shipment.methane_emission = updated["emissions"]["methane_emission"]
    shipment.nitrous_oxide_emission = updated["emissions"]["nitrous_oxide_emission"]
    shipment.start_address = updated["location"]["start_location"]["address"]
    shipment.end_address = updated["location"]["end_location"]["address"]
    shipment.start_address_coordinates = updated["location"]["start_location"]["coordinate"]
    shipment.end_address_coordinates = updated["location"]["end_location"]["coordinate"]

    db.session.commit()


def create_shipment(shipment_data, user_id, shipment_name):
    myShipment = Shipment(
        uid=user_id,
        shipment_name=shipment_name,
        trip_distance=shipment_data["distance"],
        trip_duration=shipment_data["duration"],
        load_weight=shipment_data["load_weight"],
        load_weight_unit=shipment_data["load_weight_unit"],
        shipment_created=datetime.datetime.now(),
        fuel_economy_adjustment=shipment_data["adjusted_fuel_economy"],
        carbon_dioxide_emission=shipment_data["emissions"]["carbon_dioxide_emission"],
        methane_emission=shipment_data["emissions"]["methane_emission"],
        nitrous_oxide_emission=shipment_data["emissions"]["nitrous_oxide_emission"],
        start_address=shipment_data["location"]["start_location"]["address"],
        end_address=shipment_data["location"]["end_location"]["address"],
        start_address_coordinates=shipment_data["location"]["start_location"]["coordinate"],
        end_address_coordinates=shipment_data["location"]["end_location"]["coordinate"]
    )

    db.session.add(myShipment)
    db.session.commit()

    return myShipment.shipment_id


def generate_shipment_data(loadWeight, loadWeightUnit, startAddress, endAddress):
    startAddressInfo = maproutes.search_address(startAddress)
    endAddressInfo = maproutes.search_address(endAddress)
    print(endAddressInfo)
    print(startAddressInfo)

    startAddressValidated = startAddressInfo["features"][0]["properties"]["label"]
    endAddressValidated = endAddressInfo["features"][0]["properties"]["label"]

    startAddressCoordinates = startAddressInfo["features"][0]["geometry"]["coordinates"]
    endAddressCoordinates = endAddressInfo["features"][0]["geometry"]["coordinates"]

    geoJSONData = maproutes.get_route(str(startAddressCoordinates[0]) + "," + str(startAddressCoordinates[1]), str(endAddressCoordinates[0]) + "," + str(endAddressCoordinates[1]))

    length_of_route = data_conversion.metre_to_kilometre(
        maproutes.get_length_of_route(geoJSONData))
    duration_of_route = maproutes.get_duration_of_route(geoJSONData)

    calculation_data = calculation.calculate_emissions(18.1, length_of_route, float(loadWeight), loadWeightUnit)

    response = {}

    response["emissions"] = {}
    response["emissions"]["carbon_dioxide_emission"] = calculation_data["carbon_dioxide_emission"]
    response["emissions"]["methane_emission"] = calculation_data["methane_emission"]
    response["emissions"]["nitrous_oxide_emission"] = calculation_data["nitrous_oxide_emission"]

    response["fuel_consumption"] = calculation_data["fuel_consumptionn"]
    response["adjusted_fuel_economy"] = calculation_data["adjusted_fuel_economy"]
    response["distance"] = length_of_route
    response["duration"] = duration_of_route
    response["load_weight"] = loadWeight
    response["load_weight_unit"] = loadWeightUnit

    response["location"] = {}
    response["location"]["start_location"] = {}
    response["location"]["end_location"] = {}
    response["location"]["start_location"]["address"] = startAddressValidated
    response["location"]["start_location"]["coordinate"] = str(startAddressCoordinates[0]) + "," + str(startAddressCoordinates[1])
    response["location"]["end_location"]["address"] = endAddressValidated
    response["location"]["end_location"]["coordinate"] = str(endAddressCoordinates[0]) + "," + str(endAddressCoordinates[1])

    return response
