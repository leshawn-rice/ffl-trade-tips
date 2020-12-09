from app.database import db
from espn.settings import GRADE_MAP


class LeagueModel(db.Model):
    '''
    id: primary key, from API
    num_teams: int, number of owned teams in the league
    '''
    __tablename__ = 'leagues'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    league_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'))
    year = db.Column(db.Integer, nullable=False)
    espn_s2 = db.Column(db.Text)
    swid = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    num_teams = db.Column(db.Integer, nullable=False)
    user_team = db.Column(db.Integer)

    players = db.relationship(
        'PlayerModel', backref='league')
    teams = db.relationship(
        'TeamModel', backref='league')

    def get_top_team(self):
        most_points = 0
        top_team = None
        for team in self.teams:
            if team.points > most_points:
                most_points = team.points
                top_team = team
        return top_team

    def get_bottom_team(self):
        least_points = 100000
        bottom_team = None
        for team in self.teams:
            if team.points < least_points:
                least_points = team.points
                bottom_team = team
        return bottom_team

    top_scorer = property(get_top_team)
    bottom_scorer = property(get_bottom_team)


class TeamModel(db.Model):
    '''
    team_id: primary key, from API, set to unique due to error thrown when adding
    league_id: primary key, foreign key, from leagues table
    owner_id: primary key, foreign key, from users table
    '''
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'))
    accronym = db.Column(db.Text)
    location = db.Column(db.Text)
    nickname = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    record = db.Column(db.Text)
    waiver_position = db.Column(db.Integer)
    points = db.Column(db.Float)

    players = db.relationship(
        'PlayerModel', backref='team')

    stats = db.relationship(
        'TeamStatModel', backref='team')

    def __repr__(self):
        return f'<TeamModel id={self.id}, team_name={self.team_name}, record={self.record}>'

    def get_team_name(self):
        return f'{self.location} {self.nickname}'

    team_name = property(get_team_name)


class PlayerModel(db.Model):
    '''
    id: primary key, from API
    name: text, name of player
    nfl_team: text, name of pro team (change to pro team for bball)
    '''
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'teams.id', ondelete='SET NULL'))
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    pro_team = db.Column(db.Text, nullable=False)
    position = db.Column(db.Text, nullable=False)

    points = db.Column(db.Float, nullable=False)
    projected_points = db.Column(db.Float, nullable=False)
    position_rank = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Text)

    stats = db.relationship(
        'PlayerStatModel', backref='player')

    @classmethod
    def get_trade_recs(cls, player):
        grades_to_check = GRADE_MAP[player.grade]
        matching_players = cls.query.filter(
            cls.grade in grades_to_check, cls.position == player.position)  # prolly wont work lol

        return matching_players

    def __repr__(self):
        return f'<PlayerModel id={self.id} team_id={self.team_id} league_id={self.league_id} name={self.full_name} grade={self.grade}>'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    full_name = property(get_full_name)


class PlayerStatModel(db.Model):
    '''

    '''
    __tablename__ = 'players_stats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    stat_name = db.Column(db.Text, nullable=False)
    stat_value = db.Column(db.Float, nullable=False)


class TeamStatModel(db.Model):
    '''

    '''
    __tablename__ = 'teams_stats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'teams.id', ondelete='cascade'))
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    stat_name = db.Column(db.Text, nullable=False)
    stat_value = db.Column(db.Float, nullable=False)
