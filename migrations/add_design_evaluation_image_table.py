"""
설계평가 이미지 테이블 생성 및 기존 이미지 마이그레이션

실행 방법:
    python migrations/add_design_evaluation_image_table.py
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 현재 디렉토리를 프로젝트 루트로 변경
os.chdir(project_root)

from db_config import get_db


def create_image_table():
    """평가 이미지 통합 테이블 생성"""
    print("[1/4] 평가 이미지 통합 테이블 생성 중...")

    with get_db() as conn:
        # 기존 테이블이 있으면 데이터 백업
        existing_data = []
        try:
            existing_data = conn.execute('''
                SELECT * FROM sb_design_evaluation_image
            ''').fetchall()
            if existing_data:
                print(f"  => 기존 데이터 {len(existing_data)}개 발견, 백업 중...")
        except:
            pass

        # 기존 테이블 삭제
        conn.execute('DROP TABLE IF EXISTS sb_design_evaluation_image')

        # 통합 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_evaluation_image (
                image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_type TEXT NOT NULL,
                line_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 인덱스 생성
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_eval_image_line_id
            ON sb_evaluation_image(line_id)
        ''')

        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_eval_image_type
            ON sb_evaluation_image(evaluation_type)
        ''')

        # 백업한 데이터 복원
        if existing_data:
            for row in existing_data:
                # Row 객체를 dict로 변환
                row_dict = dict(row)
                conn.execute('''
                    INSERT INTO sb_evaluation_image
                    (evaluation_type, line_id, file_path, file_name, file_size, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ('design', row_dict['line_id'], row_dict['file_path'], row_dict['file_name'],
                      row_dict.get('file_size'), row_dict.get('uploaded_at')))
            print(f"  => 기존 데이터 {len(existing_data)}개 복원 완료")

        conn.commit()
        print("  => 통합 테이블 생성 완료")


def migrate_design_images():
    """파일 시스템의 설계평가 이미지를 DB에 마이그레이션"""
    print("\n[2/4] 설계평가 이미지 마이그레이션 중...")

    with get_db() as conn:
        # 모든 설계평가 라인 조회
        lines = conn.execute('''
            SELECT l.line_id, h.rcm_id, h.header_id, l.control_code
            FROM sb_design_evaluation_line l
            JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
        ''').fetchall()

        total_images = 0

        for line in lines:
            line_id = line['line_id']
            rcm_id = line['rcm_id']
            header_id = line['header_id']
            control_code = line['control_code']

            # 이미지 디렉토리 경로
            image_dir = os.path.join('static', 'uploads', 'design_evaluations',
                                    str(rcm_id), str(header_id), control_code)

            if not os.path.exists(image_dir):
                continue

            # 디렉토리의 모든 이미지 파일 스캔
            for filename in os.listdir(image_dir):
                file_path_full = os.path.join(image_dir, filename)

                # 파일인지 확인
                if not os.path.isfile(file_path_full):
                    continue

                # 이미지 파일만 처리 (확장자 확인)
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    continue

                # 상대 경로 생성
                relative_path = f"static/uploads/design_evaluations/{rcm_id}/{header_id}/{control_code}/{filename}"

                # 파일 크기
                file_size = os.path.getsize(file_path_full)

                # DB에 이미 존재하는지 확인
                existing = conn.execute('''
                    SELECT image_id FROM sb_evaluation_image
                    WHERE evaluation_type = ? AND line_id = ? AND file_path = ?
                ''', ('design', line_id, relative_path)).fetchone()

                if existing:
                    continue

                # DB에 삽입
                conn.execute('''
                    INSERT INTO sb_evaluation_image
                    (evaluation_type, line_id, file_path, file_name, file_size, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', ('design', line_id, relative_path, filename, file_size))

                total_images += 1
                print(f"  [설계] {control_code}: {filename}")

        conn.commit()
        print(f"\n  => 설계평가 이미지 {total_images}개 마이그레이션 완료")


def migrate_operation_images():
    """파일 시스템의 운영평가 이미지를 DB에 마이그레이션"""
    print("\n[3/4] 운영평가 이미지 마이그레이션 중...")

    with get_db() as conn:
        # 모든 운영평가 라인 조회
        lines = conn.execute('''
            SELECT l.line_id, h.rcm_id, h.header_id, l.control_code
            FROM sb_operation_evaluation_line l
            JOIN sb_operation_evaluation_header h ON l.header_id = h.header_id
        ''').fetchall()

        total_images = 0

        for line in lines:
            line_id = line['line_id']
            rcm_id = line['rcm_id']
            header_id = line['header_id']
            control_code = line['control_code']

            # 이미지 디렉토리 경로
            image_dir = os.path.join('static', 'uploads', 'operation_evaluations',
                                    str(rcm_id), str(header_id), control_code)

            if not os.path.exists(image_dir):
                continue

            # 디렉토리의 모든 이미지 파일 스캔
            for filename in os.listdir(image_dir):
                file_path_full = os.path.join(image_dir, filename)

                # 파일인지 확인
                if not os.path.isfile(file_path_full):
                    continue

                # 이미지 파일만 처리 (확장자 확인)
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    continue

                # 상대 경로 생성
                relative_path = f"static/uploads/operation_evaluations/{rcm_id}/{header_id}/{control_code}/{filename}"

                # 파일 크기
                file_size = os.path.getsize(file_path_full)

                # DB에 이미 존재하는지 확인
                existing = conn.execute('''
                    SELECT image_id FROM sb_evaluation_image
                    WHERE evaluation_type = ? AND line_id = ? AND file_path = ?
                ''', ('operation', line_id, relative_path)).fetchone()

                if existing:
                    continue

                # DB에 삽입
                conn.execute('''
                    INSERT INTO sb_evaluation_image
                    (evaluation_type, line_id, file_path, file_name, file_size, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', ('operation', line_id, relative_path, filename, file_size))

                total_images += 1
                print(f"  [운영] {control_code}: {filename}")

        conn.commit()
        print(f"\n  => 운영평가 이미지 {total_images}개 마이그레이션 완료")


def verify_migration():
    """마이그레이션 결과 확인"""
    print("\n[4/4] 마이그레이션 결과 확인 중...")

    with get_db() as conn:
        # 평가 타입별 이미지 개수
        design_count = conn.execute('''
            SELECT COUNT(*) as count FROM sb_evaluation_image
            WHERE evaluation_type = 'design'
        ''').fetchone()

        operation_count = conn.execute('''
            SELECT COUNT(*) as count FROM sb_evaluation_image
            WHERE evaluation_type = 'operation'
        ''').fetchone()

        total_count = conn.execute('''
            SELECT COUNT(*) as count FROM sb_evaluation_image
        ''').fetchone()

        print(f"  => 설계평가 이미지: {design_count['count']}개")
        print(f"  => 운영평가 이미지: {operation_count['count']}개")
        print(f"  => 총 이미지 개수: {total_count['count']}개")


if __name__ == '__main__':
    print("=" * 60)
    print("평가 이미지 통합 테이블 생성 및 마이그레이션")
    print("=" * 60)

    try:
        # 1. 통합 테이블 생성
        create_image_table()

        # 2. 설계평가 이미지 마이그레이션
        migrate_design_images()

        # 3. 운영평가 이미지 마이그레이션
        migrate_operation_images()

        # 4. 결과 확인
        verify_migration()

        print("\n" + "=" * 60)
        print("[완료] 모든 작업이 성공적으로 완료되었습니다!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[오류] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
