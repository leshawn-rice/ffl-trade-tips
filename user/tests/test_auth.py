from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase
from app.app import app
from user.auth import UserAuthentication
from user.models import UserModel

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ffl_trade_tips_test'
app.config['SQLALCHEMY_ECHO'] = False

test_db = SQLAlchemy()
test_db.app = app
test_db.init_app(app)


def add_to_test_db(item):
    test_db.session.add(item)
    test_db.session.commit()


def create_test_user(auth):
    test_username = 'testuser'
    test_email = 'test@email.com'
    test_password = auth.create_hashed_password('test_password')
    test_user = UserModel(username=test_username,
                          email=test_email, password=test_password)
    add_to_test_db(test_user)


class HashPasswordTestCase(TestCase):
    def setUp(self):
        self.auth = UserAuthentication()

    # Expected cases
    def test_lowercase(self):
        '''Testing for lower case password '''
        hashedpw = self.auth.create_hashed_password('password')
        self.assertIn('$2b$12$', hashedpw)

    def test_uppercase(self):
        '''Testing for upper case password '''
        hashedpw = self.auth.create_hashed_password('PASSWORD')
        self.assertIn('$2b$12$', hashedpw)

    def test_mixed_case(self):
        '''Testing for mixed case password '''
        hashedpw = self.auth.create_hashed_password('PassWord')
        self.assertIn('$2b$12$', hashedpw)

    def test_mixed_numbers(self):
        '''Testing for mixed case password with numbers '''
        hashedpw = self.auth.create_hashed_password('1PassW0rd7')
        self.assertIn('$2b$12$', hashedpw)

    def test_mixed_numbers_symbols(self):
        '''Testing for mixed case password with numbers and symbols '''

        hashedpw = self.auth.create_hashed_password('B@k3Ry!*+C@$h')
        self.assertIn('$2b$12$', hashedpw)

    # Edge Cases
    def test_no_args(self):
        '''Testing passing no arguments'''
        hashedpw = self.auth.create_hashed_password()
        self.assertIsNone(hashedpw)

    def test_nonetype_args(self):
        '''Testing passing arguments of type NoneType'''
        hashedpw = self.auth.create_hashed_password(None)
        self.assertIsNone(hashedpw)

    def test_int_args(self):
        '''Testing passing arguments of type Integer'''
        hashedpw = self.auth.create_hashed_password(15)
        self.assertIsNone(hashedpw)

    def test_bool_args(self):
        '''Testing passing arguments of type Boolean'''
        hashedpw = self.auth.create_hashed_password(True)
        self.assertIsNone(hashedpw)


class ComparePasswordTestCase(TestCase):
    def setUp(self):
        self.auth = UserAuthentication()

    # Expected cases
    def test_matching(self):
        '''Testing passwords that match completely'''
        pw = 'password'
        hashedpw = self.auth.create_hashed_password(pw)
        is_match = self.auth.compare_passwords(hashedpw, pw)
        self.assertTrue(is_match)

    def test_different_case(self):
        '''Testing passwords that match but have different casing'''
        hashedpw = self.auth.create_hashed_password('password')
        is_match = self.auth.compare_passwords(hashedpw, 'PassWord')
        self.assertFalse(is_match)

    def test_no_match(self):
        '''Testing passwords that do not match at all'''
        hashedpw = self.auth.create_hashed_password('password')
        is_match = self.auth.compare_passwords(hashedpw, 'bucket0fEggs')
        self.assertFalse(is_match)

    # Edge Cases
    def test_no_args(self):
        '''Testing passing no arguments'''
        is_match = self.auth.compare_passwords()
        self.assertFalse(is_match)

    def test_nonetype_args(self):
        '''Testing passing arguments of type NoneType'''
        hashedpw = None
        pw = None
        is_match = self.auth.compare_passwords(
            hashed_password=hashedpw, password=pw)
        self.assertFalse(is_match)

    def test_int_args(self):
        '''Testing passing arguments of type Integer'''
        hashedpw = 3
        pw = 3
        is_match = self.auth.compare_passwords(
            hashed_password=hashedpw, password=pw)
        self.assertFalse(is_match)

    def test_bool_args(self):
        '''Testing passing arguments of type Boolean'''
        hashedpw = True
        pw = True
        is_match = self.auth.compare_passwords(
            hashed_password=hashedpw, password=pw)
        self.assertFalse(is_match)


class VerifyNewPasswordTestCase(TestCase):
    def setUp(self):
        self.auth = UserAuthentication()

    def test_verify_new_password_match(self):
        '''Testing verify_new_password_match for matches & mismatches'''
        with app.test_client() as client:
            client.get('/')
            # Two matching passwords
            pw = 'password'
            confirm_pw = 'password'
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertTrue(is_match)
            # Passwords that match but have different casing
            pw = 'password'
            confirm_pw = 'Password'
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)
            # Passwords that do not match
            pw = 'password'
            confirm_pw = 'bucket0feggs'
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)

    def test_verify_new_password_invalid(self):
        '''Testing sending invalid data to verify_new_password_match'''
        with app.test_client() as client:
            client.get('/')
            # No args
            is_match = self.auth.verify_new_password_match()
            self.assertFalse(is_match)
            # NoneType args
            pw = None
            confirm_pw = None
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)
            # int args
            pw = 3
            confirm_pw = 3
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)
            # boolean args
            pw = True
            confirm_pw = True
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)


# class VerifyEmailTestCase(TestCase):
#     def setUpClass():
#         self.auth = UserAuthentication()

#     def setUp(self):
#         test_db.create_all()
#         create_test_user(auth=self.auth)

#     def tearDown(self):
#         test_db.drop_all()
