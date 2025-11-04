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

---

## 2024-11-05 - UI 일관성 개선: 버튼 크기 및 레이아웃 통일

### 1. 메인 페이지 레이아웃 통일 (index.jsp)

#### 1.1 Private 섹션 레이아웃 정렬
- **문제**: 로그인 상태와 로그아웃 상태의 Private 메뉴 배치가 상이함
- **해결**: 로그아웃 상태 레이아웃을 로그인 상태와 동일하게 2+3 카드 구조로 변경
- **파일**: `templates/index.jsp` (288-381줄)
- **구조**:
  - 상단 2개: RCM + 내부평가 (offset-lg-3로 중앙 정렬)
  - 하단 3개: ELC + TLC + ITGC

### 2. 모달 버튼 크기 통일

#### 2.1 설계평가 시작 모달 버튼
- **문제**: "취소" 버튼 높이가 너무 큼
- **해결**: 모든 모달 버튼에 `padding: 0.25rem 0.5rem; font-size: 0.875rem;` 추가
- **수정 파일**:
  - `templates/link6_design_evaluation.jsp` (377-380줄) - ITGC
  - `templates/link6_elc_design_evaluation.jsp` (398-401줄) - ELC
  - `templates/link6_tlc_design_evaluation.jsp` (373-376줄) - TLC

#### 2.2 평가 상세 모달 버튼
- **파일**: `templates/link6_design_rcm_detail.jsp`
- **수정 위치**:
  - 평가 모달 (340-345줄): "취소", "평가 저장" 버튼
  - 파일 업로드 모달 (419-424줄): "취소", "업로드 및 적용" 버튼

#### 2.3 운영평가 및 관리자 모달 버튼
- `templates/link7_detail.jsp` (434-436줄): 자동통제 확인 모달
- `templates/admin_rcm_users.jsp` (199-200줄): RCM 권한 모달
- `templates/admin_users.jsp`:
  - 사용자 추가 모달 (164-165줄)
  - 사용자 수정 모달 (215-216줄)
  - 기한 연장 모달 (239-241줄)
  - 사용자 삭제 모달 (261-263줄)

### 3. 설계평가 페이지 UI 개선

#### 3.1 "평가 필요" 텍스트 제거
- **문제**: 평가되지 않은 항목에 "평가 필요" 표시
- **해결**: 공란(빈 문자열)으로 변경
- **파일**: `templates/link6_design_rcm_detail.jsp`
- **수정 위치**:
  - 176줄: 초기 HTML 템플릿
  - 1456줄: JavaScript 평가 결과 업데이트
  - 2052줄: UI 초기화 함수

### 4. 버튼 높이 일관성 개선 (핵심 수정)

#### 4.1 문제 분석
- **사용자 피드백**: "버튼들의 높이가 달라"
- **원인**: padding과 font-size만 조정했으나, 명시적인 height 설정 누락
- **영향**: "평가완료", "평가", "조회" 버튼들이 서로 다른 높이로 표시됨

#### 4.2 해결 방법
- **파일**: `templates/link6_design_rcm_detail.jsp`
- **수정 내용**: 모든 동적 버튼에 고정 높이 24px 적용

**수정 위치 및 코드**:

1. **초기 버튼 템플릿** (170줄):
```html
style="padding: 0.2rem 0.35rem; font-size: 0.75rem; height: 24px;"
```

2. **"평가완료" 버튼** (1454줄):
```javascript
buttonElement.style.padding = '0.2rem 0.35rem';
buttonElement.style.fontSize = '0.75rem';
buttonElement.style.height = '24px';
buttonElement.style.minWidth = '70px';
```

3. **"조회" 버튼** (1471줄):
```javascript
buttonElement.style.padding = '0.2rem 0.35rem';
buttonElement.style.fontSize = '0.75rem';
buttonElement.style.height = '24px';
buttonElement.style.minWidth = '70px';
```

4. **"평가" 버튼** (1484줄):
```javascript
buttonElement.style.padding = '0.2rem 0.35rem';
buttonElement.style.fontSize = '0.75rem';
buttonElement.style.height = '24px';
```

### 주요 변경 파일 요약

#### 템플릿 파일 (8개)
1. `templates/index.jsp` - Private 섹션 레이아웃
2. `templates/link6_design_evaluation.jsp` - ITGC 모달 버튼
3. `templates/link6_elc_design_evaluation.jsp` - ELC 모달 버튼
4. `templates/link6_tlc_design_evaluation.jsp` - TLC 모달 버튼
5. `templates/link6_design_rcm_detail.jsp` - 버튼 높이 통일 (핵심)
6. `templates/link7_detail.jsp` - 운영평가 모달
7. `templates/admin_rcm_users.jsp` - RCM 권한 관리
8. `templates/admin_users.jsp` - 사용자 관리

### 기술적 개선 사항

1. ✅ **높이 일관성**: 모든 평가 버튼 24px 고정 높이 적용
2. ✅ **모달 버튼 통일**: padding 0.25rem 0.5rem, font-size 0.875rem
3. ✅ **레이아웃 정렬**: 로그인/로그아웃 상태 Private 섹션 동일화
4. ✅ **시각적 정돈**: "평가 필요" 제거로 깔끔한 UI

### 교훈

- **높이 vs 너비**: 사용자가 "크기가 다르다"고 할 때는 **높이(height)**를 먼저 확인할 것
- **명시적 스타일링**: padding/font-size만으로는 불충분, **명시적인 height 설정** 필요
- **일관성 검증**: 동적으로 생성되는 모든 버튼 상태를 체크할 것

### 확인 방법

1. Flask 서버 재시작
2. 브라우저에서 **Ctrl+Shift+R** (하드 리프레시)
3. `/design-evaluation/rcm` 페이지에서 버튼 높이 확인
