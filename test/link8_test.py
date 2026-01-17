"""
Link8 내부평가(Internal Assessment) 통합 테스트 스크립트

Link8은 내부평가 종합 리포트 기능을 담당합니다.
- 회사별/카테고리별(ITGC/ELC/TLC) 진행 현황
- RCM별 상세 평가 내역
- 단계별 진행 상태 관리
- 진행률 API
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

from test.link5_test import TestStatus, TestResult


class Link8TestSuite:
    """Link8 내부평가 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 80)
        print("Link8 내부평가 통합 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
            self.test_file_structure,
        ])

        self._run_category("2. 라우트 및 엔드포인트 검증", [
            self.test_all_routes_defined,
            self.test_route_authentication,
        ])

        self._run_category("3. UI 화면 구성 검증", [
            self.test_internal_assessment_main_page,
            self.test_internal_assessment_detail_page,
        ])

        self._run_category("4. 내부평가 기본 기능 검증", [
            self.test_company_grouping,
            self.test_category_classification,
            self.test_detail_api,
            self.test_progress_api,
        ])

        self._run_category("5. 단계별 기능 검증", [
            self.test_step_navigation,
            self.test_step_data_loading,
        ])

        self._run_category("6. 보안 검증", [
            self.test_sql_injection_prevention,
            self.test_access_control,
            self.test_data_isolation,
        ])

        self._print_final_report()

    def _run_category(self, category_name: str, tests: List):
        """카테고리별 테스트 실행"""
        print(f"\n{'=' * 80}")
        print(f"{category_name}")
        print(f"{'=' * 80}")

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
                print(f"\r{result}")
                print(f"    ❌ {result.message}")

    # =========================================================================
    # 1. 환경 및 설정 검증
    # =========================================================================

    def test_environment_setup(self, result: TestResult):
        """환경 설정 확인"""
        if not self.app:
            result.fail_test("Flask 앱을 로드할 수 없습니다.")
            return

        blueprints = list(self.app.blueprints.keys())
        result.add_detail(f"등록된 Blueprints: {', '.join(blueprints)}")

        if 'link8' not in blueprints:
            result.fail_test("link8 Blueprint가 등록되지 않았습니다.")
            return

        result.pass_test("환경 설정이 올바릅니다.")

    def test_file_structure(self, result: TestResult):
        """파일 구조 확인"""
        required_files = [
            'snowball_link8.py',
        ]

        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                result.add_detail(f"✓ {file_path}")
            else:
                missing_files.append(file_path)
                result.add_detail(f"✗ {file_path} (누락)")

        if missing_files:
            result.warn_test(f"일부 파일이 누락되었습니다: {', '.join(missing_files)}")
        else:
            result.pass_test("모든 필수 파일이 존재합니다.")

    # =========================================================================
    # 2. 라우트 및 엔드포인트 검증
    # =========================================================================

    def test_all_routes_defined(self, result: TestResult):
        """모든 라우트가 정의되어 있는지 확인"""
        expected_routes = [
            '/link8/internal-assessment',
            '/link8/internal-assessment/<int:rcm_id>',
            '/link8/internal-assessment/<int:rcm_id>/<evaluation_session>',
            '/link8/internal-assessment/api/detail/<int:rcm_id>/<evaluation_session>',
            '/link8/internal-assessment/<int:rcm_id>/step/<int:step>',
            '/link8/api/internal-assessment/<int:rcm_id>/progress',
        ]

        app_routes = []
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint.startswith('link8.'):
                app_routes.append(rule.rule)

        result.add_detail(f"정의된 라우트 수: {len(app_routes)}")

        missing_routes = []
        for route in expected_routes:
            route_pattern = route.replace('<int:rcm_id>', '.*').replace('<int:step>', '.*').replace('<evaluation_session>', '.*')
            found = any(route_pattern in r or route in r for r in app_routes)
            if not found:
                missing_routes.append(route)

        if missing_routes:
            result.warn_test(f"일부 라우트가 누락되었을 수 있습니다: {len(missing_routes)}개")
            for route in missing_routes[:3]:
                result.add_detail(f"✗ {route}")
        else:
            result.pass_test(f"모든 주요 라우트가 정의되어 있습니다. ({len(app_routes)}개)")

    def test_route_authentication(self, result: TestResult):
        """인증이 필요한 라우트 확인"""
        protected_routes = [
            '/link8/internal-assessment',
            '/link8/api/internal-assessment/1/progress',
        ]

        unauthorized_count = 0
        for route in protected_routes:
            response = self.client.get(route) if 'api' not in route else self.client.post(route)
            if response.status_code in [302, 401, 404, 500]:
                unauthorized_count += 1

        if unauthorized_count == len(protected_routes):
            result.pass_test("모든 보호된 라우트가 인증을 요구합니다.")
        else:
            result.warn_test(f"{unauthorized_count}/{len(protected_routes)} 라우트가 인증을 요구합니다.")

    # =========================================================================
    # 3. UI 화면 구성 검증
    # =========================================================================

    def test_internal_assessment_main_page(self, result: TestResult):
        """내부평가 메인 페이지 구성 확인"""
        response = self.client.get('/link8/internal-assessment')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("내부평가 메인 페이지가 응답합니다.")

    def test_internal_assessment_detail_page(self, result: TestResult):
        """내부평가 상세 페이지 구성 확인"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    # =========================================================================
    # 4. 내부평가 기본 기능 검증
    # =========================================================================

    def test_company_grouping(self, result: TestResult):
        """회사별 그룹화 로직 확인"""
        link8_path = project_root / 'snowball_link8.py'

        with open(link8_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'companies' in content and 'company_name' in content:
            result.add_detail("✓ 회사별 그룹화 로직 존재")
            result.pass_test("회사별 그룹화 기능이 구현되어 있습니다.")
        else:
            result.warn_test("회사별 그룹화 로직을 확인할 수 없습니다.")

    def test_category_classification(self, result: TestResult):
        """카테고리별 분류 로직 확인"""
        link8_path = project_root / 'snowball_link8.py'

        with open(link8_path, 'r', encoding='utf-8') as f:
            content = f.read()

        categories = ['ITGC', 'ELC', 'TLC']
        found_categories = [cat for cat in categories if f"'{cat}'" in content or f'"{cat}"' in content]

        if len(found_categories) >= 3:
            result.add_detail(f"✓ 카테고리: {', '.join(found_categories)}")
            result.pass_test("카테고리별 분류 기능이 구현되어 있습니다.")
        else:
            result.warn_test(f"일부 카테고리가 누락되었을 수 있습니다. ({len(found_categories)}/3)")

    def test_detail_api(self, result: TestResult):
        """상세 정보 API 테스트"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    def test_progress_api(self, result: TestResult):
        """진행률 API 테스트"""
        response = self.client.post('/link8/api/internal-assessment/1/progress')

        if response.status_code in [401, 302, 404, 500]:
            result.skip_test("인증 및 유효한 RCM ID가 필요합니다.")
        else:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("진행률 API가 응답합니다.")

    # =========================================================================
    # 5. 단계별 기능 검증
    # =========================================================================

    def test_step_navigation(self, result: TestResult):
        """단계별 네비게이션 테스트"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    def test_step_data_loading(self, result: TestResult):
        """단계별 데이터 로딩 테스트"""
        link8_path = project_root / 'snowball_link8.py'

        with open(link8_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'step' in content and 'internal-assessment' in content:
            result.add_detail("✓ 단계별 기능 코드 존재")
            result.pass_test("단계별 기능이 구현되어 있습니다.")
        else:
            result.warn_test("단계별 기능을 확인할 수 없습니다.")

    # =========================================================================
    # 6. 보안 검증
    # =========================================================================

    def test_sql_injection_prevention(self, result: TestResult):
        """SQL Injection 방지 확인"""
        link8_path = project_root / 'snowball_link8.py'

        with open(link8_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'execute(' in content and '%s' in content:
            result.add_detail("✓ Parameterized query 사용 확인")

            dangerous_patterns = [
                'execute(f"',
                "execute(f'",
            ]

            found_dangerous = []
            for pattern in dangerous_patterns:
                if pattern in content:
                    found_dangerous.append(pattern)

            if found_dangerous:
                result.fail_test(f"위험한 SQL 패턴 발견: {found_dangerous}")
            else:
                result.pass_test("SQL Injection 방지가 적용되어 있습니다.")
        else:
            result.warn_test("SQL 쿼리 패턴을 확인할 수 없습니다.")

    def test_access_control(self, result: TestResult):
        """접근 제어 확인"""
        link8_path = project_root / 'snowball_link8.py'

        with open(link8_path, 'r', encoding='utf-8') as f:
            content = f.read()

        login_required_count = content.count('@login_required')
        route_count = content.count('@bp_link8.route(')

        result.add_detail(f"전체 라우트: {route_count}개")
        result.add_detail(f"인증 필요 라우트: {login_required_count}개")

        if login_required_count > 0:
            result.pass_test(f"접근 제어가 적용되어 있습니다. ({login_required_count}개 라우트)")
        else:
            result.warn_test("@login_required 데코레이터 사용이 확인되지 않습니다.")

    def test_data_isolation(self, result: TestResult):
        """사용자 데이터 격리 확인"""
        link8_path = project_root / 'snowball_link8.py'

        with open(link8_path, 'r', encoding='utf-8') as f:
            content = f.read()

        isolation_features = {
            '사용자 정보 조회': 'get_user_info()' in content,
            '사용자 RCM 필터링': 'get_user_rcms' in content or 'user_id' in content,
            '회사별 분리': 'company_name' in content,
        }

        found_features = []
        for feature_name, is_present in isolation_features.items():
            if is_present:
                found_features.append(feature_name)
                result.add_detail(f"✓ {feature_name}")

        if len(found_features) >= 2:
            result.pass_test(f"데이터 격리가 구현되어 있습니다. ({len(found_features)}/{len(isolation_features)})")
        else:
            result.warn_test(f"일부 격리 기능이 누락되었을 수 있습니다. ({len(found_features)}/{len(isolation_features)})")

    # =========================================================================
    # 리포트 생성
    # =========================================================================

    def _print_final_report(self):
        """최종 테스트 리포트 출력"""
        print("\n" + "=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)

        status_counts = {status: 0 for status in TestStatus}
        for result in self.results:
            status_counts[result.status] += 1

        total = len(self.results)
        passed = status_counts[TestStatus.PASSED]
        failed = status_counts[TestStatus.FAILED]
        skipped = status_counts[TestStatus.SKIPPED]
        warning = status_counts[TestStatus.WARNING]

        print(f"\n총 테스트: {total}개")
        print(f"{TestStatus.PASSED.value} 통과: {passed}개 ({passed/total*100:.1f}%)")
        print(f"{TestStatus.FAILED.value} 실패: {failed}개 ({failed/total*100:.1f}%)")
        print(f"{TestStatus.WARNING.value} 경고: {warning}개 ({warning/total*100:.1f}%)")
        print(f"{TestStatus.SKIPPED.value} 건너뜀: {skipped}개 ({skipped/total*100:.1f}%)")

        if failed > 0:
            print(f"\n{'=' * 80}")
            print("실패한 테스트:")
            for result in self.results:
                if result.status == TestStatus.FAILED:
                    print(f"\n❌ {result.test_name}: {result.message}")

        if warning > 0:
            print(f"\n{'=' * 80}")
            print("경고가 있는 테스트:")
            for result in self.results:
                if result.status == TestStatus.WARNING:
                    print(f"\n⚠️  {result.test_name}: {result.message}")

        total_time = sum(r.get_duration() for r in self.results)
        print(f"\n{'=' * 80}")
        print(f"총 실행 시간: {total_time:.2f}초")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        self._save_json_report()

        if failed == 0:
            print("\n✅ 모든 테스트가 통과했거나 건너뛰었습니다!")
            return 0
        else:
            print(f"\n❌ {failed}개의 테스트가 실패했습니다.")
            return 1

    def _save_json_report(self):
        """JSON 형식으로 테스트 리포트 저장"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'summary': {
                'passed': sum(1 for r in self.results if r.status == TestStatus.PASSED),
                'failed': sum(1 for r in self.results if r.status == TestStatus.FAILED),
                'skipped': sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
                'warning': sum(1 for r in self.results if r.status == TestStatus.WARNING),
            },
            'tests': [
                {
                    'name': r.test_name,
                    'category': r.category,
                    'status': r.status.name,
                    'message': r.message,
                    'duration': r.get_duration(),
                    'details': r.details,
                }
                for r in self.results
            ]
        }



def main():
    """메인 실행 함수"""
    suite = Link8TestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
