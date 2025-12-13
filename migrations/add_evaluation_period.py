"""
평가 대상 기간 컬럼 추가 마이그레이션
- sb_evaluation_header에 evaluation_period_start, evaluation_period_end 컬럼 추가
- 기존 데이터에 대해서는 evaluation_name에서 연도 추출하여 자동 설정
"""

import sqlite3
import os
import sys
from datetime import datetime

# 데이터베이스 경로
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'snowball.db')

def migrate():
    """평가 대상 기간 컬럼 추가"""

    print("\n" + "=" * 80)
    print("평가 대상 기간 컬럼 추가 마이그레이션")
    print("=" * 80)
    print(f"데이터베이스: {DB_PATH}")
    print("=" * 80)

    if not os.path.exists(DB_PATH):
        print(f"\n❌ 오류: 데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("\n[1/5] 현재 테이블 구조 확인")
        cursor.execute("PRAGMA table_info(sb_evaluation_header)")
        columns = cursor.fetchall()
        column_names = [col['name'] for col in columns]

        print(f"  현재 컬럼: {', '.join(column_names)}")

        # 이미 컬럼이 있는지 확인
        if 'evaluation_period_start' in column_names and 'evaluation_period_end' in column_names:
            print("\n✅ 이미 평가 대상 기간 컬럼이 존재합니다. 마이그레이션을 건너뜁니다.")
            return True

        print("\n[2/5] 백업 테이블 생성")
        cursor.execute("DROP TABLE IF EXISTS sb_evaluation_header_backup")
        cursor.execute("""
            CREATE TABLE sb_evaluation_header_backup AS
            SELECT * FROM sb_evaluation_header
        """)
        print("  ✅ 백업 완료")

        print("\n[3/5] 새 테이블 생성")
        cursor.execute("DROP TABLE IF EXISTS sb_evaluation_header_new")
        cursor.execute("""
            CREATE TABLE sb_evaluation_header_new (
                header_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                evaluation_name TEXT NOT NULL,
                evaluation_period_start DATE,
                evaluation_period_end DATE,
                status INTEGER DEFAULT 0,
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archived INTEGER DEFAULT 0,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm(rcm_id),
                UNIQUE(rcm_id, evaluation_name)
            )
        """)
        print("  ✅ 새 테이블 생성 완료")

        print("\n[4/5] 데이터 마이그레이션")
        old_data = cursor.execute("SELECT * FROM sb_evaluation_header").fetchall()

        migrated = 0
        for row in old_data:
            row_dict = dict(row)

            # evaluation_name에서 연도 추출 시도
            evaluation_name = row_dict.get('evaluation_name', '')
            period_start = None
            period_end = None

            # FY24, FY25 등의 패턴에서 연도 추출
            import re
            fy_match = re.search(r'FY(\d{2})', evaluation_name, re.IGNORECASE)
            year_match = re.search(r'20(\d{2})', evaluation_name)

            if fy_match:
                # FY25 -> 2025년
                year = int('20' + fy_match.group(1))
                period_start = f'{year}-01-01'
                period_end = f'{year}-12-31'
            elif year_match:
                # 2025 -> 2025년
                year = int('20' + year_match.group(1))
                period_start = f'{year}-01-01'
                period_end = f'{year}-12-31'
            # else: period_start, period_end는 NULL로 유지

            cursor.execute("""
                INSERT INTO sb_evaluation_header_new
                (header_id, rcm_id, evaluation_name, evaluation_period_start, evaluation_period_end,
                 status, progress, created_at, last_updated, archived)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row_dict.get('header_id'),
                row_dict['rcm_id'],
                row_dict['evaluation_name'],
                period_start,
                period_end,
                row_dict.get('status', 0),
                row_dict.get('progress', 0),
                row_dict.get('created_at'),
                row_dict.get('last_updated'),
                row_dict.get('archived', 0)
            ))

            migrated += 1
            if period_start:
                print(f"  • {evaluation_name}: {period_start} ~ {period_end}")
            else:
                print(f"  • {evaluation_name}: 평가 기간 미설정 (NULL)")

        print(f"\n  ✅ {migrated}개 레코드 마이그레이션 완료")

        print("\n[5/5] 테이블 교체")
        cursor.execute("DROP TABLE sb_evaluation_header")
        cursor.execute("ALTER TABLE sb_evaluation_header_new RENAME TO sb_evaluation_header")
        print("  ✅ 테이블 교체 완료")

        conn.commit()

        print("\n" + "=" * 80)
        print("✅ 마이그레이션 성공!")
        print("=" * 80)
        print(f"총 {migrated}개 평가 세션 마이그레이션 완료")
        print("\n추가된 컬럼:")
        print("  - evaluation_period_start (DATE): 평가 대상 기간 시작일")
        print("  - evaluation_period_end (DATE): 평가 대상 기간 종료일")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

        print("\n[복구] 백업에서 원본 테이블 복원 중...")
        try:
            cursor.execute("DROP TABLE IF EXISTS sb_evaluation_header")
            cursor.execute("ALTER TABLE sb_evaluation_header_backup RENAME TO sb_evaluation_header")
            conn.commit()
            print("  ✅ 복원 완료")
        except Exception as restore_error:
            print(f"  ❌ 복원 실패: {restore_error}")

        return False

    finally:
        # 백업 테이블 삭제
        try:
            cursor.execute("DROP TABLE IF EXISTS sb_evaluation_header_backup")
            conn.commit()
        except:
            pass

        conn.close()


if __name__ == '__main__':
    # UTF-8 출력 설정 (Windows용)
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n💾 평가 대상 기간 컬럼 추가 마이그레이션을 시작합니다.")
    print(f"데이터베이스: {DB_PATH}")

    # --yes 플래그가 있으면 자동으로 진행
    if '--yes' in sys.argv or '-y' in sys.argv:
        response = 'yes'
    else:
        response = input("\n계속하시겠습니까? (yes/no): ")

    if response.lower() == 'yes':
        success = migrate()
        if success:
            print("\n✅ 마이그레이션이 완료되었습니다.")
        else:
            print("\n❌ 마이그레이션이 실패했습니다.")
            sys.exit(1)
    else:
        print("취소되었습니다.")
