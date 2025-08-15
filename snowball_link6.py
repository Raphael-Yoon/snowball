from flask import Blueprint, request, jsonify
from openai import OpenAI
import os

bp_link6 = Blueprint('link6', __name__)

def _get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

@bp_link6.route('/link6_chat', methods=['POST'])
def link6_chat():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': '질문이 없습니다.'}), 400

    client = _get_openai_client()
    if client is None:
        return jsonify({'error': 'OPENAI_API_KEY가 설정되지 않았습니다.'}), 500

    try:
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "당신은 간결하고 정확하게 대답하는 한국어 도우미입니다."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=800
        )
        answer = completion.choices[0].message.content or '답변이 없습니다.'
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': f'OpenAI 호출 오류: {str(e)}'}), 500
