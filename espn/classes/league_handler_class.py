from flask import session, flash, request
from espn.models import PlayerModel, TeamModel
from espn.classes.base_classes import ESPNRequest
from espn.classes.espn_classes import League


class FakeTeam:
    def __init__(self, id, league, name, roster, record, waiver_pos, points, grade, logo_url):
        self.id = id
        self.league = league
        self.name = name
        self.players = roster
        self.record = record
        self.waiver_pos = waiver_pos
        self.points = points
        self.grade = grade
        self.logo_url = logo_url
        self.switched_id = None

    def switch_players(self, current_player, player_to_switch):
        for player in self.players:
            if player.id == current_player.id:
                self.players.remove(player)
                self.players.append(player_to_switch)
                self.switched_id = player_to_switch.id
                print(self.switched_id)


class LeagueHandler:
    '''
    Handles the adding of
    a league form the add league
    form
    '''

    def get_players(self, form):
        user_players = {
            'QB': form.player_qb.data,
            'RB': form.player_rb.data,
            'WR': form.player_wr.data,
            'TE': form.player_te.data,
            'K': form.player_k.data,
            'D/ST': form.player_dst.data
        }
        users_to_pop = []
        for pos, data in user_players.items():
            if data == 'None':
                users_to_pop.append(pos)
        for pos in users_to_pop:
            user_players.pop(pos)

        other_players = {
            'QB': form.other_qb.data,
            'RB': form.other_rb.data,
            'WR': form.other_wr.data,
            'TE': form.other_te.data,
            'K': form.other_k.data,
            'D/ST': form.player_dst.data
        }
        others_to_pop = []
        for pos, data in other_players.items():
            if data == 'None':
                others_to_pop.append(pos)

        for pos in others_to_pop:
            other_players.pop(pos)

        unmatched_users = []
        for pos, data in user_players.items():
            if pos not in other_players:
                unmatched_users.append(pos)

        for pos in unmatched_users:
            user_players.pop(pos)

        unmatched_others = []
        for pos, data in other_players.items():
            if pos not in user_players:
                unmatched_others.append(pos)

        for pos in unmatched_others:
            other_players.pop(pos)

        for pos, data in user_players.items():
            user_players[pos] = int(data)

        for pos, data in other_players.items():
            other_players[pos] = int(data)

        return [user_players, other_players]

    def simulate_trade(self, form):
        [user_players, other_players] = self.get_players(form)

        user_player_models = []
        other_player_models = []

        for id in user_players.values():
            player = PlayerModel.query.get(id)
            user_player_models.append(player)
        for id in other_players.values():
            player = PlayerModel.query.get(id)
            other_player_models.append(player)

        if not user_player_models or not other_player_models:
            return False

        else:
            user_team = TeamModel.query.get(user_player_models[0].team_id)
            fake_team = FakeTeam(user_team.id, user_team.league, user_team.team_name, user_team.players, user_team.record,
                                 user_team.waiver_position, user_team.points, user_team.grade, user_team.logo_url)
            for user_player in user_player_models:
                for other_player in other_player_models:
                    if user_player.position == other_player.position:
                        fake_team.switch_players(user_player, other_player)
            return fake_team

    def get_league_data(self, form):
        '''
        Gets league data from the form,
        then gets data from the api given
        the form data, and returns it
        '''
        league_id = form.league_id.data
        year = form.year.data
        espn_request = ESPNRequest(league_id=league_id, year=year)
        data = espn_request.get_response_data()
        return [league_id, year, data]

    def add_league(self, form):
        '''
        Adds a league to the database
        with the given form data. If successful,
        returns True, otherwise flashes a message
        to the user and returns false
        '''
        user_id = session.get('user_id')
        if not user_id:
            flash('You need to login to do that!')
            return False

        [league_id, year, data] = self.get_league_data(form)

        if data.get('teams'):
            league = League(league_id=league_id, year=year, user_id=user_id)
            return True
        else:
            flash('Invalid League ID and/or year!')
            return False
