"""
Snowball 전체 테스트 실행 스크립트

단위 테스트와 E2E 테스트를 순차적으로 실행하고 통합 결과를 생성합니다.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_unit_tests():
    """단위 테스트 실행"""
    print("\n" + "=" * 80)
    print("1️⃣  단위 테스트 실행 중...")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, str(project_root / "test" / "test_units_integrated.py")],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    return result.returncode, result.stdout, result.stderr


def run_e2e_tests(base_url="http://localhost:5001"):
    """E2E 테스트 실행"""
    print("\n" + "=" * 80)
    print("2️⃣  E2E 테스트 실행 중...")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, str(project_root / "test" / "test_e2e_integrated.py"),
         "--headless", f"--url={base_url}"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    return result.returncode, result.stdout, result.stderr


def save_combined_report(unit_output, e2e_output):
    """통합 리포트 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = project_root / 'test' / f'test_result_{timestamp}.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Snowball 전체 테스트 결과\n")
        f.write("=" * 80 + "\n")
        f.write(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n\n")

        # 단위 테스트 결과
        f.write("=" * 80 + "\n")
        f.write("📘 단위 테스트 결과\n")
        f.write("=" * 80 + "\n")
        f.write(unit_output or "단위 테스트 결과 없음")
        f.write("\n\n")

        # E2E 테스트 결과
        f.write("=" * 80 + "\n")
        f.write("📗 E2E 테스트 결과\n")
        f.write("=" * 80 + "\n")
        f.write(e2e_output or "E2E 테스트 결과 없음")
        f.write("\n\n")

    return report_path


def cleanup_individual_reports():
    """개별 테스트 결과 파일 정리"""
    test_dir = project_root / 'test'

    # 단위 테스트 결과 삭제
    for file in test_dir.glob('unit_test_result_*.txt'):
        try:
            os.remove(file)
        except:
            pass

    # E2E 테스트 결과 삭제
    for file in test_dir.glob('e2e_test_result_*.txt'):
        try:
            os.remove(file)
        except:
            pass


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 80)
    print("🧪 Snowball 전체 테스트 시작")
    print("=" * 80)

    # 단위 테스트 실행
    unit_code, unit_out, unit_err = run_unit_tests()
    print(unit_out)
    if unit_err:
        print(unit_err, file=sys.stderr)

    # E2E 테스트 실행
    print("\n⚠️  E2E 테스트를 실행하려면 애플리케이션이 실행 중이어야 합니다!")
    print("   다른 터미널에서 'python snowball.py'를 실행하세요.\n")

    response = input("애플리케이션이 실행 중입니까? (y/n): ").lower()
    if response != 'y':
        print("\n❌ E2E 테스트를 건너뜁니다.")
        e2e_out = "E2E 테스트가 실행되지 않았습니다 (애플리케이션이 실행되지 않음)"
        e2e_code = 0
    else:
        e2e_code, e2e_out, e2e_err = run_e2e_tests()
        print(e2e_out)
        if e2e_err:
            print(e2e_err, file=sys.stderr)

    # 통합 리포트 저장
    report_path = save_combined_report(unit_out, e2e_out)

    # 개별 리포트 정리
    cleanup_individual_reports()

    # 최종 결과
    print("\n" + "=" * 80)
    print("✅ 전체 테스트 완료")
    print("=" * 80)
    print(f"📄 통합 결과 저장됨: {report_path}")
    print(f"🧹 개별 결과 파일 정리 완료")

    # 종료 코드 반환 (하나라도 실패하면 1)
    return 1 if (unit_code != 0 or e2e_code != 0) else 0


if __name__ == "__main__":
    sys.exit(main())
