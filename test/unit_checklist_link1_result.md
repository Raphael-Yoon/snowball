<!-- Test Run: 2026-02-12 13:33:53 -->
# Link1: RCM 자동생성 Unit 테스트 시나리오

## 1. 페이지 접근 및 사용자 정보 확인
- [ ] **test_link1_access_logged_in**: 로그인 상태에서 `/link1` 접근 시, 세션의 사용자 이름과 이메일 주소가 입력 필드에 자동으로 채워지는지 확인
- [ ] **test_link1_access_guest**: 비로그인 상태에서 접근 시 'Guest'로 표시되며, 이메일 필드가 비어 있는지 확인

## 2. 입력 폼 유효성 및 옵션 선택
- [ ] **test_rcm_form_fields**: 시스템명, Cloud 타입, 인프라 타입(OS/DB), 도구 사용 여부 등 모든 입력 요소가 화면에 정상적으로 표시되는지 확인
- [ ] **test_rcm_validation_email**: 이메일 주소 형식이 잘못되었거나 누락된 상태로 생성 요청 시 에러 처리 확인
- [ ] **test_rcm_validation_system_name**: 시스템명이 입력되지 않았을 때의 동작 확인

## 3. RCM 생성 및 필터링 로직 (Backend 연동)
- [ ] **test_rcm_generate_logic_common**: 생성된 파일에서 모든 환경 공통 항목(Common 섹션)이 누락 없이 포함되어 있는지 확인
- [ ] **test_rcm_generate_logic_cloud**: 선택한 Cloud 타입(AWS, Azure 등)에 해당하지 않는 행들이 엑셀에서 정상적으로 삭제되는지 확인
- [ ] **test_rcm_generate_logic_infra**: 선택한 OS(Linux, Windows) 및 DB(Oracle, MySQL 등) 타입별 통제 항목 필터링 동작 확인
- [ ] **test_rcm_tool_filtering**: 'OS/DB 점검도구 사용' 체크박스 선택 여부에 따라 `OS_Tool`, `DB_Tool` 섹션의 포함/제외 여부 확인

## 4. 메일 전송 및 완료 화면
- [ ] **test_rcm_mail_send_success**: 모든 조건 입력 후 생성 버튼 클릭 시 `mail_sent.jsp`로 이동하며 성공 메시지가 표시되는지 확인

---
## 테스트 결과 요약

| 항목 | 개수 | 비율 |
|------|------|------|
| PASS | 10 | 100.0% |
| FAIL | 0 | 0.0% |
| SKIP | 0 | 0.0% |
| **총계** | **10** | **100%** |
