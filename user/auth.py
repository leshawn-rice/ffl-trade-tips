from flask import flash, session
from flask_bcrypt import Bcrypt
from app.database import add_to_db, delete_from_db
from espn.classes.base_classes import ESPNRequest
from espn.classes.espn_classes import League
from user.models import UserModel


bcrypt = Bcrypt()


class UserAuthentication:
    def create_hashed_password(self, password=None):
        '''
        Creates and returns a hashed version of the
        given password
        '''
        # If the password is None or not a string, return None
        if not password or not isinstance(password, str):
            return None

        hashed_password = bcrypt.generate_password_hash(
            password)
        return hashed_password.decode('utf8')

    def compare_passwords(self, hashed_password=None, password=None):
        '''
        Compares the hashed password to the plain text password,
        returns True if they match, otherwise returns False
        '''
        if not hashed_password or not password:
            return False

        if not isinstance(hashed_password, str) or not isinstance(password, str):
            return False

        return bcrypt.check_password_hash(hashed_password, password)

    def verify_new_password_match(self, password=None, confirm_password=None):
        '''
        Verifies the given passwords match each other
        '''

        if not password or not confirm_password:
            flash('Neither password can be blank!')
            return False

        if not isinstance(password, str) or not isinstance(confirm_password, str):
            flash('Invalid password!')
            return False

        if password == confirm_password:
            return True
        else:
            flash('Passwords Must Match!')
            return False

    def verify_email_unique(self, email=None):
        '''
        Verifies the given email does not exist
        in UserModel table
        '''

        if not email or not isinstance(email, str):
            return False

        if not UserModel.query.filter(UserModel.email.ilike(email)).first():
            return True
        else:
            session['email_taken'] = True
            return False

    def verify_username_unique(self, username=None):
        '''
        Verifies the given username does not exist
        in UserModel table
        '''

        if not username or not isinstance(username, str):
            return False

        if not UserModel.query.filter(UserModel.username.ilike(username)).first():
            return True
        else:
            session['username_taken'] = True
            return False

    def verify_user_data(self, user_data=None):
        '''
        Verifies that none of the given user data
        conflicts with existing users, and that
        the given passwords match. Returns True
        or False based on the result
        '''
        if not user_data:
            return False

        for item in user_data:
            if not isinstance(item, str):
                return False

        [email, username, password, confirm_password] = user_data

        if self.verify_username_unique(username) and self.verify_email_unique(email) and self.verify_new_password_match(password, confirm_password):
            return True
        else:
            return False

    def get_new_user_data(self, form=None):
        '''
        Gets the entered data from the form
        and returns it as a list
        '''

        if not form:
            return None

        try:
            email = form.email.data
            username = form.username.data
            password = form.password.data
            confirm_password = form.confirm_password.data
        except AttributeError:
            return None

        data = [email, username, password, confirm_password]

        for item in data:
            if not isinstance(item, str):
                return None

        return data

    def create_user(self, user_data=None):
        '''
        Creates a new user with the given user_data,
        adds them to the db, and sets the user's id 
        into the session.
        '''
        if not user_data:
            return None

        [email, username, password, confirm_password] = user_data

        for item in user_data:
            if not item or not isinstance(item, str):
                return None

        hashed_password = self.create_hashed_password(password)
        new_user = UserModel(
            email=email, username=username, password=hashed_password)
        add_to_db(new_user)
        session['user_id'] = new_user.id
        return new_user

    def delete(self, user_id):
        '''
        Deletes the user with user_id
        from the database and flashes 
        a success message
        404's if the user_id can't be found
        '''
        user = UserModel.query.get(user_id)
        if not user:
            flash('Account could not be deleted!', 'danger')
            return
        else:
            delete_from_db(user)
            flash('Account Deleted Successfuly', 'success')

    def sign_up(self, form=None):
        '''
        Drives the logic behind signing up a new user
        Gets data from the form,
        Verifies the data does not conflict with an
        existing user,
        Hashes the password,
        Creates a new user,
        And logs the user in
        '''

        if not form:
            return False

        new_user_data = self.get_new_user_data(form)
        if not new_user_data:
            return False
        if self.verify_user_data(new_user_data):
            return self.create_user(new_user_data)
        else:
            return False

    def log_in(self, form=None):
        '''
        Checks if the username and password match a record
        in the UserModel table with the given username.
        If so, sets the session['user_id'] to the user's id
        and returns True. Otherwise, flashes 'Username/Password'
        do not match and returns False
        '''
        if not form:
            return False

        try:
            username = form.username.data
            password = form.password.data
        except AttributeError:
            return False

        if not isinstance(username, str) or not isinstance(password, str):
            return False

        user = UserModel.query.filter(
            username.upper() == username.upper()).first()

        if user:
            if self.compare_passwords(user.password, password):
                session['user_id'] = user.id
                return True
            else:
                flash('Username/Password do not match!')
                return False
        else:
            flash('Username/Password do not match!')
            return False
