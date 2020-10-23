from flask import Blueprint, request, render_template, url_for, redirect, flash
from afcc.extensions import db
from afcc.shipment.models import Shipment
from afcc.user.models import User
from flask_login import current_user




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

    # split search string on spaces
    splitted = input.split(" ")

    # generate query string for SQL based on query terms
    query_string = "SELECT shipment_id, shipment_name, uid FROM shipment WHERE TRUE"

    for i in range(len(splitted)):
        query_string = query_string + " AND (CAST(shipment_id AS TEXT) ILIKE '%%{}%%' OR shipment_name ILIKE '%%{}%%')".format(splitted[i], splitted[i])

    print(user.uid)

    query_string = query_string + "AND uid={} LIMIT 5;".format(user.uid)

    result = db.engine.execute(query_string)
    
    results_dict = {}

    d, a = {}, []
    for rowproxy in result:
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
        results_dict[d['shipment_id']] = d['shipment_name']

    return results_dict


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