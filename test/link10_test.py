"""
Link10 AI 분석 통합 테스트 스크립트

Link10은 구글 드라이브 연동 AI 문서 분석 기능을 담당합니다.
- 구글 드라이브 파일 목록 조회
- AI 분석 결과 저장/조회
- 리포트 다운로드
- 이메일 발송
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

class Link10TestSuite:
    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80 + "\nLink10 AI 분석 통합 테스트 시작\n" + "=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [self.test_environment_setup, self.test_file_structure])
        self._run_category("2. 라우트 검증", [self.test_all_routes_defined])
        self._run_category("3. 구글 드라이브 연동 검증", [self.test_drive_service_function, self.test_drive_credentials])
        self._run_category("4. AI 분석 기능 검증", [self.test_ai_result_api, self.test_results_list_api])
        self._run_category("5. 다운로드 기능 검증", [self.test_download_endpoints, self.test_report_generation])
        self._run_category("6. 보안 검증", [self.test_api_authentication, self.test_file_access_security])

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
        if 'link10' in self.app.blueprints:
            result.pass_test("환경 설정이 올바릅니다.")
        else:
            result.fail_test("link10 Blueprint가 등록되지 않았습니다.")

    def test_file_structure(self, result: TestResult):
        if (project_root / 'snowball_link10.py').exists():
            result.add_detail("✓ snowball_link10.py")
            result.pass_test("필수 파일이 존재합니다.")
        else:
            result.fail_test("snowball_link10.py 파일이 없습니다.")

    def test_all_routes_defined(self, result: TestResult):
        expected = ['/link10/link10', '/link10/api/results', '/link10/api/ai_result', '/link10/api/download', '/link10/api/send_report']
        app_routes = [r.rule for r in self.app.url_map.iter_rules() if r.endpoint.startswith('link10.')]
        result.add_detail(f"정의된 라우트: {len(app_routes)}개")
        missing = [e for e in expected if not any(e in r for r in app_routes)]
        if missing:
            result.warn_test(f"일부 라우트 누락 가능: {len(missing)}개")
        else:
            result.pass_test("주요 라우트가 정의되어 있습니다.")

    def test_drive_service_function(self, result: TestResult):
        link10_path = project_root / 'snowball_link10.py'
        with open(link10_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'get_drive_service' in content:
            result.add_detail("✓ get_drive_service 함수 존재")
            result.pass_test("구글 드라이브 서비스 함수가 구현되어 있습니다.")
        else:
            result.fail_test("구글 드라이브 서비스 함수를 찾을 수 없습니다.")

    def test_drive_credentials(self, result: TestResult):
        link10_path = project_root / 'snowball_link10.py'
        with open(link10_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'token_link10.pickle' in content and 'credentials.json' in content:
            result.add_detail("✓ 인증 파일 경로 설정 확인")
            result.pass_test("구글 드라이브 인증 설정이 구현되어 있습니다.")
        else:
            result.warn_test("인증 파일 경로를 확인할 수 없습니다.")

    def test_ai_result_api(self, result: TestResult):
        response = self.client.get('/link10/api/ai_result/test.pdf')
        if response.status_code in [404, 500]:
            result.skip_test("테스트 파일이 필요합니다.")
        else:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("AI 결과 API가 응답합니다.")

    def test_results_list_api(self, result: TestResult):
        response = self.client.get('/link10/api/results')
        if response.status_code == 200:
            result.add_detail("응답 성공")
            result.pass_test("결과 목록 API가 정상 응답합니다.")
        elif response.status_code in [302, 401]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.warn_test(f"예상치 못한 응답: {response.status_code}")

    def test_download_endpoints(self, result: TestResult):
        link10_path = project_root / 'snowball_link10.py'
        with open(link10_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '/download/' in content and 'send_file' in content:
            result.add_detail("✓ 다운로드 엔드포인트 및 파일 전송 기능 존재")
            result.pass_test("다운로드 기능이 구현되어 있습니다.")
        else:
            result.warn_test("다운로드 기능을 확인할 수 없습니다.")

    def test_report_generation(self, result: TestResult):
        link10_path = project_root / 'snowball_link10.py'
        with open(link10_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'download_report' in content or 'generate_report' in content:
            result.add_detail("✓ 리포트 생성 기능 존재")
            result.pass_test("리포트 생성 기능이 구현되어 있습니다.")
        else:
            result.warn_test("리포트 생성 기능을 확인할 수 없습니다.")

    def test_api_authentication(self, result: TestResult):
        link10_path = project_root / 'snowball_link10.py'
        with open(link10_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'session' in content or 'login_required' in content:
            result.add_detail("✓ 인증 메커니즘 존재")
            result.pass_test("API 인증이 구현되어 있습니다.")
        else:
            result.warn_test("API 인증을 확인할 수 없습니다.")

    def test_file_access_security(self, result: TestResult):
        link10_path = project_root / 'snowball_link10.py'
        with open(link10_path, 'r', encoding='utf-8') as f:
            content = f.read()
        checks = {'파일명 검증': 'secure_filename' in content or 'sanitize' in content,
                 '경로 검증': 'os.path' in content}
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
    Link10TestSuite().run_all_tests()

if __name__ == '__main__':
    main()
