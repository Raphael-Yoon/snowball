from flask import Blueprint, request, render_template, session, url_for, jsonify
from datetime import datetime
import os
import json
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from auth import log_user_activity, login_required
from openai import OpenAI

# Blueprint 생성
bp_link1_1 = Blueprint('link1_1', __name__)

# ================================
# 마스터 통제 항목 정의 (표준 ITGC 36개)
# ================================
MASTER_ITGC_CONTROLS = [
    {"id": "PWC01", "name": "IT 정책서 관리", "category": "IT정책", "objective": "IT 정책의 명문화 및 준수 보장"},
    {"id": "APD01", "name": "Application 권한 승인", "category": "계정관리", "objective": "인가된 사용자에게 적절한 권한 부여"},
    {"id": "APD02", "name": "Application 부서이동자 권한 회수", "category": "계정관리", "objective": "이동 시 불필요 권한 즉시 회수"},
    {"id": "APD03", "name": "Application 퇴사자 접근권한 회수", "category": "계정관리", "objective": "퇴사자 시스템 접근 차단"},
    {"id": "APD04", "name": "Application 권한 Monitoring", "category": "계정관리", "objective": "권한 부여의 적정성 주기적 검토"},
    {"id": "APD05", "name": "Application 관리자 권한 제한", "category": "계정관리", "objective": "관리자 권한 오남용 방지"},
    {"id": "APD06", "name": "Application 패스워드", "category": "계정관리", "objective": "강력한 인증 체계 유지"},
    {"id": "APD07", "name": "Data 변경 승인", "category": "데이터관리", "objective": "DB 데이터 직접 변경의 승인 체계 확보"},
    {"id": "APD08", "name": "Data 변경 권한 제한", "category": "데이터관리", "objective": "DB 직접 접근 권한 제한"},
    {"id": "APD09", "name": "OS 접근권한 승인", "category": "OS관리", "objective": "서버 인프라 접근 승인 절차 준수"},
    {"id": "APD10", "name": "OS 패스워드", "category": "OS관리", "objective": "인프라 계정 보안 강화"},
    {"id": "APD11", "name": "OS 관리자 권한 제한", "category": "OS관리", "objective": "서버 관리자 권한 최소화"},
    {"id": "APD12", "name": "DB 접근권한 승인", "category": "DB관리", "objective": "DB 접근 승인 절차 준수"},
    {"id": "APD13", "name": "DB 패스워드", "category": "DB관리", "objective": "DB 계정 보안 강화"},
    {"id": "APD14", "name": "DB 관리자 권한 제한", "category": "DB관리", "objective": "DB 관리자 권한 최소화"},
    {"id": "PC01", "name": "프로그램 변경 승인", "category": "변경관리", "objective": "프로그램 변경 전 승인 득함"},
    {"id": "PC02", "name": "프로그램 변경 사용자 테스트", "category": "변경관리", "objective": "사용자 검증을 통한 품질 확보"},
    {"id": "PC03", "name": "프로그램 변경 이관 승인", "category": "변경관리", "objective": "운영 반영 전 최종 승인 확인"},
    {"id": "PC04", "name": "개발/운영 환경의 분리", "category": "변경관리", "objective": "개발과 운영 독립성 확보"},
    {"id": "PC05", "name": "이관담당자 권한 제한", "category": "변경관리", "objective": "배포 권한의 분리 및 최소화"},
    {"id": "PC06", "name": "OS 설정변경", "category": "변경관리", "objective": "인프라 설정 변경의 통제"},
    {"id": "PC07", "name": "DB 설정변경", "category": "변경관리", "objective": "DB 설정 변경의 통제"},
    {"id": "CO01", "name": "Batch Schedule 등록/변경 요청 및 승인", "category": "운영관리", "objective": "배치 작업 변경의 무결성 확보"},
    {"id": "CO02", "name": "Batch Schedule 등록/변경 권한 제한", "category": "운영관리", "objective": "스케줄링 권한 오남용 방지"},
    {"id": "CO03", "name": "Batch Schedule 모니터링", "category": "운영관리", "objective": "배치 작업 실패 시 적시 대응"},
    {"id": "CO04", "name": "백업 모니터링", "category": "운영관리", "objective": "백업 성공 여부 모니터링"},
    {"id": "CO05", "name": "장애 관리", "category": "운영관리", "objective": "시스템 장애 기록 및 원인 분석"},
    {"id": "CO06", "name": "데이터센터 접근 제한", "category": "운영관리", "objective": "서버실 물리적 출입 통제"},
    {"id": "PD01", "name": "사용자 인수 테스트", "category": "개발관리", "objective": "최종 사용자의 시스템 수용 검증"},
    {"id": "PD02", "name": "데이터 이관", "category": "개발관리", "objective": "이관 데이터의 완전성 및 정확성 보장"},
    {"id": "PD03", "name": "이슈 관리", "category": "개발관리", "objective": "개발 이슈의 누적 관리 및 해결"},
    {"id": "PD04", "name": "사용자 교육", "category": "개발관리", "objective": "운영 준비를 위한 사용자 교육 실시"},
    {"id": "ST01", "name": "Supporting Tool Super User 권한 제한", "category": "지원툴관리", "objective": "보조 툴 관리자 권한 통제"},
    {"id": "ST02", "name": "Supporting Tool 패스워드 설정", "category": "지원툴관리", "objective": "보조 툴 보안 설정 유지"},
    {"id": "ST03", "name": "Supporting Tool 기능 변경 요청 및 승인", "category": "지원툴관리", "objective": "지원 도구 변경의 이력 관리"},
    {"id": "PWC02", "name": "정보보안 교육", "category": "IT정책", "objective": "전사 보안 의식 함양 및 법적 준수"},
]

def get_user_info():
    """현재 로그인한 사용자 정보 반환"""
    if 'user_id' in session:
        return session.get('user_info')
    return None

# ================================
# AI 엔진: 통제 활동 자동 생성
# ================================
def generate_ai_rcm_content(system_info):
    """
    AI를 사용하여 시스템 환경에 맞는 통제 활동 및 기술적 증적 생성
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {"error": "API Key not found"}

    client = OpenAI(api_key=api_key)
    
    # 컨텍스트 요약
    context = (
        f"시스템명: {system_info.get('system_name')}, "
        f"유형: {system_info.get('system_type')}, "
        f"SW: {system_info.get('software')}, "
        f"OS: {system_info.get('os')}, "
        f"DB: {system_info.get('db')}"
    )

    prompt = f"""당신은 IT 감사 및 ITGC 전문가입니다.
다음 시스템 환경에 대해 주어진 ITGC 통제 항목별 '통제 활동'과 '테스트 절차'를 생성하십시오.

[시스템 환경]
{context}

[작성 지침]
1. 각 통제 항목에 대해 해당 기술 스택에 적합한 '기술적 증적(Technical Objects)'을 명시하십시오.
   - 예: SAP -> SU01, PFCG, STAD, SE16
   - 예: Oracle ERP -> FND_USER, FND_RESPONSIBILITY, AD_APPL_TOP
   - 예: DB가 Oracle일 경우 → DBA_USERS, DBA_TAB_PRIVS, Audit Trail
   - 예: Linux일 경우 → /etc/passwd, sudoers, syslog
2. 시스템 유형(System Type)에 따라 다음 통제 범위를 적용하십시오:
   - In-house (자체개발): 개발 및 변경관리(SDLC) 전체 통제 항목을 상세히 포함.
   - Package-Modifiable: 패키지 표준 기능 + 커스터마이징 영역에 대한 변경 통제 포함.
   - Package-Non-modifiable: 운영 및 권한 통제 위주로 작성하고, 개발/변경 통제는 제외하거나 최소화.
3. 응답은 반드시 아래 JSON 형식으로만 작성하십시오.

[JSON 형식]
{{
  "controls": [
    {{
      "id": "APD01",
      "activity": "통제 활동 내용...",
      "procedure": "테스트 절차 내용..."
    }},
    ...
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 IT 전문 감사인이며 정확한 기술 용어를 사용합니다."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ================================
# Blueprint 라우트
# ================================

@bp_link1_1.route('/link1_1')
def link1_1():
    """AI RCM Builder 메인 페이지"""
    user_info = get_user_info()
    users = user_info['user_name'] if user_info else "Guest"
    user_email = user_info.get('user_email', '') if user_info else ''

    return render_template('link1_1.jsp',
                         users=users,
                         is_logged_in='user_id' in session,
                         user_info=user_info,
                         user_email=user_email,
                         master_controls=MASTER_ITGC_CONTROLS)

@bp_link1_1.route('/api/rcm/ai_generate', methods=['POST'])
@login_required
def api_rcm_ai_generate():
    """AI를 통한 RCM 내용 생성 API"""
    data = request.json
    result = generate_ai_rcm_content(data)
    
    if "error" in result:
        return jsonify({"success": False, "message": result["error"]}), 500
        
    return jsonify({"success": True, "data": result["controls"]})

@bp_link1_1.route('/api/rcm/export_excel', methods=['POST'])
@login_required
def api_rcm_export_excel():
    """최종 RCM 엑셀 내보내기"""
    data = request.json
    rcm_data = data.get('rcm_data', [])
    system_info = data.get('system_info', {})
    
    wb = load_workbook(os.path.join("static", "RCM_Generate.xlsx")) if os.path.exists(os.path.join("static", "RCM_Generate.xlsx")) else load_workbook(os.path.join("static", "RCM_Template_Base.xlsx")) if os.path.exists(os.path.join("static", "RCM_Template_Base.xlsx")) else None
    
    if not wb:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "RCM"
    else:
        if "RCM" in wb.sheetnames:
            ws = wb["RCM"]
            # 기존 데이터 정리 (2행부터 삭제)
            if ws.max_row >= 2:
                ws.delete_rows(2, ws.max_row - 1)
        else:
            ws = wb.create_sheet("RCM")

    # 헤더 작성 (간소화된 RCM 양식)
    headers = ["통제 ID", "통제 항목명", "통제 목적", "통제 활동 내용", "테스트 절차", "통제 주기", "통제 담당자"]
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)
        # 스타일 적용
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # 데이터 작성
    for row_idx, item in enumerate(rcm_data, 2):
        ws.cell(row=row_idx, column=1, value=item.get('id'))
        ws.cell(row=row_idx, column=2, value=item.get('name'))
        ws.cell(row=row_idx, column=3, value=item.get('objective'))
        ws.cell(row=row_idx, column=4, value=item.get('activity'))
        ws.cell(row=row_idx, column=5, value=item.get('procedure'))
        ws.cell(row=row_idx, column=6, value=item.get('frequency', '정기'))
        ws.cell(row=row_idx, column=7, value=item.get('owner', 'IT팀'))
        
        # 줄바꿈 및 상단 정렬
        for col in range(1, 8):
            ws.cell(row=row_idx, column=col).alignment = Alignment(wrap_text=True, vertical="top")

    # 열 너비 조정
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 50
    ws.column_dimensions['E'].width = 50
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 15

    # 결과 전송
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    today = datetime.now().strftime("%Y%m%d")
    filename = f"AI_ITGC_RCM_{system_info.get('system_name', 'System')}_{today}.xlsx"
    
    # Flask에서 파일 다운로드를 위해 BytesIO 데이터를 일시적으로 저장하거나 직접 전송
    # 여기선 Base64 등으로 브라우저에 내려주거나 할 수 있음. 간단하게 API 응답으로 처리
    import base64
    xlsx_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
    
    return jsonify({
        "success": True, 
        "filename": filename,
        "file_data": xlsx_base64
    })
