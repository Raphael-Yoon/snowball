"""
pytest configuration and shared fixtures
"""
import pytest
import os
import sys
import tempfile
from datetime import datetime

# Add parent directory to path to import snowball modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snowball import app as flask_app
from auth import get_db


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    # Set test configuration
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key',
        'SESSION_COOKIE_SECURE': False,
        'WTF_CSRF_ENABLED': False,
    })

    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    flask_app.config['DATABASE'] = db_path

    # Initialize test database
    with flask_app.app_context():
        try:
            from migrate import upgrade_database
            upgrade_database(db_path)
        except Exception as e:
            print(f"Database initialization warning: {e}")
            # If migration fails, create basic tables manually
            _create_basic_test_tables(db_path)

    yield flask_app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


def _create_basic_test_tables(db_path):
    """Create basic test tables if migration fails"""
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create essential tables for testing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sb_user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT UNIQUE NOT NULL,
            user_name TEXT NOT NULL,
            company_name TEXT,
            phone_number TEXT,
            admin_flag TEXT DEFAULT 'N',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login_date TIMESTAMP,
            effective_end_date TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sb_otp (
            otp_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_used INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sb_user_activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            activity_description TEXT,
            page_url TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        with get_db() as conn:
            # Check if user already exists
            existing = conn.execute(
                'SELECT * FROM sb_user WHERE user_email = %s',
                ('test@example.com',)
            ).fetchone()

            if existing:
                # Return existing user
                return dict(existing)

            # Create new user
            cursor = conn.execute('''
                INSERT INTO sb_user (user_email, user_name, company_name, phone_number, admin_flag)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('test@example.com', 'Test User', 'Test Company', '010-1234-5678', 'N'))
            user_id = cursor.lastrowid
            conn.commit()

            # Return user info dictionary
            return {
                'user_id': user_id,
                'user_email': 'test@example.com',
                'user_name': 'Test User',
                'company_name': 'Test Company',
                'phone_number': '010-1234-5678',
                'admin_flag': 'N'
            }


@pytest.fixture
def admin_user(app):
    """Create an admin user in the database."""
    with app.app_context():
        with get_db() as conn:
            # Check if user already exists
            existing = conn.execute(
                'SELECT * FROM sb_user WHERE user_email = %s',
                ('admin@example.com',)
            ).fetchone()

            if existing:
                # Return existing user
                return dict(existing)

            # Create new user
            cursor = conn.execute('''
                INSERT INTO sb_user (user_email, user_name, company_name, phone_number, admin_flag)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin@example.com', 'Admin User', 'Admin Company', '010-9999-9999', 'Y'))
            user_id = cursor.lastrowid
            conn.commit()

            return {
                'user_id': user_id,
                'user_email': 'admin@example.com',
                'user_name': 'Admin User',
                'company_name': 'Admin Company',
                'phone_number': '010-9999-9999',
                'admin_flag': 'Y'
            }


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client with a logged-in user."""
    with client.session_transaction() as session:
        session['user_id'] = test_user['user_id']
        session['user_email'] = test_user['user_email']
        session['user_info'] = test_user
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = datetime.now().isoformat()

    return client


@pytest.fixture
def mock_gmail_send(mocker):
    """Mock Gmail sending functionality."""
    mock = mocker.patch('snowball_mail.send_gmail')
    mock.return_value = True
    return mock


@pytest.fixture
def mock_gmail_send_with_attachment(mocker):
    """Mock Gmail sending with attachment functionality."""
    mock = mocker.patch('snowball_mail.send_gmail_with_attachment')
    mock.return_value = True
    return mock


@pytest.fixture(autouse=True)
def disable_email_sending(mocker):
    """
    자동으로 모든 테스트에서 실제 이메일 전송을 차단합니다.
    테스트 시 실제 메일이 발송되지 않도록 합니다.
    """
    # snowball_mail의 모든 이메일 전송 함수를 Mock으로 대체
    mocker.patch('snowball_mail.send_gmail', return_value=True)
    mocker.patch('snowball_mail.send_gmail_with_attachment', return_value=None)

    # 혹시 다른 모듈에서 직접 import하는 경우도 대비
    try:
        mocker.patch('snowball_link1.send_gmail_with_attachment', return_value=None)
    except:
        pass

    try:
        mocker.patch('snowball_link2.send_gmail_with_attachment', return_value=None)
    except:
        pass
