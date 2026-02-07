# Public 기능 통합 Unit 테스트 결과

- 실행 시간: 2026-02-07 18:44:39
- 소요 시간: 19.9초
- 모드: Headless

## 테스트 대상

| Link | 설명 | Public |
|------|------|--------|
| Link1 | RCM 자동생성 | O |
| Link2 | 인터뷰/설계평가 | O |
| Link3 | 조서 템플릿 | O |
| Link4 | 컨텐츠 | O |
| Link9 | 문의/피드백 | O |
| Link10 | AI 결과 | O |
| Link11 | 공시 | O |

## 요약 (그룹별)

### ✅ Link1 (9/9)

| 그룹 | 결과 | 상태 |
|------|------|------|
| 1번 | 2/2 | ✅ |
| 2번 | 3/3 | ✅ |
| 3번 | 4/4 | ✅ |

## 상세 결과

### Link1 상세

#### 1번 (2/2)

| 테스트 | 상태 | 메시지 |
|--------|------|--------|
| test_link1_access_guest | ✅ | 테스트 통과 |
| test_link1_access_logged_in | ✅ | 로그인 사용자 이메일 자동 입력 확인: snowball2727@naver.com |

#### 2번 (3/3)

| 테스트 | 상태 | 메시지 |
|--------|------|--------|
| test_rcm_form_fields | ✅ | test_link1_access_guest 에서 확인됨 |
| test_rcm_validation_email | ✅ | 잘못된 이메일 형식에서 폼 제출 방지됨 (HTML5 검증) |
| test_rcm_validation_system_name | ✅ | 시스템명 필수 입력 검증 동작 확인 |

#### 3번 (4/4)

| 테스트 | 상태 | 메시지 |
|--------|------|--------|
| test_rcm_tool_filtering | ✅ | 테스트 통과 |
| test_rcm_generate_logic_common | ✅ | Common 섹션 포함 확인 - 총 21개 항목 |
| test_rcm_generate_logic_cloud | ✅ | Cloud(AWS) 필터링 적용됨 - 파일 생성 확인 |
| test_rcm_generate_logic_infra | ✅ | OS(Linux)/DB(Oracle) 필터링 적용됨 - 21개 항목 |

---

## 전체 요약

- 총 테스트: 9
- 통과: 9 (100.0%)
- 실패: 0 (0.0%)
