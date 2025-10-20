# SnowBall 프로젝트 작업 기록

## 현재 상태 (2025-10-10)

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

### 2025-10-19
- **내부평가 (Link8) 기능 개선 및 버그 수정**
  - **세션별 진행 상황 표시 개선**
    - ARCHIVED 세션 필터링: 내부평가 목록에서 제외
    - 설계평가와 운영평가 상태를 모두 확인하여 세션 표시 여부 결정
    - 파일: `snowball_link8.py` (세션 조회 쿼리 개선)

  - **세션 상태 배지 로직 수정**
    - 설계평가 COMPLETED + 운영평가 COMPLETED = "완료"
    - 설계평가 IN_PROGRESS OR 운영평가 IN_PROGRESS = "진행중"
    - 그 외 = "대기"
    - 파일: `templates/internal_assessment_main.jsp`

  - **진행률 계산 정확도 개선**
    - 설계평가 헤더의 `total_controls` 대신 실제 라인 개수를 집계
    - 빈 `control_code` 항목 제외 처리
    - 실제 평가 완료 개수를 라인에서 직접 계산
    - 파일: `snowball_link8.py` (update_progress_from_actual_data)

  - **운영평가 자동 완료 로직 제거**
    - 운영평가 데이터 존재 시 설계평가를 자동 완료하던 잘못된 로직 제거
    - 설계평가 `evaluation_status`만으로 완료 여부 판단
    - 파일: `snowball_link8.py` (line 368-377 삭제)

  - **버튼 표시 로직 전면 개선**
    - 설계평가/운영평가 버튼을 항상 표시
    - 상태에 따라 버튼 텍스트 변경:
      - COMPLETED: "확인" 버튼 (초록 외곽선)
      - IN_PROGRESS: "계속" 버튼 (파란/초록)
      - 미시작: "시작" 버튼
      - 잠김: 설계평가 미완료 시 운영평가 버튼 비활성화
    - 파일: `templates/internal_assessment_main.jsp`

  - **카드 높이 통일**
    - 진행률 정보가 없을 때도 "0%, (시작 전)" 표시하여 카드 높이 동일하게 유지
    - 버튼 최소 높이 설정 (42px)
    - 파일: `templates/internal_assessment_main.jsp` (CSS 추가)

  - **현재 단계 표시 개선**
    - 설계평가 세션 미생성 시: "미진행" (회색 배지)
    - 진행 중: 실제 단계명 표시
    - 파일: `templates/internal_assessment_main.jsp`

  - **버튼 활성화 조건 명확화**
    1. 설계평가 진행중 → 설계평가 계속만 활성화
    2. 설계평가 완료 → 설계평가 확인 + 운영평가 시작 활성화
    3. 운영평가 진행중 → 설계평가 확인 + 운영평가 계속 활성화
    4. 운영평가 완료 → 설계평가 확인 + 운영평가 확인 활성화

### 2025-10-18
- **인터뷰 기능 버그 수정 및 개선**
  - **[CRITICAL] Method Not Allowed 에러 수정**
    - 문제: 인터뷰 완료 후 "Method Not Allowed" 에러 발생하여 메일 전송 안됨
    - 원인: `snowball.py:621` 에 `@app.route('/paper_generate', methods=['POST'])` 데코레이터만 있고 함수 정의 없음
    - 결과: 다음 함수인 `ai_review_selection`이 `/paper_generate` 라우트에 잘못 연결됨
    - 해결: 사용되지 않는 `@app.route('/paper_generate')` 데코레이터 제거
    - 파일: `snowball.py:621`

  - **스킵샘플 버튼 오류 수정**
    - 문제: 질문 8번 "권한 승인 절차" 질문에서 스킵샘플 버튼 작동 안함
    - 원인: `templates/link2.jsp:449` 에서 `type: 'skip'`으로 설정되어 `return`으로 함수 종료
    - 결과: 자동 제출 로직이 실행되지 않아 다음 질문으로 넘어가지 않음
    - 해결: `type: 'radio_textarea', radio: 'N', textarea: ''`로 변경
    - 파일: `templates/link2.jsp:449`

  - **인터뷰 이메일 전송 테스트 추가**
    - Link2 (인터뷰) 이메일 전송 기능 테스트 7개 추가
    - RCM 자동생성처럼 인터뷰도 메일을 보내는데 테스트가 없었던 것을 발견
    - 테스트 항목:
      1. export_interview_excel_and_send 함수 존재 확인
      2. 이메일 전송 확인
      3. 첨부파일 포함 확인
      4. 이메일 실패 처리
      5. AI 검토와 함께 이메일 전송
      6. 한글 파일명 생성
      7. 진행률 콜백 호출
    - 파일: `tests/test_link2_interview.py` (18개→25개 테스트)
    - 디버그 스크립트 작성: `debug_interview_email.py`

  - **조건부 질문 로직 검증**
    - 인터뷰 질문의 조건부 스킵 로직 논리적 일관성 검증
    - 검증 스크립트 작성: `validate_interview_logic.py`, `test_conditional_skip.py`
    - 테스트 결과:
      - ✅ Q3='N' → Q4, Q5, Q47 자동 스킵 (정상)
      - ✅ Q14='N' → Q15~Q23 자동 스킵 (정상)
      - ✅ Q24='N' → Q25~Q30 자동 스킵 (정상)
      - ✅ Q31='N' → Q32~Q37 자동 스킵 (정상)
      - ✅ Q38='N' → Q39~Q43 자동 스킵 (정상)
    - 결론: 스킵샘플 데이터가 모순처럼 보이지만, 실제 조건부 로직은 정상 작동
    - 스킵될 질문에 기본값이 있어도 실제로는 사용자에게 표시되지 않음

- **테스트 커버리지 분석 및 에러 핸들링 테스트 추가**
  - 테스트 커버리지 분석 스크립트 작성: `analyze_test_coverage.py`
    - 전체 라우트 수: 109개
    - 기존 테스트: 290개
    - 누락 영역 5개 식별: Link8, Auth Flow, Error Handling, Database, Integration
    - 우선순위: HIGH (Link8), MEDIUM (Error Handling, Auth, Database), LOW (Integration)

  - **에러 핸들링 테스트 추가** (사용자 요청: "에러 핸들링은 있어야지")
    - 새 테스트 파일: `tests/test_error_handling.py` (27개 테스트)
    - 테스트 클래스 10개:
      1. `TestNotFoundErrors`: 404 에러 (존재하지 않는 라우트, RCM ID, 사용자)
      2. `TestUnauthorizedErrors`: 403 권한 에러 (관리자 페이지, 다른 사용자 RCM, 미인증 접근)
      3. `TestBadRequestErrors`: 400 잘못된 요청 (필수 필드 누락, 잘못된 이메일, 빈 데이터, 잘못된 JSON)
      4. `TestServerErrors`: 500 서버 에러 (RCM 생성 실패, 이메일 전송 실패)
      5. `TestSessionErrors`: 세션 에러 (만료된 세션, 세션 데이터 없음, task_id 없음)
      6. `TestInputValidation`: 입력 검증 (SQL Injection, XSS, 긴 입력, 특수문자)
      7. `TestFileUploadErrors`: 파일 업로드 에러 (파일 없음, 잘못된 타입, 빈 파일)
      8. `TestRateLimiting`: 과도한 요청 (연속 요청, 반복 로그인)
      9. `TestDatabaseErrors`: DB 에러 (연결 실패, 잘못된 파라미터)
      10. `TestConcurrency`: 동시성 (동시 RCM 생성)
    - 테스트 수정 사항:
      - 파일 업로드 라우트 수정: `/operation-evaluation/apd01/upload` → `/api/operation-evaluation/apd01/upload-population`
      - 308 Permanent Redirect 상태 코드 허용 (Flask의 슬래시 처리)
      - Mock 패치 위치 수정 (실제 함수 위치 기준)
    - 모든 에러 핸들링 테스트 통과 ✅

- **UI 통합 테스트 추가 및 버그 수정**
  - **통합 UI 테스트 72개 추가** (사용자 관점에서 모든 페이지/버튼 작동 확인)
  - 테스트 클래스 14개:
    1. `TestMainNavigation`: 홈, 로그인, 로그아웃, 헬스체크
    2. `TestLink0Dashboard`: 대시보드 페이지
    3. `TestLink1RCMGeneration`: RCM 생성 전체 플로우
    4. `TestLink2Interview`: 인터뷰 답변 제출, 이전 버튼, AI 검토
    5. `TestLink3ControlGuide`: 통제 가이드, 템플릿 다운로드
    6. `TestLink4EducationVideos`: 교육 영상 페이지
    7. `TestLink5RCMMapping`: RCM 매핑 및 검토
    8. `TestLink6DesignEvaluation`: 설계평가 전체 플로우
    9. `TestLink7OperationEvaluation`: 운영평가 (APD01/07/09/12)
    10. `TestUserPages`: 사용자 페이지들
    11. `TestAdminPages`: 관리자 페이지 권한 확인
    12. `TestSessionManagement`: 세션 연장/초기화/이메일 업데이트
    13. `TestAPIEndpoints`: API 엔드포인트 테스트
    14. `TestGenericManualControls`: Generic 수동통제 페이지
    15. `TestButtonFunctionality`: 주요 버튼 기능
    16. `TestPageNotFound`: 404 에러 처리

  - **발견 및 수정한 실제 버그 3개**:
    1. **url_for('home') 오류** (`snowball_admin.py`)
       - 문제: `url_for('home')` 호출하지만 함수명은 `index`
       - 영향: 관리자 페이지에서 홈으로 리다이렉트 시 BuildError 발생
       - 수정: 모든 `url_for('home')`을 `url_for('index')`로 변경 (5곳)
       - 파일: `snowball_admin.py:315, 332, 449, 631, 662`

    2. **paper_request 템플릿 변수 누락** (`snowball.py:604`)
       - 문제: `render_template('link2.jsp')`에 필수 변수 전달 안함
       - 영향: `/paper_request` 호출 시 `UndefinedError: 'question' is undefined`
       - 수정: Deprecated 함수로 표시하고 link2로 리다이렉트하도록 변경
       - 파일: `snowball.py:604-614`

    3. **세션 변수명 불일치** (테스트 코드)
       - 문제: Link2는 `question_index`를 사용하는데 테스트는 `current_question` 사용
       - 영향: 테스트 실행 시 KeyError 발생
       - 수정: 테스트에서 올바른 세션 변수명 사용
       - 파일: `tests/test_integration_ui.py:93-95`

- **Link8 내부평가 대시보드 개선**
  - **목표**: Link5(RCM 매핑), Link6(설계평가), Link7(운영평가)의 진행현황을 대시보드 형태로 시각화

  - **백엔드 개선** ([snowball_link8.py](snowball_link8.py:245-345))
    - `update_progress_from_actual_data()` 함수 대폭 개선:
      - **Link5 진행현황**: RCM 통제별 매핑 완료율 (50%) + 검토 완료율 (50%)
        - 전체 통제 수, 매핑된 통제 수, 검토된 통제 수 추적
        - 예: "매핑: 25/50, 검토: 20/50 → 45% 완료"
      - **Link6 진행현황**: 설계평가 세션별 완료율
        - 전체 세션 수, 완료된 세션 수 추적
        - 예: "완료: 2/3세션 → 67% 완료"
      - **Link7 진행현황**: 운영평가 통제별 완료율
        - 전체 평가 대상 통제 수, 완료된 통제 수 추적
        - 예: "완료: 15/20통제 → 75% 완료"
    - 각 단계별 `details` 정보에 구체적인 진행 데이터 포함
    - 진행률에 따른 상태 자동 업데이트 (pending → in_progress → completed)

  - **프론트엔드 개선** ([templates/internal_assessment_main.jsp](templates/internal_assessment_main.jsp:151-185))
    - **상세 진행률 바 추가**: 각 단계별로 프로그레스 바와 세부 정보 표시
    - 단계별 표시 정보:
      - **1단계 (RCM 평가)**: "매핑: X/Y, 검토: A/B"
      - **2단계 (설계평가)**: "완료: X/Y세션"
      - **3단계 (운영평가)**: "완료: X/Y통제"
    - 진행률 퍼센트와 컬러 코딩 (파란색: 진행중, 초록색: 완료, 회색: 대기)
    - 기존 원형 차트 + 단계 인디케이터는 유지

  - **버그 수정 2개**:
    1. **url_for 오류** ([snowball_link8.py](snowball_link8.py:68,100,105))
       - 문제: `link9.internal_assessment` 호출 (잘못된 blueprint)
       - 수정: `link8.internal_assessment`로 변경 (3곳)

  - **테스트 추가** ([tests/test_link8_dashboard.py](tests/test_link8_dashboard.py))
    - 26개 테스트 신규 작성
    - 8개 테스트 클래스:
      1. `TestLink8InternalAssessment`: 메인 페이지 (4개)
      2. `TestLink8AssessmentDetail`: 상세 페이지 (3개)
      3. `TestLink8AssessmentStep`: 단계별 페이지 (3개)
      4. `TestLink8API`: API 엔드포인트 (4개)
      5. `TestLink8ProgressCalculation`: 진행현황 계산 (3개)
      6. `TestLink8StepSequence`: 순차 진행 (2개)
      7. `TestLink8Navigation`: 네비게이션 (2개)
      8. `TestLink8GuideSection`: 가이드 섹션 (2개)
      9. `TestLink8EmptyState`: 빈 상태 (1개)
      10. `TestLink8Responsiveness`: 반응형 (2개)
    - 모든 테스트 통과 ✅

- **테스트 현황**
  - **전체 테스트: 415개 (100% 통과)** ⬆️ 389개 → 415개 (+26개)
  - Link2 인터뷰 테스트: 25개
  - 에러 핸들링 테스트: 27개
  - UI 통합 테스트: 72개
  - Link8 대시보드 테스트: 26개 (신규)
  - **모든 페이지, 버튼, API 엔드포인트 정상 작동 확인 ✅**

### 2025-10-16
- **ITGC Shield 웹사이트 UI 개선**
  - CSS 수정: `itgc_shield/css/style.css`, `itgc_shield/css/responsive.css`
  - HTML 수정: `itgc_shield/index.html`
  - 반응형 디자인 및 스타일링 업데이트
- **교육 콘텐츠 비디오 리소스 정리**
  - 추가: Snowball APD 시연 영상 4개 (APD01~04)
  - 추가: 내부회계관리제도 팟캐스트 영상
  - 추가: DDL 변경통제 관련 영상 및 슬라이드
  - 추가: 데이터변경모니터링 관련 영상 및 슬라이드
  - 삭제: ITGC 패스워드 관련 기존 영상 파일 (재편집 예정)
  - 정리: `mov/DDL/`, `mov/데이터변경모니터링/` 디렉토리 생성하여 체계화
- **MCP (Model Context Protocol) 연구**
  - 웹 크롤링 테스트 코드 작성: `MCP/test.py`
    - k-icfr.org Q&A 게시판 데이터 수집 스크립트
    - BeautifulSoup, pandas 활용
  - 샘플 코드: `MCP/sample.py`
- **새 프로젝트 개발**
  - **our_lotte_day**: 롯데 기념일 웹페이지 프로젝트
    - HTML, CSS, JavaScript 구현
    - 이미지 리소스 포함
  - **stock**: 주식 정보 프로젝트
    - OpenDART API 연동 (`opendart.py`)
    - 웹 인터페이스 (`web.py`)
    - 종목코드 데이터베이스 구축
  - **yujuduck**: 이미지 기반 프로젝트
    - 데이터 및 이미지 리소스 관리
  - **github_test**: GitHub 테스트 저장소
    - 다양한 언어 테스트 코드 (C++, Java, Python)
    - Wordcloud 실험
- **데이터베이스**
  - `snowball.db` 파일 생성 (SQLite)
  - Snowball 프로젝트 로컬 DB 구축
- **개발 환경 설정**
  - VSCode 디버거 설정 추가: `.vscode/launch.json`
    - Python 디버거 구성 (debugpy)
    - 현재 파일 실행 설정
  - Git 서브모듈 업데이트: `SnowBall`, `TAX`, `macbook_air`
- **파일 정리**
  - 삭제: `itgc.txt`, `rule.txt` (불필요한 텍스트 파일 제거)
  - 프로젝트 구조 재정리 및 최적화

### 2025-10-14
- **"당기 발생사실 없음" 표시 개선**
  - 문제: "Effective (발생사실 없음)" 텍스트가 너무 길게 표시됨
  - 해결: 아이콘으로 간결하게 표시
  - 구현: `Effective <i class="fas fa-info-circle"></i>` 형태
  - 위치: `templates/link7_detail.jsp:1245` - `updateEvaluationUI()` 함수
  - 배지 색상: 녹색(bg-success) - 일반 Effective와 동일
  - 툴팁: 아이콘에 마우스 오버 시 "당기 발생사실 없음" 표시
  - 조건: `conclusion === 'not_applicable' && no_occurrence === true`

### 2025-10-10
- **DB 마이그레이션 실행**
  - 운영평가 파일 경로 컬럼 추가 (migration 004)
  - 운영평가 Line 테이블에 last_updated 컬럼 추가 (migration 005)
- **Windows 임시 파일 삭제 오류 수정**
  - 문제: `[WinError 32] 다른 프로세스가 파일을 사용 중` 에러 발생
  - 원인: openpyxl 등이 파일 핸들을 유지 중일 때 `os.unlink()` 실패
  - 해결: try-except로 감싸서 삭제 실패 시 무시하도록 수정
  - 적용 파일: `snowball_link7.py` (APD01/07/09/12), `operation_evaluation_generic.py`, `file_manager.py`
- **예외 체크 로직 개선**
  - 승인일자 비교 로직 수정: 날짜가 없을 때 기본값을 `false`→`true`로 변경
  - **승인일자 누락을 예외로 추가**: APD01/07/09/12에서 승인일자가 없으면 예외(Y)로 표시
  - 예외 조건 명확화: 정상(N)이 되려면 승인일자가 반드시 있어야 함
- **PC01 선행 조건 체크 구현**
  - PC02/PC03은 PC01의 모집단 업로드 및 표본 추출 후에만 진행 가능
  - `isPC01Completed()` 함수: PC01의 `test_results_path` 또는 `samples_path` 확인
  - 선행 조건 미충족 시 세련된 Bootstrap 모달로 안내
    - 진행 순서 단계별 설명 (4단계 리스트)
    - "PC01 평가 시작" 버튼으로 바로 PC01 모달 열기 가능
- **UX 개선: 스크롤 위치 유지**
  - 문제: 모달 닫을 때 `location.reload()`로 인해 페이지 맨 위로 이동
  - 해결: `sessionStorage`에 스크롤 위치 저장 후 복원
  - `reloadWithScrollPosition()` 함수 구현
  - 모든 모달에 적용: APD01/07/09/12, PC01/02/03, CO01

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
