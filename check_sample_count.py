import sys
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db

# 현재 통제의 샘플 개수 확인
with get_db() as conn:
    # FY25_내부평가 세션의 C-EL-CA-10-01 통제 찾기
    line = conn.execute('''
        SELECT l.line_id, l.control_code, l.sample_size
        FROM sb_evaluation_line l
        JOIN sb_evaluation_header h ON l.header_id = h.header_id
        WHERE h.evaluation_name = 'FY25_내부평가'
          AND h.rcm_id = 18
          AND l.control_code = 'C-EL-CA-10-01'
    ''').fetchone()

    if line:
        ld = dict(line)
        print(f"통제: {ld['control_code']}")
        print(f"표본 크기 (sample_size): {ld['sample_size']}")

        # 실제 저장된 샘플 개수 확인
        samples = conn.execute('''
            SELECT COUNT(*) as count
            FROM sb_evaluation_sample
            WHERE line_id = ? AND evaluation_type = 'operation'
        ''', (ld['line_id'],)).fetchone()

        print(f"저장된 운영평가 샘플 개수: {dict(samples)['count']}")

        # 각 샘플 상세 정보
        samples_detail = conn.execute('''
            SELECT sample_number, evidence, has_exception
            FROM sb_evaluation_sample
            WHERE line_id = ? AND evaluation_type = 'operation'
            ORDER BY sample_number
        ''', (ld['line_id'],)).fetchall()

        print(f"\n샘플 상세:")
        for s in samples_detail:
            sd = dict(s)
            print(f"  #{sd['sample_number']}: has_exception={sd['has_exception']}, evidence={sd['evidence'][:50] if sd['evidence'] else 'None'}...")
    else:
        print("통제를 찾을 수 없습니다!")
