# SnowBall 프로젝트 작업 기록

## 현재 상태 (2025-10-09)

### 핵심 아키텍처
- **수동통제 Generic 시스템**: APD01/07/09/12, PC01/02/03, CO01을 단일 구현으로 통합
  - `control_config.py`: 통제별 설정 (필드, 컬럼, 레이블, 의존성)
  - `operation_evaluation_generic.py`: 3개 API (페이지/업로드/저장)
  - `templates/link7_manual_generic.jsp`: 동적 템플릿
  - 라우트: `/operation-evaluation/manual/{control_code}`
- **통제 의존성 관리**: PC02/PC03은 PC01 데이터를 자동으로 복사 (`skip_upload: true`)

### 주요 기능
1. **운영평가**: 모집단 업로드 → 표본 자동 추출 → 테스트 결과 입력 → 엑셀 저장
2. **데이터 저장**: 템플릿 기반 엑셀 단일 파일 (Population + Testing Table)
3. **이어하기**: 기존 데이터 자동 로드, 세션 없이도 저장 가능
4. **리셋**: 통제별 독립적 초기화

### 파일 구조
```
snowball/
├── control_config.py              # 통제 설정 (APD/PC/CO 통제 정의)
├── operation_evaluation_generic.py # Generic API (통합 라우트)
├── snowball_link7.py              # 운영평가 메인 라우트
├── file_manager.py                # 파일 처리, 표본 추출
├── templates/
│   ├── link7.jsp                  # 운영평가 메인 (RCM 목록)
│   ├── link7_detail.jsp           # RCM 통제 목록 상세 페이지
│   └── link7_manual_generic.jsp   # 통합 평가 팝업 (iframe)
└── static/
    ├── paper/Template_manual.xlsx  # 수동통제 템플릿
    └── uploads/operation_evaluations/{rcm_id}/{header_id}/{control_code}_evaluation.xlsx
```

### 최근 해결한 이슈
- ✅ 기존 데이터 로드 시 화면 표시 안됨 → `samples_data` 구조 수정
- ✅ 저장 시 세션 오류 → DB에서 `operation_header_id` 조회로 해결

### 새 통제 추가 방법
1. `control_config.py`의 `MANUAL_CONTROLS`에 설정 추가
2. `file_manager.py`의 `load_operation_test_data()`에 elif 블록 추가
3. 완료 (라우트/템플릿/API 모두 자동 적용)

---

## 작업 히스토리

### 2025-10-09
- **PC02/PC03/CO01 통제 구현 완료**
  - PC02: 사용자 테스트 확인 (PC01 의존)
  - PC03: 배포 승인 확인 (PC01 의존)
  - CO01: 배치 스케줄 승인
- **통제 의존성 시스템 구현**
  - `skip_upload: true` 옵션으로 PC01 데이터 자동 복사
  - PC02/PC03 평가 시 자동으로 PC01 모집단 로드
- **예외 로직 구현**
  - PC02: 사용자테스트 미수행, 테스트일자 누락, 테스트일자 > 반영일자
  - PC03: 배포요청자/승인자 동일인, 부서 상이, 승인일자 > 반영일자
  - CO01: APD 스타일 예외 로직 (부서 상이, 승인자 누락, 승인일자 이후 등)
- **파일 네이밍 리팩토링**
  - `user_operation_evaluation.jsp` → `link7.jsp`
  - `user_operation_evaluation_rcm.jsp` → `link7_detail.jsp`
  - `operation_evaluation_manual_generic.jsp` → `link7_manual_generic.jsp`
  - 다른 link 파일들과 일관성 확보
- **버그 수정**
  - 필드 ID 불일치 수정 (`appr_${idx}` → `appr_name_${idx}`, `date_${idx}` → `appr_date_${idx}`)
  - 필수 컬럼 표시 한글화 (`required_fields` → `population_headers`)
- **UI 개선**
  - 모든 운영평가 페이지에 파비콘 추가
  - 리셋 기능 통일 (PC02/PC03은 페이지 새로고침)

### 2025-10-07
- APD01/07/09/12 Generic 리팩토링 (12함수→3함수, 183KB 제거)
- 세션 없이 저장 기능, 데이터 로드 버그 수정

### 2025-10-07 (오전)
- APD07 완성: 이어하기, 리셋, 날짜 포맷
- Template_manual.xlsx 수정 (C:쿼리, D:실행일자)
- UI 개선: 버튼 스타일 통일, 저장 후 모달 유지

### 2025-10-06
- APD07 모달 구현 (iframe 기반)
- 엑셀 백업 파일 생성 제거
- 리셋 시 DB 라인 데이터 삭제

### 2025-10-06 (주요)
- **템플릿 기반 엑셀 저장 전환**: JSON 제거, 엑셀 단일 소스화
- `save_operation_test_data()`, `load_operation_test_data()` 구현
- DB 스키마: `sb_operation_evaluation_line`에 파일 경로 컬럼 추가
- 저장 구조: `/{rcm_id}/{operation_header_id}/{control_code}_evaluation.xlsx`

### 2025-10-05
- APD01 운영평가 구현 (팝업, 필드 매핑, 표본 추출)
- APD07 운영평가 구현 (필수 필드: 쿼리, 변경일자)
- 필드 매핑 UI: 드롭다운 선택, XLSX.js 활용
- 기존 데이터 자동 로드 기능

---

## 참고

### 표본 크기
```
모집단    표본
1-4       2
5-12      2
13-52     5
53-250    20
251+      25
```

### 필수 필드 (모집단)
- **APD01**: user_id, user_name, department, permission, grant_date
- **APD07**: change_id, change_date
- **APD09**: account, grant_date
- **APD12**: account, grant_date
- **PC01**: program_name, deploy_date
- **PC02**: PC01과 동일 (자동 복사)
- **PC03**: PC01과 동일 (자동 복사)
- **CO01**: batch_schedule_name, register_date

### 구현된 통제 목록
| 통제코드 | 통제명 | 모집단 필드 | 평가 필드 | 특이사항 |
|---------|--------|------------|----------|---------|
| APD01 | 권한 관리 | 사용자ID, 이름, 부서, 권한, 부여일 | 요청서번호, 요청자, 승인자, 승인일자 등 | - |
| APD07 | 데이터 변경 승인 | 쿼리, 변경일자 | 요청서번호, 요청자, 승인자, 승인일자 등 | - |
| APD09 | OS/DB 접근권한 | 계정, 부여일 | 요청서번호, 요청자, 승인자, 승인일자 등 | - |
| APD12 | 특수권한 관리 | 계정, 부여일 | 요청서번호, 요청자, 승인자, 승인일자 등 | - |
| PC01 | 프로그램 변경 승인 | 프로그램명, 반영일자 | 요청번호, 요청자, 승인자, 개발담당자, 배포담당자 | - |
| PC02 | 사용자 테스트 | PC01과 동일 | 변경요청서번호, 테스트유무, 담당자, 일자 | PC01 의존 |
| PC03 | 배포 승인 | PC01과 동일 | 변경요청서번호, 배포요청자/부서, 승인자/부서, 승인일자 | PC01 의존 |
| CO01 | 배치 스케줄 승인 | 배치스케줄이름, 등록일자 | 요청번호, 요청자, 승인자, 승인일자 등 | - |
