"""
Link5 (RCM 조회/검토) 기능 테스트
RCM 목록, 상세보기, 매핑, 완성도 평가, AI 검토 기능 검증
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# ================================
# RCM 목록 페이지 테스트
# ================================

def test_rcm_list_page_requires_login(client):
    """로그인하지 않으면 RCM 목록 페이지 접근 불가"""
    response = client.get('/rcm')
    assert response.status_code == 302  # 리다이렉트
    assert '/login' in response.location

def test_rcm_list_page_rendering(authenticated_client, test_user):
    """RCM 목록 페이지가 정상 렌더링"""
    response = authenticated_client.get('/rcm')
    assert response.status_code == 200
    assert 'link5_rcm_list.jsp' in response.request.path or b'RCM' in response.data

def test_rcm_list_shows_user_rcms(authenticated_client, test_user):
    """사용자가 접근 권한을 가진 RCM만 표시"""
    response = authenticated_client.get('/rcm')
    assert response.status_code == 200
    # RCM 데이터가 템플릿에 전달되는지 확인
    # 실제 데이터는 get_user_rcms 함수로부터 조회됨

def test_rcm_list_logs_user_activity(authenticated_client, test_user):
    """RCM 목록 페이지 접근 시 활동 로그 기록"""
    with patch('snowball_link5.log_user_activity') as mock_log:
        response = authenticated_client.get('/rcm')
        assert response.status_code == 200
        mock_log.assert_called_once()
        call_args = mock_log.call_args[0]
        assert call_args[1] == 'PAGE_ACCESS'
        assert '사용자 RCM 조회' in call_args[2]

# ================================
# RCM 상세보기 페이지 테스트
# ================================

def test_rcm_view_requires_login(client):
    """로그인하지 않으면 RCM 상세 페이지 접근 불가"""
    response = client.get('/rcm/1/view')
    assert response.status_code == 302
    assert '/login' in response.location

def test_rcm_view_with_valid_rcm(authenticated_client, test_user):
    """유효한 RCM ID로 상세 페이지 접근"""
    with patch('snowball_link5.has_rcm_access', return_value=True):
        with patch('snowball_link5.get_user_rcms', return_value=[
            {'rcm_id': 1, 'rcm_name': 'Test RCM', 'company_name': 'Test Company'}
        ]):
            with patch('snowball_link5.get_rcm_details', return_value=[]):
                response = authenticated_client.get('/rcm/1/view')
                assert response.status_code == 200

def test_rcm_view_without_access(authenticated_client, test_user):
    """접근 권한이 없는 RCM 조회 시 리다이렉트"""
    with patch('snowball_link5.has_rcm_access', return_value=False):
        response = authenticated_client.get('/rcm/999/view')
        assert response.status_code == 302
        assert '/rcm' in response.location

def test_rcm_view_displays_rcm_details(authenticated_client, test_user):
    """RCM 상세 데이터가 페이지에 표시"""
    mock_details = [
        {
            'detail_id': 1,
            'control_code': 'APD01',
            'control_name': 'Test Control',
            'control_description': 'Test Description'
        }
    ]

    with patch('snowball_link5.has_rcm_access', return_value=True):
        with patch('snowball_link5.get_user_rcms', return_value=[
            {'rcm_id': 1, 'rcm_name': 'Test RCM'}
        ]):
            with patch('snowball_link5.get_rcm_details', return_value=mock_details):
                response = authenticated_client.get('/rcm/1/view')
                assert response.status_code == 200

# ================================
# API: RCM 현황 조회 테스트
# ================================

def test_rcm_status_api_requires_login(client):
    """로그인하지 않으면 RCM 현황 API 접근 불가"""
    response = client.get('/api/rcm-status')
    assert response.status_code == 302

def test_rcm_status_api_returns_json(authenticated_client, test_user):
    """RCM 현황 API가 JSON 데이터 반환"""
    with patch('snowball_link5.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/api/rcm-status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert 'rcm_status' in data
        assert 'total_count' in data

def test_rcm_status_includes_evaluation_counts(authenticated_client, test_user):
    """RCM 현황에 설계평가/운영평가 개수 포함"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.count_design_evaluations', return_value=5):
            with patch('snowball_link5.count_operation_evaluations', return_value=3):
                with patch('snowball_link5.get_rcm_details', return_value=[{}, {}, {}, {}, {}, {}, {}, {}, {}, {}]):  # 10개
                    response = authenticated_client.get('/api/rcm-status')
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert len(data['rcm_status']) == 1
                    assert data['rcm_status'][0]['design_evaluated'] == 5
                    assert data['rcm_status'][0]['operation_evaluated'] == 3
                    assert data['rcm_status'][0]['total_controls'] == 10

def test_rcm_status_calculates_progress(authenticated_client, test_user):
    """RCM 현황에서 진행률 계산"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.count_design_evaluations', return_value=5):
            with patch('snowball_link5.count_operation_evaluations', return_value=2):
                with patch('snowball_link5.get_rcm_details', return_value=[{} for _ in range(10)]):  # 10개
                    response = authenticated_client.get('/api/rcm-status')
                    data = json.loads(response.data)
                    assert data['rcm_status'][0]['design_progress'] == 50.0  # 5/10 * 100
                    assert data['rcm_status'][0]['operation_progress'] == 20.0  # 2/10 * 100

# ================================
# API: RCM 목록 조회 테스트
# ================================

def test_rcm_list_api_requires_login(client):
    """로그인하지 않으면 RCM 목록 API 접근 불가"""
    response = client.get('/api/rcm-list')
    assert response.status_code == 302

def test_rcm_list_api_returns_user_rcms(authenticated_client, test_user):
    """RCM 목록 API가 사용자 RCM 목록 반환"""
    mock_rcms = [
        {'rcm_id': 1, 'rcm_name': 'RCM A'},
        {'rcm_id': 2, 'rcm_name': 'RCM B'}
    ]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        response = authenticated_client.get('/api/rcm-list')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['rcms']) == 2

# ================================
# API: 기준통제 초기화 테스트 (관리자 전용)
# ================================

def test_init_standard_controls_requires_admin(authenticated_client, test_user):
    """관리자가 아니면 기준통제 초기화 불가"""
    # test_user는 일반 사용자 (admin_flag != 'Y')
    response = authenticated_client.post('/api/init-standard-controls')
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['success'] is False
    assert '관리자 권한' in data['message']

def test_init_standard_controls_with_admin(authenticated_client, admin_user):
    """관리자는 기준통제 초기화 가능"""
    # admin_user 픽스처 사용
    with patch('snowball_link5.initialize_standard_controls'):
        response = authenticated_client.post('/api/init-standard-controls')
        # admin_user가 제대로 설정되어 있다면 성공
        # 실제로는 conftest.py에 admin_user 픽스처가 필요

# ================================
# API: 기준통제 목록 조회 테스트
# ================================

def test_get_standard_controls_api(authenticated_client, test_user):
    """기준통제 목록 조회 API"""
    mock_controls = [
        {'std_control_id': 1, 'control_code': 'APD01', 'control_name': 'Application 신규 권한 승인'},
        {'std_control_id': 2, 'control_code': 'APD02', 'control_name': 'Application 부서이동자 권한 회수'}
    ]

    with patch('snowball_link5.get_standard_controls', return_value=mock_controls):
        response = authenticated_client.get('/api/standard-controls')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['controls']) == 2

# ================================
# RCM 매핑 페이지 테스트
# ================================

def test_rcm_mapping_page_requires_login(client):
    """로그인하지 않으면 매핑 페이지 접근 불가"""
    response = client.get('/rcm/1/mapping')
    assert response.status_code == 302

def test_rcm_mapping_page_with_access(authenticated_client, test_user):
    """접근 권한이 있으면 매핑 페이지 표시"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_details', return_value=[]):
            with patch('snowball_link5.get_standard_controls', return_value=[]):
                with patch('snowball_link5.get_rcm_detail_mappings', return_value=[]):
                    response = authenticated_client.get('/rcm/1/mapping')
                    assert response.status_code == 200

def test_rcm_mapping_page_without_access(authenticated_client, test_user):
    """접근 권한이 없으면 매핑 페이지 리다이렉트"""
    with patch('snowball_link5.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/rcm/999/mapping')
        assert response.status_code == 302
        assert '/rcm' in response.location

# ================================
# API: RCM 매핑 저장/조회/삭제 테스트
# ================================

def test_rcm_mapping_api_get(authenticated_client, test_user):
    """RCM 매핑 조회 API"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]
    mock_mappings = [
        {'control_code': 'APD01', 'mapped_std_control_id': 1}
    ]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_detail_mappings', return_value=mock_mappings):
            response = authenticated_client.get('/api/rcm/1/mapping')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['mappings']) == 1

def test_rcm_mapping_api_post(authenticated_client, test_user):
    """RCM 매핑 저장 API"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_conn.execute.return_value.fetchone.return_value = {'detail_id': 1}
            mock_db.return_value.__enter__.return_value = mock_conn

            with patch('snowball_link5.save_rcm_mapping'):
                response = authenticated_client.post(
                    '/api/rcm/1/mapping',
                    data=json.dumps({
                        'control_code': 'APD01',
                        'std_control_id': 1
                    }),
                    content_type='application/json'
                )
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True

def test_rcm_mapping_api_delete(authenticated_client, test_user):
    """RCM 매핑 삭제 API"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_conn.execute.return_value.fetchone.return_value = {'detail_id': 1}
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.delete(
                '/api/rcm/1/mapping',
                data=json.dumps({'control_code': 'APD01'}),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

def test_rcm_mapping_api_without_access(authenticated_client, test_user):
    """접근 권한 없는 RCM 매핑 시도"""
    with patch('snowball_link5.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/api/rcm/999/mapping')
        assert response.status_code == 403

# ================================
# API: RCM 완성도 평가 테스트
# ================================

def test_evaluate_completeness_api(authenticated_client, test_user):
    """RCM 완성도 평가 API"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]
    mock_eval_result = {
        'completeness_score': 75.5,
        'total_controls': 10,
        'mapped_controls': 8,
        'details': []
    }

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_details', return_value=[]):
            with patch('snowball_link5.get_standard_controls', return_value=[]):
                with patch('snowball_link5.get_rcm_standard_mappings', return_value=[]):
                    with patch('snowball_link5.evaluate_rcm_completeness', return_value=mock_eval_result):
                        response = authenticated_client.post('/api/rcm/1/evaluate-completeness')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['success'] is True
                        assert data['result']['completeness_score'] == 75.5

def test_evaluate_completeness_without_access(authenticated_client, test_user):
    """접근 권한 없는 RCM 완성도 평가 시도"""
    with patch('snowball_link5.get_user_rcms', return_value=[]):
        response = authenticated_client.post('/api/rcm/999/evaluate-completeness')
        assert response.status_code == 403

# ================================
# 완성도 보고서 페이지 테스트
# ================================

def test_completeness_report_page(authenticated_client, test_user):
    """완성도 보고서 페이지 렌더링"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]
    mock_eval_result = {
        'completeness_score': 80.0,
        'total_controls': 10,
        'mapped_controls': 8,
        'details': []
    }

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_details', return_value=[]):
            with patch('snowball_link5.evaluate_rcm_completeness', return_value=mock_eval_result):
                response = authenticated_client.get('/rcm/1/completeness-report')
                assert response.status_code == 200

def test_completeness_report_handles_errors(authenticated_client, test_user):
    """완성도 평가 오류 시 기본값 반환"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_details', return_value=[]):
            with patch('snowball_link5.evaluate_rcm_completeness', side_effect=Exception('Test error')):
                response = authenticated_client.get('/rcm/1/completeness-report')
                assert response.status_code == 200
                # 에러 발생 시에도 페이지는 렌더링되고 기본값 사용

# ================================
# API: RCM 완료 상태 토글 테스트
# ================================

def test_toggle_rcm_completion_complete(authenticated_client, test_user):
    """RCM 검토 완료 처리"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            with patch('snowball_link5.log_user_activity'):
                response = authenticated_client.post(
                    '/rcm/1/toggle-completion',
                    data=json.dumps({'complete': True}),
                    content_type='application/json'
                )
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert 'RCM 검토가 완료' in data['message']

def test_toggle_rcm_completion_uncomplete(authenticated_client, test_user):
    """RCM 검토 완료 해제"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            with patch('snowball_link5.log_user_activity'):
                response = authenticated_client.post(
                    '/rcm/1/toggle-completion',
                    data=json.dumps({'complete': False}),
                    content_type='application/json'
                )
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert '완료가 해제' in data['message']

# ================================
# API: 개별 통제 검토 결과 저장/조회 테스트
# ================================

def test_control_review_api_get(authenticated_client, test_user):
    """개별 통제 검토 결과 조회"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]
    mock_review = {
        'review_id': 1,
        'std_control_id': 1,
        'ai_review_recommendation': 'Test recommendation',
        'status': 'completed'
    }

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_control_review_result', return_value=mock_review):
            response = authenticated_client.get('/api/rcm/1/detail/1/review')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['has_saved_review'] is True
            assert data['review_result']['std_control_id'] == 1

def test_control_review_api_post(authenticated_client, test_user):
    """개별 통제 검토 결과 저장"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.save_control_review_result'):
            response = authenticated_client.post(
                '/api/rcm/1/detail/1/review',
                data=json.dumps({
                    'std_control_id': 1,
                    'ai_review_recommendation': 'Good control design',
                    'status': 'completed'
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

# ================================
# API: RCM 검토 결과 자동 저장 테스트
# ================================

def test_rcm_review_auto_save(authenticated_client, test_user):
    """RCM 검토 결과 자동 저장"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.save_rcm_review_result', return_value=123):
            response = authenticated_client.post(
                '/api/rcm/1/review/auto-save',
                data=json.dumps({
                    'mapping_data': {'APD01': 1},
                    'ai_review_data': {'APD01': 'Good'}
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['review_id'] == 123

# ================================
# API: AI 검토 테스트
# ================================

def test_control_ai_review_requires_mapping(authenticated_client, test_user):
    """매핑되지 않은 통제는 AI 검토 불가"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]
    mock_detail = {
        'detail_id': 1,
        'control_code': 'APD01',
        'control_name': 'Test Control',
        'mapped_std_control_id': None  # 매핑 안됨
    }

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_details', return_value=[mock_detail]):
            response = authenticated_client.post('/api/rcm/1/detail/1/ai-review')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert '매핑을 완료하세요' in data['message']

def test_control_ai_review_success(authenticated_client, test_user):
    """매핑된 통제의 AI 검토 성공"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]
    mock_detail = {
        'detail_id': 1,
        'control_code': 'APD01',
        'control_name': 'Application 신규 권한 승인',
        'control_description': 'Test description',
        'control_type': 'Preventive',
        'responsible_party': 'IT Team',
        'mapped_std_control_id': 1
    }
    mock_std_control = {
        'std_control_id': 1,
        'control_name': 'Application 신규 권한 승인',
        'control_description': 'Standard control description'
    }

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_rcm_details', return_value=[mock_detail]):
            with patch('snowball_link5.get_standard_controls', return_value=[mock_std_control]):
                with patch('snowball_link5.get_rcm_ai_review', return_value='AI recommendation text'):
                    with patch('snowball_link5.save_rcm_ai_review'):
                        response = authenticated_client.post('/api/rcm/1/detail/1/ai-review')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['success'] is True
                        assert 'recommendation' in data

@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
def test_get_rcm_ai_review_function():
    """get_rcm_ai_review 함수 동작 확인"""
    from snowball_link5 import get_rcm_ai_review

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '개선권고사항: Test AI response'

    with patch('snowball_link5.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        result = get_rcm_ai_review(
            control_content='Test control content',
            std_control_name='APD01'
        )

        assert result == 'Test AI response'  # 접두사 제거 확인
        mock_client.chat.completions.create.assert_called_once()

def test_get_rcm_ai_review_no_api_key():
    """OpenAI API 키가 없을 때 에러 메시지 반환"""
    from snowball_link5 import get_rcm_ai_review

    with patch.dict('os.environ', {}, clear=True):
        result = get_rcm_ai_review('Test content')
        assert 'API 키가 설정되지 않았습니다' in result

# ================================
# API: 개별 통제 매핑 저장/삭제 테스트
# ================================

def test_control_mapping_post(authenticated_client, test_user):
    """개별 통제 매핑 저장"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.save_rcm_mapping'):
            response = authenticated_client.post(
                '/api/rcm/1/detail/1/mapping',
                data=json.dumps({'std_control_id': 1}),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

def test_control_mapping_delete(authenticated_client, test_user):
    """개별 통제 매핑 삭제"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.delete_rcm_mapping'):
            response = authenticated_client.delete('/api/rcm/1/detail/1/mapping')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

# ================================
# API: 기준통제 일괄 매핑 해제 테스트
# ================================

def test_delete_standard_control_mappings(authenticated_client, test_user):
    """특정 기준통제에 매핑된 모든 통제 해제"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link5.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link5.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_result = MagicMock()
            mock_result.rowcount = 5  # 5개 매핑 해제
            mock_conn.execute.return_value = mock_result
            mock_db.return_value.__enter__.return_value = mock_conn

            with patch('snowball_link5.clear_rcm_completion'):
                response = authenticated_client.delete('/api/rcm/1/standard-control/1/mappings')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['affected_count'] == 5

# ================================
# RCM 프롬프트 설정 검증
# ================================

def test_rcm_control_prompts_exist():
    """RCM_CONTROL_PROMPTS에 모든 기준통제 프롬프트 존재"""
    from snowball_link5 import RCM_CONTROL_PROMPTS

    # 기본 프롬프트 존재 확인
    assert 'default' in RCM_CONTROL_PROMPTS

    # 주요 통제코드 프롬프트 존재 확인
    expected_codes = ['APD01', 'APD06', 'APD07', 'APD09', 'APD12',
                      'CO01', 'CO05', 'PC01', 'PC05', 'PD01']
    for code in expected_codes:
        assert code in RCM_CONTROL_PROMPTS
        assert len(RCM_CONTROL_PROMPTS[code]) > 100  # 프롬프트가 충분한 길이

def test_rcm_control_prompts_formatting():
    """RCM 프롬프트가 올바른 변수 플레이스홀더 포함"""
    from snowball_link5 import RCM_CONTROL_PROMPTS

    # default 프롬프트는 {control_content} 포함
    assert '{control_content}' in RCM_CONTROL_PROMPTS['default']

    # APD01 프롬프트도 {control_content} 포함
    assert '{control_content}' in RCM_CONTROL_PROMPTS['APD01']

# ================================
# 헬퍼 함수 테스트
# ================================

def test_get_user_info_from_session(authenticated_client, test_user):
    """세션에서 사용자 정보 조회"""
    from snowball_link5 import get_user_info

    with authenticated_client.session_transaction() as sess:
        sess['user_info'] = {'user_id': 'test_user', 'username': 'Test User'}

    with authenticated_client.application.app_context():
        user_info = get_user_info()
        # 실제로는 세션 컨텍스트에서 작동하는지 확인

def test_is_logged_in_function(authenticated_client, test_user):
    """로그인 상태 확인 함수"""
    from snowball_link5 import is_logged_in

    with authenticated_client.application.app_context():
        # is_logged_in 함수는 main snowball 모듈의 함수 호출
        # 여기서는 함수 존재 여부만 확인
        assert callable(is_logged_in)

# ================================
# RCM 업로드 기능 테스트
# ================================

def test_rcm_upload_page_requires_login(client):
    """로그인하지 않으면 RCM 업로드 페이지 접근 불가"""
    response = client.get('/rcm/upload')
    assert response.status_code == 302
    assert '/login' in response.location

def test_rcm_upload_page_for_regular_user(authenticated_client, test_user):
    """일반 사용자도 RCM 업로드 페이지 접근 가능"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            {'user_id': 1, 'user_name': 'Test', 'user_email': 'test@test.com', 'company_name': 'Test Company'}
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.get('/rcm/upload')
        assert response.status_code == 200

def test_rcm_upload_shows_only_company_users_for_regular_user(authenticated_client, test_user):
    """일반 사용자는 본인 회사 사용자만 조회"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            {'user_id': 1, 'user_name': 'Test', 'user_email': 'test@test.com', 'company_name': 'Test Company'}
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.get('/rcm/upload')
        assert response.status_code == 200
        # SQL에서 company_name 필터링 확인
        call_args = mock_conn.execute.call_args
        assert 'company_name = ?' in str(call_args)

def test_rcm_process_upload_validates_file_type(authenticated_client, test_user):
    """Excel 파일만 업로드 가능"""
    from io import BytesIO

    with patch('snowball_link5.get_db') as mock_db:
        response = authenticated_client.post(
            '/rcm/process_upload',
            data={
                'rcm_name': 'Test RCM',
                'control_category': 'ITGC',
                'description': 'Test',
                'rcm_file': (BytesIO(b'test'), 'test.txt')  # 잘못된 파일 형식
            },
            content_type='multipart/form-data'
        )
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Excel' in data['message']

def test_rcm_process_upload_validates_category(authenticated_client, test_user):
    """유효한 카테고리만 허용"""
    from io import BytesIO

    response = authenticated_client.post(
        '/rcm/process_upload',
        data={
            'rcm_name': 'Test RCM',
            'control_category': 'INVALID',  # 잘못된 카테고리
            'description': 'Test',
            'rcm_file': (BytesIO(b'test'), 'test.xlsx')
        },
        content_type='multipart/form-data'
    )
    data = json.loads(response.data)
    assert data['success'] is False
    assert '카테고리' in data['message']

def test_rcm_process_upload_regular_user_company_check(authenticated_client, test_user):
    """일반 사용자는 다른 회사 사용자에게 권한 부여 불가"""
    from io import BytesIO

    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        # 다른 회사 사용자
        mock_conn.execute.return_value.fetchone.return_value = {'company_name': 'Other Company'}
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.post(
            '/rcm/process_upload',
            data={
                'rcm_name': 'Test RCM',
                'control_category': 'ITGC',
                'description': 'Test',
                'access_users': ['999'],  # 다른 회사 사용자
                'rcm_file': (BytesIO(b'test'), 'test.xlsx')
            },
            content_type='multipart/form-data'
        )
        data = json.loads(response.data)
        assert data['success'] is False
        assert '본인 회사' in data['message']

def test_rcm_process_upload_grants_admin_permission_to_uploader(authenticated_client, test_user):
    """업로드한 사용자에게 admin 권한 자동 부여"""
    from io import BytesIO
    import pandas as pd

    # 테스트용 Excel 데이터
    df = pd.DataFrame({'control_code': ['AC-01'], 'control_name': ['Test Control']})
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)

    with patch('snowball_link5.create_rcm', return_value=123):
        with patch('snowball_link5.save_rcm_details'):
            with patch('snowball_link5.grant_rcm_access') as mock_grant:
                with patch('snowball_link5.log_user_activity'):
                    response = authenticated_client.post(
                        '/rcm/process_upload',
                        data={
                            'rcm_name': 'Test RCM',
                            'control_category': 'ITGC',
                            'description': 'Test',
                            'rcm_file': (excel_buffer, 'test.xlsx')
                        },
                        content_type='multipart/form-data'
                    )
                    data = json.loads(response.data)
                    assert data['success'] is True
                    # 업로드한 사용자에게 admin 권한 부여 확인
                    mock_grant.assert_called()
                    # 첫 번째 호출이 admin 권한 부여인지 확인
                    first_call = mock_grant.call_args_list[0]
                    assert first_call[0][2] == 'admin'

def test_rcm_upload_with_real_excel_file(authenticated_client, test_user):
    """실제 Excel 파일로 RCM 업로드 통합 테스트"""
    from io import BytesIO
    import pandas as pd

    # 실제와 유사한 RCM Excel 데이터 생성
    df = pd.DataFrame({
        'control_code': ['APD01', 'APD07', 'PC01'],
        'control_name': ['권한 관리', '데이터 변경 승인', '프로그램 변경 승인'],
        'control_description': ['신규 권한 승인 절차', 'DB 변경 승인 절차', '소스 변경 승인 절차'],
        'key_control': ['Y', 'Y', 'Y'],
        'control_frequency': ['Monthly', 'Daily', 'Weekly'],
        'control_type': ['예방', '예방', '예방'],
        'control_nature': ['Manual', 'Manual', 'Manual'],
        'test_procedure': ['승인 문서 확인', 'SQL 로그 검토', 'Git 커밋 로그 검토']
    })
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    with patch('snowball_link5.log_user_activity'):
        response = authenticated_client.post(
            '/rcm/process_upload',
            data={
                'rcm_name': '2024 ITGC 테스트',
                'control_category': 'ITGC',
                'description': 'Integration test RCM',
                'header_row': '0',
                'column_mapping': json.dumps({
                    'control_code': 0,
                    'control_name': 1,
                    'control_description': 2,
                    'key_control': 3,
                    'control_frequency': 4,
                    'control_type': 5,
                    'control_nature': 6,
                    'test_procedure': 7
                }),
                'rcm_file': (excel_buffer, 'test_itgc.xlsx')
            },
            content_type='multipart/form-data'
        )
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'rcm_id' in data
        assert data['record_count'] == 3

def test_rcm_upload_with_column_mapping(authenticated_client, test_user):
    """컬럼 매핑 정보를 포함한 업로드 테스트"""
    from io import BytesIO
    import pandas as pd

    # 컬럼명이 다른 Excel 파일
    df = pd.DataFrame({
        '통제코드': ['APD01', 'APD07'],
        '통제명': ['권한 관리', '데이터 변경'],
        '통제설명': ['설명1', '설명2'],
        '핵심통제': ['Y', 'Y'],
        '주기': ['Monthly', 'Daily'],
        '성격': ['예방', '예방'],
        '방법': ['Manual', 'Manual'],
        '테스트': ['확인1', '확인2']
    })
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    # 컬럼 매핑 정보
    column_mapping = {
        'control_code': 0,
        'control_name': 1,
        'control_description': 2,
        'key_control': 3,
        'control_frequency': 4,
        'control_type': 5,
        'control_nature': 6,
        'test_procedure': 7
    }

    with patch('snowball_link5.log_user_activity'):
        response = authenticated_client.post(
            '/rcm/process_upload',
            data={
                'rcm_name': '컬럼 매핑 테스트',
                'control_category': 'ITGC',
                'description': 'Column mapping test',
                'header_row': '0',
                'column_mapping': json.dumps(column_mapping),
                'rcm_file': (excel_buffer, 'mapping_test.xlsx')
            },
            content_type='multipart/form-data'
        )
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'mapping_info' in data

def test_rcm_upload_validates_required_columns(authenticated_client, test_user):
    """필수 컬럼 누락 시 업로드 실패"""
    from io import BytesIO
    import pandas as pd

    # 필수 컬럼(control_code, control_name) 누락
    df = pd.DataFrame({
        'description': ['Test1', 'Test2'],
        'type': ['A', 'B']
    })
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    response = authenticated_client.post(
        '/rcm/process_upload',
        data={
            'rcm_name': '필수 컬럼 누락 테스트',
            'control_category': 'ITGC',
            'description': 'Should fail',
            'rcm_file': (excel_buffer, 'incomplete.xlsx')
        },
        content_type='multipart/form-data'
    )
    data = json.loads(response.data)
    assert data['success'] is False
    # 필수 컬럼 누락 에러 확인

# ================================
# RCM 삭제 기능 테스트 (평가 상태별)
# ================================

def test_check_ongoing_evaluations_function():
    """진행 중인 평가 확인 함수 테스트"""
    from snowball_link5 import check_ongoing_evaluations

    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        # 설계평가 진행 중
        design_cursor = MagicMock()
        design_cursor.fetchall.return_value = [
            {'evaluation_session': '2024-01', 'evaluation_status': 'IN_PROGRESS'}
        ]
        # 운영평가 없음
        operation_cursor = MagicMock()
        operation_cursor.fetchall.return_value = []

        mock_conn.execute.side_effect = [design_cursor, operation_cursor]
        mock_db.return_value.__enter__.return_value = mock_conn

        result = check_ongoing_evaluations(1, 1)
        assert result['has_design'] is True
        assert result['has_operation'] is False
        assert len(result['design_sessions']) == 1

def test_rcm_delete_requires_admin_permission(authenticated_client, test_user):
    """RCM 삭제는 admin 권한 필요"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.side_effect = [
            {'rcm_name': 'Test RCM', 'upload_user_id': 999},  # RCM 정보
            None  # 권한 없음
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.post('/rcm/1/delete')
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'admin 권한' in data['message']

def test_rcm_delete_blocked_during_operation_evaluation(authenticated_client, test_user):
    """운영평가 진행 중에는 RCM 삭제 불가"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.side_effect = [
            {'rcm_name': 'Test RCM', 'upload_user_id': 1},
            {'permission_type': 'admin'}  # admin 권한 있음
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        with patch('snowball_link5.check_ongoing_evaluations', return_value={
            'has_design': False,
            'has_operation': True,
            'design_sessions': [],
            'operation_sessions': [{'evaluation_session': '2024-01'}]
        }):
            response = authenticated_client.post(
                '/rcm/1/delete',
                data=json.dumps({'force': False}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            assert data['success'] is False
            assert '운영평가가 진행 중' in data['message']
            assert data['ongoing_operation'] is True

def test_rcm_delete_warning_during_design_evaluation(authenticated_client, test_user):
    """설계평가 진행 중에는 경고 메시지 표시"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.side_effect = [
            {'rcm_name': 'Test RCM', 'upload_user_id': 1},
            {'permission_type': 'admin'}
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        with patch('snowball_link5.check_ongoing_evaluations', return_value={
            'has_design': True,
            'has_operation': False,
            'design_sessions': [{'evaluation_session': '2024-01', 'evaluation_status': 'IN_PROGRESS'}],
            'operation_sessions': []
        }):
            response = authenticated_client.post(
                '/rcm/1/delete',
                data=json.dumps({'force': False}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            assert data['success'] is False
            assert '진행 중인 설계평가' in data['message']
            assert data['ongoing_design'] is True
            assert data['require_confirmation'] is True

def test_rcm_delete_force_with_design_evaluation(authenticated_client, test_user):
    """force=true로 설계평가 진행 중에도 삭제 가능"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.side_effect = [
            {'rcm_name': 'Test RCM', 'upload_user_id': 1},
            {'permission_type': 'admin'}
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        with patch('snowball_link5.check_ongoing_evaluations', return_value={
            'has_design': True,
            'has_operation': False,
            'design_sessions': [{'evaluation_session': '2024-01', 'evaluation_status': 'IN_PROGRESS'}],
            'operation_sessions': []
        }):
            with patch('snowball_link5.log_user_activity'):
                response = authenticated_client.post(
                    '/rcm/1/delete',
                    data=json.dumps({'force': True}),
                    content_type='application/json'
                )
                data = json.loads(response.data)
                assert data['success'] is True
                # 설계평가가 ARCHIVED 상태로 변경되었는지 확인
                archive_call = [call for call in mock_conn.execute.call_args_list
                               if 'ARCHIVED' in str(call)]
                assert len(archive_call) > 0

def test_rcm_delete_success_no_evaluations(authenticated_client, test_user):
    """진행 중인 평가가 없으면 자유롭게 삭제"""
    with patch('snowball_link5.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.side_effect = [
            {'rcm_name': 'Test RCM', 'upload_user_id': 1},
            {'permission_type': 'admin'}
        ]
        mock_db.return_value.__enter__.return_value = mock_conn

        with patch('snowball_link5.check_ongoing_evaluations', return_value={
            'has_design': False,
            'has_operation': False,
            'design_sessions': [],
            'operation_sessions': []
        }):
            with patch('snowball_link5.log_user_activity'):
                response = authenticated_client.post(
                    '/rcm/1/delete',
                    data=json.dumps({'force': False}),
                    content_type='application/json'
                )
                data = json.loads(response.data)
                assert data['success'] is True
                assert '삭제되었습니다' in data['message']
