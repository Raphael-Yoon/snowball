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
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO

import link_admin
import link1_rcm
import link1_pbc
import link2_design
import link3_operation
import snowball_db

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
    result = snowball_db.get_user_list()
    client_ip = request.remote_addr
    return render_template('index.jsp', user_name = result, return_code=0, client_ip=client_ip)

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
    users = snowball_db.get_user_list()
    return render_template('link1.jsp', return_code=0, users=users)

# Answer Type: 0: 리스트박스, 1: Y/N, 2: Textbox, 3: Y/N-Textbox, 4: Y/N-Textarea, 5: Textarea
s_questions = [
    {"index": 0, "text": "산출물을 전달받을 e-Mail 주소를 입력해주세요.", "category": "Complete", "help": "", "answer_type": "2", "text_help": ""},
    {"index": 1, "text": "시스템 이름을 적어주세요.", "category": "IT PwC", "help": "", "answer_type": "2", "text_help": ""},
    {"index": 2, "text": "사용하고 있는 시스템은 상용소프트웨어입니까?", "category": "IT PwC", "help": "", "answer_type": "3", "text_help": "SAP ERP, Oracle ERP, 더존ERP 등"},
    {"index": 3, "text": "주요 로직을 회사내부에서 수정하여 사용할 수 있습니까?", "category": "IT PwC", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 4, "text": "Cloud 서비스를 사용하고 있습니까?", "category": "IT PwC", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 5, "text": "어떤 종류의 Cloud입니까?", "category": "IT PwC", "help": "SaaS (Software as a Service): 사용자가 직접 설치 및 관리할 필요 없이, 클라우드에서 제공되는 ERP 소프트웨어를 사용하는 방식.<br>예: SAP S/4HANA Cloud, Oracle NetSuite, Microsoft Dynamics 365 → 기업이 재무, 인사, 회계, 공급망 관리 등을 클라우드에서 운영 가능.<br>IaaS (Infrastructure as a Service): 기업이 자체적으로 ERP 시스템을 구축하고 운영할 수 있도록 서버, 스토리지, 네트워크 등의 인프라를 제공하는 방식.<br>예: AWS EC2, Microsoft Azure Virtual Machines, Google Cloud Compute Engine → 기업이 SAP, Oracle ERP 등의 온프레미스 버전을 클라우드 환경에서 직접 운영.", "answer_type": "2", "text_help": ""},
    {"index": 6, "text": "Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?", "category": "IT PwC", "help": "SOC 1 Report (Service Organization Control 1 보고서)는 재무 보고와 관련된 내부 통제 사항을 검증하는 보고서입니다.", "answer_type": "1", "text_help": ""},
    {"index": 7, "text": "OS 종류와 버전을 작성해 주세요.", "category": "IT PwC", "help": "예: 윈도우즈 서버 2012, Unix AIX, Linux Redhat 등", "answer_type": "2", "text_help": ""},
    {"index": 8, "text": "OS 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: Hiware, CyberArk 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 9, "text": "DB 종류와 버전을 작성해 주세요.", "category": "IT PwC", "help": "예: Oracle R12, MS SQL Server 2008 등", "answer_type": "2", "text_help": ""},
    {"index": 10, "text": "DB 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: DBi, DB Safer 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 11, "text": "별도의 Batch Schedule Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: Waggle, JobScheduler 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 12, "text": "사용자 권한부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "사용자A가 재무권한을 가지고 있었는데 당기에 구매권한을 추가로 받았을 경우 언제(날짜 등) 구매권한을 받았는지 시스템에서 관리되는 경우를 의미합니다.", "answer_type": "1", "text_help": ""},
    {"index": 13, "text": "사용자 권한회수 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "기존 권한 회수시 History를 관리하고 있는지를 확인합니다.<br>Standard 기능을 기준으로 SAP ERP의 경우 권한회수이력을 별도로 저장하며 Oracle ERP의 경우 권한 데이터를 삭제하지 않고 Effective Date로 관리합니다", "answer_type": "1", "text_help": ""},
    {"index": 14, "text": "사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) 새로운 권한이 필요한 경우 ITSM을 통해 요청서를 작성하고 팀장의 승인을 받은 후 IT팀에서 해당 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 15, "text": "부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?", "category": "APD", "help": "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 기존 권한을 회수함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 기존 권한을 회수함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 16, "text": "퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?", "category": "APD", "help": "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 접근권한을 차단함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 접근권한을 차단함", "answer_type": "4", "text_help": "관련 절차를 입력하세요"},
    {"index": 17, "text": "전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?", "category": "APD", "help": "", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 18, "text": "패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 19, "text": "데이터 변경 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "시스템의 기능을 이용하여 데이터를 변경한 것이 아닌 관리자 등이 DB에 접속하여 쿼리를 통해 데이터를 변경한 건이 대상이며 해당 변경건만 추출이 가능해야 합니다", "answer_type": "1", "text_help": ""},
    {"index": 20, "text": "데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) 데이터 변경 필요시 담당자는 ITSM을 통해 요성서를 작성하고 책임자의 승인을 받은 후 IT담당자가 데이터를 변경함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 21, "text": "DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 22, "text": "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) DB 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 23, "text": "DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예) 인프라관리팀 김xx 과장, DBA", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 24, "text": "DB 패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 25, "text": "OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 26, "text": "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) OS 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 27, "text": "OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예) 인프라관리팀 이xx 책임, 보안관리자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 28, "text": "OS 패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 29, "text": "프로그램 변경 이력이 시스템에 기록되고 있습니까?", "category": "PC", "help": "변경에 대한 History가 시스템에 의해 기록되어야 합니다. A화면을 1, 3, 5월에 요청서를 받아 변경했다면 각각의 이관(배포)이력이 기록되어야 하며 자체기능, 배포툴, 형상관리툴 등을 사용할 수 있습니다.", "answer_type": "1", "text_help": ""},
    {"index": 30, "text": "프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 필요시 ITSM을 통해 요청서를 작성하고 부서장의 승인을 득함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 31, "text": "프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?", "category": "PC", "help": ") 프로그램 기능 변경 완료 후 요청자에 의해 사용자 테스트가 수행되고 그 결과가 문서화됨", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 32, "text": "프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 및 사용자 테스트 완료 후 변경담당자로부터 이관 요청서가 작성되고 부서장의 승인을 득함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 33, "text": "이관(배포)권한을 보유한 인원에 대해 기술해 주세요.", "category": "PC", "help": "예) 인프라관리팀 박xx 수석, 서버관리자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 34, "text": "운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?", "category": "PC", "help": "JSP, ASP 등으로 개발된 웹시스템의 경우 localhost 또는 127.0.0.1을 개발서버로도 볼 수 있습니다", "answer_type": "1", "text_help": ""},
    {"index": 35, "text": "배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?", "category": "CO", "help": "개발되어 등록된 배치 프로그램(Background Job)을 스케줄로 등록 또는 변경한 경우로 한정합니다. 배치 프로그램을 개발하여 운영서버에 반영하는 것은 이 경우에 포함되지 않습니다", "answer_type": "1", "text_help": ""},
    {"index": 36, "text": "배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "CO", "help": "예) 배치 스케줄이 필요한 경우 ITSM을 통해 요청서를 작성하고 승인권자의 승인을 득한 후 적절한 담당자에 의해 스케줄이 등록됨", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 37, "text": "배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.", "category": "CO", "help": "예) 시스템 운영팀 최xx 과장, 시스템운영자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 38, "text": "배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.", "category": "CO", "help": "예1) 매일 아침 배치수행결과를 확인하며 문서화하며 오류 발생시 원인파악 및 조치현황 등을 함께 기록함<br>예2) 오류 발생시에만 점검결과를 작성하며 오류 발생 기록은 삭제하지 않고 유지됨", "answer_type": "5", "text_help": ""},
    {"index": 39, "text": "장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.", "category": "CO", "help": "", "answer_type": "5", "text_help": ""},
    {"index": 40, "text": "백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.", "category": "CO", "help": "", "answer_type": "5", "text_help": ""},
    {"index": 41, "text": "서버실 출입시의 절차에 대해 기술해 주세요.", "category": "CO", "help": "", "answer_type": "5", "text_help": ""}
]

question_count = len(s_questions)

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
        users = snowball_db.get_user_list()
        return render_template('link2.jsp', question=s_questions[session['question_index']], 
                             question_count=question_count, 
                             current_index=session['question_index'],
                             remote_addr=request.remote_addr,
                             users=users)

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
    return render_template('link2.jsp', question=question, question_count=question_count, current_index=session['question_index'], remote_addr=request.remote_addr)
    
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
        company_name = snowball_db.get_user_info(answers[0], 1)
        user_name = snowball_db.get_user_info(answers[0], 2)
        ws['B3'] = company_name
        ws['B5'] = user_name

@app.route('/export_excel', methods=['GET'])
def save_to_excel():
    answers = session.get('answer', [])
    textarea_answers = session.get('textarea_answer', [])
    today = datetime.today().strftime('%Y%m%d')
    file_name = f"{answers[1]}_{today}.xlsx" if len(answers) > 1 and answers[1] else f"responses_{today}.xlsx"

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
        fill_sheet(ws, text_data, answers)
        if is_ineffective(control, answers):
            ws['C14'] = 'Ineffective'
            ws.sheet_properties.tabColor = "FF0000"
        else:
            ws['C13'] = '화면 증빙을 첨부해주세요'

    # 메모리 버퍼에 저장
    excel_stream = BytesIO()
    wb.save(excel_stream)
    wb.close()
    excel_stream.seek(0)

    user_email = ''
    if answers and answers[0]:
        user_email = answers[0]
    elif 'a0_text' in answers:
        user_email = answers['a0_text']
    elif len(answers) > 0 and hasattr(answers, 'get') and answers.get('a0_text'):
        user_email = answers.get('a0_text')

    if user_email:
        subject = '인터뷰 결과 파일'
        body = '인터뷰 내용에 따라 ITGC 설계평가 문서를 첨부합니다.'
        try:
            send_gmail_with_attachment(
                to=user_email,
                subject=subject,
                body=body,
                file_stream=excel_stream,
                file_name=file_name
            )
            return '<h3>인터뷰 내용에 따른 ITGC 설계평가 문서가 입력하신 메일로 전송되었습니다.<br>메일함을 확인해 주세요.</h3>\n<a href="/" style="display:inline-block;margin-top:20px;padding:10px 20px;background:#1976d2;color:#fff;text-decoration:none;border-radius:5px;">처음으로</a>'
        except Exception as e:
            return f'<h3>메일 전송에 실패했습니다: {e}</h3>'
    else:
        return '<h3>메일 주소가 입력되지 않았습니다. 43번 질문에 메일 주소를 입력해 주세요.</h3>'

    # 바로 다운로드로 반환
    return send_file(
        excel_stream,
        as_attachment=True,
        download_name=file_name,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

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
    # 파일명 생성: 입력받은 파일명(param2)_RCM_YYMMDD.xlsx
    base_name = form_data.get('param2', 'output')
    today = datetime.today().strftime('%y%m%d')
    file_name = f"{base_name}_ITGC_RCM_{today}.xlsx"
    excel_stream = link1_rcm.rcm_generate(form_data, file_name=file_name)

    # 담당자 user_id는 param1
    user_email = form_data.get('param1')

    if user_email:
        subject = 'RCM 자동생성 결과 파일'
        body = '요청하신 RCM 자동생성 엑셀 파일을 첨부합니다.'
        try:
            send_gmail_with_attachment(
                to=user_email,
                subject=subject,
                body=body,
                file_stream=excel_stream,
                file_name=file_name
            )
            return render_template('mail_sent.jsp', user_email=user_email)
        except Exception as e:
            return f'<h3>메일 전송에 실패했습니다: {e}</h3>'
    else:
        return '<h3>메일 주소가 없습니다. 담당자 정보를 확인해 주세요.</h3>'
    
    # 바로 다운로드로 반환
    # return send_file(
    #     excel_stream,
    #     as_attachment=True,
    #     download_name=file_name,
    #     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #  )

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
        'ETC': ['OVERVIEW', 'PW', 'PW_DETAIL', 'MONITOR']
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

def send_gmail_with_attachment(to, subject, body, file_stream=None, file_path=None, file_name=None):
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