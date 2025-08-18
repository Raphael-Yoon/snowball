from datetime import datetime
import os
from io import BytesIO
from openpyxl import load_workbook
from openai import OpenAI

# 인터뷰 질문 리스트 (생략 없이 전체 복사)
s_questions = [
    {"index": 0, "text": "산출물을 전달받을 e-Mail 주소를 입력해주세요.", "category": "Complete", "help": "", "answer_type": "2", "text_help": ""},
    {"index": 1, "text": "시스템 이름을 적어주세요.", "category": "IT PwC", "help": "", "answer_type": "2", "text_help": ""},
    {"index": 2, "text": "사용하고 있는 시스템은 상용소프트웨어입니까?", "category": "IT PwC", "help": "", "answer_type": "3", "text_help": "SAP ERP, Oracle ERP, 더존ERP 등"},
    {"index": 3, "text": "주요 로직을 회사내부에서 수정하여 사용할 수 있습니까?", "category": "IT PwC", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 4, "text": "Cloud 서비스를 사용하고 있습니까?", "category": "IT PwC", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 5, "text": "어떤 종류의 Cloud입니까?", "category": "IT PwC", "help": "SaaS (Software as a Service): 사용자가 직접 설치 및 관리할 필요 없이, 클라우드에서 제공되는 ERP 소프트웨어를 사용하는 방식.<br>예: SAP S/4HANA Cloud, Oracle NetSuite, Microsoft Dynamics 365 → 기업이 재무, 인사, 회계, 공급망 관리 등을 클라우드에서 운영 가능.<br>IaaS (Infrastructure as a Service): 기업이 자체적으로 ERP 시스템을 구축하고 운영할 수 있도록 서버, 스토리지, 네트워크 등의 인프라를 제공하는 방식.<br>예: AWS EC2, Microsoft Azure Virtual Machines, Google Cloud Compute Engine → 기업이 SAP, Oracle ERP 등의 온프레미스 버전을 클라우드 환경에서 직접 운영.", "answer_type": "2", "text_help": ""},
    {"index": 6, "text": "Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?", "category": "IT PwC", "help": "SOC 1 Report (Service Organization Control 1 보고서)는 재무 보고와 관련된 내부 통제 사항을 검증하는 보고서입니다.", "answer_type": "1", "text_help": ""},
    {"index": 7, "text": "OS 종류와 버전을 작성해 주세요.", "category": "IT PwC", "help": "예: 윈도우즈 서버 2012, Unix AIX, Linux Redhat 등", "answer_type": "2", "text_help": ""},
    {"index": 8, "text": "OS 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: Hiware, CyberArk 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 9, "text": "DB 종류와 버전을 작성해 주세요.", "category": "IT PwC", "help": "예: Oracle R12, MS SQL Server 2008 등", "answer_type": "2", "text_help": ""},
    {"index": 10, "text": "DB 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: DBi, DB Safer 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 11, "text": "별도의 Batch Schedule Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: Waggle, JobScheduler 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 12, "text": "사용자 권한부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "사용자A가 재무권한을 가지고 있었는데 당기에 구매권한을 추가로 받았을 경우 언제(날짜 등) 구매권한을 받았는지 시스템에서 관리되는 경우를 의미합니다.", "answer_type": "1", "text_help": ""},
    {"index": 13, "text": "사용자 권한회수 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "기존 권한 회수시 History를 관리하고 있는지를 확인합니다.<br>Standard 기능을 기준으로 SAP ERP의 경우 권한회수이력을 별도로 저장하며 Oracle ERP의 경우 권한 데이터를 삭제하지 않고 Effective Date로 관리합니다", "answer_type": "1", "text_help": ""},
    {"index": 14, "text": "사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) 새로운 권한이 필요한 경우 ITSM을 통해 요청서를 작성하고 팀장의 승인을 받은 후 IT팀에서 해당 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 15, "text": "부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?", "category": "APD", "help": "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 기존 권한을 회수함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 기존 권한을 회수함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 16, "text": "퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?", "category": "APD", "help": "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 접근권한을 차단함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 접근권한을 차단함", "answer_type": "4", "text_help": "관련 절차를 입력하세요"},
    {"index": 17, "text": "Application 관리자(Superuser) 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예1) IT운영팀 김xx 책임", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 18, "text": "전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?", "category": "APD", "help": "", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 19, "text": "패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 20, "text": "데이터 변경 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "시스템의 기능을 이용하여 데이터를 변경한 것이 아닌 관리자 등이 DB에 접속하여 쿼리를 통해 데이터를 변경한 건이 대상이며 해당 변경건만 추출이 가능해야 합니다", "answer_type": "1", "text_help": ""},
    {"index": 21, "text": "데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) 데이터 변경 필요시 담당자는 ITSM을 통해 요성서를 작성하고 책임자의 승인을 받은 후 IT담당자가 데이터를 변경함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 22, "text": "데이터 변경 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예1) IT운영팀 최xx 책임", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 23, "text": "DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 24, "text": "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) DB 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 25, "text": "DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예) 인프라관리팀 김xx 과장, DBA", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 26, "text": "DB 패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 27, "text": "OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "", "answer_type": "1", "text_help": ""},
    {"index": 28, "text": "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) OS 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 29, "text": "OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예) 인프라관리팀 이xx 책임, 보안관리자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 30, "text": "OS 패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 31, "text": "프로그램 변경 이력이 시스템에 기록되고 있습니까?", "category": "PC", "help": "변경에 대한 History가 시스템에 의해 기록되어야 합니다. A화면을 1, 3, 5월에 요청서를 받아 변경했다면 각각의 이관(배포)이력이 기록되어야 하며 자체기능, 배포툴, 형상관리툴 등을 사용할 수 있습니다.", "answer_type": "1", "text_help": ""},
    {"index": 32, "text": "프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 필요시 ITSM을 통해 요청서를 작성하고 부서장의 승인을 득함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 33, "text": "프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?", "category": "PC", "help": ") 프로그램 기능 변경 완료 후 요청자에 의해 사용자 테스트가 수행되고 그 결과가 문서화됨", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 34, "text": "프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 및 사용자 테스트 완료 후 변경담당자로부터 이관 요청서가 작성되고 부서장의 승인을 득함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 35, "text": "이관(배포)권한을 보유한 인원에 대해 기술해 주세요.", "category": "PC", "help": "예) 인프라관리팀 박xx 수석, 서버관리자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 36, "text": "운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?", "category": "PC", "help": "JSP, ASP 등으로 개발된 웹시스템의 경우 localhost 또는 127.0.0.1을 개발서버로도 볼 수 있습니다", "answer_type": "1", "text_help": ""},
    {"index": 37, "text": "배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?", "category": "CO", "help": "개발되어 등록된 배치 프로그램(Background Job)을 스케줄로 등록 또는 변경한 경우로 한정합니다. 배치 프로그램을 개발하여 운영서버에 반영하는 것은 이 경우에 포함되지 않습니다", "answer_type": "1", "text_help": ""},
    {"index": 38, "text": "배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "CO", "help": "예) 배치 스케줄이 필요한 경우 ITSM을 통해 요청서를 작성하고 승인권자의 승인을 득한 후 적절한 담당자에 의해 스케줄이 등록됨", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 39, "text": "배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.", "category": "CO", "help": "예) 시스템 운영팀 최xx 과장, 시스템운영자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 40, "text": "배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.", "category": "CO", "help": "예1) 매일 아침 배치수행결과를 확인하며 문서화하며 오류 발생시 원인파악 및 조치현황 등을 함께 기록함<br>예2) 오류 발생시에만 점검결과를 작성하며 오류 발생 기록은 삭제하지 않고 유지됨", "answer_type": "5", "text_help": ""},
    {"index": 41, "text": "장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.", "category": "CO", "help": "", "answer_type": "5", "text_help": ""},
    {"index": 42, "text": "백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.", "category": "CO", "help": "", "answer_type": "5", "text_help": ""},
    {"index": 43, "text": "서버실 출입시의 절차에 대해 기술해 주세요.", "category": "CO", "help": "", "answer_type": "5", "text_help": ""}
]

question_count = len(s_questions)

# --- 통제별 검토 기준 정의 (토큰 절약을 위해 간소화) ---
CONTROL_SPECIFIC_CRITERIA = {
    'APD01': [
        "권한 부여 이력이 시스템에 기록되는지 확인"
    ],
    'APD02': [
        "부서이동 시 자동 또는 수동 권한 회수 절차가 있는지 확인",
        "부서이동자가 직접 요청항 회수하는 경우는 인정 안됨"
    ],
    'APD03': [
        "퇴사자 발생 시 자동 또는 수동 권한 회수 절차가 있는지 확인"
    ],
    'APD04': [
        "Application 관리자 권한 보유 인원이 명확히 식별되는지 확인",
        "관리자 권한 보유자의 부서, 직급, 직무가 구체적으로 기술되어 있는지 확인",
        "권한 보유자가 1명인 것은 이슈가 아님"
    ],
    'APD05': [
        "사용자 권한 모니터링 절차가 정기적으로 수행되는지 확인",
        "모니터링 결과에 따른 조치 절차가 있는지 확인",
        "권한 검토 주기는 판단하지 않음"
    ],
    'APD06': [
        "Application 패스워드 최소 길이가 8자 이상인지 확인",
        "Application 패스워드 복잡성(영문/숫자/특수문자) 요구사항이 있는지 확인"
    ],
    'APD07': [
        "데이터 변경 이력이 시스템에 기록되는지 확인"
    ],
    'APD08': [
        "데이터 변경 권한 보유 인원이 명확히 식별되는지 확인",
        "권한 보유자가 1명인 것은 이슈가 아님"
    ],
    'APD09': [
        "DB 접근권한 부여 이력이 시스템에 기록되는지 확인"
    ],
    'APD10': [
        "DB 관리자 권한 보유 인원이 명확히 식별되는지 확인",
        "권한 보유자가 1명인 것은 이슈가 아님",
        "DB 관리자의 자격 요건이 적절한지 확인"
    ],
    'APD11': [
        "DB 패스워드 최소 길이가 8자 이상인지 확인",
        "DB 패스워드 복잡성(영문/숫자/특수문자) 요구사항이 있는지 확인"
    ],
    'APD12': [
        "OS 접근권한 부여 이력이 시스템에 기록되는지 확인"
    ],
    'APD13': [
        "OS 관리자 권한 보유 인원이 명확히 식별되는지 확인",
        "권한 보유자가 1명인 것은 이슈가 아님",
        "OS 관리자의 자격 요건이 적절한지 확인"
    ],
    'APD14': [
        "OS 패스워드 최소 길이가 8자 이상인지 확인",
        "OS 패스워드 복잡성(영문/숫자/특수문자) 요구사항이 있는지 확인"
    ],
    'PC01': [
        "프로그램 변경 이력이 시스템에 기록되는지 확인"
    ],
    'PC02': [
        "프로그램 변경 시 사용자 테스트 수행 절차가 있는지 확인",
        "사용자 테스트는 요청자가 수행하는 것이 정상",
        "테스트 결과 문서화 절차가 있는지 확인"
    ],
    'PC03': [
        "프로그램 변경 이관(배포) 승인 절차가 있는지 확인"
    ],
    'PC04': [
        "이관(배포) 권한 보유 인원이 명확히 식별되는지 확인",
        "권한 보유자가 1명인 것은 이슈가 아님"
    ],
    'PC05': [
        "운영환경과 개발/테스트 환경이 물리적 또는 논리적으로 분리되어 있는지 확인"
    ],
    'CO01': [
        "배치 스케줄 등록/변경 이력이 시스템에 기록되는지 확인"
    ],
    'CO02': [
        "배치 스케줄 등록/변경 권한 보유 인원이 명확히 식별되는지 확인",
        "권한 보유자가 1명인 것은 이슈가 아님"
    ],
    'CO03': [
        "배치 실행 결과 모니터링 절차가 있는지 확인",
        "모니터링 결과 문서화 및 보관 절차가 있는지 확인"
    ],
    'CO04': [
        "장애 발생 시 대응 절차가 명확하게 정의되어 있는지 확인",
        "장애 대응 담당자가 명확히 지정되어 있는지 확인",
        "장애 처리 결과 문서화 및 사후 분석 절차가 있는지 확인"
    ],
    'CO05': [
        "백업 수행 절차가 명확하게 정의되어 있는지 확인",
        "백업 결과 모니터링 및 확인 절차가 있는지 확인",
        "백업 데이터 복구 테스트가 정기적으로 수행되는지 확인"
    ],
    'CO06': [
        "서버실 출입 승인 절차가 있는지 확인",
        "서버실 출입 기록이 관리되는지 확인",
        "서버실 물리적 보안 체계가 적절한지 확인"
    ]
}

# --- 리팩토링: Ineffective 조건 체크 함수 ---
def is_ineffective(control, answers):
    conditions = {
        'APD01': len(answers) > 14 and (answers[12] == 'N' or answers[14] == 'N'),
        'APD02': len(answers) > 15 and answers[15] == 'N',
        'APD03': len(answers) > 16 and answers[16] == 'N',
        'APD04': len(answers) > 17 and answers[17] == 'N',
        'APD06': len(answers) > 20 and (answers[19] == 'N' or answers[20] == 'N'),
        'APD07': len(answers) > 22 and (answers[21] == 'N' or answers[22] == 'N'),
        'APD10': len(answers) > 26 and (answers[25] == 'N' or answers[26] == 'N'),
        'PC01': (len(answers) > 30 and answers[29] == 'N') or (len(answers) > 30 and answers[30] == 'N'),
        'PC02': (len(answers) > 31 and answers[29] == 'N') or (len(answers) > 31 and answers[31] == 'N'),
        'PC03': (len(answers) > 32 and answers[29] == 'N') or (len(answers) > 32 and answers[32] == 'N'),
        'PC05': len(answers) > 34 and answers[34] == 'N',
        'CO01': len(answers) > 36 and (answers[35] == 'N' or answers[36] == 'N'),
    }
    return conditions.get(control, False)

def get_ai_review(content, control_number=None):
    """
    AI를 사용하여 ITGC 내용을 검토하고 개선 제안을 반환합니다.
    Summary 시트의 C열(검토결과), D열(결론), E열(개선필요사항)에 맞는 구조화된 결과를 반환합니다.
    """
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 통제별 특정 기준만 가져오기 (토큰 절약)
        specific_criteria = CONTROL_SPECIFIC_CRITERIA.get(control_number, [])
        
        # 간소화된 기준 텍스트 생성 (토큰 절약)
        if specific_criteria:
            criteria_text = f"검토기준: " + ", ".join(specific_criteria)
        else:
            criteria_text = "기본기준: 담당자1명 허용, 절차/이력 부재시 미비점"
        
        # 공통 기준은 프롬프트에 간단히 포함
        common_note = "공통기준: 보완통제 유무는 검토대상 아님, 부서장승인 필요"

        prompt = f"""ITGC {control_number} 검토:
{content}

{criteria_text}
{common_note}

응답형식:
검토결과: [간결한 분석]
결론: [Effective/Ineffective]
개선필요사항: [Ineffective시만 3가지 이내, Effective시 공란]
"""

        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # 기본값으로 gpt-4o-mini 사용

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "ITGC 검토 전문가. 간결하고 정확한 검토 제공."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )

        ai_response = response.choices[0].message.content

        # AI 응답을 파싱하여 각 컬럼별로 분리
        result = {
            'review_result': '',  # C열: 검토결과
            'conclusion': '',     # D열: 결론
            'improvements': ''    # E열: 개선필요사항
        }

        lines = ai_response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('검토결과:'):
                result['review_result'] = line.replace('검토결과:', '').strip()
                current_section = 'review_result'
            elif line.startswith('결론:'):
                result['conclusion'] = line.replace('결론:', '').strip()
                current_section = 'conclusion'
            elif line.startswith('개선필요사항:'):
                result['improvements'] = line.replace('개선필요사항:', '').strip()
                current_section = 'improvements'
            elif line and current_section:
                # 다음 섹션이 시작되기 전까지 내용을 이어서 추가
                if not any(line.startswith(prefix) for prefix in ['검토결과:', '결론:', '개선필요사항:']):
                    if result[current_section]:
                        result[current_section] += '\n' + line
                    else:
                        result[current_section] = line

        return result

    except Exception as e:
        return {
            'review_result': f"AI 검토 중 오류 발생: {str(e)}",
            'conclusion': "검토 불가",
            'improvements': "AI 검토 시스템 점검 필요"
        }

# --- 리팩토링: 시트 값 입력 함수 ---
def fill_sheet(ws, text_data, answers):
    if 'A1' in text_data:
        ws['C7'] = text_data['A1']
    if 'B1' in text_data:
        ws['C8'] = text_data['B1']
    if 'B2' in text_data:
        ws['C12'] = text_data['B2']
        value = str(text_data['B2'])
        num_lines = value.count('\n') + 1
        approx_lines = num_lines + (len(value) // 50)
        ws.row_dimensions[12].height = 15 * approx_lines
    # B3: company_name, B5: user_name
    if len(answers) > 0 and answers[0]:
        company_name = "Company Name" # Placeholder for company name
        user_name = "User Name" # Placeholder for user name
        ws['B3'] = company_name
        ws['B5'] = user_name

def get_text_itgc(answers, control_number, textarea_answers=None, enable_ai_review=False):
    result = {}
    if textarea_answers is None:
        textarea_answers = [''] * len(answers)

    if control_number == 'APD01':
        result['A1'] = "APD01"
        result['B1'] = "사용자 신규 권한 승인"
        result['B2'] = "사용자 권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[12] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "새로운 권한 요청 시, 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[14]}" if textarea_answers[14] else "\n\n권한 부여 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[14] == 'Y' else "새로운 권한 요청 시 승인 절차가 없습니다.")

    elif control_number == 'APD02':
        result['A1'] = "APD02"
        result['B1'] = "부서이동자 권한 회수"
        result['B2'] = "사용자 권한 회수 이력이 시스템에 " + ("기록되고 있습니다." if answers[13] == 'Y' else "기록되지 않습니다.") + "\n\n" + (
            "부서 이동 시 기존 권한을 회수하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[15]}" if textarea_answers[15] else "\n\n부서 이동 시 권한 회수 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[15] == 'Y' else "부서 이동 시 기존 권한 회수 절차가 없습니다.")

    elif control_number == 'APD03':
        result['A1'] = "APD03"
        result['B1'] = "퇴사자 접근권한 회수"
        result['B2'] = "퇴사자 발생 시 접근권한을 " + ("차단하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[16] == 'Y' else "차단 절차가 없습니다.") + (
            f"\n{textarea_answers[16]}" if textarea_answers[16] else "\n퇴사자 접근권한 차단 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD04':
        result['A1'] = "APD04"
        result['B1'] = "Application 관리자 권한 제한"
        result['B2'] = "Application 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[17] if answers[17] else "Application 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD05':
        result['A1'] = "APD05"
        result['B1'] = "사용자 권한 Monitoring"
        result['B2'] = "전체 사용자가 보유한 권한에 대한 적절성을 " + ("모니터링하는 절차가 있습니다." if answers[18] == 'Y' else "모니터링 절차가 존재하지 않습니다.")

    elif control_number == 'APD06':
        result['A1'] = "APD06"
        result['B1'] = "Application 패스워드"
        result['B2'] = "패스워드 설정 사항은 아래와 같습니다 \n\n" + (answers[19] if answers[19] else "패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD07':
        result['A1'] = "APD07"
        result['B1'] = "데이터 직접 변경"
        result['B2'] = "데이터 변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[20] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "데이터 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[21]}" if textarea_answers[21] else "데이터 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[21] == 'Y' else "데이터 변경 시 승인 절차가 없습니다.")

    elif control_number == 'APD08':
            result['A1'] = "APD08"
            result['B1'] = "데이터 변경 권한 제한"
            result['B2'] = "데이터 변경 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[22] if answers[22] else "데이터 변경 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD09':
        result['A1'] = "APD09"
        result['B1'] = "DB 접근권한 승인"
        result['B2'] = f"DB 종류와 버전: {answers[9]}" + f"\n\nDB 접근제어 Tool 사용 여부: {'사용' if answers[10] == 'Y' else '미사용'}" + "\n\n" + (
            "DB 접근권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[23] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
                "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                    f"\n{textarea_answers[24]}" if textarea_answers[24] else "DB 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
                ) if answers[24] == 'Y' else "DB 접근권한 요청 시 승인 절차가 없습니다."
            )
        )

    elif control_number == 'APD10':
        result['A1'] = "APD10"
        result['B1'] = "DB 관리자 권한 제한"
        result['B2'] = "DB 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[25] if answers[25] else "DB 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD11':
        result['A1'] = "APD11"
        result['B1'] = "DB 패스워드"
        result['B2'] = "DB 패스워드 설정사항은 아래와 같습니다.\n" + (answers[26] if answers[26] else "DB 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD12':
        result['A1'] = "APD12"
        result['B1'] = "OS 접근권한 승인"
        result['B2'] = f"OS 종류와 버전: {answers[7]}" + f"\n\nOS 접근제어 Tool 사용 여부: {'사용' if answers[8] == 'Y' else '미사용'}" + "\n\n" + (
            "OS 접근권한 부여 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[27] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
                "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                    f"\n{textarea_answers[28]}" if textarea_answers[28] else "OS 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
                ) if answers[28] == 'Y' else "OS 접근권한 요청 시 승인 절차가 없습니다."
            )
        )

    elif control_number == 'APD13':
        result['A1'] = "APD13"
        result['B1'] = "OS 관리자 권한 제한"
        result['B2'] = "OS 관리자 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[29] if answers[29] else "OS 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'APD14':
        result['A1'] = "APD14"
        result['B1'] = "OS 패스워드"
        result['B2'] = "OS 패스워드 설정사항은 아래와 같습니다.\n" + (answers[30] if answers[30] else "OS 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC01':
        result['A1'] = "PC01"
        result['B1'] = "프로그램 변경 승인"
        result['B2'] = "프로그램 변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[31] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "프로그램 변경 시 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[32]}" if textarea_answers[32] else "\n프로그램 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[32] == 'Y' else "프로그램 변경 시 승인 절차가 없습니다.")

    elif control_number == 'PC02':
        result['A1'] = "PC02"
        result['B1'] = "프로그램 변경 사용자 테스트"
        result['B2'] = "프로그램 변경 시 사용자 테스트를 " + ("수행하고 그 결과를 문서화하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[33] == 'Y' else "수행하지 않습니다.") + (
            f"\n{textarea_answers[33]}" if textarea_answers[33] else "\n프로그램 변경 사용자 테스트 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC03':
        result['A1'] = "PC03"
        result['B1'] = "프로그램 변경 이관 승인"
        result['B2'] = "프로그램 변경 완료 후 이관(배포)을 위해 " + ("부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." if answers[34] == 'Y' else "이관(배포) 절차가 없습니다.") + (
            f"\n{textarea_answers[34]}" if textarea_answers[34] else "\n프로그램 변경 이관 승인 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC04':
        result['A1'] = "PC04"
        result['B1'] = "이관(배포) 권한 제한"
        result['B2'] = "이관(배포) 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[35] if answers[35] else "이관(배포) 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'PC05':
        result['A1'] = "PC05"
        result['B1'] = "개발/운영 환경 분리"
        result['B2'] = "운영서버 외 별도의 개발 또는 테스트 서버를 " + ("운용하고 있습니다." if answers[36] == 'Y' else "운용하지 않습니다.")

    elif control_number == 'CO01':
        result['A1'] = "CO01"
        result['B1'] = "배치 스케줄 등록/변경 승인"
        result['B2'] = "배치 스케줄 등록/변경 이력이 시스템에 " + ("기록되고 있어 모집단 확보가 가능합니다." if answers[37] == 'Y' else "기록되지 않아 모집단 확보가 불가합니다.") + "\n\n" + (
            "배치 스케줄 등록/변경 시 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다." + (
                f"\n{textarea_answers[38]}" if textarea_answers[38] else "\n배치 스케줄 등록/변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다."
            ) if answers[38] == 'Y' else "배치 스케줄 등록/변경 시 승인 절차가 없습니다.")

    elif control_number == 'CO02':
        result['A1'] = "CO02"
        result['B1'] = "배치 스케줄 등록/변경 권한 제한"
        result['B2'] = "배치 스케줄 등록/변경 권한을 보유한 인원은 아래와 같습니다.\n" + (answers[39] if answers[39] else "배치 스케줄 등록/변경 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO03':
        result['A1'] = "CO03"
        result['B1'] = "배치 실행 모니터링"
        result['B2'] = "배치 실행 오류 등에 대한 모니터링은 아래와 같이 수행되고 있습니다\n" + (answers[40] if answers[40] else "배치 실행 오류 등에 대한 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO04':
        result['A1'] = "CO04"
        result['B1'] = "장애 대응 절차"
        result['B2'] = "장애 발생시 이에 대응하고 조치하는 절차는 아래와 같습니다\n" + (answers[41] if answers[41] else "장애 발생시 이에 대응하고 조치하는 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO05':
        result['A1'] = "CO05"
        result['B1'] = "백업 및 모니터링"
        result['B2'] = "백업 수행 및 모니터링 절차는 아래와 같습니다.\n" + (answers[42] if answers[42] else "백업 수행 및 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.")

    elif control_number == 'CO06':
        result['A1'] = "CO06"
        result['B1'] = "서버실 출입 절차"
        result['B2'] = "서버실 출입 절차는 아래와 같습니다.\n" + (answers[43] if answers[43] else "서버실 출입 절차에 대한 상세 기술이 제공되지 않았습니다.")

    else:
        result['A1'] = f"Unknown control number: {control_number}"
        result['B1'] = ""
        result['B2'] = "알 수 없는 통제 번호입니다."

    # AI 검토 기능이 활성화되어 있고 B2 값이 있는 경우 AI 검토 수행
    if enable_ai_review and 'B2' in result and result['B2']:
        print(f"🤖 AI 검토 시작: {control_number}")
        ai_review = get_ai_review(result['B2'], control_number)
        result['AI_Review'] = ai_review
        # Summary 시트용 AI 검토 결과도 저장
        result['AI_Summary'] = ai_review
        print(f"✅ AI 검토 완료: {control_number}")

    return result

# link2_prev의 핵심 로직만 분리 (세션 객체는 snowball.py에서 전달)
def link2_prev_logic(session):
    question_index = session.get('question_index', 0)
    if question_index > 0:
        session['question_index'] = question_index - 1
    return session

def export_interview_excel_and_send(answers, textarea_answers, get_text_itgc, fill_sheet, is_ineffective, send_gmail_with_attachment, enable_ai_review=False):
    """
    인터뷰 답변을 받아 엑셀 파일을 생성하고 메일로 전송합니다.
    answers: list (사용자 답변)
    textarea_answers: list (텍스트에어리어 답변)
    get_text_itgc: 텍스트 생성 함수
    fill_sheet: 시트 채우기 함수
    is_ineffective: 비효과적 통제 체크 함수
    send_gmail_with_attachment: 메일 전송 함수
    """
    today = datetime.today().strftime('%Y%m%d')
    file_name = f"{answers[1]}_{today}.xlsx" if len(answers) > 1 and answers[1] else f"responses_{today}.xlsx"

    # 1. 템플릿 파일 불러오기
    template_path = os.path.join("static", "Design_Template.xlsx")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
    wb = load_workbook(template_path)

    # 2. Summary sheet에 작성할 AI 검토 결과 수집
    summary_ai_reviews = {}

    # 3. 각 통제별 시트에 값 입력
    control_list = [
        'APD01', 'APD02', 'APD03', 'APD04', 'APD05', 'APD06', 'APD07', 'APD08', 'APD09', 'APD10', 'APD11', 'APD12', 'APD13', 'APD14',
        'PC01', 'PC02', 'PC03', 'PC04', 'PC05',
        'CO01', 'CO02', 'CO03', 'CO04', 'CO05', 'CO06'
    ]
    for control in control_list:
        text_data = get_text_itgc(answers, control, textarea_answers, enable_ai_review)
        ws = wb[control]
        fill_sheet(ws, text_data, answers)

        # AI 검토 결과가 있는 경우 Summary 시트용 데이터 수집
        if enable_ai_review and 'AI_Summary' in text_data and isinstance(text_data['AI_Summary'], dict):
            summary_ai_reviews[control] = text_data['AI_Summary']

        # AI 검토 결과가 있는 경우와 없는 경우에 따라 C14 처리
        ai_review_processed = False
        if enable_ai_review and 'AI_Review' in text_data:
            if isinstance(text_data['AI_Review'], dict):
                # 결론만 C14에 기록
                conclusion = text_data['AI_Review'].get('conclusion', '')
                ws['C14'] = conclusion
                ai_review_processed = True

                # AI 결론이 Ineffective인 경우 시트 탭 색상을 빨간색으로 변경
                if 'Ineffective' in conclusion:
                    ws.sheet_properties.tabColor = "FF0000"

                # 전체 AI 검토 결과를 C15 셀에 추가 (기존 기능 유지)
                review_text = f"검토결과: {text_data['AI_Review'].get('review_result', '')}\n결론: {text_data['AI_Review'].get('conclusion', '')}\n개선필요사항: {text_data['AI_Review'].get('improvements', '')}"
                ws['C15'] = f"=== AI 검토 결과 ===\n{review_text}"
                # AI 검토 결과 셀의 높이 조정
                ai_review_lines = review_text.count('\n') + 1
                ws.row_dimensions[15].height = 15 * max(5, ai_review_lines // 3)
            else:
                # 기존 형식인 경우 그대로 C14에 기록
                ws['C14'] = str(text_data['AI_Review'])
                ai_review_processed = True

                # 기존 형식에서도 Ineffective 체크
                if 'Ineffective' in str(text_data['AI_Review']):
                    ws.sheet_properties.tabColor = "FF0000"

        # AI 검토 결과가 없는 경우에만 기존 로직 적용
        if not ai_review_processed and is_ineffective(control, answers):
            ws['C13'] = ''
            ws['C14'] = 'Ineffective'
            ws.sheet_properties.tabColor = "FF0000"
            # ws.sheet_properties.tabColor = "FF0000"
        #else:
        #    ws['C13'] = '화면 증빙을 첨부해주세요'

    # 4. Summary 시트에 AI 검토 결과 작성
    if enable_ai_review and summary_ai_reviews:
        try:
            # Summary 시트가 존재하는지 확인하고 없으면 생성
            if 'Summary' not in wb.sheetnames:
                summary_ws = wb.create_sheet('Summary')
                # 헤더 추가
                summary_ws['A1'] = '통제번호'
                summary_ws['B1'] = '통제명'
                summary_ws['C1'] = '검토결과'
                summary_ws['D1'] = '결론'
                summary_ws['E1'] = '개선필요사항'
            else:
                summary_ws = wb['Summary']

            # 통제명 매핑 딕셔너리
            control_names = {
                'APD01': '사용자 신규 권한 승인',
                'APD02': '부서이동자 권한 회수',
                'APD03': '퇴사자 접근권한 회수',
                'APD04': 'Application 관리자 권한 제한',
                'APD05': '사용자 권한 Monitoring',
                'APD06': 'Application 패스워드',
                'APD07': '데이터 직접 변경',
                'APD08': '데이터 변경 권한 제한',
                'APD09': 'DB 접근권한 승인',
                'APD10': 'DB 관리자 권한 제한',
                'APD11': 'DB 패스워드',
                'APD12': 'OS 접근권한 승인',
                'APD13': 'OS 관리자 권한 제한',
                'APD14': 'OS 패스워드',
                'PC01': '프로그램 변경 승인',
                'PC02': '프로그램 변경 사용자 테스트',
                'PC03': '프로그램 변경 이관 승인',
                'PC04': '이관(배포) 권한 제한',
                'PC05': '개발/운영 환경 분리',
                'CO01': '배치 스케줄 등록/변경 승인',
                'CO02': '배치 스케줄 등록/변경 권한 제한',
                'CO03': '배치 실행 모니터링',
                'CO04': '장애 대응 절차',
                'CO05': '백업 및 모니터링',
                'CO06': '서버실 출입 절차'
            }

            row_index = 2  # 헤더 다음 행부터 시작

            for control, ai_review in summary_ai_reviews.items():
                if isinstance(ai_review, dict):
                    # A열: 통제번호
                    summary_ws[f'A{row_index}'] = control
                    # B열: 통제명
                    summary_ws[f'B{row_index}'] = control_names.get(control, '')
                    # C열: 검토결과
                    review_result = ai_review.get('review_result', '')
                    if len(review_result) > 32767:  # 엑셀 셀 최대 문자 수 제한
                        review_result = review_result[:32760] + "..."
                    summary_ws[f'C{row_index}'] = review_result
                    # D열: 결론
                    summary_ws[f'D{row_index}'] = ai_review.get('conclusion', '')
                    # E열: 개선필요사항
                    improvements = ai_review.get('improvements', '')
                    if len(improvements) > 32767:  # 엑셀 셀 최대 문자 수 제한
                        improvements = improvements[:32760] + "..."
                    summary_ws[f'E{row_index}'] = improvements
                    row_index += 1
        except Exception as e:
            print(f"Summary 시트 작성 중 오류 발생: {str(e)}")
            # Summary 시트 오류가 발생해도 전체 프로세스는 계속 진행

    # 메모리 버퍼에 저장 (안전한 방식)
    excel_stream = BytesIO()
    excel_stream_copy = None
    try:
        # 엑셀 파일 저장 전 검증
        if not wb.worksheets:
            raise Exception("워크북에 시트가 없습니다.")
        
        wb.save(excel_stream)
        excel_stream.seek(0)

        # 전송용 복사본 생성
        excel_data = excel_stream.getvalue()
        
        # 파일 크기 검증 (최소 크기 체크)
        if len(excel_data) < 1000:  # 1KB 미만이면 문제가 있을 가능성
            raise Exception("생성된 엑셀 파일이 너무 작습니다. 파일 생성에 문제가 있을 수 있습니다.")
        
        excel_stream_copy = BytesIO(excel_data)
        
    except Exception as e:
        # 오류 발생 시 리소스 정리
        if excel_stream:
            excel_stream.close()
        if excel_stream_copy:
            excel_stream_copy.close()
        wb.close()
        raise Exception(f"엑셀 파일 생성 중 오류 발생: {str(e)}")
    finally:
        # 원본 스트림은 항상 닫기
        if excel_stream:
            excel_stream.close()

    user_email = ''
    if answers and answers[0]:
        user_email = answers[0]

    if user_email:
        subject = '인터뷰 결과 파일'
        body = '인터뷰 내용에 따라 ITGC 설계평가 문서를 첨부합니다.'
        try:
            # 파일 스트림 검증
            if not excel_stream_copy:
                raise Exception("엑셀 파일 스트림이 생성되지 않았습니다.")
            
            # 파일 스트림 위치 확인 및 리셋
            excel_stream_copy.seek(0)
            
            send_gmail_with_attachment(
                to=user_email,
                subject=subject,
                body=body,
                file_stream=excel_stream_copy,
                file_name=file_name
            )
            return True, user_email, None
        except Exception as e:
            return False, user_email, str(e)
        finally:
            # 전송 완료 후 스트림 정리
            if excel_stream_copy:
                excel_stream_copy.close()
            wb.close()
    else:
        # 이메일이 없는 경우에도 리소스 정리
        if excel_stream_copy:
            excel_stream_copy.close()
        wb.close()
        return False, None, '메일 주소가 입력되지 않았습니다. 1번 질문에 메일 주소를 입력해 주세요.'

def test_ai_review_feature():
    """
    AI 검토 기능을 테스트하는 함수 (Summary 시트 기능 포함)
    """
    # 테스트용 답변 데이터
    test_answers = ['test@example.com', 'Test System', 'Y'] + ['N'] * 40
    test_textarea_answers = [''] * 43

    # AI 검토 기능 활성화로 테스트
    result = get_text_itgc(test_answers, 'APD01', test_textarea_answers, enable_ai_review=True)

    print("=== AI 검토 기능 테스트 (Summary 시트 포함) ===")
    print(f"Control: APD01")
    print(f"B1: {result.get('B1', 'N/A')}")
    print(f"B2: {result.get('B2', 'N/A')}")
    print(f"AI Review 존재 여부: {'AI_Review' in result}")
    print(f"AI Summary 존재 여부: {'AI_Summary' in result}")

    if 'AI_Review' in result:
        ai_review = result['AI_Review']
        if isinstance(ai_review, dict):
            print(f"\n=== Summary 시트용 AI 검토 결과 ===")
            print(f"검토결과 (C열): {ai_review.get('review_result', 'N/A')}")
            print(f"결론 (D열): {ai_review.get('conclusion', 'N/A')}")
            print(f"개선필요사항 (E열): {ai_review.get('improvements', 'N/A')}")
        else:
            print(f"\n기존 형식 AI 검토 결과:\n{ai_review}")

    # 직접 AI 검토 함수 테스트
    test_content = "사용자 권한 부여 이력이 시스템에 기록되지 않아 모집단 확보가 불가합니다. 새로운 권한 요청 시 승인 절차가 없습니다."
    direct_ai_result = get_ai_review(test_content, 'APD01')

    print(f"\n=== 직접 AI 검토 함수 테스트 ===")
    if isinstance(direct_ai_result, dict):
        print(f"검토결과: {direct_ai_result.get('review_result', 'N/A')}")
        print(f"결론: {direct_ai_result.get('conclusion', 'N/A')}")
        print(f"개선필요사항: {direct_ai_result.get('improvements', 'N/A')}")
    else:
        print(f"오류 또는 예상치 못한 형식: {direct_ai_result}")

    return result

if __name__ == "__main__":
    test_ai_review_feature()