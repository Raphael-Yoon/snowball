"""
인증(Auth) E2E 테스트 - Playwright 기반

실제 브라우저를 통해 로그인, OTP 인증, 세션 관리 등을
엔드투엔드로 테스트합니다.
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, E2ETestResult, PageHelper


class AuthE2ETestSuite(PlaywrightTestBase):
    """인증 관련 E2E 테스트 스위트"""

    def __init__(self):
        super().__init__(base_url="http://localhost:5000", headless=False)  # 개발 시 headless=False
        self.test_email = "test@example.com"
        self.test_otp = "123456"

    def run_all_tests(self):
        """모든 E2E 테스트 실행"""
        print("=" * 80)
        print("Auth 인증 E2E 테스트 시작 (Playwright)")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print(f"Headless: {self.headless}\n")

        try:
            self.setup()

            self.run_category("1. 페이지 접근 및 렌더링", [
                self.test_login_page_loads,
                self.test_main_page_requires_login,
            ])

            self.run_category("2. 로그인 플로우", [
                self.test_login_email_submission,
                self.test_otp_page_renders,
                self.test_complete_login_flow,
            ])

            self.run_category("3. 로그인 실패 시나리오", [
                self.test_login_with_invalid_email,
                self.test_login_with_wrong_otp,
            ])

            self.run_category("4. 세션 및 로그아웃", [
                self.test_logout_clears_session,
            ])

        finally:
            self.teardown()

        exit_code = self.print_final_report()
        self.save_json_report("auth_e2e")
        return exit_code

    # =========================================================================
    # 1. 페이지 접근 및 렌더링
    # =========================================================================

    def test_login_page_loads(self, result: E2ETestResult):
        """로그인 페이지가 정상적으로 로드되는지 확인"""
        self.navigate_to("/login")

        # 페이지 타이틀 확인
        title = self.page.title()
        result.add_detail(f"페이지 타이틀: {title}")

        # 이메일 입력 필드 존재 확인
        email_input_exists = self.check_element_exists("input[name='email']")
        if not email_input_exists:
            result.fail_test("이메일 입력 필드를 찾을 수 없습니다")
            return

        # 제출 버튼 존재 확인
        submit_button_exists = self.check_element_exists("button[type='submit']")
        if not submit_button_exists:
            result.fail_test("제출 버튼을 찾을 수 없습니다")
            return

        result.add_detail("✓ 이메일 입력 필드 존재")
        result.add_detail("✓ 제출 버튼 존재")

        # 스크린샷 캡처
        screenshot = self.take_screenshot("login_page")
        result.add_screenshot(screenshot)

        result.pass_test("로그인 페이지가 정상적으로 로드됩니다")

    def test_main_page_requires_login(self, result: E2ETestResult):
        """로그인하지 않고 메인 페이지 접근 시 리다이렉트 확인"""
        # 세션 없이 메인 페이지 접근 시도
        self.navigate_to("/main")

        # 로그인 페이지로 리다이렉트 되었는지 확인
        current_url = self.page.url
        result.add_detail(f"현재 URL: {current_url}")

        if "/login" in current_url:
            result.pass_test("미로그인 시 로그인 페이지로 리다이렉트됩니다")
        else:
            result.fail_test(f"로그인 페이지로 리다이렉트되지 않았습니다: {current_url}")

    # =========================================================================
    # 2. 로그인 플로우
    # =========================================================================

    @patch('auth.send_otp')
    def test_login_email_submission(self, result: E2ETestResult, mock_send_otp):
        """이메일 제출 시 OTP 발송 확인"""
        mock_send_otp.return_value = (True, "OTP가 발송되었습니다")

        self.navigate_to("/login")

        # 이메일 입력
        self.fill_input("input[name='email']", self.test_email)
        result.add_detail(f"✓ 이메일 입력: {self.test_email}")

        # 폼 제출
        self.click_button("button[type='submit']")
        result.add_detail("✓ 폼 제출 클릭")

        # OTP 페이지로 전환 대기
        try:
            self.page.wait_for_url("**/otp**", timeout=5000)
            result.add_detail("✓ OTP 페이지로 이동 확인")
            result.pass_test("이메일 제출 후 OTP 페이지로 이동합니다")
        except:
            current_url = self.page.url
            result.fail_test(f"OTP 페이지로 이동하지 않았습니다: {current_url}")

    def test_otp_page_renders(self, result: E2ETestResult):
        """OTP 입력 페이지가 올바르게 렌더링되는지 확인"""
        # 먼저 로그인 페이지에서 이메일 제출
        self.navigate_to("/login")
        self.fill_input("input[name='email']", self.test_email)

        with patch('auth.send_otp') as mock_send:
            mock_send.return_value = (True, "OTP 발송됨")
            self.click_button("button[type='submit']")

            # OTP 페이지 대기
            try:
                self.page.wait_for_url("**/otp**", timeout=5000)
            except:
                result.skip_test("OTP 페이지로 이동 실패")
                return

        # OTP 입력 필드 확인
        otp_input_exists = self.check_element_exists("input[name='otp']")
        if not otp_input_exists:
            result.fail_test("OTP 입력 필드를 찾을 수 없습니다")
            return

        result.add_detail("✓ OTP 입력 필드 존재")

        # 스크린샷 캡처
        screenshot = self.take_screenshot("otp_page")
        result.add_screenshot(screenshot)

        result.pass_test("OTP 페이지가 정상적으로 렌더링됩니다")

    @patch('auth.verify_otp')
    @patch('auth.send_otp')
    def test_complete_login_flow(self, result: E2ETestResult, mock_send_otp, mock_verify_otp):
        """전체 로그인 플로우 테스트 (이메일 → OTP → 메인)"""
        mock_send_otp.return_value = (True, "OTP 발송됨")
        mock_verify_otp.return_value = (True, {
            'user_id': 1,
            'user_email': self.test_email,
            'user_name': 'Test User',
            'admin_flag': 'N'
        })

        # 1. 로그인 페이지에서 이메일 입력
        self.navigate_to("/login")
        self.fill_input("input[name='email']", self.test_email)
        self.click_button("button[type='submit']")
        result.add_detail("✓ 1단계: 이메일 제출")

        # 2. OTP 페이지에서 OTP 입력
        try:
            self.page.wait_for_url("**/otp**", timeout=5000)
            result.add_detail("✓ 2단계: OTP 페이지 도달")

            self.fill_input("input[name='otp']", self.test_otp)
            self.click_button("button[type='submit']")
            result.add_detail("✓ 3단계: OTP 제출")

            # 3. 메인 페이지로 리다이렉트 확인
            self.page.wait_for_url("**/main", timeout=5000)
            result.add_detail("✓ 4단계: 메인 페이지 도달")

            # 스크린샷 캡처
            screenshot = self.take_screenshot("login_success")
            result.add_screenshot(screenshot)

            result.pass_test("전체 로그인 플로우가 정상적으로 작동합니다")

        except Exception as e:
            result.fail_test(f"로그인 플로우 실패: {str(e)}")

    # =========================================================================
    # 3. 로그인 실패 시나리오
    # =========================================================================

    def test_login_with_invalid_email(self, result: E2ETestResult):
        """잘못된 이메일 형식으로 로그인 시도"""
        self.navigate_to("/login")

        # 잘못된 이메일 입력
        invalid_email = "not-an-email"
        self.fill_input("input[name='email']", invalid_email)
        self.click_button("button[type='submit']")

        # HTML5 validation 또는 서버 에러 메시지 확인
        # (브라우저가 자동으로 validation을 수행할 수 있음)
        current_url = self.page.url

        if "/login" in current_url:
            result.add_detail("✓ 로그인 페이지에 머물러 있음")
            result.pass_test("잘못된 이메일 형식은 거부됩니다")
        else:
            result.warn_test("이메일 검증이 클라이언트/서버에서 처리되지 않을 수 있습니다")

    @patch('auth.verify_otp')
    @patch('auth.send_otp')
    def test_login_with_wrong_otp(self, result: E2ETestResult, mock_send_otp, mock_verify_otp):
        """잘못된 OTP로 로그인 시도"""
        mock_send_otp.return_value = (True, "OTP 발송됨")
        mock_verify_otp.return_value = (False, "OTP가 틀렸습니다")

        # 이메일 제출
        self.navigate_to("/login")
        self.fill_input("input[name='email']", self.test_email)
        self.click_button("button[type='submit']")

        try:
            self.page.wait_for_url("**/otp**", timeout=5000)

            # 잘못된 OTP 입력
            wrong_otp = "000000"
            self.fill_input("input[name='otp']", wrong_otp)
            self.click_button("button[type='submit']")

            # 에러 메시지가 표시되거나 OTP 페이지에 머물러야 함
            self.page.wait_for_timeout(1000)  # 1초 대기
            current_url = self.page.url

            if "/otp" in current_url or "/login" in current_url:
                result.add_detail("✓ 잘못된 OTP 입력 시 로그인 차단")
                result.pass_test("잘못된 OTP는 거부됩니다")
            else:
                result.fail_test(f"잘못된 OTP로 로그인되었습니다: {current_url}")

        except:
            result.skip_test("OTP 페이지 접근 실패")

    # =========================================================================
    # 4. 세션 및 로그아웃
    # =========================================================================

    @patch('auth.verify_otp')
    @patch('auth.send_otp')
    def test_logout_clears_session(self, result: E2ETestResult, mock_send_otp, mock_verify_otp):
        """로그아웃 시 세션이 정리되는지 확인"""
        # 먼저 로그인
        mock_send_otp.return_value = (True, "OTP 발송됨")
        mock_verify_otp.return_value = (True, {
            'user_id': 1,
            'user_email': self.test_email,
            'user_name': 'Test User',
            'admin_flag': 'N'
        })

        self.navigate_to("/login")
        self.fill_input("input[name='email']", self.test_email)
        self.click_button("button[type='submit']")

        try:
            self.page.wait_for_url("**/otp**", timeout=5000)
            self.fill_input("input[name='otp']", self.test_otp)
            self.click_button("button[type='submit']")
            self.page.wait_for_url("**/main", timeout=5000)
            result.add_detail("✓ 로그인 완료")

            # 로그아웃
            self.navigate_to("/logout")
            result.add_detail("✓ 로그아웃 실행")

            # 다시 메인 페이지 접근 시도
            self.navigate_to("/main")
            current_url = self.page.url

            if "/login" in current_url:
                result.pass_test("로그아웃 후 세션이 정리되어 로그인 페이지로 이동합니다")
            else:
                result.fail_test("로그아웃 후에도 세션이 유지됩니다")

        except Exception as e:
            result.fail_test(f"세션 테스트 실패: {str(e)}")


def main():
    """메인 실행 함수"""
    suite = AuthE2ETestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
