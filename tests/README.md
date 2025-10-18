# Snowball 테스트 가이드

## 테스트 실행 방법

### 전체 테스트 실행
```bash
pytest
```

### 특정 테스트 파일 실행
```bash
pytest tests/test_auth.py
pytest tests/test_routes.py
pytest tests/test_link2_interview.py
```

### 특정 테스트 클래스 실행
```bash
pytest tests/test_auth.py::TestUserManagement
pytest tests/test_routes.py::TestPublicPages
```

### 특정 테스트 함수 실행
```bash
pytest tests/test_auth.py::TestUserManagement::test_find_user_by_email_existing
```

### 마커를 사용한 테스트 실행
```bash
# 인증 관련 테스트만 실행
pytest -m auth

# 느린 테스트 제외
pytest -m "not slow"

# 통합 테스트만 실행
pytest -m integration
```

### 상세 출력으로 실행
```bash
pytest -v
pytest -vv  # 더 상세한 출력
```

### 실패한 테스트만 재실행
```bash
pytest --lf  # last failed
pytest --ff  # failed first
```

### 커버리지 리포트 생성
```bash
pytest --cov=snowball --cov-report=html
# 결과는 htmlcov/index.html 에서 확인
```

## 테스트 구조

```
tests/
├── __init__.py                  # 테스트 패키지 초기화
├── conftest.py                  # pytest 설정 및 공통 fixture
├── test_auth.py                 # 인증 기능 테스트
├── test_routes.py               # 라우팅 테스트
├── test_link2_interview.py      # 인터뷰 기능 테스트
└── README.md                    # 이 파일
```

## Fixture 설명

### `app`
- Flask 애플리케이션 인스턴스 (테스트 모드)
- 임시 데이터베이스 사용

### `client`
- Flask 테스트 클라이언트
- HTTP 요청 시뮬레이션

### `test_user`
- 일반 사용자 데이터베이스 레코드
- email: test@example.com

### `admin_user`
- 관리자 사용자 데이터베이스 레코드
- email: admin@example.com

### `authenticated_client`
- 로그인된 상태의 테스트 클라이언트
- test_user로 자동 로그인됨

### `mock_gmail_send`
- Gmail 발송 기능 모킹
- 실제 이메일 발송 없이 테스트

## 테스트 작성 가이드

### 1. 테스트 파일 명명 규칙
- `test_*.py` 형식으로 작성
- 기능별로 파일 분리

### 2. 테스트 클래스 명명 규칙
- `Test*` 로 시작
- 관련 기능별로 그룹화

### 3. 테스트 함수 명명 규칙
- `test_*` 로 시작
- 명확하고 설명적인 이름 사용

### 4. 테스트 작성 예시

```python
def test_user_login_success(client, test_user):
    """사용자가 올바른 정보로 로그인할 수 있는지 테스트"""
    response = client.post('/login', data={
        'email': test_user['user_email'],
        'password': 'correct_password'
    })
    assert response.status_code == 200
    assert '로그인 성공' in response.data.decode('utf-8')
```

## CI/CD 통합 (향후 계획)

GitHub Actions를 사용하여 자동 테스트를 실행할 수 있습니다:

```yaml
# .github/workflows/test.yml
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
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=snowball
```

## 문제 해결

### 데이터베이스 관련 오류
- conftest.py의 `_create_basic_test_tables` 함수 확인
- 테스트 데이터베이스가 올바르게 초기화되는지 확인

### Import 오류
- PYTHONPATH 설정 확인
- conftest.py에서 sys.path 설정 확인

### Fixture 오류
- conftest.py에서 fixture가 올바르게 정의되어 있는지 확인
- fixture 이름 철자 확인
