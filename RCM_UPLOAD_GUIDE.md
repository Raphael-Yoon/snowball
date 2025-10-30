# RCM 업로드 개선 사항

## 주요 개선 내용

### 1. 멀티라인 헤더 지원
- **문제**: 기존에는 첫 번째 행만 헤더로 인식하여 멀티라인 헤더가 있는 엑셀 파일 업로드 시 오류 발생
- **해결**: "데이터 시작 행" 옵션 추가로 사용자가 헤더 위치 직접 지정 가능
- **사용법**:
  - 기본값: 0 (첫 번째 행이 헤더)
  - 헤더가 3줄인 경우: 2를 입력 (0부터 시작)

### 2. 유연한 컬럼명 매핑
- **문제**: 컬럼명이 정확히 일치하지 않으면 데이터 매핑 실패
- **해결**: 다양한 컬럼명 변형 자동 인식
  - 대소문자 무시 (Control Code = control code = CONTROL CODE)
  - 공백/특수문자 처리 (Control_Code = Control-Code = Control Code)
  - 한글/영문 모두 지원 (통제코드 = Control Code)

### 3. 지원되는 컬럼명 매핑

| 표준 컬럼명 | 인식 가능한 변형들 |
|-------------|-------------------|
| control_code | Control Code, controlcode, 통제코드, 코드, ctrl_code 등 |
| control_name | Control Name, controlname, 통제명, 통제이름, name 등 |
| control_description | Control Description, description, 통제설명, 설명, desc 등 |
| key_control | Key Control, keycontrol, 핵심통제, key, 중요통제 등 |
| control_frequency | Control Frequency, frequency, 통제빈도, 빈도, freq 등 |
| control_type | Control Type, type, 통제유형, 유형 등 |
| control_nature | Control Nature, nature, 통제속성, 속성 등 |
| population | Population, pop, 모집단, 대상 등 |
| population_completeness_check | Completeness Check, 완전성확인, 모집단완전성 등 |
| population_count | Population Count, count, 모집단건수, 건수 등 |
| test_procedure | Test Procedure, procedure, 검증절차, 절차, test 등 |

## 사용 예시

### 예시 1: 기본 사용 (단일 헤더)
```
엑셀 파일 구조:
┌────────────┬────────────┬──────────────┐
│ 통제코드   │ 통제명     │ 통제설명     │
├────────────┼────────────┼──────────────┤
│ ITGC-001   │ 접근통제   │ 권한 관리    │
│ ITGC-002   │ 변경관리   │ 변경 승인    │
└────────────┴────────────┴──────────────┘

업로드 설정:
- 데이터 시작 행: 0 (기본값)
```

### 예시 2: 멀티라인 헤더
```
엑셀 파일 구조:
┌──────────────────┬──────────────────┬───────────────┐
│ IT 일반 통제 대장│ 통제 관리        │ 2024년        │  ← 0행 (제목)
├──────────────────┼──────────────────┼───────────────┤
│ ITGC Controls    │ Control Mgmt     │ Year 2024     │  ← 1행 (부제)
├──────────────────┼──────────────────┼───────────────┤
│ 통제코드         │ 통제명           │ 통제설명      │  ← 2행 (실제 헤더)
├──────────────────┼──────────────────┼───────────────┤
│ ITGC-001         │ 접근통제         │ 권한 관리     │  ← 3행 (데이터)
│ ITGC-002         │ 변경관리         │ 변경 승인     │  ← 4행 (데이터)
└──────────────────┴──────────────────┴───────────────┘

업로드 설정:
- 데이터 시작 행: 2 (3번째 행이 헤더)
```

### 예시 3: 영문 컬럼명
```
엑셀 파일 구조:
┌──────────────┬─────────────────┬────────────────┐
│ Control Code │ Control Name    │ Description    │
├──────────────┼─────────────────┼────────────────┤
│ ELC-001      │ Code of Conduct │ Ethics policy  │
│ ELC-002      │ Risk Assessment │ Risk review    │
└──────────────┴─────────────────┴────────────────┘

업로드 설정:
- 데이터 시작 행: 0
- 자동으로 표준 컬럼명으로 매핑됨
```

## 테스트 파일

프로젝트에 포함된 샘플 파일:
1. `tests/sample_rcm_korean.xlsx` - 한글 컬럼명 (5개 레코드)
2. `tests/sample_rcm_english.xlsx` - 영문 컬럼명 (3개 레코드)
3. `tests/sample_rcm_multiline_header.xlsx` - 멀티라인 헤더 (데이터 시작 행: 2)
4. `tests/sample_rcm_mixed.xlsx` - 한글+영문 혼합 (2개 레코드)

## 데이터 유효성 검증

업로드 시 다음 사항을 자동 검증합니다:
- ✅ 최소 1개 이상의 통제 레코드 존재
- ✅ control_code 또는 control_name 컬럼 필수
- ✅ 빈 행 자동 제거
- ✅ 컬럼명 자동 매핑 및 로그 기록

## 업로드 후 확인사항

업로드 성공 시 다음 정보가 반환됩니다:
```json
{
  "success": true,
  "message": "RCM \"테스트 RCM\"이(가) 성공적으로 업로드되었습니다. (총 5개 통제)",
  "rcm_id": 123,
  "record_count": 5,
  "mapping_info": {
    "통제코드": "control_code",
    "통제명": "control_name",
    "통제설명": "control_description"
  }
}
```

## 문제 해결

### 문제: "통제코드 또는 통제명 컬럼을 찾을 수 없습니다"
- **원인**: 엑셀 파일에 필수 컬럼이 없거나 헤더 행이 잘못 지정됨
- **해결**:
  1. 엑셀 파일에 '통제코드' 또는 'Control Code' 컬럼 추가
  2. '데이터 시작 행' 값 확인 및 수정

### 문제: "엑셀 파일에서 유효한 데이터를 찾을 수 없습니다"
- **원인**: 데이터 행이 모두 비어있거나 헤더 행 지정 오류
- **해결**:
  1. 엑셀 파일에 실제 데이터 행이 있는지 확인
  2. '데이터 시작 행' 값을 조정하여 재시도

### 문제: 업로드는 성공했지만 데이터가 이상함
- **원인**: 잘못된 헤더 행 지정으로 데이터가 헤더로 인식됨
- **해결**:
  1. RCM 삭제
  2. 올바른 '데이터 시작 행' 값으로 재업로드

## 개발자 정보

### 관련 파일
- `snowball/rcm_utils.py` - 엑셀 파싱 및 컬럼 매핑 유틸리티
- `snowball/snowball_link5.py` - RCM 업로드 엔드포인트 (rcm_process_upload)
- `templates/link5_rcm_upload.jsp` - 업로드 UI
- `tests/test_rcm_utils.py` - 단위 테스트
- `tests/create_sample_rcm_excel.py` - 샘플 파일 생성 스크립트

### 테스트 실행
```bash
# 단위 테스트
python tests/test_rcm_utils.py

# 샘플 파일 생성
python tests/create_sample_rcm_excel.py
```

### 컬럼 매핑 추가 방법
`rcm_utils.py`의 `COLUMN_MAPPING` 딕셔너리에 새로운 매핑 추가:
```python
COLUMN_MAPPING = {
    'new_column': [
        'new_column', 'newcolumn', 'new column',
        '새컬럼', '새로운컬럼', '신규컬럼'
    ],
    # ...
}
```
