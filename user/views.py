from flask import redirect, render_template, session, flash, request, jsonify
from app.app import app
from app.database import db, add_to_db, delete_from_db
from app.forms import LoginForm, CreateUserForm, AddLeagueForm
from user.auth import UserAuthentication
from user.models import UserModel, TradeModel
from espn.models import PlayerModel

authentication = UserAuthentication()


def create_saved_trade_data(user_id):
    '''
    Gets the saved trade data passed by 
    the 'addSaveTradeListener' function
    in app.js, and creates a new row in the
    trademodel table with the data.
    '''
    data = request.json
    current_player_id = data['trading_player_id']
    trading_player_ids = data['player_ids']
    num_trades = len(trading_player_ids)
    if num_trades == 0:
        return False
    if num_trades == 1:
        new_trade = TradeModel(
            user_id=user_id, player_to_trade_id=current_player_id, first_player_id=trading_player_ids[0])
    if num_trades == 2:
        new_trade = TradeModel(
            user_id=user_id, player_to_trade_id=current_player_id, first_player_id=trading_player_ids[0], second_player_id=trading_player_ids[1])
    if num_trades == 3:
        new_trade = TradeModel(
            user_id=user_id, player_to_trade_id=current_player_id, first_player_id=trading_player_ids[0], second_player_id=trading_player_ids[1], third_player_id=trading_player_ids[2])
    return new_trade


def get_saved_trades(saved_trades):
    '''
    Gets the players with the ids in 
    saved_trades, and adds them to a list
    of dictionaries, each with info about
    a single trade
    '''
    trades = []
    for trade_data in saved_trades:
        current_player = PlayerModel.query.get(trade_data.player_to_trade_id)
        first_player = PlayerModel.query.get(trade_data.first_player_id)
        second_player = PlayerModel.query.get(trade_data.second_player_id)
        third_player = PlayerModel.query.get(trade_data.third_player_id)
        trade = {
            'Current Player': current_player,
            'First Player': first_player,
            'Second Player': second_player,
            'Third Player': third_player
        }
        trades.append(trade)
    return trades


@app.route('/sign-out')
def signout():
    '''Signs the current user out'''
    session.pop('user_id')
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    If currently logged in, redirects to homepage, otherwise
    Displays the login form and verifies login information.
    If login info is correct, redirects to homepage, otherwise
    displays the login form again.
    '''
    if 'user_id' in session:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        user = authentication.log_in(form)
        if user:
            return redirect('/')
        else:
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)


@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    '''
    If currently logged in, redirects to homepage, otherwise
    Displays the signup form and verifies information.
    If info is valid, redirects to homepage, otherwise
    displays the signup form again.
    '''
    if 'user_id' in session:
        return redirect('/')
    # If we alert the user their username is taken, remove it from
    # the session to prevent subsequent alerts
    if session.get('username_taken'):
        session.pop('username_taken')
    # If we alert the user their email is taken, remove it from
    # the session to prevent subsequent alerts
    if session.get('email_taken'):
        session.pop('email_taken')

    form = CreateUserForm()
    if form.validate_on_submit():
        user = authentication.sign_up(form)
        if user:
            return redirect('/add-league')
        else:
            return render_template('signup.html', form=form)
    else:
        return render_template('signup.html', form=form)


@app.route('/profile')
def profile_page():
    '''
    Renders the users profile page
    if they're logged in
    '''
    if 'user_id' not in session:
        return redirect('/')
    user_id = session.get('user_id')
    user = UserModel.query.get_or_404(user_id)
    saved_trades = TradeModel.query.filter_by(user_id=user_id).all()
    trades = get_saved_trades(saved_trades)

    return render_template('profile.html', user=user, trades=trades)


@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    '''
    Deletes the user with id user_id from
    the database, if authentication succeeds.
    Otherwise returns home
    '''
    if 'user_id' not in session:
        flash('You need to be logged in to do that!', 'danger')
    elif user_id == session.get('user_id'):
        authentication.delete(user_id)
        return redirect('/sign-out')
    else:
        flash('You cannot delete an account that isn\'t yours!', 'danger')
    return redirect('/')


@app.route('/users/<int:user_id>/save-trade', methods=['POST'])
def save_trade(user_id):
    new_trade = create_saved_trade_data(user_id)

    if not new_trade:
        return jsonify({'message': 'No Trades to save!'}, 200)

    add_to_db(new_trade)
    return (jsonify({'message': 'Trade Saved!'}), 200)
