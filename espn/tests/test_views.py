from flask import session, request
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase
from app.app import app
from app.secrets import test_league_id, test_year
from app.database import db, add_to_db
from app.forms import AddLeagueForm, SelectTeamForm
from espn import views
from espn.classes.espn_classes import League
from espn.models import LeagueModel
from user.auth import UserAuthentication
from user.models import UserModel

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


def create_test_league(test_user_id):
    test_league = League(league_id=test_league_id,
                         year=test_year, user_id=test_user_id)

    return test_league


class ESPNViewTestCase(TestCase):
    '''Test Case for User views'''

    def setUp(self):
        db.create_all()
        create_test_user()

    def tearDown(self):
        db.drop_all()

    def test_recent_news(self):
        with app.test_client() as client:
            response = client.get('/recent-news')
            response_body = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Recent NFL News', response_body)
            self.assertIn('Story', response_body)
            self.assertIn('Source', response_body)
            self.assertIn(
                '<td class="shadow-lg p-3 mb-5 rounded"><h3>', response_body)

    def test_add_league(self):
        with app.test_client() as client:
            client.get('/')

            form = AddLeagueForm()
            form.league_id.data = test_league_id
            form.year.data = test_year

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            response = client.post(
                '/add-league', data=form.data, follow_redirects=True)

            self.assertEqual(session['user_id'], 1)
            self.assertIn('select-team', request.path)

    def test_delete_league(self):
        with app.test_client() as client:
            client.get('/')

            create_test_league(1)

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            response = client.get(
                '/leagues/1/delete', follow_redirects=True)

            league = LeagueModel.query.get(1)
            self.assertFalse(league)
            self.assertEqual(session['user_id'], 1)
            self.assertEqual('/', request.path)

    def test_leagues(self):
        with app.test_client() as client:
            client.get('/')

            create_test_league(1)

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            response = client.get(
                '/leagues', follow_redirects=True)
            response_body = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Minshew Crew II', response_body)
            self.assertIn('Teams', response_body)

    def test_select_team(self):
        with app.test_client() as client:
            client.get('/')

            create_test_league(1)

            form = SelectTeamForm()
            form.team.data = 1

            with client.session_transaction() as session:
                session['user_id'] = 1
                self.assertIn('user_id', session)
                self.assertEqual(session['user_id'], 1)

            response = client.post(
                '/select-team', data=form.data, follow_redirects=True)

            self.assertEqual(session['user_id'], 1)
            self.assertIn('select-team', request.path)
