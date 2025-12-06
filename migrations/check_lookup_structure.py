import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    print("=== sb_lookup 테이블 구조 ===")
    result = conn.execute('PRAGMA table_info(sb_lookup)').fetchall()
    for r in result:
        print(dict(r))

    print("\n=== sb_lookup 테이블 내용 샘플 ===")
    samples = conn.execute('SELECT * FROM sb_lookup LIMIT 10').fetchall()
    for s in samples:
        print(dict(s))
