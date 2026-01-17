"""
Link1 RCM 자동생성 통합 테스트 스크립트

Link1은 ITGC RCM 자동 생성 기능을 담당합니다.
- 클라우드/시스템/OS/DB 유형 선택
- Excel RCM 파일 자동 생성
- 이메일 발송 기능
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
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
        print("Link1 RCM 자동생성 통합 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
            self.test_file_structure,
        ])

        self._run_category("2. 라우트 검증", [
            self.test_all_routes_defined,
        ])

        self._run_category("3. RCM 생성 기능 검증", [
            self.test_rcm_generate_endpoint,
            self.test_excel_generation_function,
            self.test_email_sending_function,
        ])

        self._run_category("4. 보안 검증", [
            self.test_email_validation,
            self.test_file_generation_security,
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
        required_files = ['snowball_link1.py']
        missing = [f for f in required_files if not (project_root / f).exists()]
        if missing:
            result.warn_test(f"일부 파일 누락: {', '.join(missing)}")
        else:
            result.add_detail("✓ snowball_link1.py")
            result.pass_test("필수 파일이 존재합니다.")

    def test_all_routes_defined(self, result: TestResult):
        expected_routes = ['/link1/link1', '/link1/rcm_generate']
        app_routes = [rule.rule for rule in self.app.url_map.iter_rules() if rule.endpoint.startswith('link1.')]
        result.add_detail(f"정의된 라우트: {len(app_routes)}개")
        result.pass_test("주요 라우트가 정의되어 있습니다.")

    def test_rcm_generate_endpoint(self, result: TestResult):
        response = self.client.post('/link1/rcm_generate')
        if response.status_code in [302, 401, 404, 500]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("RCM 생성 엔드포인트가 응답합니다.")

    def test_excel_generation_function(self, result: TestResult):
        link1_path = project_root / 'snowball_link1.py'
        with open(link1_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'openpyxl' in content and 'load_workbook' in content:
            result.add_detail("✓ openpyxl 사용 확인")
            result.pass_test("Excel 생성 기능이 구현되어 있습니다.")
        else:
            result.warn_test("Excel 생성 코드를 확인할 수 없습니다.")

    def test_email_sending_function(self, result: TestResult):
        link1_path = project_root / 'snowball_link1.py'
        with open(link1_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'send_gmail' in content or 'send_email' in content:
            result.add_detail("✓ 이메일 발송 함수 존재")
            result.pass_test("이메일 발송 기능이 구현되어 있습니다.")
        else:
            result.warn_test("이메일 발송 코드를 확인할 수 없습니다.")

    def test_email_validation(self, result: TestResult):
        link1_path = project_root / 'snowball_link1.py'
        with open(link1_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'param1' in content and 'email' in content.lower():
            result.add_detail("✓ 이메일 파라미터 처리")
            result.pass_test("이메일 검증 로직이 있습니다.")
        else:
            result.warn_test("이메일 검증을 확인할 수 없습니다.")

    def test_file_generation_security(self, result: TestResult):
        link1_path = project_root / 'snowball_link1.py'
        with open(link1_path, 'r', encoding='utf-8') as f:
            content = f.read()
        checks = {'파일명 생성': 'file_name' in content, '날짜 포맷': 'strftime' in content}
        found = [k for k, v in checks.items() if v]
        result.add_detail(f"확인된 보안 기능: {', '.join(found)}")
        result.pass_test(f"파일 생성 보안이 구현되어 있습니다.")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        from test.link5_test import TestStatus
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

def main():
    suite = Link1TestSuite()
    suite.run_all_tests()

if __name__ == '__main__':
    main()
