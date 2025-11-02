# Snowball 프로젝트 작업 로그

## 2024-11-02 - 설계평가/운영평가 페이지 개선 및 테스트 추가

### 1. 데이터베이스 수정

#### 1.1 sb_user_rcm 테이블 수정
- **문제**: 권한 제거 시 `last_updated` 컬럼 없음 오류 발생
- **해결**: `sb_user_rcm` 테이블에 `last_updated` 컬럼 추가
- **파일**: `migrations/versions/008_add_last_updated_to_user_rcm.py`

#### 1.2 sb_rcm_detail_v 뷰 수정
- **문제**: 통제주기/통제유형이 표시되지 않음
- **해결**: View에 `control_category` 컬럼 추가, `COALESCE`로 데이터 포맷 불일치 대응
- **파일**: `migrations/versions/009_add_control_category_to_view.py`

### 2. 설계평가 페이지 개선 (Link6)

#### 2.1 평가 유형별 동적 타이틀 표시
- `evaluation_type` 파라미터로 "ITGC/ELC/TLC 설계평가" 동적 표시
- **파일**: `snowball_link6.py`, `templates/link6_design_rcm_detail.jsp`

#### 2.2 통제 카테고리 필터 UI 제거
- 하단 필터 버튼 제거, `evaluation_type`으로 자동 필터링
- **파일**: `snowball_link6.py` (91-93줄)

#### 2.3 기준통제 매핑 기능 제한
- ITGC에서만 기준통제 매핑 컬럼 표시
- **파일**: `templates/link6_design_rcm_detail.jsp` (144-181줄)

#### 2.4 통제주기/통제유형 필드명 수정
- 템플릿 필드명 수정: `control_frequency_name` → `control_frequency`

### 3. 운영평가 페이지 전면 개편 (Link7)

#### 3.1 페이지 구조 변경
**새 구조**:
1. 보유 RCM 목록 (간단한 테이블)
2. 설계평가 현황 (진행중 + 완료)
3. 운영평가 현황 (진행중 + 완료 통합)

#### 3.2 통합 템플릿 생성
- **파일**: `templates/link7_operation_evaluation_unified.jsp` (신규)
- ITGC, ELC, TLC 하나의 템플릿으로 통합
- `evaluation_type` 변수로 동적 표시

#### 3.3 설계평가 현황 개선
- 진행 중인 설계평가 표시 추가
- **함수**: `get_all_design_evaluation_sessions()` 추가 (auth.py)
- **표시**:
  - 진행 중: 세션명, 시작일, 진행률, 상태
  - 완료됨: 세션명, 완료일, 평가 대상 통제, 운영평가 가능 여부

#### 3.4 진행률 표시 개선
- 프로그레스 바 + "13/20" 형식으로 개수 표시
- **파일**: `templates/link7_operation_evaluation_unified.jsp` (142-151줄)

#### 3.5 라우트 수정
- ITGC: `/operation-evaluation`
- ELC: `/elc/operation-evaluation`
- TLC: `/tlc/operation-evaluation`
- 모두 통합 템플릿 사용

### 4. 네비게이션 플로우 테스트 추가

#### 4.1 테스트 파일 생성
- **파일**: `tests/test_navigation_flow.py` (16KB, 19개 테스트)
- RCM 관리 ↔ 설계평가 ↔ 운영평가 간 전환 테스트
- ITGC, ELC, TLC 모든 카테고리 커버
- 세션 관리, 에러 처리, 권한 검증 포함

#### 4.2 테스트 문서 작성
- `tests/README_NAVIGATION_TEST.md` - 상세 가이드
- `tests/NAVIGATION_TEST_SUMMARY.md` - 테스트 요약
- `tests/HOW_TO_RUN_TESTS.md` - 빠른 시작

### 5. 파일 정리

#### 삭제된 파일
- 임시 테스트 파일 4개
- 템플릿 백업 파일 3개

### 주요 변경 파일

#### Python
- `snowball_link6.py`, `snowball_link7.py`, `auth.py`
- `migrations/versions/008_*.py`, `009_*.py` (신규)

#### 템플릿
- `templates/link6_design_rcm_detail.jsp`
- `templates/link7_operation_evaluation_unified.jsp` (신규)
- `templates/link7_elc_operation_evaluation.jsp`
- `templates/link7_tlc_operation_evaluation.jsp`

#### 테스트 (신규)
- `tests/test_navigation_flow.py`
- `tests/README_NAVIGATION_TEST.md`
- `tests/NAVIGATION_TEST_SUMMARY.md`
- `tests/HOW_TO_RUN_TESTS.md`

### 테스트 실행

```bash
pip install pytest pytest-mock
python -m pytest tests/test_navigation_flow.py -v
```

### 주요 개선 사항

1. ✅ 데이터베이스 안정성 (컬럼 누락 해결)
2. ✅ 사용자 경험 (명확한 타이틀, 불필요 UI 제거)
3. ✅ 코드 품질 (템플릿 통합, 중복 제거)
4. ✅ 정보 가시성 (진행 중 평가 표시)
5. ✅ 테스트 커버리지 (19개 네비게이션 테스트)

### 참고

- 템플릿 변경 후 Ctrl+Shift+R로 캐시 새로고침
- 코드 변경 후 Flask 서버 재시작 필수
- DB 변경 후 `python migrate.py upgrade` 실행
