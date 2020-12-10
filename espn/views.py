from flask import render_template, redirect, session, request, jsonify
from app.app import app
from app.database import db
from espn.settings import POSITIONS, GRADE_MAP
from espn.classes.news_class import News
from espn.models import LeagueModel, TeamModel, PlayerModel
from user.models import UserModel
from user.auth import UserAuthentication
from app.forms import AddLeagueForm, SelectTeamForm

authentication = UserAuthentication()


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
        league = authentication.add_league(form)
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
        if request.method == 'POST':
            trade_suggestions = get_trade_suggestions(player)
            return render_template('player.html', player=player, trade_suggestions=trade_suggestions)
        else:
            return render_template('player.html', player=player)
    return redirect(f'/teams/{player.team.id}')


@app.route('/players/<int:player_id>/stats-data')
def get_player_stats(player_id):
    player = PlayerModel.query.get_or_404(player_id)
    print(player.stats)
    stats = []
    for stat in player.stats:
        stat_dict = {}
        stat_dict['name'] = stat.stat_name
        stat_dict['value'] = stat.stat_value
        stats.append(stat_dict)
    return (jsonify(stats=stats), 200)
