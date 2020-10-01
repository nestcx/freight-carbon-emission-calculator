from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

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