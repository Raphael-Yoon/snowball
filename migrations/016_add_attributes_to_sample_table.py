"""
Migration 016: sb_operation_evaluation_sample 테이블에 attribute 컬럼 추가
"""

def upgrade(conn):
    """
    sb_operation_evaluation_sample 테이블에 attribute01부터 attribute10까지의 컬럼을 추가합니다.
    """
    cursor = conn.cursor()
    
    # 현재 테이블의 컬럼 정보 가져오기
    cursor.execute("PRAGMA table_info(sb_operation_evaluation_sample)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # 추가할 컬럼들
    for i in range(1, 11):
        col_name = f'attribute{i:02d}'
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE sb_operation_evaluation_sample ADD COLUMN {col_name} TEXT")
                print(f"  - Added column '{col_name}' to 'sb_operation_evaluation_sample' table.")
            except Exception as e:
                print(f"  - Warning: Could not add column '{col_name}'. It might already exist. Error: {e}")
    
    conn.commit()

def downgrade(conn):
    """
    sb_operation_evaluation_sample 테이블에서 attribute 컬럼들을 제거합니다.
    SQLite에서는 컬럼 삭제를 직접 지원하지 않으므로, 테이블을 재생성하는 방식을 사용합니다.
    """
    cursor = conn.cursor()
    
    try:
        # 1. 기존 테이블을 백업 테이블로 이름 변경
        cursor.execute("ALTER TABLE sb_operation_evaluation_sample RENAME TO sb_operation_evaluation_sample_old")
        
        # 2. 새 스키마로 테이블 재생성 (attribute 컬럼 제외)
        cursor.execute('''
            CREATE TABLE sb_operation_evaluation_sample (
                sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                line_id INTEGER,
                sample_number INTEGER,
                evidence TEXT,
                has_exception INTEGER,
                mitigation TEXT,
                request_number TEXT,
                requester_name TEXT,
                requester_department TEXT,
                approver_name TEXT,
                approver_department TEXT,
                approval_date TEXT,
                FOREIGN KEY (line_id) REFERENCES sb_operation_evaluation_line (line_id)
            )
        ''')
        
        # 3. 백업 테이블에서 데이터 복사
        cursor.execute('''
            INSERT INTO sb_operation_evaluation_sample (sample_id, line_id, sample_number, evidence, has_exception, mitigation, request_number, requester_name, requester_department, approver_name, approver_department, approval_date)
            SELECT sample_id, line_id, sample_number, evidence, has_exception, mitigation, request_number, requester_name, requester_department, approver_name, approver_department, approval_date FROM sb_operation_evaluation_sample_old
        ''')
        
        # 4. 백업 테이블 삭제
        cursor.execute("DROP TABLE sb_operation_evaluation_sample_old")
        
        conn.commit()
        print("  - Downgraded 'sb_operation_evaluation_sample' table (removed attribute columns).")
    except Exception as e:
        print(f"  - Error during downgrade: {e}")
        conn.rollback()