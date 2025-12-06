import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    # status 5 추가 (운영평가 완료 후 새 사이클 시작)
    existing = conn.execute('''
        SELECT * FROM sb_lookup
        WHERE lookup_type = 'evaluation_status' AND lookup_code = '5'
    ''').fetchone()

    if existing:
        print("Status 5가 이미 존재합니다.")
    else:
        conn.execute('''
            INSERT INTO sb_lookup (lookup_code, lookup_name, description, lookup_type)
            VALUES ('5', '설계 시작', 'Start Design Evaluation (New Cycle)', 'evaluation_status')
        ''')
        conn.commit()
        print("Status 5 추가 완료: 설계 시작 (새 사이클)")

    print("\n=== 전체 evaluation_status 확인 ===")
    result = conn.execute('''
        SELECT * FROM sb_lookup
        WHERE lookup_type = 'evaluation_status'
        ORDER BY lookup_code
    ''').fetchall()

    for r in result:
        print(f"  {dict(r)}")
