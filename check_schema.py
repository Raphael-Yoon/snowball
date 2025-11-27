"""Check the schema of sb_rcm table"""
import sqlite3

conn = sqlite3.connect('snowball.db')
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(sb_rcm)")
columns = cursor.fetchall()

print("sb_rcm Table Structure:")
print("=" * 60)
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Get a sample row
cursor.execute("SELECT * FROM sb_rcm LIMIT 1")
row = cursor.fetchone()

if row:
    print("\nSample row:")
    for i, col in enumerate(columns):
        print(f"  {col[1]}: {row[i]}")

conn.close()
