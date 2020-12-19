from app.database import db
from espn.classes.base_classes import ESPNBase
from espn.classes.grade_class import GradeCalculator
from espn.classes.model_handler_classes import LeagueModelHandler, TeamModelHandler, PlayerModelHandler
from espn.models import LeagueModel, TeamModel, TeamStatModel, PlayerModel, PlayerStatModel
from espn.settings import PRO_TEAM_MAP, STATS_MAP, POSITION_MAP, DEFAULT_STAT_VALUES, GRADE_TO_VALUE, VALUE_TO_GRADE


class LeagueSettings:
    '''Class for ESPN League Settings'''

    def __init__(self, data):
        '''
        Get current week, league, and
        scoring settings
        '''
        self.scoring_settings = {}
        self.data = data
        self.current_week = self.data['scoringPeriodId']
        self.get_league_settings()
        self.get_scoring_settings()

    def get_league_settings(self):
        '''
        Get total number of weeks and
        whether the league is active
        '''
        self.is_active = self.data['status']['isActive']
        self.total_weeks = self.data['status']['finalScoringPeriod']

    def get_scoring_settings(self):
        '''
        Get scoring settings from
        the API. This gets point
        values for each stat
        '''
        scoring_settings = self.data['settings']['scoringSettings']
        scoring_items = scoring_settings['scoringItems']
        for stat in scoring_items:
            if stat['statId'] in STATS_MAP:
                stat_name = STATS_MAP[stat['statId']]
                # '16' designates a custom stat
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
        # Cookies are currently unnecessary, but will be needed for private league support in v2
        self.cookies = cookies
        self.user_id = user_id
        self.league_info = {'league_model_id': None, 'league_id': self.id,
                            'year': self.year, 'cookies': self.cookies, 'user_id': self.user_id}
        self.create_league()

    def get_data(self):
        '''
        Gets the data for the league,
        we use this data to create the league,
        every team, and every player
        '''
        super().__init__()
        views = ['mTeam', 'mRoster', 'mSettings', 'kona_playercard']
        params = {'view': views}
        self.data = self.make_espn_request(params)

    def get_settings(self):
        '''
        Gets JSON league settings from
        API, then creates an instance of
        the Settings class and assigns it
        to the settings attribute
        '''
        self.settings = LeagueSettings(self.data)
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
        name = self.data['settings']['name']
        self.week = self.data['scoringPeriodId']
        return name

    def get_num_teams(self):
        '''
        Gets the number of teams
        in the league from the API
        '''
        self.num_teams = 0

        for team in self.data['teams']:
            self.num_teams += 1

    def get_teams(self):
        '''
        Gets team data from the
        API, and iterates through
        the response, adding instances
        of the Team class to the teams attribute
        '''
        for team in self.data['teams']:
            new_team = Team(data=team, league_info=self.league_info)
            self.teams.add(new_team)

        self.num_teams = len(self.teams)

    def get_scoring_ranges(self):
        '''
        Gets the max and min score
        for each position in order
        to accurately grade players
        '''
        for team in self.teams:
            for player in team.roster:
                record = PlayerModel.query.filter_by(
                    player_id=player.id, league_id=player.league_id).first()
                self.grader.get_pos_extremes(record)

    def get_grades(self):
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
                record.grade = self.grader.grade_player(record)
                db.session.commit()
                team_score += GRADE_TO_VALUE[record.grade]

            team_grade = team_score / len(team.roster)
            team_grade = VALUE_TO_GRADE[round(team_grade)]

            record = TeamModel.query.filter_by(
                team_id=team.id, league_id=team.league_id, user_id=self.user_id).first()
            record.grade = team_grade
            db.session.commit()

    def create_grader(self):
        self.grader = GradeCalculator(self.settings.scoring_settings)

    def start_grading(self):
        '''Calls grading functions'''
        self.create_grader()
        self.get_scoring_ranges()
        self.grader.set_grade_ranges()

    def handle_db(self):
        '''Handles adding league info to the database'''
        # The purpose of this is to make it so we can
        # Refresh league stats without having to worry
        # About whether a record already exists
        db_handler = LeagueModelHandler(self)
        db_handler.add_or_update_record()

    def create_league(self):
        '''
        Calls functions needed to
        create the league
        '''
        self.get_data()
        self.get_basic_info()
        self.get_settings()
        self.get_num_teams()


class Team(ESPNBase):
    '''ESPN API Wrapper for Teams'''

    def __init__(self, data, league_info):
        '''
        Gets basic team info and intializes
        the roster attribute to an empty set
        '''
        self.league_info = league_info
        self.data = data
        self.user_id = league_info.get('user_id')
        self.roster = set()
        self.create_team()

    def get_basic_info(self):
        '''
        Gets all basic team info
        '''
        self.id = self.data['id']
        self.league_id = self.league_info.get('league_model_id')
        self.accronym = self.data['abbrev']
        self.location = self.data['location']
        self.nickname = self.data['nickname']
        self.logo_url = self.data['logo']
        self.points = self.data['points']
        self.points = round(self.points, 2)
        wins = self.data['record']['overall']['wins']
        losses = self.data['record']['overall']['losses']
        self.record = f'{wins}-{losses}'
        self.waiver_position = self.data['waiverRank']

    def get_stats(self):
        '''Gets the stats for the team'''
        self.stats = {}
        self.add_stats(self.data['valuesByStat'])

    def create_player(self, player):
        '''
        Creates a new instance of the player class 
        given the JSON for the player from the API, 
        then adds them to the roster attribute
        '''
        # Some of the data from the API is strange, if we cannot find the ranking with playerPoolEntry
        # Then the player does not have a ranking
        rank = player['playerPoolEntry']['ratings']['0']['positionalRanking'] if 'playerPoolEntry' in player else 0
        player_data = player['playerPoolEntry']['player'] if 'playerPoolEntry' in player else player['player']
        team_id = TeamModel.query.filter_by(
            team_id=self.id, league_id=self.league_id, user_id=self.user_id).first().id
        new_player = Player(
            data=player_data, league_info=self.league_info, team_id=team_id, rank=rank)
        self.roster.add(new_player)

    def get_roster(self):
        '''
        Gets team roster JSON from the API,
        then iterates through it and creates
        an instance of the player class for
        each players
        '''
        for player in self.data['roster']['entries']:
            self.create_player(player)

    def handle_db(self):
        '''Handles adding the team to the database'''
        # Used to add or update the db as needed
        db_handler = TeamModelHandler(self)
        db_handler.add_or_update_record()

    def create_team(self):
        '''Drives necessary functions for adding a team'''
        self.get_basic_info()
        self.get_stats()


class Player(ESPNBase):
    '''ESPN API Wrapper for Players'''

    def __init__(self, data, league_info, team_id, rank):
        '''
        Gets basic player info and calls driving
        function
        '''
        self.league_info = league_info
        self.team_id = team_id
        self.league_id = league_info.get('league_model_id')
        self.league_info['team_id'] = team_id
        self.data = data
        self.rank = rank
        self.create_player()

    def get_basic_info(self):
        '''
        Gets all basic info for the player
        from the API and sets it into attributes
        on the instance
        '''
        self.id = self.data['id']
        self.position = POSITION_MAP[self.data['defaultPositionId']]
        self.first_name = self.data['firstName']
        self.last_name = self.data['lastName']
        self.outlooks = []
        # Some players don't have any outlooks, so we need this if statement
        if 'outlooks' in self.data:
            for week, outlook in self.data['outlooks']['outlooksByWeek'].items():
                int_week = int(week)
                self.outlooks.append((int_week, outlook))
        else:
            self.outlooks = []

        self.injured = self.data.get('injured', False)
        self.injury_status = self.data.get('injuryStatus', 'ACTIVE')
        self.pro_team = PRO_TEAM_MAP[self.data.get('proTeamId')]
        # Some players may be owned, but not on a pro team, thus we need to check for this
        if self.pro_team == 'None':
            self.pro_team = 'FA'

    def get_stat_data(self):
        '''
        Gets stat data for the player
        from the API and adds it to the
        stats attribute
        '''
        # The data['stats'] has many entries, but we only need the year that the league
        # is currently in. So we filter with 00YEAR
        year = self.league_info['year']
        year_id = f'00{year}'

        stat_block = [x for x in self.data['stats'] if x['id'] == year_id][0]
        self.points = stat_block['appliedTotal']
        self.points = round(self.points, 2)
        # Currently pulling point_avg from the API, but could be calculated using points / current week
        self.point_avg = stat_block['appliedAverage']
        self.projected_points = self.point_avg * \
            self.league_info['total_weeks']
        self.projected_points = round(self.projected_points, 2)

        stats_to_check = stat_block['appliedStats'] if stat_block.get(
            'appliedStats') else stat_block['stats']
        return stats_to_check

    def get_stats(self):
        '''
        Initializes the stats attribute to an empty
        dictionary, gets all stat data from the api,
        then adds the stats to the dictionary
        '''
        self.stats = {}
        stat_data = self.get_stat_data()
        self.add_stats(stat_data)

    def handle_db(self):
        '''Handles adding the instance to the database'''
        # Allows us to add or update without any crazy logic
        db_handler = PlayerModelHandler(self)
        db_handler.add_record()

    def create_player(self):
        '''Drives player creation'''
        self.get_basic_info()
        self.get_stats()
