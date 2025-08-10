<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>GPT 챗봇</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/common.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}
    <div class="container mt-4">
        {% if remote_addr == '127.0.0.1' %}
        <h4>GPT 챗봇</h4>
        <div class="input-group mb-3">
            <input type="text" id="chat-input" class="form-control" placeholder="질문을 입력하세요...">
            <button class="btn btn-success" id="chat-send">전송</button>
        </div>
        <div id="chat-answer" class="alert alert-secondary" style="display:none;"></div>
        {% else %}
        <div class="alert alert-warning mt-5">이 기능은 로컬(127.0.0.1)에서만 사용할 수 있습니다.</div>
        {% endif %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% if remote_addr == '127.0.0.1' %}
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
    {% endif %}
</body>
</html>