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
