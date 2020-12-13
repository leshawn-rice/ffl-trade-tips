from flask import session, flash, request
from app.database import delete_from_db
from espn.settings import GRADE_MAP
from espn.models import PlayerModel, TeamModel, LeagueModel
from espn.classes.base_classes import ESPNRequest
from espn.classes.espn_classes import League


class FakeTeam:
    '''
    Class used for rendering
    team data after trade sim
    '''

    def __init__(self, id, league, name, roster, record, waiver_pos, points, grade, logo_url):
        '''
        Gets necessary data about team
        in order to render on page
        '''
        self.id = id
        self.league = league
        self.name = name
        self.players = roster
        self.record = record
        self.waiver_pos = waiver_pos
        self.points = points
        self.grade = grade
        self.logo_url = logo_url

    def switch_players(self, current_player, player_to_switch):
        '''
        Switches player 'current_player'
        with player 'player_to_switch' in the
        players attribute
        '''
        for player in self.players:
            if player.id == current_player.id:
                # Remove the current player
                self.players.remove(player)
                # Add the player the user is wanting to receive
                self.players.append(player_to_switch)


class LeagueHandler:
    '''
    Handles the adding of
    a league form the add league
    form
    '''

    def get_sim_players(self, form):
        '''
        Gets the player_ids from
        the form data, and returns a list
        of dictionaries with positions as
        keys and player ids as values
        '''

        # Dict with form data for user players
        user_players = {
            'QB': form.player_qb.data,
            'RB': form.player_rb.data,
            'WR': form.player_wr.data,
            'TE': form.player_te.data,
            'K': form.player_k.data,
            'D/ST': form.player_dst.data
        }
        # We need to remove keys that have values of 'None'
        users_to_pop = []
        for pos, data in user_players.items():
            if data == 'None':
                users_to_pop.append(pos)
        for pos in users_to_pop:
            user_players.pop(pos)

        # Dict with form data for other players
        other_players = {
            'QB': form.other_qb.data,
            'RB': form.other_rb.data,
            'WR': form.other_wr.data,
            'TE': form.other_te.data,
            'K': form.other_k.data,
            'D/ST': form.player_dst.data
        }
        # We need to remove keys that have values of 'None'
        others_to_pop = []
        for pos, data in other_players.items():
            if data == 'None':
                others_to_pop.append(pos)

        for pos in others_to_pop:
            other_players.pop(pos)

        # If a user player is selected but
        # no matching other player @ that position
        # Then we cannot simulate the trade
        # And need to remove that player
        unmatched_users = []
        for pos, data in user_players.items():
            if pos not in other_players:
                unmatched_users.append(pos)
        for pos in unmatched_users:
            user_players.pop(pos)

        # If a non-user player is selected but
        # no matching user player @ that position
        # Then we cannot simulate the trade
        # And need to remove that player
        unmatched_others = []
        for pos, data in other_players.items():
            if pos not in user_players:
                unmatched_others.append(pos)
        for pos in unmatched_others:
            other_players.pop(pos)

        # Convert ids to integers
        for pos, data in user_players.items():
            user_players[pos] = int(data)
        for pos, data in other_players.items():
            other_players[pos] = int(data)

        return [user_players, other_players]

    def simulate_trade(self, form):
        '''
        Creates a fake team with the
        primary player's team data,
        and replaces the players we are
        trading away with the players we
        are receiving, returns the fake team
        or False if the trade sim cannot be done
        '''
        [user_players, other_players] = self.get_sim_players(form)

        user_player_models = []
        other_player_models = []

        for id in user_players.values():
            player = PlayerModel.query.get(id)
            user_player_models.append(player)
        for id in other_players.values():
            player = PlayerModel.query.get(id)
            other_player_models.append(player)

        # If there are no players in either one, then the trade
        # sim cannot be completed, return false
        if not user_player_models or not other_player_models:
            return False

        else:
            # Get the team for the primary player (player page we redirected from)
            user_team = TeamModel.query.get(user_player_models[0].team_id)
            # Create a fake team instance for rendering on the page
            fake_team = FakeTeam(user_team.id, user_team.league, user_team.team_name, user_team.players, user_team.record,
                                 user_team.waiver_position, user_team.points, user_team.grade, user_team.logo_url)
            for user_player in user_player_models:
                for other_player in other_player_models:
                    if user_player.position == other_player.position:
                        fake_team.switch_players(user_player, other_player)
            return fake_team

    def get_trade_suggestions(self, user_id, player):
        '''
        Gets players with grades 1 below and above the current
        player's with the same position, and returns a list of them.
        '''
        player_grade = request.form.get('player_grade')
        trade_suggestions = []
        if player_grade:
            acceptable_grades = GRADE_MAP[player_grade]
            teams = TeamModel.query.filter_by(user_id=user_id)
            for team in teams:
                for p in team.players:
                    if p.grade in (acceptable_grades) and p.position == player.position and p.id != player.id and p.points >= player.points:
                        trade_suggestions.append(p)
        if trade_suggestions:
            return trade_suggestions[:3]
        else:
            return ['NO PLAYERS FOUND']

    def get_league_data(self, form):
        '''
        Gets league data from the form,
        then gets data from the api given
        the form data, and returns it
        '''
        league_id = form.league_id.data
        year = form.year.data
        # We make this single request in order to validate the league id and year
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

        # data['teams'] will only be present if we sent a valid request
        if data.get('teams'):
            league = League(league_id=league_id, year=year, user_id=user_id)
            return True
        else:
            flash('Invalid League ID and/or year!', 'danger')
            return False

    def delete(self, league_id):
        '''Deletes the league from the db'''
        league = LeagueModel.query.get_or_404(league_id)
        delete_from_db(league)
        flash('League Deleted Successfuly', 'success')

    def set_trade_sim_choices(self, player, form):
        '''
        Gets the players in each position on the current
        players team and not on their team, and puts them
        in a list of choices for their respective category
        '''

        # Ideally this would be in a loop, but I'm not quite sure how to do that
        form.player_qb.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'QB', PlayerModel.team_id == player.team_id)]
        form.player_qb.choices.insert(0, (None, 'NONE'))
        form.player_rb.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'RB', PlayerModel.team_id == player.team_id)]
        form.player_rb.choices.insert(0, (None, 'NONE'))
        form.player_wr.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'WR', PlayerModel.team_id == player.team_id)]
        form.player_wr.choices.insert(0, (None, 'NONE'))
        form.player_te.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'TE', PlayerModel.team_id == player.team_id)]
        form.player_te.choices.insert(0, (None, 'NONE'))
        form.player_k.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'K', PlayerModel.team_id == player.team_id)]
        form.player_k.choices.insert(0, (None, 'NONE'))
        form.player_dst.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'D/ST', PlayerModel.team_id == player.team_id)]
        form.player_dst.choices.insert(0, (None, 'NONE'))

        form.other_qb.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'QB', PlayerModel.team_id != player.team_id)]
        form.other_qb.choices.insert(0, (None, 'NONE'))
        form.other_rb.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'RB', PlayerModel.team_id != player.team_id)]
        form.other_rb.choices.insert(0, (None, 'NONE'))
        form.other_wr.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'WR', PlayerModel.team_id != player.team_id)]
        form.other_wr.choices.insert(0, (None, 'NONE'))
        form.other_te.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'TE', PlayerModel.team_id != player.team_id)]
        form.other_te.choices.insert(0, (None, 'NONE'))
        form.other_k.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'K', PlayerModel.team_id != player.team_id)]
        form.other_k.choices.insert(0, (None, 'NONE'))
        form.other_dst.choices = [(p.id, p.full_name) for p in PlayerModel.query.filter(
            PlayerModel.position == 'D/ST', PlayerModel.team_id != player.team_id)]
        form.other_dst.choices.insert(0, (None, 'NONE'))
