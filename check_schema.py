import sqlite3
db_path = 'c:/Python/snowball/snowball.db'
conn = sqlite3.connect(db_path)
cursor = conn.execute("PRAGMA table_info(sb_internal_assessment)")
for row in cursor.fetchall():
    print(row[1])
conn.close()
