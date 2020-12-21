from flask import render_template, flash, redirect
from app.app import app
import user.views
import espn.views
import os


@app.route('/')
def index():
    '''Displays the homepage'''
    return render_template('index.html')


@app.route('/about')
def about_page():
    '''Renders the About Page'''
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
