#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Snowball 데이터베이스 초기화 스크립트
기존 데이터베이스를 백업하고 최신 스키마로 재생성합니다.
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = 'snowball.db'

def backup_database():
    """데이터베이스 백업"""
    if not os.path.exists(DB_PATH):
        print(f"[INFO] 기존 데이터베이스가 없습니다: {DB_PATH}")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'snowball.db.backup_{timestamp}'

    print(f"[BACKUP] 데이터베이스 백업 중: {backup_path}")
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] 백업 완료!")

    return backup_path

def drop_all_tables(conn):
    """모든 테이블과 뷰 삭제"""
    cursor = conn.cursor()

    # 뷰 삭제
    print("[DROP] 모든 뷰 삭제 중...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    for view in views:
        print(f"  - Dropping view: {view[0]}")
        cursor.execute(f"DROP VIEW IF EXISTS {view[0]}")

    # 테이블 삭제
    print("[DROP] 모든 테이블 삭제 중...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - Dropping table: {table[0]}")
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

    conn.commit()
    print("[DROP] 삭제 완료!")

def create_tables(conn):
    """테이블 생성"""
    cursor = conn.cursor()

    print("[CREATE] 테이블 생성 중...")

    # 1. sb_user
    print("  - sb_user")
    cursor.execute("""
        CREATE TABLE sb_user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            user_name TEXT NOT NULL,
            user_email TEXT NOT NULL,
            phone_number TEXT,
            admin_flag TEXT,
            effective_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            effective_end_date TIMESTAMP,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login_date TIMESTAMP,
            otp_code TEXT,
            otp_expires_at TIMESTAMP,
            otp_attempts INTEGER DEFAULT 0,
            otp_method TEXT,
            ai_review_count INTEGER DEFAULT 0,
            ai_review_limit INTEGER DEFAULT 3
        )
    """)

    # 2. sb_rcm
    print("  - sb_rcm")
    cursor.execute("""
        CREATE TABLE sb_rcm (
            rcm_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_name TEXT NOT NULL,
            description TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER NOT NULL,
            is_active TEXT DEFAULT 'Y',
            completion_date TIMESTAMP DEFAULT NULL,
            original_filename TEXT,
            control_category TEXT DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES sb_user (user_id)
        )
    """)

    # 3. sb_rcm_detail
    print("  - sb_rcm_detail")
    cursor.execute("""
        CREATE TABLE sb_rcm_detail (
            detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            control_code TEXT NOT NULL,
            control_name TEXT NOT NULL,
            control_description TEXT,
            key_control TEXT,
            control_frequency TEXT,
            control_type TEXT,
            control_nature TEXT,
            population TEXT,
            population_completeness_check TEXT,
            population_count TEXT,
            test_procedure TEXT,
            mapped_std_control_id INTEGER,
            mapped_date TIMESTAMP,
            mapped_by INTEGER,
            ai_review_status TEXT DEFAULT 'not_reviewed',
            ai_review_recommendation TEXT,
            ai_reviewed_date TIMESTAMP,
            ai_reviewed_by INTEGER,
            mapping_status TEXT,
            control_category TEXT DEFAULT 'ITGC',
            recommended_sample_size INTEGER DEFAULT NULL,
            process_area TEXT,
            risk_description TEXT,
            risk_impact TEXT,
            risk_likelihood TEXT,
            control_owner TEXT,
            control_performer TEXT,
            evidence_type TEXT,
            attribute0 VARCHAR(100),
            attribute1 VARCHAR(100),
            attribute2 VARCHAR(100),
            attribute3 VARCHAR(100),
            attribute4 VARCHAR(100),
            attribute5 VARCHAR(100),
            attribute6 VARCHAR(100),
            attribute7 VARCHAR(100),
            attribute8 VARCHAR(100),
            attribute9 VARCHAR(100),
            population_attribute_count INTEGER DEFAULT 2,
            FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
            FOREIGN KEY (mapped_std_control_id) REFERENCES sb_standard_control (std_control_id),
            FOREIGN KEY (mapped_by) REFERENCES sb_user (user_id),
            FOREIGN KEY (ai_reviewed_by) REFERENCES sb_user (user_id),
            UNIQUE(rcm_id, control_code)
        )
    """)

    # 4. sb_lookup
    print("  - sb_lookup")
    cursor.execute("""
        CREATE TABLE sb_lookup (
            lookup_code TEXT NOT NULL,
            lookup_name TEXT NOT NULL,
            description TEXT,
            lookup_type TEXT NOT NULL
        )
    """)

    # 5. sb_standard_control
    print("  - sb_standard_control")
    cursor.execute("""
        CREATE TABLE sb_standard_control (
            std_control_id INTEGER PRIMARY KEY AUTOINCREMENT,
            control_category TEXT NOT NULL,
            control_code TEXT NOT NULL,
            control_name TEXT NOT NULL,
            control_description TEXT,
            ai_review_prompt TEXT,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. sb_design_evaluation_header
    print("  - sb_design_evaluation_header")
    cursor.execute("""
        CREATE TABLE sb_design_evaluation_header (
            header_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            evaluation_session TEXT NOT NULL,
            evaluation_status TEXT DEFAULT 'IN_PROGRESS',
            total_controls INTEGER DEFAULT 0,
            evaluated_controls INTEGER DEFAULT 0,
            progress_percentage REAL DEFAULT 0.0,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_date TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
            FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
            UNIQUE(rcm_id, evaluation_session)
        )
    """)

    # 7. sb_design_evaluation_line
    print("  - sb_design_evaluation_line")
    cursor.execute("""
        CREATE TABLE sb_design_evaluation_line (
            line_id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_id INTEGER NOT NULL,
            control_code TEXT NOT NULL,
            control_sequence INTEGER DEFAULT 1,
            description_adequacy TEXT,
            improvement_suggestion TEXT,
            overall_effectiveness TEXT,
            evaluation_evidence TEXT,
            evaluation_rationale TEXT,
            design_comment TEXT,
            recommended_actions TEXT,
            evaluation_date TIMESTAMP DEFAULT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            no_occurrence INTEGER DEFAULT 0,
            no_occurrence_reason TEXT,
            FOREIGN KEY (header_id) REFERENCES sb_design_evaluation_header (header_id) ON DELETE CASCADE,
            UNIQUE(header_id, control_code)
        )
    """)

    # 8. sb_operation_evaluation_header
    print("  - sb_operation_evaluation_header")
    cursor.execute("""
        CREATE TABLE sb_operation_evaluation_header (
            header_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            evaluation_session TEXT NOT NULL,
            design_evaluation_session TEXT NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_date TIMESTAMP DEFAULT NULL,
            evaluation_status TEXT DEFAULT 'IN_PROGRESS',
            evaluated_controls INTEGER DEFAULT 0,
            total_controls INTEGER DEFAULT 0,
            progress_percentage REAL DEFAULT 0.0,
            FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
            FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
            UNIQUE(rcm_id, evaluation_session, design_evaluation_session)
        )
    """)

    # 9. sb_operation_evaluation_line
    print("  - sb_operation_evaluation_line")
    cursor.execute("""
        CREATE TABLE sb_operation_evaluation_line (
            line_id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_id INTEGER NOT NULL,
            control_code TEXT NOT NULL,
            control_sequence INTEGER,
            sample_size INTEGER DEFAULT 0,
            exception_count INTEGER DEFAULT 0,
            exception_details TEXT,
            conclusion TEXT,
            improvement_plan TEXT,
            evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            population_path TEXT DEFAULT NULL,
            samples_path TEXT DEFAULT NULL,
            test_results_path TEXT DEFAULT NULL,
            population_count INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT NULL,
            sample_details TEXT DEFAULT NULL,
            no_occurrence INTEGER DEFAULT 0,
            no_occurrence_reason TEXT,
            mitigating_factors TEXT,
            review_comment TEXT,
            FOREIGN KEY (header_id) REFERENCES sb_operation_evaluation_header(header_id)
        )
    """)

    # 10. sb_evaluation_sample
    print("  - sb_evaluation_sample")
    cursor.execute("""
        CREATE TABLE sb_evaluation_sample (
            sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
            line_id INTEGER,
            sample_number INTEGER,
            evidence TEXT,
            has_exception INTEGER DEFAULT 0,
            mitigation TEXT,
            evaluation_type TEXT DEFAULT 'operation',
            attribute0 TEXT,
            attribute1 TEXT,
            attribute2 TEXT,
            attribute3 TEXT,
            attribute4 TEXT,
            attribute5 TEXT,
            attribute6 TEXT,
            attribute7 TEXT,
            attribute8 TEXT,
            attribute9 TEXT,
            FOREIGN KEY (line_id) REFERENCES sb_operation_evaluation_line (line_id) ON DELETE CASCADE
        )
    """)

    # 11. sb_user_rcm
    print("  - sb_user_rcm")
    cursor.execute("""
        CREATE TABLE sb_user_rcm (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rcm_id INTEGER NOT NULL,
            permission_type TEXT,
            granted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            granted_by INTEGER,
            is_active TEXT,
            last_updated TIMESTAMP
        )
    """)

    # 12. sb_user_activity_log
    print("  - sb_user_activity_log")
    cursor.execute("""
        CREATE TABLE sb_user_activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_email TEXT,
            user_name TEXT,
            action_type TEXT NOT NULL,
            page_name TEXT,
            url_path TEXT,
            ip_address TEXT,
            user_agent TEXT,
            access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            additional_info TEXT
        )
    """)

    # 13. sb_rcm_standard_mapping
    print("  - sb_rcm_standard_mapping")
    cursor.execute("""
        CREATE TABLE sb_rcm_standard_mapping (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            control_code TEXT NOT NULL,
            std_control_id INTEGER NOT NULL,
            mapping_confidence REAL DEFAULT 0,
            mapping_type TEXT,
            mapped_by INTEGER,
            mapping_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active TEXT
        )
    """)

    # 14. sb_rcm_completeness_eval
    print("  - sb_rcm_completeness_eval")
    cursor.execute("""
        CREATE TABLE sb_rcm_completeness_eval (
            eval_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            eval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_controls INTEGER DEFAULT 0,
            mapped_controls INTEGER DEFAULT 0,
            missing_fields_count INTEGER DEFAULT 0,
            completeness_score REAL DEFAULT 0,
            eval_details TEXT,
            eval_by INTEGER
        )
    """)

    # 15. sb_internal_assessment
    print("  - sb_internal_assessment")
    cursor.execute("""
        CREATE TABLE sb_internal_assessment (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            evaluation_session TEXT,
            step INTEGER NOT NULL,
            progress_data TEXT,
            status TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 16. sb_request
    print("  - sb_request")
    cursor.execute("""
        CREATE TABLE sb_request (
            request_id INTEGER,
            request_type TEXT,
            request_file TEXT,
            request_date TEXT,
            return_yn TEXT,
            client_name TEXT,
            email_address TEXT,
            request_content TEXT
        )
    """)

    # 17. sb_user_request
    print("  - sb_user_request")
    cursor.execute("""
        CREATE TABLE sb_user_request (
            company_name TEXT,
            user_name TEXT,
            user_email TEXT,
            interface_yn TEXT,
            creation_date TEXT,
            request_id INTEGER
        )
    """)

    # 18. sb_user_log
    print("  - sb_user_log")
    cursor.execute("""
        CREATE TABLE sb_user_log (
            user_id INTEGER,
            log_date TEXT,
            log_type TEXT
        )
    """)

    # 19. sb_migration_history
    print("  - sb_migration_history")
    cursor.execute("""
        CREATE TABLE sb_migration_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INTEGER,
            status TEXT DEFAULT 'success'
        )
    """)

    conn.commit()
    print("[CREATE] 테이블 생성 완료!")

def create_views(conn):
    """뷰 생성"""
    cursor = conn.cursor()

    print("[CREATE] 뷰 생성 중...")

    # sb_rcm_detail_v
    print("  - sb_rcm_detail_v")
    cursor.execute("""
        CREATE VIEW sb_rcm_detail_v AS
        SELECT
            d.detail_id,
            d.rcm_id,
            d.control_code,
            d.control_name,
            d.control_description,
            COALESCE(lk.lookup_name, d.key_control) AS key_control,
            COALESCE(lf.lookup_name, d.control_frequency) AS control_frequency,
            COALESCE(lt.lookup_name, d.control_type) AS control_type,
            COALESCE(ln.lookup_name, d.control_nature) AS control_nature,
            d.population,
            d.population_completeness_check,
            d.population_count,
            d.test_procedure,
            d.mapped_std_control_id,
            d.mapped_date,
            d.mapped_by,
            d.ai_review_status,
            d.ai_review_recommendation,
            d.ai_reviewed_date,
            d.ai_reviewed_by,
            d.mapping_status,
            d.control_category,
            d.recommended_sample_size,
            d.population_attribute_count,
            d.attribute0,
            d.attribute1,
            d.attribute2,
            d.attribute3,
            d.attribute4,
            d.attribute5,
            d.attribute6,
            d.attribute7,
            d.attribute8,
            d.attribute9,
            d.control_frequency AS control_frequency_code,
            d.control_type AS control_type_code,
            d.control_nature AS control_nature_code,
            lf.lookup_name AS control_frequency_name,
            lt.lookup_name AS control_type_name,
            ln.lookup_name AS control_nature_name
        FROM sb_rcm_detail d
        LEFT JOIN sb_lookup lk ON lk.lookup_type = 'key_control'
            AND UPPER(lk.lookup_code) = UPPER(d.key_control)
        LEFT JOIN sb_lookup lf ON lf.lookup_type = 'control_frequency'
            AND UPPER(lf.lookup_code) = UPPER(d.control_frequency)
        LEFT JOIN sb_lookup lt ON lt.lookup_type = 'control_type'
            AND UPPER(lt.lookup_code) = UPPER(d.control_type)
        LEFT JOIN sb_lookup ln ON ln.lookup_type = 'control_nature'
            AND UPPER(ln.lookup_code) = UPPER(d.control_nature)
    """)

    conn.commit()
    print("[CREATE] 뷰 생성 완료!")

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("Snowball 데이터베이스 초기화")
    print("=" * 70)
    print()

    # 1. 백업
    backup_path = backup_database()

    # 2. 데이터베이스 연결
    print(f"[CONNECT] 데이터베이스 연결 중: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    try:
        # 3. 기존 테이블/뷰 삭제
        drop_all_tables(conn)

        # 4. 테이블 생성
        create_tables(conn)

        # 5. 뷰 생성
        create_views(conn)

        # 6. 마이그레이션 히스토리 기록
        print("[MIGRATION] 마이그레이션 히스토리 기록 중...")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sb_migration_history (version, name, status)
            VALUES ('000', 'initial_database_setup', 'success')
        """)
        conn.commit()

        print()
        print("=" * 70)
        print("✅ 데이터베이스 초기화 완료!")
        print("=" * 70)

        if backup_path:
            print(f"📁 백업 파일: {backup_path}")

        print()
        print("다음 단계:")
        print("1. 서버 재시작: python snowball.py")
        print("2. 기본 데이터 입력 (사용자, Lookup 등)")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        if backup_path:
            print(f"\n백업에서 복원하려면:")
            print(f"  cp {backup_path} {DB_PATH}")
        raise

    finally:
        conn.close()

if __name__ == '__main__':
    main()
