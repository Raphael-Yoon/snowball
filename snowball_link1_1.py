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
    {
        "id": "PWC01", "name": "IT 정책서 관리", "category": "IT정책", "objective": "IT 정책의 명문화 및 준수 보장",
        "risk_code": "R-01", "risk_description": "IT 프로세스에 대한 정책이 수립되지 않을 위험 - ITGCs",
        "control_description": "1. 하기 영역에 대한 IT운영프로세스에 관한 정책이 IT정책서에 명시되어 있음\n - Access to programs and data\n - Changes to application Programs\n - Program Development\n - Computer Operations\n2. IT정책서는 매년 경영정보팀장의 검토 및 승인을 득함\n3. 검토된 IT정책서는 그룹웨어 게시판에 게시됨",
        "type": "Manual", "frequency": "연", "method": "예방",
        "test_procedure_manual": "1. IT운영프로세스가 명시된 '운영보안 규정' 정책서를 입수함\n2. 입수한 운영보안 규정상 제·개정 이력을 검토하고 매년 경영정보팀장의 검토 및 승인을 득하였는지 여부를 검토함\n3. 검토 및 승인을 득한 운영보안 규정이 그룹웨어 내 문서관리-규정문서 항목상 전체 공지 되고 있는지 여부를 확인함",
        "test_procedure_auto": "1. IT정책서 관리 시스템의 자동 알림/승인 워크플로우 설정을 확인함\n2. 모집단에서 임의의 샘플 1건을 추출하여 시스템에 의해 자동으로 검토 요청 및 게시가 수행되었는지 확인함"
    },
    {
        "id": "APD01", "name": "Application 권한 승인", "category": "계정관리", "objective": "인가된 사용자에게 적절한 권한 부여",
        "risk_code": "R-02", "risk_description": "시스템 사용자가 시스템에서 규정하는 승인과 업무분장을 우회 할 위험",
        "control_description": "권한 요청에 대해 요청 부서장 또는 IT팀장 등 책임자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "아래의 순서에 따라 통제 테스트를 수행한다.\n\n1. 모집단에서 샘플을 추출한다.\n2. 추출된 샘플의 권한 요청서 작성 여부와 부서장 등 책임권자의 승인 여부를 확인한다.\n3. 권한 요청 및 승인 완료 후 권한 부여가 수행되었는지 확인한다\n  - 권한 요청서 작성/승인 일자 < 권한부여 일자",
        "test_procedure_auto": "1. 권한 부여 시 시스템에 의한 자동 승인 워크플로우 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 시스템에 의해 승인 후 권한이 부여되었는지 확인한다"
    },
    {
        "id": "APD02", "name": "Application 부서이동자 권한 회수", "category": "계정관리", "objective": "부서 이동시 불필요 권한 즉시 회수",
        "risk_code": "R-03", "risk_description": "시스템 사용자가 시스템에서 규정하는 승인과 업무분장을 우회 할 위험",
        "control_description": "전배 등 기존 권한에 대한 회수 사유 발생시 즉시 회수한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "부서이동(전배)자의 기존 권한 회수 여부를 검토한다\n\n1. 모집단에서 샘플을 추출한다.\n2. 기존 권한의 회수 여부를 확인한다\n  - 권한 회수 일자 < 부서이동(전배) 일자",
        "test_procedure_auto": "1. 인사시스템과 연동된 권한 자동회수 프로그램 로직을 확인한다\n2. 모집단(부서이동자)에서 임의의 샘플 1건을 추출하여 기존 권한이 자동 회수되었는지 확인한다"
    },
    {
        "id": "APD03", "name": "Application 퇴사자 접근권한 회수", "category": "계정관리", "objective": "퇴사자 시스템 접근 차단",
        "risk_code": "R-04", "risk_description": "시스템 사용자가 시스템에서 규정하는 승인과 업무분장을 우회 할 위험",
        "control_description": "퇴사 등 계정삭제(비활성화) 사유 발생시 시스템에 의해 계정이 자동 삭제(비활성화)된다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "Application 계정 삭제(비활성화)에 대해 아래와 같이 검토한다\n\n1. 권한회수 프로그램 Source에 Logic이 정확히 구현되어 있는지 확인한다\n2. 모집단(퇴사자)에서 임의의 샘플 1건을 추출하여 퇴사자 계정이 모두 삭제(비활성화)되었는지 확인한다",
        "test_procedure_manual": "1. 모집단(퇴사자)에서 샘플을 추출한다\n2. 퇴사자 계정 삭제 요청서 작성 및 승인 여부를 확인한다\n3. 승인 후 계정이 삭제(비활성화)되었는지 확인한다"
    },
    {
        "id": "APD04", "name": "Application 권한 Monitoring", "category": "계정관리", "objective": "권한 부여의 적정성 주기적 검토",
        "risk_code": "R-05", "risk_description": "시스템 사용자가 시스템에서 규정하는 승인과 업무분장을 우회 할 위험",
        "control_description": "전체 사용자가 보유한 권한에 대해 Monitoring이 수행되며 결과는 책임자에 의해 승인된다",
        "type": "Manual", "frequency": "분기", "method": "적발",
        "test_procedure_manual": "권한 Monitoring 통제에 대해 아래와 같이 검토한다\n\n1. 모집단에서 샘플을 추출한다\n2. Application/서버(OS/DB)/VPN에 대해 보유권한 적정성이 검토되었는지 확인한다\n3. 승인권자의 승인 여부를 확인한다",
        "test_procedure_auto": "1. 시스템에 의한 권한 모니터링 자동 수행 로직을 확인한다\n2. 자동 생성된 모니터링 보고서 샘플 1건을 추출하여 정상 생성 여부를 확인한다"
    },
    {
        "id": "APD05", "name": "Application 관리자 권한 제한", "category": "계정관리", "objective": "관리자 권한 오남용 방지",
        "risk_code": "R-06", "risk_description": "위험하고 강력한 계정사용자가 시스템에서 규정하는 승인과 업무분장을 우회 할 위험",
        "control_description": "관리자 권한은 지정된 담당자로 제한된다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. 관리자 권한을 보유한 인원을 추출한다.\n2. 해당 인원의 부서, 직책, 직무 등을 검토하여 적절성 여부를 확인한다",
        "test_procedure_manual": "1. 관리자 권한 보유 현황을 추출한다\n2. 모집단에서 샘플을 추출하여 관리자 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "APD06", "name": "Application 패스워드", "category": "계정관리", "objective": "강력한 인증 체계 유지",
        "risk_code": "R-07", "risk_description": "취약한 패스워드 정책이나 보안 설정으로 인해 시스템 접근 통제를 우회할 위험",
        "control_description": "1. Application 패스워드는 최소 아래 기준 이상으로 설정함\n 1) 복잡성: 문자, 숫자, 특수문자 포함\n 2) 최소 길이: 8자리 이상",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "Application 패스워드 설정 내역을 검토하여 정책서와 상이한 부분이 존재하는지 확인한다\n\nT-Code:SE38에서 RSPARAM 조회\n  .login/min_password_lng: 최소자리\n  .login/min_password_special: 특수문자\n  .login/min_letters: 문자\n  .login/min_digit: 숫자",
        "test_procedure_manual": "1. 패스워드 정책 변경 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 변경 요청 및 승인 여부를 확인한다"
    },
    {
        "id": "APD07", "name": "Data 변경 승인", "category": "데이터관리", "objective": "DB 데이터 직접 변경의 승인 체계 확보",
        "risk_code": "R-08", "risk_description": "기본적인 거래정보나 마스터 데이터를 부적절하게 변경 할 위험",
        "control_description": "데이터 직접 변경은 적절한 승인권자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. 데이터 변경 이력을 조회하고, 조회화면(조회 조건, 조회된 전체 데이터 수 확인 가능한 화면) 및 조회 결과를 문서화함\n2. 위의 1.에서 조회된 데이터 변경의 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 샘플을 선정함\n3. 샘플에 대하여 승인권자의 승인을 득하였는지 여부를 확인함",
        "test_procedure_auto": "1. 데이터 변경 시 시스템에 의한 자동 승인 워크플로우 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 변경이 수행되었는지 확인한다"
    },
    {
        "id": "APD08", "name": "Data 변경 권한 제한", "category": "데이터관리", "objective": "DB 직접 접근 권한 제한",
        "risk_code": "R-09", "risk_description": "인가받지 않은 DB 접근으로 인하여 거래정보나 마스터 데이터가 부적절하게 변경 될 위험",
        "control_description": "데이터 변경 권한은 지정된 담당자로 제한된다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. 데이터 변경 권한을 보유한 인원을 추출한다.\n2. 해당 인원의 부서, 직책, 직무 등을 검토하여 적절성 여부를 확인한다.",
        "test_procedure_manual": "1. 데이터 변경 권한 부여 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "APD09", "name": "OS 접근권한 승인", "category": "OS관리", "objective": "서버 인프라 접근 승인 절차 준수",
        "risk_code": "R-10", "risk_description": "인가받지 않은 OS 접근으로 인하여 운영서버 상의 프로그램이 부적절하게 변경 될 위험",
        "control_description": "OS에 접근권한은 적절한 승인권자의 승인을 득한 후 부여한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. 테스트 기간 동안 신규 부여된 OS 접근권한 목록을 조회하고, 조회화면 및 조회 결과를 문서화한다.\n2. 위의 1.에서 조회된 모집단의 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 샘플을 선정한다.\n3. 샘플에 대하여 승인권자의 승인을 득하였는지 여부를 확인한다.",
        "test_procedure_auto": "1. OS 접근권한 자동 부여 시스템 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 권한이 부여되었는지 확인한다"
    },
    {
        "id": "APD10", "name": "OS 패스워드", "category": "OS관리", "objective": "인프라 계정 보안 강화",
        "risk_code": "R-11", "risk_description": "취약한 패스워드 정책이나 보안 설정으로 인해 시스템 접근 통제를 우회할 위험",
        "control_description": "OS 패스워드는 회사의 규정에 따라 최소자리, 복잡성 등을 설정한다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. OS서버 또는 OS 접근제어 Tool에 설정된 패스워드를 확인하여 아래 기준으로 설정되어 있는지 여부를 검토한다.\n 1) 복잡성: 문자, 숫자, 특수문자 포함\n 2) 최소 길이: 8자리 이상",
        "test_procedure_manual": "1. OS 패스워드 정책 변경 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 변경 요청 및 승인 여부를 확인한다"
    },
    {
        "id": "APD11", "name": "OS 관리자 권한 제한", "category": "OS관리", "objective": "서버 관리자 권한 최소화",
        "risk_code": "R-12", "risk_description": "인가받지 않은 OS 접근으로 인하여 운영서버 상의 프로그램이 부적절하게 변경 될 위험",
        "control_description": "OS Super User 권한은 지정된 인원으로 제한한다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. OS 또는 OS 접근제어 Tool에서 슈퍼권한자 목록을 확인함\n2. 해당 권한을 보유한 인원의 부서, 직책, 직무 등을 검토하여 적절성 여부를 확인한다.",
        "test_procedure_manual": "1. OS 관리자 권한 부여 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "APD12", "name": "DB 접근권한 승인", "category": "DB관리", "objective": "DB 접근 승인 절차 준수",
        "risk_code": "R-13", "risk_description": "인가받지 않은 DB 접근으로 인하여 거래정보나 마스터 데이터가 부적절하게 변경 될 위험",
        "control_description": "DB에 접근권한은 적절한 승인권자의 승인을 득한 후 부여한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. DB 또는 DB 접근제어 Tool에서 테스트 기간 동안 신규 부여된 접근권한 목록을 조회하고, 조회화면 및 조회 결과를 문서화함\n2. 위의 1.에서 조회된 모집단의 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 샘플을 선정함\n3. 샘플에 대하여 적절한 승인권자의 승인을 득하였는지 여부를 확인함",
        "test_procedure_auto": "1. DB 접근권한 자동 부여 시스템 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 권한이 부여되었는지 확인한다"
    },
    {
        "id": "APD13", "name": "DB 패스워드", "category": "DB관리", "objective": "DB 계정 보안 강화",
        "risk_code": "R-14", "risk_description": "취약한 패스워드 정책이나 보안 설정으로 인해 시스템 접근 통제를 우회할 위험",
        "control_description": "DB 패스워드는 회사의 규정에 따라 최소자리, 복잡성 등을 설정한다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. DB의 패스워드 정책을 확인하여 아래 기준으로 설정되어 있는지 여부를 검토함.\n 1) 복잡성: 문자, 숫자, 특수문자 포함\n 2) 최소 길이: 8자리 이상",
        "test_procedure_manual": "1. DB 패스워드 정책 변경 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 변경 요청 및 승인 여부를 확인한다"
    },
    {
        "id": "APD14", "name": "DB 관리자 권한 제한", "category": "DB관리", "objective": "DB 관리자 권한 최소화",
        "risk_code": "R-15", "risk_description": "인가받지 않은 DB 접근으로 인하여 거래정보나 마스터 데이터가 부적절하게 변경 될 위험",
        "control_description": "DB Super User 권한은 지정된 인원으로 제한한다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. DBSafer 권한 정책을 확인하여 ERP plus DB Super User 권한자 목록을 확인함\n2. ERP plus DB Super User 권한이 지정된 담당자에게만 부여되어 있는지 여부를 검토함",
        "test_procedure_manual": "1. DB 관리자 권한 부여 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "PC01", "name": "프로그램 변경 승인", "category": "변경관리", "objective": "프로그램 변경 전 승인 득함",
        "risk_code": "R-16", "risk_description": "승인 또는 테스트 절차 없이 수행된 프로그램 변경이 주요 거래정보를 왜곡 할 위험",
        "control_description": "프로그램 변경 필요시 변경요청서를 작성하고 요청부서장 등 책임자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "프로그램 변경 요청에 대해 SR(Service Request)의 작성/승인 완료 여부를 검토한다\n\n1. 모집단에서 샘플을 추출한다\n2. 샘플건이 SR의 작성 및 승인권자(요청 부서장)의 승인 여부를 확인한다\n3. SR 작성/승인 이후 프로그램 이관이 수행되었는지 확인한다\n  - SR 작성/승인 완료 일자 < 프로그램 이관 일자",
        "test_procedure_auto": "1. 프로그램 변경 시 시스템에 의한 자동 승인 워크플로우 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 이관이 수행되었는지 확인한다"
    },
    {
        "id": "PC02", "name": "프로그램 변경 사용자 테스트", "category": "변경관리", "objective": "사용자 검증을 통한 품질 확보",
        "risk_code": "R-17", "risk_description": "승인 또는 테스트 절차 없이 수행된 프로그램 변경이 주요 거래정보를 왜곡 할 위험",
        "control_description": "프로그램 변경 후 요청자에 의한 사용자인수테스트가 수행되며 결과는 문서화된다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "프로그램 변경(개발) 완료 후 테스트 통제에 대해 사용자 테스트 결과서 작성 여부를 검토한다\n\n1. 모집단에서 샘플을 추출한다\n2. 샘플건이 프로그램 변경(개발) 완료 후 사용자 테스트가 수행되었고 결과의 문서화 여부를 확인한다\n3. 사용자 테스트 완료 이후 프로그램 이관이 수행되었는지 확인한다\n  - 사용자 테스트 완료 일자 < 프로그램 이관 일자",
        "test_procedure_auto": "1. 자동화된 테스트 시스템의 로직 및 테스트 케이스 설정을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 테스트가 수행되었는지 확인한다"
    },
    {
        "id": "PC03", "name": "프로그램 변경 이관 승인", "category": "변경관리", "objective": "운영 반영 전 최종 승인 확인",
        "risk_code": "R-18", "risk_description": "승인 또는 테스트 절차 없이 수행된 프로그램 변경이 주요 거래정보를 왜곡 할 위험",
        "control_description": "개발완료 후 개발자는 이관을 요청하고 IT팀장 등 책임자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "프로그램 이관 요청/승인 통제에 대해 이관 요청서의 작성/승인 완료 여부를 검토한다\n\n1. 모집단에서 샘플을 추출한다\n2. 샘플건이 프로그램 변경(개발) 완료 후 이관 요청서가 작성되었고 승인권자(IT운영팀장)의 승인 여부를 확인한다\n3. 이관 요청 및 승인 완료 후 프로그램 이관이 수행되었는지 확인한다\n  - 이관 요청/승인 완료 일자 < 프로그램 이관 일자",
        "test_procedure_auto": "1. 자동 이관 시스템의 승인 워크플로우 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 이관이 수행되었는지 확인한다"
    },
    {
        "id": "PC04", "name": "개발/운영 환경의 분리", "category": "변경관리", "objective": "개발과 운영 독립성 확보",
        "risk_code": "R-19", "risk_description": "승인 또는 테스트 절차 없이 수행된 프로그램 변경이 주요 거래정보를 왜곡 할 위험",
        "control_description": "개발과 운영 환경은 논리적으로 분리되어 있다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. 개발/운영 환경 구성을 확인함\n2. \"exGate 관리자\" 도구에서 ERP plus 운영서버(\"SKERP\")의 IP 정보를 확인함\n3. 접근통제툴에서 개발환경 IP 정보를 확인함",
        "test_procedure_manual": "1. 개발/운영 환경 분리에 대한 정책서를 입수한다\n2. 환경 분리 변경 이력에 대한 승인 여부를 확인한다"
    },
    {
        "id": "PC05", "name": "이관담당자 권한 제한", "category": "변경관리", "objective": "배포 권한의 분리 및 최소화",
        "risk_code": "R-20", "risk_description": "승인 또는 테스트 절차 없이 수행된 프로그램 변경이 주요 거래정보를 왜곡 할 위험",
        "control_description": "이관담당자과 개발담당자는 직무상 분리되어 있으며 시스템 권한도 분리되어 있다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. 개발자와 이관담당자의 권한을 각각 확인함\n2. 개발자가 운영환경에 직접 이관할 수 없도록 권한이 분리되어 있는지 확인함",
        "test_procedure_manual": "1. 이관 권한 부여 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "PC06", "name": "OS 설정변경", "category": "변경관리", "objective": "인프라 설정 변경의 통제",
        "risk_code": "R-21", "risk_description": "인가받지 않은 OS/DB 설정 변경으로 인해 프로그램이 부적절하게 변경 될 위험",
        "control_description": "OS 설정변경시 적절한 승인권자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. In-scope 시스템 OS/DB의 변경이력(업데이트/패치 이력)을 아래 조건으로 추출함\n  - 작업일자 : 테스트 대상 기간\n\n2. 조회 된 건수의 빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n\n3. 샘플로 선정된 건에 대하여 적절한 근거가 존재하는지 확인함\n  - OS/DB 변경(업데이트/패치 이력)에 대한 요청 및 승인\n  - 변경(업데이트/패치 이력) 건에 대한 테스트 결과",
        "test_procedure_auto": "1. OS 설정변경 자동 승인 시스템 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 변경이 수행되었는지 확인한다"
    },
    {
        "id": "PC07", "name": "DB 설정변경", "category": "변경관리", "objective": "DB 설정 변경의 통제",
        "risk_code": "R-22", "risk_description": "인가받지 않은 OS/DB 설정 변경으로 인해 프로그램이 부적절하게 변경 될 위험",
        "control_description": "DB 설정변경시 적절한 승인권자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. In-scope 시스템 OS/DB의 변경이력(업데이트/패치 이력)을 아래 조건으로 추출함\n  - 작업일자 : 테스트 대상 기간\n\n2. 조회 된 건수의 빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n\n3. 샘플로 선정된 건에 대하여 적절한 근거가 존재하는지 확인함\n  - OS/DB 변경(업데이트/패치 이력)에 대한 요청 및 승인\n  - 변경(업데이트/패치 이력) 건에 대한 테스트 결과",
        "test_procedure_auto": "1. DB 설정변경 자동 승인 시스템 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 변경이 수행되었는지 확인한다"
    },
    {
        "id": "CO01", "name": "Batch Schedule 등록/변경 요청 및 승인", "category": "운영관리", "objective": "배치 작업 변경의 무결성 확보",
        "risk_code": "R-23", "risk_description": "배치 프로세스가 부적절하게 변경되거나 실패할 위험",
        "control_description": "새로운 배치 작업 등록 시 요청서를 작성하고 IT팀장 등 책임자의 승인을 득한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. Batch 작업 목록 중 아래 조건의 배치 등록/변경 이력을 추출함\n2. 조회 된 건수의 빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n3. 샘플로 선정된 Batch 작업 건에 대하여 하기 사항을 확인함\n - 샘플로 선정된 Batch에 대한 IT 시스템 설정 변경 승인서\n - Batch 등록, 변경에 대한 승인권자의 승인 여부\n - Batch 등록 결과가 요청상의 내용과 동일한지 여부",
        "test_procedure_auto": "1. Batch 등록/변경 자동 승인 시스템 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 등록이 수행되었는지 확인한다"
    },
    {
        "id": "CO02", "name": "Batch Schedule 등록/변경 권한 제한", "category": "운영관리", "objective": "스케줄링 권한 오남용 방지",
        "risk_code": "R-24", "risk_description": "배치 프로세스가 부적절하게 변경되거나 실패할 위험",
        "control_description": "Batch Schedule 등록/변경 권한은 지정된 담당자로 제한된다",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. Batch Schedule 등록 쿼리에서 SDLUNAME 컬럼을 확인함\n- 해당 컬럼의 데이터가 Batch Schedule을 등록한 인원임\n2. 해당 인원의 부서, 직급, 직무 등을 검토하여 적절한 인원인지 확인함",
        "test_procedure_manual": "1. Batch 권한 부여 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "CO03", "name": "Batch Schedule 모니터링", "category": "운영관리", "objective": "배치 작업 실패 시 적시 대응",
        "risk_code": "R-23", "risk_description": "배치 프로세스가 부적절하게 변경되거나 실패할 위험",
        "control_description": "Batch 오류는 담당자가 인식할 수 있어야 하며 오류 내역 및 조치결과가 문서화된다",
        "type": "Manual", "frequency": "일", "method": "적발",
        "test_procedure_manual": "1. IT 주간점검보고 5건에 대하여 하기 사항을 확인함\n - 주별 Batch 모니터링 수행 여부\n - 점검 결과에 대한 문서화 여부\n - 이상 건 식별 시, 해당 건에 대한 조치 완료 여부 및 결과 문서화 여부\n - 모니터링 결과에 대한 보고 여부",
        "test_procedure_auto": "1. 자동 Batch 모니터링 시스템의 알림 설정을 확인한다\n2. 자동 생성된 모니터링 보고서 샘플 1건을 추출하여 정상 생성 여부를 확인한다"
    },
    {
        "id": "CO04", "name": "백업 모니터링", "category": "운영관리", "objective": "백업 성공 여부 모니터링",
        "risk_code": "R-24", "risk_description": "시스템 오류 등으로 거래 데이터가 손상되거나 복구되지 않을 위험",
        "control_description": "주기적으로 백업 및 복구가 수행되고, 백업미디어는 소산보관된다",
        "type": "Manual", "frequency": "일", "method": "적발",
        "test_procedure_manual": "1. IT 주간점검보고 5건에 대하여 하기 사항을 확인함\n - 주별 백업 모니터링 수행 여부\n - 점검 결과에 대한 문서화 여부\n - 이상 건 식별 시, 해당 건에 대한 조치 완료 여부 및 결과 문서화 여부\n - 모니터링 결과에 대한 보고 여부",
        "test_procedure_auto": "1. 자동 백업 시스템의 스케줄 및 설정을 확인한다\n2. 자동 생성된 백업 로그 샘플 1건을 추출하여 정상 수행 여부를 확인한다"
    },
    {
        "id": "CO05", "name": "장애 관리", "category": "운영관리", "objective": "시스템 장애 기록 및 원인 분석",
        "risk_code": "R-25", "risk_description": "시스템 운영 중 발생한 오류가 적시에 해결되지 않을 위험",
        "control_description": "복구절차의 효과성을 정기적으로 테스트하기 위한 절차가 존재한다",
        "type": "Manual", "frequency": "수시", "method": "적발",
        "test_procedure_manual": "1. 서버유지보수업체로부터 매월 보고 받는 월간 보고서를 입수함\n2. 시스템 오류와 관련하여 원인, 해결방안, 재발방지 대책이 문서화 되었는지 여부를 검토함\n3. 작성된 장애보고서가 IT부서장에게 보고 되었는지 여부를 확인함",
        "test_procedure_auto": "1. 자동 장애 감지 및 알림 시스템의 설정을 확인한다\n2. 자동 생성된 장애 로그 샘플 1건을 추출하여 정상 기록 여부를 확인한다"
    },
    {
        "id": "CO06", "name": "데이터센터 접근 제한", "category": "운영관리", "objective": "서버실 물리적 출입 통제",
        "risk_code": "R-26", "risk_description": "IT 시설, 장비, 자원에 승인되지 않은 접근이 발생 할 위험",
        "control_description": "외부 인원의 데이터 센터 출입시 방문일지를 작성하고 서버담당자의 동행하에 출입한다",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. 분기 통제이므로 데이터센터 출입이력 검토 내역 중 임의의 샘플을 무작위로 샘플링함\n\n2. 샘플 건에 대해서 하기 사항을 확인함\n - 데이터센터 출입이력 검토내역에 주요 서버실 포함 여부\n - 출입인원에 대한 적절한 검토 여부 (특정인원 출입빈도 / 사유파악 등)\n - 출입이력 검토내역에 대한 IT부서장의 승인 여부",
        "test_procedure_auto": "1. 자동 출입통제 시스템의 설정 및 권한을 확인한다\n2. 출입 로그 샘플 1건을 추출하여 권한에 따른 접근 통제가 정상 작동하는지 확인한다"
    },
    {
        "id": "PD01", "name": "사용자 인수 테스트", "category": "개발관리", "objective": "최종 사용자의 시스템 수용 검증",
        "risk_code": "R-27", "risk_description": "주요 정보가 불완전하고 부정확하게 이관 될 위험",
        "control_description": "1. 프로젝트 진행 확정 시 품의 진행 및 승인 득함\n2. 개발 과정에서 단위/통합/사용자 테스트 수행 및 결과 문서화\n3. 프로젝트 완료 시 결과보고 진행",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. 경영정보팀에서 관리하고 있는 SI완료 건 중 아래 내역을 대상으로 하여 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n - 내부회계운영 지원 시스템 (In-scope)\n - 재무보고와 관련있는 개발건\n2. 샘플로 선정한 시스템 추가/기능 개선 등의 프로젝트 건에 대하여 개발 과정에서 인수테스트(단위테스트/통합테스트/사용자 테스트)가 수행되고 테스트 결과가 문서화 되었는 지 여부를 검토함\n사용자 테스트 결과 특이사항이 없는 경우 검토승인->검토완료 변경처리됨.",
        "test_procedure_auto": "1. 자동화된 테스트 시스템의 로직 및 테스트 케이스 설정을 확인한다\n2. 자동 테스트 결과 로그 샘플 1건을 추출하여 정상 수행 여부를 확인한다"
    },
    {
        "id": "PD02", "name": "데이터 이관", "category": "개발관리", "objective": "이관 데이터의 완전성 및 정확성 보장",
        "risk_code": "R-28", "risk_description": "새로운 시스템에 불완전하거나 부정확하게 데이터가 생성 될 위험",
        "control_description": "1. 중요한 데이터 이관 시 별도의 데이터 테스트를 수행하며, 테스트 결과 및 승인 이력이 문서화 관리됨",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. IT부서에서 관리하고 있는 SI완료 건 중 아래 내역을 대상으로 하여 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n - 내부회계운영 지원 시스템 (In-scope)\n - 재무보고와 관련있는 개발건\n - 데이터 마이그레이션이 동반된 건\n\n2. 개발 중 유효한 마이그레이션 테스트가 수행되었는지 아래 사항을 기준으로 검토함.\n - 기존 시스템의 데이터 필드와 목표 시스템의 데이터 필드의 적절한 mapping에 대한 확인 여부\n - 이관 결과에 대한 승인 존재 여부\n - 이관된 데이터의 완전성, 정확성 및 유효성 검증 여부",
        "test_procedure_auto": "1. 자동 데이터 이관 시스템의 매핑 설정 및 검증 로직을 확인한다\n2. 자동 이관 로그 샘플 1건을 추출하여 정상 수행 여부를 확인한다"
    },
    {
        "id": "PD03", "name": "이슈 관리", "category": "개발관리", "objective": "개발 이슈의 누적 관리 및 해결",
        "risk_code": "R-29", "risk_description": "새로운 시스템에 불완전하거나 부정확하게 데이터가 생성 될 위험",
        "control_description": "1. 프로젝트 중 발생하는 이슈 및 오류는 주기적으로 집계 및 관리됨\n2. 관리되는 이슈는 적시에 해결되어 프로젝트 관리자에게 보고 됨",
        "type": "Manual", "frequency": "수시", "method": "적발",
        "test_procedure_manual": "1. IT부서에서 관리하고 있는 SI완료 건 중 아래 내역을 대상으로 하여 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n - 내부회계운영 지원 시스템 (In-scope)\n - 재무보고와 관련있는 개발건\n2. 샘플로 선정한 SI건에 대해 이슈 및 오류내역이 문서화 되어 있는지 검토함\n3. 이슈 및 오류내역이 주기적으로 프로젝트 관리자에게 보고 및 조치되었는지 검토함",
        "test_procedure_auto": "1. 자동 이슈 추적 시스템의 설정 및 알림 로직을 확인한다\n2. 자동 생성된 이슈 보고서 샘플 1건을 추출하여 정상 생성 여부를 확인한다"
    },
    {
        "id": "PD04", "name": "사용자 교육", "category": "개발관리", "objective": "운영 준비를 위한 사용자 교육 실시",
        "risk_code": "R-30", "risk_description": "새로운 시스템에 불완전하거나 부정확하게 데이터가 생성 될 위험",
        "control_description": "1. 시스템 추가/기능 개선 프로젝트 종료 시 사용자 교육 또는 매뉴얼 배포가 수행 됨",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. 경영정보팀에서 관리하고 있는 SI완료 건 중 아래 내역을 대상으로 하여 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 무작위로 샘플링 함\n - 내부회계운영 지원 시스템 (In-scope)\n - 재무보고와 관련있는 개발건\n2. 샘플로 선정한 SI건에 대한 교육 및 매뉴얼 배포가 설계 및 수행되었는지 검토함",
        "test_procedure_auto": "1. 자동 교육 시스템(LMS)의 설정 및 교육 이수 추적 로직을 확인한다\n2. 교육 이수 로그 샘플 1건을 추출하여 정상 기록 여부를 확인한다"
    },
    {
        "id": "ST01", "name": "Supporting Tool Super User 권한 제한", "category": "지원툴관리", "objective": "보조 툴 관리자 권한 통제",
        "risk_code": "R-31", "risk_description": "위험하고 강력한 계정사용자가 시스템 통제를 우회 할 위험",
        "control_description": "1. Supporting tool의 Super User는 지정된 담당자로 제한되어 있음",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. Supporting Tool의 관리자 권한 목록을 확인함\n2. 관리자 권한이 지정된 담당자로 제한되어 있음을 확인함",
        "test_procedure_manual": "1. 관리자 권한 부여 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 권한 부여에 대한 승인 여부를 확인한다"
    },
    {
        "id": "ST02", "name": "Supporting Tool 패스워드 설정", "category": "지원툴관리", "objective": "보조 툴 보안 설정 유지",
        "risk_code": "R-32", "risk_description": "취약한 패스워드 정책으로 인해 시스템 접근 통제를 우회할 위험",
        "control_description": "1. Supporting tool의 패스워드는 최소 8자리 이상, 문자/숫자/특수문자 조합, 분기별 변경 적용",
        "type": "Auto", "frequency": "기타", "method": "예방",
        "test_procedure_auto": "1. Supporting Tool 패스워드 환경설정 정보를 확인하여 아래 기준으로 설정되어 있는지 여부를 검토함.\n 1) 복잡성: 문자, 숫자, 특수문자 포함\n 2) 최소 길이: 8자리 이상",
        "test_procedure_manual": "1. 패스워드 정책 변경 이력을 조회한다\n2. 모집단에서 샘플을 추출하여 변경 요청 및 승인 여부를 확인한다"
    },
    {
        "id": "ST03", "name": "Supporting Tool 기능 변경 요청 및 승인", "category": "지원툴관리", "objective": "지원 도구 변경의 이력 관리",
        "risk_code": "R-33", "risk_description": "승인 없이 수행된 시스템 설정 변경이 데이터를 왜곡 할 위험",
        "control_description": "1. Supporting tool(DBSafer 등) 변경 시 요청서 작성 및 IT부서장 승인 득함\n2. 테스트 수행 및 최종 적용 검토 후 운영환경 적용",
        "type": "Manual", "frequency": "수시", "method": "예방",
        "test_procedure_manual": "1. 테스트기간 동안 발생한 Supporting Tool 프로그램 변경 이력을 조회하고, 조회화면(조회 조건, 조회된 전체 데이터 수 확인 가능한 화면) 및 조회 결과를 문서화함\n2. 위의 1.에서 조회된Supporting Tool 변경의 발생빈도에 따라 샘플 Guide의 샘플 수를 적용하여 샘플을 선정함\n3. 샘플에 대하여 전자결재상 \"IT 시스템 설정 변경 승인서\"를 확인하고 승인권자의 승인을 득하였는지 여부를 확인함",
        "test_procedure_auto": "1. Supporting Tool 변경 자동 승인 시스템 로직을 확인한다\n2. 모집단에서 임의의 샘플 1건을 추출하여 자동 승인 후 변경이 수행되었는지 확인한다"
    },
    {
        "id": "PWC02", "name": "정보보안 교육", "category": "IT정책", "objective": "전사 보안 의식 함양 및 법적 준수",
        "risk_code": "R-34", "risk_description": "정보보안 교육이 적절하게 이루어지지 않을 위험",
        "control_description": "1. 모든 임직원 대상 매분기 1회 개인정보보호 및 정보보안 교육 실시 및 관련 자료 게시",
        "type": "Manual", "frequency": "분기", "method": "예방",
        "test_procedure_manual": "1. 경영정보팀에서 모든 임직원을 대상으로 분기별 개인정보보호 및 정보보안 교육을 위해 정보보안 게시판에 게시물을 게시하였는지 확인함.",
        "test_procedure_auto": "1. 자동 교육 시스템(LMS)의 설정 및 교육 공지 로직을 확인한다\n2. 자동 발송된 교육 알림 로그 샘플 1건을 추출하여 정상 발송 여부를 확인한다"
    },
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

# 주기별 모집단/표본수 기준 (백엔드 계산용)
FREQUENCY_POPULATION = {'연': 1, '분기': 4, '월': 12, '주': 52, '일': 250, '수시': 0, '기타': 0}
FREQUENCY_SAMPLE = {'연': 1, '분기': 2, '월': 2, '주': 5, '일': 20, '수시': 25, '기타': 0}

@bp_link1_1.route('/api/rcm/export_excel', methods=['POST'])
@login_required
def api_rcm_export_excel():
    """최종 RCM 엑셀 내보내기 - 마스터 데이터 기반"""
    import base64
    from openpyxl import Workbook

    data = request.json
    user_overrides = {item['id']: item for item in data.get('rcm_data', [])}
    system_info = data.get('system_info', {})

    # 마스터 데이터를 ID로 조회할 수 있게 딕셔너리로 변환
    master_dict = {ctrl['id']: ctrl for ctrl in MASTER_ITGC_CONTROLS}

    wb = Workbook()
    ws = wb.active
    ws.title = "RCM"

    # 헤더 작성 (UI의 모든 컬럼 반영)
    headers = [
        "Risk Code", "Risk Name", "Category", "Control Code", "Control Name",
        "Control Description", "구분", "주기", "성격", "모집단", "모집단 수", "모집단 완전성", "표본수", "테스트 절차"
    ]


    # 헤더 스타일 적용
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # 데이터 작성 - 마스터 데이터 순서대로
    for row_idx, control in enumerate(MASTER_ITGC_CONTROLS, 2):
        ctrl_id = control['id']
        override = user_overrides.get(ctrl_id, {})

        # 1. Risk Code / 2. Risk Name / 3. Category
        ws.cell(row=row_idx, column=1, value=control.get('risk_code', ''))
        ws.cell(row=row_idx, column=2, value=control.get('risk_description', ''))
        ws.cell(row=row_idx, column=3, value=control.get('category', ''))
        
        # 4. Control Code / 5. Control Name
        ws.cell(row=row_idx, column=4, value=ctrl_id)
        ws.cell(row=row_idx, column=5, value=control.get('name', ''))
        
        # 6. Control Description (AI 분석 결과 우선)
        activity = override.get('activity', control.get('control_description', ''))
        ws.cell(row=row_idx, column=6, value=activity)

        # 7. 구분 / 8. 주기 / 9. 성격 (UI 선택값 우선)
        selected_type = override.get('type', control.get('type', ''))
        selected_freq = override.get('frequency', control.get('frequency', ''))
        selected_method = override.get('method', control.get('method', ''))

        ws.cell(row=row_idx, column=7, value=selected_type)
        ws.cell(row=row_idx, column=8, value=selected_freq)
        ws.cell(row=row_idx, column=9, value=selected_method)

        # 10. 모집단 / 11. 모집단 수 / 12. 모집단 완전성 / 13. 표본수
        pop_names = {'연': '연간 모니터링 문서', '분기': '분기별 모니터링 문서', '월': '월별 모니터링 문서', '주': '주별 모니터링 문서', '일': '일별 모니터링 문서'}
        pop_name = pop_names.get(selected_freq, '')
        pop_count = FREQUENCY_POPULATION.get(selected_freq, 0)
        
        completeness = ""
        if pop_name and pop_count > 0:
            completeness = f"{pop_name}이므로 {pop_count}건을 완전성 있는 것으로 확인함"
        
        # 자동통제이거나 주기가 '기타'인 경우 표본은 0
        if selected_type in ['Auto', '자동'] or selected_freq == '기타':
            sample_count = 0
        else:
            sample_count = FREQUENCY_SAMPLE.get(selected_freq, 0)

        ws.cell(row=row_idx, column=10, value=pop_name)
        ws.cell(row=row_idx, column=11, value=pop_count)
        ws.cell(row=row_idx, column=12, value=completeness)
        ws.cell(row=row_idx, column=13, value=sample_count)

        # 14. 테스트 절차 (화면에서 보낸 값이 있으면 우선 사용, 없으면 마스터 데이터)
        procedure = override.get('procedure')
        if not procedure:
            if selected_type in ['Auto', '자동']:
                procedure = control.get('test_procedure_auto', '')
            else:
                procedure = control.get('test_procedure_manual', '')
        
        ws.cell(row=row_idx, column=14, value=procedure)

        # 셀 스타일 적용
        for col in range(1, 15):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = thin_border

    # 열 너비 조정
    column_widths = {
        'A': 10, 'B': 40, 'C': 12, 'D': 12, 'E': 25,
        'F': 50, 'G': 10, 'H': 10, 'I': 10, 'J': 20, 'K': 10, 'L': 45, 'M': 10, 'N': 60
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    # 첫 행 고정
    ws.freeze_panes = 'A2'

    # 결과 전송
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    today = datetime.now().strftime("%Y%m%d")
    system_name = system_info.get('system_name', 'System').replace(' ', '_')
    filename = f"ITGC_RCM_{system_name}_{today}.xlsx"

    xlsx_base64 = base64.b64encode(output.getvalue()).decode('utf-8')

    return jsonify({
        "success": True,
        "filename": filename,
        "file_data": xlsx_base64
    })
