import sqlite3

conn = sqlite3.connect('c:/Python/snowball/snowball.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Checking 'created_at' defaults:")
for (table_name,) in tables:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        if 'created_at' in col[1]:
            print(f"Table: {table_name}, Column: {col[1]}, Default: {col[4]}")

conn.close()
