from flask import Blueprint, request, render_template, url_for, redirect, flash
from afcc.extensions import db
from afcc.shipment.models import Shipment, TruckConfiguration
from afcc.user.models import User
from flask_login import current_user
from sqlalchemy import desc, cast, or_
from sqlalchemy.types import String



# create tools blueprint.
tools_bp = Blueprint(
    'tools', __name__, template_folder='tools-templates', static_folder='tools-static')


@tools_bp.route('/tools', methods=['GET'])
def tools():
    return render_template('tools.html')


@tools_bp.route('/tools/compare', methods=['GET'])
def compare():

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    return render_template('compare.html')




# WARNING: This is terrible code. 

@tools_bp.route('/tools/compare/search', methods=['GET'])
def search():

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

    # get the search string input
    input = request.args.get('q')
    
    search_id = "%%{}%%".format(input)

    result = Shipment.query.order_by(desc(Shipment.shipment_id)).\
        filter_by(uid=user.uid).\
        filter(
            (cast(Shipment.shipment_id, String ).ilike(search_id)) | 
            (Shipment.shipment_name.ilike(search_id)))\
            .limit(5)\
            .all()

    results_dict = {}
    
    i = 0
    for s in result:

        shipment_info = {
            'shipment_id': s.shipment_id, 
            'shipment_name': s.shipment_name, 
            'uid': s.uid
        }

        results_dict[i] = shipment_info
        i = i + 1

    return results_dict


@tools_bp.route('/tools/compare/shipment_information', methods=['GET'])
def shipment_information():

    # get the search string input
    shipment_id = request.args.get('id')

    # authenticate user
    authentication = authenticate_user()
    if authentication[0] is True: user = authentication[1]
    elif authentication[0] is False: return redirect(url_for(authentication[1]))

     # get shipment.
    try:
        shipment = Shipment.query.get(shipment_id)
    except Exception:
        return "error"
    
     # check shipment exists and belongs to user.
    result = check_user_shipment(user, shipment)
    if result is False:
        return "error"

    result = {}
    result["shipment_id"] = shipment.shipment_id
    result["carbon_dioxide"] = shipment.carbon_dioxide_emission
    result["name"] = shipment.shipment_name
    result["trip_distance"] = shipment.trip_distance
    result["trip_duration"] = shipment.trip_duration
    result["load_weight"] = shipment.load_weight
    result["load_weight_unit"] = shipment.load_weight_unit
    result["start_address"] = shipment.start_address
    result["end_address"] = shipment.end_address

    # get truck name from truck id
    truck_name = TruckConfiguration.query.get(shipment.truck_configuration_id).description
    result["truck_id"] = truck_name
    
    return result
    
    




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