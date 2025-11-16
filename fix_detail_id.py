"""
sb_rcm_detail 테이블의 detail_id 문제 수정 스크립트

문제: detail_id가 TEXT 타입이고 PRIMARY KEY가 아니며, 모든 값이 NULL
해결: 테이블을 올바른 스키마로 재생성하고 detail_id를 자동 생성
"""

import sqlite3
import sys
import os

# 데이터베이스 경로
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snowball.db')

def fix_detail_id():
    """sb_rcm_detail 테이블의 detail_id 문제 수정"""
    
    print("=" * 70)
    print("sb_rcm_detail 테이블 detail_id 수정 스크립트")
    print("=" * 70)
    print(f"데이터베이스: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"\n[ERROR] 데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # 현재 스키마 확인
        cursor = conn.execute("PRAGMA table_info(sb_rcm_detail)")
        columns = cursor.fetchall()
        
        print("\n[1] 현재 테이블 스키마:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - PK: {col[5]}, NOT NULL: {col[3]}")
        
        # detail_id가 TEXT인지 확인
        detail_id_col = next((col for col in columns if col[1] == 'detail_id'), None)
        if detail_id_col and detail_id_col[2] == 'TEXT':
            print("\n[WARNING] detail_id가 TEXT 타입입니다. 수정이 필요합니다.")
        elif detail_id_col and detail_id_col[5] == 0:
            print("\n[WARNING] detail_id가 PRIMARY KEY가 아닙니다. 수정이 필요합니다.")
        else:
            print("\n[INFO] detail_id 스키마가 정상입니다.")
            return
        
        # 데이터 백업
        print("\n[2] 데이터 백업 중...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_rcm_detail_backup AS
            SELECT * FROM sb_rcm_detail
        ''')
        backup_count = conn.execute("SELECT COUNT(*) FROM sb_rcm_detail_backup").fetchone()[0]
        print(f"  백업 완료: {backup_count}개 레코드")
        
        # 기존 테이블 삭제
        print("\n[3] 기존 테이블 삭제 중...")
        conn.execute('DROP TABLE IF EXISTS sb_rcm_detail')
        
        # 올바른 스키마로 테이블 재생성
        print("\n[4] 올바른 스키마로 테이블 재생성 중...")
        conn.execute('''
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
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (mapped_std_control_id) REFERENCES sb_standard_control (std_control_id),
                FOREIGN KEY (mapped_by) REFERENCES sb_user (user_id),
                FOREIGN KEY (ai_reviewed_by) REFERENCES sb_user (user_id),
                UNIQUE(rcm_id, control_code)
            )
        ''')
        
        # 백업 데이터 복원 (detail_id 제외)
        print("\n[5] 데이터 복원 중...")
        backup_columns = [col[1] for col in conn.execute("PRAGMA table_info(sb_rcm_detail_backup)").fetchall() 
                         if col[1] != 'detail_id']
        new_columns = [col[1] for col in conn.execute("PRAGMA table_info(sb_rcm_detail)").fetchall() 
                      if col[1] != 'detail_id']
        
        # 공통 컬럼만 선택
        common_columns = [col for col in backup_columns if col in new_columns]
        columns_str = ', '.join(common_columns)
        
        conn.execute(f'''
            INSERT INTO sb_rcm_detail ({columns_str})
            SELECT {columns_str}
            FROM sb_rcm_detail_backup
        ''')
        
        restored_count = conn.execute("SELECT COUNT(*) FROM sb_rcm_detail").fetchone()[0]
        print(f"  복원 완료: {restored_count}개 레코드")
        
        # detail_id 확인
        print("\n[6] detail_id 확인 중...")
        test_result = conn.execute('''
            SELECT detail_id, control_code
            FROM sb_rcm_detail
            LIMIT 5
        ''').fetchall()
        
        print("  처음 5개 레코드의 detail_id:")
        for row in test_result:
            print(f"    detail_id: {row[0]}, control_code: {row[1]}")
        
        # 백업 테이블 삭제
        print("\n[7] 백업 테이블 삭제 중...")
        conn.execute('DROP TABLE IF EXISTS sb_rcm_detail_backup')
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("[OK] detail_id 수정 완료!")
        print("=" * 70)
        
        # 뷰 재생성 필요 안내
        print("\n[주의] sb_rcm_detail_v 뷰를 재생성해야 할 수 있습니다.")
        print("       다음 명령을 실행하세요:")
        print("       python migrate.py upgrade --target 015")
    
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        fix_detail_id()
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

