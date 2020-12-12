from flask import render_template, redirect, session, request, jsonify
from app.app import app
from app.database import db
from espn.settings import POSITIONS, GRADE_MAP
from espn.classes.news_class import News
from espn.classes.league_handler_class import LeagueHandler
from espn.models import LeagueModel, TeamModel, PlayerModel
from user.models import UserModel
from app.forms import AddLeagueForm, SelectTeamForm, SimulateTradeForm

league_handler = LeagueHandler()


def get_trade_suggestions(player):
    '''
    Gets players with grades 1 below and above the current
    player's with the same position, and returns a list of them.
    '''
    user_id = session.get('user_id')
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


def set_trade_sim_choices(player, form):
    '''
    Gets the players in each position on the current
    players team and not on their team, and puts them
    in a list of choices for their respective category
    '''
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


@app.route('/recent-news')
def show_news():
    '''
    Gets recent NFL news and
    displays it on the page
    '''
    news = News()
    news.get_news()
    return render_template('news.html', news=news.data)


@app.route('/add-league', methods=['GET', 'POST'])
def add_league():
    '''
    Displays the form, and handles the form, for when
    a player needs to add or refresh a league
    '''
    form = AddLeagueForm()

    if form.validate_on_submit():
        league = league_handler.add_league(form)
        if league:
            user_id = session.get('user_id')
            league_model = LeagueModel.query.filter_by(
                league_id=form.league_id.data, user_id=user_id).first()
            return redirect(f'/leagues/{league_model.id}/select-team')
        else:
            return render_template('add_league.html', form=form)
    else:
        return render_template('add_league.html', form=form)


@app.route('/leagues')
def show_leagues():
    '''
    Displays all the users leagues
    '''
    if 'user_id' not in session:
        return redirect('/login')
    user = UserModel.query.get(session['user_id'])
    leagues = user.leagues
    return render_template('all_leagues.html', leagues=leagues)


@app.route('/leagues/<int:league_id>/select-team', methods=['GET', 'POST'])
def select_team(league_id):
    '''Allows User to select their team from list of teams'''
    if 'user_id' not in session:
        return redirect('/login')
    league = LeagueModel.query.get_or_404(league_id)
    if league.user_id == session.get('user_id'):
        form = SelectTeamForm()
        choices = [(t.id, t.team_name) for t in league.teams]
        form.team.choices = choices
        if form.validate_on_submit():
            user_team_id = form.team.data
            league.user_team = user_team_id
            db.session.commit()
            return redirect('/')

        return render_template('select_team.html', form=form)

    flash('You cannot do that for league you don\'t own!', 'danger')
    return redirect('/')


@app.route('/leagues/<int:league_id>')
def league_page(league_id):
    '''Displays information about the league with id league_id'''
    if 'user_id' not in session:
        return redirect('/login')
    league = LeagueModel.query.get_or_404(league_id)
    if league.user_id == session.get('user_id'):
        user_team = TeamModel.query.get_or_404(league.user_team)
        return render_template('league.html', league=league, user_team=user_team)

    return redirect('/leagues')


@app.route('/teams/<int:team_id>')
def team_page(team_id):
    '''Displays the team page'''
    if 'user_id' not in session:
        return redirect('/login')
    team = TeamModel.query.get_or_404(team_id)
    league = team.league
    if league.user_id == session.get('user_id'):
        return render_template('team.html', team=team)

    return redirect('/leagues')


@app.route('/players/<int:player_id>', methods=['GET', 'POST'])
def player_page(player_id):
    '''Displays the player page'''
    if 'user_id' not in session:
        return redirect('/login')
    player = PlayerModel.query.get_or_404(player_id)
    league = player.league
    if league.user_id == session.get('user_id'):
        form = SimulateTradeForm()
        set_trade_sim_choices(player, form)
        if request.form.get('player_grade'):
            trade_suggestions = get_trade_suggestions(player)
            return render_template('player.html', player=player, trade_suggestions=trade_suggestions, form=form)
        else:
            return render_template('player.html', player=player, form=form)
    return redirect(f'/teams/{player.team.id}')


@app.route('/players/<int:player_id>/stats-data')
def get_player_stats(player_id):
    player = PlayerModel.query.get_or_404(player_id)
    stats = []
    for stat in player.stats:
        stat_dict = {}
        stat_dict['name'] = stat.stat_name
        stat_dict['value'] = stat.stat_value
        stats.append(stat_dict)
    return (jsonify(stats=stats), 200)


@app.route('/players/<int:player_id>/outlooks-data')
def get_player_outlooks(player_id):
    player = PlayerModel.query.get_or_404(player_id)
    outlooks = []
    for outlook in player.outlooks:
        outlook_dict = {
            'week': outlook.week,
            'outlook': outlook.outlook
        }
        outlooks.append(outlook_dict)
    return (jsonify(outlooks=outlooks), 200)


@app.route('/leagues/<int:league_id>/trade-sim', methods=['POST'])
def show_trade_sim(league_id):
    form = SimulateTradeForm()
    if form.validate_on_submit:
        new_team = league_handler.simulate_trade(form)
        return render_template('trade_sim.html', team=new_team)
