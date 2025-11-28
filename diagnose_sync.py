"""
동기화 문제 진단 스크립트

운영서버에서 실행하여 SQLite와 MySQL 상태를 확인합니다.
"""

import sqlite3
import os
import sys

def check_sqlite():
    """SQLite 데이터베이스 상태 확인"""
    print("=" * 80)
    print("SQLite 데이터베이스 확인")
    print("=" * 80)

    sqlite_file = 'snowball.db'

    # 파일 존재 확인
    if not os.path.exists(sqlite_file):
        print(f"\n❌ {sqlite_file} 파일이 없습니다!")
        return False

    print(f"\n✓ SQLite 파일 존재: {sqlite_file}")
    print(f"  파일 크기: {os.path.getsize(sqlite_file):,} bytes")

    # 테이블 목록 확인
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()

        # 모든 테이블 조회
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n✓ 테이블 개수: {len(tables)}")
        print("\n테이블 목록:")

        important_tables = ['sb_rcm', 'sb_user', 'sb_rcm_detail', 'sb_evaluation_sample']

        for table in tables:
            # 각 테이블의 행 개수
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

            marker = "⭐" if table in important_tables else "  "
            print(f"  {marker} {table:<40} ({count:>6} rows)")

        # sb_rcm 테이블 스키마 확인
        if 'sb_rcm' in tables:
            print("\n✓ sb_rcm 테이블 스키마:")
            cursor.execute("PRAGMA table_info(sb_rcm)")
            columns = cursor.fetchall()

            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                pk_mark = " [PK]" if is_pk else ""
                print(f"    - {col_name:<25} {col_type:<15}{pk_mark}")

            # user_id vs upload_user_id 확인
            col_names = [col[1] for col in columns]
            if 'user_id' in col_names:
                print("\n  ✅ 'user_id' 컬럼 존재 (최신 버전)")
            elif 'upload_user_id' in col_names:
                print("\n  ⚠️  'upload_user_id' 컬럼 존재 (구버전)")
                print("      migration 필요!")

        else:
            print("\n❌ sb_rcm 테이블이 없습니다!")

        # sb_evaluation_sample 테이블 확인
        if 'sb_evaluation_sample' in tables:
            print("\n✓ sb_evaluation_sample 테이블 스키마:")
            cursor.execute("PRAGMA table_info(sb_evaluation_sample)")
            columns = cursor.fetchall()

            col_names = [col[1] for col in columns]

            # 중요 컬럼 체크
            checks = [
                ('evaluation_type', '평가 타입 구분'),
                ('attribute0', 'attribute 필드'),
            ]

            for col_name, description in checks:
                if col_name in col_names:
                    print(f"    ✅ {col_name} - {description}")
                else:
                    print(f"    ❌ {col_name} - {description} (누락)")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ SQLite 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_mysql():
    """MySQL 데이터베이스 상태 확인"""
    print("\n" + "=" * 80)
    print("MySQL 데이터베이스 확인")
    print("=" * 80)

    try:
        import pymysql
    except ImportError:
        print("\n⚠️  PyMySQL이 설치되지 않았습니다.")
        print("   운영서버에서는 설치되어 있어야 합니다.")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'snowball'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
    }

    print(f"\n연결 정보:")
    print(f"  Host: {config['host']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")

    try:
        conn = pymysql.connect(**config, charset='utf8mb4')
        cursor = conn.cursor()

        print(f"\n✓ MySQL 연결 성공")

        # 테이블 목록 조회
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\n✓ 테이블 개수: {len(tables)}")

        if not tables:
            print("\n⚠️  MySQL에 테이블이 하나도 없습니다!")
            print("   full_sync_sqlite_to_mysql.py --apply 를 실행하세요.")
            return False

        print("\n테이블 목록:")
        important_tables = ['sb_rcm', 'sb_user', 'sb_rcm_detail', 'sb_evaluation_sample']

        for table in tables:
            # 각 테이블의 행 개수
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]

            marker = "⭐" if table in important_tables else "  "
            print(f"  {marker} {table:<40} ({count:>6} rows)")

        # sb_rcm 테이블 확인
        if 'sb_rcm' in tables:
            print("\n✓ sb_rcm 테이블 스키마:")
            cursor.execute("DESCRIBE sb_rcm")
            columns = cursor.fetchall()

            for col in columns:
                field, type_, null, key, default, extra = col
                key_mark = f" [{key}]" if key else ""
                print(f"    - {field:<25} {type_:<15}{key_mark}")

            # user_id vs upload_user_id 확인
            col_names = [col[0] for col in columns]
            if 'user_id' in col_names:
                print("\n  ✅ 'user_id' 컬럼 존재 (최신 버전)")
            elif 'upload_user_id' in col_names:
                print("\n  ⚠️  'upload_user_id' 컬럼 존재 (구버전)")
                print("      동기화 필요!")
        else:
            print("\n❌ sb_rcm 테이블이 없습니다!")
            print("   full_sync_sqlite_to_mysql.py --apply 를 실행하세요.")

        # sb_evaluation_sample 테이블 확인
        if 'sb_evaluation_sample' in tables:
            print("\n✓ sb_evaluation_sample 테이블 스키마:")
            cursor.execute("DESCRIBE sb_evaluation_sample")
            columns = cursor.fetchall()

            col_names = [col[0] for col in columns]

            # 중요 컬럼 체크
            checks = [
                ('evaluation_type', '평가 타입 구분'),
                ('attribute0', 'attribute 필드'),
            ]

            for col_name, description in checks:
                if col_name in col_names:
                    print(f"    ✅ {col_name} - {description}")
                else:
                    print(f"    ❌ {col_name} - {description} (누락)")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ MySQL 연결 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def recommend_action():
    """권장 조치 출력"""
    print("\n" + "=" * 80)
    print("권장 조치")
    print("=" * 80)

    print("""
1. SQLite와 MySQL 스키마가 다른 경우:
   → python full_sync_sqlite_to_mysql.py --apply

2. MySQL에 테이블이 없는 경우:
   → python full_sync_sqlite_to_mysql.py --apply

3. sb_rcm 테이블이 없는 경우:
   → 로컬 SQLite 파일을 서버에 업로드했는지 확인
   → python full_sync_sqlite_to_mysql.py --apply 실행

4. user_id/upload_user_id 불일치:
   → python full_sync_sqlite_to_mysql.py --apply

5. 동기화 후:
   → sudo systemctl restart snowball (또는 해당 프로세스 재시작)
""")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "Snowball 동기화 진단 도구" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    sqlite_ok = check_sqlite()
    mysql_ok = check_mysql()

    recommend_action()

    print("\n")

    if sqlite_ok and mysql_ok:
        sys.exit(0)
    else:
        sys.exit(1)
