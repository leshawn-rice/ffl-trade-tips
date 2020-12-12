from app.database import db
from espn.settings import GRADE_MAP


class LeagueModel(db.Model):
    '''
    id: primary key, from API
    league_id: int that holds ESPN league id
    user_id: int FK connected to users
    year: int that holds ESPN year
    espn_s2: text holds espn_s2 for private leagues
    swid: text holds swid for private leagues
    name: text holds league name
    num_teams: int, number of owned teams in the league
    user_team: int holds id for the team the user claimed
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

    def __repr__(self):
        return f'<LeagueModel id={self.id} league_id={self.league_id} year={self.year} user_id={self.user_id}>'

    def get_top_team(self):
        '''
        Returns the team with the most points
        '''
        most_points = 0
        top_team = None
        for team in self.teams:
            if team.points > most_points:
                most_points = team.points
                top_team = team
        return top_team

    def get_bottom_team(self):
        '''
        Returns the team with the least points
        '''
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
    user_id: primary key, foreign key, from users table
    accronym: text accronym for the team
    location: text location for team (first half of name)
    nickname: text nickname for team (second half of name)
    logo_url: text url for team logo
    record: text Win-Loss record for team
    waiver_position: int team's position on the waivers
    points: float team total points
    grade: text team letter grade
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
    grade = db.Column(db.Text)

    players = db.relationship(
        'PlayerModel', backref='team', cascade='all, delete')

    stats = db.relationship(
        'TeamStatModel', backref='team', cascade='all, delete')

    def __repr__(self):
        return f'<TeamModel id={self.id} team_id={self.team_id} league_id={self.league_id} user_id={self.user_id}>'

    def get_team_name(self):
        return f'{self.location} {self.nickname}'

    team_name = property(get_team_name)


class PlayerModel(db.Model):
    '''
    id: primary key, from API
    player_id: int ESPN player id
    team_id: int FK connected to teams
    league_id: int FK connected to leagues
    first_name: text player first name
    last_name: text player last name
    pro_team: text player current pro team
    position: text player position
    points: float player total points
    projected_points: float player projected points
    position_rank: int player rank in their position
    grade: text player letter grade
    '''
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'teams.id', ondelete='cascade'))
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
    outlooks = db.relationship('PlayerOutlookModel', backref='player')

    def __repr__(self):
        return f'<PlayerModel id={self.id} team_id={self.team_id} league_id={self.league_id} name={self.full_name} grade={self.grade}>'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    full_name = property(get_full_name)


class PlayerStatModel(db.Model):
    '''
    id: int serial primary key
    player_id: int FK connected to players
    league_id: int FK connected to leagues
    stat_name: text name of stat
    stat_value: float points in stat
    '''
    __tablename__ = 'players_stats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    stat_name = db.Column(db.Text, nullable=False)
    stat_value = db.Column(db.Float, nullable=False)


class PlayerOutlookModel(db.Model):
    '''
    id: int serial primary key
    player_id: int FK connected to players
    league_id: int FK connected to leagues
    week: int week of outlook
    outlook: text outlook text
    '''
    __tablename__ = 'players_outlooks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey(
        'players.id', ondelete='cascade'))
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    week = db.Column(db.Integer, nullable=False)
    outlook = db.Column(db.Text, nullable=False)


class TeamStatModel(db.Model):
    '''
    id: int serial primary key
    team_id: int FK connected to teams
    league_id: int FK connected to leagues
    stat_name: text name of stat
    stat_value: float points in stat
    '''
    __tablename__ = 'teams_stats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'teams.id', ondelete='cascade'))
    league_id = db.Column(db.Integer, db.ForeignKey(
        'leagues.id', ondelete='cascade'))
    stat_name = db.Column(db.Text, nullable=False)
    stat_value = db.Column(db.Float, nullable=False)
