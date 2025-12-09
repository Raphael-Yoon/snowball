"""
SQLite에서 MySQL로 전체 데이터 마이그레이션

실행 방법:
    python migrations/migrate_sqlite_to_mysql.py
"""

import sys
import os
import sqlite3

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 현재 디렉토리를 프로젝트 루트로 변경
os.chdir(project_root)

try:
    import pymysql
except ImportError:
    print("PyMySQL이 설치되어 있지 않습니다.")
    print("pip install pymysql")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

SQLITE_DB = 'snowball.db'


def get_mysql_connection():
    """MySQL 연결"""
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'snowball'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def get_sqlite_connection():
    """SQLite 연결"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_table_schema(sqlite_cursor, table_name):
    """SQLite 테이블 스키마 조회"""
    sqlite_cursor.execute(f'PRAGMA table_info({table_name})')
    return sqlite_cursor.fetchall()


def convert_sqlite_type_to_mysql(sqlite_type):
    """SQLite 타입을 MySQL 타입으로 변환"""
    type_mapping = {
        'INTEGER': 'INT',
        'TEXT': 'TEXT',
        'REAL': 'DOUBLE',
        'BLOB': 'BLOB',
        'TIMESTAMP': 'DATETIME',
    }

    sqlite_type_upper = sqlite_type.upper()

    # VARCHAR, DATETIME 등은 그대로 사용
    if 'VARCHAR' in sqlite_type_upper or 'CHAR' in sqlite_type_upper:
        return sqlite_type
    if 'DATETIME' in sqlite_type_upper:
        return 'DATETIME'

    # 매핑에 있으면 변환, 없으면 TEXT
    for sqlite_key, mysql_type in type_mapping.items():
        if sqlite_key in sqlite_type_upper:
            return mysql_type

    return 'TEXT'


def create_mysql_table(mysql_cursor, table_name, schema):
    """MySQL 테이블 생성"""
    columns = []
    primary_keys = []

    for col in schema:
        col_name = col['name']
        col_type = convert_sqlite_type_to_mysql(col['type'])

        # PRIMARY KEY 처리
        if col['pk']:
            primary_keys.append(col_name)
            # AUTO_INCREMENT 처리
            if col_type == 'INT' and col['pk']:
                col_def = f"`{col_name}` {col_type} AUTO_INCREMENT"
            else:
                col_def = f"`{col_name}` {col_type}"
        else:
            col_def = f"`{col_name}` {col_type}"

        # NOT NULL 처리
        if col['notnull'] and not col['pk']:
            col_def += ' NOT NULL'

        # DEFAULT 처리
        if col['dflt_value'] is not None:
            if col['dflt_value'].upper() in ('CURRENT_TIMESTAMP', 'NULL'):
                col_def += f" DEFAULT {col['dflt_value']}"
            else:
                col_def += f" DEFAULT {col['dflt_value']}"

        columns.append(col_def)

    # PRIMARY KEY 추가
    if primary_keys:
        columns.append(f"PRIMARY KEY ({', '.join([f'`{pk}`' for pk in primary_keys])})")

    create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  " + ",\n  ".join(columns) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

    mysql_cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
    mysql_cursor.execute(create_sql)
    print(f"  테이블 생성: {table_name}")


def migrate_table_data(sqlite_conn, mysql_conn, table_name):
    """테이블 데이터 마이그레이션"""
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()

    # 데이터 조회
    sqlite_cursor.execute(f'SELECT * FROM {table_name}')
    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"  데이터 없음: {table_name}")
        return 0

    # 컬럼명 가져오기
    columns = [description[0] for description in sqlite_cursor.description]

    # INSERT 쿼리 생성
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join([f'`{col}`' for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"

    # 데이터 삽입
    count = 0
    for row in rows:
        try:
            mysql_cursor.execute(insert_sql, tuple(row))
            count += 1
        except Exception as e:
            print(f"    오류 (row {count}): {str(e)}")
            print(f"    데이터: {dict(row)}")

    mysql_conn.commit()
    print(f"  데이터 마이그레이션 완료: {table_name} ({count}개 행)")
    return count


def get_all_tables(sqlite_conn):
    """모든 테이블 목록 조회"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [row['name'] for row in cursor.fetchall()]


def main():
    print("=" * 60)
    print("SQLite에서 MySQL로 전체 데이터 마이그레이션")
    print("=" * 60)

    # 연결
    print("\n[1/4] 데이터베이스 연결 중...")
    sqlite_conn = get_sqlite_connection()
    mysql_conn = get_mysql_connection()

    try:
        # 테이블 목록 조회
        print("\n[2/4] 테이블 목록 조회 중...")
        tables = get_all_tables(sqlite_conn)
        print(f"  총 {len(tables)}개 테이블 발견")

        # 스키마 생성
        print("\n[3/4] MySQL 테이블 생성 중...")
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()

        for table in tables:
            schema = get_table_schema(sqlite_cursor, table)
            create_mysql_table(mysql_cursor, table, schema)

        mysql_conn.commit()

        # 데이터 마이그레이션
        print("\n[4/4] 데이터 마이그레이션 중...")
        total_rows = 0
        for table in tables:
            count = migrate_table_data(sqlite_conn, mysql_conn, table)
            total_rows += count

        print("\n" + "=" * 60)
        print(f"[완료] 마이그레이션이 성공적으로 완료되었습니다!")
        print(f"  총 {len(tables)}개 테이블, {total_rows}개 행 마이그레이션")
        print("=" * 60)

    except Exception as e:
        print(f"\n[오류] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        sqlite_conn.close()
        mysql_conn.close()


if __name__ == '__main__':
    main()
