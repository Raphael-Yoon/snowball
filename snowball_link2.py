from datetime import datetime
import os
import re
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ================================
# AI 문장 다듬기 설정 (수기 조정 가능)
# ================================

# ===========================================
# 📝 AI 문장 다듬기 규칙 설정 (여기서 수정하세요!)
# ===========================================

# AI 프롬프트 템플릿 (토큰 절약을 위해 간소화)
AI_REFINEMENT_PROMPT = """문법교정만 하세요. 내용변경금지.

{answer_text}

오타수정, 문체통일, "답변:" 등 제거"""

# OpenAI 모델 설정
AI_MODEL_CONFIG = {
    'model': 'gpt-4o-mini',  # 사용할 모델 (gpt-4o-mini는 저렴)
    'max_tokens': 800,       # 최대 토큰 수
    'temperature': 0.3       # 창의성 수준 (0.0-1.0, 낮을수록 일관적)
}

# 텍스트 길이 제한 (토큰 절약)
TEXT_LENGTH_LIMITS = {
    'min_length': 20,        # 이보다 짧으면 AI 다듬기 건너뜀 (Summary 시트 포함을 위해 낮춤)
    'max_length': 2000,      # 이보다 길면 AI 다듬기 건너뜀
}

# 제거할 접두사 목록 (AI 응답에서 자동 제거)
PREFIXES_TO_REMOVE = [
    '답변:', '결과:', '개선된 답변:', '수정된 답변:', '다듬어진 답변:', '교정된 답변:',
    '중요한 규칙:', '지침:', '교정된 텍스트:', '수정된 내용:', '개선 결과:'
]

# 제거할 불필요한 문구 목록 (AI 응답 중간에 나타날 수 있는 메타 정보)
UNWANTED_PHRASES = [
    '중요한 규칙:', '지침:', '다음은 교정된 내용입니다:', 
    '교정된 텍스트는 다음과 같습니다:', '개선된 버전:'
]

# 자동 문단 나누기 설정
AUTO_PARAGRAPH_BREAK = {
    'enable_sentence_break': True,   # 마침표 뒤 자동 줄바꿈 (예: "있습니다. 새로운" → "있습니다.\n\n새로운")
    'enable_phrase_break': True,     # "아래와 같습니다" 뒤 자동 줄바꿈
}

# 추가 텍스트 처리 규칙
TEXT_PROCESSING_RULES = {
    'remove_double_spaces': True,    # 이중 공백 제거
    'unify_punctuation': True,       # 문장부호 통일 (예: "。" → ".")
    'normalize_line_breaks': True,   # 줄바꿈 정규화
}

# ITGC 통제 정의 (반복 코드 제거를 위한 데이터 구조)
ITGC_CONTROLS = {
    'APD01': {
        'title': '사용자 신규 권한 승인',
        'template': '사용자 권한 부여 이력이 시스템에 {history_status}\n\n{procedure_text}',
        'history_idx': 6,
        'procedure_idx': 8,
        'textarea_idx': 8,
        'history_yes': '기록되고 있어 모집단 확보가 가능합니다.',
        'history_no': '기록되지 않아 모집단 확보가 불가합니다.',
        'procedure_prefix': '새로운 권한 요청 시, 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '새로운 권한 요청 시 승인 절차가 없습니다.',
        'default_msg': '권한 부여 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD02': {
        'title': '부서이동자 권한 회수',
        'template': '사용자 권한 회수 이력이 시스템에 {history_status}\n\n{procedure_text}',
        'history_idx': 7,
        'procedure_idx': 9,
        'textarea_idx': 9,
        'history_yes': '기록되고 있습니다.',
        'history_no': '기록되지 않습니다.',
        'procedure_prefix': '부서 이동 시 기존 권한을 회수하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '부서 이동 시 기존 권한 회수 절차가 없습니다.',
        'default_msg': '부서 이동 시 권한 회수 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD03': {
        'title': '퇴사자 접근권한 회수',
        'type': 'simple_procedure',
        'procedure_idx': 10,
        'textarea_idx': 10,
        'procedure_prefix': '퇴사자 발생 시 접근권한을 차단하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '퇴사자 발생 시 접근권한을 차단 절차가 없습니다.',
        'default_msg': '퇴사자 접근권한 차단 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD04': {
        'title': 'Application 관리자 권한 제한',
        'type': 'simple_list',
        'template': 'Application 관리자 권한을 보유한 인원은 아래와 같습니다.\n\n{content}',
        'answer_idx': 11,
        'default_msg': 'Application 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD05': {
        'title': '사용자 권한 Monitoring',
        'type': 'simple_status',
        'template': '전체 사용자가 보유한 권한에 대한 적절성을 {status}',
        'answer_idx': 12,
        'status_yes': '모니터링하는 절차가 있습니다.',
        'status_no': '모니터링 절차가 존재하지 않습니다.'
    },
    'APD06': {
        'title': 'Application 패스워드',
        'type': 'simple_list',
        'template': '패스워드 설정 사항은 아래와 같습니다.\n\n{content}',
        'answer_idx': 13,
        'default_msg': '패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD07': {
        'title': '데이터 직접 변경',
        'template': '데이터 변경 이력이 시스템에 {history_status}\n\n{procedure_text}',
        'history_idx': 14,
        'procedure_idx': 15,
        'textarea_idx': 15,
        'history_yes': '기록되고 있어 모집단 확보가 가능합니다.',
        'history_no': '기록되지 않아 모집단 확보가 불가합니다.',
        'procedure_prefix': '데이터 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '데이터 변경 시 승인 절차가 없습니다.',
        'default_msg': '데이터 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD08': {
        'title': '데이터 변경 권한 제한',
        'type': 'simple_list',
        'template': '데이터 변경 권한을 보유한 인원은 아래와 같습니다.\n\n{content}',
        'answer_idx': 16,
        'default_msg': '데이터 변경 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD09': {
        'title': 'DB 접근권한 승인',
        'type': 'complex_db',
        'db_type_idx': 18,
        'db_tool_idx': 19,
        'history_idx': 20,
        'procedure_idx': 21,
        'textarea_idx': 21,
        'history_yes': '기록되고 있어 모집단 확보가 가능합니다.',
        'history_no': '기록되지 않아 모집단 확보가 불가합니다.',
        'procedure_prefix': 'DB 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': 'DB 접근권한 요청 시 승인 절차가 없습니다.',
        'default_msg': 'DB 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD10': {
        'title': 'DB 관리자 권한 제한',
        'type': 'simple_list',
        'template': 'DB 관리자 권한을 보유한 인원은 아래와 같습니다.\n\n{content}',
        'answer_idx': 22,
        'default_msg': 'DB 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD11': {
        'title': 'DB 패스워드',
        'type': 'simple_list',
        'template': 'DB 패스워드 설정사항은 아래와 같습니다.\n\n{content}',
        'answer_idx': 23,
        'default_msg': 'DB 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD12': {
        'title': 'OS 접근권한 승인',
        'type': 'complex_os',
        'os_type_idx': 25,
        'os_tool_idx': 26,
        'history_idx': 27,
        'procedure_idx': 28,
        'textarea_idx': 28,
        'history_yes': '기록되고 있어 모집단 확보가 가능합니다.',
        'history_no': '기록되지 않아 모집단 확보가 불가합니다.',
        'procedure_prefix': 'OS 접근권한이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': 'OS 접근권한 요청 시 승인 절차가 없습니다.',
        'default_msg': 'OS 접근권한 승인 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD13': {
        'title': 'OS 관리자 권한 제한',
        'type': 'simple_list',
        'template': 'OS 관리자 권한을 보유한 인원은 아래와 같습니다.\n\n{content}',
        'answer_idx': 29,
        'default_msg': 'OS 관리자 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'APD14': {
        'title': 'OS 패스워드',
        'type': 'simple_list',
        'template': 'OS 패스워드 설정사항은 아래와 같습니다.\n\n{content}',
        'answer_idx': 30,
        'default_msg': 'OS 패스워드 설정 사항에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'PC01': {
        'title': '프로그램 변경 승인',
        'template': '프로그램 변경 이력이 시스템에 {history_status}\n\n{procedure_text}',
        'history_idx': 32,
        'procedure_idx': 33,
        'textarea_idx': 33,
        'history_yes': '기록되고 있어 모집단 확보가 가능합니다.',
        'history_no': '기록되지 않아 모집단 확보가 불가합니다.',
        'procedure_prefix': '프로그램 변경 시 요청서를 작성하고 부서장의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '프로그램 변경 시 승인 절차가 없습니다.',
        'default_msg': '프로그램 변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'PC02': {
        'title': '프로그램 변경 사용자 테스트',
        'type': 'simple_procedure',
        'procedure_idx': 34,
        'textarea_idx': 34,
        'procedure_prefix': '프로그램 변경 시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '프로그램 변경 시 사용자 테스트를 수행하지 않습니다.',
        'default_msg': '프로그램 변경 사용자 테스트 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'PC03': {
        'title': '프로그램 변경 이관 승인',
        'type': 'simple_procedure',
        'procedure_idx': 35,
        'textarea_idx': 35,
        'procedure_prefix': '프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '프로그램 변경 완료 후 이관(배포) 절차가 없습니다.',
        'default_msg': '프로그램 변경 이관 승인 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'PC04': {
        'title': '이관(배포) 권한 제한',
        'type': 'simple_list',
        'template': '이관(배포) 권한을 보유한 인원은 아래와 같습니다.\n\n{content}',
        'answer_idx': 36,
        'default_msg': '이관(배포) 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'PC05': {
        'title': '개발/운영 환경 분리',
        'type': 'simple_status',
        'template': '운영서버 외 별도의 개발 또는 테스트 서버를 {status}',
        'answer_idx': 37,
        'status_yes': '운용하고 있습니다.',
        'status_no': '운용하지 않습니다.'
    },
    'CO01': {
        'title': '배치 스케줄 등록/변경 승인',
        'template': '배치 스케줄 등록/변경 이력이 시스템에 {history_status}\n\n{procedure_text}',
        'history_idx': 40,
        'procedure_idx': 41,
        'textarea_idx': 41,
        'history_yes': '기록되고 있어 모집단 확보가 가능합니다.',
        'history_no': '기록되지 않아 모집단 확보가 불가합니다.',
        'procedure_prefix': '배치 스케줄 등록/변경 시 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있으며 그 절차는 아래와 같습니다.',
        'procedure_no': '배치 스케줄 등록/변경 시 승인 절차가 없습니다.',
        'default_msg': '배치 스케줄 등록/변경 승인 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'CO02': {
        'title': '배치 스케줄 등록/변경 권한 제한',
        'type': 'simple_list',
        'template': '배치 스케줄 등록/변경 권한을 보유한 인원은 아래와 같습니다.\n\n{content}',
        'answer_idx': 42,
        'default_msg': '배치 스케줄 등록/변경 권한을 보유한 인원에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'CO03': {
        'title': '배치 실행 모니터링',
        'type': 'simple_list',
        'template': '배치 실행 오류 등에 대한 모니터링은 아래와 같이 수행되고 있습니다.\n\n{content}',
        'answer_idx': 43,
        'default_msg': '배치 실행 오류 등에 대한 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'CO04': {
        'title': '장애 대응 절차',
        'type': 'simple_list',
        'template': '장애 발생시 이에 대응하고 조치하는 절차는 아래와 같습니다.\n\n{content}',
        'answer_idx': 45,
        'default_msg': '장애 발생시 이에 대응하고 조치하는 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'CO05': {
        'title': '백업 및 모니터링',
        'type': 'simple_list',
        'template': '백업 수행 및 모니터링 절차는 아래와 같습니다.\n\n{content}',
        'answer_idx': 46,
        'default_msg': '백업 수행 및 모니터링 절차에 대한 상세 기술이 제공되지 않았습니다.'
    },
    'CO06': {
        'title': '서버실 출입 절차',
        'type': 'simple_list',
        'template': '서버실 출입 절차는 아래와 같습니다.\n\n{content}',
        'answer_idx': 47,
        'default_msg': '서버실 출입 절차에 대한 상세 기술이 제공되지 않았습니다.'
    }
}
# 인터뷰 질문 리스트 (생략 없이 전체 복사)
s_questions = [
    {"index": 0, "text": "산출물을 전달받을 e-Mail 주소를 입력해주세요.", "category": "Complete", "help": "인터뷰 완료 후 최종 평가 결과 및 관련 산출물을 받을 이메일 주소를 입력하세요.<br>예: admin@company.com", "answer_type": "2", "text_help": ""},
    {"index": 1, "text": "시스템 이름을 적어주세요.", "category": "IT PwC", "help": "평가 대상이 되는 정보시스템의 이름을 입력하세요.<br>예: SAP ERP, 인사관리시스템, 회계시스템, 고객관리시스템 등", "answer_type": "2", "text_help": ""},
    {"index": 2, "text": "사용하고 있는 시스템은 상용소프트웨어입니까?", "category": "IT PwC", "help": "", "answer_type": "3", "text_help": "SAP ERP, Oracle ERP, 더존ERP 등"},
    {"index": 3, "text": "Cloud 서비스를 사용하고 있습니까?", "category": "IT PwC", "help": "해당 시스템이 클라우드 환경에서 운영되고 있는지 확인하는 질문입니다.<br>- 예: AWS, Azure, GCP 등의 클라우드 서비스를 이용<br>- 아니오: 자체 데이터센터나 온프레미스 환경에서 운영", "answer_type": "1", "text_help": ""},
    {"index": 4, "text": "어떤 종류의 Cloud입니까?", "category": "IT PwC", "help": "SaaS (Software as a Service): 사용자가 직접 설치 및 관리할 필요 없이, 클라우드에서 제공되는 ERP 소프트웨어를 사용하는 방식.<br>예: SAP S/4HANA Cloud, Oracle NetSuite, Microsoft Dynamics 365<br><br>PaaS (Platform as a Service): 애플리케이션 개발 및 배포를 위한 플랫폼을 클라우드에서 제공하는 방식.<br>예: Microsoft Azure App Service, Google App Engine<br><br>IaaS (Infrastructure as a Service): 기업이 자체적으로 ERP 시스템을 구축하고 운영할 수 있도록 서버, 스토리지, 네트워크 등의 인프라를 제공하는 방식.<br>예: AWS EC2, Microsoft Azure Virtual Machines, Google Cloud Compute Engine", "answer_type": "6", "text_help": "SaaS|PaaS|IaaS"},
    {"index": 5, "text": "Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?", "category": "IT PwC", "help": "SOC 1 Report (Service Organization Control 1 보고서)는 재무 보고와 관련된 내부 통제 사항을 검증하는 보고서입니다.", "answer_type": "1", "text_help": ""},
    {"index": 6, "text": "사용자 권한부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "사용자A가 재무권한을 가지고 있었는데 당기에 구매권한을 추가로 받았을 경우 언제(날짜 등) 구매권한을 받았는지 시스템에서 관리되는 경우를 의미합니다.", "answer_type": "1", "text_help": ""},
    {"index": 7, "text": "사용자 권한회수 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "기존 권한 회수시 History를 관리하고 있는지를 확인합니다.<br>Standard 기능을 기준으로 SAP ERP의 경우 권한회수이력을 별도로 저장하며 Oracle ERP의 경우 권한 데이터를 삭제하지 않고 Effective Date로 관리합니다", "answer_type": "1", "text_help": ""},
    {"index": 8, "text": "사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) 새로운 권한이 필요한 경우 ITSM을 통해 요청서를 작성하고 팀장의 승인을 받은 후 IT팀에서 해당 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 9, "text": "부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?", "category": "APD", "help": "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 기존 권한을 회수함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 기존 권한을 회수함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 10, "text": "퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?", "category": "APD", "help": "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 접근권한을 차단함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 접근권한을 차단함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 11, "text": "Application 관리자(Superuser) 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예1) IT운영팀 김xx 책임", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 12, "text": "전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?", "category": "APD", "help": "사용자에게 부여된 권한이 현재 업무에 적합한지를 주기적으로 검토하는 절차를 의미합니다.<br>예: 매분기 사용자 권한 적정성 검토 수행, 부서이동 시 기존 권한 회수 및 새로운 권한 부여 모니터링", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 13, "text": "패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 14, "text": "회사에서 DB에 접속하여 필요한 작업을 수행하는 것이 가능하십니까?", "category": "APD", "help": "회사에서 데이터가 저장된 곳에 직접 들어가서 데이터를 확인하거나 수정할 수 있는지를 묻는 질문입니다.<br><br>예시:<br>- 가능한 경우: IT 관리자가 데이터베이스에 직접 접속해서 고객 정보를 수정하거나 조회할 수 있음<br>- 불가능한 경우: 모든 데이터 작업은 시스템 화면을 통해서만 가능하고, 데이터베이스에 직접 들어갈 수 없음<br><br>이 질문에 '아니오'로 답하면, 데이터베이스 관련 검토 항목들은 해당되지 않는 것으로 처리됩니다.", "answer_type": "1", "text_help": ""},
    {"index": 15, "text": "데이터 변경 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "시스템의 기능을 이용하여 데이터를 변경한 것이 아닌 관리자 등이 DB에 접속하여 쿼리를 통해 데이터를 변경한 건이 대상이며 해당 변경건만 추출이 가능해야 합니다", "answer_type": "1", "text_help": ""},
    {"index": 16, "text": "데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) 데이터 변경 필요시 담당자는 ITSM을 통해 요성서를 작성하고 책임자의 승인을 받은 후 IT담당자가 데이터를 변경함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 17, "text": "데이터 변경 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예1) IT운영팀 최xx 책임", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 18, "text": "DB 종류와 버전을 작성해 주세요.", "category": "IT PwC", "help": "예: Oracle R12, MS SQL Server 2008 등", "answer_type": "2", "text_help": ""},
    {"index": 19, "text": "DB 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: DBi, DB Safer 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 20, "text": "DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "데이터베이스 접근 권한을 부여한 날짜, 사용자, 부여자, 권한 종류 등의 이력이 시스템에 기록되고 있는지 확인하는 질문입니다.<br>예: 권한 부여 시 로그 기록, DB 내장 관리 시스템에의 이력 저장", "answer_type": "1", "text_help": ""},
    {"index": 21, "text": "DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) DB 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 22, "text": "DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예) 인프라관리팀 김xx 과장, DBA", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 23, "text": "DB 패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 24, "text": "회사에서 OS서버에 접속하여 필요한 작업을 수행하는 것이 가능하십니까?", "category": "APD", "help": "운영체제(OS) 수준에서 서버에 직접 접속하여 시스템 관리, 파일 수정, 로그 확인 등의 작업을 수행할 수 있는지를 확인하는 질문입니다.<br>예: SSH, Telnet, RDP 등을 통한 서버 접속 가능 여부<br>이 질문의 답변이 '아니오'일 경우, OS 관련 통제(APD12, APD13, APD14)는 해당사항이 없는 것으로 처리됩니다.", "answer_type": "1", "text_help": ""},
    {"index": 25, "text": "OS 종류와 버전을 작성해 주세요.", "category": "IT PwC", "help": "예: 윈도우즈 서버 2012, Unix AIX, Linux Redhat 등", "answer_type": "2", "text_help": ""},
    {"index": 26, "text": "OS 접근제어 Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: Hiware, CyberArk 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 27, "text": "OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?", "category": "APD", "help": "운영체제 수준의 접근 권한을 부여한 날짜, 사용자, 부여자, 권한 내용 등의 이력이 시스템에 기록되고 있는지 확인하는 질문입니다.<br>예: Active Directory 로그, 리눅스 audit 로그, 보안 관리 솔루션 내 이력 관리", "answer_type": "1", "text_help": ""},
    {"index": 28, "text": "OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "APD", "help": "예) OS 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 29, "text": "OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.", "category": "APD", "help": "예) 인프라관리팀 이xx 책임, 보안관리자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 30, "text": "OS 패스워드 설정사항을 기술해 주세요.", "category": "APD", "help": "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등", "answer_type": "5", "text_help": ""},
    {"index": 31, "text": "주요 로직을 회사내부에서 수정하여 사용할 수 있습니까?", "category": "IT PwC", "help": "시스템의 핵심 기능을 회사에서 직접 변경할 수 있는지를 의미합니다.<br>예:<br>- 가능: 회사 개발팀이 계산 방식이나 업무 절차를 수정할 수 있음<br>- 불가능: 외부에서 만든 패키지 소프트웨어로 수정 불가", "answer_type": "1", "text_help": ""},
    {"index": 32, "text": "프로그램 변경 이력이 시스템에 기록되고 있습니까?", "category": "PC", "help": "변경에 대한 History가 시스템에 의해 기록되어야 합니다. A화면을 1, 3, 5월에 요청서를 받아 변경했다면 각각의 이관(배포)이력이 기록되어야 하며 자체기능, 배포툴, 형상관리툴 등을 사용할 수 있습니다.", "answer_type": "1", "text_help": ""},
    {"index": 33, "text": "프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 필요시 ITSM을 통해 요청서를 작성하고 부서장의 승인을 득함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 34, "text": "프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 완료 후 요청자에 의해 사용자 테스트가 수행되고 그 결과가 문서화됨", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 35, "text": "프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "PC", "help": "예) 프로그램 기능 변경 및 사용자 테스트 완료 후 변경담당자로부터 이관 요청서가 작성되고 부서장의 승인을 득함", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 36, "text": "이관(배포)권한을 보유한 인원에 대해 기술해 주세요.", "category": "PC", "help": "예) 인프라관리팀 박xx 수석, 서버관리자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 37, "text": "운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?", "category": "PC", "help": "JSP, ASP 등으로 개발된 웹시스템의 경우 localhost 또는 127.0.0.1을 개발서버로도 볼 수 있습니다", "answer_type": "1", "text_help": ""},
    {"index": 38, "text": "현재 실행중인 배치 스케줄이 있습니까?", "category": "CO", "help": "시스템이 정해진 시간에 자동으로 수행하는 작업이 있는지 확인하는 질문입니다.<br>예:<br>- 매일 밤 12시에 주문 데이터 집계 작업<br>- 매월 말 월천결산 데이터 백업<br>- 매주 월요일 사용자 권한 점검", "answer_type": "1", "text_help": ""},
    {"index": 39, "text": "별도의 Batch Schedule Tool을 사용하고 있습니까?", "category": "IT PwC", "help": "예: Waggle, JobScheduler 등", "answer_type": "3", "text_help": "제품명을 입력하세요"},
    {"index": 40, "text": "배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?", "category": "CO", "help": "개발되어 등록된 배치 프로그램(Background Job)을 스케줄로 등록 또는 변경한 경우로 한정합니다. 배치 프로그램을 개발하여 운영서버에 반영하는 것은 이 경우에 포함되지 않습니다", "answer_type": "1", "text_help": ""},
    {"index": 41, "text": "배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?", "category": "CO", "help": "예) 배치 스케줄이 필요한 경우 ITSM을 통해 요청서를 작성하고 승인권자의 승인을 득한 후 적절한 담당자에 의해 스케줄이 등록됨", "answer_type": "4", "text_help": "관련 절차를 입력하세요."},
    {"index": 42, "text": "배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.", "category": "CO", "help": "예) 시스템 운영팀 최xx 과장, 시스템운영자", "answer_type": "5", "text_help": "권한 보유 인원의 부서, 직급, 직무 등"},
    {"index": 43, "text": "배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.", "category": "CO", "help": "예1) 매일 아침 배치수행결과를 확인하며 문서화하며 오류 발생시 원인파악 및 조치현황 등을 함께 기록함<br>예2) 오류 발생시에만 점검결과를 작성하며 오류 발생 기록은 삭제하지 않고 유지됨", "answer_type": "5", "text_help": ""},
    {"index": 44, "text": "장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.", "category": "CO", "help": "시스템에 문제가 생겼을 때 어떻게 대처하고 해결하는지에 대한 절차를 설명해 주세요.<br>예:<br>- 시스템 중단 시 연락체계 및 복구 절차<br>- 데이터 오류 발견 시 수정 및 보고 절차<br>- 외부 공격이나 보안 사고 대응 방법", "answer_type": "5", "text_help": ""},
    {"index": 45, "text": "백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.", "category": "CO", "help": "시스템의 데이터를 안전하게 복사해서 보조하는 방법과 이것이 제대로 되고 있는지 확인하는 방법을 설명해 주세요.<br>예:<br>- 매일 밤에 전체 데이터 복사 후 외부 저장장치에 저장<br>- 백업 완료 시 알림 메일 발송<br>- 주기적으로 백업 데이터 복구 테스트 수행", "answer_type": "5", "text_help": ""},
    {"index": 46, "text": "서버실 출입시의 절차에 대해 기술해 주세요.", "category": "CO", "help": "서버나 주요 IT 장비가 있는 방에 들어갈 때의 보안 절차를 설명해 주세요.<br>예:<br>- 신분증 확인 및 출입자 명부 작성<br>- 보안카드나 비밀번호로 출입문 통과<br>- 출입 시간 기록 및 CCTV 모니터링<br>- 외부 인원의 경우 동반자 필요 여부", "answer_type": "5", "text_help": ""}
]

question_count = len(s_questions)

# --- 조건부 질문 생략 로직 ---
def get_conditional_questions(answers):
    """
    답변에 따라 조건부로 질문을 필터링하는 함수
    """
    print(f"[SKIP DEBUG] get_conditional_questions 호출됨, 답변 수: {len(answers) if answers else 0}")
    
    if not answers or len(answers) < 4:
        print(f"[SKIP DEBUG] 답변 부족, 전체 질문 반환")
        return s_questions
    
    skip_ranges = []
    
    # 3번 답변이 N이면 4~5번 질문 생략
    if len(answers) > 3 and answers[3] and str(answers[3]).upper() == 'N':
        skip_ranges.append((4, 5))
        print(f"[SKIP DEBUG] 3번 답변 'N' -> 4~5번 스킵")
    
    # 14번 답변이 N이면 15~23번 질문 생략
    if len(answers) > 14 and answers[14] and str(answers[14]).upper() == 'N':
        skip_ranges.append((15, 23))
        print(f"[SKIP DEBUG] 14번 답변 'N' -> 15~23번 스킵")
    
    # 24번 답변이 N이면 25~30번 질문 생략
    if len(answers) > 24 and answers[24] and str(answers[24]).upper() == 'N':
        skip_ranges.append((25, 30))
        print(f"[SKIP DEBUG] 24번 답변 'N' -> 25~30번 스킵")
    
    # 31번 답변이 N이면 32~37번 질문 생략
    if len(answers) > 31 and answers[31] and str(answers[31]).upper() == 'N':
        skip_ranges.append((32, 37))
        print(f"[SKIP DEBUG] 31번 답변 'N' -> 32~37번 스킵")
    
    # 38번 답변이 N이면 39~43번 질문 생략
    if len(answers) > 38 and answers[38] and str(answers[38]).upper() == 'N':
        skip_ranges.append((39, 43))
        print(f"[SKIP DEBUG] 38번 답변 'N' -> 39~43번 스킵")
    
    print(f"[SKIP DEBUG] 스킵 범위: {skip_ranges}")
    
    if not skip_ranges:
        print(f"[SKIP DEBUG] 스킵할 질문 없음, 전체 질문 반환")
        return s_questions
    
    filtered_questions = []
    skipped_count = 0
    for question in s_questions:
        question_index = question['index']
        should_skip = False
        
        for start, end in skip_ranges:
            if start <= question_index <= end:
                should_skip = True
                skipped_count += 1
                break
        
        if not should_skip:
            filtered_questions.append(question)
    
    print(f"[SKIP DEBUG] {skipped_count}개 질문 스킵됨, 필터링된 질문 수: {len(filtered_questions)}")
    return filtered_questions

def get_conditional_question_count(answers):
    """
    조건부 질문 생략을 고려한 총 질문 수 반환
    """
    conditional_questions = get_conditional_questions(answers)
    return len(conditional_questions)

def get_skipped_controls(answers):
    """
    스킵된 질문과 관련된 통제 목록을 반환
    """
    skipped_controls = set()
    
    if not answers or len(answers) < 4:
        return skipped_controls
    
    # 3번 답변이 N이면 Cloud 관련 통제는 해당없음 (현재는 별도 통제가 없음)
    
    # 17번 답변이 N이면 DB 관련 통제는 해당없음
    if len(answers) > 17 and answers[17] and str(answers[17]).upper() == 'N':
        skipped_controls.update(['APD09', 'APD10', 'APD11'])
    
    # 24번 답변이 N이면 OS 관련 통제는 해당없음
    if len(answers) > 24 and answers[24] and str(answers[24]).upper() == 'N':
        skipped_controls.update(['APD12', 'APD13', 'APD14'])
    
    # 31번 답변이 N이면 PC 관련 통제는 해당없음
    if len(answers) > 31 and answers[31] and str(answers[31]).upper() == 'N':
        skipped_controls.update(['PC01', 'PC02', 'PC03', 'PC04', 'PC05'])
    
    # 38번 답변이 N이면 배치 관련 통제(CO01-03)는 해당없음
    if len(answers) > 38 and answers[38] and str(answers[38]).upper() == 'N':
        skipped_controls.update(['CO01', 'CO02', 'CO03'])
    
    print(f"[SKIP DEBUG] 스킵된 통제 목록: {skipped_controls}")
    return skipped_controls

def set_sheet_tab_color_for_skipped_controls(wb, answers):
    """
    스킵된 통제에 해당하는 시트 탭을 회색으로 설정
    """
    skipped_controls = get_skipped_controls(answers)
    
    for sheet_name in wb.sheetnames:
        if sheet_name in skipped_controls:
            try:
                ws = wb[sheet_name]
                # 시트 탭을 회색으로 설정 (RGB: 808080)
                ws.sheet_properties.tabColor = "808080"
                print(f"[SHEET COLOR] {sheet_name} 시트를 회색으로 설정했습니다.")
            except Exception as e:
                print(f"[SHEET COLOR] {sheet_name} 시트 색상 설정 실패: {e}")
    
    print(f"[SHEET COLOR] 총 {len(skipped_controls)}개 통제 시트를 회색으로 처리했습니다.")

# --- 통제별 검토 기준 정의 (수기 수정 가능) ---
# 공통 감사기준 (엄격한 전문 접근)
COMMON_AUDIT_CRITERIA = [
    "명시적으로 '모집단 확보가 불가'라고 기술된 경우는 Ineffective",
    "명시적으로 '절차가 없다'고 기술된 경우는 Ineffective",
    "이력이 기록되고 적절한 절차가 있으면 Effective",
    "통제 목적이 달성되고 있으면 Effective",
    "소규모 회사의 현실적 제약을 고려하되 기본 요구사항은 충족되어야 함",
    "Package S/W 등 기술적 제약이 있는 경우 N/A 처리"
]

# 엄격한 전문 감사를 위한 핵심 고려사항
SPECIAL_CONSIDERATIONS = {
    "STRICT_APPROACH": "핵심 통제 요구사항이 충족되지 않으면 Ineffective",
    "PACKAGE_SW": "상용소프트웨어 사용시에만 해당 통제를 N/A로 처리",
    "AUDIT_TRAIL": "감사증적이 없으면 통제 검증이 불가능하므로 Ineffective",
    "CLOUD_SERVICE": "클라우드 서비스 이용시에도 기본적인 통제는 필요",
    "DOCUMENTATION": "절차 문서화는 통제의 일관성과 연속성 확보를 위해 필수",
    "SEGREGATION": "직무분리 원칙을 위반하면 통제 효과성이 현저히 저하"
}

CONTROL_SPECIFIC_CRITERIA = {
    'APD01': [
        "사용자 권한 부여 이력이 시스템에 자동으로 기록되는지 확인",
        "권한 요청 시 적절한 승인권자(부서장 등)의 사전 승인을 받는지 확인",
        "권한 부여 절차가 문서화되어 있고 준수되고 있는지 확인",
        "임시 권한의 경우 만료일 설정 및 자동 회수 여부 확인"
    ],
    'APD02': [
        "부서이동 시 기존 권한의 자동 또는 수동 회수 절차가 있는지 확인",
        "부서이동자가 직접 권한 회수를 요청하는 경우는 통제로 인정하지 않음",
        "인사시스템과 연계하여 자동 권한 회수가 되는지 확인",
        "권한 회수까지의 기간이 합리적인지 확인 (통상 1주일 이내)"
    ],
    'APD03': [
        "퇴사자 발생 시 즉시 접근 권한을 차단하는 절차가 있는지 확인",
        "퇴사일 당일 또는 익일까지 권한 회수가 완료되는지 확인",
        "인사팀과 IT팀 간의 퇴사자 정보 전달 체계가 있는지 확인",
        "퇴사자 계정의 완전 삭제 또는 비활성화 절차가 있는지 확인"
    ],
    'APD04': [
        "Application 관리자(Superuser) 권한 보유 인원이 명확히 식별되는지 확인",
        "관리자 권한 보유자의 소속, 직급, 담당 업무가 구체적으로 기술되어 있는지 확인",
        "관리자 권한 보유자가 업무상 필요한 적정 인원인지 판단",
        "관리자 권한의 정기적 검토 및 재승인 절차가 있는지 확인",
        "권한 보유자 수의 적정성은 회사 규모를 고려하여 판단"
    ],
    'APD05': [
        "사용자 권한의 적절성을 정기적으로 검토하는 절차가 있는지 확인",
        "전체 사용자 권한을 대상으로 검토하는지 확인 (일부만 검토 시 합리적 이유 필요)",
        "권한 검토 결과 발견된 이슈에 대한 조치 절차가 있는지 확인",
        "권한 검토 결과가 문서화되고 적절한 승인을 받는지 확인",
        "검토 주기의 적정성보다는 정기적 수행 여부에 중점",
        "권한 검토 시 직무분리 원칙 준수 여부도 확인"
    ],
    'APD06': [
        "Application 패스워드 최소 길이가 8자 이상으로 설정되어 있는지 확인",
        "패스워드 복잡성 요구사항(영문, 숫자, 특수문자 조합)이 있는지 확인",
        "패스워드 변경 주기 정책이 있는지 확인 (90일 이내 권장)",
        "최소 요구사항을 일부 충족하지 않더라도 다른 보안 조치가 있으면 경감요소로 고려",
        "패스워드 재사용 방지 정책이 있는지 확인"
    ],
    'APD07': [
        "데이터 변경 이력이 시스템에 자동으로 기록되는지 확인 (누가, 언제, 무엇을 변경했는지)",
        "데이터 변경 요청 시 적절한 승인권자의 사전 승인을 받는지 확인",
        "회사에서 직접 데이터 변경을 하지 않는 경우 이력 기록 불필요",
        "응급 상황 시 데이터 변경에 대한 사후 승인 절차가 있는지 확인",
        "데이터 변경 사유 및 영향범위가 기록되는지 확인"
    ],
    'APD08': [
        "데이터 변경 권한 보유 인원이 최소한으로 제한되어 있는지 확인",
        "데이터 변경 권한 보유자의 소속, 직급, 담당 업무가 명확히 기술되어 있는지 확인",
        "권한 보유자가 업무상 필요한 적정 인원인지 판단 (회사 규모 고려)",
        "데이터 변경 권한의 정기적 검토 절차가 있는지 확인",
        "일반 사용자와 데이터 변경 권한자의 명확한 분리가 되어 있는지 확인"
    ],
    'APD09': [
        "DB 접근권한 부여 이력이 시스템에 기록되는지 확인",
        "DB 접근 필요시 승인권자의 승인 여부"
    ],
    'APD10': [
        "DB 관리자 권한 보유 인원이 명확히 식별되는지 확인",
        "DB 관리자 권한 보유자의 부서, 직급, 직무가 구체적으로 기술되어 있는지 확인",
        "DB 관리자가 적정한 인원인지 판단",
        "권한 보유자가 몇 명인지는 판단하지 않음"

    ],
    'APD11': [
        "DB 패스워드 최소 길이가 8자 이상인지 확인",
        "DB 패스워드 복잡성(영문/숫자/특수문자) 요구사항이 있는지 확인"
    ],
    'APD12': [
        "OS 접근권한 부여 이력이 시스템에 기록되는지 확인",
        "OS 접근 필요시 승인권자의 승인 여부"
    ],
    'APD13': [
        "OS 관리자 권한 보유 인원이 명확히 식별되는지 확인",
        "OS 관리자 권한 보유자의 부서, 직급, 직무가 구체적으로 기술되어 있는지 확인",
        "OS 관리자가 적정한 인원인지 판단",
        "권한 보유자가 몇 명인지는 판단하지 않음"
    ],
    'APD14': [
        "OS 패스워드 최소 길이가 8자 이상인지 확인",
        "OS 패스워드 복잡성(영문/숫자/특수문자) 요구사항이 있는지 확인"
    ],
    'PC01': [
        "프로그램 변경 이력이 시스템에 자동으로 기록되는지 확인 (변경일시, 변경자, 변경내용)",
        "프로그램 변경 요청 시 적절한 승인권자의 사전 승인을 받는지 확인",
        "변경 요청서에 변경 사유, 영향범위, 테스트 계획이 포함되어 있는지 확인",
        "Package S/W 사용 시 본 통제는 적용되지 않음 (N/A 처리)",
        "형상관리 도구나 배포 도구를 통한 이력 관리도 인정"
    ],
    'PC02': [
        "프로그램 변경 후 사용자 테스트(UAT) 수행 절차가 있는지 확인",
        "사용자 테스트는 변경을 요청한 업무 담당자가 수행하는 것이 바람직",
        "테스트 결과가 문서화되고 승인되는 절차가 있는지 확인",
        "Package S/W 사용 시 본 통제는 적용되지 않음 (N/A 처리)",
        "테스트 실패 시 운영 반영을 중단하는 절차가 있는지 확인"
    ],
    'PC03': [
        "프로그램 변경 완료 후 운영 이관(배포) 전 최종 승인 절차가 있는지 확인",
        "이관 승인권자가 변경 요청 승인권자와 동일해도 무방",
        "Package S/W 사용 시 본 통제는 적용되지 않음 (N/A 처리)",
        "응급 변경 시에도 사후 승인 절차가 있는지 확인"
    ],
    'PC04': [
        "운영 서버 이관(배포) 권한 보유 인원이 명확히 제한되어 있는지 확인",
        "이관 권한 보유자의 소속, 직급, 담당 업무가 구체적으로 기술되어 있는지 확인",
        "이관 권한 보유자가 업무상 필요한 최소 인원인지 판단 (회사 규모 고려)",
        "Package S/W 사용 시 본 통제는 적용되지 않음 (N/A 처리)",
        "개발자와 이관 담당자의 분리가 되어 있는지 확인 (소규모는 예외)"
    ],
    'PC05': [
        "운영환경과 개발/테스트 환경이 물리적 또는 논리적으로 분리되어 있는지 확인",
        "개발 환경에서 운영 데이터에 직접 접근할 수 없도록 차단되어 있는지 확인",
        "localhost나 127.0.0.1을 개발서버로 사용하는 것도 분리로 인정",
        "Package S/W 사용 시에도 개발/운영 환경 분리는 적용 가능",
        "클라우드 환경의 경우 논리적 분리(VPC, 계정 분리 등)도 인정"
    ],
    'CO01': [
        "배치 스케줄 등록/변경 이력이 시스템에 기록되는지 확인",
        "배치 스케줄 등록/변경시 승인권자의 승인 여부"
    ],
    'CO02': [
        "배치 스케줄 등록/변경 권한 보유 인원이 명확히 식별되는지 확인",
        "배치 스케줄 등록 권한 보유자의 부서, 직급, 직무가 구체적으로 기술되어 있는지 확인",
        "배치 스케줄 등록 권한 보유자가 적정한 인원인지 판단",
        "권한 보유자가 몇 명인지는 판단하지 않음"
    ],
    'CO03': [
        "배치 실행 결과 모니터링 절차가 있는지 확인",
        "모니터링 결과 문서화 및 보관 절차가 있는지 확인"
    ],
    'CO04': [
        "장애 발생 시 대응 절차가 명확하게 정의되어 있는지 확인",
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
    # 조건부 질문 생략 로직 적용
    if not answers or len(answers) < 8:
        return False  # 답변이 부족하면 기본값 반환
    
    # 조건부 N/A 처리
    if control.startswith('PC') and answers[31] == 'N':
        return False  # 31번 답변이 N이면 프로그램 변경 관련 통제는 N/A
    
    if control in ['APD09', 'APD10', 'APD11'] and answers[17] == 'N':
        return False  # 17번 답변이 N이면 DB 관련 통제는 N/A
    
    if control in ['APD12', 'APD13', 'APD14'] and answers[24] == 'N':
        return False  # 24번 답변이 N이면 OS 관련 통제는 N/A
    
    if control in ['CO01', 'CO02', 'CO03'] and answers[38] == 'N':
        return False  # 38번 답변이 N이면 배치 스케줄 관련 통제(CO01-03)는 N/A
    
    # 7번 답변이 N이면 8~9번 질문 관련 통제는 N/A
    if control in ['APD07', 'APD08'] and answers[7] == 'N':
        return False  # 7번 답변이 N이면 DB 접근 관련 통제는 N/A
    
    conditions = {
        'APD01': len(answers) > 14 and (answers[12] == 'N' or answers[14] == 'N'),
        'APD02': len(answers) > 15 and answers[15] == 'N',
        'APD03': len(answers) > 16 and answers[16] == 'N',
        'APD04': len(answers) > 17 and answers[17] == 'N',
        'APD05': len(answers) > 18 and answers[18] == 'N',  # 사용자 권한 Monitoring
        'APD06': len(answers) > 20 and (answers[19] == 'N' or answers[20] == 'N'),
        'APD07': len(answers) > 22 and answers[17] == 'Y' and (answers[21] == 'N' or answers[22] == 'N'),  # DB 접근 가능할 때만 체크
        'APD08': len(answers) > 22 and answers[17] == 'Y' and answers[22] == 'N',  # DB 접근 가능할 때만 체크
        'APD09': len(answers) > 26 and answers[17] == 'Y' and (answers[25] == 'N' or answers[26] == 'N'),  # DB 접근 가능할 때만 체크
        'APD10': len(answers) > 28 and answers[17] == 'Y' and (answers[27] == 'N' or answers[28] == 'N'),  # DB 접근 가능할 때만 체크
        'APD12': len(answers) > 32 and (answers[31] == 'N' or answers[32] == 'N'),  # OS 접근권한 부여 이력 + 승인절차
        'APD13': len(answers) > 33 and answers[33] == 'N',  # OS 관리자 권한 제한
        'PC01': (len(answers) > 36 and answers[24] == 'Y') and (answers[35] == 'N' or answers[36] == 'N'),
        'PC02': (len(answers) > 37 and answers[24] == 'Y') and (answers[37] == 'N'),
        'PC03': (len(answers) > 38 and answers[24] == 'Y') and (answers[38] == 'N'),
        'PC05': len(answers) > 40 and answers[40] == 'N',
        'CO01': len(answers) > 42 and answers[38] == 'Y' and (answers[41] == 'N' or answers[42] == 'N'),  # 배치 스케줄이 있을 때만 체크
        'CO02': len(answers) > 43 and answers[38] == 'Y' and answers[43] == 'N',  # 배치 스케줄이 있을 때만 체크
        'CO03': len(answers) > 44 and answers[38] == 'Y' and answers[44] == 'N',  # 배치 스케줄이 있을 때만 체크
    }
    return conditions.get(control, False)

def ai_improve_interview_answer(question_text, answer_text):
    """
    AI를 사용하여 인터뷰 답변을 문법적으로 다듬고 일관성 있게 개선합니다.
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            # API 키가 있으면 AI로 개선
            client = OpenAI(api_key=api_key)
            prompt = AI_REFINEMENT_PROMPT.format(answer_text=answer_text)
            model_name = os.getenv('OPENAI_MODEL', AI_MODEL_CONFIG['model'])
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "한국어 문서 교정 전문가"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=AI_MODEL_CONFIG['max_tokens'],
                temperature=AI_MODEL_CONFIG['temperature']
            )
            
            result = response.choices[0].message.content.strip()
        else:
            # API 키가 없으면 원본 텍스트 사용
            result = answer_text
        
        # 불필요한 접두사 및 문구 제거
        for prefix in PREFIXES_TO_REMOVE:
            if result.startswith(prefix):
                result = result[len(prefix):].strip()
                break
        
        # 중간에 나타날 수 있는 불필요한 문구들 제거
        for phrase in UNWANTED_PHRASES:
            if phrase in result:
                # 해당 문구가 포함된 줄을 제거
                lines = result.split('\n')
                result = '\n'.join([line for line in lines if phrase not in line])
        
        # 텍스트 형식 개선 (설정에 따라 적용)
        import re
        
        # 마침표 뒤 엔터값 추가 (마침표+공백 패턴만)
        if AUTO_PARAGRAPH_BREAK['enable_sentence_break']:
            result = re.sub(r'[.] ', '.\n\n', result)
        
        # 추가 텍스트 처리 규칙 적용
        if TEXT_PROCESSING_RULES['remove_double_spaces']:
            # 이중 공백 제거 (줄바꿈은 제외)
            result = re.sub(r' {2,}', ' ', result)
        
        if TEXT_PROCESSING_RULES['unify_punctuation']:
            # 문장부호 통일
            result = result.replace('。', '.')
            result = result.replace('、', ',')
        
        if TEXT_PROCESSING_RULES['normalize_line_breaks']:
            # 줄바꿈 정규화 (3개 이상의 연속 줄바꿈을 2개로)
            result = re.sub(r'\n{3,}', '\n\n', result)
        
        return {
            'improved_answer': result or answer_text,
            'suggestions': ""
        }
        
    except Exception as e:
        print(f"답변 개선 중 오류 발생: {e}")
        return {
            'improved_answer': answer_text,
            'suggestions': ""
        }

def check_answer_consistency(answers, textarea_answers):
    """
    답변들 간의 일관성을 체크합니다.
    """
    consistency_issues = []
    
    # 시스템 관련 일관성 체크
    if len(answers) > 2:
        # 상용소프트웨어 사용 여부와 내부 수정 가능성 체크
        is_commercial = answers[2] == 'Y'  # 2번: 상용소프트웨어 여부
        can_modify = answers[31] == 'Y' if len(answers) > 31 else False  # 31번: 내부 수정 가능성
        
        if is_commercial and can_modify:
            consistency_issues.append("상용소프트웨어를 사용하면서 내부에서 주요 로직을 수정할 수 있다고 답변하셨습니다. 일반적으로 상용소프트웨어는 내부 수정이 제한적입니다.")
    
    # 클라우드 관련 일관성 체크
    if len(answers) > 7:
        uses_cloud = answers[7] == 'Y'  # 7번: 클라우드 사용 여부
        cloud_type = textarea_answers[8] if len(textarea_answers) > 8 else ""  # 8번: 클라우드 종류
        
        if uses_cloud and not cloud_type.strip():
            consistency_issues.append("클라우드 서비스를 사용한다고 답변하셨지만 클라우드 종류가 입력되지 않았습니다.")
    
    # 권한 관리 일관성 체크
    if len(answers) > 11:
        has_auth_history = answers[11] == 'Y'  # 11번: 사용자 권한부여 이력 기록 여부
        has_revoke_history = answers[12] == 'Y' if len(answers) > 12 else False  # 12번: 권한회수 이력 기록 여부
        
        if has_auth_history and not has_revoke_history:
            consistency_issues.append("권한 부여 이력은 기록되지만 권한 회수 이력은 기록되지 않는다고 답변하셨습니다. 권한 관리의 완전성을 위해 두 이력 모두 기록되는 것이 바람직합니다.")
    
    # 데이터베이스 관련 일관성 체크
    if len(answers) > 24:
        has_data_change_history = answers[19] == 'Y' if len(answers) > 19 else False  # 19번: 데이터 변경 이력
        has_db_auth_history = answers[25] == 'Y'  # 25번: DB 접근권한 부여 이력
        
        if has_db_auth_history and not has_data_change_history:
            consistency_issues.append("DB 접근권한 이력은 기록되지만 데이터 변경 이력은 기록되지 않는다고 답변하셨습니다. 보안 관점에서 데이터 변경 이력도 기록되어야 합니다.")
    
    return consistency_issues

def ai_improve_answer_consistency(answers, textarea_answers):
    """
    AI를 사용하여 답변들의 일관성을 체크하고 개선 제안을 제공합니다.
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                'consistency_check': "OpenAI API 키가 설정되지 않았습니다.",
                'suggestions': []
            }
        
        client = OpenAI(api_key=api_key)
        
        # 조건부 질문 필터링 적용
        filtered_questions = get_conditional_questions(answers)
        
        # 중요한 답변들만 선별하여 컨텍스트 구성
        key_answers = []
        for question in filtered_questions:
            question_index = question['index']
            if question_index < len(answers) and answers[question_index]:
                answer_text = answers[question_index]
                if question_index < len(textarea_answers) and textarea_answers[question_index]:
                    answer_text += f" ({textarea_answers[question_index]})"
                key_answers.append(f"Q{question_index+1}: {question['text']} -> A: {answer_text}")
        
        context = "\n".join(key_answers[:20])  # 처음 20개 질문만 사용
        
        prompt = f"""다음은 ITGC 인터뷰의 질문과 답변들입니다. 답변들 간의 논리적 일관성을 검토하고 개선 제안을 해주세요.

{context}

검토 기준:
1. 시스템 아키텍처 관련 답변들의 일관성
2. 보안 정책 및 권한 관리의 일관성
3. 프로세스 및 절차의 일관성
4. 기술적 구성요소들 간의 호환성

응답 형식:
일관성 검토: [전체적인 일관성 평가]
개선 제안: [구체적인 개선 사항들을 번호로 나열]"""

        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "ITGC 전문가. 답변의 논리적 일관성을 검토하고 개선 제안을 제공합니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        
        # 기본 일관성 체크도 추가
        basic_issues = check_answer_consistency(answers, textarea_answers)
        
        return {
            'ai_consistency_check': result,
            'basic_consistency_issues': basic_issues
        }
        
    except Exception as e:
        print(f"일관성 체크 중 오류 발생: {e}")
        basic_issues = check_answer_consistency(answers, textarea_answers)
        return {
            'ai_consistency_check': f"AI 일관성 체크 중 오류가 발생했습니다: {str(e)}",
            'basic_consistency_issues': basic_issues
        }

def get_ai_review(content, control_number=None, answers=None):
    """
    AI를 사용하여 ITGC 내용을 검토하고 개선 제안을 반환합니다.
    Summary 시트의 C열(검토결과), D열(결론), E열(개선필요사항)에 맞는 구조화된 결과를 반환합니다.
    answers: 인터뷰 답변 리스트 (Package S/W 상황 판단용)
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                'review_result': "OpenAI API 키가 설정되지 않았습니다.",
                'conclusion': "검토 불가",
                'improvements': "OPENAI_API_KEY 환경변수를 설정해주세요."
            }
        
        client = OpenAI(api_key=api_key)
        
        # 통제별 특정 기준만 가져오기 (토큰 절약)
        specific_criteria = CONTROL_SPECIFIC_CRITERIA.get(control_number, [])
        
        # 특별 상황 확인 및 컨텍스트 생성
        special_context = ""
        if answers and len(answers) > 3:
            is_package_sw = answers[2] == 'Y'  # 질문2: 상용소프트웨어 사용
            cannot_modify = answers[31] == 'N'  # 질문31: 내부 수정 불가
            
            if is_package_sw and cannot_modify:
                if control_number and control_number.startswith('PC'):
                    special_context = "\n중요: 이 시스템은 Package S/W이며 회사내에서 수정이 불가능합니다. 프로그램 변경(PC) 통제는 적용되지 않으므로(N/A) 미비점이 아닙니다."
        
        # 배치 스케줄 상황 확인
        if answers and len(answers) > 6:
            has_batch_schedule = answers[38] == 'Y'  # 질문38: 배치 스케줄 유무
            
            if not has_batch_schedule:
                if control_number and control_number in ['CO01', 'CO02', 'CO03']:
                    special_context += "\n중요: 현재 실행중인 배치 스케줄이 없습니다. 배치 관련 통제(CO01-CO03)는 적용되지 않으므로(N/A) 미비점이 아닙니다."
        
        # 공통 감사기준 포함
        common_criteria_text = "공통기준: " + " | ".join(COMMON_AUDIT_CRITERIA)
        
        # 통제별 특정 기준 텍스트 생성
        if specific_criteria:
            specific_criteria_text = f"특정기준: " + " | ".join(specific_criteria[:3])  # 토큰 절약을 위해 최대 3개만
        else:
            specific_criteria_text = "특정기준: 표준 ITGC 검토 기준 적용"

        prompt = f"""ITGC {control_number} 검토:
{content}

{common_criteria_text}
{specific_criteria_text}{special_context}

**검토 기준: 전문적이고 균형잡힌 감사 접근**
- 실제 사용자가 작성한 답변 내용을 기반으로 평가 (시스템 자동 생성 문구는 제외)
- 통제의 설계와 운영 상태를 실질적으로 분석
- 이력 기록 여부, 승인 절차 존재 여부, 권한 관리 적절성 등을 종합적으로 판단
- 소규모 조직의 현실적 제약을 고려하되 핵심 통제 요구사항은 충족되어야 함
- 명확한 통제 미비점이 확인되는 경우에만 Ineffective 판정
- 적절한 통제가 운영되고 있다면 Effective 판정

응답형식 (정확히 이 형식으로만 답변):
검토결과: [전문적 감사 관점에서 엄격하게 분석]
결론: Effective (또는 결론: Ineffective - 반드시 이 두 단어 중 하나만 단독으로 사용)
개선필요사항: [Ineffective시 구체적이고 실행가능한 개선방안 제시, Effective시 빈칸]

중요: 
1. 결론 부분에는 반드시 'Effective' 또는 'Ineffective' 단어만 사용할 것
2. 시스템이 자동으로 생성한 문구는 평가에서 제외하고, 실제 사용자 답변 내용만 분석할 것
3. 예시: "ITSM을 통해 요청서 작성 후 팀장 승인을 받아 권한 부여" → 사용자가 직접 작성한 절차 설명이므로 평가 대상
"""

        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # 기본값으로 gpt-4o-mini 사용

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "전문적이고 균형잡힌 ITGC 감사 전문가. 명백한 미비점은 정확히 식별하되, 적절히 운영되는 통제는 Effective로 인정하는 합리적 판단을 수행."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3  # 균형잡힌 전문 판정을 위한 설정 (0=경직, 1=유연)
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
    
    # C12: AI로 다듬어진 내용 또는 원본 내용
    if 'C2' in text_data:
        ws['C12'] = text_data['C2']  # AI로 다듬어진 내용
        # 행 높이 조정 (AI 다듬어진 내용 기준)
        value = str(text_data['C2'])
        num_lines = value.count('\n') + 1
        approx_lines = num_lines + (len(value) // 50)
        ws.row_dimensions[12].height = 15 * approx_lines
        
    # C2가 없는 경우 (AI 비활성화 상태)
    elif 'B2' in text_data:
        ws['C12'] = text_data['B2']
        # 행 높이 조정
        value = str(text_data['B2'])
        num_lines = value.count('\n') + 1
        approx_lines = num_lines + (len(value) // 50)
        ws.row_dimensions[12].height = 15 * approx_lines
        
    # B3: 시스템명, B5: user_email
    if len(answers) > 1 and answers[1]:
        system_name = answers[1]  # 1번: 시스템 이름
        ws['B3'] = system_name
    
    if len(answers) > 0 and answers[0]:
        user_email = answers[0]  # 0번: 이메일 주소
        ws['B5'] = user_email

# 텍스트 길이 체크 (토큰 사용량 최적화)
def should_apply_ai_refinement(text):
    """AI 다듬기를 적용할지 결정 (설정 기반)"""
    text_len = len(text)
    return TEXT_LENGTH_LIMITS['min_length'] <= text_len <= TEXT_LENGTH_LIMITS['max_length']

# 공통 템플릿 처리 함수
def build_control_text(control_config, answers, textarea_answers):
    """ITGC 통제 텍스트를 공통 로직으로 생성"""
    control_type = control_config.get('type', 'history_procedure')
    
    if control_type == 'complex_db':
        # APD09 방식 (DB 복합)
        db_info = f"DB 종류와 버전: {answers[control_config['db_type_idx']]}"
        db_tool = f"DB 접근제어 Tool 사용 여부: {'사용' if answers[control_config['db_tool_idx']] == 'Y' else '미사용'}"
        
        history_status = (control_config['history_yes'] if answers[control_config['history_idx']] == 'Y' 
                         else control_config['history_no'])
        
        if answers[control_config['procedure_idx']] == 'Y':
            textarea_content = textarea_answers[control_config['textarea_idx']] if textarea_answers[control_config['textarea_idx']] else control_config['default_msg']
            procedure_text = f"{control_config['procedure_prefix']}\n\n{textarea_content}"
        else:
            procedure_text = control_config['procedure_no']
            
        return f"{db_info}\n\n{db_tool}\n\nDB 접근권한 부여 이력이 시스템에 {history_status}\n\n{procedure_text}"
    
    elif control_type == 'complex_os':
        # APD12 방식 (OS 복합)
        os_info = f"OS 종류와 버전: {answers[control_config['os_type_idx']]}"
        os_tool = f"OS 접근제어 Tool 사용 여부: {'사용' if answers[control_config['os_tool_idx']] == 'Y' else '미사용'}"
        
        history_status = (control_config['history_yes'] if answers[control_config['history_idx']] == 'Y' 
                         else control_config['history_no'])
        
        if answers[control_config['procedure_idx']] == 'Y':
            textarea_content = textarea_answers[control_config['textarea_idx']] if textarea_answers[control_config['textarea_idx']] else control_config['default_msg']
            procedure_text = f"{control_config['procedure_prefix']}\n\n{textarea_content}"
        else:
            procedure_text = control_config['procedure_no']
            
        return f"{os_info}\n\n{os_tool}\n\nOS 접근권한 부여 이력이 시스템에 {history_status}\n\n{procedure_text}"
    
    elif control_type == 'history_procedure' or 'history_idx' in control_config:
        # 기존 APD01, APD02 방식 (이력 + 절차)
        history_status = (control_config['history_yes'] if answers[control_config['history_idx']] == 'Y' 
                         else control_config['history_no'])
        
        if 'procedure_idx' in control_config:
            if answers[control_config['procedure_idx']] == 'Y':
                textarea_content = textarea_answers[control_config['textarea_idx']] if textarea_answers[control_config['textarea_idx']] else control_config['default_msg']
                procedure_text = f"{control_config['procedure_prefix']}\n\n{textarea_content}"
            else:
                procedure_text = control_config['procedure_no']
        else:
            procedure_text = ""
            
        return control_config['template'].format(
            history_status=history_status,
            procedure_text=procedure_text
        )
    
    elif control_type == 'simple_procedure':
        # APD03 방식 (단순 절차)
        if answers[control_config['procedure_idx']] == 'Y':
            textarea_content = textarea_answers[control_config['textarea_idx']] if textarea_answers[control_config['textarea_idx']] else control_config['default_msg']
            return f"{control_config['procedure_prefix']}\n\n{textarea_content}"
        else:
            return control_config['procedure_no']
    
    elif control_type == 'simple_list':
        # APD04, APD06 방식 (단순 리스트)
        content = answers[control_config['answer_idx']] if answers[control_config['answer_idx']] else control_config['default_msg']
        return control_config['template'].format(content=content)
    
    elif control_type == 'simple_status':
        # APD05, PC05 방식 (단순 상태)
        status = (control_config['status_yes'] if answers[control_config['answer_idx']] == 'Y' 
                 else control_config['status_no'])
        return control_config['template'].format(status=status)
    
    
    return control_config.get('default_msg', '상세 기술이 제공되지 않았습니다.')

def get_text_itgc(answers, control_number, textarea_answers=None, enable_ai_review=False):
    result = {}
    if textarea_answers is None:
        textarea_answers = [''] * len(answers)

    # 조건부 질문 생략 로직 적용
    if answers and len(answers) >= 8:
        # 조건부 N/A 처리
        # 31번 질문: "주요 로직을 회사내부에서 수정하여 사용할 수 있습니까?"
        if control_number.startswith('PC') and answers[31] == 'N':
            result['A1'] = control_number
            result['B1'] = ITGC_CONTROLS.get(control_number, {}).get('title', control_number)
            result['B2'] = f"이 시스템은 상용소프트웨어이며 회사내에서 수정이 불가능합니다. {control_number} 통제는 적용되지 않으므로(N/A) 미비점이 아닙니다."
            result['C2'] = result['B2']
            return result
        
        # 17번 질문: "회사에서 DB에 접속하여 필요한 작업을 수행하는 것이 가능하십니까?"
        if control_number in ['APD09', 'APD10', 'APD11'] and answers[17] == 'N':
            result['A1'] = control_number
            result['B1'] = ITGC_CONTROLS.get(control_number, {}).get('title', control_number)
            result['B2'] = f"회사에서 DB에 접속하여 필요한 작업을 수행할 수 없습니다. {control_number} 통제는 적용되지 않으므로(N/A) 미비점이 아닙니다."
            result['C2'] = result['B2']
            return result
        
        # 24번 질문: "회사에서 OS서버에 접속하여 필요한 작업을 수행하는 것이 가능하십니까?"
        if control_number in ['APD12', 'APD13', 'APD14'] and answers[24] == 'N':
            result['A1'] = control_number
            result['B1'] = ITGC_CONTROLS.get(control_number, {}).get('title', control_number)
            result['B2'] = f"회사에서 OS서버에 접속하여 필요한 작업을 수행할 수 없습니다. {control_number} 통제는 적용되지 않으므로(N/A) 미비점이 아닙니다."
            result['C2'] = result['B2']
            return result
        
        if control_number in ['CO01', 'CO02', 'CO03'] and answers[38] == 'N':
            result['A1'] = control_number
            result['B1'] = ITGC_CONTROLS.get(control_number, {}).get('title', control_number)
            result['B2'] = f"현재 실행중인 배치 스케줄이 없습니다. {control_number} 통제는 적용되지 않으므로(N/A) 미비점이 아닙니다."
            result['C2'] = result['B2']
            return result
        
        if control_number in ['APD07', 'APD08'] and answers[7] == 'N':
            result['A1'] = control_number
            result['B1'] = ITGC_CONTROLS.get(control_number, {}).get('title', control_number)
            result['B2'] = f"회사에서 DB에 접속하여 필요한 작업을 수행할 수 없습니다. {control_number} 통제는 적용되지 않으므로(N/A) 미비점이 아닙니다."
            result['C2'] = result['B2']
            return result

    # 공통 로직으로 처리
    result['A1'] = control_number
    
    if control_number in ITGC_CONTROLS:
        config = ITGC_CONTROLS[control_number]
        result['B1'] = config['title']
        result['B2'] = build_control_text(config, answers, textarea_answers)

    # APD03-CO06은 이제 모두 ITGC_CONTROLS에서 처리됨
    
    else:
        # 알 수 없는 통제 번호 처리
        result['A1'] = f"Unknown control number: {control_number}"
        result['B1'] = ""
        result['B2'] = "알 수 없는 통제 번호입니다."

    # AI 기능 적용 (토큰 사용량 최적화)
    if enable_ai_review and 'B2' in result and result['B2']:
        # 텍스트 길이 체크로 불필요한 API 호출 방지
        if should_apply_ai_refinement(result['B2']):
            print(f"🤖 AI 다듬기 시작: {control_number}")
            
            improved_text = ai_improve_interview_answer("", result['B2'])  # 질문 텍스트 제거로 토큰 절약
            if improved_text and improved_text.get('improved_answer'):
                result['C2'] = improved_text['improved_answer']
                print(f"📝 AI 다듬기 완료: {control_number}")
            else:
                result['C2'] = result['B2']
            
            # AI 검토 수행
            print(f"🔍 AI 검토 시작: {control_number}")
            ai_review = get_ai_review(result['C2'], control_number, answers)
            result['AI_Review'] = ai_review
            result['AI_Summary'] = ai_review
            print(f"✅ AI 검토 완료: {control_number}")
        else:
            print(f"⏭️ AI 다듬기 건너뜀 (길이): {control_number}")
            result['C2'] = result['B2']
    else:
        result['C2'] = result['B2']

    return result

# link2_prev의 핵심 로직만 분리 (세션 객체는 snowball.py에서 전달)
def link2_prev_logic(session):
    question_index = session.get('question_index', 0)
    print(f"[PREV DEBUG] 현재 question_index: {question_index}")
    
    if question_index > 0:
        # 조건부 질문 생략 로직 (역방향)
        if question_index == 24:  # 24번 질문에서 이전으로 갈 때 (OS서버 접속)
            # 17번 답변 확인 (DB 접속 가능 여부)
            answer_17 = session.get('answer', [])[17] if len(session.get('answer', [])) > 17 else ''
            print(f"[PREV DEBUG] 24번에서 이전, 17번 답변: {answer_17}")
            if answer_17 == 'N':
                # 17번 답변이 'N'이면 17번으로 이동 (18~23번 스킵)
                session['question_index'] = 17
                print(f"[PREV DEBUG] 17번으로 이동 (18~23번 스킵)")
            else:
                # 아니면 23번으로 이동
                session['question_index'] = 23
                print(f"[PREV DEBUG] 23번으로 이동")
        elif question_index == 31: # 31번 질문에서 이전으로 갈 때 (프로그램 수정 가능 여부)
            # 24번 답변 확인 (OS서버 접속 가능 여부)
            answer_24 = session.get('answer', [])[24] if len(session.get('answer', [])) > 24 else ''
            print(f"[PREV DEBUG] 31번에서 이전, 24번 답변: {answer_24}")
            if answer_24 == 'N':
                # 24번 답변이 'N'이면 24번으로 이동 (25~30번 스킵)
                session['question_index'] = 24
                print(f"[PREV DEBUG] 24번으로 이동 (25~30번 스킵)")
            else:
                # 아니면 30번으로 이동
                session['question_index'] = 30
                print(f"[PREV DEBUG] 30번으로 이동")
        elif question_index == 38:  # 38번 질문에서 이전으로 갈 때 (배치 스케줄 유무)
            # 31번 답변 확인 (프로그램 수정 가능 여부)
            answer_31 = session.get('answer', [])[31] if len(session.get('answer', [])) > 31 else ''
            print(f"[PREV DEBUG] 38번에서 이전, 31번 답변: {answer_31}")
            if answer_31 == 'N':
                # 31번 답변이 'N'이면 31번으로 이동 (32~37번 스킵)
                session['question_index'] = 31
                print(f"[PREV DEBUG] 31번으로 이동 (32~37번 스킵)")
            else:
                # 아니면 37번으로 이동
                session['question_index'] = 37
                print(f"[PREV DEBUG] 37번으로 이동")
        elif question_index == 6:  # 6번 질문에서 이전으로 갈 때 (사용자 권한부여 이력)
            # 3번 답변 확인 (Cloud 서비스 사용 여부)
            answer_3 = session.get('answer', [])[3] if len(session.get('answer', [])) > 3 else ''
            print(f"[PREV DEBUG] 6번에서 이전, 3번 답변: {answer_3}")
            if answer_3 == 'N':
                # Cloud 서비스를 사용하지 않으면 3번으로 이동 (4~5번 스킵)
                session['question_index'] = 3
                print(f"[PREV DEBUG] 3번으로 이동 (4~5번 스킵)")
            else:
                # Cloud 서비스를 사용하면 5번으로 이동
                session['question_index'] = 5
                print(f"[PREV DEBUG] 5번으로 이동")
        elif question_index in [4, 5]:  # 4~5번 질문에서 이전으로 갈 때 (Cloud 관련)
            # 모두 3번으로 이동 (Cloud 서비스 사용 여부)
            session['question_index'] = 3
            print(f"[PREV DEBUG] {question_index}번에서 3번으로 이동")
        elif question_index in [18, 19, 20, 21, 22, 23]:  # 18~23번 질문에서 이전으로 갈 때 (DB 관련)
            # 모두 17번으로 이동 (DB 접속 가능 여부)
            session['question_index'] = 17
            print(f"[PREV DEBUG] {question_index}번에서 17번으로 이동")
        elif question_index in [25, 26, 27, 28, 29, 30]:  # 25~30번 질문에서 이전으로 갈 때 (OS 관련)
            # 모두 24번으로 이동 (OS서버 접속 가능 여부)
            session['question_index'] = 24
            print(f"[PREV DEBUG] {question_index}번에서 24번으로 이동")
        elif question_index in [32, 33, 34, 35, 36, 37]:  # 32~37번 질문에서 이전으로 갈 때 (PC 관련)
            # 모두 31번으로 이동 (프로그램 수정 가능 여부)
            session['question_index'] = 31
            print(f"[PREV DEBUG] {question_index}번에서 31번으로 이동")
        elif question_index in [39, 40, 41, 42, 43]:  # 39~43번 질문에서 이전으로 갈 때 (배치 관련)
            # 모두 38번으로 이동 (배치 스케줄 유무)
            session['question_index'] = 38
            print(f"[PREV DEBUG] {question_index}번에서 38번으로 이동")
        elif question_index in [44, 45, 46]:  # 44~46번 질문에서 이전으로 갈 때 (CO04~06)
            # 38번 배치 스케줄 답변 확인
            answer_38 = session.get('answer', [])[38] if len(session.get('answer', [])) > 38 else ''
            print(f"[PREV DEBUG] {question_index}번에서 이전, 38번 답변: {answer_38}")
            if answer_38 == 'N':
                # 배치 스케줄이 없으면 38번으로 이동 (39~43번 스킵)
                session['question_index'] = 38
                print(f"[PREV DEBUG] 38번으로 이동 (39~43번 스킵)")
            else:
                # 배치 스케줄이 있으면 이전 질문으로 이동
                if question_index == 44:
                    session['question_index'] = 43
                    print(f"[PREV DEBUG] 43번으로 이동")
                else:
                    session['question_index'] = question_index - 1
                    print(f"[PREV DEBUG] {question_index - 1}번으로 이동")
        else:
            session['question_index'] = question_index - 1
            print(f"[PREV DEBUG] 일반 이전: {question_index} -> {question_index - 1}")
    
    print(f"[PREV DEBUG] 최종 question_index: {session['question_index']}")
    return session

def export_interview_excel_and_send(answers, textarea_answers, get_text_itgc, fill_sheet, is_ineffective, send_gmail_with_attachment, enable_ai_review=False, progress_callback=None):
    """
    인터뷰 답변을 받아 엑셀 파일을 생성하고 메일로 전송합니다.
    진행률 처리 개선 및 서버 환경 호환성 강화
    answers: list (사용자 답변)
    textarea_answers: list (텍스트에어리어 답변)
    get_text_itgc: 텍스트 생성 함수
    fill_sheet: 시트 채우기 함수
    is_ineffective: 비효과적 통제 체크 함수
    send_gmail_with_attachment: 메일 전송 함수
    progress_callback: 진행률 업데이트 콜백 함수
    """
    today = datetime.today().strftime('%Y%m%d')
    
    # 한글 파일명 처리 개선 - 유틸리티 함수 사용
    from korean_filename_utils import convert_korean_to_english_filename, generate_excel_filename
    
    if len(answers) > 1 and answers[1]:
        system_name = answers[1].strip()
        file_name = generate_excel_filename(system_name, "ITGC")
    else:
        file_name = f"ITGC_System_{today}.xlsx"

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
    
    total_controls = len(control_list)
    processed_controls = []
    failed_controls = []
    
    for idx, control in enumerate(control_list):
        # 진행률 계산 (20%에서 80% 사이에서 진행)
        progress_percent = 20 + int((idx / total_controls) * 60)
        
        if progress_callback:
            if enable_ai_review:
                progress_callback(progress_percent, f"AI가 {control} 통제를 검토하고 있습니다... ({idx+1}/{total_controls})")
            else:
                progress_callback(progress_percent, f"{control} 통제 문서를 생성하고 있습니다... ({idx+1}/{total_controls})")
        
        try:
            text_data = get_text_itgc(answers, control, textarea_answers, enable_ai_review)
            ws = wb[control]
            fill_sheet(ws, text_data, answers)
            processed_controls.append(control)
            print(f"✓ {control} 처리 완료")
        except Exception as e:
            failed_controls.append((control, str(e)))
            print(f"✗ {control} 처리 실패: {str(e)}")

        # AI 검토 결과가 있는 경우 Summary 시트용 데이터 수집
        if enable_ai_review and 'AI_Summary' in text_data and isinstance(text_data['AI_Summary'], dict):
            summary_ai_reviews[control] = text_data['AI_Summary']
            print(f"📊 {control} AI 검토 결과 Summary 수집 완료")
        elif enable_ai_review:
            print(f"⚠️ {control} AI_Summary 데이터 없음: keys={list(text_data.keys()) if hasattr(text_data, 'keys') else 'N/A'}")

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

    # 처리 결과 요약 출력
    print(f"\n📋 처리 완료: {len(processed_controls)}개 통제")
    print(f"❌ 처리 실패: {len(failed_controls)}개 통제")
    if failed_controls:
        for control, error in failed_controls:
            print(f"  - {control}: {error}")
    
    # 4. Summary 시트 처리
    print(f"\n📊 Summary 시트 데이터: {len(summary_ai_reviews)}개 통제")
    for control in summary_ai_reviews.keys():
        print(f"  - {control}")
    
    if enable_ai_review and summary_ai_reviews:
        # AI 검토가 활성화된 경우 Summary 시트 생성
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

            # 스킵된 통제 목록 가져오기
            skipped_controls = get_skipped_controls(answers)
            
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
                    
                    # 스킵된 통제인 경우 행을 회색으로 표시
                    if control in skipped_controls:
                        from openpyxl.styles import PatternFill
                        gray_fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
                        for col in ['A', 'B', 'C', 'D', 'E']:
                            summary_ws[f'{col}{row_index}'].fill = gray_fill
                        print(f"[SUMMARY] {control} 통제를 Summary 시트에서 회색으로 표시했습니다.")
                    
                    row_index += 1
        except Exception as e:
            print(f"Summary 시트 작성 중 오류 발생: {str(e)}")
            # Summary 시트 오류가 발생해도 전체 프로세스는 계속 진행
    else:
        # AI 검토가 비활성화된 경우 기존 Summary 시트 삭제
        if 'Summary' in wb.sheetnames:
            try:
                wb.remove(wb['Summary'])
                print("AI 검토 미사용으로 Summary 시트를 삭제했습니다.")
            except Exception as e:
                print(f"Summary 시트 삭제 중 오류 발생: {str(e)}")

    # 메모리 버퍼에 저장 (안전한 방식) - 한글 처리 개선
    excel_stream = BytesIO()
    excel_stream_copy = None
    try:
        # 엑셀 파일 저장 전 검증
        if not wb.worksheets:
            raise Exception("워크북에 시트가 없습니다.")
        
        # 한글 처리를 위한 엑셀 저장 옵션 설정
        from openpyxl.workbook.workbook import Workbook
        from openpyxl.writer.excel import ExcelWriter
        
        # 스킵된 통제의 시트 탭을 회색으로 설정
        set_sheet_tab_color_for_skipped_controls(wb, answers)
        
        # 엑셀 파일을 메모리에 저장 (한글 인코딩 처리)
        # MIME 타입을 명시적으로 설정하여 한글 처리 개선
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
        if progress_callback:
            progress_callback(85, "엑셀 파일을 메일로 전송하고 있습니다...")
            
        subject = '인터뷰 결과 파일'
        body = '인터뷰 내용에 따라 ITGC 설계평가 문서를 첨부합니다.'
        try:
            # 파일 스트림 검증
            if not excel_stream_copy:
                raise Exception("엑셀 파일 스트림이 생성되지 않았습니다.")
            
            # 파일 스트림 위치 확인 및 리셋
            excel_stream_copy.seek(0)
            
            if progress_callback:
                progress_callback(90, "메일 전송 중...")
            
            # 한글 파일명을 안전하게 처리하여 메일 첨부
            from korean_filename_utils import convert_korean_to_english_filename
            safe_file_name = convert_korean_to_english_filename(file_name.replace('.xlsx', '')) + '.xlsx'
            
            send_gmail_with_attachment(
                to=user_email,
                subject=subject,
                body=body,
                file_stream=excel_stream_copy,
                file_name=safe_file_name
            )
            
            if progress_callback:
                progress_callback(95, "메일 전송이 완료되었습니다!")
                
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

def test_conditional_questions():
    """
    조건부 질문 생략 로직을 테스트하는 함수
    """
    print("=== 조건부 질문 생략 로직 테스트 ===")
    
    # 테스트 케이스들
    test_cases = [
        {
            'name': '모든 질문 표시 (기본)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 47
        },
        {
            'name': '3번 답변이 N (프로그램 변경 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'N', 'Y', 'Y', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 41  # 34-39번 질문 6개 생략
        },
        {
            'name': '4번 답변이 N (DB 관련 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'N', 'Y', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 41  # 22-27번 질문 6개 생략
        },
        {
            'name': '5번 답변이 N (OS 관련 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'Y', 'N', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 41  # 28-33번 질문 6개 생략
        },
        {
            'name': '6번 답변이 N (배치 스케줄 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'Y', 'Y', 'N', 'Y'] + ['N'] * 40,
            'expected_count': 43  # 41-43번 질문 3개 생략
        },
        {
            'name': '7번 답변이 N (Cloud 관련 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'Y', 'Y', 'Y', 'N'] + ['N'] * 40,
            'expected_count': 45  # 8-9번 질문 2개 생략
        },
        {
            'name': '모든 조건부 질문 생략',
            'answers': ['test@example.com', 'Test System', 'Y', 'N', 'N', 'N', 'N', 'N'] + ['N'] * 40,
            'expected_count': 23  # 35-40, 23-28, 29-34, 41-43, 8-9번 질문들 생략
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        conditional_questions = get_conditional_questions(test_case['answers'])
        actual_count = len(conditional_questions)
        expected_count = test_case['expected_count']
        
        print(f"예상 질문 수: {expected_count}")
        print(f"실제 질문 수: {actual_count}")
        print(f"결과: {'✅ 통과' if actual_count == expected_count else '❌ 실패'}")
        
        # 생략된 질문들 확인
        all_indices = [q['index'] for q in s_questions]
        conditional_indices = [q['index'] for q in conditional_questions]
        skipped_indices = [idx for idx in all_indices if idx not in conditional_indices]
        
        if skipped_indices:
            print(f"생략된 질문 인덱스: {skipped_indices}")
    
    # 통제별 N/A 처리 테스트
    print(f"\n=== 통제별 N/A 처리 테스트 ===")
    
    # 3번 답변이 N인 경우 PC 통제들 테스트
    test_answers = ['test@example.com', 'Test System', 'Y', 'N', 'Y', 'Y', 'Y', 'Y'] + ['N'] * 40
    pc_controls = ['PC01', 'PC02', 'PC03', 'PC04', 'PC05']
    
    for control in pc_controls:
        result = get_text_itgc(test_answers, control)
        print(f"{control}: {result.get('B2', 'N/A')[:50]}...")
    
    # 4번 답변이 N인 경우 DB 관련 통제들 테스트
    test_answers = ['test@example.com', 'Test System', 'Y', 'Y', 'N', 'Y', 'Y', 'Y'] + ['N'] * 40
    db_controls = ['APD09', 'APD10', 'APD11']
    
    for control in db_controls:
        result = get_text_itgc(test_answers, control)
        print(f"{control}: {result.get('B2', 'N/A')[:50]}...")
    
    # 7번 답변이 N인 경우 Cloud 관련 통제들 테스트
    test_answers = ['test@example.com', 'Test System', 'Y', 'Y', 'Y', 'Y', 'Y', 'N'] + ['N'] * 40
    cloud_controls = ['APD07', 'APD08']  # Cloud 관련 통제들
    
    for control in cloud_controls:
        result = get_text_itgc(test_answers, control)
        print(f"{control}: {result.get('B2', 'N/A')[:50]}...")
    
    return True

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
    # 조건부 질문 생략 로직 테스트
    test_conditional_questions()
    
    # AI 검토 기능 테스트
    test_ai_review_feature()
    # 강제 수정1