from flask import Flask, render_template, request, send_file, redirect, url_for, session
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
from snowball_link2 import export_interview_excel_and_send, s_questions, question_count

app = Flask(__name__)
app.secret_key = '150606' 

# 시작할 질문 번호 설정 (1부터 시작)
if __name__ == '__main__':
    START_QUESTION = 0
else:
    START_QUESTION = 0

load_dotenv()

@app.route('/')
def index():
    result = "User List" # Placeholder for user list
    return render_template('index.jsp', user_name = result, return_code=0)

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
    return render_template('link1.jsp', return_code=0, users=users)

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

        # 마지막 질문 제출 시에만 save_to_excel 호출(메일 전송)
        if question_index == question_count - 1:
            print('excel download')
            print('--- 모든 답변(answers) ---')
            for idx, ans in enumerate(session.get('answer', [])):
                print(f"a{idx}: {ans}")
            print('--- 모든 textarea 답변(textarea_answer) ---')
            for idx, ans in enumerate(session.get('textarea_answer', [])):
                print(f"a{idx}_1: {ans}")
            return save_to_excel()

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
    # 세션에서 현재 인덱스 가져오기
    question_index = session.get('question_index', 0)
    # 0보다 크면 1 감소
    if question_index > 0:
        session['question_index'] = question_index - 1
    # 다시 질문 페이지로 이동
    return redirect(url_for('link2'))

# --- 리팩토링: Ineffective 조건 체크 함수 ---
def is_ineffective(control, answers):
    conditions = {
        'APD01': len(answers) > 14 and (answers[12] == 'N' or answers[14] == 'N'),
        'APD02': len(answers) > 15 and answers[15] == 'N',
        'APD03': len(answers) > 16 and answers[16] == 'N',
        'APD04': len(answers) > 17 and answers[17] == 'N',
        'APD06': len(answers) > 20 and (answers[19] == 'N' or answers[20] == 'N'),
        'APD07': len(answers) > 22 and (answers[21] == 'N' or answers[22] == 'N'),
        'APD10': len(answers) > 26 and (answers[25] == 'N' or answers[26] == 'N'),
        'PC01': (len(answers) > 30 and answers[29] == 'N') or (len(answers) > 30 and answers[30] == 'N'),
        'PC02': (len(answers) > 31 and answers[29] == 'N') or (len(answers) > 31 and answers[31] == 'N'),
        'PC03': (len(answers) > 32 and answers[29] == 'N') or (len(answers) > 32 and answers[32] == 'N'),
        'PC05': len(answers) > 34 and answers[34] == 'N',
        'CO01': len(answers) > 36 and (answers[35] == 'N' or answers[36] == 'N'),
    }
    return conditions.get(control, False)

# --- 리팩토링: 시트 값 입력 함수 ---
def fill_sheet(ws, text_data, answers):
    if 'A1' in text_data:
        ws['C7'] = text_data['A1']
    if 'B1' in text_data:
        ws['C8'] = text_data['B1']
    if 'B2' in text_data:
        ws['C12'] = text_data['B2']
        value = str(text_data['B2'])
        num_lines = value.count('\n') + 1
        approx_lines = num_lines + (len(value) // 50)
        ws.row_dimensions[12].height = 15 * approx_lines
    # B3: company_name, B5: user_name
    if len(answers) > 0 and answers[0]:
        company_name = "Company Name" # Placeholder for company name
        user_name = "User Name" # Placeholder for user name
        ws['B3'] = company_name
        ws['B5'] = user_name

@app.route('/export_excel', methods=['GET'])
def save_to_excel():
    answers = session.get('answer', [])
    textarea_answers = session.get('textarea_answer', [])
    success, user_email, error = export_interview_excel_and_send(
        answers,
        textarea_answers,
        get_text_itgc,
        fill_sheet,
        is_ineffective,
        send_gmail_with_attachment
    )
    if success:
        return '<h3>인터뷰 내용에 따른 ITGC 설계평가 문서가 입력하신 메일로 전송되었습니다.<br>메일함을 확인해 주세요.</h3>\n<a href="/" style="display:inline-block;margin-top:20px;padding:10px 20px;background:#1976d2;color:#fff;text-decoration:none;border-radius:5px;">처음으로</a>'
    else:
        return f'<h3>메일 전송에 실패했습니다: {error}</h3>' if user_email else '<h3>메일 주소가 입력되지 않았습니다. 43번 질문에 메일 주소를 입력해 주세요.</h3>'

def get_text_itgc(answers, control_number, textarea_answers=None):
    result = {}
    if textarea_answers is None:
        textarea_answers = [''] * len(answers)
    
    if control_number == 'APD01':
        result['A1'] = "APD01"
        result['B1'] = "사용자 신규 권한 승인"
        result['B2'] = "사용자 권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[12] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "새로운 권한 요청 시, 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[14]}" if textarea_answers[14] else "\n\n권한 부여 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[14] == 'Y' else "새로운 권한 요청 시 승인 절차가 없습니다.")
    
    elif control_number == 'APD02':
        result['A1'] = "APD02"
        result['B1'] = "부서이동자 권한 회수"
        result['B2'] = "사용자 권한 회수 이력이 시스템에 " + ("기록되고 있습니다." if answers[13] == 'Y' else "기록되지 않습니다.") + "\n\n" + (
            "부서 이동 시 기존 권한을 회수하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[15]}" if textarea_answers[15] else "\n\n부서 이동 시 권한 회수 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[15] == 'Y' else "부서 이동 시 기존 권한 회수 절차가 없습니다.")

    elif control_number == 'APD03':
        result['A1'] = "APD03"
        result['B1'] = "퇴사자 접근권한 회수"
        result['B2'] = "퇴사자 발생 시 접근권한을 " + ("차단하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[16] == 'Y' else "차단 절차가 없습니다.") + (
            f"\n{textarea_answers[16]}" if textarea_answers[16] else "\n퇴사자 접근권한 차단 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD04':
        result['A1'] = "APD04"
        result['B1'] = "사용자 권한 Monitoring"
        result['B2'] = "전체 사용자가 보유한 권한에 대한 적절성을 " + ("모니터링하는 절차가 있습니다." if answers[17] == 'Y' else "모니터링 절차가 존재하지 않습니다.")

    elif control_number == 'APD05':
        result['A1'] = "APD05"
        result['B1'] = "Application 패스워드"
        result['B2'] = "패스워드 설정 사항은 아래와 같습니다 \n\n" + (answers[18] if answers[18] else "패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")
    
    elif control_number == 'APD06':
        result['A1'] = "APD06"
        result['B1'] = "데이터 직접 변경"
        result['B2'] = "데이터 변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[19] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "데이터 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[20]}" if textarea_answers[20] else "데이터 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[20] == 'Y' else "데이터 변경 시 승인 절차가 없습니다.")

    elif control_number == 'APD07':
        result['A1'] = "APD07"
        result['B1'] = "DB 접근권한 승인"
        result['B2'] = f"DB 종류와 버전: {answers[9]}" + f"\n\nDB 접근제어 Tool 사용 여부: {'사용' if answers[10] == 'Y' else '미사용'}" + "\n\n" + (
            "DB 접근권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[21] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
                "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                    f"\n{textarea_answers[22]}" if textarea_answers[22] else "DB 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
                ) if answers[22] == 'Y' else "DB 접근권한 요청 시 승인 절차가 없습니다."
            )
        )

    elif control_number == 'APD08':
        result['A1'] = "APD08"
        result['B1'] = "DB 관리자 권한 제한"
        result['B2'] = "DB 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[23] if answers[23] else "DB 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD09':
        result['A1'] = "APD09"
        result['B1'] = "DB 패스워드"
        result['B2'] = "DB 패스워드 설정사항은 아래와 같습니다.\n" + (answers[24] if answers[24] else "DB 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD10':
        result['A1'] = "APD10"
        result['B1'] = "OS 접근권한 승인"
        result['B2'] = f"OS 종류와 버전: {answers[7]}" + f"\n\nOS 접근제어 Tool 사용 여부: {'사용' if answers[8] == 'Y' else '미사용'}" + "\n\n" + (
            "OS 접근권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[25] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
                "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                    f"\n{textarea_answers[26]}" if textarea_answers[26] else "OS 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
                ) if answers[26] == 'Y' else "OS 접근권한 요청 시 승인 절차가 없습니다."
            )
        )

    elif control_number == 'APD11':
        result['A1'] = "APD11"
        result['B1'] = "OS 관리자 권한 제한"
        result['B2'] = "OS 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[27] if answers[27] else "OS 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD12':
        result['A1'] = "APD12"
        result['B1'] = "OS 패스워드"
        result['B2'] = "OS 패스워드 설정사항은 아래와 같습니다.\n" + (answers[28] if answers[28] else "OS 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC01':
        result['A1'] = "PC01"
        result['B1'] = "프로그램 변경 승인"
        result['B2'] = "프로그램 변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[29] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "프로그램 변경 시 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[30]}" if textarea_answers[30] else "\n프로그램 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[30] == 'Y' else "프로그램 변경 시 승인 절차가 없습니다.")

    elif control_number == 'PC02':
        result['A1'] = "PC02"
        result['B1'] = "프로그램 변경 사용자 테스트"
        result['B2'] = "프로그램 변경 시 사용자 테스트를 " + ("수행하고 그 결과를 문서화하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[31] == 'Y' else "수행하지 않습니다.") + (
            f"\n{textarea_answers[31]}" if textarea_answers[31] else "\n프로그램 변경 사용자 테스트 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC03':
        result['A1'] = "PC03"
        result['B1'] = "프로그램 변경 이관 승인"
        result['B2'] = "프로그램 변경 완료 후 이관(배포)을 위해 " + ("부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[32] == 'Y' else "이관(배포) 절차가 없습니다.") + (
            f"\n{textarea_answers[32]}" if textarea_answers[32] else "\n프로그램 변경 이관 승인 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC04':
        result['A1'] = "PC04"
        result['B1'] = "이관(배포) 권한 제한"
        result['B2'] = "이관(배포) 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[33] if answers[33] else "이관(배포) 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC05':
        result['A1'] = "PC05"
        result['B1'] = "개발/운영 환경 분리"
        result['B2'] = "운영서버 외 별도의 개발 또는 테스트 서버를 " + ("운용하고 있습니다." if answers[34] == 'Y' else "운용하지 않습니다.")

    elif control_number == 'CO01':
        result['A1'] = "CO01"
        result['B1'] = "배치 스케줄 등록/변경 승인"
        result['B2'] = "배치 스케줄 등록/변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[35] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "배치 스케줄 등록/변경 시 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[36]}" if textarea_answers[36] else "\n배치 스케줄 등록/변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[36] == 'Y' else "배치 스케줄 등록/변경 시 승인 절차가 없습니다.")

    elif control_number == 'CO02':
        result['A1'] = "CO02"
        result['B1'] = "배치 스케줄 등록/변경 권한 제한"
        result['B2'] = "배치 스케줄 등록/변경 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[37] if answers[37] else "배치 스케줄 등록/변경 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO03':
        result['A1'] = "CO03"
        result['B1'] = "배치 실행 모니터링"
        result['B2'] = "배치 실행 오류 등에 대한 모니터링은 아래와 같이 수행되고 있습니다\n" + (answers[38] if answers[38] else "배치 실행 오류 등에 대한 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO04':
        result['A1'] = "CO04"
        result['B1'] = "장애 대응 절차"
        result['B2'] = "장애 발생시 이에 대응하고 조치하는 절차는 아래와 같습니다\n" + (answers[39] if answers[39] else "장애 발생시 이에 대응하고 조치하는 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO05':
        result['A1'] = "CO05"
        result['B1'] = "백업 및 모니터링"
        result['B2'] = "백업 수행 및 모니터링 절차는 아래와 같습니다.\n" + (answers[40] if answers[40] else "백업 수행 및 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO06':
        result['A1'] = "CO06"
        result['B1'] = "서버실 출입 절차"
        result['B2'] = "서버실 출입 절차는 아래와 같습니다.\n" + (answers[41] if answers[41] else "서버실 출입 절차에 대한 상세 기술이 제공되지 않았습니다.")
        
    else:
        result['A1'] = f"Unknown control number: {control_number}"
        result['B1'] = ""
        result['B2'] = "알 수 없는 통제 번호입니다."
    
    return result

@app.route('/link3')
def link3():
    print("Paper Function")
    return render_template('link3.jsp')

@app.route('/link4')
def link4():
    print("Video Function")
    return render_template('link4.jsp')

@app.route('/link9')
def link9():
    print("ETC Function")
    return render_template('link9.jsp')

@app.route('/register', methods=['POST'])
def register():
    print("Register")
    return render_template('register.jsp')

@app.route('/register_request', methods=['POST'])
def register_request():
    print("Register request")

    form_data = request.form.to_dict()

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')
    param3 = form_data.get('param3')

    print("Param1 = ", param1)
    print("Param2 = ", param2)
    print("Param3 = ", param3)

    result = "User Registered" # Placeholder for registration result
    return render_template('index.jsp', user_name = result, return_code=2)

@app.route('/set_regist', methods=['POST'])
def set_regist():

    form_data = request.form.to_dict()

    result = "Regist Set" # Placeholder for regist setting result
    return render_template('link.jsp', user_request = "User Request List") # Placeholder for user request list
    
@app.route('/rcm_generate', methods=['POST'])
def rcm_generate():
    form_data = request.form.to_dict()
    success, user_email, error = generate_and_send_rcm_excel(form_data, send_gmail_with_attachment)
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
    # type별 데이터 맵
    video_map = {
        'APD01': {
            'youtube_url': 'https://www.youtube.com/embed/8QqNfcO9NPI?si=x4nMkbfyFRyRi7jI&autoplay=1&mute=1',
            'img_url': None,
            'title': 'Access Program & Data',
            'desc': 'APD01 설명'
        },
        'APD02': {
            'youtube_url': 'https://www.youtube.com/embed/vfWdDOb11RY?si=Nv-PDzWCD4hmi2Ja&autoplay=1&mute=1',
            'img_url': None,
            'title': 'Access Program & Data',
            'desc': 'APD02 설명'
        },
        'APD03': {
            'youtube_url': 'https://www.youtube.com/embed/2cAd2HOzICU?si=ZNXR_u8uAjWIsUd6&autoplay=1&mute=1',
            'img_url': None,
            'title': 'Access Program & Data',
            'desc': 'APD03 설명'
        },
        'PC01': {
            'youtube_url': 'https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal&autoplay=1&mute=1',
            'img_url': '/static/img/PC01.jpg',
            'title': '프로그램 변경 승인',
            'desc': '프로그램 변경 필요시 적절한 승인권자의 승인을 득합니다.'
        },
        'CO01': {
            'youtube_url': 'https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal&autoplay=1&mute=1',
            'img_url': '/static/img/CO01.png',
            'title': '배치잡 스케줄 등록 승인',
            'desc': '배치잡 스케줄 등록 시 적절한 승인권자의 승인을 득합니다.'
        },
        'OVERVIEW': {
            'youtube_url': 'https://www.youtube.com/embed/8ZnUo41usRk?si=8vkxW6vENB-689GV&autoplay=1&mute=1',
            'img_url': None,
            'title': '내부회계관리제도 Overview',
            'desc': '내부회계관리제도 개요 영상'
        },
        'PW': {
            'youtube_url': 'https://www.youtube.com/embed/0zpXQNFBHOI?si=v-BPoHFtzi4mhnUs&autoplay=1&mute=1',
            'img_url': None,
            'title': '패스워드 기준',
            'desc': 'ITGC 패스워드 기준 영상'
        },
        'PW_DETAIL': {
            'youtube_url': 'https://www.youtube.com/embed/-TjiH1fR5aI?si=nTj52Jzfz_XRKfZB&autoplay=1&mute=1',
            'img_url': None,
            'title': '패스워드 기준 상세',
            'desc': 'ITGC 패스워드 기준 심화 영상'
        },
        'MONITOR': {
            'youtube_url': 'https://www.youtube.com/embed/XXEE7C0t_70?si=fjx-2AbZwz9c0vwp&autoplay=1&mute=1',
            'img_url': None,
            'title': '모니터링 통제',
            'desc': 'ITGC 모니터링 통제 영상'
        },
    }
    if not content_type or content_type not in video_map:
        return '<div style="text-align: center; padding: 20px;"><h3>준비 중입니다</h3><p>해당 항목은 현재 영상제작 중 입니다.</p></div>'
    data = video_map[content_type]
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

def get_gmail_credentials():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_gmail(to, subject, body):
    creds = get_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    send_message = service.users().messages().send(userId="me", body=message).execute()
    return send_message

def send_gmail_with_attachment(to, subject, body, file_stream=None, file_path=None, file_name=None):
    creds = get_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)

    # 메일 생성
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message['Bcc'] = 'snowball2727@naver.com'
    message.attach(MIMEText(body, 'plain'))

    # 첨부파일 추가 (메모리 버퍼 우선, 없으면 파일 경로)
    part = MIMEBase('application', 'octet-stream')
    if file_stream is not None:
        file_stream.seek(0)
        part.set_payload(file_stream.read())
    elif file_path is not None:
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
    else:
        raise ValueError('첨부할 파일이 없습니다.')
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
    message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
    return send_message

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
            return render_template('contact.jsp', success=True)
        except Exception as e:
            print(f"[!] 문의 메일 전송 실패: {e}")
            return render_template('contact.jsp', success=False, error=str(e))
    print("[0] Contact 폼 GET 요청")
    return render_template('contact.jsp')

if __name__ == '__main__':
    main()