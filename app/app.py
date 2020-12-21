from flask import Flask
from app.database import connect_db
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'j8k9z411b')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///ffl-trades-db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

connect_db(app)
