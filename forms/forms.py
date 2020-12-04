from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField, SelectField, PasswordField, IntegerField, FloatField
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


class SelectTeamForm(FlaskForm):
    team = SelectField('Team')


class SearchTradeForm(FlaskForm):
    '''
    Form for searching for a player
    Fields:
            position, position rank minimum, position rank maximum, point minimum, point maximum
    Validation:
                Only position required

    '''
    position = SelectField('Position', choices=[
        (pos, pos) for pos in POSITIONS], validators=[InputRequired()])
    pos_rank_min = IntegerField('Rank Min', validators=[Optional(),
                                                        NumberRange(min=1, max=100)])
    pos_rank_max = IntegerField('Rank Max', validators=[Optional(),
                                                        NumberRange(min=1, max=100)])
    points_min = FloatField('Points Min', validators=[Optional(),
                                                      NumberRange(min=1, max=1000)])
    points_max = FloatField('Points Max', validators=[Optional(),
                                                      NumberRange(min=1, max=1000)])
    grade = SelectField(
        'Grade', choices=['A', 'B', 'C', 'D', 'F'], validators=[Optional()])
