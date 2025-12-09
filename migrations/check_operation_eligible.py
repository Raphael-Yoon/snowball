import sys
import os
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db
from evaluation_utils import get_evaluation_status

print("=" * 60)
print("운영평가 대상 통제 확인")
print("=" * 60)

with get_db() as conn:
    # 모든 evaluation_header 조회
    headers = conn.execute('''
        SELECT h.header_id, h.evaluation_name, r.rcm_name
        FROM sb_evaluation_header h
        LEFT JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        WHERE r.control_category = 'ELC'
        ORDER BY h.header_id
    ''').fetchall()

    for h in headers:
        h_dict = dict(h)
        header_id = h_dict['header_id']

        print(f"\n[{h_dict['rcm_name']} - {h_dict['evaluation_name']}]")

        # 상태 정보 조회
        status_info = get_evaluation_status(conn, header_id)

        print(f"  Status: {status_info['status']}")
        print(f"  설계평가: {status_info['design_completed_count']}/{status_info['design_total_count']} ({status_info['design_progress']}%)")
        print(f"  운영평가 대상: {status_info['operation_total_count']}개")
        print(f"  운영평가 완료: {status_info['operation_completed_count']}개 ({status_info['operation_progress']}%)")

        # 설계평가 결과 확인
        lines = conn.execute('''
            SELECT control_code, overall_effectiveness
            FROM sb_evaluation_line
            WHERE header_id = ?
        ''', (header_id,)).fetchall()

        proper_count = 0
        for line in lines:
            line_dict = dict(line)
            if line_dict['overall_effectiveness'] == '적정':
                proper_count += 1

        print(f"  '적정' 판정: {proper_count}개")

        if proper_count == 0 and status_info['design_completed_count'] > 0:
            print("  [경고] 설계평가가 완료되었지만 '적정' 판정이 없어 운영평가를 시작할 수 없습니다!")

print("\n" + "=" * 60)
