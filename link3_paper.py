import openpyxl

def paper_generate(form_data):
    print("Paper Generate called")

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

    if param2 == "APD05":
        workbook = openpyxl.load_workbook('./paper_templates/APD05_template.xlsx')
        sheet = workbook["Testing Table"]
        sheet["F4"] = param3
        sheet["F5"] = param4
        sheet["F6"] = param5
        
    output_path = './paper_templates/' + param2 + '.xlsx'
    workbook.save(output_path)
    workbook.close()

    print("output = ", output_path)

    return output_path