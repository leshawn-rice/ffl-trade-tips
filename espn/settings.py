STANDARD_SEASON_LENGTH = 13

POSITION_MAP = {
    0: 'QB', 1: 'QB', 2: 'RB', 3: 'WR', 4: 'WR', 5: 'K',
    6: 'TE', 7: 'OP', 8: 'DT', 9: 'DE', 10: 'LB', 11: 'DL',
    12: 'CB', 13: 'S', 14: 'DB', 15: 'DP', 16: 'D/ST', 17: 'K',
    25: 'Rookie'
}

GRADE_MAP = {
    'A': ('A', 'B'),
    'B': ('A', 'B', 'C'),
    'C': ('B', 'C', 'D'),
    'D': ('C', 'D' 'F'),
    'F': ('D', 'F')
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
    3: 'Passing Yards', 4: 'Passing Touchdowns', 19: 'Passing 2 PT Conversions', 20: 'Passing Interceptions',
    24: 'Rushing Yards', 25: 'Rushing Touchdowns', 26: 'Rushing 2 PT Conversions', 42: 'Lost Fumbles',
    43: 'Receiving Touchdowns', 44: 'Receiving 2 PT Conversions', 53: 'Receiving Receptions', 72: 'Lost Fumbles',
    # Kicking stats
    74: 'Made FGs From over 50 Yds', 77: 'Made FGs From 40-49 Yards', 80: 'Made FGs Under 40 Yards',
    85: 'Missed FGs', 86: 'Made PATs', 88: 'Missed PATs',
    # Defensive stats
    89: 'Allowed 0 Points', 90: 'Allowed 1-6 Points', 91: 'Allowed 7-13 Points',
    92: 'Allowed 14-17 Points', 93: 'Defensive Blocked PATs', 95: 'Defensive Interceptions',
    96: 'Defensive Fumbles', 97: 'Defensive Blocked Kicks', 98: 'Defensive Safeties',
    99: 'Defensive Sacks', 123: 'Allowed 28-34 Points', 124: 'Allowed 35-45 Points',
    129: 'Allowed 100-199 Yards', 130: 'Allowed 200-299 Yards', 131: 'Allowed 300-349 Yards',
    132: 'Allowed 350-399 Yards', 133: 'Allowed 400-449 Yards', 134: 'Allowed 450-499 Yards',
    135: 'Allowed 500-549 Yards', 136: 'Allowed Over 500 Yards',
    # Extra stats
    155: 'TeamWin', 171: '20-24pointLossMargin', 172: '25+pointLossMargin',
}
