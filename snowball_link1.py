from datetime import datetime
import os
from io import BytesIO
from openpyxl import load_workbook

def generate_and_send_rcm_excel(form_data, send_gmail_with_attachment):
    """
    form_data: dict (Flask의 request.form.to_dict())
    send_gmail_with_attachment: 메일 전송 함수 (to, subject, body, file_stream, file_name)
    """
    # 파일명 생성: 입력받은 파일명(param2)_RCM_YYMMDD.xlsx
    base_name = form_data.get('param2', 'output')
    today = datetime.today().strftime('%y%m%d')
    file_name = f"{base_name}_ITGC_RCM_{today}.xlsx"
    # 엑셀 파일 생성 (템플릿 사용)
    excel_stream = BytesIO()
    template_path = os.path.join("static", "Design_Template.xlsx")
    wb = load_workbook(template_path)
    wb.save(excel_stream)
    wb.close()
    excel_stream.seek(0)

    # 담당자 user_id는 param1
    user_email = form_data.get('param1')

    if user_email:
        subject = 'RCM 자동생성 결과 파일'
        body = '요청하신 RCM 자동생성 엑셀 파일을 첨부합니다.'
        try:
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
    else:
        return False, None, '메일 주소가 없습니다. 담당자 정보를 확인해 주세요.' 