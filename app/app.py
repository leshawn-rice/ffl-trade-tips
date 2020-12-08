from flask import Flask
from app.database import connect_db
from app.secrets import email_username, email_password

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ffl_trade_tips'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hz752lasbv82ckjb'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = email_username
app.config['MAIL_PASSWORD'] = email_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

connect_db(app)
