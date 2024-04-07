from flask import Flask, render_template, request, send_file
from openpyxl import load_workbook

import link1_pbc
import link2_rcm

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.jsp")

def main():
    app.run(host='0.0.0.0', debug=False, port=8001)
    #app.run(host='127.0.0.1', debug=False, port=8001)

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
    print("ETC Function")
    return render_template('link4.jsp')

@app.route('/pbc_generate', methods=['POST'])
def pbc_generate():
    form_data = request.form.to_dict()

    output_path = link1_pbc.pbc_generate(form_data)

    return send_file(output_path, as_attachment=True)

@app.route('/rcm_generate', methods=['POST'])
def rcm_generate():
    print("RCM Generate called")

    form_data = request.form.to_dict()

    output_path = link2_rcm.rcm_generate(form_data)

    #return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    main()