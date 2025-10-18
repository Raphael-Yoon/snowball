"""
Tests for core routing functionality
"""
import pytest


class TestPublicPages:
    """Test publicly accessible pages"""

    def test_index_page(self, client):
        """Test main index page is accessible"""
        response = client.get('/')
        assert response.status_code == 200

    def test_login_page(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'

    def test_link0_reload(self, client):
        """Test link0 (reload) page"""
        response = client.get('/link0')
        assert response.status_code == 200

    def test_link1_rcm(self, client):
        """Test link1 (RCM) page is accessible"""
        response = client.get('/link1')
        assert response.status_code == 200

    def test_link3_paper(self, client):
        """Test link3 (Paper) page is accessible"""
        response = client.get('/link3')
        assert response.status_code == 200

    def test_link4_video(self, client):
        """Test link4 (Video) page is accessible"""
        response = client.get('/link4')
        assert response.status_code == 200


class TestAuthenticatedPages:
    """Test pages that require authentication"""

    def test_authenticated_index_shows_username(self, authenticated_client, test_user):
        """Test index page shows user name when authenticated"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert test_user['user_name'].encode() in response.data

    def test_link2_interview_authenticated(self, authenticated_client, test_user):
        """Test interview page for authenticated user (should skip email question)"""
        response = authenticated_client.get('/link2')
        assert response.status_code == 200
        # Authenticated users should have email pre-filled


class TestSessionManagement:
    """Test session management endpoints"""

    def test_extend_session_authenticated(self, authenticated_client):
        """Test session extension for authenticated user"""
        response = authenticated_client.post('/extend_session')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True

    def test_extend_session_unauthenticated(self, client):
        """Test session extension fails for unauthenticated user"""
        response = client.post('/extend_session')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False

    def test_logout_redirects(self, authenticated_client):
        """Test logout redirects to index"""
        response = authenticated_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith('/')


class TestInterviewFlow:
    """Test interview (link2) flow"""

    def test_link2_initial_access(self, client):
        """Test initial access to interview page"""
        response = client.get('/link2')
        assert response.status_code == 200

    def test_link2_reset_parameter(self, client):
        """Test interview reset with query parameter"""
        response = client.get('/link2?reset=1')
        assert response.status_code == 200

    def test_link2_authenticated_starts_at_question_1(self, authenticated_client):
        """Test authenticated user starts at question 1 (email pre-filled)"""
        # Reset first
        response = authenticated_client.get('/link2?reset=1')
        assert response.status_code == 200

        # Check session
        with authenticated_client.session_transaction() as session:
            assert 'question_index' in session
            # Authenticated users skip email question
            assert session['question_index'] == 1


class TestContentEndpoints:
    """Test dynamic content endpoints"""

    def test_get_content_link3(self, client):
        """Test link3 content endpoint"""
        response = client.get('/get_content_link3')
        assert response.status_code == 200

    def test_get_content_link4_no_type(self, client):
        """Test link4 content without type parameter"""
        response = client.get('/get_content_link4')
        assert response.status_code == 200
        assert '준비 중' in response.data.decode('utf-8')


class TestRCMGeneration:
    """Test RCM generation endpoint"""

    def test_rcm_generate_missing_data(self, client):
        """Test RCM generation with missing data"""
        response = client.post('/rcm_generate', data={})
        assert response.status_code == 200
        # Should handle missing data gracefully


class TestAIReviewFlow:
    """Test AI review selection flow"""

    def test_ai_review_selection_without_session(self, client):
        """Test AI review selection redirects when no session"""
        response = client.get('/ai_review_selection', follow_redirects=False)
        # Should redirect to link2 if no session data
        assert response.status_code in [200, 302]

    def test_processing_page(self, client):
        """Test processing page is accessible"""
        with client.session_transaction() as session:
            session['answer'] = ['test@example.com'] + [''] * 20
            session['enable_ai_review'] = False

        response = client.get('/processing')
        assert response.status_code == 200


class TestEmailUpdate:
    """Test email update functionality"""

    def test_update_session_email_valid(self, client):
        """Test updating session email with valid email"""
        with client.session_transaction() as session:
            session['answer'] = ['old@example.com'] + [''] * 20

        response = client.post('/update_session_email',
                              json={'email': 'new@example.com'},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True

    def test_update_session_email_invalid(self, client):
        """Test updating session email with invalid email"""
        with client.session_transaction() as session:
            session['answer'] = ['old@example.com'] + [''] * 20

        response = client.post('/update_session_email',
                              json={'email': 'invalid-email'},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False

    def test_update_session_email_empty(self, client):
        """Test updating session email with empty email"""
        with client.session_transaction() as session:
            session['answer'] = ['old@example.com'] + [''] * 20

        response = client.post('/update_session_email',
                              json={'email': ''},
                              content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False
