"""
외래키 컬럼 인덱스 추가 마이그레이션

목적:
- N+1 쿼리 문제 해결을 위한 외래키 인덱스 추가
- 조인 성능 향상

호환성:
- SQLite와 MySQL 모두 지원
- 표준 SQL 사용

실행 방법:
    python migrations/add_foreign_key_indexes.py

롤백 방법:
    python migrations/add_foreign_key_indexes.py --rollback
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 현재 디렉토리를 프로젝트 루트로 변경
os.chdir(project_root)

from db_config import get_db, is_mysql


def upgrade(conn):
    """외래키 인덱스 생성"""
    print("\n[외래키 인덱스 추가 시작]")
    print("=" * 60)

    indexes = [
        # sb_user_activity_log 테이블
        {
            'name': 'idx_user_activity_log_user_id',
            'table': 'sb_user_activity_log',
            'columns': 'user_id',
            'description': '사용자 활동 로그 - 사용자별 조회'
        },

        # sb_rcm 테이블
        {
            'name': 'idx_rcm_user_id',
            'table': 'sb_rcm',
            'columns': 'user_id',
            'description': 'RCM - 업로드 사용자별 조회'
        },

        # sb_rcm_detail 테이블
        {
            'name': 'idx_rcm_detail_rcm_id',
            'table': 'sb_rcm_detail',
            'columns': 'rcm_id',
            'description': 'RCM 상세 - RCM별 조회'
        },
        {
            'name': 'idx_rcm_detail_mapped_std_control_id',
            'table': 'sb_rcm_detail',
            'columns': 'mapped_std_control_id',
            'description': 'RCM 상세 - 기준통제별 조회'
        },
        {
            'name': 'idx_rcm_detail_mapped_by',
            'table': 'sb_rcm_detail',
            'columns': 'mapped_by',
            'description': 'RCM 상세 - 매핑 작업자별 조회'
        },
        {
            'name': 'idx_rcm_detail_ai_reviewed_by',
            'table': 'sb_rcm_detail',
            'columns': 'ai_reviewed_by',
            'description': 'RCM 상세 - AI 검토자별 조회'
        },

        # sb_user_rcm 테이블
        {
            'name': 'idx_user_rcm_user_id',
            'table': 'sb_user_rcm',
            'columns': 'user_id',
            'description': '사용자-RCM 매핑 - 사용자별 조회'
        },
        {
            'name': 'idx_user_rcm_rcm_id',
            'table': 'sb_user_rcm',
            'columns': 'rcm_id',
            'description': '사용자-RCM 매핑 - RCM별 조회'
        },
        {
            'name': 'idx_user_rcm_granted_by',
            'table': 'sb_user_rcm',
            'columns': 'granted_by',
            'description': '사용자-RCM 매핑 - 권한 부여자별 조회'
        },

        # sb_evaluation_header 테이블 (통합 평가 헤더)
        # 주의: user_id 컬럼은 마이그레이션으로 제거됨
        {
            'name': 'idx_evaluation_header_rcm_id',
            'table': 'sb_evaluation_header',
            'columns': 'rcm_id',
            'description': '평가 헤더 - RCM별 조회'
        },

        # sb_evaluation_line 테이블 (통합 평가 라인)
        {
            'name': 'idx_evaluation_line_header_id',
            'table': 'sb_evaluation_line',
            'columns': 'header_id',
            'description': '평가 라인 - 헤더별 조회'
        },

        # sb_evaluation_sample 테이블
        {
            'name': 'idx_evaluation_sample_line_id',
            'table': 'sb_evaluation_sample',
            'columns': 'line_id',
            'description': '평가 표본 - 라인별 조회'
        },

        # sb_evaluation_image 테이블
        {
            'name': 'idx_evaluation_image_line_id',
            'table': 'sb_evaluation_image',
            'columns': 'line_id',
            'description': '평가 이미지 - 라인별 조회'
        },

        # sb_internal_assessment 테이블
        {
            'name': 'idx_internal_assessment_rcm_id',
            'table': 'sb_internal_assessment',
            'columns': 'rcm_id',
            'description': '내부평가 진행상황 - RCM별 조회'
        },
        {
            'name': 'idx_internal_assessment_user_id',
            'table': 'sb_internal_assessment',
            'columns': 'user_id',
            'description': '내부평가 진행상황 - 사용자별 조회'
        },

        # sb_rcm_standard_mapping 테이블
        {
            'name': 'idx_rcm_standard_mapping_rcm_id',
            'table': 'sb_rcm_standard_mapping',
            'columns': 'rcm_id',
            'description': 'RCM-기준통제 매핑 - RCM별 조회'
        },
        {
            'name': 'idx_rcm_standard_mapping_std_control_id',
            'table': 'sb_rcm_standard_mapping',
            'columns': 'std_control_id',
            'description': 'RCM-기준통제 매핑 - 기준통제별 조회'
        },
        {
            'name': 'idx_rcm_standard_mapping_mapped_by',
            'table': 'sb_rcm_standard_mapping',
            'columns': 'mapped_by',
            'description': 'RCM-기준통제 매핑 - 매핑 작업자별 조회'
        },

        # sb_rcm_completeness_eval 테이블
        {
            'name': 'idx_rcm_completeness_eval_rcm_id',
            'table': 'sb_rcm_completeness_eval',
            'columns': 'rcm_id',
            'description': 'RCM 완성도 평가 - RCM별 조회'
        },
        {
            'name': 'idx_rcm_completeness_eval_eval_by',
            'table': 'sb_rcm_completeness_eval',
            'columns': 'eval_by',
            'description': 'RCM 완성도 평가 - 평가자별 조회'
        },

        # 레거시 테이블 인덱스 (아직 사용 중인 경우를 대비)
        {
            'name': 'idx_design_eval_header_rcm_id',
            'table': 'sb_design_evaluation_header',
            'columns': 'rcm_id',
            'description': '설계평가 헤더 - RCM별 조회 (레거시)'
        },
        {
            'name': 'idx_design_eval_header_user_id',
            'table': 'sb_design_evaluation_header',
            'columns': 'user_id',
            'description': '설계평가 헤더 - 사용자별 조회 (레거시)'
        },
        {
            'name': 'idx_design_eval_line_header_id',
            'table': 'sb_design_evaluation_line',
            'columns': 'header_id',
            'description': '설계평가 라인 - 헤더별 조회 (레거시)'
        },
        {
            'name': 'idx_operation_eval_header_rcm_id',
            'table': 'sb_operation_evaluation_header',
            'columns': 'rcm_id',
            'description': '운영평가 헤더 - RCM별 조회 (레거시)'
        },
        {
            'name': 'idx_operation_eval_header_user_id',
            'table': 'sb_operation_evaluation_header',
            'columns': 'user_id',
            'description': '운영평가 헤더 - 사용자별 조회 (레거시)'
        },
        {
            'name': 'idx_operation_eval_line_header_id',
            'table': 'sb_operation_evaluation_line',
            'columns': 'header_id',
            'description': '운영평가 라인 - 헤더별 조회 (레거시)'
        },
    ]

    created_count = 0
    skipped_count = 0
    error_count = 0

    for idx in indexes:
        try:
            # 테이블 존재 여부 확인 (SQLite/MySQL 호환)
            if is_mysql():
                table_check = conn.execute(f"""
                    SELECT TABLE_NAME as name FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{idx['table']}'
                """).fetchone()
            else:
                table_check = conn.execute(f"""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='{idx['table']}'
                """).fetchone()

            if not table_check:
                print(f"[SKIP] 테이블 없음: {idx['table']} - 건너뜀")
                skipped_count += 1
                continue

            # 인덱스 생성 (IF NOT EXISTS 사용으로 중복 방지)
            sql = f"""
                CREATE INDEX IF NOT EXISTS {idx['name']}
                ON {idx['table']}({idx['columns']})
            """
            conn.execute(sql)
            print(f"[OK] 생성: {idx['name']}")
            print(f"     {idx['description']}")
            created_count += 1

        except Exception as e:
            print(f"[ERROR] 오류: {idx['name']} - {str(e)}")
            error_count += 1

    conn.commit()

    print("\n" + "=" * 60)
    print(f"[완료] 인덱스 추가 완료")
    print(f"  - 생성: {created_count}개")
    print(f"  - 건너뜀: {skipped_count}개")
    print(f"  - 오류: {error_count}개")
    print("=" * 60)


def downgrade(conn):
    """외래키 인덱스 제거"""
    print("\n[외래키 인덱스 제거 시작]")
    print("=" * 60)

    # upgrade 함수에서 정의한 모든 인덱스 이름
    index_names = [
        'idx_user_activity_log_user_id',
        'idx_rcm_user_id',
        'idx_rcm_detail_rcm_id',
        'idx_rcm_detail_mapped_std_control_id',
        'idx_rcm_detail_mapped_by',
        'idx_rcm_detail_ai_reviewed_by',
        'idx_user_rcm_user_id',
        'idx_user_rcm_rcm_id',
        'idx_user_rcm_granted_by',
        'idx_evaluation_header_rcm_id',
        'idx_evaluation_line_header_id',
        'idx_evaluation_sample_line_id',
        'idx_evaluation_image_line_id',
        'idx_internal_assessment_rcm_id',
        'idx_internal_assessment_user_id',
        'idx_rcm_standard_mapping_rcm_id',
        'idx_rcm_standard_mapping_std_control_id',
        'idx_rcm_standard_mapping_mapped_by',
        'idx_rcm_completeness_eval_rcm_id',
        'idx_rcm_completeness_eval_eval_by',
        'idx_design_eval_header_rcm_id',
        'idx_design_eval_header_user_id',
        'idx_design_eval_line_header_id',
        'idx_operation_eval_header_rcm_id',
        'idx_operation_eval_header_user_id',
        'idx_operation_eval_line_header_id',
    ]

    removed_count = 0
    not_found_count = 0

    for idx_name in index_names:
        try:
            # 인덱스 존재 여부 확인 (SQLite/MySQL 호환)
            if is_mysql():
                index_check = conn.execute(f"""
                    SELECT INDEX_NAME as name FROM information_schema.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE() AND INDEX_NAME = '{idx_name}'
                """).fetchone()
            else:
                index_check = conn.execute(f"""
                    SELECT name FROM sqlite_master
                    WHERE type='index' AND name='{idx_name}'
                """).fetchone()

            if not index_check:
                print(f"[SKIP] 인덱스 없음: {idx_name}")
                not_found_count += 1
                continue

            # 인덱스 제거
            conn.execute(f"DROP INDEX IF EXISTS {idx_name}")
            print(f"[OK] 제거: {idx_name}")
            removed_count += 1

        except Exception as e:
            print(f"[ERROR] 오류: {idx_name} - {str(e)}")

    conn.commit()

    print("\n" + "=" * 60)
    print(f"[완료] 인덱스 제거 완료")
    print(f"  - 제거: {removed_count}개")
    print(f"  - 없음: {not_found_count}개")
    print("=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='외래키 인덱스 마이그레이션')
    parser.add_argument('--rollback', action='store_true', help='인덱스 제거 (롤백)')
    args = parser.parse_args()

    try:
        with get_db() as conn:
            if args.rollback:
                print("\n롤백 모드: 인덱스를 제거합니다.")
                response = input("정말 인덱스를 제거하시겠습니까? (yes/no): ")
                if response.lower() == 'yes':
                    downgrade(conn)
                else:
                    print("취소되었습니다.")
            else:
                upgrade(conn)

    except Exception as e:
        print(f"\n[오류] 마이그레이션 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
