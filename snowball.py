from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from openpyxl import load_workbook
from snowball_link1 import bp_link1
from snowball_link2 import export_interview_excel_and_send, s_questions, question_count, is_ineffective, fill_sheet, link2_prev_logic, get_text_itgc, get_conditional_questions, clear_skipped_answers, get_progress_status, set_progress_status, update_progress, reset_progress
from snowball_link3 import bp_link3
from snowball_link4 import bp_link4
from snowball_link5 import bp_link5
from snowball_link6 import bp_link6
from snowball_link7 import bp_link7
from snowball_link8 import bp_link8
from snowball_link9 import bp_link9
from snowball_link10 import bp_link10
from snowball_admin import admin_bp
from auth import send_otp, verify_otp, login_required, get_current_user, get_db, log_user_activity, get_user_activity_logs, get_activity_log_count, check_ai_review_limit, increment_ai_review_count, get_ai_review_status, create_rcm, get_user_rcms, get_rcm_details, save_rcm_details, grant_rcm_access, get_all_rcms, save_design_evaluation, get_design_evaluations, save_operation_evaluation, get_operation_evaluations, find_user_by_email
from snowball_mail import get_gmail_credentials, send_gmail, send_gmail_with_attachment
from snowball_drive import append_to_work_log, get_work_log
import base64
import pickle
import os
import uuid
import json
import re

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', '150606')
# 세션 만료 시간 설정 (24시간으로 연장)
# 브라우저 종료시에만 세션 만료 (permanent session 사용하지 않음)

# 세션 보안 설정 - 환경에 따른 동적 설정
is_production = os.getenv('PYTHONANYWHERE_DOMAIN') is not None or 'pythonanywhere' in os.getenv('SERVER_NAME', '')
app.config.update(
    SESSION_COOKIE_SECURE=is_production,  # 운영환경(HTTPS)에서만 True
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    # 브라우저 종료 후에도 세션 유지되도록 설정
    SESSION_COOKIE_MAX_AGE=timedelta(hours=24).total_seconds(),  # 24시간
    # 템플릿 자동 리로드 설정 (개발 환경)
    TEMPLATES_AUTO_RELOAD=True
)

# Jinja2 템플릿 자동 리로드 강제 설정
app.jinja_env.auto_reload = True

print(f"세션 설정 - Production: {is_production}, Secure: {app.config['SESSION_COOKIE_SECURE']}")

# 앱 시작 시 기본 정보 출력
print(f"Flask 앱 시작 - Secret Key: {app.secret_key[:10]}...")
print(f"환경 변수(초기 로드 전) - PYTHONANYWHERE_AUTH_CODE: {os.getenv('PYTHONANYWHERE_AUTH_CODE', 'undefined')}")

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
print(f"환경 변수 - PYTHONANYWHERE_AUTH_CODE: {PYTHONANYWHERE_AUTH_CODE}")

# 데이터베이스 초기화
# 데이터베이스 초기화는 더 이상 서버 시작 시 자동 실행되지 않습니다.
# 마이그레이션 시스템을 사용하세요: python migrate.py upgrade
#
# try:
#     print("데이터베이스 초기화 시작")
#     with app.app_context():
#         init_db()
#     print("데이터베이스 초기화 완료")
# except Exception as e:
#     print(f"데이터베이스 초기화 오류: {e}")
#     import traceback
#     traceback.print_exc()

@app.context_processor
def inject_globals():
    """모든 템플릿에 전역 변수 주입"""
    return {
        'is_production': is_production
    }

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


@app.route('/')
def index():
    
    # 자동 로그인 로직 제거됨 (수동 로그인으로 변경)
    
    user_info = get_user_info()
    user_name = user_info['user_name'] if user_info else "Guest"
    
    # 로그인한 사용자만 활동 로그 기록
    host = request.headers.get('Host', '')
    # 로컬 환경에서는 로그인 로그 기록 안함
    if is_logged_in() and host.startswith('snowball.pythonanywhere.com'):
        log_user_activity(user_info, 'PAGE_ACCESS', '메인 페이지', '/',
                          request.remote_addr, request.headers.get('User-Agent'))

    # 카드 순서 정의 (Dashboard를 RCM 앞으로)
    card_order = ['dashboard', 'rcm', 'interview', 'design_evaluation', 'operation_evaluation']

    return render_template('index.jsp',
                         user_name=user_name, 
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         return_code=0, 
                         remote_addr=request.remote_addr,
                         card_order=card_order)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        from datetime import datetime  # datetime import 추가
        print("로그인 페이지 접근 시작")
        action = None
        if request.method == 'POST':
            action = request.form.get('action')
            print(f"POST 요청 액션: {action}")
        else:
            # GET 요청 시에는 액션 없음
            action = None
        
        if action == 'admin_login':
            # 관리자 로그인 (IP 제한 없음)
            client_ip = request.environ.get('REMOTE_ADDR', '')
            server_port = request.environ.get('SERVER_PORT', '')

            # IP 제한 제거 - 어느 주소에서든 관리자 로그인 가능
            if True:
                with get_db() as conn:
                    user = conn.execute(
                        'SELECT * FROM sb_user WHERE user_email = %s AND (effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP)',
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

                        print(f"관리자 로그인 성공: {user_dict['user_email']} (admin_flag: {user_dict.get('admin_flag', 'N')}) from {client_ip}:{server_port}")
                        return redirect(url_for('index'))
                    else:
                        return render_template('login.jsp', error="관리자 계정을 찾을 수 없습니다.", remote_addr=request.remote_addr)
        
        elif action == 'send_otp':
            # OTP 발송 요청 (이메일만 지원)
            email = request.form.get('email')
            host = request.headers.get('Host', '')

            if not email:
                return render_template('login.jsp', error="이메일을 입력해주세요.", remote_addr=request.remote_addr, show_direct_login=host.startswith('snowball.pythonanywhere.com'))

            # snowball.pythonanywhere.com에서는 실제 OTP 발송하지 않고 고정 메시지 표시
            if host.startswith('snowball.pythonanywhere.com'):
                print(f"운영서버 OTP 발송 요청 - Host: {host}, Email: {email}")

                # 사용자가 존재하는지만 확인
                user = find_user_by_email(email)
                print(f"사용자 존재 확인 결과: {user is not None}")

                if not user:
                    print(f"등록되지 않은 사용자: {email}")
                    return render_template('login.jsp', error="등록되지 않은 사용자입니다.", remote_addr=request.remote_addr, show_direct_login=True)

                print(f"세션에 login_email 저장: {email}")
                session['login_email'] = email
                return render_template('login.jsp', step='verify', email=email,
                                     message="인증 코드를 입력해주세요.",
                                     remote_addr=request.remote_addr,
                                     show_direct_login=True)
            else:
                # 일반적인 OTP 발송 (이메일만)
                success, message = send_otp(email, method='email')
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
            
            print(f"OTP 검증 시도 - Host: {host}, Session Email: {email}, Input OTP: {otp_code}")
            
            if not email or not otp_code:
                print(f"필수 정보 누락 - Email: {email}, OTP: {otp_code}")
                return render_template('login.jsp', error="인증 코드를 입력해주세요.", remote_addr=request.remote_addr)
            
            # snowball.pythonanywhere.com에서는 고정 코드 확인
            if host.startswith('snowball.pythonanywhere.com'):
                print(f"운영서버 로그인 시도 - Host: {host}, Email: {email}, OTP: {otp_code}, Expected: {PYTHONANYWHERE_AUTH_CODE}")
                
                if otp_code == PYTHONANYWHERE_AUTH_CODE:
                    # 사용자 정보 조회
                    user = find_user_by_email(email)
                    print(f"사용자 조회 결과: {user is not None}")
                    
                    if user:
                        print(f"사용자 정보: {user}")
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
                        try:
                            with get_db() as conn:
                                conn.execute(
                                    'UPDATE sb_user SET last_login_date = CURRENT_TIMESTAMP WHERE user_email = %s',
                                    (email,)
                                )
                                conn.commit()
                            print(f"로그인 날짜 업데이트 성공")
                        except Exception as e:
                            print(f"로그인 날짜 업데이트 실패: {e}")
                        
                        print(f"고정 코드 로그인 성공: {user['user_name']} ({user['user_email']}) from {host}")
                        return redirect(url_for('index'))
                    else:
                        print(f"사용자를 찾을 수 없음: {email}")
                        return render_template('login.jsp', step='verify', email=email, error="사용자 정보를 찾을 수 없습니다.", remote_addr=request.remote_addr, show_direct_login=True)
                else:
                    print(f"잘못된 인증 코드: 입력값={otp_code}, 기대값={PYTHONANYWHERE_AUTH_CODE}")
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
    
        # GET 혹은 액션 미지정 시 로그인 폼 표시
        print("GET/기본 로그인 폼 표시")
        host = request.headers.get('Host', '')
        show_direct_login = host.startswith('snowball.pythonanywhere.com')
        print(f"폼 렌더 - Host: {host}, show_direct_login: {show_direct_login}")
        return render_template('login.jsp', remote_addr=request.remote_addr, show_direct_login=show_direct_login)
        
    except Exception as e:
        print(f"로그인 페이지 오류: {e}")
        import traceback
        traceback.print_exc()
        return f"로그인 페이지 오류가 발생했습니다: {str(e)}", 500


@app.route('/logout')
def logout():
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


@app.route('/health')
def health_check():
    """서버 상태 확인"""
    try:
        return {
            'status': 'ok', 
            'host': request.headers.get('Host', ''),
            'remote_addr': request.remote_addr,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """브라우저 종료 시 세션 해제 엔드포인트"""
    if 'user_id' in session:
        user_name = session.get('user_name', 'Unknown')
        session.clear()
        print(f"브라우저 종료로 세션 해제: {user_name}")
    return '', 204

def main():
    app.run(host='0.0.0.0', debug=False, port=5001, use_reloader=False)
    #app.run(host='127.0.0.1', debug=False, port=8001)

@app.route('/link0')   
def link0():
    print("Reload")
    return render_template('link0.jsp')

@app.route('/proposal')
def proposal():
    """Snowball 제안서 페이지"""
    return render_template('proposal.jsp')

# link1 라우트는 bp_link1 Blueprint로 이동됨

@app.route('/link2', methods=['GET', 'POST'])
def link2():
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

# link3 라우트는 bp_link3 Blueprint로 이동됨

# link4 라우트는 bp_link4 Blueprint로 이동됨

def sanitize_text(text, allow_newlines=False):
    """텍스트 입력값 정제"""
    if not text:
        return ""
    text = text.strip()
    if not allow_newlines:
        text = text.replace('\r', '').replace('\n', ' ')
    return text[:5000]

def is_valid_email(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# rcm_generate 라우트는 bp_link1 Blueprint로 이동됨

@app.route('/paper_request', methods=['POST'])
def paper_request():
    """
    Deprecated: 이 라우트는 더 이상 사용되지 않습니다.
    기존 코드와의 호환성을 위해 유지되고 있습니다.
    """
    print("Paper Request called (Deprecated)")
    print("Warning: /paper_request is deprecated and should not be used")

    # Link2로 리다이렉트
    return redirect(url_for('link2'))

# paper_template_download 라우트는 bp_link3 Blueprint로 이동됨
# paper_generate 라우트는 제거됨 (사용되지 않음)

# get_content_link3 라우트는 bp_link3 Blueprint로 이동됨
# get_content_link4 라우트는 bp_link4 Blueprint로 이동됨

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

@app.route('/update_session_email', methods=['POST'])
def update_session_email():
    """세션의 이메일 주소 업데이트"""
    try:
        data = request.get_json()
        new_email = data.get('email', '').strip()
        
        if not new_email:
            return jsonify({'success': False, 'message': '이메일 주소가 비어있습니다.'})
        
        # 이메일 유효성 검사 (서버 측)
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, new_email):
            return jsonify({'success': False, 'message': '올바른 이메일 형식이 아닙니다.'})
        
        # 세션의 answer 배열 첫 번째 요소(이메일) 업데이트
        if 'answer' in session:
            session['answer'][0] = new_email
            session.modified = True  # 세션이 수정되었음을 명시
        else:
            return jsonify({'success': False, 'message': '세션 정보를 찾을 수 없습니다.'})
        
        print(f"이메일 업데이트 완료: {new_email}")
        return jsonify({'success': True, 'message': '이메일이 성공적으로 변경되었습니다.'})
        
    except Exception as e:
        print(f"이메일 업데이트 오류: {e}")
        return jsonify({'success': False, 'message': '서버 오류가 발생했습니다.'})

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
def user_rcm_view_old(rcm_id):
    """사용자 RCM 상세 보기 - 구버전 호환용 (세션에 저장 후 리다이렉트)"""
    return redirect(url_for('link5.select_rcm', rcm_id=rcm_id))

@app.route('/user/rcm/view')
@login_required
def user_rcm_view():
    """사용자 RCM 상세 보기 - link5로 리다이렉션"""
    return redirect(url_for('link5.user_rcm_view'))

@app.route('/user/design-evaluation', methods=['GET', 'POST'])
@login_required
def user_design_evaluation():
    """설계평가 페이지 - 세션에 데이터 저장 후 설계평가 작업 페이지로 리디렉트"""
    if request.method == 'POST':
        # POST로 받은 데이터를 세션에 저장
        rcm_id = request.form.get('rcm_id')
        evaluation_session = request.form.get('session')

        if rcm_id and evaluation_session:
            # 세션에 저장 (설계평가 작업 페이지에서 사용)
            session['current_design_rcm_id'] = int(rcm_id)
            session['current_evaluation_session'] = evaluation_session

            # RCM 정보 조회하여 카테고리 확인
            with get_db() as conn:
                rcm = conn.execute("SELECT control_category FROM sb_rcm WHERE rcm_id = ?", (rcm_id,)).fetchone()

            if rcm:
                category = rcm['control_category']
                session['current_evaluation_type'] = category

            # 설계평가 작업 페이지로 리디렉트
            return redirect(url_for('link6.user_design_evaluation_rcm'))

        flash('잘못된 요청입니다.', 'danger')
        return redirect(url_for('link8.internal_assessment'))
    else:
        # GET 요청 - 레거시 지원
        return redirect(url_for('link6.itgc_evaluation'))

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
#                 WHERE user_id = %s AND rcm_id = %s AND is_active = 'Y'
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
#                 WHERE user_id = %s AND rcm_id = %s AND is_active = 'Y'
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
#                 WHERE rcm_id = %s AND user_id = %s
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
                WHERE user_id = %s AND rcm_id = %s AND is_active = 'Y'
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
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, datetime('now'))
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

@app.route('/user/operation-evaluation', methods=['GET', 'POST'])
@login_required
def user_operation_evaluation():
    """운영평가 페이지 - 세션에 데이터 저장 후 운영평가 작업 페이지로 리디렉트"""
    if request.method == 'POST':
        # POST로 받은 데이터를 세션에 저장
        rcm_id = request.form.get('rcm_id')
        evaluation_session = request.form.get('session')

        if rcm_id and evaluation_session:
            # 세션에 저장 (운영평가 페이지에서 사용)
            session['current_operation_rcm_id'] = int(rcm_id)
            session['current_design_evaluation_session'] = evaluation_session
            session['redirect_to_operation'] = True

            # 운영평가 작업 페이지로 리디렉트
            return redirect(url_for('link7.user_operation_evaluation_rcm'))

        flash('잘못된 요청입니다.', 'danger')
        return redirect(url_for('link8.internal_assessment'))
    else:
        # GET 요청 - 레거시 지원
        return redirect(url_for('link7.user_operation_evaluation'))

@app.route('/user/internal-assessment')
@login_required
def user_internal_assessment():
    """내부평가 페이지 - link8로 리디렉션"""
    return redirect(url_for('link8.internal_assessment'))

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

@app.route('/api/rcm/update_controls', methods=['POST'])
@login_required
def api_rcm_update_controls():
    """RCM 통제 정보 업데이트 API (인라인 편집)"""
    user_info = get_current_user()

    try:
        data = request.get_json()
        updates = data.get('updates', [])

        if not updates:
            return jsonify({'success': False, 'message': '업데이트할 데이터가 없습니다.'}), 400

        with get_db() as conn: # with 문으로 DB 연결을 안전하게 관리
            updated_count = 0

            # 각 통제에 대해 업데이트 수행
            for update in updates:
                detail_id = update.get('detail_id')
                fields = update.get('fields', {})

                if not detail_id or not fields:
                    continue

                # 해당 통제가 속한 RCM에 대한 접근 권한 확인
                rcm_check_result = conn.execute('''
                    SELECT rcm_id FROM sb_rcm_detail WHERE detail_id = %s
                ''', (detail_id,)).fetchone()

                if not rcm_check_result:
                    continue

                rcm_id = rcm_check_result['rcm_id']

                # 권한 확인 로직을 반복문 안으로 이동
                access = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE rcm_id = %s AND user_id = %s
                ''', (rcm_id, user_info['user_id'])).fetchone()

                # admin 또는 edit 권한이 있는지 확인
                if not access or access['permission_type'] not in ('admin', 'edit'):
                    continue

                # 허용된 필드만 업데이트 (통제코드와 통제명은 제외)
                allowed_fields = [
                    'control_description', 'key_control', 'control_frequency',
                    'control_type', 'control_nature', 'process_area',
                    'risk_description', 'risk_impact', 'risk_likelihood', 'population',
                    'population_completeness_check', 'population_count', 'test_procedure',
                    'control_owner', 'control_performer', 'evidence_type',
                    'recommended_sample_size'  # 권장 표본수 필드 추가
                ]

                # SQL UPDATE 문 생성
                update_fields = []
                update_values = []

                for field, value in fields.items():
                    if field in allowed_fields:
                        update_fields.append(f"{field} = %s")
                        update_values.append(value if value else None)

                if update_fields:
                    update_values.append(detail_id)
                    sql = f"UPDATE sb_rcm_detail SET {', '.join(update_fields)} WHERE detail_id = %s"
                    conn.execute(sql, update_values)
                    updated_count += 1

            # 모든 업데이트가 끝난 후 한 번만 커밋

        return jsonify({
            'success': True,
            'message': f'{updated_count}개 통제 정보가 업데이트되었습니다.',
            'updated_count': updated_count
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'업데이트 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/work-log', methods=['GET', 'POST'])
@login_required
def work_log_api():
    """작업 로그 API - Google Drive에 저장"""
    user_info = get_user_info()

    if request.method == 'POST':
        # 작업 로그 추가
        data = request.get_json()
        log_entry = data.get('log_entry', '')

        if not log_entry:
            return jsonify({
                'success': False,
                'message': '로그 내용이 비어있습니다.'
            })

        # 사용자 정보와 함께 로그 작성
        result = append_to_work_log(
            log_entry=log_entry,
            user_name=user_info.get('user_name', ''),
            user_email=user_info.get('user_email', '')
        )

        # 활동 로그 기록
        if result['success']:
            log_user_activity(user_info, 'WORK_LOG', '작업 로그 작성', '/api/work-log',
                            request.remote_addr, request.headers.get('User-Agent'))

        return jsonify(result)

    else:
        # 작업 로그 조회
        result = get_work_log()

        if result['success']:
            log_user_activity(user_info, 'WORK_LOG_VIEW', '작업 로그 조회', '/api/work-log',
                            request.remote_addr, request.headers.get('User-Agent'))

        return jsonify(result)

@app.route('/api/check-operation-evaluation/<control_type>')
@login_required
def check_operation_evaluation(control_type):
    """진행 중인 운영평가가 있는지 확인하는 API

    Args:
        control_type: ELC, TLC, ITGC 중 하나

    Returns:
        JSON: {
            "has_operation_evaluation": true/false,
            "evaluation_sessions": [...] (있는 경우)
        }
    """
    user_info = get_current_user()

    with get_db() as conn:
        # 특정 control_type의 RCM에 대한 운영평가 헤더 조회
        # sb_rcm.control_category로 필터링 (훨씬 간단!)
        headers = conn.execute('''
            SELECT DISTINCT
                oeh.evaluation_session,
                oeh.design_evaluation_session,
                oeh.rcm_id,
                r.rcm_name,
                r.control_category
            FROM sb_evaluation_header oeh
            JOIN sb_rcm r ON oeh.rcm_id = r.rcm_id
            WHERE oeh.user_id = %s
              AND r.control_category = %s
            ORDER BY oeh.evaluation_session DESC
        ''', (user_info['user_id'], control_type.upper())).fetchall()

        evaluation_sessions = []
        for header in headers:
            evaluation_sessions.append({
                "rcm_id": header['rcm_id'],
                "rcm_name": header['rcm_name'],
                "evaluation_session": header['evaluation_session'],
                "design_evaluation_session": header['design_evaluation_session']
            })

        return jsonify({
            "has_operation_evaluation": len(evaluation_sessions) > 0,
            "evaluation_sessions": evaluation_sessions,
            "control_type": control_type.upper()
        })


app.register_blueprint(bp_link1)
app.register_blueprint(bp_link3)
app.register_blueprint(bp_link4)
app.register_blueprint(bp_link5)
app.register_blueprint(bp_link6)
app.register_blueprint(bp_link7)
app.register_blueprint(bp_link8)
app.register_blueprint(bp_link9)
app.register_blueprint(bp_link10)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    main()