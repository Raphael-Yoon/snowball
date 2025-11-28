# Snowball 프로젝트 작업 로그

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
