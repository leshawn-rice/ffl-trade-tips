from flask import render_template
from app.app import app
import users.views
import espn.views
import requests


@app.route('/')
def index():
    '''Displays the homepage'''
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
