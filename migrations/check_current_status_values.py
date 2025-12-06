import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    print("=== sb_evaluation_header의 status 값 ===")
    result = conn.execute('SELECT DISTINCT status FROM sb_evaluation_header ORDER BY status').fetchall()
    for r in result:
        print(f"  - {r['status']}")

    print("\n=== 각 평가 세션별 상세 정보 ===")
    headers = conn.execute('''
        SELECT rcm_id, evaluation_session, status, progress
        FROM sb_evaluation_header
        ORDER BY rcm_id, evaluation_session
    ''').fetchall()
    for h in headers:
        print(f"  RCM {h['rcm_id']}: {h['evaluation_session']} - {h['status']} ({h['progress']}%)")
