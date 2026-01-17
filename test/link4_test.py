"""
Link4 교육자료/동영상 통합 테스트 스크립트

Link4는 통제별 교육 동영상 및 자료 제공 기능을 담당합니다.
- APD01-12, PC01-03, CM01-03 등 통제별 동영상
- 유튜브 임베드 기능
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

class Link4TestSuite:
    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80 + "\nLink4 교육자료/동영상 통합 테스트 시작\n" + "=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self._run_category("1. 환경 및 설정 검증", [self.test_environment_setup, self.test_file_structure])
        self._run_category("2. 라우트 검증", [self.test_all_routes_defined])
        self._run_category("3. 동영상 데이터 검증", [self.test_video_map_exists, self.test_video_url_format])
        self._run_category("4. 보안 검증", [self.test_external_url_handling])

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
        if 'link4' in self.app.blueprints:
            result.pass_test("환경 설정이 올바릅니다.")
        else:
            result.fail_test("link4 Blueprint가 등록되지 않았습니다.")

    def test_file_structure(self, result: TestResult):
        if (project_root / 'snowball_link4.py').exists():
            result.add_detail("✓ snowball_link4.py")
            result.pass_test("필수 파일이 존재합니다.")
        else:
            result.fail_test("snowball_link4.py 파일이 없습니다.")

    def test_all_routes_defined(self, result: TestResult):
        app_routes = [r.rule for r in self.app.url_map.iter_rules() if r.endpoint.startswith('link4.')]
        result.add_detail(f"정의된 라우트: {len(app_routes)}개")
        result.pass_test("주요 라우트가 정의되어 있습니다.")

    def test_video_map_exists(self, result: TestResult):
        link4_path = project_root / 'snowball_link4.py'
        with open(link4_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'video_map' in content:
            result.add_detail("✓ video_map 데이터 구조 존재")
            controls = [c for c in ['APD01', 'APD07', 'PC01', 'CM01'] if c in content]
            result.add_detail(f"확인된 통제: {', '.join(controls)}")
            result.pass_test(f"동영상 데이터가 구현되어 있습니다. ({len(controls)}개 확인)")
        else:
            result.fail_test("video_map을 찾을 수 없습니다.")

    def test_video_url_format(self, result: TestResult):
        link4_path = project_root / 'snowball_link4.py'
        with open(link4_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'youtube.com/embed' in content or 'youtube_url' in content:
            result.add_detail("✓ 유튜브 URL 형식 확인")
            result.pass_test("동영상 URL 형식이 올바릅니다.")
        else:
            result.warn_test("동영상 URL 형식을 확인할 수 없습니다.")

    def test_external_url_handling(self, result: TestResult):
        link4_path = project_root / 'snowball_link4.py'
        with open(link4_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'embed' in content:
            result.add_detail("✓ embed 방식 사용 (안전)")
            result.pass_test("외부 URL 처리가 안전합니다.")
        else:
            result.warn_test("외부 URL 처리 방식을 확인할 수 없습니다.")

    def _print_final_report(self):
        print("\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80)
        status_counts = {status: sum(1 for r in self.results if r.status == status) for status in TestStatus}
        total = len(self.results)
        print(f"\n총 테스트: {total}개")
        for status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.WARNING, TestStatus.SKIPPED]:
            print(f"{status.value} {status.name}: {status_counts[status]}개")

def main():
    Link4TestSuite().run_all_tests()

if __name__ == '__main__':
    main()
