from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, current_user
from openpyxl import load_workbook
import pandas as pd
import os
from datetime import datetime

import link_admin
import link1_rcm
import link1_pbc
import link2_design
import link3_operation
import snowball_db

app = Flask(__name__)
app.secret_key = '150606'

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
    {"index": 14, "text": "권한이 부여되는 절차를 기술해 주세요.", "category": "APD"},
    {"index": 15, "text": "부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?", "category": "APD"},
    {"index": 16, "text": "부서이동 등 기존권한의 회수가 필요한 경우 수행되는 절차를 기술해 주세요.", "category": "APD"},
    {"index": 17, "text": "퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?", "category": "APD"},
    {"index": 18, "text": "퇴사자 발생시 접근권한을 차단하는(계정 삭제 등) 절차를 기술해 주세요.", "category": "APD"},
    {"index": 19, "text": "전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?", "category": "APD"},
    {"index": 20, "text": "패스워드 설정사항을 기술해 주세요.", "category": "APD"},
    {"index": 21, "text": "데이터 변경 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 22, "text": "데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 23, "text": "DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 24, "text": "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 25, "text": "DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD"},
    {"index": 26, "text": "DB 패스워드 설정사항을 기술해 주세요.", "category": "APD"},
    {"index": 27, "text": "OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD"},
    {"index": 28, "text": "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD"},
    {"index": 29, "text": "OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD"},
    {"index": 30, "text": "OS 패스워드 설정사항을 기술해 주세요.", "category": "APD"},
    {"index": 31, "text": "프로그램 변경 이력이 시스템에 기록되고 있습니까?", "category": "PC"},
    {"index": 32, "text": "프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?", "category": "PC"},
    {"index": 33, "text": "프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?", "category": "PC"},
    {"index": 34, "text": "프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "PC"},
    {"index": 35, "text": "이관(배포)권한을 보유한 인원에 대해 기술해 주세요.", "category": "PC"},
    {"index": 36, "text": "운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?", "category": "PC"},
    {"index": 37, "text": "배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?", "category": "CO"},
    {"index": 38, "text": "배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "CO"},
    {"index": 39, "text": "배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.", "category": "CO"},
    {"index": 40, "text": "배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.", "category": "CO"},
    {"index": 41, "text": "장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.", "category": "CO"},
    {"index": 42, "text": "백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.", "category": "CO"},
    {"index": 43, "text": "서버실 출입시의 절차에 대해 기술해 주세요.", "category": "CO"}
]

question_count = len(s_questions)

@app.route('/link2', methods=['GET', 'POST'])
def link2():
    print("Interview Function")

    if request.method == 'GET':
        # 세션 초기화
        session.clear()
        session['question_index'] = 0
        session['answer'] = [''] * question_count  # 필요한 만큼 동적으로 조절 가능
        session['System'] = ''
        session['Cloud'] = ''
        session['OS_Tool'] = ''
        session['DB_Tool'] = ''
        session['Batch_Tool'] = ''

    question_index = session['question_index']

    if request.method == 'POST':
        form_data = request.form
        session['answer'][question_index] = form_data.get(f"a{question_index}", '')
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

        # 기본 흐름: 각 질문이 다음 질문으로 자연스럽게 진행
        next_question = {i: i + 1 for i in range(43)}

        # 예외적인 분기 처리
        conditional_routes = {
            1: 2 if session['answer'][question_index] == 'Y' else 3,
            3: 4 if session['answer'][question_index] == 'Y' else 6,
            13: 14 if session['answer'][question_index] == 'Y' else 15,
            15: 16 if session['answer'][question_index] == 'Y' else 17,
            17: 18 if session['answer'][question_index] == 'Y' else 19,
            41: 42 if session['answer'][3] == 'Y' else 44
        }

        # 조건이 있는 질문 반영
        next_question.update(conditional_routes)

        session['question_index'] = next_question.get(question_index, question_index)
        print(f"goto {session['question_index']}")

        # 현재 응답 상태 출력 (join 사용)
        print("Answers:", ", ".join(f"{i}: {ans}" for i, ans in enumerate(session['answer'])))
        
        if session['question_index'] >= question_count:
            print('excel download')
            return save_to_excel()

    # 현재 질문을 렌더링
    question = s_questions[session['question_index']]
    return render_template('link2_system.jsp', question=question['text'], question_number=session['question_index'])
    
@app.route('/export_excel', methods=['GET'])
def save_to_excel():
    answers = session.get('answer', [])
    system_info = [session.get(key, '') for key in ['System', 'Cloud', 'OS_Tool', 'DB_Tool', 'Batch_Tool']]
    system_info = [info if info else '' for info in system_info]  # NaN 방지
    today = datetime.today().strftime('%Y%m%d')
    file_name = f"{answers[0]}_{today}.xlsx" if answers else f"responses_{today}.xlsx"
    
    df = pd.DataFrame({'Question': [q['text'] for q in s_questions], 'Answer': answers}).fillna('')
    df.loc[[1, 3, 6, 7, 8], 'Extra Info'] = system_info
    df = df.fillna('')  # NaN 방지
    file_path = os.path.join("static", file_name)

    # ExcelWriter 블록 내부에서 Understanding 시트도 작성하도록 변경**
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        # Responses 시트 작성
        df = pd.DataFrame({'Question': [q['text'] for q in s_questions], 'Answer': answers}).fillna('')
        df.to_excel(writer, sheet_name='Responses', index=False)
        worksheet = writer.sheets['Responses']
        worksheet.set_column('A:A', max(df['Question'].apply(len)) + 2)

        # 시트 생성 함수 호출
        create_itgc_sheet(writer, 'APD01', get_text_itgc(answers, 'APD01')) # 사용자 권한 승인
        create_itgc_sheet(writer, 'APD02', get_text_itgc(answers, 'APD02')) # 부서이동자 권한 회수
        create_itgc_sheet(writer, 'APD03', get_text_itgc(answers, 'APD03')) # 퇴사자 접근권한 회수
        create_itgc_sheet(writer, 'APD04', get_text_itgc(answers, 'APD04')) # 사용자 권한 Monitoring
        create_itgc_sheet(writer, 'APD05', get_text_itgc(answers, 'APD05')) # Application 패스워드
        create_itgc_sheet(writer, 'APD06', get_text_itgc(answers, 'APD06')) # 데이터 직접 변경
        create_itgc_sheet(writer, 'APD07', get_text_itgc(answers, 'APD07')) # DB 접근권한 승인
        create_itgc_sheet(writer, 'APD08', get_text_itgc(answers, 'APD08')) # DB 관리자 권한 제한
        create_itgc_sheet(writer, 'APD09', get_text_itgc(answers, 'APD09')) # DB 패스워드
        create_itgc_sheet(writer, 'APD10', get_text_itgc(answers, 'APD10')) # OS 접근권한 승인
        create_itgc_sheet(writer, 'APD11', get_text_itgc(answers, 'APD11')) # OS 관리자 권한 제한
        create_itgc_sheet(writer, 'APD12', get_text_itgc(answers, 'APD12')) # OS 패스워드
        create_itgc_sheet(writer, 'PC01', get_text_itgc(answers, 'PC01'))  # 프로그램 변경 승인
        create_itgc_sheet(writer, 'PC02', get_text_itgc(answers, 'PC02'))  # 프로그램 변경 사용자 테스트
        create_itgc_sheet(writer, 'PC03', get_text_itgc(answers, 'PC03'))  # 프로그램 변경 이관 승인
        create_itgc_sheet(writer, 'PC04', get_text_itgc(answers, 'PC04'))  # 이관(배포) 권한 제한
        create_itgc_sheet(writer, 'PC05', get_text_itgc(answers, 'PC05'))  # 개발/운영 환경 분리
        create_itgc_sheet(writer, 'CO01', get_text_itgc(answers, 'CO01'))  # 배치 스케줄 등록/변경 승인
        create_itgc_sheet(writer, 'CO02', get_text_itgc(answers, 'CO02'))  # 배치 스케줄 등록/변경 권한 제한
        create_itgc_sheet(writer, 'CO03', get_text_itgc(answers, 'CO03'))  # 배치 실행 모니터링
        create_itgc_sheet(writer, 'CO04', get_text_itgc(answers, 'CO04'))  # 장애 대응 절차
        create_itgc_sheet(writer, 'CO05', get_text_itgc(answers, 'CO05'))  # 백업 및 모니터링
        create_itgc_sheet(writer, 'CO06', get_text_itgc(answers, 'CO06'))  # 서버실 출입 절차

    return send_file(file_path, as_attachment=True)
    
def create_itgc_sheet(writer, sheet_name, text_data):
    df = pd.DataFrame({'Interview 내용': text_data})
    df.to_excel(writer, sheet_name=sheet_name, index=False)

def get_text_itgc(answers, control_number):
    text = []
    
    if control_number == 'APD01':
        text.append("APD01 - 사용자 신규 권한 승인")
        text.append("사용자 권한 부여 이력이 시스템에 기록되고 있습니다." if answers[11] == 'Y' else "사용자 권한 부여 이력이 시스템에 기록되지 않습니다.")
        if answers[13] == 'Y':
            text.append("새로운 권한 요청 시, 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니다.")
            text.append(f"권한이 부여되는 절차: {answers[14]}" if answers[14] else "권한 부여 절차에 대한 상세 기술이 제공되지 않았습니다.")
        else:
            text.append("새로운 권한 요청 시 승인 절차가 없습니다.")
            
    elif control_number == 'APD02':
        text.append("APD02 - 부서이동자 권한 회수")
        text.append("사용자 권한 회수 이력이 시스템에 기록되고 있습니다." if answers[12] == 'Y' else "사용자 권한 회수 이력이 시스템에 기록되지 않습니다.")
        if answers[15] == 'Y':
            text.append("부서 이동 시 기존 권한을 회수하는 절차가 있습니다.")
            text.append(f"부서 이동 시 권한 회수 절차: {answers[16]}" if answers[16] else "부서 이동 시 권한 회수 절차에 대한 상세 기술이 제공되지 않았습니다.")
        else:
            text.append("부서 이동 시 기존 권한 회수 절차가 없습니다.")
            
    elif control_number == 'APD03':
        text.append("APD03 - 퇴사자 접근권한 회수")
        text.append("퇴사자 발생 시 접근권한을 차단하는 절차가 있습니다." if answers[17] == 'Y' else "퇴사자 발생 시 접근권한 차단 절차가 없습니다.")
        if answers[18]:
            text.append(f"퇴사자 접근권한 차단 절차: {answers[18]}")
        else:
            text.append("퇴사자 접근권한 차단 절차에 대한 상세 기술이 제공되지 않았습니다.")
            
    elif control_number == 'APD04':
        text.append("APD04 - 사용자 권한 Monitoring")
        text.append("전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니다." if answers[19] == 'Y' else "전체 사용자가 보유한 권한에 대한 모니터링 절차가 존재하지 않습니다.")
        
    elif control_number == 'APD05':
        text.append("APD05 - Application 패스워드")
        text.append(f"패스워드 설정 사항: {answers[20]}")
        
    elif control_number == 'APD06':
        text.append("APD06 - 데이터 직접 변경")
        text.append("데이터 변경 이력이 시스템에 기록되고 있습니다." if answers[21] == 'Y' else "데이터 변경 이력이 시스템에 기록되지 않습니다.")
        text.append("데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니다." if answers[22] == 'Y' else "데이터 변경이 필요한 경우 승인 절차가 존재하지 않습니다.")
        
    elif control_number == 'APD07':
        text.append("APD07 - DB 접근권한 승인")
        text.append(f"DB 종류와 버전: {answers[8]}")
        text.append(f"DB 접근제어 Tool 사용 여부: {'사용 중' if answers[9] == 'Y' else '사용하지 않음'}")
        text.append("DB 접근권한 부여 이력이 시스템에 기록되고 있습니다." if answers[23] == 'Y' else "DB 접근권한 부여 이력이 시스템에 기록되지 않습니다.")
        text.append("DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니다." if answers[24] == 'Y' else "DB 접근권한이 필요한 경우 승인 절차가 존재하지 않습니다.")
        
    elif control_number == 'APD08':
        text.append("APD08 - DB 관리자 권한 제한")
        text.append(f"DB 관리자 권한을 보유한 인원: {answers[25]}")
        
    elif control_number == 'APD09':
        text.append("APD09 - DB 패스워드")
        text.append(f"DB 패스워드 설정사항: {answers[26]}")
        
    elif control_number == 'APD10':
        text.append("APD10 - OS 접근권한 승인")
        text.append(f"OS 종류와 버전: {answers[6]}")
        text.append(f"OS 접근제어 Tool 사용 여부: {'사용 중' if answers[7] == 'Y' else '사용하지 않음'}")
        text.append("OS 접근권한 부여 이력이 시스템에 기록되고 있습니다." if answers[27] == 'Y' else "OS 접근권한 부여 이력이 시스템에 기록되지 않습니다.")
        text.append("OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니다." if answers[28] == 'Y' else "OS 접근권한이 필요한 경우 승인 절차가 존재하지 않습니다.")
        
    elif control_number == 'APD11':
        text.append("APD11 - OS 관리자 권한 제한")
        text.append(f"OS 관리자 권한을 보유한 인원: {answers[29]}")
        
    elif control_number == 'APD12':
        text.append("APD12 - OS 패스워드")
        text.append(f"OS 패스워드 설정사항: {answers[30]}")
        
    elif control_number == 'PC01':
        text.append("PC01 - 프로그램 변경 승인")
        text.append("프로그램 변경 이력이 시스템에 기록되고 있습니다." if answers[31] == 'Y' else "프로그램 변경 이력이 시스템에 기록되지 않습니다.")
        if answers[32] == 'Y':
            text.append("프로그램 변경 시 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니다.")
        else:
            text.append("프로그램 변경 시 승인 절차가 없습니다.")
            
    elif control_number == 'PC02':
        text.append("PC02 - 프로그램 변경 사용자 테스트")
        if answers[33] == 'Y':
            text.append("프로그램 변경 시 사용자 테스트를 수행하고 결과를 문서화하는 절차가 있습니다.")
        else:
            text.append("프로그램 변경 시 사용자 테스트 수행 및 문서화 절차가 없습니다.")
            
    elif control_number == 'PC03':
        text.append("PC03 - 프로그램 변경 이관 승인")
        if answers[34] == 'Y':
            text.append("프로그램 변경 완료 후 이관(배포)을 위해 부서장의 승인을 득하는 절차가 있습니다.")
        else:
            text.append("프로그램 변경 완료 후 별도의 승인 절차가 없습니다.")
            
    elif control_number == 'PC04':
        text.append("PC04 - 이관(배포) 권한 제한")
        if answers[35]:
            text.append(f"이관(배포) 권한을 보유한 인원: {answers[35]}")
        else:
            text.append("이관(배포) 권한 보유 인원에 대한 정보가 제공되지 않았습니다.")
            
    elif control_number == 'PC05':
        text.append("PC05 - 개발/운영 환경 분리")
        if answers[36] == 'Y':
            text.append("운영 서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니다.")
        else:
            text.append("운영 서버 외 추가적인 개발 또는 테스트 서버가 없습니다.")
            
    elif control_number == 'CO01':
        text.append("CO01 - 배치 스케줄 등록/변경 승인")
        text.append("배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니다." if answers[37] == 'Y' else "배치 스케줄 등록/변경 이력이 시스템에 기록되지 않습니다.")
        if answers[38] == 'Y':
            text.append("배치 스케줄 등록/변경 시 요청서 작성 및 승인 절차가 있습니다.")
        else:
            text.append("배치 스케줄 등록/변경 시 승인 절차가 없습니다.")
            
    elif control_number == 'CO02':
        text.append("CO02 - 배치 스케줄 등록/변경 권한 제한")
        text.append(f"배치 스케줄 등록/변경 담당자: {answers[39]}" if answers[39] else "배치 스케줄 등록/변경 담당자 정보가 제공되지 않았습니다.")
        
    elif control_number == 'CO03':
        text.append("CO03 - 배치 실행 모니터링")
        text.append(f"배치 실행 오류 모니터링: {answers[40]}" if answers[40] else "배치 실행 오류 모니터링 정보가 제공되지 않았습니다.")
        
    elif control_number == 'CO04':
        text.append("CO04 - 장애 대응 절차")
        text.append(f"장애 발생시 대응 절차: {answers[41]}" if answers[41] else "장애 대응 절차 정보가 제공되지 않았습니다.")
        
    elif control_number == 'CO05':
        text.append("CO05 - 백업 및 모니터링")
        text.append(f"백업 수행 및 모니터링: {answers[42]}" if answers[42] else "백업 및 모니터링 정보가 제공되지 않았습니다.")
        
    elif control_number == 'CO06':
        text.append("CO06 - 서버실 출입 절차")
        text.append(f"서버실 출입 절차: {answers[43]}" if answers[43] else "서버실 출입 절차 정보가 제공되지 않았습니다.")
        
    else:
        text.append(f"Unknown control number: {control_number}")
    
    return text

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

if __name__ == '__main__':
    main()