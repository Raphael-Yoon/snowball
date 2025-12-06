import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

# evaluation_action lookup 데이터 정의
# lookup_code는 evaluation_status 값 (0~5)
evaluation_actions = [
    ('0', '설계 시작', 'Start Design Evaluation'),
    ('1', '설계 계속', 'Continue Design Evaluation'),
    ('2', '설계 계속', 'Continue Design Evaluation'),
    ('3', '운영 시작', 'Start Operation Evaluation'),
    ('4', '운영 계속', 'Continue Operation Evaluation'),
    ('5', '설계 시작', 'Start Design Evaluation (New Cycle)')
]

with get_db() as conn:
    print("=== evaluation_action lookup 추가 ===")

    for lookup_code, lookup_name, description in evaluation_actions:
        # 이미 존재하는지 확인
        existing = conn.execute('''
            SELECT * FROM sb_lookup
            WHERE lookup_type = 'evaluation_action' AND lookup_code = ?
        ''', (lookup_code,)).fetchone()

        if existing:
            print(f"  이미 존재: {lookup_code} - {lookup_name}")
        else:
            conn.execute('''
                INSERT INTO sb_lookup (lookup_code, lookup_name, description, lookup_type)
                VALUES (?, ?, ?, 'evaluation_action')
            ''', (lookup_code, lookup_name, description))
            print(f"  추가: {lookup_code} - {lookup_name}")

    conn.commit()

    print("\n=== 추가된 evaluation_action lookup 확인 ===")
    result = conn.execute('''
        SELECT * FROM sb_lookup
        WHERE lookup_type = 'evaluation_action'
        ORDER BY lookup_code
    ''').fetchall()

    for r in result:
        print(f"  {dict(r)}")
