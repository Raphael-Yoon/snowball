"""
운영평가 필드를 sb_evaluation_line 테이블에 추가

추가되는 컬럼:
- exception_count: 예외사항 개수
- mitigating_factors: 경감요소
- population_path: 모집단 파일 경로
- samples_path: 샘플 파일 경로
- test_results_path: 테스트 결과 파일 경로
- population_count: 모집단 개수
"""
import sys
import os
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db

print("=" * 60)
print("운영평가 필드 추가 마이그레이션")
print("=" * 60)

with get_db() as conn:
    # 기존 컬럼 확인
    existing_columns = [dict(r)['name'] for r in conn.execute('PRAGMA table_info(sb_evaluation_line)').fetchall()]
    print(f"\n기존 컬럼: {len(existing_columns)}개")

    columns_to_add = [
        ('exception_count', 'INTEGER DEFAULT 0'),
        ('mitigating_factors', 'TEXT'),
        ('population_path', 'TEXT'),
        ('samples_path', 'TEXT'),
        ('test_results_path', 'TEXT'),
        ('population_count', 'INTEGER'),
    ]

    added_count = 0
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                conn.execute(f'''
                    ALTER TABLE sb_evaluation_line
                    ADD COLUMN {col_name} {col_type}
                ''')
                print(f"[OK] {col_name} 컬럼 추가")
                added_count += 1
            except Exception as e:
                print(f"[ERROR] {col_name} 추가 실패: {e}")
        else:
            print(f"[SKIP] {col_name} 이미 존재")

    conn.commit()

    print(f"\n추가된 컬럼: {added_count}개")

print("=" * 60)
print("마이그레이션 완료")
print("=" * 60)
