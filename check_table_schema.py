import sys
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db

with get_db() as conn:
    result = conn.execute('PRAGMA table_info(sb_evaluation_line)').fetchall()
    print("sb_evaluation_line 테이블 컬럼:")
    for r in result:
        rd = dict(r)
        print(f"  {rd['name']} ({rd['type']})")
