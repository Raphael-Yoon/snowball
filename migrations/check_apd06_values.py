import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    # APD06 설계평가 데이터 확인
    result = conn.execute('''
        SELECT l.control_code, l.evaluation_evidence
        FROM sb_design_evaluation_line l
        JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
        WHERE h.rcm_id = 2 AND h.evaluation_session = 'FY25_설계평가2차' AND l.control_code = 'APD06'
    ''').fetchone()

    if result:
        import json
        data = dict(result)
        print("=== APD06 설계평가 데이터 ===")
        print(f"control_code: {data['control_code']}")
        if data['evaluation_evidence']:
            evidence = json.loads(data['evaluation_evidence'])
            print("evaluation_evidence:")
            for key, value in evidence.items():
                print(f"  {key}: {value}")
    else:
        print("APD06 설계평가 데이터를 찾을 수 없습니다.")
