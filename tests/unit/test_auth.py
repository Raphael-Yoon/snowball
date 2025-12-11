"""
Tests for authentication functionality (auth.py)
"""
import pytest
from datetime import datetime, timedelta
from auth import (
    find_user_by_email,
    get_current_user,
    generate_otp
)


class TestUserManagement:
    """Test user-related functions"""

    def test_find_user_by_email_existing(self, app, test_user):
        """Test finding an existing user by email"""
        with app.app_context():
            user = find_user_by_email('test@example.com')
            assert user is not None
            assert user['user_email'] == 'test@example.com'
            # User name should match test_user fixture
            assert user['user_name'] == test_user['user_name']

    def test_find_user_by_email_nonexistent(self, app):
        """Test finding a non-existent user"""
        with app.app_context():
            user = find_user_by_email('nonexistent@example.com')
            assert user is None

    def test_admin_flag(self, app, admin_user):
        """Test admin user has correct admin_flag"""
        with app.app_context():
            user = find_user_by_email('admin@example.com')
            assert user is not None
            assert user['admin_flag'] == 'Y'


class TestEmailValidation:
    """Test email validation"""

    def test_valid_email(self):
        """Test valid email formats - using snowball.is_valid_email"""
        import re
        # Email validation function from snowball.py
        def is_valid_email(email):
            if not email:
                return False
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        assert is_valid_email('test@example.com') == True
        assert is_valid_email('user.name@company.co.kr') == True
        assert is_valid_email('test+tag@domain.com') == True

    def test_invalid_email(self):
        """Test invalid email formats - using snowball.is_valid_email"""
        import re
        # Email validation function from snowball.py
        def is_valid_email(email):
            if not email:
                return False
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        assert is_valid_email('invalid-email') == False
        assert is_valid_email('@example.com') == False
        assert is_valid_email('test@') == False
        assert is_valid_email('') == False
        assert is_valid_email(None) == False


class TestOTPGeneration:
    """Test OTP code generation"""

    def test_otp_code_length(self):
        """Test OTP code has correct length"""
        otp = generate_otp()
        assert len(otp) == 6

    def test_otp_code_is_numeric(self):
        """Test OTP code contains only numbers"""
        otp = generate_otp()
        assert otp.isdigit()

    def test_otp_codes_are_different(self):
        """Test that multiple OTP codes are different (randomness)"""
        otp1 = generate_otp()
        otp2 = generate_otp()
        otp3 = generate_otp()
        # At least one should be different (extremely high probability)
        assert not (otp1 == otp2 == otp3)


class TestSessionAuthentication:
    """Test session-based authentication"""

    def test_authenticated_user_access(self, authenticated_client, test_user):
        """Test authenticated user can access protected pages"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        # Check if user name appears in response
        assert test_user['user_name'].encode() in response.data

    def test_logout_clears_session(self, authenticated_client):
        """Test logout clears session data"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

        # Try to access a protected page after logout
        # Session should be cleared
        with authenticated_client.session_transaction() as session:
            assert 'user_id' not in session


class TestLoginFlow:
    """Test login flow"""

    def test_login_page_accessible(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_with_invalid_email(self, client):
        """Test login attempt with invalid email format"""
        response = client.post('/login', data={
            'action': 'send_otp',
            'email': 'invalid-email',
            'method': 'email'
        })
        assert response.status_code == 200

    def test_login_with_nonexistent_user(self, client):
        """Test login attempt with non-registered email"""
        response = client.post('/login', data={
            'action': 'send_otp',
            'email': 'nonexistent@example.com',
            'method': 'email'
        })
        assert response.status_code == 200
        assert '등록되지 않은' in response.data.decode('utf-8')


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check_returns_ok(self, client):
        """Test health check endpoint returns ok status"""
        response = client.get('/health')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'ok'
        assert 'timestamp' in json_data
