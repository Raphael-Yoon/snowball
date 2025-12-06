import sys
import os
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

print("=" * 60)
print("sb_evaluation_header에 archived 필드 추가")
print("=" * 60)

with get_db() as conn:
    # archived 컬럼 추가
    try:
        conn.execute('''
            ALTER TABLE sb_evaluation_header
            ADD COLUMN archived INTEGER DEFAULT 0
        ''')
        conn.commit()
        print("[OK] archived 컬럼 추가 완료")
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print("[WARN] archived 컬럼이 이미 존재합니다")
        else:
            print(f"[ERROR] 오류: {e}")
            raise

    # status=5인 레코드를 archived=1로 변경
    result = conn.execute('''
        UPDATE sb_evaluation_header
        SET archived = 1
        WHERE status = 5
    ''')
    conn.commit()
    print(f"[OK] status=5인 레코드를 archived=1로 변경 완료")

print("=" * 60)
print("마이그레이션 완료")
print("=" * 60)
