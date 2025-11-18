# 모집단 업로드 기능 구현 완료 보고서

## 구현 일자
2025-11-17

## 구현 개요
표본 크기가 0으로 설정된 통제에 대해 범용 모집단 업로드 기능을 구현하였습니다.
사용자가 Excel 파일을 업로드하면 자동으로 표본이 추출되며, 증빙 항목(attribute) 필드를 설정할 수 있습니다.

## 주요 변경 사항

### 1. 프론트엔드 변경 (link7_detail.jsp)

#### 1.1 모집단 업로드 UI 추가 (라인 299-357)
- Excel 파일 업로드 입력 필드
- 필드 매핑 UI (번호, 설명)
- 업로드 결과 표시
- Attribute 설정 테이블 (attribute0~10)

#### 1.2 JavaScript 함수 추가 (라인 2510-2738)

**handlePopulationFileSelected()**
- SheetJS를 사용하여 클라이언트에서 Excel 헤더 읽기
- 파일 선택 시 필드 매핑 UI 표시

**showFieldMapping(headers)**
- Excel 컬럼을 필수 필드(번호, 설명)에 매핑하는 UI 생성

**uploadPopulationFile()**
- FormData를 사용하여 서버에 파일 및 매핑 정보 전송
- 업로드 성공 시 attribute 설정 UI로 전환

**showAttributeSettings()**
- attribute0~10 필드 설정 테이블 생성
- 각 attribute의 사용 여부와 필드명 입력 가능

**saveAttributeSettings()**
- 설정된 attribute 정보를 서버에 저장
- 저장 완료 후 모달 닫기 및 페이지 새로고침

#### 1.3 모달 열기 로직 수정 (라인 1060-1071)
```javascript
if (recommendedSampleSize === 0) {
    // 표본수가 0이면 모집단 업로드 UI 표시
    if (populationUploadSection) populationUploadSection.style.display = 'block';
    if (evaluationFields) evaluationFields.style.display = 'none';
} else {
    // 표본수가 0이 아니면 기존 평가 UI 표시
    if (populationUploadSection) populationUploadSection.style.display = 'none';
    if (evaluationFields) evaluationFields.style.display = 'block';
}
```

### 2. 백엔드 변경 (snowball_link7.py)

#### 2.1 모집단 업로드 API (라인 1679-1860)
**엔드포인트**: `/api/operation-evaluation/upload-population`
**메서드**: POST
**기능**:
- Excel 파일 업로드 및 검증 (.xlsx, .xlsm만 허용)
- openpyxl을 사용한 파일 파싱
- 필드 매핑에 따른 모집단 데이터 추출
- 표본 크기 자동 계산 (file_manager.calculate_sample_size 사용)
- 무작위 표본 추출 (random.sample)
- DB에 header/line/sample 데이터 저장
- 한글 파일명 처리 개선

**처리 로직**:
1. 파일 및 파라미터 검증
2. 파일을 `uploads/populations/` 디렉토리에 저장
3. Excel 파일 읽기 (openpyxl read_only 모드)
4. 필드 매핑에 따라 번호, 설명 추출
5. 모집단 크기에 따른 표본 크기 계산
6. 무작위 표본 추출
7. 운영평가 세션 확인/생성
8. Header 확인/생성
9. Line 확인/업데이트 또는 생성
10. Sample 데이터 저장 (evidence 필드에 번호, 설명 저장)

#### 2.2 Attribute 설정 저장 API (라인 1863-1890)
**엔드포인트**: `/api/operation-evaluation/save-attributes`
**메서드**: POST
**기능**:
- Attribute 설정 정보 수신 (line_id, attributes 배열)
- 현재는 로그로만 출력 (향후 DB 스키마에 따라 확장 가능)

### 3. 표본 크기 계산 로직 (file_manager.py)

**함수**: `calculate_sample_size(population_count)`
**로직** (라인 239-278):
- 모집단 0개 → 표본 0개
- 모집단 1개 → 표본 1개
- 모집단 2~4개 → 표본 2개
- 모집단 5~12개 → 표본 2개
- 모집단 13~52개 → 표본 5개
- 모집단 53~250개 → 표본 20개
- 모집단 250개 이상 → 표본 25개

**검증**: 모든 테스트 케이스 통과 확인

## 해결된 문제들

### 문제 1: 모달창이 열리지 않음
**원인**: `initializePopulationUpload()` 함수가 정의되지 않음
**해결**: 함수 호출 주석 처리 및 null 체크 추가

### 문제 2: pandas 모듈 없음
**원인**: Python 3.14에 pandas가 설치되지 않음
**해결**: openpyxl만 사용하도록 변경

### 문제 3: .xls 파일 지원 불가
**원인**: openpyxl은 .xls 형식을 지원하지 않음
**해결**: 파일 확장자 검증 추가, .xlsx/.xlsm만 허용

### 문제 4: 한글 파일명 처리
**원인**: secure_filename()이 한글 문자를 제거
**해결**: 확장자를 별도로 추출하여 재구성

### 문제 5: DB 컬럼 오류
**원인**: population_file_path, population_count 컬럼 없음
**해결**: INSERT/UPDATE 문에서 해당 컬럼 제거

### 문제 6: SQLite vs MySQL 함수
**원인**: LAST_INSERT_ID() (MySQL) 사용
**해결**: last_insert_rowid() (SQLite)로 변경

### 문제 7: Attribute 필드 오해
**원인**: Attribute를 Excel 컬럼에 매핑하려 함
**해결**: Attribute는 증빙 항목으로, Excel과 별개로 필드명만 설정

## 테스트 결과

### 단위 테스트
✅ 표본 크기 계산 로직 - 모든 케이스 통과
✅ Excel 파일 읽기 - 정상 작동
✅ 무작위 표본 추출 - 정상 작동
✅ 모듈 임포트 - 구문 오류 없음

### 통합 테스트
✅ Flask 서버 시작 - 정상
✅ 업로드 디렉토리 생성 - 정상
✅ API 엔드포인트 등록 - 정상

### 파일 검증
✅ link7_detail.jsp - 구문 오류 없음
✅ snowball_link7.py - 구문 오류 없음
✅ file_manager.py - 기존 함수 정상 작동

## 사용 시나리오

### 1. 모집단 업로드
1. 운영평가 화면에서 표본 크기가 0인 통제 선택
2. 평가 모달에서 모집단 업로드 섹션 표시 확인
3. Excel 파일 (.xlsx) 선택
4. 필드 매핑 (번호, 설명) 설정
5. "업로드 및 표본 추출" 버튼 클릭
6. 모집단 수 및 자동 계산된 표본 수 확인

### 2. Attribute 설정
1. 업로드 성공 후 attribute 설정 테이블 표시
2. 사용할 attribute 체크박스 선택 (attribute0~10)
3. 각 attribute의 필드명 입력 (예: 승인자, 승인일자, 요청번호)
4. "저장 및 완료" 버튼 클릭
5. 모달 닫힘 및 페이지 새로고침

## 데이터베이스 스키마

### sb_operation_evaluation_header
- header_id (PK)
- rcm_id
- user_id
- evaluation_session
- design_evaluation_session
- ...

### sb_operation_evaluation_line
- line_id (PK)
- header_id (FK)
- control_code
- sample_size (자동 계산된 표본 수 저장)
- ...

### sb_operation_evaluation_sample
- sample_id (PK)
- line_id (FK)
- sample_number (표본 번호)
- evidence (번호, 설명 저장)
- population_data (NULL)
- ...

## 향후 개선 사항

### 1. Attribute 메타데이터 저장
현재는 attribute 설정이 로그로만 출력됩니다.
향후 DB 스키마를 확장하여 attribute 메타데이터를 저장하고,
표본 테이블에서 동적으로 컬럼을 표시할 수 있도록 개선 필요.

**제안**:
- `sb_operation_evaluation_line_attributes` 테이블 생성
- 컬럼: line_id, attribute_name (attribute0~10), display_name, is_enabled

### 2. 업로드된 표본 데이터 표시
현재 표본 데이터는 DB에 저장되지만, 모달을 다시 열었을 때 표시되지 않을 수 있습니다.
이는 `evaluated_controls` 딕셔너리가 `conclusion` 값이 있는 경우만 채워지기 때문입니다.

**제안**:
- 페이지 로드 시 표본 데이터도 함께 로드
- 표본 테이블 UI 추가하여 업로드된 표본 표시

### 3. 모집단 파일 다운로드
업로드한 모집단 파일을 나중에 다시 다운로드할 수 있는 기능 추가.

### 4. 표본 재추출
모집단은 유지하되 표본만 다시 추출하는 기능 추가.

## 관련 파일

- `C:\Pythons\snowball\templates\link7_detail.jsp` - 프론트엔드 UI
- `C:\Pythons\snowball\snowball_link7.py` - 백엔드 API
- `C:\Pythons\snowball\file_manager.py` - 표본 크기 계산 로직
- `C:\Pythons\snowball\test_population.xlsx` - 테스트용 Excel 파일
- `C:\Pythons\snowball\uploads\populations\` - 업로드 파일 저장 디렉토리

## 의존성

- Flask
- openpyxl
- werkzeug
- SheetJS (XLSX.js) - 클라이언트 측 Excel 파싱

## 주의사항

1. **.xls 파일은 지원하지 않습니다** - Excel에서 .xlsx로 변환 후 업로드 필요
2. **로그인 필요** - @login_required 데코레이터 적용
3. **파일 크기 제한** - 서버 설정에 따라 업로드 파일 크기 제한 가능
4. **한글 파일명** - 안전하게 처리되지만 가능하면 영문 파일명 권장

## 서버 실행

```bash
cd C:\Pythons\snowball
python snowball.py
```

서버는 http://127.0.0.1:5001 에서 실행됩니다.

## 테스트 데이터 생성

```bash
cd C:\Pythons\snowball
python -c "
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws.title = '모집단'
ws.append(['번호', '설명', '비고'])
for i in range(1, 31):
    ws.append([f'POP-{i:03d}', f'테스트 항목 {i}', f'비고 {i}'])
wb.save('test_population.xlsx')
print('테스트 파일 생성 완료')
"
```

## 구현 완료 확인

- [x] 모집단 업로드 UI 추가
- [x] 필드 매핑 기능
- [x] 표본 크기 자동 계산
- [x] 무작위 표본 추출
- [x] DB에 데이터 저장
- [x] Attribute 설정 UI
- [x] Attribute 저장 API
- [x] 한글 파일명 처리
- [x] 파일 형식 검증
- [x] 에러 처리 및 로깅
- [x] 단위 테스트
- [x] 서버 실행 확인

## 작성자
Claude Code Agent

## 검토 필요 사항
- Attribute 메타데이터 저장 방식 결정
- 업로드된 표본 데이터 표시 방법
- 데이터 지속성 문제 (페이지 새로고침 시 표본 표시)
