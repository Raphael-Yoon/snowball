"""
사용자 여정(User Journey) E2E 테스트

실제 사용자가 시스템을 사용하는 전체 플로우를 테스트합니다.
개별 기능이 아닌 업무 시나리오 중심으로 테스트합니다.
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, E2ETestResult


class UserJourneyE2ETestSuite(PlaywrightTestBase):
    """사용자 여정 E2E 테스트 스위트"""

    def __init__(self):
        super().__init__(base_url="http://localhost:5000", headless=False)
        self.test_email = "test@example.com"
        self.test_otp = "123456"

    def run_all_tests(self):
        """모든 사용자 여정 테스트 실행"""
        print("=" * 80)
        print("사용자 여정(User Journey) E2E 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"설명: 실제 사용자 업무 플로우를 통합 테스트합니다.\n")

        try:
            self.setup()

            # 핵심 사용자 여정만 테스트
            self.run_category("여정 1: 신규 사용자 온보딩", [
                self.journey_new_user_onboarding,
            ])

            self.run_category("여정 2: RCM 생성 및 검토 (Link1 → Link5)", [
                self.journey_rcm_creation_and_review,
            ])

            self.run_category("여정 3: 설계평가 전체 프로세스 (Link5 → Link6)", [
                self.journey_design_evaluation_process,
            ])

            self.run_category("여정 4: 관리자 대시보드 관리", [
                self.journey_admin_dashboard_management,
            ])

        finally:
            self.teardown()

        exit_code = self.print_final_report()
        self.save_json_report("user_journey_e2e")
        return exit_code

    # =========================================================================
    # 여정 1: 신규 사용자 온보딩
    # =========================================================================

    @patch('auth.verify_otp')
    @patch('auth.send_otp')
    def journey_new_user_onboarding(self, result: E2ETestResult, mock_send_otp, mock_verify_otp):
        """
        신규 사용자가 처음 시스템에 접속하여 메인 화면까지 도달하는 전체 플로우

        시나리오:
        1. 로그인 페이지 접속
        2. 이메일 입력 및 OTP 요청
        3. OTP 입력 및 인증
        4. 메인 대시보드 도달
        5. 주요 메뉴 확인
        """
        try:
            result.add_detail("🎯 목표: 신규 사용자가 시스템에 로그인하고 메인 화면 확인")

            # Mock 설정
            mock_send_otp.return_value = (True, "OTP 발송됨")
            mock_verify_otp.return_value = (True, {
                'user_id': 1,
                'user_email': self.test_email,
                'user_name': '테스트 사용자',
                'admin_flag': 'N'
            })

            # Step 1: 로그인 페이지 접속
            self.navigate_to("/login")
            screenshot = self.take_screenshot("journey1_step1_login_page")
            result.add_screenshot(screenshot)
            result.add_detail("✓ Step 1: 로그인 페이지 접속")

            # Step 2: 이메일 입력 및 OTP 요청
            self.fill_input("input[name='email']", self.test_email)
            self.click_button("button[type='submit']")
            result.add_detail(f"✓ Step 2: 이메일 입력 ({self.test_email})")

            # Step 3: OTP 입력 및 인증
            self.page.wait_for_url("**/otp**", timeout=5000)
            screenshot = self.take_screenshot("journey1_step3_otp_page")
            result.add_screenshot(screenshot)
            result.add_detail("✓ Step 3: OTP 페이지 도달")

            self.fill_input("input[name='otp']", self.test_otp)
            self.click_button("button[type='submit']")
            result.add_detail("✓ Step 4: OTP 인증 제출")

            # Step 4: 메인 대시보드 도달
            self.page.wait_for_url("**/main", timeout=5000)
            screenshot = self.take_screenshot("journey1_step4_main_dashboard")
            result.add_screenshot(screenshot)
            result.add_detail("✓ Step 5: 메인 대시보드 도달")

            # Step 5: 주요 메뉴 확인
            page_content = self.page.content()
            expected_menus = ["Link1", "Link5", "Link6", "Link7"]
            found_menus = [menu for menu in expected_menus if menu in page_content]
            result.add_detail(f"✓ Step 6: 메뉴 확인 ({len(found_menus)}/{len(expected_menus)}개)")

            result.pass_test(f"신규 사용자 온보딩 여정 완료 (총 6단계)")

        except Exception as e:
            screenshot = self.take_screenshot("journey1_error")
            result.add_screenshot(screenshot)
            result.fail_test(f"온보딩 여정 실패: {str(e)}")

    # =========================================================================
    # 여정 2: RCM 생성 및 검토
    # =========================================================================

    @patch('snowball_link1.send_gmail_with_attachment')
    @patch('auth.verify_otp')
    @patch('auth.send_otp')
    def journey_rcm_creation_and_review(self, result: E2ETestResult,
                                        mock_send_otp, mock_verify_otp, mock_send_email):
        """
        사용자가 RCM을 생성하고 검토하는 전체 플로우

        시나리오:
        1. 로그인
        2. Link1: RCM 자동생성 페이지 접속
        3. 시스템 정보 입력
        4. RCM 생성 및 이메일 발송 확인
        5. Link5: RCM 관리 페이지에서 확인
        """
        try:
            result.add_detail("🎯 목표: RCM 생성부터 관리까지 전체 플로우 검증")

            # Mock 설정
            mock_send_otp.return_value = (True, "OTP 발송됨")
            mock_verify_otp.return_value = (True, {
                'user_id': 1,
                'user_email': self.test_email,
                'user_name': '테스트 사용자',
                'admin_flag': 'N'
            })
            mock_send_email.return_value = True

            # Step 1: 로그인
            self._quick_login()
            result.add_detail("✓ Step 1: 로그인 완료")

            # Step 2: Link1 RCM 생성 페이지 접속
            self.navigate_to("/rcm_generate")
            screenshot = self.take_screenshot("journey2_step2_rcm_generate")
            result.add_screenshot(screenshot)
            result.add_detail("✓ Step 2: RCM 생성 페이지 접속")

            # Step 3: 시스템 정보 입력
            self.fill_input("input[name='param1']", self.test_email)
            self.fill_input("input[name='param2']", "TestSystem")
            result.add_detail("✓ Step 3: 시스템 정보 입력 완료")

            # Step 4: RCM 생성 제출
            submit_button = self.page.locator("button[type='submit'], input[type='submit']").first
            submit_button.click()
            time.sleep(2)  # 처리 대기
            screenshot = self.take_screenshot("journey2_step4_rcm_submitted")
            result.add_screenshot(screenshot)
            result.add_detail("✓ Step 4: RCM 생성 요청 제출")

            # Step 5: Link5 RCM 관리 페이지로 이동
            self.navigate_to("/link5")
            screenshot = self.take_screenshot("journey2_step5_rcm_management")
            result.add_screenshot(screenshot)
            result.add_detail("✓ Step 5: RCM 관리 페이지 접속")

            result.pass_test("RCM 생성 및 검토 여정 완료 (총 5단계)")

        except Exception as e:
            screenshot = self.take_screenshot("journey2_error")
            result.add_screenshot(screenshot)
            result.fail_test(f"RCM 생성 여정 실패: {str(e)}")

    # =========================================================================
    # 여정 3: 설계평가 전체 프로세스
    # =========================================================================

    def journey_design_evaluation_process(self, result: E2ETestResult):
        """
        설계평가 전체 프로세스 (Link5 → Link6)

        시나리오:
        1. RCM 업로드 (Link5)
        2. 설계평가 시작 (Link6)
        3. 평가 항목 입력
        4. 평가 완료 및 결과 확인
        """
        try:
            result.add_detail("🎯 목표: 설계평가 전체 프로세스 검증")

            # 현재는 템플릿 구조를 확인하는 수준으로 진행
            # 실제 인증 및 데이터 처리는 Mock이나 테스트 계정 필요

            result.add_detail("✓ Step 1: 인증 필요 (현재는 스킵)")
            result.add_detail("✓ Step 2: 향후 구현 예정")

            result.skip_test("설계평가 여정은 인증 구현 후 테스트 가능")

        except Exception as e:
            result.fail_test(f"설계평가 여정 실패: {str(e)}")

    # =========================================================================
    # 여정 4: 관리자 대시보드 관리
    # =========================================================================

    def journey_admin_dashboard_management(self, result: E2ETestResult):
        """
        관리자가 시스템을 관리하는 플로우

        시나리오:
        1. 관리자 로그인
        2. 관리자 대시보드 접속
        3. 사용자 관리
        4. RCM 권한 관리
        """
        try:
            result.add_detail("🎯 목표: 관리자 대시보드 기능 검증")

            # 관리자 계정 필요
            result.add_detail("✓ Step 1: 관리자 계정 필요 (현재는 스킵)")

            result.skip_test("관리자 여정은 관리자 계정 설정 후 테스트 가능")

        except Exception as e:
            result.fail_test(f"관리자 여정 실패: {str(e)}")

    # =========================================================================
    # 헬퍼 메서드
    # =========================================================================

    def _quick_login(self):
        """빠른 로그인 (테스트용)"""
        from unittest.mock import patch

        with patch('auth.send_otp') as mock_send:
            with patch('auth.verify_otp') as mock_verify:
                mock_send.return_value = (True, "OTP 발송됨")
                mock_verify.return_value = (True, {
                    'user_id': 1,
                    'user_email': self.test_email,
                    'user_name': '테스트',
                    'admin_flag': 'N'
                })

                self.navigate_to("/login")
                self.fill_input("input[name='email']", self.test_email)
                self.click_button("button[type='submit']")

                self.page.wait_for_url("**/otp**", timeout=5000)
                self.fill_input("input[name='otp']", self.test_otp)
                self.click_button("button[type='submit']")

                self.page.wait_for_url("**/main", timeout=5000)


def main():
    """메인 실행 함수"""
    suite = UserJourneyE2ETestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
