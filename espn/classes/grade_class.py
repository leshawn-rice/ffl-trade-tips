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
        '''
        Sets necessary info to attributes 
        (positions, cap, weight, stat_scores),
        then sets the extremes attributes
        to values that should be overwritten
        by player data
        '''
        self.positions = POSITIONS
        self.cap = 1
        # 0.05 is an arbitrary value. Any value that is less than cap will work. I use 0.05 since it is 0.05% of the cap
        # (1), which lowers the margin of error when grading
        self.weight = 0.05
        self.stat_scores = stat_scores
        self.extremes = {}

        for position in self.positions:
            # Set the min/max for each position to scores that unobtainable
            self.extremes[position] = {'MIN': 1000, 'MAX': -1000}

    def get_grade(self, score, pos):
        '''
        Given a position and a weighted score,
        returns the letter grade for the player
        '''
        for grade, grade_range in self.grade_ranges[pos].items():
            if (grade_range[0] <= score <= grade_range[1]):
                return grade
        return 'A'  # The player will only have a score outside the range if it is above the A grade

    def adjust_score_total(self, player_stats, current_stat, current_total):
        '''
        Adjusts the total score for the player
        given a single stat (not currently used)
        '''
        # So in PPR this would mean (Receptions=1 => 1 * 0.05 = 0.05 is the stat weight)
        stat_weight = (self.stat_scores[current_stat] * self.weight)
        player_stat = [s for s in player_stats if s.stat_name == current_stat]
        if player_stat:
            # So if they have 50 points from receptions, thats 50 * 0.05 which = 2.5. This is basically
            # their score in that stat. The app currently only evaluates points, because it is faster
            # And if you add up all the stat values you get the point value anyway
            current_total += (player_stat[0].stat_value * stat_weight)
        return current_total

    def get_score(self, player):
        '''
        Calculates and returns the
        players weighted score
        '''
        stats = player.stats
        total = 0

        # If a player has 500 points and weight is 0.05 their total = 25
        total += player.points * self.weight

        if total >= 0:
            # If we change the cap then this will affect the total. Currently with cap @ 1, score = total,
            # but if we adjust cap to 0.5 for example, the score increases. This doesn't necessarily matter
            # as long as the cap is the same for every score, because they will be graded based on score extremes
            score = (total / self.cap)
        else:
            score = 0

        return score

    def set_grade_ranges(self):
        '''
        Calculates grade ranges (A-F)
        based on previously calculated
        position extremes (minScore-maxScore)
        '''
        self.grade_ranges = {}

        for position in self.extremes.keys():
            # Because there are 5 grades, there needs to be 5 ranges
            increment = self.extremes[position]['MAX'] / 5
            # Because we set score to 0 if total < 0, 0 is our starting point,
            # and increment * 5  is the position max
            self.grade_ranges[position] = {
                'A': (increment * 4, increment * 5),
                'B': (increment * 3, increment * 4),
                'C': (increment * 2, increment * 3),
                'D': (increment, increment * 2),
                'F': (0, increment)
            }

    def get_pos_extremes(self, player):
        '''
        Gets max and min for the given player's
        position, and puts it in the extremes attribute.
        This is used to get the grade ranges for positions.
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
