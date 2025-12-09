"""
구 평가 테이블 삭제 스크립트
통합 테이블(sb_evaluation_header/line)로 완전 전환 후 실행
"""
import sqlite3
import os

def drop_old_tables():
    db_path = 'snowball.db'

    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 삭제할 테이블 목록
    tables_to_drop = [
        'sb_design_evaluation_header2',
        'sb_design_evaluation_line2',
        'sb_operation_evaluation_header',
        'sb_operation_evaluation_line'
    ]

    print("=" * 60)
    print("구 평가 테이블 삭제 시작")
    print("=" * 60)

    for table in tables_to_drop:
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))

        if cursor.fetchone():
            # 데이터 개수 확인
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"\n📋 {table}: {count}개 row 존재")

            # 테이블 삭제
            cursor.execute(f"DROP TABLE {table}")
            print(f"✅ {table} 삭제 완료")
        else:
            print(f"\n⚠️  {table}: 존재하지 않음 (이미 삭제됨)")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("✅ 모든 구 테이블 삭제 완료")
    print("=" * 60)

    # 남아있는 평가 테이블 확인
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE '%evaluation%'
        ORDER BY name
    """)

    remaining_tables = cursor.fetchall()
    print("\n📊 남아있는 평가 관련 테이블:")
    for table in remaining_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count}개 row")

    conn.close()

if __name__ == '__main__':
    import sys
    # UTF-8 출력 설정
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    response = input("\n구 평가 테이블을 삭제하시겠습니까? (yes/no): ")
    if response.lower() == 'yes':
        drop_old_tables()
    else:
        print("취소되었습니다.")
