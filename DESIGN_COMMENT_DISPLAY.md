# 운영평가 모달에 설계평가 의견 표시 기능 추가

## 작업 일시
2025-12-02

## 변경 목적
운영평가 수행 시 설계평가 검토 의견을 참고할 수 있도록 모달 상단에 읽기 전용으로 표시

## 변경 사항

### 1. 데이터베이스 쿼리 수정 (auth.py)

**파일**: `auth.py`
**함수**: `get_key_rcm_details()`
**라인**: 756

#### 변경 내용
설계평가 의견(design_comment) 컬럼을 SELECT 쿼리에 추가

```python
# 이전
SELECT DISTINCT d.*, l.evaluation_evidence, h.header_id
FROM sb_rcm_detail_v d
...

# 변경 후
SELECT DISTINCT d.*, l.evaluation_evidence, l.design_comment, h.header_id
FROM sb_rcm_detail_v d
...
```

### 2. JSP 템플릿 수정 (link7_detail.jsp)

#### 2-1. 데이터 속성 추가
**라인**: 197

버튼 요소에 `data-design-comment` 속성 추가

```html
<button ...
    data-design-evaluation-evidence="{{ (detail.evaluation_evidence or '')|e }}"
    data-design-comment="{{ (detail.design_comment or '')|e }}"
    ...
>
```

#### 2-2. HTML 섹션 추가
**라인**: 320-334

설계평가 의견을 표시할 읽기 전용 섹션 추가 (통제 정보와 설계평가 이미지 사이)

```html
<!-- 설계평가 의견 표시 섹션 (읽기 전용) -->
<div class="mb-3" id="designCommentSection" style="display: none;">
    <label class="form-label fw-bold">
        <i class="fas fa-clipboard-check me-1"></i>설계평가 검토 의견
    </label>
    <div class="p-3 bg-light border rounded" style="white-space: pre-wrap; min-height: 60px;">
        <span id="designCommentText" class="text-dark"></span>
    </div>
    <div class="form-text">
        <small class="text-muted">
            <i class="fas fa-info-circle me-1"></i>
            설계평가 시 작성된 검토 의견입니다 (읽기 전용)
        </small>
    </div>
</div>
```

#### 2-3. JavaScript 함수 추가
**라인**: 1001-1021

설계평가 의견을 표시하는 함수 추가

```javascript
// 설계평가 의견 표시 함수
function displayDesignComment(comment) {
    const section = document.getElementById('designCommentSection');
    const textElement = document.getElementById('designCommentText');

    if (!section || !textElement) {
        console.error('Design comment section not found');
        return;
    }

    // 의견이 없으면 섹션 숨김
    if (!comment || comment.trim() === '') {
        section.style.display = 'none';
        textElement.textContent = '';
        return;
    }

    // 의견이 있으면 섹션 표시
    section.style.display = 'block';
    textElement.textContent = comment;
}
```

#### 2-4. 모달 열기 로직 수정
**라인**: 1076, 1521

```javascript
// 데이터 속성 읽기
const designComment = buttonElement.getAttribute('data-design-comment');

// 모달 표시 시 설계평가 의견 표시
displayDesignComment(designComment);
```

## 모달 레이아웃 최종 순서

1. 통제 정보
2. **설계평가 검토 의견** ✨ **새로 추가 (읽기 전용)**
3. 설계평가 증빙 이미지
4. 당기 발생사실 없음
5. 모집단 업로드
6. 표본 크기 입력
7. 표본 라인 테이블
8. 전체 결론
9. 검토 의견 (운영평가)
10. 예외사항 세부내용
11. 개선계획
12. 운영평가 증빙 이미지
13. 수동통제 엑셀
14. 당기 발생사실 없음 사유

## 주요 특징

### 1. 읽기 전용 표시
- 설계평가 의견은 수정 불가 (읽기 전용)
- 배경색과 테두리로 읽기 전용임을 시각적으로 표시
- `white-space: pre-wrap` 스타일로 줄바꿈 유지

### 2. 조건부 표시
- 설계평가 의견이 있는 경우에만 섹션 표시
- 의견이 없으면 자동으로 숨김

### 3. 사용자 경험 개선
- 운영평가 수행 시 설계평가 의견을 쉽게 참고
- 스크롤 없이 상단에서 바로 확인 가능
- 설계평가 → 운영평가의 자연스러운 흐름

## 스타일 특징

```css
- 배경색: bg-light (연한 회색)
- 테두리: border rounded
- 패딩: p-3
- 최소 높이: min-height: 60px
- 텍스트 색상: text-dark
- 줄바꿈 유지: white-space: pre-wrap
```

## 데이터 흐름

```
1. DB (sb_design_evaluation_line.design_comment)
   ↓
2. auth.py get_key_rcm_details() - SELECT 쿼리
   ↓
3. JSP 템플릿 - data-design-comment 속성
   ↓
4. JavaScript - getAttribute('data-design-comment')
   ↓
5. displayDesignComment() 함수
   ↓
6. 모달 화면에 표시
```

## 수정된 파일
- ✅ `auth.py` (라인 756)
- ✅ `templates/link7_detail.jsp` (라인 197, 320-334, 1001-1021, 1076, 1521)

## 영향 범위
- 기존 기능에 영향 없음 (추가 기능)
- 데이터베이스 스키마 변경 없음 (기존 컬럼 활용)
- 성능 영향 없음 (기존 쿼리에 컬럼 1개 추가)

## 테스트 항목
1. ✅ 운영평가 모달 열기
2. ✅ 설계평가 의견이 있는 통제 확인
   - 설계평가 의견 섹션이 표시되는지
   - 의견 내용이 올바르게 표시되는지
   - 줄바꿈이 유지되는지
3. ✅ 설계평가 의견이 없는 통제 확인
   - 설계평가 의견 섹션이 숨겨지는지
4. ✅ 읽기 전용 확인
   - 텍스트 편집 불가능한지
5. ✅ 레이아웃 확인
   - 통제 정보 바로 다음에 표시되는지
   - 설계평가 이미지 위에 배치되는지

## 비고
- 설계평가 의견은 운영평가 수행 시 참고 자료로 활용
- 운영평가 의견(review_comment)과는 별개의 필드
- 설계평가 → 운영평가의 일관성 있는 평가 지원
