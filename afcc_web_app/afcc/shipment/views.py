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
        #Sets all the data into the global variable FILEDATA
        FILEDATA['origin']=[shipment_form.pickuploc.data]
        FILEDATA['destination']=[shipment_form.dropoffloc.data]
        FILEDATA['itemWeight']=[(shipment_form.cargoweight.data)]
        FILEDATA['itemQuantity']=[1]
        FILEDATA['name']=[shipment_form.shipmentname.data]

        print(FILEDATA)

        try:
            get_emission_calculation()
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
            
            new_shipment=Shipment(shipment_id = 123 ,uid = user.uid,shipment_created = datetime.datetime.now(),
            shipment_name =FILEDATA['name'][0] ,trip_distance = FILEDATA['distance'][0],trip_duration =FILEDATA['duration'][0] ,
            fuel_economy_adjustment = FILEDATA['emissions'][0]["adjusted_fuel_economy"] ,
            carbon_dioxide_emission = FILEDATA['emissions'][0]['emissions']['carbon_dioxide_emission']  ,
            methane_emission = FILEDATA['emissions'][0]['emissions']['methane_emission'],
            nitrous_oxide_emission = FILEDATA['emissions'][0]['emissions']['nitrous_oxide_emission']
            ,start_address = FILEDATA['emissions'][0]["location"]["start_location"]["address"] ,
            start_address_coordinates = FILEDATA['emissions'][0]["location"]["start_location"]["coordinate"] ,
            end_address = FILEDATA['emissions'][0]["location"]["end_location"]["address"] ,
            end_address_coordinates = FILEDATA['emissions'][0]["location"]["end_location"]["coordinate"] )
            
            db.session.add(new_shipment)
            db.session.commit()
        

    return render_template('dashboard.html')


# GET  /shipments/new  -  show form to create new shipment
@shipment_bp.route('/shipments/new', methods=['GET'])
def show_create_shipment_form():
    FILEDATA.clear()
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


##########################################################################################################
#####################################      Calculation part            ###################################
#####################################             Below                ###################################
##########################################################################################################

#FILEDATA -- local variable which is used to manipulate all the file data.
#   It only stores data needed for calculation. Calculation emission is also included in this 
#   dictionary once the emissions are calculated.   

FILEDATA={
    'origin' : [],
    'destination' : [],
    'itemQuantity' : [],
    'itemWeight' : [],
    'distance' : [],
    'duration' :[],
    'emissions' : [],
    'name' : [],
    'origincoords' : [],
    'destcoords' : []
    }


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

def set_emission_calculation_factors(fdata):
    
    #Sets the file data to different keys of FILEDATA dictionary

    FILEDATA['origin']=fdata['From']
    FILEDATA['destination']=fdata['To']
    FILEDATA['itemQuantity']=(fdata['Items'])
    FILEDATA['itemWeight']=(fdata['Weight'])

    #For Debugging purposes
    print(FILEDATA['origin'][0],FILEDATA['destination'][0],FILEDATA['itemQuantity'][0],FILEDATA['itemWeight'][0])

def get_emission_calculation():

    ''' Method to get the emission calculation

        Keyword Variables:
        length_of_data -- Checks the number of shipments uploaded in the excel/csv file
        emis_temp_array -- temporary array to store responses of emissions from caculation py file 

        All the emssions are stored in the FILEDATA['emission'] which can be accessed using 
        FILEDATA['emission'][x] where x is the number of shipment you want to access.
    '''
    #For Debugging purposes
    print('Flag - Calculate Emission Function')
    #print(FILEDATA['origin'],FILEDATA['destination'],FILEDATA['itemQuantity'],FILEDATA['itemWeight'])

    calculate_distance_for_given_address()

    #For Debugging purposes
    print('Flag - End Calculate Distance Function')

    length_of_data=len(FILEDATA['origin'])
    
    emis_temp_array=[]

    #For Debugging purposes
    print('Flag - Entered Calculate Emission Function ')
    
    for x in range(0 , length_of_data):
        emis_temp_array.append(calculation.calculate_emissions(18.1,FILEDATA['distance'][x],(FILEDATA['itemQuantity'][x])*(FILEDATA['itemWeight'][x])))

    #For Debugging purposes
    print('Flag - Calculate Emission Function done')

    FILEDATA['emission']=emis_temp_array
    #For Debugging Purposes
    print(FILEDATA['emission'])
    return FILEDATA

def calculate_distance_for_given_address():

    ''' Uses maproutes py to calculate distance for emission calculation

        Keyword Arguments:
        length_of_data -- Checks the number of shipments uploaded in the excel/csv file
        dist_temp_array -- Temporary array that stores all the distances
        dur_temp_array -- Temporary array that stores all the duration

    '''
    print('Flag - Calculate Distance Function')

    length_of_data=len(FILEDATA['origin'])
    
    #For Debugging Purposes
    print(length_of_data)
 
    dist_temp_array=[]
    dur_temp_array=[]

    start_coords=[]
    end_coords=[]        

    for x in range(0 , length_of_data):
        startAddressInfo = maproutes.search_address(FILEDATA['origin'][x])
        endAddressInfo = maproutes.search_address(FILEDATA['destination'][x])

        startAddressValidated = startAddressInfo["features"][0]["properties"]["label"]
        endAddressValidated = endAddressInfo["features"][0]["properties"]["label"]

        startAddressCoordinates = startAddressInfo["features"][0]["geometry"]["coordinates"]
        endAddressCoordinates = endAddressInfo["features"][0]["geometry"]["coordinates"]

        start_coords.append(startAddressCoordinates)
        end_coords.append(endAddressCoordinates)

        geoJSONData = maproutes.get_route(str(startAddressCoordinates[0]) + "," + str(startAddressCoordinates[1]), str(endAddressCoordinates[0]) + "," + str(endAddressCoordinates[1]))

        dist_temp_array.append(data_conversion.metre_to_kilometre(maproutes.get_length_of_route(geoJSONData)))
        dur_temp_array.append(maproutes.get_duration_of_route(geoJSONData))

        #For Debugging Purposes
        print(dist_temp_array)
    #Stores distances and duration into the local array.
    FILEDATA['distance'] = dist_temp_array   
    FILEDATA['duration'] = dur_temp_array
    FILEDATA['origincoords'] = start_coords
    FILEDATA['destcoords'] = end_coords