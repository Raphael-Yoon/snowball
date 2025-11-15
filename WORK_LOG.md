# Snowball 프로젝트 작업 로그

## 2025-11-14 - MySQL/SQLite 호환성 개선 및 파일 정리

### 1. DatabaseConnection 래퍼 클래스 개선

#### 1.1 문제점
- PythonAnywhere 운영 서버(MySQL)에서 `TypeError: not enough arguments for format string` 발생
- 원인: `get_rcm_details()` 함수의 ORDER BY 절에 LIKE 패턴 6개 추가했으나 params에 포함 안 됨

#### 1.2 해결 방법
**파일**: `auth.py`

**수정된 함수들**:
1. `get_rcm_details()` (445-487줄)
2. `get_key_controls()` (489-566줄)

**변경 내용**:
```python
# ORDER BY LIKE 패턴을 params에 추가
order_params = ['PWC%', 'APD%', 'PC%', 'CO%', 'PD%', 'ST%']
params.extend(order_params)
params = tuple(params)
```

#### 1.3 fetchone() 안전성 개선
- **문제**: MySQL에서 `COUNT(*)` 반환값이 딕셔너리 형태 → 인덱스 접근 불가
- **해결**: `_get_first_value()` 헬퍼 함수 추가
  - 딕셔너리: 첫 번째 값 추출
  - 튜플/리스트: `row[0]` 접근
  - None 또는 에러: None 반환

**수정된 함수들**:
- `get_activity_log_count()` (271-278줄)
- `generate_unique_filename()` (322-363줄)
- `count_design_evaluations()` (1224-1231줄)
- `count_operation_evaluations()` (1233-1256줄)
- `count_completed_operation_evaluations()` (1258-1266줄)

### 2. MySQL 연결 안정성 개선

#### 2.1 PyMySQL 임포트 에러 처리
**파일**: `auth.py` (135-160줄)

```python
if USE_MYSQL:
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError(
            "MySQL 연결을 사용하려면 PyMySQL 패키지가 필요합니다. "
            "로컬에서 SQLite만 사용할 경우 USE_MYSQL 환경 변수를 false로 설정하세요."
        ) from exc
```

**효과**:
- 로컬 개발 시 PyMySQL 미설치 상태에서도 명확한 에러 메시지
- 운영 서버와 로컬 환경 구분 명확화

### 3. 뷰 동기화 스크립트 개선

#### 3.1 sync_views_to_mysql.py
**파일**: `migrations/sync_views_to_mysql.py`

**기능**:
- SQLite의 모든 뷰(VIEW)를 MySQL로 마이그레이션
- 뷰 정의 SQL을 MySQL 문법으로 자동 변환
- Dry run 모드 지원

**사용법**:
```bash
python migrations/sync_views_to_mysql.py          # Dry run
python migrations/sync_views_to_mysql.py --apply  # 실제 적용
```

**변환 로직**:
- `CREATE VIEW` → `CREATE OR REPLACE VIEW`
- SQLite와 MySQL 대부분 호환 (COALESCE, UPPER, LEFT JOIN 등)

### 4. 파일 정리

#### 4.1 삭제된 파일
**SQL 파일** (불필요):
- `migrations/add_evaluation_session_to_internal_assessment.sql`
- `migrations/create_mysql_view.sql`

**마크다운 파일** (WORK_LOG.md 제외 모두 삭제):
- `README.md`
- `migrations/README.md`
- `migrations/README_MYSQL.md`
- `tests/HOW_TO_RUN_TESTS.md`
- `tests/README_NAVIGATION_TEST.md`
- `tests/BUTTON_TEST_GUIDE.md`
- `tests/README.md`
- `tests/NAVIGATION_TEST_SUMMARY.md`

#### 4.2 유지된 파일
- `WORK_LOG.md` (이 파일) - 모든 작업 기록 통합

### 5. 환경 설정

#### 5.1 .env 파일
```
# 로컬 개발
USE_MYSQL=false

# PythonAnywhere 운영
USE_MYSQL=true
MYSQL_HOST=itap.mysql.pythonanywhere-services.com
MYSQL_USER=itap
MYSQL_PASSWORD=qpspelrxm1!
MYSQL_DATABASE=itap$snowball
MYSQL_PORT=3306
```

### 6. 주요 개선 사항

1. ✅ **MySQL 호환성**: ORDER BY LIKE 패턴 매개변수화 완료
2. ✅ **타입 안전성**: fetchone() 결과 안전하게 처리
3. ✅ **에러 처리**: PyMySQL 임포트 에러 명확한 메시지
4. ✅ **뷰 동기화**: SQLite 뷰를 MySQL로 자동 마이그레이션
5. ✅ **파일 정리**: 불필요한 문서 제거, WORK_LOG.md로 통합

### 7. 배포 체크리스트

**PythonAnywhere 배포 시**:
1. 파일 업로드:
   - `auth.py` (DatabaseConnection 개선)
   - `migrations/sync_views_to_mysql.py` (뷰 동기화)

2. Bash 콘솔에서 뷰 동기화:
```bash
cd ~/snowball
python migrations/sync_views_to_mysql.py --apply
```

3. Web App Reload

### 8. 문제 해결 로그

**에러**: `TypeError: not enough arguments for format string`
- **위치**: `auth.py:591` (`get_rcm_details()`)
- **원인**: ORDER BY LIKE %s 6개 추가했으나 params에 미포함
- **해결**: `order_params` 리스트를 params에 extend

**에러**: `'DictCursor' object is not subscriptable`
- **위치**: `auth.py:275` (`get_activity_log_count()`)
- **원인**: MySQL DictCursor는 `row[0]` 접근 불가
- **해결**: `_get_first_value()` 헬퍼 함수로 안전한 값 추출

---

## 2025-11-13 - 설계평가 엑셀 다운로드 기능 및 UI 개선

### 1. 설계평가 엑셀 다운로드 기능 구현

#### 1.1 기능 개요
- **파일**: `snowball_link6.py` (1575-1745줄)
- Design_Template.xlsx 템플릿 기반 다운로드 기능
- 평가된 각 통제별로 별도 시트 생성

#### 1.2 구현 내용
- **템플릿 시트 활용**: `paper_templates/Design_Template.xlsx`의 Template 시트를 복사
- **시트명**: 통제번호(control_code)로 설정
- **데이터 매핑**:
  - C2: 회사명 (company_name)
  - C4: 작성자 (user_name)
  - C7-C10: 통제번호, 통제명, 주기, 구분
  - C11: 테스트 절차 (control_description)
  - C12: 검토 결과 (evaluation_rationale)
  - C13~: 증빙 이미지
  - C14+: 결론 (이미지 개수에 따라 동적 위치)

#### 1.3 자동 행 높이 조정
- 텍스트 줄바꿈 개수를 기반으로 행 높이 자동 계산
- C11(테스트 절차), C12(검토 결과) 행 높이 자동 조정
- 공식: `15 + (줄수 × 15)`, 최대 300 포인트

#### 1.4 이미지 삽입 기능
- **라이브러리**: Pillow (Python 3.14용 설치 완료)
- **위치**: C13부터 순차적으로 삽입
- **이미지 크기**: 너비 300px로 자동 조정
- **결론 위치**: 이미지 개수에 따라 동적 조정
- **오류 처리**: 이미지 삽입 실패 시 파일명으로 대체

#### 1.5 한글 파일명 지원
- RFC 5987 표준 사용: `filename*=UTF-8''...`
- Content-Disposition 헤더 직접 설정
- 파일명: `{평가세션명}.xlsx` (예: FY25_내부평가.xlsx)

### 2. UI 버그 수정

#### 2.1 설계평가 완료 버튼 표시 문제
- **문제**: 평가 완료 후 버튼이 "조회"로 변경되지 않음
- **원인**:
  1. 66개의 불필요한 fetch 로그 요청으로 인한 브라우저 과부하
  2. API가 중복 호출됨 (`loadExistingEvaluationData` + `loadExistingEvaluations`)
  3. 버튼 초기 HTML의 고정된 height: 24px
- **해결**:
  - fetch 로그를 console.log로 교체
  - 중복 API 호출 제거
  - 버튼 높이를 auto로 변경, white-space: nowrap 추가
  - 초기 HTML에 텍스트 추가 ("평가")

### 3. 데이터베이스 마이그레이션

#### 3.1 RCM 테이블에 control_category 추가
- **파일**: `migrations/versions/012_add_control_category_to_rcm.py`
- sb_rcm 테이블에 control_category 컬럼 추가
- 기존 RCM 데이터에 자동 카테고리 설정:
  - RCM명 기반 자동 분류 (ITGC, ELC, TLC 키워드)
  - detail의 control_category 다수결로 결정

#### 3.2 스키마 마이그레이션 도구 생성
- **파일**: `sync_sqlite_to_mysql.py` (신규)
- SQLite 스키마를 MySQL로 동기화 (데이터는 제외)
- **기능**:
  - 새 테이블 감지 및 생성
  - 새 컬럼 감지 및 추가
  - 외래키 관계 보존
  - Dry run 모드 지원 (--apply 옵션)
- **사용법**:
  ```bash
  python sync_sqlite_to_mysql.py          # Dry run
  python sync_sqlite_to_mysql.py --apply  # 실제 적용
  ```

### 4. 기술적 개선사항

#### 4.1 Python 환경 관리
- Python 3.14 환경에 Pillow 설치
- 명령어: `py -3.14 -m pip install Pillow`

#### 4.2 파일 네이밍 컨벤션
- 기존: `sync_mysql_to_sqlite.py` (MySQL → SQLite)
- 신규: `sync_sqlite_to_mysql.py` (SQLite → MySQL)
- 일관된 네이밍으로 방향성 명확화

### 5. 파일 변경 이력

#### 수정된 파일:
- `snowball_link6.py`: 다운로드 라우트 추가 (1575-1745줄)
- `templates/link6_design_rcm_detail.jsp`: 버튼 UI 수정 (166-173줄, 1410-1558줄)

#### 신규 파일:
- `sync_sqlite_to_mysql.py`: 스키마 마이그레이션 도구
- `migrations/versions/012_add_control_category_to_rcm.py`: RCM 카테고리 추가 마이그레이션

### 6. 미해결 이슈
- 설계평가 완료 버튼 표시 문제 (디버깅 중)
  - API 데이터는 정상
  - JavaScript updateEvaluationUI 함수 실행 확인됨
  - 원인 파악 진행 중

---

## 2024-11-02 - 설계평가/운영평가 페이지 개선 및 테스트 추가

### 1. 데이터베이스 수정

#### 1.1 sb_user_rcm 테이블 수정
- **문제**: 권한 제거 시 `last_updated` 컬럼 없음 오류 발생
- **해결**: `sb_user_rcm` 테이블에 `last_updated` 컬럼 추가
- **파일**: `migrations/versions/008_add_last_updated_to_user_rcm.py`

#### 1.2 sb_rcm_detail_v 뷰 수정
- **문제**: 통제주기/통제유형이 표시되지 않음
- **해결**: View에 `control_category` 컬럼 추가, `COALESCE`로 데이터 포맷 불일치 대응
- **파일**: `migrations/versions/009_add_control_category_to_view.py`

### 2. 설계평가 페이지 개선 (Link6)

#### 2.1 평가 유형별 동적 타이틀 표시
- `evaluation_type` 파라미터로 "ITGC/ELC/TLC 설계평가" 동적 표시
- **파일**: `snowball_link6.py`, `templates/link6_design_rcm_detail.jsp`

#### 2.2 통제 카테고리 필터 UI 제거
- 하단 필터 버튼 제거, `evaluation_type`으로 자동 필터링
- **파일**: `snowball_link6.py` (91-93줄)

#### 2.3 기준통제 매핑 기능 제한
- ITGC에서만 기준통제 매핑 컬럼 표시
- **파일**: `templates/link6_design_rcm_detail.jsp` (144-181줄)

#### 2.4 통제주기/통제유형 필드명 수정
- 템플릿 필드명 수정: `control_frequency_name` → `control_frequency`

### 3. 운영평가 페이지 전면 개편 (Link7)

#### 3.1 페이지 구조 변경
**새 구조**:
1. 보유 RCM 목록 (간단한 테이블)
2. 설계평가 현황 (진행중 + 완료)
3. 운영평가 현황 (진행중 + 완료 통합)

#### 3.2 통합 템플릿 생성
- **파일**: `templates/link7_operation_evaluation_unified.jsp` (신규)
- ITGC, ELC, TLC 하나의 템플릿으로 통합
- `evaluation_type` 변수로 동적 표시

#### 3.3 설계평가 현황 개선
- 진행 중인 설계평가 표시 추가
- **함수**: `get_all_design_evaluation_sessions()` 추가 (auth.py)
- **표시**:
  - 진행 중: 세션명, 시작일, 진행률, 상태
  - 완료됨: 세션명, 완료일, 평가 대상 통제, 운영평가 가능 여부

#### 3.4 진행률 표시 개선
- 프로그레스 바 + "13/20" 형식으로 개수 표시
- **파일**: `templates/link7_operation_evaluation_unified.jsp` (142-151줄)

#### 3.5 라우트 수정
- ITGC: `/operation-evaluation`
- ELC: `/elc/operation-evaluation`
- TLC: `/tlc/operation-evaluation`
- 모두 통합 템플릿 사용

### 4. 네비게이션 플로우 테스트 추가

#### 4.1 테스트 파일 생성
- **파일**: `tests/test_navigation_flow.py` (16KB, 19개 테스트)
- RCM 관리 ↔ 설계평가 ↔ 운영평가 간 전환 테스트
- ITGC, ELC, TLC 모든 카테고리 커버
- 세션 관리, 에러 처리, 권한 검증 포함

#### 4.2 테스트 문서 작성
- `tests/README_NAVIGATION_TEST.md` - 상세 가이드
- `tests/NAVIGATION_TEST_SUMMARY.md` - 테스트 요약
- `tests/HOW_TO_RUN_TESTS.md` - 빠른 시작

### 5. 파일 정리

#### 삭제된 파일
- 임시 테스트 파일 4개
- 템플릿 백업 파일 3개

### 주요 변경 파일

#### Python
- `snowball_link6.py`, `snowball_link7.py`, `auth.py`
- `migrations/versions/008_*.py`, `009_*.py` (신규)

#### 템플릿
- `templates/link6_design_rcm_detail.jsp`
- `templates/link7_operation_evaluation_unified.jsp` (신규)
- `templates/link7_elc_operation_evaluation.jsp`
- `templates/link7_tlc_operation_evaluation.jsp`

#### 테스트 (신규)
- `tests/test_navigation_flow.py`
- `tests/README_NAVIGATION_TEST.md`
- `tests/NAVIGATION_TEST_SUMMARY.md`
- `tests/HOW_TO_RUN_TESTS.md`

### 테스트 실행

```bash
pip install pytest pytest-mock
python -m pytest tests/test_navigation_flow.py -v
```

### 주요 개선 사항

1. ✅ 데이터베이스 안정성 (컬럼 누락 해결)
2. ✅ 사용자 경험 (명확한 타이틀, 불필요 UI 제거)
3. ✅ 코드 품질 (템플릿 통합, 중복 제거)
4. ✅ 정보 가시성 (진행 중 평가 표시)
5. ✅ 테스트 커버리지 (19개 네비게이션 테스트)

### 참고

- 템플릿 변경 후 Ctrl+Shift+R로 캐시 새로고침
- 코드 변경 후 Flask 서버 재시작 필수
- DB 변경 후 `python migrate.py upgrade` 실행

---

## 2024-11-05 - UI 일관성 개선: 버튼 크기 및 레이아웃 통일

### 1. 메인 페이지 레이아웃 통일 (index.jsp)

#### 1.1 Private 섹션 레이아웃 정렬
- **문제**: 로그인 상태와 로그아웃 상태의 Private 메뉴 배치가 상이함
- **해결**: 로그아웃 상태 레이아웃을 로그인 상태와 동일하게 2+3 카드 구조로 변경
- **파일**: `templates/index.jsp` (288-381줄)
- **구조**:
  - 상단 2개: RCM + 내부평가 (offset-lg-3로 중앙 정렬)
  - 하단 3개: ELC + TLC + ITGC

### 2. 모달 버튼 크기 통일

#### 2.1 설계평가 시작 모달 버튼
- **문제**: "취소" 버튼 높이가 너무 큼
- **해결**: 모든 모달 버튼에 `padding: 0.25rem 0.5rem; font-size: 0.875rem;` 추가
- **수정 파일**:
  - `templates/link6_design_evaluation.jsp` (377-380줄) - ITGC
  - `templates/link6_elc_design_evaluation.jsp` (398-401줄) - ELC
  - `templates/link6_tlc_design_evaluation.jsp` (373-376줄) - TLC

#### 2.2 평가 상세 모달 버튼
- **파일**: `templates/link6_design_rcm_detail.jsp`
- **수정 위치**:
  - 평가 모달 (340-345줄): "취소", "평가 저장" 버튼
  - 파일 업로드 모달 (419-424줄): "취소", "업로드 및 적용" 버튼

#### 2.3 운영평가 및 관리자 모달 버튼
- `templates/link7_detail.jsp` (434-436줄): 자동통제 확인 모달
- `templates/admin_rcm_users.jsp` (199-200줄): RCM 권한 모달
- `templates/admin_users.jsp`:
  - 사용자 추가 모달 (164-165줄)
  - 사용자 수정 모달 (215-216줄)
  - 기한 연장 모달 (239-241줄)
  - 사용자 삭제 모달 (261-263줄)

### 3. 설계평가 페이지 UI 개선

#### 3.1 "평가 필요" 텍스트 제거
- **문제**: 평가되지 않은 항목에 "평가 필요" 표시
- **해결**: 공란(빈 문자열)으로 변경
- **파일**: `templates/link6_design_rcm_detail.jsp`
- **수정 위치**:
  - 176줄: 초기 HTML 템플릿
  - 1456줄: JavaScript 평가 결과 업데이트
  - 2052줄: UI 초기화 함수

### 4. 버튼 높이 일관성 개선 (핵심 수정)

#### 4.1 문제 분석
- **사용자 피드백**: "버튼들의 높이가 달라"
- **원인**: padding과 font-size만 조정했으나, 명시적인 height 설정 누락
- **영향**: "평가완료", "평가", "조회" 버튼들이 서로 다른 높이로 표시됨

#### 4.2 해결 방법
- **파일**: `templates/link6_design_rcm_detail.jsp`
- **수정 내용**: 모든 동적 버튼에 고정 높이 24px 적용

**수정 위치 및 코드**:

1. **초기 버튼 템플릿** (170줄):
```html
style="padding: 0.2rem 0.35rem; font-size: 0.75rem; height: 24px;"
```

2. **"평가완료" 버튼** (1454줄):
```javascript
buttonElement.style.padding = '0.2rem 0.35rem';
buttonElement.style.fontSize = '0.75rem';
buttonElement.style.height = '24px';
buttonElement.style.minWidth = '70px';
```

3. **"조회" 버튼** (1471줄):
```javascript
buttonElement.style.padding = '0.2rem 0.35rem';
buttonElement.style.fontSize = '0.75rem';
buttonElement.style.height = '24px';
buttonElement.style.minWidth = '70px';
```

4. **"평가" 버튼** (1484줄):
```javascript
buttonElement.style.padding = '0.2rem 0.35rem';
buttonElement.style.fontSize = '0.75rem';
buttonElement.style.height = '24px';
```

### 주요 변경 파일 요약

#### 템플릿 파일 (8개)
1. `templates/index.jsp` - Private 섹션 레이아웃
2. `templates/link6_design_evaluation.jsp` - ITGC 모달 버튼
3. `templates/link6_elc_design_evaluation.jsp` - ELC 모달 버튼
4. `templates/link6_tlc_design_evaluation.jsp` - TLC 모달 버튼
5. `templates/link6_design_rcm_detail.jsp` - 버튼 높이 통일 (핵심)
6. `templates/link7_detail.jsp` - 운영평가 모달
7. `templates/admin_rcm_users.jsp` - RCM 권한 관리
8. `templates/admin_users.jsp` - 사용자 관리

### 기술적 개선 사항

1. ✅ **높이 일관성**: 모든 평가 버튼 24px 고정 높이 적용
2. ✅ **모달 버튼 통일**: padding 0.25rem 0.5rem, font-size 0.875rem
3. ✅ **레이아웃 정렬**: 로그인/로그아웃 상태 Private 섹션 동일화
4. ✅ **시각적 정돈**: "평가 필요" 제거로 깔끔한 UI

### 교훈

- **높이 vs 너비**: 사용자가 "크기가 다르다"고 할 때는 **높이(height)**를 먼저 확인할 것
- **명시적 스타일링**: padding/font-size만으로는 불충분, **명시적인 height 설정** 필요
- **일관성 검증**: 동적으로 생성되는 모든 버튼 상태를 체크할 것

### 확인 방법

1. Flask 서버 재시작
2. 브라우저에서 **Ctrl+Shift+R** (하드 리프레시)
3. `/design-evaluation/rcm` 페이지에서 버튼 높이 확인

---

## 2025-01-07 - VSCode 디버그 설정 및 Dashboard 이미지 적용

### 1. VSCode/Cursor 디버그 설정 개선

#### 1.1 작업 디렉토리 설정
- **문제**: F5로 Flask 서버 실행 시 작업 디렉토리가 상위 폴더(Pythons)로 설정됨
- **해결**: `launch.json`에 `cwd: "${fileDirname}"` 추가
- **파일**: `.vscode/launch.json`
- **효과**: `snowball.py` 실행 시 자동으로 `snowball` 폴더가 작업 디렉토리로 설정됨

**변경 내용**:
```json
{
    "name": "Python Debugger: Current File",
    "type": "debugpy",
    "request": "launch",
    "program": "${file}",
    "console": "integratedTerminal",
    "cwd": "${fileDirname}"  // 추가
}
```

### 2. Dashboard 이미지 적용

#### 2.1 메인 페이지 이미지 교체
- **대상**: index.jsp의 Dashboard 카드
- **변경**: `img/review.jpg` → `img/dashboard.jpg`
- **파일**: `templates/index.jsp` (129줄, 316줄)
- **적용 위치**:
  - 로그인 상태 Private 섹션
  - 비로그인 상태 Private 미리보기 섹션

### 3. 미사용 이미지 분석 및 정리

#### 3.1 중복/대체된 이미지 정리
- **review.jpg** ← dashboard.jpg로 대체됨 (삭제 권장)
- contact_us.png (jpg 버전 사용 중)
- rcm_inquiry.png (jpg 버전 사용 중)
- interview.png (jpg 버전 사용 중)
- operational_review.png (jpg 버전 사용 중)

### 주요 변경 파일

#### 설정 파일
- `.vscode/launch.json` - 작업 디렉토리 설정 추가

#### 템플릿 파일
- `templates/index.jsp` - Dashboard 이미지 교체 (2개 위치)

### 개선 사항

1. ✅ **개발 환경**: F5 디버그 실행 시 올바른 작업 디렉토리 설정
2. ✅ **UI 일관성**: Dashboard 전용 이미지 적용
3. ✅ **리소스 관리**: 중복 이미지 파악 및 정리 대상 선정

### 참고

- 작업 디렉토리 확인: Flask 실행 시 `templates/`, `static/` 폴더 접근 가능 여부 확인
- 이미지 교체 후 브라우저 캐시 클리어 권장 (Ctrl+Shift+R)
- 미사용 이미지는 백업 후 삭제 권장

---

## 2025-01-07 - MySQL 마이그레이션 및 백업 스크립트 구현

### 1. SQLite → MySQL 마이그레이션 스크립트

#### 1.1 migrate_to_mysql.py 개선
- **목적**: 로컬 SQLite DB를 PythonAnywhere MySQL로 마이그레이션
- **파일**: `migrate_to_mysql.py`

**주요 기능**:
1. **DROP & RECREATE 모드**: 기존 테이블 삭제 후 재생성
2. **날짜/시간 변환**: SQLite TIMESTAMP → MySQL DATETIME 자동 변환
3. **배치 처리**: 1000개 단위 배치 커밋으로 성능 최적화
4. **에러 핸들링**: 개별 행 에러 발생 시 건너뛰고 계속 진행

**추가된 함수**:
- `convert_datetime_value()`: 날짜/시간 문자열을 MySQL 호환 형식으로 변환
- `create_mysql_table()`: drop_if_exists 옵션 추가

**실행 방법**:
```bash
python migrate_to_mysql.py
# "YES" 입력하여 확인
```

**해결된 문제**:
- PRIMARY KEY 중복 오류 → DROP TABLE로 해결
- 날짜 형식 변환 오류 → convert_datetime_value() 함수 추가
- 배치 처리 중 에러 → 개별 행 에러 무시하고 계속 진행

### 2. MySQL → SQLite 백업 스크립트

#### 2.1 backup_mysql_to_sqlite.py 신규 작성
- **목적**: 프로덕션 MySQL 데이터를 로컬 SQLite로 백업
- **파일**: `backup_mysql_to_sqlite.py` (신규)
- **배치 스케줄**: cron 또는 작업 스케줄러로 주기적 실행 가능

**주요 기능**:
1. **자동 백업**: 기존 SQLite DB를 타임스탬프와 함께 백업
   - 백업 위치: `backups/snowball_YYYYMMDD_HHMMSS.db`
2. **백업 관리**: 최근 10개 백업만 유지, 오래된 파일 자동 삭제
3. **스키마 복제**: MySQL 테이블 구조를 SQLite로 변환
4. **인덱스 복제**: MySQL 인덱스를 SQLite에 재생성
5. **배치 처리**: 1000개 단위로 데이터 복사
6. **Exit Code**: 성공 시 0, 실패 시 1 반환 (스케줄러 모니터링용)

**타입 변환 매핑**:
```python
MySQL          → SQLite
INT/BIGINT     → INTEGER
VARCHAR/TEXT   → TEXT
DOUBLE/FLOAT   → REAL
DATETIME       → TIMESTAMP
BLOB           → BLOB
TINYINT(1)     → INTEGER (boolean)
```

**실행 방법**:
```bash
# 수동 실행
python backup_mysql_to_sqlite.py

# cron 설정 (매일 새벽 3시)
0 3 * * * cd /path/to/snowball && python3 backup_mysql_to_sqlite.py >> backups/backup.log 2>&1
```

**백업 파일 구조**:
```
snowball/
├── snowball.db                    # 현재 DB
└── backups/
    ├── snowball_20250107_030000.db
    ├── snowball_20250106_030000.db
    └── ... (최근 10개 유지)
```

### 3. 주요 변경 파일

#### Python 스크립트
1. **migrate_to_mysql.py** (수정)
   - 날짜/시간 변환 로직 추가 (158-193줄)
   - DROP TABLE 옵션 추가 (81-88줄)
   - 단순화된 확인 프로세스 (281-294줄)

2. **backup_mysql_to_sqlite.py** (신규)
   - MySQL → SQLite 백업 스크립트
   - 자동 백업 관리 기능
   - 배치 스케줄러 호환

### 4. 워크플로우

#### 개발 → 프로덕션 (SQLite → MySQL)
```bash
1. 로컬에서 개발 (SQLite)
2. python migrate_to_mysql.py 실행
3. PythonAnywhere MySQL에 데이터 업로드
```

#### 프로덕션 → 개발 (MySQL → SQLite)
```bash
1. python backup_mysql_to_sqlite.py 실행
2. MySQL 데이터를 로컬 SQLite로 백업
3. 로컬에서 개발 계속
```

### 5. 기술적 개선 사항

1. ✅ **양방향 마이그레이션**: SQLite ↔ MySQL 모두 지원
2. ✅ **데이터 안전성**: 백업 자동 생성 및 관리
3. ✅ **배치 스케줄**: cron/작업 스케줄러 호환
4. ✅ **에러 복구**: 실패 시에도 기존 백업 유지
5. ✅ **성능 최적화**: 배치 처리로 대용량 데이터 처리

### 6. 주의사항

- **migrate_to_mysql.py**:
  - MySQL 데이터 전체 삭제 후 재생성
  - .env 파일에 MYSQL_PASSWORD 필수
  - "YES" 정확히 입력해야 실행

- **backup_mysql_to_sqlite.py**:
  - 프로덕션 MySQL 접속 권한 필요
  - backups/ 디렉토리 자동 생성
  - 디스크 용량 확인 필요 (DB 크기에 따라)

### 7. 테스트 계획

로컬에서는 MySQL이 없어 서버에서 테스트 필요:

1. **migrate_to_mysql.py** 테스트:
   - PythonAnywhere 콘솔에서 실행
   - 테이블 생성 확인
   - 데이터 카운트 확인

2. **backup_mysql_to_sqlite.py** 테스트:
   - PythonAnywhere 콘솔에서 실행
   - backups/ 디렉토리 생성 확인
   - 백업 파일 다운로드 후 로컬에서 검증

### 8. 다음 단계

1. 서버에 스크립트 업로드
2. migrate_to_mysql.py 실행하여 초기 데이터 마이그레이션
3. sync_mysql_to_sqlite.py 테스트 (파일명 변경)
4. cron 작업 설정 (옵션)

### 9. 파일 정리 및 최종 결정

**삭제된 파일**:
- 중복 이미지 8개 (~14MB)
- 백업 Excel 파일 1개
- Python 캐시 파일 다수

**파일명 변경**:
- `backup_mysql_to_sqlite.py` → `sync_mysql_to_sqlite.py`

**운영 방침 확정**:
- ✅ **운영 서버**: MySQL 데이터베이스 사용
- ✅ **로컬 개발**: SQLite 파일 사용
- ✅ **데이터 동기화**: 양방향 마이그레이션 스크립트 활용

---

## 2025-01-08 - ELC 운영평가 모달 UI/UX 개선

### 1. 개요
- **목적**: ELC 운영평가 모달의 사용성 개선 및 전체 결론 로직 수정
- **대상 파일**: `templates/link7_detail.jsp`
- **작업 시작**: 이전 세션에서 계속됨

### 2. 주요 변경 사항

#### 2.1 "결론" 컬럼 제거
- **위치**: 표본별 테스트 결과 테이블
- **변경 내용**:
  - 테이블 헤더에서 "결론" 컬럼 제거
  - JavaScript에서 결론 배지 생성 코드 삭제
  - `updateSampleConclusion()` 함수 완전 제거
  - `handleSampleResultChange()` 함수 간소화
  - Mitigation 행의 colspan 4→3으로 조정
- **수정 라인**: 315-320, 1290-1299, 1307, 1343
- **이유**: 표본별 결론은 불필요하고, 전체 결론만 표시하면 충분

#### 2.2 모달 너비 조정
- **변경 과정**:
  1. 1200px → 70% (반응형)
  2. 70% → 840px (고정, 70% of 1200px)
  3. 840px → **800px** (최종)
- **수정 라인**: 240
- **이유**: 사용자가 고정 너비를 선호, 800px가 적당한 크기

#### 2.3 표본 크기 필드 조정
- **필드 너비**: col-md-6 → col-md-3 (절반 크기)
- **정렬**: `text-end` 클래스 추가 (우측 정렬)
- **수정 라인**: 300, 302
- **이유**: 숫자 입력 필드는 작아도 되고 우측 정렬이 자연스러움

#### 2.4 권장 표본수 안내 텍스트 개선
- **문제**: col-md-3 안에 있어서 텍스트가 짧게 잘림
- **해결**:
  - 안내 텍스트를 별도 col-md-9 영역으로 분리
  - `d-flex align-items-end` 클래스로 하단 정렬
- **수정 라인**: 304-308
- **결과**: 안내 텍스트 전체가 보이고 입력 필드 하단에 자연스럽게 정렬

#### 2.5 전체 결론 로직 수정 ⭐
- **문제**: `rows.forEach((row, index)` 루프가 모든 `<tr>` 요소(mitigation 행 포함)를 카운트하여 잘못된 sample numbering 발생
- **해결**:
  - `rows.forEach()` 대신 `for (let i = 1; i <= sampleSize; i++)` 루프 사용
  - `sample_size` 입력값을 기준으로 정확한 샘플 개수만큼 반복
  - 각 샘플의 ID로 직접 요소 조회
- **로직**:
  - 경감요소 없는 Exception 1건이라도 있으면 → "Ineffective"
  - 모든 Exception에 경감요소가 있으면 → "Effective"
  - Exception이 없으면 → "Effective"
- **수정 라인**: 1368-1423
- **추가 개선**: 경감요소 입력 시 실시간 업데이트 (`oninput="updateOverallConclusion()"` 추가)
- **수정 라인**: 1314, 1351

#### 2.6 평가결과 텍스트 변경
- **변경**: "Exception" → "Ineffective" (미비)
- **위치**: 전체 결론 표시 (`updateOverallConclusion()` 함수)
- **수정 라인**: 1408
- **유지**: "Effective" (적정)
- **참고**: 목록 페이지의 "Exception" 표시는 사용자 요청으로 원복

#### 2.7 표본별 테스트 결과 테이블 컬럼 너비 조정
- **변경 과정**:
  1. 표본 #: 10%, 증빙 내용: 75%, 결과: 15% (초기)
  2. 표본 #: 10%, 증빙 내용: 65%, 결과: 25% (1차 수정)
  3. 표본 #: 10%, 증빙 내용: 70%, 결과: 20% (최종)
- **수정 라인**: 319-321
- **이유**: "No Exception" 텍스트가 잘리지 않도록 결과 컬럼 확대

### 3. 기술적 세부사항

#### 3.1 JavaScript 함수 변경

**updateOverallConclusion() - Before:**
```javascript
const rows = tbody.querySelectorAll('tr');
rows.forEach((row, index) => {
    const sampleNumber = index + 1;  // ❌ mitigation 행도 카운트됨
    const resultSelect = document.getElementById(`sample-result-${sampleNumber}`);
    // ...
});
```

**updateOverallConclusion() - After:**
```javascript
const sampleSize = parseInt(document.getElementById('sample_size').value) || 0;
for (let i = 1; i <= sampleSize; i++) {  // ✅ 정확한 샘플 개수만 반복
    const resultSelect = document.getElementById(`sample-result-${i}`);
    const mitigationTextarea = document.getElementById(`sample-mitigation-${i}`);
    // ...
}
```

#### 3.2 실시간 업데이트 구현
- Mitigation 입력 필드에 `oninput` 이벤트 핸들러 추가
- 사용자가 경감요소를 입력하면 즉시 전체 결론이 업데이트됨
- UX 개선: 별도 버튼 클릭 없이 자동 반영

#### 3.3 Bootstrap Grid 활용
- 표본 크기 입력: `col-md-3`
- 권장 표본수 안내: `col-md-9 d-flex align-items-end`
- 반응형 레이아웃 유지하면서 가독성 향상

### 4. 테스트 체크리스트

- [x] 표본 크기 입력 시 라인 생성
- [x] Exception 선택 시 경감요소 입력란 표시
- [x] 경감요소 입력 시 실시간 전체 결론 업데이트
- [x] 경감요소 없는 Exception → Ineffective 표시
- [x] 모든 Exception에 경감요소 있음 → Effective 표시
- [x] No Exception만 있음 → Effective 표시
- [x] 권장 표본수 안내 텍스트 전체 표시
- [x] 표본 크기 필드 우측 정렬
- [x] 모달 너비 800px 적용
- [x] "No Exception" 텍스트가 잘리지 않음

### 5. 파일 변경 요약

**수정된 파일**: `templates/link7_detail.jsp`

**변경된 섹션**:
1. 모달 너비 설정 (line 240)
2. 표본 크기 입력 필드 (lines 300-309)
3. 표본별 테스트 결과 테이블 헤더 (lines 317-323)
4. 샘플 라인 생성 JavaScript (lines 1272-1320)
5. 샘플 결과 변경 핸들러 (lines 1330-1365)
6. 전체 결론 계산 함수 (lines 1368-1423)

**삭제된 함수**:
- `updateSampleConclusion()` (표본별 결론 업데이트 - 불필요)

### 6. 사용자 피드백 반영

1. ✅ "결론 컬럼 삭제" - 완료
2. ✅ "모달 너비 800px" - 완료
3. ✅ "표본 크기 필드 크기 조정" - 완료
4. ✅ "숫자 우측 정렬" - 완료
5. ✅ "전체 결론 로직 수정" - 완료
6. ✅ "권장 표본수 안내 개선" - 완료
7. ✅ "목록의 Exception 표시 유지" - 사용자 요청으로 원복
8. ✅ "결과 컬럼 너비 조정" - 20%로 최종 확정

### 7. 향후 개선 가능 사항

- 표본별 테스트 결과 자동 저장 기능
- 경감요소 템플릿/자동완성 기능
- 표본 크기별 권장값 자동 설정
- 평가 진행률 실시간 표시

---

## 2025-01-09 - 운영평가 모달 UI/UX 개선 및 버그 수정

### 1. 개요
- **목적**: 운영평가 모달의 사용성 개선 및 저장 로직 버그 수정
- **대상 파일**: `templates/link7_detail.jsp`, `gmail_schedule.py`
- **주요 이슈**:
  1. 데이터 미입력 시 "Effective" 표시 문제
  2. Exception 선택했는데 목록에서 "Effective" 표시 문제
  3. 예외사항 관련 필드 항상 표시 문제
  4. 표본 크기 변경 시 입력 데이터 손실 문제

### 2. 주요 변경 사항

#### 2.1 예외사항 관련 필드 조건부 표시 ⭐
- **문제**: "예외사항 세부내용"과 "개선계획" 필드가 항상 표시됨
- **해결**: Exception이 있을 때만 필드 표시
- **수정 위치**:
  - HTML: lines 345-353 (ID 추가 및 초기 숨김)
  - JavaScript: lines 1461-1480 (toggleExceptionFields 함수 추가)
- **동작**:
  - Exception 없음 → 필드 숨김 + 내용 초기화
  - Exception 있음 → 필드 표시

```javascript
function toggleExceptionFields(show) {
    const exceptionDetailsSection = document.getElementById('exception-details-section');
    const improvementPlanSection = document.getElementById('improvement-plan-section');

    if (exceptionDetailsSection) {
        exceptionDetailsSection.style.display = show ? 'block' : 'none';
    }
    if (improvementPlanSection) {
        improvementPlanSection.style.display = show ? 'block' : 'none';
    }

    // Exception이 없을 때는 필드 내용도 초기화
    if (!show) {
        document.getElementById('exception_details').value = '';
        document.getElementById('improvement_plan').value = '';
    }
}
```

#### 2.2 전체 결론 자동 계산 로직 개선 ⭐⭐
- **문제 1**: 아무 데이터도 입력하지 않았는데 "Effective" 표시
- **문제 2**: 증빙 내용 입력 시 실시간 업데이트 안 됨
- **해결**: 증빙 내용 입력 여부 확인 로직 추가
- **수정 위치**: lines 1372-1459

**결론 표시 규칙**:

| 상태 | 결론 배지 | 메시지 | 예외 필드 |
|------|----------|--------|----------|
| 표본 크기 = 0 | `-` (회색) | "표본별 결과를 입력하면 자동으로 계산됩니다" | 숨김 |
| 증빙 내용 미입력 | `-` (회색) | "증빙 내용을 입력해주세요 (N개 표본)" | 숨김 |
| 경감요소 없는 예외 | `Ineffective` (빨강) | "경감요소 없는 예외 N건 발견" | 표시 |
| 예외 없음 또는<br>모든 예외에 경감요소 | `Effective` (초록) | "No Exception: N건, 경감요소 있는 Exception: M건" | 조건부 표시 |

```javascript
// 증빙 내용이 입력되었는지 확인
let evidenceFilledCount = 0;
for (let i = 1; i <= sampleSize; i++) {
    const evidenceInput = document.getElementById(`sample-evidence-${i}`);
    if (evidenceInput && evidenceInput.value.trim().length > 0) {
        evidenceFilledCount++;
    }
}

// 증빙 내용이 하나도 없으면 결론 표시 안 함
if (evidenceFilledCount === 0) {
    conclusionSpan.textContent = '-';
    toggleExceptionFields(false);
    return;
}
```

#### 2.3 저장 시 결론 계산 버그 수정 ⭐⭐⭐
- **문제**: 표본별로 Exception을 선택했는데도 목록에서 "Effective"로 표시됨
- **원인**: 저장 함수가 표본별 결과를 무시하고 `exception_count` 필드만 확인
- **해결**: 표본별 결과를 집계하여 결론 자동 계산
- **수정 위치**: lines 1716-1767

**이전 로직 (잘못됨)**:
```javascript
// exception_count 필드 값으로만 판단
const exceptionCount = parseInt(formData.get('exception_count')) || 0;
finalConclusion = exceptionCount > 0 ? 'exception' : 'effective';
```

**수정된 로직 (올바름)**:
```javascript
// 표본 라인을 반복하면서 실제 결과 확인
let exceptionCount = 0;
let exceptionWithoutMitigationCount = 0;

for (let i = 1; i <= sampleSize; i++) {
    const result = resultEl.value || 'no_exception';
    const mitigation = mitigationEl ? mitigationEl.value || '' : '';

    if (result === 'exception') {
        exceptionCount++;
        // 경감요소 없는 Exception 카운트
        if (!mitigation.trim()) {
            exceptionWithoutMitigationCount++;
        }
    }
}

// 경감요소 없는 Exception이 하나라도 있으면 'exception'
const finalConclusion = exceptionWithoutMitigationCount > 0 ? 'exception' : 'effective';
```

#### 2.4 표본 크기 변경 시 데이터 보존 ⭐⭐
- **문제**: 표본 크기를 변경하면 기존에 입력한 증빙 내용이 삭제됨
- **해결**: 표본 라인 재생성 전에 현재 화면의 입력값을 먼저 수집
- **수정 위치**: lines 1250-1308

**데이터 우선순위**:
1. **1순위**: 현재 화면 입력값 (사용자가 지금 입력 중인 데이터)
2. **2순위**: DB 저장 데이터 (이전에 저장한 데이터)
3. **3순위**: 기본값 (빈 문자열 또는 'no_exception')

```javascript
// 기존 라인을 초기화하기 전에 현재 화면의 입력값을 먼저 수집
const currentInputData = [];
const existingRows = tbody.querySelectorAll('tr:not([id^="mitigation-row"])');
existingRows.forEach((row, index) => {
    const sampleNumber = index + 1;
    const evidenceEl = document.getElementById(`sample-evidence-${sampleNumber}`);
    const resultEl = document.getElementById(`sample-result-${sampleNumber}`);
    const mitigationEl = document.getElementById(`sample-mitigation-${sampleNumber}`);

    if (evidenceEl && resultEl) {
        currentInputData.push({
            sample_number: sampleNumber,
            evidence: evidenceEl.value || '',
            result: resultEl.value || 'no_exception',
            mitigation: mitigationEl ? (mitigationEl.value || '') : ''
        });
    }
});

// 이제 기존 라인 초기화
tbody.innerHTML = '';

// 우선순위에 따라 데이터 복원
const currentInput = currentInputData.find(s => s.sample_number === i);
const existingSample = existingSampleLines.find(s => s.sample_number === i);

const evidence = currentInput?.evidence || existingSample?.evidence || '';
const result = currentInput?.result || existingSample?.result || 'no_exception';
const mitigation = currentInput?.mitigation || existingSample?.mitigation || '';
```

#### 2.5 실시간 업데이트 추가
- **증빙 내용 입력 시**: `oninput="updateOverallConclusion()"` 추가 (line 1290)
- **결과 선택 시**: 기존 `onchange` 이벤트 유지
- **경감요소 입력 시**: 기존 `oninput` 이벤트 유지
- **효과**: 사용자가 데이터를 입력하는 즉시 결론이 자동으로 업데이트됨

### 3. Gmail 스케줄러 개선

#### 3.1 MySQL 동기화 결과 메일 전송
- **파일**: `gmail_schedule.py`
- **목적**: MySQL → SQLite 동기화 스크립트 실행 후 결과를 메일로 전송
- **기능**:
  1. `sync_mysql_to_sqlite.py` 스크립트 실행
  2. 실행 로그 수집 (stdout, stderr)
  3. 실행 결과를 이메일로 전송

**주요 함수**:
- `run_mysql_sync()`: subprocess로 스크립트 실행 및 결과 반환
- `send_sync_result_email()`: 동기화 결과를 포함한 이메일 생성 및 전송

**메일 내용 예시**:
```
MySQL to SQLite 동기화 실행 결과
실행 일시: 2025-01-09 14:30:00

============================================================
상태: 성공
반환 코드: 0
============================================================

[ 실행 로그 ]
============================================================
MySQL to SQLite Backup
Started at: 2025-01-09 14:28:00
============================================================
Total rows backed up: 1234
Completed at: 2025-01-09 14:29:45
============================================================
```

### 4. 기술적 세부사항

#### 4.1 JavaScript 함수 구조

```
openOperationEvaluationModal()  // 모달 열기
  ├─ generateSampleLines()  // 표본 라인 생성
  │   └─ updateOverallConclusion()  // 전체 결론 계산
  │       └─ toggleExceptionFields()  // 예외 필드 표시/숨김
  └─ handleSampleResultChange()  // 결과 변경 처리
      └─ updateOverallConclusion()

saveOperationEvaluation()  // 저장
  ├─ 표본별 결과 집계
  ├─ 결론 자동 계산
  └─ API 호출
```

#### 4.2 상태 전이 다이어그램

```
[초기 상태]
  ↓ 표본 크기 입력
[표본 라인 생성] → 결론: "-" (회색)
  ↓ 증빙 내용 입력
[증빙 입력 완료] → 결론: 여전히 "-"
  ↓ 결과 선택 (No Exception)
[평가 완료] → 결론: "Effective" (초록), 예외 필드 숨김
  ↓ 결과 변경 (Exception)
[예외 발견] → 예외 필드 자동 표시, 결론: "Ineffective" (빨강)
  ↓ 경감요소 입력
[경감요소 입력] → 결론: "Effective" (초록), 예외 필드 유지
```

### 5. 테스트 시나리오

#### 시나리오 1: 정상 케이스
1. 평가 모달 열기 → 예외사항 필드 숨김
2. 증빙 내용 입력 → 결론 여전히 `-`
3. 결과를 "No Exception" 선택 → 결론 `Effective`, 예외 필드 숨김
4. 결과를 "Exception" 변경 → 예외 필드 자동 표시
5. 경감요소 입력 → 결론은 여전히 `Effective`
6. 경감요소 삭제 → 결론 `Ineffective`

#### 시나리오 2: 표본 크기 변경
1. 표본 #1에 "증빙서류 확인" 입력
2. 표본 크기를 3으로 변경
3. ✅ 표본 #1의 "증빙서류 확인" **유지**
4. ✅ 표본 #2, #3 새로 생성 (빈 상태)

#### 시나리오 3: 저장 및 목록 표시
1. Exception 선택 (경감요소 없음)
2. 저장 버튼 클릭
3. ✅ 모달에서 "Ineffective" 표시
4. ✅ 목록에서도 "Ineffective" 표시 (버그 수정 완료)

### 6. 파일 변경 요약

**수정된 파일**:
1. `templates/link7_detail.jsp` (+115줄, -29줄)
2. `gmail_schedule.py` (+47줄, -12줄)

**주요 변경 섹션** (link7_detail.jsp):
- 예외사항 필드 HTML (lines 345-353)
- 증빙 내용 입력 필드 (line 1290)
- 표본 라인 생성 함수 (lines 1250-1308)
- 전체 결론 계산 함수 (lines 1372-1459)
- 예외 필드 토글 함수 (lines 1461-1480)
- 저장 함수 (lines 1716-1767)

### 7. 해결된 문제들

1. ✅ 아무 데이터를 입력하지 않은 상태에서 결론이 Effective로 표시되던 문제
2. ✅ Exception을 선택했는데도 목록에서 Effective로 나오던 문제
3. ✅ 예외사항 관련 필드가 항상 표시되어 혼란스러웠던 문제
4. ✅ 표본 크기 변경 시 입력한 데이터가 삭제되던 문제

### 8. 추가 개선 사항

1. ✅ 증빙 내용 입력 시 실시간 결론 업데이트
2. ✅ Exception 여부에 따른 필드 자동 표시/숨김
3. ✅ 표본별 결과 기반 정확한 결론 계산
4. ✅ 데이터 입력 중 표본 크기 변경 시 데이터 보존

### 9. 사용자 피드백 반영

- 사용자: "아무 데이터를 입력하지 않은 상태에서는 결론을 Effective로 표시하면 안 될 것 같은데"
  → ✅ 증빙 내용 미입력 시 결론 `-`로 표시

- 사용자: "예외사항 세부내용과 개선계획은 Exception이 있을 때만 나오는게 좋지 않을까"
  → ✅ Exception 있을 때만 필드 표시

- 사용자: "표본별 테스트 결과에서 증빙 내용을 입력한 상태에서 표본 크기를 변경하면 입력한 데이터가 삭제되네"
  → ✅ 현재 화면 입력값 우선 보존

- 사용자: "C-EL-CA-10-02 통제는 Exception으로 입력했고 전체 결론도 Ineffective로 표시되었는데 통제 운영평가 List에는 Effective로 나오네"
  → ✅ 표본별 결과 기반 결론 계산으로 수정

### 10. 향후 개선 가능 사항

- 표본별 테스트 결과 자동 저장 기능 (임시 저장)
- 경감요소 템플릿/자동완성 기능
- 표본 크기 변경 시 확인 다이얼로그 추가
- 평가 진행률 실시간 표시
- 증빙 내용 필수 입력 검증 추가

---

## 2025-01-10 - 평가 유형 선택 기능 및 데이터베이스 구조 개선

### 배경

Index 페이지에서 ELC, TLC, ITGC를 클릭할 때 진행 중인 운영평가가 있는 경우 사용자가 설계평가 또는 운영평가를 선택할 수 있도록 개선

### 1. 평가 유형 선택 기능 구현

#### 1.1 운영평가 확인 API 추가
**파일**: [snowball.py:1034-1083](snowball.py#L1034-L1083)

```python
@app.route('/api/check-operation-evaluation/<control_type>')
@login_required
def check_operation_evaluation(control_type):
    """진행 중인 운영평가가 있는지 확인하는 API"""
```

**기능**:
- 사용자가 소유한 RCM 중 특정 control_type(ELC/TLC/ITGC)의 운영평가 존재 여부 확인
- 진행 중인 운영평가 세션 목록 반환
- RCM별, 세션별 정보 제공

**응답 형식**:
```json
{
    "has_operation_evaluation": true,
    "evaluation_sessions": [
        {
            "rcm_id": 1,
            "rcm_name": "쿠쿠홈시스_ELC",
            "evaluation_session": "2024-Q4",
            "design_evaluation_session": "2024-Q3"
        }
    ],
    "control_type": "ELC"
}
```

#### 1.2 Index 페이지 UI 수정
**파일**: [templates/index.jsp](templates/index.jsp)

**링크 수정** (154, 170, 186줄):
```javascript
// 기존: 직접 링크
<a href="/elc/design-evaluation">

// 변경: JavaScript 함수 호출
<a href="#" onclick="event.preventDefault(); checkEvaluationType('ELC', '/elc/design-evaluation', '/elc/operation-evaluation');">
```

**JavaScript 함수 추가** (503-571줄):

1. **checkEvaluationType()**: API 호출 및 분기 처리
```javascript
async function checkEvaluationType(controlType, designUrl, operationUrl) {
    const response = await fetch(`/api/check-operation-evaluation/${controlType}`);
    const data = await response.json();

    if (data.has_operation_evaluation) {
        showEvaluationTypeModal(...);  // 모달 표시
    } else {
        window.location.href = designUrl;  // 바로 설계평가로
    }
}
```

2. **showEvaluationTypeModal()**: 평가 유형 선택 모달 생성
```javascript
function showEvaluationTypeModal(controlType, designUrl, operationUrl, evaluationSessions) {
    // Bootstrap 모달로 설계평가/운영평가 선택 UI 표시
    // 진행 중인 세션 개수 표시
}
```

**모달 UI**:
```
┌─────────────────────────────────┐
│ ELC 평가 유형 선택            × │
├─────────────────────────────────┤
│ 진행하실 평가 유형을 선택해주세요:│
│                                   │
│ ┌───────────────────────────┐   │
│ │  설계평가                   │   │
│ │  통제 설계의 적정성을 평가  │   │
│ └───────────────────────────┘   │
│                                   │
│ ┌───────────────────────────┐   │
│ │  운영평가                   │   │
│ │  통제 운영의 효과성을 평가  │   │
│ │  ✓ 진행 중인 세션 2개      │   │
│ └───────────────────────────┘   │
└─────────────────────────────────┘
```

#### 1.3 트러블슈팅

**문제 1**: 모달이 잠깐 나타났다가 사라짐
- **원인**: `<a>` 태그의 기본 동작(페이지 이동)이 막히지 않음
- **해결**: `return false;` → `event.preventDefault();`로 변경

**문제 2**: `no such column: r.control_type`
- **원인**: sb_rcm 테이블에 control_type 컬럼이 없음
- **해결**: 데이터베이스 구조 개선 작업으로 이어짐

### 2. 데이터베이스 구조 개선

#### 2.1 문제 분석

**기존 구조**:
- `sb_rcm`: RCM 메타데이터만 (카테고리 정보 없음)
- `sb_rcm_detail`: 개별 통제 항목 (control_category 있음)

**문제점**:
- RCM 레벨에서 ELC/TLC/ITGC 구분 불가
- 필터링 시 서브쿼리 필요 (성능 저하)
- 쿼리 복잡도 증가

**실제 사용 패턴**:
- 하나의 RCM은 단일 카테고리만 포함
- "쿠쿠홈시스_ELC", "쿠쿠홈시스_TLC", "쿠쿠홈시스_ITGC" 형태로 완전 분리

#### 2.2 마이그레이션 생성

**파일**: [migrations/versions/012_add_control_category_to_rcm.py](migrations/versions/012_add_control_category_to_rcm.py)

**작업 내용**:

1. **컬럼 추가**:
```sql
ALTER TABLE sb_rcm
ADD COLUMN control_category TEXT DEFAULT NULL
```

2. **RCM 이름 기반 카테고리 자동 설정**:
```sql
-- ITGC
UPDATE sb_rcm SET control_category = 'ITGC'
WHERE rcm_name LIKE '%ITGC%' OR rcm_name LIKE '%IT일반통제%'

-- ELC
UPDATE sb_rcm SET control_category = 'ELC'
WHERE rcm_name LIKE '%ELC%' OR rcm_name LIKE '%전사수준통제%'

-- TLC
UPDATE sb_rcm SET control_category = 'TLC'
WHERE rcm_name LIKE '%TLC%' OR rcm_name LIKE '%거래수준통제%'
```

3. **sb_rcm_detail 기반 보완 처리**:
```sql
-- 이름으로 판단 불가한 경우, detail의 다수결로 결정
UPDATE sb_rcm
SET control_category = (
    SELECT control_category
    FROM sb_rcm_detail
    WHERE rcm_id = sb_rcm.rcm_id
    GROUP BY control_category
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
WHERE control_category IS NULL
```

4. **통계 출력**:
```
✅ 카테고리별 RCM 통계:
   - ELC: 5개
   - ITGC: 10개
   - TLC: 1개
```

#### 2.3 API 쿼리 간소화

**파일**: [snowball.py:1050-1065](snowball.py#L1050-L1065)

**변경 전 (복잡)**:
```sql
SELECT DISTINCT
    oeh.evaluation_session,
    oeh.design_evaluation_session,
    oeh.rcm_id,
    r.rcm_name
FROM sb_operation_evaluation_header oeh
JOIN sb_rcm r ON oeh.rcm_id = r.rcm_id
WHERE oeh.user_id = ?
  AND EXISTS (
      SELECT 1 FROM sb_rcm_detail rd
      WHERE rd.rcm_id = oeh.rcm_id
        AND rd.control_category = ?
  )
ORDER BY oeh.evaluation_session DESC
```

**변경 후 (간단)**:
```sql
SELECT DISTINCT
    oeh.evaluation_session,
    oeh.design_evaluation_session,
    oeh.rcm_id,
    r.rcm_name,
    r.control_category
FROM sb_operation_evaluation_header oeh
JOIN sb_rcm r ON oeh.rcm_id = r.rcm_id
WHERE oeh.user_id = ?
  AND r.control_category = ?
ORDER BY oeh.evaluation_session DESC
```

**개선 효과**:
- EXISTS 서브쿼리 제거
- 단순 JOIN 조건으로 변경
- 쿼리 실행 속도 향상
- 코드 가독성 향상

### 3. 주요 파일 변경 내역

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `snowball.py` | 수정 | 운영평가 확인 API 추가 및 쿼리 간소화 |
| `templates/index.jsp` | 수정 | 평가 유형 선택 UI 및 JavaScript 로직 추가 |
| `migrations/versions/012_add_control_category_to_rcm.py` | 신규 | sb_rcm 테이블 구조 개선 마이그레이션 |

### 4. 동작 흐름

```
사용자 클릭 (ELC/TLC/ITGC)
         ↓
checkEvaluationType() 실행
         ↓
API 호출: /api/check-operation-evaluation/{control_type}
         ↓
데이터베이스 쿼리: sb_rcm.control_category = ?
         ↓
        분기
    ┌────┴────┐
    ↓         ↓
운영평가 있음  운영평가 없음
    ↓         ↓
모달 표시     설계평가로 이동
    ↓
사용자 선택
    ↓
해당 페이지로 이동
```

### 5. 개선 사항

1. ✅ **사용자 경험 개선**: 운영평가 진행 중인지 자동 확인
2. ✅ **선택권 제공**: 설계평가/운영평가 명시적 선택 가능
3. ✅ **데이터베이스 구조 개선**: RCM 레벨에서 카테고리 관리
4. ✅ **성능 향상**: 서브쿼리 제거, 단순 JOIN으로 변경
5. ✅ **코드 가독성**: 쿼리가 간결하고 이해하기 쉬움
6. ✅ **유지보수성**: RCM 생성 시 카테고리 지정 가능

### 6. 배포 가이드

**PythonAnywhere 배포 시**:
1. 파일 업로드:
   - `snowball.py`
   - `templates/index.jsp`
   - `migrations/versions/012_add_control_category_to_rcm.py`

2. Bash 콘솔에서 마이그레이션 실행:
```bash
cd ~/mysite
python migrations/migration_manager.py
```

3. Web App Reload

### 7. 향후 고려사항

- RCM 생성/수정 시 control_category 필수 입력 추가
- RCM 목록 화면에서 카테고리별 필터링 기능
- 카테고리 변경 시 sb_rcm_detail과의 일관성 체크
- 혼합 카테고리 RCM 지원 여부 결정