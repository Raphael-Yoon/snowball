"""
인증 및 권한(auth.py) 단위 테스트 스크립트
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
    import auth
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

from test.link5_test import TestStatus, TestResult

class AuthTestSuite:
    """인증 및 권한 단위 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80)
        print("Auth 인증 및 권한 단위 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
        ])

        self._run_category("2. OTP 로직 검증", [
            self.test_otp_generation,
            self.test_otp_verification_success,
            self.test_otp_verification_expired,
            self.test_otp_verification_wrong_code,
            self.test_otp_max_attempts,
        ])

        self._run_category("3. 권한 및 세션 검증", [
            self.test_login_required_decorator,
            self.test_admin_required_decorator,
            self.test_rcm_access_control,
        ])

        self._run_category("4. AI 검토 제한 검증", [
            self.test_ai_review_limit,
        ])

        return self._print_final_report()

    def _run_category(self, category_name: str, tests: List):
        print(f"\n{'=' * 80}")
        print(f"{category_name}")
        print(f"{'=' * 80}")

        for test_func in tests:
            result = TestResult(test_func.__name__, category_name)
            self.results.append(result)

            try:
                result.start()
                print(f"\n{TestStatus.RUNNING.value} {test_func.__name__}...", end=" ")
                test_func(result)
                if result.status == TestStatus.RUNNING:
                    result.pass_test()
                print(f"\r{result}")

                if result.details:
                    for detail in result.details:
                        print(f"    ℹ️  {detail}")

            except Exception as e:
                result.fail_test(f"예외 발생: {str(e)}")
                print(f"\r{result}")
                print(f"    ❌ {result.message}")

    # =========================================================================
    # 1. 환경 및 설정 검증
    # =========================================================================

    def test_environment_setup(self, result: TestResult):
        """auth 모듈 로드 확인"""
        if hasattr(auth, 'verify_otp'):
            result.pass_test("auth 모듈이 정상적으로 로드되었습니다.")
        else:
            result.fail_test("auth 모듈 로드 실패")

    # =========================================================================
    # 2. OTP 로직 검증
    # =========================================================================

    def test_otp_generation(self, result: TestResult):
        """OTP 생성 규칙 확인"""
        otp = auth.generate_otp()
        if len(otp) == 6 and otp.isdigit():
            result.add_detail(f"생성된 OTP: {otp}")
            result.pass_test("6자리 숫자 OTP가 정상 생성됩니다.")
        else:
            result.fail_test(f"잘못된 OTP 형식: {otp}")

    @patch('auth.get_db')
    def test_otp_verification_success(self, result: TestResult, mock_db):
        """정확한 OTP 입력 시 성공 확인"""
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        
        # 가짜 사용자 데이터
        mock_conn.execute.return_value.fetchone.return_value = {
            'user_id': 1,
            'user_email': 'test@example.com',
            'otp_code': '123456',
            'otp_expires_at': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'otp_attempts': 0,
            'effective_start_date': '2000-01-01 00:00:00',
            'effective_end_date': None
        }

        success, user = auth.verify_otp('test@example.com', '123456')
        
        if success:
            result.pass_test("정확한 OTP 입력 시 인증에 성공합니다.")
        else:
            result.fail_test(f"인증 실패: {user}")

    @patch('auth.get_db')
    def test_otp_verification_expired(self, result: TestResult, mock_db):
        """만료된 OTP 입력 시 실패 확인"""
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        
        mock_conn.execute.return_value.fetchone.return_value = {
            'user_id': 1,
            'user_email': 'test@example.com',
            'otp_code': '123456',
            'otp_expires_at': (datetime.now() - timedelta(minutes=1)).isoformat(),
            'otp_attempts': 0,
            'effective_start_date': '2000-01-01 00:00:00',
            'effective_end_date': None
        }

        success, message = auth.verify_otp('test@example.com', '123456')
        
        if not success and "만료" in message:
            result.pass_test("만료된 OTP를 정확히 감지합니다.")
        else:
            result.fail_test(f"잘못된 응답: {message}")

    @patch('auth.get_db')
    def test_otp_verification_wrong_code(self, result: TestResult, mock_db):
        """틀린 OTP 입력 시 실패 확인"""
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        
        mock_conn.execute.return_value.fetchone.return_value = {
            'user_id': 1,
            'user_email': 'test@example.com',
            'otp_code': '123456',
            'otp_expires_at': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'otp_attempts': 0,
            'effective_start_date': '2000-01-01 00:00:00',
            'effective_end_date': None
        }

        success, message = auth.verify_otp('test@example.com', '000000')
        
        if not success and "틀렸습니다" in message:
            result.pass_test("틀린 OTP를 정확히 감지합니다.")
        else:
            result.fail_test(f"잘못된 응답: {message}")

    @patch('auth.get_db')
    def test_otp_max_attempts(self, result: TestResult, mock_db):
        """3회 이상 실패 시 차단 확인"""
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        
        mock_conn.execute.return_value.fetchone.return_value = {
            'user_id': 1,
            'user_email': 'test@example.com',
            'otp_code': '123456',
            'otp_expires_at': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'otp_attempts': 3,
            'effective_start_date': '2000-01-01 00:00:00',
            'effective_end_date': None
        }

        success, message = auth.verify_otp('test@example.com', '123456')
        
        if not success and "초과" in message:
            result.pass_test("최대 시도 횟수 초과 시 차단합니다.")
        else:
            result.fail_test(f"잘못된 응답: {message}")

    # =========================================================================
    # 3. 권한 및 세션 검증
    # =========================================================================

    def test_login_required_decorator(self, result: TestResult):
        """로그인 필수 데코레이터 작동 확인"""
        @auth.login_required
        def protected_route():
            return "OK"

        with self.app.test_request_context():
            # 세션에 user_id가 없는 경우
            response = protected_route()
            if response.status_code == 302: # 로그인 페이지로 리다이렉트
                result.add_detail("✓ 미로그인 시 리다이렉트 확인")
                result.pass_test("login_required 데코레이터가 정상 작동합니다.")
            else:
                result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    @patch('auth.get_current_user')
    def test_admin_required_decorator(self, result: TestResult, mock_get_user):
        """관리자 권한 데코레이터 작동 확인"""
        # 1. 일반 사용자인 경우
        mock_get_user.return_value = {'admin_flag': 'N'}
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_info'] = {'admin_flag': 'N'}

        # 실제 라우트를 통해 테스트
        @self.app.route('/test_admin_only')
        @auth.admin_required
        def test_admin_only():
            return "OK"

        response = self.client.get('/test_admin_only')
        
        if response.status_code == 403:
            result.add_detail("✓ 일반 사용자 접근 차단 확인 (403)")
            result.pass_test("admin_required 데코레이터가 정상 작동합니다.")
        else:
            result.fail_test(f"잘못된 응답: {response.status_code}")

    @patch('auth.get_db')
    def test_rcm_access_control(self, result: TestResult, mock_db):
        """RCM 접근 권한 로직 확인"""
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        
        # 1. 관리자인 경우
        mock_conn.execute.return_value.fetchone.return_value = {'admin_flag': 'Y'}
        if auth.has_rcm_access(1, 100):
            result.add_detail("✓ 관리자 모든 RCM 접근 허용")
        else:
            result.fail_test("관리자 접근 거부됨")
            return

        # 2. 일반 사용자 - 권한 있음
        mock_conn.execute.return_value.fetchone.side_effect = [{'admin_flag': 'N'}, {'1': 1}]
        if auth.has_rcm_access(1, 100):
            result.add_detail("✓ 권한 있는 일반 사용자 접근 허용")
        else:
            result.fail_test("권한 있는 사용자 접근 거부됨")
            return

        result.pass_test("RCM 접근 제어 로직이 정상입니다.")

    # =========================================================================
    # 4. AI 검토 제한 검증
    # =========================================================================

    @patch('auth.get_db')
    def test_ai_review_limit(self, result: TestResult, mock_db):
        """AI 검토 횟수 제한 로직 확인"""
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        
        # 1. 제한 도달
        mock_conn.execute.return_value.fetchone.return_value = {'ai_review_count': 3, 'ai_review_limit': 3}
        can_review, count, limit = auth.check_ai_review_limit('test@example.com')
        if not can_review:
            result.add_detail(f"✓ 제한 도달 시 차단 확인 ({count}/{limit})")
        else:
            result.fail_test("제한 도달 시에도 허용됨")
            return

        # 2. 여유 있음
        mock_conn.execute.return_value.fetchone.return_value = {'ai_review_count': 1, 'ai_review_limit': 3}
        can_review, count, limit = auth.check_ai_review_limit('test@example.com')
        if can_review:
            result.add_detail(f"✓ 여유 있을 시 허용 확인 ({count}/{limit})")
        else:
            result.fail_test("여유 있음에도 차단됨")
            return

        result.pass_test("AI 검토 제한 로직이 정상입니다.")

    # =========================================================================
    # 리포트 생성
    # =========================================================================

    def _print_final_report(self):
        print("\n" + "=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)

        status_counts = {status: 0 for status in TestStatus}
        for result in self.results:
            status_counts[result.status] += 1

        total = len(self.results)
        passed = status_counts[TestStatus.PASSED]
        failed = status_counts[TestStatus.FAILED]
        skipped = status_counts[TestStatus.SKIPPED]

        print(f"\n총 테스트: {total}개")
        print(f"{TestStatus.PASSED.value} 통과: {passed}개")
        print(f"{TestStatus.FAILED.value} 실패: {failed}개")
        print(f"{TestStatus.SKIPPED.value} 건너뜀: {skipped}개")

        self._save_json_report()

        return 0 if failed == 0 else 1

    def _save_json_report(self):
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'summary': {
                'passed': sum(1 for r in self.results if r.status == TestStatus.PASSED),
                'failed': sum(1 for r in self.results if r.status == TestStatus.FAILED),
                'skipped': sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
            },
            'tests': [
                {
                    'name': r.test_name,
                    'category': r.category,
                    'status': r.status.name,
                    'message': r.message,
                    'duration': r.get_duration(),
                    'details': r.details,
                }
                for r in self.results
            ]
        }

        report_path = project_root / 'test' / f'auth_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        if os.environ.get('SNOWBALL_KEEP_REPORT') != '1':
            try:
                os.remove(report_path)
            except:
                pass

def main():
    suite = AuthTestSuite()
    sys.exit(suite.run_all_tests())

if __name__ == '__main__':
    main()
