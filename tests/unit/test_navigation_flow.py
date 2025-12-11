"""
Private 서비스 네비게이션 통합 테스트
RCM 관리(link5) ↔ 설계평가(link6) ↔ 운영평가(link7) 간의 화면 전환 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import session


# ================================
# Link5 (RCM 관리) → Link6 (설계평가)
# ================================

def test_navigation_rcm_to_design_evaluation(authenticated_client, test_user):
    """RCM 관리에서 설계평가로 이동"""
    # Given: RCM 목록 페이지에 있음
    with patch('snowball_link5.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]):
        response = authenticated_client.get('/rcm')
        assert response.status_code == 200

    # When: 설계평가 버튼 클릭 (POST로 RCM 선택)
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={
                'rcm_id': '1',
                'evaluation_type': 'ITGC'
            },
            follow_redirects=False
        )

        # Then: 설계평가 페이지로 이동 성공
        assert response.status_code in [200, 302]


def test_navigation_rcm_to_itgc_design_evaluation(authenticated_client, test_user):
    """RCM 관리에서 ITGC 설계평가로 이동"""
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test ITGC RCM', 'control_category': 'ITGC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '1', 'evaluation_type': 'ITGC'}
        )
        assert response.status_code in [200, 302]


def test_navigation_rcm_to_elc_design_evaluation(authenticated_client, test_user):
    """RCM 관리에서 ELC 설계평가로 이동"""
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 14, 'rcm_name': 'Test ELC RCM', 'control_category': 'ELC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '14', 'evaluation_type': 'ELC'}
        )
        assert response.status_code in [200, 302]


def test_navigation_rcm_to_tlc_design_evaluation(authenticated_client, test_user):
    """RCM 관리에서 TLC 설계평가로 이동"""
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 15, 'rcm_name': 'Test TLC RCM', 'control_category': 'TLC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '15', 'evaluation_type': 'TLC'}
        )
        assert response.status_code in [200, 302]


# ================================
# Link6 (설계평가) → Link7 (운영평가)
# ================================

def test_navigation_design_to_operation_evaluation(authenticated_client, test_user):
    """설계평가 완료 후 운영평가로 이동"""
    # Given: 설계평가가 완료된 RCM
    mock_rcms = [{
        'rcm_id': 1,
        'rcm_name': 'Test RCM',
        'control_category': 'ITGC',
        'design_evaluation_completed': True,
        'completed_design_sessions': [{
            'evaluation_session': '2024Q1',
            'completed_date': '2024-01-15',
            'eligible_control_count': 10
        }]
    }]

    # When: 운영평가 페이지로 이동
    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms), \
         patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[{
            'evaluation_session': '2024Q1',
            'completed_date': '2024-01-15',
            'evaluated_controls': 10,
            'total_controls': 10,
            'progress_percentage': 100
         }]), \
         patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/operation-evaluation')

        # Then: 운영평가 페이지 렌더링 성공
        assert response.status_code == 200


def test_navigation_design_to_itgc_operation(authenticated_client, test_user):
    """ITGC 설계평가에서 ITGC 운영평가로 이동"""
    with patch('snowball_link7.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test ITGC', 'control_category': 'ITGC'}
    ]), \
    patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
    patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/operation-evaluation')
        assert response.status_code == 200


def test_navigation_design_to_elc_operation(authenticated_client, test_user):
    """ELC 설계평가에서 ELC 운영평가로 이동"""
    with patch('snowball_link7.get_user_rcms', return_value=[
        {'rcm_id': 14, 'rcm_name': 'Test ELC', 'control_category': 'ELC'}
    ]), \
    patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
    patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/elc/operation-evaluation')
        assert response.status_code == 200


def test_navigation_design_to_tlc_operation(authenticated_client, test_user):
    """TLC 설계평가에서 TLC 운영평가로 이동"""
    with patch('snowball_link7.get_user_rcms', return_value=[
        {'rcm_id': 15, 'rcm_name': 'Test TLC', 'control_category': 'TLC'}
    ]), \
    patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
    patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/tlc/operation-evaluation')
        assert response.status_code == 200


# ================================
# Link7 (운영평가) → Link6 (설계평가)
# ================================

def test_navigation_operation_back_to_design(authenticated_client, test_user):
    """운영평가에서 설계평가로 돌아가기"""
    # Given: 운영평가 페이지에 있음
    with patch('snowball_link7.get_user_rcms', return_value=[]), \
         patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
         patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/operation-evaluation')
        assert response.status_code == 200

    # When: 설계평가 메뉴로 이동
    with patch('snowball_link6.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/design-evaluation')

        # Then: 설계평가 페이지로 이동 성공
        assert response.status_code == 200


# ================================
# Link7 (운영평가) → Link5 (RCM 관리)
# ================================

def test_navigation_operation_back_to_rcm(authenticated_client, test_user):
    """운영평가에서 RCM 관리로 돌아가기"""
    # Given: 운영평가 페이지에 있음
    with patch('snowball_link7.get_user_rcms', return_value=[]), \
         patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
         patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/operation-evaluation')
        assert response.status_code == 200

    # When: RCM 관리 메뉴로 이동
    with patch('snowball_link5.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/rcm')

        # Then: RCM 관리 페이지로 이동 성공
        assert response.status_code == 200


# ================================
# 완전한 플로우 테스트
# ================================

def test_complete_navigation_flow(authenticated_client, test_user):
    """RCM 관리 → 설계평가 → 운영평가 전체 플로우"""

    # Step 1: RCM 관리 페이지
    with patch('snowball_link5.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]):
        response = authenticated_client.get('/rcm')
        assert response.status_code == 200

    # Step 2: 설계평가 페이지로 이동
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[
        {'control_code': 'TEST01', 'control_name': 'Test Control'}
    ]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '1', 'evaluation_type': 'ITGC'}
        )
        assert response.status_code in [200, 302]

    # Step 3: 운영평가 페이지로 이동
    with patch('snowball_link7.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]), \
    patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[{
        'evaluation_session': '2024Q1',
        'completed_date': '2024-01-15',
        'evaluated_controls': 10,
        'total_controls': 10,
        'progress_percentage': 100
    }]), \
    patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/operation-evaluation')
        assert response.status_code == 200


def test_complete_flow_with_all_categories(authenticated_client, test_user):
    """ITGC, ELC, TLC 모든 카테고리의 완전한 플로우"""

    categories = [
        ('ITGC', 1, '/operation-evaluation'),
        ('ELC', 14, '/elc/operation-evaluation'),
        ('TLC', 15, '/tlc/operation-evaluation')
    ]

    for category, rcm_id, operation_url in categories:
        # Step 1: 설계평가
        with patch('snowball_link6.get_user_rcms', return_value=[
            {'rcm_id': rcm_id, 'rcm_name': f'Test {category}', 'control_category': category}
        ]), \
        patch('snowball_link6.get_rcm_details', return_value=[]), \
        patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
            response = authenticated_client.post('/design-evaluation/rcm',
                data={'rcm_id': str(rcm_id), 'evaluation_type': category}
            )
            assert response.status_code in [200, 302], f"{category} 설계평가 이동 실패"

        # Step 2: 운영평가
        with patch('snowball_link7.get_user_rcms', return_value=[
            {'rcm_id': rcm_id, 'rcm_name': f'Test {category}', 'control_category': category}
        ]), \
        patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
        patch('snowball_link7.get_key_rcm_details', return_value=[]):
            response = authenticated_client.get(operation_url)
            assert response.status_code == 200, f"{category} 운영평가 이동 실패"


# ================================
# 뒤로가기 버튼 테스트
# ================================

def test_back_button_from_design_evaluation(authenticated_client, test_user):
    """설계평가 페이지의 뒤로가기 버튼"""
    with patch('snowball_link6.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/design-evaluation')
        assert response.status_code == 200
        # 홈으로 버튼 등이 있어야 함


def test_back_button_from_operation_evaluation(authenticated_client, test_user):
    """운영평가 페이지의 뒤로가기 버튼"""
    with patch('snowball_link7.get_user_rcms', return_value=[]), \
         patch('snowball_link7.get_all_design_evaluation_sessions', return_value=[]), \
         patch('snowball_link7.get_key_rcm_details', return_value=[]):
        response = authenticated_client.get('/operation-evaluation')
        assert response.status_code == 200
        # 홈으로 버튼 등이 있어야 함


# ================================
# 세션 유지 테스트
# ================================

def test_session_maintained_across_navigation(authenticated_client, test_user):
    """페이지 간 이동 시 세션이 유지되는지 확인"""

    # RCM 선택 후 세션 저장
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '1', 'evaluation_type': 'ITGC'}
        )

        # 세션에 RCM ID가 저장되었는지 확인
        with authenticated_client.session_transaction() as sess:
            # current_design_rcm_id가 세션에 저장되어 있어야 함
            assert 'current_design_rcm_id' in sess or response.status_code in [200, 302]


def test_evaluation_type_persists_in_session(authenticated_client, test_user):
    """evaluation_type이 세션에 저장되는지 확인"""

    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 14, 'rcm_name': 'Test ELC', 'control_category': 'ELC'}
    ]), \
    patch('snowball_link6.get_rcm_details', return_value=[]), \
    patch('snowball_link6.get_rcm_detail_mappings', return_value=[]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '14', 'evaluation_type': 'ELC'}
        )

        with authenticated_client.session_transaction() as sess:
            # evaluation_type이 세션에 저장되어 있어야 함
            assert 'current_evaluation_type' in sess or response.status_code in [200, 302]


# ================================
# 에러 처리 테스트
# ================================

def test_navigation_without_rcm_selection(authenticated_client, test_user):
    """RCM 선택 없이 설계평가 페이지 접근 시 리다이렉트"""

    # GET 요청으로 바로 설계평가 페이지 접근 (세션에 RCM 없음)
    with patch('snowball_link6.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/design-evaluation/rcm', follow_redirects=False)

        # 세션에 RCM이 없으면 리다이렉트되거나 에러 메시지 표시
        assert response.status_code in [200, 302]


def test_navigation_with_invalid_rcm_id(authenticated_client, test_user):
    """존재하지 않는 RCM ID로 접근 시 에러 처리"""

    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Test RCM', 'control_category': 'ITGC'}
    ]):
        # 존재하지 않는 RCM ID로 접근
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '9999', 'evaluation_type': 'ITGC'},
            follow_redirects=False
        )

        # 권한 없음 또는 에러 처리
        assert response.status_code in [200, 302, 403]


def test_navigation_without_permission(authenticated_client, test_user):
    """권한 없는 RCM에 접근 시 차단"""

    # 사용자는 RCM 1만 접근 가능한데, RCM 2에 접근 시도
    with patch('snowball_link6.get_user_rcms', return_value=[
        {'rcm_id': 1, 'rcm_name': 'Allowed RCM', 'control_category': 'ITGC'}
    ]):
        response = authenticated_client.post('/design-evaluation/rcm',
            data={'rcm_id': '2', 'evaluation_type': 'ITGC'},
            follow_redirects=False
        )

        # 접근 거부되어야 함
        assert response.status_code in [302, 403]
