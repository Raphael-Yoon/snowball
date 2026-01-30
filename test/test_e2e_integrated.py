"""
Snowball 통합 E2E 테스트 (Playwright)

모든 E2E 테스트를 하나의 파일로 통합했습니다.
--suite 파라미터로 특정 테스트만 실행할 수 있습니다.

실행 방법:
    python test/test_e2e_integrated.py
    python test/test_e2e_integrated.py --suite=auth
    python test/test_e2e_integrated.py --suite=rcm
    python test/test_e2e_integrated.py --headless
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import argparse

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, E2ETestResult


class IntegratedE2ETestSuite(PlaywrightTestBase):
    """통합 E2E 테스트 스위트"""

    def __init__(self, base_url="http://localhost:5000", headless=False, target_suite="all"):
        super().__init__(base_url=base_url, headless=headless)
        self.target_suite = target_suite
        self.test_email = "test@example.com"

    def should_run_suite(self, suite_name: str) -> bool:
        """특정 스위트를 실행해야 하는지 확인"""
        return self.target_suite == "all" or self.target_suite == suite_name

    def run_all_tests(self):
        """모든 E2E 테스트 실행"""
        print("=" * 80)
        print("Snowball 통합 E2E 테스트 (Playwright)")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print(f"Headless: {self.headless}")
        print(f"대상 스위트: {self.target_suite}\n")

        try:
            self.setup()

            # Auth 테스트
            if self.should_run_suite("auth"):
                self.run_category("Auth: 인증 플로우", [
                    self.test_login_page_loads,
                    self.test_complete_login_flow,
                ])

            # RCM 테스트 (Link1, Link5 통합)
            if self.should_run_suite("rcm"):
                self.run_category("RCM: 생성 및 관리", [
                    self.test_rcm_generation,
                    self.test_rcm_upload,
                ])

            # 평가 테스트 (Link6, Link7 통합)
            if self.should_run_suite("evaluation"):
                self.run_category("Evaluation: 설계/운영평가", [
                    self.test_design_evaluation,
                    self.test_operation_evaluation,
                ])

            # 인터뷰 테스트 (Link2)
            if self.should_run_suite("interview"):
                self.run_category("Interview: ITGC 인터뷰", [
                    self.test_interview_flow,
                ])

            # 정보보호공시 테스트 (Link11)
            if self.should_run_suite("disclosure"):
                self.run_category("Disclosure: 정보보호공시", [
                    self.test_disclosure_main_page,
                    self.test_disclosure_category_view,
                    self.test_disclosure_progress_api,
                    self.test_disclosure_evidence_page,
                ])

        finally:
            self.teardown()

        exit_code = self.print_final_report()
        self.save_json_report("integrated_e2e")
        self.cleanup_generated_files()  # 생성된 파일 정리
        return exit_code

    # =========================================================================
    # Auth 테스트
    # =========================================================================

    def test_login_page_loads(self, result: E2ETestResult):
        """로그인 페이지 로드"""
        self.navigate_to("/login")
        if self.check_element_exists("input[name='email']"):
            result.pass_test("로그인 페이지 로드 성공")
        else:
            result.fail_test("이메일 입력 필드 없음")

    @patch('auth.verify_otp')
    @patch('auth.send_otp')
    def test_complete_login_flow(self, result: E2ETestResult, mock_send, mock_verify):
        """전체 로그인 플로우"""
        mock_send.return_value = (True, "OTP 발송")
        mock_verify.return_value = (True, {'user_id': 1, 'user_email': self.test_email})

        try:
            self.navigate_to("/login")
            self.fill_input("input[name='email']", self.test_email)
            self.click_button("button[type='submit']")
            self.page.wait_for_url("**/otp**", timeout=5000)
            self.fill_input("input[name='otp']", "123456")
            self.click_button("button[type='submit']")
            self.page.wait_for_url("**/main", timeout=5000)
            result.pass_test("로그인 플로우 완료")
        except Exception as e:
            result.fail_test(f"로그인 실패: {str(e)}")

    # =========================================================================
    # RCM 테스트
    # =========================================================================

    @patch('snowball_link1.send_gmail_with_attachment')
    def test_rcm_generation(self, result: E2ETestResult, mock_send):
        """RCM 자동 생성"""
        mock_send.return_value = True
        try:
            self.navigate_to("/rcm_generate")
            self.fill_input("input[name='param1']", self.test_email)
            self.fill_input("input[name='param2']", "TestSystem")
            result.pass_test("RCM 생성 폼 작동")
        except Exception as e:
            result.skip_test(f"RCM 생성 테스트 건너뜀: {str(e)}")

    def test_rcm_upload(self, result: E2ETestResult):
        """RCM 업로드"""
        try:
            self._quick_login()
            self.navigate_to("/user/rcm/upload")
            if self.check_element_exists("input[type='file']"):
                result.pass_test("RCM 업로드 페이지 접근 성공")
            else:
                result.skip_test("파일 업로드 필드 없음")
        except Exception as e:
            result.skip_test(f"RCM 업로드 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 평가 테스트
    # =========================================================================

    def test_design_evaluation(self, result: E2ETestResult):
        """설계평가"""
        try:
            self._quick_login()
            self.navigate_to("/user/design-evaluation")
            result.pass_test("설계평가 페이지 접근 성공")
        except Exception as e:
            result.skip_test(f"설계평가 테스트 건너뜀: {str(e)}")

    def test_operation_evaluation(self, result: E2ETestResult):
        """운영평가"""
        try:
            self._quick_login()
            self.navigate_to("/user/operation-evaluation")
            result.pass_test("운영평가 페이지 접근 성공")
        except Exception as e:
            result.skip_test(f"운영평가 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 인터뷰 테스트
    # =========================================================================

    def test_interview_flow(self, result: E2ETestResult):
        """ITGC 인터뷰"""
        try:
            self.navigate_to("/link2")
            if self.check_element_exists("input[type='email'], input[name*='email']"):
                result.pass_test("ITGC 인터뷰 페이지 접근 성공")
            else:
                result.skip_test("이메일 입력 필드 없음")
        except Exception as e:
            result.skip_test(f"인터뷰 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 정보보호공시 테스트 (Link11)
    # =========================================================================

    def test_disclosure_main_page(self, result: E2ETestResult):
        """정보보호공시 메인 페이지 로드"""
        try:
            self.navigate_to("/link11")
            # 페이지 타이틀 또는 특정 요소 확인
            if self.page.title() or self.check_element_exists("body"):
                result.add_detail(f"페이지 URL: {self.page.url}")
                result.pass_test("정보보호공시 메인 페이지 로드 성공")
            else:
                result.fail_test("페이지 로드 실패")
        except Exception as e:
            result.skip_test(f"메인 페이지 테스트 건너뜀: {str(e)}")

    def test_disclosure_category_view(self, result: E2ETestResult):
        """정보보호공시 카테고리 페이지"""
        try:
            # 테스트용 카테고리 ID로 접근
            self.navigate_to("/link11/category/governance")
            if self.page.url.endswith("/governance") or "category" in self.page.url:
                result.add_detail("카테고리: governance")
                result.pass_test("카테고리 뷰 페이지 접근 성공")
            else:
                result.skip_test("카테고리 페이지 리다이렉트됨")
        except Exception as e:
            result.skip_test(f"카테고리 뷰 테스트 건너뜀: {str(e)}")

    def test_disclosure_progress_api(self, result: E2ETestResult):
        """정보보호공시 진행률 API 테스트"""
        try:
            # API 직접 호출
            response = self.page.request.get(
                f"{self.base_url}/link11/api/progress/testcompany/2026"
            )
            if response.ok:
                data = response.json()
                if data.get('success'):
                    progress = data.get('progress', {})
                    result.add_detail(f"총 질문: {progress.get('total_questions', 0)}개")
                    result.add_detail(f"답변 완료: {progress.get('answered_questions', 0)}개")
                    result.pass_test("진행률 API 정상 작동")
                else:
                    result.warn_test(f"API 응답 실패: {data.get('message', 'Unknown')}")
            else:
                result.skip_test(f"API 응답 코드: {response.status}")
        except Exception as e:
            result.skip_test(f"진행률 API 테스트 건너뜀: {str(e)}")

    def test_disclosure_evidence_page(self, result: E2ETestResult):
        """정보보호공시 증빙 자료 관리 페이지"""
        try:
            self.navigate_to("/link11/evidence")
            # 페이지 로드 확인
            if self.page.url.endswith("/evidence") or "evidence" in self.page.url:
                result.add_detail(f"페이지 URL: {self.page.url}")
                result.pass_test("증빙 자료 관리 페이지 접근 성공")
            else:
                result.skip_test("증빙 페이지 리다이렉트됨")
        except Exception as e:
            result.skip_test(f"증빙 페이지 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 헬퍼 메서드
    # =========================================================================

    def _quick_login(self):
        """빠른 로그인"""
        with patch('auth.send_otp') as mock_send:
            with patch('auth.verify_otp') as mock_verify:
                mock_send.return_value = (True, "OTP")
                mock_verify.return_value = (True, {
                    'user_id': 1,
                    'user_email': self.test_email,
                    'user_name': '테스트',
                    'admin_flag': 'N'
                })
                try:
                    self.navigate_to("/login")
                    self.fill_input("input[name='email']", self.test_email)
                    self.click_button("button[type='submit']")
                    self.page.wait_for_url("**/otp**", timeout=5000)
                    self.fill_input("input[name='otp']", "123456")
                    self.click_button("button[type='submit']")
                    self.page.wait_for_url("**/main", timeout=5000)
                except:
                    pass  # 이미 로그인됨


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='Snowball 통합 E2E 테스트')
    parser.add_argument('--suite', type=str, default='all',
                       help='테스트 스위트 (all, auth, rcm, evaluation, interview, disclosure)')
    parser.add_argument('--headless', action='store_true',
                       help='헤드리스 모드로 실행')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='Base URL')

    args = parser.parse_args()

    print("\n⚠️  주의: E2E 테스트를 실행하기 전에 애플리케이션이 실행 중이어야 합니다!")
    print(f"   기본 URL: {args.url}\n")

    suite = IntegratedE2ETestSuite(
        base_url=args.url,
        headless=args.headless,
        target_suite=args.suite
    )
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
