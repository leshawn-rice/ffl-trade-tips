from flask import render_template
from app.app import app
from app.database import refresh_tables
import user.views
import espn.views
import requests


@app.route('/')
def index():
    '''Displays the homepage'''
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
