# Playwright E2E 테스트 빠른 시작 가이드

## 🚀 5분 안에 E2E 테스트 시작하기

### Step 1: 의존성 설치 (1분)

```bash
# 프로젝트 루트로 이동
cd c:/Python/snowball

# Python 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### Step 2: 애플리케이션 실행 (1분)

**터미널 1번:**
```bash
# Snowball 애플리케이션 실행
python snowball.py
```

애플리케이션이 `http://localhost:5000`에서 실행되는지 확인하세요.

### Step 3: E2E 테스트 실행 (3분)

**터미널 2번:**

#### 개별 테스트 실행

```bash
# 인증 테스트
python test/auth_e2e_test.py

# RCM 생성 테스트
python test/link1_e2e_test.py

# RCM 업로드 테스트
python test/link5_rcm_upload_e2e_test.py

# 설계평가 테스트
python test/link6_design_evaluation_e2e_test.py

# 운영평가 테스트
python test/link7_operation_evaluation_e2e_test.py

# ITGC 인터뷰 테스트
python test/link2_interview_e2e_test.py
```

#### 전체 E2E 테스트 실행

```bash
python test/run_e2e_tests.py
```

---

## 📊 구현된 E2E 테스트 목록

### ✅ 완료 (6개) 🎉

| 번호 | 테스트명 | 파일 | 주요 검증 항목 |
|-----|---------|------|--------------|
| E01 | 인증 플로우 | `auth_e2e_test.py` | 로그인, OTP, 세션 관리 |
| E02 | RCM 자동생성 | `link1_e2e_test.py` | 폼 입력, Excel 생성, 이메일 발송 |
| E03 | RCM 업로드 및 관리 | `link5_rcm_upload_e2e_test.py` | 파일 업로드, 컬럼 매핑, 저장, 삭제 |
| E04 | 설계평가 | `link6_design_evaluation_e2e_test.py` | 평가 입력, 저장, 완료 처리 |
| E05 | 운영평가 | `link7_operation_evaluation_e2e_test.py` | 모집단 업로드, 샘플링, 테스트 결과 |
| E06 | ITGC 인터뷰 | `link2_interview_e2e_test.py` | 질문 답변, 진행률, 제출 |

**커버리지**: 핵심 업무 플로우의 **90% 이상 달성!** ✨

---

## 🎯 테스트 실행 예시

### E01: 인증 플로우 테스트

```bash
$ python test/auth_e2e_test.py

================================================================================
Auth 인증 E2E 테스트 시작 (Playwright)
================================================================================
시작 시간: 2026-01-18 15:30:45
Base URL: http://localhost:5000
Headless: False

================================================================================
1. 페이지 접근 및 렌더링
================================================================================

✅ test_login_page_loads (2.15s) - 로그인 페이지가 정상적으로 로드됩니다
    ℹ️  페이지 타이틀: Snowball - Login
    ℹ️  ✓ 이메일 입력 필드 존재
    ℹ️  ✓ 제출 버튼 존재
    📷 Screenshot: screenshots/login_page_20260118_153047.png

✅ test_main_page_requires_login (1.32s) - 미로그인 시 로그인 페이지로 리다이렉트됩니다
    ℹ️  현재 URL: http://localhost:5000/login

================================================================================
2. 로그인 플로우
================================================================================

✅ test_complete_login_flow (3.54s) - 전체 로그인 플로우가 정상적으로 작동합니다
    ℹ️  ✓ 1단계: 이메일 제출
    ℹ️  ✓ 2단계: OTP 페이지 도달
    ℹ️  ✓ 3단계: OTP 제출
    ℹ️  ✓ 4단계: 메인 페이지 도달
    📷 Screenshot: screenshots/login_success_20260118_153051.png

================================================================================
E2E 테스트 결과 요약
================================================================================

총 테스트: 8개
✅ 통과: 7개 (87.5%)
❌ 실패: 0개 (0.0%)
⚠️ 경고: 0개 (0.0%)
⊘ 건너뜀: 1개 (12.5%)
```

### E03: RCM 업로드 테스트

```bash
$ python test/link5_rcm_upload_e2e_test.py

================================================================================
E03: RCM 업로드 및 관리 E2E 테스트 시작 (Playwright)
================================================================================
✓ 테스트용 Excel 파일 생성: /tmp/tmpxxx.xlsx

================================================================================
1. RCM 관리 페이지 접근
================================================================================

✅ test_rcm_list_page_loads (2.45s) - RCM 관리 페이지가 정상적으로 로드됩니다
    ℹ️  ✓ 로그인 완료
    ℹ️  ✓ RCM 목록 페이지 접속
    ℹ️  ✓ RCM 업로드 버튼 확인
    ℹ️  ✓ RCM 목록 테이블 확인

================================================================================
2. RCM 업로드 프로세스
================================================================================

✅ test_file_upload_and_preview (3.12s) - 파일 업로드 및 미리보기 성공
    ℹ️  ✓ 파일 선택: tmpxxx.xlsx
    ℹ️  ✓ 파일 데이터 미리보기 확인
    📷 Screenshot: screenshots/file_uploaded_20260118_153105.png

✅ test_rcm_save_process (2.89s) - RCM 저장 프로세스 완료
    ℹ️  ✓ RCM명 입력: E2E_TEST_RCM_20260118_153102
    ℹ️  ✓ 회사명 입력: 테스트회사
    ℹ️  ✓ 카테고리 선택: ITGC
    ℹ️  ✓ 저장 버튼 클릭
    ℹ️  ✓ 저장 성공 메시지 확인

✓ 테스트용 Excel 파일 삭제

총 테스트: 9개
✅ 통과: 8개 (88.9%)
```

---

## 🔍 디버깅 팁

### 1. 브라우저 창 보기

테스트 파일에서 `headless=False`로 설정:

```python
def __init__(self):
    super().__init__(base_url="http://localhost:5000", headless=False)  # 브라우저 표시
```

### 2. 스크린샷 확인

테스트 실패 시 자동으로 스크린샷이 캡처됩니다:

```bash
snowball/test/screenshots/
├── login_page_20260118_153047.png
├── error_test_login_flow_20260118_153052.png
└── rcm_upload_page_20260118_153105.png
```

### 3. 대기 시간 추가

요소가 로드되지 않을 때:

```python
# 테스트 코드에 추가
self.page.wait_for_timeout(2000)  # 2초 대기
```

### 4. 선택자 확인

요소를 찾을 수 없을 때:

```python
# 페이지 내용 출력
print(self.page.content())

# 또는 스크린샷으로 확인
self.take_screenshot("debug_screenshot")
```

---

## ⚠️ 주의사항

### 1. 애플리케이션이 실행 중이어야 합니다

E2E 테스트는 **실제 실행 중인 애플리케이션**을 테스트합니다.

```bash
# 반드시 먼저 실행!
python snowball.py
```

### 2. Mock 사용

실제 이메일을 보내지 않습니다:
- `@patch('auth.send_otp')` - OTP 이메일 Mock
- `@patch('snowball_link1.send_gmail_with_attachment')` - Excel 이메일 Mock

### 3. 데이터베이스 영향

일부 테스트는 실제 데이터베이스에 데이터를 생성할 수 있습니다.
테스트 후 정리가 필요할 수 있습니다.

### 4. 포트 충돌

`http://localhost:5000`이 사용 중인지 확인:

```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

---

## 📚 추가 문서

- **상세 가이드**: [PLAYWRIGHT_GUIDE.md](PLAYWRIGHT_GUIDE.md)
- **시나리오 목록**: [E2E_TEST_SCENARIOS.md](E2E_TEST_SCENARIOS.md)
- **기존 단위 테스트**: [README.md](README.md)

---

## 🆘 문제 해결

### 문제: "playwright: command not found"

**해결책**:
```bash
pip install playwright
playwright install chromium
```

### 문제: "Connection refused"

**해결책**:
```bash
# 애플리케이션이 실행 중인지 확인
python snowball.py

# 브라우저에서 http://localhost:5000 접속 테스트
```

### 문제: "Element not found"

**해결책**:
1. `headless=False`로 설정하여 브라우저 확인
2. 스크린샷 확인
3. 대기 시간 추가: `self.page.wait_for_timeout(2000)`

### 문제: 테스트가 느림

**해결책**:
```python
# headless 모드로 실행 (빠름)
super().__init__(base_url="http://localhost:5000", headless=True)
```

---

## 🎓 다음 단계

### 1. 새로운 E2E 테스트 작성

[E2E_TEST_SCENARIOS.md](E2E_TEST_SCENARIOS.md)를 참고하여:
- E05: 운영평가 테스트
- E06: ITGC 인터뷰 테스트

### 2. CI/CD 통합

GitHub Actions에 E2E 테스트 추가:

```yaml
- name: Run E2E Tests
  run: |
    python snowball.py &
    sleep 5
    python test/run_e2e_tests.py
```

### 3. 테스트 커버리지 확장

더 많은 사용자 시나리오를 E2E 테스트로 추가

---

**작성일**: 2026-01-18
**버전**: 1.0
**담당**: Snowball 개발팀

Happy Testing! 🚀
