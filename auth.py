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
    """사용자 테이블 및 로그 테이블 초기화"""
    with get_db() as conn:
        # 새로운 스키마 (enabled_flag 제거됨)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_user_new (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                user_name TEXT NOT NULL,
                user_email TEXT UNIQUE NOT NULL,
                phone_number TEXT,
                admin_flag TEXT DEFAULT 'N',
                effective_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                effective_end_date TIMESTAMP DEFAULT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login_date TIMESTAMP,
                otp_code TEXT,
                otp_expires_at TIMESTAMP,
                otp_attempts INTEGER DEFAULT 0,
                otp_method TEXT DEFAULT 'email',
                ai_review_count INTEGER DEFAULT 0,
                ai_review_limit INTEGER DEFAULT 3
            )
        ''')
        
        # 사용자 활동 로그 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_user_activity_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_email TEXT,
                user_name TEXT,
                action_type TEXT NOT NULL,
                page_name TEXT,
                url_path TEXT,
                ip_address TEXT,
                user_agent TEXT,
                access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                additional_info TEXT,
                FOREIGN KEY (user_id) REFERENCES sb_user (user_id)
            )
        ''')
        
        # RCM 마스터 테이블 생성 (기존 테이블이 있으면 유지)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_rcm (
                rcm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_name TEXT NOT NULL,
                description TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                upload_user_id INTEGER NOT NULL,
                is_active TEXT DEFAULT 'Y',
                FOREIGN KEY (upload_user_id) REFERENCES sb_user (user_id)
            )
        ''')
        
        # RCM 상세 데이터 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_rcm_detail (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                control_code TEXT NOT NULL,
                control_name TEXT NOT NULL,
                control_description TEXT,
                key_control TEXT,
                control_frequency TEXT,
                control_type TEXT,
                control_nature TEXT,
                population TEXT,
                population_completeness_check TEXT,
                population_count TEXT,
                test_procedure TEXT,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                UNIQUE(rcm_id, control_code)
            )
        ''')
        
        # 사용자-RCM 매핑 테이블 생성 (N:M 관계)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_user_rcm (
                mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rcm_id INTEGER NOT NULL,
                permission_type TEXT DEFAULT 'READ',
                granted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by INTEGER,
                is_active TEXT DEFAULT 'Y',
                FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (granted_by) REFERENCES sb_user (user_id),
                UNIQUE(user_id, rcm_id)
            )
        ''')
        
        # 설계평가 헤더 테이블 (평가 세션 정보)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_design_evaluation_header (
                header_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                evaluation_session TEXT NOT NULL,
                evaluation_status TEXT DEFAULT 'IN_PROGRESS',
                total_controls INTEGER DEFAULT 0,
                evaluated_controls INTEGER DEFAULT 0,
                progress_percentage REAL DEFAULT 0.0,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP DEFAULT NULL,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
                UNIQUE(rcm_id, user_id, evaluation_session)
            )
        ''')
        
        # 설계평가 라인 테이블 (개별 통제 평가)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_design_evaluation_line (
                line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                header_id INTEGER NOT NULL,
                control_code TEXT NOT NULL,
                control_sequence INTEGER DEFAULT 1,
                description_adequacy TEXT,
                improvement_suggestion TEXT,
                overall_effectiveness TEXT,
                evaluation_rationale TEXT,
                recommended_actions TEXT,
                evaluation_date TIMESTAMP DEFAULT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (header_id) REFERENCES sb_design_evaluation_header (header_id) ON DELETE CASCADE,
                UNIQUE(header_id, control_code)
            )
        ''')
        
        # 기존 단일 테이블을 레거시로 유지 (호환성을 위해)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_design_evaluation_legacy (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                control_code TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                description_adequacy TEXT,
                improvement_suggestion TEXT,
                overall_effectiveness TEXT,
                evaluation_rationale TEXT,
                recommended_actions TEXT,
                evaluation_date TIMESTAMP DEFAULT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                evaluation_session TEXT DEFAULT NULL,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (user_id) REFERENCES sb_user (user_id)
            )
        ''')
        
        # 기존 데이터를 레거시 테이블로 마이그레이션
        try:
            conn.execute('''
                INSERT OR IGNORE INTO sb_design_evaluation_legacy 
                SELECT * FROM sb_design_evaluation
            ''')
            conn.execute('DROP TABLE IF EXISTS sb_design_evaluation')
        except:
            pass  # 기존 테이블이 없거나 이미 마이그레이션된 경우 무시
        
        # 운영평가 진행상황 저장 테이블
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_operation_evaluation (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                control_code TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                test_method TEXT,
                sample_size INTEGER,
                exceptions_found INTEGER,
                test_results TEXT,
                conclusion TEXT,
                evaluation_notes TEXT,
                evaluation_date TIMESTAMP DEFAULT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (user_id) REFERENCES sb_user (user_id),
                UNIQUE(rcm_id, control_code, user_id)
            )
        ''')
        
        # 기존 테이블이 있는지 확인하고 데이터 마이그레이션
        existing_table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sb_user'"
        ).fetchone()
        
        if existing_table:
            # 기존 테이블의 컬럼 정보 확인
            columns = [row[1] for row in conn.execute('PRAGMA table_info(sb_user)').fetchall()]
            
            # enabled_flag가 여전히 존재하는지 확인 (마이그레이션이 필요한지 체크)
            if 'enabled_flag' in columns:
                print("기존 sb_user 테이블을 발견했습니다. 데이터 마이그레이션을 수행합니다.")
                
                # 기존 데이터를 새 테이블로 복사 (enabled_flag 제외, 없는 컬럼은 기본값 사용)
                admin_flag_col = 'admin_flag' if 'admin_flag' in columns else "'N'"
                effective_start_col = 'effective_start_date' if 'effective_start_date' in columns else 'CURRENT_TIMESTAMP'
                effective_end_col = 'effective_end_date' if 'effective_end_date' in columns else 'NULL'
                otp_method_col = 'otp_method' if 'otp_method' in columns else "'email'"
                ai_review_count_col = 'ai_review_count' if 'ai_review_count' in columns else '0'
                ai_review_limit_col = 'ai_review_limit' if 'ai_review_limit' in columns else '3'
                
                conn.execute(f'''
                    INSERT INTO sb_user_new (
                        user_id, company_name, user_name, user_email, phone_number,
                        admin_flag, effective_start_date, effective_end_date,
                        creation_date, last_login_date, otp_code, otp_expires_at,
                        otp_attempts, otp_method, ai_review_count, ai_review_limit
                    )
                    SELECT 
                        user_id, company_name, user_name, user_email, phone_number,
                        {admin_flag_col},
                        {effective_start_col},
                        {effective_end_col},
                        creation_date, last_login_date, otp_code, otp_expires_at,
                        COALESCE(otp_attempts, 0), {otp_method_col}, {ai_review_count_col}, {ai_review_limit_col}
                    FROM sb_user
                ''')
                
                # 기존 테이블 삭제하고 새 테이블 이름 변경
                conn.execute('DROP TABLE sb_user')
                conn.execute('ALTER TABLE sb_user_new RENAME TO sb_user')
                print("데이터 마이그레이션이 완료되었습니다. enabled_flag 컬럼이 제거되었습니다.")
            else:
                # 이미 마이그레이션된 테이블인 경우 임시 테이블 삭제
                conn.execute('DROP TABLE sb_user_new')
        else:
            # 기존 테이블이 없으면 새 테이블을 sb_user로 이름 변경
            conn.execute('ALTER TABLE sb_user_new RENAME TO sb_user')
            print("새로운 sb_user 테이블이 생성되었습니다.")
        
        conn.commit()

def generate_otp():
    """6자리 OTP 코드 생성"""
    return ''.join(random.choices(string.digits, k=6))

def find_user_by_email(email):
    """이메일로 사용자 찾기 (날짜 기반 활성화 체크)"""
    with get_db() as conn:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = conn.execute('''
            SELECT * FROM sb_user 
            WHERE user_email = ? 
            AND effective_start_date <= ? 
            AND (effective_end_date IS NULL OR effective_end_date >= ?)
        ''', (email, current_time, current_time)).fetchone()
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
    """OTP 코드 검증 (날짜 기반 활성화 체크)"""
    with get_db() as conn:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = conn.execute('''
            SELECT * FROM sb_user 
            WHERE user_email = ? 
            AND effective_start_date <= ? 
            AND (effective_end_date IS NULL OR effective_end_date >= ?)
        ''', (email, current_time, current_time)).fetchone()
        
        if not user:
            return False, "사용자를 찾을 수 없거나 활성화 기간이 아닙니다."
        
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

def set_user_effective_period(user_email, start_date, end_date):
    """사용자 활성화 기간 설정"""
    with get_db() as conn:
        conn.execute('''
            UPDATE sb_user 
            SET effective_start_date = ?, effective_end_date = ?
            WHERE user_email = ?
        ''', (start_date, end_date, user_email))
        conn.commit()
        print(f"사용자 {user_email}의 활성화 기간이 {start_date} ~ {end_date}로 설정되었습니다.")

def disable_user_temporarily(user_email, disable_until_date):
    """사용자 임시 비활성화 (특정 날짜까지)"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    set_user_effective_period(user_email, tomorrow, disable_until_date)

def enable_user_permanently(user_email):
    """사용자 영구 활성화 (종료일을 NULL로 설정)"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_db() as conn:
        conn.execute('''
            UPDATE sb_user 
            SET effective_start_date = ?, effective_end_date = NULL
            WHERE user_email = ?
        ''', (current_time, user_email))
        conn.commit()
        print(f"사용자 {user_email}이 영구 활성화되었습니다.")

def is_user_active(user_email):
    """사용자 활성 상태 확인"""
    user = find_user_by_email(user_email)
    return user is not None

def log_user_activity(user_info, action_type, page_name, url_path, ip_address, user_agent, additional_info=None):
    """사용자 활동 로그 기록"""
    if not user_info:
        return
    
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO sb_user_activity_log 
                (user_id, user_email, user_name, action_type, page_name, url_path, 
                 ip_address, user_agent, additional_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_info.get('user_id'),
                user_info.get('user_email'),
                user_info.get('user_name'),
                action_type,
                page_name,
                url_path,
                ip_address,
                user_agent[:500] if user_agent else None,  # User-Agent는 길 수 있으므로 제한
                additional_info
            ))
            conn.commit()
    except Exception as e:
        print(f"로그 기록 중 오류 발생: {e}")

def get_user_activity_logs(limit=100, offset=0, user_id=None):
    """사용자 활동 로그 조회"""
    with get_db() as conn:
        query = '''
            SELECT log_id, user_id, user_email, user_name, action_type, page_name, 
                   url_path, ip_address, access_time, additional_info
            FROM sb_user_activity_log
        '''
        params = []
        
        if user_id:
            query += ' WHERE user_id = ?'
            params.append(user_id)
        
        query += ' ORDER BY access_time DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        logs = conn.execute(query, params).fetchall()
        return [dict(log) for log in logs]

def get_activity_log_count(user_id=None):
    """활동 로그 총 개수 조회"""
    with get_db() as conn:
        if user_id:
            count = conn.execute('SELECT COUNT(*) FROM sb_user_activity_log WHERE user_id = ?', (user_id,)).fetchone()[0]
        else:
            count = conn.execute('SELECT COUNT(*) FROM sb_user_activity_log').fetchone()[0]
        return count

def check_ai_review_limit(user_email):
    """AI 검토 횟수 제한 확인"""
    with get_db() as conn:
        user = conn.execute(
            'SELECT ai_review_count, ai_review_limit FROM sb_user WHERE user_email = ?',
            (user_email,)
        ).fetchone()
        
        if not user:
            return False, 0, 0
        
        ai_review_count = user['ai_review_count'] or 0
        ai_review_limit = user['ai_review_limit'] or 3
        
        return ai_review_count < ai_review_limit, ai_review_count, ai_review_limit

def increment_ai_review_count(user_email):
    """AI 검토 횟수 증가"""
    with get_db() as conn:
        conn.execute(
            'UPDATE sb_user SET ai_review_count = COALESCE(ai_review_count, 0) + 1 WHERE user_email = ?',
            (user_email,)
        )
        conn.commit()
        
def get_ai_review_status(user_email):
    """AI 검토 현황 조회"""
    with get_db() as conn:
        user = conn.execute(
            'SELECT ai_review_count, ai_review_limit FROM sb_user WHERE user_email = ?',
            (user_email,)
        ).fetchone()
        
        if not user:
            return 0, 3
        
        return user['ai_review_count'] or 0, user['ai_review_limit'] or 3

# RCM 관리 함수들

def create_rcm(rcm_name, description, upload_user_id):
    """RCM 생성"""
    with get_db() as conn:
        cursor = conn.execute('''
            INSERT INTO sb_rcm (rcm_name, description, upload_user_id)
            VALUES (?, ?, ?)
        ''', (rcm_name, description, upload_user_id))
        conn.commit()
        return cursor.lastrowid

def get_user_rcms(user_id):
    """사용자가 접근 가능한 RCM 목록 조회"""
    with get_db() as conn:
        rcms = conn.execute('''
            SELECT r.rcm_id, r.rcm_name, r.description, r.upload_date, 
                   ur.permission_type, u.company_name
            FROM sb_rcm r
            INNER JOIN sb_user_rcm ur ON r.rcm_id = ur.rcm_id
            INNER JOIN sb_user u ON r.upload_user_id = u.user_id
            WHERE ur.user_id = ? AND ur.is_active = 'Y' AND r.is_active = 'Y'
            ORDER BY r.upload_date DESC
        ''', (user_id,)).fetchall()
        return [dict(rcm) for rcm in rcms]

def get_rcm_details(rcm_id):
    """RCM 상세 데이터 조회"""
    with get_db() as conn:
        details = conn.execute('''
            SELECT * FROM sb_rcm_detail
            WHERE rcm_id = ?
            ORDER BY control_code
        ''', (rcm_id,)).fetchall()
        return [dict(detail) for detail in details]

def save_rcm_details(rcm_id, rcm_data):
    """RCM 상세 데이터 저장 (추가 방식)"""
    with get_db() as conn:
        # 새 데이터 삽입 (기존 데이터 삭제하지 않음)
        for data in rcm_data:
            conn.execute('''
                INSERT OR REPLACE INTO sb_rcm_detail (
                    rcm_id, control_code, control_name, control_description,
                    key_control, control_frequency, control_type, control_nature,
                    population, population_completeness_check, population_count, test_procedure
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rcm_id,
                data.get('control_code', ''),
                data.get('control_name', ''),
                data.get('control_description', ''),
                data.get('key_control', ''),
                data.get('control_frequency', ''),
                data.get('control_type', ''),
                data.get('control_nature', ''),
                data.get('population', ''),
                data.get('population_completeness_check', ''),
                data.get('population_count', ''),
                data.get('test_procedure', '')
            ))
        conn.commit()

def grant_rcm_access(user_id, rcm_id, permission_type, granted_by):
    """사용자에게 RCM 접근 권한 부여"""
    with get_db() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO sb_user_rcm (user_id, rcm_id, permission_type, granted_by)
            VALUES (?, ?, ?, ?)
        ''', (user_id, rcm_id, permission_type, granted_by))
        conn.commit()

def get_all_rcms():
    """모든 RCM 조회 (관리자용)"""
    with get_db() as conn:
        rcms = conn.execute('''
            SELECT r.*, u.user_name as upload_user_name, u.company_name
            FROM sb_rcm r
            LEFT JOIN sb_user u ON r.upload_user_id = u.user_id
            WHERE r.is_active = 'Y'
            ORDER BY r.upload_date DESC
        ''').fetchall()
        return [dict(rcm) for rcm in rcms]

def save_design_evaluation(rcm_id, control_code, user_id, evaluation_data, evaluation_session=None):
    """설계평가 결과 저장 (Header-Line 구조)"""
    with get_db() as conn:
        # 1. Header 존재 확인 및 생성
        header_id = get_or_create_evaluation_header(conn, rcm_id, user_id, evaluation_session)
        
        # 2. Line 데이터 저장/업데이트
        # 기존 레코드만 업데이트 (평가 저장은 이미 생성된 레코드에만 수행)
        cursor = conn.execute('''
            UPDATE sb_design_evaluation_line SET
                description_adequacy = ?, improvement_suggestion = ?,
                overall_effectiveness = ?, evaluation_rationale = ?,
                recommended_actions = ?, evaluation_date = CURRENT_TIMESTAMP,
                last_updated = CURRENT_TIMESTAMP
            WHERE header_id = ? AND control_code = ?
        ''', (
            evaluation_data.get('adequacy'),
            evaluation_data.get('improvement'),
            evaluation_data.get('effectiveness'),
            evaluation_data.get('rationale'),
            evaluation_data.get('actions'),
            header_id, control_code
        ))
        
        # 업데이트된 레코드가 없으면 오류
        if cursor.rowcount == 0:
            raise ValueError(f"평가할 통제({control_code})를 찾을 수 없습니다. 먼저 평가 구조를 생성해주세요.")
        
        # 3. Header 진행률 업데이트
        update_evaluation_progress(conn, header_id)
        
        conn.commit()

def create_evaluation_structure(rcm_id, user_id, evaluation_session):
    """평가 시작 시 완전한 Header-Line 구조 생성"""
    if not evaluation_session or evaluation_session.strip() == '':
        raise ValueError("평가 세션명이 필요합니다.")
    
    with get_db() as conn:
        # 1. RCM 상세 정보 조회
        rcm_details = get_rcm_details(rcm_id)
        if not rcm_details:
            raise ValueError(f"RCM ID {rcm_id}에 대한 상세 정보를 찾을 수 없습니다.")
        
        total_controls = len(rcm_details)
        
        # 2. 헤더 생성
        cursor = conn.execute('''
            INSERT INTO sb_design_evaluation_header (
                rcm_id, user_id, evaluation_session, total_controls,
                evaluated_controls, progress_percentage, evaluation_status
            ) VALUES (?, ?, ?, ?, 0, 0.0, 'IN_PROGRESS')
        ''', (rcm_id, user_id, evaluation_session, total_controls))
        
        header_id = cursor.lastrowid
        
        # 3. 모든 통제에 대한 빈 라인 생성
        for idx, control in enumerate(rcm_details, 1):
            conn.execute('''
                INSERT INTO sb_design_evaluation_line (
                    header_id, control_code, control_sequence,
                    description_adequacy, improvement_suggestion, 
                    overall_effectiveness, evaluation_rationale, recommended_actions
                ) VALUES (?, ?, ?, '', '', '', '', '')
            ''', (header_id, control['control_code'], idx))
        
        conn.commit()
        return header_id

def get_or_create_evaluation_header(conn, rcm_id, user_id, evaluation_session):
    """평가 헤더 조회 또는 생성 (레거시 호환용)"""
    if not evaluation_session:
        raise ValueError("평가 세션명이 필요합니다.")
    
    # 기존 헤더 확인
    header = conn.execute('''
        SELECT header_id FROM sb_design_evaluation_header
        WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
    ''', (rcm_id, user_id, evaluation_session)).fetchone()
    
    if header:
        return header['header_id']
    
    # 새 구조로 생성
    return create_evaluation_structure(rcm_id, user_id, evaluation_session)

def update_evaluation_progress(conn, header_id):
    """평가 진행률 업데이트"""
    # 완료된 평가 수 계산 (evaluation_date 기준)
    result = conn.execute('''
        SELECT COUNT(*) as evaluated_count
        FROM sb_design_evaluation_line
        WHERE header_id = ? AND evaluation_date IS NOT NULL
    ''', (header_id,)).fetchone()
    
    evaluated_count = result['evaluated_count']
    
    # 헤더 정보 조회
    header = conn.execute('''
        SELECT total_controls FROM sb_design_evaluation_header
        WHERE header_id = ?
    ''', (header_id,)).fetchone()
    
    total_controls = header['total_controls']
    progress = (evaluated_count / total_controls * 100) if total_controls > 0 else 0
    status = 'COMPLETED' if progress >= 100 else 'IN_PROGRESS'
    
    # 헤더 업데이트
    conn.execute('''
        UPDATE sb_design_evaluation_header
        SET evaluated_controls = ?, 
            progress_percentage = ?,
            evaluation_status = ?,
            last_updated = CURRENT_TIMESTAMP,
            completed_date = CASE WHEN ? = 'COMPLETED' THEN CURRENT_TIMESTAMP ELSE completed_date END
        WHERE header_id = ?
    ''', (evaluated_count, progress, status, status, header_id))

def get_design_evaluations(rcm_id, user_id, evaluation_session=None):
    """특정 RCM의 사용자별 설계평가 결과 조회 (Header-Line 구조)"""
    print(f"get_design_evaluations called: rcm_id={rcm_id}, user_id={user_id}, evaluation_session='{evaluation_session}'")
    
    try:
        with get_db() as conn:
            if evaluation_session:
                # 특정 평가 세션의 결과 조회
                evaluations = conn.execute('''
                SELECT l.*, h.evaluation_session, h.start_date, h.evaluation_status
                FROM sb_design_evaluation_line l
                JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
                WHERE h.rcm_id = ? AND h.user_id = ? AND h.evaluation_session = ?
                ORDER BY l.control_sequence, l.control_code
                ''', (rcm_id, user_id, evaluation_session)).fetchall()
            else:
                # 가장 최근 세션의 결과 조회
                evaluations = conn.execute('''
                    SELECT l.*, h.evaluation_session, h.start_date, h.evaluation_status
                    FROM sb_design_evaluation_line l
                    JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
                    WHERE h.rcm_id = ? AND h.user_id = ?
                          AND h.header_id = (
                              SELECT header_id FROM sb_design_evaluation_header
                              WHERE rcm_id = ? AND user_id = ?
                              ORDER BY start_date DESC LIMIT 1
                          )
                    ORDER BY l.control_sequence, l.control_code
                ''', (rcm_id, user_id, rcm_id, user_id)).fetchall()
            
        print(f"Found {len(evaluations)} evaluation records")
        if evaluations:
            print(f"Sample evaluation columns: {list(evaluations[0].keys())}")
        
        return [dict(eval) for eval in evaluations]
    
    except Exception as e:
        print(f"Error in get_design_evaluations: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return []

def get_user_evaluation_sessions(rcm_id, user_id):
    """사용자의 설계평가 세션 목록 조회 (Header-Line 구조)"""
    with get_db() as conn:
        sessions = conn.execute('''
            SELECT h.evaluation_session, h.start_date, h.last_updated,
                   h.evaluated_controls, h.total_controls, h.progress_percentage,
                   h.evaluation_status, h.completed_date
            FROM sb_design_evaluation_header h
            WHERE h.rcm_id = ? AND h.user_id = ?
            ORDER BY h.start_date DESC
        ''', (rcm_id, user_id)).fetchall()
        return [dict(session) for session in sessions]

def delete_evaluation_session(rcm_id, user_id, evaluation_session):
    """특정 평가 세션 삭제 (Header-Line 구조)"""
    with get_db() as conn:
        # 헤더 조회
        header = conn.execute('''
            SELECT header_id FROM sb_design_evaluation_header
            WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
        ''', (rcm_id, user_id, evaluation_session)).fetchone()
        
        if not header:
            return 0
        
        header_id = header['header_id']
        
        # 1. 먼저 line 레코드들 삭제
        conn.execute('''
            DELETE FROM sb_design_evaluation_line 
            WHERE header_id = ?
        ''', (header_id,))
        
        # 2. header 레코드 삭제
        cursor = conn.execute('''
            DELETE FROM sb_design_evaluation_header 
            WHERE header_id = ?
        ''', (header_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count

# 임시로 비활성화 - 테이블 구조 문제로 인해 
# def get_design_evaluation_versions(rcm_id, control_code, company_name):
#     """특정 통제의 모든 설계평가 버전 조회"""
#     pass

def save_operation_evaluation(rcm_id, control_code, user_id, evaluation_data):
    """운영평가 결과 저장"""
    with get_db() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO sb_operation_evaluation (
                rcm_id, control_code, user_id, test_method, 
                sample_size, exceptions_found, test_results, 
                conclusion, evaluation_notes, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            rcm_id, control_code, user_id,
            evaluation_data.get('method'),
            evaluation_data.get('sample_size'),
            evaluation_data.get('exceptions'),
            evaluation_data.get('results'),
            evaluation_data.get('conclusion'),
            evaluation_data.get('notes')
        ))
        conn.commit()

def get_operation_evaluations(rcm_id, user_id):
    """특정 RCM의 사용자별 운영평가 결과 조회"""
    with get_db() as conn:
        evaluations = conn.execute('''
            SELECT * FROM sb_operation_evaluation
            WHERE rcm_id = ? AND user_id = ?
            ORDER BY control_code
        ''', (rcm_id, user_id)).fetchall()
        return [dict(eval) for eval in evaluations]