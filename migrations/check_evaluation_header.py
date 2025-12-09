import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    # sb_evaluation_header 테이블 확인
    try:
        result = conn.execute('PRAGMA table_info(sb_evaluation_header)').fetchall()
        if result:
            print("=== sb_evaluation_header 테이블 존재 ===")
            for r in result:
                print(dict(r))
        else:
            print("sb_evaluation_header 테이블이 존재하지 않습니다.")
    except Exception as e:
        print(f"오류: {e}")
        print("sb_evaluation_header 테이블이 존재하지 않습니다.")
