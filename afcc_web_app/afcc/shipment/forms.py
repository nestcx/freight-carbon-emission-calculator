from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, Length, NumberRange

class ShipmentdataForm(FlaskForm):
    pickuploc = StringField('Pick up location', validators=[
        DataRequired(message='Must enter Pick up location'),
        Length(min=4, message='The length of the Pickup Location is too short')])

    dropoffloc = StringField('Drop off location', validators=[
        DataRequired(message='Must enter Pick up location'),
        Length(min=4, message='The length of the Pickup Location is too short')])

    cargoweight = IntegerField('Cargo Weight', validators=[
        DataRequired(message='Must enter an email address'),
        NumberRange(min=1, message='The value of weight entered is incorrect')])
    
    shipmentname = StringField('Shipment Name', validators=[
        DataRequired(message='Must enter a shipment name'),
        Length(min=4, message='The length of the Shipment name is too short')])

    weightunit = SelectField('Weight Unit', choices= [('kilograms (kgs)'),('pounds (lbs)')])


    submit = SubmitField('Add Shipment')
