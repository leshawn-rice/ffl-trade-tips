from flask import session
from espn.models import PlayerModel
from espn.settings import POSITIONS


class GradeCalculator:
    def __init__(self):
        self.positions = POSITIONS
        self.cap = 1
        self.weight = 0.05
        # Different ranges for different positions
        # Check print statement for max and min on each player
        # F min will always be 0, f max should be lowest score for that pos

        self.grade_ranges = {
            'A': (20, 25),
            'B': (15, 19),
            'C': (10, 14),
            'D': (5, 9),
            'F': (0, 4)
        }

        self.stat_scores = {
            # Offensive stats
            'passing_2_pts': 2, 'passing_yds': 0.04, 'passing_interceptions': -2, 'passing_tds': 4,
            'rushing_yds': 0.1, 'rushing_tds': 6, 'rushing_2_pts': 2, 'lost_fumbles': -2,
            'receiving_receptions': 1, 'receiving_yds': 0.1, 'receiving_tds': 6, 'receiving_2_pts': 2,
            # Kicking stats
            'made_fgs_under_40': 3, 'made_fgs_40_to_49': 4, "made_fgs_50_plus": 5,
            'made_pats': 1, 'missed_fgs': -1.5, 'missed_pats': 0,
            # Defensive stats
            "d_blocked_kick_tds": 2, "d_interceptions": 2, "d_fumbles": 2,
            "d_blocked_kicks": 2, "d_safeties": 2, "d_sacks": 1,
            "d_0_pts": 5, "d_1_to_6_pts": 4, "d_7_to_13_pts": 3,
            "d_14_to_17_pts": 1, "d_28_to_34_pts": -1, "d_35_to_45_pts": -3,
            "d_100_to_199_yds": 3, "d_200_to_299_yds": 2, "d_300_to_349_yds": 0,
            "d_350_to_399_yds": -1, "d_400_to_449_yds": -3, "d_450_to_499_yds": -5,
            "d_500_to_549_yds": -6, "d_over_550_yds": -7
        }

    def get_grade(self, score):
        for grade, grade_range in self.grade_ranges.items():
            if (grade_range[0] <= score <= grade_range[1]):
                return grade

    def adjust_score_total(self, player_stats, current_stat, current_total):
        stat_weight = (self.stat_scores[current_stat] * self.weight)
        player_stat = [s for s in player_stats if s.stat_name == current_stat]
        if player_stat:
            current_total += (player_stat[0].stat_value * stat_weight)
        return current_total

    def get_pos_extremes(self, player):
        # Get max pos score
        pos_max = session.get(f'{player.position}_max')
        if pos_max:
            if score > pos_max:
                session[player.position] = score
        else:
            session[f'{player.position}_max'] = score
        pos_min = session.get(f'{player.position}_min')
        if pos_min:
            if score < pos_min:
                session[player.position] = score
        else:
            session[f'{player.position}_min'] = score

    def grade_player(self, player):
        stats = player.stats
        total = 0

        for stat in self.stat_scores.keys():
            total = self.adjust_score_total(player_stats=stats,
                                            current_stat=stat, current_total=total)
        if total != 0:
            score = (total / self.cap)
        else:
            score = 0
        self.get_pos_extremes(player)
        p_max = session.get(f'{player.position}_max')
        p_min = session.get(f'{player.position}_min')
        print(f'Position: {player.position}\nMax: {p_max}\nMin: {p_min}')
        grade = self.get_grade(score)
        return grade
