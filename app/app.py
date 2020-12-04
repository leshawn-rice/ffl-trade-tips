from flask import Flask, request, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from app.database import db, connect_db
from espn.models import TeamModel, PlayerModel
from users.models import UserModel
from forms.forms import CreateUserForm, LoginForm, SearchTradeForm, AddLeagueForm, SelectTeamForm
from forms.handle_forms import FormHandler

# Trade logic:
# A Players get A & B
# B Players get A & C
# C Players get B & D
# D Players get C & F
# F Players get D & F

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ffl_trade_tips'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hz752lasbv82ckjb'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)


if __name__ == "__main__":
    app.run()
