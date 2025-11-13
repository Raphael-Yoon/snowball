"""
운영 서버에서 누락된 sb_rcm_detail_v 뷰를 수동으로 생성

사용법:
    python migrations/fix_missing_view.py
"""

import sqlite3
import sys
import os

# 상위 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations.versions import create_rcm_detail_view

def main():
    db_path = 'snowball.db'

    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return

    print("=" * 60)
    print("sb_rcm_detail_v 뷰 생성 스크립트")
    print("=" * 60)

    conn = sqlite3.connect(db_path)

    try:
        # 뷰가 이미 있는지 확인
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name='sb_rcm_detail_v'"
        )
        if cursor.fetchone():
            print("\n✅ sb_rcm_detail_v 뷰가 이미 존재합니다.")

            # 확인을 위해 뷰 내용 출력
            cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name='sb_rcm_detail_v'")
            view_sql = cursor.fetchone()[0]
            print("\n현재 뷰 정의:")
            print(view_sql)

            response = input("\n뷰를 재생성하시겠습니까? (y/N): ")
            if response.lower() != 'y':
                print("종료합니다.")
                return

        print("\n[1] sb_rcm_detail_v 뷰 생성 중...")
        create_rcm_detail_view.upgrade(conn)
        conn.commit()

        # 확인
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name='sb_rcm_detail_v'"
        )
        if cursor.fetchone():
            print("\n✅ sb_rcm_detail_v 뷰가 성공적으로 생성되었습니다!")

            # 뷰에서 데이터 조회 테스트
            cursor = conn.execute("SELECT COUNT(*) FROM sb_rcm_detail_v")
            count = cursor.fetchone()[0]
            print(f"   뷰에서 조회된 레코드 수: {count}")
        else:
            print("\n❌ 뷰 생성에 실패했습니다.")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("완료")
    print("=" * 60)


if __name__ == '__main__':
    main()
