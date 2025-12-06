import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

# evaluation_status lookup 데이터 정의
evaluation_statuses = [
    ('NOT_STARTED', '미시작', 'Not Started'),
    ('IN_PROGRESS', '진행중', 'In Progress'),
    ('COMPLETED', '완료', 'Completed'),
    ('ARCHIVED', '보관됨', 'Archived')
]

with get_db() as conn:
    print("=== evaluation_status lookup 추가 ===")

    for lookup_code, lookup_name, description in evaluation_statuses:
        # 이미 존재하는지 확인
        existing = conn.execute('''
            SELECT * FROM sb_lookup
            WHERE lookup_type = 'evaluation_status' AND lookup_code = ?
        ''', (lookup_code,)).fetchone()

        if existing:
            print(f"  이미 존재: {lookup_code} - {lookup_name}")
        else:
            conn.execute('''
                INSERT INTO sb_lookup (lookup_code, lookup_name, description, lookup_type)
                VALUES (?, ?, ?, 'evaluation_status')
            ''', (lookup_code, lookup_name, description))
            print(f"  추가: {lookup_code} - {lookup_name}")

    conn.commit()

    print("\n=== 추가된 evaluation_status lookup 확인 ===")
    result = conn.execute('''
        SELECT * FROM sb_lookup
        WHERE lookup_type = 'evaluation_status'
        ORDER BY lookup_code
    ''').fetchall()

    for r in result:
        print(f"  {dict(r)}")
