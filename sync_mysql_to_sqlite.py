"""
MySQL에서 SQLite로 데이터 백업 스크립트

배치 스케줄러나 cron으로 주기적으로 실행하여
MySQL 데이터를 로컬 SQLite로 백업합니다.

사용법:
    python backup_mysql_to_sqlite.py
"""
import os
import sqlite3
import pymysql
from dotenv import load_dotenv
from datetime import datetime
import shutil

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

# SQLite 설정
SQLITE_DB = 'snowball.db'
BACKUP_DIR = 'backups'

def get_mysql_connection():
    """MySQL 연결"""
    return pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_sqlite_connection():
    """SQLite 연결"""
    conn = sqlite3.connect(SQLITE_DB)
    return conn

def create_backup():
    """기존 SQLite DB 백업"""
    if not os.path.exists(SQLITE_DB):
        print("No existing SQLite database to backup")
        return None

    # 백업 디렉토리 생성
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # 타임스탬프 포함한 백업 파일명
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'snowball_{timestamp}.db')

    # 백업 생성
    shutil.copy2(SQLITE_DB, backup_file)
    print(f"Created backup: {backup_file}")

    # 오래된 백업 정리 (최근 10개만 유지)
    cleanup_old_backups()

    return backup_file

def cleanup_old_backups(keep=10):
    """오래된 백업 파일 정리"""
    if not os.path.exists(BACKUP_DIR):
        return

    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('snowball_') and f.endswith('.db')]
    backups.sort(reverse=True)

    # 오래된 백업 삭제
    for old_backup in backups[keep:]:
        old_path = os.path.join(BACKUP_DIR, old_backup)
        os.remove(old_path)
        print(f"Removed old backup: {old_backup}")

def get_mysql_tables(mysql_conn):
    """MySQL의 모든 테이블 목록 가져오기"""
    cursor = mysql_conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
    return tables

def get_table_schema_mysql(mysql_conn, table_name):
    """MySQL 테이블 스키마 가져오기"""
    cursor = mysql_conn.cursor()
    cursor.execute(f"DESCRIBE `{table_name}`")
    return cursor.fetchall()

def mysql_to_sqlite_type(mysql_type):
    """MySQL 타입을 SQLite 타입으로 변환"""
    mysql_type_upper = mysql_type.upper()

    # AUTO_INCREMENT는 INTEGER PRIMARY KEY로 처리
    if 'INT' in mysql_type_upper:
        return 'INTEGER'
    elif any(t in mysql_type_upper for t in ['VARCHAR', 'TEXT', 'CHAR', 'ENUM', 'SET']):
        return 'TEXT'
    elif any(t in mysql_type_upper for t in ['DOUBLE', 'FLOAT', 'DECIMAL']):
        return 'REAL'
    elif any(t in mysql_type_upper for t in ['DATETIME', 'TIMESTAMP']):
        return 'TIMESTAMP'
    elif 'DATE' in mysql_type_upper:
        return 'DATE'
    elif 'TIME' in mysql_type_upper:
        return 'TIME'
    elif any(t in mysql_type_upper for t in ['BLOB', 'BINARY']):
        return 'BLOB'
    elif 'BOOL' in mysql_type_upper or 'TINYINT(1)' in mysql_type_upper:
        return 'INTEGER'

    # 기본값
    return 'TEXT'

def create_sqlite_table(sqlite_conn, table_name, schema):
    """SQLite에 테이블 생성"""
    cursor = sqlite_conn.cursor()

    # 기존 테이블 삭제
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

    columns = []
    primary_keys = []

    for col in schema:
        col_name = col['Field']
        col_type = mysql_to_sqlite_type(col['Type'])

        col_def = f"`{col_name}` {col_type}"

        # PRIMARY KEY 처리
        if col['Key'] == 'PRI':
            primary_keys.append(col_name)
            # AUTO_INCREMENT는 INTEGER PRIMARY KEY로
            if 'auto_increment' in col['Extra'].lower():
                col_def = f"`{col_name}` INTEGER PRIMARY KEY AUTOINCREMENT"

        # NOT NULL
        if col['Null'] == 'NO' and col['Key'] != 'PRI':
            col_def += " NOT NULL"

        # DEFAULT
        if col['Default'] is not None:
            if col['Default'].upper() == 'CURRENT_TIMESTAMP':
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            elif col_type == 'TEXT':
                col_def += f" DEFAULT '{col['Default']}'"
            else:
                col_def += f" DEFAULT {col['Default']}"

        columns.append(col_def)

    # 복합 PRIMARY KEY 처리 (단일 PRIMARY KEY는 위에서 처리)
    if len(primary_keys) > 1:
        pk_cols = ', '.join([f"`{pk}`" for pk in primary_keys])
        columns.append(f"PRIMARY KEY ({pk_cols})")

    create_sql = f"CREATE TABLE `{table_name}` ({', '.join(columns)})"

    print(f"Creating table: {table_name}")
    cursor.execute(create_sql)
    sqlite_conn.commit()

def backup_table_data(mysql_conn, sqlite_conn, table_name):
    """테이블 데이터 백업"""
    print(f"Backing up data for table: {table_name}")

    # MySQL에서 데이터 읽기
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = mysql_cursor.fetchall()

    if not rows:
        print(f"  - No data to backup")
        return 0

    # SQLite에 데이터 삽입
    sqlite_cursor = sqlite_conn.cursor()

    # 컬럼 이름 가져오기
    columns = list(rows[0].keys())
    placeholders = ', '.join(['?'] * len(columns))
    column_names = ', '.join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"

    backed_up_count = 0
    batch_size = 1000
    batch_data = []

    for row in rows:
        try:
            values = [row[col] for col in columns]
            batch_data.append(values)

            if len(batch_data) >= batch_size:
                sqlite_cursor.executemany(insert_sql, batch_data)
                sqlite_conn.commit()
                backed_up_count += len(batch_data)
                print(f"  - Backed up {backed_up_count} rows...")
                batch_data = []

        except Exception as e:
            print(f"  - Error backing up row: {e}")
            print(f"    Row data: {dict(row)}")

    # 남은 데이터 커밋
    if batch_data:
        try:
            sqlite_cursor.executemany(insert_sql, batch_data)
            sqlite_conn.commit()
            backed_up_count += len(batch_data)
        except Exception as e:
            print(f"  - Error backing up final batch: {e}")

    print(f"  - Total backed up: {backed_up_count} rows")
    return backed_up_count

def get_mysql_indexes(mysql_conn, table_name):
    """MySQL 인덱스 정보 가져오기"""
    cursor = mysql_conn.cursor()
    cursor.execute(f"SHOW INDEX FROM `{table_name}`")
    indexes = cursor.fetchall()

    # 인덱스를 이름별로 그룹화
    index_dict = {}
    for idx in indexes:
        idx_name = idx['Key_name']
        if idx_name == 'PRIMARY':
            continue  # PRIMARY KEY는 스킵

        if idx_name not in index_dict:
            index_dict[idx_name] = {
                'name': idx_name,
                'unique': not idx['Non_unique'],
                'columns': []
            }

        index_dict[idx_name]['columns'].append(idx['Column_name'])

    return list(index_dict.values())

def create_sqlite_indexes(sqlite_conn, table_name, indexes):
    """SQLite에 인덱스 생성"""
    if not indexes:
        return

    cursor = sqlite_conn.cursor()
    for idx in indexes:
        try:
            unique = "UNIQUE" if idx['unique'] else ""
            columns = ', '.join([f"`{col}`" for col in idx['columns']])
            index_name = f"idx_{table_name}_{idx['name']}"

            sql = f"CREATE {unique} INDEX IF NOT EXISTS `{index_name}` ON `{table_name}` ({columns})"
            print(f"  - Creating index: {index_name}")
            cursor.execute(sql)
        except Exception as e:
            print(f"  - Warning: Could not create index {idx['name']}: {e}")

    sqlite_conn.commit()

def main():
    """메인 백업 프로세스"""
    print("="*60)
    print("MySQL to SQLite Backup")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # MySQL 비밀번호 확인
    if not MYSQL_CONFIG['password']:
        print("ERROR: MySQL password not set in .env file")
        return False

    try:
        # 기존 SQLite DB 백업
        backup_file = create_backup()

        # 데이터베이스 연결
        print("\nConnecting to databases...")
        mysql_conn = get_mysql_connection()
        sqlite_conn = get_sqlite_connection()
        print("  - Connected to MySQL")
        print("  - Connected to SQLite")

        # 테이블 목록 가져오기
        tables = get_mysql_tables(mysql_conn)
        print(f"\nFound {len(tables)} tables to backup")

        total_backed_up = 0

        # 각 테이블 백업
        for table_name in tables:
            # migration_history 테이블은 건너뛰기
            if table_name in ['sb_migration_history', 'alembic_version']:
                print(f"\n--- Skipping table: {table_name} ---")
                continue

            print(f"\n--- Processing table: {table_name} ---")

            # 스키마 가져오기
            schema = get_table_schema_mysql(mysql_conn, table_name)

            # SQLite 테이블 생성
            create_sqlite_table(sqlite_conn, table_name, schema)

            # 데이터 백업
            count = backup_table_data(mysql_conn, sqlite_conn, table_name)
            total_backed_up += count

            # 인덱스 생성
            indexes = get_mysql_indexes(mysql_conn, table_name)
            if indexes:
                print(f"Creating indexes for {table_name}...")
                create_sqlite_indexes(sqlite_conn, table_name, indexes)

        print("\n" + "="*60)
        print(f"Backup completed successfully!")
        print(f"Total rows backed up: {total_backed_up}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        return True

    except pymysql.Error as e:
        print(f"\nMySQL Error: {e}")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'mysql_conn' in locals():
            mysql_conn.close()
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
