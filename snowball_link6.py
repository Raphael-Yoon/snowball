from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import uuid

bp_link6 = Blueprint('link6', __name__)

# 미리 정의된 질문 목록
PREDEFINED_QUESTIONS = [
    "시스템 이름을 적어주세요.",
    "사용하고 있는 시스템은 상용소프트웨어입니까?",
    "기능을 회사내부에서 수정하여 사용할 수 있습니까?",
    "Cloud 서비스를 사용하고 있습니까?",
    "어떤 종류의 Cloud입니까?",
    "Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?",
    "OS 종류와 버전을 작성해 주세요.",
    "OS 접근제어 Tool 을 사용하고 있습니까?",
    "DB 종류와 버전을 작성해 주세요.",
    "DB 접근제어 Tool 을 사용하고 있습니까?",
    "별도의 Batch Schedule Tool 을 사용하고 있습니까?",
    "사용자 권한부여 이력이 시스템에 기록되고 있습니까?",
    "사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?",
    "권한이 부여되는 절차를 기술해 주세요.",
    "사용자 권한회수 이력이 시스템에 기록되고 있습니까?",
    "부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?",
    "부서이동 등 기존권한의 회수가 필요한 경우 수행되는 절차를 기술해 주세요.",
    "퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?",
    "퇴사자 발생시 접근권한을 차단하는(계정 삭제 등) 절차를 기술해 주세요.",
    "전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?",
    "패스워드 설정사항을 기술해 주세요(최소자리, 복잡성, 변경주기 등)"
]

# 질문 스킵 로직 매핑
QUESTION_SKIP_LOGIC = {
    1: {  # "상용소프트웨어입니까?"
        "skip_if": ["아니오", "N", "no", "아니다"],
        "skip_to": [2]  # "기능을 회사내부에서 수정하여 사용할 수 있습니까?" 스킵
    },
    3: {  # "Cloud 서비스를 사용하고 있습니까?"
        "skip_if": ["아니오", "N", "no", "아니다"],
        "skip_to": [4, 5]  # Cloud 관련 후속 질문들 스킵
    },
    12: {  # "사용자가 새로운 권한이 필요한 경우... 절차가 있습니까?"
        "skip_if": ["아니오", "N", "no", "아니다"],
        "skip_to": [13]  # "절차를 기술해 주세요" 스킵
    },
    15: {  # "기존권한의 회수가 필요한 경우... 절차가 있습니까?"
        "skip_if": ["아니오", "N", "no", "아니다"],
        "skip_to": [16]  # "절차를 기술해 주세요" 스킵
    },
    17: {  # "퇴사자 발생시... 절차가 있습니까?"
        "skip_if": ["아니오", "N", "no", "아니다"],
        "skip_to": [18]  # "절차를 기술해 주세요" 스킵
    }
}

# 세션별 데이터 저장
user_sessions = {}
conversation_histories = {}

def _get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def _get_next_question_index(current_index, user_answer, skipped_questions):
    """다음 질문 인덱스를 결정하는 함수 (스킵 로직 포함)"""
    # 현재 질문에 스킵 로직이 있는지 확인
    if current_index in QUESTION_SKIP_LOGIC:
        skip_config = QUESTION_SKIP_LOGIC[current_index]
        # 사용자 답변이 스킵 조건에 해당하는지 확인
        if any(skip_word.lower() in user_answer.lower() for skip_word in skip_config["skip_if"]):
            # 스킵할 질문들을 기록
            for skip_index in skip_config["skip_to"]:
                skipped_questions.add(skip_index)
    
    # 다음 질문 인덱스 찾기 (스킵된 질문들 제외)
    next_index = current_index + 1
    while next_index < len(PREDEFINED_QUESTIONS) and next_index in skipped_questions:
        next_index += 1
    
    return next_index


@bp_link6.route('/link6_start_interview', methods=['POST'])
def link6_start_interview():
    # 새 인터뷰 세션 시작
    session_id = str(uuid.uuid4())
    
    # 세션 데이터 초기화
    user_sessions[session_id] = {
        'current_question_index': 0,
        'user_answers': [],
        'completed': False,
        'skipped_questions': set(),  # 스킵된 질문 인덱스들
        'total_questions_to_answer': len(PREDEFINED_QUESTIONS)  # 동적으로 업데이트됨
    }
    conversation_histories[session_id] = []
    
    # 첫 번째 질문 반환
    first_question = PREDEFINED_QUESTIONS[0]
    
    return jsonify({
        'session_id': session_id,
        'question': first_question,
        'question_number': 1,
        'total_questions': len(PREDEFINED_QUESTIONS),
        'message': '인터뷰를 시작합니다!'
    })

@bp_link6.route('/link6_submit_answer', methods=['POST'])
def link6_submit_answer():
    data = request.get_json() or {}
    session_id = data.get('session_id', '')
    user_answer = data.get('answer', '').strip()
    
    if not session_id or session_id not in user_sessions:
        return jsonify({'error': '유효하지 않은 세션입니다.'}), 400
    
    if not user_answer:
        return jsonify({'error': '답변을 입력해주세요.'}), 400
    
    session_data = user_sessions[session_id]
    current_index = session_data['current_question_index']
    
    if current_index >= len(PREDEFINED_QUESTIONS):
        return jsonify({'error': '모든 질문이 완료되었습니다.'}), 400
    
    # 사용자 답변 저장
    current_question = PREDEFINED_QUESTIONS[current_index]
    session_data['user_answers'].append({
        'question': current_question,
        'answer': user_answer,
        'timestamp': str(uuid.uuid4())[:8]
    })
    
    # 대화 히스토리에 추가
    conversation_histories[session_id].extend([
        {"role": "assistant", "content": current_question},
        {"role": "user", "content": user_answer}
    ])
    
    # 다음 질문 인덱스 결정 (스킵 로직 적용)
    next_index = _get_next_question_index(
        current_index, 
        user_answer, 
        session_data['skipped_questions']
    )
    
    # 전체 질문 수 업데이트 (스킵된 질문 제외)
    session_data['total_questions_to_answer'] = len(PREDEFINED_QUESTIONS) - len(session_data['skipped_questions'])
    
    if next_index >= len(PREDEFINED_QUESTIONS):
        # 모든 질문 완료
        session_data['completed'] = True
        return jsonify({
            'completed': True,
            'message': '모든 질문에 답변해주셔서 감사합니다!',
            'total_answers': len(session_data['user_answers']),
            'skipped_questions': len(session_data['skipped_questions'])
        })
    
    # 다음 질문으로 이동
    session_data['current_question_index'] = next_index
    next_question = PREDEFINED_QUESTIONS[next_index]
    
    # 실제 답변한 질문 수 계산
    answered_questions = len(session_data['user_answers'])
    
    return jsonify({
        'question': next_question,
        'question_number': answered_questions + 1,
        'total_questions': session_data['total_questions_to_answer'],
        'session_id': session_id,
        'skipped_info': f"{len(session_data['skipped_questions'])}개 질문 스킵됨" if session_data['skipped_questions'] else None
    })

@bp_link6.route('/link6_get_summary', methods=['POST'])
def link6_get_summary():
    data = request.get_json() or {}
    session_id = data.get('session_id', '')
    
    if not session_id or session_id not in user_sessions:
        return jsonify({'error': '유효하지 않은 세션입니다.'}), 400
    
    session_data = user_sessions[session_id]
    if not session_data['completed']:
        return jsonify({'error': '아직 인터뷰가 완료되지 않았습니다.'}), 400
    
    client = _get_openai_client()
    if client is None:
        return jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}), 500

    try:
        # 사용자 답변들을 정리해서 요약 요청
        answers_text = "\n".join([
            f"Q: {qa['question']}\nA: {qa['answer']}\n"
            for qa in session_data['user_answers']
        ])
        
        summary_prompt = f"""
다음은 IT 시스템에 대한 정보 수집 결과입니다. 답변을 바탕으로 시스템 현황을 분석하여 요약해주세요:

{answers_text}

다음 형식으로 요약해주세요:
1. 시스템 개요 (시스템명, 유형, 클라우드 여부 등)
2. 기술적 환경 (OS, DB, 보안도구 등)
3. 권한 관리 현황 (권한 부여/회수 절차, 모니터링 등)
4. 보안 수준 평가 및 개선 권장사항
5. 컴플라이언스 관련 사항
"""
        
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "당신은 IT 시스템 보안 및 컴플라이언스 전문가입니다. 기업의 IT 환경을 분석하고 보안 위험도를 평가하는 역할을 합니다."},
                {"role": "user", "content": summary_prompt}
            ],
            max_completion_tokens=1000
        )
        summary = completion.choices[0].message.content or '요약을 생성할 수 없습니다.'
        
        return jsonify({
            'summary': summary,
            'user_answers': session_data['user_answers'],
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': f'요약 생성 오류: {str(e)}'}), 500

@bp_link6.route('/link6_session_status', methods=['POST'])
def link6_session_status():
    data = request.get_json() or {}
    session_id = data.get('session_id', '')
    
    if not session_id or session_id not in user_sessions:
        return jsonify({'error': '유효하지 않은 세션입니다.'}), 400
    
    session_data = user_sessions[session_id]
    return jsonify({
        'session_id': session_id,
        'current_question_index': session_data['current_question_index'],
        'total_questions': len(PREDEFINED_QUESTIONS),
        'completed': session_data['completed'],
        'answers_count': len(session_data['user_answers'])
    })
