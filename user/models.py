from app.database import db


class UserModel(db.Model):
    '''
    id: primary key, autoincrements
    username: str with max-length 20, unique
    email: text, unique
    password: text
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    leagues = db.relationship(
        'LeagueModel', cascade='all, delete', backref='user')
    teams = db.relationship('TeamModel', cascade='all, delete', backref='user')
