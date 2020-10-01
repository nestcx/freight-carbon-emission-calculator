from flask_wtf import FlaskForm

################################### SAIS 
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
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

    weightunit = SelectField('Weight Unit', choices= [('kilograms (kgs)'),('pounds (lbs)')])
        
    shipmentname = StringField('Shipment Name', validators=[
        DataRequired(message='Must enter a shipment name'),
        Length(min=4, message='The length of the Shipment name is too short')])


    submit = SubmitField('Add Shipment')
from wtforms import StringField, DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


################################################################## MARCUS'
class CreateShipmentForm(FlaskForm):
    shipment_name = StringField('Shipment Name', validators =[
        Length(min=4, message='Shipment name must be at least 4 characters')
    ])

    start_address = StringField('Start Address', validators =[
        DataRequired(message='Please enter a start location'),
        Length(min=2, message='Start location must be longer than 2 characters')
    ])

    end_address = StringField('End Address', validators =[
        DataRequired(message='Please enter an end location'),
        Length(min=2, message='End location must be longer than 2 characters')
    ])

    load_weight = DecimalField('Load Weight', validators=[
        DataRequired(message='Please enter a load weight')
    ])

    load_weight_unit = SelectField('Load Weight Unit', choices=[
        ('kilogram', 'Kilograms'), 
        ('tonne', 'Tonnes')],
        validators = [DataRequired(message='Please enter a load weight unit')])

    submit = SubmitField('Create Shipment')

class EditShipmentForm(FlaskForm):
    shipment_name = StringField('Shipment Name', validators =[
        Length(min=4, message='Shipment name must be at least 4 characters')
    ])

    start_address = StringField('Start Address', validators =[
        DataRequired(message='Please enter a start location'),
        Length(min=2, message='Start location must be longer than 2 characters')
    ])

    end_address = StringField('End Address', validators =[
        DataRequired(message='Please enter an end location'),
        Length(min=2, message='End location must be longer than 2 characters')
    ])

    load_weight = DecimalField('Load Weight', validators=[
        DataRequired(message='Please enter a load weight')
    ])

    load_weight_unit = SelectField('Load Weight Unit', choices=[
        ('kilogram', 'Kilograms'), 
        ('tonne', 'Tonnes')], 
        validators = [DataRequired(message='Please enter a load weight unit')])

    submit = SubmitField('Edit Shipment')
