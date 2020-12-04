STANDARD_SEASON_LENGTH = 13

POSITION_MAP = {
    0: 'QB', 1: 'QB', 2: 'RB', 3: 'WR', 4: 'WR', 5: 'K',
    6: 'TE', 7: 'OP', 8: 'DT', 9: 'DE', 10: 'LB', 11: 'DL',
    12: 'CB', 13: 'S', 14: 'DB', 15: 'DP', 16: 'D/ST', 17: 'K',
    25: 'Rookie'
}

POSITIONS = list(set([pos for pos in POSITION_MAP.values()]))

PRO_TEAM_MAP = {
    0: 'None', 1: 'ATL', 2: 'BUF', 3: 'CHI', 4: 'CIN', 5: 'CLE', 6: 'DAL',
    7: 'DEN', 8: 'DET', 9: 'GB', 10: 'TEN', 11: 'IND', 12: 'KC', 13: 'OAK',
    14: 'LAR', 15: 'MIA', 16: 'MIN', 17: 'NE', 18: 'NO', 19: 'NYG', 20: 'NYJ',
    21: 'PHI', 22: 'ARI', 23: 'PIT', 24: 'LAC', 25: 'SF', 26: 'SEA', 27: 'TB',
    28: 'WSH', 29: 'CAR', 30: 'JAX', 33: 'BAL', 34: 'HOU'
}

ACTIVITY_MAP = {
    178: 'FA ADDED', 180: 'WAIVER ADDED', 179: 'DROPPED',
    181: 'DROPPED', 239: 'DROPPED', 244: 'TRADED',
    'FA': 178, 'WAIVER': 180, 'TRADED': 244
}

STATS_MAP = {
    # Offensive stats
    3: "passing_yds", 4: "passing_tds", 19: "passing_2_pts", 20: "passing_interceptions",
    24: "rushing_yds", 25: "rushing_tds", 26: "rushing_2_pts", 42: "receiving_yds",
    43: "receiving_tds", 44: "receiving_2_pts", 53: "receiving_receptions", 72: "lost_fumbles",
    # Kicking stats
    74: "made_fg_50_plus", 77: "made_fg_40_to_49", 80: "made_fg_under_40",
    85: "missed_fgs", 86: "made_pats", 88: "missed_pats",
    # Defensive stats
    89: "d_0_pts", 90: "d_1_to_6_pts", 91: "d_7_to_13_pts",
    92: "d_14_to_17_pts", 93: "d_blocked_kick_tds", 95: "d_interceptions",
    96: "d_fumbles", 97: "d_blocked_kicks", 98: "d_safeties",
    99: "d_sacks", 123: "d_28_to_34_pts", 124: "d_35_to_45_pts",
    129: "d_100_to_199_yds", 130: "d_200_to_299_yds", 131: "d_300_to_349_yds",
    132: "d_350_to_399_yds", 133: "d_400_to_449_yds", 134: "d_450_to_499_yds",
    135: "d_500_to_549_yds", 136: "d_over_550_yds",
    # Extra stats
    155: "TeamWin", 171: "20-24pointLossMargin", 172: "25+pointLossMargin",
}
