"""
Migration 016: sb_evaluation_sample 테이블에 attribute 컬럼 추가 (DEPRECATED - 017로 대체됨)
이 마이그레이션은 더 이상 사용되지 않습니다.
"""

def upgrade(conn):
    """
    DEPRECATED: 이 마이그레이션은 017로 대체되었습니다.
    """
    print("  - Migration 016 is deprecated. Use 017 instead.")
    pass

def downgrade(conn):
    """
    DEPRECATED: 이 마이그레이션은 017로 대체되었습니다.
    """
    print("  - Migration 016 downgrade is deprecated.")
    pass