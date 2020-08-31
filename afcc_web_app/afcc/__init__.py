from flask import Flask
from flask import render_template

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

''' ##################  These are the imports for fielupload py  ################## '''
from flask import redirect
from flask import url_for
import pandas as pd
from flask import request
from flask import flash
import string

limiter = Limiter(key_func=get_remote_address, default_limits=["2000 per day", "100 per hour"])

def create_app():

    app = Flask(__name__, template_folder='templates', static_folder='static')

    limiter.init_app(app)

    # import blueprints.
    from afcc import maproutes, calculation, fileupload

    # register blueprints
    app.register_blueprint(maproutes.maproutes_bp)
    app.register_blueprint(calculation.calculation_bp)    
    app.register_blueprint(fileupload.fileupload_bp)

    
    @app.route("/")
    def index():
        return render_template("main.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")



    ''' ###############################################################################################
        ###############################################################################################
        ###############################################################################################
        ###############################################################################################
        
        All the data below this line is supposed to go to fileupload.py file. I put this data here since
        it didn't let me work with blueprint and always showed error /fileupload page not found.
        
        ###############################################################################################
        ###############################################################################################
        ###############################################################################################
        ###############################################################################################
        
        
        '''
    from afcc import data_conversion

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
        filename -- filename sent from the fileupload function from the file uploaded by the user.

        Returns:
        [File Extension] -- returns the extension of the file uploaded by the user.   
        '''

        #For Debugging purposes
        print(filename.rsplit('.', 1)[1].lower())
        return filename.rsplit('.', 1)[1].lower()
        

    @app.route("/fileupload", methods=["GET", "POST"])
    def fileupload():

        '''Bring the uploaded file to the Flask Server and stores it into variable.
            
        Keyword Variables :

        file_ex -- stores the extension of the file.
        data -- retreives data from the file uploaded.
        fdata or final data -- converts the file data into a dictionary which is used to set FILEUPLOAD

        Returns:

        [render template of data.html] -- It sends back an html which is filled with the data upload.
        --- I could not find the fix for this. I tried to keep it in the same page but i got stuck here.---
        '''

        file_ex = get_file_extension(file.filename)

        if request.method == "POST":
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file uploaded')
            return redirect(request.url)

            file = request.files["filename"]
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            #Checks if the file is excel or csv
            if file_ex='xlsx' or 'xls':
                data = pd.read_excel(file)
            elif file_ex='csv':
                data = pd.read_csv(file)
            
            fdata = data.to_dict()
            
            #Sends data to set it into a local variable FILEUPLOAD
            set_emission_calculation_factors(fdata)
            
            #gets the emission calculation
            get_emission_calculation()

            return render_template('data.html', data=data.to_dict())
    
    def set_emission_calculation_factors(fdata):

        #Sets the file data to different keys of FILEUPLOAD dictionary

        FILEDATA['origin']=fdata['From']
        FILEDATA['destination']=fdata['To']
        FILEDATA['itemQuantity']=fdata['Items']
        FILEDATA['itemWeight']=fdata['Weight']

        #For Debugging purposes
        print(FILEDATA['origin'][0],FILEDATA['destination'][0],FILEDATA['itemQuantity'][0],FILEDATA['itemWeight'][0])

    def get_emission_calculation():

        ''' Method to get the emission calculation

            Keyword Variables:
            length_of_data -- Checks the number of shipments uploaded in the excel/csv file
            emis_temp_array -- temporary array to store responses of emissions from caculation py file 

            All the emssions are stored in the FILEUPLOAD['emission'] which can be accessed using 
            FILEUPLOAD['emission'][x] where x is the number of shipment you want to access.
        '''

        calculate_distance_for_given_address()

        length_of_data=len(FILEDATA['origin'])

        emis_temp_array=[]

        for x in range(0 , length_of_data):
            emis_temp_array.append(calculation.calculate_emissions(18.1,FILEDATA['distance'][x],(FILEDATA['itemQuantity'][x])*(FILEDATA['itemWeight'][x])))

        FILEDATA['emission']=emis_temp_array
        #For Debugging Purposes
        print(FILEDATA['emission'])

    def calculate_distance_for_given_address():

        ''' Uses maproutes py to calculate distance for emission calculation

            Keyword Arguments:
            length_of_data -- Checks the number of shipments uploaded in the excel/csv file
            dist_temp_array -- Temporary array that stores all the distances
            dur_temp_array -- Temporary array that stores all the duration

        '''

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



    
        

    return app
