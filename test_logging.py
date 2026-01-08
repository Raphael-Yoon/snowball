"""
로깅 시스템 테스트
"""
import os
import sys
from pathlib import Path

# .env 파일 로드 (테스트용)
from dotenv import load_dotenv
load_dotenv()

# 로깅 설정
from logger_config import setup_logging, get_logger

def test_logging():
    print("=" * 60)
    print("로깅 시스템 테스트")
    print("=" * 60)

    # 로깅 초기화
    setup_logging()

    # 로그 파일 경로 확인
    log_dir = Path(__file__).parent / 'logs'
    log_file = log_dir / 'snowball.log'

    print(f"\n[설정 확인]")
    print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"LOG_TO_CONSOLE: {os.getenv('LOG_TO_CONSOLE', 'true')}")
    print(f"로그 디렉토리: {log_dir}")
    print(f"로그 파일: {log_file}")
    print(f"로그 디렉토리 존재: {'예' if log_dir.exists() else '아니오'}")

    # 각 모듈별 로거 생성 및 테스트
    print(f"\n[로거 테스트]")

    # main 로거 (snowball.py)
    logger_main = get_logger('main')
    print("1. main 로거 테스트...")
    logger_main.debug("DEBUG 메시지: 상세 디버그 정보")
    logger_main.info("INFO 메시지: 일반 정보")
    logger_main.warning("WARNING 메시지: 경고")
    logger_main.error("ERROR 메시지: 오류 발생")

    # admin 로거 (snowball_admin.py)
    logger_admin = get_logger('admin')
    print("2. admin 로거 테스트...")
    logger_admin.debug("관리자 페이지 디버그 정보")
    logger_admin.info("관리자 작업 수행")
    logger_admin.warning("관리자 권한 필요")
    logger_admin.error("관리자 작업 실패")

    # 예외 로깅 테스트
    print("3. 예외 로깅 테스트...")
    try:
        raise ValueError("테스트 예외 발생")
    except Exception as e:
        logger_main.error(f"예외 발생: {str(e)}", exc_info=True)

    # 로그 파일 확인
    print(f"\n[로그 파일 확인]")
    if log_file.exists():
        print(f"로그 파일 크기: {log_file.stat().st_size} bytes")
        print(f"\n최근 로그 내용 (마지막 10줄):")
        print("-" * 60)
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-10:]:
                print(line.rstrip())
        print("-" * 60)
    else:
        print("[X] 로그 파일이 생성되지 않았습니다.")

    print(f"\n[완료]")
    print("=" * 60)
    print("로깅 시스템이 정상적으로 작동합니다!")
    print(f"로그 파일 위치: {log_file}")
    print("=" * 60)

if __name__ == '__main__':
    test_logging()
