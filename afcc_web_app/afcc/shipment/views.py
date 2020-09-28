from flask import Blueprint, request, render_template, flash, redirect, url_for
from afcc.extensions import db
from afcc.shipment.models import Shipment
from afcc.user.models import User
from afcc.shipment.models import Shipment
from flask_login import current_user
import datetime

####### Imports needed for my calculation part #########

import os
import pandas as pd

from flask import jsonify
from afcc import maproutes
from afcc import calculation

from afcc import data_conversion
from afcc.shipment.forms import ShipmentdataForm
import string

# create shipment blueprint.
shipment_bp = Blueprint('shipment', __name__, template_folder='templates', static_folder='shipment-static')


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
    shipment_form=ShipmentdataForm()

    if shipment_form.validate_on_submit():

        #Sets all the data into the local variable FILEDATA
        start_address=shipment_form.pickuploc.data
        end_address=shipment_form.dropoffloc.data
        item_weight=shipment_form.cargoweight.data
        shipmentname=shipment_form.shipmentname.data
        
        result={}

        #This is to get the emission calculation result from calculation.py
        try:
            result=calculation.get_emission_calculation(start_address,end_address,item_weight,1)
        except:
            print("Error")

        # check that user is logged in.
        if current_user.is_authenticated:
            # try to find user's details.
            try:
                user = User.query.filter_by(email=current_user.email).first()
            except Exception:
                flash("An error has occurred.")
                return redirect(url_for('display_error_page'))


            #This is to set the values in the variables for the query.
            new_shipment=Shipment(uid = user.uid,shipment_created = datetime.datetime.now(),
            shipment_name =shipmentname ,trip_distance = result['distance'],trip_duration =result['duration'] ,
            fuel_economy_adjustment = result['emission']["adjusted_fuel_economy"] ,
            carbon_dioxide_emission = result['emission']['carbon_dioxide_emission']  ,
            methane_emission = result['emission']['methane_emission'],
            nitrous_oxide_emission = result['emission']['nitrous_oxide_emission']
            ,start_address = result['origin'] ,
            start_address_coordinates = str(result['origincoords'][0])+","+str(result['origincoords'][1]),
            end_address = result['destination'] ,
            end_address_coordinates = str(result['destcoords'][0])+","+str(result['destcoords'][1]) )
            
            db.session.add(new_shipment)
            db.session.commit()
        

    return render_template('dashboard.html')


# GET  /shipments/new  -  show form to create new shipment
@shipment_bp.route('/shipments/new', methods=['GET'])
def show_create_shipment_form():
    shipment_form=ShipmentdataForm()
    return render_template('shipmentform.html', form=shipment_form)
    


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
@shipment_bp.route('/shipments/<int:shipment_id>/edit', methods=['GET'])
def show_edit_shipment_form(shipment_id):
    return 'not implemented'


def get_file_extension(filename):

    '''Get the uploaded file's extension.
        
    Arguments:
    filename -- filename sent from the shipments function from the file uploaded by the user.

    Returns:
    [File Extension] -- returns the extension of the file uploaded by the user.   
    '''

    #For Debugging purposes
    print(filename.rsplit('.', 1)[1].lower())
    return filename.rsplit('.', 1)[1].lower()

