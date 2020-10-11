from afcc.extensions import db

class Route(db.Model):

    point_a_region_name = db.Column(db.String(100))
    point_a_postcode = db.Column(db.Integer, nullable=False, primary_key=True)
    point_a_lat = db.Column(db.Float, nullable=False)
    point_a_long = db.Column(db.Float, nullable=False)

    point_b_region_name = db.Column(db.String(100))
    point_b_postcode = db.Column(db.Integer, nullable=False, primary_key=True)
    point_b_lat = db.Column(db.Float, nullable=False)
    point_b_long = db.Column(db.Float, nullable=False)

    route_distance_in_km = db.Column(db.Float, nullable=False)
    estimated_duration_in_seconds = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.Date, nullable=False)


class Postcode(db.Model):
    postcode = db.Column(db.Integer, nullable=False, primary_key=True)
    region_name = db.Column(db.String(200), nullable=False)
    long = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)

