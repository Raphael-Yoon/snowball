"""
SQLite 스키마를 MySQL로 마이그레이션 (데이터는 제외)

개발 중 DB 구조가 변경될 때 사용:
1. 로컬 SQLite에서 개발 및 마이그레이션 실행
2. 이 스크립트로 변경된 스키마만 MySQL에 반영
3. 기존 MySQL 데이터는 보존

사용법:
    python migrations/migrate_schema_to_mysql.py
"""

import sqlite3
import pymysql
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# MySQL 설정
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'itap.mysql.pythonanywhere-services.com'),
    'user': os.getenv('MYSQL_USER', 'itap'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE', 'itap$snowball'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'charset': 'utf8mb4',
}

SQLITE_DB = 'snowball.db'


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
        AND name != 'temp'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_table_schema(sqlite_conn, table_name):
    """SQLite 테이블 스키마 조회"""
    cursor = sqlite_conn.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()


def get_table_indexes(sqlite_conn, table_name):
    """SQLite 테이블 인덱스 조회"""
    cursor = sqlite_conn.execute(f"PRAGMA index_list({table_name})")
    indexes = []
    for row in cursor.fetchall():
        index_name = row[1]
        is_unique = row[2]
        # 인덱스 컬럼 조회
        index_cols = sqlite_conn.execute(f"PRAGMA index_info({index_name})").fetchall()
        col_names = [col[2] for col in index_cols]
        indexes.append({
            'name': index_name,
            'unique': is_unique,
            'columns': col_names
        })
    return indexes


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

        # DEFAULT
        if default_val is not None:
            if default_val == 'CURRENT_TIMESTAMP':
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            elif default_val.replace('.', '').replace('-', '').isdigit():
                col_def += f" DEFAULT {default_val}"
            else:
                col_def += f" DEFAULT '{default_val}'"

        col_defs.append(col_def)

    # PRIMARY KEY
    if primary_keys:
        col_defs.append(f"PRIMARY KEY (`{'`, `'.join(primary_keys)}`)")

    # FOREIGN KEY
    for fk in foreign_keys:
        fk_id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
        fk_def = f"FOREIGN KEY (`{from_col}`) REFERENCES `{ref_table}`(`{to_col}`)"
        if on_delete and on_delete != 'NO ACTION':
            fk_def += f" ON DELETE {on_delete}"
        if on_update and on_update != 'NO ACTION':
            fk_def += f" ON UPDATE {on_update}"
        col_defs.append(fk_def)

    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  "
    sql += ",\n  ".join(col_defs)
    sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

    return sql


def compare_schemas(sqlite_conn, mysql_conn):
    """스키마 비교 및 변경사항 감지"""
    changes = {
        'new_tables': [],
        'new_columns': {},
        'type_changes': {}
    }

    # SQLite 테이블 목록
    sqlite_tables = get_sqlite_tables(sqlite_conn)

    mysql_cursor = mysql_conn.cursor()

    for table_name in sqlite_tables:
        # MySQL에 테이블이 존재하는지 확인
        mysql_cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not mysql_cursor.fetchone():
            changes['new_tables'].append(table_name)
            continue

        # 컬럼 비교
        sqlite_cols = {col[1]: col for col in get_table_schema(sqlite_conn, table_name)}

        mysql_cursor.execute(f"DESCRIBE `{table_name}`")
        mysql_cols = {row[0]: row for row in mysql_cursor.fetchall()}

        # 새 컬럼 찾기
        new_cols = set(sqlite_cols.keys()) - set(mysql_cols.keys())
        if new_cols:
            changes['new_columns'][table_name] = list(new_cols)

    return changes


def migrate_schema(dry_run=True):
    """스키마 마이그레이션 실행"""
    print("=" * 80)
    print("SQLite Schema to MySQL Migration")
    print("=" * 80)

    # 연결
    print(f"\n[1] Connecting to SQLite: {SQLITE_DB}")
    sqlite_conn = sqlite3.connect(SQLITE_DB)

    print(f"[2] Connecting to MySQL: {MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    except Exception as e:
        print(f"\n❌ MySQL 연결 실패: {e}")
        print("\n다음을 확인하세요:")
        print("  - MySQL 서버 실행 여부")
        print("  - .env 파일의 MySQL 설정")
        print("  - pymysql 설치: pip install pymysql")
        return

    mysql_cursor = mysql_conn.cursor()

    # 스키마 비교
    print("\n[3] Comparing schemas...")
    changes = compare_schemas(sqlite_conn, mysql_conn)

    if changes['new_tables']:
        print(f"\n  📋 New tables to create: {len(changes['new_tables'])}")
        for table in changes['new_tables']:
            print(f"     - {table}")

    if changes['new_columns']:
        print(f"\n  ➕ Tables with new columns: {len(changes['new_columns'])}")
        for table, cols in changes['new_columns'].items():
            print(f"     - {table}: {', '.join(cols)}")

    if not changes['new_tables'] and not changes['new_columns']:
        print("\n  ✅ No schema changes detected. MySQL is up to date!")
        return

    # Dry run 모드
    if dry_run:
        print("\n" + "=" * 80)
        print("🔍 DRY RUN MODE - No changes will be applied")
        print("=" * 80)
        print("\nGenerated SQL statements:\n")
    else:
        print("\n" + "=" * 80)
        print("🚀 APPLYING CHANGES TO MYSQL")
        print("=" * 80)

    # 새 테이블 생성
    for table_name in changes['new_tables']:
        columns = get_table_schema(sqlite_conn, table_name)
        foreign_keys = get_foreign_keys(sqlite_conn, table_name)

        create_sql = generate_create_table_sql(table_name, columns, foreign_keys)

        print(f"\n-- Creating table: {table_name}")
        print(create_sql + ";")

        if not dry_run:
            try:
                mysql_cursor.execute(create_sql)
                print(f"  ✅ Created table: {table_name}")
            except Exception as e:
                print(f"  ❌ Error creating table {table_name}: {e}")

    # 새 컬럼 추가
    for table_name, new_cols in changes['new_columns'].items():
        columns = {col[1]: col for col in get_table_schema(sqlite_conn, table_name)}

        for col_name in new_cols:
            col = columns[col_name]
            col_id, col_name, col_type, not_null, default_val, is_pk = col

            mysql_type = convert_type(col_type)
            alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {mysql_type}"

            if default_val is not None:
                if default_val == 'CURRENT_TIMESTAMP':
                    alter_sql += " DEFAULT CURRENT_TIMESTAMP"
                elif default_val.replace('.', '').replace('-', '').isdigit():
                    alter_sql += f" DEFAULT {default_val}"
                else:
                    alter_sql += f" DEFAULT '{default_val}'"

            print(f"\n-- Adding column to {table_name}")
            print(alter_sql + ";")

            if not dry_run:
                try:
                    mysql_cursor.execute(alter_sql)
                    print(f"  ✅ Added column: {table_name}.{col_name}")
                except Exception as e:
                    print(f"  ❌ Error adding column {table_name}.{col_name}: {e}")

    if not dry_run:
        mysql_conn.commit()
        print("\n" + "=" * 80)
        print("✅ Migration completed successfully!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("To apply these changes, run:")
        print("  python migrations/migrate_schema_to_mysql.py --apply")
        print("=" * 80)

    # 연결 종료
    sqlite_conn.close()
    mysql_conn.close()


if __name__ == '__main__':
    import sys

    # --apply 옵션이 있으면 실제 적용, 없으면 dry run
    dry_run = '--apply' not in sys.argv

    if dry_run:
        print("\n⚠️  Running in DRY RUN mode (no changes will be applied)")
        print("   To apply changes, run with --apply flag\n")

    migrate_schema(dry_run=dry_run)
