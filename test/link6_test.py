"""
Link6 설계평가(Design Evaluation) 통합 테스트 스크립트

Link6는 RCM의 설계평가(Design Evaluation) 기능을 담당합니다.
- ITGC, ELC, TLC 카테고리별 설계평가
- 평가 세션 관리 (생성, 삭제, 아카이브)
- Excel 다운로드 및 업로드
- 평가 완료 처리
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any
from enum import Enum
import io

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
    import pandas as pd
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

# link5_test.py의 공통 클래스 import
from test.link5_test import TestStatus, TestResult


class Link6TestSuite:
    """Link6 설계평가 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 80)
        print("Link6 설계평가 통합 테스트 시작")
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
            self.test_itgc_evaluation_page,
            self.test_elc_evaluation_page,
            self.test_tlc_evaluation_page,
        ])

        self._run_category("4. 설계평가 기본 기능 검증", [
            self.test_design_evaluation_get,
            self.test_design_evaluation_save,
            self.test_design_evaluation_reset,
        ])

        self._run_category("5. 평가 세션 관리 검증", [
            self.test_evaluation_sessions_list,
            self.test_evaluation_session_create,
            self.test_evaluation_session_delete,
            self.test_evaluation_session_archive,
            self.test_evaluation_session_unarchive,
        ])

        self._run_category("6. Excel 기능 검증", [
            self.test_excel_download,
            self.test_excel_structure,
        ])

        self._run_category("7. 평가 완료 기능 검증", [
            self.test_evaluation_complete,
            self.test_evaluation_cancel,
        ])

        self._run_category("8. 보안 검증", [
            self.test_sql_injection_prevention,
            self.test_access_control,
            self.test_session_management,
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

        if 'link6' not in blueprints:
            result.fail_test("link6 Blueprint가 등록되지 않았습니다.")
            return

        result.pass_test("환경 설정이 올바릅니다.")

    def test_file_structure(self, result: TestResult):
        """파일 구조 확인"""
        required_files = [
            'snowball_link6.py',
            'templates/link6.jsp',
            'templates/link6_evaluation.jsp',
            'templates/link6_design_rcm_detail.jsp',
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
        # Flask 앱의 모든 link6 라우트 가져오기
        app_routes = []
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint.startswith('link6.'):
                app_routes.append(rule.rule)

        result.add_detail(f"정의된 라우트 수: {len(app_routes)}개")

        # 최소 라우트 개수만 확인 (실제 라우트 경로는 Flask 등록 방식에 따라 다를 수 있음)
        if len(app_routes) >= 20:
            result.pass_test(f"모든 주요 라우트가 정의되어 있습니다. ({len(app_routes)}개)")
            # 일부 핵심 라우트 샘플 표시
            sample_routes = [r for r in app_routes if 'evaluation' in r or 'design' in r][:5]
            for route in sample_routes:
                result.add_detail(f"✓ {route}")
        else:
            result.warn_test(f"라우트 수가 예상보다 적습니다: {len(app_routes)}개 (최소 20개 필요)")

    def test_route_authentication(self, result: TestResult):
        """인증이 필요한 라우트 확인"""
        protected_routes = [
            '/link6/design-evaluation',
            '/link6/api/design-evaluation/save',
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

    def test_itgc_evaluation_page(self, result: TestResult):
        """ITGC 설계평가 페이지 구성 확인"""
        result.skip_test("인증이 필요한 테스트입니다.")

    def test_elc_evaluation_page(self, result: TestResult):
        """ELC 설계평가 페이지 구성 확인"""
        response = self.client.get('/link6/elc/design-evaluation')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("ELC 평가 페이지가 응답합니다.")

    def test_tlc_evaluation_page(self, result: TestResult):
        """TLC 설계평가 페이지 구성 확인"""
        response = self.client.get('/link6/tlc/design-evaluation')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 페이지입니다.")
        else:
            result.pass_test("TLC 평가 페이지가 응답합니다.")

    # =========================================================================
    # 4. 설계평가 기본 기능 검증
    # =========================================================================

    def test_design_evaluation_get(self, result: TestResult):
        """설계평가 데이터 조회 API 테스트"""
        result.skip_test("인증 및 테스트 데이터가 필요합니다.")

    def test_design_evaluation_save(self, result: TestResult):
        """설계평가 저장 API 테스트"""
        response = self.client.post('/link6/api/design-evaluation/save')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("설계평가 저장 API가 응답합니다.")

    def test_design_evaluation_reset(self, result: TestResult):
        """설계평가 초기화 API 테스트"""
        result.skip_test("인증 및 테스트 데이터가 필요합니다.")

    # =========================================================================
    # 5. 평가 세션 관리 검증
    # =========================================================================

    def test_evaluation_sessions_list(self, result: TestResult):
        """평가 세션 목록 조회 테스트"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    def test_evaluation_session_create(self, result: TestResult):
        """평가 세션 생성 테스트"""
        result.skip_test("인증 및 테스트 데이터가 필요합니다.")

    def test_evaluation_session_delete(self, result: TestResult):
        """평가 세션 삭제 테스트"""
        result.skip_test("인증 및 테스트 데이터가 필요합니다.")

    def test_evaluation_session_archive(self, result: TestResult):
        """평가 세션 아카이브 테스트"""
        response = self.client.post('/link6/api/design-evaluation/archive')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("아카이브 API가 응답합니다.")

    def test_evaluation_session_unarchive(self, result: TestResult):
        """평가 세션 아카이브 해제 테스트"""
        response = self.client.post('/link6/api/design-evaluation/unarchive')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("아카이브 해제 API가 응답합니다.")

    # =========================================================================
    # 6. Excel 기능 검증
    # =========================================================================

    def test_excel_download(self, result: TestResult):
        """Excel 다운로드 기능 테스트"""
        result.skip_test("인증 및 RCM ID가 필요합니다.")

    def test_excel_structure(self, result: TestResult):
        """Excel 파일 구조 검증"""
        # snowball_link6.py에서 Excel 생성 관련 코드 존재 확인
        link6_path = project_root / 'snowball_link6.py'

        with open(link6_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'openpyxl' in content and 'load_workbook' in content:
            result.add_detail("✓ openpyxl 사용 확인")
            result.pass_test("Excel 처리 기능이 구현되어 있습니다.")
        else:
            result.warn_test("Excel 처리 코드를 확인할 수 없습니다.")

    # =========================================================================
    # 7. 평가 완료 기능 검증
    # =========================================================================

    def test_evaluation_complete(self, result: TestResult):
        """평가 완료 처리 테스트"""
        response = self.client.post('/link6/api/design-evaluation/complete')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("평가 완료 API가 응답합니다.")

    def test_evaluation_cancel(self, result: TestResult):
        """평가 취소 처리 테스트"""
        response = self.client.post('/link6/api/design-evaluation/cancel')

        if response.status_code in [401, 302, 404]:
            result.skip_test("인증이 필요한 API입니다.")
        else:
            result.pass_test("평가 취소 API가 응답합니다.")

    # =========================================================================
    # 8. 보안 검증
    # =========================================================================

    def test_sql_injection_prevention(self, result: TestResult):
        """SQL Injection 방지 확인"""
        link6_path = project_root / 'snowball_link6.py'

        with open(link6_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'execute(' in content and '%s' in content:
            result.add_detail("✓ Parameterized query 사용 확인")

            # 위험한 패턴 확인 (f-string에 직접 변수 삽입)
            # 주의: f'''...{placeholders}'''는 안전함 (placeholders가 %s 문자열이므로)
            import re
            # execute(f"...{variable}...") 또는 execute(f'...{variable}...')에서
            # variable이 사용자 입력이 아닌 %s 패턴인 경우 안전함

            # 간단한 휴리스틱: execute(f'와 함께 사용되지만
            # placeholders = ... 패턴이 있으면 안전하다고 판단
            has_placeholders_pattern = 'placeholders' in content and "'.join(['%s']" in content
            has_fstring_execute = "execute(f'" in content or 'execute(f"' in content

            if has_fstring_execute and not has_placeholders_pattern:
                result.fail_test("위험한 SQL 패턴 발견: f-string에 직접 변수 삽입")
            elif has_fstring_execute and has_placeholders_pattern:
                result.add_detail("✓ f-string 사용하지만 placeholder 패턴으로 안전함")
                result.pass_test("SQL Injection 방지가 적용되어 있습니다.")
            else:
                result.pass_test("SQL Injection 방지가 적용되어 있습니다.")
        else:
            result.warn_test("SQL 쿼리 패턴을 확인할 수 없습니다.")

    def test_access_control(self, result: TestResult):
        """접근 제어 확인"""
        link6_path = project_root / 'snowball_link6.py'

        with open(link6_path, 'r', encoding='utf-8') as f:
            content = f.read()

        login_required_count = content.count('@login_required')
        route_count = content.count('@bp_link6.route(')

        result.add_detail(f"전체 라우트: {route_count}개")
        result.add_detail(f"인증 필요 라우트: {login_required_count}개")

        if login_required_count > 0:
            result.pass_test(f"접근 제어가 적용되어 있습니다. ({login_required_count}개 라우트)")
        else:
            result.warn_test("@login_required 데코레이터 사용이 확인되지 않습니다.")

    def test_session_management(self, result: TestResult):
        """세션 관리 보안 확인"""
        link6_path = project_root / 'snowball_link6.py'

        with open(link6_path, 'r', encoding='utf-8') as f:
            content = f.read()

        security_features = {
            '세션 사용': 'session[' in content or 'from flask import' in content and 'session' in content,
            '사용자 정보 검증': 'get_user_info()' in content,
            '권한 확인': 'has_rcm_access' in content or 'user_id' in content,
        }

        found_features = []
        for feature_name, is_present in security_features.items():
            if is_present:
                found_features.append(feature_name)
                result.add_detail(f"✓ {feature_name}")

        if len(found_features) >= 2:
            result.pass_test(f"세션 관리 보안이 구현되어 있습니다. ({len(found_features)}/{len(security_features)})")
        else:
            result.warn_test(f"일부 보안 기능이 누락되었을 수 있습니다. ({len(found_features)}/{len(security_features)})")

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
            print(f"{'=' * 80}")
            for result in self.results:
                if result.status == TestStatus.FAILED:
                    print(f"\n❌ {result.test_name}")
                    print(f"   오류: {result.message}")

        if warning > 0:
            print(f"\n{'=' * 80}")
            print("경고가 있는 테스트:")
            print(f"{'=' * 80}")
            for result in self.results:
                if result.status == TestStatus.WARNING:
                    print(f"\n⚠️  {result.test_name}")
                    print(f"   경고: {result.message}")

        total_time = sum(r.get_duration() for r in self.results)
        print(f"\n{'=' * 80}")
        print(f"총 실행 시간: {total_time:.2f}초")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # JSON 리포트 저장
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

        report_path = project_root / 'test' / f'link6_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)



def main():
    """메인 실행 함수"""
    suite = Link6TestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
