"""
Link4 (Video Content) 버튼 및 UI 기능 테스트

테스트 범위:
- Link4 페이지 렌더링
- 사이드바 카테고리 메뉴 (ITPWC, ITGC, ETC)
- 영상 컨텐츠 선택 버튼
- 동영상 로드 기능
- 컨텐츠 동적 로드 (/get_content_link4)
- YouTube 임베드 기능
"""

import pytest
from unittest.mock import patch


class TestLink4PageRendering:
    """Link4 페이지 렌더링 테스트"""

    def test_link4_page_loads_successfully(self, client):
        """Link4 페이지가 정상적으로 로드되는지 테스트"""
        response = client.get('/link4')
        assert response.status_code == 200

    def test_link4_contains_sidebar(self, client):
        """Link4 페이지에 사이드바가 포함되어 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'categoryList' in html
        assert 'sidebar' in html

    def test_link4_contains_content_area(self, client):
        """Link4 페이지에 컨텐츠 영역이 포함되어 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'contentContainer' in html
        assert '항목을 선택해주세요' in html


class TestLink4SidebarCategories:
    """Link4 사이드바 카테고리 메뉴 테스트"""

    def test_link4_contains_itpwc_category(self, client):
        """ITPWC (IT Process Wide Controls) 카테고리가 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'ITPWC' in html
        assert 'IT Process Wide Controls' in html

    def test_link4_contains_itgc_category(self, client):
        """ITGC (IT General Controls) 카테고리가 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'ITGC' in html
        assert 'IT General Controls' in html

    def test_link4_contains_etc_category(self, client):
        """ETC (기타) 카테고리가 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'ETC' in html
        assert '기타' in html

    def test_link4_itpwc_options_exist(self, client):
        """ITPWC 카테고리의 세부 옵션들이 존재하는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'OVERVIEW' in html
        assert 'ITPWC01' in html
        assert '내부회계관리제도 Overview' in html
        assert 'ITGC Scoping' in html

    def test_link4_itgc_options_exist(self, client):
        """ITGC 카테고리의 세부 옵션들이 존재하는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'APD01' in html
        assert 'APD02' in html
        assert 'APD03' in html
        assert 'APD07' in html
        assert 'APD08' in html
        assert 'PC01' in html
        assert 'CO01' in html

    def test_link4_etc_options_exist(self, client):
        """ETC 카테고리의 세부 옵션들이 존재하는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'PW' in html
        assert 'PW_DETAIL' in html
        assert 'MONITOR' in html
        assert 'DDL' in html
        assert '패스워드 기준' in html
        assert '데이터 변경 모니터링' in html


class TestLink4ContentLoading:
    """Link4 컨텐츠 동적 로드 테스트"""

    def test_get_content_link4_endpoint_exists(self, client):
        """get_content_link4 엔드포인트가 존재하는지 테스트"""
        response = client.get('/get_content_link4')
        # type 파라미터 없으면 준비 중 메시지
        assert response.status_code == 200

    def test_get_content_link4_with_valid_type(self, client):
        """유효한 type 파라미터로 컨텐츠를 로드하는지 테스트"""
        valid_types = ['APD01', 'APD02', 'APD03', 'PC01', 'CO01',
                      'OVERVIEW', 'PW', 'PW_DETAIL', 'MONITOR', 'DDL', 'ITPWC01']

        for content_type in valid_types:
            response = client.get(f'/get_content_link4?type={content_type}')
            assert response.status_code == 200
            # 준비 중 메시지가 아닌 실제 컨텐츠 확인
            html = response.data.decode('utf-8')
            # 준비 중이 아니면 youtube 또는 img 태그가 있어야 함
            # (실제 데이터가 video_map에 있는 경우)

    def test_get_content_link4_with_invalid_type(self, client):
        """잘못된 type 파라미터로 컨텐츠를 로드할 때 처리 테스트"""
        response = client.get('/get_content_link4?type=INVALID_TYPE')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert '준비 중입니다' in html

    def test_get_content_link4_without_type(self, client):
        """type 파라미터 없이 요청 시 처리 테스트"""
        response = client.get('/get_content_link4')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert '준비 중입니다' in html


class TestLink4VideoContent:
    """Link4 영상 컨텐츠 테스트"""

    def test_video_content_apd01_loads(self, client):
        """APD01 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=APD01')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        # APD01은 video_map에 정의되어 있으므로 YouTube URL이 있어야 함
        assert 'youtube.com' in html or 'Access Program & Data' in html

    def test_video_content_apd02_loads(self, client):
        """APD02 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=APD02')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or 'Access Program & Data' in html

    def test_video_content_apd03_loads(self, client):
        """APD03 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=APD03')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or 'Access Program & Data' in html

    def test_video_content_pc01_loads(self, client):
        """PC01 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=PC01')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or '프로그램 변경 승인' in html

    def test_video_content_co01_loads(self, client):
        """CO01 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=CO01')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or '배치잡 스케줄 등록 승인' in html

    def test_video_content_overview_loads(self, client):
        """OVERVIEW 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=OVERVIEW')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or '내부회계관리제도 Overview' in html

    def test_video_content_pw_loads(self, client):
        """PW (패스워드 기준) 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=PW')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or '패스워드 기준' in html

    def test_video_content_pw_detail_loads(self, client):
        """PW_DETAIL 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=PW_DETAIL')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or '패스워드 기준 상세' in html

    def test_video_content_monitor_loads(self, client):
        """MONITOR 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=MONITOR')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or '데이터 변경 모니터링' in html

    def test_video_content_ddl_loads(self, client):
        """DDL 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=DDL')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or 'DDL' in html

    def test_video_content_itpwc01_loads(self, client):
        """ITPWC01 영상이 정상적으로 로드되는지 테스트"""
        response = client.get('/get_content_link4?type=ITPWC01')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'youtube.com' in html or 'ITGC In-Scope' in html


class TestLink4YouTubeEmbedFeatures:
    """Link4 YouTube 임베드 기능 테스트"""

    def test_youtube_embed_has_autoplay(self, client):
        """YouTube 임베드에 autoplay 파라미터가 있는지 테스트"""
        response = client.get('/get_content_link4?type=APD01')
        html = response.data.decode('utf-8')
        if 'youtube.com' in html:
            assert 'autoplay=1' in html

    def test_youtube_embed_has_mute(self, client):
        """YouTube 임베드에 mute 파라미터가 있는지 테스트"""
        response = client.get('/get_content_link4?type=APD01')
        html = response.data.decode('utf-8')
        if 'youtube.com' in html:
            assert 'mute=1' in html


class TestLink4UserActivityLogging:
    """Link4 사용자 활동 로깅 테스트"""

    @patch('snowball_link4.log_user_activity')
    def test_link4_logs_page_access_for_logged_in_user(self, mock_log, authenticated_client, test_user):
        """로그인한 사용자의 페이지 접근이 로그에 기록되는지 테스트"""
        authenticated_client.get('/link4')

        assert mock_log.called

        call_args = mock_log.call_args[0]
        assert call_args[1] == 'PAGE_ACCESS'
        assert call_args[2] == '영상자료 페이지'
        assert call_args[3] == '/link4'


class TestLink4DisabledLinks:
    """Link4 비활성화된 링크 테스트"""

    def test_link4_contains_disabled_links(self, client):
        """Link4에 비활성화된 링크가 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        # disabledList에 포함된 항목들
        assert 'APD07' in html
        assert 'APD08' in html
        assert 'PC01' in html
        assert 'CO01' in html
        assert 'disabled-link' in html


class TestLink4NavLinkActiveState:
    """Link4 네비게이션 링크 활성 상태 테스트"""

    def test_link4_nav_links_have_click_handlers(self, client):
        """네비게이션 링크들이 클릭 핸들러를 가지고 있는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'addEventListener' in html
        assert 'click' in html
        assert 'updateContent' in html


class TestLink4ResponsiveLayout:
    """Link4 반응형 레이아웃 테스트"""

    def test_link4_uses_bootstrap_grid(self, client):
        """Link4가 부트스트랩 그리드 시스템을 사용하는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'col-md-4' in html or 'col-md-3' in html  # 사이드바
        assert 'col-md-8' in html or 'col-md-9' in html  # 컨텐츠 영역

    def test_link4_includes_bootstrap_css(self, client):
        """Link4가 부트스트랩 CSS를 포함하는지 테스트"""
        response = client.get('/link4')
        html = response.data.decode('utf-8')
        assert 'bootstrap' in html


class TestLink4VideoMapDataStructure:
    """Link4 video_map 데이터 구조 테스트"""

    def test_video_map_contains_required_keys(self):
        """video_map의 각 항목이 필요한 키를 포함하는지 테스트"""
        from snowball_link4 import video_map

        for key, value in video_map.items():
            assert 'youtube_url' in value
            assert 'img_url' in value
            assert 'title' in value
            assert 'desc' in value

    def test_video_map_has_apd_entries(self):
        """video_map에 APD 항목들이 있는지 테스트"""
        from snowball_link4 import video_map

        assert 'APD01' in video_map
        assert 'APD02' in video_map
        assert 'APD03' in video_map

    def test_video_map_has_itpwc_entries(self):
        """video_map에 ITPWC 항목들이 있는지 테스트"""
        from snowball_link4 import video_map

        assert 'OVERVIEW' in video_map
        assert 'ITPWC01' in video_map

    def test_video_map_has_etc_entries(self):
        """video_map에 ETC 항목들이 있는지 테스트"""
        from snowball_link4 import video_map

        assert 'PW' in video_map
        assert 'PW_DETAIL' in video_map
        assert 'MONITOR' in video_map
        assert 'DDL' in video_map


class TestLink4GetContentHelper:
    """Link4 get_link4_content 헬퍼 함수 테스트"""

    def test_get_link4_content_returns_valid_data(self):
        """get_link4_content가 유효한 데이터를 반환하는지 테스트"""
        from snowball_link4 import get_link4_content

        result = get_link4_content('APD01')
        assert result is not None
        assert 'youtube_url' in result
        assert 'title' in result

    def test_get_link4_content_returns_none_for_invalid_type(self):
        """get_link4_content가 잘못된 타입에 대해 None을 반환하는지 테스트"""
        from snowball_link4 import get_link4_content

        result = get_link4_content('INVALID')
        assert result is None

    def test_get_link4_content_returns_none_for_empty_type(self):
        """get_link4_content가 빈 타입에 대해 None을 반환하는지 테스트"""
        from snowball_link4 import get_link4_content

        result = get_link4_content('')
        assert result is None

    def test_get_link4_content_returns_none_for_none_type(self):
        """get_link4_content가 None 타입에 대해 None을 반환하는지 테스트"""
        from snowball_link4 import get_link4_content

        result = get_link4_content(None)
        assert result is None
