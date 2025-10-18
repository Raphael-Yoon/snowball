# Snowball 버튼 테스트 가이드

## 개요

이 문서는 Snowball 애플리케이션의 각 화면 버튼 및 UI 요소들을 모듈화하여 테스트하는 방법을 설명합니다.

## 버튼 테스트 모듈 구조

```
tests/
├── test_link1_buttons.py    # Link1 (RCM Builder) 버튼 테스트 (19개)
├── test_link3_buttons.py    # Link3 (Operation Test) 버튼 테스트 (25개)
├── test_link4_buttons.py    # Link4 (Video Content) 버튼 테스트 (39개)
└── BUTTON_TEST_GUIDE.md     # 이 문서
```

## 총 테스트 현황

### 전체 테스트: 138개
- **test_auth.py**: 14개 (인증 기능)
- **test_routes.py**: 23개 (라우팅)
- **test_link2_interview.py**: 18개 (인터뷰 기능)
- **test_link1_buttons.py**: 19개 (Link1 버튼/UI)
- **test_link3_buttons.py**: 25개 (Link3 버튼/UI)
- **test_link4_buttons.py**: 39개 (Link4 버튼/UI)

**모든 138개 테스트 통과 ✅**

---

## Link1 (RCM Builder) 버튼 테스트

**파일**: [test_link1_buttons.py](test_link1_buttons.py)
**테스트 수**: 19개

### 테스트 범위

#### 1. 폼 렌더링 (7개 테스트)
- 페이지 로드
- 이메일 입력 필드
- 시스템명 입력 필드
- System 라디오 버튼 (SAP, Oracle, 더존, 영림원, 기타)
- OS 라디오 버튼 (Unix, Windows, Linux, 기타)
- DB 라디오 버튼 (Oracle, MS-SQL, MY-SQL, 기타)
- 제출 버튼

#### 2. 로그인 사용자 동작 (2개 테스트)
- 이메일 자동 채움
- 이메일 필드 readonly 상태

#### 3. RCM 생성 버튼 기능 (6개 테스트)
- 유효한 데이터 제출
- RCM 생성 프로세스 성공
- 다양한 시스템 조합 테스트
- 이메일 누락 처리
- 시스템명 누락 처리
- 인증 사용자 RCM 생성

#### 4. 이메일 검증 (2개 테스트)
- 유효한 이메일 형식
- 잘못된 이메일 형식

#### 5. 활동 로깅 (2개 테스트)
- 로그인 사용자 페이지 접근 로그
- 비로그인 사용자 로그 미기록

### 주요 테스트 예시

```python
def test_form_contains_submit_button(self, client):
    """폼에 제출 버튼이 있는지 테스트"""
    response = client.get('/link1')
    html = response.data.decode('utf-8')
    assert 'type="submit"' in html
    assert '메일로 보내기' in html

def test_rcm_generate_with_different_systems(self, mock_send_gmail, client):
    """다양한 시스템 선택으로 RCM 생성이 정상 작동하는지 테스트"""
    system_combinations = [
        ('SAP', 'UNIX', 'ORACLE'),
        ('ORACLE', 'WINDOWS', 'MSSQL'),
        ('DOUZONE', 'LINUX', 'MYSQL'),
        ('YOUNG', 'UNIX', 'ORACLE'),
        ('ETC', 'WINDOWS', 'MSSQL')
    ]

    for system, os, db in system_combinations:
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': f'{system} 시스템',
            'param3': system,
            'param4': os,
            'param5': db
        })
        assert response.status_code in [200, 302]
```

---

## Link3 (Operation Test) 버튼 테스트

**파일**: [test_link3_buttons.py](test_link3_buttons.py)
**테스트 수**: 25개

### 테스트 범위

#### 1. 페이지 렌더링 (4개 테스트)
- 페이지 로드
- 사이드바 존재
- 컨텐츠 영역
- 템플릿 다운로드 버튼

#### 2. 사이드바 카테고리 (6개 테스트)
- APD (Access Program & Data) 카테고리
- PC (Program Changes) 카테고리
- CO (Computer Operations) 카테고리
- APD 세부 옵션 (APD01-13)
- PC 세부 옵션 (PC01-07)
- CO 세부 옵션 (CO01-06)

#### 3. 컨텐츠 동적 로드 (2개 테스트)
- `/get_content_link3` 엔드포인트
- HTML 응답 확인

#### 4. 템플릿 다운로드 버튼 (3개 테스트)
- 엔드포인트 존재
- 파일 존재 시 다운로드
- POST 메서드만 허용

#### 5. Step-by-Step 네비게이션 (4개 테스트)
- 네비게이션 요소 존재
- APD01 step 데이터
- PC01 step 데이터
- CO01 step 데이터

#### 6. 기타 (6개 테스트)
- 사용자 활동 로깅
- 이미지 리소스 참조
- 템플릿 버튼 동적 동작
- 반응형 레이아웃

### 주요 테스트 예시

```python
def test_link3_contains_step_data_for_apd01(self, client):
    """APD01에 대한 step 데이터가 정의되어 있는지 테스트"""
    response = client.get('/link3')
    html = response.data.decode('utf-8')
    assert 'APD01' in html
    assert 'Step 1: 모집단 확인' in html
    assert 'Step 2: 샘플 선정' in html
    assert 'Step 3: 증빙 확인' in html

def test_paper_template_download_post_method_only(self, client):
    """템플릿 다운로드는 POST 메서드만 허용하는지 테스트"""
    response = client.get('/paper_template_download')
    assert response.status_code == 405  # Method Not Allowed
```

---

## Link4 (Video Content) 버튼 테스트

**파일**: [test_link4_buttons.py](test_link4_buttons.py)
**테스트 수**: 39개

### 테스트 범위

#### 1. 페이지 렌더링 (3개 테스트)
- 페이지 로드
- 사이드바
- 컨텐츠 영역

#### 2. 사이드바 카테고리 (6개 테스트)
- ITPWC (IT Process Wide Controls) 카테고리
- ITGC (IT General Controls) 카테고리
- ETC (기타) 카테고리
- 각 카테고리 세부 옵션

#### 3. 컨텐츠 동적 로드 (4개 테스트)
- 엔드포인트 존재
- 유효한 타입 파라미터
- 잘못된 타입 처리
- 파라미터 없음 처리

#### 4. 영상 컨텐츠 로드 (11개 테스트)
- APD01, APD02, APD03 영상
- PC01, CO01 영상
- OVERVIEW, PW, PW_DETAIL, MONITOR, DDL, ITPWC01 영상

#### 5. YouTube 임베드 기능 (2개 테스트)
- autoplay 파라미터
- mute 파라미터

#### 6. video_map 데이터 구조 (8개 테스트)
- 필수 키 존재
- APD, ITPWC, ETC 항목
- get_link4_content 헬퍼 함수

#### 7. 기타 (5개 테스트)
- 사용자 활동 로깅
- 비활성화된 링크
- 네비게이션 클릭 핸들러
- 반응형 레이아웃

### 주요 테스트 예시

```python
def test_video_content_apd01_loads(self, client):
    """APD01 영상이 정상적으로 로드되는지 테스트"""
    response = client.get('/get_content_link4?type=APD01')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'youtube.com' in html or 'Access Program & Data' in html

def test_video_map_contains_required_keys(self):
    """video_map의 각 항목이 필요한 키를 포함하는지 테스트"""
    from snowball_link4 import video_map

    for key, value in video_map.items():
        assert 'youtube_url' in value
        assert 'img_url' in value
        assert 'title' in value
        assert 'desc' in value
```

---

## 테스트 실행 방법

### 1. 전체 버튼 테스트 실행

```bash
# 모든 버튼 테스트 실행
pytest tests/test_link*_buttons.py -v

# 간단한 출력
pytest tests/test_link*_buttons.py -q
```

### 2. 특정 링크의 버튼 테스트만 실행

```bash
# Link1 버튼 테스트만
pytest tests/test_link1_buttons.py -v

# Link3 버튼 테스트만
pytest tests/test_link3_buttons.py -v

# Link4 버튼 테스트만
pytest tests/test_link4_buttons.py -v
```

### 3. 특정 테스트 클래스만 실행

```bash
# Link1 폼 렌더링 테스트만
pytest tests/test_link1_buttons.py::TestLink1FormRendering -v

# Link3 사이드바 카테고리 테스트만
pytest tests/test_link3_buttons.py::TestLink3SidebarCategories -v

# Link4 영상 컨텐츠 테스트만
pytest tests/test_link4_buttons.py::TestLink4VideoContent -v
```

### 4. 특정 테스트 함수만 실행

```bash
pytest tests/test_link1_buttons.py::TestLink1FormRendering::test_form_contains_submit_button -v
```

### 5. run_tests.sh 스크립트 사용

```bash
# 전체 테스트 (버튼 테스트 포함)
./run_tests.sh all

# 빠른 테스트
./run_tests.sh quick

# 커버리지 포함 테스트
./run_tests.sh coverage
```

---

## 버튼 테스트 작성 가이드

### 1. 새로운 버튼 테스트 추가하기

Link5~9에 대한 버튼 테스트를 추가하려면 다음 구조를 따르세요:

```python
"""
Link5 (기능명) 버튼 및 UI 기능 테스트

테스트 범위:
- 페이지 렌더링
- 버튼 기능
- ...
"""

import pytest
from unittest.mock import patch


class TestLink5PageRendering:
    """Link5 페이지 렌더링 테스트"""

    def test_link5_page_loads_successfully(self, client):
        """Link5 페이지가 정상적으로 로드되는지 테스트"""
        response = client.get('/link5')
        assert response.status_code == 200


class TestLink5ButtonFunctionality:
    """Link5 버튼 기능 테스트"""

    def test_button_click_action(self, client):
        """버튼 클릭 시 정상 동작하는지 테스트"""
        response = client.post('/link5_action', data={
            'param': 'value'
        })
        assert response.status_code in [200, 302]
```

### 2. 버튼 테스트 베스트 프랙티스

#### ✅ Good

```python
def test_submit_button_exists(self, client):
    """제출 버튼이 존재하는지 테스트"""
    response = client.get('/link1')
    html = response.data.decode('utf-8')
    assert 'type="submit"' in html
    assert '메일로 보내기' in html
```

#### ❌ Bad

```python
def test_button(self, client):
    """버튼 테스트"""
    response = client.get('/link1')
    assert response.status_code == 200
```

### 3. 테스트 클래스 네이밍

- **TestPageRendering**: 페이지 및 UI 요소 렌더링
- **TestButtonFunctionality**: 버튼 클릭 동작
- **TestFormValidation**: 폼 검증
- **TestDynamicContent**: 동적 컨텐츠 로드
- **TestUserInteraction**: 사용자 인터랙션
- **TestDataStructure**: 데이터 구조 검증

---

## 버튼 테스트 체크리스트

새로운 화면/기능을 추가할 때 다음을 확인하세요:

### UI 요소 테스트
- [ ] 페이지가 정상적으로 로드되는가?
- [ ] 모든 버튼이 렌더링되는가?
- [ ] 폼 필드가 올바르게 표시되는가?
- [ ] 필수 입력 필드가 표시되는가?

### 버튼 기능 테스트
- [ ] 버튼 클릭 시 올바른 엔드포인트가 호출되는가?
- [ ] 성공 시 적절한 응답을 반환하는가?
- [ ] 실패 시 적절한 오류 처리를 하는가?
- [ ] 검증 로직이 정상 작동하는가?

### 사용자 상태 테스트
- [ ] 로그인 사용자에게 올바른 UI가 표시되는가?
- [ ] 비로그인 사용자에게 올바른 UI가 표시되는가?
- [ ] 권한에 따라 버튼이 활성화/비활성화되는가?

### 데이터 처리 테스트
- [ ] 유효한 데이터가 정상 처리되는가?
- [ ] 잘못된 데이터가 거부되는가?
- [ ] 누락된 데이터가 적절히 처리되는가?

---

## 문제 해결

### 테스트 실패 시

1. **404 에러**: 라우트가 올바르게 등록되었는지 확인
   ```python
   # snowball.py에서 Blueprint 등록 확인
   app.register_blueprint(bp_link1)
   ```

2. **Mock 객체 오류**: import 경로가 올바른지 확인
   ```python
   # Bad: @patch('snowball_link1.send_gmail')
   # Good: @patch('snowball_mail.send_gmail_with_attachment')
   ```

3. **Assertion 오류**: 실제 로그/응답과 기대값 비교
   ```python
   # 실제 출력 확인
   print(response.data.decode('utf-8'))
   print(mock_log.call_args)
   ```

---

## 다음 단계

### 추가 구현 예정
1. **Link5 버튼 테스트**: RCM 조회 기능
2. **Link6 버튼 테스트**: 설계평가 기능
3. **Link7 버튼 테스트**: 운영평가 기능
4. **Link8 버튼 테스트**: 내부평가 기능
5. **Admin 페이지 버튼 테스트**: 관리자 기능

### 향상 계획
- E2E 테스트 추가 (Selenium/Playwright)
- JavaScript 버튼 이벤트 테스트
- 접근성 테스트 (a11y)
- 성능 테스트 (버튼 응답 시간)

---

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [pytest-flask 문서](https://pytest-flask.readthedocs.io/)
- [Flask Testing 가이드](https://flask.palletsprojects.com/en/latest/testing/)
- [TEST_AUTOMATION_GUIDE.md](../TEST_AUTOMATION_GUIDE.md)

---

**마지막 업데이트**: 2025-10-18
**총 버튼 테스트**: 83개
**상태**: ✅ All 138 tests passing
**커버리지**: 향상 중
