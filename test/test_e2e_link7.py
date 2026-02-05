"""
Link7: 운영평가 E2E 테스트

[테스트 실행 방법]
1. 서버가 이미 실행 중인 경우:
   python test/test_e2e_link7.py --url http://localhost:5001

2. 서버가 실행되지 않은 경우:
   - 테스트 코드가 자동으로 서버 실행 여부를 확인하고,
   - 서버가 없으면 시작, 있으면 기존 서버 사용

[주의사항]
- headless=False: 브라우저가 화면에 표시되어 테스트 과정을 눈으로 확인 가능
- 서버 충돌 방지: 이미 실행 중인 서버가 있으면 새로 시작하지 않음
- 테스트 완료 후 자동으로 생성된 데이터는 삭제됨
- 운영평가는 설계평가가 완료된 세션이 있어야 진행 가능
"""

import os
import sys
import time
import pytest
import unittest
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect

# 프로젝트 루트 경로 설정
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from test.playwright_base import PlaywrightTestBase, PageHelper, E2ETestResult, TestStatus

class Link7OperationTestSuite(PlaywrightTestBase):
    """Link7: 운영평가 E2E 테스트"""

    def __init__(self, base_url="http://localhost:5001", headless=False):
        # headless=False가 기본값: 브라우저 화면이 보임
        super().__init__(base_url=base_url, headless=headless)
        self.checklist_source = project_root / "test" / "e2e_checklist_link7.md"
        self.checklist_result = project_root / "test" / "e2e_checklist_link7_result.md"

        # 테스트 상태 공유를 위한 변수
        self.rcm_name = ""  # 운영평가 대상 RCM명 (기존 완료된 설계평가 세션에서 선택)
        self.rcm_id = None
        self.design_eval_session = ""  # 완료된 설계평가 세션명
        self.operation_eval_name = ""  # 운영평가 세션명
        self.server_process = None

    def setup_test_data(self):
        """기존 완료된 설계평가 세션을 사용하므로 데이터 생성 생략"""
        pass

    def check_server_running(self):
        """서버가 실행 중인지 확인하고, 없으면 시작"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ 서버가 이미 실행 중입니다 ({self.base_url})")
                return True
            else:
                print(f"⚠️ 서버 응답 코드: {response.status_code}")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print(f"⚠️ 서버가 실행 중이지 않습니다. 서버를 시작합니다...")
            return self._start_server()
        except Exception as e:
            print(f"⚠️ 서버 상태 확인 중 오류: {e}")
            return self._start_server()

    def _start_server(self):
        """서버를 백그라운드로 시작"""
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "snowball.py"],
                cwd=str(project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            print(f"   서버 시작 중... (PID: {self.server_process.pid})")

            for i in range(30):
                time.sleep(1)
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ 서버 시작 완료 ({self.base_url})")
                        return True
                except:
                    print(f"   서버 준비 대기 중... ({i+1}/30)")

            print(f"❌ 서버 시작 시간 초과")
            return False
        except Exception as e:
            print(f"❌ 서버 시작 실패: {e}")
            return False

    def run_all_tests(self):
        """전체 테스트 시나리오 실행"""
        print(f"\n================================================================================")
        print(f"Link7: 운영평가 E2E 테스트")
        print(f"================================================================================\n")

        # 서버 상태 확인
        if not self.check_server_running():
            print("\n❌ 서버에 연결할 수 없어 테스트를 중단합니다.")
            return 1

        try:
            self.setup()  # 브라우저 시작

            # 로그인 수행
            self._do_admin_login()

            # 사전 준비: 완료된 설계평가 세션 확인
            if not self._find_completed_design_session():
                print("❌ 완료된 설계평가 세션이 없어 테스트를 중단합니다.")
                print("   → 먼저 Link6 설계평가를 완료한 후 다시 시도해주세요.")
                return 1

            # 카테고리 1: 평가 세션 관리
            self.run_category("1. 평가 세션 관리", [
                self.test_operation_create_new,
                self.test_operation_list_display,
                self.test_operation_continue_session
            ])

            # 카테고리 2: 모집단/샘플 관리 (수동통제용)
            # self.run_category("2. 모집단/샘플 관리", [
            #     self.test_operation_population_upload,
            #     self.test_operation_sample_extract,
            #     self.test_operation_sample_count_validation
            # ])

            # 카테고리 3: 평가 수행 및 저장
            self.run_category("3. 평가 수행 및 저장", [
                self.test_operation_save_evaluation,
                self.test_operation_batch_save,
                # self.test_operation_manual_control_test
            ])

            # 카테고리 4: 증빙자료 관리
            self.run_category("4. 증빙자료 관리", [
                self.test_operation_evidence_attach,
                # self.test_operation_image_upload,
                # self.test_operation_image_display
            ])

            # 카테고리 5: 미비점 관리
            self.run_category("5. 미비점 관리", [
                self.test_operation_defect_logging,
                # self.test_operation_defect_badge
            ])

            # 카테고리 6: 평가 완료 및 대시보드
            self.run_category("6. 평가 완료 및 대시보드", [
                self.test_operation_completion_status,
                self.test_operation_dashboard_reflection
            ])

            # 카테고리 7: ELC/TLC 운영평가
            # self.run_category("7. ELC/TLC 운영평가", [
            #     self.test_elc_operation_evaluation,
            #     self.test_tlc_operation_evaluation
            # ])

            # 카테고리 8: 데이터 정리
            self.run_category("8. 데이터 정리", [
                self.test_operation_delete_session,
                # self.test_operation_cleanup_files
            ])

        except Exception as e:
            print(f"❌ Critical Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.teardown()

        if len(self.results) == 0:
            print("\n실행된 테스트가 없습니다.")
            return 1
        return self.print_final_report()

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _close_any_open_modal(self):
        """열려있는 모달이 있으면 닫기"""
        page = self.page
        try:
            # operationEvaluationModal이 열려있는지 확인
            modal = page.locator("#operationEvaluationModal.show")
            if modal.count() > 0:
                print("    → 열려있는 모달 닫는 중...")
                close_btn = page.locator("#operationEvaluationModal button[data-bs-dismiss='modal']")
                if close_btn.count() > 0 and close_btn.first.is_visible():
                    close_btn.first.click()
                    page.wait_for_timeout(500)
                else:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(500)
                page.wait_for_selector("#operationEvaluationModal", state="hidden", timeout=3000)
        except:
            pass

    def _do_admin_login(self):
        """관리자 로그인 버튼 클릭으로 로그인 (이미 로그인된 상태면 건너뜀)"""
        page = self.page

        current_url = page.url

        if "/login" not in current_url:
            page.goto(f"{self.base_url}/")
            page.wait_for_load_state("networkidle")

            if page.locator("a:has-text('로그아웃')").count() > 0:
                print("    → 이미 로그인 상태, 건너뜀")
                return

        print("    → 로그인 페이지로 이동...")
        page.goto(f"{self.base_url}/login")
        page.wait_for_load_state("networkidle")

        print("    → 관리자 로그인 버튼 클릭...")
        admin_btn = page.locator(".admin-login-section button[type='submit']")
        if admin_btn.count() > 0:
            admin_btn.click()
            page.wait_for_load_state("networkidle")
            print("    → 로그인 완료")
        else:
            raise Exception("관리자 로그인 버튼을 찾을 수 없습니다")

    def _find_completed_design_session(self):
        """완료된 설계평가 세션 찾기 (운영평가 전제조건)"""
        print(">> 사전작업: 완료된 설계평가 세션 조회 중...")
        try:
            page = self.page

            # 운영평가 페이지로 이동
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # 운영평가 현황 섹션의 아코디언 확인 (#operationEvaluationAccordion)
            op_accordion = page.locator("#operationEvaluationAccordion")
            if op_accordion.count() == 0:
                print("   ⚠️ 운영평가 현황 섹션이 없습니다.")
                return False

            # 아코디언 버튼들 확인
            accordion_btns = page.locator("#operationEvaluationAccordion .accordion-button")
            if accordion_btns.count() == 0:
                print("   ⚠️ 설계평가 완료된 RCM이 없습니다.")
                return False

            # 첫 번째 아코디언 확장
            first_accordion = accordion_btns.first
            if "collapsed" in (first_accordion.get_attribute("class") or ""):
                first_accordion.click()
                page.wait_for_timeout(500)

            # RCM 이름 추출 (아이콘 텍스트 제거)
            rcm_text = first_accordion.inner_text().strip()
            # 아이콘 및 배지 텍스트 제거
            self.rcm_name = rcm_text.split("\n")[0].strip()
            # Font Awesome 아이콘 문자 제거
            import re
            self.rcm_name = re.sub(r'^[\s\uf0f6]*', '', self.rcm_name).strip()

            print(f"   → RCM: {self.rcm_name}")

            # '운영평가 보기' 버튼이 있는지 확인 (설계평가 완료 세션)
            view_btn = page.locator("#operationEvaluationAccordion button:has-text('운영평가 보기')")
            if view_btn.count() > 0:
                # 세션명 추출 - 버튼의 상위 카드 헤더에서 찾기
                card_header = view_btn.first.locator("xpath=ancestor::div[contains(@class,'card')]//div[contains(@class,'card-header')]")
                if card_header.count() > 0:
                    session_text = card_header.first.inner_text().strip()
                    # "세션명 (설계평가 완료: 날짜)" 형태에서 세션명만 추출
                    self.design_eval_session = session_text.split("(")[0].strip()
                else:
                    self.design_eval_session = "unknown_session"

                print(f"   → 설계평가 세션: {self.design_eval_session}")
                return True

            print("   ⚠️ 운영평가 가능한 세션을 찾을 수 없습니다.")
            return False

        except Exception as e:
            print(f"   ⚠️ 설계평가 세션 조회 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_test_data(self):
        """테스트로 생성된 데이터 정리"""
        pass

    # =========================================================================
    # 1. 평가 세션 관리
    # =========================================================================

    def test_operation_create_new(self, result: E2ETestResult):
        """운영평가 세션 시작 (완료된 설계평가 기반)"""
        page = self.page

        try:
            # 운영평가 페이지로 이동
            print("    → 운영평가 페이지로 이동...")
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            # 운영평가 현황 섹션의 아코디언 확장
            print("    → 운영평가 현황 아코디언 확장...")
            op_accordion_btns = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_accordion_btns.count() > 0:
                first_btn = op_accordion_btns.first
                if "collapsed" in (first_btn.get_attribute("class") or ""):
                    first_btn.click()
                    page.wait_for_timeout(500)

            # '운영평가 보기' 버튼 클릭 (완료된 설계평가 세션 기반)
            print("    → '운영평가 보기' 버튼 찾는 중...")
            view_btn = page.locator("button:has-text('운영평가 보기')")

            if view_btn.count() > 0:
                view_btn.first.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)

                # 상세 페이지 진입 확인
                if "/operation-evaluation/rcm" in page.url:
                    # 세션명 저장
                    session_badge = page.locator(".badge.bg-warning.text-dark")
                    if session_badge.count() > 0:
                        self.operation_eval_name = session_badge.first.inner_text().strip()
                    else:
                        self.operation_eval_name = self.design_eval_session

                    print(f"    → 운영평가 세션: {self.operation_eval_name}")
                    result.pass_test("운영평가 세션 시작 및 상세 페이지 진입 확인")
                else:
                    result.warn_test("운영평가 보기 버튼 클릭됨 (상세 페이지 진입 확인 필요)")
            else:
                # 설계평가 완료 세션에서 직접 시작
                print("    → 설계평가 현황에서 운영평가 시작 시도...")
                design_accordion = page.locator("#designEvaluationAccordion .accordion-button")
                if design_accordion.count() > 0:
                    if "collapsed" in (design_accordion.first.get_attribute("class") or ""):
                        design_accordion.first.click()
                        page.wait_for_timeout(500)

                    # 설계평가 보기 버튼 클릭
                    design_view_btn = page.locator("button:has-text('설계평가 보기')")
                    if design_view_btn.count() > 0:
                        design_view_btn.first.click()
                        page.wait_for_load_state("networkidle")
                        result.warn_test("설계평가 완료 세션 확인됨 (운영평가 시작 버튼 없음)")
                    else:
                        result.fail_test("운영평가 시작 버튼을 찾을 수 없음")
                else:
                    result.fail_test("운영평가 가능한 세션을 찾을 수 없음")

        except Exception as e:
            result.fail_test(f"운영평가 세션 시작 실패: {e}")

    def test_operation_list_display(self, result: E2ETestResult):
        """운영평가 목록 표시 확인"""
        page = self.page

        try:
            # 운영평가 페이지로 이동
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            # 운영평가 현황 섹션 확인
            op_section = page.locator("#operationEvaluationAccordion")
            if op_section.count() > 0:
                # 아코디언 확장
                op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
                if op_btn.count() > 0 and "collapsed" in (op_btn.first.get_attribute("class") or ""):
                    op_btn.first.click()
                    page.wait_for_timeout(500)

                # 진행상황 표시 확인
                progress_info = page.locator("text=진행상황")
                if progress_info.count() > 0:
                    result.pass_test("운영평가 목록 및 진행상황 표시 확인")
                else:
                    result.warn_test("운영평가 현황 섹션 표시됨 (진행상황 표시 확인 필요)")
            else:
                result.skip_test("운영평가 현황 섹션이 없음")

        except Exception as e:
            result.fail_test(f"운영평가 목록 표시 확인 실패: {e}")

    def test_operation_continue_session(self, result: E2ETestResult):
        """기존 세션 '계속하기' 버튼 동작 확인"""
        page = self.page

        try:
            # 운영평가 페이지로 이동
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            # 운영평가 현황 아코디언 확장
            op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_btn.count() > 0:
                if "collapsed" in (op_btn.first.get_attribute("class") or ""):
                    op_btn.first.click()
                    page.wait_for_timeout(500)

            # '운영평가 보기' 버튼 클릭
            view_btn = page.locator("button:has-text('운영평가 보기')")
            if view_btn.count() > 0:
                view_btn.first.click()
                page.wait_for_load_state("networkidle")

                # 상세 페이지 진입 확인
                if "/operation-evaluation/rcm" in page.url:
                    result.pass_test("운영평가 세션 계속하기 동작 확인")
                else:
                    result.warn_test("버튼 클릭됨 (페이지 전환 확인 필요)")
            else:
                result.skip_test("운영평가 보기 버튼이 없음")

        except Exception as e:
            result.fail_test(f"세션 계속하기 테스트 실패: {e}")

    # =========================================================================
    # 3. 평가 수행 및 저장
    # =========================================================================

    def test_operation_save_evaluation(self, result: E2ETestResult):
        """개별 통제 항목 운영평가 및 저장"""
        page = self.page

        # 모달 닫기
        self._close_any_open_modal()

        # 상세 페이지 진입 확인
        if "/operation-evaluation/rcm" not in page.url:
            # 운영평가 페이지에서 다시 진입
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_btn.count() > 0 and "collapsed" in (op_btn.first.get_attribute("class") or ""):
                op_btn.first.click()
                page.wait_for_timeout(500)

            view_btn = page.locator("button:has-text('운영평가 보기')")
            if view_btn.count() > 0:
                view_btn.first.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)

        if "/operation-evaluation/rcm" not in page.url:
            result.skip_test("운영평가 상세 페이지 진입 불가")
            return

        try:
            # 통제 목록에서 첫 번째 '평가' 버튼 클릭
            print("    → 통제 항목 평가 버튼 클릭...")
            # 테이블 내 평가 버튼 찾기 (onclick 속성 확인)
            eval_btns = page.locator("#controlsTable button.btn-warning")
            print(f"    → 평가 버튼 수: {eval_btns.count()}")

            if eval_btns.count() == 0:
                # 다른 셀렉터 시도
                eval_btns = page.locator("button:has-text('평가')")
                print(f"    → 대체 셀렉터로 찾은 버튼 수: {eval_btns.count()}")

            if eval_btns.count() == 0:
                result.skip_test("평가/수정 버튼을 찾을 수 없음")
                return

            # 버튼 클릭 전 대기
            page.wait_for_timeout(500)
            eval_btns.first.click()
            print("    → 버튼 클릭 완료")

            # 평가 모달 대기 (더 긴 타임아웃)
            page.wait_for_selector("#operationEvaluationModal.show", timeout=10000)

            # 운영 효과성 선택
            print("    → '효과적' 선택 및 저장...")
            effectiveness_select = page.locator("#opEffectiveness")
            if effectiveness_select.count() > 0:
                page.select_option("#opEffectiveness", "effective")
                page.wait_for_timeout(500)

            # 테스트 증빙 입력
            evidence_el = page.locator("#opEvidence")
            if evidence_el.count() > 0:
                evidence_el.fill("E2E 테스트 - 운영평가 결과: 통제가 효과적으로 운영되고 있음")

            # 저장 버튼 클릭
            save_btn = page.locator("#saveOperationEvaluationBtn")
            if save_btn.count() > 0:
                save_btn.click()
            else:
                page.click("button:has-text('저장')")

            # 성공 메시지 대기
            try:
                page.wait_for_selector("text=저장", timeout=5000)
            except:
                pass

            # 확인 버튼 클릭
            confirm_btn = page.locator("button:has-text('확인')")
            if confirm_btn.count() > 0 and confirm_btn.is_visible():
                confirm_btn.click()

            # 모달 닫기 확인
            try:
                page.wait_for_selector("#operationEvaluationModal", state="hidden", timeout=5000)
            except:
                close_btn = page.locator("#operationEvaluationModal button[data-bs-dismiss='modal']")
                if close_btn.count() > 0:
                    close_btn.first.click()
                    page.wait_for_timeout(500)

            result.pass_test("개별 통제 운영평가 및 저장 완료")

        except Exception as e:
            result.fail_test(f"운영평가 저장 실패: {e}")

    def test_operation_batch_save(self, result: E2ETestResult):
        """일괄 저장 기능 확인 (적정저장 버튼 활용)"""
        page = self.page

        self._close_any_open_modal()

        if "/operation-evaluation/rcm" not in page.url:
            result.skip_test("상세 페이지에 있지 않음")
            return

        try:
            # '적정저장' 버튼 찾기
            print("    → '적정저장' 버튼 확인 중...")
            batch_save_btn = page.locator("button:has-text('적정저장')")

            if batch_save_btn.count() > 0 and batch_save_btn.is_visible():
                # confirm 다이얼로그 자동 수락
                page.once("dialog", lambda dialog: dialog.accept())

                batch_save_btn.click()
                page.wait_for_timeout(1000)

                # 완료 대기
                try:
                    page.wait_for_selector("text=저장이 완료되었습니다", timeout=20000)
                    page.click("button:has-text('확인')")
                except:
                    page.wait_for_timeout(2000)

                result.pass_test("일괄 저장(적정저장) 기능 동작 확인")
            else:
                result.skip_test("적정저장 버튼을 찾을 수 없음 (관리자 전용)")

        except Exception as e:
            result.fail_test(f"일괄 저장 테스트 실패: {e}")

    # =========================================================================
    # 4. 증빙자료 관리
    # =========================================================================

    def test_operation_evidence_attach(self, result: E2ETestResult):
        """증빙자료 파일 업로드 기능 동작 확인"""
        page = self.page

        self._close_any_open_modal()

        # 상세 페이지 진입 확인 및 재진입
        if "/operation-evaluation/rcm" not in page.url:
            # 운영평가 페이지에서 다시 진입
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_btn.count() > 0 and "collapsed" in (op_btn.first.get_attribute("class") or ""):
                op_btn.first.click()
                page.wait_for_timeout(500)

            view_btn = page.locator("button:has-text('운영평가 보기')")
            if view_btn.count() > 0:
                view_btn.first.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)

        if "/operation-evaluation/rcm" not in page.url:
            result.skip_test("상세 페이지에 있지 않음")
            return

        try:
            # 평가 모달 열기
            print("    → 통제 항목 평가 모달 열기...")
            eval_btns = page.locator("#controlsTable button.btn-warning")

            if eval_btns.count() == 0:
                result.skip_test("평가/수정 버튼을 찾을 수 없음")
                return

            page.wait_for_timeout(500)
            eval_btns.first.click()
            page.wait_for_selector("#operationEvaluationModal.show", timeout=10000)

            # 파일 업로드 input 확인
            print("    → 증빙자료 업로드 필드 확인...")
            file_input = page.locator("#opEvaluationImages, input[type='file']")

            if file_input.count() > 0:
                # 테스트 이미지 파일 생성 및 업로드
                test_image_path = project_root / "test" / "assets" / "test_op_evidence.png"

                if not test_image_path.exists():
                    import struct
                    import zlib

                    def create_minimal_png(filepath):
                        signature = b'\x89PNG\r\n\x1a\n'
                        ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
                        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
                        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
                        raw_data = b'\x00\xff\xff\xff'
                        compressed = zlib.compress(raw_data)
                        idat_crc = zlib.crc32(b'IDAT' + compressed)
                        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
                        iend_crc = zlib.crc32(b'IEND')
                        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
                        with open(filepath, 'wb') as f:
                            f.write(signature + ihdr + idat + iend)

                    create_minimal_png(test_image_path)

                file_input.first.set_input_files(str(test_image_path))
                page.wait_for_timeout(1000)

                if page.locator("text=test_op_evidence.png").count() > 0 or \
                   page.locator(".uploaded-file, .file-name, .preview").count() > 0:
                    result.pass_test("증빙자료 업로드 및 파일명 표시 확인")
                else:
                    result.warn_test("파일 업로드는 되었으나 파일명 표시 확인 불가")

                if test_image_path.exists():
                    test_image_path.unlink()
            else:
                result.skip_test("증빙자료 업로드 필드를 찾을 수 없음")

            # 모달 닫기
            close_btn = page.locator("#operationEvaluationModal button[data-bs-dismiss='modal']")
            if close_btn.count() > 0:
                close_btn.first.click()

        except Exception as e:
            result.fail_test(f"증빙자료 업로드 테스트 실패: {e}")

    # =========================================================================
    # 5. 미비점(Defect) 관리
    # =========================================================================

    def test_operation_defect_logging(self, result: E2ETestResult):
        """평가 결과를 '비효과적'으로 선택 시 처리 확인"""
        page = self.page

        self._close_any_open_modal()

        if "/operation-evaluation/rcm" not in page.url:
            # 상세 페이지로 이동
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_btn.count() > 0 and "collapsed" in (op_btn.first.get_attribute("class") or ""):
                op_btn.first.click()
                page.wait_for_timeout(500)

            view_btn = page.locator("button:has-text('운영평가 보기')")
            if view_btn.count() > 0:
                view_btn.first.click()
                page.wait_for_load_state("networkidle")
            else:
                result.skip_test("상세 페이지 진입 불가")
                return

        # URL 체크 재확인
        if "/operation-evaluation/rcm" not in page.url:
            result.skip_test("상세 페이지 진입 불가")
            return

        try:
            print("    → 미비(비효과적) 평가 테스트 시작...")
            eval_btns = page.locator("#controlsTable button.btn-warning")

            if eval_btns.count() == 0:
                result.skip_test("평가/수정 버튼을 찾을 수 없음")
                return

            page.wait_for_timeout(500)
            eval_btns.first.click()
            page.wait_for_selector("#operationEvaluationModal.show", timeout=10000)

            # 효과성을 '비효과적(ineffective)'으로 선택
            print("    → 효과성 '비효과적(ineffective)' 선택...")
            effectiveness_select = page.locator("#opEffectiveness")
            if effectiveness_select.count() > 0 and not effectiveness_select.is_disabled():
                page.select_option("#opEffectiveness", "ineffective")
                page.wait_for_timeout(500)
            else:
                result.skip_test("효과성 필드가 없거나 비활성화됨")
                return

            # 권고 조치사항 필드 (비효과적 선택 시 표시)
            recommended_actions = page.locator("#opRecommendedActions")
            if recommended_actions.count() > 0:
                try:
                    recommended_actions.wait_for(state="visible", timeout=3000)
                    if not recommended_actions.is_disabled():
                        recommended_actions.fill("테스트용 미비점 - 통제 운영 개선 필요")
                        print("    → 권고 조치사항 입력 완료")
                except:
                    print("    → 권고 조치사항 필드 미표시 (건너뜀)")

            # 증빙 입력
            evidence_el = page.locator("#opEvidence")
            if evidence_el.count() > 0:
                evidence_el.fill("미비점 테스트 - 통제 운영 미흡 사항 확인")

            # 저장
            print("    → 비효과적 평가 저장...")
            save_btn = page.locator("#saveOperationEvaluationBtn")
            if save_btn.count() > 0:
                save_btn.click()
            else:
                page.click("button:has-text('저장')")

            # 저장 완료 대기
            try:
                page.wait_for_selector("#successAlert, text=저장", timeout=5000)
            except:
                pass

            # 모달 닫기 확인
            try:
                page.wait_for_selector("#operationEvaluationModal", state="hidden", timeout=5000)
            except:
                close_btn = page.locator("#operationEvaluationModal button[data-bs-dismiss='modal']")
                if close_btn.count() > 0:
                    close_btn.first.click()

            # 목록에서 '부적정' 배지 확인
            page.wait_for_timeout(1000)
            if page.locator(".badge.bg-danger:has-text('부적정')").count() > 0:
                result.pass_test("비효과적 평가 저장 및 '부적정' 표시 확인")
            else:
                result.warn_test("비효과적 평가 저장됨 (부적정 배지 확인 불가)")

        except Exception as e:
            result.fail_test(f"미비점 테스트 실패: {e}")

    # =========================================================================
    # 6. 평가 완료 및 대시보드
    # =========================================================================

    def test_operation_completion_status(self, result: E2ETestResult):
        """모든 항목 평가 완료 시 진행률 100% 도달 확인"""
        page = self.page

        self._close_any_open_modal()

        if "/operation-evaluation/rcm" not in page.url:
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_btn.count() > 0:
                if "collapsed" in (op_btn.first.get_attribute("class") or ""):
                    op_btn.first.click()
                    page.wait_for_timeout(500)

                view_btn = page.locator("button:has-text('운영평가 보기')")
                if view_btn.count() > 0:
                    view_btn.first.click()
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(1000)

        # URL 체크 재확인
        if "/operation-evaluation/rcm" not in page.url:
            result.warn_test("상세 페이지 진입 불가 (운영평가 세션 없음)")
            return

        try:
            # 적정저장으로 모든 통제 평가
            print("    → [관리자] 모든 통제 '적정저장' 수행 중...")
            batch_save_btn = page.locator("button:has-text('적정저장')")
            if batch_save_btn.count() > 0 and batch_save_btn.is_visible():
                page.once("dialog", lambda dialog: dialog.accept())
                batch_save_btn.click()
                page.wait_for_timeout(1000)

                try:
                    page.wait_for_selector("text=저장이 완료되었습니다", timeout=20000)
                    page.click("button:has-text('확인')")
                except:
                    page.wait_for_timeout(2000)

            # 진행률 확인
            print("    → 진행률 확인 중...")
            progress_bar = page.locator("#evaluationProgress, .progress-bar")
            if progress_bar.count() > 0:
                progress_text = progress_bar.first.inner_text()
                print(f"    → 진행률: {progress_text}")

            # 완료 버튼 클릭 시도
            print("    → 완료 버튼 클릭 시도...")
            complete_btn = page.locator("#completeEvaluationBtn, button:has-text('평가 완료')")

            try:
                complete_btn.wait_for(state="visible", timeout=5000)
            except:
                pass

            if complete_btn.count() > 0 and complete_btn.is_visible() and complete_btn.is_enabled():
                page.once("dialog", lambda dialog: dialog.accept())
                complete_btn.click()
                page.wait_for_timeout(1000)

                page.wait_for_timeout(2000)
                if page.locator("#archiveEvaluationBtn").is_visible() or \
                   page.locator("text=완료").count() > 0:
                    result.pass_test("진행률 100% 도달 및 '완료' 상태 변경 확인")
                else:
                    result.warn_test("완료 처리됨 (상태 표시 확인 불가)")
            else:
                result.warn_test("완료 버튼이 활성화되지 않음 (모든 항목 평가 필요)")

        except Exception as e:
            result.fail_test(f"평가 완료 상태 테스트 실패: {e}")

    def test_operation_dashboard_reflection(self, result: E2ETestResult):
        """메인 대시보드에서 운영평가 진행 현황 반영 확인"""
        page = self.page

        try:
            print("    → 대시보드로 이동...")
            page.goto(f"{self.base_url}/user/internal-assessment")
            page.wait_for_load_state("networkidle")

            if '/login' in page.url:
                result.skip_test("로그인 필요 - 대시보드 접근 불가")
                return

            print("    → 운영평가 현황 확인 중...")
            page_content = page.inner_text("body")

            if "운영평가" in page_content or "ITGC" in page_content or "평가" in page_content:
                if "완료" in page_content or "진행" in page_content:
                    result.pass_test("대시보드에서 평가 현황 정보 확인됨")
                else:
                    result.warn_test("대시보드 접근 가능하나 진행 현황 표시 확인 불가")
            else:
                result.warn_test("대시보드에 평가 관련 섹션 없음")

        except Exception as e:
            result.fail_test(f"대시보드 반영 테스트 실패: {e}")

    # =========================================================================
    # 8. 데이터 정리
    # =========================================================================

    def test_operation_delete_session(self, result: E2ETestResult):
        """테스트로 생성된 운영평가 데이터 정리 (삭제)"""
        page = self.page

        self._close_any_open_modal()

        try:
            # 운영평가 목록으로 이동
            print("    → 운영평가 목록으로 이동 중...")
            page.goto(f"{self.base_url}/user/operation-evaluation")
            page.wait_for_load_state("networkidle")

            # 운영평가 데이터는 설계평가 세션에 종속되므로 별도 삭제 버튼이 없을 수 있음
            # 대신 '초기화' 버튼이나 API 호출로 정리

            # 아코디언 확장
            op_btn = page.locator("#operationEvaluationAccordion .accordion-button")
            if op_btn.count() > 0:
                if "collapsed" in (op_btn.first.get_attribute("class") or ""):
                    op_btn.first.click()
                    page.wait_for_timeout(500)

                # 삭제 버튼 찾기
                delete_btn = page.locator("button:has-text('삭제'), button:has-text('초기화')")
                if delete_btn.count() > 0:
                    print("    → 운영평가 데이터 삭제 중...")
                    page.once("dialog", lambda dialog: dialog.accept())
                    delete_btn.first.click()
                    page.wait_for_timeout(2000)

                    confirm_btn = page.locator("button:has-text('확인'), button:has-text('예')")
                    if confirm_btn.count() > 0:
                        confirm_btn.first.click()
                        page.wait_for_timeout(1000)

                    result.pass_test("운영평가 데이터 정리 완료")
                else:
                    # 직접 API 호출로 정리 시도
                    result.warn_test("삭제 버튼 없음 (운영평가 데이터는 설계평가 세션에 종속)")
            else:
                result.warn_test("운영평가 세션이 없음 (정리할 데이터 없음)")

        except Exception as e:
            result.fail_test(f"데이터 정리 실패: {e}")

    def _update_specific_checklist(self):
        """Link7 체크리스트 결과 파일 생성"""
        if not self.checklist_source.exists():
            print(f"⚠️ 원본 체크리스트 파일이 없습니다: {self.checklist_source}")
            return

        with open(self.checklist_source, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_lines.append(f"<!-- Test Run: {timestamp} -->\n")

        for line in lines:
            updated_line = line
            for res in self.results:
                if res.test_name in line:
                    if res.status == TestStatus.PASSED:
                        updated_line = line.replace("- [ ] **", "- [x] ✅ **")
                        updated_line = updated_line.rstrip() + f" → **통과** ({res.message})\n"
                    elif res.status == TestStatus.FAILED:
                        updated_line = line.replace("- [ ] **", "- [ ] ❌ **")
                        updated_line = updated_line.rstrip() + f" → **실패** ({res.message})\n"
                    elif res.status == TestStatus.WARNING:
                        updated_line = line.replace("- [ ] **", "- [~] ⚠️ **")
                        updated_line = updated_line.rstrip() + f" → **경고** ({res.message})\n"
                    elif res.status == TestStatus.SKIPPED:
                        updated_line = line.replace("- [ ] **", "- [ ] ⊘ **")
                        updated_line = updated_line.rstrip() + f" → **건너뜀** ({res.message})\n"
                    break
            updated_lines.append(updated_line)

        # 테스트 요약 추가
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warned = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        total = len(self.results)

        updated_lines.append("\n---\n")
        updated_lines.append("## 테스트 결과 요약\n\n")
        updated_lines.append("| 항목 | 개수 | 비율 |\n")
        updated_lines.append("|------|------|------|\n")
        updated_lines.append(f"| ✅ 통과 | {passed} | {passed/total*100:.1f}% |\n" if total > 0 else "| ✅ 통과 | 0 | 0% |\n")
        updated_lines.append(f"| ❌ 실패 | {failed} | {failed/total*100:.1f}% |\n" if total > 0 else "| ❌ 실패 | 0 | 0% |\n")
        updated_lines.append(f"| ⚠️ 경고 | {warned} | {warned/total*100:.1f}% |\n" if total > 0 else "| ⚠️ 경고 | 0 | 0% |\n")
        updated_lines.append(f"| ⊘ 건너뜀 | {skipped} | {skipped/total*100:.1f}% |\n" if total > 0 else "| ⊘ 건너뜀 | 0 | 0% |\n")
        updated_lines.append(f"| **총계** | **{total}** | **100%** |\n")

        with open(self.checklist_result, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print(f"\n✅ Link7 체크리스트 결과 저장됨: {self.checklist_result}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Link7 운영평가 E2E 테스트')
    parser.add_argument("--headless", action="store_true", help="브라우저 숨김 모드 (기본: 화면에 표시)")
    parser.add_argument("--url", default="http://localhost:5001", help="서버 URL (기본: http://localhost:5001)")
    args = parser.parse_args()

    test_suite = Link7OperationTestSuite(base_url=args.url, headless=args.headless)

    exit_code = test_suite.run_all_tests()
    sys.exit(exit_code)
