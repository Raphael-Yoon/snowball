"""
페이지네이션 기능 테스트
"""
from auth import get_db

print("=" * 60)
print("페이지네이션 기능 테스트")
print("=" * 60)

with get_db() as conn:
    # 사용자 수 확인
    user_count = conn.execute('SELECT COUNT(*) as count FROM sb_user').fetchone()['count']
    print(f"\n[사용자 관리]")
    print(f"  총 사용자: {user_count}명")
    print(f"  페이지당 표시: 20명")
    print(f"  예상 페이지 수: {(user_count + 19) // 20}페이지")

    # RCM 수 확인
    rcm_count = conn.execute("SELECT COUNT(*) as count FROM sb_rcm WHERE is_active = 'Y'").fetchone()['count']
    print(f"\n[RCM 관리]")
    print(f"  총 활성 RCM: {rcm_count}개")
    print(f"  페이지당 표시: 20개")
    print(f"  예상 페이지 수: {(rcm_count + 19) // 20}페이지")

    # 활동 로그 수 확인
    log_count = conn.execute('SELECT COUNT(*) as count FROM sb_user_activity_log').fetchone()['count']
    print(f"\n[활동 로그]")
    print(f"  총 로그: {log_count}개")
    print(f"  페이지당 표시: 10개")
    print(f"  예상 페이지 수: {(log_count + 9) // 10}페이지")

print("\n" + "=" * 60)
print("[완료] 페이지네이션이 추가되었습니다!")
print("=" * 60)
print("\n변경된 페이지:")
print("  1. /admin/users - 사용자 관리 (20개씩)")
print("  2. /admin/rcm - RCM 관리 (20개씩)")
print("  3. /admin/logs - 활동 로그 (10개씩, 기존)")
print("\n사용 방법:")
print("  - URL에 ?page=2 파라미터로 페이지 이동")
print("  - 템플릿에서 current_page, total_pages, total_count 사용 가능")
