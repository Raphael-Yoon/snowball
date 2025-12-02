# Attribute 처리 방식 문서

## 개요
Snowball 시스템에서 평가 표본의 모집단 항목과 증빙 항목을 관리하는 방식을 설명합니다.

## 데이터베이스 구조

### sb_evaluation_sample 테이블
- **attribute0 ~ attribute9**: 총 10개의 TEXT 컬럼
  - 모집단 항목과 증빙 항목 데이터를 모두 저장
  - 예: attribute0="2024-001", attribute1="지적번호", attribute2="검토완료", attribute3="승인"

### sb_rcm_detail 테이블
- **population_attribute_count**: INTEGER
  - 모집단 항목이 몇 개인지 정의
  - 예: `population_attribute_count = 2`이면 attribute0, attribute1이 모집단
  - 예: `population_attribute_count = 3`이면 attribute0, attribute1, attribute2가 모집단

## Attribute 구분 로직

### 기본 원칙
```
if (attribute_index < population_attribute_count) {
    // 모집단 항목
} else {
    // 증빙 항목
}
```

### 예시
**Case 1: population_attribute_count = 2**
- attribute0: 모집단 항목 (번호)
- attribute1: 모집단 항목 (설명)
- attribute2: 증빙 항목 1
- attribute3: 증빙 항목 2
- attribute4: 증빙 항목 3

**Case 2: population_attribute_count = 3**
- attribute0: 모집단 항목 (번호)
- attribute1: 모집단 항목 (설명)
- attribute2: 모집단 항목 (추가 필드)
- attribute3: 증빙 항목 1
- attribute4: 증빙 항목 2

## 모집단 업로드 시 처리 (표본수 0인 통제)

### 1. 데이터 저장
모집단 엑셀 업로드 시 항상 **attribute0**부터 순서대로 저장:
- attribute0: 엑셀의 "번호" 컬럼 매핑 값
- attribute1: 엑셀의 "설명" 컬럼 매핑 값
- attribute2~9: 비어있음 (증빙 항목으로 나중에 입력)

### 2. Attribute 정의 생성
API 응답으로 attributes 배열 반환:
```json
{
  "attributes": [
    {
      "attribute": "attribute0",
      "name": "지적번호",  // 엑셀 헤더에서 가져온 이름
      "type": "population"
    },
    {
      "attribute": "attribute1",
      "name": "지적사항",  // 엑셀 헤더에서 가져온 이름
      "type": "population"
    },
    {
      "attribute": "attribute2",
      "name": "증빙 항목 1",  // 기본 이름
      "type": "evidence"
    }
  ],
  "population_attribute_count": 2
}
```

### 3. 코드 위치
**Backend: `snowball_link7.py`**
```python
# 모집단 업로드 API (1943-1987줄)
@bp_link7.route('/api/operation-evaluation/upload-population')

# 1. RCM detail에서 population_attribute_count 조회
population_attr_count = rcm_detail['population_attribute_count'] or 2

# 2. 샘플 데이터에서 실제 사용된 attribute 확인
used_attributes = set()
for sample in saved_samples:
    for i in range(10):
        if sample[f'attribute{i}'] is not None:
            used_attributes.add(i)

# 3. attribute 정의 생성
for i in sorted(used_attributes):
    if i < population_attr_count:
        attr_type = 'population'
        name = number_col_name if i == 0 else desc_col_name if i == 1 else f'모집단 항목 {i+1}'
    else:
        attr_type = 'evidence'
        name = f'증빙 항목 {i - population_attr_count + 1}'
```

**Frontend: `link7_detail.jsp`**
```javascript
// 테이블 헤더 생성 (3223-3233줄)
const popAttrCount = window.currentPopulationAttributeCount || 0;
attributes.forEach((attr, index) => {
    const isPopulation = index < popAttrCount;
    const badge = isPopulation
        ? '<span class="badge bg-primary">모집단</span>'
        : '<span class="badge bg-success">증빙</span>';
    headerHtml += `<th>${attr.name}${badge}</th>`;
});

// 테이블 바디 생성 (3271-3283줄)
attributes.forEach(attr => {
    const attrValue = sample?.attributes?.[attr.attribute] || '';
    const isPopulation = attr.type === 'population';
    // 모집단 항목은 readonly로 설정
    rowHtml += `<input ... ${isPopulation ? 'readonly' : ''}>`;
});
```

## 샘플 데이터 조회 시 처리

### API: `/api/operation-evaluation/samples/<line_id>`
**Backend: `snowball_link7.py` (488-525줄)**
```python
# 1. 샘플 데이터 조회
sample_lines = get_operation_evaluation_samples(line_id)

# 2. RCM detail에서 attributes 정보 조회
rcm_detail = conn.execute('''
    SELECT population_attribute_count
    FROM sb_rcm_detail
    WHERE rcm_id = %s AND control_code = %s
''', ...).fetchone()

# 3. 응답 반환
return jsonify({
    'samples': sample_lines,
    'attributes': attributes,
    'population_attribute_count': population_attribute_count
})
```

**Frontend: `link7_detail.jsp` (1338-1344줄)**
```javascript
// attributes가 있으면 generateSampleLinesWithAttributes 사용
if (data.attributes && data.attributes.length > 0) {
    generateSampleLinesWithAttributes(data.attributes, data.samples.length);
} else {
    generateSampleLines();
}
```

## 주의사항

### ❌ 잘못된 가정
- "attribute0, attribute1은 항상 모집단이다" ← **틀림**
- "attributes는 JSON 컬럼에 저장된다" ← **틀림** (실제로는 attribute0~9 컬럼에 데이터 저장)

### ✅ 올바른 이해
- **population_attribute_count**를 기준으로 모집단/증빙 구분
- attribute0~9 컬럼에 실제 데이터 저장
- 샘플 데이터를 확인하여 실제 사용된 attribute만 표시
- RCM detail의 설정에 따라 동적으로 처리

## 테이블 UI 표시

### 헤더 예시
```
| 표본 # | 증빙 내용 | 지적번호 🔵모집단 | 지적사항 🔵모집단 | 검토결과 🟢증빙 | 결과 |
```

### 데이터 입력
- 모집단 항목: readonly (모집단 업로드로 자동 채워짐)
- 증빙 항목: 편집 가능 (사용자가 직접 입력)

## 엑셀 다운로드 시 처리

### Testing Table 시트
- Row 4: 헤더
  - 모집단 항목: 노란색 배경 (PatternFill: 'FFFF00')
  - 증빙 항목: 초록색 배경 (PatternFill: '00FF00')
- Row 5~: 샘플 데이터
  - attribute0~9의 값을 해당 컬럼에 출력

**코드 위치: `snowball_link7.py` (2286-2297줄)**
```python
for row_idx, sample in enumerate(samples, start=5):
    sample_attributes = sample.get('attributes', {})
    for i in range(10):
        attr_key = f'attribute{i}'
        if attr_key in sample_attributes:
            # 컬럼 인덱스: B(2) + 모집단 개수(population_count) + 증빙 개수(evidence_count) + attribute 인덱스
            col_idx = 2 + population_count + evidence_count + i
            cell = testing_table.cell(row=row_idx, column=col_idx)
            cell.value = sample_attributes[attr_key]
```

## 디버깅 팁

### 1. 콘솔 로그 확인
```javascript
console.log('[uploadPopulationFile] attributes:', data.attributes);
console.log('[uploadPopulationFile] population_attribute_count:', data.population_attribute_count);
```

### 2. 서버 로그 확인
```python
print(f"[upload_general_population] RCM detail population_attribute_count: {population_attr_count}")
print(f"[upload_general_population] 사용된 attributes: {sorted(used_attributes)}")
print(f"[upload_general_population] attributes 생성: {attributes}")
```

### 3. 데이터베이스 확인
```sql
-- RCM detail 설정 확인
SELECT control_code, population_attribute_count
FROM sb_rcm_detail
WHERE rcm_id = ? AND control_code = ?;

-- 샘플 데이터 확인
SELECT sample_number, attribute0, attribute1, attribute2, attribute3, attribute4
FROM sb_evaluation_sample
WHERE line_id = ?;
```

## 관련 파일
- `c:\Pythons\snowball\snowball_link7.py`: 백엔드 API
- `c:\Pythons\snowball\templates\link7_detail.jsp`: 프론트엔드 UI
- `c:\Pythons\snowball\auth.py`: 샘플 데이터 조회 함수
- `c:\Pythons\snowball\work_log.md`: 변경 이력
