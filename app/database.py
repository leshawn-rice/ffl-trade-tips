from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def refresh_tables():
    db.drop_all()
    db.create_all()


def connect_db(app):
    '''Connects the app to the db'''
    db.app = app
    db.init_app(app)


def add_to_db(item_to_add):
    db.session.add(item_to_add)
    db.session.commit()
