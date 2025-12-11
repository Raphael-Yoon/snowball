"""
Tests for interview functionality (link2)
"""
import pytest
from unittest.mock import patch, MagicMock
from snowball_link2 import (
    get_conditional_questions,
    clear_skipped_answers,
    s_questions,
    question_count,
    export_interview_excel_and_send
)


class TestConditionalQuestions:
    """Test conditional question filtering logic"""

    def test_get_conditional_questions_all_empty(self):
        """Test with all empty answers"""
        answers = [''] * question_count
        filtered = get_conditional_questions(answers)
        # Should return at least some questions
        assert len(filtered) > 0
        assert all('index' in q for q in filtered)

    def test_get_conditional_questions_basic(self):
        """Test basic question filtering"""
        answers = ['test@example.com'] + [''] * (question_count - 1)
        filtered = get_conditional_questions(answers)
        assert len(filtered) > 0
        # First question (email) should be included
        assert any(q['index'] == 0 for q in filtered)


class TestClearSkippedAnswers:
    """Test clearing skipped answers"""

    def test_clear_skipped_answers_basic(self):
        """Test clearing skipped answers"""
        answers = ['test@example.com', 'answer1', '', 'answer3']
        textarea_answers = ['', 'textarea1', '', 'textarea3']

        clear_skipped_answers(answers, textarea_answers)

        # Function should maintain structure
        assert len(answers) == 4
        assert len(textarea_answers) == 4


class TestInterviewSessionFlow:
    """Test interview session flow"""

    def test_interview_initial_load_unauthenticated(self, client):
        """Test initial interview load for unauthenticated user"""
        response = client.get('/link2')
        assert response.status_code == 200

        # Check session initialization
        with client.session_transaction() as session:
            assert 'question_index' in session
            assert 'answer' in session
            assert 'textarea_answer' in session

    def test_interview_initial_load_authenticated(self, authenticated_client, test_user):
        """Test initial interview load for authenticated user"""
        response = authenticated_client.get('/link2?reset=1')
        assert response.status_code == 200

        # Check session initialization with email pre-filled
        with authenticated_client.session_transaction() as session:
            assert session['question_index'] == 1  # Skip email question
            assert session['answer'][0] == test_user['user_email']

    def test_interview_answer_submission(self, client):
        """Test submitting an answer to interview question"""
        # Initialize session
        with client.session_transaction() as session:
            session['question_index'] = 0
            session['answer'] = [''] * question_count
            session['textarea_answer'] = [''] * question_count

        # Submit answer
        response = client.post('/link2', data={
            'a0': 'test@example.com',
            'a0_1': ''
        })

        # Should redirect or show next question
        assert response.status_code in [200, 302]

    def test_interview_previous_navigation(self, client):
        """Test going back to previous question"""
        # Set up session at question 2
        with client.session_transaction() as session:
            session['question_index'] = 2
            session['answer'] = ['test@example.com', 'answer1', ''] + [''] * (question_count - 3)
            session['textarea_answer'] = [''] * question_count

        # Go to previous question
        response = client.get('/link2/prev', follow_redirects=False)
        assert response.status_code == 302

    def test_interview_reset(self, client):
        """Test interview reset functionality"""
        # Set some session data
        with client.session_transaction() as session:
            session['question_index'] = 5
            session['answer'] = ['old@example.com'] + ['answer'] * (question_count - 1)

        # Reset interview
        response = client.get('/link2?reset=1')
        assert response.status_code == 200

        # Check session is reset
        with client.session_transaction() as session:
            assert session['question_index'] == 0
            assert all(ans == '' for ans in session['answer'])


class TestAIReviewSelection:
    """Test AI review selection functionality"""

    def test_ai_review_selection_page_with_session(self, client):
        """Test AI review selection page with valid session"""
        with client.session_transaction() as session:
            session['answer'] = ['test@example.com'] + ['answer'] * (question_count - 1)
            session['textarea_answer'] = [''] * question_count

        response = client.get('/ai_review_selection')
        assert response.status_code == 200
        assert 'test@example.com' in response.data.decode('utf-8')

    def test_ai_review_selection_without_email(self, client):
        """Test AI review selection redirects when no email in session"""
        response = client.get('/ai_review_selection', follow_redirects=False)
        # Should redirect to link2 to start interview
        assert response.status_code in [200, 302]

    def test_process_with_ai_enabled(self, client, test_user):
        """Test processing with AI review enabled"""
        with client.session_transaction() as session:
            session['user_id'] = test_user['user_id']
            session['user_info'] = test_user
            session['answer'] = ['test@example.com'] + ['answer'] * (question_count - 1)

        response = client.post('/process_with_ai_option', data={
            'enable_ai_review': 'true'
        }, follow_redirects=False)

        assert response.status_code == 302

        # Check AI review flag is set
        with client.session_transaction() as session:
            assert session.get('enable_ai_review') == True

    def test_process_with_ai_disabled(self, client):
        """Test processing with AI review disabled"""
        with client.session_transaction() as session:
            session['answer'] = ['test@example.com'] + ['answer'] * (question_count - 1)

        response = client.post('/process_with_ai_option', data={
            'enable_ai_review': 'false'
        }, follow_redirects=False)

        assert response.status_code == 302

        # Check AI review flag is set to False
        with client.session_transaction() as session:
            assert session.get('enable_ai_review') == False


class TestProgressTracking:
    """Test progress tracking for interview processing"""

    def test_get_progress_no_task_id(self, client):
        """Test progress endpoint without task_id"""
        response = client.get('/get_progress')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_progress_with_task_id(self, client):
        """Test progress endpoint with task_id"""
        import uuid
        task_id = str(uuid.uuid4())

        response = client.get(f'/get_progress?task_id={task_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'percentage' in data
        assert 'current_task' in data


class TestInterviewProcessing:
    """Test interview data processing"""

    def test_process_interview_no_task_id(self, client):
        """Test processing without task_id"""
        response = client.post('/process_interview',
                              json={},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False

    def test_process_interview_no_data(self, client):
        """Test processing without interview data"""
        import uuid
        task_id = str(uuid.uuid4())

        response = client.post('/process_interview',
                              json={'task_id': task_id},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False


class TestQuestionData:
    """Test question data structure"""

    def test_questions_have_required_fields(self):
        """Test all questions have required fields"""
        for idx, question in enumerate(s_questions):
            # Questions use 'text' instead of 'question_text'
            assert 'text' in question, f"Question {idx} missing text"
            assert 'answer_type' in question, f"Question {idx} missing answer_type"
            assert 'index' in question, f"Question {idx} missing index"

    def test_question_count_matches(self):
        """Test question_count variable matches actual questions"""
        assert question_count == len(s_questions)


class TestInterviewEmailSending:
    """Test email sending functionality for interview processing"""

    def test_export_interview_excel_and_send_function_exists(self):
        """export_interview_excel_and_send 함수 존재 확인"""
        assert callable(export_interview_excel_and_send)

    def test_export_interview_sends_email(self):
        """인터뷰 처리 시 이메일 전송 확인"""
        # Mock dependencies
        mock_send_gmail = MagicMock(return_value=None)
        mock_get_text_itgc = MagicMock(return_value="Test ITGC text")
        mock_fill_sheet = MagicMock()
        mock_is_ineffective = MagicMock(return_value=False)

        # Test data
        answers = ['test@example.com', 'System Name'] + ['answer'] * (question_count - 2)
        textarea_answers = [''] * question_count

        # Execute
        success, email, error = export_interview_excel_and_send(
            answers, textarea_answers,
            mock_get_text_itgc, mock_fill_sheet, mock_is_ineffective,
            mock_send_gmail, enable_ai_review=False
        )

        # Verify email was sent
        assert success is True
        assert email == 'test@example.com'
        mock_send_gmail.assert_called_once()

    def test_export_interview_email_includes_attachment(self):
        """이메일에 엑셀 파일이 첨부되는지 확인"""
        mock_send_gmail = MagicMock(return_value=None)
        mock_get_text_itgc = MagicMock(return_value="Test ITGC text")
        mock_fill_sheet = MagicMock()
        mock_is_ineffective = MagicMock(return_value=False)

        answers = ['user@example.com', 'TestSystem'] + ['answer'] * (question_count - 2)
        textarea_answers = [''] * question_count

        success, email, error = export_interview_excel_and_send(
            answers, textarea_answers,
            mock_get_text_itgc, mock_fill_sheet, mock_is_ineffective,
            mock_send_gmail, enable_ai_review=False
        )

        # Check that send_gmail_with_attachment was called with file_stream and file_name
        assert mock_send_gmail.called
        call_kwargs = mock_send_gmail.call_args[1]
        assert 'file_stream' in call_kwargs
        assert 'file_name' in call_kwargs
        assert call_kwargs['to'] == 'user@example.com'

    def test_export_interview_email_failure(self):
        """이메일 전송 실패 시 에러 처리"""
        mock_send_gmail = MagicMock(side_effect=Exception('Email error'))
        mock_get_text_itgc = MagicMock(return_value="Test ITGC text")
        mock_fill_sheet = MagicMock()
        mock_is_ineffective = MagicMock(return_value=False)

        answers = ['test@example.com', 'System'] + ['answer'] * (question_count - 2)
        textarea_answers = [''] * question_count

        success, email, error = export_interview_excel_and_send(
            answers, textarea_answers,
            mock_get_text_itgc, mock_fill_sheet, mock_is_ineffective,
            mock_send_gmail, enable_ai_review=False
        )

        # Should handle error gracefully
        assert success is False
        assert error is not None

    def test_export_interview_with_ai_review(self, app):
        """AI 검토 활성화 시 이메일 전송"""
        mock_send_gmail = MagicMock(return_value=None)
        mock_get_text_itgc = MagicMock(return_value="Test ITGC text")
        mock_fill_sheet = MagicMock()
        mock_is_ineffective = MagicMock(return_value=False)

        answers = ['ai@example.com', 'AISystem'] + ['answer'] * (question_count - 2)
        textarea_answers = [''] * question_count

        # AI review requires app context
        with app.app_context():
            success, email, error = export_interview_excel_and_send(
                answers, textarea_answers,
                mock_get_text_itgc, mock_fill_sheet, mock_is_ineffective,
                mock_send_gmail, enable_ai_review=True
            )

        assert success is True
        assert email == 'ai@example.com'
        mock_send_gmail.assert_called_once()

    def test_export_interview_filename_generation(self):
        """한글 시스템명이 파일명에 포함되는지 확인"""
        mock_send_gmail = MagicMock(return_value=None)
        mock_get_text_itgc = MagicMock(return_value="Test ITGC text")
        mock_fill_sheet = MagicMock()
        mock_is_ineffective = MagicMock(return_value=False)

        answers = ['test@example.com', '재무시스템'] + ['answer'] * (question_count - 2)
        textarea_answers = [''] * question_count

        success, email, error = export_interview_excel_and_send(
            answers, textarea_answers,
            mock_get_text_itgc, mock_fill_sheet, mock_is_ineffective,
            mock_send_gmail, enable_ai_review=False
        )

        # Check that file_name contains the system name
        assert mock_send_gmail.called
        call_kwargs = mock_send_gmail.call_args[1]
        assert '재무시스템' in call_kwargs['file_name']
        assert '.xlsx' in call_kwargs['file_name']

    def test_export_interview_progress_callback(self):
        """진행률 콜백이 호출되는지 확인"""
        mock_send_gmail = MagicMock(return_value=None)
        mock_get_text_itgc = MagicMock(return_value="Test ITGC text")
        mock_fill_sheet = MagicMock()
        mock_is_ineffective = MagicMock(return_value=False)
        mock_progress = MagicMock()

        answers = ['test@example.com', 'System'] + ['answer'] * (question_count - 2)
        textarea_answers = [''] * question_count

        success, email, error = export_interview_excel_and_send(
            answers, textarea_answers,
            mock_get_text_itgc, mock_fill_sheet, mock_is_ineffective,
            mock_send_gmail, enable_ai_review=False,
            progress_callback=mock_progress
        )

        # Progress callback should be called multiple times
        assert mock_progress.called
        assert mock_progress.call_count > 0
