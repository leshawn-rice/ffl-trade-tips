from flask import flash, session
from app.database import add_to_db
from users.models import UserModel
from espn.models import PlayerModel, TeamModel, LeagueModel
from espn.classes.espn_classes import League
from espn.classes.base_classes import ESPNRequest


# Change to just get from espn class
class UserID:
    def __init__(self, id):
        self.id = id


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

        # query = db.session.query(PlayerModel)

        # if position:
        #     query = query.filter(date == pos)

        # if date_end:
        #     query = query.filter(date <= date_end)

        # if broker_list:
        #     query = query.filter(login_model.Invoice.broker.in_(broker_list))

        # if hcode_list:
        #     query = query.filter(
        #         login_model.Invoice.health_code.in_(hcode_list))

        # result = query.all()

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

    def create_user(self, user_data):
        '''
        Creates a new user with the given user_data and adds them to the db,
        if a user with the given username already exists, 
        returns none.
        '''
        [email, username, password, confirm_password] = user_data
        if not (UserModel.query.filter_by(username=username).first()):
            if not (UserModel.query.filter_by(email=email).first()):
                new_user = UserModel(
                    email=email, username=username, password=password)
                add_to_db(new_user)
                return new_user
            else:
                session['email_taken'] = True
                return None
        else:
            session['username_taken'] = True
            return None

    def get_user_data(self, form):
        '''
        Gets the entered data from the form
        and returns it as a list
        '''
        email = form.email.data
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        return [email, username, password, confirm_password]

    def sign_up(self, form):
        '''
        Drives the logic behind signing up a new user
        Gets data from the form,
        Creates a new user,
        Adds the user's league info to the database,
        And logs the user in
        '''
        new_user_data = self.get_user_data(form)
        user = self.create_user(new_user_data)
        if user:
            session['user_id'] = user.id
            session['logged_in'] = True
            return user
        else:
            return False

    def log_in(self, form):
        '''
        Logs the user in given the form data
        '''
        username = form.username.data
        password = form.password.data

        # Case sensitive, need to change
        user = UserModel.query.filter_by(
            username=username, password=password).first()
        if user:
            session['logged_in'] = True
            session['user_id'] = user.id
            return True
        else:
            flash('Username/Password do not match!')
            return False

    def add_league(self, form):
        league_id = form.league_id.data
        year = form.year.data
        is_valid = ESPNRequest(league_id=league_id, year=year)
        data = is_valid.get_response_data()
        u = UserID(session['user_id'])
        if data.get('teams'):
            league = League(league_id=league_id, year=year, user=u)
            session['league_id'] = league.id
            return True
        else:
            flash('Invalid League ID and/or year!')
            return False
