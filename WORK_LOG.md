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
