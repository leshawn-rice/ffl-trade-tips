from flask import render_template, redirect, session
from app.app import app
from espn.classes.news_class import News
from users.models import UserModel


@app.route('/recent-news')
def show_news():
    news = News()
    news.get_news()
    return render_template('news.html', news=news.data)


@app.route('/leagues')
def show_leagues():
    if 'user_id' not in session:
        return redirect('/login')
    user = UserModel.query.get(session['user_id'])
    leagues = user.leagues
    return render_template('leagues.html', leagues=leagues)
