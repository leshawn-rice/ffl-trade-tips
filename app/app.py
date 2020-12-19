from flask import Flask
from app.database import connect_db
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'j8k9z411b')
EMAIL = os.environ.get('EMAIL', None)
EMAIL_PASS = os.environ.get('EMAIL_PASS', None)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///ffl-trades-db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = EMAIL_PASS
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

connect_db(app)
