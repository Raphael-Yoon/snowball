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
from snowball_link2 import export_interview_excel_and_send, s_questions, question_count, is_ineffective, fill_sheet, link2_prev_logic, get_text_itgc
from snowball_link4 import get_link4_content
from snowball_mail import get_gmail_credentials, send_gmail, send_gmail_with_attachment
from snowball_link5 import bp_link5
from snowball_link6 import bp_link6
from auth import init_db, send_otp, verify_otp, login_required, get_current_user
import uuid
import json

app = Flask(__name__)
app.secret_key = '150606'

# 세션 만료 시간 설정 (10분)
app.permanent_session_lifetime = timedelta(minutes=10)

# 세션 보안 설정
app.config.update(
    SESSION_COOKIE_SECURE=False,  # HTTPS 환경에서는 True로 설정
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
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
        
        session.permanent = True
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
    user_info = get_user_info()
    user_name = user_info['user_name'] if user_info else "Guest"
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
                session.permanent = True  # 영구 세션 설정
                session['user_id'] = user['user_id']
                session['user_name'] = user['user_name']
                session['user_info'] = {
                    'user_id': user['user_id'],
                    'user_name': user['user_name'],
                    'user_email': user['user_email'],
                    'company_name': user.get('company_name', ''),
                    'phone_number': user.get('phone_number', '')
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
        session.permanent = True
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
        return render_template('link2.jsp',
                             question=s_questions[session['question_index']],
                             question_count=question_count,
                             current_index=session['question_index'],
                             remote_addr=request.remote_addr,
                             users=users,
                             is_logged_in=is_logged_in(),
                             user_info=user_info,
                             answer=session['answer'],
                             textarea_answer=session['textarea_answer'])

    question_index = session['question_index']

    if request.method == 'POST':
        form_data = request.form
        session['answer'][question_index] = form_data.get(f"a{question_index}", '')
        session['textarea_answer'][question_index] = form_data.get(f"a{question_index}_1", '')
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

        # 다음 질문 인덱스를 결정하는 매핑
        next_question = {i: i + 1 for i in range(43)}
        conditional_routes = {
            4: 5 if session['answer'][question_index] == 'Y' else 7,
            3: 4 if session['answer'][question_index] == 'Y' else 4
        }
        next_question.update(conditional_routes)

        # 마지막 질문 제출 시 AI 검토 선택 페이지로 이동
        if question_index == question_count - 1:
            print('interview completed - redirecting to AI review selection page')
            print('--- 모든 답변(answers) ---')
            for idx, ans in enumerate(session.get('answer', [])):
                print(f"a{idx}: {ans}")
            print('--- 모든 textarea 답변(textarea_answer) ---')
            for idx, ans in enumerate(session.get('textarea_answer', [])):
                print(f"a{idx}_1: {ans}")

            # AI 검토 선택 페이지로 리디렉션
            return redirect(url_for('ai_review_selection'))

        session['question_index'] = next_question.get(question_index, question_index)
        print(f"goto {session['question_index']}")
        print("Answers:", ", ".join(f"{i}: {ans}" for i, ans in enumerate(session['answer'])))
        print(f"입력받은 값(a{question_index}): {session['answer'][question_index]}")
        print(f"textarea 값(a{question_index}_1): {session['textarea_answer'][question_index]}")

        if session['question_index'] >= question_count:
            # 마지막 질문 이후에는 save_to_excel 호출하지 않음
            return redirect(url_for('index'))

    # 현재 질문을 렌더링
    question = s_questions[session['question_index']]
    user_info = get_user_info()
    users = user_info['user_name'] if user_info else "User List"
    return render_template(
        'link2.jsp',
        question=question,
        question_count=question_count,
        current_index=session['question_index'],
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
    # AI 검토 기능 활성화 (환경변수로 제어 가능)
    enable_ai_review = os.getenv('ENABLE_AI_REVIEW', 'false').lower() == 'true'

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
    return render_template('link3.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
                         remote_addr=request.remote_addr)

@app.route('/link4')
def link4():
    log_session_info("영상자료 페이지")
    print("Video Function")
    return render_template('link4.jsp', 
                         is_logged_in=is_logged_in(),
                         user_info=get_user_info(),
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
    return render_template('link2_ai_review.jsp', 
                         user_email=user_email,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@app.route('/process_with_ai_option', methods=['POST'])
def process_with_ai_option():
    """AI 검토 옵션에 따라 처리 페이지로 이동"""
    enable_ai_review = request.form.get('enable_ai_review', 'false').lower() == 'true'
    
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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # 로그인 상태 확인
    is_logged_in = 'user_id' in session
    user_info = session.get('user_info', {})
    
    if request.method == 'POST':
        print("[1] Contact 폼 제출됨")
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"[2] 폼 데이터 파싱 완료: name={name}, email={email}")

        subject = f'Contact Us 문의: {name}'
        body = f'이름: {name}\n이메일: {email}\n문의내용:\n{message}'
        try:
            send_gmail(
                to='snowball1566@gmail.com',
                subject=subject,
                body=body
            )
            print("[6] 메일 전송 성공")
            return render_template('contact.jsp', success=True, remote_addr=request.remote_addr,
                                 is_logged_in=is_logged_in, user_info=user_info)
        except Exception as e:
            print(f"[!] 문의 메일 전송 실패: {e}")
            return render_template('contact.jsp', success=False, error=str(e), remote_addr=request.remote_addr,
                                 is_logged_in=is_logged_in, user_info=user_info)
    print("[0] Contact 폼 GET 요청")
    return render_template('contact.jsp', remote_addr=request.remote_addr,
                         is_logged_in=is_logged_in, user_info=user_info)

@app.route('/service_inquiry', methods=['POST'])
def service_inquiry():
    try:
        company_name = request.form.get('company_name')
        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        
        print(f"[서비스 문의] 회사명: {company_name}, 담당자: {contact_name}, 이메일: {contact_email}")
        
        subject = f'SnowBall 서비스 가입 문의: {company_name}'
        body = f'''SnowBall 서비스 가입 문의가 접수되었습니다.

회사명: {company_name}
담당자명: {contact_name}
이메일: {contact_email}

내부통제 평가 및 ITGC 관련 서비스에 관심을 보여주셔서 감사합니다.
빠른 시일 내에 담당자가 연락드리겠습니다.'''
        
        send_gmail(
            to='snowball1566@gmail.com',
            subject=subject,
            body=body
        )
        
        # 성공 메시지를 포함하여 로그인 페이지로 리다이렉트
        return render_template('login.jsp', 
                             service_inquiry_success=True,
                             remote_addr=request.remote_addr)
    except Exception as e:
        print(f"[!] 서비스 문의 메일 전송 실패: {e}")
        return render_template('login.jsp', 
                             service_inquiry_error=str(e),
                             remote_addr=request.remote_addr)



app.register_blueprint(bp_link5)
app.register_blueprint(bp_link6)

if __name__ == '__main__':
    main()
# 강제수정1