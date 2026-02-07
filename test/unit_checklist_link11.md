# Link11: 정보보호공시 E2E 테스트 시나리오

## 1. 대시보드 및 네비게이션

- **test_link11_access**: `/link11` 페이지가 정상적으로 로드되는지 확인
- **test_link11_dashboard_stats**: 대시보드 카드(투자 비율, 인력 비율 등)가 표시되는지 확인
- **test_link11_category_navigation**: 카테고리 카드 클릭 시 해당 카테고리 질문 페이지로 이동하는지 확인

## 2. 질문 응답 기능 (카테고리 1: 정보보호 투자)

- **test_link11_answer_yes_no**: YES/NO 질문 클릭 시 색상 변경 및 활성화 상태 확인
- **test_link11_dependent_questions**: Q1에서 '예' 선택 시 하위 질문(Q2, Q3...)이 나타나는지 확인
- **test_link11_currency_input**: 금액 입력 시 쉼표(,) 자동 포맷팅 확인
- **test_link11_validation_b_lt_a**: '정보보호 투자액(B)'이 '정보기술 투자액(A)'보다 클 때 저장 시도 시 경고 메시지 확인
- **test_link11_validation_negative**: 숫자/금액 필드에 음수 입력 시 방지되는지 확인 (min="0", 서버 검증)

## 3. 질문 응답 기능 (카테고리 2: 정보보호 인력)

- **test_link11_validation_personnel**: 인력 수 계층 검증 (총 임직원 >= IT 인력 >= 보안 인력)

## 4. 질문 응답 기능 (기타 유형)

- **test_link11_multi_select**: 체크박스형 질문(카테고리 4 등)에서 다중 선택 및 저장 확인
- **test_link11_number_input**: 숫자 필드(인력 수 등) 입력 및 저장 확인
- **test_link11_auto_calculation**: 답변 입력 후 상단 진행률 또는 대시보드 수치가 업데이트되는지 확인

## 5. 증빙 자료 관리

- **test_link11_evidence_modal**: 질문 하단의 '증빙 자료 업로드' 버튼 클릭 시 파일 선택창/모달 노출 확인
- **test_link11_evidence_view_page**: `/link11/evidence` 페이지에서 전체 증빙 자료 목록 확인
- **test_link11_evidence_mime_validation**: 확장자가 변조된 파일 업로드 시 MIME 타입 검증으로 거부되는지 확인

## 6. 공시 자료 생성 (리포트)

- **test_link11_report_preview**: `/link11/report` 페이지에서 지금까지 입력한 내용의 미리보기가 표시되는지 확인
- **test_link11_report_download**: '공시자료 생성 및 다운로드' 버튼 클릭 시 파일 생성 프로세스(로딩 오버레이) 시작 확인

## 7. 회사별 데이터 격리

- **test_link11_company_data_isolation**: 사용자 전환 후 본인 회사 데이터만 조회 가능한지 확인
  - 우측 상단 사용자명 클릭하여 다른 회사 계정으로 전환
  - 해당 회사의 공시 데이터만 표시되는지 확인
  - '관리자로 돌아가기' 버튼으로 원래 계정 복귀

