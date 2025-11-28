"""
SQLite와 MySQL 스키마 비교 도구

개발환경(SQLite)과 운영환경(MySQL) 간의 스키마 차이를 분석하고
필요한 마이그레이션 SQL을 자동 생성합니다.
"""

import sqlite3
import sys
import os

def get_sqlite_schema():
    """SQLite 데이터베이스의 스키마 정보 추출"""
    conn = sqlite3.connect('snowball.db')
    cursor = conn.cursor()

    tables = {}

    # 모든 테이블 목록
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    table_names = [row[0] for row in cursor.fetchall()]

    for table_name in table_names:
        if table_name.startswith('sqlite_'):
            continue

        # 각 테이블의 컬럼 정보
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {}
        for row in cursor.fetchall():
            col_id, col_name, col_type, not_null, default_val, pk = row
            columns[col_name] = {
                'type': col_type,
                'not_null': not_null,
                'default': default_val,
                'primary_key': pk
            }
        tables[table_name] = columns

    conn.close()
    return tables

def get_mysql_schema():
    """MySQL 데이터베이스의 스키마 정보 추출"""
    try:
        import pymysql
    except ImportError:
        print("오류: PyMySQL 패키지가 설치되지 않았습니다.")
        print("운영서버의 MySQL 정보를 수동으로 입력하세요.")
        return None

    # MySQL 연결 정보 입력 또는 환경 변수 사용
    host = input("MySQL 호스트 (기본: localhost): ").strip() or 'localhost'
    user = input("MySQL 사용자명: ").strip()
    password = input("MySQL 비밀번호: ").strip()
    database = input("MySQL 데이터베이스명: ").strip()
    port = int(input("MySQL 포트 (기본: 3306): ").strip() or '3306')

    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset='utf8mb4'
        )

        cursor = conn.cursor()

        tables = {}

        # 모든 테이블 목록
        cursor.execute("SHOW TABLES")
        table_names = [row[0] for row in cursor.fetchall()]

        for table_name in table_names:
            # 각 테이블의 컬럼 정보
            cursor.execute(f"DESCRIBE {table_name}")
            columns = {}
            for row in cursor.fetchall():
                col_name, col_type, null, key, default, extra = row
                columns[col_name] = {
                    'type': col_type,
                    'null': null,
                    'key': key,
                    'default': default,
                    'extra': extra
                }
            tables[table_name] = columns

        conn.close()
        return tables

    except Exception as e:
        print(f"MySQL 접속 오류: {e}")
        return None

def normalize_type(sqlite_type):
    """SQLite 타입을 MySQL 타입으로 변환"""
    type_map = {
        'INTEGER': 'INT',
        'TEXT': 'TEXT',
        'REAL': 'FLOAT',
        'BLOB': 'BLOB',
        'TIMESTAMP': 'TIMESTAMP'
    }

    sqlite_type_upper = sqlite_type.upper()
    for key, value in type_map.items():
        if key in sqlite_type_upper:
            return value

    return 'TEXT'  # 기본값

def compare_schemas(sqlite_schema, mysql_schema):
    """두 스키마를 비교하고 차이점을 출력"""

    print("=" * 80)
    print("SQLite vs MySQL 스키마 비교 결과")
    print("=" * 80)
    print()

    migration_sqls = []

    # SQLite에만 있는 테이블
    sqlite_only = set(sqlite_schema.keys()) - set(mysql_schema.keys())
    if sqlite_only:
        print("⚠️  SQLite에만 존재하는 테이블:")
        for table in sorted(sqlite_only):
            print(f"    - {table}")
        print()

    # MySQL에만 있는 테이블
    mysql_only = set(mysql_schema.keys()) - set(sqlite_schema.keys())
    if mysql_only:
        print("⚠️  MySQL에만 존재하는 테이블:")
        for table in sorted(mysql_only):
            print(f"    - {table}")
        print()

    # 공통 테이블의 컬럼 비교
    common_tables = set(sqlite_schema.keys()) & set(mysql_schema.keys())

    for table_name in sorted(common_tables):
        sqlite_cols = sqlite_schema[table_name]
        mysql_cols = mysql_schema[table_name]

        # SQLite에만 있는 컬럼 (MySQL에 추가해야 함)
        sqlite_only_cols = set(sqlite_cols.keys()) - set(mysql_cols.keys())

        # MySQL에만 있는 컬럼
        mysql_only_cols = set(mysql_cols.keys()) - set(sqlite_cols.keys())

        # 컬럼명이 다른 경우 (rename 후보)
        renamed_candidates = []

        if sqlite_only_cols or mysql_only_cols:
            print(f"📋 테이블: {table_name}")
            print("-" * 80)

            if sqlite_only_cols:
                print(f"  ✅ SQLite에만 있는 컬럼 (MySQL에 추가 필요):")
                for col in sorted(sqlite_only_cols):
                    col_info = sqlite_cols[col]
                    mysql_type = normalize_type(col_info['type'])
                    not_null = 'NOT NULL' if col_info['not_null'] else ''
                    default = f"DEFAULT '{col_info['default']}'" if col_info['default'] else ''

                    print(f"      - {col}: {col_info['type']} ({mysql_type})")

                    # Migration SQL 생성
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col} {mysql_type}"
                    if not_null:
                        sql += f" {not_null}"
                    if default:
                        sql += f" {default}"
                    sql += ";"

                    migration_sqls.append(sql)
                print()

            if mysql_only_cols:
                print(f"  ⚠️  MySQL에만 있는 컬럼:")
                for col in sorted(mysql_only_cols):
                    col_info = mysql_cols[col]
                    print(f"      - {col}: {col_info['type']}")
                print()

            # 컬럼명 변경 감지 (예: upload_user_id -> user_id)
            for sqlite_col in sqlite_only_cols:
                for mysql_col in mysql_only_cols:
                    # 비슷한 이름 찾기 (간단한 휴리스틱)
                    if 'user_id' in sqlite_col and 'user_id' in mysql_col:
                        renamed_candidates.append((mysql_col, sqlite_col))
                    elif sqlite_col.replace('_', '') == mysql_col.replace('_', ''):
                        renamed_candidates.append((mysql_col, sqlite_col))

            if renamed_candidates:
                print(f"  🔄 컬럼명 변경 후보:")
                for old_name, new_name in renamed_candidates:
                    print(f"      {old_name} → {new_name}")
                    mysql_type = normalize_type(sqlite_cols[new_name]['type'])
                    sql = f"ALTER TABLE {table_name} CHANGE COLUMN {old_name} {new_name} {mysql_type};"
                    migration_sqls.append(sql)
                print()

    print("=" * 80)
    print("생성된 마이그레이션 SQL")
    print("=" * 80)
    print()

    if migration_sqls:
        for sql in migration_sqls:
            print(sql)
        print()

        # SQL 파일로 저장
        with open('migrations/auto_generated_migration.sql', 'w', encoding='utf-8') as f:
            f.write("-- 자동 생성된 MySQL 마이그레이션 스크립트\n")
            f.write("-- 생성일: " + str(sys.argv[0]) + "\n\n")
            f.write("START TRANSACTION;\n\n")
            for sql in migration_sqls:
                f.write(sql + "\n")
            f.write("\nCOMMIT;\n")

        print(f"✅ 마이그레이션 SQL이 'migrations/auto_generated_migration.sql'에 저장되었습니다.")
    else:
        print("✅ 스키마가 동일합니다. 마이그레이션이 필요하지 않습니다.")

    print()

def main():
    print("SQLite 스키마 로딩 중...")
    sqlite_schema = get_sqlite_schema()

    print("MySQL 스키마 로딩 중...")
    mysql_schema = get_mysql_schema()

    if mysql_schema is None:
        print("MySQL 스키마를 가져올 수 없습니다. db_config.json을 확인하세요.")
        return

    compare_schemas(sqlite_schema, mysql_schema)

if __name__ == '__main__':
    main()
