"""
SQLite에서 MySQL로 데이터 마이그레이션 스크립트

사용법:
1. .env 파일에 MySQL 설정 완료
2. PythonAnywhere MySQL 데이터베이스 생성 완료
3. python migrate_to_mysql.py 실행
"""
import os
import sqlite3
import pymysql
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# SQLite 설정
SQLITE_DB = 'snowball.db'

# MySQL 설정
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'itap.mysql.pythonanywhere-services.com'),
    'user': os.getenv('MYSQL_USER', 'itap'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE', 'itap$snowball'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'charset': 'utf8mb4',
}

def get_sqlite_connection():
    """SQLite 연결"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_mysql_connection():
    """MySQL 연결"""
    return pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_table_list(sqlite_conn):
    """SQLite의 모든 테이블 목록 가져오기"""
    cursor = sqlite_conn.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        AND name != 'sb_migration_history'
        ORDER BY name
    """)
    return [row['name'] for row in cursor.fetchall()]

def get_table_schema(sqlite_conn, table_name):
    """테이블 스키마 가져오기"""
    cursor = sqlite_conn.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def sqlite_to_mysql_type(sqlite_type):
    """SQLite 타입을 MySQL 타입으로 변환"""
    sqlite_type_upper = sqlite_type.upper()

    type_mapping = {
        'INTEGER': 'INT',
        'TEXT': 'TEXT',
        'REAL': 'DOUBLE',
        'BLOB': 'BLOB',
        'NUMERIC': 'DOUBLE',
        'TIMESTAMP': 'DATETIME',
        'DATETIME': 'DATETIME',
        'DATE': 'DATE',
        'TIME': 'TIME',
        'BOOLEAN': 'TINYINT(1)',
    }

    for sqlite, mysql in type_mapping.items():
        if sqlite in sqlite_type_upper:
            return mysql

    # 기본값
    return 'TEXT'

def create_mysql_table(mysql_conn, table_name, schema, drop_if_exists=False):
    """MySQL에 테이블 생성"""
    cursor = mysql_conn.cursor()

    # 기존 테이블 삭제 (옵션)
    if drop_if_exists:
        print(f"Dropping existing table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

    columns = []
    primary_keys = []

    for col in schema:
        col_name = col['name']
        col_type = sqlite_to_mysql_type(col['type'])

        # AUTO_INCREMENT 처리
        if col['pk'] and 'INTEGER' in col['type'].upper():
            col_def = f"`{col_name}` {col_type} AUTO_INCREMENT"
        else:
            col_def = f"`{col_name}` {col_type}"

        # NOT NULL
        if col['notnull']:
            col_def += " NOT NULL"

        # DEFAULT (MySQL에서는 TEXT/BLOB 타입에 DEFAULT 설정 불가)
        if col['dflt_value']:
            # TEXT, BLOB 타입은 DEFAULT 값 설정 제외
            if col_type.upper() not in ['TEXT', 'BLOB', 'LONGTEXT', 'MEDIUMTEXT', 'TINYTEXT']:
                if col['dflt_value'].upper() == 'CURRENT_TIMESTAMP':
                    col_def += " DEFAULT CURRENT_TIMESTAMP"
                else:
                    col_def += f" DEFAULT {col['dflt_value']}"

        columns.append(col_def)

        if col['pk']:
            primary_keys.append(f"`{col_name}`")

    # PRIMARY KEY
    if primary_keys:
        columns.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

    create_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            {', '.join(columns)}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

    print(f"Creating table: {table_name}")
    cursor.execute(create_sql)
    mysql_conn.commit()

def get_indexes(sqlite_conn, table_name):
    """테이블의 인덱스 정보 가져오기"""
    cursor = sqlite_conn.execute(f"""
        SELECT name, sql FROM sqlite_master
        WHERE type='index'
        AND tbl_name='{table_name}'
        AND sql IS NOT NULL
        AND name NOT LIKE 'sqlite_%'
    """)
    return cursor.fetchall()

def create_indexes(mysql_conn, table_name, indexes):
    """MySQL에 인덱스 생성"""
    if not indexes:
        return

    cursor = mysql_conn.cursor()
    for idx in indexes:
        try:
            # SQLite CREATE INDEX 문을 MySQL용으로 변환
            sql = idx['sql'].replace('"', '`')
            print(f"  - Creating index: {idx['name']}")
            cursor.execute(sql)
        except Exception as e:
            print(f"  - Warning: Could not create index {idx['name']}: {e}")

    mysql_conn.commit()

def convert_datetime_value(value):
    """날짜/시간 값 변환 (MySQL 호환)"""
    if value is None:
        return None

    if isinstance(value, str):
        # 빈 문자열 처리
        if not value.strip():
            return None

        # 다양한 날짜 형식 처리
        try:
            # ISO 8601 형식 (YYYY-MM-DD HH:MM:SS)
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass

        try:
            # ISO 8601 형식 with microseconds
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass

        try:
            # DATE only
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass

        # 변환 실패 시 원본 반환
        return value

    return value

def migrate_table_data(sqlite_conn, mysql_conn, table_name):
    """테이블 데이터 마이그레이션 (배치 처리)"""
    print(f"Migrating data for table: {table_name}")

    # SQLite에서 데이터 읽기
    sqlite_cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    if not rows:
        print(f"  - No data to migrate")
        return 0

    # 컬럼 이름과 타입 가져오기
    columns = [description[0] for description in sqlite_cursor.description]

    # 컬럼 타입 정보 가져오기 (날짜/시간 컬럼 식별용)
    schema = get_table_schema(sqlite_conn, table_name)
    datetime_columns = set()
    for col in schema:
        col_type = col['type'].upper()
        if any(t in col_type for t in ['TIMESTAMP', 'DATETIME', 'DATE']):
            datetime_columns.add(col['name'])

    # MySQL에 데이터 삽입 (배치 처리)
    mysql_cursor = mysql_conn.cursor()

    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"

    migrated_count = 0
    batch_size = 1000  # 배치 크기
    batch_data = []

    for row in rows:
        try:
            row_dict = dict(row)
            values = []

            # 각 컬럼 값 처리
            for col in columns:
                value = row_dict[col]

                # 날짜/시간 컬럼이면 변환
                if col in datetime_columns and value is not None:
                    value = convert_datetime_value(value)

                values.append(value)

            batch_data.append(values)

            # 배치 크기에 도달하면 커밋
            if len(batch_data) >= batch_size:
                mysql_cursor.executemany(insert_sql, batch_data)
                mysql_conn.commit()
                migrated_count += len(batch_data)
                print(f"  - Migrated {migrated_count} rows...")
                batch_data = []

        except Exception as e:
            print(f"  - Error migrating row: {e}")
            print(f"    Row data: {dict(row)}")
            # 개별 행 에러는 건너뛰고 계속 진행

    # 남은 데이터 커밋
    if batch_data:
        try:
            mysql_cursor.executemany(insert_sql, batch_data)
            mysql_conn.commit()
            migrated_count += len(batch_data)
        except Exception as e:
            print(f"  - Error migrating final batch: {e}")

    print(f"  - Total migrated: {migrated_count} rows")
    return migrated_count

def main(drop_tables=False):
    """메인 마이그레이션 프로세스"""
    print("="*60)
    print("SQLite to MySQL Migration")
    print("="*60)

    # MySQL 비밀번호 확인
    if not MYSQL_CONFIG['password']:
        print("ERROR: MySQL password not set in .env file")
        print("Please set MYSQL_PASSWORD in your .env file")
        return

    # SQLite 파일 확인
    if not os.path.exists(SQLITE_DB):
        print(f"ERROR: SQLite database not found: {SQLITE_DB}")
        return

    try:
        # 데이터베이스 연결
        print("\nConnecting to databases...")
        sqlite_conn = get_sqlite_connection()
        mysql_conn = get_mysql_connection()
        print("  - Connected to SQLite")
        print("  - Connected to MySQL")

        # 테이블 목록 가져오기
        tables = get_table_list(sqlite_conn)
        print(f"\nFound {len(tables)} tables to migrate")

        if drop_tables:
            print("\n⚠️  DROP TABLES mode enabled - existing tables will be deleted!")

        total_migrated = 0

        # 각 테이블 마이그레이션
        for table_name in tables:
            print(f"\n--- Processing table: {table_name} ---")

            # 스키마 가져오기
            schema = get_table_schema(sqlite_conn, table_name)

            # MySQL 테이블 생성
            create_mysql_table(mysql_conn, table_name, schema, drop_if_exists=drop_tables)

            # 데이터 마이그레이션
            count = migrate_table_data(sqlite_conn, mysql_conn, table_name)
            total_migrated += count

            # 인덱스 생성
            indexes = get_indexes(sqlite_conn, table_name)
            if indexes:
                print(f"Creating indexes for {table_name}...")
                create_indexes(mysql_conn, table_name, indexes)

        print("\n" + "="*60)
        print(f"Migration completed successfully!")
        print(f"Total rows migrated: {total_migrated}")
        print("="*60)

    except pymysql.Error as e:
        print(f"\nMySQL Error: {e}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'mysql_conn' in locals():
            mysql_conn.close()

if __name__ == '__main__':
    # 확인 메시지
    print("\n⚠️⚠️⚠️  WARNING  ⚠️⚠️⚠️")
    print("This will DROP and RECREATE all tables in MySQL!")
    print("ALL EXISTING DATA will be DELETED!")
    print(f"\nTarget MySQL Database: {MYSQL_CONFIG['database']}")
    print(f"Target MySQL Host: {MYSQL_CONFIG['host']}")

    confirm = input("\nType 'YES' to continue: ").strip()

    if confirm == 'YES':
        main(drop_tables=True)
    else:
        print("Migration cancelled")
