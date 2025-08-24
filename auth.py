import sqlite3
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request, flash

DATABASE = 'snowball.db'

def get_db():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """사용자 테이블 초기화"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_user (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                user_name TEXT NOT NULL,
                user_email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                enabled_flag INTEGER DEFAULT 1,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login_date TIMESTAMP,
                otp_code TEXT,
                otp_expires_at TIMESTAMP,
                otp_attempts INTEGER DEFAULT 0,
                otp_method TEXT DEFAULT 'email'
            )
        ''')
        conn.commit()

def generate_otp():
    """6자리 OTP 코드 생성"""
    return ''.join(random.choices(string.digits, k=6))

def find_user_by_email(email):
    """이메일로 사용자 찾기"""
    with get_db() as conn:
        user = conn.execute(
            'SELECT * FROM sb_user WHERE user_email = ? AND enabled_flag = "Y"', 
            (email,)
        ).fetchone()
        return dict(user) if user else None

def send_otp(user_email, method='email'):
    """OTP 발송 및 DB 저장"""
    user = find_user_by_email(user_email)
    if not user:
        return False, "등록되지 않은 사용자입니다."
    
    # OTP 코드 생성
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)  # 5분 후 만료
    
    # DB에 OTP 저장
    with get_db() as conn:
        conn.execute('''
            UPDATE sb_user 
            SET otp_code = ?, otp_expires_at = ?, otp_attempts = 0, otp_method = ?
            WHERE user_email = ?
        ''', (otp_code, expires_at, method, user_email))
        conn.commit()
    
    # OTP 발송 (이메일 또는 SMS)
    if method == 'email':
        return send_otp_email(user_email, otp_code, user['user_name'])
    elif method == 'sms':
        return send_otp_sms(user['phone_number'], otp_code)
    
    return False, "지원하지 않는 발송 방법입니다."

def send_otp_email(email, otp_code, user_name):
    """이메일로 OTP 발송"""
    try:
        from snowball_mail import send_gmail
        subject = "[SnowBall] 로그인 인증 코드"
        body = f"""
안녕하세요 {user_name}님,

로그인 인증 코드입니다:

인증 코드: {otp_code}

이 코드는 5분간 유효합니다.
본인이 요청하지 않았다면 이 메일을 무시하세요.

SnowBall 시스템
        """
        send_gmail(email, subject, body)
        return True, "인증 코드가 이메일로 전송되었습니다."
    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return False, "이메일 발송에 실패했습니다."

def send_otp_sms(phone_number, otp_code):
    """SMS로 OTP 발송 (테스트 모드)"""
    # 테스트 모드: 콘솔과 로그 파일에 OTP 코드 저장
    print(f"[SMS 테스트] {phone_number}로 인증코드 {otp_code} 발송")
    
    # 테스트용: OTP 코드를 파일에 저장 (실제 운영에서는 제거 필요)
    try:
        with open('sms_test_log.txt', 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f"{datetime.now()}: {phone_number} -> {otp_code}\n")
    except:
        pass
    
    return True, f"인증 코드가 {phone_number}로 발송되었습니다. (테스트 모드: 콘솔 확인)"

def verify_otp(email, otp_code):
    """OTP 코드 검증"""
    with get_db() as conn:
        user = conn.execute('''
            SELECT * FROM sb_user 
            WHERE user_email = ? AND enabled_flag = "Y"
        ''', (email,)).fetchone()
        
        if not user:
            return False, "사용자를 찾을 수 없습니다."
        
        # OTP 만료 확인
        if not user['otp_expires_at'] or datetime.now() > datetime.fromisoformat(user['otp_expires_at']):
            return False, "인증 코드가 만료되었습니다."
        
        # 시도 횟수 확인
        if user['otp_attempts'] >= 3:
            return False, "인증 시도 횟수를 초과했습니다. 새로운 코드를 요청하세요."
        
        # OTP 코드 확인
        if user['otp_code'] == otp_code:
            # 로그인 성공 - OTP 정보 클리어 및 로그인 시간 업데이트
            conn.execute('''
                UPDATE sb_user 
                SET otp_code = NULL, otp_expires_at = NULL, otp_attempts = 0,
                    last_login_date = CURRENT_TIMESTAMP
                WHERE user_email = ?
            ''', (email,))
            conn.commit()
            return True, dict(user)
        else:
            # OTP 틀림 - 시도 횟수 증가
            conn.execute('''
                UPDATE sb_user 
                SET otp_attempts = otp_attempts + 1
                WHERE user_email = ?
            ''', (email,))
            conn.commit()
            remaining = 3 - (user['otp_attempts'] + 1)
            return False, f"인증 코드가 틀렸습니다. (남은 시도: {remaining}회)"

def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """현재 로그인한 사용자 정보"""
    if 'user_id' not in session:
        return None
    
    with get_db() as conn:
        user = conn.execute(
            'SELECT * FROM sb_user WHERE user_id = ?', (session['user_id'],)
        ).fetchone()
        return dict(user) if user else None