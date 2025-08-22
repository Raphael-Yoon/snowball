<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Ollama</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}
    <div class="container mt-4">
        <h4>Ollama</h4>
        <div class="input-group mb-3">
            <input type="text" id="chat-input" class="form-control" placeholder="질문을 입력하세요...">
            <button class="btn btn-success" id="chat-send">전송</button>
        </div>
        <div id="chat-answer" class="alert alert-secondary" style="display:none;"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    let loadingInterval = null;
    function startLoadingAnimation() {
        const answerDiv = document.getElementById('chat-answer');
        let dots = 1;
        loadingInterval = setInterval(() => {
            answerDiv.textContent = '답변을 불러오는 중' + '.'.repeat(dots);
            dots = dots < 3 ? dots + 1 : 1;
        }, 400);
    }
    function stopLoadingAnimation() {
        if (loadingInterval) clearInterval(loadingInterval);
        loadingInterval = null;
    }
    function sendChat() {
        const input = document.getElementById('chat-input');
        const answerDiv = document.getElementById('chat-answer');
        const question = input.value.trim();
        if (!question) return;
        answerDiv.style.display = 'block';
        startLoadingAnimation();
        fetch('/link5_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: question })
        })
        .then(res => res.json())
        .then(data => {
            stopLoadingAnimation();
            if (data.answer) answerDiv.textContent = data.answer;
            else answerDiv.textContent = data.error || '오류 발생';
        })
        .catch(() => {
            stopLoadingAnimation();
            answerDiv.textContent = '서버 오류';
        });
    }
    document.getElementById('chat-send').onclick = sendChat;
    document.getElementById('chat-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendChat();
        }
    });
    </script>
</body>
</html>