from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, current_user
from openpyxl import load_workbook

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
    app.run(host='0.0.0.0', debug=False, port=5000)
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
    {'index': 1, 'text': '사용하고 있는 시스템 종류는?'},
    {'index': 2, 'text': '사용하고 있는 OS 종류는?'},
    {'index': 3, 'text': '사용하고 있는 DB 종류는?'},
    {'index': 4, 'text': 'OS 접근제어 Tool 사용 여부'},
    {'index': 5, 'text': 'DB 접근제어 Tool 사용 여부'},
    {'index': 6, 'text': 'Batch Schedule Tool 사용 여부'}
]

@app.route('/link2', methods=['GET', 'POST'])
def link2():
    print("Question Function")

    if request.method == 'GET':
        # 세션을 열 때마다 초기화
        session.clear()  # 모든 세션 값 초기화
        session['question_index'] = 0
        session['answers'] = []

    question_index = session['question_index']
    question = s_questions[question_index]

    # POST 요청 처리 (다음 버튼을 눌렀을 때)
    if request.method == 'POST':
        form_data = request.form

        s_q1 = form_data.get("s_q1")
        s_q2 = form_data.get("s_q2")
        s_q3 = form_data.get("s_q3")
        s_q4 = form_data.get("s_q4")
        s_q5 = form_data.get("s_q5")
        s_q6 = form_data.get("s_q6")
        print(f"s_q1: {s_q1}, s_q2: {s_q2}, s_q3: {s_q3}, s_q4: {s_q4}, s_q5: {s_q5}, s_q6: {s_q6}")
        print('index = ', session['question_index'])
        answer_key = f's_q{question_index + 1}'  # ex) 's_q1', 's_q2', ...
        answer_value = form_data.get(answer_key)

        # 다음 질문으로 이동
        session['question_index'] += 1

        # 모든 질문이 끝나면 결과 페이지로 이동
        if session['question_index'] >= len(s_questions):
            return redirect(url_for('result'))

    # 현재 질문을 렌더링
    question = s_questions[session['question_index']]

    return render_template('link2.jsp', question=question['text'], question_number=session['question_index'] + 1)

@app.route('/result')
def result():
    return render_template('result.jsp', answers=session.get('answers', []))

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