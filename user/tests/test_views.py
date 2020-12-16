from flask import session
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase
from app.app import app
from app.database import db, add_to_db
from app.forms import CreateUserForm, LoginForm
from user.auth import UserAuthentication
from user.models import UserModel
from user import views

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ffl_trade_tips_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()


def create_test_user():
    auth = UserAuthentication()
    test_username = 'testuser'
    test_email = 'test@email.com'
    test_password = auth.create_hashed_password('test_password')
    test_user = UserModel(username=test_username,
                          email=test_email, password=test_password)
    add_to_db(test_user)


class UserViewTestCase(TestCase):
    '''Test Case for User views'''

    def setUp(self):
        db.create_all()
        create_test_user()

    def tearDown(self):
        db.drop_all()

    def test_sign_out(self):
        '''Testing sign out page'''
        with app.test_client() as client:
            client.get('/')

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            client.get('/sign-out')

            with client.session_transaction() as session:
                self.assertNotIn('user_id', session)

    def test_login(self):
        '''Testing login page'''
        with app.test_client() as client:
            client.get('/')
            form = LoginForm()
            form.username.data = 'testuser'
            form.password.data = 'test_password'

            client.post('/login', data=form.data, follow_redirects=True)

            self.assertIn('user_id', session)
            self.assertEqual(session['user_id'], 1)

    def test_sign_up(self):
        '''Testing sign up page'''
        with app.test_client() as client:
            client.get('/')
            form = CreateUserForm()
            form.username.data = 'uniqueUser'
            form.email.data = 'unique@email.com'
            form.password.data = 'Password123'
            form.confirm_password.data = 'Password123'

            response = client.post(
                '/sign-up', data=form.data, follow_redirects=True)

            self.assertIn('user_id', session)
            self.assertEqual(session['user_id'], 2)

    def test_profile(self):
        '''Testing profile page'''
        with app.test_client() as client:
            client.get('/')

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            response = client.get('/profile')
            response_body = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Your Profile', response_body)
            self.assertIn('testuser', response_body)
            self.assertIn('test@email.com', response_body)

    def test_delete(self):
        '''Testing delete page'''
        with app.test_client() as client:
            client.get('/')

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            response = client.get('/users/1/delete', follow_redirects=True)

            self.assertFalse(UserModel.query.get(1))
