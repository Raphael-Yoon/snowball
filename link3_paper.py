def paper_generate(form_data):
    print("Paper Generate called")

    param1 = form_data.get('param1')
    param2 = form_data.get('param2')

    print("Param1 = ", param1)
    print("Param2 = ", param2)

    output_path = 'rcm.xlsx'
    
    return output_path