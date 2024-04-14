from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import openpyxl

def paper_template_download(form_data):
    print("Paper Template called")

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')
    param3 = form_data.get('param3')
    param4 = form_data.get('param4')
    param5 = form_data.get('param5')

    print("Param1 = ", param1)
    print("Param2 = ", param2)
    print("Param3 = ", param3)
    print("Param4 = ", param4)
    print("Param5 = ", param5)

    workbook = openpyxl.load_workbook('./paper_templates/APD05_template.xlsx')
        
    output_path = './paper_templates/' + param2 + '.xlsx'
    workbook.save(output_path)
    workbook.close()

    print("output = ", output_path)

    return output_path

def paper_generate(form_data):
    print("Paper Generate called")

    param3 = form_data.get('param3')
    param4 = form_data.get('param4')

    print("Param3 = ", param3)
    print("Param4 = ", param4)

    uploaded_file = request.files['param4']
    print('upload 1')
    filename = secure_filename(uploaded_file.filename)
    print('upload 2')
    file_path = os.path.join('uploads', uploaded_file.filename)
    print('upload 3')
    uploaded_file.save(file_path)
    print('upload complete')

    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook['모집단']
    a1_value = sheet['A1'].value
    print("A1 = ", a1_value)
        
    #output_path = './paper_templates/' + param2 + '.xlsx'
    output_path = ''
    workbook.save(output_path)
    workbook.close()

    print("output = ", output_path)

    return output_path