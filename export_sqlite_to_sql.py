"""
SQLite 데이터를 MySQL 호환 SQL 파일로 내보내기

사용법:
python export_sqlite_to_sql.py
"""
import sqlite3
import os
from datetime import datetime

SQLITE_DB = 'snowball.db'
OUTPUT_SQL = f'snowball_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'

def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn

def escape_value(value):
    """MySQL용 값 이스케이프"""
    if value is None:
        return 'NULL'
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        # 문자열 이스케이프
        value = str(value).replace('\\', '\\\\').replace("'", "\\'")
        return f"'{value}'"

def export_to_sql():
    print(f"SQLite to MySQL SQL Export")
    print("="*60)

    if not os.path.exists(SQLITE_DB):
        print(f"ERROR: {SQLITE_DB} not found")
        return

    conn = get_sqlite_connection()
    cursor = conn.cursor()

    # 테이블 목록 가져오기
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        AND name != 'sb_migration_history'
        ORDER BY name
    """)
    tables = [row['name'] for row in cursor.fetchall()]

    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write("-- SQLite to MySQL Export\n")
        f.write(f"-- Generated: {datetime.now()}\n")
        f.write("-- Database: snowball.db\n\n")
        f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

        for table_name in tables:
            print(f"Exporting table: {table_name}")

            # 데이터 조회
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            if not rows:
                print(f"  - No data")
                continue

            # 컬럼 이름
            columns = [desc[0] for desc in cursor.description]
            column_names = ', '.join([f"`{col}`" for col in columns])

            f.write(f"-- Table: {table_name}\n")
            f.write(f"DELETE FROM `{table_name}`;\n")

            # INSERT 문 생성 (배치)
            batch_size = 100
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]

                f.write(f"INSERT INTO `{table_name}` ({column_names}) VALUES\n")

                values_list = []
                for row in batch:
                    values = ', '.join([escape_value(row[col]) for col in columns])
                    values_list.append(f"({values})")

                f.write(',\n'.join(values_list))
                f.write(';\n\n')

            print(f"  - Exported {len(rows)} rows")

        f.write("SET FOREIGN_KEY_CHECKS=1;\n")

    print("="*60)
    print(f"✓ Export completed: {OUTPUT_SQL}")
    print(f"✓ Upload this file to PythonAnywhere and run:")
    print(f"  mysql -u itap -p itap\\$snowball < {OUTPUT_SQL}")

if __name__ == '__main__':
    export_to_sql()
