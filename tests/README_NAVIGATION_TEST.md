# 네비게이션 플로우 테스트 가이드

## 개요
RCM 관리(link5) ↔ 설계평가(link6) ↔ 운영평가(link7) 간의 화면 전환을 테스트합니다.

## 테스트 파일
- `test_navigation_flow.py` - 네비게이션 통합 테스트

## 테스트 범위

### 1. Link5 (RCM 관리) → Link6 (설계평가)
- ✅ ITGC 설계평가로 이동
- ✅ ELC 설계평가로 이동
- ✅ TLC 설계평가로 이동
- ✅ evaluation_type 파라미터 전달 확인

### 2. Link6 (설계평가) → Link7 (운영평가)
- ✅ 설계평가 완료 후 운영평가로 이동
- ✅ ITGC 운영평가로 이동 (`/operation-evaluation`)
- ✅ ELC 운영평가로 이동 (`/elc/operation-evaluation`)
- ✅ TLC 운영평가로 이동 (`/tlc/operation-evaluation`)

### 3. 역방향 네비게이션
- ✅ 운영평가 → 설계평가
- ✅ 운영평가 → RCM 관리
- ✅ 설계평가 → RCM 관리

### 4. 완전한 플로우
- ✅ RCM 관리 → 설계평가 → 운영평가 (ITGC)
- ✅ RCM 관리 → 설계평가 → 운영평가 (ELC)
- ✅ RCM 관리 → 설계평가 → 운영평가 (TLC)

### 5. 세션 관리
- ✅ RCM ID 세션 유지
- ✅ evaluation_type 세션 유지
- ✅ 페이지 간 이동 시 세션 유지

### 6. 에러 처리
- ✅ RCM 선택 없이 접근 시 리다이렉트
- ✅ 존재하지 않는 RCM ID 처리
- ✅ 권한 없는 RCM 접근 차단

## 테스트 실행 방법

### Prerequisites
```bash
# pytest 설치 (아직 설치되지 않은 경우)
pip install pytest pytest-mock
```

### 전체 네비게이션 테스트 실행
```bash
cd c:\Python\snowball
python -m pytest tests/test_navigation_flow.py -v
```

### 특정 테스트만 실행
```bash
# RCM → 설계평가 테스트만
python -m pytest tests/test_navigation_flow.py::test_navigation_rcm_to_design_evaluation -v

# 설계평가 → 운영평가 테스트만
python -m pytest tests/test_navigation_flow.py::test_navigation_design_to_operation_evaluation -v

# 완전한 플로우 테스트만
python -m pytest tests/test_navigation_flow.py::test_complete_navigation_flow -v
```

### 빠른 테스트 (간단한 출력)
```bash
python -m pytest tests/test_navigation_flow.py -q
```

### 실패한 테스트만 재실행
```bash
python -m pytest tests/test_navigation_flow.py --lf -v
```

## 테스트 시나리오 상세

### 시나리오 1: ITGC 완전한 플로우
```
1. RCM 관리 페이지 접속
2. "ITGC 설계평가 시작" 버튼 클릭
3. RCM 선택 (rcm_id=1, evaluation_type=ITGC)
4. 설계평가 페이지로 이동 확인
5. 설계평가 완료
6. "ITGC 운영평가" 버튼 클릭
7. 운영평가 페이지로 이동 확인
```

### 시나리오 2: ELC 완전한 플로우
```
1. RCM 관리 페이지 접속
2. "ELC 설계평가 시작" 버튼 클릭
3. RCM 선택 (rcm_id=14, evaluation_type=ELC)
4. 설계평가 페이지로 이동 확인
5. 설계평가 완료
6. "ELC 운영평가" 버튼 클릭
7. /elc/operation-evaluation 페이지로 이동 확인
```

### 시나리오 3: TLC 완전한 플로우
```
1. RCM 관리 페이지 접속
2. "TLC 설계평가 시작" 버튼 클릭
3. RCM 선택 (rcm_id=15, evaluation_type=TLC)
4. 설계평가 페이지로 이동 확인
5. 설계평가 완료
6. "TLC 운영평가" 버튼 클릭
7. /tlc/operation-evaluation 페이지로 이동 확인
```

## 예상되는 테스트 결과

### 성공 케이스
```
✓ test_navigation_rcm_to_design_evaluation
✓ test_navigation_rcm_to_itgc_design_evaluation
✓ test_navigation_rcm_to_elc_design_evaluation
✓ test_navigation_rcm_to_tlc_design_evaluation
✓ test_navigation_design_to_operation_evaluation
✓ test_navigation_design_to_itgc_operation
✓ test_navigation_design_to_elc_operation
✓ test_navigation_design_to_tlc_operation
✓ test_navigation_operation_back_to_design
✓ test_navigation_operation_back_to_rcm
✓ test_complete_navigation_flow
✓ test_complete_flow_with_all_categories
✓ test_back_button_from_design_evaluation
✓ test_back_button_from_operation_evaluation
✓ test_session_maintained_across_navigation
✓ test_evaluation_type_persists_in_session
✓ test_navigation_without_rcm_selection
✓ test_navigation_with_invalid_rcm_id
✓ test_navigation_without_permission

19 tests passed
```

## 주요 검증 포인트

### 1. URL 라우팅
- `/design-evaluation/rcm` (POST) - RCM 선택 후 설계평가
- `/operation-evaluation` - ITGC 운영평가
- `/elc/operation-evaluation` - ELC 운영평가
- `/tlc/operation-evaluation` - TLC 운영평가

### 2. 세션 데이터
- `current_design_rcm_id` - 선택된 RCM ID
- `current_evaluation_type` - 평가 유형 (ITGC/ELC/TLC)

### 3. POST 데이터
- `rcm_id` - RCM ID
- `evaluation_type` - 평가 유형

### 4. 응답 상태 코드
- `200` - 정상 렌더링
- `302` - 리다이렉트 (로그인, 권한 없음 등)
- `403` - 접근 거부

## 문제 해결

### pytest를 찾을 수 없는 경우
```bash
pip install pytest pytest-mock
```

### 테스트 실패 시
1. `conftest.py` 확인 (fixture 정의)
2. Mock 데이터 확인
3. 세션 설정 확인
4. 로그인 상태 확인

## 관련 파일
- `snowball_link5.py` - RCM 관리 라우트
- `snowball_link6.py` - 설계평가 라우트
- `snowball_link7.py` - 운영평가 라우트
- `link6_design_rcm_detail.jsp` - 설계평가 템플릿
- `link7_operation_evaluation_unified.jsp` - 운영평가 통합 템플릿

## 향후 개선 사항
- [ ] UI 자동화 테스트 추가 (Selenium)
- [ ] E2E 테스트 추가
- [ ] 성능 테스트 추가
- [ ] 동시성 테스트 추가
