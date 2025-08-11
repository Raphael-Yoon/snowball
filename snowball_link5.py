from flask import Blueprint, request, jsonify
import requests
from requests.exceptions import Timeout, ConnectionError

bp_link5 = Blueprint('link5', __name__)

OLLAMA_URL = "http://192.168.45.181:11434/api/generate"
OLLAMA_MODEL = "gpt-oss:20b"  # 필요시 변경

@bp_link5.route('/link5_chat', methods=['POST'])
def link5_chat():
    data = request.get_json()
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'error': '질문이 없습니다.'}), 400
    # Ollama 서버 헬스체크
    try:
        health = requests.get(OLLAMA_URL.replace('/api/generate', '/api/tags'), timeout=2)
        if health.status_code != 200:
            return jsonify({'error': 'AI 서버가 비활성화되어 있습니다.'}), 503
    except Exception:
        return jsonify({'error': 'AI 서버가 비활성화되어 있습니다.'}), 503
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=600)
        response.raise_for_status()
        answer = response.json().get("response", "답변이 없습니다.")
        return jsonify({'answer': answer})
    except (Timeout, ConnectionError):
        return jsonify({'error': '챗봇 서버가 응답하지 않습니다.'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500
