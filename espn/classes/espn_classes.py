from app.database import db
from espn.classes.base_classes import ESPNBase
from espn.classes.grade_class import GradeCalculator
from espn.classes.model_handler_classes import LeagueModelHandler, TeamModelHandler, PlayerModelHandler
from espn.models import LeagueModel, TeamModel, TeamStatModel, PlayerModel, PlayerStatModel
from espn.settings import PRO_TEAM_MAP, STATS_MAP, POSITION_MAP, STANDARD_SEASON_LENGTH


class League(ESPNBase):
    def __init__(self, league_id, year, user, cookies=None):
        self.id = league_id
        self.year = year
        self.cookies = cookies
        self.user_id = user.id
        self.league_info = {'league_model_id': None, 'league_id': self.id,
                            'year': self.year, 'cookies': self.cookies}
        self.create_league()

    def get_basic_info(self):
        self.teams = set()
        self.name = self.get_name()

    def get_name(self):
        super().__init__()
        data = self.make_espn_request()
        name = data['settings']['name']

    def get_num_teams(self):
        self.num_teams = 0

        views = ['mTeam']
        params = {'view': views}
        data = self.make_espn_request(params)

        for team in data['teams']:
            self.num_teams += 1

    def get_teams(self):
        views = ['mTeam']
        params = {'view': views}
        data = self.make_espn_request(params)

        for team in data['teams']:
            new_team = Team(data=team, league_info=self.league_info)
            self.teams.add(new_team)

        self.num_teams = len(self.teams)

    def handle_db(self):
        db_handler = LeagueModelHandler(self)
        db_handler.add_or_update_record()

    def create_league(self):
        self.get_basic_info()
        self.get_num_teams()
        self.handle_db()
        self.get_teams()


class Team(ESPNBase):
    def __init__(self, data, league_info):
        self.league_info = league_info
        self.roster = set()
        self.create_team(data)

    def get_basic_info(self, data):
        self.id = data['id']
        self.league_id = self.league_info.get('league_model_id')
        self.accronym = data['abbrev']
        self.location = data['location']
        self.nickname = data['nickname']
        self.logo_url = data['logo']
        wins = data['record']['overall']['wins']
        losses = data['record']['overall']['losses']
        self.record = f'{wins}-{losses}'
        self.waiver_position = data['waiverRank']

    def get_stats(self, data):
        self.stats = {}
        self.add_stats(data['valuesByStat'])

    def create_player(self, player):
        player_data = player['playerPoolEntry']['player'] if 'playerPoolEntry' in player else player['player']
        new_player = Player(
            data=player_data, league_info=self.league_info, team_id=self.id)
        self.roster.add(new_player)

    def get_roster(self):
        views = ['mRoster']
        params = {'view': views, 'forTeamId': self.id}
        super().__init__()
        data = self.make_espn_request(params)
        roster_data = data['teams'][0]
        for player in roster_data['roster']['entries']:
            self.create_player(player)

    def handle_db(self):
        db_handler = TeamModelHandler(self)
        db_handler.add_or_update_record()

    def create_team(self, data):
        self.get_basic_info(data)
        self.get_stats(data)
        self.handle_db()
        self.get_roster()


class Player(ESPNBase):
    def __init__(self, data, league_info, team_id):
        self.league_info = league_info
        self.team_id = team_id
        self.league_id = league_info.get('league_model_id')
        self.league_info['team_id'] = team_id
        self.create_player(data)

    def get_rank(self):
        super().__init__()
        views = ['kona_playercard']
        params = {'view': views}
        data = self.make_espn_request(params)
        for p in data['players']:
            if p['player']['fullName'] == f'{self.first_name} {self.last_name}':
                return p['ratings']['0']['positionalRanking']
        return 0

    def get_basic_info(self, data):
        self.id = data['id']
        self.position = POSITION_MAP[data['defaultPositionId']]
        self.first_name = data['firstName']
        self.last_name = data['lastName']
        self.rank = self.get_rank()
        self.injured = data.get('injured', False)
        self.injury_status = data.get('injuryStatus', 'ACTIVE')
        self.pro_team = PRO_TEAM_MAP[data.get('proTeamId')]
        if self.pro_team == 'None':
            self.pro_team = 'FA'

    def get_stat_data(self, data):
        year = self.league_info['year']
        year_id = f'00{year}'

        stat_block = [x for x in data['stats'] if x['id'] == year_id][0]
        self.points = stat_block['appliedTotal']
        self.point_avg = stat_block['appliedAverage']
        self.projected_points = self.point_avg * STANDARD_SEASON_LENGTH

        stats_to_check = stat_block['appliedStats'] if stat_block.get(
            'appliedStats') else stat_block['stats']
        return stats_to_check

    def get_stats(self, data):
        self.stats = {}
        stat_data = self.get_stat_data(data)
        self.add_stats(stat_data)

    def get_grade(self):
        grader = GradeCalculator()
        record = PlayerModel.query.filter_by(
            player_id=self.id, league_id=self.league_id).first()
        record.grade = grader.grade_player(record)
        db.session.commit()

    def handle_db(self):
        db_handler = PlayerModelHandler(self)
        db_handler.add_or_update_record()

    def create_player(self, data):
        self.get_basic_info(data)
        self.get_stats(data)
        self.handle_db()
        self.get_grade()
