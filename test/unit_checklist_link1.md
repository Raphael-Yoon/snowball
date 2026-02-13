# Link1: RCM 자동생성 Unit 테스트 시나리오

## 1. 페이지 접근 및 사용자 정보 확인
- [ ] **test_link1_access_logged_in**: 로그인 상태에서 `/link1` 접근 시, 세션의 사용자 이름과 이메일 주소가 입력 필드에 자동으로 채워지는지 확인
- [ ] **test_link1_access_guest**: 비로그인 상태에서 접근 시 'Guest'로 표시되며, 이메일 필드가 비어 있는지 확인

## 2. 입력 폼 유효성 및 옵션 선택
- [ ] **test_rcm_form_fields**: 시스템명, Cloud 타입, 인프라 타입(OS/DB), Tool 선택(OS접근제어, DB접근제어, 배포Tool, 배치스케줄러) 등 모든 입력 요소가 화면에 정상적으로 표시되는지 확인
- [ ] **test_rcm_validation_email**: 이메일 주소 형식이 잘못되었거나 누락된 상태로 생성 요청 시 에러 처리 확인
- [ ] **test_rcm_validation_system_name**: 시스템명이 입력되지 않았을 때의 동작 확인

## 3. RCM 생성 및 필터링 로직 (Backend 연동)
- [ ] **test_rcm_generate_logic_common**: 생성된 파일에서 모든 환경 공통 항목(Common 섹션)이 누락 없이 포함되어 있는지 확인
- [ ] **test_rcm_generate_logic_cloud**: 선택한 Cloud 타입(AWS, Azure 등)에 해당하지 않는 행들이 엑셀에서 정상적으로 삭제되는지 확인
- [ ] **test_rcm_generate_logic_infra**: 선택한 OS(Linux, Windows) 및 DB(Oracle, MySQL 등) 타입별 통제 항목 필터링 동작 확인
- [ ] **test_rcm_tool_filtering**: Tool 선택(OS접근제어, DB접근제어, 배포Tool, 배치스케줄러)에 따라 해당 Tool 템플릿이 모집단/테스트절차에 반영되는지 확인

## 4. API 테스트
- [ ] **test_link1_population_templates_api**: 모집단 템플릿 API 호출 시 기본 템플릿(sw, os, db)과 Tool 템플릿(os_tool, db_tool, deploy_tool, batch_tool)이 모두 반환되는지 확인

## 5. 메일 전송 및 완료 화면
- [ ] **test_rcm_mail_send_success**: 모든 조건 입력 후 생성 버튼 클릭 시 `mail_sent.jsp`로 이동하며 성공 메시지가 표시되는지 확인
