from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase
from app.app import app
from app.database import db, add_to_db, delete_from_db
from app.forms import CreateUserForm, LoginForm
from user.auth import UserAuthentication
from user.models import UserModel

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ffl_trade_tips_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()


def create_test_user(auth):
    test_username = 'testuser'
    test_email = 'test@email.com'
    test_password = auth.create_hashed_password('test_password')
    test_user = UserModel(username=test_username,
                          email=test_email, password=test_password)
    db.session.add(test_user)


class HashPasswordTestCase(TestCase):
    '''Test Case for UserAuthentication.create_hashed_password()'''

    def setUp(self):
        self.auth = UserAuthentication()

    def test_lowercase(self):
        '''Testing password '''
        hashedpw = self.auth.create_hashed_password('password')
        self.assertIn('$2b$12$', hashedpw)

    def test_uppercase(self):
        '''Testing PASSWORD'''
        hashedpw = self.auth.create_hashed_password('PASSWORD')
        self.assertIn('$2b$12$', hashedpw)

    def test_mixed_case(self):
        '''Testing PassWord'''
        hashedpw = self.auth.create_hashed_password('PassWord')
        self.assertIn('$2b$12$', hashedpw)

    def test_mixed_numbers(self):
        '''Testing 1PassW0rd7'''
        hashedpw = self.auth.create_hashed_password('1PassW0rd7')
        self.assertIn('$2b$12$', hashedpw)

    def test_mixed_numbers_symbols(self):
        '''Testing B@k3Ry!*+C@$h'''

        hashedpw = self.auth.create_hashed_password('B@k3Ry!*+C@$h')
        self.assertIn('$2b$12$', hashedpw)

    def test_invalid(self):
        '''Testing passing invalid passwords'''
        # No args
        hashedpw = self.auth.create_hashed_password()
        self.assertIsNone(hashedpw)
        # NoneType arg
        hashedpw = self.auth.create_hashed_password(None)
        self.assertIsNone(hashedpw)
        # Integer arg
        hashedpw = self.auth.create_hashed_password(15)
        self.assertIsNone(hashedpw)
        # Boolean arg
        hashedpw = self.auth.create_hashed_password(True)
        self.assertIsNone(hashedpw)


class ComparePasswordTestCase(TestCase):
    '''Test Case for UserAuthentication.compare_passwords()'''

    def setUp(self):
        self.auth = UserAuthentication()

    def test_match(self):
        '''Testing password vs hash for password'''
        pw = 'password'
        hashedpw = self.auth.create_hashed_password(pw)
        is_match = self.auth.compare_passwords(hashedpw, pw)
        self.assertTrue(is_match)

    def test_different_case(self):
        '''Testing password vs hash for PassWord'''
        hashedpw = self.auth.create_hashed_password('password')
        is_match = self.auth.compare_passwords(hashedpw, 'PassWord')
        self.assertFalse(is_match)

    def test_no_match(self):
        '''Testing password vs hash for bucket0fEggs'''
        hashedpw = self.auth.create_hashed_password('password')
        is_match = self.auth.compare_passwords(hashedpw, 'bucket0fEggs')
        self.assertFalse(is_match)

    def test_invalid(self):
        '''Testing passing invalid password/passwordhashes'''
        # No passwords
        is_match = self.auth.compare_passwords()
        self.assertFalse(is_match)
        # NoneType passwords
        is_match = self.auth.compare_passwords(
            hashed_password=None, password=None)
        self.assertFalse(is_match)
        # Integer passwords
        is_match = self.auth.compare_passwords(
            hashed_password=17, password=17)
        self.assertFalse(is_match)
        # Boolean passwords
        is_match = self.auth.compare_passwords(
            hashed_password=True, password=True)
        self.assertFalse(is_match)


class VerifyNewPasswordTestCase(TestCase):
    '''Test Case for UserAuthentication.verify_new_password_match()'''

    def setUp(self):
        self.auth = UserAuthentication()

    def test_match(self):
        '''Testing password vs password'''
        with app.test_client() as client:
            client.get('/')
            pw = 'password'
            confirm_pw = 'password'
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertTrue(is_match)

    def test_different_case(self):
        '''Testing password vs PassWord'''
        with app.test_client() as client:
            client.get('/')
            pw = 'password'
            confirm_pw = 'PassWord'
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)

    def test_no_match(self):
        '''Testing password vs bucket0fEggs'''
        with app.test_client() as client:
            client.get('/')
            pw = 'password'
            confirm_pw = 'bucket0fEggs'
            is_match = self.auth.verify_new_password_match(
                password=pw, confirm_password=confirm_pw)
            self.assertFalse(is_match)

    def test_invalid(self):
        '''Testing passing invalid passwords'''
        with app.test_client() as client:
            client.get('/')
            # No passwords
            is_match = self.auth.verify_new_password_match()
            self.assertFalse(is_match)
            # NoneType passwords
            is_match = self.auth.verify_new_password_match(
                password=None, confirm_password=None)
            self.assertFalse(is_match)
            # Integer passwords
            is_match = self.auth.verify_new_password_match(
                password=3, confirm_password=3)
            self.assertFalse(is_match)
            # Boolean passwords
            is_match = self.auth.verify_new_password_match(
                password=True, confirm_password=True)
            self.assertFalse(is_match)


class VerifyEmailTestCase(TestCase):
    '''Test Case for UserAuthentication.verify_email_unique()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()

    def test_match(self):
        '''Testing test@email.com vs test@email.com'''
        with app.test_client() as client:
            client.get('/')
            email = 'test@email.com'
            is_unique = self.auth.verify_email_unique(email=email)
            self.assertFalse(is_unique)

    def test_different_case(self):
        '''Testing TeSt@emAiL.coM vs test@email.com'''
        with app.test_client() as client:
            client.get('/')
            email = 'TeSt@emAiL.coM'
            is_unique = self.auth.verify_email_unique(email=email)
            self.assertFalse(is_unique)

    def test_unique(self):
        '''Testing buttersoup@dairy.com vs test@email.com'''
        with app.test_client() as client:
            client.get('/')
            email = 'buttersoup@dairy.com'
            is_unique = self.auth.verify_email_unique(email=email)
            self.assertTrue(is_unique)

    def test_invalid(self):
        '''Testing passing an invalid email'''
        with app.test_client() as client:
            client.get('/')
            # No email
            is_unique = self.auth.verify_email_unique()
            self.assertFalse(is_unique)
            # NoneType email
            is_unique = self.auth.verify_email_unique(email=None)
            self.assertFalse(is_unique)
            # Integer email
            is_unique = self.auth.verify_email_unique(email=7)
            self.assertFalse(is_unique)
            # Boolean email
            is_unique = self.auth.verify_email_unique(email=True)
            self.assertFalse(is_unique)


class VerifyUsernameTestCase(TestCase):
    '''Test Case for UserAuthentication.verify_username_unique()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()

    def test_match(self):
        '''Testing testuser vs testuser'''
        with app.test_client() as client:
            client.get('/')
            username = 'testuser'
            is_unique = self.auth.verify_username_unique(username=username)
            self.assertFalse(is_unique)

    def test_different_case(self):
        '''Testing TeStUSer vs testuser'''
        with app.test_client() as client:
            client.get('/')
            username = 'TeStUSer'
            is_unique = self.auth.verify_username_unique(username=username)
            self.assertFalse(is_unique)

    def test_unique(self):
        '''Testing M33rkatse7en vs testuser'''
        with app.test_client() as client:
            client.get('/')
            username = 'M33rkatse7en'
            is_unique = self.auth.verify_username_unique(username=username)
            self.assertTrue(is_unique)

    def test_invalid(self):
        '''Testing passing invalid username'''
        with app.test_client() as client:
            client.get('/')
            # No username
            is_unique = self.auth.verify_username_unique()
            self.assertFalse(is_unique)
            # NoneType username
            is_unique = self.auth.verify_username_unique(username=None)
            self.assertFalse(is_unique)
            # Integer username
            is_unique = self.auth.verify_username_unique(username=7)
            self.assertFalse(is_unique)
            # Boolean username
            is_unique = self.auth.verify_username_unique(username=True)
            self.assertFalse(is_unique)


class VerifyUserDataTestCase(TestCase):
    '''Test Case for UserAuthentication.verify_user_data()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()

    def test_good_data(self):
        '''Testing unique data, passwords match'''
        with app.test_client() as client:
            client.get('/')
            username = 'uniqueUser'
            email = 'unique@email.com'
            password = 'password'
            is_verified = self.auth.verify_user_data(
                [email, username, password, password])
            self.assertTrue(is_verified)

    def test_bad_username(self):
        '''Testing non-unique username'''
        with app.test_client() as client:
            client.get('/')
            username = 'testuser'
            email = 'unique@email.com'
            password = 'password'
            is_verified = self.auth.verify_user_data(
                [email, username, password, password])
            self.assertFalse(is_verified)

    def test_bad_email(self):
        '''Testing non-unique email'''
        with app.test_client() as client:
            client.get('/')
            username = 'uniqueUser'
            email = 'test@email.com'
            password = 'password'
            is_verified = self.auth.verify_user_data(
                [email, username, password, password])
            self.assertFalse(is_verified)

    def test_bad_password(self):
        '''Testing non-matching passwords'''
        with app.test_client() as client:
            client.get('/')
            username = 'testuser'
            email = 'test@email.com'
            password = 'password'
            is_verified = self.auth.verify_user_data(
                [email, username, password, 'N0Match'])
            self.assertFalse(is_verified)

    def test_invalid_data(self):
        '''Testing various invalid types as elements in user_data'''
        with app.test_client() as client:
            client.get('/')
            self.assertFalse(
                self.auth.verify_user_data(['uniqueemail@email.com', 'uniqueUser', None, 'password']))
            self.assertFalse(
                self.auth.verify_user_data(['uniqueemail@email.com', None, 'password', 'password']))
            self.assertFalse(
                self.auth.verify_user_data([None, 'uniqueUser', 'password', 'password']))
            self.assertFalse(
                self.auth.verify_user_data([9, 'uniqueUser', 'password', 'password']))
            self.assertFalse(
                self.auth.verify_user_data(['uniqueemail@email.com', True, 'password', 'password']))


class GetNewUserDataTestCase(TestCase):
    '''Test Case for UserAuthentication.get_new_user_data()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()

    def test_good_data(self):
        '''Testing valid data'''
        with app.test_client() as client:
            client.get('/')
            form = CreateUserForm()
            form.username.data = 'uniqueUser'
            form.email.data = 'unique@email.com'
            form.password.data = 'password'
            form.confirm_password.data = 'password'

            user_data = self.auth.get_new_user_data(form)

            self.assertIsInstance(user_data, list)
            self.assertEqual(
                user_data, ['unique@email.com', 'uniqueUser', 'password', 'password'])

    def test_no_data(self):
        '''Testing no data'''
        with app.test_client() as client:
            client.get('/')
            user_data = self.auth.get_new_user_data()
            self.assertIsNone(user_data)

    def test_bad_username(self):
        '''Testing invalid username'''
        with app.test_client() as client:
            client.get('/')
            form = CreateUserForm()
            form.username.data = None
            form.email.data = 'unique@email.com'
            form.password.data = 'password'
            form.confirm_password.data = 'password'

            user_data = self.auth.get_new_user_data(form)

            self.assertIsNone(user_data)

    def test_bad_email(self):
        '''Testing invalid email'''
        with app.test_client() as client:
            client.get('/')
            form = CreateUserForm()
            form.username.data = 'uniqueUser'
            form.email.data = 7
            form.password.data = 'password'
            form.confirm_password.data = 'password'

            user_data = self.auth.get_new_user_data(form)

            self.assertIsNone(user_data)

    def test_bad_password(self):
        '''Testing invalid passwords'''
        with app.test_client() as client:
            client.get('/')
            form = CreateUserForm()
            form.username.data = 'uniqueUser'
            form.email.data = 'unique@email.com'
            form.password.data = True
            form.confirm_password.data = True

            user_data = self.auth.get_new_user_data(form)

            self.assertIsNone(user_data)


class CreateUserTestCase(TestCase):
    '''Test Case for UserAuthentication.create_user()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()

    def test_successful_creation(self):
        '''Testing good data that should result in successful user creation'''
        with app.test_client() as client:
            client.get('/')
            user_data = ['unique@email.com',
                         'uniqueUser', 'password', 'password']

            user = self.auth.create_user(user_data=user_data)
            matching_user = UserModel.query.get(user.id)

            self.assertTrue(user)
            self.assertIsInstance(user, UserModel)
            self.assertTrue(matching_user)
            self.assertEqual(user, matching_user)


class DeleteTestCase(TestCase):
    '''Test Case for UserAuthentication.delete()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()


class SignUpTestCase(TestCase):
    '''Test Case for UserAuthentication.signup()'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()


class LoginTestCase(TestCase):
    '''Test Case for UserAuthentication.login'''

    def setUp(self):
        db.create_all()
        self.auth = UserAuthentication()
        create_test_user(auth=self.auth)

    def tearDown(self):
        db.drop_all()
