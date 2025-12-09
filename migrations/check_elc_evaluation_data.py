import sys
import os
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

print("=" * 60)
print("ELC 평가 데이터 확인")
print("=" * 60)

with get_db() as conn:
    # sb_evaluation_header 전체 데이터 확인
    print("\n[1] sb_evaluation_header 전체 데이터")
    headers = conn.execute('''
        SELECT h.header_id, h.rcm_id, r.rcm_name, h.evaluation_name, h.status, h.progress, h.created_at
        FROM sb_evaluation_header h
        LEFT JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        ORDER BY h.header_id
    ''').fetchall()

    for h in headers:
        h_dict = dict(h)
        print(f"  ID={h_dict['header_id']}, RCM={h_dict['rcm_name']}, "
              f"세션={h_dict['evaluation_name']}, status={h_dict['status']}, "
              f"progress={h_dict['progress']}%")

    # ELC RCM 확인
    print("\n[2] ELC RCM 목록")
    rcms = conn.execute('''
        SELECT rcm_id, rcm_name, control_category
        FROM sb_rcm
        WHERE control_category = 'ELC'
    ''').fetchall()

    for r in rcms:
        r_dict = dict(r)
        print(f"  RCM ID={r_dict['rcm_id']}, Name={r_dict['rcm_name']}")

    # 특정 RCM의 평가 현황 확인
    if rcms:
        test_rcm_id = dict(rcms[0])['rcm_id']
        print(f"\n[3] RCM ID={test_rcm_id}의 평가 현황")

        # 설계평가 (status 0-1)
        design = conn.execute('''
            SELECT evaluation_name, status, progress
            FROM sb_evaluation_header
            WHERE rcm_id = %s AND status >= 0 AND status <= 1
            ORDER BY last_updated DESC
        ''', (test_rcm_id,)).fetchall()

        print(f"  설계평가 세션: {len(design)}개")
        for d in design:
            d_dict = dict(d)
            print(f"    - {d_dict['evaluation_name']}: status={d_dict['status']}, progress={d_dict['progress']}%")

        # 운영평가 (status >= 2)
        operation = conn.execute('''
            SELECT evaluation_name, status, progress
            FROM sb_evaluation_header
            WHERE rcm_id = %s AND status >= 2
            ORDER BY last_updated DESC
        ''', (test_rcm_id,)).fetchall()

        print(f"  운영평가 세션: {len(operation)}개")
        for o in operation:
            o_dict = dict(o)
            print(f"    - {o_dict['evaluation_name']}: status={o_dict['status']}, progress={o_dict['progress']}%")

print("\n" + "=" * 60)
