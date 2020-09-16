from afcc.extensions import db

# TODO:  fix coordinates data-type.
class Shipment(db.Model):
    shipment_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    shipment_created = db.Column(db.DateTime, nullable=False)
    shipment_name = db.Column(db.String(100), nullable=False)
    trip_distance = db.Column(db.Float, nullable=False)
    trip_duration = db.Column(db.Integer, nullable=False)
    fuel_economy_adjustment = db.Column(db.Float, nullable=False)
    carbon_dioxide_emission = db.Column(db.Float, nullable=False)
    methane_emission = db.Column(db.Float, nullable=False)
    nitrous_oxide_emission = db.Column(db.Float, nullable=False)
    start_address = db.Column(db.String(255), nullable=False)
    start_address_coordinates = db.Column(db.String(255), nullable=False)
    end_address = db.Column(db.String(255), nullable=False)
    end_address_coordinates = db.Column(db.String(255), nullable=False)