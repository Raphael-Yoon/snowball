# 설계평가-운영평가 샘플 연계 방안

## 배경

### 현재 상황
- **설계평가**: 표본 1개 테스트
- **운영평가**: 표본 N개 테스트 (표본수 0인 경우 모집단 전체)
- **문제**: 설계평가에서 이미 테스트한 샘플을 운영평가에서 다시 테스트하는 중복 발생

### 목표
설계평가의 1개 샘플 = 운영평가의 N개 샘플 중 1개로 활용

## 데이터 구조

### sb_evaluation_sample 테이블
```sql
CREATE TABLE sb_evaluation_sample (
    sample_id INTEGER PRIMARY KEY,
    line_id INTEGER,
    sample_number INTEGER,
    evaluation_type TEXT,  -- 'design' 또는 'operation'
    attribute0 TEXT,       -- 모집단 항목 1
    attribute1 TEXT,       -- 모집단 항목 2
    attribute2 TEXT,       -- 증빙 항목 1
    attribute3 TEXT,       -- 증빙 항목 2
    ...
);
```

### 작동 방식
설계평가 데이터: '문서1'
운영평가 모집단(표본 3개 필요): 1, 2, 3, 4, 5, 6, 7, 8, 9

기존 방식은 운영평가 모집단에서 무작위로 3개 추출: 1, 3, 5
따라서 화면에는 아래와 같이 나옴
모집단  증빙
1   (공란) 
3   (공란)
5   (공란)

여기서 설계평가에 입력한 '문서1'이라는 증빙이 1번 표본의 증빙인 경우 이렇게 나와야 함
1   문서1
3   (공란)
5   (공란)
하지만 표본1과 '문서1'과의 매핑키가 없음
따라서 이렇게 나오면 될 것 같음
일단 표본은 정해진 표본수-1로 생성
모집단  증빙
(공란)  '문서1'
3   (공란)
5   (공란)
여기서 첫번째 행은 설계평가 데이터이므로 모집단을 드롭박스 형태로 모집단 데이터에서 선택할 수 있도록 구성
2, 3번 행은 무작위 추출된 표본이므로 지금처럼 수정안되게 고정하고 증빙을 입력할 수 있도록 구성성

### 예시 데이터

**설계평가 (1개 샘플):**
```
sample_id: 100
line_id: 1
sample_number: 1
evaluation_type: 'design'
attribute0: '2024-001'
attribute1: 'ABC 문서'
attribute2: '2024-01-15'
attribute3: '완료'
```

**운영평가 (5개 샘플):**
```
sample_id: 201, line_id: 1, sample_number: 1, evaluation_type: 'operation'
  attribute0='2024-001', attribute1='ABC 문서', attribute2='2024-01-15', attribute3='완료'

sample_id: 202, line_id: 1, sample_number: 2, evaluation_type: 'operation'
  attribute0='2024-002', attribute1='DEF 문서', attribute2='2024-02-01', attribute3='진행중'

sample_id: 203, line_id: 1, sample_number: 3, evaluation_type: 'operation'
  attribute0='2024-003', attribute1='GHI 문서', attribute2='2024-03-01', attribute3='완료'
...
```

→ 운영평가의 첫 번째 샘플(201)이 설계평가 샘플(100)과 동일

## 해결 방안

### 방안 1: 자동 매칭 (추천)

#### 개념
모집단 업로드 시 attribute 값을 비교하여 설계평가 샘플과 일치하는 항목을 자동으로 찾아서 연결

#### 매칭 조건
- `attribute0` (모집단 항목 1) 일치
- `attribute1` (모집단 항목 2) 일치
- 선택적: 추가 attribute도 비교 가능

#### 구현 방법

**1. 매칭 플래그 추가**
```python
# sb_evaluation_sample 테이블에 컬럼 추가 (선택사항)
ALTER TABLE sb_evaluation_sample ADD COLUMN linked_sample_id INTEGER;

# 또는 메모리에서만 관리 (frontend)
sample['is_design_evaluated'] = True
```

**2. 매칭 로직 (Backend)**
```python
# snowball_link7.py - 모집단 업로드 API
def upload_population():
    # 1. 모집단 데이터 저장
    for idx, sample in enumerate(samples, 1):
        conn.execute('''
            INSERT INTO sb_evaluation_sample
            (line_id, sample_number, evaluation_type, attribute0, attribute1, ...)
            VALUES (%s, %s, %s, %s, %s, ...)
        ''', (line_id, idx, 'operation', sample['attribute0'], sample['attribute1'], ...))

    # 2. 설계평가 샘플 조회
    design_sample = conn.execute('''
        SELECT sample_id, attribute0, attribute1, attribute2, attribute3
        FROM sb_evaluation_sample
        WHERE line_id = %s AND evaluation_type = 'design'
    ''', (line_id,)).fetchone()

    # 3. 운영평가 샘플과 매칭
    matched_sample_id = None
    if design_sample:
        operation_samples = conn.execute('''
            SELECT sample_id, sample_number, attribute0, attribute1
            FROM sb_evaluation_sample
            WHERE line_id = %s AND evaluation_type = 'operation'
        ''', (line_id,)).fetchall()

        for op_sample in operation_samples:
            if (op_sample['attribute0'] == design_sample['attribute0'] and
                op_sample['attribute1'] == design_sample['attribute1']):
                matched_sample_id = op_sample['sample_id']
                break

    # 4. 응답에 매칭 정보 포함
    return jsonify({
        'success': True,
        'samples': sample_lines,
        'design_sample_match': {
            'matched': matched_sample_id is not None,
            'sample_number': matched_sample_number if matched_sample_id else None,
            'design_sample': design_sample if design_sample else None
        }
    })
```

**3. UI 표시 (Frontend)**
```javascript
// link7_detail.jsp - generateSampleLinesWithAttributes()
function generateSampleLinesWithAttributes(attributes, sampleSize, designMatch) {
    // 테이블 생성 시
    for (let i = 1; i <= sampleSize; i++) {
        const sample = existingSampleLines.find(s => s.sample_number === i);

        // 설계평가와 매칭된 샘플인지 확인
        const isDesignSample = designMatch && designMatch.matched &&
                              designMatch.sample_number === i;

        let rowHtml = `<td class="text-center align-middle">
            #${i}
            ${isDesignSample ? '<span class="badge bg-info ms-1" title="설계평가 완료">설계</span>' : ''}
        </td>`;

        // ... 나머지 컬럼
    }
}
```

**4. UI 예시**
```
┌────┬────────┬──────────┬────────┬────────┬──────┐
│ #  │ 번호   │ 문서번호  │ 완료일 │ 완료   │ 결과 │
├────┼────────┼──────────┼────────┼────────┼──────┤
│ #1 │2024-001│ABC 문서   │2024-01│완료    │ ✓    │
│설계│        │           │        │        │      │
├────┼────────┼──────────┼────────┼────────┼──────┤
│ #2 │2024-002│DEF 문서   │2024-02│진행중  │      │
├────┼────────┼──────────┼────────┼────────┼──────┤
│ #3 │2024-003│GHI 문서   │2024-03│완료    │      │
└────┴────────┴──────────┴────────┴────────┴──────┘

"설계" 배지: 이 샘플은 설계평가에서 이미 테스트 완료
```

#### 장점
- 자동화 - 사용자 개입 불필요
- 직관적 - 배지로 명확히 표시
- 중복 작업 방지 - 설계평가 완료 샘플 확인 가능

#### 단점
- 매칭 실패 가능성 (데이터 불일치 시)
- 추가 로직 필요

---

### 방안 2: 수동 선택

#### 개념
운영평가 모달에서 사용자가 직접 "이 샘플은 설계평가 샘플입니다" 지정

#### UI
```
┌─────────────────────────────────────────────┐
│ 설계평가 샘플 정보:                          │
│ 번호: 2024-001, 문서: ABC 문서              │
│ 완료일: 2024-01-15, 완료여부: 완료          │
│                                             │
│ ▼ 표본 #1을 설계평가 샘플로 지정            │
└─────────────────────────────────────────────┘

표본별 테스트 결과:
┌────┬────────┬──────────┬────────┬────────┐
│ #1 │2024-001│ABC 문서   │2024-01│완료    │ ← 설계평가
│ #2 │2024-002│DEF 문서   │        │        │
│ #3 │2024-003│GHI 문서   │        │        │
└────┴────────┴──────────┴────────┴────────┘
```

#### 구현
```javascript
// 드롭다운으로 선택
function setDesignSample(sampleNumber) {
    // 해당 샘플에 플래그 설정
    // UI 업데이트
}
```

#### 장점
- 유연성 - 사용자가 원하는 샘플 선택 가능
- 매칭 실패 걱정 없음

#### 단점
- 수동 작업 필요
- UI 복잡도 증가

---

### 방안 3: 자동 매칭 + 수동 수정 (최적)

#### 개념
1. 기본적으로 자동 매칭 시도
2. 매칭 실패 시 사용자에게 선택 UI 제공
3. 매칭 성공해도 사용자가 변경 가능

#### UI 시나리오

**시나리오 1: 자동 매칭 성공**
```
┌─────────────────────────────────────────────┐
│ ✓ 설계평가 샘플 자동 매칭 완료: 표본 #1     │
│ [변경]                                      │
└─────────────────────────────────────────────┘

표본별 테스트 결과:
┌────┬────────┬──────────┐
│ #1 │2024-001│ABC 문서   │ [설계평가 완료]
│ #2 │2024-002│DEF 문서   │
└────┴────────┴──────────┘
```

**시나리오 2: 자동 매칭 실패**
```
┌─────────────────────────────────────────────┐
│ ⚠ 설계평가 샘플과 일치하는 항목 없음        │
│ 설계평가 샘플: 번호=2024-001, 문서=ABC      │
│                                             │
│ 설계평가 샘플로 지정: ▼ 표본 선택           │
└─────────────────────────────────────────────┘
```

#### 장점
- 자동화 + 유연성
- 사용자 확인 가능
- 오류 수정 가능

#### 단점
- 구현 복잡도 가장 높음

---

## 추가 고려사항

### 1. 매칭 기준
**옵션 A: 모집단 항목만 비교 (추천)**
- `attribute0`, `attribute1` (모집단)만 비교
- 증빙 항목은 운영평가에서 추가 입력 가능

**옵션 B: 모든 항목 비교**
- `attribute0` ~ `attribute9` 모두 비교
- 완전히 동일한 경우만 매칭
- 너무 엄격할 수 있음

### 2. 데이터베이스 변경 필요 여부
**필요 없음:**
- 매칭 정보를 메모리(frontend)에서만 관리
- 표시만 달리함

**필요함 (선택):**
- `linked_sample_id` 컬럼 추가
- 매칭 관계 영구 저장
- 나중에 리포트/통계에 활용

### 3. 엑셀 다운로드 시 표시
조서 다운로드 시 설계평가 샘플 표시:
```
Testing Table 시트:
┌────┬────────┬──────────┬────────┬────────┬──────┐
│ #  │ 번호   │ 문서번호  │ 완료일 │ 완료   │ 비고 │
├────┼────────┼──────────┼────────┼────────┼──────┤
│ #1 │2024-001│ABC 문서   │2024-01│완료    │설계평가│
│ #2 │2024-002│DEF 문서   │2024-02│진행중  │      │
└────┴────────┴──────────┴────────┴────────┴──────┘
```

---

## 구현 우선순위

### Phase 1: 자동 매칭 (방안 1)
- 백엔드: 매칭 로직 추가
- 프론트엔드: 배지 표시
- 테스트: 매칭 정확도 확인

### Phase 2: 수동 수정 (방안 3으로 확장)
- UI: 매칭 변경 기능 추가
- 백엔드: 매칭 정보 저장 (선택)

### Phase 3: 엑셀 다운로드 연계
- 조서에 설계평가 샘플 표시

---

## 질문 및 결정 사항

1. **매칭 기준**: 모집단 항목(attribute0, 1)만? 모든 항목?
2. **DB 저장**: 매칭 정보를 DB에 저장? 메모리만?
3. **UI 형태**: 배지만? 아니면 상세 정보 표시?
4. **수동 선택**: Phase 1부터 포함? 나중에 추가?

---

---

## **최종 채택 방안: 설계평가 샘플을 첫 번째 행으로 고정**

### 핵심 아이디어 (사용자 제안)

**문제:**
- 설계평가 증빙과 모집단 항목 간 매핑 키 없음
- 무작위 추출된 표본이 설계평가 샘플을 포함하지 않을 수 있음

**해결책:**
1. 첫 번째 표본은 설계평가 증빙으로 고정
2. 모집단 항목은 드롭다운으로 선택 (사용자가 직접 매핑)
3. 나머지 표본은 (필요 표본수 - 1)개만큼 무작위 추출

### UI 구조

```
┌─────────────────────────────────────────────────────┐
│ 표본별 테스트 결과                                    │
├─────┬──────────────┬────────────────┬────────┬──────┤
│  #  │  모집단 번호  │     증빙       │  결과  │ 비고 │
├─────┼──────────────┼────────────────┼────────┼──────┤
│ #1  │ [▼ 드롭다운] │ 문서1 (readonly)│   ✓   │ 설계 │
│     │  1-9 선택    │                │        │      │
├─────┼──────────────┼────────────────┼────────┼──────┤
│ #2  │ 3 (readonly) │ (입력 가능)    │        │      │
├─────┼──────────────┼────────────────┼────────┼──────┤
│ #3  │ 5 (readonly) │ (입력 가능)    │        │      │
└─────┴──────────────┴────────────────┴────────┴──────┘
```

### 동작 방식

**1. 표본 생성 로직 변경**
```python
# 기존: 표본수만큼 무작위 추출
sample_count = 3
random_samples = random.sample(population, sample_count)  # [1, 3, 5]

# 변경: (표본수 - 1)개만 무작위 추출
sample_count = 3
design_sample_row = 1  # 첫 번째 행은 설계평가용
operation_sample_count = sample_count - 1  # 2개만 추출
random_samples = random.sample(population, operation_sample_count)  # [3, 5]
```

**2. UI 생성**
```javascript
function generateSampleLines() {
    // 설계평가 샘플 조회
    const designSample = getDesignEvaluationSample(lineId);

    // 첫 번째 행: 설계평가 샘플
    let row1 = `
        <tr>
            <td>#1 <span class="badge bg-info">설계</span></td>
            <td>
                <select class="form-select form-select-sm" id="design-population-select">
                    <option value="">모집단 번호 선택</option>
                    ${populationItems.map(item =>
                        `<option value="${item.id}">${item.번호} - ${item.문서번호}</option>`
                    ).join('')}
                </select>
            </td>
            <td>
                <input type="text" value="${designSample.증빙}" readonly class="form-control form-control-sm">
            </td>
            <td>
                <select class="form-select form-select-sm">
                    <option value="no_exception">No Exception</option>
                    <option value="exception">Exception</option>
                </select>
            </td>
        </tr>
    `;

    // 나머지 행: 무작위 추출된 표본
    for (let i = 0; i < randomSamples.length; i++) {
        const sample = randomSamples[i];
        let row = `
            <tr>
                <td>#${i+2}</td>
                <td>
                    <input type="text" value="${sample.번호}" readonly class="form-control form-control-sm">
                </td>
                <td>
                    <input type="text" class="form-control form-control-sm" placeholder="증빙 입력">
                </td>
                <td>
                    <select class="form-select form-select-sm">
                        <option value="no_exception">No Exception</option>
                        <option value="exception">Exception</option>
                    </select>
                </td>
            </tr>
        `;
    }
}
```

**3. 저장 로직**
```python
def save_operation_evaluation():
    samples = []

    # 첫 번째 샘플: 설계평가 샘플
    design_population_id = request.json['design_population_select']
    design_sample = {
        'sample_number': 1,
        'population_id': design_population_id,  # 사용자가 선택한 모집단 항목
        'evidence': design_evaluation_evidence,  # 설계평가 증빙 (readonly)
        'result': request.json['sample_result_1'],
        'is_design_sample': True  # 플래그
    }
    samples.append(design_sample)

    # 나머지 샘플: 무작위 추출된 샘플
    for i in range(2, sample_count + 1):
        sample = {
            'sample_number': i,
            'population_id': request.json[f'population_id_{i}'],  # 무작위 추출된 항목
            'evidence': request.json[f'evidence_{i}'],
            'result': request.json[f'sample_result_{i}'],
            'is_design_sample': False
        }
        samples.append(sample)

    # DB 저장
    save_samples(line_id, samples)
```

### 장점
1. **명확한 구분**: 첫 번째 행이 항상 설계평가 샘플
2. **유연성**: 사용자가 직접 모집단 항목 선택 (매핑 키 문제 해결)
3. **간단한 구현**: 복잡한 자동 매칭 로직 불필요
4. **데이터 재사용**: 설계평가 증빙을 그대로 활용
5. **DB 변경 최소**: 기존 구조 그대로 사용 가능

### 단점
1. **수동 작업**: 사용자가 모집단 항목을 직접 선택해야 함
2. **표본수 -1**: 실제 무작위 추출되는 표본이 1개 줄어듦

---

## 구현 계획

### Phase 1: 기본 구조 (우선)
1. **표본 생성 로직 변경**
   - 첫 번째 행 고정
   - (표본수 - 1)개만 무작위 추출

2. **UI 구현**
   - 첫 번째 행: 모집단 드롭다운 + 증빙 readonly
   - 나머지 행: 기존과 동일

3. **저장/조회 로직**
   - 첫 번째 샘플 플래그 관리
   - 설계평가 증빙 자동 채우기

### Phase 2: 개선 (선택)
1. **모집단 드롭다운 자동 선택**
   - 설계평가 샘플과 일치하는 항목 자동 선택
   - 사용자가 변경 가능

2. **조서 다운로드**
   - 설계평가 샘플 표시

---

## 다음 단계

1. UI 목업 확인
2. 표본 생성 로직 구현
3. 테스트
4. 사용자 피드백 수집
