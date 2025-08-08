from datetime import datetime
import os
from io import BytesIO
from openpyxl import load_workbook
from snowball_mail import send_gmail_with_attachment

def generate_and_send_rcm_excel(form_data):
    """
    form_data: dict (Flask의 request.form.to_dict())
    RCM 엑셀 파일을 생성하고 이메일로 전송
    """
    # 파라미터 출력
    print("=== RCM Generate 파라미터 ===")
    print(f"param1 (email): {form_data.get('param1', 'N/A')}")
    print(f"param2 (system_name): {form_data.get('param2', 'N/A')}")
    print(f"param3 (system_type): {form_data.get('param3', 'N/A')}")
    print(f"param4 (os_type): {form_data.get('param4', 'N/A')}")
    print(f"param5 (db_type): {form_data.get('param5', 'N/A')}")
    print("=============================")
    
    # 파일명 생성: 입력받은 파일명(param2)_RCM_YYMMDD.xlsx
    base_name = form_data.get('param2', 'output')
    today = datetime.today().strftime('%y%m%d')
    file_name = f"{base_name}_ITGC_RCM_{today}.xlsx"
    
    # 엑셀 파일 생성 (템플릿 사용)
    excel_stream = BytesIO()
    template_path = os.path.join("static", "RCM_Generate.xlsx")
    wb = load_workbook(template_path)
    
    # RCM 시트에서 파라미터에 따라 행 필터링
    if 'RCM' in wb.sheetnames:
        ws = wb['RCM']
        rows_to_delete = []
        
        # 2행부터 시작 (헤더 제외)
        for row_num in range(2, ws.max_row + 1):
            section_col = ws[f'B{row_num}'].value  # B컬럼 (Section)
            value_col = ws[f'C{row_num}'].value    # C컬럼 (Value)
            
            # B컬럼이 Common인 경우는 유지
            if section_col == 'Common':
                continue
            
            # B컬럼이 APP인 경우 param3와 비교
            elif section_col == 'APP':
                if value_col != form_data.get('param3'):
                    rows_to_delete.append(row_num)
            
            # B컬럼이 OS인 경우 param4와 비교
            elif section_col == 'OS':
                if value_col != form_data.get('param4'):
                    rows_to_delete.append(row_num)
            
            # B컬럼이 DB인 경우 param5와 비교
            elif section_col == 'DB':
                if value_col != form_data.get('param5'):
                    rows_to_delete.append(row_num)
        
        # 역순으로 행 삭제 (인덱스 변화 방지)
        for row_num in sorted(rows_to_delete, reverse=True):
            ws.delete_rows(row_num)
        
        print(f"필터링 완료: {len(rows_to_delete)}개 행 삭제됨")
            
    wb.save(excel_stream)
    wb.close()
    excel_stream.seek(0)

    # 이메일 전송
    user_email = form_data.get('param1')
    if not user_email:
        return False, None, "이메일 주소가 없습니다."

    try:
        subject = 'RCM 자동생성 결과 파일'
        body = '요청하신 RCM 자동생성 엑셀 파일을 첨부합니다.'
        send_gmail_with_attachment(
            to=user_email,
            subject=subject,
            body=body,
            file_stream=excel_stream,
            file_name=file_name
        )
        return True, user_email, None
    except Exception as e:
        return False, user_email, str(e)