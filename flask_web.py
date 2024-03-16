from flask import Flask, render_template, request, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

def main():
    app.run(host='0.0.0.0', debug=False, port=8001)

@app.route('/calculate', methods=['POST'])
def calculate():
    print("Python function called")
    form_data = request.form.to_dict()

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')

    print("Param1 = ", param1)
    print("Param2 = ", param2)

    df = pd.read_excel('ITGC_template.xlsx', engine='openpyxl')
    df1 = df[df['Major P. Name']==param1]
    df2 = df[df['Major P. Name']==param2]

    output_path = 'pbc.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        df1.to_excel(writer, sheet_name=param1, index=False)
        df2.to_excel(writer, sheet_name=param2, index=False)
    
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    main()