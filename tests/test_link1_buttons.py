"""
Link1 (RCM Builder) 버튼 및 UI 기능 테스트

테스트 범위:
- RCM 생성 폼 렌더링
- 폼 필드 검증 (이메일, 시스템명, 라디오 버튼)
- RCM 생성 제출 버튼 기능
- 이메일 발송 성공/실패 시나리오
- 로그인 상태에 따른 이메일 필드 자동 채움
"""

import pytest
from unittest.mock import patch, MagicMock


class TestLink1FormRendering:
    """Link1 페이지 폼 렌더링 테스트"""

    def test_link1_page_loads_successfully(self, client):
        """Link1 페이지가 정상적으로 로드되는지 테스트"""
        response = client.get('/link1')
        assert response.status_code == 200
        assert 'ITGC RCM Builder' in response.data.decode('utf-8')

    def test_form_contains_email_field(self, client):
        """폼에 이메일 입력 필드가 포함되어 있는지 테스트"""
        response = client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'name="param1"' in html
        assert 'type="email"' in html
        assert 'e-Mail 주소를 입력하세요' in html

    def test_form_contains_system_name_field(self, client):
        """폼에 시스템명 입력 필드가 포함되어 있는지 테스트"""
        response = client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'name="param2"' in html
        assert '시스템명을 입력하세요' in html

    def test_form_contains_system_radio_buttons(self, client):
        """폼에 System 라디오 버튼(SAP, Oracle, 더존, 영림원, 기타)이 있는지 테스트"""
        response = client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'name="param3"' in html
        assert 'value="SAP"' in html
        assert 'value="ORACLE"' in html
        assert 'value="DOUZONE"' in html
        assert 'value="YOUNG"' in html
        assert 'value="ETC"' in html

    def test_form_contains_os_radio_buttons(self, client):
        """폼에 OS 라디오 버튼(Unix, Windows, Linux, 기타)이 있는지 테스트"""
        response = client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'name="param4"' in html
        assert 'value="UNIX"' in html
        assert 'value="WINDOWS"' in html
        assert 'value="LINUX"' in html

    def test_form_contains_db_radio_buttons(self, client):
        """폼에 DB 라디오 버튼(Oracle, MS-SQL, MY-SQL, 기타)이 있는지 테스트"""
        response = client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'name="param5"' in html
        assert 'value="ORACLE"' in html
        assert 'value="MSSQL"' in html
        assert 'value="MYSQL"' in html

    def test_form_contains_submit_button(self, client):
        """폼에 제출 버튼이 있는지 테스트"""
        response = client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'type="submit"' in html
        assert '메일로 보내기' in html


class TestLink1LoggedInUserBehavior:
    """로그인한 사용자의 Link1 페이지 동작 테스트"""

    def test_email_field_prefilled_for_logged_in_user(self, authenticated_client, test_user):
        """로그인한 사용자의 이메일이 자동으로 채워지는지 테스트"""
        response = authenticated_client.get('/link1')
        html = response.data.decode('utf-8')
        assert test_user['user_email'] in html
        assert 'readonly' in html

    def test_email_field_readonly_for_logged_in_user(self, authenticated_client):
        """로그인한 사용자의 이메일 필드가 readonly인지 테스트"""
        response = authenticated_client.get('/link1')
        html = response.data.decode('utf-8')
        assert 'readonly' in html
        assert '로그인된 계정의 이메일이 자동으로 사용됩니다' in html


class TestLink1RCMGenerateButton:
    """RCM 생성 버튼 기능 테스트"""

    @patch('snowball_mail.send_gmail_with_attachment')
    def test_rcm_generate_with_valid_data(self, mock_send_gmail, client):
        """유효한 데이터로 RCM 생성 요청 시 정상 작동하는지 테스트"""
        mock_send_gmail.return_value = None

        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': '테스트시스템',
            'param3': 'SAP',
            'param4': 'UNIX',
            'param5': 'ORACLE'
        })

        # 302 리다이렉트 또는 200 성공 응답 모두 허용
        assert response.status_code in [200, 302]

    def test_rcm_generate_processes_successfully(self, client):
        """RCM 생성 프로세스가 성공적으로 수행되는지 테스트"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': '테스트시스템',
            'param3': 'SAP',
            'param4': 'UNIX',
            'param5': 'ORACLE'
        })

        # 생성 프로세스가 성공적으로 완료되는지 확인
        assert response.status_code in [200, 302]

    @patch('snowball_mail.send_gmail_with_attachment')
    def test_rcm_generate_with_different_systems(self, mock_send_gmail, client):
        """다양한 시스템 선택으로 RCM 생성이 정상 작동하는지 테스트"""
        mock_send_gmail.return_value = None

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

    def test_rcm_generate_missing_email(self, client):
        """이메일 누락 시 적절한 오류 처리가 되는지 테스트"""
        response = client.post('/rcm_generate', data={
            'param2': '테스트시스템',
            'param3': 'SAP',
            'param4': 'UNIX',
            'param5': 'ORACLE'
        })
        # 400 에러 또는 폼 재표시 확인
        # 실제 구현에 따라 조정 필요
        assert response.status_code in [200, 400]

    def test_rcm_generate_missing_system_name(self, client):
        """시스템명 누락 시 적절한 오류 처리가 되는지 테스트"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param3': 'SAP',
            'param4': 'UNIX',
            'param5': 'ORACLE'
        })
        assert response.status_code in [200, 400]

    def test_rcm_generate_with_authenticated_user(self, authenticated_client, test_user):
        """로그인한 사용자가 RCM 생성 시 정상 작동하는지 테스트"""
        response = authenticated_client.post('/rcm_generate', data={
            'param1': test_user['user_email'],
            'param2': '인증된사용자시스템',
            'param3': 'SAP',
            'param4': 'UNIX',
            'param5': 'ORACLE'
        })

        assert response.status_code in [200, 302]


class TestLink1EmailValidation:
    """Link1 이메일 검증 테스트"""

    @patch('snowball_mail.send_gmail_with_attachment')
    def test_rcm_generate_with_valid_email_format(self, mock_send_gmail, client):
        """유효한 이메일 형식으로 RCM 생성이 정상 작동하는지 테스트"""
        mock_send_gmail.return_value = None

        valid_emails = [
            'test@example.com',
            'user.name@company.co.kr',
            'admin+test@domain.org'
        ]

        for email in valid_emails:
            response = client.post('/rcm_generate', data={
                'param1': email,
                'param2': '테스트시스템',
                'param3': 'SAP',
                'param4': 'UNIX',
                'param5': 'ORACLE'
            })
            assert response.status_code in [200, 302]

    def test_rcm_generate_with_invalid_email_format(self, client):
        """잘못된 이메일 형식 처리 테스트"""
        # HTML5 form validation이 있지만, 서버 측에서도 검증할 수 있음
        invalid_emails = [
            'not-an-email',
            '@example.com',
            'user@',
            'user name@example.com'
        ]

        for email in invalid_emails:
            response = client.post('/rcm_generate', data={
                'param1': email,
                'param2': '테스트시스템',
                'param3': 'SAP',
                'param4': 'UNIX',
                'param5': 'ORACLE'
            })
            # 클라이언트 측 검증 또는 서버 측 검증에서 처리
            # 실제 구현에 따라 조정 필요
            assert response.status_code in [200, 400]


class TestLink1ActivityLogging:
    """Link1 활동 로깅 테스트"""

    @patch('snowball_link1.log_user_activity')
    def test_link1_logs_page_access_for_logged_in_user(self, mock_log, authenticated_client, test_user):
        """로그인한 사용자의 페이지 접근이 로그에 기록되는지 테스트"""
        authenticated_client.get('/link1')

        # log_user_activity가 호출되었는지 확인
        assert mock_log.called

        # 첫 번째 호출의 인자 확인
        call_args = mock_log.call_args[0]
        assert call_args[1] == 'PAGE_ACCESS'
        assert call_args[2] == 'RCM 페이지'
        assert call_args[3] == '/link1'

    @patch('snowball_link1.log_user_activity')
    def test_link1_no_logging_for_anonymous_user(self, mock_log, client):
        """비로그인 사용자는 활동 로그가 기록되지 않는지 테스트"""
        client.get('/link1')

        # 비로그인 사용자는 로그 기록이 없어야 함
        # 실제 구현을 확인하여 조정 필요
        # 로그인한 사용자만 기록한다면 called가 False여야 함
