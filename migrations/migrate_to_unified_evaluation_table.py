"""
설계평가/운영평가 테이블을 통합 테이블로 마이그레이션

FROM (기존):
- sb_design_evaluation_header, sb_design_evaluation_line
- sb_operation_evaluation_header, sb_operation_evaluation_line

TO (통합):
- sb_evaluation_header, sb_evaluation_line

ELC RCM의 데이터만 마이그레이션 (ITGC는 기존 테이블 유지)
"""
import sys
import os
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db

print("=" * 60)
print("평가 데이터 마이그레이션 → 통합 테이블")
print("=" * 60)

with get_db() as conn:
    # ELC RCM 목록 조회
    elc_rcms = conn.execute('''
        SELECT rcm_id, rcm_name
        FROM sb_rcm
        WHERE control_category = 'ELC'
    ''').fetchall()

    print(f"\n[대상] ELC RCM: {len(elc_rcms)}개")
    for rcm in elc_rcms:
        print(f"  - {dict(rcm)['rcm_name']}")

    # ============================================================
    # 1단계: 설계평가 데이터 마이그레이션
    # ============================================================
    print("\n" + "=" * 60)
    print("[1단계] 설계평가 데이터 마이그레이션")
    print("=" * 60)

    design_headers = conn.execute('''
        SELECT h.*, r.rcm_name
        FROM sb_design_evaluation_header h
        INNER JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        WHERE r.control_category = 'ELC'
    ''').fetchall()

    print(f"\n설계평가 헤더: {len(design_headers)}개")

    migrated_design_count = 0

    for header in design_headers:
        hd = dict(header)
        print(f"\n처리 중: {hd['rcm_name']} - {hd['evaluation_session']}")

        # 통합 테이블에 이미 존재하는지 확인
        existing = conn.execute('''
            SELECT header_id FROM sb_evaluation_header
            WHERE rcm_id = ? AND evaluation_name = ?
        ''', (hd['rcm_id'], hd['evaluation_session'])).fetchone()

        if existing:
            print(f"  [SKIP] 이미 존재함 (header_id={dict(existing)['header_id']})")
            new_header_id = dict(existing)['header_id']
        else:
            # 헤더 생성
            cursor = conn.execute('''
                INSERT INTO sb_evaluation_header (
                    rcm_id, evaluation_name, status, created_at, last_updated
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                hd['rcm_id'],
                hd['evaluation_session'],
                hd.get('status', 0),
                hd.get('created_at'),
                hd.get('last_updated')
            ))
            new_header_id = cursor.lastrowid
            print(f"  [OK] 헤더 생성 (new_header_id={new_header_id})")

        # 설계평가 line 데이터 가져오기
        design_lines = conn.execute('''
            SELECT * FROM sb_design_evaluation_line
            WHERE header_id = ?
        ''', (hd['header_id'],)).fetchall()

        print(f"  설계평가 line: {len(design_lines)}개")

        # line 데이터 마이그레이션
        for line in design_lines:
            ld = dict(line)

            # 통합 테이블에 이미 존재하는지 확인
            existing_line = conn.execute('''
                SELECT line_id FROM sb_evaluation_line
                WHERE header_id = ? AND control_code = ?
            ''', (new_header_id, ld['control_code'])).fetchone()

            if existing_line:
                # 이미 있으면 설계평가 필드만 업데이트
                conn.execute('''
                    UPDATE sb_evaluation_line
                    SET description_adequacy = ?,
                        improvement_suggestion = ?,
                        overall_effectiveness = ?,
                        evaluation_rationale = ?,
                        design_comment = ?,
                        recommended_actions = ?,
                        no_occurrence = ?,
                        no_occurrence_reason = ?,
                        evaluation_evidence = ?,
                        evaluation_date = COALESCE(?, evaluation_date),
                        last_updated = COALESCE(?, last_updated)
                    WHERE line_id = ?
                ''', (
                    ld.get('description_adequacy'),
                    ld.get('improvement_suggestion'),
                    ld.get('overall_effectiveness'),
                    ld.get('evaluation_rationale'),
                    ld.get('design_comment'),
                    ld.get('recommended_actions'),
                    ld.get('no_occurrence'),
                    ld.get('no_occurrence_reason'),
                    ld.get('evaluation_evidence'),
                    ld.get('evaluation_date'),
                    ld.get('last_updated'),
                    dict(existing_line)['line_id']
                ))
            else:
                # 새로 생성
                conn.execute('''
                    INSERT INTO sb_evaluation_line (
                        header_id, control_code, control_sequence,
                        description_adequacy, improvement_suggestion, overall_effectiveness,
                        evaluation_rationale, design_comment, recommended_actions,
                        no_occurrence, no_occurrence_reason, evaluation_evidence,
                        evaluation_date, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_header_id,
                    ld['control_code'],
                    ld.get('control_sequence'),
                    ld.get('description_adequacy'),
                    ld.get('improvement_suggestion'),
                    ld.get('overall_effectiveness'),
                    ld.get('evaluation_rationale'),
                    ld.get('design_comment'),
                    ld.get('recommended_actions'),
                    ld.get('no_occurrence'),
                    ld.get('no_occurrence_reason'),
                    ld.get('evaluation_evidence'),
                    ld.get('evaluation_date'),
                    ld.get('last_updated')
                ))

        migrated_design_count += 1

    print(f"\n설계평가 마이그레이션 완료: {migrated_design_count}개 세션")

    # ============================================================
    # 2단계: 운영평가 데이터 마이그레이션
    # ============================================================
    print("\n" + "=" * 60)
    print("[2단계] 운영평가 데이터 마이그레이션")
    print("=" * 60)

    operation_headers = conn.execute('''
        SELECT h.*, r.rcm_name
        FROM sb_operation_evaluation_header h
        INNER JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        WHERE r.control_category = 'ELC'
    ''').fetchall()

    print(f"\n운영평가 헤더: {len(operation_headers)}개")

    migrated_operation_count = 0

    for header in operation_headers:
        hd = dict(header)
        print(f"\n처리 중: {hd['rcm_name']} - {hd['design_evaluation_session']}")

        # 통합 테이블에서 해당 설계평가 세션 찾기
        unified_header = conn.execute('''
            SELECT header_id FROM sb_evaluation_header
            WHERE rcm_id = ? AND evaluation_name = ?
        ''', (hd['rcm_id'], hd['design_evaluation_session'])).fetchone()

        if not unified_header:
            print(f"  [ERROR] 설계평가 세션 없음: {hd['design_evaluation_session']}")
            continue

        unified_header_id = dict(unified_header)['header_id']
        print(f"  통합 header_id: {unified_header_id}")

        # 운영평가 상태로 업데이트 (status >= 2)
        conn.execute('''
            UPDATE sb_evaluation_header
            SET status = CASE
                WHEN ? >= 2 THEN ?
                ELSE status
            END
            WHERE header_id = ?
        ''', (hd.get('status', 0), hd.get('status', 2), unified_header_id))

        # 운영평가 line 데이터 가져오기
        operation_lines = conn.execute('''
            SELECT * FROM sb_operation_evaluation_line
            WHERE header_id = ?
        ''', (hd['header_id'],)).fetchall()

        print(f"  운영평가 line: {len(operation_lines)}개")

        updated_count = 0
        for line in operation_lines:
            ld = dict(line)

            # 통합 테이블에서 해당 control_code의 line 찾기
            unified_line = conn.execute('''
                SELECT line_id FROM sb_evaluation_line
                WHERE header_id = ? AND control_code = ?
            ''', (unified_header_id, ld['control_code'])).fetchone()

            if not unified_line:
                print(f"    [SKIP] {ld['control_code']}: 설계평가 line 없음")
                continue

            # 운영평가 필드 업데이트
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
                ld.get('sample_size'),
                ld.get('exception_details'),
                ld.get('conclusion'),
                ld.get('improvement_plan'),
                ld.get('review_comment'),
                ld.get('last_updated'),
                dict(unified_line)['line_id']
            ))

            if ld.get('conclusion'):
                updated_count += 1

        print(f"  업데이트된 line (conclusion 있음): {updated_count}개")
        migrated_operation_count += 1

    print(f"\n운영평가 마이그레이션 완료: {migrated_operation_count}개 세션")

    conn.commit()

    # ============================================================
    # 결과 확인
    # ============================================================
    print("\n" + "=" * 60)
    print("[결과 확인] 통합 테이블 데이터")
    print("=" * 60)

    result = conn.execute('''
        SELECT h.evaluation_name, r.rcm_name, h.status,
               COUNT(*) as total_lines,
               COUNT(CASE WHEN l.overall_effectiveness IS NOT NULL THEN 1 END) as design_completed,
               COUNT(CASE WHEN l.conclusion IS NOT NULL THEN 1 END) as operation_completed
        FROM sb_evaluation_header h
        INNER JOIN sb_rcm r ON h.rcm_id = r.rcm_id
        INNER JOIN sb_evaluation_line l ON h.header_id = l.header_id
        WHERE r.control_category = 'ELC'
        GROUP BY h.header_id, h.evaluation_name, r.rcm_name, h.status
        ORDER BY r.rcm_name, h.evaluation_name
    ''').fetchall()

    print()
    for row in result:
        rd = dict(row)
        print(f"{rd['rcm_name']} - {rd['evaluation_name']} (status={rd['status']})")
        print(f"  설계평가: {rd['design_completed']}/{rd['total_lines']}")
        print(f"  운영평가: {rd['operation_completed']}/{rd['total_lines']}")

print("\n" + "=" * 60)
print("마이그레이션 완료!")
print("=" * 60)
