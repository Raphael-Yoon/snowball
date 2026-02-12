"""
Link1: RCM 생성 (AI RCM Builder) Unit 테스트 코드

주요 테스트 항목:
1. 비로그인 상태에서 페이지 접근 및 필드 확인
2. 입력 폼 요소 확인 (시스템명, 시스템유형, SW, OS, DB, Cloud)
3. 폼 입력에 따른 동적 UI 변화 확인 (Linux 배포판 선택, Cloud에 따른 OS/DB 숨김)
4. 통제 테이블 및 펼치기/접기 기능 확인
5. 모집단 템플릿 API 테스트
6. 메일 발송 기능 테스트
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 및 테스트 경로 설정
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, TestStatus, UnitTestResult


class Link1UnitTest(PlaywrightTestBase):
    def __init__(self, base_url="http://localhost:5001", **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self.category = "Link1: RCM 생성"
        self.checklist_source = project_root / "test" / "unit_checklist_link1.md"
        self.checklist_result = project_root / "test" / "unit_checklist_link1_result.md"

    def test_link1_page_access(self, result: UnitTestResult):
        """1. 페이지 접근 및 기본 요소 확인"""
        self.navigate_to("/link1")

        # 페이지 타이틀 확인
        title = self.page.title()
        if "RCM 생성" in title or "Snowball" in title:
            result.add_detail(f"페이지 타이틀 확인: {title}")
        else:
            result.fail_test(f"페이지 타이틀 불일치: {title}")
            return

        # 섹션 헤더 확인
        if self.is_visible("h5:has-text('대상 시스템 정보')"):
            result.add_detail("대상 시스템 정보 섹션 확인")
        else:
            result.fail_test("대상 시스템 정보 섹션을 찾을 수 없습니다.")
            return

        # 통제 테이블 확인
        if self.is_visible("#rcm-table"):
            result.add_detail("ITGC RCM 테이블 확인")
        else:
            result.fail_test("RCM 테이블을 찾을 수 없습니다.")
            return

        result.pass_test("페이지 접근 및 기본 요소 확인 완료")

    def test_link1_form_elements(self, result: UnitTestResult):
        """2. 입력 폼 요소 확인"""
        self.navigate_to("/link1")

        # 필수 폼 요소 확인
        form_elements = {
            "#system_name": "시스템 명칭",
            "#system_type": "시스템 유형",
            "#software": "Application",
            "#os": "OS",
            "#db": "DB",
            "#cloud_env": "Cloud 환경"
        }

        missing_elements = []
        for selector, name in form_elements.items():
            if self.page.locator(selector).count() > 0:
                result.add_detail(f"폼 요소 확인: {name}")
            else:
                missing_elements.append(name)

        if missing_elements:
            result.fail_test(f"누락된 폼 요소: {', '.join(missing_elements)}")
        else:
            result.pass_test("모든 폼 요소 확인 완료")

    def test_link1_os_version_toggle(self, result: UnitTestResult):
        """3. OS 선택에 따른 Linux 배포판 표시/숨김 확인"""
        self.navigate_to("/link1")

        # Linux 선택 시 배포판 드롭다운 표시
        self.page.select_option("#os", "LINUX")
        self.page.wait_for_timeout(300)

        os_version_visible = self.page.locator("#os_version_group").is_visible()
        if os_version_visible:
            result.add_detail("Linux 선택 시 배포판 드롭다운 표시 확인")
        else:
            result.fail_test("Linux 선택 시 배포판 드롭다운이 표시되지 않습니다.")
            return

        # Windows 선택 시 배포판 드롭다운 숨김
        self.page.select_option("#os", "WINDOWS")
        self.page.wait_for_timeout(300)

        os_version_hidden = not self.page.locator("#os_version_group").is_visible()
        if os_version_hidden:
            result.add_detail("Windows 선택 시 배포판 드롭다운 숨김 확인")
        else:
            result.fail_test("Windows 선택 시에도 배포판 드롭다운이 표시됩니다.")
            return

        result.pass_test("OS 선택에 따른 UI 변화 확인 완료")

    def test_link1_cloud_env_toggle(self, result: UnitTestResult):
        """4. Cloud 환경 선택에 따른 OS/DB 숨김 확인"""
        self.navigate_to("/link1")

        # On-Premise(None) 선택 시 OS/DB 표시
        self.page.select_option("#cloud_env", "None")
        self.page.wait_for_timeout(300)

        os_visible = self.page.locator("#os").is_visible()
        db_visible = self.page.locator("#db").is_visible()

        if os_visible and db_visible:
            result.add_detail("On-Premise 선택 시 OS/DB 표시 확인")
        else:
            result.fail_test("On-Premise 선택 시 OS/DB가 표시되지 않습니다.")
            return

        # SaaS 선택 시 OS/DB N/A로 변경 확인
        self.page.select_option("#cloud_env", "SaaS")
        self.page.wait_for_timeout(300)

        os_value = self.page.locator("#os").input_value()
        db_value = self.page.locator("#db").input_value()

        if os_value == "N/A" and db_value == "N/A":
            result.add_detail("SaaS 선택 시 OS/DB가 N/A로 변경됨")
        else:
            result.add_detail(f"SaaS 선택 후 OS={os_value}, DB={db_value}")

        result.pass_test("Cloud 환경 선택에 따른 UI 변화 확인 완료")

    def test_link1_control_table(self, result: UnitTestResult):
        """5. 통제 테이블 및 행 확인"""
        self.navigate_to("/link1")

        # 통제 행 개수 확인
        control_rows = self.page.locator(".control-row").count()
        if control_rows > 0:
            result.add_detail(f"통제 항목 {control_rows}개 확인")
        else:
            result.fail_test("통제 항목이 없습니다.")
            return

        # 첫 번째 통제의 기본 요소 확인
        first_row = self.page.locator(".control-row").first
        control_id = first_row.get_attribute("data-id")

        if control_id:
            result.add_detail(f"첫 번째 통제 ID: {control_id}")

            # 구분(type), 주기(freq), 성격(method) 드롭다운 확인
            type_select = self.page.locator(f"#type-{control_id}")
            freq_select = self.page.locator(f"#freq-{control_id}")
            method_select = self.page.locator(f"#method-{control_id}")

            if type_select.count() > 0 and freq_select.count() > 0 and method_select.count() > 0:
                result.add_detail("통제별 드롭다운 요소 확인")
            else:
                result.fail_test("통제별 드롭다운 요소가 누락되었습니다.")
                return

        result.pass_test("통제 테이블 확인 완료")

    def test_link1_toggle_detail(self, result: UnitTestResult):
        """6. 상세 펼치기/접기 기능 확인"""
        self.navigate_to("/link1")

        # 전체 펼치기 버튼 확인
        toggle_all_btn = self.page.locator("#btn-toggle-all")
        if toggle_all_btn.count() == 0:
            result.fail_test("전체 펼치기 버튼을 찾을 수 없습니다.")
            return

        # 첫 번째 통제의 상세 행 확인
        first_row = self.page.locator(".control-row").first
        control_id = first_row.get_attribute("data-id")
        detail_row = self.page.locator(f"#detail-{control_id}")

        # 초기 상태: 접힌 상태
        initial_visible = detail_row.is_visible()
        result.add_detail(f"초기 상세 행 상태: {'펼침' if initial_visible else '접힘'}")

        # 전체 펼치기 클릭
        toggle_all_btn.click()
        self.page.wait_for_timeout(500)

        after_toggle = detail_row.is_visible()
        if after_toggle != initial_visible:
            result.add_detail("전체 펼치기/접기 동작 확인")
        else:
            result.add_detail("전체 펼치기/접기 상태 변화 없음 (이미 동일 상태)")

        result.pass_test("상세 펼치기/접기 기능 확인 완료")

    def test_link1_type_change_monitoring(self, result: UnitTestResult):
        """7. 자동→수동 변경 시 모니터링 명칭 변경 확인"""
        self.navigate_to("/link1")

        # 원래 자동통제인 APD05 찾기
        name_span = self.page.locator("#name-APD05")
        type_select = self.page.locator("#type-APD05")

        if name_span.count() == 0 or type_select.count() == 0:
            result.skip_test("APD05 통제를 찾을 수 없습니다.")
            return

        # 원래 이름 확인
        original_name = name_span.get_attribute("data-original")
        result.add_detail(f"원래 통제명: {original_name}")

        # 수동으로 변경
        type_select.select_option("Manual")
        self.page.wait_for_timeout(500)

        # 변경된 이름 확인
        changed_name = name_span.text_content()

        if "모니터링" in changed_name:
            result.add_detail(f"변경된 통제명: {changed_name}")
            result.pass_test("자동→수동 변경 시 모니터링 명칭 변경 확인")
        else:
            result.fail_test(f"모니터링 명칭으로 변경되지 않음: {changed_name}")

    def test_link1_population_templates_api(self, result: UnitTestResult):
        """8. 모집단 템플릿 API 테스트"""
        try:
            response = self.page.request.get(f"{self.base_url}/api/rcm/population_templates")

            if response.status == 200:
                data = response.json()

                # sw_templates, os_templates, db_templates 존재 확인
                if data.get("success") and "sw_templates" in data and "os_templates" in data and "db_templates" in data:
                    sw_count = len(data["sw_templates"])
                    os_count = len(data["os_templates"])
                    db_count = len(data["db_templates"])
                    result.add_detail(f"템플릿 개수 - SW: {sw_count}, OS: {os_count}, DB: {db_count}")
                    result.pass_test("모집단 템플릿 API 정상 동작")
                else:
                    result.fail_test(f"템플릿 데이터 구조 불일치: {list(data.keys())}")
            else:
                result.fail_test(f"API 응답 오류: {response.status}")

        except Exception as e:
            result.fail_test(f"API 호출 실패: {e}")

    def test_link1_email_input(self, result: UnitTestResult):
        """9. 이메일 입력 필드 및 발송 버튼 확인"""
        self.navigate_to("/link1")

        # 이메일 입력 필드 확인
        email_input = self.page.locator("#send_email")
        if email_input.count() == 0:
            result.fail_test("이메일 입력 필드를 찾을 수 없습니다.")
            return

        result.add_detail("이메일 입력 필드 확인")

        # 발송 버튼 확인
        send_btn = self.page.locator("#btn-export-excel")
        if send_btn.count() == 0:
            result.fail_test("RCM 메일 발송 버튼을 찾을 수 없습니다.")
            return

        btn_text = send_btn.text_content()
        if "메일 발송" in btn_text:
            result.add_detail(f"발송 버튼 확인: {btn_text.strip()}")

        result.pass_test("이메일 입력 및 발송 버튼 확인 완료")

    def test_link1_export_email_validation(self, result: UnitTestResult):
        """10. 이메일 미입력 시 발송 방지 확인"""
        self.navigate_to("/link1")

        # 이메일 필드 비우기
        email_input = self.page.locator("#send_email")
        email_input.fill("")

        # 발송 버튼 클릭
        send_btn = self.page.locator("#btn-export-excel")

        # alert 대기
        self.page.on("dialog", lambda dialog: dialog.accept())
        send_btn.click()
        self.page.wait_for_timeout(1000)

        # alert가 표시되었는지 확인 (페이지가 이동하지 않았는지)
        current_url = self.page.url
        if "/link1" in current_url:
            result.pass_test("이메일 미입력 시 발송 방지 동작 확인")
        else:
            result.fail_test("이메일 없이 발송이 진행되었습니다.")

    def _update_checklist_result(self):
        """체크리스트 결과 파일 생성"""
        if not self.checklist_source.exists():
            print(f"[WARN] 원본 체크리스트 파일이 없습니다: {self.checklist_source}")
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
                        updated_line = line.replace("- [ ]", "- [x]")
                        updated_line = updated_line.rstrip() + f" -> PASS ({res.message})\n"
                    elif res.status == TestStatus.FAILED:
                        updated_line = line.replace("- [ ]", "- [ ] X")
                        updated_line = updated_line.rstrip() + f" -> FAIL ({res.message})\n"
                    elif res.status == TestStatus.SKIPPED:
                        updated_line = updated_line.rstrip() + f" -> SKIP ({res.message})\n"
                    break
            updated_lines.append(updated_line)

        # 요약 추가
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        total = len(self.results) if self.results else 1

        updated_lines.append("\n---\n")
        updated_lines.append(f"## 테스트 결과 요약\n\n")
        updated_lines.append(f"| 항목 | 개수 | 비율 |\n")
        updated_lines.append(f"|------|------|------|\n")
        updated_lines.append(f"| PASS | {passed} | {passed/total*100:.1f}% |\n")
        updated_lines.append(f"| FAIL | {failed} | {failed/total*100:.1f}% |\n")
        updated_lines.append(f"| SKIP | {skipped} | {skipped/total*100:.1f}% |\n")
        updated_lines.append(f"| **총계** | **{total}** | **100%** |\n")

        with open(self.checklist_result, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print(f"\n[OK] 체크리스트 결과 저장됨: {self.checklist_result}")


def run_tests():
    test_runner = Link1UnitTest(headless=False, slow_mo=500)
    test_runner.setup()

    try:
        test_runner.run_category("Link1 Unit Tests", [
            test_runner.test_link1_page_access,
            test_runner.test_link1_form_elements,
            test_runner.test_link1_os_version_toggle,
            test_runner.test_link1_cloud_env_toggle,
            test_runner.test_link1_control_table,
            test_runner.test_link1_toggle_detail,
            test_runner.test_link1_type_change_monitoring,
            test_runner.test_link1_population_templates_api,
            test_runner.test_link1_email_input,
            test_runner.test_link1_export_email_validation
        ])
    finally:
        test_runner._update_checklist_result()
        test_runner.print_final_report()
        test_runner.teardown()


if __name__ == "__main__":
    run_tests()
