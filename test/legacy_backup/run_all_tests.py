"""
전체 테스트 통합 실행 스크립트

Link5, Link6, Link7, Link8의 모든 테스트를 실행하고
체크리스트 형태의 텍스트 리포트를 생성합니다.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestReportGenerator:
    """체크리스트 형태의 테스트 리포트 생성기"""

    def __init__(self):
        self.test_results = {}
        self.report_path = None

    def run_test(self, test_name: str, test_file: str):
        """개별 테스트 실행"""
        print(f"\n{'=' * 80}")
        print(f"Running {test_name}...")
        print(f"{'=' * 80}")

        try:
            # 테스트 실행 (전체 테스트 시에는 JSON 파일을 삭제하지 않도록 환경변수 설정)
            env = os.environ.copy()
            env['SNOWBALL_KEEP_REPORT'] = '1'
            
            result = subprocess.run(
                [sys.executable, f"test/{test_file}"],
                cwd=project_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60,
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

    def generate_checklist_report(self):
        """체크리스트 형태의 텍스트 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_path = project_root / 'test' / f'test_checklist_{timestamp}.txt'

        with open(self.report_path, 'w', encoding='utf-8') as f:
            # 헤더
            f.write("=" * 100 + "\n")
            f.write(" " * 30 + "Snowball 통합 테스트 체크리스트\n")
            f.write("=" * 100 + "\n")
            f.write(f"\n생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"테스트 대상: 전체 Link 모듈 (Link1, Link3-10)\n")
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
                f.write(f"{status_icon} {test_name:20s}: {passed:3d}개 통과 / {failed:3d}개 실패 / {warning:3d}개 경고 / {skipped:3d}개 건너뜀 (총 {total}개)\n")

            f.write("\n" + "-" * 100 + "\n")
            f.write(f"{'총계':<20s}: {total_passed:3d}개 통과 / {total_failed:3d}개 실패 / {total_warning:3d}개 경고 / {total_skipped:3d}개 건너뜀 (총 {total_tests}개)\n")
            f.write("-" * 100 + "\n")

            # 최종 판정
            if total_failed == 0:
                f.write("\n✅ 최종 판정: 성공 - 모든 핵심 기능이 정상 작동합니다!\n")
            else:
                f.write(f"\n❌ 최종 판정: 실패 - {total_failed}개의 테스트가 실패했습니다. 즉시 조치가 필요합니다.\n")

            # 상세 체크리스트
            f.write("\n\n" + "=" * 100 + "\n")
            f.write("📋 상세 테스트 체크리스트\n")
            f.write("=" * 100 + "\n")

            for test_name, report_data in self.test_results.items():
                self._write_test_checklist(f, test_name, report_data)

            # 실패한 테스트 요약
            if total_failed > 0:
                f.write("\n\n" + "=" * 100 + "\n")
                f.write("❌ 실패한 테스트 상세 내역\n")
                f.write("=" * 100 + "\n")

                for test_name, report_data in self.test_results.items():
                    failed_tests = [t for t in report_data.get('tests', []) if t['status'] == 'FAILED']
                    if failed_tests:
                        f.write(f"\n[{test_name}]\n")
                        for test in failed_tests:
                            f.write(f"  ❌ {test['name']}\n")
                            f.write(f"     카테고리: {test['category']}\n")
                            f.write(f"     오류: {test['message']}\n")
                            if test.get('details'):
                                for detail in test['details']:
                                    f.write(f"     - {detail}\n")
                            f.write("\n")

            # 경고가 있는 테스트 요약
            if total_warning > 0:
                f.write("\n\n" + "=" * 100 + "\n")
                f.write("⚠️  경고가 있는 테스트 상세 내역\n")
                f.write("=" * 100 + "\n")

                for test_name, report_data in self.test_results.items():
                    warning_tests = [t for t in report_data.get('tests', []) if t['status'] == 'WARNING']
                    if warning_tests:
                        f.write(f"\n[{test_name}]\n")
                        for test in warning_tests:
                            f.write(f"  ⚠️  {test['name']}\n")
                            f.write(f"     카테고리: {test['category']}\n")
                            f.write(f"     경고: {test['message']}\n")
                            if test.get('details'):
                                for detail in test['details']:
                                    f.write(f"     - {detail}\n")
                            f.write("\n")

            # 권장 조치 사항
            f.write("\n\n" + "=" * 100 + "\n")
            f.write("💡 권장 조치 사항\n")
            f.write("=" * 100 + "\n\n")

            if total_failed > 0:
                f.write("🔴 실패한 테스트가 있습니다:\n")
                f.write("  1. 위의 '실패한 테스트 상세 내역'을 확인하세요.\n")
                f.write("  2. 각 오류 메시지를 읽고 문제를 파악하세요.\n")
                f.write("  3. 최근 코드 변경 사항을 검토하세요.\n")
                f.write("  4. 문제를 수정한 후 다시 테스트를 실행하세요.\n\n")

            if total_warning > 0:
                f.write("🟡 경고가 있는 테스트가 있습니다:\n")
                f.write("  1. 경고는 즉시 수정이 필요하지는 않지만, 검토가 필요합니다.\n")
                f.write("  2. '경고가 있는 테스트 상세 내역'을 확인하세요.\n")
                f.write("  3. 가능하면 경고 사항을 개선하세요.\n\n")

            if total_failed == 0:
                f.write("🟢 모든 핵심 테스트가 통과했습니다:\n")
                f.write("  1. 코드를 자신있게 배포할 수 있습니다.\n")
                f.write("  2. 정기적으로 테스트를 실행하여 품질을 유지하세요.\n")
                f.write("  3. 새로운 기능을 추가할 때마다 관련 테스트를 추가하세요.\n\n")

            # 푸터
            f.write("\n" + "=" * 100 + "\n")
            f.write("테스트 리포트 끝\n")
            f.write("=" * 100 + "\n")

        print(f"\n\n✅ 체크리스트 리포트 생성 완료: {self.report_path}")
        return self.report_path

    def _write_test_checklist(self, f, test_name: str, report_data: dict):
        """개별 테스트의 체크리스트 작성"""
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
                if status == 'PASSED':
                    icon = "✅"
                elif status == 'FAILED':
                    icon = "❌"
                elif status == 'WARNING':
                    icon = "⚠️ "
                elif status == 'SKIPPED':
                    icon = "⊘ "
                else:
                    icon = "❓"

                # 테스트 이름과 상태
                f.write(f"{icon} {name:50s} ({duration:.2f}s)\n")

                # 메시지가 있으면 표시
                if message:
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
    print(" " * 35 + "Snowball 전체 테스트 실행")
    print("=" * 100)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    generator = TestReportGenerator()

    # 각 테스트 실행
    tests = [
        ("Auth (인증 및 권한)", "auth_test.py"),
        ("Admin (관리자 기능)", "admin_test.py"),
        ("Link1 (RCM 자동생성)", "link1_test.py"),
        ("Link2 (ITGC 인터뷰)", "link2_test.py"),
        ("Link3 (운영평가 템플릿)", "link3_test.py"),
        ("Link4 (교육자료/동영상)", "link4_test.py"),
        ("Link5 (RCM 관리)", "link5_test.py"),
        ("Link6 (설계평가)", "link6_test.py"),
        ("Link7 (운영평가)", "link7_test.py"),
        ("Link8 (내부평가)", "link8_test.py"),
        ("Link9 (문의하기)", "link9_test.py"),
        ("Link10 (AI 분석)", "link10_test.py"),
    ]

    success_count = 0
    for test_name, test_file in tests:
        if generator.run_test(test_name, test_file):
            success_count += 1

    # 체크리스트 리포트 생성
    print("\n\n" + "=" * 100)
    print("체크리스트 리포트 생성 중...")
    print("=" * 100)

    checklist_path = generator.generate_checklist_report()

    # JSON 파일 삭제
    print("\n" + "=" * 100)
    print("JSON 임시 파일 정리 중...")
    print("=" * 100)

    test_dir = project_root / 'test'
    json_files = list(test_dir.glob('*_test_report_*.json'))

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
    print(" " * 35 + "테스트 실행 완료")
    print("=" * 100)
    print(f"\n실행된 테스트: {success_count}/{len(tests)}개")
    print(f"\n생성된 리포트: 📄 {checklist_path}")
    print("\n" + "=" * 100)


if __name__ == '__main__':
    main()
