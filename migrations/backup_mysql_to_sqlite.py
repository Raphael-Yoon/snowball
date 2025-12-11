"""
MySQL에서 SQLite로 데이터 백업
- MySQL의 모든 테이블과 데이터를 SQLite로 복사
- 기존 SQLite 데이터베이스는 백업 후 덮어쓰기
- 운영 환경(PythonAnywhere)에서 로컬로 데이터 백업 시 사용

사용 예시:
    python backup_mysql_to_sqlite.py
    python backup_mysql_to_sqlite.py --output custom_backup.db
"""

import sqlite3
import pymysql
import sys
import os
import shutil
from datetime import datetime

# .env 파일 로드
def load_env():
    """프로젝트 루트의 .env 파일을 로드"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 환경변수에 없으면 .env 값 사용
                    if not os.getenv(key.strip()):
                        os.environ[key.strip()] = value.strip()

load_env()

# 환경 변수에서 MySQL 설정 로드
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'itap.mysql.pythonanywhere-services.com'),
    'user': os.getenv('MYSQL_USER', 'itap'),
    'password': os.getenv('MYSQL_PASSWORD'),  # None if not set
    'database': os.getenv('MYSQL_DATABASE', 'itap$snowball'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'charset': 'utf8mb4',
    'connect_timeout': 10,
}

# SQLite 데이터베이스 경로 (기본값)
DEFAULT_SQLITE_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'snowball.db')

# 백업 제외 테이블 (MySQL 시스템 테이블)
EXCLUDED_TABLES = []


def convert_mysql_type_to_sqlite(mysql_type):
    """MySQL 데이터 타입을 SQLite 타입으로 변환"""
    mysql_type_upper = mysql_type.upper()

    # 정수형
    if any(t in mysql_type_upper for t in ['INT', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT']):
        return 'INTEGER'

    # 실수형
    if any(t in mysql_type_upper for t in ['FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC']):
        return 'REAL'

    # 날짜/시간
    if any(t in mysql_type_upper for t in ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR']):
        return 'TEXT'

    # BLOB
    if any(t in mysql_type_upper for t in ['BLOB', 'BINARY', 'VARBINARY']):
        return 'BLOB'

    # 기본값은 TEXT
    return 'TEXT'


def get_mysql_table_schema(mysql_conn, table_name):
    """MySQL 테이블 스키마 조회"""
    cursor = mysql_conn.cursor()
    cursor.execute(f"DESCRIBE `{table_name}`")
    columns = cursor.fetchall()
    return columns


def backup_sqlite_db(sqlite_path):
    """기존 SQLite 데이터베이스 백업"""
    if os.path.exists(sqlite_path):
        timestamp = datetime.now().strftime('%Y%m%d')
        # snowball.db → snowball_20251211.db
        backup_path = sqlite_path.replace('.db', f'_{timestamp}.db')
        shutil.copy2(sqlite_path, backup_path)
        print(f"📦 기존 DB 백업: {backup_path}")
        return backup_path
    return None


def create_sqlite_table(sqlite_conn, table_name, columns):
    """SQLite 테이블 생성"""
    cursor = sqlite_conn.cursor()

    # 기존 테이블 삭제
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

    # CREATE TABLE 문 생성
    col_definitions = []
    primary_keys = []

    for col in columns:
        # MySQL DESCRIBE 결과: Field, Type, Null, Key, Default, Extra
        if isinstance(col, dict):
            field_name = col['Field']
            field_type = col['Type']
            is_null = col['Null']
            is_key = col['Key']
            default_val = col['Default']
            extra = col['Extra']
        else:
            field_name, field_type, is_null, is_key, default_val, extra = col

        sqlite_type = convert_mysql_type_to_sqlite(field_type)

        # 컬럼 정의
        col_def = f"`{field_name}` {sqlite_type}"

        # PRIMARY KEY
        if is_key == 'PRI':
            if 'auto_increment' in str(extra).lower():
                col_def += " PRIMARY KEY AUTOINCREMENT"
            else:
                col_def += " PRIMARY KEY"
            primary_keys.append(field_name)

        # NOT NULL
        elif is_null == 'NO':
            col_def += " NOT NULL"

        # DEFAULT 값
        if default_val is not None and is_key != 'PRI':
            if default_val == 'CURRENT_TIMESTAMP':
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            elif str(default_val).replace('.', '').replace('-', '').isdigit():
                col_def += f" DEFAULT {default_val}"
            else:
                col_def += f" DEFAULT '{default_val}'"

        col_definitions.append(col_def)

    create_sql = f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(col_definitions) + "\n)"

    print(f"\n📋 테이블 생성: {table_name}")
    cursor.execute(create_sql)
    sqlite_conn.commit()


def migrate_table_data(mysql_conn, sqlite_conn, table_name):
    """테이블 데이터 마이그레이션 (MySQL → SQLite)"""
    # MySQL에서 데이터 조회
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = mysql_cursor.fetchall()

    if not rows:
        print(f"   ⚠️  데이터 없음")
        return 0

    # 컬럼 이름 가져오기
    if isinstance(rows[0], dict):
        columns = list(rows[0].keys())
    else:
        columns = [desc[0] for desc in mysql_cursor.description]

    # SQLite에 데이터 삽입
    sqlite_cursor = sqlite_conn.cursor()

    placeholders = ', '.join(['?'] * len(columns))
    column_names = ', '.join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"

    # 배치 단위로 데이터 삽입
    batch_size = 1000
    total_inserted = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]

        # dict를 tuple로 변환
        if isinstance(batch[0], dict):
            batch_tuples = [tuple(row.values()) for row in batch]
        else:
            batch_tuples = batch

        sqlite_cursor.executemany(insert_sql, batch_tuples)
        sqlite_conn.commit()
        total_inserted += len(batch)

        if len(rows) > batch_size:
            print(f"   📦 {total_inserted}/{len(rows)} rows 삽입 중...")

    print(f"   ✅ {total_inserted} rows 삽입 완료")
    return total_inserted


def backup_mysql_to_sqlite(sqlite_path=None):
    """MySQL → SQLite 백업 메인 함수"""
    # UTF-8 출력 설정 (Windows용)
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    sqlite_path = sqlite_path or DEFAULT_SQLITE_DB

    print("\n" + "=" * 80)
    print("MySQL → SQLite 백업")
    print("=" * 80)
    print(f"MySQL Host: {MYSQL_CONFIG['host']}")
    print(f"MySQL DB: {MYSQL_CONFIG['database']}")
    print(f"SQLite DB: {sqlite_path}")
    print("=" * 80)

    # MySQL 연결
    print(f"\n🔌 MySQL 연결 중... ({MYSQL_CONFIG['host']})")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        print("✅ MySQL 연결 성공")
    except Exception as e:
        print(f"❌ MySQL 연결 실패: {e}")
        return

    # 기존 SQLite DB 백업
    backup_path = backup_sqlite_db(sqlite_path)

    # SQLite 연결
    print(f"🔌 SQLite 연결 중... ({sqlite_path})")
    sqlite_conn = sqlite3.connect(sqlite_path)
    print("✅ SQLite 연결 성공")

    try:
        # MySQL에서 모든 테이블 조회
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SHOW TABLES")
        table_results = mysql_cursor.fetchall()

        # 테이블 이름 추출
        tables = []
        for row in table_results:
            if isinstance(row, dict):
                table_name = list(row.values())[0]
            else:
                table_name = row[0]

            if table_name not in EXCLUDED_TABLES:
                tables.append(table_name)

        print("\n" + "=" * 80)
        print(f"백업 대상 테이블: {len(tables)}개")
        print("=" * 80)

        total_rows = 0
        success_count = 0

        # 각 테이블 백업
        for i, table_name in enumerate(tables, 1):
            print(f"\n[{i}/{len(tables)}] {table_name}")
            print("-" * 80)

            try:
                # 스키마 조회
                columns = get_mysql_table_schema(mysql_conn, table_name)

                # SQLite 테이블 생성
                create_sqlite_table(sqlite_conn, table_name, columns)

                # 데이터 마이그레이션
                row_count = migrate_table_data(mysql_conn, sqlite_conn, table_name)
                total_rows += row_count
                success_count += 1

            except Exception as e:
                print(f"   ❌ 오류 발생: {e}")
                import traceback
                traceback.print_exc()

        # 최종 결과
        print("\n" + "=" * 80)
        print("백업 완료")
        print("=" * 80)
        print(f"✅ 성공: {success_count}/{len(tables)} 테이블")
        print(f"📊 총 백업된 데이터: {total_rows:,} rows")
        print(f"💾 백업 파일: {sqlite_path}")
        if backup_path:
            print(f"📦 이전 백업: {backup_path}")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 백업 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

        # 오류 발생 시 기존 백업 복원
        if backup_path:
            print(f"\n🔄 기존 백업 복원 중...")
            shutil.copy2(backup_path, sqlite_path)
            print(f"✅ 복원 완료")

    finally:
        # 연결 종료
        sqlite_conn.close()
        mysql_conn.close()
        print("\n🔌 데이터베이스 연결 종료")


def verify_backup(sqlite_path=None):
    """백업 결과 검증"""
    sqlite_path = sqlite_path or DEFAULT_SQLITE_DB

    print("\n" + "=" * 80)
    print("백업 결과 검증")
    print("=" * 80)

    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    sqlite_conn = sqlite3.connect(sqlite_path)

    try:
        # MySQL 테이블 목록 및 row 수
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("SHOW TABLES")
        mysql_tables = {}

        for row in mysql_cursor.fetchall():
            if isinstance(row, dict):
                table_name = list(row.values())[0]
            else:
                table_name = row[0]

            if table_name not in EXCLUDED_TABLES:
                mysql_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = mysql_cursor.fetchone()
                if isinstance(count, dict):
                    mysql_tables[table_name] = list(count.values())[0]
                else:
                    mysql_tables[table_name] = count[0]

        # SQLite 테이블 목록 및 row 수
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        sqlite_tables = {}
        for row in sqlite_cursor.fetchall():
            table_name = row[0]
            if table_name != 'sqlite_sequence':
                count = sqlite_conn.execute(f"SELECT COUNT(*) FROM `{table_name}`").fetchone()[0]
                sqlite_tables[table_name] = count

        # 비교 결과 출력
        print(f"\n{'테이블명':<40} {'MySQL':<15} {'SQLite':<15} {'상태':<10}")
        print("-" * 80)

        all_match = True
        for table_name in sorted(mysql_tables.keys()):
            mysql_count = mysql_tables[table_name]
            sqlite_count = sqlite_tables.get(table_name, 0)
            status = "✅" if mysql_count == sqlite_count else "❌"

            if mysql_count != sqlite_count:
                all_match = False

            print(f"{table_name:<40} {mysql_count:<15,} {sqlite_count:<15,} {status:<10}")

        print("-" * 80)
        if all_match:
            print("✅ 모든 테이블 데이터가 정확히 백업되었습니다!")
        else:
            print("⚠️  일부 테이블의 데이터 개수가 일치하지 않습니다.")

    finally:
        sqlite_conn.close()
        mysql_conn.close()


if __name__ == '__main__':
    import argparse

    # UTF-8 출력 설정
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='MySQL에서 SQLite로 데이터 백업')
    parser.add_argument('--output', '-o', help='출력 SQLite 파일 경로 (기본: snowball.db)')
    parser.add_argument('--verify', '-v', action='store_true', help='백업 후 검증 수행')
    args = parser.parse_args()

    # 출력 경로 설정
    output_path = args.output if args.output else DEFAULT_SQLITE_DB

    # 비밀번호가 환경변수에 없으면 입력받기
    if not MYSQL_CONFIG['password']:
        import getpass
        MYSQL_CONFIG['password'] = getpass.getpass("MySQL 비밀번호를 입력하세요: ")

    print("\n💾 MySQL 데이터를 SQLite로 백업합니다.")
    print(f"출력 파일: {output_path}")

    response = input("\n계속하시겠습니까? (yes/no): ")

    if response.lower() == 'yes':
        backup_mysql_to_sqlite(output_path)

        # 검증 수행
        if args.verify:
            verify_backup(output_path)
        else:
            verify_response = input("\n백업 결과를 검증하시겠습니까? (yes/no): ")
            if verify_response.lower() == 'yes':
                verify_backup(output_path)
    else:
        print("취소되었습니다.")
