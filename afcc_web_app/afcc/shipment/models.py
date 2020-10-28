from afcc.extensions import db

# TODO:  fix coordinates data-type.
class Shipment(db.Model):

    __tablename__ = 'shipment'

    shipment_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    shipment_created = db.Column(db.DateTime)
    shipment_name = db.Column(db.String(100), nullable=False)
    trip_distance = db.Column(db.Float, nullable=False)
    trip_duration = db.Column(db.Integer, nullable=False)
    load_weight = db.Column(db.Float, nullable=False)
    load_weight_unit = db.Column(db.String(20), nullable=False)
    load_volume = db.Column(db.Float, nullable=True) # Volume in cubic metres
    fuel_economy_adjustment = db.Column(db.Float, nullable=False)
    carbon_dioxide_emission = db.Column(db.Float, nullable=False)
    methane_emission = db.Column(db.Float, nullable=False)
    nitrous_oxide_emission = db.Column(db.Float, nullable=False)
    start_address = db.Column(db.String(255), nullable=False)
    start_address_coordinates = db.Column(db.String(255), nullable=False)
    end_address = db.Column(db.String(255), nullable=False)
    end_address_coordinates = db.Column(db.String(255), nullable=False)
    truck_configuration_id = db.Column(db.String(255), nullable=False)

class TruckConfiguration(db.Model):

    __tablename__ = 'truck_configuration'

    config_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    gcm = db.Column(db.String, nullable=False)
    payload = db.Column(db.Float, nullable=False)
    fuel_economy = db.Column(db.Integer, nullable=False)
    overall_length = db.Column(db.Float, nullable=False)