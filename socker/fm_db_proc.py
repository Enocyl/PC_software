import sqlite3

# 数据
football_match_data = {
    'England': {
        '2023-2024': {
            'Premier League': {
                'Round 1': [
                    {'match_id': 1, 'home_team': 'Arsenal', 'away_team': 'Chelsea', 'score': '3-1'},
                    {'match_id': 2, 'home_team': 'Manchester United', 'away_team': 'Liverpool', 'score': '2-2'}
                ],
                'Round 2': [
                    {'match_id': 3, 'home_team': 'Chelsea', 'away_team': 'Manchester United', 'score': '1-0'},
                    {'match_id': 4, 'home_team': 'Liverpool', 'away_team': 'Arsenal', 'score': '0-2'}
                ]
            }
        }
    },
    'Spain': {
        '2023-2024': {
            'La Liga': {
                'Round 1': [
                    {'match_id': 5, 'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'score': '2-1'},
                    {'match_id': 6, 'home_team': 'Atletico Madrid', 'away_team': 'Sevilla', 'score': '3-0'}
                ],
                'Round 2': [
                    {'match_id': 7, 'home_team': 'Barcelona', 'away_team': 'Atletico Madrid', 'score': '2-2'},
                    {'match_id': 8, 'home_team': 'Sevilla', 'away_team': 'Real Madrid', 'score': '1-3'}
                ]
            }
        }
    }
}

# 创建数据库连接
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 创建表格
def create_tables(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS countries 
                      (country_id INTEGER PRIMARY KEY, country_name TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS seasons 
                      (season_id INTEGER PRIMARY KEY, season_name TEXT, country_id INTEGER,
                       FOREIGN KEY(country_id) REFERENCES countries(country_id),
                       UNIQUE(season_name, country_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS leagues 
                      (league_id INTEGER PRIMARY KEY, league_name TEXT, season_id INTEGER,
                       FOREIGN KEY(season_id) REFERENCES seasons(season_id),
                       UNIQUE(league_name, season_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rounds 
                      (round_id INTEGER PRIMARY KEY, round_name TEXT, league_id INTEGER,
                       FOREIGN KEY(league_id) REFERENCES leagues(league_id),
                       UNIQUE(round_name, league_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches 
                      (match_id INTEGER PRIMARY KEY, round_id INTEGER, home_team TEXT, away_team TEXT, score TEXT,
                       FOREIGN KEY(round_id) REFERENCES rounds(round_id),
                       UNIQUE(round_id, home_team, away_team))''')

# 插入数据
def insert_data(cursor, data):
    for country, country_data in data.items():
        country_id = insert_country(cursor, country)
        for season, season_data in country_data.items():
            season_id = insert_season(cursor, season, country_id)
            for league, league_data in season_data.items():
                league_id = insert_league(cursor, league, season_id)
                for round_name, matches in league_data.items():
                    round_id = insert_round(cursor, round_name, league_id)
                    for match in matches:
                        insert_match(cursor, match['match_id'], round_id, match['home_team'], match['away_team'], match['score'])

# 插入国家数据
def insert_country(cursor, country_name):
    cursor.execute("INSERT OR IGNORE INTO countries (country_name) VALUES (?)", (country_name,))
    cursor.execute("SELECT country_id FROM countries WHERE country_name = ?", (country_name,))
    return cursor.fetchone()[0]

# 插入赛季数据
def insert_season(cursor, season_name, country_id):
    cursor.execute("INSERT OR IGNORE INTO seasons (season_name, country_id) VALUES (?, ?)", (season_name, country_id))
    cursor.execute("SELECT season_id FROM seasons WHERE season_name = ? AND country_id = ?", (season_name, country_id))
    return cursor.fetchone()[0]

# 插入联赛数据
def insert_league(cursor, league_name, season_id):
    cursor.execute("INSERT OR IGNORE INTO leagues (league_name, season_id) VALUES (?, ?)", (league_name, season_id))
    cursor.execute("SELECT league_id FROM leagues WHERE league_name = ? AND season_id = ?", (league_name, season_id))
    return cursor.fetchone()[0]

# 插入轮次数据
def insert_round(cursor, round_name, league_id):
    cursor.execute("INSERT OR IGNORE INTO rounds (round_name, league_id) VALUES (?, ?)", (round_name, league_id))
    cursor.execute("SELECT round_id FROM rounds WHERE round_name = ? AND league_id = ?", (round_name, league_id))
    return cursor.fetchone()[0]

# 插入比赛数据
def insert_match(cursor, match_id, round_id, home_team, away_team, score):
    cursor.execute("INSERT OR IGNORE INTO matches (match_id, round_id, home_team, away_team, score) VALUES (?, ?, ?, ?, ?)",
                   (match_id, round_id, home_team, away_team, score))

def query_countries(cursor):
    #cursor.execute('''SELECT season_id FROM seasons
    cursor.execute('''SELECT * FROM countries ''')
    return cursor.fetchall()

# 根据国家查询赛季
def query_seasons_by_country(cursor, country_name):
    #cursor.execute('''SELECT season_id FROM seasons
    cursor.execute('''SELECT * FROM seasons 
                      WHERE country_id = (SELECT country_id FROM countries WHERE country_name = ?)''', (country_name,))
    return cursor.fetchall()

# 根据赛季查询联赛
def query_leagues_by_season(cursor, season_id):
    cursor.execute('''SELECT league_id FROM leagues 
                      WHERE season_id = ?''', (season_id,))
    return cursor.fetchall()

# 根据联赛查询轮次
def query_rounds_by_league(cursor, league_id):
    cursor.execute('''SELECT round_id FROM rounds 
                      WHERE league_id = ?''', (league_id,))
    return cursor.fetchall()

# 根据轮次查询比赛
def query_matches_by_round(cursor, round_id):
    cursor.execute('''SELECT match_id FROM matches 
                      WHERE round_id = ?''', (round_id,))
    return cursor.fetchall()

# 查询比赛信息
def query_match_info(cursor, match_id):
    cursor.execute('''SELECT * FROM matches 
                      WHERE match_id = ?''', (match_id,))
    return cursor.fetchone()

def query_match_ids(cursor, country_name, season_name, league_name, round_name):
    # 查询国家ID
    cursor.execute("SELECT country_id FROM countries WHERE country_name = ?", (country_name,))
    country_id = cursor.fetchone()[0]

    # 查询赛季ID
    cursor.execute("SELECT season_id FROM seasons WHERE season_name = ? AND country_id = ?", (season_name, country_id))
    season_id = cursor.fetchone()[0]

    # 查询联赛ID
    cursor.execute("SELECT league_id FROM leagues WHERE league_name = ? AND season_id = ?", (league_name, season_id))
    league_id = cursor.fetchone()[0]

    # 查询轮次ID
    cursor.execute("SELECT round_id FROM rounds WHERE round_name = ? AND league_id = ?", (round_name, league_id))
    round_id = cursor.fetchone()[0]

    # 查询比赛信息
    match_ids = query_matches_by_round(cursor, round_id)
    return match_ids

def query_match_data_by_hierarchy(cursor, country_name, season_name, league_name, round_name, match_id):
    # 查询国家ID
    cursor.execute("SELECT country_id FROM countries WHERE country_name = ?", (country_name,))
    country_id = cursor.fetchone()[0]

    # 查询赛季ID
    cursor.execute("SELECT season_id FROM seasons WHERE season_name = ? AND country_id = ?", (season_name, country_id))
    season_id = cursor.fetchone()[0]

    # 查询联赛ID
    cursor.execute("SELECT league_id FROM leagues WHERE league_name = ? AND season_id = ?", (league_name, season_id))
    league_id = cursor.fetchone()[0]

    # 查询轮次ID
    cursor.execute("SELECT round_id FROM rounds WHERE round_name = ? AND league_id = ?", (round_name, league_id))
    round_id = cursor.fetchone()[0]

    # 查询比赛信息
    match_info = query_match_info(cursor, match_id)
    return match_info

# 创建表格
create_tables(cursor)

# 插入数据
insert_data(cursor, football_match_data)

# 提交事务
conn.commit()


country_info = query_countries(cursor)
print(country_info)

season_info = query_seasons_by_country(cursor, 'England')
print(season_info)

match_ids = query_match_ids(cursor, 'England', '2023-2024', 'Premier League', 'Round 2')
print(match_ids)

match_info = query_match_data_by_hierarchy(cursor, 'England', '2023-2024', 'Premier League', 'Round 1', match_ids[1][0])
print(match_info)

# 关闭连接
conn.close()
