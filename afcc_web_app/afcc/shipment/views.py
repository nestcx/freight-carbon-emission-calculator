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
@shipment_bp.route('/uploadshipments', methods=['GET', 'POST'])
def CR_shipments():

    shipment_form=ShipmentdataForm()
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
        render_template('dashboard.html', shipments=shipments)

    if request.method == "POST":
    
        file = request.files["filename"]
        file_ex = get_file_extension(file.filename)
        
        #Checks if the file is excel or csv
        if file_ex == 'xlsx' or 'xls':
            data = pd.read_excel(file)
        elif file_ex =='csv':
            data = pd.read_csv(file)
        else:
            flash("Wrong File input")
        
        fdata = data.to_dict()
            
        result = {}

        #This for loop is to read all the elements of shipments
        #len(fdata['To']) is used to find number of shipments in the excel file
        #result is an array of dictionary.
        #To access result you will have to use result[i]['Key']
        #For eg. result[1]['distance']=[{},{distance},{},{},{},{},{}....]
        for i in range(0, len(fdata['To'])):
            result[i]=calculation.get_emission_calculation(fdata['From'][i],fdata['To'][i],fdata['Weight'][i],fdata['Items'][i])    


        for i in range(0, len(fdata['To'])):
            new_shipment=Shipment(uid = user.uid,shipment_created = datetime.datetime.now(),
            trip_distance = result[i]['distance'],trip_duration =result[i]['duration'] ,
            fuel_economy_adjustment = result[i]['emission']["adjusted_fuel_economy"] ,
            carbon_dioxide_emission = result[i]['emission']['carbon_dioxide_emission']  ,
            methane_emission = result[i]['emission']['methane_emission'],
            nitrous_oxide_emission = result[i]['emission']['nitrous_oxide_emission']
            ,start_address = result[i]['origin'] ,
            start_address_coordinates = str(result[i]['origincoords'][0])+","+str(result[i]['origincoords'][1]),
            end_address = result[i]['destination'] ,
            end_address_coordinates = str(result[i]['destcoords'][0])+","+str(result[i]['destcoords'][0]) )
            
            db.session.add(new_shipment)
            db.session.commit()

    return render_template('dashboard.html')

@shipment_bp.route('/shipments', methods=['GET'])
def show_upload_shipment_form():
    shipment_form=ShipmentdataForm()
    return render_template('uploadshipments.html', form=shipment_form)

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
            #origincoords[0] in start address coordinates in query is used because that value
            #is an array of two float values, which is why in start address coordinates I am converting
            #that to a string value.            
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

