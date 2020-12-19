from flask import render_template, flash, redirect
from flask_mail import Mail, Message
from app.app import app
from app.database import db
from app.forms import ContactForm
import user.views
import espn.views
import os

EMAIL = os.environ.get('EMAIL', None)

mail = Mail(app)

db.drop_all()
db.create_all()


def send_email(sender, message):
    '''
    Sends an email from the sender email to the email
    address in app.secrets
    '''
    msg = Message('Contact From FFL-Trade-Tips', sender=sender,
                  recipients=[EMAIL])
    msg.body = f'From email: {sender}\nMessage: {message}'
    mail.send(msg)


@app.route('/')
def index():
    '''Displays the homepage'''
    return render_template('index.html')


@app.route('/about')
def about_page():
    '''Renders the About Page'''
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    '''Renders the Contact Page'''
    form = ContactForm()
    if form.validate_on_submit():
        sender = form.email.data
        message = form.message.data
        send_email(sender=sender, message=message)
        flash('Email Sent!', 'success')
        return redirect('/')
    return render_template('contact.html', form=form)


if __name__ == '__main__':
    app.run()
