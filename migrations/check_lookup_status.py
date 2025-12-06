import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    print("=== sb_lookup 테이블에서 evaluation_status 확인 ===")
    result = conn.execute('SELECT * FROM sb_lookup WHERE category = ?', ('evaluation_status',)).fetchall()
    if result:
        for r in result:
            print(dict(r))
    else:
        print("evaluation_status 카테고리가 없습니다.")

    print("\n=== sb_lookup 테이블의 모든 카테고리 ===")
    categories = conn.execute('SELECT DISTINCT category FROM sb_lookup ORDER BY category').fetchall()
    for cat in categories:
        print(cat['category'])
