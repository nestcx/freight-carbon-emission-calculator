import os
import pandas as pd

from flask import request
from flask import redirect
from flask import url_for

from flask import jsonify
from flask import Blueprint
from flask import render_template

from afcc import maproutes
from afcc import calculation
from afcc import data_conversion

from flask import flash
import string

shipments_bp = Blueprint("shipments", __name__, url_prefix='/shipments', template_folder='templates', static_folder='static')


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
    'emissions' : []
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
    
@shipments_bp.route("/", methods=["GET", "POST"])
def newshipment():

    '''API endpoint for the front-end javascript file, gets contacted using axios
        
    Keyword Variables :

    data -- stores the data received from the front-end javascript.
    
    Returns:

    FILEDATA- It contains all the information regarding the trip including emissions
    '''   

    FILEDATA.clear()
    
    #For Debugging purposes
    print(FILEDATA)

    data = request.get_json(silent=True)

    #Sets all the data into the global variable FILEDATA
    FILEDATA['origin']=[data.get('pickuploc')]
    FILEDATA['destination']=[data.get('dropoffloc')]
    FILEDATA['itemWeight']=[int(data.get('weight'))]
    FILEDATA['itemQuantity']=[1]

    try:
        get_emission_calculation()
    except:
        print("Error")
    
    return FILEDATA

@shipments_bp.route("/new", methods=["GET", "POST"])
def shipments():

    '''Bring the uploaded file to the Flask Server and stores it into variable.
        
    Keyword Variables :

    file_ex -- stores the extension of the file.
    data -- retreives data from the file uploaded.
    fdata or final data -- converts the file data into a dictionary which is used to set shipments

    Returns:

    [render template of data.html] -- It sends back an html which is filled with the data upload.
    --- I could not find the fix for this. I tried to keep it in the same page but i got stuck here.---
    '''    
    FILEDATA.clear()

    #For Debugging purposes
    print(FILEDATA)

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
        
        #Sends data to set it into a local variable FILEDATA
        try:
            set_emission_calculation_factors(fdata)
        except:
            print("Error")

        #gets the emission calculation
        try:
            get_emission_calculation()
        except:
            print("Error")

        try:
            return render_template('data.html', data=FILEDATA)
        except:
            return -1

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
        

    for x in range(0 , length_of_data):
        startAddressInfo = maproutes.search_address(FILEDATA['origin'][x])
        endAddressInfo = maproutes.search_address(FILEDATA['destination'][x])

        startAddressValidated = startAddressInfo["features"][0]["properties"]["label"]
        endAddressValidated = endAddressInfo["features"][0]["properties"]["label"]

        startAddressCoordinates = startAddressInfo["features"][0]["geometry"]["coordinates"]
        endAddressCoordinates = endAddressInfo["features"][0]["geometry"]["coordinates"]

        geoJSONData = maproutes.get_route(str(startAddressCoordinates[0]) + "," + str(startAddressCoordinates[1]), str(endAddressCoordinates[0]) + "," + str(endAddressCoordinates[1]))

        dist_temp_array.append(data_conversion.metre_to_kilometre(maproutes.get_length_of_route(geoJSONData)))
        dur_temp_array.append(maproutes.get_duration_of_route(geoJSONData))

        #For Debugging Purposes
        print(dist_temp_array)
    #Stores distances and duration into the local array.
    FILEDATA['distance'] = dist_temp_array   
    FILEDATA['duration'] = dur_temp_array

    
    