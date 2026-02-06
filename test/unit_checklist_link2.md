# Link2: 인터뷰/설계평가 E2E 테스트 시나리오

## 1. 페이지 접근 및 사용자 정보 확인
- [ ] **test_link2_access_guest**: 비로그인 상태에서 `/link2` 접근 시 첫 번째 질문(이메일 입력)이 표시되는지 확인
- [ ] **test_link2_access_logged_in**: 로그인 상태에서 `/link2` 접근 시 이메일 필드가 자동으로 채워지고 `readonly` 상태인지 확인

## 2. 인터뷰 진행 기능 (UI/UX)
- [ ] **test_link2_progress_bar**: 질문 진행에 따라 상단 진행률 바가 정상적으로 업데이트되는지 확인
- [ ] **test_link2_navigation**: '다음' 버튼 클릭 시 다음 질문으로 이동하고, '이전' 버튼 클릭 시 이전 답변이 유지된 채로 돌아오는지 확인
- [ ] **test_link2_input_types**: 질문 타입별(텍스트, 라디오, 텍스트 포함 라디오 등) 입력 요소가 정상적으로 렌더링되는지 확인

## 3. 조건부 질문 로직 (Dynamic Flow)
- [ ] **test_link2_conditional_skip_cloud**: 4번 질문(Cloud 사용 여부)에서 '아니오' 선택 시 5, 6번 질문이 건너뛰어지는지 확인
- [ ] **test_link2_conditional_skip_db**: 15번 질문(DB 접속 가능 여부)에서 '아니오' 선택 시 DB 관련 질문들(16~24)이 건너뛰어지는지 확인
- [ ] **test_link2_conditional_skip_os**: 25번 질문(OS 접속 가능 여부)에서 '아니오' 선택 시 OS 관련 질문들(26~31)이 건너뛰어지는지 확인

## 4. 관리자 전용 기능 (Admin Features)
- [ ] **test_link2_admin_sample_buttons**: 관리자 로그인 시 '샘플입력', '스킵샘플' 버튼이 표시되는지 확인
- [ ] **test_link2_sample_fill_click**: '샘플입력' 클릭 시 현재 질문의 답변이 자동으로 채워지고 다음 질문으로 넘어가는지 확인
