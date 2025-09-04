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
from snowball_link2 import export_interview_excel_and_send, s_questions, question_count, is_ineffective, fill_sheet, link2_prev_logic, get_text_itgc, get_conditional_questions, clear_skipped_answers, get_progress_status, set_progress_status, update_progress, reset_progress
from snowball_link4 import get_link4_content
from snowball_mail import get_gmail_credentials, send_gmail, send_gmail_with_attachment
from snowball_link5 import bp_link5
from snowball_link6 import bp_link6
from snowball_link7 import bp_link7
from snowball_link8 import bp_link8
from snowball_admin import admin_bp
from auth import init_db, send_otp, verify_otp, login_required, get_current_user, get_db, log_user_activity, get_user_activity_logs, get_activity_log_count, check_ai_review_limit, increment_ai_review_count, get_ai_review_status, create_rcm, get_user_rcms, get_rcm_details, save_rcm_details, grant_rcm_access, get_all_rcms, save_design_evaluation, get_design_evaluations, save_operation_evaluation, get_operation_evaluations, find_user_by_email
import uuid
import json
import re


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', '150606')

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
# 진행률 관련 기능은 snowball_link2.py로 이동됨

# 시작할 질문 번호 설정 (1부터 시작)
if __name__ == '__main__':
    START_QUESTION = 0
else:
    START_QUESTION = 0

load_dotenv()

# 보안 관련 상수 (환경변수에서 로드)
PYTHONANYWHERE_AUTH_CODE = os.getenv('PYTHONANYWHERE_AUTH_CODE', '150606')

# 데이터베이스 초기화
with app.app_context():
    init_db()

@app.before_request
def before_request():
    """모든 요청 전에 실행되는 함수"""
    # 필요시 추가 처리를 위한 함수
    pass

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
    
    # 개발 단계: 127.0.0.1:5001 접속시 자동 로그인 (Snowball 계정)
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
            host = request.headers.get('Host', '')
            
            if not email:
                return render_template('login.jsp', error="이메일을 입력해주세요.", remote_addr=request.remote_addr, show_direct_login=host.startswith('snowball.pythonanywhere.com'))
            
            # snowball.pythonanywhere.com에서는 실제 OTP 발송하지 않고 고정 메시지 표시
            if host.startswith('snowball.pythonanywhere.com'):
                # 사용자가 존재하는지만 확인
                user = find_user_by_email(email)
                if not user:
                    return render_template('login.jsp', error="등록되지 않은 사용자입니다.", remote_addr=request.remote_addr, show_direct_login=True)
                
                session['login_email'] = email
                return render_template('login.jsp', step='verify', email=email, 
                                     message="인증 코드를 입력해주세요.", 
                                     remote_addr=request.remote_addr, 
                                     show_direct_login=True)
            else:
                # 일반적인 OTP 발송
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
            host = request.headers.get('Host', '')
            
            if not email or not otp_code:
                return render_template('login.jsp', error="인증 코드를 입력해주세요.", remote_addr=request.remote_addr)
            
            # snowball.pythonanywhere.com에서는 고정 코드 확인
            if host.startswith('snowball.pythonanywhere.com'):
                if otp_code == PYTHONANYWHERE_AUTH_CODE:
                    # 사용자 정보 조회
                    user = find_user_by_email(email)
                    if user:
                        # 로그인 성공
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
                        session['last_activity'] = datetime.now().isoformat()
                        session.pop('login_email', None)  # 임시 이메일 정보 삭제
                        
                        # 마지막 로그인 날짜 업데이트
                        with get_db() as conn:
                            conn.execute(
                                'UPDATE sb_user SET last_login_date = CURRENT_TIMESTAMP WHERE user_email = ?',
                                (email,)
                            )
                            conn.commit()
                        
                        print(f"고정 코드 로그인 성공: {user['user_name']} ({user['user_email']}) from {host}")
                        return redirect(url_for('index'))
                    else:
                        return render_template('login.jsp', step='verify', email=email, error="사용자 정보를 찾을 수 없습니다.", remote_addr=request.remote_addr, show_direct_login=True)
                else:
                    return render_template('login.jsp', step='verify', email=email, error="잘못된 인증 코드입니다.", remote_addr=request.remote_addr, show_direct_login=True)
            else:
                # 일반적인 OTP 검증
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
    
    # GET 요청 시 현재 호스트 확인하여 로그인 폼 표시
    host = request.headers.get('Host', '')
    show_direct_login = host.startswith('snowball.pythonanywhere.com')
    
    return render_template('login.jsp', remote_addr=request.remote_addr, show_direct_login=show_direct_login)


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


# 관리자 기능들이 제거됨


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
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    main()