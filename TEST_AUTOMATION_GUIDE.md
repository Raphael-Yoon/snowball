# Snowball 테스트 자동화 가이드

## 개요

이 프로젝트는 pytest 기반의 테스트 자동화 시스템을 구축했습니다. 새로운 기능을 추가하거나 기존 기능을 수정할 때마다 자동으로 테스트를 실행하여 기능이 정상적으로 작동하는지 확인할 수 있습니다.

## 빠른 시작

### 1. 전체 테스트 실행
```bash
./run_tests.sh
# 또는
pytest
```

### 2. 빠른 테스트 (간단한 출력)
```bash
./run_tests.sh quick
```

### 3. 커버리지 확인
```bash
./run_tests.sh coverage
# 결과: htmlcov/index.html 파일 생성
```

## 테스트 구조

```
snowball/
├── tests/                          # 테스트 디렉토리
│   ├── __init__.py                # 패키지 초기화
│   ├── conftest.py                # pytest 설정 및 fixture
│   ├── test_auth.py               # 인증 기능 테스트 (14개)
│   ├── test_routes.py             # 라우팅 테스트 (23개)
│   ├── test_link2_interview.py    # 인터뷰 기능 테스트 (18개)
│   └── README.md                  # 테스트 상세 가이드
├── pytest.ini                      # pytest 설정 파일
├── run_tests.sh                    # 테스트 실행 스크립트
└── htmlcov/                        # 커버리지 리포트 (자동 생성)
```

## 현재 테스트 현황

### 총 테스트 수: 138개
- ✅ **test_auth.py**: 14개 테스트
  - 사용자 관리 (3)
  - 이메일 검증 (2)
  - OTP 생성 (3)
  - 세션 인증 (2)
  - 로그인 플로우 (3)
  - 헬스체크 (1)

- ✅ **test_routes.py**: 23개 테스트
  - 공개 페이지 (7)
  - 인증 페이지 (2)
  - 세션 관리 (3)
  - 인터뷰 플로우 (3)
  - 컨텐츠 엔드포인트 (2)
  - RCM 생성 (1)
  - AI 검토 플로우 (2)
  - 이메일 업데이트 (3)

- ✅ **test_link2_interview.py**: 18개 테스트
  - 조건부 질문 (2)
  - 건너뛴 답변 처리 (1)
  - 인터뷰 세션 플로우 (5)
  - AI 검토 선택 (4)
  - 진행률 추적 (2)
  - 인터뷰 처리 (2)
  - 질문 데이터 구조 (2)

- ✅ **test_link1_buttons.py**: 19개 테스트 (NEW!)
  - 폼 렌더링 (7)
  - 로그인 사용자 동작 (2)
  - RCM 생성 버튼 기능 (6)
  - 이메일 검증 (2)
  - 활동 로깅 (2)

- ✅ **test_link3_buttons.py**: 25개 테스트 (NEW!)
  - 페이지 렌더링 (4)
  - 사이드바 카테고리 (6)
  - 컨텐츠 동적 로드 (2)
  - 템플릿 다운로드 버튼 (3)
  - Step-by-step 네비게이션 (4)
  - 기타 (6)

- ✅ **test_link4_buttons.py**: 39개 테스트 (NEW!)
  - 페이지 렌더링 (3)
  - 사이드바 카테고리 (6)
  - 컨텐츠 동적 로드 (4)
  - 영상 컨텐츠 로드 (11)
  - YouTube 임베드 기능 (2)
  - video_map 데이터 구조 (8)
  - 기타 (5)

### 코드 커버리지: 향상 중
- snowball.py 메인 파일 커버리지 향상 중
- 핵심 기능 및 UI 버튼 기능 대부분 테스트됨
- **버튼 및 UI 테스트 83개 추가**로 전체 기능 커버리지 크게 향상

## 테스트 실행 옵션

### 기본 실행 방법
```bash
# 전체 테스트
pytest

# 특정 파일만 테스트
pytest tests/test_auth.py

# 특정 테스트 클래스
pytest tests/test_auth.py::TestUserManagement

# 특정 테스트 함수
pytest tests/test_auth.py::TestUserManagement::test_find_user_by_email_existing
```

### 편리한 스크립트 사용
```bash
# 전체 테스트
./run_tests.sh all

# 빠른 테스트
./run_tests.sh quick

# 커버리지 생성
./run_tests.sh coverage

# 인증 테스트만
./run_tests.sh auth

# 라우팅 테스트만
./run_tests.sh routes

# 인터뷰 테스트만
./run_tests.sh interview

# 실패한 테스트만 재실행
./run_tests.sh failed
```

## 새로운 기능 추가 시 테스트 작성 방법

### 1. 테스트 파일 생성
```python
# tests/test_새기능.py
import pytest

class Test새기능:
    """새 기능에 대한 테스트"""

    def test_기본_동작(self, client):
        """기본 동작 테스트"""
        response = client.get('/새기능')
        assert response.status_code == 200

    def test_인증된_사용자(self, authenticated_client):
        """로그인한 사용자 테스트"""
        response = authenticated_client.post('/새기능', data={
            'field': 'value'
        })
        assert response.status_code == 200
```

### 2. 사용 가능한 Fixture

#### `app`
- Flask 애플리케이션 인스턴스 (테스트 모드)
- 임시 데이터베이스 사용

```python
def test_example(app):
    with app.app_context():
        # 앱 컨텍스트 내에서 작업
        pass
```

#### `client`
- Flask 테스트 클라이언트 (비로그인)

```python
def test_public_page(client):
    response = client.get('/')
    assert response.status_code == 200
```

#### `authenticated_client`
- 로그인된 테스트 클라이언트

```python
def test_protected_page(authenticated_client):
    response = authenticated_client.get('/protected')
    assert response.status_code == 200
```

#### `test_user`
- 일반 테스트 사용자 (test@example.com)

```python
def test_user_info(test_user):
    assert test_user['user_email'] == 'test@example.com'
    assert test_user['admin_flag'] == 'N'
```

#### `admin_user`
- 관리자 테스트 사용자 (admin@example.com)

```python
def test_admin_access(admin_user):
    assert admin_user['admin_flag'] == 'Y'
```

## 테스트 작성 Best Practices

### 1. 명확한 테스트 이름
```python
# Good
def test_user_can_login_with_valid_credentials(client):
    pass

# Bad
def test_login(client):
    pass
```

### 2. 하나의 테스트는 하나의 기능만 검증
```python
# Good
def test_login_success(client):
    response = client.post('/login', data={'email': 'test@example.com'})
    assert response.status_code == 200

def test_login_failure(client):
    response = client.post('/login', data={'email': 'invalid'})
    assert response.status_code == 400

# Bad - 여러 시나리오를 한 테스트에
def test_login(client):
    # 성공 케이스
    # 실패 케이스
    # ...
```

### 3. AAA 패턴 사용 (Arrange-Act-Assert)
```python
def test_create_user(client):
    # Arrange - 테스트 준비
    user_data = {'name': 'Test', 'email': 'test@example.com'}

    # Act - 실제 동작
    response = client.post('/user', data=user_data)

    # Assert - 결과 검증
    assert response.status_code == 201
    assert 'user_id' in response.get_json()
```

## CI/CD 통합 (향후 계획)

GitHub Actions를 사용하여 자동 테스트를 실행할 수 있습니다:

```yaml
# .github/workflows/test.yml (예시)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-flask pytest-cov
      - name: Run tests
        run: pytest --cov=snowball
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 테스트 실행 예시

```bash
# 1. 새 기능 개발 전 - 기존 기능 확인
$ ./run_tests.sh
✓ 모든 테스트가 성공했습니다! (55 passed)

# 2. 새 기능 개발 및 테스트 작성
$ vim snowball/new_feature.py
$ vim tests/test_new_feature.py

# 3. 새 기능 테스트
$ pytest tests/test_new_feature.py -v
✓ 5 passed

# 4. 전체 테스트 - 기존 기능 영향 확인
$ ./run_tests.sh
✓ 모든 테스트가 성공했습니다! (60 passed)

# 5. 커버리지 확인
$ ./run_tests.sh coverage
Coverage: 65% (+4%)
```

## 문제 해결

### 테스트가 실패하는 경우

1. **데이터베이스 관련 오류**
   - 임시 DB가 올바르게 생성되는지 확인
   - `conftest.py`의 fixture 확인

2. **Import 오류**
   - PYTHONPATH 설정 확인
   - 모듈 경로가 올바른지 확인

3. **Fixture 오류**
   - fixture 이름 철자 확인
   - fixture 의존성 확인

### 상세 로그 보기
```bash
pytest -vv --tb=long
```

## 버튼 테스트 가이드

각 화면의 버튼과 UI 요소를 체계적으로 테스트하는 방법은 다음 문서를 참고하세요:

📄 **[BUTTON_TEST_GUIDE.md](tests/BUTTON_TEST_GUIDE.md)**

### 버튼 테스트 특징
- **모듈화**: 각 화면별로 독립적인 테스트 모듈
- **포괄적**: 폼, 버튼, 동적 컨텐츠, 사용자 인터랙션 모두 테스트
- **유지보수 용이**: 명확한 네이밍과 구조화된 테스트 클래스

### 버튼 테스트 실행
```bash
# 모든 버튼 테스트
pytest tests/test_link*_buttons.py -v

# 특정 화면의 버튼 테스트
pytest tests/test_link1_buttons.py -v
pytest tests/test_link3_buttons.py -v
pytest tests/test_link4_buttons.py -v
```

## 다음 단계

1. **추가 버튼 테스트 작성**
   - link5 (RCM 조회) 버튼 테스트
   - link6 (설계평가) 버튼 테스트
   - link7 (운영평가) 버튼 테스트
   - link8 (내부평가) 버튼 테스트
   - Admin 페이지 버튼 테스트

2. **통합 테스트 추가**
   - 전체 워크플로우 테스트
   - 이메일 발송 통합 테스트
   - E2E 테스트 (Selenium/Playwright)

3. **성능 테스트**
   - 부하 테스트
   - 버튼 응답 시간 측정
   - 페이지 로드 시간 측정

4. **CI/CD 파이프라인 구축**
   - GitHub Actions 설정
   - 자동 배포 연동
   - 자동 테스트 실행

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [pytest-flask 문서](https://pytest-flask.readthedocs.io/)
- [Flask Testing 가이드](https://flask.palletsprojects.com/en/latest/testing/)

---

**마지막 업데이트**: 2025-10-18
**테스트 수**: 138개 (기존 55개 + 버튼 테스트 83개)
**커버리지**: 향상 중
**상태**: ✅ All 138 tests passing
**버튼 테스트 추가**: Link1 (19), Link3 (25), Link4 (39)
