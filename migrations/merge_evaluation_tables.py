"""
설계평가와 운영평가 테이블 통합 마이그레이션

실행 방법:
    python migrations/merge_evaluation_tables.py
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 현재 디렉토리를 프로젝트 루트로 변경
os.chdir(project_root)

from db_config import get_db


def create_unified_tables():
    """통합 평가 테이블 생성"""
    print("[1/3] 통합 평가 테이블 생성 중...")

    with get_db() as conn:
        # 1. sb_evaluation_header 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_evaluation_header (
                header_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                evaluation_session TEXT NOT NULL,
                status TEXT DEFAULT 'in_progress',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. sb_evaluation_line 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_evaluation_line (
                line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                header_id INTEGER NOT NULL,
                control_code TEXT NOT NULL,
                control_sequence INTEGER,

                -- 설계평가 필드
                description_adequacy TEXT,
                improvement_suggestion TEXT,
                overall_effectiveness TEXT,
                evaluation_rationale TEXT,
                design_comment TEXT,
                recommended_actions TEXT,
                no_occurrence INTEGER DEFAULT 0,
                no_occurrence_reason TEXT,
                evaluation_evidence TEXT,

                -- 운영평가 필드
                sample_size INTEGER DEFAULT 0,
                exception_details TEXT,
                conclusion TEXT,
                improvement_plan TEXT,
                review_comment TEXT,

                evaluation_date TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (header_id) REFERENCES sb_evaluation_header(header_id)
            )
        ''')

        # 인덱스 생성
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_eval_header_rcm_session
            ON sb_evaluation_header(rcm_id, evaluation_session)
        ''')

        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_eval_line_header
            ON sb_evaluation_line(header_id)
        ''')

        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_eval_line_control
            ON sb_evaluation_line(control_code)
        ''')

        conn.commit()
        print("  => 통합 테이블 생성 완료")


def migrate_design_evaluations():
    """설계평가 데이터 마이그레이션"""
    print("\n[2/3] 설계평가 데이터 마이그레이션 중...")

    with get_db() as conn:
        # 설계평가 헤더 조회
        design_headers = conn.execute('''
            SELECT header_id, rcm_id, evaluation_session, evaluation_status,
                   progress_percentage, start_date, last_updated
            FROM sb_design_evaluation_header
        ''').fetchall()

        header_id_map = {}  # 구 header_id -> 신 header_id 매핑

        for header in design_headers:
            old_header_id = header['header_id']

            # 새 헤더 삽입
            cursor = conn.execute('''
                INSERT INTO sb_evaluation_header (rcm_id, evaluation_session, status, progress, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (header['rcm_id'], header['evaluation_session'], header['evaluation_status'],
                  int(header['progress_percentage'] or 0), header['start_date'], header['last_updated']))

            new_header_id = cursor.lastrowid
            header_id_map[old_header_id] = new_header_id
            print(f"  헤더 마이그레이션: {header['evaluation_session']} (old_id={old_header_id} -> new_id={new_header_id})")

        # 설계평가 라인 조회
        design_lines = conn.execute('''
            SELECT line_id, header_id, control_code, control_sequence,
                   description_adequacy, improvement_suggestion, overall_effectiveness,
                   evaluation_rationale, design_comment, recommended_actions,
                   no_occurrence, no_occurrence_reason, evaluation_evidence,
                   evaluation_date, last_updated
            FROM sb_design_evaluation_line
        ''').fetchall()

        line_id_map = {}  # 구 line_id -> 신 line_id 매핑

        for line in design_lines:
            old_line_id = line['line_id']
            old_header_id = line['header_id']
            new_header_id = header_id_map.get(old_header_id)

            if not new_header_id:
                print(f"  경고: header_id {old_header_id}를 찾을 수 없음")
                continue

            # 새 라인 삽입
            cursor = conn.execute('''
                INSERT INTO sb_evaluation_line (
                    header_id, control_code, control_sequence,
                    description_adequacy, improvement_suggestion, overall_effectiveness,
                    evaluation_rationale, design_comment, recommended_actions,
                    no_occurrence, no_occurrence_reason, evaluation_evidence,
                    evaluation_date, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (new_header_id, line['control_code'], line['control_sequence'],
                  line['description_adequacy'], line['improvement_suggestion'], line['overall_effectiveness'],
                  line['evaluation_rationale'], line['design_comment'], line['recommended_actions'],
                  line['no_occurrence'], line['no_occurrence_reason'], line['evaluation_evidence'],
                  line['evaluation_date'], line['last_updated']))

            new_line_id = cursor.lastrowid
            line_id_map[old_line_id] = new_line_id

        # sb_evaluation_sample의 line_id 업데이트 (evaluation_type='design')
        for old_line_id, new_line_id in line_id_map.items():
            conn.execute('''
                UPDATE sb_evaluation_sample
                SET line_id = ?
                WHERE line_id = ? AND evaluation_type = 'design'
            ''', (new_line_id, old_line_id))

        # sb_evaluation_image의 line_id 업데이트 (evaluation_type='design')
        for old_line_id, new_line_id in line_id_map.items():
            conn.execute('''
                UPDATE sb_evaluation_image
                SET line_id = ?
                WHERE line_id = ? AND evaluation_type = 'design'
            ''', (new_line_id, old_line_id))

        conn.commit()
        print(f"  => 설계평가 {len(design_headers)}개 헤더, {len(design_lines)}개 라인 마이그레이션 완료")


def migrate_operation_evaluations():
    """운영평가 데이터 마이그레이션"""
    print("\n[3/3] 운영평가 데이터 마이그레이션 중...")

    with get_db() as conn:
        # 운영평가 헤더 조회
        operation_headers = conn.execute('''
            SELECT header_id, rcm_id, evaluation_session, evaluation_status,
                   progress_percentage, start_date, last_updated
            FROM sb_operation_evaluation_header
        ''').fetchall()

        header_id_map = {}  # 구 header_id -> 신 header_id 매핑

        for header in operation_headers:
            old_header_id = header['header_id']

            # 새 헤더 삽입
            cursor = conn.execute('''
                INSERT INTO sb_evaluation_header (rcm_id, evaluation_session, status, progress, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (header['rcm_id'], header['evaluation_session'], header['evaluation_status'],
                  int(header['progress_percentage'] or 0), header['start_date'], header['last_updated']))

            new_header_id = cursor.lastrowid
            header_id_map[old_header_id] = new_header_id
            print(f"  헤더 마이그레이션: {header['evaluation_session']} (old_id={old_header_id} -> new_id={new_header_id})")

        # 운영평가 라인 조회
        operation_lines = conn.execute('''
            SELECT line_id, header_id, control_code, control_sequence,
                   sample_size, exception_count, exception_details,
                   conclusion, improvement_plan, review_comment,
                   evaluation_date, last_updated
            FROM sb_operation_evaluation_line
        ''').fetchall()

        line_id_map = {}  # 구 line_id -> 신 line_id 매핑

        for line in operation_lines:
            old_line_id = line['line_id']
            old_header_id = line['header_id']
            new_header_id = header_id_map.get(old_header_id)

            if not new_header_id:
                print(f"  경고: header_id {old_header_id}를 찾을 수 없음")
                continue

            # 새 라인 삽입
            cursor = conn.execute('''
                INSERT INTO sb_evaluation_line (
                    header_id, control_code, control_sequence,
                    sample_size, exception_details, conclusion, improvement_plan, review_comment,
                    evaluation_date, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (new_header_id, line['control_code'], line['control_sequence'],
                  line['sample_size'], line['exception_details'], line['conclusion'],
                  line['improvement_plan'], line['review_comment'],
                  line['evaluation_date'], line['last_updated']))

            new_line_id = cursor.lastrowid
            line_id_map[old_line_id] = new_line_id

        # sb_evaluation_sample의 line_id 업데이트 (evaluation_type='operation')
        for old_line_id, new_line_id in line_id_map.items():
            conn.execute('''
                UPDATE sb_evaluation_sample
                SET line_id = ?
                WHERE line_id = ? AND evaluation_type = 'operation'
            ''', (new_line_id, old_line_id))

        # sb_evaluation_image의 line_id 업데이트 (evaluation_type='operation')
        for old_line_id, new_line_id in line_id_map.items():
            conn.execute('''
                UPDATE sb_evaluation_image
                SET line_id = ?
                WHERE line_id = ? AND evaluation_type = 'operation'
            ''', (new_line_id, old_line_id))

        conn.commit()
        print(f"  => 운영평가 {len(operation_headers)}개 헤더, {len(operation_lines)}개 라인 마이그레이션 완료")


def verify_migration():
    """마이그레이션 결과 확인"""
    print("\n[검증] 마이그레이션 결과 확인 중...")

    with get_db() as conn:
        # 헤더 개수 확인
        header_count = conn.execute('SELECT COUNT(*) as count FROM sb_evaluation_header').fetchone()
        design_header_count = conn.execute('SELECT COUNT(*) as count FROM sb_design_evaluation_header').fetchone()
        operation_header_count = conn.execute('SELECT COUNT(*) as count FROM sb_operation_evaluation_header').fetchone()

        print(f"  => 통합 헤더: {header_count['count']}개")
        print(f"  => 기존 설계평가 헤더: {design_header_count['count']}개")
        print(f"  => 기존 운영평가 헤더: {operation_header_count['count']}개")

        # 라인 개수 확인
        line_count = conn.execute('SELECT COUNT(*) as count FROM sb_evaluation_line').fetchone()
        design_line_count = conn.execute('SELECT COUNT(*) as count FROM sb_design_evaluation_line').fetchone()
        operation_line_count = conn.execute('SELECT COUNT(*) as count FROM sb_operation_evaluation_line').fetchone()

        print(f"  => 통합 라인: {line_count['count']}개")
        print(f"  => 기존 설계평가 라인: {design_line_count['count']}개")
        print(f"  => 기존 운영평가 라인: {operation_line_count['count']}개")

        expected_total = design_line_count['count'] + operation_line_count['count']
        if line_count['count'] == expected_total:
            print(f"  [OK] 라인 개수 일치: {line_count['count']} == {expected_total}")
        else:
            print(f"  [ERROR] 라인 개수 불일치: {line_count['count']} != {expected_total}")


if __name__ == '__main__':
    print("=" * 60)
    print("설계평가와 운영평가 테이블 통합")
    print("=" * 60)

    try:
        # 1. 통합 테이블 생성
        create_unified_tables()

        # 2. 설계평가 데이터 마이그레이션
        migrate_design_evaluations()

        # 3. 운영평가 데이터 마이그레이션
        migrate_operation_evaluations()

        # 4. 결과 검증
        verify_migration()

        print("\n" + "=" * 60)
        print("[완료] 마이그레이션이 성공적으로 완료되었습니다!")
        print("=" * 60)
        print("\n주의: 기존 테이블(sb_design_evaluation_*, sb_operation_evaluation_*)은 삭제하지 않았습니다.")
        print("모든 기능이 정상 작동하는 것을 확인한 후 수동으로 삭제하세요.")

    except Exception as e:
        print(f"\n[오류] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
