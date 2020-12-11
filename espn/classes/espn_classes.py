from app.database import db
from espn.classes.base_classes import ESPNBase
from espn.classes.grade_class import GradeCalculator
from espn.classes.model_handler_classes import LeagueModelHandler, TeamModelHandler, PlayerModelHandler
from espn.models import LeagueModel, TeamModel, TeamStatModel, PlayerModel, PlayerStatModel
from espn.settings import PRO_TEAM_MAP, STATS_MAP, POSITION_MAP, STANDARD_SEASON_LENGTH, DEFAULT_STAT_VALUES, GRADE_TO_VALUE, VALUE_TO_GRADE


class Settings:
    '''Class for ESPN League Settings'''

    def __init__(self, data):
        '''
        Get current week, league, and
        scoring settings
        '''
        self.scoring_settings = {}
        self.current_week = data['scoringPeriodId']
        self.get_league_settings(data)
        self.get_scoring_settings(data)

    def get_league_settings(self, data):
        '''
        Get total number of weeks and
        whether the league is active
        '''
        self.is_active = data['status']['isActive']
        self.total_weeks = data['status']['finalScoringPeriod']

    def get_scoring_settings(self, data):
        '''
        Get scoring settings from
        the API. This gets point
        values for each stat
        '''
        scoring_settings = data['settings']['scoringSettings']
        scoring_items = scoring_settings['scoringItems']
        for stat in scoring_items:
            if stat['statId'] in STATS_MAP:
                stat_name = STATS_MAP[stat['statId']]
                if '16' in stat['pointsOverrides']:
                    self.scoring_settings[stat_name] = stat['pointsOverrides']['16']
                else:
                    self.scoring_settings[stat_name] = DEFAULT_STAT_VALUES[stat_name]


class League(ESPNBase):
    '''ESPN API Wrapper for Leagues'''

    def __init__(self, league_id, year, user_id, cookies=None):
        '''
        Gets basic league settings then
        creates the league
        '''
        self.id = league_id
        self.year = year
        self.cookies = cookies
        self.user_id = user_id
        self.league_info = {'league_model_id': None, 'league_id': self.id,
                            'year': self.year, 'cookies': self.cookies, 'user_id': self.user_id}
        self.create_league()

    def get_settings(self):
        '''
        Gets JSON league settings from
        API, then creates an instance of
        the Settings class and assigns it
        to the settings attribute
        '''
        params = {'view': 'mSettings'}
        data = self.make_espn_request(params)
        self.settings = Settings(data)
        self.league_info['current_week'] = self.settings.current_week
        self.league_info['total_weeks'] = self.settings.total_weeks

    def get_basic_info(self):
        '''
        Initialize teams attribute
        to an empty set, and gets
        the name of the league
        '''
        self.teams = set()
        self.name = self.get_name()

    def get_name(self):
        '''
        Gets the name of the league
        and the current week from the
        API
        '''
        super().__init__()
        data = self.make_espn_request()
        name = data['settings']['name']
        self.week = data['scoringPeriodId']
        return name

    def get_num_teams(self):
        '''
        Gets the number of teams
        in the league from the API
        '''
        self.num_teams = 0

        views = ['mTeam']
        params = {'view': views}
        data = self.make_espn_request(params)

        for team in data['teams']:
            self.num_teams += 1

    def get_teams(self):
        '''
        Gets team data from the
        API, and iterates through
        the response, adding instances
        of the Team class to the teams attribute
        '''
        views = ['mTeam']
        params = {'view': views}
        data = self.make_espn_request(params)

        for team in data['teams']:
            new_team = Team(data=team, league_info=self.league_info)
            self.teams.add(new_team)

        self.num_teams = len(self.teams)

    def handle_db(self):
        '''Handles adding league info to the database'''
        db_handler = LeagueModelHandler(self)
        db_handler.add_or_update_record()

    def get_scoring_ranges(self, grader):
        '''
        Gets the max and min score
        for each position in order
        to accurately grade players
        '''
        for team in self.teams:
            for player in team.roster:
                record = PlayerModel.query.filter_by(
                    player_id=player.id, league_id=player.league_id).first()
                grader.get_pos_extremes(record)

    def get_grades(self, grader):
        '''
        Gets the letter grades for each
        player in the league, then uses those
        grades to get the average grade of
        each team.
        '''
        for team in self.teams:
            team_score = 0
            for player in team.roster:
                record = PlayerModel.query.filter_by(
                    player_id=player.id, league_id=player.league_id).first()
                record.grade = grader.grade_player(record)
                db.session.commit()
                team_score += GRADE_TO_VALUE[record.grade]

            team_grade = team_score / len(team.roster)
            team_grade = VALUE_TO_GRADE[round(team_grade)]

            record = TeamModel.query.filter_by(
                team_id=team.id, league_id=team.league_id, user_id=self.user_id).first()
            record.grade = team_grade
            db.session.commit()

    def grade_teams(self):
        '''Calls grading functions'''
        grader = GradeCalculator(self.settings.scoring_settings)
        self.get_scoring_ranges(grader)
        grader.set_grade_ranges()
        self.get_grades(grader)

    def create_league(self):
        '''
        Calls functions needed to
        create the league'''
        self.get_basic_info()
        self.get_settings()
        self.get_num_teams()
        self.handle_db()
        self.get_teams()
        self.grade_teams()


class Team(ESPNBase):
    '''ESPN API Wrapper for Teams'''

    def __init__(self, data, league_info):
        '''
        Gets basic team info and intializes
        the roster attribute to an empty set
        '''
        self.league_info = league_info
        self.user_id = league_info.get('user_id')
        self.roster = set()
        self.create_team(data)

    def get_basic_info(self, data):
        '''
        Gets all basic team info
        '''
        self.id = data['id']
        self.league_id = self.league_info.get('league_model_id')
        self.accronym = data['abbrev']
        self.location = data['location']
        self.nickname = data['nickname']
        self.logo_url = data['logo']
        self.points = data['points']
        self.points = round(self.points, 2)
        wins = data['record']['overall']['wins']
        losses = data['record']['overall']['losses']
        self.record = f'{wins}-{losses}'
        self.waiver_position = data['waiverRank']

    def get_stats(self, data):
        '''Gets the stats for the team'''
        self.stats = {}
        self.add_stats(data['valuesByStat'])

    def create_player(self, player):
        '''
        Creates a new instance of the player class 
        given the JSON for the player from the API, 
        then adds them to the roster attribute
        '''
        player_data = player['playerPoolEntry']['player'] if 'playerPoolEntry' in player else player['player']
        team_id = TeamModel.query.filter_by(
            team_id=self.id, league_id=self.league_id, user_id=self.user_id).first().id
        new_player = Player(
            data=player_data, league_info=self.league_info, team_id=team_id)
        self.roster.add(new_player)

    def get_roster(self):
        '''
        Gets team roster JSON from the API,
        then iterates through it and creates
        an instance of the player class for
        each players
        '''
        views = ['mRoster']
        params = {'view': views, 'forTeamId': self.id}
        super().__init__()
        data = self.make_espn_request(params)
        roster_data = data['teams'][0]
        for player in roster_data['roster']['entries']:
            self.create_player(player)

    def handle_db(self):
        '''Handles adding the team to the database'''
        db_handler = TeamModelHandler(self)
        db_handler.add_or_update_record()

    def create_team(self, data):
        '''Drives necessary functions for adding a team'''
        self.get_basic_info(data)
        self.get_stats(data)
        self.handle_db()
        self.get_roster()


class Player(ESPNBase):
    '''ESPN API Wrapper for Players'''

    def __init__(self, data, league_info, team_id):
        '''
        Gets basic player info and calls driving
        function
        '''
        self.league_info = league_info
        self.team_id = team_id
        self.league_id = league_info.get('league_model_id')
        self.league_info['team_id'] = team_id
        self.create_player(data)

    def get_rank(self):
        '''
        Gets the player position
        rank data from the api and
        sets it to the rank attribute
        '''
        super().__init__()
        views = ['mRoster']
        params = {'view': views}
        data = self.make_espn_request(params)
        for team in data['teams']:
            for player in team['roster']['entries']:
                player_data = player['playerPoolEntry']
                if player_data['id'] == self.id:
                    return player_data['ratings']['0']['positionalRanking']
        return 0

    def get_basic_info(self, data):
        '''
        Gets all basic info for the player
        from the API and sets it into attributes
        on the instance
        '''
        self.id = data['id']
        self.position = POSITION_MAP[data['defaultPositionId']]
        self.first_name = data['firstName']
        self.last_name = data['lastName']
        self.outlooks = []
        if 'outlooks' in data:
            for week, outlook in data['outlooks']['outlooksByWeek'].items():
                int_week = int(week)
                self.outlooks.append((int_week, outlook))
        else:
            self.outlooks = []

        self.rank = self.get_rank()
        self.injured = data.get('injured', False)
        self.injury_status = data.get('injuryStatus', 'ACTIVE')
        self.pro_team = PRO_TEAM_MAP[data.get('proTeamId')]
        if self.pro_team == 'None':
            self.pro_team = 'FA'

    def get_stat_data(self, data):
        '''
        Gets stat data for the player
        from the API and adds it to the
        stats attribute
        '''
        year = self.league_info['year']
        year_id = f'00{year}'

        stat_block = [x for x in data['stats'] if x['id'] == year_id][0]
        self.points = stat_block['appliedTotal']
        self.points = round(self.points, 2)
        self.point_avg = stat_block['appliedAverage']
        self.projected_points = self.point_avg * \
            self.league_info['total_weeks']
        self.projected_points = round(self.projected_points, 2)

        stats_to_check = stat_block['appliedStats'] if stat_block.get(
            'appliedStats') else stat_block['stats']
        return stats_to_check

    def get_stats(self, data):
        '''
        Initializes the stats attribute to an empty
        dictionary, gets all stat data from the api,
        then adds the stats to the dictionary
        '''
        self.stats = {}
        stat_data = self.get_stat_data(data)
        self.add_stats(stat_data)

    def handle_db(self):
        '''Handles adding the instance to the database'''
        db_handler = PlayerModelHandler(self)
        db_handler.add_or_update_record()

    def create_player(self, data):
        '''Drives player creation'''
        self.get_basic_info(data)
        self.get_stats(data)
        self.handle_db()
