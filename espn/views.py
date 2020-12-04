from espn.classes.news_class import News
from flask import render_template
from app.app import app


@ app.route('/recent-news')
def show_news():
    news = News()
    news.get_news()
    return render_template('news.html', news=news.data)
