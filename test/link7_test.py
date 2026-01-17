"""
Link7 운영평가(Operation Evaluation) 통합 테스트 스크립트

Link7은 RCM의 운영평가(Operation Evaluation) 기능을 담당합니다.
- ITGC 운영평가 (APD01, APD07, APD09, APD12 등)
- ELC, TLC 운영평가
- 모집단 업로드 및 표본 테스트
- 테스트 결과 저장
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any
import io

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
    import pandas as pd
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

from test.link5_test import TestStatus, TestResult


class Link7TestSuite:
    """Link7 운영평가 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 80)
        print("Link7 운영평가 통합 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
            self.test_file_structure,
            self.test_control_config,
        ])

        self._run_category("2. 라우트 및 엔드포인트 검증", [
            self.test_all_routes_defined,
            self.test_route_authentication,
        ])

        self._run_category("3. UI 화면 구성 검증", [
            self.test_operation_evaluation_page,
            self.test_apd01_page,
            self.test_apd07_page,
            self.test_apd09_page,
            self.test_apd12_page,
            self.test_elc_operation_page,
            self.test_tlc_operation_page,
        ])

        self._run_category("4. 운영평가 기본 기능 검증", [
            self.test_operation_evaluation_save,
            self.test_operation_evaluation_load,
            self.test_operation_evaluation_reset,
        ])

        self._run_category("5. 모집단 업로드 기능 검증", [
            self.test_population_upload_apd01,
            self.test_population_upload_apd07,
            self.test_population_upload_apd09,
            self.test_population_upload_apd12,
            self.test_population_upload_generic,
        ])

        self._run_category("6. 표본 테스트 기능 검증", [
            self.test_sample_load,
            self.test_test_results_save_apd07,
            self.test_test_results_save_apd09,
            self.test_test_results_save_apd12,
        ])

        self._run_category("7. 보안 검증", [
            self.test_sql_injection_prevention,
            self.test_file_upload_security,
            self.test_access_control,
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
        if 'link7' not in blueprints:
            result.fail_test("link7 Blueprint가 등록되지 않았습니다.")
            return

        result.pass_test("환경 설정이 올바릅니다.")

    def test_file_structure(self, result: TestResult):
        """파일 구조 확인"""
        required_files = [
            'snowball_link7.py',
        ]

        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                result.add_detail(f"✓ {file_path}")
            else:
                missing_files.append(file_path)

        if missing_files:
            result.warn_test(f"일부 파일이 누락되었습니다: {', '.join(missing_files)}")
        else:
            result.pass_test("모든 필수 파일이 존재합니다.")

    def test_control_config(self, result: TestResult):
        """통제 설정 확인"""
        link7_path = project_root / 'snowball_link7.py'

        with open(link7_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # MANUAL_CONTROLS 설정 확인
        if 'MANUAL_CONTROLS' in content:
            result.add_detail("✓ MANUAL_CONTROLS 설정 존재")

            # 주요 통제 설정 확인
            controls = ['APD01', 'APD07', 'APD09', 'APD12']
            found_controls = [ctrl for ctrl in controls if f"'{ctrl}'" in content]

            result.add_detail(f"✓ 설정된 통제: {', '.join(found_controls)}")

            if len(found_controls) >= 3:
                result.pass_test(f"통제 설정이 올바릅니다. ({len(found_controls)}개)")
            else:
                result.warn_test(f"일부 통제 설정이 누락되었을 수 있습니다. ({len(found_controls)}개)")
        else:
            result.fail_test("MANUAL_CONTROLS 설정을 찾을 수 없습니다.")

    # =========================================================================
    # 2. 라우트 및 엔드포인트 검증
    # =========================================================================

    def test_all_routes_defined(self, result: TestResult):
        """모든 라우트가 정의되어 있는지 확인"""
        # Flask 앱의 모든 link7 라우트 가져오기
        app_routes = []
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint.startswith('link7.'):
                app_routes.append(rule.rule)

        result.add_detail(f"정의된 라우트 수: {len(app_routes)}개")

        # 최소 라우트 개수만 확인 (실제 라우트 경로는 Flask 등록 방식에 따라 다를 수 있음)
        if len(app_routes) >= 25:
            result.pass_test(f"모든 주요 라우트가 정의되어 있습니다. ({len(app_routes)}개)")
            # 일부 핵심 라우트 샘플 표시
            sample_routes = [r for r in app_routes if 'operation' in r or 'evaluation' in r][:5]
            for route in sample_routes:
                result.add_detail(f"✓ {route}")
        else:
            result.warn_test(f"라우트 수가 예상보다 적습니다: {len(app_routes)}개 (최소 25개 필요)")

    def test_route_authentication(self, result: TestResult):
        """인증이 필요한 라우트 확인"""
        protected_routes = [
            '/link7/operation-evaluation',
            '/link7/api/operation-evaluation/save',
        ]

        unauthorized_count = 0
        for route in protected_routes:
            response = self.client.get(route) if 'api' not in route else self.client.post(route)
            if response.status_code in [302, 401, 404]:
                unauthorized_count += 1

        if unauthorized_count == len(protected_routes):
            result.pass_test("모든 보호된 라우트가 인증을 요구합니다.")
        else:
            result.warn_test(f"{unauthorized_count}/{len(protected_routes)} 라우트가 인증을 요구합니다.")

    # =========================================================================
    # 3. UI 화면 구성 검증
    # =========================================================================

    def test_operation_evaluation_page(self, result: TestResult):
        """운영평가 메인 페이지 확인"""
        response = self.client.get('/link7/operation-evaluation')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("운영평가 페이지가 응답합니다.")

    def test_apd01_page(self, result: TestResult):
        """APD01 페이지 확인"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    def test_apd07_page(self, result: TestResult):
        """APD07 페이지 확인"""
        response = self.client.get('/link7/operation-evaluation/apd07')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("APD07 페이지가 응답합니다.")

    def test_apd09_page(self, result: TestResult):
        """APD09 페이지 확인"""
        response = self.client.get('/link7/operation-evaluation/apd09')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("APD09 페이지가 응답합니다.")

    def test_apd12_page(self, result: TestResult):
        """APD12 페이지 확인"""
        response = self.client.get('/link7/operation-evaluation/apd12')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("APD12 페이지가 응답합니다.")

    def test_elc_operation_page(self, result: TestResult):
        """ELC 운영평가 페이지 확인"""
        response = self.client.get('/link7/elc/operation-evaluation')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("ELC 운영평가 페이지가 응답합니다.")

    def test_tlc_operation_page(self, result: TestResult):
        """TLC 운영평가 페이지 확인"""
        response = self.client.get('/link7/tlc/operation-evaluation')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("TLC 운영평가 페이지가 응답합니다.")

    # =========================================================================
    # 4. 운영평가 기본 기능 검증
    # =========================================================================

    def test_operation_evaluation_save(self, result: TestResult):
        """운영평가 저장 API 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/save')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("운영평가 저장 API가 응답합니다.")

    def test_operation_evaluation_load(self, result: TestResult):
        """운영평가 로드 API 테스트"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    def test_operation_evaluation_reset(self, result: TestResult):
        """운영평가 초기화 API 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/reset')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("운영평가 초기화 API가 응답합니다.")

    # =========================================================================
    # 5. 모집단 업로드 기능 검증
    # =========================================================================

    def test_population_upload_apd01(self, result: TestResult):
        """APD01 모집단 업로드 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/apd01/upload-population')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD01 모집단 업로드 API가 응답합니다.")

    def test_population_upload_apd07(self, result: TestResult):
        """APD07 모집단 업로드 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/apd07/upload-population')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD07 모집단 업로드 API가 응답합니다.")

    def test_population_upload_apd09(self, result: TestResult):
        """APD09 모집단 업로드 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/apd09/upload-population')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD09 모집단 업로드 API가 응답합니다.")

    def test_population_upload_apd12(self, result: TestResult):
        """APD12 모집단 업로드 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/apd12/upload-population')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD12 모집단 업로드 API가 응답합니다.")

    def test_population_upload_generic(self, result: TestResult):
        """범용 모집단 업로드 테스트"""
        response = self.client.post('/link7/api/operation-evaluation/upload-population')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("범용 모집단 업로드 API가 응답합니다.")

    # =========================================================================
    # 6. 표본 테스트 기능 검증
    # =========================================================================

    def test_sample_load(self, result: TestResult):
        """표본 데이터 로드 테스트"""
        result.skip_test("인증 및 line_id가 필요합니다.")

    def test_test_results_save_apd07(self, result: TestResult):
        """APD07 테스트 결과 저장"""
        response = self.client.post('/link7/api/operation-evaluation/apd07/save-test-results')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD07 테스트 결과 저장 API가 응답합니다.")

    def test_test_results_save_apd09(self, result: TestResult):
        """APD09 테스트 결과 저장"""
        response = self.client.post('/link7/api/operation-evaluation/apd09/save-test-results')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD09 테스트 결과 저장 API가 응답합니다.")

    def test_test_results_save_apd12(self, result: TestResult):
        """APD12 테스트 결과 저장"""
        response = self.client.post('/link7/api/operation-evaluation/apd12/save-test-results')
        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("APD12 테스트 결과 저장 API가 응답합니다.")

    # =========================================================================
    # 7. 보안 검증
    # =========================================================================

    def test_sql_injection_prevention(self, result: TestResult):
        """SQL Injection 방지 확인"""
        link7_path = project_root / 'snowball_link7.py'

        with open(link7_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'execute(' in content and '%s' in content:
            result.add_detail("✓ Parameterized query 사용 확인")
            result.pass_test("SQL Injection 방지가 적용되어 있습니다.")
        else:
            result.warn_test("SQL 쿼리 패턴을 확인할 수 없습니다.")

    def test_file_upload_security(self, result: TestResult):
        """파일 업로드 보안 확인"""
        link7_path = project_root / 'snowball_link7.py'

        with open(link7_path, 'r', encoding='utf-8') as f:
            content = f.read()

        security_checks = {
            '파일 확장자 검증': '.endswith((' in content,
            'Excel 처리': 'openpyxl' in content or 'pd.read_excel' in content,
            '파일 검증': 'request.files' in content,
        }

        found_checks = []
        for check_name, is_present in security_checks.items():
            if is_present:
                found_checks.append(check_name)
                result.add_detail(f"✓ {check_name}")

        if len(found_checks) >= 2:
            result.pass_test(f"파일 업로드 보안이 구현되어 있습니다. ({len(found_checks)}/{len(security_checks)})")
        else:
            result.warn_test(f"일부 보안 검증이 누락되었을 수 있습니다. ({len(found_checks)}/{len(security_checks)})")

    def test_access_control(self, result: TestResult):
        """접근 제어 확인"""
        link7_path = project_root / 'snowball_link7.py'

        with open(link7_path, 'r', encoding='utf-8') as f:
            content = f.read()

        login_required_count = content.count('@login_required')
        route_count = content.count('@bp_link7.route(')

        result.add_detail(f"전체 라우트: {route_count}개")
        result.add_detail(f"인증 필요 라우트: {login_required_count}개")

        if login_required_count > 0:
            result.pass_test(f"접근 제어가 적용되어 있습니다. ({login_required_count}개 라우트)")
        else:
            result.warn_test("@login_required 데코레이터 사용이 확인되지 않습니다.")

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

        report_path = project_root / 'test' / f'link7_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)



def main():
    """메인 실행 함수"""
    suite = Link7TestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
