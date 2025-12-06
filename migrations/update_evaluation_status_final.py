import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

# evaluation_status 최종 정의
# 0 - 설계 시작
# 1 - 설계 계속
# 2 - 운영 시작
# 3 - 운영 계속
# 4 - 완료

evaluation_statuses = [
    ('0', '설계 시작', 'Start Design Evaluation'),
    ('1', '설계 계속', 'Continue Design Evaluation'),
    ('2', '운영 시작', 'Start Operation Evaluation'),
    ('3', '운영 계속', 'Continue Operation Evaluation'),
    ('4', '완료', 'Completed')
]

with get_db() as conn:
    print("=== 기존 evaluation_status 삭제 ===")
    conn.execute("DELETE FROM sb_lookup WHERE lookup_type = 'evaluation_status'")

    print("\n=== 새로운 evaluation_status 추가 ===")
    for lookup_code, lookup_name, description in evaluation_statuses:
        conn.execute('''
            INSERT INTO sb_lookup (lookup_code, lookup_name, description, lookup_type)
            VALUES (?, ?, ?, 'evaluation_status')
        ''', (lookup_code, lookup_name, description))
        print(f"  추가: {lookup_code} - {lookup_name}")

    conn.commit()

    print("\n=== 업데이트된 evaluation_status 확인 ===")
    result = conn.execute('''
        SELECT * FROM sb_lookup
        WHERE lookup_type = 'evaluation_status'
        ORDER BY lookup_code
    ''').fetchall()

    for r in result:
        print(f"  {dict(r)}")
