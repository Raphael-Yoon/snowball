# Population Attribute Count 구현 완료

## 구현 일시
2025-11-18

## 목적
통제별로 attribute 필드 중 모집단 항목과 증빙 항목을 구분하기 위해 `population_attribute_count` 필드를 추가했습니다.

## 배경
- 각 통제마다 attribute0~9 필드를 가지지만, 일부는 모집단 데이터용이고 일부는 증빙 데이터용입니다
- 예시:
  - 통제 A: attribute0~2(모집단 3개) + attribute3~5(증빙 3개)
  - 통제 B: attribute0~4(모집단 5개) + attribute5~6(증빙 2개)
- 이를 구분하기 위해 "모집단 항목 수"를 저장하는 필드가 필요했습니다

## 구현 내용

### 1. 데이터베이스 변경

#### Migration 파일
**파일**: `C:\Pythons\snowball\migrations\versions\018_add_population_attribute_count.py`

```python
def upgrade(conn):
    """sb_rcm_detail 테이블에 population_attribute_count 컬럼 추가"""
    try:
        conn.execute('''
            ALTER TABLE sb_rcm_detail
            ADD COLUMN population_attribute_count INTEGER DEFAULT 2
        ''')
        conn.commit()
```

**변경사항**:
- `sb_rcm_detail` 테이블에 `population_attribute_count` 컬럼 추가
- 타입: INTEGER
- 기본값: 2 (번호, 설명)

### 2. 프론트엔드 변경

#### Admin RCM View
**파일**: `C:\Pythons\snowball\templates\admin_rcm_view.jsp`

**변경사항**:
1. 모달에 "모집단 항목 수" 입력 필드 추가 (라인 322-338)
```html
<div class="mb-3">
    <label for="population-attr-count" class="form-label">
        <strong>모집단 항목 수</strong>
        <small class="text-muted">(attribute0부터 시작, 나머지는 증빙 항목)</small>
    </label>
    <input type="number"
           class="form-control form-control-sm"
           id="population-attr-count"
           min="1"
           max="10"
           value="2"
           style="width: 100px;"
           placeholder="예: 2">
    <small class="text-muted">
        예: 2로 설정 시 attribute0~1은 모집단, attribute2~9는 증빙
    </small>
</div>
```

2. JavaScript loadAttributes() 함수 수정 (라인 609-613)
```javascript
// population_attribute_count 로드
const popCountInput = document.getElementById('population-attr-count');
if (popCountInput) {
    popCountInput.value = data.population_attribute_count || 2;
}
```

3. JavaScript saveAttributes() 함수 수정 (라인 639-651)
```javascript
// population_attribute_count 수집
const popCountInput = document.getElementById('population-attr-count');
const populationAttributeCount = popCountInput ? parseInt(popCountInput.value) : 2;

// 서버에 저장
fetch(`/admin/rcm/detail/${currentDetailId}/attributes`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        attributes,
        population_attribute_count: populationAttributeCount
    })
})
```

#### User RCM View (Link5)
**파일**: `C:\Pythons\snowball\templates\link5_rcm_view.jsp`

**변경사항**: Admin view와 동일한 변경사항 적용
- 모달에 "모집단 항목 수" 입력 필드 추가 (라인 322-338)
- JavaScript loadAttributes() 함수 수정 (라인 613-617)
- JavaScript saveAttributes() 함수 수정 (라인 643-656)

### 3. 백엔드 변경

#### Admin API
**파일**: `C:\Pythons\snowball\snowball_admin.py`

**GET /admin/rcm/detail/<detail_id>/attributes** (라인 1180-1215)
```python
# SQL 쿼리에 population_attribute_count 추가
cursor = db.execute('''
    SELECT attribute0, attribute1, attribute2, attribute3, attribute4,
           attribute5, attribute6, attribute7, attribute8, attribute9,
           population_attribute_count
    FROM sb_rcm_detail
    WHERE detail_id = ?
''', (detail_id,))

# 응답에 population_attribute_count 포함
population_attr_count = row[10] if len(row) > 10 and row[10] is not None else 2

return jsonify({
    'success': True,
    'attributes': attributes,
    'population_attribute_count': population_attr_count
})
```

**POST /admin/rcm/detail/<detail_id>/attributes** (라인 1230-1264)
```python
# 요청에서 population_attribute_count 받기
data = request.get_json()
attributes = data.get('attributes', {})
population_attribute_count = data.get('population_attribute_count', 2)

# UPDATE 쿼리에 population_attribute_count 포함
db.execute('''
    UPDATE sb_rcm_detail
    SET attribute0 = ?, attribute1 = ?, attribute2 = ?, attribute3 = ?, attribute4 = ?,
        attribute5 = ?, attribute6 = ?, attribute7 = ?, attribute8 = ?, attribute9 = ?,
        population_attribute_count = ?
    WHERE detail_id = ?
''', (*attr_values, population_attribute_count, detail_id))
```

#### User API (Link5)
**파일**: `C:\Pythons\snowball\snowball_link5.py`

**변경사항**: Admin API와 동일한 변경사항 적용
- GET `/api/rcm/detail/<detail_id>/attributes` (라인 1788-1826)
- POST `/api/rcm/detail/<detail_id>/attributes` (라인 1838-1873)

## 사용 방법

### 1. RCM 설정 페이지에서 Attribute 설정

1. **Admin RCM 관리**: http://127.0.0.1:5001/admin/rcm/18
   - 또는 **User RCM 보기**: http://127.0.0.1:5001/rcm/18/view

2. 각 통제의 "Attribute 설정" 버튼 클릭

3. 모달에서:
   - **모집단 항목 수** 설정 (예: 2)
   - **attribute0~9** 필드명 입력
     - attribute0: 번호
     - attribute1: 설명
     - attribute2: 완료예정일 (증빙)
     - attribute3: 완료여부 (증빙)
     - ...

4. "저장" 버튼 클릭

### 2. 의미

- **모집단 항목 수 = 2**로 설정한 경우:
  - attribute0, attribute1: 모집단 항목 (Excel에서 가져올 필드)
  - attribute2~9: 증빙 항목 (사용자가 입력할 필드)

- **모집단 항목 수 = 5**로 설정한 경우:
  - attribute0~4: 모집단 항목
  - attribute5~9: 증빙 항목

### 3. 향후 활용

이 설정은 다음과 같이 활용됩니다:

1. **모집단 업로드 시**:
   - RCM 설정에서 `population_attribute_count` 조회
   - 모집단 항목 개수만큼 Excel 매핑 UI 생성
   - 예: `population_attribute_count = 3`이면 attribute0, attribute1, attribute2 매핑

2. **운영평가 표본 입력 시**:
   - 모집단 항목(0~N-1)은 읽기 전용으로 표시
   - 증빙 항목(N~9)은 편집 가능으로 표시

## 테스트

### 서버 실행
```bash
cd C:\Pythons\snowball
python snowball.py
```

서버 URL:
- http://127.0.0.1:5001
- http://192.168.45.27:5001

### 테스트 시나리오

1. **Admin 페이지 테스트**:
   - http://127.0.0.1:5001/admin/rcm/18 접속
   - 통제 선택 후 "Attribute 설정" 클릭
   - "모집단 항목 수" 필드 확인
   - 값 변경 후 저장
   - 모달 닫고 재오픈하여 값 유지 확인

2. **User 페이지 테스트**:
   - http://127.0.0.1:5001/rcm/18/view 접속
   - 동일한 테스트 수행

3. **API 테스트**:
   - GET 요청 시 `population_attribute_count` 반환 확인
   - POST 요청 시 `population_attribute_count` 저장 확인
   - 기본값 2가 정상 작동하는지 확인

## 구현 완료 항목

✅ Database migration 파일 생성 (018)
✅ sb_rcm_detail 테이블에 population_attribute_count 컬럼 추가
✅ admin_rcm_view.jsp 모달에 입력 필드 추가
✅ admin_rcm_view.jsp JavaScript 함수 업데이트
✅ link5_rcm_view.jsp 모달에 입력 필드 추가
✅ link5_rcm_view.jsp JavaScript 함수 업데이트
✅ snowball_admin.py GET API 업데이트
✅ snowball_admin.py POST API 업데이트
✅ snowball_link5.py GET API 업데이트
✅ snowball_link5.py POST API 업데이트
✅ Flask 서버 재시작

## 다음 단계

1. **모집단 업로드 로직 업데이트**:
   - RCM attribute 설정 조회
   - `population_attribute_count` 기반으로 Excel 매핑 UI 생성
   - 모집단 항목만 매핑하여 샘플 데이터 생성

2. **운영평가 표본 표시 로직 업데이트**:
   - `population_attribute_count` 조회
   - 모집단 항목(0~N-1)은 읽기 전용
   - 증빙 항목(N~9)은 편집 가능

3. **유효성 검증 추가**:
   - `population_attribute_count`는 1~10 범위 내
   - attribute 개수보다 클 수 없음

## 관련 파일

### Migration
- `C:\Pythons\snowball\migrations\versions\018_add_population_attribute_count.py`

### 템플릿
- `C:\Pythons\snowball\templates\admin_rcm_view.jsp`
- `C:\Pythons\snowball\templates\link5_rcm_view.jsp`

### 백엔드
- `C:\Pythons\snowball\snowball_admin.py`
- `C:\Pythons\snowball\snowball_link5.py`

### 문서
- `C:\Pythons\snowball\IMPLEMENTATION_SUMMARY.txt` (기존 모집단 업로드 구현)
- `C:\Pythons\snowball\POPULATION_ATTRIBUTE_COUNT_IMPLEMENTATION.md` (이 문서)

## 작업 완료
2025-11-18 - population_attribute_count 필드 구현 완료
