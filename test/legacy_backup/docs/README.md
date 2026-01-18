# Snowball 테스트 가이드 📚

> **통합 버전 2.0** - 깔끔하고 간단한 테스트 구조!

## 🎯 빠른 시작

```bash
# 단위 테스트 (1~2분)
python test/test_units_integrated.py

# E2E 테스트 (10~15분) - 애플리케이션 실행 필요!
python snowball.py &
python test/test_e2e_integrated.py
```

---

## 📁 디렉토리 구조 (깔끔함!)

```
test/
├── 📘 단위 테스트
│   └── test_units_integrated.py         # 모든 단위 테스트 (통합)
│
├── 📗 E2E 테스트
│   └── test_e2e_integrated.py           # 모든 E2E 테스트 (통합)
│
├── 🛠️ 유틸리티
│   ├── playwright_base.py               # Playwright 베이스 클래스
│   └── __init__.py
│
├── 📚 문서
│   ├── README.md                        # 이 파일 ⭐
│   ├── QUICKSTART_E2E.md                # 5분 빠른 시작
│   ├── PLAYWRIGHT_GUIDE.md              # Playwright 상세 가이드
│   └── E2E_TEST_SCENARIOS.md            # 시나리오 목록
│
└── 📦 백업
    └── legacy_backup/                   # 기존 파일들 (21개)
```

**Before**: 23개 파일 ❌
**After**: 4개 파일 ✅ (90% 감소!)

---

## 🚀 사용법

### 1. 단위 테스트 (Unit Tests)

```bash
# 전체 실행
python test/test_units_integrated.py

# 특정 모듈만 실행
python test/test_units_integrated.py --module=auth
python test/test_units_integrated.py --module=link5
python test/test_units_integrated.py --module=link6
python test/test_units_integrated.py --module=link7
```

**특징**:
- ⚡ 빠름 (밀리초~초 단위)
- 🎯 함수/API 레벨 검증
- 🔧 Mock 기반
- 💻 브라우저 불필요

**용도**: 개발 중, 커밋 전

---

### 2. E2E 테스트 (End-to-End Tests)

```bash
# 애플리케이션 먼저 실행 (터미널 1)
python snowball.py

# E2E 테스트 실행 (터미널 2)
python test/test_e2e_integrated.py

# 특정 스위트만 실행
python test/test_e2e_integrated.py --suite=auth
python test/test_e2e_integrated.py --suite=rcm
python test/test_e2e_integrated.py --suite=evaluation
python test/test_e2e_integrated.py --suite=interview

# 헤드리스 모드 (브라우저 UI 숨김)
python test/test_e2e_integrated.py --headless
```

**특징**:
- 🐢 느림 (초~분 단위)
- 🎨 UI/UX 검증
- 🌐 실제 브라우저 (Chromium)
- 📸 스크린샷 자동 캡처

**용도**: PR 생성 시, 배포 전

---

## 📊 파라미터 옵션

### 단위 테스트
```
--module=MODULE    # all, auth, link1, link5, link6, link7
```

### E2E 테스트
```
--suite=SUITE      # all, auth, rcm, evaluation, interview
--headless         # 헤드리스 모드
--url=URL          # Base URL (기본: http://localhost:5000)
```

---

## 🎯 모듈/스위트 매핑

### 단위 테스트 모듈

| 모듈 | 내용 |
|------|------|
| `auth` | 인증, OTP, 세션 |
| `link1` | RCM 자동생성 |
| `link5` | RCM 업로드, 파일 검증 |
| `link6` | 설계평가 |
| `link7` | 운영평가 |

### E2E 테스트 스위트

| 스위트 | 내용 | 시간 |
|--------|------|------|
| `auth` | 로그인, OTP | 2~3분 |
| `rcm` | RCM 생성 + 업로드 | 3~5분 |
| `evaluation` | 설계 + 운영평가 | 4~6분 |
| `interview` | ITGC 인터뷰 | 2~3분 |

---

## 💡 실전 예시

### 개발 중
```bash
# Link5 수정 후 빠른 검증
python test/test_units_integrated.py --module=link5
```

### 커밋 전
```bash
# 전체 단위 테스트
python test/test_units_integrated.py
```

### PR 생성 시
```bash
# 핵심 E2E만
python snowball.py &
python test/test_e2e_integrated.py --suite=rcm --headless
```

### 배포 전
```bash
# 단위 + E2E 전체
python test/test_units_integrated.py
python snowball.py &
python test/test_e2e_integrated.py --headless
```

---

## 📈 실행 결과

### 단위 테스트
```
================================================================================
Snowball 통합 단위 테스트
================================================================================
시작 시간: 2026-01-18 16:30:45
대상 모듈: all

✅ Auth: 2개 통과
✅ Link5: 2개 통과
✅ Link6: 1개 통과
✅ Link7: 1개 통과

총계: 6개 테스트, 6개 통과 (100%)
```

### E2E 테스트
```
================================================================================
Snowball 통합 E2E 테스트 (Playwright)
================================================================================
시작 시간: 2026-01-18 16:35:12
대상 스위트: all

✅ Auth: 2개 통과
✅ RCM: 2개 통과
✅ Evaluation: 2개 통과
✅ Interview: 1개 통과

총계: 7개 테스트, 7개 통과 (100%)
스크린샷: test/screenshots/ (15개)
```

---

## 🔄 기존 파일에서 마이그레이션

### Before (기존 - 복잡함 ❌)
```bash
python test/auth_test.py
python test/link1_test.py
python test/link5_test.py
python test/link6_test.py
# ... 23개 파일
```

### After (통합 - 간단함 ✅)
```bash
python test/test_units_integrated.py
```

---

## 📚 추가 문서

| 문서 | 내용 |
|------|------|
| [QUICKSTART_E2E.md](QUICKSTART_E2E.md) | 5분 빠른 시작 가이드 |
| [PLAYWRIGHT_GUIDE.md](PLAYWRIGHT_GUIDE.md) | Playwright 상세 가이드 |
| [E2E_TEST_SCENARIOS.md](E2E_TEST_SCENARIOS.md) | 전체 시나리오 목록 |

---

## 🆚 단위 테스트 vs E2E 테스트

| 구분 | 단위 테스트 | E2E 테스트 |
|-----|-----------|-----------|
| **속도** | ⚡ 빠름 (1~2분) | 🐢 느림 (10~15분) |
| **브라우저** | ❌ 불필요 | ✅ Chromium |
| **검증 범위** | 함수/API | 전체 플로우 |
| **실행 시점** | 개발 중, 커밋 전 | PR, 배포 전 |
| **CI/CD** | 모든 커밋 | PR/배포 시 |

**권장**: 둘 다 사용! (70% 단위 + 30% E2E)

---

## 🎉 요약

### ✅ 달성한 것

1. **파일 정리**: 23개 → 4개 (90% 감소)
2. **통합 구조**: 모든 테스트를 2개 파일로 통합
3. **파라미터화**: `--module`, `--suite`로 선택 실행
4. **중복 제거**: 공통 코드 통합
5. **유지보수성**: 훨씬 간편해짐

### 📦 백업

기존 파일들은 `legacy_backup/` 폴더에 안전하게 백업되어 있습니다.

---

## 🚀 지금 바로 시작!

```bash
# 단위 테스트
python test/test_units_integrated.py

# E2E 테스트
python snowball.py &
python test/test_e2e_integrated.py --headless
```

---

**버전**: 2.0 (통합)
**작성일**: 2026-01-18
**담당**: Snowball 개발팀

Happy Testing! 🎉
