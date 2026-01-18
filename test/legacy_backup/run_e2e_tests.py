"""
Playwright E2E 테스트 통합 실행 스크립트

모든 Playwright 기반 E2E 테스트를 실행하고
통합 리포트를 생성합니다.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class E2ETestReportGenerator:
    """E2E 테스트 리포트 생성기"""

    def __init__(self):
        self.test_results = {}
        self.report_path = None

    def run_test(self, test_name: str, test_file: str):
        """개별 E2E 테스트 실행"""
        print(f"\n{'=' * 80}")
        print(f"Running {test_name}...")
        print(f"{'=' * 80}")

        try:
            # 테스트 실행
            env = os.environ.copy()
            env['SNOWBALL_KEEP_REPORT'] = '1'

            result = subprocess.run(
                [sys.executable, f"test/{test_file}"],
                cwd=project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120,  # E2E 테스트는 더 긴 타임아웃
                env=env
            )

            # 출력 표시
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            # JSON 리포트 찾기
            test_reports = sorted(
                (project_root / 'test').glob(f'{test_file.replace(".py", "")}_report_*.json'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            if test_reports:
                with open(test_reports[0], 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    self.test_results[test_name] = report_data
                    return True
            else:
                print(f"⚠️  JSON 리포트를 찾을 수 없습니다: {test_name}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ 테스트 시간 초과: {test_name}")
            return False
        except Exception as e:
            print(f"❌ 테스트 실행 실패: {test_name} - {str(e)}")
            return False

    def generate_integrated_report(self):
        """통합 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_path = project_root / 'test' / f'e2e_test_report_{timestamp}.txt'

        with open(self.report_path, 'w', encoding='utf-8') as f:
            # 헤더
            f.write("=" * 100 + "\n")
            f.write(" " * 30 + "Snowball E2E 테스트 리포트 (Playwright)\n")
            f.write("=" * 100 + "\n")
            f.write(f"\n생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"테스트 도구: Playwright\n")
            f.write(f"테스트 유형: End-to-End (E2E)\n")
            f.write("\n" + "=" * 100 + "\n")

            # 전체 요약
            f.write("\n📊 전체 테스트 요약\n")
            f.write("-" * 100 + "\n\n")

            total_tests = 0
            total_passed = 0
            total_failed = 0
            total_warning = 0
            total_skipped = 0

            for test_name, report_data in self.test_results.items():
                summary = report_data.get('summary', {})
                passed = summary.get('passed', 0)
                failed = summary.get('failed', 0)
                warning = summary.get('warning', 0)
                skipped = summary.get('skipped', 0)
                total = report_data.get('total_tests', 0)

                total_tests += total
                total_passed += passed
                total_failed += failed
                total_warning += warning
                total_skipped += skipped

                status_icon = "✅" if failed == 0 else "❌"
                f.write(f"{status_icon} {test_name:30s}: {passed:3d}개 통과 / {failed:3d}개 실패 / "
                       f"{warning:3d}개 경고 / {skipped:3d}개 건너뜀 (총 {total}개)\n")

            f.write("\n" + "-" * 100 + "\n")
            f.write(f"{'총계':<30s}: {total_passed:3d}개 통과 / {total_failed:3d}개 실패 / "
                   f"{total_warning:3d}개 경고 / {total_skipped:3d}개 건너뜀 (총 {total_tests}개)\n")
            f.write("-" * 100 + "\n")

            # 최종 판정
            if total_failed == 0:
                f.write("\n✅ 최종 판정: 성공 - 모든 E2E 테스트가 통과했습니다!\n")
            else:
                f.write(f"\n❌ 최종 판정: 실패 - {total_failed}개의 E2E 테스트가 실패했습니다.\n")

            # 상세 내역
            f.write("\n\n" + "=" * 100 + "\n")
            f.write("📋 상세 테스트 내역\n")
            f.write("=" * 100 + "\n")

            for test_name, report_data in self.test_results.items():
                self._write_test_details(f, test_name, report_data)

            # 스크린샷 목록
            f.write("\n\n" + "=" * 100 + "\n")
            f.write("📷 캡처된 스크린샷\n")
            f.write("=" * 100 + "\n")

            screenshot_count = 0
            for test_name, report_data in self.test_results.items():
                for test in report_data.get('tests', []):
                    screenshots = test.get('screenshots', [])
                    if screenshots:
                        f.write(f"\n[{test_name}] {test['name']}\n")
                        for screenshot in screenshots:
                            f.write(f"  📷 {screenshot}\n")
                            screenshot_count += 1

            if screenshot_count == 0:
                f.write("\n캡처된 스크린샷이 없습니다.\n")
            else:
                f.write(f"\n총 {screenshot_count}개의 스크린샷이 캡처되었습니다.\n")

            # 권장 조치 사항
            f.write("\n\n" + "=" * 100 + "\n")
            f.write("💡 권장 조치 사항\n")
            f.write("=" * 100 + "\n\n")

            if total_failed > 0:
                f.write("🔴 E2E 테스트 실패:\n")
                f.write("  1. 애플리케이션이 실행 중인지 확인하세요 (http://localhost:5000)\n")
                f.write("  2. 캡처된 스크린샷을 확인하여 UI 문제를 파악하세요\n")
                f.write("  3. 브라우저 콘솔 로그를 확인하세요\n")
                f.write("  4. 테스트 환경 설정을 검토하세요\n\n")

            if total_warning > 0:
                f.write("🟡 경고 사항:\n")
                f.write("  1. UI/UX 개선이 필요할 수 있습니다\n")
                f.write("  2. 사용자 피드백 메시지를 강화하세요\n\n")

            if total_failed == 0:
                f.write("🟢 모든 E2E 테스트 통과:\n")
                f.write("  1. 실제 사용자 시나리오가 정상 작동합니다\n")
                f.write("  2. UI/UX가 예상대로 동작합니다\n")
                f.write("  3. 정기적으로 E2E 테스트를 실행하세요\n\n")

            # 푸터
            f.write("\n" + "=" * 100 + "\n")
            f.write("E2E 테스트 리포트 끝\n")
            f.write("=" * 100 + "\n")

        print(f"\n\n✅ E2E 테스트 리포트 생성 완료: {self.report_path}")
        return self.report_path

    def _write_test_details(self, f, test_name: str, report_data: dict):
        """개별 테스트의 상세 내역 작성"""
        f.write(f"\n\n{'=' * 100}\n")
        f.write(f"{test_name}\n")
        f.write(f"{'=' * 100}\n")

        # 카테고리별로 그룹화
        tests_by_category = {}
        for test in report_data.get('tests', []):
            category = test.get('category', '기타')
            if category not in tests_by_category:
                tests_by_category[category] = []
            tests_by_category[category].append(test)

        # 카테고리별로 출력
        for category, tests in tests_by_category.items():
            f.write(f"\n{category}\n")
            f.write(f"{'-' * 100}\n")

            for test in tests:
                status = test.get('status', 'UNKNOWN')
                name = test.get('name', 'unknown')
                message = test.get('message', '')
                duration = test.get('duration', 0)

                # 상태 아이콘
                icons = {
                    'PASSED': "✅",
                    'FAILED': "❌",
                    'WARNING': "⚠️",
                    'SKIPPED': "⊘"
                }
                icon = icons.get(status, "❓")

                # 테스트 이름과 상태
                f.write(f"{icon} {name:50s} ({duration:.2f}s)\n")
                f.write(f"   💬 {message}\n")

                # 상세 정보
                details = test.get('details', [])
                if details:
                    for detail in details:
                        f.write(f"   ℹ️  {detail}\n")

                f.write("\n")


def main():
    """메인 실행 함수"""
    print("=" * 100)
    print(" " * 30 + "Snowball E2E 테스트 실행 (Playwright)")
    print("=" * 100)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 애플리케이션 실행 확인
    print("⚠️  주의: E2E 테스트를 실행하기 전에 애플리케이션이 실행 중이어야 합니다!")
    print("   예: python snowball.py 또는 flask run")
    print("   기본 URL: http://localhost:5000\n")

    response = input("애플리케이션이 실행 중입니까? (y/n): ")
    if response.lower() != 'y':
        print("\n❌ 테스트 중단. 먼저 애플리케이션을 실행하세요.")
        sys.exit(1)

    generator = E2ETestReportGenerator()

    # 각 E2E 테스트 실행
    tests = [
        ("Auth E2E (인증 플로우)", "auth_e2e_test.py"),
        ("Link1 E2E (RCM 생성)", "link1_e2e_test.py"),
        ("Link2 E2E (ITGC 인터뷰)", "link2_interview_e2e_test.py"),
        ("Link5 E2E (RCM 업로드 및 관리)", "link5_rcm_upload_e2e_test.py"),
        ("Link6 E2E (설계평가)", "link6_design_evaluation_e2e_test.py"),
        ("Link7 E2E (운영평가)", "link7_operation_evaluation_e2e_test.py"),
        # 추가 E2E 테스트를 여기에 등록
        # ("User Journey E2E (통합 여정)", "user_journey_e2e_test.py"),
    ]

    success_count = 0
    for test_name, test_file in tests:
        if generator.run_test(test_name, test_file):
            success_count += 1

    # 통합 리포트 생성
    print("\n\n" + "=" * 100)
    print("통합 리포트 생성 중...")
    print("=" * 100)

    report_path = generator.generate_integrated_report()

    # JSON 파일 정리
    print("\n" + "=" * 100)
    print("JSON 임시 파일 정리 중...")
    print("=" * 100)

    test_dir = project_root / 'test'
    json_files = list(test_dir.glob('*_e2e_report_*.json'))

    if json_files:
        for json_file in json_files:
            try:
                json_file.unlink()
                print(f"✓ 삭제: {json_file.name}")
            except Exception as e:
                print(f"⚠️  삭제 실패: {json_file.name} - {str(e)}")
        print(f"\n총 {len(json_files)}개 JSON 파일 삭제 완료")
    else:
        print("삭제할 JSON 파일이 없습니다.")

    # 최종 요약
    print("\n\n" + "=" * 100)
    print(" " * 30 + "E2E 테스트 실행 완료")
    print("=" * 100)
    print(f"\n실행된 테스트: {success_count}/{len(tests)}개")
    print(f"\n생성된 리포트: 📄 {report_path}")
    print(f"스크린샷 디렉토리: 📷 {test_dir / 'screenshots'}")
    print("\n" + "=" * 100)


if __name__ == '__main__':
    main()
