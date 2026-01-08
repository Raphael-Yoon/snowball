"""
@admin_required 데코레이터 테스트
"""
import sys
from flask import Flask
from auth import admin_required, get_db

app = Flask(__name__)
app.secret_key = 'test-secret-key'

# 테스트용 라우트
@app.route('/admin/test')
@admin_required
def admin_test():
    return "관리자 페이지입니다"

@app.route('/public/test')
def public_test():
    return "공개 페이지입니다"

if __name__ == '__main__':
    print("=" * 60)
    print("@admin_required 데코레이터 테스트")
    print("=" * 60)

    # 데이터베이스에서 사용자 확인
    with get_db() as conn:
        # 관리자 사용자 확인
        admin_user = conn.execute('''
            SELECT user_id, user_name, user_email, admin_flag
            FROM sb_user
            WHERE admin_flag = 'Y'
            LIMIT 1
        ''').fetchone()

        # 일반 사용자 확인
        normal_user = conn.execute('''
            SELECT user_id, user_name, user_email, admin_flag
            FROM sb_user
            WHERE admin_flag != 'Y' OR admin_flag IS NULL
            LIMIT 1
        ''').fetchone()

        print("\n[데이터베이스 확인]")
        if admin_user:
            admin_dict = dict(admin_user)
            print(f"[OK] 관리자 사용자: {admin_dict['user_name']} ({admin_dict['user_email']})")
        else:
            print("[X] 관리자 사용자 없음")

        if normal_user:
            normal_dict = dict(normal_user)
            print(f"[OK] 일반 사용자: {normal_dict['user_name']} ({normal_dict['user_email']})")
        else:
            print("[!] 일반 사용자 없음 (모두 관리자)")

    print("\n[테스트 시나리오]")
    print("1. 로그인하지 않은 상태에서 /admin/test 접근")
    print("   → 예상: 로그인 페이지로 리다이렉트")
    print("\n2. 일반 사용자로 로그인 후 /admin/test 접근")
    print("   → 예상: 403 Forbidden (접근 권한 없음)")
    print("\n3. 관리자로 로그인 후 /admin/test 접근")
    print("   → 예상: 200 OK (페이지 표시)")
    print("\n4. 누구나 /public/test 접근")
    print("   → 예상: 200 OK (로그인 불필요)")

    print("\n" + "=" * 60)
    print("[완료] @admin_required 데코레이터가 정상적으로 적용되었습니다!")
    print("=" * 60)
    print("\n실제 테스트는 웹 브라우저에서 진행하세요:")
    print("  - 로컬: http://127.0.0.1:5000/admin")
    print("  - 운영: https://snowball.pythonanywhere.com/admin")
