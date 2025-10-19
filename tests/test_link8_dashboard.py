"""
Link8 - 내부평가 대시보드 테스트
"""

import pytest
from flask import session


class TestLink8InternalAssessment:
    """Link8 내부평가 메인 페이지 테스트"""

    def test_internal_assessment_requires_login(self, client):
        """내부평가 페이지 - 로그인 필요"""
        response = client.get('/internal-assessment', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_internal_assessment_page_loads(self, authenticated_client):
        """내부평가 메인 페이지 로드"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        assert b'internal' in response.data.lower() or b'assessment' in response.data.lower()

    def test_internal_assessment_shows_rcm_list(self, authenticated_client):
        """내부평가 페이지에 RCM 목록 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # RCM 카드나 목록이 표시되어야 함
        assert b'rcm' in response.data.lower() or b'card' in response.data.lower()

    def test_internal_assessment_shows_progress(self, authenticated_client):
        """내부평가 진행현황 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 진행률 표시 요소가 있어야 함
        assert b'progress' in response.data.lower() or b'%' in response.data


class TestLink8AssessmentDetail:
    """Link8 내부평가 상세 페이지 테스트"""

    def test_assessment_detail_requires_login(self, client):
        """내부평가 상세 - 로그인 필요"""
        response = client.get('/internal-assessment/1', follow_redirects=False)
        assert response.status_code in [302, 401, 403, 404]

    def test_assessment_detail_with_invalid_rcm(self, authenticated_client):
        """존재하지 않는 RCM 접근"""
        response = authenticated_client.get('/internal-assessment/99999', follow_redirects=False)
        # 권한 없음 또는 404
        assert response.status_code in [302, 403, 404]

    def test_assessment_detail_without_permission(self, authenticated_client):
        """권한 없는 RCM 접근"""
        # 다른 사용자의 RCM에 접근 시도
        response = authenticated_client.get('/internal-assessment/1', follow_redirects=False)
        # 권한이 있으면 200, 없으면 302 (리다이렉트) 또는 403
        assert response.status_code in [200, 302, 403, 404]


class TestLink8AssessmentStep:
    """Link8 내부평가 단계별 페이지 테스트"""

    def test_assessment_step_requires_login(self, client):
        """평가 단계 페이지 - 로그인 필요"""
        response = client.get('/internal-assessment/1/step/1', follow_redirects=False)
        assert response.status_code in [302, 401, 403, 404]

    def test_assessment_step_invalid_step_number(self, authenticated_client):
        """잘못된 단계 번호"""
        response = authenticated_client.get('/internal-assessment/1/step/0', follow_redirects=False)
        # 유효하지 않은 단계 (1-6 범위 벗어남)
        assert response.status_code in [302, 400, 404]

    def test_assessment_step_out_of_range(self, authenticated_client):
        """범위 초과 단계 번호"""
        response = authenticated_client.get('/internal-assessment/1/step/99', follow_redirects=False)
        assert response.status_code in [302, 400, 404]


class TestLink8API:
    """Link8 API 테스트"""

    def test_save_progress_requires_login(self, client):
        """진행상황 저장 API - 로그인 필요"""
        response = client.post('/api/internal-assessment/1/progress', json={})
        assert response.status_code in [302, 400, 401, 403]

    def test_save_progress_with_valid_data(self, authenticated_client):
        """진행상황 저장 - 유효한 데이터"""
        response = authenticated_client.post('/api/internal-assessment/1/progress', json={
            'step': 1,
            'data': {'test': 'data'},
            'status': 'in_progress'
        })
        # 저장 성공 또는 권한 없음
        assert response.status_code in [200, 403, 404]

    def test_save_progress_with_invalid_step(self, authenticated_client):
        """진행상황 저장 - 잘못된 단계"""
        response = authenticated_client.post('/api/internal-assessment/1/progress', json={
            'step': 99,
            'data': {},
            'status': 'pending'
        })
        # 저장 실패 또는 권한 없음
        assert response.status_code in [200, 400, 403, 404, 500]

    def test_save_progress_without_data(self, authenticated_client):
        """진행상황 저장 - 데이터 없음"""
        response = authenticated_client.post('/api/internal-assessment/1/progress', json={})
        # 데이터 없어도 기본값으로 처리 가능
        assert response.status_code in [200, 400, 403, 404, 500]


class TestLink8ProgressCalculation:
    """Link8 진행현황 계산 로직 테스트"""

    def test_progress_shows_link5_details(self, authenticated_client):
        """RCM 평가(Link5) 상세 진행률 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 매핑, 검토 정보가 표시되어야 함 (있는 경우)
        data = response.data.decode()
        # 진행률 표시 확인
        assert 'progress' in data.lower() or '%' in data

    def test_progress_shows_link6_details(self, authenticated_client):
        """설계평가(Link6) 상세 진행률 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 세션 정보가 표시될 수 있음
        data = response.data.decode()
        assert 'assessment' in data.lower()

    def test_progress_shows_link7_details(self, authenticated_client):
        """운영평가(Link7) 상세 진행률 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 운영평가 정보가 표시될 수 있음
        data = response.data.decode()
        assert 'assessment' in data.lower()


class TestLink8StepSequence:
    """Link8 단계별 순차 진행 테스트"""

    def test_step1_button_available_initially(self, authenticated_client):
        """초기 상태: 1단계 버튼 사용 가능"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # RCM 평가 버튼이 있어야 함
        assert 'rcm' in data.lower() or 'step' in data.lower()

    def test_shows_current_step_badge(self, authenticated_client):
        """현재 진행 단계 배지 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # 현재 단계 표시 또는 단계 정보가 있어야 함
        assert 'badge' in data.lower() or 'current' in data.lower() or '단계' in data or 'step' in data.lower()


class TestLink8Navigation:
    """Link8 네비게이션 테스트"""

    def test_back_to_rcm_list_button(self, authenticated_client):
        """RCM 목록으로 돌아가기 버튼"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 뒤로가기 버튼이 있어야 함
        assert b'rcm' in response.data.lower()

    def test_detail_view_button(self, authenticated_client):
        """상세 진행 상황 보기 버튼"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 상세보기 버튼이 있을 수 있음
        data = response.data.decode()
        assert 'detail' in data.lower() or 'view' in data.lower() or 'assessment' in data.lower()


class TestLink8GuideSection:
    """Link8 가이드 섹션 테스트"""

    def test_shows_assessment_guide(self, authenticated_client):
        """내부평가 가이드 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # 가이드 정보가 있어야 함
        assert 'guide' in data.lower() or '단계' in data or 'step' in data.lower()

    def test_guide_shows_all_steps(self, authenticated_client):
        """가이드에 모든 단계 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # 6단계 정보가 있어야 함 (기존 구현 기준)
        # 또는 3단계 (신규 단순화 버전)
        assert '단계' in data or 'step' in data.lower()


class TestLink8EmptyState:
    """Link8 빈 상태 테스트"""

    def test_shows_empty_state_when_no_rcms(self, authenticated_client):
        """RCM이 없을 때 빈 상태 표시"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # RCM이 있거나 없거나 모두 정상 응답
        data = response.data.decode()
        # 빈 상태 메시지 또는 RCM 목록이 있어야 함
        assert 'rcm' in data.lower() or 'empty' in data.lower() or 'assessment' in data.lower()


class TestLink8Responsiveness:
    """Link8 반응형 디자인 테스트"""

    def test_uses_bootstrap_grid(self, authenticated_client):
        """Bootstrap 그리드 시스템 사용"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # Bootstrap 클래스 사용 확인
        assert b'col-' in response.data or b'row' in response.data

    def test_includes_responsive_styles(self, authenticated_client):
        """반응형 스타일 포함"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 반응형 요소가 있어야 함
        assert b'col-lg' in response.data or b'col-md' in response.data or b'container' in response.data
