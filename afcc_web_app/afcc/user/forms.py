from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
  email = StringField('email', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  remember_me = BooleanField('remember me')
  submit = SubmitField('log in')


class SignupForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  email = StringField('email', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  password_confirm = PasswordField('password', validators=[DataRequired(), EqualTo('password', 'Password confirmation must match password field')])
  submit = SubmitField('create account')
