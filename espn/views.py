from flask import render_template, redirect, session, request, jsonify, flash
from app.app import app
from app.database import db, delete_from_db
from espn.settings import POSITIONS, GRADE_MAP
from espn.classes.news_class import News
from espn.classes.league_handler_class import LeagueHandler
from espn.models import LeagueModel, TeamModel, PlayerModel
from user.models import UserModel
from app.forms import AddLeagueForm, SelectTeamForm, SimulateTradeForm

league_handler = LeagueHandler()


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


@app.route('/leagues/<int:league_id>')
def league_page(league_id):
    '''Displays information about the league with id league_id'''
    if 'user_id' not in session:
        return redirect('/login')
    league = LeagueModel.query.get(league_id)
    if league.user_id == session.get('user_id'):
        user_team = TeamModel.query.get_or_404(league.user_team)
        return render_template('league.html', league=league, user_team=user_team)

    return redirect('/leagues')


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


@app.route('/leagues/<int:league_id>/trade-sim', methods=['POST'])
def show_trade_sim(league_id):
    form = SimulateTradeForm()
    if form.validate_on_submit:
        new_team = league_handler.simulate_trade(form)
        if new_team:
            return render_template('trade_sim.html', team=new_team)
        else:
            flash('There was an error in simulating your trade!', 'danger')
            return redirect(f'/leagues/{league_id}')


@app.route('/leagues/<int:league_id>/delete')
def delete_league(league_id):
    '''
    Deletes the league with id league_id from
    the database, if authentication succeeds.
    Otherwise returns home
    '''
    league = LeagueModel.query.get_or_404(league_id)
    if 'user_id' not in session:
        flash('You need to be logged in to do that!', 'danger')
    elif league.user_id == session.get('user_id'):
        league_handler.delete(league_id)
    else:
        flash('You cannot delete an account that isn\'t yours!', 'danger')
    return redirect('/')


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
        league_handler.set_trade_sim_choices(player, form)
        if request.form.get('player_grade'):
            trade_suggestions = league_handler.get_trade_suggestions(
                league.user_id, player)
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
