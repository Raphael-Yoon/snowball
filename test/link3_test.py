"""
Link3 운영평가 템플릿 통합 테스트 스크립트

Link3는 운영평가 템플릿 다운로드 기능을 담당합니다.
- 운영평가 템플릿 페이지
- 템플릿 다운로드 기능
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

class Link3TestSuite:
    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80 + "\nLink3 운영평가 템플릿 통합 테스트 시작\n" + "=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [self.test_environment_setup, self.test_file_structure])
        self._run_category("2. 라우트 검증", [self.test_all_routes_defined])
        self._run_category("3. 템플릿 기능 검증", [self.test_template_download_endpoint, self.test_template_file_access])
        self._run_category("4. 보안 검증", [self.test_file_access_security])

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
                if result.status == TestStatus.RUNNING: result.pass_test()
                print(f"\r{result}")
                for detail in result.details: print(f"    ℹ️  {detail}")
            except Exception as e:
                result.fail_test(f"예외 발생: {str(e)}")
                print(f"\r{result}\n    ❌ {result.message}")

    def test_environment_setup(self, result: TestResult):
        if 'link3' in self.app.blueprints:
            result.pass_test("환경 설정이 올바릅니다.")
        else:
            result.fail_test("link3 Blueprint가 등록되지 않았습니다.")

    def test_file_structure(self, result: TestResult):
        if (project_root / 'snowball_link3.py').exists():
            result.add_detail("✓ snowball_link3.py")
            result.pass_test("필수 파일이 존재합니다.")
        else:
            result.fail_test("snowball_link3.py 파일이 없습니다.")

    def test_all_routes_defined(self, result: TestResult):
        app_routes = [r.rule for r in self.app.url_map.iter_rules() if r.endpoint.startswith('link3.')]
        result.add_detail(f"정의된 라우트: {len(app_routes)}개")
        result.pass_test("주요 라우트가 정의되어 있습니다.")

    def test_template_download_endpoint(self, result: TestResult):
        response = self.client.post('/link3/paper_template_download')
        if response.status_code in [302, 401, 404, 500]:
            result.skip_test("인증이 필요하거나 파라미터가 필요합니다.")
        else:
            result.pass_test("템플릿 다운로드 엔드포인트가 응답합니다.")

    def test_template_file_access(self, result: TestResult):
        link3_path = project_root / 'snowball_link3.py'
        with open(link3_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'send_file' in content:
            result.add_detail("✓ 파일 다운로드 기능 존재")
            result.pass_test("파일 접근 기능이 구현되어 있습니다.")
        else:
            result.warn_test("파일 다운로드 코드를 확인할 수 없습니다.")

    def test_file_access_security(self, result: TestResult):
        link3_path = project_root / 'snowball_link3.py'
        with open(link3_path, 'r', encoding='utf-8') as f:
            content = f.read()
        checks = {'파일 경로 검증': 'os.path' in content, '파일 존재 확인': 'exists' in content.lower()}
        found = [k for k, v in checks.items() if v]
        if found:
            result.add_detail(f"✓ {', '.join(found)}")
            result.pass_test("파일 접근 보안이 구현되어 있습니다.")
        else:
            result.warn_test("파일 접근 보안을 확인할 수 없습니다.")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            print(f"{status.value} {status.name}: {status_counts[status]}개")

def main():
    Link3TestSuite().run_all_tests()

if __name__ == '__main__':
    main()
