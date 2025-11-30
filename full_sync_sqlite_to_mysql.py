"""
SQLite를 MySQL로 완전 동기화 (스키마 + 데이터)

⚠️  경고: 이 스크립트는 MySQL의 모든 테이블을 삭제하고 SQLite 데이터로 교체합니다!

사용법:
    # Dry run (변경사항 미리보기)
    python full_sync_sqlite_to_mysql.py

    # 실제 적용
    python full_sync_sqlite_to_mysql.py --apply

    # 특정 테이블만 동기화
    python full_sync_sqlite_to_mysql.py --apply --tables sb_rcm,sb_user
"""

import sqlite3
import pymysql
from dotenv import load_dotenv
import os
import sys

# 환경 변수 로드
load_dotenv()

# MySQL 설정
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'snowball'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'charset': 'utf8mb4',
}

SQLITE_DB = 'snowball.db'

# 동기화 제외 테이블 (시스템 테이블 등)
EXCLUDE_TABLES = ['sqlite_sequence', 'migration_history']


def convert_type(sqlite_type):
    """SQLite 타입을 MySQL 타입으로 변환"""
    type_map = {
        'INTEGER': 'INT',
        'TEXT': 'TEXT',
        'REAL': 'DOUBLE',
        'BLOB': 'LONGBLOB',
        'NUMERIC': 'DECIMAL(10,2)',
    }

    sqlite_type_upper = sqlite_type.upper()

    # TIMESTAMP, DATETIME 처리
    if 'TIMESTAMP' in sqlite_type_upper or 'DATETIME' in sqlite_type_upper:
        return 'DATETIME'

    # 괄호 포함 타입 처리 (예: VARCHAR(50))
    for sqlite_key, mysql_type in type_map.items():
        if sqlite_type_upper.startswith(sqlite_key):
            return mysql_type

    return 'TEXT'


def get_sqlite_tables(conn):
    """SQLite 테이블 목록 조회"""
    cursor = conn.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    return [t for t in tables if t not in EXCLUDE_TABLES]


def get_sqlite_views(conn):
    """SQLite 뷰 목록 및 정의 조회"""
    cursor = conn.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='view'
        ORDER BY name
    """)
    return cursor.fetchall()


def get_table_schema(sqlite_conn, table_name):
    """SQLite 테이블 스키마 조회"""
    cursor = sqlite_conn.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()


def get_foreign_keys(sqlite_conn, table_name):
    """SQLite 외래키 조회"""
    cursor = sqlite_conn.execute(f"PRAGMA foreign_key_list({table_name})")
    return cursor.fetchall()


def generate_create_table_sql(table_name, columns, foreign_keys):
    """MySQL CREATE TABLE 문 생성"""
    col_defs = []
    primary_keys = []

    for col in columns:
        col_id, col_name, col_type, not_null, default_val, is_pk = col

        mysql_type = convert_type(col_type)
        col_def = f"`{col_name}` {mysql_type}"

        # AUTO_INCREMENT for INTEGER PRIMARY KEY
        if is_pk and 'INT' in mysql_type:
            col_def += " AUTO_INCREMENT"
            primary_keys.append(col_name)

        # NOT NULL
        if not_null and not is_pk:
            col_def += " NOT NULL"

        # DEFAULT (MySQL 제약사항 고려)
        # - TEXT, BLOB 타입: DEFAULT 불가
        # - DATETIME: CURRENT_TIMESTAMP만 가능
        if default_val is not None:
            # TEXT/BLOB 타입은 DEFAULT 불가
            if mysql_type in ('TEXT', 'LONGBLOB', 'BLOB'):
                pass
            # NULL 값 처리
            elif str(default_val).upper() == 'NULL':
                # DEFAULT NULL은 명시하지 않음 (MySQL에서 자동)
                pass
            # CURRENT_TIMESTAMP
            elif default_val == 'CURRENT_TIMESTAMP':
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            # DATETIME 타입은 CURRENT_TIMESTAMP 외 DEFAULT 불가
            elif mysql_type == 'DATETIME':
                # DATETIME은 DEFAULT 값 무시
                pass
            # 숫자 값
            elif str(default_val).replace('.', '').replace('-', '').replace('+', '').isdigit():
                col_def += f" DEFAULT {default_val}"
            # 문자열 값 (작은따옴표로 감싸되, 이스케이프 처리)
            else:
                escaped_val = str(default_val).replace("'", "\\'")
                col_def += f" DEFAULT '{escaped_val}'"

        col_defs.append(col_def)

    # PRIMARY KEY
    if primary_keys:
        col_defs.append(f"PRIMARY KEY (`{'`, `'.join(primary_keys)}`)")

    # FOREIGN KEY (외래키는 모든 테이블 생성 후 추가)
    # for fk in foreign_keys:
    #     fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
    #     fk_def = f"FOREIGN KEY (`{from_col}`) REFERENCES `{ref_table}`(`{to_col}`)"
    #     if on_delete and on_delete != 'NO ACTION':
    #         fk_def += f" ON DELETE {on_delete}"
    #     if on_update and on_update != 'NO ACTION':
    #         fk_def += f" ON UPDATE {on_update}"
    #     col_defs.append(fk_def)

    sql = f"CREATE TABLE `{table_name}` (\n  "
    sql += ",\n  ".join(col_defs)
    sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

    return sql


def get_table_data(sqlite_conn, table_name):
    """SQLite 테이블 데이터 조회"""
    cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
    return cursor.fetchall()


def drop_all_mysql_tables(mysql_conn):
    """MySQL의 모든 테이블과 뷰 삭제"""
    cursor = mysql_conn.cursor()

    # 외래키 체크 비활성화
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    # 모든 테이블 조회
    cursor.execute("SHOW FULL TABLES")
    tables_and_views = cursor.fetchall()

    dropped = []

    for item in tables_and_views:
        name = item[0]
        obj_type = item[1]  # 'BASE TABLE' or 'VIEW'

        try:
            if obj_type == 'VIEW':
                cursor.execute(f"DROP VIEW IF EXISTS `{name}`")
                dropped.append(f"VIEW: {name}")
            else:
                cursor.execute(f"DROP TABLE IF EXISTS `{name}`")
                dropped.append(f"TABLE: {name}")
        except Exception as e:
            print(f"  [WARNING] Failed to drop {obj_type} {name}: {e}")

    # 외래키 체크 재활성화
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    return dropped


def sync_table_data(sqlite_conn, mysql_conn, table_name, columns):
    """테이블 데이터 동기화"""
    # 데이터 조회
    data = get_table_data(sqlite_conn, table_name)

    if not data:
        return 0

    # 컬럼명 추출
    col_names = [col[1] for col in columns]

    # INSERT 문 생성
    placeholders = ', '.join(['%s'] * len(col_names))
    col_list = ', '.join([f"`{name}`" for name in col_names])
    insert_sql = f"INSERT INTO `{table_name}` ({col_list}) VALUES ({placeholders})"

    # 배치 삽입
    mysql_cursor = mysql_conn.cursor()
    inserted = 0

    try:
        for row in data:
            # datetime 객체를 문자열로 변환
            converted_row = []
            for val in row:
                if val is None:
                    converted_row.append(None)
                elif isinstance(val, (int, float, str)):
                    converted_row.append(val)
                else:
                    converted_row.append(str(val))

            mysql_cursor.execute(insert_sql, converted_row)
            inserted += 1

        mysql_conn.commit()

    except Exception as e:
        print(f"  [ERROR] Error inserting data: {e}")
        mysql_conn.rollback()
        raise

    return inserted


def full_sync(dry_run=True, specific_tables=None):
    """SQLite를 MySQL로 완전 동기화"""
    print("=" * 80)
    print("SQLite to MySQL FULL SYNC (Schema + Data)")
    print("=" * 80)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be applied")
    else:
        print("\n⚠️  WARNING: This will DELETE ALL MySQL tables and data!")
        print("⚠️  Press Ctrl+C within 5 seconds to cancel...")
        import time
        for i in range(5, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("\n   Starting sync...\n")

    # SQLite 연결
    print(f"\n[1] Connecting to SQLite: {SQLITE_DB}")
    sqlite_conn = sqlite3.connect(SQLITE_DB)

    # MySQL 연결
    print(f"[2] Connecting to MySQL: {MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    except Exception as e:
        print(f"\n[ERROR] MySQL connection failed: {e}")
        print("\nPlease check:")
        print("  - MySQL server is running")
        print("  - .env file MySQL configuration")
        print("  - pymysql is installed: pip install pymysql")
        return

    # 테이블 목록
    all_tables = get_sqlite_tables(sqlite_conn)

    if specific_tables:
        tables_to_sync = [t for t in specific_tables if t in all_tables]
        print(f"\n[3] Syncing specific tables: {', '.join(tables_to_sync)}")
    else:
        tables_to_sync = all_tables
        print(f"\n[3] Syncing all tables ({len(tables_to_sync)} tables)")

    print(f"    Tables: {', '.join(tables_to_sync)}")

    if dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN - Preview of operations")
        print("=" * 80)

        # 삭제될 MySQL 객체 미리보기
        print("\n[4] MySQL objects to be dropped:")
        cursor = mysql_conn.cursor()
        cursor.execute("SHOW FULL TABLES")
        mysql_objects = cursor.fetchall()

        if mysql_objects:
            for obj in mysql_objects:
                name, obj_type = obj
                print(f"    - {obj_type}: {name}")
        else:
            print("    (none)")

        # 생성될 테이블 미리보기
        print(f"\n[5] Tables to be created: {len(tables_to_sync)}")
        for table_name in tables_to_sync:
            row_count = sqlite_conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"    - {table_name} ({row_count} rows)")

        # 생성될 뷰 미리보기
        views = get_sqlite_views(sqlite_conn)
        print(f"\n[6] Views to be created: {len(views)}")
        for view_name, _ in views:
            print(f"    - {view_name}")

        print("\n" + "=" * 80)
        print("To apply these changes, run:")
        print("  python full_sync_sqlite_to_mysql.py --apply")
        print("=" * 80)

    else:
        # 실제 동기화 수행
        print("\n[4] Dropping all MySQL tables and views...")
        dropped = drop_all_mysql_tables(mysql_conn)
        print(f"    Dropped {len(dropped)} objects")

        # 외래키 체크 비활성화
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        print(f"\n[5] Creating tables and syncing data...")
        total_rows = 0

        for i, table_name in enumerate(tables_to_sync, 1):
            print(f"\n  [{i}/{len(tables_to_sync)}] {table_name}")

            # 스키마 조회
            columns = get_table_schema(sqlite_conn, table_name)
            foreign_keys = get_foreign_keys(sqlite_conn, table_name)

            # 테이블 생성
            create_sql = generate_create_table_sql(table_name, columns, foreign_keys)

            try:
                mysql_cursor.execute(create_sql)
                print(f"      ✓ Table created")
            except Exception as e:
                print(f"      ✗ Error creating table: {e}")
                continue

            # 데이터 동기화
            try:
                row_count = sync_table_data(sqlite_conn, mysql_conn, table_name, columns)
                print(f"      ✓ Synced {row_count} rows")
                total_rows += row_count
            except Exception as e:
                print(f"      ✗ Error syncing data: {e}")

        # 외래키 체크 재활성화
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 뷰 생성
        print(f"\n[6] Creating views...")
        views = get_sqlite_views(sqlite_conn)

        if views:
            for view_name, view_sql in views:
                print(f"  Creating view: {view_name}")
                try:
                    # SQLite SQL을 MySQL 호환으로 변환 (기본적으로 그대로 사용)
                    mysql_cursor.execute(view_sql)
                    print(f"      ✓ View created")
                except Exception as e:
                    print(f"      ✗ Error creating view: {e}")
        else:
            print("  (no views to create)")

        mysql_conn.commit()

        print("\n" + "=" * 80)
        print(f"✅ Sync completed successfully!")
        print(f"   Tables: {len(tables_to_sync)}")
        print(f"   Views: {len(views)}")
        print(f"   Total rows: {total_rows}")
        print("=" * 80)

    # 연결 종료
    sqlite_conn.close()
    mysql_conn.close()


if __name__ == '__main__':
    # 명령행 인자 파싱
    dry_run = '--apply' not in sys.argv

    # 특정 테이블만 동기화
    specific_tables = None
    if '--tables' in sys.argv:
        idx = sys.argv.index('--tables')
        if idx + 1 < len(sys.argv):
            specific_tables = sys.argv[idx + 1].split(',')

    full_sync(dry_run=dry_run, specific_tables=specific_tables)
