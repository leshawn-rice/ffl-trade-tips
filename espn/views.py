from flask import render_template, redirect, session, request
from app.app import app
from espn.settings import POSITIONS, GRADE_MAP
from espn.classes.news_class import News
from espn.models import LeagueModel, TeamModel, PlayerModel
from user.models import UserModel
from user.auth import UserAuthentication
from app.forms import AddLeagueForm

authentication = UserAuthentication()


@app.route('/recent-news')
def show_news():
    news = News()
    news.get_news()
    return render_template('news.html', news=news.data)


@app.route('/add-league', methods=['GET', 'POST'])
def add_league():
    form = AddLeagueForm()

    if form.validate_on_submit():
        league = authentication.add_league(form)
        if league:
            return redirect('/')
        else:
            return render_template('add_league.html', form=form)
    else:
        return render_template('add_league.html', form=form)


@app.route('/leagues')
def show_leagues():
    if 'user_id' not in session:
        return redirect('/login')
    user = UserModel.query.get(session['user_id'])
    leagues = user.leagues
    return render_template('all_leagues.html', leagues=leagues)


@app.route('/leagues/<int:league_id>')
def league_page(league_id):
    if 'user_id' not in session:
        return redirect('/login')
    league = LeagueModel.query.get_or_404(league_id)
    if league.user_id == session.get('user_id'):
        return render_template('league.html', league=league)

    return redirect('/leagues')


@app.route('/teams/<int:team_id>')
def team_page(team_id):
    if 'user_id' not in session:
        return redirect('/login')
    team = TeamModel.query.get_or_404(team_id)
    league = team.league
    if league.user_id == session.get('user_id'):
        return render_template('team.html', team=team)

    return redirect('/leagues')


@app.route('/players/<int:player_id>', methods=['GET', 'POST'])
def player_page(player_id):
    if 'user_id' not in session:
        return redirect('/login')
    player = PlayerModel.query.get_or_404(player_id)
    league = player.league
    if league.user_id == session.get('user_id'):
        player_grade = request.form.get('player_grade')
        if player_grade:
            acceptable_grades = GRADE_MAP[player_grade]
            trade_suggestions = PlayerModel.query.filter(
                PlayerModel.grade.in_(acceptable_grades), PlayerModel.position == player.position, PlayerModel.id != player.id).all()
            print(trade_suggestions)
            return render_template('player.html', player=player, trade_suggestions=trade_suggestions)
        return render_template('player.html', player=player)

    return redirect(f'/teams/{player.team.id}')
