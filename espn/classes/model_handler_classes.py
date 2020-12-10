from app.database import db, add_to_db
from espn.classes.base_classes import ModelHandlerBase
from espn.models import LeagueModel, TeamModel, TeamStatModel, PlayerModel, PlayerStatModel


class LeagueModelHandler(ModelHandlerBase):
    def __init__(self, current_instance):
        self.instance = current_instance

    def add_record(self):
        if self.instance.cookies:
            new_league = LeagueModel(
                league_id=self.instance.id, user_id=self.instance.user_id, year=self.instance.year, espn_s2=espn_s2, swid=swid, num_teams=self.instance.num_teams, name=self.instance.name, week=self.instance.week)
        else:
            new_league = LeagueModel(
                league_id=self.instance.id, user_id=self.instance.user_id, year=self.instance.year, num_teams=self.instance.num_teams, name=self.instance.name, week=self.instance.week)

        add_to_db(new_league)
        self.instance.league_info['league_model_id'] = new_league.id

    def update_league_info(self, league):
        league.name = self.instance.name
        league.week = self.instance.week
        league.year = self.instance.year
        league.num_teams = self.instance.num_teams
        league.espn_s2 = self.instance.league_info.get('espn_s2')
        league.swid = self.instance.league_info.get('swid')
        db.session.commit()

    def update_record(self):
        league = LeagueModel.query.filter_by(
            league_id=self.instance.id, user_id=self.instance.user_id)
        self.update_league_info(league)
        self.instance.league_info['league_model_id'] = record.id

    def check_for_record_update(self):
        record = LeagueModel.query.filter_by(
            league_id=self.instance.id, user_id=self.instance.user_id).first()

        if (record.year == self.instance.year) and (record.num_teams == self.instance.num_teams) and (record.name == self.instance.name) and (record.week == self.instance.week):
            self.instance.league_info['league_model_id'] = record.id
            return False
        else:
            return True

    def check_for_record(self):
        record = LeagueModel.query.filter_by(
            league_id=self.instance.id, user_id=self.instance.user_id).all()
        if record:
            return True
        else:
            return False


class TeamModelHandler(ModelHandlerBase):
    def __init__(self, current_instance):
        self.instance = current_instance

    def add_record(self):
        new_team = TeamModel(team_id=self.instance.id, league_id=self.instance.league_id, accronym=self.instance.accronym,
                             location=self.instance.location, nickname=self.instance.nickname, logo_url=self.instance.logo_url, record=self.instance.record, waiver_position=self.instance.waiver_position, points=self.instance.points, user_id=self.instance.user_id)
        add_to_db(new_team)

        for stat, val in self.instance.stats.items():
            new_stat = TeamStatModel(
                team_id=new_team.id, league_id=self.instance.league_id, stat_name=stat, stat_value=val)
            add_to_db(new_stat)

    def update_team_stats(self, stat_records):
        stat_names = []
        for stat in stat_records:
            stat_names.append(stat.stat_name)
            if stat.stat_name in self.instance.stats.keys():
                stat.stat_value = self.instance.stats[stat.stat_name]

        for stat in self.instance.stats.keys():
            if stat not in stat_names:
                new_stat = TeamStatModel(
                    team_id=new_team.id, league_id=self.instance.league_id, stat_name=stat, stat_val=value)
                db.session.add(new_stat)
        db.session.commit()

    def update_team_info(self, team):
        team.acronym = self.instance.accronym
        team.location = self.instance.location
        team.nickname = self.instance.nickname
        team.logo_url = self.instance.logo_url
        team.record = self.instance.record
        team.waiver_position = self.instance.waiver_position
        team.points = self.instance.points
        db.session.commit()

    def update_record(self):
        team = TeamModel.query.filter_by(
            team_id=self.instance.id, league_id=self.instance.league_id).first()
        self.update_team_info(team)
        stat_records = TeamStatModel.query.filter_by(
            team_id=self.instance.id, league_id=self.instance.league_id).all()
        self.update_team_stats(stat_records)

    def check_for_record_update(self):
        record = TeamModel.query.filter_by(
            team_id=self.instance.id, league_id=self.instance.league_id).first()
        if (record.accronym == self.instance.accronym and record.location == self.instance.location and record.nickname == self.instance.nickname) and (record.logo_url == self.instance.logo_url and record.record == self.instance.record and record.waiver_position == self.instance.waiver_position) and (record.points == self.instance.points):
            return False
        else:
            return True

    def check_for_record(self):
        record = TeamModel.query.filter_by(
            team_id=self.instance.id, league_id=self.instance.league_id).all()
        if record:
            return True
        else:
            return False


class PlayerModelHandler(ModelHandlerBase):
    def __init__(self, current_instance):
        self.instance = current_instance

    def add_record(self):
        new_player = PlayerModel(player_id=self.instance.id, league_id=self.instance.league_id, team_id=self.instance.team_id, first_name=self.instance.first_name, last_name=self.instance.last_name,
                                 pro_team=self.instance.pro_team, position=self.instance.position, points=self.instance.points, projected_points=self.instance.projected_points, position_rank=self.instance.rank)
        add_to_db(new_player)

        for stat, val in self.instance.stats.items():
            new_stat = PlayerStatModel(
                player_id=new_player.id, league_id=new_player.league_id, stat_name=stat, stat_value=val)
            add_to_db(new_stat)

    def update_player_stats(self, stat_records):
        player_id = PlayerModel.query.filter_by(
            player_id=self.instance.id, league_id=self.instance.league_id).first().id
        stat_names = []
        for stat in stat_records:
            stat_names.append(stat.stat_name)
            if stat.stat_name in self.instance.stats.keys():
                stat.stat_value = self.instance.stats[stat.stat_name]

        db.session.commit()
        print(stat_names)
        for stat, val in self.instance.stats.items():
            if stat not in stat_names:
                print(stat)
                new_stat = PlayerStatModel(
                    player_id=player_id, league_id=self.instance.league_id, stat_name=stat, stat_value=val)
                db.session.add(new_stat)
        db.session.commit()

    def update_player_info(self, player):
        player.team_id = self.instance.team_id
        player.first_name = self.instance.first_name
        player.last_name = self.instance.last_name
        player.pro_team = self.instance.pro_team
        player.position = self.instance.position
        player.position_rank = self.instance.rank
        player.points = self.instance.points
        player.projected_points = self.instance.projected_points
        db.session.commit()

    def update_record(self):
        player = PlayerModel.query.filter_by(
            player_id=self.instance.id, league_id=self.instance.league_id).first()
        self.update_player_info(player)
        stat_records = PlayerStatModel.query.filter_by(
            player_id=self.instance.id, league_id=self.instance.league_id).all()
        self.update_player_stats(stat_records)

    def check_for_record_update(self):
        record = PlayerModel.query.filter_by(
            player_id=self.instance.id, league_id=self.instance.league_id).first()
        if (record.team_id == self.instance.team_id and record.first_name == self.instance.first_name and record.last_name == self.instance.last_name) and (record.pro_team == self.instance.pro_team and record.position == self.instance.position and record.position_rank == self.instance.rank) and (record.points == self.instance.points and record.projected_points == self.instance.projected_points):
            return False
        else:
            return True

    def check_for_record(self):
        record = PlayerModel.query.filter_by(
            player_id=self.instance.id, league_id=self.instance.league_id).all()
        if record:
            return True
        else:
            return False
