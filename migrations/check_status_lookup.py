import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    print("=== status/evaluation 관련 lookup ===")
    result = conn.execute('''
        SELECT * FROM sb_lookup
        WHERE lookup_type LIKE '%status%'
           OR lookup_type LIKE '%evaluation%'
    ''').fetchall()

    if result:
        for r in result:
            print(dict(r))
    else:
        print("status/evaluation 관련 lookup이 없습니다.")

    print("\n=== 모든 lookup_type 목록 ===")
    types = conn.execute('SELECT DISTINCT lookup_type FROM sb_lookup ORDER BY lookup_type').fetchall()
    for t in types:
        print(f"  - {t['lookup_type']}")
