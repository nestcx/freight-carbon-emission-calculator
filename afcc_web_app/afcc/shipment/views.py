import re # Used for regex 
import json
import datetime
import os
import string
import threading
from itertools import chain
from os.path import splitext 
from flask import Blueprint, request, render_template, flash, redirect, url_for, g, jsonify
from flask_login import current_user
import pandas as pd
from sqlalchemy import desc
from afcc.extensions import db
from afcc.shipment.models import Shipment
from afcc.user.models import User
from afcc.models import Postcode, Route
from afcc import maproutes
from afcc import calculation
from afcc import data_conversion
from afcc.shipment.forms import CreateShipmentForm, EditShipmentForm, ShipmentsForm


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

    # create file form
    file_form = ShipmentsForm()

    shipments = Shipment.query.order_by(desc(Shipment.shipment_created)).filter_by(uid=user.uid).all()

    # Check if the request is a GET request before continuing. If so, find all shipments belonging to them
    # and display them
    if (request.method == 'GET'):
        return render_template('shipments.html', shipments=shipments, file_form=file_form)

    # Check if the request includes a file to process, and if so, continue
    # if 'file' not in request.files:
        flash('No file was submitted. Please submit a csv or xls file')
        return jsonify('No file was submitted'), 400


    # Check file extension and read file
    uploaded_file = request.files['file']

    # if file_form.validate_on_submit():
        
    #     # 1. - check file extension and read file
    #     uploaded_file = file_form.shipments.data

    file_extension = splitext(uploaded_file.filename)[1]
    if file_extension == '.xlsx' or file_extension == '.xls':
        file_data = pd.read_excel(uploaded_file)
    elif file_extension =='.csv':
        file_data = pd.read_csv(uploaded_file)
    else:
        flash('Invalid file type. Acceptable file types are .xls, .xlsx and .csv')
        return jsonify('Invalid file type. Acceptable file types are .xls, .xlsx and .csv'), 400
    
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
    list_of_fifty_postcodes = [list(set_of_new_routes_to_add)[i:i+25] for i in range(0, len(set_of_new_routes_to_add), 25)]
    
    # Since a matrix can only have a max of 50x50, we need to have multiple matrices in order
    # to be able to process files with more than 50 shipments. Therefore generate all the 
    # matrices and append all the routes found from them into a list. Note that the matrix
    # function returns a list, so list_of_routes will become a 2D array, which would need
    # to be flattened
    list_of_routes = []

    threads = []

    print('number of matrices that will need to be generated: ' + str(len(list_of_fifty_postcodes)))

    # OpenRouteService limits Matrix API requests to 40 per minute
    # TODO: Add an if statement to check if more than 40 requests are required, and handle it
    # accordingly if so.
    for i in range(0, len(list_of_fifty_postcodes)):
        thread = threading.Thread(
            target=maproutes.add_routes_matrix, 
            args=(set(list_of_fifty_postcodes[i]), list_of_routes))
        threads.append(thread)
        thread.start()


    # Only continue once all the threads have completed, meaning that once all the
    # matrices have been generated and stored in the list
    for i in range(len(threads)):
        threads[i].join()

    # Now store all the shipments from list_of_routes in the db
    db.session.bulk_save_objects(list_of_routes)
    db.session.commit()


    # created shipment id's saved in this dictionary for optional use at
    # completion of upload.
    created_shipment_ids = []
    invalid_shipment_msg = []

    slower_route_fallback_option = False

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
            print('shipments/views/bulkshipments: Route does not exist between ' + from_postcode.group() + ' > ' + to_postcode.group())
            
            # OpenRouteService matrix option has a hard limit of 350m radius in which it
            # it looks for an accessible road when trying to calculate routes and their distances/
            # durations. This means that some routes will fail, as the coordinate may not have
            # a road within 350m radius.

            # The API call for directions allow you to specify a larger radius, which increases tolerance
            # and makes it so that more shipments are able to be processed.

            # NOTE: Calling directions for individual routes is much slower than the matrix call,
            # so making slower_route_fallback_option: false will make the bulk shipment processing
            # much faster, at the expense of not being able to process some shipments 
            if slower_route_fallback_option is True:
                postcode_a_obj = Postcode.query.get(from_postcode.group())
                postcode_b_obj = Postcode.query.get(to_postcode.group())
                # Postcode.query.get(postcode)
                # postcode_a_obj = maproutes.get_postcode(from_postcode.group())
                # postcode_b_obj = maproutes.get_postcode(to_postcode.group())
                if postcode_a_obj is None:
                    invalid_shipment_msg.append('Error: cannot locate postcode: ' + from_postcode.group())
                elif postcode_b_obj is None:
                    invalid_shipment_msg.append('Error: cannot locate postcode: ' + to_postcode.group())
                else:

                    a_coords = [postcode_a_obj.long, postcode_a_obj.lat]
                    b_coords = [postcode_b_obj.long, postcode_b_obj.lat]

                    # Try find a route by sending a POST directions request, and see if the API service was
                    # was able to generate a route
                    route_geojson = maproutes.get_route_geojson_data(a_coords, b_coords)

                    if route_geojson is not None:
                        # The API service was able to find the route once the fallback option was used,
                        # therefore, create a new Route object and store the route data in the database
                        route = Route(
                            point_a_postcode = postcode_a_obj.postcode,
                            point_a_region_name =  postcode_a_obj.region_name,
                            point_a_long =  postcode_a_obj.long,
                            point_a_lat =  postcode_a_obj.lat,

                            point_b_postcode = postcode_b_obj.postcode,
                            point_b_region_name = postcode_b_obj.region_name,
                            point_b_long = postcode_b_obj.long,
                            point_b_lat = postcode_b_obj.lat,
                            
                            route_distance_in_km = route_geojson.get_distance(),
                            estimated_duration_in_seconds = route_geojson.get_duration(),
                            last_updated = datetime.date.today()
                        )

                        # Now add this route to the DB to avoid having to use the slower process
                        # whenever a new shipment with the same start and end addresses is added 
                        db.session.add(route)
                        db.session.commit()
                        
                    else:
                        invalid_shipment_msg.append(
                            'Error: could not create shipment data for shipment between: ' + \
                                str(dfile_data['From'][i]) + ' to ' + str(dfile_data['To'][i]))

                        # Shipment can't be created no matter what, so skip the rest of the steps
                        # for this particular shipment
                        continue


        # If the route is outdated, update it, as there may be new roads or obstacles
        # that will affect the route and distance from point a to point b
        elif not maproutes.route_is_up_to_date(route):
            maproutes.update_route(route)

        try:
            shipment_data = generate_bulk_shipment_data(
                dfile_data['Weight'][i], 
                'tonne',
                dfile_data['Volume'][i],
                route)
        except Exception as e:
            invalid_shipment_msg.append(
                'Error: could not create shipment data for shipment between: ' + \
                    str(dfile_data['From'][i]) + ' to ' + str(dfile_data['To'][i]))

            continue


        # Add shipment to database session
        try:
            created_shipment_ids.append(create_shipment(shipment_data, 
                                                        user.uid, 
                                                        False, 
                                                        shipment_name=''))
        except Exception:
            print('shipments/view/bulkshipments: Shipment object could not be inserted into db')
            invalid_shipment_msg.append('Shipment for row ' + str(i) + ' could not be created')
            continue

    try:
        db.session.commit()
        flash("Processed " + str(len(created_shipment_ids)) + " shipments from file.")
    except Exception:
        flash("Error saving shipments")


    # If there were shipments that couldn't be processed, inform the user
    # if len(invalid_shipment_msg) != 0:
        # flash('Some shipments could not be processed.\nThe number of shipments that ' \
        #     'couldn\'t be processed: ' + str(len(invalid_shipment_msg)))

        # Flash all errors
        # for i in range(len(invalid_shipment_msg)):
        #     flash(invalid_shipment_msg[i])
    

    shipments = Shipment.query.order_by(desc(Shipment.shipment_created)).filter_by(uid=user.uid).all()
    # return render_template('shipments.html', shipments=shipments, file_form=file_form)
    return jsonify(invalid_shipment_msg), 200



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
                create_shipment_form.load_volume.data,
                create_shipment_form.start_address.data,
                create_shipment_form.end_address.data
            )
        except Exception as e:
            print(e)
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
@shipment_bp.route('/shipments/<int:shipment_id>', methods=['GET', 'DELETE'])
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
       
    if (request.method == 'GET'):
        if result is True:
            return render_template('shipment.html', shipment=shipment)
       
        return redirect(url_for('shipment.CR_shipments'))
    
    if (request.method == 'DELETE'):  
        if result is False:
            flash("Error deleting shipment")
     
        # delete shipment and commit database session
        try:
            db.session.delete(shipment)
            db.session.commit()
            flash("Deleted Shipment: " + str(shipment_id))
        except Exception:
            flash("Error deleting shipment")

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
                edit_shipment_form.load_volume.data,
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
    shipment.load_volume = update["load_volume"]
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
        load_volume=shipment_data["load_volume"],
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


def generate_bulk_shipment_data(loadWeight, loadWeightUnit, loadVolume, route):
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
    response["load_volume"] = loadVolume

    response["location"] = {}
    response["location"]["start_location"] = {}
    response["location"]["end_location"] = {}
    response["location"]["start_location"]["address"] = route.point_a_region_name
    response["location"]["start_location"]["coordinate"] = str(route.point_a_long) + "," + str(route.point_a_lat)
    response["location"]["end_location"]["address"] = route.point_b_region_name
    response["location"]["end_location"]["coordinate"] = str(route.point_b_long) + "," + str(route.point_b_lat)

    return response




def generate_shipment_data(loadWeight, loadWeightUnit, loadVolume, point_a, point_b):
    
    # Create a GeoJSON object containing data about the each location
    startAddress = maproutes.search_address(point_a)
    endAddress = maproutes.search_address(point_b)

    if startAddress.is_valid() and endAddress.is_valid():

        # Create a GeoJSON_Route object which wraps the GeoJSON data from the API service
        route_geojson = maproutes.get_route_geojson_data(
            [startAddress.get_long(), startAddress.get_lat()],
            [endAddress.get_long(), endAddress.get_lat()])
            
        length_of_route = data_conversion.metre_to_kilometre(route_geojson.get_distance())
        duration_of_route = route_geojson.get_duration()

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
        response["load_volume"] = loadVolume

        response["location"] = {}
        response["location"]["start_location"] = {}
        response["location"]["end_location"] = {}
        response["location"]["start_location"]["address"] = startAddress.get_address_name()
        response["location"]["start_location"]["coordinate"] = str(startAddress.get_long()) + "," + str(startAddress.get_lat())
        response["location"]["end_location"]["address"] = endAddress.get_address_name()
        response["location"]["end_location"]["coordinate"] = str(endAddress.get_long()) + "," + str(endAddress.get_lat())

        return response
