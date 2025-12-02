# 운영평가 엑셀 다운로드 기능 수정 완료

## 작업 일시
2025-12-02

## 변경 사항

### 1. 엑셀 템플릿 구조 변경

**이전:**
- 12행(C12): 검토 결과(설계평가)
- 13행(C13): 검토 결과(운영평가)
- 14행(C14): 결론

**변경 후:**
- 12행(C12): 검토 결과(설계평가)
- 13행(C13): 검토 결과(운영평가 의견) ← **새로 추가**
- 14행(C14): 결론(운영평가) ← **13행에서 이동**

### 2. 소스 코드 수정

#### 파일: snowball_link7.py

**1) SQL 쿼리 수정 (라인 2161-2189)**
- `l.review_comment` 컬럼 추가하여 운영평가 검토의견 조회

**2) 엑셀 데이터 작성 로직 수정 (라인 2272-2303)**

```python
# 설계평가 검토 결과 (C12)
design_comment = design_eval_dict.get('design_comment', '')
template_sheet['C12'] = design_comment
# + 행 높이 자동 조정 로직

# 운영평가 의견 작성 (C13) ← 새로 추가
operation_review_comment = eval_dict.get('review_comment', '')
template_sheet['C13'] = operation_review_comment
# + 행 높이 자동 조정 로직

# 운영평가 결론 작성 (C14) ← 13행에서 14행으로 이동
operation_conclusion = eval_dict.get('conclusion', '')
template_sheet['C14'] = operation_conclusion
```

**주요 변경점:**
- `improvement_plan` 대신 `review_comment` 필드 사용
- 13행에 운영평가 의견(review_comment) 표시
- 14행으로 운영평가 결론(conclusion) 이동
- 각 행에 대한 자동 행 높이 조정 로직 추가

### 3. 템플릿 파일 수정

**파일:** `paper_templates/Template_Manual.xlsx`
- B13 셀: "검토 결과(운영평가)" → "검토 결과(운영평가 의견)"
- B14 셀: "결론" → "결론(운영평가)"

**백업 파일:**
- `Template_Manual_backup.xlsx`: 원본 백업
- `Template_Manual_old.xlsx`: 교체 전 파일

## 데이터 필드 정의

### review_comment
- 운영평가 화면의 "검토 의견" 필드
- DB 컬럼: `sb_operation_evaluation_line.review_comment`
- 엑셀 13행(C13)에 표시

### conclusion
- 운영평가 결론 (Effective/Ineffective)
- DB 컬럼: `sb_operation_evaluation_line.conclusion`
- 엑셀 14행(C14)에 표시

### improvement_plan (참고)
- 개선계획 필드 (예외사항이 있을 때만 입력)
- DB 컬럼: `sb_operation_evaluation_line.improvement_plan`
- 엑셀에는 직접 표시되지 않음

## 테스트 필요 사항

1. **서버 재시작** 필요
2. **테스트 시나리오:**
   - 운영평가 데이터 입력 (검토 의견 포함)
   - 운영평가 엑셀 다운로드
   - 13행에 "검토 의견" 내용 확인
   - 14행에 "결론" 내용 확인
   - 행 높이가 텍스트 길이에 맞게 자동 조정되는지 확인

## 관련 파일

- 수정된 코드: `snowball_link7.py`
- 수정된 템플릿: `paper_templates/Template_Manual.xlsx`
- 백업 파일들: `paper_templates/Template_Manual_backup.xlsx`, `Template_Manual_old.xlsx`
- 업데이트 스크립트: `update_template.py`, `replace_template.py`

## 주의사항

- `review_comment` 필드는 운영평가 화면에서 "검토 의견"으로 표시됩니다
- 기존 운영평가 데이터에 `review_comment`가 없으면 13행이 공란으로 표시됩니다
- 새로 입력하는 운영평가부터 13행에 내용이 표시됩니다
