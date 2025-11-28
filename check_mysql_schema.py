"""
MySQL 데이터베이스 스키마 확인 스크립트
운영서버에서 직접 실행하여 현재 스키마 상태를 확인합니다.
"""

def check_schema():
    """MySQL 데이터베이스의 주요 테이블 스키마 확인"""
    from auth import get_db

    print("=" * 80)
    print("MySQL 데이터베이스 스키마 확인")
    print("=" * 80)
    print()

    with get_db() as conn:
        # 주요 테이블 목록
        tables_to_check = [
            'sb_rcm',
            'sb_evaluation_sample',
            'sb_design_evaluation_line',
            'sb_design_evaluation_header',
            'sb_operation_evaluation_line'
        ]

        for table_name in tables_to_check:
            print(f"📋 테이블: {table_name}")
            print("-" * 80)

            try:
                # MySQL DESCRIBE 명령 실행
                if conn._is_mysql:
                    result = conn.execute(f"DESCRIBE {table_name}").fetchall()
                    print(f"{'필드명':<30} {'타입':<20} {'Null':<8} {'Key':<8} {'Default':<15}")
                    print("-" * 80)
                    for row in result:
                        field = row.get('Field', '')
                        type_ = row.get('Type', '')
                        null = row.get('Null', '')
                        key = row.get('Key', '')
                        default = row.get('Default', '')
                        print(f"{field:<30} {type_:<20} {null:<8} {key:<8} {str(default):<15}")
                else:
                    # SQLite PRAGMA
                    result = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                    print(f"{'필드명':<30} {'타입':<20} {'Not Null':<10} {'PK':<5}")
                    print("-" * 80)
                    for row in result:
                        col_name = row[1]
                        col_type = row[2]
                        not_null = row[3]
                        pk = row[5]
                        print(f"{col_name:<30} {col_type:<20} {not_null:<10} {pk:<5}")

                print()

            except Exception as e:
                print(f"  ⚠️  오류: {e}")
                print()

        # 특정 컬럼 확인
        print("=" * 80)
        print("주요 컬럼 확인")
        print("=" * 80)
        print()

        checks = [
            ("sb_rcm 테이블에 user_id 컬럼 존재 여부",
             "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_rcm' AND COLUMN_NAME='user_id'",
             "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_rcm') WHERE name='user_id'"),

            ("sb_rcm 테이블에 upload_user_id 컬럼 존재 여부",
             "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_rcm' AND COLUMN_NAME='upload_user_id'",
             "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_rcm') WHERE name='upload_user_id'"),

            ("sb_evaluation_sample 테이블에 attribute0 컬럼 존재 여부",
             "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_evaluation_sample' AND COLUMN_NAME='attribute0'",
             "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_evaluation_sample') WHERE name='attribute0'"),

            ("sb_evaluation_sample 테이블에 evaluation_type 컬럼 존재 여부",
             "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_evaluation_sample' AND COLUMN_NAME='evaluation_type'",
             "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_evaluation_sample') WHERE name='evaluation_type'"),
        ]

        for description, mysql_query, sqlite_query in checks:
            try:
                query = mysql_query if conn._is_mysql else sqlite_query
                result = conn.execute(query).fetchone()
                count = result['cnt'] if hasattr(result, 'get') else result[0]
                status = "✅ 존재" if count > 0 else "❌ 없음"
                print(f"{description}: {status}")
            except Exception as e:
                print(f"{description}: ⚠️  오류 - {e}")

        print()

        # 필요한 마이그레이션 제안
        print("=" * 80)
        print("필요한 마이그레이션")
        print("=" * 80)
        print()

        with get_db() as conn:
            migrations_needed = []

            # upload_user_id 체크
            try:
                query = "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_rcm' AND COLUMN_NAME='upload_user_id'" if conn._is_mysql else "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_rcm') WHERE name='upload_user_id'"
                result = conn.execute(query).fetchone()
                count = result['cnt'] if hasattr(result, 'get') else result[0]
                if count > 0:
                    migrations_needed.append("Migration 024: sb_rcm.upload_user_id → user_id 변경")
            except:
                pass

            # attribute 컬럼 체크
            try:
                query = "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_evaluation_sample' AND COLUMN_NAME='attribute0'" if conn._is_mysql else "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_evaluation_sample') WHERE name='attribute0'"
                result = conn.execute(query).fetchone()
                count = result['cnt'] if hasattr(result, 'get') else result[0]
                if count == 0:
                    migrations_needed.append("Migration 027: sb_evaluation_sample에 attribute0-9 컬럼 추가")
            except:
                pass

            # evaluation_type 컬럼 체크
            try:
                query = "SELECT COUNT(*) as cnt FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='sb_evaluation_sample' AND COLUMN_NAME='evaluation_type'" if conn._is_mysql else "SELECT COUNT(*) as cnt FROM pragma_table_info('sb_evaluation_sample') WHERE name='evaluation_type'"
                result = conn.execute(query).fetchone()
                count = result['cnt'] if hasattr(result, 'get') else result[0]
                if count == 0:
                    migrations_needed.append("Migration 026: sb_evaluation_sample에 evaluation_type 컬럼 추가")
            except:
                pass

            if migrations_needed:
                print("다음 마이그레이션이 필요합니다:")
                for mig in migrations_needed:
                    print(f"  - {mig}")
                print()
                print("migrations/mysql_migration_step_by_step.sql 파일을 실행하세요.")
            else:
                print("✅ 모든 마이그레이션이 적용되었습니다.")

        print()

if __name__ == '__main__':
    check_schema()
