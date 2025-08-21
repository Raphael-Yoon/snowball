from flask import Flask, render_template, request, send_file, redirect, url_for, session, jsonify
import os
from datetime import datetime
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
from snowball_link2 import export_interview_excel_and_send, s_questions, question_count, is_ineffective, fill_sheet, link2_prev_logic, get_text_itgc, ai_improve_answer_consistency
from snowball_link4 import get_link4_content
from snowball_mail import get_gmail_credentials, send_gmail, send_gmail_with_attachment
from snowball_link5 import bp_link5
from snowball_link6 import bp_link6

app = Flask(__name__)
app.secret_key = '150606'

# 전역 진행률 상태 관리 (세션 기반으로 변경)
# 서버 환경에서 다중 프로세스 문제 해결을 위해 세션에 저장
def get_progress_status():
    if 'progress_status' not in session:
        session['progress_status'] = {
            'percentage': 0,
            'current_task': 'AI 검토를 준비하고 있습니다...',
            'is_processing': False
        }
    return session['progress_status']

def set_progress_status(status):
    session['progress_status'] = status

# 시작할 질문 번호 설정 (1부터 시작)
if __name__ == '__main__':
    START_QUESTION = 0
else:
    START_QUESTION = 0

load_dotenv()

def update_progress(percentage, task_description):
    """진행률 업데이트 함수"""
    progress_status = get_progress_status()
    progress_status['percentage'] = percentage
    progress_status['current_task'] = task_description
    progress_status['is_processing'] = True
    set_progress_status(progress_status)
    print(f"Progress: {percentage}% - {task_description}")

def reset_progress():
    """진행률 초기화 함수"""
    progress_status = {
        'percentage': 0,
        'current_task': 'AI 검토를 준비하고 있습니다...',
        'is_processing': False
    }
    set_progress_status(progress_status)

@app.route('/')
def index():
    result = "User List" # Placeholder for user list
    return render_template('index.jsp', user_name=result, return_code=0, remote_addr=request.remote_addr)


def main():
    app.run(host='0.0.0.0', debug=False, port=5001)
    #app.run(host='127.0.0.1', debug=False, port=8001)

@app.route('/link0')
def link0():
    print("Reload")
    return render_template('link0.jsp')

@app.route('/link1')
def link1():
    print("RCM Function")
    users = "User List" # Placeholder for user list
    return render_template('link1.jsp', return_code=0, users=users, remote_addr=request.remote_addr)

# Answer Type: 0: 리스트박스, 1: Y/N, 2: Textbox, 3: Y/N-Textbox, 4: Y/N-Textarea, 5: Textarea
# 기존 s_questions, question_count 정의 부분은 삭제

@app.route('/link2', methods=['GET', 'POST'])
def link2():
    print("Interview Function")

    if request.method == 'GET':
        # 쿼리 파라미터로 reset이 있을 때만 세션 초기화
        if request.args.get('reset') == '1':
            session.clear()
            # START_QUESTION이 유효한 범위인지 확인
            if 1 <= START_QUESTION <= question_count:
                session['question_index'] = START_QUESTION - 1  # 1-based를 0-based로 변환
            else:
                session['question_index'] = 0
            session['answer'] = [''] * question_count  # 필요한 만큼 동적으로 조절 가능
            session['textarea_answer'] = [''] * question_count  # textarea 값 저장용
        # 세션에 값이 없으면(최초 진입)만 초기화
        elif 'question_index' not in session:
            session['question_index'] = 0
            session['answer'] = [''] * question_count
            session['textarea_answer'] = [''] * question_count

        users = "User List" # Placeholder for user list
        return render_template('link2.jsp',
                             question=s_questions[session['question_index']],
                             question_count=question_count,
                             current_index=session['question_index'],
                             remote_addr=request.remote_addr,
                             users=users,
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
            3: 4 if session['answer'][question_index] == 'Y' else 6
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
    return render_template(
        'link2.jsp',
        question=question,
        question_count=question_count,
        current_index=session['question_index'],
        remote_addr=request.remote_addr,
        users="User List", # Placeholder for user list
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
    print("Paper Function")
    return render_template('link3.jsp', remote_addr=request.remote_addr)

@app.route('/link4')
def link4():
    print("Video Function")
    return render_template('link4.jsp', remote_addr=request.remote_addr)

@app.route('/link5', methods=['GET'])
def link5():
    return render_template('link5.jsp', remote_addr=request.remote_addr)

@app.route('/link6', methods=['GET'])
def link6():
    return render_template('link6.jsp', remote_addr=request.remote_addr)

@app.route('/link9')
def link9():
    print("ETC Function")
    return render_template('link9.jsp', remote_addr=request.remote_addr)

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
    return render_template('link2.jsp', return_code = 2)

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
    return render_template('link2_ai_review.jsp', user_email=user_email)

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
    reset_progress()  # 진행률 초기화
    return render_template('processing.jsp', user_email=user_email, enable_ai_review=enable_ai_review)

@app.route('/get_progress')
def get_progress():
    """진행률 상태 조회 엔드포인트"""
    progress_status = get_progress_status()
    return jsonify(progress_status)

@app.route('/process_interview', methods=['POST'])
def process_interview():
    """실제 인터뷰 처리 및 메일 발송"""
    try:
        # 세션 기반 진행률 관리로 변경
        progress_status = get_progress_status()
        progress_status['is_processing'] = True
        set_progress_status(progress_status)
        update_progress(5, "인터뷰 데이터를 확인하고 있습니다...")
        
        # 세션에서 답변 데이터 가져오기
        answers = session.get('answer', [])
        textarea_answers = session.get('textarea_answer', [])
        
        if not answers:
            reset_progress()
            return jsonify({'success': False, 'error': '인터뷰 데이터가 없습니다.'})
        
        user_email = answers[0] if answers else ''
        if not user_email:
            reset_progress()
            return jsonify({'success': False, 'error': '메일 주소가 입력되지 않았습니다.'})
        
        update_progress(10, "AI 검토 설정을 확인하고 있습니다...")
        
        # 사용자가 선택한 AI 검토 옵션 사용
        enable_ai_review = session.get('enable_ai_review', False)
        
        print(f"Processing interview for {user_email}")
        update_progress(15, "ITGC 설계평가 문서 생성을 시작합니다...")
        
        # 메일 발송 처리
        success, returned_email, error = export_interview_excel_and_send(
            answers,
            textarea_answers,
            get_text_itgc,
            fill_sheet,
            is_ineffective,
            send_gmail_with_attachment,
            enable_ai_review,
            update_progress  # 진행률 업데이트 함수 전달
        )
        
        if success:
            update_progress(100, "처리가 완료되었습니다!")
            progress_status = get_progress_status()
            progress_status['is_processing'] = False
            set_progress_status(progress_status)
            print(f"Mail sent successfully to {returned_email}")
            return jsonify({'success': True, 'email': returned_email})
        else:
            reset_progress()
            print(f"Mail send failed: {error}")
            return jsonify({'success': False, 'error': error})
            
    except Exception as e:
        reset_progress()
        print(f"Error in process_interview: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/contact', methods=['GET', 'POST'])
def contact():
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
            return render_template('contact.jsp', success=True, remote_addr=request.remote_addr)
        except Exception as e:
            print(f"[!] 문의 메일 전송 실패: {e}")
            return render_template('contact.jsp', success=False, error=str(e), remote_addr=request.remote_addr)
    print("[0] Contact 폼 GET 요청")
    return render_template('contact.jsp', remote_addr=request.remote_addr)


@app.route('/check_consistency', methods=['POST'])
def check_consistency():
    """답변들의 일관성을 체크합니다."""
    try:
        data = request.get_json()
        answers = data.get('answers', [])
        textarea_answers = data.get('textarea_answers', [])
        
        result = ai_improve_answer_consistency(answers, textarea_answers)
        return jsonify(result)
        
    except Exception as e:
        print(f"일관성 체크 API 오류: {e}")
        return jsonify({
            'ai_consistency_check': f'일관성 체크 중 오류가 발생했습니다: {str(e)}',
            'basic_consistency_issues': []
        })

app.register_blueprint(bp_link5)
app.register_blueprint(bp_link6)

if __name__ == '__main__':
    main()