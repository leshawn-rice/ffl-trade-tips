from flask import render_template, flash, redirect
from app.secrets import email_username
from flask_mail import Mail, Message
from app.app import app
from app.database import refresh_tables
from app.forms import ContactForm
import user.views
import espn.views

mail = Mail(app)

# Add change username/email/password
# Add docs
# Add tests
# Update readme
# Deploy


def send_email(sender, message):
    '''
    Sends an email from the sender email to the email
    address in app.secrets
    '''
    msg = Message('Contact From FFL-Trade-Tips', sender=sender,
                  recipients=[email_username])
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
