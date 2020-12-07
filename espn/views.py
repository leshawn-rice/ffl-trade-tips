from flask import render_template, redirect, session
from app.app import app
from espn.classes.news_class import News
from users.models import UserModel
from users.auth import UserAuthentication
from forms.forms import AddLeagueForm
from espn.settings import POSITIONS

authentication = UserAuthentication()


@app.route('/recent-news')
def show_news():
    news = News()
    news.get_news()
    return render_template('news.html', news=news.data)


@app.route('/add-league', methods=['GET', 'POST'])
def add_league():
    form = AddLeagueForm()

    if form.validate_on_submit():
        league = authentication.add_league(form)
        if league:
            return redirect('/')
        else:
            return render_template('add_league_form.html', form=form)
    else:
        return render_template('add_league_form.html', form=form)


@app.route('/leagues')
def show_leagues():
    if 'user_id' not in session:
        return redirect('/login')
    user = UserModel.query.get(session['user_id'])
    leagues = user.leagues
    return render_template('leagues.html', leagues=leagues)
