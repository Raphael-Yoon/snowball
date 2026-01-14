<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snowball - AI 분석 결과 조회</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        /* Link10 페이지 전용 스타일 */
        .link10-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }

        .page-header {
            margin-bottom: 40px;
            text-align: center;
        }

        .page-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 10px;
        }

        .page-description {
            color: #6c757d;
            font-size: 1.1rem;
        }

        .section-header {
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border-color);
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary-color);
            margin: 0;
        }

        /* 결과 카드 그리드 */
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
        }

        .result-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
            border-color: var(--secondary-color);
        }

        .result-header {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 20px;
        }

        .result-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            flex-shrink: 0;
        }

        .result-info {
            flex: 1;
            min-width: 0;
        }

        .result-filename {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text-color);
            margin-bottom: 8px;
            word-break: break-word;
        }

        .result-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9rem;
            color: #6c757d;
        }

        .result-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .result-badges {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            flex-wrap: wrap;
        }

        .badge-tag {
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .badge-market {
            background-color: #e0f2fe;
            color: #0369a1;
        }

        .badge-market.kospi {
            background-color: #dbeafe;
            color: #1e40af;
        }

        .badge-market.kosdaq {
            background-color: #fce7f3;
            color: #be185d;
        }

        .badge-market.all {
            background-color: #f3e8ff;
            color: #7c3aed;
        }

        .badge-count {
            background-color: #fef3c7;
            color: #92400e;
        }

        .result-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .result-btn {
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            border: 2px solid transparent;
            display: inline-block;
        }

        .result-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .btn-download {
            background-color: #10b981;
            color: white;
        }

        .btn-download:hover {
            background-color: #059669;
            color: white;
        }

        .btn-ai {
            background-color: #8b5cf6;
            color: white;
        }

        .btn-ai:hover {
            background-color: #7c3aed;
            color: white;
        }

        .btn-ai:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .btn-drive {
            background-color: #4285f4;
            color: white;
        }

        .btn-drive:hover {
            background-color: #3367d6;
            color: white;
        }

        /* 모달 스타일 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(5px);
            z-index: 2000;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .modal-content {
            background: white;
            border-radius: 16px;
            width: 100%;
            max-width: 1000px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .modal-header {
            padding: 25px 30px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 16px 16px 0 0;
        }

        .modal-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .modal-body {
            padding: 30px;
            overflow-y: auto;
            flex: 1;
        }

        .modal-footer {
            padding: 20px 30px;
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            background: var(--light-bg);
            border-radius: 0 0 16px 16px;
        }

        .close-modal {
            font-size: 28px;
            cursor: pointer;
            color: white;
            line-height: 1;
            opacity: 0.8;
            transition: opacity 0.3s;
        }

        .close-modal:hover {
            opacity: 1;
        }

        .ai-markdown-body {
            line-height: 1.8;
            color: var(--text-color);
        }

        .ai-markdown-body h1,
        .ai-markdown-body h2,
        .ai-markdown-body h3 {
            color: var(--primary-color);
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 700;
        }

        .ai-markdown-body h1 {
            font-size: 2rem;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 10px;
        }

        .ai-markdown-body h2 {
            font-size: 1.5rem;
        }

        .ai-markdown-body h3 {
            font-size: 1.25rem;
        }

        .ai-markdown-body p {
            margin-bottom: 16px;
        }

        .ai-markdown-body ul,
        .ai-markdown-body ol {
            margin-bottom: 16px;
            padding-left: 30px;
        }

        .ai-markdown-body li {
            margin-bottom: 8px;
        }

        .ai-markdown-body table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            border: 1px solid var(--border-color);
        }

        .ai-markdown-body th,
        .ai-markdown-body td {
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            text-align: left;
        }

        .ai-markdown-body th {
            background-color: var(--light-bg);
            color: var(--primary-color);
            font-weight: 700;
        }

        .ai-markdown-body tr:hover {
            background-color: var(--hover-color);
        }

        /* 첫 번째 테이블 (종합 추천 의견) - 순위 컬럼 넓게 */
        .ai-markdown-body table:first-of-type th:first-child,
        .ai-markdown-body table:first-of-type td:first-child {
            width: 80px;
            min-width: 80px;
        }

        /* 첫 번째 테이블 (종합 추천 의견) - 종목명 컬럼 넓게 */
        .ai-markdown-body table:first-of-type th:nth-child(2),
        .ai-markdown-body table:first-of-type td:nth-child(2) {
            width: 180px;
            min-width: 180px;
        }

        /* 두 번째 테이블 (리스크 요인) - 리스크 유형 컬럼 */
        .ai-markdown-body table:nth-of-type(2) th:first-child,
        .ai-markdown-body table:nth-of-type(2) td:first-child {
            width: 150px;
            min-width: 150px;
        }

        /* 두 번째 테이블 (리스크 요인) - 상세 내용과 투자 조언 컬럼을 반반으로 */
        .ai-markdown-body table:nth-of-type(2) th:nth-child(2),
        .ai-markdown-body table:nth-of-type(2) td:nth-child(2),
        .ai-markdown-body table:nth-of-type(2) th:nth-child(3),
        .ai-markdown-body table:nth-of-type(2) td:nth-child(3) {
            width: 45%;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }

        .empty-state i {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.3;
        }

        @media (max-width: 768px) {
            .results-grid {
                grid-template-columns: 1fr;
            }

            .result-actions {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>
    {% include 'navi.jsp' %}

    <!-- AI Analysis Modal -->
    <div id="aiModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2><i class="fas fa-robot"></i> AI 투자 리포트</h2>
                <span class="close-modal" onclick="closeAiModal()">&times;</span>
            </div>
            <div id="aiResultContent" class="modal-body">
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">불러오는 중...</span>
                    </div>
                    <p class="mt-3 text-muted">리포트를 불러오는 중...</p>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeAiModal()">닫기</button>
            </div>
        </div>
    </div>

    <!-- Email Input Modal -->
    <div id="emailModal" class="modal">
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2><i class="fas fa-envelope"></i> 이메일로 리포트 전송</h2>
                <span class="close-modal" onclick="closeEmailModal()">&times;</span>
            </div>
            <div class="modal-body">
                <p class="mb-3">AI 분석 리포트를 받으실 이메일 주소를 입력해주세요.</p>
                <div class="mb-3">
                    <label for="recipientEmail" class="form-label">이메일 주소</label>
                    <input type="email" class="form-control" id="recipientEmail" placeholder="example@email.com" required>
                    <div class="invalid-feedback" id="emailError" style="display: none;">
                        올바른 이메일 주소를 입력해주세요.
                    </div>
                </div>
                <div id="sendingStatus" style="display: none;" class="alert alert-info">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">전송 중...</span>
                    </div>
                    이메일을 전송하는 중입니다...
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeEmailModal()">취소</button>
                <button class="btn btn-primary" onclick="sendReportByEmail()">
                    <i class="fas fa-paper-plane"></i> 전송
                </button>
            </div>
        </div>
    </div>

    <div class="link10-container">
        <div class="page-header">
            <h1 class="page-title">
                <i class="fas fa-chart-line"></i> AI 분석 결과 조회
            </h1>
        </div>

        <div id="resultsList" class="results-grid">
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">불러오는 중...</span>
                </div>
                <p class="mt-3">목록을 불러오는 중...</p>
            </div>
        </div>
    </div>

    <script>
        let currentFilename = null; // 현재 열려있는 리포트의 파일명
        const isLoggedIn = {{ 'true' if is_logged_in else 'false' }};

        window.onload = function () {
            loadResults();
        };

        function loadResults() {
            const resultsList = document.getElementById('resultsList');
            resultsList.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">불러오는 중...</span>
                    </div>
                    <p class="mt-3">목록을 불러오는 중...</p>
                </div>
            `;

            fetch('/link10/api/results')
                .then(response => response.json())
                .then(files => {
                    // AI 분석이 있는 파일만 필터링
                    const filesWithAi = files.filter(file => file.has_ai);

                    if (filesWithAi.length === 0) {
                        resultsList.innerHTML = `
                            <div class="empty-state" style="grid-column: 1/-1;">
                                <i class="fas fa-inbox"></i>
                                <h3>AI 분석 결과가 없습니다</h3>
                                <p>Trade 프로젝트에서 AI 분석을 실행하면 여기에 표시됩니다.</p>
                            </div>
                        `;
                        return;
                    }
                    resultsList.innerHTML = filesWithAi.map(file => {
                        // 파일명 파싱: {market}_{count}_{timestamp}.xlsx
                        const fileNameParts = file.filename.replace('.xlsx', '').split('_');
                        let marketLabel = '';
                        let marketClass = '';
                        let countLabel = '';
                        let displayTitle = file.filename; // 기본값
                        let collectionDate = '';

                        if (fileNameParts.length >= 4) {
                            const market = fileNameParts[0].toUpperCase();
                            const count = fileNameParts[1];
                            const dateStr = fileNameParts[2]; // YYYYMMDD
                            const timeStr = fileNameParts[3]; // HHMMSS

                            // 시장 라벨
                            if (market === 'KOSPI') {
                                marketLabel = 'KOSPI';
                                marketClass = 'kospi';
                            } else if (market === 'KOSDAQ') {
                                marketLabel = 'KOSDAQ';
                                marketClass = 'kosdaq';
                            } else if (market === 'ALL') {
                                marketLabel = '전체시장';
                                marketClass = 'all';
                            }

                            // 종목 개수 라벨
                            if (count === 'all') {
                                countLabel = '전체 종목';
                            } else if (count.startsWith('top')) {
                                const num = count.replace('top', '');
                                countLabel = `상위 ${num}개`;
                            }

                            // 제목 생성
                            if (marketLabel && countLabel) {
                                displayTitle = `${marketLabel} ${countLabel} 분석`;
                            }

                            // 수집 일자 포맷팅: 20251228 -> 2025-12-28
                            if (dateStr && dateStr.length === 8) {
                                const year = dateStr.substring(0, 4);
                                const month = dateStr.substring(4, 6);
                                const day = dateStr.substring(6, 8);
                                collectionDate = `${year}-${month}-${day}`;
                            }
                        }

                        return `
                        <div class="result-card">
                            <div class="result-header">
                                <div class="result-icon">
                                    <i class="fas fa-chart-line" style="color: white;"></i>
                                </div>
                                <div class="result-info">
                                    <div class="result-filename">${displayTitle}</div>
                                    <div class="result-meta">
                                        ${collectionDate ? `<span><i class="far fa-calendar-alt"></i> 데이터 수집: ${collectionDate}</span>` : ''}
                                    </div>
                                </div>
                            </div>
                            <div class="result-actions">
                                <button onclick="viewAiReport('${file.filename}')" class="result-btn btn-ai">
                                    <i class="fas fa-robot"></i> AI 리포트 보기
                                </button>
                                <button onclick="handleReportSend('${file.filename}')" class="result-btn btn-download">
                                    <i class="fas fa-paper-plane"></i> AI 리포트 전송
                                </button>
                            </div>
                        </div>
                        `;
                    }).join('');
                })
                .catch(error => {
                    console.error('결과 목록 로드 실패:', error);
                    resultsList.innerHTML = `
                        <div class="empty-state" style="grid-column: 1/-1;">
                            <i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i>
                            <h3>목록을 불러오는데 실패했습니다</h3>
                            <p style="color: #dc3545;">${error.message || '서버 오류가 발생했습니다.'}</p>
                            <button class="btn btn-primary mt-3" onclick="loadResults()">
                                <i class="fas fa-redo"></i> 다시 시도
                            </button>
                        </div>
                    `;
                });
        }

        function viewAiReport(filename) {
            const modal = document.getElementById('aiModal');
            const content = document.getElementById('aiResultContent');

            content.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">불러오는 중...</span>
                    </div>
                    <p class="mt-3 text-muted">리포트를 불러오는 중...</p>
                </div>
            `;
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';

            fetch(`/link10/api/ai_result/${filename}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        content.innerHTML = `<div class="ai-markdown-body">${marked.parse(data.result)}</div>`;
                    } else {
                        content.innerHTML = `
                            <div class="alert alert-warning" role="alert">
                                <i class="fas fa-exclamation-circle"></i>
                                <strong>알림:</strong> ${data.message}
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    content.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            <i class="fas fa-times-circle"></i>
                            <strong>오류:</strong> ${error.message || '리포트를 불러오는 중 오류가 발생했습니다.'}
                        </div>
                    `;
                });
        }

        function downloadReport(format) {
            if (!currentFilename) {
                alert('다운로드할 리포트가 선택되지 않았습니다.');
                return;
            }

            // 다운로드 URL 생성 (PDF 형식 고정)
            const downloadUrl = `/link10/api/download_report/${currentFilename}?format=pdf`;

            // 다운로드 시작
            window.location.href = downloadUrl;

            // Toast 메시지 표시 (Bootstrap Toast 사용)
            const toastHtml = `
                <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
                    <div class="toast show" role="alert">
                        <div class="toast-header">
                            <i class="fas fa-download text-success me-2"></i>
                            <strong class="me-auto">다운로드 시작</strong>
                            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                        </div>
                        <div class="toast-body">
                            PDF 형식으로 다운로드를 시작합니다.
                        </div>
                    </div>
                </div>
            `;

            // Toast를 body에 추가
            const toastContainer = document.createElement('div');
            toastContainer.innerHTML = toastHtml;
            document.body.appendChild(toastContainer);

            // 3초 후 Toast 제거
            setTimeout(() => {
                toastContainer.remove();
            }, 3000);
        }

        function closeAiModal() {
            document.getElementById('aiModal').style.display = 'none';
            document.body.style.overflow = 'auto';
        }

        function closeEmailModal() {
            document.getElementById('emailModal').style.display = 'none';
            document.getElementById('recipientEmail').value = '';
            document.getElementById('emailError').style.display = 'none';
            document.getElementById('sendingStatus').style.display = 'none';
            document.body.style.overflow = 'auto';
        }

        function showToast(type, title, message) {
            // type: 'success', 'danger', 'warning', 'info'
            const iconMap = {
                'success': 'fa-check-circle',
                'danger': 'fa-times-circle',
                'warning': 'fa-exclamation-triangle',
                'info': 'fa-info-circle'
            };

            const icon = iconMap[type] || 'fa-info-circle';

            const toastHtml = `
                <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
                    <div class="toast show" role="alert">
                        <div class="toast-header">
                            <i class="fas ${icon} text-${type} me-2"></i>
                            <strong class="me-auto">${title}</strong>
                            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                        </div>
                        <div class="toast-body">
                            ${message}
                        </div>
                    </div>
                </div>
            `;

            const toastContainer = document.createElement('div');
            toastContainer.innerHTML = toastHtml;
            document.body.appendChild(toastContainer);

            // 3초 후 Toast 제거
            setTimeout(() => {
                toastContainer.remove();
            }, 3000);
        }

        function handleReportSend(filename) {
            currentFilename = filename;

            if (isLoggedIn) {
                // 로그인한 경우: 바로 다운로드
                window.location.href = `/link10/api/download_report/${filename}?format=pdf`;
            } else {
                // 로그인하지 않은 경우: 이메일 입력 모달 표시
                document.getElementById('emailModal').style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        }

        function sendReportByEmail() {
            const emailInput = document.getElementById('recipientEmail');
            const email = emailInput.value.trim();
            const emailError = document.getElementById('emailError');
            const sendingStatus = document.getElementById('sendingStatus');

            // 이메일 유효성 검사
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                emailError.style.display = 'block';
                emailInput.classList.add('is-invalid');
                return;
            }

            emailError.style.display = 'none';
            emailInput.classList.remove('is-invalid');
            sendingStatus.style.display = 'block';

            // 버튼 비활성화
            const sendButton = event.target;
            sendButton.disabled = true;

            // 이메일 전송 API 호출
            fetch('/link10/api/send_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: currentFilename,
                    email: email
                })
            })
            .then(response => response.json())
            .then(data => {
                sendingStatus.style.display = 'none';
                sendButton.disabled = false;

                if (data.success) {
                    // 성공 토스트 메시지
                    showToast('success', '전송 완료', '이메일이 성공적으로 전송되었습니다!');
                    closeEmailModal();
                } else {
                    // 실패 토스트 메시지
                    showToast('danger', '전송 실패', data.message || '알 수 없는 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                sendingStatus.style.display = 'none';
                sendButton.disabled = false;
                // 오류 토스트 메시지
                showToast('danger', '오류 발생', '이메일 전송 중 오류가 발생했습니다.');
            });
        }

        window.onclick = function (event) {
            const aiModal = document.getElementById('aiModal');
            const emailModal = document.getElementById('emailModal');

            if (event.target == aiModal) {
                closeAiModal();
            }
            if (event.target == emailModal) {
                closeEmailModal();
            }
        }

        // ESC 키로 모달 닫기
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                const modal = document.getElementById('aiModal');
                if (modal.style.display === 'flex') {
                    closeAiModal();
                }
            }
        });
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>