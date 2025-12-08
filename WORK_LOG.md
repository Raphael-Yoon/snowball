# Snowball 프로젝트 작업 로그

## 2025-12-07
- **ELC 통합 테이블 마이그레이션 완료**
  - 설계평가와 운영평가 데이터를 별도 테이블에서 통합 테이블로 마이그레이션
  - 기존: `sb_design_evaluation_*`, `sb_operation_evaluation_*` (ITGC용)
  - 신규: `sb_evaluation_header`, `sb_evaluation_line` (ELC용 통합)
  - 하나의 header/line 레코드가 설계평가 + 운영평가 데이터를 모두 포함

- **운영평가 저장 로직 수정**
  - 문제: ELC 운영평가 데이터 저장 시 ITGC 테이블에 저장되어 데이터가 유실됨
  - 원인: `save_operation_evaluation()` 함수가 모든 RCM에 대해 ITGC 테이블만 사용
  - 수정 (auth.py:1490-1603):
    - RCM의 `control_category` 확인 추가
    - ELC: `_save_operation_evaluation_unified()` 호출 → 통합 테이블(`sb_evaluation_line`) 사용
    - ITGC/TLC: 기존 로직 유지 → 별도 테이블(`sb_operation_evaluation_line`) 사용
  - `_save_operation_evaluation_unified()` 함수 신규 추가:
    - `sb_evaluation_line` 테이블에 운영평가 데이터 업데이트
    - 샘플 데이터는 `sb_evaluation_sample` 테이블에 `evaluation_type='operation'`으로 저장
    - 운영평가 진행에 따라 header의 status 자동 업데이트 (3=진행중, 4=완료)

- **설계평가 완료 확인 로직 수정**
  - 문제: 운영평가 저장 시 "설계평가 세션이 완료되지 않음" 오류 발생
  - 원인: `get_completed_design_evaluation_sessions()` 함수가 `status IN (0, 1)`만 체크
    - status=3 (운영평가 진행중)인 세션을 설계평가 완료로 인식하지 못함
  - 수정 (auth.py:1973-2011):
    - ELC: `status >= 1` AND `archived = 0` 조건으로 변경
    - ITGC/TLC: 기존 `progress = 100` 로직 유지
    - 설계평가 완료 = status가 1 이상 (설계평가 완료, 운영평가 시작/진행/완료 모두 포함)

- **UI 개선**
  - link6_elc_evaluation.jsp:
    - 설계/운영평가 설명 카드에 collapse 기능 추가 (좌우 2열 레이아웃 유지)
    - "세션명" → "평가명"으로 용어 변경
    - 운영평가 테이블에서 "(33개 통제)" 표시 제거 (진행률로 충분)
    - "운영평가 시작 가능" 섹션에 "설계평가 보기" 버튼 추가
  - link7_detail.jsp:
    - 운영평가 상단 "설계평가 보기" 버튼 기능 변경
    - 모달 표시 대신 설계평가 상세 화면으로 이동 (`/design-evaluation/rcm?rcm_id=...&session=...`)
  - link7_elc_operation_evaluation.jsp:
    - 각 운영평가 세션별 "설계평가 보기" 버튼 추가

- **마이그레이션 스크립트**
  - `migrations/migrate_to_unified_evaluation_table.py`: 설계평가 데이터 마이그레이션 (33개 세션)
  - `migrations/migrate_operation_data_to_unified_table.py`: 운영평가 데이터 마이그레이션 (7개 완료된 평가)
  - `migrations/add_archived_to_evaluation_header.py`: archived 컬럼 추가 및 status=5 데이터 변환

- **평가 상태 관리 체계 정립**
  - status 값 의미:
    - 0: 설계평가 진행중
    - 1: 설계평가 완료
    - 2: 운영평가 시작 가능
    - 3: 운영평가 진행중
    - 4: 운영평가 완료
    - 5: 아카이브 (deprecated, archived=1로 대체)
  - evaluation_utils.py:
    - `calculate_design_progress()`: 설계평가 진행률 계산 (overall_effectiveness 기준)
    - `calculate_operation_progress()`: 운영평가 진행률 계산 (conclusion 기준)
    - `get_evaluation_status()`: 상태 정보 통합 조회

## 2025-12-04
- **운영평가 엑셀 다운로드 Testing Table 개선**
  - Testing Table 결과(결론) 컬럼 동적 배치:
    - 템플릿 구조: C~L(3~12)은 Attribute0~9, M(13)은 결론, N(14)은 천고사항/비고
    - 사용하지 않는 attribute 컬럼만 삭제하고, 결론/비고 컬럼은 템플릿 그대로 유지
    - attribute 개수에 따라 결론 컬럼 위치 자동 계산 (snowball_link7.py:2363-2375)
    - 예: attribute 0개 → C열=결론, attribute 2개 → E열=결론
  - 경감요소(mitigation)를 비고 컬럼에 작성 (snowball_link7.py:2410-2413)
  - 다운로드 파일명을 `통제번호_통제명.xlsx` 형식으로 변경 (snowball_link7.py:2599-2604)
  - 11번 행(통제 설명/테스트 절차) 높이 자동 조정 추가 (snowball_link7.py:2274-2282)
    - 줄바꿈 개수 계산하여 행 높이 결정 (기본 15 + 각 줄당 15, 최대 300)

- **샘플 데이터 저장/로드 디버깅**
  - 문제: 샘플 결과(Exception/No Exception)와 경감요소를 수정하고 저장해도 다시 로드 시 표시되지 않음
  - 원인 분석: 프론트엔드에서 `sample_lines` 배열을 evaluation_data에 포함하여 전송하고 있었음 (link7_detail.jsp:2433)
  - 백엔드에서 `sample_lines` 처리 로직 확인 (auth.py:1381, 1554)
  - 디버깅 로그 추가 (auth.py:1382-1383, 1539, 1547):
    - sample_lines 전송 여부 확인
    - 각 샘플의 result, mitigation 값 확인
    - 샘플 삽입 시 상세 로그 출력
  - 테스트 결과: 정상 동작 확인 (캐시/세션 문제였을 가능성)

## 2025-12-02
- **표본수 0 통제의 모집단 업로드 후 데이터 표시 버그 수정**
  - 문제: 모집단 업로드 직후에는 데이터가 보이지만, 페이지 새로고침 후 평가 모달을 열면 데이터가 표시되지 않음
  - 원인 분석:
    1. 업로드 API: RCM detail에 정의된 모든 attributes를 반환하지 않고 실제 사용된 attributes만 반환
    2. 조회 API: 동일한 문제 - 실제 사용된 attributes만 반환
    3. 저장 함수: 잘못된 ID로 input 요소를 찾아서 빈 값으로 덮어씀 (`sample-attr0-1` 대신 `sample-1-attribute0` 사용해야 함)
    4. 화면 표시: 부모 요소 `evaluation-fields`가 `display: none`으로 숨겨져 있음
  - 수정 내용:
    - **snowball_link7.py (업로드 API, 1983-2020줄)**:
      - `for i in sorted(used_attributes)` → `for i in range(10)`로 변경
      - RCM detail에 정의된 모든 attributes 반환 (이름이 없는 attribute는 skip)
    - **snowball_link7.py (조회 API, 514-536줄)**:
      - 동일하게 RCM detail에 정의된 모든 attributes 반환하도록 수정
      - 샘플 데이터에서 사용된 attribute만 찾는 로직 제거
    - **auth.py (get_operation_evaluation_samples, 1702-1726줄)**:
      - 디버깅 로그 추가: attribute 값, attributes dict, 반환할 sample_lines 출력
    - **link7_detail.jsp (저장 함수, 2306줄)**:
      - attribute 수집 시 ID 수정: `sample-attr${attrIdx}-${i}` → `sample-${i}-attribute${attrIdx}`
    - **link7_detail.jsp (generateSampleLinesWithAttributes, 3309-3320줄)**:
      - HTML 삽입 후 JavaScript로 각 input의 value를 직접 설정 (템플릿 리터럴 특수문자 문제 방지)
      - 디버깅 로그 추가: 설정하는 값과 실제 설정된 값 출력
    - **link7_detail.jsp (generateSampleLinesWithAttributes, 3328-3333줄)**:
      - `evaluation-fields` 요소를 `display: block`으로 설정 (부모 요소가 숨겨져서 테이블이 보이지 않던 문제 해결)
  - 테스트 결과: 모집단 업로드 후 페이지 새로고침해도 데이터가 정상적으로 표시됨

- **초기화 버튼 기능 개선**
  - 문제: 초기화 버튼 클릭 시 데이터는 삭제되지만 메인 페이지의 평가 결과 배지가 "Effective"로 남아있음
  - 수정: `resetPopulationUpload()` 함수에서 evaluated_controls 완전 삭제 및 평가 결과 배지를 "Not Evaluated"로 변경 (link7_detail.jsp:3181-3189)

- **Attribute 처리 방식 문서화**
  - `work_attribute.md` 파일 생성
  - 모집단/증빙 항목 구분 로직, 데이터베이스 구조, API 처리 방식 등 상세 문서화
  - 디버깅 팁 및 관련 파일 위치 정리

## 2025-12-01
- **운영평가 엑셀 다운로드 기능 구현**
  - Backend: snowball_link7.py에 `/operation-evaluation/download` 엔드포인트 추가
  - Template_Manual.xlsx 사용 (Template, Testing Table, Population 시트)
  - Template 시트: 통제 기본 정보 (C2~C13)
    - C2: 회사명, C4: 사용자명, C7~C11: 통제 정보
    - C12: 설계평가 검토 결과, C13: 운영평가 결론
  - Testing Table 시트: 샘플 데이터 표
    - Row 4: 헤더 (모집단 항목=노란색, 증빙 항목=초록색)
    - Row 5~64: 샘플 데이터 (60개 준비, 표본수에 따라 행 삭제)
    - 사용하지 않는 컬럼 삭제 (attribute 개수에 따라)
    - Row 66: "Testing Table" 구분자 (행 삭제 후 위로 이동, 전체 행 색상 유지)
    - 이미지 삽입 위치:
      - 설계평가 이미지: "Testing Table" 구분자 2칸 아래 (예: 8행 구분자 → 10행)
      - 운영평가 이미지: 설계평가 이미지 2칸 아래 (예: 10행 설계평가 → 12행 운영평가)
      - 같은 종류의 이미지는 모두 같은 행에 삽입, 행 높이는 가장 큰 이미지에 맞춤
  - Population 시트: recommended_sample_size가 0이면 유지, 아니면 삭제
  - 시트 순서: 통제코드 시트(1), Testing Table(2), Population(3, 조건부)
  - Frontend: link7_detail.jsp 모달 푸터에 다운로드 버튼 추가
  - 파일명: `{control_code}_{evaluation_session}.xlsx`
  - Excel 오류 수정:
    - 외부 링크 제거: `load_workbook(keep_links=False)` + `wb._external_links = []`
    - 명명된 범위 제거: `wb.defined_names` 전체 삭제

- **운영평가 이미지 업로드 기능 추가**
  - Backend API (snowball_link7.py):
    - `/api/operation-evaluation/upload-image`: 이미지 업로드
    - `/api/operation-evaluation/images/<rcm_id>/<header_id>/<control_code>`: 이미지 목록 조회
    - `/api/operation-evaluation/delete-image`: 이미지 삭제
  - 저장 경로: `static/uploads/operation_evaluations/{rcm_id}/{header_id}/{control_code}/`
  - Frontend (link7_detail.jsp):
    - 운영평가 모달에 이미지 업로드 섹션 추가
    - 파일 선택 후 업로드 버튼 클릭으로 업로드
    - 업로드된 이미지 미리보기 (전체 너비, 썸네일 스타일)
    - 이미지 클릭 시 원본 크기로 새 창에서 보기
    - 각 이미지마다 삭제 버튼 제공
  - JavaScript 함수:
    - `uploadOperationImage()`: 이미지 업로드 (header_id 필요)
    - `loadOperationImages()`: 이미지 목록 로드
    - `displayOperationImages()`: 이미지 미리보기 표시
    - `deleteOperationImage()`: 이미지 삭제
  - 평가 저장 시 header_id를 evaluated_controls에 저장하여 이미지 업로드 가능하도록 함
  - 엑셀 다운로드 시 설계평가 이미지와 함께 운영평가 이미지도 Testing Table에 삽입

- **표본수 0 통제의 모집단 업로드 UI 표시 버그 수정**
  - 문제: 표본수가 0인 통제에서 모집단 업로드 섹션이 표시되지 않는 문제
  - 원인: `hasSavedData` 체크 로직이 `line_id` 존재 여부만으로 판단하여, 모집단을 업로드하지 않았어도 이전 저장 기록이 있으면 `hasSavedData=true`가 되어 모집단 업로드 UI가 숨겨짐
  - 수정: 표본수 0인 경우 `sample_lines` 배열이 있는 경우에만 저장된 데이터로 간주하도록 로직 변경 (link7_detail.jsp:1144-1156)
  - 표본수 0 통제:
    - 모집단 업로드 전: `population-upload-section` 표시
    - 모집단 업로드 후: `evaluation-fields` + 초기화 버튼 표시
  - 일반 통제: 기존 로직 유지 (`line_id` 또는 `sample_lines` 존재 시 저장된 것으로 간주)

- **표본수 0 통제의 모집단 데이터 엑셀 다운로드 포함**
  - 업로드된 모집단 파일(`uploads/populations/{user_id}_{control_code}_*`)을 찾아서 Population 시트에 데이터 복사
  - 파일 패턴 매칭으로 가장 최신 파일 사용 (glob.glob + max by mtime)
  - Population 시트는 recommended_sample_size가 0인 경우에만 유지됨 (snowball_link7.py:2378-2424)

- **모집단 업로드 후 표본 테이블에 모집단/증빙 항목 표시 기능 추가**
  - 문제: 모집단 업로드 후 표본 테이블에 "문서번호1234", "234"만 표시되고 컬럼 헤더에 모집단/증빙 구분이 없음
  - Backend (snowball_link7.py):
    - `/api/operation-evaluation/upload-population`: 응답에 `attributes` 배열 추가 (필드 매핑에서 컬럼명 추출)
    - `/api/operation-evaluation/samples/<line_id>`: 응답에 `attributes` 배열 추가 (RCM detail에서 조회)
    - `population_attribute_count` 반환으로 모집단 항목 개수 전달 (1912-1937, 491-525줄)
  - Frontend (link7_detail.jsp):
    - 모집단 업로드 성공 시 `generateSampleLinesWithAttributes()` 호출 (3117-3123줄)
    - 모달 열기/샘플 조회 시 attributes가 있으면 `generateSampleLinesWithAttributes()` 호출 (1338-1344줄)
    - `generateSampleLinesWithAttributes()` 함수에서:
      - 헤더에 모집단/증빙 배지 표시 (3227-3230줄)
      - 샘플 데이터의 attributes 값을 input 필드에 채움 (3273줄)
      - 모집단 항목은 readonly로 설정 (3281줄)

## 2025-11-28
- **설계평가 "당기 발생사실 없음" 기능 추가**
  - DB: sb_design_evaluation_line 테이블에 no_occurrence, no_occurrence_reason 컬럼 추가 (마이그레이션 028)
  - Backend: auth.py 저장/로드 로직에 no_occurrence 처리 추가
  - Frontend: link6_design_rcm_detail.jsp에 체크박스 UI 및 토글 로직 추가
  - 조건: 표준표본수가 0인 통제에만 체크박스 표시
  - 체크 시: 증빙 테이블 숨김, 사유 입력란 표시

- **sb_evaluation_sample 테이블 attribute 컬럼 복원**
  - 마이그레이션 027: attribute0~9 컬럼 추가 (총 17개 컬럼)
  - sb_rcm_detail의 attribute 정의에 따라 동적 표본 데이터 저장
  - auth.py: request_number 등 삭제된 컬럼 참조 제거

- **RCM 표본수 관리 개선**
  - snowball_link5.py: `/rcm/detail/<detail_id>/sample-size` 엔드포인트 추가 (일반 사용자용)
  - link5_rcm_view.jsp: control_frequency_code 사용하도록 수정
  - placeholder 제거 (빈 값과 실제 값 명확히 구분)
  - 표본수 자동계산 버튼 추가 (통제주기 기준 일괄 계산)
  - 표본수 계산 기준: 연/반기 1개, 분기/월 2개, 주 5개, 일 20개, 일 초과 25개
  - 영문 통제주기 이름 지원 (Annually, Quarterly, Monthly, Weekly, Daily, Multi-Day 등)

- **파일 업로드 경로 정리**
  - uploads/ : RCM 원본 파일, 모집단
  - static/uploads/design_evaluations/ : 설계평가 증빙 파일
  - static/uploads/operation_evaluations/ : 운영평가 모집단, 샘플, 테스트 결과

## 2025-11-24
- 설계평가 모달: 평가 증빙 이미지 크기 개선 (반응형, 원본 크기 존중)
- 설계평가 모달: 평가 완료 시 파일 업로드 섹션 숨김
- 설계평가 모달: 적정성/효과성 선택 시 증빙 내용 자동 입력
- 운영평가 모달: 설계평가 증빙 이미지 크기 개선 (반응형)
- 운영평가 모달: "당기 발생사실 없음" 체크박스 조건부 표시 (표본수 0일 때만)
- 운영평가 모달: 모집단 업로드 초기화 기능 추가 (파일 및 DB 데이터 삭제)
- 운영평가 모달: 초기화 버튼을 모달 푸터의 저장 버튼 옆으로 이동
- 운영평가 모달: '취소' 버튼을 '닫기'로 변경
- 백엔드 API: `/api/operation-evaluation/reset-population` 엔드포인트 추가

## 2025-11-22
- MySQL/SQLite 호환성 문제 해결 (auth.py: IndexableDict 추가, snowball_link8.py: 분기 처리)
- 설계평가 코멘트 필드 추가
- RCM 테이블 UI 개선 (조치사항 컬럼 제거, 너비 조정)
- Dashboard 메뉴 순서 변경 (최상단 이동)

## 2025-11-20
- 운영평가 결론 계산 로직 버그 수정 (JavaScript 구문 오류, for 루프 로직 개선)

## 2025-11-19
- Flask 템플릿 캐싱 문제 해결 (TEMPLATES_AUTO_RELOAD 설정 추가)
- GitHub Push 성공 (developer 브랜치)
- 테스트 파일 정리 및 MySQL 동기화 스크립트 정리

## 2025-11-16
- 권장 표본수 0 지원 기능 구현 (모집단 업로드 모드)
- Jinja2/JavaScript 템플릿 수정 (0을 유효한 값으로 처리)

## 2025-11-16
- 권장 표본수 기능 추가 (RCM detail에서 통제별 설정)
- Admin RCM 상세보기 UI 개선 (일괄 저장, Toast 알림)
- 운영평가 라인 생성 시 권장 표본수 자동 적용
- 모집단 업로드 시 권장 표본수 우선 사용

## 2025-11-14
- DatabaseConnection 래퍼 클래스 개선 (MySQL 호환성)
- MySQL 연결 안정성 개선 (PyMySQL 임포트 에러 처리)
- 뷰 동기화 스크립트 개선 (sync_views_to_mysql.py)
- 불필요 파일 정리 (마크다운 문서, SQL 파일)

## 2025-11-13
- 설계평가 엑셀 다운로드 기능 구현 (Design_Template.xlsx 기반)
- 설계평가 완료 버튼 표시 문제 해결
- RCM 테이블에 control_category 추가
- 스키마 마이그레이션 도구 생성 (sync_sqlite_to_mysql.py)

## 2024-11-05
- UI 일관성 개선 (모달 버튼 크기 통일)
- 설계평가 페이지 "평가 필요" 텍스트 제거
- 버튼 높이 일관성 개선 (24px 고정)

## 2024-11-02
- sb_user_rcm 테이블 수정 (last_updated 컬럼 추가)
- sb_rcm_detail_v 뷰 수정 (control_category 추가)
- 설계평가 페이지 개선 (평가 유형별 동적 타이틀)
- 운영평가 페이지 전면 개편 (통합 템플릿)
- 네비게이션 플로우 테스트 추가

## 2025-01-10
- 평가 유형 선택 기능 구현 (ELC/TLC/ITGC 클릭 시 설계/운영평가 선택)
- 운영평가 확인 API 추가
- sb_rcm 테이블에 control_category 컬럼 추가
- 데이터베이스 쿼리 간소화 (서브쿼리 제거)

## 2025-01-09
- 운영평가 모달 예외사항 필드 조건부 표시
- 전체 결론 자동 계산 로직 개선
- 저장 시 결론 계산 버그 수정
- 표본 크기 변경 시 데이터 보존 기능
- Gmail 스케줄러 개선 (MySQL 동기화 결과 메일 전송)

## 2025-01-08
- ELC 운영평가 모달 UI/UX 개선
- "결론" 컬럼 제거
- 모달 너비 조정 (800px)
- 표본 크기 필드 조정
- 전체 결론 로직 수정 (경감요소 기반)

## 2025-01-07
- VSCode 디버그 설정 개선 (작업 디렉토리 설정)
- Dashboard 이미지 적용
- MySQL 마이그레이션 스크립트 개선 (migrate_to_mysql.py)
- MySQL → SQLite 백업 스크립트 생성 (backup_mysql_to_sqlite.py)

## 2024-11-02 (추가)
- 메인 페이지 레이아웃 통일
- 모달 버튼 크기 통일
