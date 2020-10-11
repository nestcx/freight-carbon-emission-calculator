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
from afcc.shipment.forms import ShipmentsForm
from os.path import splitext 
from sqlalchemy import desc
import re # Used for regex 
import json

# create shipment blueprint.
shipment_bp = Blueprint(
    'shipment', __name__, template_folder='templates', static_folder='shipment-static')



# GET  /shipments  -  get a list of shipments
# POST /shipments  -  upload a list of shipments
@shipment_bp.route('/shipments', methods=['GET', 'POST'])
def CR_shipments():

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    # find all shipments that belong to the user.
    if (request.method == 'GET'):
        shipments = Shipment.query.order_by(desc(Shipment.shipment_created)).filter_by(uid=user.uid).all()

    # create file form
    file_form = ShipmentsForm()

    if file_form.validate_on_submit():
        
        # 1. - check file extension and read file
        uploaded_file = file_form.shipments.data
        file_extension = splitext(uploaded_file.filename)[1]
        if file_extension == '.xlsx' or file_extension == '.xls':
            file_data = pd.read_excel(uploaded_file)
        elif file_extension =='.csv':
            file_data = pd.read_csv(uploaded_file)
        else:
            flash("invalid file type")
            return redirect(url_for('shipment.CR_shipments'))
        
        # Convert file data to python dictionary and then get shipment count
        dfile_data = file_data.to_dict()
        rows = len(dfile_data["From"])

        # Use sets rather than arrays, as we don't want to create duplicates when creating
        # new routes or post code entries
        set_of_new_routes_to_add = set()


        for i in range(rows):
            
            # Get the postcodes from the row. Do so by finding a 4 digit number
            # in both the 'from' and 'to' columns
            pattern = '(?<!\d)(?!0000)\d{4}(?!\d)'

            from_postcode = re.search(pattern, dfile_data['From'][i])
            to_postcode = re.search(pattern, dfile_data['To'][i])

            # If a valid postcode was found in both the 'From' and 'To' column in the file, proceed
            if from_postcode and to_postcode:

                # Check if a route already exists between the 2 postcodes, and if they don't,
                # add the route to the set of routes, so that a matrix of routes and their
                # distances/durations can be calculated later
                route = maproutes.route_exists(from_postcode.group(), to_postcode.group())
                if route is None:
                    # Insert the route as a tuple of postcode_a and postcode_b
                    set_of_new_routes_to_add.add((from_postcode.group(), to_postcode.group()))


        # Seperate the set of new routes into lists of 50 elements, as OpenRouteService
        # allows a max of 50x50 for the matrix of addresses
        list_of_fifty_postcodes = [list(set_of_new_routes_to_add)[i:i+49] for i in range(0, len(set_of_new_routes_to_add), 49)]
        
        # Since a matrix can only have a max of 50x50, we need to have multiple matrices in order
        # to be able to process files with more than 50 shipments. Therefore have a list
        # of 50x50 matrices
        list_of_matrices = []

        # Now generate all the matrices and append them to 1 list
        for i in range(0, len(list_of_fifty_postcodes)):
            list_of_matrices.append(maproutes.add_routes_matrix(set(list_of_fifty_postcodes[i])))


        # # Now create another list, which will store only the geojson data, so that
        # # the geojson data of all matrices can easily be returned to an API client or user
        # list_geojson_data = []

        # for i in range(len(list_of_matrices)):
        #     list_geojson_data.append(list_of_matrices[i].get_geojson_data())

        # return jsonify(list_geojson_data)


        # created shipment id's saved in this dictionary for optional use at
        # completion of upload.
        created_shipment_ids = []
        invalid_shipment_count = 0

        # Loop through again, this time, inserting the shipments. Now the routes should exist
        # in the database, and if they don't something has gone wrong with processing that
        # specific route, therefore, ignore it
        for i in range(rows):

            # This pattern is to ensure that there is a postcode in the 'From' and 'To' columns
            # There must be exactly 4 digits and they can't all be 0
            pattern = '(?<!\d)(?!0000)\d{4}(?!\d)'

            from_postcode = re.search(pattern, dfile_data['From'][i])
            to_postcode = re.search(pattern, dfile_data['To'][i])

            route = maproutes.route_exists(from_postcode.group(), to_postcode.group())

            if route is None:
                # TODO: Some postcodes can't be processed, so see if we can find another way
                # to create a route between 2 postcodes (using another API request maybe)
                invalid_shipment_count += 1
                continue

            # If the route is outdated, update it
            elif not maproutes.route_is_up_to_date(route):
                maproutes.update_route(route)

            try:
                shipment_data = generate_bulk_shipment_data(
                    dfile_data['Weight'][i], 
                    'tonne',
                    route)
            except Exception:
                invalid_shipment_count += 1
                continue


            # add shipment to database session
            try:
                created_shipment_ids.append(create_shipment(shipment_data, 
                                                            user.uid, 
                                                            False, 
                                                            shipment_name=''))
            except Exception:
                invalid_shipment_count += 1
                continue

        try:
            db.session.commit()
            flash("Success! Created " + str(len(created_shipment_ids)) + " shipments.")
        except Exception:
            flash("Error saving shipments")


        # If there were shipments that couldn't be processed, inform the user
        if invalid_shipment_count is not 0:
            flash('Some shipments could not be processed.\nThe number of shipments that couldn\'t be processed: ' + str(invalid_shipment_count))

        return redirect(url_for('shipment.CR_shipments'))


    return render_template('shipments.html', shipments=shipments, file_form=file_form)



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
                shipment_name=create_shipment_form.shipment_name.data
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
            edit_shipment(shipment, shipment_data, shipment_name=edit_shipment_form.shipment_name.data)
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


def create_shipment(shipment_data, user_id, commit=True, **kwargs):
    if ("shipment_name" in kwargs):
        shipment_name = kwargs['shipment_name']
    
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

    if commit == True:
        db.session.commit()

    return myShipment.shipment_id



def generate_bulk_shipment_data(loadWeight, loadWeightUnit, route):
    print('doing bulk shipment')
    """
    This function is a faster, though less-accurate alternative to generating shipment data.
    It is specifically used for bulk shipments from file uploads 

    """
    calculation_data = calculation.calculate_emissions(
        18.1, 
        route.route_distance_in_km, 
        float(loadWeight), 
        loadWeightUnit)

    response = {}

    response["emissions"] = {}
    response["emissions"]["carbon_dioxide_emission"] = calculation_data["carbon_dioxide_emission"]
    response["emissions"]["methane_emission"] = calculation_data["methane_emission"]
    response["emissions"]["nitrous_oxide_emission"] = calculation_data["nitrous_oxide_emission"]

    response["fuel_consumption"] = calculation_data["fuel_consumptionn"]
    response["adjusted_fuel_economy"] = calculation_data["adjusted_fuel_economy"]
    response["distance"] = route.route_distance_in_km
    response["duration"] = route.estimated_duration_in_seconds
    response["load_weight"] = loadWeight
    response["load_weight_unit"] = loadWeightUnit

    response["location"] = {}
    response["location"]["start_location"] = {}
    response["location"]["end_location"] = {}
    response["location"]["start_location"]["address"] = route.point_a_region_name
    response["location"]["start_location"]["coordinate"] = str(route.point_a_long) + "," + str(route.point_a_lat)
    response["location"]["end_location"]["address"] = route.point_b_region_name
    response["location"]["end_location"]["coordinate"] = str(route.point_b_long) + "," + str(route.point_b_lat)

    return response




def generate_shipment_data(loadWeight, loadWeightUnit, startAddress, endAddress):
    
    startAddressInfo = maproutes.search_address(startAddress)
    endAddressInfo = maproutes.search_address(endAddress)
    
    print(startAddressInfo)
    print(endAddressInfo)

    startAddressValidated = startAddressInfo["features"][0]["properties"]["label"]
    endAddressValidated = endAddressInfo["features"][0]["properties"]["label"]

    startAddressCoordinates = startAddressInfo["features"][0]["geometry"]["coordinates"]
    endAddressCoordinates = endAddressInfo["features"][0]["geometry"]["coordinates"]

    geoJSONData = maproutes.get_route(
        [startAddressCoordinates[0], startAddressCoordinates[1]],
        [endAddressCoordinates[0], endAddressCoordinates[1]])
        

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
