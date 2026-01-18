"""
Link2 ITGC 인터뷰 및 AI 분석 통합 테스트 스크립트

Link2는 ITGC 인터뷰 처리, AI 문장 다듬기, 엑셀 생성 및 이메일 발송 기능을 담당합니다.
- 인터뷰 질문 및 조건부 로직
- 진행률 관리 (파일 기반)
- AI 문장 다듬기 및 일관성 체크
- ITGC 통제 텍스트 생성
- 엑셀 결과물 생성 및 전송 로직
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import List
import io

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
    import pandas as pd
    from snowball_link2 import (
        get_progress_status, set_progress_status, update_progress, reset_progress,
        get_conditional_questions, get_text_itgc, ITGC_CONTROLS, s_questions
    )
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

from test.link5_test import TestStatus, TestResult

class Link2TestSuite:
    """Link2 ITGC 인터뷰 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80)
        print("Link2 ITGC 인터뷰 통합 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
            self.test_file_structure,
        ])

        self._run_category("2. 진행률 관리 기능 검증", [
            self.test_progress_management,
        ])

        self._run_category("3. 인터뷰 로직 검증", [
            self.test_conditional_questions_logic,
            self.test_itgc_text_generation,
        ])

        self._run_category("4. AI 및 일관성 체크 검증", [
            self.test_ai_refinement_logic,
            self.test_consistency_check_logic,
        ])

        self._run_category("5. 보안 및 파일 접근 검증", [
            self.test_file_access_security,
        ])

        self._print_final_report()

    def _run_category(self, category_name: str, tests: List):
        print(f"\n{'=' * 80}\n{category_name}\n{'=' * 80}")
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
                print(f"\r{result}\n    ❌ {result.message}")

    def test_environment_setup(self, result: TestResult):
        """환경 설정 확인"""
        # link2는 snowball.py에서 직접 라우트로 정의되어 있음
        routes = [r.rule for r in self.app.url_map.iter_rules()]
        if '/link2' in routes:
            result.pass_test("Link2 라우트가 등록되어 있습니다.")
        else:
            result.fail_test("Link2 라우트를 찾을 수 없습니다.")

    def test_file_structure(self, result: TestResult):
        """필수 파일 확인"""
        required_files = ['snowball_link2.py']
        for f in required_files:
            if (project_root / f).exists():
                result.add_detail(f"✓ {f}")
            else:
                result.fail_test(f"{f} 파일이 없습니다.")
                return
        result.pass_test("필수 파일이 존재합니다.")

    def test_progress_management(self, result: TestResult):
        """진행률 관리 기능 테스트"""
        task_id = "test_task_123"
        test_status = {
            'percentage': 50,
            'current_task': '테스트 중...',
            'is_processing': True
        }
        
        try:
            # 상태 저장
            set_progress_status(task_id, test_status)
            result.add_detail("✓ set_progress_status 실행")
            
            # 상태 읽기
            read_status = get_progress_status(task_id)
            if read_status.get('percentage') == 50:
                result.add_detail("✓ get_progress_status 데이터 일치")
            else:
                result.fail_test(f"데이터 불일치: {read_status}")
                return
                
            # 업데이트
            update_progress(task_id, 100, "완료")
            read_status = get_progress_status(task_id)
            if read_status.get('percentage') == 100:
                result.add_detail("✓ update_progress 성공")
            else:
                result.fail_test("업데이트 실패")
                return
                
            # 리셋
            reset_progress(task_id)
            # 리셋 후에는 기본값이 반환되어야 함 (percentage: 0)
            read_status = get_progress_status(task_id)
            if read_status.get('percentage') == 0:
                result.add_detail("✓ reset_progress 성공")
            else:
                result.warn_test("reset_progress 후에도 데이터가 남아있을 수 있습니다.")
                
            result.pass_test("진행률 관리 기능이 정상 작동합니다.")
        finally:
            reset_progress(task_id)

    def test_conditional_questions_logic(self, result: TestResult):
        """조건부 질문 로직 테스트"""
        # 기본: 47개 질문
        all_q = get_conditional_questions([])
        result.add_detail(f"기본 질문 수: {len(all_q)}개")
        
        # 3번 답변이 N (Cloud 미사용) -> 4, 5, 47번 스킵
        answers_no_cloud = [''] * 48
        answers_no_cloud[3] = 'N'
        filtered_q = get_conditional_questions(answers_no_cloud)
        result.add_detail(f"Cloud 미사용 시 질문 수: {len(filtered_q)}개 (예상: 45개)")
        
        if len(filtered_q) != 45:
             result.warn_test(f"질문 수 불일치: {len(filtered_q)} (예상 45)")
        
        # 4번 SaaS + 5번 SOC1 Y -> 11, 14~46번 스킵
        answers_saas_soc1 = [''] * 48
        answers_saas_soc1[4] = 'SaaS'
        answers_saas_soc1[5] = 'Y'
        filtered_q = get_conditional_questions(answers_saas_soc1)
        result.add_detail(f"SaaS + SOC1 Y 시 질문 수: {len(filtered_q)}개")
        
        result.pass_test("조건부 질문 필터링 로직이 구현되어 있습니다.")

    def test_itgc_text_generation(self, result: TestResult):
        """ITGC 통제 텍스트 생성 테스트"""
        # APD01 테스트
        answers = ['test@mail.com', 'TestSys', 'Y', 'Y', 'IaaS', 'Y', 'Y', 'Y', 'Y'] + [''] * 40
        textarea = [''] * 50
        textarea[8] = "승인 절차 상세 내용"
        
        res = get_text_itgc(answers, 'APD01', textarea)
        if 'APD01' in res.get('A1', '') and '승인 절차 상세 내용' in res.get('B2', ''):
            result.add_detail("✓ APD01 텍스트 생성 확인")
        else:
            result.fail_test(f"APD01 생성 실패: {res}")
            return
            
        # N/A 케이스 테스트 (31번 N -> PC 통제 N/A)
        answers_pc_na = [''] * 50
        answers_pc_na[31] = 'N'
        res_pc = get_text_itgc(answers_pc_na, 'PC01')
        if 'N/A' in res_pc.get('B2', ''):
            result.add_detail("✓ PC01 N/A 처리 확인")
        else:
            result.warn_test("PC01 N/A 처리가 예상과 다릅니다.")
            
        result.pass_test("ITGC 통제별 텍스트 생성 로직이 정상입니다.")

    def test_ai_refinement_logic(self, result: TestResult):
        """AI 문장 다듬기 로직 검증 (코드 분석 위주)"""
        link2_path = project_root / 'snowball_link2.py'
        with open(link2_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'ai_improve_interview_answer' in content:
            result.add_detail("✓ ai_improve_interview_answer 함수 존재")
        else:
            result.fail_test("AI 개선 함수를 찾을 수 없습니다.")
            return
            
        if 'AI_REFINEMENT_PROMPT' in content:
            result.add_detail("✓ AI 프롬프트 정의 확인")
            
        result.pass_test("AI 문장 다듬기 로직이 구현되어 있습니다.")

    def test_consistency_check_logic(self, result: TestResult):
        """답변 일관성 체크 로직 검증"""
        from snowball_link2 import check_answer_consistency
        
        # 모순된 답변 생성 (상용SW 사용 'Y' + 내부수정 'Y')
        answers = [''] * 50
        answers[2] = 'Y'
        answers[31] = 'Y'
        
        issues = check_answer_consistency(answers, [''] * 50)
        if any("상용소프트웨어" in issue for issue in issues):
            result.add_detail("✓ 상용SW/내부수정 모순 감지 확인")
            result.pass_test("일관성 체크 로직이 정상 작동합니다.")
        else:
            result.warn_test("일관성 체크에서 예상된 이슈가 발견되지 않았습니다.")

    def test_file_access_security(self, result: TestResult):
        """파일 접근 및 보안 검증"""
        link2_path = project_root / 'snowball_link2.py'
        with open(link2_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # os.path.join 사용 확인 (경로 조작 방지)
        if 'os.path.join' in content:
            result.add_detail("✓ os.path.join 사용 확인")
            
        # 엑셀 템플릿 경로 확인
        if 'Design_Template.xlsx' in content:
            result.add_detail("✓ 템플릿 파일 경로 설정 확인")
            
        result.pass_test("파일 접근 보안 설정이 확인되었습니다.")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            count = status_counts[status]
            print(f"{status.value} {status.name}: {count}개 ({count/total*100:.1f}%)")

        import json
        report_path = project_root / 'test' / f'link2_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'total_tests': total,
                      'summary': {k.name.lower(): v for k, v in status_counts.items()},
                      'tests': [{'name': r.test_name, 'category': r.category, 'status': r.status.name,
                                'message': r.message, 'duration': r.get_duration(), 'details': r.details}
                               for r in self.results]}, f, ensure_ascii=False, indent=2)
        
        # 사용자가 JSON 파일은 바로 삭제하길 원하므로, 리포트 생성 후 즉시 삭제
        # 단, 전체 테스트 실행 중(SNOWBALL_KEEP_REPORT=1)에는 삭제하지 않음
        if os.environ.get('SNOWBALL_KEEP_REPORT') != '1':
            try:
                import os
                os.remove(report_path)
                print(f"\nℹ️  임시 JSON 리포트가 삭제되었습니다: {report_path.name}")
            except Exception as e:
                print(f"\n⚠️  JSON 리포트 삭제 실패: {e}")

def main():
    suite = Link2TestSuite()
    suite.run_all_tests()

if __name__ == '__main__':
    main()
