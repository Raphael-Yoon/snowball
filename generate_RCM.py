from flask import Flask, render_template, request, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("test.html")

def main():
    app.run(host='127.0.0.1', debug=False, port=80)

@app.route('/calculate', methods=['POST'])
def calculate():
    print("Python function called")
    form_data = request.form.to_dict()

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')

    print("Param1 = ", param1)
    print("Param2 = ", param2)

    df = pd.read_excel('ITGC_template.xlsx', engine='openpyxl')
    pbc_df = df[df['Major P. Name']==param1]

    output_path = 'pbc.xlsx'
    pbc_df.to_excel(output_path, index=False)
    print(pbc_df)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    main()