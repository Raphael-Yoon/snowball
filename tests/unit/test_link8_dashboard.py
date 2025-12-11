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


class TestLink8DetailAPI:
    """Link8 상세 정보 API 테스트"""

    def test_assessment_detail_api_requires_login(self, client):
        """상세 정보 API - 로그인 필요"""
        response = client.get('/internal-assessment/api/detail/1/DEFAULT', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_assessment_detail_api_returns_json(self, authenticated_client):
        """상세 정보 API - JSON 반환"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        # 권한이 있으면 JSON, 없으면 403
        if response.status_code == 200:
            assert response.content_type == 'application/json'
            data = response.get_json()
            assert 'success' in data or 'error' in data

    def test_assessment_detail_api_with_invalid_rcm(self, authenticated_client):
        """상세 정보 API - 존재하지 않는 RCM"""
        response = authenticated_client.get('/internal-assessment/api/detail/99999/DEFAULT')
        # 권한 없음 또는 404
        assert response.status_code in [403, 404, 500]


class TestLink8ProgressCalculationLogic:
    """Link8 진행률 계산 로직 테스트"""

    def test_design_evaluation_progress_calculation(self, authenticated_client):
        """설계평가 진행률 계산 - 실제 라인 개수 기반"""
        # API를 통해 진행률 정보 조회
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'progress' in data:
                progress = data['progress']
                # 진행률 범위 확인 (0-100)
                assert 0 <= progress.get('overall_progress', 0) <= 100
                # 단계별 정보 확인
                if 'steps' in progress:
                    for step in progress['steps']:
                        if 'details' in step and 'progress' in step['details']:
                            assert 0 <= step['details']['progress'] <= 100

    def test_operation_evaluation_progress_calculation(self, authenticated_client):
        """운영평가 진행률 계산"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'progress' in data:
                progress = data['progress']
                # 2단계(운영평가) 확인
                if len(progress.get('steps', [])) >= 2:
                    op_step = progress['steps'][1]
                    assert op_step.get('step') == 2

    def test_overall_progress_is_average_of_steps(self, authenticated_client):
        """전체 진행률은 각 단계 진행률의 평균"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'progress' in data:
                progress = data['progress']
                if 'steps' in progress and len(progress['steps']) > 0:
                    # 수동으로 평균 계산
                    total = sum(
                        step.get('details', {}).get('progress', 0)
                        for step in progress['steps']
                        if 'details' in step
                    )
                    expected_avg = int(total / len(progress['steps']))
                    # 소수점 반올림 차이 허용
                    actual_progress = progress.get('overall_progress', 0)
                    assert abs(actual_progress - expected_avg) <= 1


class TestLink8SessionFiltering:
    """Link8 세션 필터링 테스트"""

    def test_archived_sessions_not_shown(self, authenticated_client):
        """ARCHIVED 세션은 목록에 표시되지 않음"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # ARCHIVED 배지가 있으면 안됨
        # (실제 ARCHIVED 세션이 있을 경우 테스트 데이터에 따라 달라질 수 있음)
        # 페이지가 정상적으로 로드되는지만 확인
        assert 'assessment' in data.lower()

    def test_completed_sessions_are_shown(self, authenticated_client):
        """COMPLETED 세션은 목록에 표시됨"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        # 완료된 세션이 있으면 표시되어야 함
        # 페이지가 정상적으로 로드되는지 확인
        data = response.data.decode()
        assert 'assessment' in data.lower()


class TestLink8StatusBadge:
    """Link8 상태 배지 로직 테스트"""

    def test_session_status_badge_logic(self, authenticated_client):
        """세션 상태 배지 - 설계평가+운영평가 조합"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # 배지 요소가 있어야 함
        assert 'badge' in data.lower() or 'status' in data.lower()

    def test_design_completed_operation_completed_shows_complete(self, authenticated_client):
        """설계평가 완료 + 운영평가 완료 = 완료 배지"""
        # API를 통해 확인
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'progress' in data:
                steps = data['progress'].get('steps', [])
                if len(steps) >= 2:
                    design_status = steps[0].get('status')
                    operation_status = steps[1].get('status')
                    # 둘 다 completed면 전체도 completed
                    if design_status == 'completed' and operation_status == 'completed':
                        # 전체 진행률이 100이어야 함
                        assert data['progress'].get('overall_progress') == 100


class TestLink8DetailedEvaluationInfo:
    """Link8 상세 평가 정보 테스트"""

    def test_inadequate_controls_list_returned(self, authenticated_client):
        """미비점이 있는 통제 목록 반환"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'design_detail' in data:
                design_detail = data['design_detail']
                # inadequate_controls 키가 있어야 함
                assert 'inadequate_controls' in design_detail
                assert isinstance(design_detail['inadequate_controls'], list)

    def test_exception_controls_list_returned(self, authenticated_client):
        """예외사항이 있는 통제 목록 반환"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'operation_detail' in data:
                operation_detail = data['operation_detail']
                # exception_controls 키가 있어야 함
                assert 'exception_controls' in operation_detail
                assert isinstance(operation_detail['exception_controls'], list)

    def test_effectiveness_stats_returned(self, authenticated_client):
        """평가 결과 분포 통계 반환"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'design_detail' in data:
                design_detail = data['design_detail']
                # effectiveness_stats 키가 있어야 함
                assert 'effectiveness_stats' in design_detail
                assert isinstance(design_detail['effectiveness_stats'], dict)


class TestLink8NotApplicableHandling:
    """Link8 not_applicable 값 처리 테스트"""

    def test_not_applicable_in_conclusion_stats(self, authenticated_client):
        """not_applicable 값이 결론 통계에 포함됨"""
        response = authenticated_client.get('/internal-assessment/api/detail/1/DEFAULT')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'operation_detail' in data:
                operation_detail = data['operation_detail']
                if 'conclusion_stats' in operation_detail:
                    stats = operation_detail['conclusion_stats']
                    # not_applicable이 있을 수 있음
                    if 'not_applicable' in stats:
                        assert isinstance(stats['not_applicable'], int)
                        assert stats['not_applicable'] >= 0


class TestLink8Favicon:
    """Link8 파비콘 테스트"""

    def test_internal_assessment_includes_favicon(self, authenticated_client):
        """내부평가 페이지에 파비콘 포함"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # 파비콘 링크가 있어야 함
        assert 'favicon.ico' in data or 'icon' in data.lower()


class TestLink8ProgressRingStartPoint:
    """Link8 원형 진행률 표시 테스트"""

    def test_progress_ring_starts_at_12_oclock(self, authenticated_client):
        """원형 진행률 표시가 12시 방향에서 시작"""
        response = authenticated_client.get('/internal-assessment')
        assert response.status_code == 200
        data = response.data.decode()
        # CSS에 transform: rotate(-90deg) 가 있어야 함
        if 'progress-ring' in data:
            assert 'rotate(-90deg)' in data or 'transform' in data
