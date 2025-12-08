import sys
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db

print("=" * 60)
print("운영평가 저장 데이터 확인")
print("=" * 60)

with get_db() as conn:
    # 1. FY25_내부평가 헤더 확인
    header = conn.execute('''
        SELECT header_id, rcm_id, evaluation_name, status, last_updated
        FROM sb_evaluation_header
        WHERE evaluation_name = 'FY25_내부평가' AND rcm_id = 18
    ''').fetchone()

    if not header:
        print("헤더를 찾을 수 없습니다!")
        exit(1)

    hd = dict(header)
    print(f"\n[헤더] header_id={hd['header_id']}, status={hd['status']}, last_updated={hd['last_updated']}")

    # 2. C-EL-CA-10-01 통제의 라인 데이터 확인
    line = conn.execute('''
        SELECT line_id, control_code,
               overall_effectiveness,
               sample_size, exception_count, conclusion,
               mitigating_factors, exception_details,
               last_updated
        FROM sb_evaluation_line
        WHERE header_id = ? AND control_code = 'C-EL-CA-10-01'
    ''', (hd['header_id'],)).fetchone()

    if not line:
        print("라인을 찾을 수 없습니다!")
        exit(1)

    ld = dict(line)
    print(f"\n[라인] line_id={ld['line_id']}")
    print(f"  설계평가: overall_effectiveness={ld['overall_effectiveness']}")
    print(f"  운영평가: sample_size={ld['sample_size']}, exception_count={ld['exception_count']}")
    print(f"           conclusion={ld['conclusion']}")
    print(f"           mitigating_factors={ld['mitigating_factors']}")
    print(f"           exception_details={ld['exception_details']}")
    print(f"  last_updated={ld['last_updated']}")

    # 3. 샘플 데이터 확인
    samples = conn.execute('''
        SELECT sample_number, evaluation_type, evidence, has_exception, mitigation
        FROM sb_evaluation_sample
        WHERE line_id = ?
        ORDER BY evaluation_type, sample_number
    ''', (ld['line_id'],)).fetchall()

    print(f"\n[샘플] 총 {len(samples)}개")
    for sample in samples:
        sd = dict(sample)
        print(f"  #{sd['sample_number']} [{sd['evaluation_type']}] has_exception={sd['has_exception']}, evidence={sd['evidence'][:30] if sd['evidence'] else 'None'}, mitigation={sd['mitigation'][:30] if sd['mitigation'] else 'None'}")

print("\n" + "=" * 60)
