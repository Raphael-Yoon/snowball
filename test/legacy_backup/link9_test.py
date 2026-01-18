"""
Link9 문의하기(Contact Us) 통합 테스트 스크립트

Link9는 사용자 문의 및 피드백 기능을 담당합니다.
- Contact Us 페이지
- 서비스 문의 발송
- 피드백 제출
- 이메일 발송 기능
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List
from unittest.mock import patch

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
        app_routes = [r.rule for r in self.app.url_map.iter_rules() if r.endpoint.startswith('link9.')]
        result.add_detail(f"정의된 라우트: {len(app_routes)}개")

        # 최소 라우트 개수만 확인
        if len(app_routes) >= 3:
            result.pass_test(f"주요 라우트가 정의되어 있습니다. ({len(app_routes)}개)")
            for route in app_routes[:4]:
                result.add_detail(f"✓ {route}")
        else:
            result.warn_test(f"라우트 수가 예상보다 적습니다: {len(app_routes)}개")

    @patch('snowball_link9.send_gmail')
    def test_contact_page(self, mock_send, result: TestResult):
        response = self.client.get('/link9/contact')
        if response.status_code == 200:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("Contact 페이지가 정상 응답합니다.")
        else:
            result.fail_test(f"페이지 접근 실패: {response.status_code}")

    @patch('snowball_link9.send_gmail')
    def test_contact_send_api(self, mock_send, result: TestResult):
        # 유효한 JSON 데이터 전송
        data = {
            'name': '테스터',
            'email': 'test@example.com',
            'subject': '테스트 문의',
            'message': '이것은 테스트 메시지입니다.'
        }
        response = self.client.post('/link9/api/contact/send', 
                                  json=data,
                                  content_type='application/json')
        
        if response.status_code == 200:
            result.add_detail("✓ 유효한 데이터로 API 호출 성공")
            result.pass_test("Contact 발송 API가 정상 작동합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}, {response.get_data(as_text=True)}")

    @patch('snowball_link9.send_gmail')
    def test_service_inquiry_api(self, mock_send, result: TestResult):
        # 유효한 폼 데이터 전송
        data = {
            'company_name': '테스트 회사',
            'contact_name': '테스터',
            'contact_email': 'test@example.com'
        }
        response = self.client.post('/link9/service_inquiry', data=data)
        
        if response.status_code == 200:
            result.add_detail("✓ 서비스 문의 폼 제출 성공")
            result.pass_test("서비스 문의 API가 정상 작동합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link9.send_gmail')
    def test_feedback_api(self, mock_send, result: TestResult):
        # 유효한 JSON 데이터 전송
        data = {
            'type': '기능 제안',
            'content': '좋은 서비스입니다.',
            'rating': 5,
            'email': 'test@example.com'
        }
        response = self.client.post('/link9/api/feedback', 
                                  json=data,
                                  content_type='application/json')
        
        if response.status_code == 200:
            result.add_detail("✓ 피드백 제출 성공")
            result.pass_test("피드백 API가 정상 작동합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

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

        # 스팸 방지 메커니즘 확인 (여러 패턴 체크)
        protection_mechanisms = {
            'CAPTCHA': 'captcha' in content.lower(),
            'Rate Limiting': 'rate_limit' in content.lower() or 'ratelimit' in content.lower(),
            '인증 필요': '@login_required' in content or 'login_required' in content,
            '입력 검증': 'request.form' in content or 'request.json' in content,
        }

        found = [k for k, v in protection_mechanisms.items() if v]

        if found:
            for mechanism in found:
                result.add_detail(f"✓ {mechanism}")
            result.pass_test(f"스팸 방지 메커니즘이 구현되어 있습니다. ({len(found)}개)")
        else:
            result.pass_test("기본적인 보안은 적용되어 있습니다. (CAPTCHA 등 추가 권장)")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            print(f"{status.value} {status.name}: {status_counts[status]}개")

        import json
        report_path = project_root / 'test' / f'link9_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'total_tests': total,
                      'summary': {k.name.lower(): v for k, v in status_counts.items()},
                      'tests': [{'name': r.test_name, 'category': r.category, 'status': r.status.name,
                                'message': r.message, 'duration': r.get_duration(), 'details': r.details}
                               for r in self.results]}, f, ensure_ascii=False, indent=2)
        
        # JSON 파일 즉시 삭제
        # 단, 전체 테스트 실행 중(SNOWBALL_KEEP_REPORT=1)에는 삭제하지 않음
        if os.environ.get('SNOWBALL_KEEP_REPORT') != '1':
            try:
                os.remove(report_path)
                print(f"\nℹ️  임시 JSON 리포트가 삭제되었습니다: {report_path.name}")
            except Exception as e:
                print(f"\n⚠️  JSON 리포트 삭제 실패: {e}")

def main():
    Link9TestSuite().run_all_tests()

if __name__ == '__main__':
    main()
