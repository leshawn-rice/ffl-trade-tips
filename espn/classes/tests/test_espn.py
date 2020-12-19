from flask import session
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase
from app.app import app
from app.database import db, add_to_db
from espn.classes.base_classes import ESPNRequest
from espn.classes.espn_classes import League
from user.models import UserModel
from user.auth import UserAuthentication
import os

test_league_id = os.getenv('test_league_id')
test_year = os.getenv('test_year')

app.config['TESTING'] = True
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

    return test_user.id


def create_test_league(test_user_id):
    test_league = League(league_id=test_league_id,
                         year=test_year, user_id=test_user_id)

    return test_league


class ESPNRequestTestCase(TestCase):
    '''Test Case for ESPNRequest Class'''

    def test_init(self):
        base = ESPNRequest(league_id=test_league_id, year=test_year)

        self.assertEqual(
            base.base_url, f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{test_year}/segments/0/leagues/{test_league_id}')

    def test_make_request(self):
        base = ESPNRequest(league_id=test_league_id, year=test_year)
        data = base.get_response_data()
        self.assertIn('teams', data)
        self.assertIn('settings', data)
        self.assertIn('members', data)


class LeagueTestCase(TestCase):
    '''Test Case for League API Wrapper'''

    def setUp(self):
        db.create_all()
        user_id = create_test_user()
        self.league = create_test_league(user_id)

    def tearDown(self):
        db.drop_all()

    def test_league(self):
        self.assertEqual(self.league.num_teams, 12)
        self.assertEqual(self.league.name, 'Minshew Crew II')
        for team in self.league.teams:
            self.assertEqual(team.user_id, 1)
            self.assertIsNotNone(team.location)
            self.assertIsNotNone(team.nickname)
            self.assertIsNotNone(team.points)
            self.assertIsNotNone(team.record)
            self.assertIsNotNone(team.waiver_position)
            self.assertIsNotNone(team.roster)
            for player in team.roster:
                self.assertIsNotNone(player.first_name)
                self.assertIsNotNone(player.last_name)
                self.assertIsNotNone(player.points)
                self.assertIsNotNone(player.projected_points)
                self.assertIsNotNone(player.rank)
                self.assertIsNotNone(player.position)
