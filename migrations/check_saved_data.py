import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db
import json

with get_db() as conn:
    # line_id=521 데이터 확인
    result = conn.execute('''
        SELECT l.*, h.evaluation_session, h.design_evaluation_session, h.rcm_id, h.user_id
        FROM sb_operation_evaluation_line l
        JOIN sb_operation_evaluation_header h ON l.header_id = h.header_id
        WHERE l.line_id = 521
    ''').fetchone()

    if result:
        data = dict(result)
        print("=== line_id=521 데이터 ===")
        print(f"control_code: {data.get('control_code')}")
        print(f"conclusion: {data.get('conclusion')[:100] if data.get('conclusion') else 'None'}")
        print(f"sample_size: {data.get('sample_size')}")
        print(f"rcm_id: {data.get('rcm_id')}")
        print(f"user_id: {data.get('user_id')}")
        print(f"evaluation_session: {data.get('evaluation_session')}")
        print(f"design_evaluation_session: {data.get('design_evaluation_session')}")
        print(f"header_id: {data.get('header_id')}")
    else:
        print("line_id=521 데이터를 찾을 수 없습니다.")

    # APD06 통제 모든 데이터 확인
    print("\n=== control_code=APD06 모든 데이터 ===")
    results = conn.execute('''
        SELECT l.line_id, l.control_code, l.conclusion, l.sample_size,
               h.evaluation_session, h.design_evaluation_session, h.rcm_id, h.user_id
        FROM sb_operation_evaluation_line l
        JOIN sb_operation_evaluation_header h ON l.header_id = h.header_id
        WHERE l.control_code = 'APD06' AND h.rcm_id = 2
        ORDER BY l.line_id DESC
    ''').fetchall()

    for row in results:
        data = dict(row)
        print(f"line_id={data['line_id']}, eval_session={data['evaluation_session']}, design_session={data['design_evaluation_session']}, conclusion={data.get('conclusion')[:50] if data.get('conclusion') else 'None'}")
