from flask import redirect, render_template, session, flash, request, jsonify
from app.app import app
from app.database import db
from app.forms import LoginForm, CreateUserForm, AddLeagueForm
from user.auth import UserAuthentication
from user.models import UserModel, TradeModel
from espn.models import PlayerModel

authentication = UserAuthentication()


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
    trades_a = TradeModel.query.filter_by(user_id=user_id).all()
    trades = []
    for t in trades_a:
        current_player = PlayerModel.query.get(t.player_to_trade)
        first_player = PlayerModel.query.get(t.first_player)
        second_player = PlayerModel.query.get(t.second_player)
        third_player = PlayerModel.query.get(t.third_player)
        trade = {
            'Current Player': current_player,
            'First Player': first_player,
            'Second Player': second_player,
            'Third Player': third_player
        }
        trades.append(trade)
    print(trades)
    return render_template('profile.html', user=user, trades=trades)


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
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('Account Deleted Successfuly', 'success')
        return redirect('/sign-out')
    else:
        flash('You cannot delete an account that isn\'t yours!', 'danger')
    return redirect('/')


@app.route('/users/<int:user_id>/save-trade', methods=['POST'])
def save_trade(user_id):
    data = request.json
    current_player_id = data['trading_player_id']
    trading_player_ids = data['player_ids']
    num_trades = len(trading_player_ids)
    if num_trades == 0:
        return (jsonify({'message': 'No Trade To Save!'}), 200)
    if num_trades == 1:
        new_trade = TradeModel(
            user_id=user_id, player_to_trade=current_player_id, first_player=trading_player_ids[0])
    if num_trades == 2:
        new_trade = TradeModel(
            user_id=user_id, player_to_trade=current_player_id, first_player=trading_player_ids[0], second_player=trading_player_ids[1])
    if num_trades == 3:
        new_trade = TradeModel(
            user_id=user_id, player_to_trade=current_player_id, first_player=trading_player_ids[0], second_player=trading_player_ids[1], third_player=trading_player_ids[2])
    db.session.add(new_trade)
    db.session.commit()

    return (jsonify({'message': 'Trade Saved!'}), 200)
