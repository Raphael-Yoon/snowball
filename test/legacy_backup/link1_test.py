"""
Link1 RCM 자동생성 통합 테스트 스크립트 (강화 버전)

Link1은 ITGC RCM 자동 생성 기능을 담당합니다.
- 클라우드/시스템/OS/DB 유형 선택
- Excel RCM 파일 자동 생성
- 이메일 발송 기능
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List
import io
from unittest.mock import patch, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
    from snowball_link1 import generate_and_send_rcm_excel
    import openpyxl
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

from test.link5_test import TestStatus, TestResult

class Link1TestSuite:
    """Link1 RCM 자동생성 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80)
        print("Link1 RCM 자동생성 통합 테스트 시작 (강화 버전)")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
            self.test_file_structure,
        ])

        self._run_category("2. 라우트 검증", [
            self.test_all_routes_defined,
        ])

        self._run_category("3. RCM 생성 기능 검증 (실행 기반)", [
            self.test_rcm_generation_logic,
            self.test_rcm_generation_with_invalid_data,
        ])

        self._run_category("4. 보안 및 유효성 검증", [
            self.test_email_validation_logic,
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
        if 'link1' not in self.app.blueprints:
            result.fail_test("link1 Blueprint가 등록되지 않았습니다.")
        else:
            result.pass_test("환경 설정이 올바릅니다.")

    def test_file_structure(self, result: TestResult):
        required_files = ['snowball_link1.py', 'static/RCM_Generate.xlsx']
        for f in required_files:
            if (project_root / f).exists():
                result.add_detail(f"✓ {f}")
            else:
                result.fail_test(f"{f} 파일이 없습니다.")
                return
        result.pass_test("필수 파일이 존재합니다.")

    def test_all_routes_defined(self, result: TestResult):
        routes = [rule.rule for rule in self.app.url_map.iter_rules()]
        # snowball.py에서 url_prefix 없이 등록됨
        if '/link1' in routes and '/rcm_generate' in routes:
            result.pass_test("주요 라우트가 등록되어 있습니다.")
        else:
            result.fail_test(f"일부 라우트가 누락되었습니다. (발견된 라우트: {routes})")

    @patch('snowball_link1.send_gmail_with_attachment')
    def test_rcm_generation_logic(self, result: TestResult, mock_send):
        """실제 RCM 생성 로직 테스트 (Mock 사용)"""
        # patch 데코레이터는 mock을 인자의 마지막(또는 지정된 위치)에 추가함. 
        # _run_category에서 test_func(result)로 호출하므로 (self, result, mock_send) 순서가 맞음.

        form_data = {
            'param1': 'test@example.com',
            'param2': 'TestSystem',
            'param_cloud': 'AWS',
            'param3': 'Web',
            'param4': 'Linux',
            'param5': 'MySQL',
            'use_os_tool': 'Y',
            'use_db_tool': 'N'
        }
        
        success, email, error = generate_and_send_rcm_excel(form_data)
        
        if success:
            result.add_detail("✓ 함수 실행 성공")
            if mock_send.called:
                result.add_detail("✓ 이메일 발송 함수 호출 확인")
                # 첨부파일 확인
                args, kwargs = mock_send.call_args
                file_stream = kwargs.get('file_stream')
                file_name = kwargs.get('file_name')
                
                if file_stream and file_name.startswith('TestSystem_ITGC_RCM_'):
                    result.add_detail(f"✓ 파일명 확인: {file_name}")
                    # 엑셀 내용 살짝 확인
                    wb = openpyxl.load_workbook(file_stream)
                    if 'RCM' in wb.sheetnames:
                        result.add_detail("✓ 엑셀 시트(RCM) 존재 확인")
                    else:
                        result.warn_test("RCM 시트를 찾을 수 없습니다.")
                else:
                    result.fail_test("생성된 파일 정보가 올바르지 않습니다.")
            else:
                result.fail_test("이메일 발송 함수가 호출되지 않았습니다.")
        else:
            result.fail_test(f"RCM 생성 실패: {error}")

    def test_rcm_generation_with_invalid_data(self, result: TestResult):
        """잘못된 데이터 입력 시 처리 테스트"""
        form_data = {
            'param1': '', # 이메일 누락
            'param2': 'Test'
        }
        success, email, error = generate_and_send_rcm_excel(form_data)
        if not success and "이메일 주소" in error:
            result.pass_test("이메일 누락 시 에러 처리가 정상입니다.")
        else:
            result.fail_test("이메일 누락 에러 처리가 미흡합니다.")

    def test_email_validation_logic(self, result: TestResult):
        """이메일 형식 검증 로직 확인 (코드 내 존재 여부)"""
        link1_path = project_root / 'snowball_link1.py'
        with open(link1_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'param1' in content and 'if not user_email' in content:
            result.pass_test("이메일 필수값 체크 로직이 확인되었습니다.")
        else:
            result.warn_test("이메일 검증 로직을 찾을 수 없습니다.")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            count = status_counts[status]
            print(f"{status.value} {status.name}: {count}개 ({count/total*100:.1f}%)")

        import json
        report_path = project_root / 'test' / f'link1_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
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
                os.remove(report_path)
                print(f"\nℹ️  임시 JSON 리포트가 삭제되었습니다: {report_path.name}")
            except Exception as e:
                print(f"\n⚠️  JSON 리포트 삭제 실패: {e}")

def main():
    suite = Link1TestSuite()
    suite.run_all_tests()

if __name__ == '__main__':
    main()

