from flask import Flask, render_template, request, send_file, session
from openpyxl import load_workbook

import link_admin
import link1_pbc
import link2_design
import link3_operation
import snowball_db

app = Flask(__name__)

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
    return render_template('link.jsp', user_request = result)

@app.route('/link0')
def link0():
    print("Reload")
    return render_template('link0.jsp')

@app.route('/link1')
def link1():
    print("PBC Function")
    return render_template('link1.jsp')

@app.route('/link2')
def link2():
    print("RCM Function")
    return render_template('link2.jsp')

@app.route('/link3')
def link3():
    print("Paper Function")
    return render_template('link3.jsp')

@app.route('/link4')
def link4():
    print("Monitoring Function")
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
        return render_template('link0.jsp', login_code = 0)
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
    

@app.route('/pbc_generate', methods=['POST'])
def pbc_generate():

    form_data = request.form.to_dict()
    output_path = link1_pbc.pbc_generate(form_data)

    return send_file(output_path, as_attachment=True)

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