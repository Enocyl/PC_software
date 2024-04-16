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
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches 
                      (match_id INTEGER PRIMARY KEY, home_team TEXT, away_team TEXT, score TEXT)''')

# 插入数据
def insert_data(cursor, data):
    for country, country_data in data.items():
        for season, season_data in country_data.items():
            for league, league_data in season_data.items():
                for round_name, matches in league_data.items():
                    for match in matches:
                        cursor.execute("INSERT INTO matches (match_id, home_team, away_team, score) VALUES (?, ?, ?, ?)",
                                       (match['match_id'], match['home_team'], match['away_team'], match['score']))

# 按指定条件查询数据
def query_matches_by_criteria(cursor, country=None, season=None, league=None, round_name=None, match_id=None):
    query = "SELECT * FROM matches"
    conditions = []
    params = []
    if country:
        conditions.append("match_id IN (SELECT match_id FROM matches WHERE round_name IN (SELECT round_name FROM rounds WHERE league_name IN (SELECT league_name FROM leagues WHERE season_name IN (SELECT season_name FROM seasons WHERE country_name = ?))))")
        params.append(country)
    if season:
        conditions.append("match_id IN (SELECT match_id FROM matches WHERE round_name IN (SELECT round_name FROM rounds WHERE league_name IN (SELECT league_name FROM leagues WHERE season_name = ?)))")
        params.append(season)
    if league:
        conditions.append("match_id IN (SELECT match_id FROM matches WHERE round_name IN (SELECT round_name FROM rounds WHERE league_name = ?))")
        params.append(league)
    if round_name:
        conditions.append("match_id IN (SELECT match_id FROM matches WHERE round_name = ?)")
        params.append(round_name)
    if match_id:
        conditions.append("match_id = ?")
        params.append(match_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    cursor.execute(query, params)
    return cursor.fetchall()

# 创建表格
create_tables(cursor)

# 插入数据
insert_data(cursor, football_match_data)

# 提交事务
conn.commit()

# 查询示例
result = query_matches_by_criteria(cursor, country='England', season='2023-2024', league='Premier League', round_name='Round 1', match_id=1)
print(result)

# 关闭连接
conn.close()
