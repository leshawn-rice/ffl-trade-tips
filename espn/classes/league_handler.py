class LeagueHandler:
    '''
    Handles the adding of
    a league form the add league
    form
    '''

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
