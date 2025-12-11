"""
Link9 (Contact Us) 기능 테스트
문의하기, 서비스 문의, 피드백 전송 기능 검증
"""

import pytest
import json
from unittest.mock import patch, MagicMock

# ================================
# Contact Us 페이지 테스트
# ================================

def test_contact_page_renders(client):
    """Contact Us 페이지 렌더링"""
    response = client.get('/contact')
    assert response.status_code == 200

def test_contact_page_accessible_without_login(client):
    """로그인 없이도 Contact Us 페이지 접근 가능"""
    response = client.get('/contact')
    assert response.status_code == 200

def test_contact_page_with_authenticated_user(authenticated_client, test_user):
    """로그인 사용자의 Contact Us 페이지"""
    response = authenticated_client.get('/contact')
    assert response.status_code == 200

# ================================
# Contact 메시지 전송 테스트
# ================================

def test_contact_form_submission(client):
    """Contact 폼 제출"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/contact', data={
            'name': 'Test User',
            'company_name': 'Test Company',
            'email': 'test@example.com',
            'message': 'Test message'
        })
        assert response.status_code == 200
        assert b'success' in response.data or b'Success' in response.data or response.status_code == 200

def test_contact_form_sends_email(client):
    """Contact 폼 제출 시 이메일 전송"""
    with patch('snowball_link9.send_gmail') as mock_send:
        response = client.post('/contact', data={
            'name': 'Test User',
            'company_name': 'Test Company',
            'email': 'test@example.com',
            'message': 'Test inquiry'
        })
        assert response.status_code == 200
        # send_gmail이 호출되었는지 확인
        mock_send.assert_called_once()

def test_contact_form_email_failure(client):
    """이메일 전송 실패 시 에러 처리"""
    with patch('snowball_link9.send_gmail', side_effect=Exception('Email error')):
        response = client.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test'
        })
        assert response.status_code == 200
        # 에러가 발생해도 페이지는 렌더링됨

# ================================
# 서비스 문의 테스트
# ================================

def test_service_inquiry(client):
    """서비스 가입 문의 전송"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/service_inquiry', data={
            'company_name': 'Test Corp',
            'contact_name': 'John Doe',
            'contact_email': 'john@example.com'
        })
        assert response.status_code == 200

def test_service_inquiry_sends_confirmation_email(client):
    """서비스 문의 시 확인 이메일 전송"""
    with patch('snowball_link9.send_gmail') as mock_send:
        response = client.post('/service_inquiry', data={
            'company_name': 'Test Corp',
            'contact_name': 'John Doe',
            'contact_email': 'john@example.com'
        })
        assert response.status_code == 200
        # send_gmail 호출 확인
        mock_send.assert_called_once()

def test_service_inquiry_error_handling(client):
    """서비스 문의 실패 시 에러 처리"""
    with patch('snowball_link9.send_gmail', side_effect=Exception('Email error')):
        response = client.post('/service_inquiry', data={
            'company_name': 'Test Corp',
            'contact_name': 'John Doe',
            'contact_email': 'john@example.com'
        })
        assert response.status_code == 200
        # 에러가 있어도 페이지 렌더링

# ================================
# API: Contact 메시지 전송 테스트
# ================================

def test_contact_api_send_message(client):
    """Contact API로 메시지 전송"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/api/contact/send',
            data=json.dumps({
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': '일반 문의',
                'message': 'Test message content'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

def test_contact_api_missing_fields(client):
    """필수 필드 누락 시 에러"""
    response = client.post('/api/contact/send',
        data=json.dumps({
            'name': 'Test User'
            # email, message 누락
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False

def test_contact_api_sends_auto_reply(client):
    """Contact API가 자동 응답 메일 전송"""
    with patch('snowball_link9.send_gmail') as mock_send:
        response = client.post('/api/contact/send',
            data=json.dumps({
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': '문의',
                'message': 'Test message'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        # send_gmail이 2번 호출 (1. 관리자에게, 2. 자동응답)
        assert mock_send.call_count == 2

def test_contact_api_error_handling(client):
    """Contact API 에러 처리"""
    with patch('snowball_link9.send_gmail', side_effect=Exception('Email error')):
        response = client.post('/api/contact/send',
            data=json.dumps({
                'name': 'Test User',
                'email': 'test@example.com',
                'message': 'Test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False

# ================================
# API: 피드백 전송 테스트
# ================================

def test_feedback_api_submit(client):
    """피드백 전송 API"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/api/feedback',
            data=json.dumps({
                'type': '기능 개선 제안',
                'content': 'Great service!',
                'rating': 5,
                'email': 'user@example.com'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

def test_feedback_api_anonymous(client):
    """익명 피드백 전송"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/api/feedback',
            data=json.dumps({
                'type': '일반 피드백',
                'content': 'Good service'
                # email 생략 (익명)
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

def test_feedback_api_missing_content(client):
    """피드백 내용 누락 시 에러"""
    response = client.post('/api/feedback',
        data=json.dumps({
            'type': '피드백'
            # content 누락
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False

def test_feedback_api_with_rating(client):
    """평점 포함 피드백"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/api/feedback',
            data=json.dumps({
                'content': 'Excellent service',
                'rating': 5
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

def test_feedback_api_error_handling(client):
    """피드백 전송 중 에러 처리"""
    with patch('snowball_link9.send_gmail', side_effect=Exception('Email error')):
        response = client.post('/api/feedback',
            data=json.dumps({
                'content': 'Test feedback'
            }),
            content_type='application/json'
        )
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False

# ================================
# 헬퍼 함수 테스트
# ================================

def test_get_user_info_function():
    """get_user_info 함수 존재 확인"""
    from snowball_link9 import get_user_info
    assert callable(get_user_info)

def test_is_logged_in_function():
    """is_logged_in 함수 존재 확인"""
    from snowball_link9 import is_logged_in
    assert callable(is_logged_in)

# ================================
# 블루프린트 등록 확인
# ================================

def test_link9_blueprint_registered(app):
    """Link9 블루프린트가 앱에 등록되어 있는지 확인"""
    assert 'link9' in [bp.name for bp in app.blueprints.values()]

def test_link9_routes_exist(app):
    """Link9의 주요 라우트 존재 확인"""
    routes = [rule.rule for rule in app.url_map.iter_rules()]

    assert any('/contact' in route for route in routes)
    assert any('/service_inquiry' in route for route in routes)
    assert any('/api/contact/send' in route for route in routes)
    assert any('/api/feedback' in route for route in routes)

# ================================
# 통합 시나리오 테스트
# ================================

def test_contact_full_workflow(client):
    """Contact Us 전체 워크플로우"""
    # 1. Contact 페이지 접근
    response = client.get('/contact')
    assert response.status_code == 200

    # 2. Contact 폼 제출
    with patch('snowball_link9.send_gmail'):
        response = client.post('/contact', data={
            'name': 'Test User',
            'company_name': 'Test Co',
            'email': 'test@example.com',
            'message': 'Test inquiry'
        })
        assert response.status_code == 200

def test_service_inquiry_workflow(client):
    """서비스 문의 워크플로우"""
    with patch('snowball_link9.send_gmail'):
        response = client.post('/service_inquiry', data={
            'company_name': 'NewCorp',
            'contact_name': 'Jane Doe',
            'contact_email': 'jane@newcorp.com'
        })
        assert response.status_code == 200

def test_feedback_workflow(client):
    """피드백 워크플로우"""
    with patch('snowball_link9.send_gmail'):
        # API를 통한 피드백 전송
        response = client.post('/api/feedback',
            data=json.dumps({
                'type': '버그 리포트',
                'content': 'Found a bug in the system',
                'rating': 4,
                'email': 'reporter@example.com'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
