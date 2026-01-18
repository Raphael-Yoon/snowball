# Playwright E2E 테스트 가이드

## 📋 목차
1. [개요](#개요)
2. [설치 및 설정](#설치-및-설정)
3. [테스트 실행](#테스트-실행)
4. [테스트 구조](#테스트-구조)
5. [새로운 테스트 작성](#새로운-테스트-작성)
6. [디버깅](#디버깅)
7. [모범 사례](#모범-사례)

## 개요

Playwright는 Microsoft에서 개발한 엔드투엔드(E2E) 테스트 프레임워크입니다.
실제 브라우저를 자동화하여 사용자의 실제 경험을 테스트할 수 있습니다.

### 기존 단위 테스트 vs Playwright E2E 테스트

| 구분 | 단위 테스트 (Unit Test) | E2E 테스트 (Playwright) |
|------|------------------------|------------------------|
| **목적** | 개별 함수/클래스 검증 | 실제 사용자 시나리오 검증 |
| **실행 환경** | Mock 기반 | 실제 브라우저 |
| **속도** | 빠름 (밀리초) | 느림 (초 단위) |
| **커버리지** | 로직 중심 | UI/UX 포함 전체 플로우 |
| **실행 시점** | 개발 중 / 커밋 전 | 배포 전 / 정기적 |

### Playwright의 장점

- ✅ **실제 브라우저 테스트**: Chrome, Firefox, Safari 지원
- ✅ **자동 대기**: 요소가 준비될 때까지 자동으로 대기
- ✅ **스크린샷 캡처**: 실패 시 자동으로 화면 캡처
- ✅ **네트워크 모니터링**: API 호출 추적
- ✅ **크로스 플랫폼**: Windows, Mac, Linux 모두 지원
- ✅ **헤드리스 모드**: CI/CD 환경에서 자동 실행

## 설치 및 설정

### 1. 의존성 설치

```bash
# requirements.txt에 이미 추가됨
pip install -r requirements.txt
```

### 2. Playwright 브라우저 설치

```bash
# Playwright가 사용할 브라우저 다운로드
playwright install

# Chromium만 설치 (권장)
playwright install chromium
```

### 3. 설치 확인

```bash
# Playwright 버전 확인
playwright --version
```

## 테스트 실행

### 전체 E2E 테스트 실행

```bash
cd snowball
python test/run_e2e_tests.py
```

⚠️ **중요**: E2E 테스트를 실행하기 전에 애플리케이션이 실행 중이어야 합니다!

```bash
# 터미널 1: 애플리케이션 실행
python snowball.py

# 터미널 2: E2E 테스트 실행
python test/run_e2e_tests.py
```

### 개별 테스트 실행

```bash
# Auth 테스트만 실행
python test/auth_e2e_test.py

# Link1 테스트만 실행
python test/link1_e2e_test.py
```

### 헤드리스 모드 설정

테스트 파일에서 `headless` 파라미터를 변경:

```python
# 브라우저 UI 보이기 (개발/디버깅용)
super().__init__(base_url="http://localhost:5000", headless=False)

# 헤드리스 모드 (CI/CD용)
super().__init__(base_url="http://localhost:5000", headless=True)
```

## 테스트 구조

### 프로젝트 구조

```
snowball/test/
├── playwright_base.py          # 베이스 클래스 및 유틸리티
├── auth_e2e_test.py            # 인증 E2E 테스트
├── link1_e2e_test.py           # Link1 RCM 생성 E2E 테스트
├── run_e2e_tests.py            # 통합 실행 스크립트
├── screenshots/                # 스크린샷 저장 디렉토리
│   ├── login_page_20260118_103045.png
│   └── error_test_*.png
└── PLAYWRIGHT_GUIDE.md         # 이 문서
```

### 테스트 클래스 구조

```python
from test.playwright_base import PlaywrightTestBase, E2ETestResult

class MyE2ETestSuite(PlaywrightTestBase):
    def __init__(self):
        super().__init__(base_url="http://localhost:5000", headless=False)

    def run_all_tests(self):
        self.setup()  # 브라우저 초기화

        self.run_category("카테고리명", [
            self.test_something,
            self.test_another,
        ])

        self.teardown()  # 브라우저 종료
        return self.print_final_report()

    def test_something(self, result: E2ETestResult):
        self.navigate_to("/some-page")

        # 테스트 로직
        if self.is_visible(".element"):
            result.pass_test("테스트 통과")
        else:
            result.fail_test("요소를 찾을 수 없음")
```

## 새로운 테스트 작성

### Step 1: 테스트 파일 생성

```python
# test/link2_e2e_test.py
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.playwright_base import PlaywrightTestBase, E2ETestResult

class Link2E2ETestSuite(PlaywrightTestBase):
    def __init__(self):
        super().__init__(base_url="http://localhost:5000", headless=False)

    def run_all_tests(self):
        self.setup()

        self.run_category("1. 페이지 접근", [
            self.test_link2_page_loads,
        ])

        self.teardown()
        return self.print_final_report()

    def test_link2_page_loads(self, result: E2ETestResult):
        """Link2 페이지 로드 테스트"""
        self.navigate_to("/link2")

        # 페이지 타이틀 확인
        title = self.page.title()
        result.add_detail(f"페이지 타이틀: {title}")

        # 스크린샷 캡처
        screenshot = self.take_screenshot("link2_page")
        result.add_screenshot(screenshot)

        result.pass_test("Link2 페이지가 정상 로드됨")

def main():
    suite = Link2E2ETestSuite()
    sys.exit(suite.run_all_tests())

if __name__ == '__main__':
    main()
```

### Step 2: 통합 스크립트에 등록

`run_e2e_tests.py`에 추가:

```python
tests = [
    ("Auth E2E (인증 플로우)", "auth_e2e_test.py"),
    ("Link1 E2E (RCM 생성)", "link1_e2e_test.py"),
    ("Link2 E2E (ITGC 인터뷰)", "link2_e2e_test.py"),  # 추가
]
```

## 디버깅

### 1. 헤드리스 모드 비활성화

브라우저 UI를 보면서 테스트:

```python
super().__init__(base_url="http://localhost:5000", headless=False)
```

### 2. 스크린샷 캡처

```python
def test_something(self, result: E2ETestResult):
    self.navigate_to("/page")

    # 특정 시점에 스크린샷 캡처
    screenshot = self.take_screenshot("debug_screenshot")
    result.add_screenshot(screenshot)
```

### 3. 브라우저 콘솔 로그 확인

콘솔 로그는 자동으로 캡처되어 터미널에 표시됩니다:

```
[Browser Console] log: User logged in
[Browser Console] error: Failed to fetch
```

### 4. 대기 시간 추가

요소가 로드되기를 기다리거나 디버깅용:

```python
import time

self.page.wait_for_timeout(2000)  # 2초 대기
time.sleep(2)  # 2초 대기
```

### 5. 선택자 테스트

Playwright Inspector 사용:

```bash
# Inspector와 함께 테스트 실행
PWDEBUG=1 python test/auth_e2e_test.py
```

## 모범 사례

### ✅ DO: 해야 할 것들

1. **명확한 테스트 이름 사용**
   ```python
   def test_user_can_login_with_valid_credentials(self, result):
       # 무엇을 테스트하는지 명확함
   ```

2. **스크린샷 적극 활용**
   ```python
   screenshot = self.take_screenshot("after_form_submit")
   result.add_screenshot(screenshot)
   ```

3. **상세 정보 추가**
   ```python
   result.add_detail(f"✓ 이메일 입력: {email}")
   result.add_detail(f"✓ 폼 제출 완료")
   ```

4. **예외 처리**
   ```python
   try:
       self.navigate_to("/page")
       # 테스트 로직
   except Exception as e:
       result.fail_test(f"오류 발생: {str(e)}")
   ```

5. **독립적인 테스트 작성**
   - 각 테스트는 다른 테스트에 의존하지 않아야 함
   - 순서가 바뀌어도 통과해야 함

### ❌ DON'T: 하지 말아야 할 것들

1. **하드코딩된 대기 시간 남용**
   ```python
   # ❌ 나쁜 예
   time.sleep(5)  # 무조건 5초 대기

   # ✅ 좋은 예
   self.wait_for_selector(".element", timeout=5000)  # 요소가 나타날 때까지 최대 5초
   ```

2. **불안정한 선택자 사용**
   ```python
   # ❌ 나쁜 예
   self.page.click("div > div > div:nth-child(3)")

   # ✅ 좋은 예
   self.page.click("#submit-button")
   self.page.click("[data-testid='submit']")
   ```

3. **너무 많은 것을 한 테스트에**
   ```python
   # ❌ 나쁜 예
   def test_entire_application(self, result):
       # 로그인부터 로그아웃까지 전부

   # ✅ 좋은 예
   def test_login_flow(self, result):
       # 로그인만 테스트

   def test_logout_flow(self, result):
       # 로그아웃만 테스트
   ```

## 주요 API 레퍼런스

### PlaywrightTestBase 메서드

```python
# 페이지 네비게이션
self.navigate_to("/path")

# 요소 찾기 및 대기
self.wait_for_selector(".element", timeout=5000)
self.check_element_exists(".element")  # True/False 반환

# 요소 상호작용
self.click_button("#button")
self.fill_input("#email", "test@example.com")
self.select_option("#dropdown", "option_value")

# 정보 가져오기
text = self.get_text(".element")
is_visible = self.is_visible(".element")

# 스크린샷
screenshot = self.take_screenshot("name")
```

### E2ETestResult 메서드

```python
result.pass_test("성공 메시지")
result.fail_test("실패 메시지")
result.warn_test("경고 메시지")
result.skip_test("건너뛰기 메시지")

result.add_detail("상세 정보")
result.add_screenshot("/path/to/screenshot.png")
```

## 트러블슈팅

### 문제: 브라우저가 실행되지 않음

**해결책**:
```bash
# 브라우저 재설치
playwright install chromium --force
```

### 문제: 타임아웃 에러

**해결책**:
```python
# 타임아웃 시간 증가
self.wait_for_selector(".element", timeout=10000)  # 10초
```

### 문제: 요소를 찾을 수 없음

**해결책**:
```python
# 1. 페이지 로드 대기
self.page.wait_for_load_state("networkidle")

# 2. 선택자 확인
self.page.screenshot(path="debug.png")  # 스크린샷으로 확인

# 3. 다양한 선택자 시도
self.page.locator("#id")
self.page.locator(".class")
self.page.locator("text=버튼명")
```

### 문제: 테스트가 간헐적으로 실패

**해결책**:
```python
# 명시적 대기 사용
self.page.wait_for_selector(".element")
self.page.wait_for_url("**/expected-url")

# 네트워크 안정화 대기
self.page.wait_for_load_state("networkidle")
```

## CI/CD 통합

### GitHub Actions 예시

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium

    - name: Start application
      run: |
        python snowball.py &
        sleep 5

    - name: Run E2E tests
      run: python test/run_e2e_tests.py

    - name: Upload screenshots
      if: failure()
      uses: actions/upload-artifact@v2
      with:
        name: screenshots
        path: test/screenshots/
```

## 참고 자료

- [Playwright 공식 문서](https://playwright.dev/python/)
- [Playwright API Reference](https://playwright.dev/python/docs/api/class-playwright)
- [Playwright Best Practices](https://playwright.dev/python/docs/best-practices)

---

**작성일**: 2026-01-18
**버전**: 1.0
**담당**: Snowball 개발팀
