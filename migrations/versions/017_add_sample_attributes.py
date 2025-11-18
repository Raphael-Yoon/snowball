"""
운영평가 표본 테이블에 attribute 필드 추가
"""


def upgrade(conn):
    """sb_operation_evaluation_sample 테이블에 attribute0~9 컬럼 추가"""

    try:
        # attribute0~9 컬럼 추가 (실제 증빙 데이터 저장)
        for i in range(10):
            try:
                conn.execute(f'''
                    ALTER TABLE sb_operation_evaluation_sample
                    ADD COLUMN attribute{i} TEXT
                ''')
                print(f"  attribute{i} 컬럼 추가 완료")
            except Exception as e:
                # 이미 존재하는 컬럼이면 무시
                if 'duplicate column name' in str(e).lower():
                    print(f"  attribute{i} 컬럼 이미 존재")
                else:
                    raise

        conn.commit()
        print("  sb_operation_evaluation_sample 테이블 attribute 컬럼 추가 완료")

    except Exception as e:
        print(f"  컬럼 추가 실패: {e}")
        raise


def downgrade(conn):
    """sb_operation_evaluation_sample 테이블에서 attribute0~9 컬럼 삭제"""

    try:
        # SQLite는 ALTER TABLE DROP COLUMN을 지원하지 않으므로
        # 테이블 재생성 필요 (복잡하므로 주석으로만 표시)
        print("  [WARNING] SQLite에서는 컬럼 삭제가 복잡합니다.")
        print("  필요시 수동으로 테이블 재생성 필요")

    except Exception as e:
        print(f"  컬럼 삭제 실패: {e}")
        raise
