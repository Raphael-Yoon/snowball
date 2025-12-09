"""
Test script to verify design evaluation save functionality
"""
import sys
import os
project_root = os.path.join(os.path.dirname(__file__), '.')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db
from auth import save_design_evaluation

print("=" * 60)
print("설계평가 저장 테스트")
print("=" * 60)

# Test data
rcm_id = 1  # 법인세시스템_ELC
control_code = 'APD01'  # Valid control code
user_id = 1  # Not used anymore but parameter still exists
evaluation_session = 'FY25_테스트평가'

evaluation_data = {
    'description_adequacy': '통제 설명 적정',
    'improvement_suggestion': '',
    'overall_effectiveness': '적정',  # This is the key field!
    'evaluation_rationale': '테스트 평가 근거',
    'design_comment': '테스트 코멘트',
    'recommended_actions': '',
    'no_occurrence': False,
    'no_occurrence_reason': '',
    'evaluation_evidence': ''
}

try:
    print(f"\n저장 시도: rcm_id={rcm_id}, control_code={control_code}, session={evaluation_session}")
    save_design_evaluation(rcm_id, control_code, user_id, evaluation_data, evaluation_session)
    print("[OK] 저장 성공!")

    # Verify the save
    with get_db() as conn:
        # Find the header
        header = conn.execute('''
            SELECT header_id FROM sb_evaluation_header
            WHERE rcm_id = ? AND evaluation_name = ?
        ''', (rcm_id, evaluation_session)).fetchone()

        if header:
            header_id = header['header_id']
            print(f"[OK] Header found: header_id={header_id}")

            # Find the line
            line = conn.execute('''
                SELECT line_id, overall_effectiveness, evaluation_rationale
                FROM sb_evaluation_line
                WHERE header_id = ? AND control_code = ?
            ''', (header_id, control_code)).fetchone()

            if line:
                line_dict = dict(line)
                print(f"[OK] Line found: line_id={line_dict['line_id']}")
                print(f"     overall_effectiveness: {line_dict['overall_effectiveness']}")
                print(f"     evaluation_rationale: {line_dict['evaluation_rationale']}")
            else:
                print("[ERROR] Line not found!")
        else:
            print("[ERROR] Header not found!")

except Exception as e:
    print(f"[ERROR] 저장 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
