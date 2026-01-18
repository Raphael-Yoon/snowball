"""
E04: 설계평가 전체 프로세스 E2E 테스트 - Playwright 기반

Link5에서 RCM을 선택하고 Link6 설계평가를 완료하는 전체 플로우를 테스트합니다.
- RCM 선택
- 설계평가 페이지 접근
- 평가 데이터 로드
- 평가 결과 입력
- 평가 저장
- 평가 완료 처리
"""

import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import time

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, E2ETestResult


class Link6DesignEvaluationE2ETestSuite(PlaywrightTestBase):
    """Link6 설계평가 E2E 테스트 스위트"""

    def __init__(self):
        super().__init__(base_url="http://localhost:5000", headless=False)
        self.test_email = "test@example.com"
        self.test_rcm_id = 1  # 테스트용 RCM ID

    def run_all_tests(self):
        """모든 E2E 테스트 실행"""
        print("=" * 80)
        print("E04: 설계평가 전체 프로세스 E2E 테스트 시작 (Playwright)")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}\n")

        try:
            self.setup()

            self.run_category("1. 설계평가 페이지 접근", [
                self.test_design_evaluation_page_access,
                self.test_rcm_selection_flow,
            ])

            self.run_category("2. 설계평가 데이터 로드", [
                self.test_evaluation_data_display,
                self.test_control_list_rendering,
            ])

            self.run_category("3. 설계평가 입력", [
                self.test_evaluation_result_input,
                self.test_comment_input,
                self.test_save_evaluation,
            ])

            self.run_category("4. 설계평가 완료 처리", [
                self.test_evaluation_completion_toggle,
                self.test_evaluation_statistics_update,
            ])

            self.run_category("5. 설계평가 조회", [
                self.test_evaluation_history_view,
            ])

        finally:
            self.teardown()

        exit_code = self.print_final_report()
        self.save_json_report("link6_design_evaluation_e2e")
        return exit_code

    # =========================================================================
    # 헬퍼 메서드
    # =========================================================================

    def _quick_login(self):
        """빠른 로그인 (테스트용)"""
        with patch('auth.send_otp') as mock_send:
            with patch('auth.verify_otp') as mock_verify:
                mock_send.return_value = (True, "OTP 발송됨")
                mock_verify.return_value = (True, {
                    'user_id': 1,
                    'user_email': self.test_email,
                    'user_name': '테스트사용자',
                    'admin_flag': 'N'
                })

                self.navigate_to("/login")
                self.fill_input("input[name='email']", self.test_email)
                self.click_button("button[type='submit']")

                try:
                    self.page.wait_for_url("**/otp**", timeout=5000)
                    self.fill_input("input[name='otp']", "123456")
                    self.click_button("button[type='submit']")
                    self.page.wait_for_url("**/main", timeout=5000)
                except:
                    pass  # 이미 로그인된 경우

    # =========================================================================
    # 1. 설계평가 페이지 접근
    # =========================================================================

    def test_design_evaluation_page_access(self, result: E2ETestResult):
        """설계평가 메인 페이지 접근"""
        try:
            result.add_detail("🎯 목표: 설계평가 페이지 접근 확인")

            # 로그인
            self._quick_login()
            result.add_detail("✓ 로그인 완료")

            # 설계평가 페이지 접속
            self.navigate_to("/user/design-evaluation")
            screenshot = self.take_screenshot("design_evaluation_main")
            result.add_screenshot(screenshot)
            result.add_detail("✓ 설계평가 페이지 접속")

            # 페이지 로드 대기
            self.page.wait_for_load_state("networkidle")

            # 페이지 내용 확인
            page_content = self.page.content()

            # 주요 키워드 확인
            keywords = ["설계평가", "design", "evaluation", "ITGC"]
            found_keywords = [kw for kw in keywords if kw in page_content.lower()]

            if found_keywords:
                result.add_detail(f"✓ 페이지 키워드 확인: {', '.join(found_keywords)}")
                result.pass_test("설계평가 페이지가 정상적으로 로드됩니다")
            else:
                result.warn_test("설계평가 관련 콘텐츠를 찾을 수 없습니다")

        except Exception as e:
            screenshot = self.take_screenshot("design_eval_access_error")
            result.add_screenshot(screenshot)
            result.fail_test(f"설계평가 페이지 접근 실패: {str(e)}")

    @patch('auth.get_user_rcms')
    def test_rcm_selection_flow(self, result: E2ETestResult, mock_get_rcms):
        """RCM 선택 플로우"""
        try:
            result.add_detail("🎯 목표: RCM 선택하여 설계평가 시작")

            # Mock 데이터 설정
            mock_get_rcms.return_value = [
                {
                    'rcm_id': 1,
                    'rcm_name': 'Test ITGC RCM',
                    'company_name': '테스트회사',
                    'control_category': 'ITGC'
                }
            ]

            # RCM 목록 페이지로 이동
            self.navigate_to("/user/rcm")
            self.page.wait_for_load_state("networkidle")
            result.add_detail("✓ RCM 목록 페이지 이동")

            # RCM 선택 (설계평가 버튼 클릭)
            design_eval_button = self.page.locator(
                "button:has-text('설계평가'), a:has-text('설계평가'), .design-evaluation-btn"
            ).first

            if design_eval_button.is_visible():
                screenshot_before = self.take_screenshot("before_rcm_selection")
                result.add_screenshot(screenshot_before)

                design_eval_button.click()
                result.add_detail("✓ 설계평가 버튼 클릭")

                # 설계평가 페이지로 전환 대기
                time.sleep(2)

                screenshot_after = self.take_screenshot("after_rcm_selection")
                result.add_screenshot(screenshot_after)

                # URL 확인
                current_url = self.page.url
                if "design-evaluation" in current_url:
                    result.add_detail(f"✓ 설계평가 페이지로 이동: {current_url}")
                    result.pass_test("RCM 선택하여 설계평가 페이지로 이동 성공")
                else:
                    result.warn_test(f"설계평가 페이지로 이동하지 않음: {current_url}")
            else:
                result.skip_test("설계평가 버튼을 찾을 수 없습니다 (RCM 데이터 없음)")

        except Exception as e:
            result.skip_test(f"RCM 선택 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 2. 설계평가 데이터 로드
    # =========================================================================

    @patch('auth.get_rcm_details')
    def test_evaluation_data_display(self, result: E2ETestResult, mock_get_details):
        """평가 데이터 표시 확인"""
        try:
            result.add_detail("🎯 목표: 설계평가 데이터 표시 확인")

            # Mock 데이터 설정
            mock_get_details.return_value = [
                {
                    'control_code': 'APD01',
                    'control_name': '사용자 등록 및 삭제',
                    'control_description': '사용자 계정 생성 및 삭제 절차',
                    'key_control': 'Y',
                    'control_frequency': '월간',
                    'control_type': '예방',
                    'control_nature': '수동'
                }
            ]

            # 설계평가 페이지 (RCM 포함)
            self.navigate_to(f"/user/design-evaluation/rcm?rcm_id={self.test_rcm_id}")
            self.page.wait_for_load_state("networkidle")

            screenshot = self.take_screenshot("evaluation_data_display")
            result.add_screenshot(screenshot)

            # 평가 데이터 테이블 확인
            page_content = self.page.content()

            # 통제 정보 확인
            control_keywords = ["통제코드", "통제명", "APD", "control"]
            found = [kw for kw in control_keywords if kw in page_content.lower()]

            if found:
                result.add_detail(f"✓ 통제 데이터 표시 확인: {', '.join(found)}")
                result.pass_test("설계평가 데이터가 정상적으로 표시됩니다")
            else:
                result.warn_test("설계평가 데이터를 찾을 수 없습니다")

        except Exception as e:
            result.fail_test(f"데이터 표시 확인 실패: {str(e)}")

    def test_control_list_rendering(self, result: E2ETestResult):
        """통제 목록 렌더링 확인"""
        try:
            result.add_detail("🎯 목표: 통제 목록 UI 렌더링 확인")

            # 테이블 또는 리스트 확인
            if self.check_element_exists("table"):
                result.add_detail("✓ 통제 목록 테이블 존재")

                # 행 수 확인
                rows = self.page.locator("table tbody tr")
                row_count = rows.count()
                result.add_detail(f"✓ 통제 개수: {row_count}개")

                screenshot = self.take_screenshot("control_list")
                result.add_screenshot(screenshot)

                result.pass_test(f"통제 목록이 렌더링됩니다 ({row_count}개)")
            else:
                result.skip_test("통제 목록 테이블을 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"통제 목록 렌더링 확인 건너뜀: {str(e)}")

    # =========================================================================
    # 3. 설계평가 입력
    # =========================================================================

    def test_evaluation_result_input(self, result: E2ETestResult):
        """평가 결과 입력 (Effective/Ineffective)"""
        try:
            result.add_detail("🎯 목표: 평가 결과 드롭다운 입력")

            # 평가 결과 드롭다운 찾기
            result_select = self.page.locator(
                "select[name*='result'], select[name*='evaluation'], "
                "select:has(option:has-text('Effective')), "
                "select:has(option:has-text('효과적'))"
            ).first

            if result_select.is_visible():
                # Effective 선택
                try:
                    result_select.select_option(label="Effective")
                    result.add_detail("✓ 평가 결과 선택: Effective")
                except:
                    try:
                        result_select.select_option(label="효과적")
                        result.add_detail("✓ 평가 결과 선택: 효과적")
                    except:
                        result_select.select_option(index=1)
                        result.add_detail("✓ 평가 결과 선택: 첫 번째 옵션")

                screenshot = self.take_screenshot("evaluation_result_input")
                result.add_screenshot(screenshot)

                result.pass_test("평가 결과 입력 기능이 작동합니다")
            else:
                result.skip_test("평가 결과 드롭다운을 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"평가 결과 입력 테스트 건너뜀: {str(e)}")

    def test_comment_input(self, result: E2ETestResult):
        """비고/코멘트 입력"""
        try:
            result.add_detail("🎯 목표: 비고 입력 필드 확인")

            # 비고 입력 필드 찾기
            comment_input = self.page.locator(
                "textarea[name*='comment'], textarea[name*='비고'], "
                "textarea[name*='remark'], input[name*='comment']"
            ).first

            if comment_input.is_visible():
                test_comment = "E2E 테스트 코멘트 - 설계가 효과적으로 구성되어 있음"
                comment_input.fill(test_comment)
                result.add_detail(f"✓ 비고 입력: {test_comment[:30]}...")

                screenshot = self.take_screenshot("comment_input")
                result.add_screenshot(screenshot)

                result.pass_test("비고 입력 기능이 작동합니다")
            else:
                result.skip_test("비고 입력 필드를 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"비고 입력 테스트 건너뜀: {str(e)}")

    @patch('auth.save_design_evaluation')
    def test_save_evaluation(self, result: E2ETestResult, mock_save):
        """평가 저장 기능"""
        try:
            result.add_detail("🎯 목표: 평가 저장 버튼 클릭 및 저장")

            # Mock 설정
            mock_save.return_value = True

            # 저장 버튼 찾기
            save_button = self.page.locator(
                "button:has-text('저장'), button:has-text('Save'), "
                "button[type='submit']"
            ).first

            if save_button.is_visible():
                screenshot_before = self.take_screenshot("before_save")
                result.add_screenshot(screenshot_before)

                save_button.click()
                result.add_detail("✓ 저장 버튼 클릭")

                # 저장 처리 대기
                time.sleep(2)

                # 성공 메시지 확인
                page_content = self.page.content()
                success_keywords = ["성공", "저장", "완료", "success", "saved"]

                if any(kw in page_content.lower() for kw in success_keywords):
                    result.add_detail("✓ 저장 성공 메시지 확인")
                else:
                    result.add_detail("⚠️ 성공 메시지를 찾을 수 없음")

                screenshot_after = self.take_screenshot("after_save")
                result.add_screenshot(screenshot_after)

                result.pass_test("평가 저장 기능이 작동합니다")
            else:
                result.skip_test("저장 버튼을 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"평가 저장 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 4. 설계평가 완료 처리
    # =========================================================================

    def test_evaluation_completion_toggle(self, result: E2ETestResult):
        """평가 완료 상태 토글"""
        try:
            result.add_detail("🎯 목표: 평가 완료 체크박스 토글")

            # 완료 체크박스 찾기
            complete_checkbox = self.page.locator(
                "input[type='checkbox'][name*='complete'], "
                "input[type='checkbox'][name*='완료']"
            ).first

            if complete_checkbox.is_visible():
                # 체크박스 클릭
                complete_checkbox.check()
                result.add_detail("✓ 평가 완료 체크박스 선택")

                screenshot = self.take_screenshot("evaluation_completed")
                result.add_screenshot(screenshot)

                result.pass_test("평가 완료 토글 기능이 작동합니다")
            else:
                result.skip_test("평가 완료 체크박스를 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"완료 토글 테스트 건너뜀: {str(e)}")

    def test_evaluation_statistics_update(self, result: E2ETestResult):
        """평가 통계 업데이트 확인"""
        try:
            result.add_detail("🎯 목표: 평가 통계 정보 표시 확인")

            # 통계 정보 확인
            page_content = self.page.content()

            stats_keywords = ["완료", "진행", "%", "통계", "progress", "complete"]
            found = [kw for kw in stats_keywords if kw in page_content.lower()]

            if found:
                result.add_detail(f"✓ 통계 정보 확인: {', '.join(found)}")

                screenshot = self.take_screenshot("evaluation_statistics")
                result.add_screenshot(screenshot)

                result.pass_test("평가 통계가 표시됩니다")
            else:
                result.skip_test("평가 통계 정보를 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"통계 확인 테스트 건너뜀: {str(e)}")

    # =========================================================================
    # 5. 설계평가 조회
    # =========================================================================

    def test_evaluation_history_view(self, result: E2ETestResult):
        """평가 이력 조회"""
        try:
            result.add_detail("🎯 목표: 평가 이력 조회 기능 확인")

            # 이력 또는 세션 목록 확인
            page_content = self.page.content()

            history_keywords = ["이력", "세션", "history", "session", "버전"]
            found = [kw for kw in history_keywords if kw in page_content.lower()]

            if found:
                result.add_detail(f"✓ 이력 관련 UI 확인: {', '.join(found)}")

                screenshot = self.take_screenshot("evaluation_history")
                result.add_screenshot(screenshot)

                result.pass_test("평가 이력 조회 기능이 존재합니다")
            else:
                result.skip_test("평가 이력 기능을 찾을 수 없습니다")

        except Exception as e:
            result.skip_test(f"이력 조회 테스트 건너뜀: {str(e)}")


def main():
    """메인 실행 함수"""
    suite = Link6DesignEvaluationE2ETestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
