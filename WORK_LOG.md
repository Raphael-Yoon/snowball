# Snowball 작업 로그

## 2025-12-31: RCM 상세보기 화면 개선 및 기준통제 매핑 기능 추가

### 1. 모집단/증빙 구분 기능
- **admin_standard_controls.jsp**: 기준통제 관리 화면에 모집단/증빙 구분 배지 추가
- **link5_rcm_view.jsp**: RCM 상세보기 화면에 모집단/증빙 구분 표시
- `population_attribute_count` 필드로 모집단 개수 관리 (0=자동통제, 2=기본값)
- 0 입력 시 2로 변경되는 버그 수정 (JavaScript 및 Python 백엔드)
  - `snowball_admin.py`: `|| 2` → `if ... is not None else 2`
  - `admin_standard_controls.jsp`: `parseInt()` 시 `|| 2` 제거
  - `link5_rcm_view.jsp`: 동일한 로직 적용

### 2. 기준통제 매핑 기능
- 기준통제 매핑 배지 클릭 시 모달 팝업으로 기준통제 선택 가능
- 검색 기능 지원 (코드/이름/카테고리)
- 매핑/매핑해제 기능 구현
- **API 추가**:
  - `POST /api/rcm-detail/<id>/map-standard-control`: 기준통제 매핑
  - `POST /api/rcm-detail/<id>/unmap-standard-control`: 매핑 해제
- **API 수정**:
  - `/api/standard-controls`: 응답 키 변경 (`controls` → `standard_controls`)

### 3. UI 개선
- **모달 버튼 높이/너비 통일**: 취소/저장 버튼 스타일 일관성 확보
  - `link5_rcm_view.jsp`: 모달 footer 버튼 CSS 추가
  - 고정 높이 38px, min-width 80px, padding 조정
- **테이블 스크롤 시 고정 컬럼 겹침 현상 수정**:
  - z-index 레이어 구조 개선:
    - 일반 컬럼: z-index 없음
    - 고정 바디 셀: `z-index: 3`
    - 일반 헤더: `z-index: 10`
    - 고정 헤더: `z-index: 11`
  - 고정 컬럼 배경색에 `!important` 추가하여 확실하게 적용

### 4. 데이터베이스
- **sb_standard_control 테이블** attribute 데이터 입력 (32개 레코드)
  - APD: 14개 통제
  - PC: 6개 통제
  - CO: 6개 통제
  - PD: 6개 통제
- MySQL UPDATE 쿼리 생성 및 적용

### 5. 코드 정리
- 불필요한 마이그레이션 파일 삭제:
  - `migrations/029_add_attributes_to_standard_control.sql`
  - `sb_standard_control_mysql_insert.sql`

### 변경된 파일
- `templates/admin_standard_controls.jsp`
- `templates/link5_rcm_view.jsp`
- `snowball_admin.py`
- `snowball_link5.py`

### 참고사항
- Google Drive API 설정 필요 (work_log 자동 업로드용)
- 서버 재시작 필요

---

## 2026-01-08: CSRF 보호 적용, 설계평가 이미지 삭제 기능, DB 오류 수정

### 1. CSRF(Cross-Site Request Forgery) 보호 전면 적용
Flask-WTF의 CSRFProtect를 사용하여 모든 POST 폼에 CSRF 토큰 적용

#### 적용 완료된 템플릿 (25개 POST 폼)
- **snowball.py 관련**:
  - `link1.jsp`: RCM 생성 폼
  - `link2.jsp`: 인터뷰/설계평가 질문 폼
  - `link2_ai_review.jsp`: AI 검토 옵션 선택 폼
  - `login.jsp`: 서비스 문의 폼 (로그인 폼은 의도적으로 CSRF exempt)

- **관리자 메뉴**:
  - `admin_rcm.jsp`: RCM 정보 수정 폼 (1개)
  - `admin_users.jsp`: 사용자 추가/수정/연장/삭제 폼 (4개)

- **평가 관련**:
  - `contact.jsp`: 서비스 문의 폼
  - `assessment_detail.jsp`: 설계/운영평가 이동 폼 (2개)
  - `internal_assessment_main.jsp`: 설계/운영평가 이동 폼 (12개)
  - `link6_evaluation.jsp`: JavaScript 동적 폼 CSRF 토큰 추가 (2개 함수)
    - `viewDesignEvaluation()`: 완료된 설계평가 보기
    - `continueDesignEvaluation()`: 진행 중인 설계평가 계속하기

#### CSRF Exempt 유지 (보안상 정상)
- `/login` 엔드포인트: 로그인 폼 (사용자 세션 없음)
- API 엔드포인트들: `@login_required`로 인증 보호

### 2. 설계평가 이미지 삭제 기능 추가
- **백엔드 API**: `POST /api/design-evaluation/delete-image/<image_id>`
  - 파일: `snowball_link6.py`
  - 권한 확인: 관리자 또는 RCM 접근 권한 있는 사용자만 삭제 가능
  - 파일 시스템과 DB 레코드 모두 삭제

- **프론트엔드 UI**: `link6_design_rcm_detail.jsp`
  - 저장된 이미지에 × 삭제 버튼 추가
  - `deleteExistingImage()` 함수 구현
  - `showToast()` 함수 추가 (success/error/warning/info 알림)
  - 이미지 미리보기 크기 개선 (width: 100%, max-width: 600px)

- **DB 쿼리 수정**: 이미지 로드 시 `image_id` 포함
  - 기존: `SELECT file_path, file_name`
  - 변경: `SELECT image_id, file_path, file_name`

### 3. 설계평가 화면 기준통제 매핑 기능 추가
설계평가 화면에도 RCM View와 동일한 기준통제 매핑 모달 적용
- **파일**: `link6_design_rcm_detail.jsp`
- **기능**:
  - 기준통제 매핑 배지 클릭 시 모달 팝업
  - 기준통제 검색 및 선택
  - 매핑/매핑 해제
- **JavaScript 함수**:
  - `openStdControlModal()`: 모달 열기
  - `loadStdControls()`: 기준통제 목록 로드
  - `selectStdControl()`: 매핑
  - `unmapStdControl()`: 매핑 해제

### 4. 데이터베이스 연결 오류 수정
#### 문제: SQLite "Cannot operate on a closed database" 오류
- **파일**: `snowball_link7.py`
- **위치**: `download_operation_evaluation()` 함수
- **원인**: with 블록이 종료된 후 conn 객체 사용 시도
- **수정**: 2956번 줄에 새로운 `with get_db() as conn:` 블록 추가

#### 문제: 이미지 로드 시 DB 연결 오류
- **파일**: `snowball_link6.py`
- **위치**: `load_evaluation_data_api()` 함수의 이미지 조회 부분
- **원인**: with 블록이 종료된 conn 객체 재사용
- **수정**: 662번 줄에 새로운 `with get_db() as conn:` 블록 추가
- **디버깅**: 예외 발생 시 로그 출력 추가

### 5. 환경 설정 및 패키지 관리
- **requirements.txt**: 필요 패키지 설치
  - 새로 설치: flask-wtf, pytest, pytest-mock, wtforms, pygments 등
  - 이미 설치됨: python-dotenv, flask, openai, pandas, pymysql 등

- **.env 파일**: 데이터베이스 설정 추가
  ```
  # 데이터베이스 설정
  # 로컬 개발: USE_MYSQL=false (SQLite 사용)
  # PythonAnywhere 운영: USE_MYSQL=true (MySQL 사용)
  USE_MYSQL=false
  ```

### 6. 테스트 코드 정리
불필요한 테스트 파일 및 폴더 삭제:
- `tests/` 폴더 전체 삭제
- `test_admin_required.py`, `test_logging.py`, `test_pagination.py` 삭제
- `test_data/` 폴더 삭제
- `migrations/test_rcm_status.py` 삭제
- `pytest.ini`, `run_tests.sh` 삭제

### 변경된 파일
- **보안**: `snowball.py` (CSRF exempt 주석 처리)
- **템플릿 (CSRF 토큰 추가)**:
  - `link1.jsp`, `link2.jsp`, `link2_ai_review.jsp`
  - `login.jsp`, `contact.jsp`
  - `admin_rcm.jsp`, `admin_users.jsp`
  - `assessment_detail.jsp`, `internal_assessment_main.jsp`
  - `link6_evaluation.jsp`, `link6_design_rcm_detail.jsp`
- **백엔드**:
  - `snowball_link6.py` (이미지 삭제 API, DB 쿼리 수정)
  - `snowball_link7.py` (DB 연결 오류 수정)
- **환경 설정**: `.env` (DB_TYPE 주석 추가)

### 보안 개선 사항
- ✅ CSRF 보호: 모든 POST 폼에 CSRF 토큰 적용
- ✅ 이미지 삭제 권한: 관리자 또는 RCM 접근 권한 확인
- ✅ 세션 보안: FLASK_SECRET_KEY 환경 변수 필수화
- ✅ API 인증: `@login_required` 데코레이터로 보호

### 참고사항
- CSRF 보호는 로그인 폼을 제외한 모든 POST 요청에 적용
- API 엔드포인트는 AJAX 요청이므로 CSRF exempt 유지, `@login_required`로 보호
- 서버 재시작 필요
