from app.database import db, add_to_db
from espn.classes.base_classes import ModelHandlerBase
from espn.models import LeagueModel, TeamModel, TeamStatModel, PlayerModel, PlayerStatModel, PlayerOutlookModel


class LeagueModelHandler(ModelHandlerBase):
    def __init__(self, current_instance):
        '''
        Sets the instance attribute
        to an instance of the League class
        '''
        self.instance = current_instance

    def add_record(self):
        '''
        Adds a new League record to the database,
        using the information contained in 
        the instance attribute
        '''
        # Currently obsolete, but will be useful with private leagues
        if self.instance.cookies:
            new_league = LeagueModel(
                league_id=self.instance.id, user_id=self.instance.user_id, year=self.instance.year, espn_s2=espn_s2, swid=swid, num_teams=self.instance.num_teams, name=self.instance.name, week=self.instance.week)
        else:
            new_league = LeagueModel(
                league_id=self.instance.id, user_id=self.instance.user_id, year=self.instance.year, num_teams=self.instance.num_teams, name=self.instance.name, week=self.instance.week)
        add_to_db(new_league)
        self.instance.league_info['league_model_id'] = new_league.id


class TeamModelHandler(ModelHandlerBase):
    def __init__(self, current_instance):
        '''
        Sets the instance attribute (team instance) to parameter
        current_instance
        '''
        self.instance = current_instance

    def add_record(self):
        '''
        Adds a new team record to the database
        using the info from the instance attribute
        '''
        new_team = TeamModel(team_id=self.instance.id, league_id=self.instance.league_id, accronym=self.instance.accronym,
                             location=self.instance.location, nickname=self.instance.nickname, logo_url=self.instance.logo_url, record=self.instance.record, waiver_position=self.instance.waiver_position, points=self.instance.points, user_id=self.instance.user_id)
        add_to_db(new_team)

        # When we create a new team we also create their stats
        for stat, val in self.instance.stats.items():
            new_stat = TeamStatModel(
                team_id=new_team.id, league_id=self.instance.league_id, stat_name=stat, stat_value=val)
            db.session.add(new_stat)
        db.session.commit()


class PlayerModelHandler(ModelHandlerBase):
    def __init__(self, current_instance):
        '''
        Sets the instance attribute (player instance) to parameter
        current_instance
        '''
        self.instance = current_instance

    def add_record(self):
        '''
        Adds a new player record to the database given
        the instance attribute's info
        '''
        new_player = PlayerModel(player_id=self.instance.id, league_id=self.instance.league_id, team_id=self.instance.team_id, first_name=self.instance.first_name, last_name=self.instance.last_name,
                                 pro_team=self.instance.pro_team, position=self.instance.position, points=self.instance.points, projected_points=self.instance.projected_points, position_rank=self.instance.rank)
        db.session.add(new_player)
        db.session.commit()

        for stat, val in self.instance.stats.items():
            new_stat = PlayerStatModel(
                player_id=new_player.id, league_id=new_player.league_id, stat_name=stat, stat_value=val)
            db.session.add(new_stat)

        if self.instance.outlooks:
            for outlook in self.instance.outlooks:
                new_outlook = PlayerOutlookModel(
                    player_id=new_player.id, league_id=new_player.league_id, week=outlook[0], outlook=outlook[1])
                db.session.add(new_outlook)
        db.session.commit()
