# SnowBall 프로젝트 작업 기록

## 2025-10-05 (토)

### ✅ 완료된 작업

#### 1. APD01 표준통제 운영평가 기능 구현
- **파일 위치**: `snowball_link7.py`, `templates/user_operation_evaluation_apd01.jsp`
- **주요 기능**:
  - 사용자 권한 부여 승인 테스트 자동화
  - 엑셀 파일 업로드 → 헤더 자동 인식 → 필드 매핑
  - 모집단에서 표본 자동 추출 (표본 크기 자동 계산)
  - 표본 데이터 테이블 표시 및 승인 정보 입력
  - 팝업 방식으로 구현 (1400x900)
  - 저장 후 부모 창 자동 새로고침

#### 2. APD07 표준통제 운영평가 기능 구현
- **파일 위치**: `snowball_link7.py`, `templates/user_operation_evaluation_apd07.jsp`
- **주요 기능**:
  - 데이터 직접변경 승인 테스트 자동화
  - 필수 필드 단순화: 쿼리(변경내역), 변경일자만 필수
  - 선택 필드 제거로 UI 간소화
  - 팝업 방식 구현 (1600x900)

#### 3. 필드 매핑 UI/UX 개선
- **개선 내용**:
  - 엑셀 업로드 시 헤더 자동 읽기 (XLSX.js 라이브러리 활용)
  - 드롭다운 방식으로 컬럼 선택 (기존: 수동 숫자 입력)
  - 컬럼명과 위치(A열, B열 등) 함께 표시
  - 업로드 후 Step2로 자동 스크롤

#### 4. 파일 관리 모듈 확장
- **파일 위치**: `file_manager.py`
- **추가 함수**:
  - `parse_apd01_population()` - APD01 모집단 파싱
  - `parse_apd07_population()` - APD07 모집단 파싱
  - `calculate_sample_size()` - 표본 크기 자동 계산
  - `select_random_samples()` - 무작위 표본 추출

#### 5. 페이지 스타일 통일
- **변경 내용**:
  - APD01/APD07 팝업 페이지에 `style.css` 적용
  - navi.jsp 제거 (팝업이므로 불필요)
  - 카드 색상 통일: 초록색(통제 정보), 파란색(업로드), 초록색(테스트)
  - 설계평가 페이지와 동일한 디자인 시스템 적용

#### 6. Contact Us → 서비스 문의 변경
- **파일 위치**: `templates/navi.jsp`, `templates/index.jsp`, `templates/contact.jsp`, `snowball.py`
- **주요 변경**:
  - 메뉴명 한글화
  - `/contact` 라우트 추가
  - 서비스 문의 폼 기능 구현
  - 보안 강화:
    - 입력값 Sanitization (이메일 injection 방지)
    - 이메일 형식 검증
    - 에러 메시지 보안 (내부 정보 노출 방지)
    - 관리자 이메일 환경변수화

#### 7. 테스트 데이터 생성
- **파일 위치**: `downloads/APD01_모집단_샘플.xlsx`, `downloads/APD07_모집단_샘플.xlsx`
- **내용**:
  - APD01: 30건의 사용자 권한 데이터
  - APD07: 25건의 데이터 변경 이력
  - 프로젝트 downloads 폴더에 저장 (.gitignore에 포함됨)

#### 8. 코드 리뷰 및 보안 강화
- **도구**: code-reviewer agent 활용
- **적용 사항**:
  - `/contact` 라우트 보안 강화
  - XSS 방지, 입력값 검증, 에러 처리 개선

---

### 📋 내일(10/06) 작업 예정

#### 1. 파일 기반 저장 방식으로 전환 ⭐ 우선순위 높음
- **현재 문제**:
  - 모집단/표본/테스트 결과를 DB에 JSON으로 저장
  - 대용량 데이터 시 DB 부담
  - 증빙 자료 관리 어려움

- **개선 방안**:
  - 파일 기반 저장 구조로 변경
  - 저장 위치: `/static/uploads/operation_evaluations/{rcm_id}/{design_session}/{control_code}/`
  - 파일 구성:
    - `population.xlsx` - 원본 모집단 파일
    - `samples.json` - 선정된 표본 데이터
    - `test_results.json` - 입력한 테스트 결과
  - DB에는 메타데이터만 저장:
    - 파일 경로들
    - population_count
    - sample_size
    - conclusion (satisfactory/deficiency)

- **작업 목록**:
  - [ ] `file_manager.py`에 저장/로드 함수 추가
    - `save_operation_test_data()`
    - `load_operation_test_data()`
  - [ ] DB 스키마 수정
    - `sb_operation_evaluation_line` 테이블에 파일 경로 컬럼 추가
    - 또는 별도 테이블 생성 검토
  - [ ] APD01 API 수정 (`snowball_link7.py`)
    - 업로드 시 파일 저장
    - 저장 시 파일 경로 DB에 기록
  - [ ] APD07 API 수정
  - [ ] 기존 데이터 마이그레이션 고려

#### 2. 운영평가 결과 다운로드 기능 구현
- **기능 설명**:
  - 운영평가 완료 후 엑셀 파일로 다운로드
  - 포함 내용:
    - 통제 정보
    - 모집단 데이터
    - 선정된 표본
    - 테스트 결과 (승인자, 승인일 등)
    - 결론 (만족/미비)

- **작업 목록**:
  - [ ] 다운로드 API 엔드포인트 추가
  - [ ] 엑셀 생성 함수 작성 (openpyxl 활용)
  - [ ] UI에 다운로드 버튼 추가
  - [ ] 템플릿 형식 결정 (감사 증빙용)

#### 3. 추가 표준통제 구현 검토
- APD08, PC01, CO01 등 다른 준비된 표준통제
- APD01/APD07 패턴을 참고하여 확장

---

### 🗂️ 주요 파일 구조

```
snowball/
├── snowball.py                          # /contact 라우트
├── snowball_link7.py                    # 운영평가 관련 라우트 및 API
├── file_manager.py                      # 파일 업로드/다운로드 및 표본 추출
├── templates/
│   ├── navi.jsp                         # 메뉴 (서비스 문의)
│   ├── contact.jsp                      # 서비스 문의 페이지
│   ├── user_operation_evaluation.jsp    # 운영평가 목록
│   ├── user_operation_evaluation_rcm.jsp # RCM별 운영평가
│   ├── user_operation_evaluation_apd01.jsp # APD01 팝업
│   └── user_operation_evaluation_apd07.jsp # APD07 팝업
├── downloads/
│   ├── APD01_모집단_샘플.xlsx          # 테스트 데이터
│   └── APD07_모집단_샘플.xlsx          # 테스트 데이터
└── static/uploads/
    └── operation_evaluations/           # (내일 생성 예정)

```

---

### 📝 참고 사항

#### 표본 크기 계산 로직
```python
모집단 수     표본 수
0            0
1            1
2-4          2
5-12         2
13-52        5
53-250       20
251+         25
```

#### APD01 필수 필드
- 사용자ID
- 사용자명
- 부서명
- 권한명
- 권한부여일

#### APD07 필수 필드
- 쿼리(변경내역)
- 변경일자

---

### 🐛 알려진 이슈
- 없음

### 💡 개선 아이디어
- [ ] 표본 추출 알고리즘 개선 (계층 추출, 체계 추출 등)
- [ ] 운영평가 진행률 표시
- [ ] 일괄 업로드 기능 (여러 통제 동시 처리)
- [ ] 운영평가 템플릿 자동 생성 기능
