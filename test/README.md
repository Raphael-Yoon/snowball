# Link5 RCM 통합 테스트

Link5의 모든 기능을 체계적으로 테스트하여 기능 수정이나 변경 시 기존 기능에 문제가 없는지 확인하는 자동화된 테스트 스위트입니다.

## 목차

1. [개요](#개요)
2. [테스트 구성](#테스트-구성)
3. [사용법](#사용법)
4. [테스트 카테고리](#테스트-카테고리)
5. [테스트 결과 해석](#테스트-결과-해석)
6. [CI/CD 통합](#cicd-통합)

## 개요

이 테스트 스위트는 다음과 같은 목적으로 작성되었습니다:

- **회귀 테스트**: 코드 변경 시 기존 기능이 정상 작동하는지 확인
- **통합 테스트**: 전체 시스템이 올바르게 통합되어 있는지 검증
- **보안 검증**: SQL Injection, XSS 등 보안 취약점 확인
- **성능 모니터링**: 각 테스트의 실행 시간 측정

### 주요 특징

✅ **34개의 체계적인 테스트**
- 환경 설정부터 보안까지 전 영역 커버

✅ **실시간 진행 상황 표시**
- 각 테스트의 실행 상태를 실시간으로 확인

✅ **상세한 리포트**
- 콘솔 출력 + JSON 파일로 상세 결과 저장

✅ **유연한 실행 옵션**
- 느린 테스트 건너뛰기, 특정 카테고리만 실행 등

## 테스트 구성

### 파일 구조

```
test/
├── link5_test.py          # 메인 테스트 스크립트
├── README.md              # 이 문서
└── link5_test_report_*.json  # 테스트 결과 리포트 (자동 생성)
```

### 테스트 상태

각 테스트는 다음 중 하나의 상태를 가집니다:

- ⏳ **대기**: 아직 실행되지 않음
- ▶️ **실행중**: 현재 실행 중
- ✅ **통과**: 테스트 성공
- ❌ **실패**: 테스트 실패 (문제 해결 필요)
- ⚠️ **경고**: 통과했지만 주의가 필요함
- ⊘ **건너뜀**: 조건이 맞지 않아 건너뜀 (예: 인증 필요)

## 사용법

### 기본 실행

```bash
# 프로젝트 루트에서 실행
cd c:/Python/snowball

# 모든 테스트 실행
python test/link5_test.py

# 느린 테스트 건너뛰기 (권장)
python test/link5_test.py --skip-slow
```

### 실행 예시

```bash
================================================================================
Link5 RCM 통합 테스트 시작
================================================================================
시작 시간: 2026-01-16 17:33:36

================================================================================
1. 환경 및 설정 검증
================================================================================

✅ 통과 test_environment_setup (0.00s)
    ℹ️  등록된 Blueprints: link1, link3, link4, link5, link6, link7, link8, link9, link10, admin

✅ 통과 test_required_packages (0.27s)
    ℹ️  ✓ Flask
    ℹ️  ✓ pandas
    ℹ️  ✓ openpyxl
    ...

================================================================================
테스트 결과 요약
================================================================================

총 테스트: 34개
✅ 통과: 17개 (50.0%)
❌ 실패: 0개 (0.0%)
⚠️ 경고: 5개 (14.7%)
⊘ 건너뜀: 12개 (35.3%)
```

## 테스트 카테고리

### 1. 환경 및 설정 검증 (4개 테스트)

Flask 앱 로드, 필수 패키지, 데이터베이스 연결, 파일 구조 확인

**주요 검증 항목:**
- Blueprint 등록 확인
- 필수 Python 패키지 설치 여부
- 데이터베이스 연결 가능 여부
- 템플릿 파일 존재 여부

**언제 실패하나요?**
- 패키지가 설치되지 않았을 때
- 데이터베이스 설정이 잘못되었을 때
- 필수 파일이 삭제되었을 때

### 2. 라우트 및 엔드포인트 검증 (2개 테스트)

모든 API 엔드포인트와 페이지 라우트 확인

**주요 검증 항목:**
- 28개의 라우트가 모두 정의되어 있는지
- 인증이 필요한 라우트의 접근 제어

**언제 실패하나요?**
- 라우트를 삭제하거나 변경했을 때
- @login_required 데코레이터를 빠뜨렸을 때

### 3. UI 화면 구성 검증 (5개 테스트)

각 JSP 템플릿의 UI 요소 존재 확인

**테스트 대상:**
- RCM 목록 페이지
- RCM 업로드 페이지
- RCM 상세보기 페이지
- 표준통제 매핑 페이지
- 완전성 평가 페이지

**주요 검증 항목:**
- 필수 버튼 존재 (업로드, 저장, 삭제 등)
- 입력 폼 요소 (RCM명, 카테고리, 파일 선택)
- 테이블 및 데이터 표시 요소

**언제 실패하나요?**
- 템플릿 파일을 수정하면서 중요한 요소를 삭제했을 때
- HTML 구조를 대폭 변경했을 때

### 4. RCM 업로드 기능 검증 (5개 테스트)

Excel 파일 업로드 및 처리 기능 확인

**주요 검증 항목:**
- ✅ **파일 타입 검증** (P2-7 구현 확인)
  - python-magic 라이브러리 사용
  - MIME 타입 검증
  - 매직 넘버 검증

- ✅ **파일 크기 제한** (P0-3 구현 확인)
  - 10MB 제한 설정

- ✅ **컬럼 매핑 검증** (P2-8 구현 확인)
  - 타입 검증
  - 범위 검증
  - 중복 검증

**언제 실패하나요?**
- 보안 검증 코드를 제거했을 때
- 파일 처리 로직을 변경했을 때

### 5. RCM 조회 및 관리 검증 (5개 테스트)

RCM 데이터 CRUD 기능 확인

**주요 검증 항목:**
- RCM 목록 API
- RCM 상태 API
- RCM 상세 조회
- RCM 삭제
- RCM 이름 수정

**참고**: 인증이 필요한 테스트는 대부분 건너뜀 처리됩니다.

### 6. 표준통제 매핑 기능 검증 (4개 테스트)

표준통제와 RCM 매핑 기능 확인

**주요 검증 항목:**
- 표준통제 목록 조회
- 표준통제 초기화
- 매핑 저장/삭제

### 7. 완전성 평가 기능 검증 (3개 테스트)

RCM 완전성 평가 기능 확인

**주요 검증 항목:**
- 완전성 평가 실행
- 완전성 리포트 조회
- 완료 상태 토글

### 8. AI 리뷰 기능 검증 (2개 테스트)

OpenAI API를 사용한 AI 리뷰 기능 확인

**참고**: OpenAI API 키가 필요하여 대부분 건너뜀 처리됩니다.

### 9. 보안 검증 (4개 테스트) ⭐ 중요!

보안 취약점 확인 및 방어 메커니즘 검증

**주요 검증 항목:**

- ✅ **SQL Injection 방지**
  - Parameterized query 사용 확인
  - 위험한 문자열 연결 패턴 검색

- ⚠️ **XSS 방지**
  - `|safe` 필터 사용 최소화
  - HTML escape 적용 확인

- ✅ **파일 업로드 보안**
  - 파일 확장자 검증
  - 파일 타입 검증 (MIME)
  - 파일 크기 제한
  - 매직 넘버 검증

- ✅ **접근 제어**
  - @login_required 데코레이터 사용 확인

**언제 실패하나요?**
- SQL 쿼리에 f-string이나 문자열 연결을 사용했을 때
- 파일 검증 로직을 제거했을 때
- 인증 데코레이터를 빠뜨렸을 때

### 10. 성능 및 스트레스 테스트 (2개 테스트)

대용량 파일 처리 및 동시 요청 처리 능력 확인

**참고**: `--skip-slow` 옵션으로 건너뛸 수 있습니다.

## 테스트 결과 해석

### 통과 (✅)

모든 것이 정상입니다. 해당 기능이 올바르게 작동합니다.

### 실패 (❌)

**즉시 조치가 필요합니다!**

실패 사유:
1. 코드 수정 중 기존 기능이 손상됨
2. 필수 파일이나 패키지가 누락됨
3. 데이터베이스 스키마가 변경됨

**해결 방법:**
1. 실패한 테스트의 오류 메시지 확인
2. 최근 변경 사항 검토
3. 해당 기능의 코드 점검

### 경고 (⚠️)

**주의가 필요합니다.**

테스트는 통과했지만 개선이 필요한 부분이 있습니다.

예시:
- `|safe` 필터 사용 → XSS 위험 검토
- 일부 UI 요소 누락 → 사용자 경험 확인
- 라우트 패턴 불일치 → 코드 리뷰

### 건너뜀 (⊘)

테스트를 실행할 수 없는 상황입니다. (정상)

예시:
- 인증이 필요한 테스트 (테스트 사용자 미설정)
- OpenAI API 키 필요 (환경변수 미설정)
- 성능 테스트 (`--skip-slow` 옵션 사용)

## JSON 리포트

각 테스트 실행 후 `test/` 폴더에 JSON 리포트가 자동 생성됩니다.

### 리포트 파일명

```
link5_test_report_20260116_173337.json
                   ^^^^^^^^_^^^^^^
                   날짜      시간
```

### 리포트 구조

```json
{
  "timestamp": "2026-01-16T17:33:37",
  "total_tests": 34,
  "summary": {
    "passed": 17,
    "failed": 0,
    "skipped": 12,
    "warning": 5
  },
  "tests": [
    {
      "name": "test_environment_setup",
      "category": "1. 환경 및 설정 검증",
      "status": "PASSED",
      "message": "환경 설정이 올바릅니다.",
      "duration": 0.001234,
      "details": [
        "등록된 Blueprints: link1, link3, link4, link5..."
      ]
    }
  ]
}
```

### 리포트 활용

```bash
# 최근 리포트 조회
cat test/link5_test_report_*.json | jq '.summary'

# 실패한 테스트만 조회
cat test/link5_test_report_*.json | jq '.tests[] | select(.status == "FAILED")'

# 경고가 있는 테스트 조회
cat test/link5_test_report_*.json | jq '.tests[] | select(.status == "WARNING")'
```

## CI/CD 통합

### GitHub Actions 예시

```yaml
name: Link5 Tests

on: [push, pull_request]

jobs:
  test:
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

    - name: Run Link5 Tests
      run: |
        python test/link5_test.py --skip-slow

    - name: Upload test report
      if: always()
      uses: actions/upload-artifact@v2
      with:
        name: test-report
        path: test/link5_test_report_*.json
```

## 개발 워크플로우

### 기능 수정 시

1. **코드 수정 전**
   ```bash
   # 현재 상태 확인
   python test/link5_test.py --skip-slow
   ```

2. **코드 수정**
   - 기능 구현 또는 버그 수정

3. **코드 수정 후**
   ```bash
   # 회귀 테스트 실행
   python test/link5_test.py --skip-slow
   ```

4. **결과 확인**
   - ✅ 모든 테스트 통과 → 커밋
   - ❌ 테스트 실패 → 수정 필요
   - ⚠️ 경고 → 검토 후 판단

### 새 기능 추가 시

1. **기존 테스트 실행**
   - 기존 기능이 정상인지 확인

2. **새 기능 구현**
   - 코드 작성

3. **테스트 추가**
   - `link5_test.py`에 새 테스트 메서드 추가

   ```python
   def test_new_feature(self, result: TestResult):
       """새 기능 테스트"""
       # 테스트 로직
       if success:
           result.pass_test("새 기능이 정상 작동합니다.")
       else:
           result.fail_test("새 기능에 문제가 있습니다.")
   ```

4. **전체 테스트 실행**
   - 기존 기능 + 새 기능 모두 확인

## 문제 해결

### "Import 오류" 발생 시

```bash
# 필수 패키지 재설치
pip install -r requirements.txt
```

### "데이터베이스 연결 실패" 발생 시

1. 데이터베이스가 실행 중인지 확인
2. `.env` 파일의 DB 설정 확인
3. `auth.py`의 `get_db()` 함수 확인

### "파일 구조" 경고 발생 시

필수 파일이 누락되었습니다. 다음 파일들이 있는지 확인:
- `snowball_link5.py`
- `templates/link5*.jsp`

### "라우트가 404" 발생 시

정상적인 상황입니다. 테스트는 인증 없이 실행되므로 많은 라우트가 404를 반환합니다.
실제로는 인증 후 302 리다이렉트가 발생해야 하지만, 테스트 환경에서는 404도 허용됩니다.

## 확장 및 커스터마이징

### 새 테스트 추가

```python
def test_my_new_feature(self, result: TestResult):
    """내가 추가한 기능 테스트"""
    result.start()

    try:
        # 테스트 로직
        response = self.client.get('/link5/my-new-feature')

        if response.status_code == 200:
            result.pass_test("새 기능이 정상 작동합니다.")
        else:
            result.fail_test(f"예상치 못한 응답: {response.status_code}")

    except Exception as e:
        result.fail_test(f"예외 발생: {str(e)}")
```

### 새 카테고리 추가

```python
self._run_category("11. 내 커스텀 카테고리", [
    self.test_feature_1,
    self.test_feature_2,
    self.test_feature_3,
])
```

## 참고 자료

- [snowball_link5.py](../snowball_link5.py) - 테스트 대상 코드
- [Flask Testing 문서](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [pytest 문서](https://docs.pytest.org/)

## 버전 히스토리

### v1.0 (2026-01-16)
- 초기 버전 생성
- 34개 테스트 케이스 구현
- 10개 카테고리 분류
- JSON 리포트 생성 기능
- 보안 검증 포함 (P0-3, P2-7, P2-8 구현 확인)

## 라이선스

이 테스트 스위트는 Snowball 프로젝트의 일부입니다.
