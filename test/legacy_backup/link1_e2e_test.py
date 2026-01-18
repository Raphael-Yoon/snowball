"""
Link1 RCM 자동생성 E2E 테스트 - Playwright 기반

실제 브라우저를 통해 RCM 자동 생성 기능을 테스트합니다.
- 폼 입력
- Excel 파일 생성
- 이메일 발송
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, E2ETestResult


class Link1E2ETestSuite(PlaywrightTestBase):
    """Link1 RCM 생성 E2E 테스트 스위트"""

    def __init__(self):
        super().__init__(base_url="http://localhost:5000", headless=False)
        self.test_email = "test@example.com"

    def run_all_tests(self):
        """모든 E2E 테스트 실행"""
        print("=" * 80)
        print("Link1 RCM 자동생성 E2E 테스트 시작 (Playwright)")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print(f"Headless: {self.headless}\n")

        try:
            self.setup()

            # 로그인 필요한 경우를 대비해 세션 설정
            self._setup_session()

            self.run_category("1. Link1 페이지 접근", [
                self.test_link1_page_loads,
                self.test_rcm_generate_page_loads,
            ])

            self.run_category("2. RCM 생성 폼 검증", [
                self.test_form_fields_exist,
                self.test_form_validation,
            ])

            self.run_category("3. RCM 생성 플로우", [
                self.test_rcm_generation_with_valid_data,
                self.test_cloud_selection_interaction,
            ])

            self.run_category("4. 사용자 경험 검증", [
                self.test_loading_indicator,
                self.test_success_message_display,
            ])

        finally:
            self.teardown()

        exit_code = self.print_final_report()
        self.save_json_report("link1_e2e")
        return exit_code

    def _setup_session(self):
        """테스트용 세션 설정 (로그인 우회)"""
        # 세션 쿠키를 직접 설정하여 로그인 우회
        # (실제 운영 환경에서는 완전한 로그인 플로우를 거쳐야 함)
        self.context.add_cookies([
            {
                'name': 'session',
                'value': 'test_session_token',
                'domain': 'localhost',
                'path': '/'
            }
        ])

    # =========================================================================
    # 1. Link1 페이지 접근
    # =========================================================================

    def test_link1_page_loads(self, result: E2ETestResult):
        """Link1 메인 페이지가 로드되는지 확인"""
        try:
            self.navigate_to("/link1")

            # 페이지 타이틀 확인
            title = self.page.title()
            result.add_detail(f"페이지 타이틀: {title}")

            # Link1 특정 요소 확인 (예: RCM 자동생성 버튼/링크)
            page_content = self.page.content()
            if "RCM" in page_content or "ITGC" in page_content:
                result.add_detail("✓ Link1 관련 콘텐츠 확인")
            else:
                result.warn_test("Link1 관련 콘텐츠를 찾을 수 없습니다")
                return

            # 스크린샷 캡처
            screenshot = self.take_screenshot("link1_page")
            result.add_screenshot(screenshot)

            result.pass_test("Link1 페이지가 정상적으로 로드됩니다")

        except Exception as e:
            result.fail_test(f"페이지 로드 실패: {str(e)}")

    def test_rcm_generate_page_loads(self, result: E2ETestResult):
        """RCM 생성 페이지가 로드되는지 확인"""
        try:
            self.navigate_to("/rcm_generate")

            # 페이지 로드 확인
            self.page.wait_for_load_state("networkidle")

            # 폼이 존재하는지 확인
            form_exists = self.check_element_exists("form")
            if not form_exists:
                result.fail_test("RCM 생성 폼을 찾을 수 없습니다")
                return

            result.add_detail("✓ RCM 생성 폼 존재")

            # 스크린샷 캡처
            screenshot = self.take_screenshot("rcm_generate_page")
            result.add_screenshot(screenshot)

            result.pass_test("RCM 생성 페이지가 정상적으로 로드됩니다")

        except Exception as e:
            result.fail_test(f"페이지 로드 실패: {str(e)}")

    # =========================================================================
    # 2. RCM 생성 폼 검증
    # =========================================================================

    def test_form_fields_exist(self, result: E2ETestResult):
        """필수 폼 필드가 존재하는지 확인"""
        try:
            self.navigate_to("/rcm_generate")

            # 주요 입력 필드 확인
            fields_to_check = [
                ("input[name='param1']", "이메일 입력 필드"),
                ("input[name='param2']", "시스템명 입력 필드"),
                ("select[name='param_cloud'], input[name='param_cloud']", "클라우드 선택 필드"),
            ]

            all_fields_exist = True
            for selector, field_name in fields_to_check:
                # 여러 선택자를 시도 (select 또는 input)
                selectors = selector.split(", ")
                field_exists = False
                for sel in selectors:
                    if self.check_element_exists(sel.strip()):
                        field_exists = True
                        break

                if field_exists:
                    result.add_detail(f"✓ {field_name}")
                else:
                    result.add_detail(f"✗ {field_name} 없음")
                    all_fields_exist = False

            if all_fields_exist:
                result.pass_test("모든 필수 폼 필드가 존재합니다")
            else:
                result.fail_test("일부 필수 폼 필드가 누락되었습니다")

        except Exception as e:
            result.fail_test(f"폼 검증 실패: {str(e)}")

    def test_form_validation(self, result: E2ETestResult):
        """폼 검증 로직이 작동하는지 확인"""
        try:
            self.navigate_to("/rcm_generate")

            # 빈 폼 제출 시도
            submit_button = self.page.locator("button[type='submit'], input[type='submit']").first
            if submit_button.is_visible():
                submit_button.click()
                time.sleep(0.5)  # 검증 메시지 대기

                # HTML5 validation 또는 커스텀 에러 메시지 확인
                # (브라우저가 자동으로 required 필드 검증)
                current_url = self.page.url

                if "/rcm_generate" in current_url:
                    result.add_detail("✓ 빈 폼 제출 시 페이지에 머물러 있음")
                    result.pass_test("폼 검증이 작동합니다")
                else:
                    result.warn_test("폼 검증이 없거나 약할 수 있습니다")
            else:
                result.skip_test("제출 버튼을 찾을 수 없습니다")

        except Exception as e:
            result.fail_test(f"폼 검증 테스트 실패: {str(e)}")

    # =========================================================================
    # 3. RCM 생성 플로우
    # =========================================================================

    @patch('snowball_link1.send_gmail_with_attachment')
    def test_rcm_generation_with_valid_data(self, result: E2ETestResult, mock_send_email):
        """유효한 데이터로 RCM 생성 테스트"""
        mock_send_email.return_value = True

        try:
            self.navigate_to("/rcm_generate")

            # 폼 필드 채우기
            self.fill_input("input[name='param1']", self.test_email)
            result.add_detail(f"✓ 이메일 입력: {self.test_email}")

            self.fill_input("input[name='param2']", "TestSystem")
            result.add_detail("✓ 시스템명 입력: TestSystem")

            # 클라우드 선택 (select 또는 radio button)
            try:
                # Select dropdown 시도
                if self.check_element_exists("select[name='param_cloud']"):
                    self.select_option("select[name='param_cloud']", "AWS")
                    result.add_detail("✓ 클라우드 선택: AWS (dropdown)")
                # Radio button 시도
                elif self.check_element_exists("input[name='param_cloud'][value='AWS']"):
                    self.page.check("input[name='param_cloud'][value='AWS']")
                    result.add_detail("✓ 클라우드 선택: AWS (radio)")
                else:
                    result.add_detail("⚠️  클라우드 선택 필드 형식 불명")
            except Exception as e:
                result.add_detail(f"⚠️  클라우드 선택 오류: {str(e)}")

            # 기타 필드 채우기 (있는 경우)
            if self.check_element_exists("select[name='param3']"):
                self.select_option("select[name='param3']", "Web")
                result.add_detail("✓ 서비스 유형 선택: Web")

            # 스크린샷 (제출 전)
            screenshot_before = self.take_screenshot("rcm_form_filled")
            result.add_screenshot(screenshot_before)

            # 폼 제출
            submit_button = self.page.locator("button[type='submit'], input[type='submit']").first
            submit_button.click()
            result.add_detail("✓ 폼 제출 클릭")

            # 결과 페이지 대기 (성공 메시지 또는 리다이렉트)
            time.sleep(2)  # 처리 시간 대기

            # 스크린샷 (제출 후)
            screenshot_after = self.take_screenshot("rcm_form_submitted")
            result.add_screenshot(screenshot_after)

            # 성공 메시지 확인
            page_content = self.page.content()
            if "성공" in page_content or "발송" in page_content or "완료" in page_content:
                result.add_detail("✓ 성공 메시지 확인")
                result.pass_test("RCM 생성 플로우가 정상적으로 작동합니다")
            else:
                result.warn_test("성공 메시지를 명확히 확인할 수 없습니다")

        except Exception as e:
            result.fail_test(f"RCM 생성 실패: {str(e)}")

    def test_cloud_selection_interaction(self, result: E2ETestResult):
        """클라우드 선택 UI 상호작용 테스트"""
        try:
            self.navigate_to("/rcm_generate")

            # 클라우드 옵션들 확인
            cloud_options = ["AWS", "Azure", "GCP", "On-Premise"]
            found_options = []

            for option in cloud_options:
                # Select option 확인
                if self.check_element_exists(f"select[name='param_cloud'] option[value='{option}']"):
                    found_options.append(option)
                # Radio button 확인
                elif self.check_element_exists(f"input[name='param_cloud'][value='{option}']"):
                    found_options.append(option)

            if found_options:
                result.add_detail(f"✓ 발견된 클라우드 옵션: {', '.join(found_options)}")
                result.pass_test("클라우드 선택 옵션이 존재합니다")
            else:
                result.warn_test("클라우드 선택 옵션을 찾을 수 없습니다")

        except Exception as e:
            result.fail_test(f"UI 상호작용 테스트 실패: {str(e)}")

    # =========================================================================
    # 4. 사용자 경험 검증
    # =========================================================================

    def test_loading_indicator(self, result: E2ETestResult):
        """로딩 인디케이터가 표시되는지 확인"""
        try:
            self.navigate_to("/rcm_generate")

            # 로딩 관련 요소 확인 (spinner, progress bar 등)
            page_content = self.page.content()

            # 일반적인 로딩 표시 요소 검색
            loading_indicators = [
                ".spinner",
                ".loading",
                "#loading",
                "[class*='loader']",
                "[id*='loader']"
            ]

            has_loading = False
            for indicator in loading_indicators:
                if self.check_element_exists(indicator):
                    has_loading = True
                    result.add_detail(f"✓ 로딩 인디케이터 발견: {indicator}")
                    break

            if has_loading:
                result.pass_test("로딩 인디케이터가 구현되어 있습니다")
            else:
                result.skip_test("로딩 인디케이터를 찾을 수 없습니다 (구현되지 않았을 수 있음)")

        except Exception as e:
            result.skip_test(f"테스트 건너뜀: {str(e)}")

    @patch('snowball_link1.send_gmail_with_attachment')
    def test_success_message_display(self, result: E2ETestResult, mock_send_email):
        """성공 메시지가 사용자에게 표시되는지 확인"""
        mock_send_email.return_value = True

        try:
            self.navigate_to("/rcm_generate")

            # 최소한의 필수 필드만 채우기
            self.fill_input("input[name='param1']", self.test_email)
            self.fill_input("input[name='param2']", "QuickTest")

            # 제출
            submit_button = self.page.locator("button[type='submit'], input[type='submit']").first
            submit_button.click()

            # 성공 메시지 대기
            time.sleep(2)

            # 성공 메시지 요소 확인
            success_indicators = [
                ".alert-success",
                ".success-message",
                ".flash.success",
                "[class*='success']"
            ]

            success_found = False
            for indicator in success_indicators:
                try:
                    element = self.page.locator(indicator).first
                    if element.is_visible():
                        message_text = element.text_content()
                        result.add_detail(f"✓ 성공 메시지: {message_text[:50]}")
                        success_found = True
                        break
                except:
                    continue

            # 페이지 콘텐츠에서 성공 관련 텍스트 검색
            if not success_found:
                page_text = self.page.content()
                success_keywords = ["성공", "완료", "발송", "전송"]
                for keyword in success_keywords:
                    if keyword in page_text:
                        result.add_detail(f"✓ 성공 키워드 발견: {keyword}")
                        success_found = True
                        break

            if success_found:
                result.pass_test("성공 메시지가 사용자에게 표시됩니다")
            else:
                result.warn_test("명확한 성공 메시지를 찾을 수 없습니다")

        except Exception as e:
            result.fail_test(f"성공 메시지 확인 실패: {str(e)}")


def main():
    """메인 실행 함수"""
    suite = Link1E2ETestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
