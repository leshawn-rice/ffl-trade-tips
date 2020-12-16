from flask import session
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase
from app.app import app
from app.database import db, add_to_db
from espn.classes.news_class import News

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ffl_trade_tips_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()


class NewsTestCase(TestCase):
    '''Test Case for the News class'''

    def test_news(self):
        '''Testing getting new NFL news'''
        news = News()
        self.assertIsInstance(news.data, list)
        self.assertFalse(news.data)
        news.get_news()
        self.assertIsInstance(news.data, list)
        self.assertTrue(news.data)
        self.assertIsInstance(news.data[0], dict)
        self.assertNotEqual(len(news.data), 0)
        self.assertIsInstance(news.data[0]['link'], str)
        self.assertIsInstance(news.data[0]['source'], type(None))
