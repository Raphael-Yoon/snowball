"""
Link2: 인터뷰/설계평가 E2E 테스트 코드

주요 테스트 항목:
1. 비로그인/로그인 상태별 초기 접근 확인
2. 인터뷰 진행 핵심 UI 요소 확인 (진행률, 입력 타입)
3. 조건부 질문 건너뛰기 로직 확인
4. 관리자 전용 샘플 입력 기능 확인
5. 인터뷰 완료 프로세스 확인
"""

import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 및 테스트 경로 설정
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, TestStatus, E2ETestResult

class Link2E2ETest(PlaywrightTestBase):
    def __init__(self, base_url="http://localhost:5001", **kwargs):
        super().__init__(base_url=base_url, **kwargs)
        self.category = "Link2: 인터뷰/설계평가"
        self.checklist_source = project_root / "test" / "e2e_checklist_link2.md"
        self.checklist_result = project_root / "test" / "e2e_checklist_link2_result.md"

    def _do_admin_login(self):
        """관리자 로그인 (이미 로그인된 상태면 건너뜀)"""
        self.page.goto(f"{self.base_url}/login")
        self.page.wait_for_load_state("networkidle")

        if self.page.locator("a:has-text('로그아웃')").count() > 0:
            return

        admin_btn = self.page.locator(".admin-login-section button[type='submit']")
        if admin_btn.count() > 0:
            admin_btn.click()
            self.page.wait_for_load_state("networkidle")
            return
        
    def _do_logout(self):
        """로그아웃 수행"""
        self.page.goto(f"{self.base_url}/logout")
        self.page.wait_for_load_state("networkidle")

    def test_link2_access_guest(self, result: E2ETestResult):
        """1-1. 비로그인 상태에서 페이지 접근 및 첫 질문 확인"""
        self._do_logout()
        self.navigate_to("/link2")
        
        # 타이틀 확인 - link2.jsp의 h1.section-title은 카테고리명을 표시 (예: "공통사항")
        # 실제 <title> 태그는 "Snowball - 인터뷰/설계평가"
        if "공통사항" in self.get_text("h1.section-title"):
            result.add_detail("페이지 로드 확인 (카테고리: 공통사항)")
        elif "Snowball" in self.page.title():
            result.add_detail("페이지 타이틀 확인 완료")
        else:
            result.fail_test("페이지 로드 실패 또는 타이틀 불일치")
            return

        # 첫 번째 질문(이메일) 및 입력 필드 확인
        question_text = self.get_text(".card-text")
        if "e-Mail 주소" in question_text:
            result.add_detail("첫 번째 질문(이메일) 확인 완료")
        else:
            result.fail_test(f"첫 번째 질문 텍스트 다름: {question_text}")
            return

        email_input = self.page.locator("input[name='a0']")
        if email_input.count() > 0:
            result.pass_test("비로그인 상태 이메일 필드 활성화 확인")
        else:
            result.fail_test("이메일 입력 필드(a0)를 찾을 수 없습니다.")

    def test_link2_access_logged_in(self, result: E2ETestResult):
        """1-2. 로그인 상태에서 페이지 접근 및 이메일 자동 입력 확인"""
        # snowball_link2.py:55 -> 로그인 시 question_index=1 (두 번째 질문)부터 시작함
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # 질문 번호 확인
        q_title = self.get_text(".card-title")
        if "질문 2" in q_title:
            result.add_detail("로그인 시 질문 2(시스템명)로 자동 이동 확인")
            
            # 이전 버튼 눌러서 질문 1(이메일) 확인 시도
            self.page.click("a:has-text('이전')")
            self.page.wait_for_load_state("networkidle")
            
            email_input = self.page.locator("input[name='a0']")
            email_val = email_input.get_attribute("value")
            is_readonly = email_input.get_attribute("readonly") is not None
            
            if email_val == "snowball2727@naver.com" and is_readonly:
                result.pass_test("질문 1의 이메일 자동 입력 및 Readonly 확인 완료")
            else:
                result.fail_test(f"이메일 값 또는 속성 오류 (값: {email_val}, Readonly: {is_readonly})")
        else:
            result.fail_test(f"로그인 후 기대한 질문(2)이 아님: {q_title}")

    def test_link2_activity_log(self, result: E2ETestResult):
        result.skip_test("활동로그 검증 준비 중 (DB 접근 필요)")

    def test_link2_progress_bar(self, result: E2ETestResult):
        """2-1. 진행률 바 표시 확인"""
        self.navigate_to("/link2")
        progress_bar = self.page.locator(".progress-bar")
        if progress_bar.count() > 0:
            width_style = progress_bar.get_attribute("style")
            result.pass_test(f"진행률 바 확인 완료 (Style: {width_style})")
        else:
            result.fail_test("진행률 바를 찾을 수 없습니다.")

    def test_link2_navigation(self, result: E2ETestResult):
        """2-2. 질문 네비게이션 확인 (다음/이전)"""
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # 첫 질문(이메일)은 이미 채워져 있으므로 '다음' 클릭
        self.page.click("#submitBtn")
        self.page.wait_for_load_state("networkidle")
        
        if "질문 2" in self.get_text(".card-title"):
            result.add_detail("다음 질문 이동 확인")
        else:
            result.fail_test("다음 질문으로 이동하지 않았습니다.")
            return

        # '이전' 클릭
        self.page.click("a:has-text('이전')")
        self.page.wait_for_load_state("networkidle")
        
        if "질문 1" in self.get_text(".card-title"):
            result.pass_test("이전 질문으로 돌아오기 확인")
        else:
            result.fail_test("이전 질문으로 돌아오지 않았습니다.")

    def test_link2_input_types(self, result: E2ETestResult):
        """2-3. 다양한 입력 타입 렌더링 확인"""
        self.navigate_to("/link2")
        # 질문 1: Text
        if self.page.locator("input[type='text']").count() > 0:
            result.add_detail("Text 타입 렌더링 확인")
        
        # 질문 3으로 이동하여 Radio 확인 (샘플 입력을 이용해 빠르게 이동)
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        self.page.click("button:has-text('샘플입력')") # Q1 채우고 Q2로
        self.page.wait_for_timeout(500)
        self.page.click("button:has-text('샘플입력')") # Q2 채우고 Q3으로
        self.page.wait_for_timeout(500)
        
        if self.page.locator("input[type='radio']").count() > 0:
            result.pass_test("Radio 타입 렌더링 확인 완료")
        else:
            result.fail_test("Radio 타입 입력 요소를 찾을 수 없습니다.")

    def test_link2_conditional_skip_cloud(self, result: E2ETestResult):
        """3-1. Cloud 미사용 선택 시 관련 질문 건너뛰기"""
        self._do_logout() # 세션 초기화
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # Q2: 시스템명 입력
        if "질문 2" in self.get_text(".card-title"):
             self.fill_input("input[name='a1']", f"SKIP_CLOUD_{datetime.now().strftime('%H%M%S')}")
             self.page.click("#submitBtn")
             self.page.wait_for_load_state("networkidle")
            
        # Q3: 상용소프트웨어 여부
        if "질문 3" in self.get_text(".card-title"):
             self.page.check("input[name='a2'][value='Y']")
             self.fill_input("input[name='a2_1']", "SAP")
             self.page.click("#submitBtn")
             self.page.wait_for_load_state("networkidle")

        # Q4: Cloud 사용 여부 -> '아니오' 선택
        if "질문 4" in self.get_text(".card-title"):
             self.page.check("input[name='a3'][value='N']")
             self.page.click("#submitBtn")
             self.page.wait_for_load_state("networkidle")
             
             # Q5, Q6을 건너뛰고 Q7로 가야 함
             q_info = self.get_text(".card-title")
             q_text = self.get_text(".card-text")
             
             if "사용자 권한부여" in q_text:
                 result.pass_test(f"Cloud 질문 스킵 확인 완료 (도착: {q_info})")
             else:
                 result.fail_test(f"스킵 실패: {q_info} - {q_text}")
        else:
             result.fail_test(f"질문 4(Cloud)에 도달하지 못함: {self.get_text('.card-title')}")

    def test_link2_conditional_skip_db(self, result: E2ETestResult):
        """3-2. DB 접속 불가 선택 시 관련 질문(Q19~Q24) 건너뛰기"""
        self._do_logout()
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # 질문 18(인덱스 17)에 도달할 때까지 이동
        for _ in range(30):
            q_info = self.get_text(".card-title")
            q_text = self.get_text(".card-text")
            
            if "질문 18" in q_info:
                break
            if "질문 48" in q_info:
                result.fail_test(f"질문 18을 찾기 전에 끝에 도달함: {q_info}")
                return

            # SaaS + SOC1=Y가 되면 14~46번이 통째로 스킵되므로, 
            # 질문 5(Cloud 종류)에서 IaaS를 강제로 선택하여 스킵 방지
            if "질문 5" in q_info:
                self.page.check("input[name='a4'][value='IaaS']")
                self.page.click("#submitBtn")
            # 질문 15(DB 작업 가능 여부)에서는 '예'를 선택해야 DB 상세 질문이 나옴
            elif "질문 15" in q_info or "DB에 접속하여 필요한 작업을 수행하는 것이 가능" in q_text:
                self.page.check("input[name='a14'][value='Y']")
                self.page.click("#submitBtn")
            else:
                self.page.click("button:has-text('샘플입력')")
            
            self.page.wait_for_timeout(300)
            
        # 질문 18에 도달했는지 확인 (인덱스 17: 데이터 변경 권한/절차 관련)
        # snowball_link2.py:457 -> Index 17(Q18)은 "DB에 접속하여 필요한 작업 수행 가능?"
        if "DB에 접속하여" in self.get_text(".card-text"):
            result.add_detail("질문 18(DB 접속 여부) 도달 확인")
            self.page.check("input[name='a17'][value='N']")
            self.page.click("#submitBtn")
            self.page.wait_for_load_state("networkidle")
            
            # DB 질문들을 건너뛰고 OS 접속 여부(질문 25)로 가야 함
            q_text = self.get_text(".card-text")
            if "OS서버에 접속하여" in q_text:
                result.pass_test(f"DB 관련 질문 스킵 확인 완료 (도착: {self.get_text('.card-title')})")
            else:
                result.fail_test(f"스킵 실패: {self.get_text('.card-title')} - {q_text}")
        else:
            result.fail_test(f"질문 18에 도달하지 못함: {self.get_text('.card-title')}")

    def test_link2_conditional_skip_os(self, result: E2ETestResult):
        """3-3. OS 접속 불가 선택 시 관련 질문(Q26~Q31) 건너뛰기"""
        self._do_logout()
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # 질문 25(인덱스 24)까지 이동
        for _ in range(40):
            q_info = self.get_text(".card-title")
            q_text = self.get_text(".card-text")
            
            if "질문 25" in q_info:
                break
            if "질문 48" in q_info:
                result.fail_test(f"질문 25를 찾기 전에 끝에 도달함: {q_info}")
                return

            # SaaS 스킵 방지
            if "질문 5" in q_info:
                self.page.check("input[name='a4'][value='IaaS']")
                self.page.click("#submitBtn")
            # 질문 18(DB 접속)에서는 '예'로 응답해야 나머지 질문이 보임
            elif "질문 18" in q_info:
                self.page.check("input[name='a17'][value='Y']")
                self.page.click("#submitBtn")
            # 질문 25에 도달하기 위해 필요한 답변들
            elif "OS서버에 접속하여" in q_text and "질문 25" not in q_info:
                 # 혹시 이전 루프에서 걸렸을 경우를 대비
                 break
            else:
                self.page.click("button:has-text('샘플입력')")
            self.page.wait_for_timeout(300)

        # 질문 25에 도달했는지 확인
        if "OS서버에 접속하여" in self.get_text(".card-text"):
            result.add_detail("질문 25(OS 접속 여부) 도달 확인")
            self.page.check("input[name='a24'][value='N']")
            self.page.click("#submitBtn")
            self.page.wait_for_load_state("networkidle")
            
            # PC 질문(질문 32)으로 가야 함
            q_text = self.get_text(".card-text")
            if "내부에서 수정" in q_text:
                result.pass_test(f"OS 관련 질문 스킵 확인 완료 (도착: {self.get_text('.card-title')})")
            else:
                result.fail_test(f"스킵 실패: {self.get_text('.card-title')} - {q_text}")
        else:
            result.fail_test(f"질문 25에 도달하지 못함: {self.get_text('.card-title')}")

    def test_link2_admin_sample_buttons(self, result: E2ETestResult):
        """4. 관리자 샘플 버튼 표시 확인"""
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        sample_btn = self.page.locator("button:has-text('샘플입력')")
        skip_btn = self.page.locator("button:has-text('스킵샘플')")
        
        if sample_btn.count() > 0 and skip_btn.count() > 0:
            result.pass_test("관리자 샘플 입력 버튼 노출 확인")
        else:
            result.fail_test("관리자 버튼이 보이지 않습니다.")

    def test_link2_sample_fill_click(self, result: E2ETestResult):
        """4-1. 샘플입력 버튼 기능 확인"""
        self._do_logout() # 이전 테스트의 상태(Q7 등)가 남아있을 수 있으므로 로그아웃 후 다시 로그인
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # 로그인 시 Q2(시스템명)부터 시작함
        q_title = self.get_text(".card-title")
        if "질문 2" in q_title:
            self.page.click("button:has-text('샘플입력')")
            self.page.wait_for_timeout(1000) # 버튼 내부의 setTimeout(100) 대응
            
            # Q3으로 가야 함
            new_q_title = self.get_text(".card-title")
            if "질문 3" in new_q_title:
                result.pass_test("샘플입력 버튼 클릭 후 자동 입력 및 이동 확인 (Q2 -> Q3)")
            else:
                result.fail_test(f"샘플입력 후 Q3으로 이동하지 않았습니다: {new_q_title}")
        else:
            result.fail_test(f"기대한 질문(2)이 아님: {q_title}")

    def test_link2_interview_completion(self, result: E2ETestResult):
        """5. 인터뷰 완료 프로세스 (스킵 샘플 이용)"""
        self._do_admin_login()
        self.navigate_to("/link2?reset=1")
        
        # 스킵 샘플 버튼을 반복 클릭하여 끝까지 이동 (또는 JS로 직접 처리)
        # 여기서는 스킵 샘플의 특성을 이용해 빠르게 끝내는 테스트를 구상
        result.add_detail("스킵 샘플을 통한 빠른 완료 시도")
        
        # JS로 빠르게 모든 질문 채우기는 복잡하므로, 버튼 클릭 시뮬레이션
        # 47번 질문까지 가야 하므로 시간이 걸릴 수 있음
        result.skip_test("전체 완료 테스트는 런타임이 너무 길어질 수 있어 skip (수동 확인 권장)")

    def test_link2_data_persistence(self, result: E2ETestResult):
         result.skip_test("데이터 영속성 테스트 준비 중")

    def _update_checklist_result(self):
        """체크리스트 결과 파일 생성"""
        if not self.checklist_source.exists():
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
                        updated_line = line.replace("- [ ]", "- [x] ✅")
                        updated_line = updated_line.rstrip() + f" → **통과** ({res.message})\n"
                    elif res.status == TestStatus.FAILED:
                        updated_line = line.replace("- [ ]", "- [ ] ❌")
                        updated_line = updated_line.rstrip() + f" → **실패** ({res.message})\n"
                    elif res.status == TestStatus.WARNING:
                        updated_line = line.replace("- [ ]", "- [~] ⚠️")
                        updated_line = updated_line.rstrip() + f" → **경고** ({res.message})\n"
                    elif res.status == TestStatus.SKIPPED:
                        updated_line = line.replace("- [ ]", "- [ ] ⊘")
                        updated_line = updated_line.rstrip() + f" → **건너뜀** ({res.message})\n"
                    break
            updated_lines.append(updated_line)

        # 요약 추가
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warned = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        total = len(self.results) if self.results else 1

        updated_lines.append("\n---\n")
        updated_lines.append(f"## 테스트 결과 요약\n\n")
        updated_lines.append(f"| 항목 | 개수 | 비율 |\n")
        updated_lines.append(f"|------|------|------|\n")
        updated_lines.append(f"| ✅ 통과 | {passed} | {passed/total*100:.1f}% |\n")
        updated_lines.append(f"| ❌ 실패 | {failed} | {failed/total*100:.1f}% |\n")
        updated_lines.append(f"| ⚠️ 경고 | {warned} | {warned/total*100:.1f}% |\n")
        updated_lines.append(f"| ⊘ 건너뜀 | {skipped} | {skipped/total*100:.1f}% |\n")
        updated_lines.append(f"| **총계** | **{total}** | **100%** |\n")

        with open(self.checklist_result, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

def run_tests():
    test_runner = Link2E2ETest(headless=False, slow_mo=100)
    test_runner.setup()
    
    try:
        test_runner.run_category("Link2 E2E Tests", [
            test_runner.test_link2_access_guest,
            test_runner.test_link2_access_logged_in,
            test_runner.test_link2_activity_log,
            test_runner.test_link2_progress_bar,
            test_runner.test_link2_navigation,
            test_runner.test_link2_input_types,
            test_runner.test_link2_conditional_skip_cloud,
            test_runner.test_link2_conditional_skip_db,
            test_runner.test_link2_conditional_skip_os,
            test_runner.test_link2_admin_sample_buttons,
            test_runner.test_link2_sample_fill_click,
            test_runner.test_link2_interview_completion,
            test_runner.test_link2_data_persistence
        ])
    finally:
        test_runner._update_checklist_result()
        test_runner.print_final_report()
        test_runner.teardown()

if __name__ == "__main__":
    run_tests()
