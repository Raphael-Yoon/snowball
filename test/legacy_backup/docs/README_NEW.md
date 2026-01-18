
# Snowball 테스트 가이드 (통합 버전)

## 📁 새로운 구조 (정리됨!)

```
test/
├── 🔵 단위 테스트
│   └── test_units_integrated.py         # 모든 단위 테스트 통합 ⭐
│
├── 🟢 E2E 테스트
│   └── test_e2e_integrated.py           # 모든 E2E 테스트 통합 ⭐
│
├── 🛠️ 유틸리티
│   ├── playwright_base.py               # Playwright 베이스 클래스
│   └── __init__.py
│
├── 📚 문서
│   ├── README_NEW.md                    # 이 문서 ⭐
│   ├── QUICKSTART_E2E.md
│   ├── PLAYWRIGHT_GUIDE.md
│   └── E2E_TEST_SCENARIOS.md
│
└── 📁 레거시 (참고용)
    ├── auth_test.py                     # 기존 단위 테스트들
    ├── link1_test.py ~ link10_test.py
    ├── auth_e2e_test.py                 # 기존 E2E 테스트들
    ├── link1_e2e_test.py
    └── ...
```

---

## 🚀 빠른 시작

### 1. 단위 테스트 실행 (빠름 - 1~2분)

```bash
# 전체 단위 테스트
python test/test_units_integrated.py

# 특정 모듈만
python test/test_units_integrated.py --module=auth
python test/test_units_integrated.py --module=link5
python test/test_units_integrated.py --module=link6
```

### 2. E2E 테스트 실행 (느림 - 10~15분)

```bash
# 먼저 애플리케이션 실행 (터미널 1)
python snowball.py

# E2E 테스트 실행 (터미널 2)
python test/test_e2e_integrated.py

# 특정 스위트만
python test/test_e2e_integrated.py --suite=auth
python test/test_e2e_integrated.py --suite=rcm
python test/test_e2e_integrated.py --suite=evaluation
python test/test_e2e_integrated.py --suite=interview

# 헤드리스 모드 (빠름)
python test/test_e2e_integrated.py --headless
```

---

## 📊 통합 테스트의 장점

### ✅ Before (기존 - 23개 파일)

```
test/
├── auth_test.py
├── link1_test.py
├── link2_test.py
├── link3_test.py
├── link4_test.py
├── link5_test.py            # 45KB
├── link6_test.py            # 29KB
├── link7_test.py            # 29KB
├── link8_test.py
├── link9_test.py
├── link10_test.py
├── admin_test.py
├── auth_e2e_test.py
├── link1_e2e_test.py
├── link2_interview_e2e_test.py
├── link5_rcm_upload_e2e_test.py
├── link6_design_evaluation_e2e_test.py
├── link7_operation_evaluation_e2e_test.py
├── playwright_base.py
├── run_all_tests.py
├── run_e2e_tests.py
├── user_journey_e2e_test.py
└── __init__.py
```

**문제점**:
- ❌ 파일이 너무 많음 (23개)
- ❌ 중복 코드 많음
- ❌ 유지보수 어려움
- ❌ 특정 모듈만 테스트하기 어려움

### ✅ After (통합 - 2개 파일)

```
test/
├── test_units_integrated.py    # 모든 단위 테스트
├── test_e2e_integrated.py      # 모든 E2E 테스트
├── playwright_base.py          # 공통 유틸리티
└── (문서들)
```

**장점**:
- ✅ 파일 개수 90% 감소 (23개 → 2개)
- ✅ 중복 코드 제거
- ✅ 파라미터로 모듈 선택 가능
- ✅ 유지보수 간편
- ✅ 일관된 구조

---

## 💡 사용 예시

### 시나리오 1: 개발 중 빠른 검증

```bash
# Auth 모듈 수정 후
python test/test_units_integrated.py --module=auth

# Link5 모듈 수정 후
python test/test_units_integrated.py --module=link5
```

### 시나리오 2: 커밋 전 전체 검증

```bash
# 모든 단위 테스트 실행
python test/test_units_integrated.py
```

### 시나리오 3: PR 생성 시 E2E 검증

```bash
# 애플리케이션 실행
python snowball.py &

# 핵심 E2E 테스트만
python test/test_e2e_integrated.py --suite=rcm --headless
python test/test_e2e_integrated.py --suite=evaluation --headless
```

### 시나리오 4: 배포 전 완전 검증

```bash
# 1. 단위 테스트 (빠름)
python test/test_units_integrated.py

# 2. E2E 테스트 (상세)
python snowball.py &
sleep 5
python test/test_e2e_integrated.py --headless
```

---

## 📋 파라미터 옵션

### 단위 테스트 (`test_units_integrated.py`)

```bash
--module=MODULE    # 테스트할 모듈 선택
                   # 옵션: all, auth, link1, link5, link6, link7
                   # 기본값: all

# 예시
python test/test_units_integrated.py --module=auth
python test/test_units_integrated.py --module=link5
```

### E2E 테스트 (`test_e2e_integrated.py`)

```bash
--suite=SUITE      # 테스트 스위트 선택
                   # 옵션: all, auth, rcm, evaluation, interview
                   # 기본값: all

--headless         # 헤드리스 모드 (브라우저 UI 숨김)
                   # 기본값: False (브라우저 표시)

--url=URL          # Base URL
                   # 기본값: http://localhost:5000

# 예시
python test/test_e2e_integrated.py --suite=auth
python test/test_e2e_integrated.py --suite=rcm --headless
python test/test_e2e_integrated.py --suite=evaluation --url=http://localhost:8000
```

---

## 🎯 테스트 스위트 매핑

### 단위 테스트 모듈

| 모듈 | 포함 내용 |
|------|----------|
| `auth` | 인증, OTP, 권한, 세션 |
| `link1` | RCM 자동생성 |
| `link5` | RCM 업로드, 파일 검증, 컬럼 매핑 |
| `link6` | 설계평가 |
| `link7` | 운영평가 |
| `all` | 위 모든 모듈 |

### E2E 테스트 스위트

| 스위트 | 포함 내용 | 실행 시간 |
|--------|----------|----------|
| `auth` | 로그인, OTP, 세션 관리 | 2~3분 |
| `rcm` | RCM 생성(Link1) + 업로드(Link5) | 3~5분 |
| `evaluation` | 설계평가(Link6) + 운영평가(Link7) | 4~6분 |
| `interview` | ITGC 인터뷰(Link2) | 2~3분 |
| `all` | 위 모든 스위트 | 10~15분 |

---

## 🔄 마이그레이션 가이드

### 기존 테스트 파일 → 통합 테스트

#### 기존 방식
```bash
# 23개 파일 실행
python test/auth_test.py
python test/link1_test.py
python test/link5_test.py
python test/link6_test.py
python test/link7_test.py
# ...
```

#### 새로운 방식 (통합)
```bash
# 한 번에 실행
python test/test_units_integrated.py

# 또는 특정 모듈만
python test/test_units_integrated.py --module=auth
```

---

## 📈 실행 결과 예시

### 단위 테스트

```bash
$ python test/test_units_integrated.py --module=link5

================================================================================
Snowball 통합 단위 테스트
================================================================================
시작 시간: 2026-01-18 16:30:45
대상 모듈: link5

================================================================================
Link5: RCM 관리
================================================================================

✅ test_link5_route (0.01s) - Link5 Blueprint 등록 확인
✅ test_file_validation (0.02s) - 파일 검증 로직이 구현되어 있습니다
    ℹ️  파일 타입 검증 함수 존재 확인

================================================================================
테스트 결과 요약
================================================================================

모듈별 결과:
  link5     :   2/  2 통과

총계:
  총 테스트: 2개
  ✅ 통과: 2개 (100.0%)
  ❌ 실패: 0개 (0.0%)
  ⚠️ 경고: 0개 (0.0%)
  ⊘ 건너뜀: 0개 (0.0%)
```

### E2E 테스트

```bash
$ python test/test_e2e_integrated.py --suite=auth --headless

================================================================================
Snowball 통합 E2E 테스트 (Playwright)
================================================================================
시작 시간: 2026-01-18 16:35:12
Base URL: http://localhost:5000
Headless: True
대상 스위트: auth

================================================================================
Auth: 인증 플로우
================================================================================

✅ test_login_page_loads (2.15s) - 로그인 페이지 로드 성공
✅ test_complete_login_flow (3.45s) - 로그인 플로우 완료

================================================================================
E2E 테스트 결과 요약
================================================================================

총 테스트: 2개
✅ 통과: 2개 (100.0%)
❌ 실패: 0개 (0.0%)
```

---

## 🆚 기존 파일 vs 통합 파일

### 언제 기존 파일을 사용하나요?

**거의 사용하지 않습니다.** 기존 파일들은 **레거시/참고용**으로 유지됩니다.

### 언제 통합 파일을 사용하나요?

**항상 사용합니다.** 다음과 같은 모든 경우:
- ✅ 개발 중 테스트
- ✅ 커밋 전 검증
- ✅ PR 생성 시
- ✅ 배포 전 최종 검증
- ✅ CI/CD 파이프라인

---

## 🎓 추가 문서

- **E2E 상세 가이드**: [PLAYWRIGHT_GUIDE.md](PLAYWRIGHT_GUIDE.md)
- **빠른 시작**: [QUICKSTART_E2E.md](QUICKSTART_E2E.md)
- **시나리오 목록**: [E2E_TEST_SCENARIOS.md](E2E_TEST_SCENARIOS.md)

---

## 🚮 기존 파일 정리 (선택 사항)

기존 테스트 파일들을 정리하고 싶다면:

```bash
# 백업 디렉토리 생성
mkdir test/legacy

# 기존 파일 이동
mv test/auth_test.py test/legacy/
mv test/link*_test.py test/legacy/
mv test/*_e2e_test.py test/legacy/
mv test/run_all_tests.py test/legacy/
mv test/run_e2e_tests.py test/legacy/
```

**주의**: 백업 후 삭제하는 것을 권장합니다!

---

**작성일**: 2026-01-18
**버전**: 2.0 (통합 버전)
**담당**: Snowball 개발팀
