from flask import flash, session
from app.database import add_to_db
from users.models import UserModel
from espn.models import PlayerModel, TeamModel, LeagueModel
from espn.classes.espn_classes import League
from espn.classes.base_classes import ESPNRequest


class FormHandler:
    '''
    Handles logic behind all forms.
    Validates usernames and passwords.
    Handles pulling database info from
    searches.
    '''

    def get_matching_players(self, search_query):
        '''
        Gets players from the database that
        match the search query, and adds them
        to a Set 'players'
        '''
        [pos, prmin, prmax, ptmin, ptmax, grade] = search_query.values()

        players = PlayerModel.query.filter(PlayerModel.position == pos, PlayerModel.position_rank >=
                                           prmin, PlayerModel.position_rank <= prmax, PlayerModel.points >= ptmin, PlayerModel.points <= ptmax, PlayerModel.grade == grade).all()

        return players

    def get_search_query(self, form):
        '''
        Gets the search query from the form and
        puts the values into a dictionary
        '''
        pos = form.position.data
        pos_rank_min = form.pos_rank_min.data if form.pos_rank_min.data else 0
        pos_rank_max = form.pos_rank_max.data if form.pos_rank_max.data else 100
        points_min = form.points_min.data if form.points_min.data else 0
        points_max = form.points_max.data if form.points_max.data else 1000
        grade = form.grade.data

        search_query = {'pos': pos, 'prmin': pos_rank_min,
                        'prmax': pos_rank_max, 'ptmin': points_min, 'ptmax': points_max, 'grade': grade}

        return search_query

    def search_player(self, form):
        '''
        Drives the logic behind a player search.
        Gets the search query, then gets a set of players
        that match the query, and returns it
        '''
        search_query = self.get_search_query(form)
        print(search_query)
        players = self.get_matching_players(search_query)
        return players
