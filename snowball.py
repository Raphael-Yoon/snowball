from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, current_user
from openpyxl import load_workbook
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import pickle
from email.mime.text import MIMEText

import link_admin
import link1_rcm
import link1_pbc
import link2_design
import link3_operation
import snowball_db

app = Flask(__name__)
app.secret_key = '150606'

# 시작할 질문 번호 설정 (1부터 시작)
START_QUESTION = 0  # 여기서 시작 질문 번호를 변경하면 됩니다 (예: 5번 질문부터 시작)

load_dotenv()

@app.route('/')
def index():
    result = snowball_db.get_user_list()
    return render_template('index.jsp', user_name = result, return_code=0)

def main():
    app.run(host='0.0.0.0', debug=False, port=5001)
    #app.run(host='127.0.0.1', debug=False, port=8001)

@app.route('/link_admin')
def link():
    print("Admin Function")
    result = snowball_db.get_user_request()
    return render_template('link0.jsp', login_code = 0)

@app.route('/link0')
def link0():
    print("Reload")
    return render_template('link0.jsp')

@app.route('/link1')
def link1():
    print("RCM Function")
    return render_template('link1.jsp', return_code=0)

s_questions = [
    {"index": 0, "text": "시스템 이름을 적어주세요.", "category": "IT PwC"},
    {"index": 1, "text": "사용하고 있는 시스템은 상용소프트웨어입니까?", "category": "IT PwC"},
    {"index": 2, "text": "기능을 회사내부에서 수정하여 사용할 수 있습니까?(SAP, Oracle ERP 등등)", "category": "IT PwC"},
    {"index": 3, "text": "Cloud 서비스를 사용하고 있습니까?", "category": "IT PwC"},
    {"index": 4, "text": "어떤 종류의 Cloud입니까?", "category": "IT PwC"},
    {"index": 5, "text": "Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?", "category": "IT PwC"},
    {"index": 6, "text": "OS 종류와 버전을 작성해 주세요.", "category": "IT PwC"},
    {"index": 7, "text": "OS 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC"},
    {"index": 8, "text": "DB 종류와 버전을 작성해 주세요.", "category": "IT PwC"},
    {"index": 9, "text": "DB 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC"},
    {"index": 10, "text": "별도의 Batch Schedule Tool을 사용하고 있습니까?", "category": "IT PwC"},
    {"index": 11, "text": "사용자 권한부여 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 12, "text": "사용자 권한회수 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 13, "text": "사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 14, "text": "부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?", "category": "APD"},
    {"index": 15, "text": "퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?", "category": "APD"},
    {"index": 16, "text": "전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?", "category": "APD"},
    {"index": 17, "text": "패스워드 설정사항을 기술해 주세요.", "category": "APD"},
    {"index": 18, "text": "데이터 변경 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 19, "text": "데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 20, "text": "DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 21, "text": "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 22, "text": "DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD"},
    {"index": 23, "text": "DB 패스워드 설정사항을 기술해 주세요.", "category": "APD"},
    {"index": 24, "text": "OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 25, "text": "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 26, "text": "OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD"},
    {"index": 27, "text": "OS 패스워드 설정사항을 기술해 주세요.", "category": "APD"},
    {"index": 28, "text": "프로그램 변경 이력이 시스템에 기록되고 있습니까?", "category": "PC"},
    {"index": 29, "text": "프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?", "category": "PC"},
    {"index": 30, "text": "프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?", "category": "PC"},
    {"index": 31, "text": "프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "PC"},
    {"index": 32, "text": "이관(배포)권한을 보유한 인원에 대해 기술해 주세요.", "category": "PC"},
    {"index": 33, "text": "운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?", "category": "PC"},
    {"index": 34, "text": "배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?", "category": "CO"},
    {"index": 35, "text": "배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "CO"},
    {"index": 36, "text": "배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.", "category": "CO"},
    {"index": 37, "text": "배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.", "category": "CO"},
    {"index": 38, "text": "장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.", "category": "CO"},
    {"index": 39, "text": "백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.", "category": "CO"},
    {"index": 40, "text": "서버실 출입시의 절차에 대해 기술해 주세요.", "category": "CO"},
    {"index": 41, "text": "회사명을 적어주세요.", "category": "Complete"},
    {"index": 42, "text": "담당자 이름을 적어주세요.", "category": "Complete"},
    {"index": 43, "text": "산출물을 전달받을 메일 주소를 적어주세요.", "category": "Complete"}
]

question_count = len(s_questions)

@app.route('/link2/prev')
def link2_prev():
    print("Previous Question")
    if 'question_index' in session:
        # 이전 질문으로 이동 (최소 0)
        session['question_index'] = max(0, session['question_index'] - 1)
    return render_template('link2.jsp', question=s_questions[session['question_index']], 
                         question_count=question_count, 
                         current_index=session['question_index'])

@app.route('/link2', methods=['GET', 'POST'])
def link2():
    print("Interview Function")

    if request.method == 'GET':
        # 세션 초기화
        session.clear()
        # START_QUESTION이 유효한 범위인지 확인
        if 1 <= START_QUESTION <= question_count:
            session['question_index'] = START_QUESTION - 1  # 1-based를 0-based로 변환
        else:
            session['question_index'] = 0
        session['answer'] = [''] * question_count  # 필요한 만큼 동적으로 조절 가능
        session['textarea_answer'] = [''] * question_count  # textarea 값 저장용
        return render_template('link2.jsp', question=s_questions[session['question_index']], 
                             question_count=question_count, 
                             current_index=session['question_index'],
                             remote_addr=request.remote_addr)

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
            1: 2 if session['answer'][question_index] == 'Y' else 3,
            3: 4 if session['answer'][question_index] == 'Y' else 6
        }
        next_question.update(conditional_routes)

        # 43번 질문 제출 시에만 save_to_excel 호출(메일 전송)
        if question_index == 43:
            print('excel download')
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
    return render_template('link2.jsp', question=question, question_count=question_count, current_index=session['question_index'], remote_addr=request.remote_addr)
    
@app.route('/export_excel', methods=['GET'])
def save_to_excel():
    answers = session.get('answer', [])
    textarea_answers = session.get('textarea_answer', [])
    today = datetime.today().strftime('%Y%m%d')
    file_name = f"{answers[0]}_{today}.xlsx" if answers else f"responses_{today}.xlsx"
    file_path = os.path.join("static", file_name)

    # 1. 템플릿 파일 불러오기
    template_path = os.path.join("static", "Design_Template.xlsx")
    wb = load_workbook(template_path)

    # 2. 각 통제별 시트에 값 입력
    control_list = [
        'APD01', 'APD02', 'APD03', 'APD04', 'APD05', 'APD06', 'APD07', 'APD08', 'APD09', 'APD10', 'APD11', 'APD12',
        'PC01', 'PC02', 'PC03', 'PC04', 'PC05',
        'CO01', 'CO02', 'CO03', 'CO04', 'CO05', 'CO06'
    ]
    for control in control_list:
        text_data = get_text_itgc(answers, control, textarea_answers)
        ws = wb[control]
        if 'A1' in text_data:
            ws['C7'] = text_data['A1']
        if 'B1' in text_data:
            ws['C8'] = text_data['B1']
        if 'B2' in text_data:
            ws['C12'] = text_data['B2']
            # C12 셀의 데이터 길이에 따라 행 높이 자동 조정
            value = str(text_data['B2'])
            num_lines = value.count('\n') + 1
            approx_lines = num_lines + (len(value) // 50)
            ws.row_dimensions[12].height = 15 * approx_lines
        # 모든 시트에 41, 42번 답변 반영
        if len(answers) > 41:
            ws['B3'] = answers[41]
        if len(answers) > 42:
            ws['B5'] = answers[42]
        # C14 Ineffective 처리 조건-시트 매핑 (중복 제거)
        ineffective_conditions = [
            ('APD01', len(answers) > 13 and (answers[11] == 'N' or answers[13] == 'N')),
            ('APD02', len(answers) > 14 and answers[14] == 'N'),
            ('APD03', len(answers) > 15 and answers[15] == 'N'),
            ('APD04', len(answers) > 16 and answers[16] == 'N'),
            ('APD06', len(answers) > 19 and (answers[18] == 'N' or answers[19] == 'N')),
            ('APD07', len(answers) > 21 and (answers[20] == 'N' or answers[21] == 'N')),
            ('APD10', len(answers) > 25 and (answers[24] == 'N' or answers[25] == 'N')),
            ('PC01', (len(answers) > 28 and answers[28] == 'N') or (len(answers) > 29 and answers[29] == 'N')),
            ('PC02', (len(answers) > 28 and answers[28] == 'N') or (len(answers) > 30 and answers[30] == 'N')),
            ('PC03', (len(answers) > 28 and answers[28] == 'N') or (len(answers) > 31 and answers[31] == 'N')),
            ('PC05', len(answers) > 33 and answers[33] == 'N'),
            ('CO01', len(answers) > 35 and (answers[34] == 'N' or answers[35] == 'N')),
        ]
        for sheet_name, condition in ineffective_conditions:
            if control == sheet_name and condition:
                ws['C14'] = 'Ineffective'
                ws.sheet_properties.tabColor = "FF0000"  # 시트 탭 색상을 빨간색으로

    wb.save(file_path)

    # 메일 전송 (a43이 메일 주소)
    # user_email = answers[43] if len(answers) > 43 else ''
    # if user_email:
    #     import smtplib
    #     from email.mime.multipart import MIMEMultipart
    #     from email.mime.text import MIMEText
    #     from email.mime.base import MIMEBase
    #     from email import encoders
    #     
    #     smtp_server = 'smtp.naver.com'
    #     smtp_port = 587
    #     sender_email = 'snowball2727@naver.com'      # 네이버 메일 주소
    #     sender_password = os.getenv('NAVER_MAIL_PASSWORD')       # 네이버 메일 비밀번호(또는 앱 비밀번호)
    #     bcc_email = 'snowball2727@naver.com'
    #     subject = '인터뷰 결과 파일'
    #     body = '인터뷰 내용에 따라 ITGC 설계평가 문서를 첨부합니다.'
    #     
    #     msg = MIMEMultipart()
    #     msg['From'] = sender_email
    #     msg['To'] = user_email
    #     msg['Subject'] = subject
    #     msg['Bcc'] = bcc_email
    #     msg.attach(MIMEText(body, 'plain'))
    #     # 파일 첨부
    #     with open(file_path, 'rb') as f:
    #         part = MIMEBase('application', 'octet-stream')
    #         part.set_payload(f.read())
    #         encoders.encode_base64(part)
    #         part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
    #         msg.attach(part)
    #     try:
    #         server = smtplib.SMTP(smtp_server, smtp_port)
    #         server.starttls()
    #         server.login(sender_email, sender_password)
    #         recipients = [user_email, bcc_email]
    #         server.sendmail(sender_email, recipients, msg.as_string())
    #         server.quit()
    #         print('메일이 성공적으로 전송되었습니다.')
    #     except Exception as e:
    #         print('메일 전송 실패:', e)

    # 다운로드만 제공
    return send_file(file_path, as_attachment=True)

def get_text_itgc(answers, control_number, textarea_answers=None):
    result = {}
    if textarea_answers is None:
        textarea_answers = [''] * len(answers)
    
    if control_number == 'APD01':
        result['A1'] = "APD01"
        result['B1'] = "사용자 신규 권한 승인"
        result['B2'] = "사용자 권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[11] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "새로운 권한 요청 시, 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[13]}" if textarea_answers[13] else "\n\n권한 부여 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[13] == 'Y' else "새로운 권한 요청 시 승인 절차가 없습니다.")
    
    elif control_number == 'APD02':
        result['A1'] = "APD02"
        result['B1'] = "부서이동자 권한 회수"
        result['B2'] = "사용자 권한 회수 이력이 시스템에 " + ("기록되고 있습니다." if answers[12] == 'Y' else "기록되지 않습니다.") + "\n\n" + (
            "부서 이동 시 기존 권한을 회수하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[14]}" if textarea_answers[14] else "\n\n부서 이동 시 권한 회수 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[14] == 'Y' else "부서 이동 시 기존 권한 회수 절차가 없습니다.")

    elif control_number == 'APD03':
        result['A1'] = "APD03"
        result['B1'] = "퇴사자 접근권한 회수"
        result['B2'] = "퇴사자 발생 시 접근권한을 " + ("차단하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[15] == 'Y' else "차단 절차가 없습니다.") + (
            f"\n{textarea_answers[15]}" if textarea_answers[15] else "\n퇴사자 접근권한 차단 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD04':
        result['A1'] = "APD04"
        result['B1'] = "사용자 권한 Monitoring"
        result['B2'] = "전체 사용자가 보유한 권한에 대한 적절성을 " + ("모니터링하는 절차가 있습니다." if answers[19] == 'Y' else "모니터링 절차가 존재하지 않습니다.")

    elif control_number == 'APD05':
        result['A1'] = "APD05"
        result['B1'] = "Application 패스워드"
        result['B2'] = "패스워드 설정 사항은 아래와 같습니다 \n\n" + (answers[17] if answers[17] else "패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")
    
    elif control_number == 'APD06':
        result['A1'] = "APD06"
        result['B1'] = "데이터 직접 변경"
        result['B2'] = "데이터 변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[18] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "데이터 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[19]}" if textarea_answers[19] else "데이터 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[19] == 'Y' else "데이터 변경 시 승인 절차가 없습니다.")

    elif control_number == 'APD07':
        result['A1'] = "APD07"
        result['B1'] = "DB 접근권한 승인"
        result['B2'] = f"DB 종류와 버전: {answers[8]}" + f"\n\nDB 접근제어 Tool 사용 여부: {'사용' if answers[9] == 'Y' else '미사용'}" + "\n\n" + (
            "DB 접근권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[20] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
                "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                    f"\n{textarea_answers[21]}" if textarea_answers[21] else "DB 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
                ) if answers[21] == 'Y' else "DB 접근권한 요청 시 승인 절차가 없습니다."
            )
        )

    elif control_number == 'APD08':
        result['A1'] = "APD08"
        result['B1'] = "DB 관리자 권한 제한"
        result['B2'] = "DB 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[22] if answers[22] else "DB 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD09':
        result['A1'] = "APD09"
        result['B1'] = "DB 패스워드"
        result['B2'] = "DB 패스워드 설정사항은 아래와 같습니다.\n" + (answers[23] if answers[23] else "DB 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD10':
        result['A1'] = "APD10"
        result['B1'] = "OS 접근권한 승인"
        result['B2'] = f"OS 종류와 버전: {answers[6]}" + f"\n\nOS 접근제어 Tool 사용 여부: {'사용' if answers[7] == 'Y' else '미사용'}" + "\n\n" + (
            "OS 접근권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[24] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
                "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                    f"\n{textarea_answers[25]}" if textarea_answers[25] else "OS 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
                ) if answers[25] == 'Y' else "OS 접근권한 요청 시 승인 절차가 없습니다."
            )
        )

    elif control_number == 'APD11':
        result['A1'] = "APD11"
        result['B1'] = "OS 관리자 권한 제한"
        result['B2'] = "OS 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[26] if answers[26] else "OS 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD12':
        result['A1'] = "APD12"
        result['B1'] = "OS 패스워드"
        result['B2'] = "OS 패스워드 설정사항은 아래와 같습니다.\n" + (answers[27] if answers[27] else "OS 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC01':
        result['A1'] = "PC01"
        result['B1'] = "프로그램 변경 승인"
        result['B2'] = "프로그램 변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[28] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "프로그램 변경 시 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[29]}" if textarea_answers[29] else "\n프로그램 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[29] == 'Y' else "프로그램 변경 시 승인 절차가 없습니다.")

    elif control_number == 'PC02':
        result['A1'] = "PC02"
        result['B1'] = "프로그램 변경 사용자 테스트"
        result['B2'] = "프로그램 변경 시 사용자 테스트를 " + ("수행하고 그 결과를 문서화하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[30] == 'Y' else "수행하지 않습니다.") + (
            f"\n{textarea_answers[30]}" if textarea_answers[30] else "\n프로그램 변경 사용자 테스트 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC03':
        result['A1'] = "PC03"
        result['B1'] = "프로그램 변경 이관 승인"
        result['B2'] = "프로그램 변경 완료 후 이관(배포)을 위해 " + ("부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[31] == 'Y' else "이관(배포) 절차가 없습니다.") + (
            f"\n{textarea_answers[31]}" if textarea_answers[31] else "\n프로그램 변경 이관 승인 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC04':
        result['A1'] = "PC04"
        result['B1'] = "이관(배포) 권한 제한"
        result['B2'] = "이관(배포) 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[32] if answers[32] else "이관(배포) 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC05':
        result['A1'] = "PC05"
        result['B1'] = "개발/운영 환경 분리"
        result['B2'] = "운영서버 외 별도의 개발 또는 테스트 서버를 " + ("운용하고 있습니다." if answers[33] == 'Y' else "운용하지 않습니다.")

    elif control_number == 'CO01':
        result['A1'] = "CO01"
        result['B1'] = "배치 스케줄 등록/변경 승인"
        result['B2'] = "배치 스케줄 등록/변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[34] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "배치 스케줄 등록/변경 시 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[35]}" if textarea_answers[35] else "\n배치 스케줄 등록/변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[35] == 'Y' else "배치 스케줄 등록/변경 시 승인 절차가 없습니다.")

    elif control_number == 'CO02':
        result['A1'] = "CO02"
        result['B1'] = "배치 스케줄 등록/변경 권한 제한"
        result['B2'] = "배치 스케줄 등록/변경 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[36] if answers[36] else "배치 스케줄 등록/변경 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO03':
        result['A1'] = "CO03"
        result['B1'] = "배치 실행 모니터링"
        result['B2'] = "배치 실행 오류 등에 대한 모니터링은 아래와 같이 수행되고 있습니다\n" + (answers[37] if answers[37] else "배치 실행 오류 등에 대한 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO04':
        result['A1'] = "CO04"
        result['B1'] = "장애 대응 절차"
        result['B2'] = "장애 발생시 이에 대응하고 조치하는 절차는 아래와 같습니다\n" + (answers[38] if answers[38] else "장애 발생시 이에 대응하고 조치하는 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO05':
        result['A1'] = "CO05"
        result['B1'] = "백업 및 모니터링"
        result['B2'] = "백업 수행 및 모니터링 절차는 아래와 같습니다.\n" + (answers[39] if answers[39] else "백업 수행 및 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO06':
        result['A1'] = "CO06"
        result['B1'] = "서버실 출입 절차"
        result['B2'] = "서버실 출입 절차는 아래와 같습니다.\n" + (answers[40] if answers[40] else "서버실 출입 절차에 대한 상세 기술이 제공되지 않았습니다.")
        
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
    print("Education Function")
    return render_template('link4.jsp')

@app.route('/link9')
def link9():
    print("ETC Function")
    return render_template('link9.jsp')

@app.route('/login', methods=['POST'])
def login():
    print('login function')
    form_data = request.form.to_dict()

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')

    print("Param1 = ", param1)
    print("Param2 = ", param2)

    result = snowball_db.get_login(param1, param2)

    if result:
        print("Login Success")
        snowball_db.set_login(param1, param2)
        return render_template('link0.jsp', login_id = param1, login_code = 0)
    else:
        print("Login Fail")
        result = snowball_db.get_user_list()
        return render_template('index.jsp', user_name = result, return_code=1)

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

    result = snowball_db.set_user_regist_request(param1, param2, param3)
    result = snowball_db.get_user_list()
    return render_template('index.jsp', user_name = result, return_code=2)

@app.route('/set_regist', methods=['POST'])
def set_regist():

    form_data = request.form.to_dict()

    result = link_admin.set_regist(form_data)

    request_list = snowball_db.get_user_request()
    return render_template('link.jsp', user_request = request_list)
    
@app.route('/rcm_generate', methods=['POST'])
def rcm_generate():

    form_data = request.form.to_dict()
    output_path = link1_rcm.rcm_generate(form_data)

    return send_file(output_path, as_attachment=True)

@app.route('/rcm_request', methods=['POST'])
def rcm_request():

    form_data = request.form.to_dict()
    link1_rcm.rcm_request(form_data)

    return render_template('link1.jsp', return_code=1)

@app.route('/paper_request', methods=['POST'])
def paper_request():
    print("Paper Request called")

    form_data = request.form.to_dict()
    output_path = link2_design.paper_request(form_data)

    return render_template('link2.jsp', return_code = 2)

@app.route('/design_generate', methods=['POST'])
def design_generate():
    print("Design Generate called")

    form_data = request.form.to_dict()
    output_path = link2_design.design_generate(form_data)

    return send_file(output_path, as_attachment=True)

@app.route('/design_template_download', methods=['POST']) 
def design_template_downloade():
    print("Design Template Download called")

    form_data = request.form.to_dict()
    output_path = link2_design.design_template_download(form_data)

    return send_file(output_path, as_attachment=True)

@app.route('/paper_template_download', methods=['POST'])
def paper_template_download():

    form_data = request.form.to_dict()
    output_path = link3_operation.paper_template_download(form_data)

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')

    print('output = ', output_path)
    if output_path != '':
        return send_file(output_path, as_attachment=True)
    else:
        return render_template('link3.jsp', return_param1=param1, return_param2=param2)

@app.route('/paper_generate', methods=['POST'])
def paper_generate():

    form_data = request.form.to_dict()
    output_path = link3_operation.paper_generate(form_data)

    return send_file(output_path, as_attachment=True)

@app.route('/get_content')
def get_content():
    content_type = request.args.get('type')
    
    # param3가 필요한 타입들 정의
    param3_types = {
        'APD': ['APD04', 'APD05', 'APD06', 'APD08', 'APD10', 'APD11', 'APD13', 'APD14'],
        'PC': ['PC04', 'PC05'],
        'CO': ['CO02', 'CO03'],
        'ETC': ['PW', 'PW_DETAIL', 'MONITOR']
    }
    
    # 컨텐츠 타입의 접두사 확인
    prefix = content_type[:3] if content_type else ''
    
    # 해당 타입이 param3를 필요로 하는지 확인
    needs_param3 = prefix in param3_types and content_type in param3_types[prefix]
    
    try:
        if needs_param3:
            return render_template(f'link4_{content_type}.jsp', param3=content_type)
        return render_template(f'link4_{content_type}.jsp')
    except Exception as e:
        print(f"Error rendering template for {content_type}: {str(e)}")
        return '<div style="text-align: center; padding: 20px;"><h3>준비 중입니다</h3><p>해당 항목은 현재 영상제작 중 입니다.</p></div>'

def send_gmail(to, subject, body):
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
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    send_message = service.users().messages().send(userId="me", body=message).execute()
    return send_message

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        print("[1] Contact 폼 제출됨")
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f"[2] 폼 데이터 파싱 완료: name={name}, email={email}")
            print("[6] 메일 전송 성공")
            return render_template('contact.jsp', success=True)
        except Exception as e:
            print(f"[!] 문의 메일 전송 실패: {e}")
            return render_template('contact.jsp', success=False, error=str(e))
    print("[0] Contact 폼 GET 요청")
    return render_template('contact.jsp')

if __name__ == '__main__':
    main() 