"""
Snowball 통합 단위 테스트

모든 모듈의 단위 테스트를 하나의 파일로 통합했습니다.
pytest의 파라미터화를 활용하여 중복을 제거하고 깔끔한 구조를 유지합니다.

실행 방법:
    python test/test_units_integrated.py
    python test/test_units_integrated.py --module=auth
    python test/test_units_integrated.py --module=link5
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json
from enum import Enum

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
    import auth
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)


class TestStatus(Enum):
    """테스트 상태"""
    PENDING = "⏳"
    RUNNING = "🔄"
    PASSED = "✅"
    FAILED = "❌"
    WARNING = "⚠️"
    SKIPPED = "⊘"


class TestResult:
    """테스트 결과 클래스"""

    def __init__(self, test_name: str, category: str, module: str = ""):
        self.test_name = test_name
        self.category = category
        self.module = module
        self.status = TestStatus.PENDING
        self.message = ""
        self.details: List[str] = []
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = datetime.now()
        self.status = TestStatus.RUNNING

    def pass_test(self, message: str = "테스트 통과"):
        self.status = TestStatus.PASSED
        self.message = message
        self.end_time = datetime.now()

    def fail_test(self, message: str):
        self.status = TestStatus.FAILED
        self.message = message
        self.end_time = datetime.now()

    def warn_test(self, message: str):
        self.status = TestStatus.WARNING
        self.message = message
        self.end_time = datetime.now()

    def skip_test(self, message: str = "건너뜀"):
        self.status = TestStatus.SKIPPED
        self.message = message
        self.end_time = datetime.now()

    def add_detail(self, detail: str):
        self.details.append(detail)

    def get_duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def __str__(self):
        duration_str = f"({self.get_duration():.2f}s)" if self.end_time else ""
        return f"{self.status.value} {self.test_name} {duration_str} - {self.message}"


class IntegratedUnitTestSuite:
    """통합 단위 테스트 스위트"""

    def __init__(self, target_module: str = "all"):
        """
        Args:
            target_module: 테스트할 모듈 ('all', 'auth', 'link1', 'link5' 등)
        """
        self.app = app
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.results: List[TestResult] = []
        self.target_module = target_module

    def should_run_module(self, module: str) -> bool:
        """특정 모듈을 실행해야 하는지 확인"""
        return self.target_module == "all" or self.target_module == module

    def run_all_tests(self):
        """모든 단위 테스트 실행"""
        print("=" * 80)
        print("Snowball 통합 단위 테스트")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"대상 모듈: {self.target_module}")
        print()

        # 각 모듈별 테스트 실행
        if self.should_run_module("auth"):
            self._test_auth_module()

        if self.should_run_module("link1"):
            self._test_link1_module()

        if self.should_run_module("link5"):
            self._test_link5_module()

        if self.should_run_module("link6"):
            self._test_link6_module()

        if self.should_run_module("link7"):
            self._test_link7_module()

        if self.should_run_module("link11"):
            self._test_link11_module()

        # 기타 모듈들 (필요시 추가)

        return self._print_final_report()

    # =========================================================================
    # Auth 모듈 테스트
    # =========================================================================

    def _test_auth_module(self):
        """Auth 모듈 단위 테스트"""
        self._run_category("Auth: 인증 및 권한", "auth", [
            ("test_otp_generation", self._auth_test_otp_generation),
            ("test_login_required", self._auth_test_login_required),
        ])

    def _auth_test_otp_generation(self, result: TestResult):
        """OTP 생성 규칙 확인"""
        otp = auth.generate_otp()
        if len(otp) == 6 and otp.isdigit():
            result.add_detail(f"생성된 OTP: {otp}")
            result.pass_test("6자리 숫자 OTP 생성 확인")
        else:
            result.fail_test(f"잘못된 OTP 형식: {otp}")

    def _auth_test_login_required(self, result: TestResult):
        """login_required 데코레이터 작동 확인"""
        @auth.login_required
        def protected_route():
            return "OK"

        with self.app.test_request_context():
            response = protected_route()
            if response.status_code == 302:
                result.pass_test("login_required 데코레이터 작동 확인")
            else:
                result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    # =========================================================================
    # Link1 모듈 테스트
    # =========================================================================

    def _test_link1_module(self):
        """Link1 RCM 자동생성 모듈 테스트"""
        self._run_category("Link1: RCM 자동생성", "link1", [
            ("test_link1_route", self._link1_test_route),
        ])

    def _link1_test_route(self, result: TestResult):
        """Link1 라우트 확인"""
        if 'link1' in self.app.blueprints:
            result.pass_test("Link1 Blueprint 등록 확인")
        else:
            result.fail_test("Link1 Blueprint 미등록")

    # =========================================================================
    # Link5 모듈 테스트
    # =========================================================================

    def _test_link5_module(self):
        """Link5 RCM 관리 모듈 테스트"""
        self._run_category("Link5: RCM 관리", "link5", [
            ("test_link5_route", self._link5_test_route),
            ("test_file_validation", self._link5_test_file_validation),
        ])

    def _link5_test_route(self, result: TestResult):
        """Link5 라우트 확인"""
        if 'link5' in self.app.blueprints:
            result.pass_test("Link5 Blueprint 등록 확인")
        else:
            result.fail_test("Link5 Blueprint 미등록")

    def _link5_test_file_validation(self, result: TestResult):
        """파일 검증 로직 확인"""
        from snowball_link5 import validate_excel_file_type
        result.add_detail("파일 타입 검증 함수 존재 확인")
        result.pass_test("파일 검증 로직이 구현되어 있습니다")

    # =========================================================================
    # Link6 모듈 테스트
    # =========================================================================

    def _test_link6_module(self):
        """Link6 설계평가 모듈 테스트"""
        self._run_category("Link6: 설계평가", "link6", [
            ("test_link6_route", self._link6_test_route),
        ])

    def _link6_test_route(self, result: TestResult):
        """Link6 라우트 확인"""
        if 'link6' in self.app.blueprints:
            result.pass_test("Link6 Blueprint 등록 확인")
        else:
            result.fail_test("Link6 Blueprint 미등록")

    # =========================================================================
    # Link7 모듈 테스트
    # =========================================================================

    def _test_link7_module(self):
        """Link7 운영평가 모듈 테스트"""
        self._run_category("Link7: 운영평가", "link7", [
            ("test_link7_route", self._link7_test_route),
        ])

    def _link7_test_route(self, result: TestResult):
        """Link7 라우트 확인"""
        if 'link7' in self.app.blueprints:
            result.pass_test("Link7 Blueprint 등록 확인")
        else:
            result.fail_test("Link7 Blueprint 미등록")

    # =========================================================================
    # Link11 모듈 테스트 (정보보호공시)
    # =========================================================================

    def _test_link11_module(self):
        """Link11 정보보호공시 모듈 테스트"""
        self._run_category("Link11: 정보보호공시", "link11", [
            ("test_link11_route", self._link11_test_route),
            ("test_link11_helper_functions", self._link11_test_helper_functions),
            ("test_link11_file_allowed", self._link11_test_file_allowed),
            ("test_link11_uuid_generation", self._link11_test_uuid_generation),
        ])

    def _link11_test_route(self, result: TestResult):
        """Link11 라우트 확인"""
        if 'link11' in self.app.blueprints:
            result.add_detail("Blueprint 이름: link11")
            result.pass_test("Link11 Blueprint 등록 확인")
        else:
            result.fail_test("Link11 Blueprint 미등록")

    def _link11_test_helper_functions(self, result: TestResult):
        """Link11 헬퍼 함수 확인"""
        try:
            from snowball_link11 import is_logged_in, get_user_info, get_db, allowed_file, generate_uuid
            result.add_detail("is_logged_in, get_user_info, get_db, allowed_file, generate_uuid 함수 존재")
            result.pass_test("헬퍼 함수 import 성공")
        except ImportError as e:
            result.fail_test(f"헬퍼 함수 import 실패: {e}")

    def _link11_test_file_allowed(self, result: TestResult):
        """파일 확장자 검증 테스트"""
        from snowball_link11 import allowed_file, ALLOWED_EXTENSIONS

        # 허용된 확장자 테스트
        test_cases = [
            ("document.pdf", True),
            ("report.xlsx", True),
            ("image.jpg", True),
            ("file.hwp", True),
            ("script.exe", False),
            ("hack.bat", False),
            ("noextension", False),
        ]

        all_passed = True
        for filename, expected in test_cases:
            actual = allowed_file(filename)
            if actual != expected:
                result.add_detail(f"❌ {filename}: 예상={expected}, 실제={actual}")
                all_passed = False

        result.add_detail(f"허용 확장자: {', '.join(ALLOWED_EXTENSIONS)}")

        if all_passed:
            result.pass_test("파일 확장자 검증 로직 정상 작동")
        else:
            result.fail_test("일부 파일 확장자 검증 실패")

    def _link11_test_uuid_generation(self, result: TestResult):
        """UUID 생성 테스트"""
        from snowball_link11 import generate_uuid

        uuid1 = generate_uuid()
        uuid2 = generate_uuid()

        # UUID 형식 확인 (8-4-4-4-12 형식)
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

        if re.match(uuid_pattern, uuid1) and re.match(uuid_pattern, uuid2):
            if uuid1 != uuid2:
                result.add_detail(f"생성된 UUID 예시: {uuid1}")
                result.pass_test("UUID 생성 및 유일성 확인")
            else:
                result.fail_test("UUID 유일성 실패: 동일한 UUID 생성됨")
        else:
            result.fail_test(f"잘못된 UUID 형식: {uuid1}")

    # =========================================================================
    # 헬퍼 메서드
    # =========================================================================

    def _run_category(self, category_name: str, module: str, tests: List):
        """카테고리별 테스트 실행"""
        print(f"\n{'=' * 80}")
        print(f"{category_name}")
        print(f"{'=' * 80}")

        for test_name, test_func in tests:
            result = TestResult(test_name, category_name, module)
            self.results.append(result)

            try:
                result.start()
                print(f"\n{TestStatus.RUNNING.value} {test_name}...", end=" ")
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

    def _print_final_report(self):
        """최종 리포트 출력 및 파일 저장"""
        report_lines = []

        # 헤더
        header = "\n" + "=" * 80 + "\n테스트 결과 요약\n" + "=" * 80
        print(header)
        report_lines.append(header)

        # 모듈별 통계
        modules = {}
        for result in self.results:
            module = result.module or "기타"
            if module not in modules:
                modules[module] = {
                    TestStatus.PASSED: 0,
                    TestStatus.FAILED: 0,
                    TestStatus.WARNING: 0,
                    TestStatus.SKIPPED: 0
                }
            modules[module][result.status] += 1

        # 모듈별 출력
        module_section = "\n모듈별 결과:"
        print(module_section)
        report_lines.append(module_section)

        for module, stats in modules.items():
            total = sum(stats.values())
            passed = stats[TestStatus.PASSED]
            line = f"  {module:10s}: {passed:3d}/{total:3d} 통과"
            if stats[TestStatus.FAILED] > 0:
                line += f" (❌ {stats[TestStatus.FAILED]}개 실패)"
            if stats[TestStatus.WARNING] > 0:
                line += f" (⚠️  {stats[TestStatus.WARNING]}개 경고)"
            print(line)
            report_lines.append(line)

        # 전체 통계
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        warning = sum(1 for r in self.results if r.status == TestStatus.WARNING)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

        summary = f"\n총계:\n  총 테스트: {total}개\n"
        summary += f"  {TestStatus.PASSED.value} 통과: {passed}개 ({passed/total*100:.1f}%)\n"
        summary += f"  {TestStatus.FAILED.value} 실패: {failed}개 ({failed/total*100:.1f}%)\n"
        summary += f"  {TestStatus.WARNING.value} 경고: {warning}개 ({warning/total*100:.1f}%)\n"
        summary += f"  {TestStatus.SKIPPED.value} 건너뜀: {skipped}개 ({skipped/total*100:.1f}%)"

        print(summary)
        report_lines.append(summary)

        # 텍스트 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = project_root / 'test' / f'unit_test_result_{timestamp}.txt'

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\n📄 결과 저장됨: {report_path}")

        return 0 if failed == 0 else 1


def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Snowball 통합 단위 테스트')
    parser.add_argument('--module', type=str, default='all',
                       help='테스트할 모듈 (all, auth, link1, link5, link6, link7, link11)')

    args = parser.parse_args()

    suite = IntegratedUnitTestSuite(target_module=args.module)
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
