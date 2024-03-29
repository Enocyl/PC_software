import sqlite3

football_match_data = {
    'England': {
        '2023-2024': {
            'Premier League': {
                'Round 1': [
                    {'home_team': 'Arsenal', 'away_team': 'Chelsea', 'score': '3-1'},
                    {'home_team': 'Manchester United', 'away_team': 'Liverpool', 'score': '2-2'}
                ],
                'Round 2': [
                    {'home_team': 'Chelsea', 'away_team': 'Manchester United', 'score': '1-0'},
                    {'home_team': 'Liverpool', 'away_team': 'Arsenal', 'score': '0-2'}
                ]
            }
        }
    },
    'Spain': {
        '2023-2024': {
            'La Liga': {
                'Round 1': [
                    {'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'score': '2-1'},
                    {'home_team': 'Atletico Madrid', 'away_team': 'Sevilla', 'score': '3-0'}
                ],
                'Round 2': [
                    {'home_team': 'Barcelona', 'away_team': 'Atletico Madrid', 'score': '2-2'},
                    {'home_team': 'Sevilla', 'away_team': 'Real Madrid', 'score': '1-3'}
                ]
            }
        }
    }
}

def create_tables(cursor):
    """创建数据库表格"""
    cursor.execute('''CREATE TABLE IF NOT EXISTS countries 
                      (country_name TEXT PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS seasons 
                      (season_name TEXT PRIMARY KEY, country_name TEXT,
                       FOREIGN KEY(country_name) REFERENCES countries(country_name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS leagues 
                      (league_name TEXT PRIMARY KEY, season_name TEXT,
                       FOREIGN KEY(season_name) REFERENCES seasons(season_name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rounds 
                      (round_name TEXT PRIMARY KEY, league_name TEXT,
                       FOREIGN KEY(league_name) REFERENCES leagues(league_name))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches 
                          (match_id INTEGER PRIMARY KEY AUTOINCREMENT, round_name TEXT, home_team TEXT, away_team TEXT, score TEXT,
                           FOREIGN KEY(round_name) REFERENCES rounds(round_name))''')

def insert_data(cursor, data):
    #for country, seasons in data.items():
    #    cursor.execute("INSERT INTO countries VALUES (?)", (country,))
    #    cursor.execute("SELECT last_insert_rowid()")
    #    parent_id = cursor.fetchone()[0]
    #    insert_football_data(cursor, parent_id, seasons)
    create_countries_query = "INSERT INTO countries VALUES (?)"
    for country, seasons in football_match_data.items():
        cursor.execute(create_countries_query, (country,))
        cursor.execute("SELECT last_insert_rowid()")
        country_id = cursor.fetchone()[0]
        for season, leagues in seasons.items():
            cursor.execute("INSERT INTO seasons VALUES (?, ?)", (country_id, season))
            cursor.execute("SELECT last_insert_rowid()")
            season_id = cursor.fetchone()[0]
            for league, rounds in leagues.items():
                cursor.execute("INSERT INTO leagues VALUES (?, ?)", (season_id, league))
                cursor.execute("SELECT last_insert_rowid()")
                league_id = cursor.fetchone()[0]
                for round_name, matches in rounds.items():
                    cursor.execute("INSERT INTO rounds VALUES (?, ?)", (league_id, round_name))
                    cursor.execute("SELECT last_insert_rowid()")
                    round_id = cursor.fetchone()[0]
                    for match_data in matches:
                        cursor.execute("INSERT INTO matches VALUES (Null, ?, ?, ?, ?)",
                                       (
                                       round_id, match_data['home_team'], match_data['away_team'], match_data['score']))

def insert_football_data(cursor, parent_id, data):
    """递归插入足球数据"""
    for key, value in data.items():
        # 插入当前层级的数据
        if isinstance(value, dict):
            # 插入当前层级数据，并获取插入后的ID
            cursor.execute("INSERT INTO {} VALUES (?)".format(key.lower().replace(' ', '_') + 's'), (key,))
            cursor.execute("SELECT last_insert_rowid()")
            row_id = cursor.fetchone()[0]
            # 递归插入下一层级数据
            insert_football_data(cursor, row_id, value)
        elif isinstance(value, list):
            # 处理最底层的数据（比赛数据）
            for match_data in value:
                cursor.execute("INSERT INTO matches VALUES (NULL, ?, ?, ?, ?)",
                               (key, match_data['home_team'], match_data['away_team'], match_data['score']))

# 初始化连接和游标
conn = sqlite3.connect('football.db')
cursor = conn.cursor()

# 创建表格
create_tables(cursor)

# 插入足球比赛数据
#insert_football_data(cursor, None, football_match_data)
insert_data(cursor, football_match_data)

# 提交事务
conn.commit()

# 查询操作示例
cursor.execute("SELECT * FROM countries")
print("Countries:")
print(cursor.fetchall())

cursor.execute("SELECT * FROM seasons")
print("\nSeasons:")
print(cursor.fetchall())

cursor.execute("SELECT * FROM leagues")
print("\nLeagues:")
print(cursor.fetchall())

cursor.execute("SELECT * FROM rounds")
print("\nRounds:")
print(cursor.fetchall())

cursor.execute("SELECT * FROM matches")
print("\nMatches:")
print(cursor.fetchall())

# 关闭连接
conn.close()
