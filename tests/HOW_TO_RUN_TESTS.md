# 테스트 실행 방법

## 빠른 시작

### 1. pytest 설치 (한 번만)
```bash
pip install pytest pytest-mock
```

### 2. 네비게이션 테스트 실행
```bash
cd c:\Python\snowball
python -m pytest tests/test_navigation_flow.py -v
```

## 결과 예시
```
==================== test session starts ====================
collected 19 items

tests/test_navigation_flow.py::test_navigation_rcm_to_design_evaluation PASSED
tests/test_navigation_flow.py::test_navigation_rcm_to_itgc_design_evaluation PASSED
tests/test_navigation_flow.py::test_navigation_rcm_to_elc_design_evaluation PASSED
...
==================== 19 passed in 2.45s ====================
```

## 트러블슈팅

### "No module named pytest" 에러
```bash
pip install pytest pytest-mock
```

### 테스트가 실패하는 경우
```bash
# 자세한 에러 로그 보기
python -m pytest tests/test_navigation_flow.py -v --tb=long

# 실패한 테스트만 다시 실행
python -m pytest tests/test_navigation_flow.py --lf -v
```

## 더 많은 정보
- `README_NAVIGATION_TEST.md` - 상세 가이드
- `NAVIGATION_TEST_SUMMARY.md` - 테스트 요약
