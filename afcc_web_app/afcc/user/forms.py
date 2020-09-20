from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Length


class LoginForm(FlaskForm):
    email = StringField('email', validators=[
        DataRequired(message='Must enter an email address'), 
        Email(message='Must enter a valid email address')])

    password = PasswordField('password', validators=[
        DataRequired(message='Must enter a password')])

    remember_me = BooleanField('remember me')
    submit = SubmitField('log in')


class SignupForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(message='Must enter a username'),
        Length(min=3, message='The length of the username is too short')])

    email = StringField('email', validators=[
        DataRequired(message='Must enter an email address'),
        Email(message='Must enter a valid email address')])

    password = PasswordField('password', validators=[
        DataRequired(message='Must enter a password'),
        Length(min=6, message='Your password is too short. Please choose a longer password')])

    password_confirm = PasswordField('confirm password', validators=[
        DataRequired(message='Password confirmation must match password field'),
        EqualTo('password', message='Password confirmation must match password field')])

    submit = SubmitField('create account')


class UserSettingsForm(FlaskForm):
    username = StringField('Username / Display name', validators=[
        DataRequired(message='Must enter a username'),
        Length(min=3, message='The length of the username is too short')])

    update_settings = SubmitField('Update user settings')


class PasswordUpdateForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[
        DataRequired(message='Must enter your previous password'),
        Length(min=6, message='The password is too short')])

    new_password = PasswordField('New password', validators=[
        DataRequired(message='Must enter a new password'),
        Length(min=6, message='Your password is too short. Please choose a longer password')])

    password_confirm = PasswordField('Confirm new password', validators=[
        DataRequired(message='Password confirmation must match password field'),
        EqualTo('new_password', message='Password confirmation must match password field')])

    change_password = SubmitField('Update password')
