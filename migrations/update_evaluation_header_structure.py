import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

print("=" * 60)
print("sb_evaluation_header 테이블 구조 변경")
print("=" * 60)

with get_db() as conn:
    print("\n[1/5] 현재 테이블 구조 확인")
    result = conn.execute('PRAGMA table_info(sb_evaluation_header)').fetchall()
    for r in result:
        print(f"  {r['name']} - {r['type']}")
    
    print("\n[2/5] 기존 데이터 확인")
    count_result = conn.execute('SELECT COUNT(*) FROM sb_evaluation_header').fetchone()
    count = count_result[0] if count_result else 0
    print(f"  총 {count}개 레코드")
    
    # 샘플 데이터 확인
    samples = conn.execute('SELECT * FROM sb_evaluation_header LIMIT 5').fetchall()
    for s in samples:
        s_dict = dict(s)
        print(f"  ID={s_dict.get('header_id', 'N/A')}, session={s_dict.get('evaluation_session', 'N/A')}, status={s_dict.get('status', 'N/A')}")
    
    print("\n[3/5] 새 테이블 생성 (sb_evaluation_header_new)")
    conn.execute('DROP TABLE IF EXISTS sb_evaluation_header_new')
    conn.execute('''
        CREATE TABLE sb_evaluation_header_new (
            header_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rcm_id INTEGER NOT NULL,
            evaluation_name TEXT NOT NULL,
            status INTEGER DEFAULT 0,
            progress INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rcm_id) REFERENCES sb_rcm(rcm_id)
        )
    ''')
    print("  새 테이블 생성 완료")
    
    print("\n[4/5] 데이터 마이그레이션")
    # 기존 데이터 조회
    old_data = conn.execute('SELECT * FROM sb_evaluation_header').fetchall()
    
    migrated = 0
    for row in old_data:
        row_dict = dict(row)
        
        # status 변환: 'IN_PROGRESS' -> 0, 'COMPLETED' -> 4 등
        old_status = row_dict.get('status', 'IN_PROGRESS')
        new_status = 0  # 기본값
        
        if old_status == 'COMPLETED':
            new_status = 4
        elif old_status == 'IN_PROGRESS':
            # evaluation_session으로 설계/운영 판단
            eval_session = row_dict.get('evaluation_session', '')
            if eval_session and eval_session.startswith('OP_'):
                new_status = 2  # 운영 시작
            else:
                new_status = 0  # 설계 시작
        
        # 데이터 삽입
        conn.execute('''
            INSERT INTO sb_evaluation_header_new 
            (header_id, rcm_id, evaluation_name, status, progress, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            row_dict.get('header_id'),
            row_dict.get('rcm_id'),
            row_dict.get('evaluation_session', ''),  # evaluation_session -> evaluation_name
            new_status,
            row_dict.get('progress', 0),
            row_dict.get('created_at'),
            row_dict.get('last_updated')
        ))
        migrated += 1
    
    print(f"  {migrated}개 레코드 마이그레이션 완료")
    
    print("\n[5/5] 테이블 교체")
    conn.execute('DROP TABLE sb_evaluation_header')
    conn.execute('ALTER TABLE sb_evaluation_header_new RENAME TO sb_evaluation_header')
    conn.commit()
    print("  테이블 교체 완료")
    
    print("\n[완료] 변경된 테이블 구조 확인")
    result = conn.execute('PRAGMA table_info(sb_evaluation_header)').fetchall()
    for r in result:
        print(f"  {r['name']} - {r['type']}")
    
    print("\n[완료] 샘플 데이터 확인")
    samples = conn.execute('SELECT * FROM sb_evaluation_header LIMIT 5').fetchall()
    for s in samples:
        s_dict = dict(s)
        print(f"  ID={s_dict.get('header_id')}, name={s_dict.get('evaluation_name')}, status={s_dict.get('status')}")

print("\n" + "=" * 60)
print("테이블 구조 변경 완료!")
print("=" * 60)
