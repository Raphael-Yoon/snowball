"""
ITGC용 운영평가 데이터를 ELC 통합 테이블로 마이그레이션

sb_operation_evaluation_line의 데이터를 sb_evaluation_line으로 이동
- ELC RCM의 운영평가 데이터만 마이그레이션
- design_evaluation_session을 기준으로 sb_evaluation_header 찾기
- control_code를 기준으로 sb_evaluation_line 매칭
- 운영평가 필드(sample_size, exception_details, conclusion 등) 업데이트
"""
import sys
import os
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db

print("=" * 60)
print("운영평가 데이터 마이그레이션 (ITGC → ELC 통합 테이블)")
print("=" * 60)

with get_db() as conn:
    # 1. ITGC 테이블에서 ELC RCM의 운영평가 데이터 찾기
    itgc_headers = conn.execute('''
        SELECT h.header_id, h.rcm_id, h.design_evaluation_session, h.evaluation_session,
               r.rcm_name, r.control_category
        FROM sb_operation_evaluation_header h
        INNER JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        WHERE r.control_category = 'ELC'
    ''').fetchall()

    print(f"\n[1단계] ITGC 테이블의 ELC 운영평가 헤더: {len(itgc_headers)}개")

    migrated_count = 0
    skipped_count = 0

    for header in itgc_headers:
        hd = dict(header)
        print(f"\n처리 중: {hd['rcm_name']} - {hd['design_evaluation_session']}")
        print(f"  ITGC header_id: {hd['header_id']}")

        # 2. ELC 통합 테이블에서 해당 설계평가 세션 찾기
        elc_header = conn.execute('''
            SELECT header_id, evaluation_name
            FROM sb_evaluation_header
            WHERE rcm_id = ? AND evaluation_name = ?
        ''', (hd['rcm_id'], hd['design_evaluation_session'])).fetchone()

        if not elc_header:
            print(f"  [SKIP] ELC 통합 테이블에 해당 세션 없음")
            skipped_count += 1
            continue

        elc_hd = dict(elc_header)
        print(f"  ELC header_id: {elc_hd['header_id']}")

        # 3. ITGC 테이블의 운영평가 line 데이터 가져오기
        itgc_lines = conn.execute('''
            SELECT control_code, sample_size, exception_details, conclusion,
                   improvement_plan, review_comment, evaluation_date, last_updated
            FROM sb_operation_evaluation_line
            WHERE header_id = ?
        ''', (hd['header_id'],)).fetchall()

        print(f"  ITGC line 데이터: {len(itgc_lines)}개")

        # 4. ELC 통합 테이블의 해당 line에 운영평가 데이터 업데이트
        updated_lines = 0
        for line in itgc_lines:
            ld = dict(line)

            # ELC 통합 테이블에서 해당 control_code의 line 찾기
            elc_line = conn.execute('''
                SELECT line_id, control_code
                FROM sb_evaluation_line
                WHERE header_id = ? AND control_code = ?
            ''', (elc_hd['header_id'], ld['control_code'])).fetchone()

            if not elc_line:
                print(f"    [SKIP] {ld['control_code']}: ELC 테이블에 없음")
                continue

            # 운영평가 데이터 업데이트
            conn.execute('''
                UPDATE sb_evaluation_line
                SET sample_size = ?,
                    exception_details = ?,
                    conclusion = ?,
                    improvement_plan = ?,
                    review_comment = ?,
                    last_updated = COALESCE(?, last_updated)
                WHERE line_id = ?
            ''', (
                ld['sample_size'],
                ld['exception_details'],
                ld['conclusion'],
                ld['improvement_plan'],
                ld['review_comment'],
                ld['last_updated'],
                dict(elc_line)['line_id']
            ))

            updated_lines += 1
            if ld.get('conclusion'):
                print(f"    [OK] {ld['control_code']}: 운영평가 데이터 마이그레이션")

        print(f"  업데이트된 line: {updated_lines}개")
        migrated_count += 1

    conn.commit()

    print("\n" + "=" * 60)
    print(f"마이그레이션 완료: {migrated_count}개 세션 처리")
    print(f"건너뜀: {skipped_count}개 세션")
    print("=" * 60)

    # 5. 마이그레이션 결과 확인
    print("\n[확인] ELC 통합 테이블의 운영평가 데이터:")
    result = conn.execute('''
        SELECT h.evaluation_name, r.rcm_name,
               COUNT(CASE WHEN l.conclusion IS NOT NULL THEN 1 END) as completed_count,
               COUNT(*) as total_count
        FROM sb_evaluation_header h
        INNER JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        INNER JOIN sb_evaluation_line l ON h.header_id = l.header_id
        WHERE r.control_category = 'ELC'
          AND l.overall_effectiveness IN ('적정', 'effective', '효과적')
        GROUP BY h.header_id, h.evaluation_name, r.rcm_name
        HAVING COUNT(CASE WHEN l.conclusion IS NOT NULL THEN 1 END) > 0
    ''').fetchall()

    for row in result:
        rd = dict(row)
        print(f"  {rd['rcm_name']} - {rd['evaluation_name']}: {rd['completed_count']}/{rd['total_count']} 완료")
