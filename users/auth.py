from flask import flash, session
from flask_bcrypt import Bcrypt
from app.database import add_to_db
from espn.classes.base_classes import ESPNRequest
from espn.classes.espn_classes import League
from users.models import UserModel


bcrypt = Bcrypt()


class UserAuthentication:
    def create_hashed_password(self, password):
        '''
        Creates and returns a hashed version of the
        given password
        '''
        hashed_password = bcrypt.generate_password_hash(
            password)
        return hashed_password.decode('utf8')

    def compare_passwords(self, hashed_password, password):
        '''
        Compares the hashed password to the plain text password,
        returns True if they match, otherwise returns False
        '''
        return bcrypt.check_password_hash(hashed_password, password)

    def verify_password_match(self, password, confirm_password):
        '''
        Verifies the given passwords match each other
        '''
        if password == confirm_password:
            return True
        else:
            flash('Passwords Must Match!')
            return False

    def verify_email_unique(self, email):
        '''
        Verifies the given email does not exist
        in UserModel table
        '''
        if not UserModel.query.filter_by(email=email).first():
            return True
        else:
            session['email_taken'] = True
            return False

    def verify_username_unique(self, username):
        '''
        Verifies the given username does not exist
        in UserModel table
        '''
        if not UserModel.query.filter_by(username=username).first():
            return True
        else:
            session['username_taken'] = True
            return False

    def verify_user_data(self, user_data):
        '''
        Verifies that none of the given user data
        conflicts with existing users, and that
        the given passwords match. Returns True
        or False based on the result
        '''
        [email, username, password, confirm_password] = user_data

        if self.verify_username_unique(username) and self.verify_email_unique(email) and self.verify_password_match(password, confirm_password):
            return True
        else:
            return False

    def get_user_data(self, form):
        '''
        Gets the entered data from the form
        and returns it as a list
        '''
        email = form.email.data
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        return [email, username, password, confirm_password]

    def create_user(self, user_data):
        '''
        Creates a new user with the given user_data,
        adds them to the db, and sets the user's id 
        into the session.
        '''
        [email, username, password, confirm_password] = user_data
        hashed_password = self.create_hashed_password(password)
        new_user = UserModel(
            email=email, username=username, password=hashed_password)
        add_to_db(new_user)
        session['user_id'] = new_user.id
        return new_user

    def sign_up(self, form):
        '''
        Drives the logic behind signing up a new user
        Gets data from the form,
        Verifies the data does not conflict with an
        existing user,
        Hashes the password,
        Creates a new user,
        And logs the user in
        '''
        new_user_data = self.get_user_data(form)
        if self.verify_user_data(new_user_data):
            return self.create_user(new_user_data)
        else:
            return False

    def log_in(self, form):
        '''
        Checks if the username and password match a record
        in the UserModel table with the given username.
        If so, sets the session['user_id'] to the user's id
        and returns True. Otherwise, flashes 'Username/Password'
        do not match and returns False
        '''
        username = form.username.data
        password = form.password.data

        user = UserModel.query.filter(
            username.upper() == username.upper()).first()

        has_correct_password = self.compare_passwords(user.password, password)

        if has_correct_password:
            session['user_id'] = user.id
            return True
        else:
            flash('Username/Password do not match!')
            return False

    def get_league_data(self, form):
        '''
        Gets league data from the form,
        then gets data from the api given
        the form data, and returns it
        '''
        league_id = form.league_id.data
        year = form.year.data
        espn_request = ESPNRequest(league_id=league_id, year=year)
        data = espn_request.get_response_data()
        return [league_id, year, data]

    def add_league(self, form):
        '''
        Adds a league to the database
        with the given form data. If successful,
        returns True, otherwise flashes a message
        to the user and returns false
        '''
        user_id = session.get('user_id')
        if not user_id:
            flash('You need to login to do that!')
            return False

        [league_id, year, data] = self.get_league_data(form)

        if data.get('teams'):
            league = League(league_id=league_id, year=year, user_id=user_id)
            return True
        else:
            flash('Invalid League ID and/or year!')
            return False
