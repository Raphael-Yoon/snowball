<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Snowball - AI 인터뷰</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}
    
    <div class="interview-container">
        <!-- AI 인터뷰 -->
            <!-- 시작 화면 -->
            <div id="welcome-screen">
                <div class="card welcome-card text-center">
                    <div class="card-body p-5">
                        <i class="fas fa-cogs fa-3x mb-4"></i>
                        <h2 class="card-title mb-4">시스템 정보 수집에 오신 것을 환영합니다!</h2>
                        <p class="card-text fs-5 mb-4">
                            귀하의 IT 시스템에 대한 정보를 수집하겠습니다.<br>
                            각 질문에 정확하고 자세히 답변해주세요.
                        </p>
                        <button class="btn btn-light btn-lg" id="start-interview">
                            <i class="fas fa-play me-2"></i>정보 수집 시작
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- 질문 화면 -->
            <div id="question-screen" style="display:none;">
                <div class="text-center mb-4">
                    <div class="progress-circle" id="progress-circle">1/21</div>
                    <div class="progress" style="height: 8px; border-radius: 4px;">
                        <div class="progress-bar" id="progress-bar" style="width: 10%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"></div>
                    </div>
                </div>
                
                <div class="card question-card">
                    <div class="card-body p-4">
                        <h5 class="card-title text-center mb-4">
                            <i class="fas fa-question-circle text-primary me-2"></i>
                            <span id="question-text">질문이 로딩중입니다...</span>
                        </h5>
                        
                        <div class="mb-4">
                            <textarea class="form-control answer-input" id="answer-input" rows="4" 
                                      placeholder="이곳에 답변을 입력해주세요..."></textarea>
                        </div>
                        
                        <div class="text-center">
                            <button class="btn btn-primary-custom" id="submit-answer">
                                <i class="fas fa-paper-plane me-2"></i>답변 제출
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- 이전 답변들 -->
                <div class="mt-4" id="answer-history-container" style="display:none;">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-history me-2"></i>이전 답변들
                            </h6>
                        </div>
                        <div class="card-body answer-history" id="answer-history">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 완료 화면 -->
            <div id="completion-screen" style="display:none;">
                <div class="card summary-card text-center">
                    <div class="card-body p-5">
                        <i class="fas fa-check-circle fa-3x mb-4 text-success"></i>
                        <h2 class="card-title mb-4">정보 수집이 완료되었습니다!</h2>
                        <p class="card-text fs-5 mb-4">
                            모든 질문에 답변해주셔서 감사합니다.<br>
                            AI가 시스템 정보를 분석하여 요약을 생성하고 있습니다.
                        </p>
                        <button class="btn btn-primary-custom" id="get-summary">
                            <i class="fas fa-chart-pie me-2"></i>분석 결과 보기
                        </button>
                    </div>
                </div>
                
                <!-- 요약 결과 -->
                <div id="summary-result" style="display:none;" class="mt-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-server me-2"></i>시스템 분석 결과
                            </h5>
                        </div>
                        <div class="card-body" id="summary-content">
                        </div>
                    </div>
                </div>
            </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    let currentSessionId = null;
    let currentQuestionNumber = 0;
    let totalQuestions = 21;
    
    // 인터뷰 시작
    function startInterview() {
        fetch('/link6_start_interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.session_id) {
                currentSessionId = data.session_id;
                currentQuestionNumber = data.question_number;
                totalQuestions = data.total_questions;
                
                // 화면 전환
                document.getElementById('welcome-screen').style.display = 'none';
                document.getElementById('question-screen').style.display = 'block';
                
                // 질문 표시
                document.getElementById('question-text').textContent = data.question;
                updateProgress();
            } else {
                alert(data.error || '인터뷰 시작 중 오류가 발생했습니다.');
            }
        })
        .catch(() => {
            alert('서버 오류가 발생했습니다.');
        });
    }
    
    // 답변 제출
    function submitAnswer() {
        const answerInput = document.getElementById('answer-input');
        const answer = answerInput.value.trim();
        
        if (!answer) {
            alert('답변을 입력해주세요.');
            return;
        }
        
        if (!currentSessionId) {
            alert('세션이 유효하지 않습니다.');
            return;
        }
        
        // 버튼 비활성화
        const submitBtn = document.getElementById('submit-answer');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>처리중...';
        
        fetch('/link6_submit_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                answer: answer
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.completed) {
                // 인터뷰 완료
                document.getElementById('question-screen').style.display = 'none';
                document.getElementById('completion-screen').style.display = 'block';
            } else if (data.question) {
                // 다음 질문
                currentQuestionNumber = data.question_number;
                totalQuestions = data.total_questions;
                document.getElementById('question-text').textContent = data.question;
                answerInput.value = '';
                updateProgress();
                updateAnswerHistory();
                
                // 스킵 정보 표시 (있는 경우)
                if (data.skipped_info) {
                    showSkipNotification(data.skipped_info);
                }
            } else {
                alert(data.error || '오류가 발생했습니다.');
            }
        })
        .catch(() => {
            alert('서버 오류가 발생했습니다.');
        })
        .finally(() => {
            // 버튼 복원
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>답변 제출';
        });
    }
    
    // 진행률 업데이트
    function updateProgress() {
        const progressCircle = document.getElementById('progress-circle');
        const progressBar = document.getElementById('progress-bar');
        
        progressCircle.textContent = `${currentQuestionNumber}/${totalQuestions}`;
        const percentage = (currentQuestionNumber / totalQuestions) * 100;
        progressBar.style.width = `${percentage}%`;
        
        // 답변 히스토리 표시 (2번째 질문부터)
        if (currentQuestionNumber > 1) {
            document.getElementById('answer-history-container').style.display = 'block';
        }
    }
    
    // 스킵 알림 표시
    function showSkipNotification(message) {
        // 기존 알림이 있으면 제거
        const existingNotification = document.querySelector('.skip-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // 새 알림 생성
        const notification = document.createElement('div');
        notification.className = 'alert alert-info skip-notification mt-2';
        notification.innerHTML = `<i class="fas fa-info-circle me-2"></i>${message}`;
        
        // 진행률 바 아래에 삽입
        const progressContainer = document.querySelector('.text-center.mb-4');
        progressContainer.appendChild(notification);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    // 답변 히스토리 업데이트
    function updateAnswerHistory() {
        if (!currentSessionId) return;
        
        fetch('/link6_session_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId })
        })
        .then(res => res.json())
        .then(data => {
            const historyDiv = document.getElementById('answer-history');
            let historyHtml = '';
            
            // 세션 데이터에서 답변 수 계산
            const answersCount = data.answers_count || 0;
            for (let i = 1; i <= answersCount; i++) {
                historyHtml += `
                    <div class="mb-2 p-2 border-start border-primary border-3">
                        <small class="text-muted">질문 ${i}</small>
                        <div class="text-truncate" style="max-width: 300px;">답변이 저장되었습니다.</div>
                    </div>
                `;
            }
            historyDiv.innerHTML = historyHtml;
        });
    }
    
    // 요약 생성
    function getSummary() {
        if (!currentSessionId) return;
        
        const summaryBtn = document.getElementById('get-summary');
        summaryBtn.disabled = true;
        summaryBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>분석 중...';
        
        fetch('/link6_get_summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSessionId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.summary) {
                document.getElementById('summary-content').innerHTML = `
                    <div class="mb-4">${data.summary.replace(/\n/g, '<br>')}</div>
                    <hr>
                    <h6><i class="fas fa-list me-2"></i>답변 요약</h6>
                    <div class="row">
                        ${data.user_answers.map((qa, index) => `
                            <div class="col-md-6 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h6 class="card-title">질문 ${index + 1}</h6>
                                        <p class="card-text small text-muted">${qa.question}</p>
                                        <p class="card-text">${qa.answer}</p>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                document.getElementById('summary-result').style.display = 'block';
            } else {
                alert(data.error || '요약 생성 중 오류가 발생했습니다.');
            }
        })
        .catch(() => {
            alert('서버 오류가 발생했습니다.');
        })
        .finally(() => {
            summaryBtn.disabled = false;
            summaryBtn.innerHTML = '<i class="fas fa-chart-pie me-2"></i>분석 결과 보기';
        });
    }
    
    // 이벤트 리스너
    document.getElementById('start-interview').onclick = startInterview;
    document.getElementById('submit-answer').onclick = submitAnswer;
    document.getElementById('get-summary').onclick = getSummary;
    
    // Enter 키 이벤트 (Ctrl+Enter로 답변 제출)
    document.getElementById('answer-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            submitAnswer();
        }
    });
    </script>
</body>
</html>