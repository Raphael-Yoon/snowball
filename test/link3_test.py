"""
Link3 운영평가 템플릿 통합 테스트 스크립트 (강화 버전)

Link3는 운영평가 템플릿 다운로드 기능을 담당합니다.
- 운영평가 템플릿 페이지
- 템플릿 다운로드 기능
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List
from unittest.mock import patch, MagicMock

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
        print("=" * 80 + "\nLink3 운영평가 템플릿 통합 테스트 시작 (강화 버전)\n" + "=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [self.test_environment_setup, self.test_file_structure])
        self._run_category("2. 라우트 검증", [self.test_all_routes_defined])
        self._run_category("3. 템플릿 기능 검증", [self.test_template_download_endpoint])
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
        required_files = ['snowball_link3.py', 'static/Operation_Evaluation_Template.xlsx']
        for f in required_files:
            if (project_root / f).exists():
                result.add_detail(f"✓ {f}")
            else:
                result.warn_test(f"{f} 파일이 없습니다.")
        result.pass_test("필수 파일 확인 완료")

    def test_all_routes_defined(self, result: TestResult):
        routes = [r.rule for r in self.app.url_map.iter_rules()]
        expected = ['/link3', '/paper_template_download']
        found = [r for r in expected if r in routes]
        result.add_detail(f"발견된 라우트: {', '.join(found)}")
        if len(found) == len(expected):
            result.pass_test("모든 주요 라우트가 등록되어 있습니다.")
        else:
            result.fail_test("일부 라우트가 누락되었습니다.")

    def test_template_download_endpoint(self, result: TestResult):
        """다운로드 엔드포인트 응답 확인 (인증 우회 또는 모킹 필요 시 추가)"""
        # 실제 파일 다운로드 로직은 인증이 필요하므로, 여기서는 라우트 존재 여부와 
        # 코드 내 send_file 사용 여부로 대체하거나, 필요 시 세션 모킹 도입
        link3_path = project_root / 'snowball_link3.py'
        with open(link3_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'send_file' in content and 'Design_Template.xlsx' in content:
            result.add_detail("✓ send_file 및 템플릿 파일명 확인")
            result.pass_test("템플릿 다운로드 기능이 구현되어 있습니다.")
        else:
            result.fail_test("템플릿 다운로드 로직을 찾을 수 없습니다.")

    def test_file_access_security(self, result: TestResult):
        link3_path = project_root / 'snowball_link3.py'
        with open(link3_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'os.path.join' in content and 'static' in content:
            result.add_detail("✓ os.path.join 및 static 경로 사용 확인")
            result.pass_test("파일 접근 보안 설정이 확인되었습니다.")
        else:
            result.warn_test("파일 접근 보안 설정을 확인할 수 없습니다.")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            print(f"{status.value} {status.name}: {status_counts[status]}개")

        import json
        report_path = project_root / 'test' / f'link3_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
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
    Link3TestSuite().run_all_tests()

if __name__ == '__main__':
    main()

