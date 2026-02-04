# Link5: RCM 관리 E2E 테스트 시나리오

## 1. 파일 업로드 및 유효성 검사

- **test_rcm_upload_success**: 정상 엑셀 파일 업로드 성공 확인 (표준 서식 준수)
- **test_rcm_upload_invalid_ext**: .txt 등 잘못된 확장자 파일 업로드 시 거부 확인
- **test_rcm_upload_missing_required**: 필수 데이터(Control Code 등) 누락 시 에러 처리 확인

## 2. 목록 조회 및 권한 관리

- **test_rcm_list_metadata**: 목록 화면에서 업로드한 RCM의 파일명, 날짜 등 메타데이터 표시 확인
- **test_rcm_data_isolation**: 타 사용자로 로그인 시 내 RCM 데이터가 보이지 않는지 확인 (데이터 격리)

## 3. 상세 조회 및 데이터 수정

- **test_rcm_detail_mapping**: 상세 화면 진입 시 엑셀 내용이 테이블에 정확히 매핑되는지 확인
- **test_rcm_attribute_setting**: Attribute(모집단 필드 정의) 설정 및 저장 확인

## 4. 데이터 삭제

- **test_rcm_delete**: RCM 삭제 기능 수행 및 목록에서 사라짐 확인

