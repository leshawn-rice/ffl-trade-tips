from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Regexp, NumberRange, Optional, EqualTo
from espn.settings import POSITIONS


class CreateUserForm(FlaskForm):
    '''
    Form for creating a new user
    Fields:
            email, username, password
    Validation:
                All inputs required, password must be 8+ characters with one or more upper/lower case 
                letters and one or more numbers

    '''
    # Add validation for username length (no more than 20 per db)
    email = StringField('Email', validators=[InputRequired(
        message='Email cannot be blank!'), Email(message='Invalid Email!')])
    username = StringField('Username', validators=[
                           InputRequired(message='Username cannot be blank!')])
    password = PasswordField('Password', validators=[
        InputRequired(), Regexp('(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', message='Invalid Password!')])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(), Regexp('(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', message='Invalid Password!'), EqualTo('password', message='Passwords must match!')])


class LoginForm(FlaskForm):
    '''
    Form for logging a user in
    Fields:
            username, password
    Validation:
                No validation, if a username and password are
                returned as invalid, message is flashed to user 
                saying username and password don't match

    '''
    username = StringField('Username')
    password = PasswordField('Password')


class AddLeagueForm(FlaskForm):
    league_id = IntegerField('League ID', validators=[
                             InputRequired(message='You must enter a League ID!')])
    year = IntegerField('Year', validators=[InputRequired(
        message='You must enter a year!'), NumberRange(min=2000, max=2021)])
    is_ppr = BooleanField('PPR', validators=[Optional()])


class ContactForm(FlaskForm):
    '''
    Form for creating a new user
    Fields:
            email, username, password
    Validation:
                All inputs required, password must be 8+ characters with one or more upper/lower case 
                letters and one or more numbers

    '''
    # Add validation for username length (no more than 20 per db)
    email = StringField('Email', validators=[InputRequired(
        message='Email cannot be blank!'), Email(message='Invalid Email!')])
    message = TextAreaField('Message', validators=[
        InputRequired(message='Message cannot be blank!')])