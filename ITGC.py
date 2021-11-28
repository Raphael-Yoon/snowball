from io import BytesIO
import pandas as pd
import re

def set_RCM(data, output_excel, in_section1, in_section2, in_system_name):
    data_list = data['Section1'].values.tolist()
    #print(data['구분1'])
    #print(data_list)
    print("section1 = {}, section2 = {}".format(in_section1, in_section2))

    for i in range(0, len(data_list)):
        if(data['Section1'][i] == in_section1):
            print(data['통제명'][i])

            new_dic = {'Mega P. Name' : data['Mega P. Name'][i]}
            new_dic['Major P. Name'] = data['Major P. Name'][i]
            new_dic['Sub P. Name'] = data['Sub P. Name'][i]
            new_dic['위험명'] = data['위험명'][i]
            new_dic['통제명'] = data['통제명'][i]
            new_dic['통제설명'] = data['통제설명'][i]
            new_dic['통제구분'] = data['통제구분'][i]
            if(in_section2 == 'Legacy'):
                new_dic['시스템'] = in_system_name
            else:
                new_dic['시스템'] = data['시스템'][i]
            new_dic['통제주기'] = data['통제주기'][i]
            new_dic['모집단'] = data['모집단'][i]
            new_dic['테스트 절차'] = data['테스트 절차'][i]
            new_dic['모범규준'] = data['모범규준'][i]

            output_excel = output_excel.append(new_dic, ignore_index=True)
    
    return output_excel

def main_func():
    data = pd.read_excel('Template.xlsx', sheet_name='RCM').fillna('')
    output_excel = pd.read_excel('empty.xlsx', sheet_name='RCM')
    #output_excel = set_RCM(data, output_excel, '공통', '')
    output_excel = set_RCM(data, output_excel, 'APP', '')
    output_excel.to_excel('RCM.xlsx', sheet_name='RCM', index=False)

print("Start")
main_func()
print("End")