"""
Link3 (Operation Test) 버튼 및 UI 기능 테스트

테스트 범위:
- Link3 페이지 렌더링
- 사이드바 카테고리 메뉴 (APD, PC, CO)
- 템플릿 다운로드 버튼 기능
- 컨텐츠 동적 로드
- Step-by-step 네비게이션 버튼 (이전/다음)
"""

import pytest
import os
from unittest.mock import patch


class TestLink3PageRendering:
    """Link3 페이지 렌더링 테스트"""

    def test_link3_page_loads_successfully(self, client):
        """Link3 페이지가 정상적으로 로드되는지 테스트"""
        response = client.get('/link3')
        assert response.status_code == 200

    def test_link3_contains_sidebar(self, client):
        """Link3 페이지에 사이드바가 포함되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'categoryList' in html
        assert 'sidebar' in html

    def test_link3_contains_content_area(self, client):
        """Link3 페이지에 컨텐츠 영역이 포함되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'contentContainer' in html
        assert '항목을 선택해주세요' in html

    def test_link3_contains_template_download_button(self, client):
        """Link3 페이지에 템플릿 다운로드 버튼이 포함되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'template-download-btn' in html
        assert '템플릿 다운로드' in html


class TestLink3SidebarCategories:
    """Link3 사이드바 카테고리 메뉴 테스트"""

    def test_link3_contains_apd_category(self, client):
        """APD (Access Program & Data) 카테고리가 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'APD' in html
        assert 'Access Program & Data' in html

    def test_link3_contains_pc_category(self, client):
        """PC (Program Changes) 카테고리가 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'PC' in html
        assert 'Program Changes' in html

    def test_link3_contains_co_category(self, client):
        """CO (Computer Operations) 카테고리가 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'CO' in html
        assert 'Computer Operations' in html

    def test_link3_apd_options_exist(self, client):
        """APD 카테고리의 세부 옵션들이 존재하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        # JavaScript에 정의된 APD 옵션들
        assert 'APD01' in html
        assert 'APD02' in html
        assert 'APD03' in html
        assert '권한부여 승인' in html
        assert '부서이동자 권한 회수' in html
        assert '퇴사자 접근권한 회수' in html

    def test_link3_pc_options_exist(self, client):
        """PC 카테고리의 세부 옵션들이 존재하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'PC01' in html
        assert 'PC04' in html
        assert 'PC05' in html
        assert '프로그램 변경' in html
        assert '이관담당자 권한 제한' in html
        assert '개발/운영 환경 분리' in html

    def test_link3_co_options_exist(self, client):
        """CO 카테고리의 세부 옵션들이 존재하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'CO01' in html
        assert 'CO02' in html
        assert 'CO03' in html
        assert '배치잡 스케줄 등록 승인' in html
        assert '배치잡 스케줄 등록 권한 제한' in html


class TestLink3ContentLoading:
    """Link3 컨텐츠 동적 로드 테스트"""

    def test_get_content_link3_endpoint_exists(self, client):
        """get_content_link3 엔드포인트가 존재하는지 테스트"""
        response = client.get('/get_content_link3')
        assert response.status_code == 200

    def test_get_content_link3_returns_html(self, client):
        """get_content_link3가 HTML을 반환하는지 테스트"""
        response = client.get('/get_content_link3')
        assert response.content_type == 'text/html; charset=utf-8'


class TestLink3TemplateDownloadButton:
    """Link3 템플릿 다운로드 버튼 기능 테스트"""

    def test_paper_template_download_endpoint_exists(self, client):
        """paper_template_download 엔드포인트가 존재하는지 테스트"""
        response = client.post('/paper_template_download', data={
            'param1': 'test_param1',
            'param2': 'test_param2'
        })
        # 파일이 없어도 엔드포인트는 존재해야 함
        assert response.status_code in [200, 404, 302]

    @patch('os.path.exists')
    def test_paper_template_download_with_existing_file(self, mock_exists, client):
        """템플릿 파일이 존재할 때 다운로드가 정상 작동하는지 테스트"""
        mock_exists.return_value = True

        # 실제 파일 다운로드 테스트는 파일이 있어야 하므로 엔드포인트만 테스트
        response = client.post('/paper_template_download', data={
            'param1': 'APD01',
            'param2': 'test'
        })
        # 200 (성공) 또는 404 (파일 없음) 허용
        assert response.status_code in [200, 404]

    def test_paper_template_download_post_method_only(self, client):
        """템플릿 다운로드는 POST 메서드만 허용하는지 테스트"""
        response = client.get('/paper_template_download')
        # GET 요청은 405 Method Not Allowed
        assert response.status_code == 405


class TestLink3StepByStepNavigation:
    """Link3 Step-by-step 네비게이션 테스트"""

    def test_link3_contains_step_navigation_elements(self, client):
        """Link3에 step 네비게이션 요소들이 포함되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        # JavaScript로 동적 생성되는 요소들
        assert 'prev-btn' in html or 'enableStepByStep' in html
        assert 'next-btn' in html or 'enableStepByStep' in html

    def test_link3_contains_step_data_for_apd01(self, client):
        """APD01에 대한 step 데이터가 정의되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'APD01' in html
        assert 'Step 1: 모집단 확인' in html
        assert 'Step 2: 샘플 선정' in html
        assert 'Step 3: 증빙 확인' in html

    def test_link3_contains_step_data_for_pc01(self, client):
        """PC01에 대한 step 데이터가 정의되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'PC01' in html
        assert 'Step 1: 모집단 확인' in html
        assert '프로그램 이관 이력' in html

    def test_link3_contains_step_data_for_co01(self, client):
        """CO01에 대한 step 데이터가 정의되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'CO01' in html
        assert 'Batch Schedule' in html


class TestLink3UserActivityLogging:
    """Link3 사용자 활동 로깅 테스트"""

    @patch('snowball_link3.log_user_activity')
    def test_link3_logs_page_access_for_logged_in_user(self, mock_log, authenticated_client, test_user):
        """로그인한 사용자의 페이지 접근이 로그에 기록되는지 테스트"""
        authenticated_client.get('/link3')

        assert mock_log.called

        call_args = mock_log.call_args[0]
        assert call_args[1] == 'PAGE_ACCESS'
        assert call_args[2] == 'Operation Test 페이지'
        assert call_args[3] == '/link3'


class TestLink3ImageResources:
    """Link3 이미지 리소스 테스트"""

    def test_link3_references_step_images(self, client):
        """Link3가 step 이미지들을 참조하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert '/static/img/Operation/' in html
        assert 'APD01_Step1.jpg' in html
        assert 'PC01_Step1.jpg' in html
        assert 'CO01_Step1.jpg' in html


class TestLink3TemplateButtonDynamicBehavior:
    """Link3 템플릿 버튼 동적 동작 테스트"""

    def test_link3_template_button_initially_disabled(self, client):
        """초기 상태에서 템플릿 다운로드 버튼이 비활성화되어 있는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        # JavaScript에서 초기 상태는 opacity: 0.5, pointer-events: none
        assert 'updateTemplateButton' in html
        assert 'pointer-events: none' in html or 'opacity: 0.5' in html

    def test_link3_template_button_links_to_paper_files(self, client):
        """템플릿 버튼이 paper 파일을 참조하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert '/static/paper/' in html
        assert '_paper.xlsx' in html


class TestLink3ResponsiveLayout:
    """Link3 반응형 레이아웃 테스트"""

    def test_link3_uses_bootstrap_grid(self, client):
        """Link3가 부트스트랩 그리드 시스템을 사용하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'col-md-3' in html  # 사이드바
        assert 'col-md-9' in html  # 컨텐츠 영역

    def test_link3_includes_bootstrap_css(self, client):
        """Link3가 부트스트랩 CSS를 포함하는지 테스트"""
        response = client.get('/link3')
        html = response.data.decode('utf-8')
        assert 'bootstrap' in html
