#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
증분 마이그레이션 시스템 (MySQL)
데이터베이스 변경사항을 점진적으로 적용합니다.
"""

import pymysql
from datetime import datetime

# MySQL 연결 설정
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'your_username',      # 수정 필요
    'password': 'your_password',  # 수정 필요
    'database': 'snowball',       # 수정 필요
    'charset': 'utf8mb4'
}

class MigrationManager:
    def __init__(self):
        self.conn = None

    def connect(self):
        """데이터베이스 연결"""
        self.conn = pymysql.connect(**DB_CONFIG)
        self._ensure_migration_table()

    def _ensure_migration_table(self):
        """마이그레이션 히스토리 테이블 확인/생성"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sb_migration_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                version VARCHAR(10) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms INT,
                status VARCHAR(20) DEFAULT 'success'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        self.conn.commit()

    def is_applied(self, version):
        """마이그레이션 적용 여부 확인"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sb_migration_history WHERE version = %s",
            (version,)
        )
        return cursor.fetchone()[0] > 0

    def apply_migration(self, version, name, sql_statements):
        """마이그레이션 적용"""
        if self.is_applied(version):
            print(f"[SKIP] {version}: {name} (이미 적용됨)")
            return True

        print(f"[APPLY] {version}: {name}")
        cursor = self.conn.cursor()
        start_time = datetime.now()

        try:
            # SQL 문장 실행
            if isinstance(sql_statements, str):
                sql_statements = [sql_statements]

            for sql in sql_statements:
                if sql.strip():
                    cursor.execute(sql)

            # 마이그레이션 기록
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            cursor.execute("""
                INSERT INTO sb_migration_history (version, name, execution_time_ms, status)
                VALUES (%s, %s, %s, 'success')
            """, (version, name, execution_time))

            self.conn.commit()
            print(f"  ✅ 완료 ({execution_time}ms)")
            return True

        except Exception as e:
            self.conn.rollback()
            print(f"  ❌ 실패: {e}")

            # 실패 기록
            cursor.execute("""
                INSERT INTO sb_migration_history (version, name, status)
                VALUES (%s, %s, 'failed')
            """, (version, name))
            self.conn.commit()

            return False

    def get_applied_migrations(self):
        """적용된 마이그레이션 목록"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT version, name, applied_at, status
            FROM sb_migration_history
            ORDER BY version
        """)
        return cursor.fetchall()

    def close(self):
        """연결 종료"""
        if self.conn:
            self.conn.close()


# ============================================================================
# 마이그레이션 정의
# ============================================================================

MIGRATIONS = [
    # 예시: review_comment 컬럼 추가
    {
        'version': '001',
        'name': 'add_review_comment_to_operation_line',
        'sql': """
            ALTER TABLE sb_operation_evaluation_line
            ADD COLUMN review_comment TEXT
        """
    },
    # 예시: design_comment 컬럼 추가
    {
        'version': '002',
        'name': 'add_design_comment_to_design_line',
        'sql': """
            ALTER TABLE sb_design_evaluation_line
            ADD COLUMN design_comment TEXT
        """
    },
    # 향후 마이그레이션은 여기에 추가...
]


def main():
    """메인 실행"""
    print("=" * 70)
    print("Snowball 증분 마이그레이션 (MySQL)")
    print("=" * 70)
    print(f"데이터베이스: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print()

    manager = MigrationManager()
    manager.connect()

    try:
        # 기존 적용된 마이그레이션 확인
        applied = manager.get_applied_migrations()
        print(f"[INFO] 이미 적용된 마이그레이션: {len(applied)}개")
        print()

        # 새로운 마이그레이션 적용
        print("[INFO] 새로운 마이그레이션 적용 중...")
        print()

        success_count = 0
        skip_count = 0
        fail_count = 0

        for migration in MIGRATIONS:
            if manager.is_applied(migration['version']):
                skip_count += 1
                print(f"[SKIP] {migration['version']}: {migration['name']}")
                continue

            result = manager.apply_migration(
                migration['version'],
                migration['name'],
                migration['sql']
            )

            if result:
                success_count += 1
            else:
                fail_count += 1
                break  # 실패 시 중단

        # 결과 출력
        print()
        print("=" * 70)
        print("마이그레이션 결과")
        print("=" * 70)
        print(f"✅ 성공: {success_count}개")
        print(f"⏭️  건너뜀: {skip_count}개")
        print(f"❌ 실패: {fail_count}개")

        if fail_count > 0:
            print()
            print("⚠️  일부 마이그레이션이 실패했습니다.")
            print("   데이터베이스를 확인하고 문제를 해결한 후 다시 실행하세요.")

    finally:
        manager.close()


if __name__ == '__main__':
    main()
