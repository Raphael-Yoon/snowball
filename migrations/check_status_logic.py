import sys
import os
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

print("=" * 60)
print("Status 로직 테스트")
print("=" * 60)

with get_db() as conn:
    # 모든 evaluation_header 데이터
    headers = conn.execute('''
        SELECT h.header_id, r.rcm_name, h.evaluation_name, h.status, h.progress
        FROM sb_evaluation_header h
        LEFT JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        WHERE r.control_category = 'ELC'
        ORDER BY h.header_id
    ''').fetchall()

    print("\n[ELC 평가 데이터]")
    for h in headers:
        h_dict = dict(h)
        status = h_dict['status']
        progress = h_dict['progress']

        # 표시 여부 판단
        show_in_design = status >= 0
        show_in_operation = status >= 2

        design_status = ""
        if show_in_design:
            if status >= 2:
                design_status = "완료(100%)"
            elif progress == 100:
                design_status = f"완료({progress}%)"
            else:
                design_status = f"진행중({progress}%)"

        operation_status = ""
        if show_in_operation:
            if status == 4:
                operation_status = f"완료({progress}%)"
            else:
                operation_status = f"진행중({progress}%)"

        print(f"\nID={h_dict['header_id']}, {h_dict['rcm_name']}")
        print(f"  세션명: {h_dict['evaluation_name']}")
        print(f"  status={status}, progress={progress}%")
        print(f"  설계평가 현황: {design_status if show_in_design else '표시 안됨'}")
        print(f"  운영평가 현황: {operation_status if show_in_operation else '표시 안됨'}")

print("\n" + "=" * 60)
print("로직 설명:")
print("  status 0-1: 설계평가만 표시")
print("  status 2-3: 설계평가(완료) + 운영평가(진행중) 표시")
print("  status 4: 설계평가(완료) + 운영평가(완료) 표시")
print("=" * 60)
