import datetime
import requests
from app.database import db, add_to_db
from espn.settings import STATS_MAP


class ESPNRequest:
    '''
    Class used for sending a request to the
    ESPN API
    '''

    def __init__(self, league_id, year, cookies=None):
        '''
        Sets the league id & year from the parameters,
        and creates a base url with those params that will
        be used for following API requests
        '''
        self.league_id = league_id
        self.year = year
        self.cookies = cookies
        self.base_url = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{self.year}/segments/0/leagues/{self.league_id}'

    def get_response_data(self, params=None):
        '''
        Takes in a dict 'params' that contains
        any views, and other settings to use with
        the API request
        '''
        response = requests.get(self.base_url, params=params)

        data = response.json()
        return data


class ModelHandlerBase:
    def add_or_update_record(self):
        '''
        Checks if a record in the necessary table
        needs to be updated. If so updates the record,
        if a record doesn't exist then it makes one.
        '''
        if self.check_for_record():
            if self.check_for_record_update():
                self.update_record()
        else:
            self.add_record()


class ESPNBase:
    def __init__(self):
        '''
        Gets necessary league info
        to make an espn request to get
        data for the current object
        '''
        self.r_league_id = self.league_info['league_id']
        self.r_year = self.league_info['year']
        self.r_cookies = self.league_info['cookies']

    def make_espn_request(self, params=None):
        '''
        Makes an ESPN Request with the given params by
        instantiating an ESPNRequest object
        '''
        _request = ESPNRequest(
            league_id=self.r_league_id, year=self.r_year, cookies=self.r_cookies)
        return _request.get_response_data(params=params)

    def add_stats(self, stats_to_check):
        '''
        Adds each stat from dict 'stats_to_check'
        to the player's stats dict.
        '''
        for stat, val in stats_to_check.items():
            stat = int(stat)
            stat_name = STATS_MAP.get(stat)
            if stat_name:
                self.stats[stat_name] = round(val, 2)
