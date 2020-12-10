from flask import session
from espn.models import PlayerModel
from espn.settings import POSITIONS


class GradeCalculator:
    '''
    Calculates a letter
    grade for a player based
    on their stats and their position
    '''

    def __init__(self, stat_scores):
        self.positions = POSITIONS
        self.cap = 1
        self.weight = 0.05
        self.stat_scores = stat_scores
        self.extremes = {}

        for position in self.positions:
            self.extremes[position] = {'MIN': 100, 'MAX': -100}

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

    def get_score(self, player):
        stats = player.stats
        total = 0

        total += player.points * self.weight

        if total != 0:
            score = (total / self.cap)
        else:
            score = 0

        return score

    def set_grade_ranges(self):
        self.grade_ranges = {}

        for position in self.extremes.keys():
            increment = self.extremes[position]['MAX'] / 5
            f_range = (0, increment)
            d_range = (increment, increment * 2)
            c_range = (increment * 2, increment * 3)
            b_range = (increment * 3, increment * 4)
            a_range = (increment * 4, increment * 5)
            self.grade_ranges[position] = {
                'A': a_range,
                'B': b_range,
                'C': c_range,
                'D': d_range,
                'F': f_range
            }

    def get_pos_extremes(self, player):
        '''
        Gets max and min for the given player's
        position, and puts it in the session.
        This is used to get the grade ranges for players.
        '''
        score = self.get_score(player)

        pos_max = self.extremes[player.position]['MAX']
        if pos_max:
            if score > pos_max:
                self.extremes[player.position]['MAX'] = score
        else:
            self.extremes[player.position]['MAX'] = score

        pos_min = self.extremes[player.position]['MIN']
        if pos_min:
            if score < pos_min:
                self.extremes[player.position]['MIN'] = score
        else:
            self.extremes[player.position]['MIN'] = score

    def grade_player(self, player):
        '''
        Takes a player, and assigns them
        a letter grade based on their stats
        '''
        score = self.get_score(player)

        grade = self.get_grade(score, player.position)
        return grade
