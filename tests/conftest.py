"""
E2E 테스트를 위한 Selenium 설정
"""
import pytest
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session")
def app_server():
    """테스트용 Flask 서버 시작"""
    import sys
    import os

    # 프로젝트 루트를 Python 경로에 추가
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.insert(0, project_root)

    # Flask 앱 임포트
    from snowball import app

    # 테스트 모드 설정
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # CSRF 토큰 비활성화 (테스트용)

    # 테스트 서버 시작 (별도 스레드)
    def run_server():
        app.run(port=5555, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 서버 시작 대기
    time.sleep(2)

    yield "http://localhost:5555"

    # 서버는 데몬 스레드라서 자동 종료됨


@pytest.fixture(scope="function")
def browser(app_server):
    """Selenium WebDriver 인스턴스 생성"""
    chrome_options = Options()

    # 헤드리스 모드 (백그라운드 실행)
    # 개발 중에는 주석 처리해서 브라우저를 볼 수 있음
    # chrome_options.add_argument("--headless")

    # 기타 옵션
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    # 로그 레벨 설정
    chrome_options.add_argument("--log-level=3")

    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 암묵적 대기 시간 설정 (요소 찾기 대기)
    driver.implicitly_wait(10)

    yield driver

    # 테스트 종료 후 브라우저 닫기
    driver.quit()


@pytest.fixture(scope="function")
def server_url(app_server):
    """베이스 URL 반환 (base_url과 이름 충돌 방지)"""
    return app_server


@pytest.fixture(scope="function")
def logged_in_browser(browser, server_url):
    """로그인된 상태의 브라우저 반환"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # 로그인 페이지로 이동
    browser.get(f"{server_url}/login")

    # 로그인 (실제 DB에 있는 테스트 계정 사용)
    # 테스트 계정이 없으면 먼저 생성 필요
    email_input = browser.find_element(By.ID, "email")
    email_input.send_keys("test@example.com")

    # OTP 입력 (테스트용으로는 고정 OTP 또는 DB에서 조회)
    # 실제 환경에서는 테스트용 OTP를 별도로 생성해야 함
    # 여기서는 로그인 로직이 있다고 가정

    # 참고: 실제 구현 시 세션을 직접 설정하는 방법도 있음
    # browser.get(f"{base_url}/test-login?email=test@example.com")

    yield browser


# 헬퍼 함수
def wait_for_element(driver, by, value, timeout=10):
    """요소가 나타날 때까지 대기"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_for_clickable(driver, by, value, timeout=10):
    """요소가 클릭 가능해질 때까지 대기"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
