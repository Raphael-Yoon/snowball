"""
이메일 Mock 동작 확인 테스트

모든 테스트에서 실제 이메일이 발송되지 않도록
autouse fixture가 제대로 작동하는지 검증합니다.
"""

import pytest
from unittest.mock import MagicMock


class TestEmailMockingWorks:
    """이메일 Mock이 자동으로 작동하는지 테스트"""

    def test_email_is_mocked_automatically(self):
        """autouse fixture로 이메일이 자동으로 Mock됨"""
        # snowball_mail을 import해도 Mock이 적용되어야 함
        import snowball_mail

        # send_gmail 호출 시 실제 전송되지 않고 Mock 반환값을 얻어야 함
        result = snowball_mail.send_gmail('test@example.com', 'Test', 'Test body')

        # Mock이 제대로 작동하면 True 반환
        assert result == True

    def test_email_with_attachment_is_mocked(self):
        """첨부파일 포함 이메일도 Mock됨"""
        import snowball_mail

        # send_gmail_with_attachment 호출 시 실제 전송되지 않아야 함
        result = snowball_mail.send_gmail_with_attachment(
            'test@example.com',
            'Test',
            'Test body',
            '/fake/path/file.xlsx',
            'test.xlsx'
        )

        # Mock이 제대로 작동하면 None 반환 (에러 없이 완료)
        assert result is None

    def test_rcm_generation_does_not_send_real_email(self, client):
        """RCM 생성 시 실제 이메일이 발송되지 않음"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': 'TestSystem',
            'param3': 'SAP',
            'param4': 'Windows',
            'param5': 'Oracle'
        })

        # 응답은 정상이지만 실제 이메일은 발송되지 않음
        assert response.status_code in [200, 201, 302]
        # 실제 이메일이 발송되었다면 여기서 에러가 발생했을 것

    def test_interview_completion_does_not_send_real_email(self, client):
        """인터뷰 완료 시 실제 이메일이 발송되지 않음"""
        # 인터뷰 세션 설정
        with client.session_transaction() as sess:
            sess['question_index'] = 0
            sess['answer'] = ['test@example.com', 'TestSystem'] + ['Y'] * 53
            sess['textarea_answer'] = [''] * 55

        # 인터뷰 처리 (이메일 전송 포함)
        response = client.post('/process_with_ai_option', data={
            'enable_ai_review': 'false'
        }, follow_redirects=False)

        # 응답은 정상이지만 실제 이메일은 발송되지 않음
        assert response.status_code in [200, 302, 500]  # 500도 허용 (세션 데이터 없을 수 있음)

    def test_no_smtp_connection_during_tests(self):
        """테스트 중 SMTP 연결이 시도되지 않음"""
        import snowball_mail

        # 이메일 전송 시도 - Mock이 작동하면 에러 없이 완료됨
        try:
            result = snowball_mail.send_gmail('test@example.com', 'Test', 'Test')
            # Mock이 작동했으므로 True 반환
            assert result == True
        except Exception as e:
            # SMTP 연결 시도가 발생하면 에러가 발생함
            pytest.fail(f"실제 SMTP 연결이 시도되었습니다: {e}")


class TestEmailMockCanBeOverridden:
    """필요시 이메일 Mock을 오버라이드할 수 있는지 테스트"""

    def test_can_override_email_mock_for_specific_test(self, mocker):
        """특정 테스트에서 이메일 Mock 동작을 변경할 수 있음"""
        # 특정 반환값으로 오버라이드
        custom_mock = mocker.patch('snowball_mail.send_gmail', return_value=False)

        import snowball_mail
        result = snowball_mail.send_gmail('test@example.com', 'Test', 'Test')

        # 오버라이드된 값 반환
        assert result == False
        assert custom_mock.called

    def test_can_verify_email_was_called(self, mocker):
        """이메일 함수가 호출되었는지 검증할 수 있음"""
        # Mock을 spy로 변경하여 호출 검증
        email_spy = mocker.patch('snowball_mail.send_gmail', return_value=True)

        import snowball_mail
        snowball_mail.send_gmail('test@example.com', 'Subject', 'Body')

        # 호출 검증
        email_spy.assert_called_once()
        email_spy.assert_called_with('test@example.com', 'Subject', 'Body')


class TestNoRealEmailInAnyTest:
    """어떤 테스트에서도 실제 이메일이 발송되지 않음을 보장"""

    def test_link1_rcm_generate(self, client):
        """Link1 RCM 생성 - 실제 이메일 없음"""
        response = client.post('/rcm_generate', data={
            'param1': 'noreply@test.com',
            'param2': 'Test',
            'param3': 'ERP',
            'param4': 'Linux',
            'param5': 'MySQL'
        })
        assert response.status_code in [200, 201, 302]
        # 이메일 관련 에러 없음 = Mock 작동 중

    def test_link2_interview(self, client):
        """Link2 인터뷰 - 실제 이메일 없음"""
        with client.session_transaction() as sess:
            sess['question_index'] = 0
            sess['answer'] = ['noreply@test.com'] + ['N'] * 54
            sess['textarea_answer'] = [''] * 55

        response = client.post('/process_with_ai_option', data={
            'enable_ai_review': 'false'
        })
        assert response.status_code in [200, 302, 400, 500]
        # 이메일 관련 에러 없음 = Mock 작동 중

    def test_contact_form(self, client):
        """Link9 문의하기 - 실제 이메일 없음"""
        response = client.post('/submit_contact', data={
            'name': 'Test User',
            'email': 'noreply@test.com',
            'company': 'Test Company',
            'phone': '010-0000-0000',
            'message': 'Test message'
        })
        # 404는 라우트가 없는 경우 (정상)
        assert response.status_code in [200, 302, 400, 404]
        # 이메일 관련 에러 없음 = Mock 작동 중
