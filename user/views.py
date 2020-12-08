from flask import redirect, render_template, session
from app.app import app
from app.forms import LoginForm, CreateUserForm, AddLeagueForm, SearchTradeForm
from user.auth import UserAuthentication

authentication = UserAuthentication()


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

    if session.get('username_taken'):
        session.pop('username_taken')

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
