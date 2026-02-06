from auth import get_db
with get_db() as conn:
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'sb_%'").fetchall()
    relevant_tables = [t['name'] for t in tables if 'rcm' in t['name'] or 'evaluation' in t['name']]
    for table in relevant_tables:
        print(table)
