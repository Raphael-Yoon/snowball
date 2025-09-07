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
        
        # RCM 마스터 테이블 생성 (헤더 정보만 관리)
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
        
        # RCM 상세 데이터 테이블 생성 (매핑 및 AI 검토 정보 포함)
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
                -- 매핑 관련 컬럼들
                mapped_std_control_id INTEGER,  -- 매핑된 기준통제 ID
                mapped_date TIMESTAMP,
                mapped_by INTEGER,
                -- AI 검토 관련 컬럼들
                ai_review_status TEXT DEFAULT 'not_reviewed',  -- 'not_reviewed', 'in_progress', 'completed'
                ai_review_recommendation TEXT,  -- AI 개선권고사항
                ai_reviewed_date TIMESTAMP,
                ai_reviewed_by INTEGER,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (mapped_std_control_id) REFERENCES sb_standard_control (std_control_id),
                FOREIGN KEY (mapped_by) REFERENCES sb_user (user_id),
                FOREIGN KEY (ai_reviewed_by) REFERENCES sb_user (user_id),
                UNIQUE(rcm_id, control_code)
            )
        ''')
        
        # 기존 sb_rcm_detail 테이블에 새 컬럼들 추가
        try:
            detail_columns = [
                ('mapped_std_control_id', 'INTEGER'),
                ('mapped_date', 'TIMESTAMP'),
                ('mapped_by', 'INTEGER'),
                ('ai_review_status', 'TEXT DEFAULT \'not_reviewed\''),
                ('ai_review_recommendation', 'TEXT'),
                ('ai_reviewed_date', 'TIMESTAMP'),
                ('ai_reviewed_by', 'INTEGER')
            ]
            
            for col_name, col_type in detail_columns:
                try:
                    conn.execute(f'ALTER TABLE sb_rcm_detail ADD COLUMN {col_name} {col_type}')
                    print(f"sb_rcm_detail 테이블에 {col_name} 컬럼을 추가했습니다.")
                except:
                    # 컬럼이 이미 존재하는 경우 무시
                    pass
                    
        except Exception as e:
            print(f"sb_rcm_detail 컬럼 추가 중 오류 (무시됨): {e}")
            pass
        
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
        
        # 기준통제 마스터 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_standard_control (
                std_control_id INTEGER PRIMARY KEY AUTOINCREMENT,
                control_category TEXT NOT NULL,
                control_code TEXT NOT NULL,
                control_name TEXT NOT NULL,
                control_description TEXT,
                ai_review_prompt TEXT,  -- AI 검토시 사용할 프롬프트
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(control_category, control_code)
            )
        ''')
        
        # RCM과 기준통제 매핑 테이블 생성
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_rcm_standard_mapping (
                mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                control_code TEXT NOT NULL,
                std_control_id INTEGER NOT NULL,
                mapping_confidence REAL DEFAULT 0.0,  -- 매핑 신뢰도 (0.0 ~ 1.0)
                mapping_type TEXT DEFAULT 'auto',  -- 'auto', 'manual', 'ai'
                mapped_by INTEGER,
                mapping_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active TEXT DEFAULT 'Y',
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (std_control_id) REFERENCES sb_standard_control (std_control_id),
                FOREIGN KEY (mapped_by) REFERENCES sb_user (user_id),
                UNIQUE(rcm_id, control_code, std_control_id)
            )
        ''')
        
        
        # RCM 완성도 평가 결과 테이블 생성 (히스토리 관리)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sb_rcm_completeness_eval (
                eval_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rcm_id INTEGER NOT NULL,
                eval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completeness_score REAL DEFAULT 0.0,  -- 완성도 점수 (0.0 ~ 100.0)
                eval_details TEXT,  -- JSON 형태로 상세 평가 결과 저장
                eval_by INTEGER,
                FOREIGN KEY (rcm_id) REFERENCES sb_rcm (rcm_id),
                FOREIGN KEY (eval_by) REFERENCES sb_user (user_id)
            )
        ''')
        
        # 사용하지 않는 테이블 및 컬럼 정리
        try:
            # 기존 review 관련 테이블들 제거
            conn.execute('DROP TABLE IF EXISTS sb_rcm_review_result')
            conn.execute('DROP TABLE IF EXISTS sb_rcm_review')
            print("사용하지 않는 review 관련 테이블들을 제거했습니다.")
            
            # sb_rcm 테이블에서 review 관련 컬럼들 제거 (SQLite는 DROP COLUMN을 지원하지 않으므로 테이블 재생성)
            # 기존 데이터가 있는지 확인
            has_review_columns = conn.execute(
                "SELECT COUNT(*) FROM pragma_table_info('sb_rcm') WHERE name LIKE 'review_%'"
            ).fetchone()[0]
            
            if has_review_columns > 0:
                print("sb_rcm 테이블에서 review 관련 컬럼들을 제거합니다...")
                
                # 임시 테이블 생성
                conn.execute('''
                    CREATE TABLE sb_rcm_temp (
                        rcm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rcm_name TEXT NOT NULL,
                        description TEXT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        upload_user_id INTEGER NOT NULL,
                        is_active TEXT DEFAULT 'Y',
                        FOREIGN KEY (upload_user_id) REFERENCES sb_user (user_id)
                    )
                ''')
                
                # 기본 데이터만 복사
                conn.execute('''
                    INSERT INTO sb_rcm_temp (rcm_id, rcm_name, description, upload_date, upload_user_id, is_active)
                    SELECT rcm_id, rcm_name, description, upload_date, upload_user_id, is_active
                    FROM sb_rcm
                ''')
                
                # 기존 테이블 삭제 후 새 테이블로 이름 변경
                conn.execute('DROP TABLE sb_rcm')
                conn.execute('ALTER TABLE sb_rcm_temp RENAME TO sb_rcm')
                
                print("sb_rcm 테이블에서 review 관련 컬럼들이 제거되었습니다.")
            
            # sb_rcm_detail 테이블에서 불필요한 컬럼들 제거
            has_unnecessary_columns = conn.execute(
                "SELECT COUNT(*) FROM pragma_table_info('sb_rcm_detail') WHERE name IN ('mapping_confidence', 'mapping_type', 'ai_review_score')"
            ).fetchone()[0]
            
            if has_unnecessary_columns > 0:
                print("sb_rcm_detail 테이블에서 불필요한 컬럼들을 제거합니다...")
                
                # 기존 컬럼 목록 조회
                columns_info = conn.execute("PRAGMA table_info('sb_rcm_detail')").fetchall()
                
                # 제거할 컬럼을 제외한 컬럼들만 선택
                keep_columns = [col[1] for col in columns_info if col[1] not in ('mapping_confidence', 'mapping_type', 'ai_review_score')]
                columns_str = ', '.join(keep_columns)
                
                # 임시 테이블 생성 (필요한 컬럼만)
                conn.execute(f'''
                    CREATE TABLE sb_rcm_detail_temp AS 
                    SELECT {columns_str} FROM sb_rcm_detail
                ''')
                
                # 기존 테이블 삭제 후 새 테이블로 이름 변경
                conn.execute('DROP TABLE sb_rcm_detail')
                conn.execute('ALTER TABLE sb_rcm_detail_temp RENAME TO sb_rcm_detail')
                
                print("sb_rcm_detail 테이블에서 불필요한 컬럼들이 제거되었습니다.")
                
        except Exception as e:
            print(f"테이블/컬럼 정리 중 오류 (무시됨): {e}")
            pass
        
        # 기준통제 테이블에 ai_review_prompt 컬럼 추가 (기존 테이블에 없는 경우)
        try:
            conn.execute('ALTER TABLE sb_standard_control ADD COLUMN ai_review_prompt TEXT')
            print("sb_standard_control 테이블에 ai_review_prompt 컬럼을 추가했습니다.")
        except:
            # 컬럼이 이미 존재하거나 테이블이 없는 경우 무시
            pass
        
        # 불필요한 컬럼들 삭제 (SQLite는 DROP COLUMN을 지원하지 않으므로 테이블 재생성)
        try:
            # 기존 데이터 백업
            conn.execute('''
                CREATE TABLE sb_standard_control_new (
                    std_control_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    control_category TEXT NOT NULL,
                    control_code TEXT NOT NULL,
                    control_name TEXT NOT NULL,
                    control_description TEXT,
                    ai_review_prompt TEXT,
                    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(control_category, control_code)
                )
            ''')
            
            # 데이터 복사 (필요한 컬럼만)
            conn.execute('''
                INSERT INTO sb_standard_control_new 
                (std_control_id, control_category, control_code, control_name, control_description, ai_review_prompt, creation_date)
                SELECT std_control_id, control_category, control_code, control_name, control_description, ai_review_prompt, creation_date
                FROM sb_standard_control
            ''')
            
            # 기존 테이블 삭제 후 새 테이블로 이름 변경
            conn.execute('DROP TABLE sb_standard_control')
            conn.execute('ALTER TABLE sb_standard_control_new RENAME TO sb_standard_control')
            
            print("sb_standard_control 테이블에서 불필요한 컬럼들을 삭제했습니다.")
        except Exception as e:
            # 테이블 재구성 실패 시 무시 (이미 올바른 구조일 수 있음)
            print(f"테이블 재구성 중 오류 (무시됨): {e}")
            pass
        
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
        # additional_info가 딕셔너리인 경우 JSON 문자열로 변환
        if additional_info and isinstance(additional_info, dict):
            import json
            additional_info = json.dumps(additional_info, ensure_ascii=False)
        elif additional_info and not isinstance(additional_info, str):
            # 딕셔너리가 아닌 다른 타입은 문자열로 변환
            additional_info = str(additional_info)
            
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
                # 특정 평가 세션의 가장 최신 결과 조회
                query = '''
                SELECT l.*, h.evaluation_session, h.start_date, h.evaluation_status
                FROM sb_design_evaluation_line l
                JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
                WHERE h.rcm_id = ? AND h.user_id = ? AND h.evaluation_session = ?
                      AND h.header_id = (
                          SELECT header_id FROM sb_design_evaluation_header
                          WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
                          ORDER BY start_date DESC LIMIT 1
                      )
                ORDER BY l.control_sequence, l.control_code
                '''
                params = (rcm_id, user_id, evaluation_session, rcm_id, user_id, evaluation_session)
                print(f"Executing query with session: {query}")
                print(f"Parameters: rcm_id={rcm_id}, user_id={user_id}, evaluation_session='{evaluation_session}'")
                final_query = query.replace('?', '{}').format(rcm_id, user_id, f"'{evaluation_session}'", rcm_id, user_id, f"'{evaluation_session}'")
                print(f"***** FINAL QUERY WITH PARAMS: {final_query} *****")
                evaluations = conn.execute(query, params).fetchall()
            else:
                # 가장 최근 세션의 결과 조회
                query = '''
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
                '''
                params = (rcm_id, user_id, rcm_id, user_id)
                print(f"Executing query without session: {query}")
                print(f"Parameters: rcm_id={rcm_id}, user_id={user_id}")
                final_query = query.replace('?', '{}').format(rcm_id, user_id, rcm_id, user_id)
                print(f"***** FINAL QUERY WITH PARAMS: {final_query} *****")
                evaluations = conn.execute(query, params).fetchall()
            
        print(f"Found {len(evaluations)} evaluation records")
        if evaluations:
            print(f"Sample evaluation columns: {list(evaluations[0].keys())}")
            # 각 레코드의 evaluation_date 값 출력
            for i, eval_record in enumerate(evaluations):
                eval_dict = dict(eval_record)
                print(f"Record {i+1}: header_id={eval_dict.get('header_id')}, line_id={eval_dict.get('line_id')}, control_code={eval_dict.get('control_code')}, evaluation_date={eval_dict.get('evaluation_date')} (type: {type(eval_dict.get('evaluation_date'))})")
                if i >= 2:  # 처음 3개만 출력
                    print("... (showing first 3 records only)")
                    break
        
        return [dict(eval) for eval in evaluations]
    
    except Exception as e:
        print(f"Error in get_design_evaluations: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return []

def get_design_evaluations_by_header_id(rcm_id, user_id, header_id):
    """특정 header_id의 설계평가 결과 조회"""
    print(f"get_design_evaluations_by_header_id called: rcm_id={rcm_id}, user_id={user_id}, header_id={header_id}")
    
    try:
        with get_db() as conn:
            # 특정 header_id의 결과 조회 - 간단하게 header_id로만 필터링
            query = '''
            SELECT l.*, h.evaluation_session, h.start_date, h.evaluation_status
            FROM sb_design_evaluation_line l
            JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
            WHERE l.header_id = ?
            ORDER BY l.control_sequence, l.control_code
            '''
            params = (header_id,)
            
            # 실행할 쿼리를 콘솔에 출력
            final_query = f"""
            SELECT l.*, h.evaluation_session, h.start_date, h.evaluation_status
            FROM sb_design_evaluation_line l
            JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
            WHERE l.header_id = {header_id}
            ORDER BY l.control_sequence, l.control_code
            """
            
            print("="*80)
            print("📋 EXECUTING SQL QUERY:")
            print("="*80)
            print(final_query.strip())
            print("="*80)
            evaluations = conn.execute(query, params).fetchall()
            
        print(f"Found {len(evaluations)} evaluation records for header_id={header_id}")
        print(f"***** QUERY EXECUTED: header_id filter applied *****")
        if evaluations:
            print(f"Sample evaluation columns: {list(evaluations[0].keys())}")
            # 각 레코드의 evaluation_date 값 출력
            for i, eval_record in enumerate(evaluations):
                eval_dict = dict(eval_record)
                print(f"Record {i+1}: header_id={eval_dict.get('header_id')}, line_id={eval_dict.get('line_id')}, control_code={eval_dict.get('control_code')}, evaluation_date={eval_dict.get('evaluation_date')} (type: {type(eval_dict.get('evaluation_date'))})")
                if i >= 2:  # 처음 3개만 출력
                    print("... (showing first 3 records only)")
                    break
        
        return [dict(eval) for eval in evaluations]
    
    except Exception as e:
        print(f"Error in get_design_evaluations_by_header_id: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return []

def get_user_evaluation_sessions(rcm_id, user_id):
    """사용자의 설계평가 세션 목록 조회 (Header-Line 구조)"""
    with get_db() as conn:
        sessions = conn.execute('''
            SELECT h.header_id, h.evaluation_session, h.start_date, h.last_updated,
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

def count_design_evaluations(rcm_id, user_id):
    """특정 RCM의 사용자별 설계평가 헤더 개수 조회 (평가 세션 개수)"""
    with get_db() as conn:
        count = conn.execute('''
            SELECT COUNT(*) FROM sb_design_evaluation_header
            WHERE rcm_id = ? AND user_id = ?
        ''', (rcm_id, user_id)).fetchone()[0]
        return count

def count_operation_evaluations(rcm_id, user_id):
    """특정 RCM의 사용자별 운영평가 완료된 통제 수량 조회 (효율적)"""
    with get_db() as conn:
        count = conn.execute('''
            SELECT COUNT(*) FROM sb_operation_evaluation
            WHERE rcm_id = ? AND user_id = ?
        ''', (rcm_id, user_id)).fetchone()[0]
        return count

# 기준통제 관련 함수들

def initialize_standard_controls():
    """기준통제 초기 데이터 삽입 (빈 함수 - 수동으로 데이터 삽입 예정)"""
    print("기준통제 데이터는 수동으로 삽입해주세요.")

def get_standard_controls():
    """기준통제 목록 조회"""
    with get_db() as conn:
        controls = conn.execute('''
            SELECT * FROM sb_standard_control 
            ORDER BY control_category, control_code
        ''').fetchall()
        return [dict(control) for control in controls]

def save_rcm_standard_mapping(rcm_id, control_code, std_control_id, confidence, mapping_type, mapped_by):
    """RCM과 기준통제 매핑 저장"""
    with get_db() as conn:
        conn.execute('''
            INSERT OR REPLACE INTO sb_rcm_standard_mapping
            (rcm_id, control_code, std_control_id, mapping_confidence, mapping_type, mapped_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (rcm_id, control_code, std_control_id, confidence, mapping_type, mapped_by))
        conn.commit()

def get_rcm_standard_mappings(rcm_id):
    """RCM의 기준통제 매핑 조회"""
    with get_db() as conn:
        mappings = conn.execute('''
            SELECT m.*, sc.control_name as std_control_name, sc.control_category
            FROM sb_rcm_standard_mapping m
            JOIN sb_standard_control sc ON m.std_control_id = sc.std_control_id
            WHERE m.rcm_id = ? AND m.is_active = 'Y'
            ORDER BY m.control_code
        ''', (rcm_id,)).fetchall()
        return [dict(mapping) for mapping in mappings]

def evaluate_rcm_completeness(rcm_id, user_id):
    """RCM 완성도 평가 실행"""
    import json
    
    # RCM 상세 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    total_controls = len(rcm_details)
    
    if total_controls == 0:
        return {
            'completeness_score': 0.0,
            'total_controls': 0,
            'mapped_controls': 0,
            'details': []
        }
    
    # 기준통제 매핑 조회
    mappings = get_rcm_standard_mappings(rcm_id)
    mapped_controls = len(mappings)
    
    # 각 통제별 완성도 검사
    eval_details = []
    
    for detail in rcm_details:
        control_eval = {
            'control_code': detail['control_code'],
            'control_name': detail['control_name'],
            'is_mapped': False,
            'completeness': 0.0
        }
        
        # 매핑된 기준통제 찾기
        mapped_std = None
        for mapping in mappings:
            if mapping['control_code'] == detail['control_code']:
                mapped_std = mapping
                control_eval['is_mapped'] = True
                control_eval['std_control_name'] = mapping['std_control_name']
                break
        
        # 매핑된 통제는 100% 완성도로 처리 (현재는 단순 매핑 여부만 체크)
        if mapped_std:
            control_eval['completeness'] = 100.0
        
        eval_details.append(control_eval)
    
    # 전체 완성도 점수 계산 (매핑 비율 기준)
    completeness_score = (mapped_controls / total_controls * 100) if total_controls > 0 else 0.0
    
    # 결과 저장
    eval_result = {
        'completeness_score': round(completeness_score, 2),
        'total_controls': total_controls,
        'mapped_controls': mapped_controls,
        'details': eval_details
    }
    
    with get_db() as conn:
        conn.execute('''
            INSERT INTO sb_rcm_completeness_eval
            (rcm_id, total_controls, mapped_controls, 
             completeness_score, eval_details, eval_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (rcm_id, total_controls, mapped_controls,
              completeness_score, json.dumps(eval_details, ensure_ascii=False), user_id))
        conn.commit()
    
    return eval_result

# RCM 검토 결과 저장/조회 함수들

def save_rcm_mapping(rcm_id, detail_id, std_control_id, user_id):
    """개별 RCM 통제의 매핑 저장 (sb_rcm_detail 테이블 사용)"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                UPDATE sb_rcm_detail
                SET mapped_std_control_id = ?,
                    mapped_date = CURRENT_TIMESTAMP,
                    mapped_by = ?
                WHERE detail_id = ?
            ''', (std_control_id, user_id, detail_id))
            
            if cursor.rowcount == 0:
                raise Exception(f"Detail ID {detail_id}를 찾을 수 없습니다.")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"매핑 저장 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def delete_rcm_mapping(rcm_id, detail_id, user_id):
    """개별 RCM 통제의 매핑 삭제 (sb_rcm_detail 테이블 사용)"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                UPDATE sb_rcm_detail
                SET mapped_std_control_id = NULL,
                    mapped_date = NULL,
                    mapped_by = NULL,
                    ai_review_status = NULL,
                    ai_review_recommendation = NULL,
                    ai_reviewed_date = NULL,
                    ai_reviewed_by = NULL
                WHERE detail_id = ?
            ''', (detail_id,))
            
            if cursor.rowcount == 0:
                raise Exception(f"Detail ID {detail_id}를 찾을 수 없습니다.")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"매핑 삭제 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def get_rcm_detail_mappings(rcm_id):
    """RCM의 개별 통제 매핑 조회 (sb_rcm_detail 테이블 사용)"""
    with get_db() as conn:
        mappings = conn.execute('''
            SELECT 
                d.detail_id,
                d.control_code,
                d.control_name,
                d.mapped_std_control_id as std_control_id,
                d.mapped_date,
                d.mapped_by,
                sc.control_name as std_control_name,
                sc.control_category
            FROM sb_rcm_detail d
            LEFT JOIN sb_standard_control sc ON d.mapped_std_control_id = sc.std_control_id
            WHERE d.rcm_id = ? AND d.mapped_std_control_id IS NOT NULL
            ORDER BY d.control_code
        ''', (rcm_id,)).fetchall()
        return [dict(mapping) for mapping in mappings]

def save_rcm_ai_review(rcm_id, detail_id, recommendation, user_id):
    """개별 RCM 통제의 AI 검토 결과 저장"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                UPDATE sb_rcm_detail
                SET ai_review_status = 'completed',
                    ai_review_recommendation = ?,
                    ai_reviewed_date = CURRENT_TIMESTAMP,
                    ai_reviewed_by = ?
                WHERE detail_id = ?
            ''', (recommendation, user_id, detail_id))
            
            if cursor.rowcount == 0:
                raise Exception(f"Detail ID {detail_id}를 찾을 수 없습니다.")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"AI 검토 저장 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def get_control_review_result(rcm_id, detail_id):
    """개별 통제의 검토 결과 조회"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT 
                    detail_id,
                    control_code,
                    control_name,
                    mapped_std_control_id,
                    mapped_date,
                    mapped_by,
                    ai_review_status,
                    ai_review_recommendation,
                    ai_reviewed_date,
                    ai_reviewed_by
                FROM sb_rcm_detail
                WHERE detail_id = ?
            ''', (detail_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'detail_id': result[0],
                    'control_code': result[1],
                    'control_name': result[2],
                    'mapped_std_control_id': result[3],
                    'mapped_date': result[4],
                    'mapped_by': result[5],
                    'ai_review_status': result[6],
                    'ai_review_recommendation': result[7],
                    'ai_reviewed_date': result[8],
                    'ai_reviewed_by': result[9]
                }
            return None
            
    except Exception as e:
        print(f"통제 검토 결과 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_control_review_result(rcm_id, detail_id, std_control_id, ai_review_recommendation, user_id, status='completed'):
    """개별 통제 검토 결과 저장 (매핑 + AI 검토 통합)"""
    try:
        with get_db() as conn:
            cursor = conn.execute('''
                UPDATE sb_rcm_detail
                SET mapped_std_control_id = ?,
                    mapped_date = CURRENT_TIMESTAMP,
                    mapped_by = ?,
                    ai_review_status = ?,
                    ai_review_recommendation = ?,
                    ai_reviewed_date = CURRENT_TIMESTAMP,
                    ai_reviewed_by = ?
                WHERE detail_id = ?
            ''', (std_control_id, user_id, status, ai_review_recommendation, user_id, detail_id))
            
            if cursor.rowcount == 0:
                raise Exception(f"Detail ID {detail_id}를 찾을 수 없습니다.")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"통제 검토 결과 저장 오류: {e}")
        import traceback
        traceback.print_exc()
        raise

def get_rcm_review_result(rcm_id):
    """RCM 검토 결과 조회 (sb_rcm_detail 테이블에서)"""
    try:
        with get_db() as conn:
            # RCM 기본 정보
            rcm_info = conn.execute('''
                SELECT rcm_id, rcm_name FROM sb_rcm WHERE rcm_id = ?
            ''', (rcm_id,)).fetchone()
            
            if not rcm_info:
                return None
            
            # 통제별 매핑 및 AI 검토 정보
            details = conn.execute('''
                SELECT detail_id, control_code, control_name,
                       mapped_std_control_id, mapped_date, mapped_by,
                       ai_review_status, ai_review_recommendation, ai_reviewed_date, ai_reviewed_by,
                       mu.user_name as mapped_user_name,
                       au.user_name as ai_reviewed_user_name
                FROM sb_rcm_detail d
                LEFT JOIN sb_user mu ON d.mapped_by = mu.user_id
                LEFT JOIN sb_user au ON d.ai_reviewed_by = au.user_id
                WHERE d.rcm_id = ?
                ORDER BY d.control_code
            ''', (rcm_id,)).fetchall()
            
            # 데이터를 구조화
            mapping_data = {}
            ai_review_data = {}
            
            for detail in details:
                detail_dict = dict(detail)
                
                # 매핑 정보
                if detail['mapped_std_control_id']:
                    mapping_data[str(detail['mapped_std_control_id'])] = {
                        'control_code': detail['control_code'],
                        'mapped_date': detail['mapped_date'],
                        'mapped_by': detail['mapped_by'],
                        'mapped_user_name': detail['mapped_user_name']
                    }
                
                # AI 검토 정보
                if detail['ai_review_status'] == 'completed':
                    ai_review_data[str(detail['mapped_std_control_id'] or detail['detail_id'])] = {
                        'status': 'completed',
                        'recommendation': detail['ai_review_recommendation'],
                        'reviewed_date': detail['ai_reviewed_date'],
                        'reviewed_by': detail['ai_reviewed_by'],
                        'reviewed_user_name': detail['ai_reviewed_user_name']
                    }
            
            return {
                'rcm_id': rcm_info['rcm_id'],
                'rcm_name': rcm_info['rcm_name'],
                'mapping_data': mapping_data,
                'ai_review_data': ai_review_data,
                'has_data': len(mapping_data) > 0 or len(ai_review_data) > 0
            }
                
    except Exception as e:
        print(f"RCM 검토 결과 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def clear_rcm_review_result(rcm_id):
    """RCM 검토 결과 초기화"""
    try:
        with get_db() as conn:
            conn.execute('''
                UPDATE sb_rcm_detail
                SET mapped_std_control_id = NULL,
                    mapped_date = NULL,
                    mapped_by = NULL,
                    ai_review_status = 'not_reviewed',
                    ai_review_recommendation = NULL,
                    ai_reviewed_date = NULL,
                    ai_reviewed_by = NULL
                WHERE rcm_id = ?
            ''', (rcm_id,))
            conn.commit()
            return True
            
    except Exception as e:
        print(f"RCM 검토 결과 초기화 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_rcm_review_status_summary():
    """모든 RCM의 검토 상태 요약"""
    try:
        with get_db() as conn:
            results = conn.execute('''
                SELECT r.rcm_id, r.rcm_name,
                       COUNT(d.detail_id) as total_controls,
                       COUNT(d.mapped_std_control_id) as mapped_count,
                       COUNT(CASE WHEN d.ai_review_status = 'completed' THEN 1 END) as ai_reviewed_count,
                       MAX(d.mapped_date) as last_mapped_date,
                       MAX(d.ai_reviewed_date) as last_reviewed_date
                FROM sb_rcm r
                LEFT JOIN sb_rcm_detail d ON r.rcm_id = d.rcm_id
                WHERE r.is_active = 'Y'
                GROUP BY r.rcm_id, r.rcm_name
                ORDER BY r.rcm_name
            ''').fetchall()
            
            summary_list = []
            for result in results:
                result_dict = dict(result)
                
                # 검토 상태 결정
                if result['ai_reviewed_count'] > 0:
                    result_dict['review_status'] = 'in_progress'
                elif result['mapped_count'] > 0:
                    result_dict['review_status'] = 'in_progress'
                else:
                    result_dict['review_status'] = 'not_started'
                
                summary_list.append(result_dict)
            
            return summary_list
            
    except Exception as e:
        print(f"RCM 검토 상태 요약 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

# 호환성을 위한 wrapper 함수
def save_rcm_review_result(rcm_id, user_id, mapping_data, ai_review_data, status='in_progress', notes=''):
    """기존 API 호환성을 위한 wrapper 함수"""
    # 매핑 데이터 저장
    for std_control_id, mapping_info in mapping_data.items():
        if mapping_info.get('control_code'):
            save_rcm_mapping(rcm_id, mapping_info['control_code'], int(std_control_id), user_id)
    
    # AI 검토 데이터 저장
    for std_control_id, ai_info in ai_review_data.items():
        if ai_info.get('status') == 'completed' and ai_info.get('recommendation'):
            # std_control_id로 control_code 찾기
            with get_db() as conn:
                result = conn.execute('''
                    SELECT control_code FROM sb_rcm_detail
                    WHERE rcm_id = ? AND mapped_std_control_id = ?
                ''', (rcm_id, int(std_control_id))).fetchone()
                
                if result:
                    save_rcm_ai_review(rcm_id, result['control_code'], ai_info['recommendation'], user_id)
    
    return rcm_id

