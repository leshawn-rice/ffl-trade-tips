from app.database import db


class UserModel(db.Model):
    '''
    id: primary key, autoincrements
    username: text, unique
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


class TradeModel(db.Model):
    '''
    id: int primary key serial
    user_id: int FK connected to users
    player_to_trade: int FK onnected to players
    first/second/third_player: int FK connected to players
    '''

    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'))
    player_to_trade = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))

    first_player = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))
    second_player = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))
    third_player = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))
