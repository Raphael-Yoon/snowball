import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

print("=" * 60)
print("sb_evaluation_header에서 user_id 컬럼 제거")
print("=" * 60)

with get_db() as conn:
    print("\n[1/5] 현재 테이블 구조 확인")
    result = conn.execute('PRAGMA table_info(sb_evaluation_header)').fetchall()
    has_user_id = any(r['name'] == 'user_id' for r in result)

    if not has_user_id:
        print("  user_id 컬럼이 이미 존재하지 않습니다. 마이그레이션을 건너뜁니다.")
        sys.exit(0)

    for r in result:
        print(f"  {r['name']} - {r['type']}")

    print("\n[2/5] 기존 데이터 확인")
    count_result = conn.execute('SELECT COUNT(*) FROM sb_evaluation_header').fetchone()
    count = count_result[0] if count_result else 0
    print(f"  총 {count}개 레코드")

    print("\n[3/5] 새 테이블 생성 (sb_evaluation_header_new, user_id 제외)")
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

    print("\n[4/5] 데이터 마이그레이션 (user_id 제외)")
    # 기존 데이터 조회
    old_data = conn.execute('SELECT * FROM sb_evaluation_header').fetchall()

    migrated = 0
    for row in old_data:
        row_dict = dict(row)

        # 데이터 삽입 (user_id 제외)
        conn.execute('''
            INSERT INTO sb_evaluation_header_new
            (header_id, rcm_id, evaluation_name, status, progress, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            row_dict['header_id'],
            row_dict['rcm_id'],
            row_dict['evaluation_name'],
            row_dict['status'],
            row_dict['progress'],
            row_dict['created_at'],
            row_dict['last_updated']
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
        print(f"  ID={s_dict.get('header_id')}, rcm_id={s_dict.get('rcm_id')}, name={s_dict.get('evaluation_name')}, status={s_dict.get('status')}")

print("\n" + "=" * 60)
print("user_id 컬럼 제거 완료!")
print("=" * 60)
