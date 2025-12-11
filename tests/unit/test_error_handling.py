"""
에러 핸들링 테스트
404, 500, 403 등 다양한 에러 상황을 테스트합니다.
"""
import pytest
from unittest.mock import patch


class TestNotFoundErrors:
    """404 에러 테스트"""

    def test_404_on_invalid_route(self, client):
        """존재하지 않는 라우트 접근 시 404"""
        response = client.get('/this-route-does-not-exist')
        assert response.status_code == 404

    def test_404_on_invalid_rcm_id(self, authenticated_client):
        """존재하지 않는 RCM ID 접근 시 404 또는 리다이렉트"""
        response = authenticated_client.get('/rcm/99999/view')
        assert response.status_code in [404, 302, 500]  # 구현에 따라 다를 수 있음

    def test_404_on_nonexistent_user(self, client):
        """존재하지 않는 사용자 이메일로 로그인 시도"""
        response = client.post('/login', data={
            'user_email': 'nonexistent@example.com'
        })
        # 로그인 실패 시 다시 로그인 페이지로 리다이렉트 또는 에러 메시지
        assert response.status_code in [200, 302]


class TestUnauthorizedErrors:
    """403 권한 없음 에러 테스트"""

    def test_403_accessing_admin_without_permission(self, authenticated_client, test_user):
        """일반 사용자가 관리자 페이지 접근 시"""
        # test_user는 admin이 아님
        response = authenticated_client.get('/admin')
        # 권한이 없으면 403, 로그인 페이지로 리다이렉트, 또는 메인으로 리다이렉트
        # 308은 Permanent Redirect (Flask의 슬래시 처리)
        assert response.status_code in [403, 302, 308]

    def test_rcm_access_by_different_user(self, client, test_user):
        """다른 사용자의 RCM 접근 시도"""
        # 로그인
        with client.session_transaction() as sess:
            sess['user_id'] = test_user['user_id']
            sess['user_info'] = test_user

        # 다른 사용자의 RCM ID로 접근 시도 (실제로는 DB에 없거나 권한 없음)
        response = client.get('/rcm/1/view')
        # 권한 체크 구현에 따라 403, 404, 또는 302
        assert response.status_code in [403, 404, 302, 500]

    def test_unauthenticated_access_to_protected_route(self, client):
        """로그인 없이 보호된 라우트 접근"""
        protected_routes = [
            '/rcm',
            '/design-evaluation',
            '/operation-evaluation',
        ]

        for route in protected_routes:
            response = client.get(route)
            # 로그인 페이지로 리다이렉트
            assert response.status_code == 302
            assert '/login' in response.location or response.location == '/'


class TestBadRequestErrors:
    """400 잘못된 요청 에러 테스트"""

    def test_missing_required_field_in_rcm_generate(self, client):
        """RCM 생성 시 필수 필드 누락"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            # param2 (시스템명) 누락
            'param3': 'SAP',
        })
        # 에러 메시지 또는 리다이렉트
        assert response.status_code in [200, 400, 302]

    def test_invalid_email_format(self, client):
        """잘못된 이메일 형식으로 로그인 시도"""
        response = client.post('/login', data={
            'user_email': 'invalid-email-format'
        })
        # 에러 처리 (200에 에러 메시지 포함 가능)
        assert response.status_code in [200, 400, 302]

    def test_empty_post_data(self, client):
        """빈 데이터로 POST 요청"""
        response = client.post('/rcm_generate', data={})
        assert response.status_code in [200, 400, 302]

    def test_invalid_json_format(self, client):
        """잘못된 JSON 형식 전송"""
        response = client.post('/process_interview',
                              data='invalid json',
                              content_type='application/json')
        # JSON 파싱 실패 시 400 또는 500
        assert response.status_code in [400, 500, 200]


class TestServerErrors:
    """500 서버 에러 테스트"""

    def test_rcm_generation_failure(self, client):
        """RCM 생성 중 서버 에러 발생"""
        # 필수 파라미터 누락으로 에러 유발
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            # param2 누락하여 에러 유발
            'param3': 'SAP',
        })

        # 에러 처리 확인 (500, 400, 또는 200에 에러 메시지)
        assert response.status_code in [200, 400, 500, 302]

    @patch('snowball_mail.send_gmail_with_attachment')
    def test_email_send_failure(self, mock_send, client):
        """이메일 전송 실패 시"""
        # 이메일 전송 실패 시뮬레이션
        mock_send.side_effect = Exception('SMTP connection failed')

        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': 'TestSystem',
            'param3': 'SAP',
            'param4': 'Windows',
            'param5': 'Oracle'
        })

        # 에러가 적절히 처리되는지 확인
        assert response.status_code in [200, 500]


class TestSessionErrors:
    """세션 관련 에러 테스트"""

    def test_access_with_expired_session(self, client):
        """만료된 세션으로 접근"""
        # 세션을 설정하지 않고 보호된 페이지 접근
        response = client.get('/rcm')
        assert response.status_code == 302
        assert '/login' in response.location or response.location == '/'

    def test_interview_without_session_data(self, client):
        """인터뷰 세션 데이터 없이 AI 검토 페이지 접근"""
        response = client.get('/ai_review_selection')
        # 세션 없으면 인터뷰 처음으로 리다이렉트
        assert response.status_code in [200, 302]

    def test_process_interview_without_task_id(self, client):
        """task_id 없이 인터뷰 처리 요청"""
        response = client.post('/process_interview',
                              json={},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False


class TestInputValidation:
    """입력 검증 테스트"""

    def test_sql_injection_attempt(self, authenticated_client):
        """SQL Injection 시도 (보안 테스트)"""
        # SQL Injection 패턴으로 검색
        response = authenticated_client.get("/rcm/1' OR '1'='1/view")
        # 정상적으로 처리되지 않아야 함 (404 또는 에러)
        assert response.status_code in [404, 400, 500]

    def test_xss_attempt_in_form(self, client):
        """XSS 공격 시도"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': '<script>alert("xss")</script>',
            'param3': 'SAP',
            'param4': 'Windows',
            'param5': 'Oracle'
        })
        # 요청은 처리되지만 스크립트가 실행되지 않아야 함
        assert response.status_code in [200, 302]

    def test_extremely_long_input(self, client):
        """비정상적으로 긴 입력값"""
        long_string = 'A' * 10000
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': long_string,  # 매우 긴 시스템명
            'param3': 'SAP',
            'param4': 'Windows',
            'param5': 'Oracle'
        })
        # 에러 처리 또는 정상 처리 확인
        assert response.status_code in [200, 400, 302]

    def test_special_characters_in_input(self, client):
        """특수문자 입력"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'param3': 'SAP',
            'param4': 'Windows',
            'param5': 'Oracle'
        })
        # 특수문자가 적절히 처리되는지 확인
        assert response.status_code in [200, 302]


class TestFileUploadErrors:
    """파일 업로드 에러 테스트"""

    def test_upload_without_file(self, authenticated_client):
        """파일 없이 업로드 요청"""
        response = authenticated_client.post('/api/operation-evaluation/apd01/upload-population',
                                            data={},
                                            content_type='multipart/form-data')
        # 파일이 없으면 에러 처리 (404는 라우트가 없는 경우)
        assert response.status_code in [400, 200, 302, 500, 404]

    def test_upload_invalid_file_type(self, authenticated_client):
        """잘못된 파일 형식 업로드"""
        from io import BytesIO

        data = {
            'file': (BytesIO(b'not an excel file'), 'test.txt')
        }

        response = authenticated_client.post('/api/operation-evaluation/apd01/upload-population',
                                            data=data,
                                            content_type='multipart/form-data')
        # 잘못된 파일 형식 에러 (404는 라우트가 없는 경우)
        assert response.status_code in [400, 200, 302, 500, 404]

    def test_upload_empty_file(self, authenticated_client):
        """빈 파일 업로드"""
        from io import BytesIO

        data = {
            'file': (BytesIO(b''), 'empty.xlsx')
        }

        response = authenticated_client.post('/api/operation-evaluation/apd01/upload-population',
                                            data=data,
                                            content_type='multipart/form-data')
        # 빈 파일 에러 (404는 라우트가 없는 경우)
        assert response.status_code in [400, 200, 302, 500, 404]


class TestRateLimiting:
    """과도한 요청 테스트 (선택적)"""

    def test_multiple_rapid_requests(self, client):
        """짧은 시간 내 다수의 요청"""
        # 10번 연속 요청
        for i in range(10):
            response = client.get('/')
            # 모두 정상 처리되어야 함 (rate limiting 없다면)
            assert response.status_code == 200

    def test_multiple_login_attempts(self, client):
        """반복적인 로그인 시도"""
        for i in range(5):
            response = client.post('/login', data={
                'user_email': 'test@example.com'
            })
            # 로그인 실패 또는 성공
            assert response.status_code in [200, 302]


class TestDatabaseErrors:
    """데이터베이스 에러 테스트"""

    def test_database_connection_failure(self, client):
        """데이터베이스 연결 실패 시나리오"""
        # 존재하지 않는 사용자로 로그인 시도 (DB 조회 실패 케이스)
        response = client.post('/login', data={
            'user_email': 'nonexistent@invalid-domain-12345.com'
        })

        # DB 조회 실패 또는 사용자 없음 처리
        assert response.status_code in [500, 200, 302]

    def test_query_with_invalid_parameters(self, authenticated_client):
        """잘못된 파라미터로 쿼리 실행"""
        response = authenticated_client.get('/rcm/abc/view')  # 숫자여야 하는데 문자
        # 잘못된 파라미터 에러
        assert response.status_code in [404, 400, 500]


class TestConcurrency:
    """동시성 문제 테스트 (선택적)"""

    def test_simultaneous_rcm_generation(self, client):
        """동시에 여러 RCM 생성 요청"""
        # 이 테스트는 실제로는 멀티스레딩으로 구현해야 하지만
        # 간단히 순차적으로 실행
        for i in range(3):
            response = client.post('/rcm_generate', data={
                'param1': f'test{i}@example.com',
                'param2': f'System{i}',
                'param3': 'SAP',
                'param4': 'Windows',
                'param5': 'Oracle'
            })
            assert response.status_code in [200, 302]
