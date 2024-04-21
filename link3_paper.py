from flask import Flask, request
import openpyxl.utils
from werkzeug.utils import secure_filename
import os
import openpyxl
import random

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

    output_path = './paper_templates/' + param2 + '.xlsx'

    #workbook = openpyxl.load_workbook('./paper_templates/APD05_template.xlsx')
        
    #output_path = './paper_templates/' + param2 + '.xlsx'
    #workbook.save(output_path)
    #workbook.close()

    print("output = ", output_path)

    return output_path

def paper_generate(form_data):
    print("Paper Generate called")

    param3 = form_data.get('param3')
    param4 = form_data.get('param4')
    param5 = form_data.get('param5')

    print("Param3 = ", param3)
    print("Param4 = ", param4)
    print("Param5 = ", param5)

    uploaded_file = request.files['param4']
    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join('uploads', uploaded_file.filename)
    uploaded_file.save(file_path)
    print('upload complete')

    if(param3=="APD01"):
        #output_path = paper_generate_population(param3, file_path)
        #output_path = paper_generate_apd01(output_path)
        paper_test()
    else:
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

def paper_generate_population(control_code, upload_file):
    print("into paper generate population")
    
    open_path = './paper_templates/' + control_code + '_paper.xlsx'

    paper_workbook = openpyxl.load_workbook(open_path)
    paper_sheet = paper_workbook['Population']

    upload_workbook = openpyxl.load_workbook(upload_file)
    upload_sheet = upload_workbook['모집단']

    for row in upload_sheet.iter_rows():
        for cell in row:
            paper_sheet[cell.coordinate].value = cell.value
    
    output_path = './uploads/' + control_code + '_paper.xlsx'
    paper_workbook.save(output_path)
    paper_workbook.close()
    
    print("end papaer generate population")
    
    return output_path

def paper_generate_apd01(output_path):
    print("into paper generate apd01")

    paper_workbook = openpyxl.load_workbook('./uploads/APD01_paper.xlsx')
    paper_sheet = paper_workbook['Testing Table']
    paper_sheet["C5"] = "Test"

    paper_workbook.save(output_path)
    paper_workbook.close()
    
    print("end papaer generate apd01")
    
    return output_path

def paper_test():
    print("into paper_test")
    paper_workbook = openpyxl.load_workbook('./uploads/APD01_paper.xlsx')
    sheet_pop = paper_workbook['Population']
    sheet_test = paper_workbook['Testing Table']

    mapping_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    sample_col = mapping_list[sheet_pop.max_column]
    max_row = sheet_pop.max_row
    sample_size = 0
    if(max_row > 250): # multiple
        sample_size = 25
    elif(max_row > 52): # daily
        sample_size = 15
    elif(max_row > 12): # weekly
        sample_size = 2
    elif(max_row > 4): # monthly
        sample_size = 2
    elif(max_row > 1): # quarterly
        sample_size = 2
    else: # annually
        sample_size = 1

    print("max_row = ", max_row)
    print("sample_col = ", sample_col)
    print("sample Size = ", sample_size)

    random_row_indices = random.sample(range(1, max_row), sample_size)
    selected_row_data = []

    i=1
    for row_index in random_row_indices:
        row_data = [cell.value for cell in sheet_pop[row_index]]
        selected_row_data.append(row_data)
        sheet_pop[sample_col+str(row_index)] = "Sample #" + str(i)
        i=i+1
    print("Random index = ", random_row_indices)
    print("Selected:")
    i=5
    for row_data in selected_row_data:
        print(row_data)
        sheet_test["C" + str(i)] = row_data[0] # 사용자ID
        sheet_test["D" + str(i)] = row_data[1] # 사용자명
        sheet_test["E" + str(i)] = row_data[2] # 부서명
        sheet_test["F" + str(i)] = row_data[3] # 권한명
        sheet_test["G" + str(i)] = row_data[4] # 권한부여일
        i=i+1
    
    paper_workbook.save('./uploads/APD01_paper.xlsx')
    paper_workbook.close()