from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length

# Update Shipment Form
class UpdateForm(FlaskForm):
    id = IntegerField('id', validators=[DataRequired(
        message='Shipment Id must be present')])

    toAddress = StringField('to', validators=[
        DataRequired(message="Please enter end destination address")])

    fromAddress = StringField('from', validators=[
        DataRequired(message="PLease enter start destination address")])

    weight = IntegerField('weight', validators=[
        DataRequired(message="Please enter load weight")])

    unit = StringField('unit')

    submit = SubmitField('Update Shipment')
