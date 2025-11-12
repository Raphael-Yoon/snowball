"""
SQLite에서 MySQL로 데이터 마이그레이션
"""

import sqlite3
import pymysql
import sys
from datetime import datetime

# MySQL 연결 정보
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # 실제 비밀번호로 변경하세요
    'database': 'snowball',
    'charset': 'utf8mb4'
}

# SQLite 연결 정보
SQLITE_DB = 'C:/Pythons/snowball/snowball.db'


def convert_sql_type(sqlite_type):
    """SQLite 데이터 타입을 MySQL 타입으로 변환"""
    type_mapping = {
        'INTEGER': 'INT',
        'TEXT': 'TEXT',
        'REAL': 'DOUBLE',
        'BLOB': 'BLOB',
        'TIMESTAMP': 'DATETIME',
        'DATETIME': 'DATETIME',
        'DATE': 'DATE',
        'BOOLEAN': 'BOOLEAN'
    }

    sqlite_type_upper = sqlite_type.upper()
    for sqlite_key, mysql_type in type_mapping.items():
        if sqlite_key in sqlite_type_upper:
            return mysql_type
    return 'TEXT'


def get_table_schema(sqlite_conn, table_name):
    """SQLite 테이블 스키마 조회"""
    cursor = sqlite_conn.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return columns


def create_mysql_table(mysql_conn, table_name, columns, sqlite_conn):
    """MySQL 테이블 생성"""
    cursor = mysql_conn.cursor()

    # 기존 테이블 삭제
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

    # CREATE TABLE 문 생성
    col_definitions = []
    primary_keys = []

    for col in columns:
        col_id, col_name, col_type, not_null, default_val, is_pk = col

        mysql_type = convert_sql_type(col_type)

        # 컬럼 정의
        col_def = f"`{col_name}` {mysql_type}"

        # PRIMARY KEY인 경우 AUTO_INCREMENT 추가
        if is_pk and 'INT' in mysql_type:
            col_def += " AUTO_INCREMENT"
            primary_keys.append(col_name)

        # NOT NULL
        if not_null and not is_pk:
            col_def += " NOT NULL"

        # DEFAULT 값
        if default_val is not None:
            if default_val == 'CURRENT_TIMESTAMP':
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            elif default_val.isdigit():
                col_def += f" DEFAULT {default_val}"
            else:
                col_def += f" DEFAULT '{default_val}'"

        col_definitions.append(col_def)

    # PRIMARY KEY 추가
    if primary_keys:
        col_definitions.append(f"PRIMARY KEY (`{'`, `'.join(primary_keys)}`)")

    create_sql = f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(col_definitions) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

    print(f"\n=== Creating table: {table_name} ===")
    print(create_sql)

    cursor.execute(create_sql)
    mysql_conn.commit()


def migrate_table_data(sqlite_conn, mysql_conn, table_name):
    """테이블 데이터 마이그레이션"""
    print(f"\n=== Migrating data for table: {table_name} ===")

    # SQLite에서 데이터 조회
    sqlite_cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"  No data to migrate for {table_name}")
        return

    # 컬럼명 조회
    column_names = [description[0] for description in sqlite_cursor.description]

    # MySQL INSERT 준비
    mysql_cursor = mysql_conn.cursor()
    placeholders = ', '.join(['%s'] * len(column_names))
    insert_sql = f"INSERT INTO `{table_name}` (`{'`, `'.join(column_names)}`) VALUES ({placeholders})"

    # 데이터 삽입
    inserted = 0
    for row in rows:
        try:
            # None 값과 날짜 타입 처리
            values = []
            for val in row:
                if val is None:
                    values.append(None)
                elif isinstance(val, str) and ('T' in val or '-' in val):
                    # 날짜 형식인지 확인
                    try:
                        # ISO 형식 날짜 변환 시도
                        dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
                        values.append(dt)
                    except:
                        values.append(val)
                else:
                    values.append(val)

            mysql_cursor.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            print(f"  Error inserting row: {e}")
            print(f"  Row data: {row}")

    mysql_conn.commit()
    print(f"  Migrated {inserted} rows")


def main():
    print("=" * 60)
    print("SQLite to MySQL Migration Tool")
    print("=" * 60)

    # SQLite 연결
    print(f"\nConnecting to SQLite: {SQLITE_DB}")
    sqlite_conn = sqlite3.connect(SQLITE_DB)

    # MySQL 연결
    print(f"Connecting to MySQL: {MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    except Exception as e:
        print(f"MySQL 연결 실패: {e}")
        print("\n다음을 확인하세요:")
        print("1. MySQL 서버가 실행 중인지")
        print("2. 데이터베이스가 생성되어 있는지: CREATE DATABASE snowball;")
        print("3. 사용자 계정과 비밀번호가 올바른지")
        print("4. pymysql 설치: pip install pymysql")
        return

    # 테이블 목록 조회
    tables = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()

    print(f"\nFound {len(tables)} tables to migrate")

    # 각 테이블 마이그레이션
    for table in tables:
        table_name = table[0]

        # temp 테이블은 제외
        if table_name == 'temp':
            print(f"\nSkipping temporary table: {table_name}")
            continue

        # 스키마 조회
        columns = get_table_schema(sqlite_conn, table_name)

        # MySQL 테이블 생성
        create_mysql_table(mysql_conn, table_name, columns, sqlite_conn)

        # 데이터 마이그레이션
        migrate_table_data(sqlite_conn, mysql_conn, table_name)

    # 연결 종료
    sqlite_conn.close()
    mysql_conn.close()

    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
