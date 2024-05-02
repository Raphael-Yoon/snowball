from flask import Flask, render_template, request, send_file
from openpyxl import load_workbook
#import ssl

import link1_pbc
import link2_rcm
import link3_paper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.jsp")

def main():
    #app.debug = True
    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem', password='1234')
    #app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context)
    app.run(host='0.0.0.0', debug=False, port=5000)
    #app.run(host='127.0.0.1', debug=False, port=8001)

@app.route('/link0')
def link0():
    print("Reload")
    return render_template('index.jsp')

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

@app.route('/paper_template_download', methods=['POST'])
def paper_template_download():

    form_data = request.form.to_dict()
    output_path = link3_paper.paper_template_download(form_data)

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
    output_path = link3_paper.paper_generate(form_data)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    main()