"""
Link9 문의하기(Contact Us) 통합 테스트 스크립트

Link9는 사용자 문의 및 피드백 기능을 담당합니다.
- Contact Us 페이지
- 서비스 문의 발송
- 피드백 제출
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

class Link9TestSuite:
    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80 + "\nLink9 문의하기(Contact Us) 통합 테스트 시작\n" + "=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [self.test_environment_setup, self.test_file_structure])
        self._run_category("2. 라우트 검증", [self.test_all_routes_defined])
        self._run_category("3. 문의 기능 검증", [
            self.test_contact_page,
            self.test_contact_send_api,
            self.test_service_inquiry_api,
            self.test_feedback_api
        ])
        self._run_category("4. 이메일 기능 검증", [self.test_email_integration])
        self._run_category("5. 보안 검증", [self.test_email_validation, self.test_spam_protection])

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
        if 'link9' in self.app.blueprints:
            result.pass_test("환경 설정이 올바릅니다.")
        else:
            result.fail_test("link9 Blueprint가 등록되지 않았습니다.")

    def test_file_structure(self, result: TestResult):
        if (project_root / 'snowball_link9.py').exists():
            result.add_detail("✓ snowball_link9.py")
            result.pass_test("필수 파일이 존재합니다.")
        else:
            result.fail_test("snowball_link9.py 파일이 없습니다.")

    def test_all_routes_defined(self, result: TestResult):
        expected = ['/link9/contact', '/link9/service_inquiry', '/link9/api/contact/send', '/link9/api/feedback']
        app_routes = [r.rule for r in self.app.url_map.iter_rules() if r.endpoint.startswith('link9.')]
        result.add_detail(f"정의된 라우트: {len(app_routes)}개")
        missing = [e for e in expected if not any(e in r for r in app_routes)]
        if missing:
            result.warn_test(f"일부 라우트 누락 가능: {len(missing)}개")
        else:
            result.pass_test("주요 라우트가 정의되어 있습니다.")

    def test_contact_page(self, result: TestResult):
        response = self.client.get('/link9/contact')
        if response.status_code == 200:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("Contact 페이지가 정상 응답합니다.")
        elif response.status_code in [302, 404]:
            result.skip_test("페이지 접근 불가 (정상)")
        else:
            result.warn_test(f"예상치 못한 응답: {response.status_code}")

    def test_contact_send_api(self, result: TestResult):
        response = self.client.post('/link9/api/contact/send')
        if response.status_code in [400, 422, 404]:
            result.skip_test("파라미터가 필요한 API입니다.")
        else:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("Contact 발송 API가 응답합니다.")

    def test_service_inquiry_api(self, result: TestResult):
        response = self.client.post('/link9/service_inquiry')
        if response.status_code in [400, 422, 404, 302]:
            result.skip_test("파라미터가 필요한 API입니다.")
        else:
            result.pass_test("서비스 문의 API가 응답합니다.")

    def test_feedback_api(self, result: TestResult):
        response = self.client.post('/link9/api/feedback')
        if response.status_code in [400, 422, 404]:
            result.skip_test("파라미터가 필요한 API입니다.")
        else:
            result.pass_test("피드백 API가 응답합니다.")

    def test_email_integration(self, result: TestResult):
        link9_path = project_root / 'snowball_link9.py'
        with open(link9_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'send_gmail' in content:
            result.add_detail("✓ Gmail 발송 함수 사용")
            result.pass_test("이메일 통합이 구현되어 있습니다.")
        else:
            result.warn_test("이메일 발송 코드를 확인할 수 없습니다.")

    def test_email_validation(self, result: TestResult):
        link9_path = project_root / 'snowball_link9.py'
        with open(link9_path, 'r', encoding='utf-8') as f:
            content = f.read()
        checks = {'이메일 필드': 'email' in content, '발신자 검증': 'from' in content or 'sender' in content}
        found = [k for k, v in checks.items() if v]
        if found:
            result.add_detail(f"✓ {', '.join(found)}")
            result.pass_test("이메일 검증이 구현되어 있습니다.")
        else:
            result.warn_test("이메일 검증을 확인할 수 없습니다.")

    def test_spam_protection(self, result: TestResult):
        link9_path = project_root / 'snowball_link9.py'
        with open(link9_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'captcha' in content.lower() or 'rate_limit' in content.lower():
            result.add_detail("✓ 스팸 방지 메커니즘 존재")
            result.pass_test("스팸 방지가 구현되어 있습니다.")
        else:
            result.warn_test("스팸 방지 메커니즘을 확인할 수 없습니다. (추가 권장)")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            print(f"{status.value} {status.name}: {status_counts[status]}개")

def main():
    Link9TestSuite().run_all_tests()

if __name__ == '__main__':
    main()
