from flask import Flask, render_template, request, send_file, redirect, url_for, session, jsonify, flash
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from openpyxl import load_workbook
from snowball_link1 import generate_and_send_rcm_excel
from snowball_link2 import export_interview_excel_and_send, s_questions, question_count, is_ineffective, fill_sheet, link2_prev_logic, get_text_itgc, get_conditional_questions
from snowball_link4 import get_link4_content
from snowball_mail import get_gmail_credentials, send_gmail, send_gmail_with_attachment
from snowball_link5 import bp_link5
from snowball_link6 import bp_link6
from snowball_link7 import bp_link7
from snowball_link8 import bp_link8
from auth import init_db, send_otp, verify_otp, login_required, get_current_user, get_db, log_user_activity, get_user_activity_logs, get_activity_log_count, check_ai_review_limit, increment_ai_review_count, get_ai_review_status, create_rcm, get_user_rcms, get_rcm_details, save_rcm_details, grant_rcm_access, get_all_rcms, save_design_evaluation, get_design_evaluations, save_operation_evaluation, get_operation_evaluations
import uuid
import json
import re

def perform_auto_mapping(headers):
    """컬럼명 기반 자동 매핑"""
    # 시스템 필드와 가능한 컬럼명 패턴 정의
    field_patterns = {
        'control_code': [
            '통제코드', '통제 코드', 'control_code', 'control code', 
            '코드', 'code', '번호', 'no', 'id'
        ],
        'control_name': [
            '통제명', '통제 명', '통제이름', '통제 이름', 'control_name', 'control name',
            '통제활동명', '명칭', 'name', 'title', '제목'
        ],
        'control_description': [
            '통제활동설명', '통제 활동 설명', '설명', '상세설명', 'description', 'detail',
            '내용', 'content', '통제활동', '활동설명'
        ],
        'key_control': [
            '핵심통제여부', '핵심통제', '핵심 통제', 'key_control', 'key control',
            '중요통제', 'key', '핵심', '중요'
        ],
        'control_frequency': [
            '통제주기', '통제 주기', '주기', 'frequency', 'cycle',
            '빈도', '실행주기', '수행주기'
        ],
        'control_type': [
            '통제유형', '통제 유형', '유형', 'type', 'control_type',
            '예방적발', '예방/적발', '통제타입'
        ],
        'control_nature': [
            '통제구분', '통제 구분', '구분', 'nature', 'control_nature',
            '자동수동', '자동/수동', '수행방식'
        ],
        'population': [
            '모집단', '대상', 'population', '범위', 'scope',
            '테스트대상', '검토대상'
        ],
        'population_completeness_check': [
            '모집단완전성확인', '모집단 완전성 확인', '완전성확인', '완전성 확인',
            'completeness', '완전성', 'population_completeness'
        ],
        'population_count': [
            '모집단갯수', '모집단 갯수', '갯수', '건수', 'count',
            '수량', '개수', 'population_count'
        ],
        'test_procedure': [
            '테스트절차', '테스트 절차', '절차', 'procedure', 'test_procedure',
            '검토절차', '확인절차', '감사절차'
        ]
    }
    
    auto_mapping = {}
    
    for header_index, header in enumerate(headers):
        if not header or not isinstance(header, str):
            continue
            
        header_lower = header.strip().lower()
        
        # 각 시스템 필드별로 매칭 점수 계산
        best_match = None
        best_score = 0
        
        for field_key, patterns in field_patterns.items():
            for pattern in patterns:
                pattern_lower = pattern.lower()
                
                # 정확히 일치하는 경우
                if header_lower == pattern_lower:
                    score = 100
                # 포함하는 경우
                elif pattern_lower in header_lower or header_lower in pattern_lower:
                    score = 80
                # 유사한 경우 (공통 단어가 있는 경우)
                elif any(word in header_lower for word in pattern_lower.split()):
                    score = 60
                else:
                    score = 0
                
                if score > best_score:
                    best_score = score
                    best_match = field_key
        
        # 일정 점수 이상일 때만 자동 매핑
        if best_match and best_score >= 60:
            auto_mapping[best_match] = header_index
    
    print(f"자동 매핑 결과: {auto_mapping}")
    return auto_mapping

app = Flask(__name__)
app.secret_key = '150606'

# 세션 만료 시간 설정 (24시간으로 연장)
# 브라우저 종료시에만 세션 만료 (permanent session 사용하지 않음)

# 세션 보안 설정
app.config.update(
    SESSION_COOKIE_SECURE=False,  # HTTPS 환경에서는 True로 설정
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    # 브라우저 종료 후에도 세션 유지되도록 설정
    SESSION_COOKIE_MAX_AGE=timedelta(hours=24).total_seconds(),  # 24시간
)

# --- File-based Progress Tracking ---
# WSGI 환경에서 안전한 경로 사용
PROGRESS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'progress_data')
if not os.path.exists(PROGRESS_DIR):
    try:
        os.makedirs(PROGRESS_DIR, exist_ok=True)
        print(f"Created progress directory: {PROGRESS_DIR}")
    except Exception as e:
        print(f"Error creating progress directory {PROGRESS_DIR}: {e}")
        # 시스템 임시 디렉토리를 대안으로 사용
        import tempfile
        PROGRESS_DIR = os.path.join(tempfile.gettempdir(), 'snowball_progress')
        os.makedirs(PROGRESS_DIR, exist_ok=True)
        print(f"Using fallback progress directory: {PROGRESS_DIR}")

def get_progress_status(task_id):
    """파일에서 진행률 상태 읽기"""
    progress_file = os.path.join(PROGRESS_DIR, f"{task_id}.progress")
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Progress read for task {task_id}: {data}")  # 디버그 로그
                return data
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading progress file for task {task_id}: {e}")
    print(f"Progress file not found for task {task_id}, returning default")
    return {
        'percentage': 0,
        'current_task': 'AI 검토를 준비하고 있습니다...',
        'is_processing': True # 클라이언트가 폴링을 계속하도록 설정
    }

def set_progress_status(task_id, status):
    """파일에 진행률 상태 저장"""
    progress_file = os.path.join(PROGRESS_DIR, f"{task_id}.progress")
    try:
        # 임시 파일에 먼저 쓰고 원자적으로 이동 (WSGI 환경에서 안전)
        temp_file = progress_file + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
            f.flush()  # 버퍼를 즉시 플러시
            os.fsync(f.fileno())  # 디스크에 강제로 쓰기
        
        # 원자적으로 파일 이동
        os.replace(temp_file, progress_file)
        print(f"Progress written for task {task_id}: {status}")  # 디버그 로그
    except IOError as e:
        print(f"Error writing progress file for task {task_id}: {e}")
        # 임시 파일이 남아있으면 삭제
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass

def update_progress(task_id, percentage, task_description):
    """진행률 업데이트 함수 (파일 기반)"""
    if task_id is None:
        print(f"Warning: task_id is None, cannot update progress")
        return
        
    status = {
        'percentage': int(percentage),  # 정수로 변환
        'current_task': str(task_description),  # 문자열로 변환
        'is_processing': percentage < 100,  # 100%가 되면 처리 완료
        'timestamp': datetime.now().isoformat()  # 타임스탬프 추가
    }
    set_progress_status(task_id, status)
    print(f"Progress Update (Task {task_id}): {percentage}% - {task_description}")

def reset_progress(task_id):
    """진행률 파일 삭제 함수"""
    progress_file = os.path.join(PROGRESS_DIR, f"{task_id}.progress")
    if os.path.exists(progress_file):
        try:
            os.remove(progress_file)
            print(f"Progress file for task {task_id} removed.")
        except OSError as e:
            print(f"Error removing progress file: {e}")

# 시작할 질문 번호 설정 (1부터 시작)
if __name__ == '__main__':
    START_QUESTION = 0
else:
    START_QUESTION = 0

load_dotenv()

# 데이터베이스 초기화
with app.app_context():
    init_db()

@app.before_request
def before_request():
    """모든 요청 전에 실행되는 함수 - 세션 유지 처리 및 타임아웃 체크"""
    # 로그인한 사용자의 세션을 자동으로 갱신
    if 'user_id' in session:
        # 마지막 활동 시간 체크 (10분 초과 시 자동 로그아웃)
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(minutes=10):
                print(f"세션 타임아웃: 10분 비활성으로 자동 로그아웃")
                session.clear()
                return redirect(url_for('login'))
        
        # session.permanent = True  # 브라우저 종료시 세션 만료
        # 세션 갱신 시간을 업데이트
        session['last_activity'] = datetime.now().isoformat()

def is_logged_in():
    """로그인 상태 확인 함수"""
    return 'user_id' in session and get_current_user() is not None

def get_user_info():
    """현재 로그인한 사용자 정보 반환 (없으면 None)"""
    if is_logged_in():
        # 세션에 저장된 user_info를 우선 사용
        if 'user_info' in session:
            return session['user_info']
        # 없으면 데이터베이스에서 조회
        return get_current_user()
    return None

def require_login_for_feature(feature_name="이 기능"):
    """특정 기능에 로그인이 필요할 때 사용하는 함수"""
    if not is_logged_in():
        return {
            'error': True,
            'message': f'{feature_name}을 사용하려면 로그인이 필요합니다.',
            'login_url': url_for('login')
        }
    return {'error': False}

def require_admin():
    """관리자 권한 확인 함수"""
    if not is_logged_in():
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))
    
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('index'))
    
    return None

def reset_interview_session():
    """인터뷰 관련 세션만 초기화 (로그인 세션은 보존)"""
    # 인터뷰 관련 키만 제거
    interview_keys = ['question_index', 'answer', 'textarea_answer', 'System', 'Cloud', 'OS_Tool', 'DB_Tool', 'Batch_Tool']
    for key in interview_keys:
        session.pop(key, None)
    
    # 인터뷰 세션 재초기화
    user_info = get_user_info()
    if user_info and user_info.get('user_email'):
        # 로그인된 사용자: 첫 번째 질문에 이메일 자동 입력하고 두 번째 질문부터 시작
        session['question_index'] = 1
        session['answer'] = [''] * question_count
        session['textarea_answer'] = [''] * question_count
        session['answer'][0] = user_info['user_email']  # 첫 번째 답변에 이메일 설정
    else:
        # 비로그인 사용자: 첫 번째 질문부터 시작
        session['question_index'] = START_QUESTION - 1 if 1 <= START_QUESTION <= question_count else 0
        session['answer'] = [''] * question_count
        session['textarea_answer'] = [''] * question_count
    
    print("인터뷰 세션이 초기화되었습니다 (로그인 세션 보존)")

def clear_skipped_answers(answers, textarea_answers):
    """조건부 질문 스킵 시 해당 범위의 답변을 공란으로 처리"""
    if not answers or len(answers) < 4:
        return
    
    skip_ranges = []
    
    # 3번 답변이 N이면 4~5번 질문 생략
    if len(answers) > 3 and answers[3] and str(answers[3]).upper() == 'N':
        skip_ranges.append((4, 5))
    
    # 14번 답변이 N이면 15~23번 질문 생략
    if len(answers) > 14 and answers[14] and str(answers[14]).upper() == 'N':
        skip_ranges.append((15, 23))
    
    # 24번 답변이 N이면 25~30번 질문 생략
    if len(answers) > 24 and answers[24] and str(answers[24]).upper() == 'N':
        skip_ranges.append((25, 30))
    
    # 31번 답변이 N이면 32~37번 질문 생략
    if len(answers) > 31 and answers[31] and str(answers[31]).upper() == 'N':
        skip_ranges.append((32, 37))
    
    # 38번 답변이 N이면 39~43번 질문 생략
    if len(answers) > 38 and answers[38] and str(answers[38]).upper() == 'N':
        skip_ranges.append((39, 43))
    
    # 스킵된 범위의 답변을 공란으로 설정
    for start, end in skip_ranges:
        for i in range(start, end + 1):
            if i < len(answers):
                answers[i] = ''
            if i < len(textarea_answers):
                textarea_answers[i] = ''
    
    print(f"[CLEAR DEBUG] 스킵된 질문 범위: {skip_ranges}")
    for start, end in skip_ranges:
        print(f"[CLEAR DEBUG] {start}~{end}번 답변 공란 처리 완료")

def log_session_info(route_name):
    """세션 정보를 콘솔에 출력하는 디버깅 함수"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n=== [{timestamp}] {route_name} 접근 ===")
    print(f"IP: {request.remote_addr}")
    print(f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:50]}...")
    
    if 'user_id' in session:
        current_user = get_current_user()
        if current_user:
            print(f"로그인 상태: ✓")
            print(f"사용자 ID: {session['user_id']}")
            print(f"사용자 이름: {current_user['user_name']}")
            print(f"이메일: {current_user['user_email']}")
            print(f"세션 로그인 시간: {session.get('login_time', 'N/A')}")
            print(f"세션 마지막 활동: {session.get('last_activity', 'N/A')}")
            print(f"DB 마지막 로그인: {current_user.get('last_login_date', 'N/A')}")
            print(f"세션 영구 설정: {session.permanent}")
        else:
            print(f"로그인 상태: ✗ (세션은 있으나 사용자 정보 없음)")
    else:
        print(f"로그인 상태: ✗ (세션 없음)")
    
    print(f"세션 키: {list(session.keys())}")
    print("=" * 50)

@app.route('/')
def index():
    log_session_info("메인 페이지")
    
    # 개발 단계: 127.0.0.1:5001 접속시 자동 로그인
    if not is_logged_in():
        # 클라이언트 IP가 127.0.0.1이고 포트가 5001인 경우에만 자동 로그인
        client_ip = request.environ.get('REMOTE_ADDR', '')
        server_port = request.environ.get('SERVER_PORT', '')
        
        if client_ip == '127.0.0.1' and server_port == '5001':
            with get_db() as conn:
                user = conn.execute(
                    'SELECT * FROM sb_user WHERE user_email = ? AND (effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP)',
                    ('snowball2727@naver.com',)
                ).fetchone()
                
                if user:
                    # SQLite Row 객체를 딕셔너리로 변환
                    user_dict = dict(user)
                    
                    session['user_id'] = user_dict['user_id']
                    session['user_email'] = user_dict['user_email']
                    session['user_info'] = {
                        'user_id': user_dict['user_id'],
                        'user_name': user_dict['user_name'],
                        'user_email': user_dict['user_email'],
                        'company_name': user_dict.get('company_name', ''),
                        'phone_number': user_dict.get('phone_number', ''),
                        'admin_flag': user_dict.get('admin_flag', 'N')
                    }
                    from datetime import datetime
                    session['last_activity'] = datetime.now().isoformat()
                    print(f"127.0.0.1:5001 자동 로그인 성공: {user_dict['user_email']} (admin_flag: {user_dict.get('admin_flag', 'N')})")
                else:
                    print("자동 로그인 실패: snowball2727@naver.com 계정을 찾을 수 없습니다.")
        else:
            print(f"자동 로그인 조건 불만족 - IP: {client_ip}, Port: {server_port}")
    
    user_info = get_user_info()
    user_name = user_info['user_name'] if user_info else "Guest"
    
    # 로그인한 사용자만 활동 로그 기록
    if is_logged_in():
        log_user_activity(user_info, 'PAGE_ACCESS', '메인 페이지', '/', 
                         request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('index.jsp', 
                         user_name=user_name, 
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         return_code=0, 
                         remote_addr=request.remote_addr)

@app.route('/login', methods=['GET', 'POST'])
def login():
    log_session_info("로그인 페이지")
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'send_otp':
            # OTP 발송 요청
            email = request.form.get('email')
            method = request.form.get('method', 'email')
            
            if not email:
                return render_template('login.jsp', error="이메일을 입력해주세요.", remote_addr=request.remote_addr)
            
            success, message = send_otp(email, method)
            if success:
                session['login_email'] = email
                return render_template('login.jsp', step='verify', email=email, message=message, remote_addr=request.remote_addr)
            else:
                return render_template('login.jsp', error=message, remote_addr=request.remote_addr)
        
        elif action == 'verify_otp':
            # OTP 검증
            email = session.get('login_email')
            otp_code = request.form.get('otp_code')
            
            if not email or not otp_code:
                return render_template('login.jsp', error="인증 코드를 입력해주세요.", remote_addr=request.remote_addr)
            
            success, result = verify_otp(email, otp_code)
            if success:
                # 로그인 성공
                user = result
                # session.permanent = True  # 브라우저 종료시 세션 만료
                session['user_id'] = user['user_id']
                session['user_name'] = user['user_name']
                session['user_info'] = {
                    'user_id': user['user_id'],
                    'user_name': user['user_name'],
                    'user_email': user['user_email'],
                    'company_name': user.get('company_name', ''),
                    'phone_number': user.get('phone_number', ''),
                    'admin_flag': user.get('admin_flag', 'N')
                }
                session['login_time'] = datetime.now().isoformat()
                session.pop('login_email', None)  # 임시 이메일 정보 삭제
                print(f"로그인 성공: {user['user_name']} ({user['user_email']})")
                return redirect(url_for('index'))
            else:
                return render_template('login.jsp', step='verify', email=email, error=result, remote_addr=request.remote_addr)
    
    return render_template('login.jsp', remote_addr=request.remote_addr)


@app.route('/logout')
def logout():
    log_session_info("로그아웃")
    session.clear()
    return redirect(url_for('index'))

@app.route('/extend_session', methods=['POST'])
def extend_session():
    """세션 연장 엔드포인트"""
    if 'user_id' in session:
        session['last_activity'] = datetime.now().isoformat()
        # session.permanent = True  # 브라우저 종료시 세션 만료
        print(f"세션 연장: {session.get('user_name', 'Unknown')}")
        return jsonify({'success': True, 'message': '세션이 연장되었습니다.'})
    return jsonify({'success': False, 'message': '로그인이 필요합니다.'})

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """브라우저 종료 시 세션 해제 엔드포인트"""
    if 'user_id' in session:
        user_name = session.get('user_name', 'Unknown')
        session.clear()
        print(f"브라우저 종료로 세션 해제: {user_name}")
    return '', 204

@app.route('/sms_test_log')
def sms_test_log():
    """SMS 테스트 로그 확인 (개발용)"""
    try:
        with open('sms_test_log.txt', 'r', encoding='utf-8') as f:
            logs = f.readlines()
        
        log_html = "<h3>SMS OTP 테스트 로그</h3>"
        log_html += "<div style='font-family: monospace; background: #f5f5f5; padding: 15px; border-radius: 5px;'>"
        
        if logs:
            for log in logs[-10:]:  # 최근 10개만 표시
                log_html += f"{log}<br>"
        else:
            log_html += "SMS 테스트 로그가 없습니다."
        
        log_html += "</div>"
        log_html += "<br><a href='/login'>로그인 페이지로 돌아가기</a>"
        
        return log_html
    except FileNotFoundError:
        return "<h3>SMS 테스트 로그 파일이 없습니다.</h3><a href='/login'>로그인 페이지로 돌아가기</a>"


def main():
    app.run(host='0.0.0.0', debug=False, port=5001)
    #app.run(host='127.0.0.1', debug=False, port=8001)

@app.route('/link0')
def link0():
    print("Reload")
    return render_template('link0.jsp')

@app.route('/link1')
def link1():
    log_session_info("RCM 페이지")
    print("RCM Function")
    user_info = get_user_info()
    users = user_info['user_name'] if user_info else "Guest"
    # 로그인된 사용자의 이메일 주소 자동 입력
    user_email = user_info.get('user_email', '') if user_info else ''
    
    # 로그인한 사용자만 활동 로그 기록
    if is_logged_in():
        log_user_activity(user_info, 'PAGE_ACCESS', 'RCM 페이지', '/link1', 
                         request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('link1.jsp', 
                         return_code=0, 
                         users=users, 
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         user_email=user_email,
                         remote_addr=request.remote_addr)

# Answer Type: 0: 리스트박스, 1: Y/N, 2: Textbox, 3: Y/N-Textbox, 4: Y/N-Textarea, 5: Textarea
# 기존 s_questions, question_count 정의 부분은 삭제

@app.route('/link2', methods=['GET', 'POST'])
def link2():
    log_session_info("Interview 페이지")
    print("Interview Function")
    
    user_info = get_user_info()
    # Interview 기능 시작 시에만 로그 기록 (GET 요청이고 reset=1 파라미터가 있거나 최초 진입 시)
    if is_logged_in() and request.method == 'GET':
        if request.args.get('reset') == '1' or 'question_index' not in session:
            log_user_activity(user_info, 'FEATURE_START', 'Interview 기능 시작', '/link2', 
                             request.remote_addr, request.headers.get('User-Agent'))

    if request.method == 'GET':
        # 쿼리 파라미터로 reset이 있을 때만 인터뷰 세션 초기화 (로그인 세션은 보존)
        if request.args.get('reset') == '1':
            reset_interview_session()
        # 세션에 값이 없으면(최초 진입)만 초기화
        elif 'question_index' not in session:
            user_info = get_user_info()
            if user_info and user_info.get('user_email'):
                # 로그인된 사용자: 첫 번째 질문에 이메일 자동 입력하고 두 번째 질문부터 시작
                session['question_index'] = 1
                session['answer'] = [''] * question_count
                session['textarea_answer'] = [''] * question_count
                session['answer'][0] = user_info['user_email']  # 첫 번째 답변에 이메일 설정
            else:
                # 비로그인 사용자: 첫 번째 질문부터 시작
                session['question_index'] = 0
                session['answer'] = [''] * question_count
                session['textarea_answer'] = [''] * question_count

        user_info = get_user_info()
        users = user_info['user_name'] if user_info else "Guest"
        # 현재 답변을 기반으로 필터링된 질문 목록 가져오기
        filtered_questions = get_conditional_questions(session.get('answer', []))
        current_question_index = session['question_index']
        
        # 현재 질문을 필터링된 목록에서 찾기
        current_question = None
        current_filtered_index = 0
        
        for idx, q in enumerate(filtered_questions):
            if q['index'] == current_question_index:
                current_question = q
                current_filtered_index = idx
                break
                
        if current_question is None:
            # 필터링된 목록에 없으면 원본에서 가져오기 (혹시 모를 상황 대비)
            current_question = s_questions[current_question_index] if current_question_index < len(s_questions) else s_questions[0]
        
        return render_template('link2.jsp',
                             question=current_question,
                             question_count=len(filtered_questions),
                             current_index=current_filtered_index,  # 필터링된 목록에서의 인덱스
                             actual_question_number=current_question['index'] + 1,  # 실제 질문 번호
                             remote_addr=request.remote_addr,
                             users=users,
                             is_logged_in=is_logged_in(),
                             user_info=user_info,
                             answer=session['answer'],
                             textarea_answer=session['textarea_answer'])

    question_index = session['question_index']

    if request.method == 'POST':
        form_data = request.form
        
        # 현재 질문의 filtered index를 구하기
        filtered_questions_before = get_conditional_questions(session.get('answer', []))
        current_filtered_index = 0
        for i, q in enumerate(filtered_questions_before):
            if q['index'] == question_index:
                current_filtered_index = i
                break
        
        # form 데이터는 current_filtered_index 기반으로 저장됨
        session['answer'][question_index] = form_data.get(f"a{current_filtered_index}", '')
        session['textarea_answer'][question_index] = form_data.get(f"a{current_filtered_index}_1", '')
        if form_data.get('a1_1'):
            session['System'] = form_data.get('a1_1')
        if form_data.get('a4_1'):
            session['Cloud'] = form_data.get('a4_1')
        if form_data.get('a6_1'):
            session['OS_Tool'] = form_data.get('a6_1')
        if form_data.get('a7_1'):
            session['DB_Tool'] = form_data.get('a7_1')
        if form_data.get('a8_1'):
            session['Batch_Tool'] = form_data.get('a8_1')

        # 현재 답변을 기반으로 필터링된 질문 목록 가져오기
        filtered_questions = get_conditional_questions(session.get('answer', []))
        
        # 다음 질문 인덱스를 결정하는 로직 (필터링된 질문 기준)
        current_filtered_index = 0
        for i, q in enumerate(filtered_questions):
            if q['index'] == question_index:
                current_filtered_index = i
                break
        
        # 다음 필터링된 질문으로 이동
        next_filtered_index = current_filtered_index + 1
        if next_filtered_index < len(filtered_questions):
            next_question_index = filtered_questions[next_filtered_index]['index']
        else:
            next_question_index = question_count  # 마지막 질문 이후

        # 마지막 질문 제출 시 AI 검토 선택 페이지로 이동
        if next_filtered_index >= len(filtered_questions):
            print('interview completed - redirecting to AI review selection page')
            print(f'Current question_index: {question_index}, question_count: {question_count}')
            print('--- 모든 답변(answers) ---')
            for idx, ans in enumerate(session.get('answer', [])):
                print(f"a{idx}: {ans}")
            print('--- 모든 textarea 답변(textarea_answer) ---')
            for idx, ans in enumerate(session.get('textarea_answer', [])):
                print(f"a{idx}_1: {ans}")

            # AI 검토 선택 페이지로 리디렉션
            return redirect(url_for('ai_review_selection'))

        session['question_index'] = next_question_index
        print(f"goto {session['question_index']}")
        print("Answers:", ", ".join(f"{i}: {ans}" for i, ans in enumerate(session['answer'])))
        print(f"입력받은 값(a{question_index}): {session['answer'][question_index]}")
        print(f"textarea 값(a{question_index}_1): {session['textarea_answer'][question_index]}")

        if next_question_index >= question_count:
            # 마지막 질문 이후에는 save_to_excel 호출하지 않음
            return redirect(url_for('index'))

    # 현재 질문을 렌더링
    filtered_questions = get_conditional_questions(session.get('answer', []))
    current_question_index = session['question_index']
    
    # 현재 질문을 필터링된 목록에서 찾기
    current_question = None
    current_filtered_index = 0
    
    for idx, q in enumerate(filtered_questions):
        if q['index'] == current_question_index:
            current_question = q
            current_filtered_index = idx
            break
            
    if current_question is None:
        current_question = s_questions[current_question_index] if current_question_index < len(s_questions) else s_questions[0]
    
    # 9번 질문 디버깅 추가
    if current_question['index'] == 9:
        print(f"[DEBUG] 9번 질문 표시됨")
        print(f"[DEBUG] 현재 세션 답변[9]: '{session['answer'][9] if len(session['answer']) > 9 else '없음'}'")
        print(f"[DEBUG] 전체 답변 개수: {len(session['answer'])}")
        print(f"[DEBUG] 답변 내용 (0~15): {session['answer'][:16] if len(session['answer']) >= 16 else session['answer']}")
    
    # 13번 질문 디버깅 추가
    if current_question['index'] == 13:
        print(f"[DEBUG] 13번 질문 표시됨")
        print(f"[DEBUG] 현재 세션 답변[13]: '{session['answer'][13] if len(session['answer']) > 13 else '없음'}'")
        print(f"[DEBUG] 13번 질문 텍스트: {current_question['text']}")
        print(f"[DEBUG] 전체 답변 개수: {len(session['answer'])}")
        print(f"[DEBUG] 답변 내용 (10~20): {session['answer'][10:21] if len(session['answer']) >= 21 else session['answer'][10:]}")

    user_info = get_user_info()
    users = user_info['user_name'] if user_info else "User List"
    return render_template(
        'link2.jsp',
        question=current_question,
        question_count=len(filtered_questions),
        current_index=current_filtered_index,
        actual_question_number=current_question['index'] + 1,
        remote_addr=request.remote_addr,
        users=users,
        is_logged_in=is_logged_in(),
        user_info=user_info,
        answer=session['answer'],
        textarea_answer=session['textarea_answer']
    )

@app.route('/link2/prev')
def link2_prev():
    # 세션에서 현재 인덱스 가져오기 및 이전으로 이동 (로직 분리)
    link2_prev_logic(session)
    # 다시 질문 페이지로 이동
    return redirect(url_for('link2'))

@app.route('/export_excel', methods=['GET'])
def save_to_excel():
    answers = session.get('answer', [])
    textarea_answers = session.get('textarea_answer', [])
    
    # 스킵된 질문들의 답변을 최종적으로 공란으로 처리
    clear_skipped_answers(answers, textarea_answers)
    
    # AI 검토 기능 활성화 (환경변수로 제어 가능)
    env_ai_review = os.getenv('ENABLE_AI_REVIEW', 'false').lower() == 'true'
    session_ai_review = session.get('enable_ai_review', False)
    enable_ai_review = env_ai_review or session_ai_review
    
    print(f"[DEBUG] AI 검토 설정 확인:")
    print(f"  - 환경변수 ENABLE_AI_REVIEW: {os.getenv('ENABLE_AI_REVIEW', 'false')} -> {env_ai_review}")
    print(f"  - 세션 enable_ai_review: {session_ai_review}")
    print(f"  - 최종 enable_ai_review: {enable_ai_review}")
    print(f"  - OPENAI_API_KEY 설정 여부: {'설정됨' if os.getenv('OPENAI_API_KEY') else '설정되지 않음'}")
    
    # 로그인한 사용자의 AI 검토 횟수 확인
    if is_logged_in():
        user_email = answers[0] if answers else ''
        can_use_ai, current_count, limit_count = check_ai_review_limit(user_email)
        print(f"  - AI 검토 횟수: {current_count}/{limit_count} (사용 가능: {can_use_ai})")
    else:
        print(f"  - 비로그인 사용자")

    success, user_email, error = export_interview_excel_and_send(
        answers,
        textarea_answers,
        get_text_itgc,
        fill_sheet,
        is_ineffective,
        send_gmail_with_attachment,
        enable_ai_review,
        None  # progress_callback
    )
    if success:
        return '<h3>인터뷰 내용에 따른 ITGC 설계평가 문서가 입력하신 메일로 전송되었습니다.<br>메일함을 확인해 주세요.</h3>\n<a href="/" style="display:inline-block;margin-top:20px;padding:10px 20px;background:#1976d2;color:#fff;text-decoration:none;border-radius:5px;">처음으로</a>'
    else:
        return f'<h3>메일 전송에 실패했습니다: {error}</h3>' if user_email else '<h3>메일 주소가 입력되지 않았습니다. 43번 질문에 메일 주소를 입력해 주세요.</h3>'

@app.route('/link3')
def link3():
    log_session_info("Operation Test 페이지")
    print("Paper Function")
    user_info = get_user_info()
    
    # 로그인한 사용자만 활동 로그 기록
    if is_logged_in():
        log_user_activity(user_info, 'PAGE_ACCESS', 'Operation Test 페이지', '/link3', 
                         request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('link3.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/link4')
def link4():
    log_session_info("영상자료 페이지")
    print("Video Function")
    user_info = get_user_info()
    
    # 로그인한 사용자만 활동 로그 기록
    if is_logged_in():
        log_user_activity(user_info, 'PAGE_ACCESS', '영상자료 페이지', '/link4', 
                         request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('link4.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/link5', methods=['GET'])
def link5():
    log_session_info("AI 페이지")
    return render_template('link5.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
                         remote_addr=request.remote_addr)

@app.route('/link6', methods=['GET'])
def link6():
    log_session_info("AI Interview 페이지")
    return render_template('link6.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
                         remote_addr=request.remote_addr)

@app.route('/link9')
def link9():
    log_session_info("기타 기능 페이지")
    print("ETC Function")
    return render_template('link9.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
                         remote_addr=request.remote_addr)

@app.route('/rcm_generate', methods=['POST'])
def rcm_generate():
    form_data = request.form.to_dict()
    success, user_email, error = generate_and_send_rcm_excel(form_data)
    if success:
        return render_template('mail_sent.jsp', user_email=user_email)
    else:
        if user_email:
            return f'<h3>메일 전송에 실패했습니다: {error}</h3>'
        else:
            return '<h3>메일 주소가 없습니다. 담당자 정보를 확인해 주세요.</h3>'

@app.route('/rcm_request', methods=['POST'])
def rcm_request():

    form_data = request.form.to_dict()
    # link1_rcm.rcm_request(form_data) # Removed link1_rcm
    # Placeholder for rcm_request logic
    print("RCM Request called (placeholder)")
    print("Form data:", form_data)
    return render_template('link1.jsp', return_code=1)

@app.route('/paper_request', methods=['POST'])
def paper_request():
    print("Paper Request called")

    form_data = request.form.to_dict()
    # output_path = link2_design.paper_request(form_data) # Removed link2_design
    # Placeholder for paper_request logic
    print("Paper Request form data:", form_data)
    user_info = get_user_info()
    return render_template('link2.jsp', 
                         return_code=2,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/design_generate', methods=['POST'])
def design_generate():
    print("Design Generate called")

    form_data = request.form.to_dict()
    # output_path = link2_design.design_generate(form_data) # Removed link2_design
    # Placeholder for design_generate logic
    print("Design Generate form data:", form_data)
    return send_file(os.path.join("static", "Design_Template.xlsx"), as_attachment=True) # Use a dummy template

@app.route('/design_template_download', methods=['POST'])
def design_template_downloade():
    print("Design Template Download called")

    form_data = request.form.to_dict()
    # output_path = link2_design.design_template_download(form_data) # Removed link2_design
    # Placeholder for design_template_download logic
    print("Design Template Download form data:", form_data)
    return send_file(os.path.join("static", "Design_Template.xlsx"), as_attachment=True) # Use a dummy template

@app.route('/paper_template_download', methods=['POST'])
def paper_template_download():

    form_data = request.form.to_dict()
    # output_path = link3_operation.paper_template_download(form_data) # Removed link3_operation
    # Placeholder for paper_template_download logic
    print("Paper Template Download form data:", form_data)
    param1 = form_data.get('param1')
    param2 = form_data.get('param2')

    print('output = ', os.path.join("static", "Design_Template.xlsx")) # Use a dummy template
    if os.path.exists(os.path.join("static", "Design_Template.xlsx")): # Use a dummy template
        return send_file(os.path.join("static", "Design_Template.xlsx"), as_attachment=True) # Use a dummy template
    else:
        return render_template('link3.jsp', return_param1=param1, return_param2=param2)

@app.route('/paper_generate', methods=['POST'])
def paper_generate():

    form_data = request.form.to_dict()
    # output_path = link3_operation.paper_generate(form_data) # Removed link3_operation
    # Placeholder for paper_generate logic
    print("Paper Generate form data:", form_data)
    return send_file(os.path.join("static", "Design_Template.xlsx"), as_attachment=True) # Use a dummy template

@app.route('/get_content_link4')
def get_content_link4():
    content_type = request.args.get('type')
    data = get_link4_content(content_type)
    if not data:
        return '<div style="text-align: center; padding: 20px;"><h3>준비 중입니다</h3><p>해당 항목은 현재 영상제작 중 입니다.</p></div>'
    return render_template('link4_detail.jsp',
        youtube_url=data['youtube_url'],
        img_url=data['img_url'],
        title=data['title'],
        desc=data['desc']
    )

@app.route('/get_content_link3')
def get_content_link3():
    # 모든 type에 대해 공통 step-card 템플릿 반환
    return render_template('link3_detail.jsp')

@app.route('/ai_review_selection')
def ai_review_selection():
    """AI 검토 옵션 선택 화면"""
    user_email = session.get('answer', [''])[0] if session.get('answer') else ''
    if not user_email:
        return redirect(url_for('link2', reset=1))  # 세션이 없으면 인터뷰 처음으로
    
    user_info = get_user_info()
    
    # 로그인한 사용자만 AI 검토 현황 표시
    current_count = 0
    if is_logged_in():
        current_count, _ = get_ai_review_status(user_email)
    
    return render_template('link2_ai_review.jsp', 
                         user_email=user_email,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         ai_review_count=current_count if is_logged_in() else None,
                         remote_addr=request.remote_addr)

@app.route('/process_with_ai_option', methods=['POST'])
def process_with_ai_option():
    """AI 검토 옵션에 따라 처리 페이지로 이동"""
    enable_ai_review = request.form.get('enable_ai_review', 'false').lower() == 'true'
    user_email = session.get('answer', [''])[0] if session.get('answer') else ''
    
    if enable_ai_review and is_logged_in():
        # 로그인한 사용자만 AI 검토 횟수 기록
        increment_ai_review_count(user_email)
    
    # 세션에 AI 검토 옵션 저장
    session['enable_ai_review'] = enable_ai_review
    
    print(f"User selected AI review: {enable_ai_review}")
    
    # processing 페이지로 리디렉션
    return redirect(url_for('processing'))

@app.route('/processing')
def processing():
    """인터뷰 완료 후 처리 중 화면"""
    user_email = session.get('answer', [''])[0] if session.get('answer') else ''
    enable_ai_review = session.get('enable_ai_review', False)
    
    # 고유한 작업 ID 생성 및 세션에 저장
    task_id = str(uuid.uuid4())
    session['processing_task_id'] = task_id
    
    # 초기 진행률 상태 파일 생성
    reset_progress(task_id) # 기존 파일이 있다면 삭제
    initial_status = {
        'percentage': 0,
        'current_task': 'AI 검토를 준비하고 있습니다...',
        'is_processing': True
    }
    set_progress_status(task_id, initial_status)
    
    return render_template('processing.jsp', user_email=user_email, enable_ai_review=enable_ai_review, task_id=task_id)

@app.route('/get_progress')
def get_progress():
    """진행률 상태 조회 엔드포인트"""
    task_id = request.args.get('task_id')
    if not task_id:
        print("Error: No task_id provided in get_progress")
        return jsonify({'error': 'No task_id provided'}), 400
    
    print(f"GET /get_progress called for task_id: {task_id}")
    status = get_progress_status(task_id)
    print(f"Returning status for task {task_id}: {status}")
    return jsonify(status)

@app.route('/process_interview', methods=['POST'])
def process_interview():
    """실제 인터뷰 처리 및 메일 발송"""
    data = request.get_json() or {}
    task_id = data.get('task_id')

    if not task_id:
        return jsonify({'success': False, 'error': 'No task_id provided'})

    try:
        # task_id를 포함하는 콜백 함수 생성
        progress_callback = lambda p, t: update_progress(task_id, p, t)
        
        progress_callback(5, "인터뷰 데이터를 확인하고 있습니다...")
        
        answers = session.get('answer', [])
        textarea_answers = session.get('textarea_answer', [])
        
        if not answers:
            reset_progress(task_id)
            return jsonify({'success': False, 'error': '인터뷰 데이터가 없습니다.'})
        
        user_email = answers[0] if answers else ''
        if not user_email:
            reset_progress(task_id)
            return jsonify({'success': False, 'error': '메일 주소가 입력되지 않았습니다.'})
        
        progress_callback(10, "AI 검토 설정을 확인하고 있습니다...")
        
        enable_ai_review = session.get('enable_ai_review', False)
        
        print(f"Processing interview for {user_email} (Task ID: {task_id})")
        progress_callback(15, "ITGC 설계평가 문서 생성을 시작합니다...")
        
        # 스킵된 질문들의 답변을 최종적으로 공란으로 처리
        clear_skipped_answers(answers, textarea_answers)
        
        success, returned_email, error = export_interview_excel_and_send(
            answers,
            textarea_answers,
            get_text_itgc,
            fill_sheet,
            is_ineffective,
            send_gmail_with_attachment,
            enable_ai_review,
            progress_callback
        )
        
        if success:
            status = get_progress_status(task_id)
            status['percentage'] = 100
            status['current_task'] = "처리가 완료되었습니다!"
            status['is_processing'] = False
            set_progress_status(task_id, status)
            print(f"Mail sent successfully to {returned_email}")
            # 성공 시에도 파일은 유지하여 클라이언트가 100%를 확인할 시간을 줌
            # reset_progress(task_id) # -> 클라이언트가 완료를 확인한 후 삭제하는 것이 더 나을 수 있음
            return jsonify({'success': True, 'email': returned_email})
        else:
            reset_progress(task_id)
            print(f"Mail send failed: {error}")
            return jsonify({'success': False, 'error': error})
            
    except Exception as e:
        reset_progress(task_id)
        print(f"Error in process_interview: {e}")
        return jsonify({'success': False, 'error': str(e)})


# === 관리자 페이지 ===
@app.route('/admin')
def admin():
    """관리자 메인 페이지"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    log_session_info("관리자 페이지")
    user_info = get_user_info()
    
    # 관리자 페이지 접근 로그
    log_user_activity(user_info, 'PAGE_ACCESS', '관리자 대시보드', '/admin', 
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('admin.jsp',
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/admin/users')
def admin_users():
    """사용자 관리 페이지"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    with get_db() as conn:
        users = conn.execute('''
            SELECT user_id, company_name, user_name, user_email, phone_number, 
                   admin_flag, effective_start_date, effective_end_date, 
                   creation_date, last_login_date
            FROM sb_user 
            ORDER BY creation_date DESC
        ''').fetchall()
        
        users_list = [dict(user) for user in users]
    
    return render_template('admin_users.jsp',
                         users=users_list,
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
                         remote_addr=request.remote_addr)

@app.route('/admin/users/add', methods=['POST'])
def admin_add_user():
    """사용자 추가"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        company_name = request.form.get('company_name')
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        phone_number = request.form.get('phone_number')
        admin_flag = request.form.get('admin_flag', 'N')
        effective_start_date = request.form.get('effective_start_date')
        effective_end_date = request.form.get('effective_end_date')
        
        # effective_end_date가 빈 문자열이면 NULL로 처리
        if not effective_end_date:
            effective_end_date = None
        
        with get_db() as conn:
            conn.execute('''
                INSERT INTO sb_user (company_name, user_name, user_email, phone_number, 
                                   admin_flag, effective_start_date, effective_end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_name, user_name, user_email, phone_number, 
                 admin_flag, effective_start_date, effective_end_date))
            conn.commit()
        
        flash('사용자가 성공적으로 추가되었습니다.')
    except Exception as e:
        flash(f'사용자 추가 중 오류가 발생했습니다: {str(e)}')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:user_id>', methods=['POST'])
def admin_edit_user(user_id):
    """사용자 정보 수정"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        company_name = request.form.get('company_name')
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        phone_number = request.form.get('phone_number')
        admin_flag = request.form.get('admin_flag', 'N')
        effective_start_date = request.form.get('effective_start_date')
        effective_end_date = request.form.get('effective_end_date')
        
        # effective_end_date가 빈 문자열이면 NULL로 처리
        if not effective_end_date:
            effective_end_date = None
        
        with get_db() as conn:
            conn.execute('''
                UPDATE sb_user 
                SET company_name = ?, user_name = ?, user_email = ?, phone_number = ?, 
                    admin_flag = ?, effective_start_date = ?, effective_end_date = ?
                WHERE user_id = ?
            ''', (company_name, user_name, user_email, phone_number, 
                 admin_flag, effective_start_date, effective_end_date, user_id))
            conn.commit()
        
        flash('사용자 정보가 성공적으로 수정되었습니다.')
    except Exception as e:
        flash(f'사용자 정보 수정 중 오류가 발생했습니다: {str(e)}')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    """사용자 삭제"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM sb_user WHERE user_id = ?', (user_id,))
            conn.commit()
        
        flash('사용자가 성공적으로 삭제되었습니다.')
    except Exception as e:
        flash(f'사용자 삭제 중 오류가 발생했습니다: {str(e)}')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/extend/<int:user_id>', methods=['POST'])
def admin_extend_user(user_id):
    """사용자 1년 연장"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        from datetime import date, timedelta
        today = date.today().strftime('%Y-%m-%d')
        next_year = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        with get_db() as conn:
            conn.execute('''
                UPDATE sb_user 
                SET effective_start_date = ?, effective_end_date = ?
                WHERE user_id = ?
            ''', (today, next_year, user_id))
            conn.commit()
        
        flash('사용자의 사용 기간이 1년 연장되었습니다.')
    except Exception as e:
        flash(f'사용자 기간 연장 중 오류가 발생했습니다: {str(e)}')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/logs')
def admin_logs():
    """사용자 활동 로그 조회 페이지"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    user_info = get_user_info()
    # 로그 조회 페이지는 로그 기록하지 않음 (무한 루프 방지)
    
    page = int(request.args.get('page', 1))
    per_page = 10  # 10개씩 표시
    offset = (page - 1) * per_page
    
    # 필터링 옵션
    user_filter = request.args.get('user_id')
    action_filter = request.args.get('action_type')
    
    # 로그 조회
    if user_filter:
        logs = get_user_activity_logs(limit=per_page, offset=offset, user_id=user_filter)
        total_count = get_activity_log_count(user_id=user_filter)
    else:
        logs = get_user_activity_logs(limit=per_page, offset=offset)
        total_count = get_activity_log_count()
    
    # 페이지네이션 계산
    total_pages = (total_count + per_page - 1) // per_page
    
    # 사용자 목록 (필터용)
    with get_db() as conn:
        users = conn.execute('SELECT user_id, user_name, user_email FROM sb_user ORDER BY user_name').fetchall()
        users_list = [dict(user) for user in users]
    
    return render_template('admin_logs.jsp',
                         logs=logs,
                         users=users_list,
                         current_page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         user_filter=user_filter,
                         action_filter=action_filter,
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
                         remote_addr=request.remote_addr)

# RCM 관리 라우트들
@app.route('/admin/rcm')
@login_required
def admin_rcm():
    """RCM 관리 메인 페이지"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('home'))
    
    # 모든 RCM 목록 조회
    rcms = get_all_rcms()
    
    return render_template('admin_rcm.jsp',
                         rcms=rcms,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/admin/rcm/upload')
@login_required
def admin_rcm_upload():
    """RCM 업로드 페이지"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('home'))
    
    # 모든 사용자 목록 조회 (회사별 RCM 업로드용)
    with get_db() as conn:
        users = conn.execute('''
            SELECT user_id, user_name, user_email, company_name 
            FROM sb_user 
            WHERE effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP
            ORDER BY company_name, user_name
        ''').fetchall()
        users_list = [dict(user) for user in users]
    
    return render_template('admin_rcm_upload.jsp',
                         users=users_list,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/admin/rcm/process_upload', methods=['POST'])
@login_required
def admin_rcm_process_upload():
    """Excel 파일 업로드 처리"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        rcm_name = request.form.get('rcm_name', '').strip()
        description = request.form.get('description', '').strip()
        target_user_id = request.form.get('target_user_id', '').strip()
        
        if not rcm_name:
            return jsonify({'success': False, 'message': 'RCM명은 필수입니다.'})
        
        if not target_user_id:
            return jsonify({'success': False, 'message': '대상 사용자를 선택해주세요.'})
        
        target_user_id = int(target_user_id)
        
        if 'excel_file' not in request.files:
            return jsonify({'success': False, 'message': 'Excel 파일을 선택해주세요.'})
        
        file = request.files['excel_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Excel 파일을 선택해주세요.'})
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': 'Excel 파일(.xlsx, .xls)만 업로드 가능합니다.'})
        
        # RCM 생성 (선택된 사용자를 소유자로 설정)
        rcm_id = create_rcm(rcm_name, description, target_user_id)
        
        # Excel 파일 읽기
        from openpyxl import load_workbook
        import tempfile
        import os
        
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_file.name)
        temp_file.close()
        
        try:
            # Excel 파일 읽기
            workbook = load_workbook(temp_file.name)
            sheet = workbook.active
            
            # 헤더 추출 (첫 번째 행)
            headers = []
            for cell in sheet[1]:
                headers.append(cell.value if cell.value else '')
            
            # 샘플 데이터 추출 (최대 3행)
            sample_data = []
            for row_num in range(2, min(5, sheet.max_row + 1)):  # 2행부터 최대 4행까지
                row_data = []
                for col_num in range(1, len(headers) + 1):
                    cell_value = sheet.cell(row=row_num, column=col_num).value
                    row_data.append(str(cell_value) if cell_value is not None else '')
                sample_data.append(row_data)
            
            # 자동 매핑 수행
            auto_mapping = perform_auto_mapping(headers)
            
            # 세션에 업로드 정보 저장
            session[f'rcm_upload_{rcm_id}'] = {
                'headers': headers,
                'sample_data': sample_data,
                'file_path': temp_file.name,
                'total_rows': sheet.max_row - 1,  # 헤더 제외
                'auto_mapping': auto_mapping
            }
            
            return jsonify({
                'success': True, 
                'rcm_id': rcm_id,
                'headers': headers,
                'sample_data': sample_data
            })
            
        finally:
            # Excel 파일은 매핑 완료 후 삭제하므로 여기서는 삭제하지 않음
            pass
            
    except Exception as e:
        print(f"Excel 업로드 오류: {e}")
        return jsonify({'success': False, 'message': f'파일 처리 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/rcm/mapping/<int:rcm_id>')
@login_required
def admin_rcm_mapping(rcm_id):
    """컬럼 매핑 페이지"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('home'))
    
    # 세션에서 업로드 정보 가져오기
    upload_key = f'rcm_upload_{rcm_id}'
    if upload_key not in session:
        flash('업로드 정보를 찾을 수 없습니다. 다시 업로드해주세요.')
        return redirect(url_for('admin_rcm_upload'))
    
    upload_info = session[upload_key]
    
    # RCM 정보 조회
    with get_db() as conn:
        rcm_info = conn.execute(
            'SELECT * FROM sb_rcm WHERE rcm_id = ?', (rcm_id,)
        ).fetchone()
        
        if not rcm_info:
            flash('RCM 정보를 찾을 수 없습니다.')
            return redirect(url_for('admin_rcm'))
    
    # 시스템 필드 정의
    system_fields = [
        {'key': 'control_code', 'name': '통제코드', 'required': True},
        {'key': 'control_name', 'name': '통제명', 'required': True},
        {'key': 'control_description', 'name': '통제활동설명', 'required': False},
        {'key': 'key_control', 'name': '핵심통제여부', 'required': False},
        {'key': 'control_frequency', 'name': '통제주기', 'required': False},
        {'key': 'control_type', 'name': '통제유형', 'required': False},
        {'key': 'control_nature', 'name': '통제구분', 'required': False},
        {'key': 'population', 'name': '모집단', 'required': False},
        {'key': 'population_completeness_check', 'name': '모집단완전성확인', 'required': False},
        {'key': 'population_count', 'name': '모집단갯수', 'required': False},
        {'key': 'test_procedure', 'name': '테스트절차', 'required': False}
    ]
    
    return render_template('admin_rcm_mapping.jsp',
                         rcm_info=dict(rcm_info),
                         headers=upload_info['headers'],
                         sample_data=upload_info['sample_data'],
                         system_fields=system_fields,
                         total_rows=upload_info['total_rows'],
                         auto_mapping=upload_info.get('auto_mapping', {}),
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/admin/rcm/save_mapping', methods=['POST'])
@login_required
def admin_rcm_save_mapping():
    """매핑된 RCM 데이터 저장"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        rcm_id = request.form.get('rcm_id')
        if not rcm_id:
            return jsonify({'success': False, 'message': 'RCM ID가 필요합니다.'})
        
        rcm_id = int(rcm_id)
        
        # 세션에서 업로드 정보 가져오기
        upload_key = f'rcm_upload_{rcm_id}'
        if upload_key not in session:
            return jsonify({'success': False, 'message': '업로드 정보를 찾을 수 없습니다.'})
        
        upload_info = session[upload_key]
        file_path = upload_info['file_path']
        headers = upload_info['headers']
        
        # 매핑 정보 수집
        field_mapping = {}
        for key in request.form:
            if key.startswith('mapping_'):
                field_name = key.replace('mapping_', '')
                column_index = request.form.get(key)
                if column_index:
                    field_mapping[field_name] = int(column_index)
        
        
        # Excel 파일 다시 읽기
        from openpyxl import load_workbook
        import os
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Excel 파일을 찾을 수 없습니다.'})
        
        workbook = load_workbook(file_path)
        sheet = workbook.active
        
        # 데이터 처리
        rcm_data = []
        for row_num in range(2, sheet.max_row + 1):  # 헤더 제외
            row_data = {}
            
            # 각 필드별로 매핑된 컬럼에서 데이터 추출
            for field_name, column_index in field_mapping.items():
                cell_value = sheet.cell(row=row_num, column=column_index + 1).value  # Excel은 1부터 시작
                row_data[field_name] = str(cell_value) if cell_value is not None else ''
            
            # 빈 행 건너뛰기 (통제코드가 없는 경우)
            if not row_data.get('control_code', '').strip():
                continue
                
            rcm_data.append(row_data)
        
        if not rcm_data:
            return jsonify({'success': False, 'message': '저장할 데이터가 없습니다. 통제코드가 매핑되었는지 확인해주세요.'})
        
        # 데이터베이스에 저장
        save_rcm_details(rcm_id, rcm_data)
        
        # RCM 소유자에게 자동으로 접근 권한 부여
        with get_db() as conn:
            rcm_owner = conn.execute(
                'SELECT upload_user_id FROM sb_rcm WHERE rcm_id = ?', (rcm_id,)
            ).fetchone()
            
            if rcm_owner:
                grant_rcm_access(rcm_owner['upload_user_id'], rcm_id, 'admin', user_info['user_id'])
        
        # 업로더(관리자)에게도 권한 부여 (소유자와 다른 경우)
        if rcm_owner and rcm_owner['upload_user_id'] != user_info['user_id']:
            grant_rcm_access(user_info['user_id'], rcm_id, 'admin', user_info['user_id'])
        
        # 임시 파일 삭제
        try:
            os.remove(file_path)
        except:
            pass
        
        # 세션에서 업로드 정보 삭제
        del session[upload_key]
        
        print(f"RCM 저장 완료: {len(rcm_data)}개 항목")
        
        return jsonify({
            'success': True, 
            'message': f'{len(rcm_data)}개의 RCM 항목이 성공적으로 저장되었습니다.'
        })
        
    except Exception as e:
        print(f"RCM 저장 오류: {e}")
        return jsonify({'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/rcm/<int:rcm_id>/view')
@login_required
def admin_rcm_view(rcm_id):
    """RCM 상세 보기"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('home'))
    
    # RCM 기본 정보 조회
    with get_db() as conn:
        rcm_info = conn.execute('''
            SELECT r.*, u.user_name as upload_user_name, u.company_name
            FROM sb_rcm r
            LEFT JOIN sb_user u ON r.upload_user_id = u.user_id
            WHERE r.rcm_id = ? AND r.is_active = 'Y'
        ''', (rcm_id,)).fetchone()
        
        if not rcm_info:
            flash('RCM을 찾을 수 없습니다.')
            return redirect(url_for('admin_rcm'))
    
    # RCM 상세 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    
    return render_template('admin_rcm_view.jsp',
                         rcm_info=dict(rcm_info),
                         rcm_details=rcm_details,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/admin/rcm/<int:rcm_id>/users')
@login_required
def admin_rcm_users(rcm_id):
    """RCM 사용자 관리"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        flash('관리자 권한이 필요합니다.')
        return redirect(url_for('home'))
    
    # RCM 기본 정보 조회
    with get_db() as conn:
        rcm_info = conn.execute('''
            SELECT r.*, u.user_name as upload_user_name, u.company_name
            FROM sb_rcm r
            LEFT JOIN sb_user u ON r.upload_user_id = u.user_id
            WHERE r.rcm_id = ? AND r.is_active = 'Y'
        ''', (rcm_id,)).fetchone()
        
        if not rcm_info:
            flash('RCM을 찾을 수 없습니다.')
            return redirect(url_for('admin_rcm'))
        
        # RCM 접근 권한이 있는 사용자 목록
        rcm_users = conn.execute('''
            SELECT ur.*, u.user_name, u.user_email, u.company_name,
                   gb.user_name as granted_by_name
            FROM sb_user_rcm ur
            INNER JOIN sb_user u ON ur.user_id = u.user_id
            LEFT JOIN sb_user gb ON ur.granted_by = gb.user_id
            WHERE ur.rcm_id = ? AND ur.is_active = 'Y'
            ORDER BY ur.granted_date DESC
        ''', (rcm_id,)).fetchall()
        
        # 전체 사용자 목록 (권한 부여용)
        all_users = conn.execute('''
            SELECT user_id, user_name, user_email, company_name
            FROM sb_user
            WHERE effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP
            ORDER BY company_name, user_name
        ''').fetchall()
    
    return render_template('admin_rcm_users.jsp',
                         rcm_info=dict(rcm_info),
                         rcm_users=[dict(user) for user in rcm_users],
                         all_users=[dict(user) for user in all_users],
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/admin/rcm/grant_access', methods=['POST'])
@login_required
def admin_rcm_grant_access():
    """사용자에게 RCM 접근 권한 부여"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        rcm_id = request.form.get('rcm_id')
        user_id = request.form.get('user_id')
        permission_type = request.form.get('permission_type')
        
        if not all([rcm_id, user_id, permission_type]):
            return jsonify({'success': False, 'message': '필수 정보가 누락되었습니다.'})
        
        rcm_id = int(rcm_id)
        user_id = int(user_id)
        
        if permission_type not in ['read', 'admin']:
            return jsonify({'success': False, 'message': '잘못된 권한 유형입니다.'})
        
        # 이미 권한이 있는지 확인
        with get_db() as conn:
            existing = conn.execute('''
                SELECT * FROM sb_user_rcm 
                WHERE rcm_id = ? AND user_id = ? AND is_active = 'Y'
            ''', (rcm_id, user_id)).fetchone()
            
            if existing:
                return jsonify({'success': False, 'message': '이미 해당 사용자에게 권한이 부여되어 있습니다.'})
            
            # 사용자 정보 조회
            target_user = conn.execute(
                'SELECT user_name FROM sb_user WHERE user_id = ?', (user_id,)
            ).fetchone()
            
            if not target_user:
                return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'})
        
        # 권한 부여
        grant_rcm_access(user_id, rcm_id, permission_type, user_info['user_id'])
        
        permission_text = '관리자' if permission_type == 'admin' else '읽기'
        return jsonify({
            'success': True, 
            'message': f'{target_user["user_name"]} 사용자에게 {permission_text} 권한을 부여했습니다.'
        })
        
    except Exception as e:
        print(f"권한 부여 오류: {e}")
        return jsonify({'success': False, 'message': f'권한 부여 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/rcm/change_permission', methods=['POST'])
@login_required
def admin_rcm_change_permission():
    """사용자의 RCM 접근 권한 변경"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        rcm_id = request.form.get('rcm_id')
        user_id = request.form.get('user_id')
        permission_type = request.form.get('permission_type')
        
        if not all([rcm_id, user_id, permission_type]):
            return jsonify({'success': False, 'message': '필수 정보가 누락되었습니다.'})
        
        rcm_id = int(rcm_id)
        user_id = int(user_id)
        
        if permission_type not in ['read', 'admin']:
            return jsonify({'success': False, 'message': '잘못된 권한 유형입니다.'})
        
        with get_db() as conn:
            # 기존 권한 확인
            existing = conn.execute('''
                SELECT * FROM sb_user_rcm 
                WHERE rcm_id = ? AND user_id = ? AND is_active = 'Y'
            ''', (rcm_id, user_id)).fetchone()
            
            if not existing:
                return jsonify({'success': False, 'message': '해당 사용자의 권한을 찾을 수 없습니다.'})
            
            # 사용자 정보 조회
            target_user = conn.execute(
                'SELECT user_name FROM sb_user WHERE user_id = ?', (user_id,)
            ).fetchone()
            
            if not target_user:
                return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'})
            
            # 권한 변경
            conn.execute('''
                UPDATE sb_user_rcm 
                SET permission_type = ?, granted_by = ?, granted_date = CURRENT_TIMESTAMP
                WHERE rcm_id = ? AND user_id = ? AND is_active = 'Y'
            ''', (permission_type, user_info['user_id'], rcm_id, user_id))
            conn.commit()
        
        permission_text = '관리자' if permission_type == 'admin' else '읽기'
        return jsonify({
            'success': True, 
            'message': f'{target_user["user_name"]} 사용자의 권한을 {permission_text} 권한으로 변경했습니다.'
        })
        
    except Exception as e:
        print(f"권한 변경 오류: {e}")
        return jsonify({'success': False, 'message': f'권한 변경 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/rcm/revoke_access', methods=['POST'])
@login_required
def admin_rcm_revoke_access():
    """사용자의 RCM 접근 권한 제거"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        rcm_id = request.form.get('rcm_id')
        user_id = request.form.get('user_id')
        
        if not all([rcm_id, user_id]):
            return jsonify({'success': False, 'message': '필수 정보가 누락되었습니다.'})
        
        rcm_id = int(rcm_id)
        user_id = int(user_id)
        
        with get_db() as conn:
            # 기존 권한 확인
            existing = conn.execute('''
                SELECT * FROM sb_user_rcm 
                WHERE rcm_id = ? AND user_id = ? AND is_active = 'Y'
            ''', (rcm_id, user_id)).fetchone()
            
            if not existing:
                return jsonify({'success': False, 'message': '해당 사용자의 권한을 찾을 수 없습니다.'})
            
            # 사용자 정보 조회
            target_user = conn.execute(
                'SELECT user_name FROM sb_user WHERE user_id = ?', (user_id,)
            ).fetchone()
            
            if not target_user:
                return jsonify({'success': False, 'message': '사용자를 찾을 수 없습니다.'})
            
            # 권한 제거 (is_active를 N으로 변경)
            conn.execute('''
                UPDATE sb_user_rcm 
                SET is_active = 'N', granted_by = ?, granted_date = CURRENT_TIMESTAMP
                WHERE rcm_id = ? AND user_id = ? AND is_active = 'Y'
            ''', (user_info['user_id'], rcm_id, user_id))
            conn.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{target_user["user_name"]} 사용자의 RCM 접근 권한을 제거했습니다.'
        })
        
    except Exception as e:
        print(f"권한 제거 오류: {e}")
        return jsonify({'success': False, 'message': f'권한 제거 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/rcm/delete', methods=['POST'])
@login_required
def admin_rcm_delete():
    """RCM 삭제 (소프트 삭제)"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        rcm_id = request.form.get('rcm_id')
        
        if not rcm_id:
            return jsonify({'success': False, 'message': 'RCM ID가 필요합니다.'})
        
        rcm_id = int(rcm_id)
        
        with get_db() as conn:
            # RCM 정보 조회
            rcm_info = conn.execute(
                'SELECT rcm_name FROM sb_rcm WHERE rcm_id = ? AND is_active = "Y"', (rcm_id,)
            ).fetchone()
            
            if not rcm_info:
                return jsonify({'success': False, 'message': 'RCM을 찾을 수 없습니다.'})
            
            # 소프트 삭제 (is_active를 N으로 변경)
            conn.execute(
                'UPDATE sb_rcm SET is_active = "N" WHERE rcm_id = ?', (rcm_id,)
            )
            
            # 관련 사용자 권한도 비활성화
            conn.execute(
                'UPDATE sb_user_rcm SET is_active = "N" WHERE rcm_id = ?', (rcm_id,)
            )
            
            conn.commit()
        
        return jsonify({
            'success': True, 
            'message': f'"{rcm_info["rcm_name"]}" RCM이 성공적으로 삭제되었습니다.'
        })
        
    except Exception as e:
        print(f"RCM 삭제 오류: {e}")
        return jsonify({'success': False, 'message': f'RCM 삭제 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/switch_user', methods=['POST'])
@login_required
def admin_switch_user():
    """관리자가 다른 사용자로 스위치"""
    user_info = get_user_info()
    if not user_info or user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'})
    
    try:
        target_user_id = request.form.get('target_user_id')
        
        if not target_user_id:
            return jsonify({'success': False, 'message': '대상 사용자 ID가 필요합니다.'})
        
        target_user_id = int(target_user_id)
        
        # 대상 사용자 정보 조회
        with get_db() as conn:
            target_user = conn.execute(
                'SELECT * FROM sb_user WHERE user_id = ? AND (effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP)',
                (target_user_id,)
            ).fetchone()
            
            if not target_user:
                return jsonify({'success': False, 'message': '대상 사용자를 찾을 수 없거나 비활성화된 사용자입니다.'})
        
        # 현재 관리자 정보를 original_admin_id로 백업
        session['original_admin_id'] = user_info['user_id']
        session['original_admin_info'] = user_info
        
        # SQLite Row 객체를 딕셔너리로 변환
        target_user_dict = dict(target_user)
        
        # 대상 사용자로 세션 변경
        session['user_id'] = target_user_dict['user_id']
        session['user_email'] = target_user_dict['user_email']
        session['user_info'] = {
            'user_id': target_user_dict['user_id'],
            'user_name': target_user_dict['user_name'],
            'user_email': target_user_dict['user_email'],
            'company_name': target_user_dict.get('company_name', ''),
            'phone_number': target_user_dict.get('phone_number', ''),
            'admin_flag': target_user_dict.get('admin_flag', 'N')
        }
        session['last_activity'] = datetime.now().isoformat()
        
        print(f"관리자 스위치: {user_info['user_email']} -> {target_user_dict['user_email']}")
        
        return jsonify({
            'success': True, 
            'message': f'{target_user_dict["user_name"]} 사용자로 스위치되었습니다.'
        })
        
    except Exception as e:
        print(f"사용자 스위치 오류: {e}")
        return jsonify({'success': False, 'message': f'사용자 스위치 중 오류가 발생했습니다: {str(e)}'})

@app.route('/admin/switch_back')
@login_required
def admin_switch_back():
    """관리자 계정으로 돌아가기"""
    if 'original_admin_id' not in session:
        flash('스위치 상태가 아닙니다.')
        return redirect(url_for('index'))
    
    try:
        # 원래 관리자 정보로 복구
        original_admin_info = session['original_admin_info']
        
        session['user_id'] = original_admin_info['user_id']
        session['user_email'] = original_admin_info['user_email']
        session['user_info'] = original_admin_info
        session['last_activity'] = datetime.now().isoformat()
        
        # 스위치 관련 세션 정보 삭제
        session.pop('original_admin_id', None)
        session.pop('original_admin_info', None)
        
        print(f"관리자 복귀: {original_admin_info['user_email']}")
        flash('관리자 계정으로 돌아왔습니다.')
        return redirect(url_for('admin_users'))
        
    except Exception as e:
        print(f"관리자 복귀 오류: {e}")
        session.clear()  # 오류 시 세션 초기화
        flash('오류가 발생하여 로그아웃됩니다.')
        return redirect(url_for('login'))

# === 사용자 전용 페이지 ===
@app.route('/user/rcm')
@login_required
def user_rcm():
    """사용자 RCM 조회 페이지 - link5로 리디렉션"""
    return redirect(url_for('link5.user_rcm'))

@app.route('/user/rcm/<int:rcm_id>/view')
@login_required
def user_rcm_view(rcm_id):
    """사용자 RCM 상세 보기 - link5로 리디렉션"""
    return redirect(url_for('link5.user_rcm_view', rcm_id=rcm_id))

@app.route('/user/design-evaluation')
@login_required
def user_design_evaluation():
    """설계평가 페이지 - link6으로 리디렉션"""
    return redirect(url_for('link6.user_design_evaluation'))

@app.route('/user/design-evaluation/rcm/<int:rcm_id>')
@login_required
def user_design_evaluation_rcm(rcm_id):
    """RCM 기반 설계평가 페이지 - link5로 리디렉션"""
    return redirect(url_for('link5.user_design_evaluation_rcm', rcm_id=rcm_id))

# 이 함수는 snowball_link6.py로 이전됨 - 전체 주석 처리
# @app.route('/api/design-evaluation/save', methods=['POST'])
# @login_required
# def save_design_evaluation_api():
#     """설계평가 결과 저장 API"""
#     user_info = get_user_info()
#     data = request.get_json()
#     
#     rcm_id = data.get('rcm_id')
#     control_code = data.get('control_code')
#     evaluation_data = data.get('evaluation_data')
#     evaluation_session = data.get('evaluation_session')  # 평가 세션명
#     
#     if not all([rcm_id, control_code, evaluation_data, evaluation_session]):
#         missing_fields = []
#         if not rcm_id: missing_fields.append('RCM ID')
#         if not control_code: missing_fields.append('통제 코드')
#         if not evaluation_data: missing_fields.append('평가 데이터')
#         if not evaluation_session: missing_fields.append('세션명')
#         
#         return jsonify({
#             'success': False,
#             'message': f'필수 데이터가 누락되었습니다: {", ".join(missing_fields)}'
#         })
#     
#     try:
#         # 사용자가 해당 RCM에 접근 권한이 있는지 확인
#         with get_db() as conn:
#             access_check = conn.execute('''
#                 SELECT permission_type FROM sb_user_rcm
#                 WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
#             ''', (user_info['user_id'], rcm_id)).fetchone()
#             
#             if not access_check:
#                 return jsonify({
#                     'success': False,
#                     'message': '해당 RCM에 대한 접근 권한이 없습니다.'
#                 })
#         
#         # 설계평가 결과 저장
#         save_design_evaluation(rcm_id, control_code, user_info['user_id'], evaluation_data, evaluation_session)
#         
#         # 활동 로그 기록
#         log_user_activity(user_info, 'DESIGN_EVALUATION', f'설계평가 저장 - {control_code}', 
#                          f'/api/design-evaluation/save', 
#                          request.remote_addr, request.headers.get('User-Agent'))
#         
#         return jsonify({
#             'success': True,
#             'message': '설계평가 결과가 저장되었습니다.'
#         })
#         
#     except Exception as e:
#         print(f"설계평가 저장 오류: {e}")
#         return jsonify({
#             'success': False,
#             'message': '저장 중 오류가 발생했습니다.'
#         })

# 이 함수도 snowball_link6.py로 이전됨 - 주석 처리
# @app.route('/api/design-evaluation/load/<int:rcm_id>')
# @login_required
# def load_design_evaluations_api(rcm_id):
#     """설계평가 결과 불러오기 API - link5로 리디렉션"""
#     return redirect(url_for('link5.load_design_evaluation', rcm_id=rcm_id))

# 이 함수도 snowball_link6.py로 이전됨 - 주석 처리
# @app.route('/api/design-evaluation/reset', methods=['POST'])
# @login_required
# def reset_design_evaluations_api():
#     """설계평가 결과 초기화 API"""
#     user_info = get_user_info()
#     data = request.get_json()
#     
#     rcm_id = data.get('rcm_id')
#     
#     if not rcm_id:
#         return jsonify({
#             'success': False,
#             'message': 'RCM ID가 누락되었습니다.'
#         })
#     
#     try:
#         # 사용자가 해당 RCM에 접근 권한이 있는지 확인
#         with get_db() as conn:
#             access_check = conn.execute('''
#                 SELECT permission_type FROM sb_user_rcm
#                 WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
#             ''', (user_info['user_id'], rcm_id)).fetchone()
#             
#             if not access_check:
#                 return jsonify({
#                     'success': False,
#                     'message': '해당 RCM에 대한 접근 권한이 없습니다.'
#                 })
#             
#             # 해당 사용자의 모든 설계평가 결과 삭제
#             cursor = conn.execute('''
#                 DELETE FROM sb_design_evaluation 
#                 WHERE rcm_id = ? AND user_id = ?
#             ''', (rcm_id, user_info['user_id']))
#             deleted_count = cursor.rowcount
#             
#             conn.commit()
#         
#         # 활동 로그 기록
#         log_user_activity(user_info, 'DESIGN_EVALUATION_RESET', f'설계평가 초기화 - RCM ID: {rcm_id}', 
#                          f'/api/design-evaluation/reset', 
#                          request.remote_addr, request.headers.get('User-Agent'))
#         
#         return jsonify({
#             'success': True,
#             'message': f'{deleted_count}개의 설계평가 결과가 초기화되었습니다.',
#             'deleted_count': deleted_count
#         })
#         
#     except Exception as e:
#         print(f"설계평가 초기화 오류: {e}")
#         return jsonify({
#             'success': False,
#             'message': '초기화 중 오류가 발생했습니다.'
#         })

@app.route('/api/control-sample/upload', methods=['POST'])
@login_required
def upload_control_sample():
    """통제별 샘플 파일 업로드 API"""
    user_info = get_user_info()
    
    rcm_id = request.form.get('rcm_id')
    control_code = request.form.get('control_code')
    description = request.form.get('description', '')
    
    if not all([rcm_id, control_code]):
        return jsonify({
            'success': False,
            'message': '필수 데이터가 누락되었습니다.'
        })
    
    if 'files' not in request.files:
        return jsonify({
            'success': False,
            'message': '업로드할 파일이 없습니다.'
        })
    
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({
            'success': False,
            'message': '업로드할 파일을 선택해주세요.'
        })
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인
        with get_db() as conn:
            access_check = conn.execute('''
                SELECT permission_type FROM sb_user_rcm
                WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
            ''', (user_info['user_id'], rcm_id)).fetchone()
            
            if not access_check:
                return jsonify({
                    'success': False,
                    'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                })
        
        # 업로드 디렉토리 생성
        import os
        upload_dir = f"uploads/rcm_{rcm_id}/control_{control_code}"
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        
        for file in files:
            if file and file.filename:
                # 안전한 파일명 생성
                import uuid
                from werkzeug.utils import secure_filename
                
                file_ext = os.path.splitext(file.filename)[1]
                safe_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, safe_filename)
                
                # 파일 저장
                file.save(file_path)
                
                # 데이터베이스에 파일 정보 저장
                with get_db() as conn:
                    conn.execute('''
                        INSERT INTO sb_control_sample_files
                        (rcm_id, control_code, user_id, original_filename, stored_filename, 
                         file_path, file_size, description, upload_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    ''', (rcm_id, control_code, user_info['user_id'], file.filename, 
                          safe_filename, file_path, os.path.getsize(file_path), description))
                    conn.commit()
                
                uploaded_files.append({
                    'original_name': file.filename,
                    'stored_name': safe_filename
                })
        
        # 활동 로그 기록
        log_user_activity(user_info, 'SAMPLE_UPLOAD', f'통제 샘플 업로드 - {control_code}', 
                         '/api/control-sample/upload', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)}개 파일이 업로드되었습니다.',
            'uploaded_files': uploaded_files
        })
        
    except Exception as e:
        print(f"샘플 업로드 오류: {e}")
        return jsonify({
            'success': False,
            'message': '업로드 중 오류가 발생했습니다.'
        })

@app.route('/user/operation-evaluation')
@login_required
def user_operation_evaluation():
    """운영평가 페이지 - link7로 리디렉션"""
    return redirect(url_for('link7.user_operation_evaluation'))

# === API 엔드포인트 ===
@app.route('/api/user/rcm-status')
@login_required
def api_user_rcm_status():
    """사용자 RCM 현황 조회 API"""
    from snowball_link5 import user_rcm_status
    return user_rcm_status()

@app.route('/api/user/rcm-list')
@login_required
def api_user_rcm_list():
    """사용자 RCM 목록 조회 API"""
    from snowball_link5 import user_rcm_list
    return user_rcm_list()



app.register_blueprint(bp_link5)
app.register_blueprint(bp_link6)
app.register_blueprint(bp_link7)
app.register_blueprint(bp_link8)

if __name__ == '__main__':
    main()