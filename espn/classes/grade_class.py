from flask import session
from espn.models import PlayerModel
from espn.settings import POSITIONS


class GradeCalculator:
    '''
    Calculates a letter
    grade for a player based
    on their stats and their position
    '''

    def __init__(self):
        self.positions = POSITIONS
        self.cap = 1
        self.weight = 0.05
        self.ppr = None

        self.grade_ranges = {
            'QB': {
                'A': (28.8, 36),
                'B': (21.6, 28.8),
                'C': (14.4, 21.6),
                'D': (7.2, 14.4),
                'F': (0, 7.2)
            },
            'RB': {
                'A': (22.4, 28),
                'B': (16.8, 22.4),
                'C': (11.2, 16.8),
                'D': (5.6, 11.2),
                'F': (0, 5.6)
            },
            'WR': {
                'A': (22.4, 28),
                'B': (16.8, 22.4),
                'C': (11.2, 16.8),
                'D': (5.6, 11.2),
                'F': (0, 5.6)
            },
            'K': {
                'A': (1.68, 2.1),
                'B': (1.26, 1.68),
                'C': (0.84, 1.26),
                'D': (0.42, 0.84),
                'F': (0, 0.42)
            },
            'D/ST': {
                'A': (11.76, 14.7),
                'B': (8.82, 11.76),
                'C': (5.88, 8.82),
                'D': (2.94, 5.88),
                'F': (0, 2.94)
            },
            'OTHER': {
                'A': (17.40, 21.76),
                'B': (13.056, 17.408),
                'C': (8.704, 13.056),
                'D': (4.352, 8.704),
                'F': (0, 4.352)
            }
        }

        self.stat_scores = {
            # Offensive stats
            'Passing 2 PT Conversions': 2, 'Passing Yards': 0.04, 'Passing Interceptions': -2, 'Passing Touchdowns': 4,
            'Rushing Yards': 0.1, 'Rushing Touchdowns': 6, 'Rushing 2 PT Conversions': 2, 'Lost Fumbles': -2,
            'Receiving Receptions': 1, 'Receiving Yards': 0.1, 'Receiving Touchdowns': 6, 'Receiving 2 PT Conversions': 2,
            # Kicking stats
            'Made FGs Under 40 Yards': 3, 'Made FGs From 40-49 Yards': 4, 'Made FGs From over 50 Yds': 5,
            'Made PATs': 1, 'Missed FGs': -1.5, 'Missed PATs': 0,
            # Defensive stats
            'Defensive Blocked PATs': 2, 'Defensive Interceptions': 2, 'Defensive Fumbles': 2,
            'Defensive Blocked Kicks': 2, 'Defensive Safeties': 2, 'Defensive Sacks': 1,
            'Allowed 0 Points': 5, 'Allowed 1-6 Points': 4, 'Allowed 7-13 Points': 3,
            'Allowed 14-17 Points': 1, 'Allowed 28-34 Points': -1, 'Allowed 35-45 Points': -3,
            'Allowed 100-199 Yards': 3, 'Allowed 200-299 Yards': 2, 'Allowed 300-349 Yards': 0,
            'Allowed 350-399 Yards': -1, 'Allowed 400-449 Yards': -3, 'Allowed 450-499 Yards': -5,
            'Allowed 500-549 Yards': -6, 'Allowed Over 500 Yards': -7
        }

    def get_grade(self, score, pos):
        '''
        Given a position and a weighted score,
        returns the letter grade for the player
        '''
        if pos not in self.grade_ranges:
            pos = 'OTHER'
        for grade, grade_range in self.grade_ranges[pos].items():
            if (grade_range[0] <= score <= grade_range[1]):
                return grade
        return 'A'  # The player will only have a score outside the range if it is above the A grade

    def adjust_score_total(self, player_stats, current_stat, current_total):
        '''
        Adjusts the total score for the player
        given a single stat
        '''
        stat_weight = (self.stat_scores[current_stat] * self.weight)
        player_stat = [s for s in player_stats if s.stat_name == current_stat]
        if player_stat:
            current_total += (player_stat[0].stat_value * stat_weight)
        return current_total

    def get_pos_extremes(self, player, score):
        '''
        Gets max and min for the given player's
        position, and puts it in the session.
        This is used to get the grade ranges for players.
        '''
        pos_max = session.get(f'{player.position}_max')
        if pos_max:
            if score > pos_max:
                session[f'{player.position}_max'] = score
        else:
            session[f'{player.position}_max'] = score
        pos_min = session.get(f'{player.position}_min')
        if pos_min:
            if score < pos_min:
                session[f'{player.position}_min'] = score
        else:
            session[f'{player.position}_min'] = score

    def get_ppr(self):
        self.ppr = session.get('PPR')
        if self.ppr:
            self.ppr = 1
        else:
            self.ppr = 0.5
        self.stat_scores['Receiving Receptions'] = self.ppr

    def grade_player(self, player):
        '''
        Takes a player, and assigns them
        a letter grade based on their stats
        '''
        self.get_ppr()
        stats = player.stats
        total = 0

        for stat in self.stat_scores.keys():
            total = self.adjust_score_total(player_stats=stats,
                                            current_stat=stat, current_total=total)
        if total != 0:
            score = (total / self.cap)
        else:
            score = 0

        grade = self.get_grade(score, player.position)
        return grade
