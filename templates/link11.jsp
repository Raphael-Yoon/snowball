<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snowball - 정보보호공시</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <style>
        /* 정보보호공시 페이지 전용 스타일 */
        .disclosure-container {
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
            letter-spacing: -0.03em;
        }

        .page-description {
            color: #6c757d;
            font-size: 1.1rem;
        }

        /* 대시보드 카드 */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        }

        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            font-size: 24px;
            color: white;
        }

        .stat-icon.investment { background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); }
        .stat-icon.personnel { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
        .stat-icon.certification { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
        .stat-icon.activity { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 5px;
        }

        .stat-label {
            color: #6c757d;
            font-size: 0.95rem;
        }

        /* 진행률 바 */
        .progress-section {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 40px;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .progress-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .progress-percentage {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--secondary-color);
        }

        .progress-bar-container {
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
        }

        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--secondary-color) 0%, var(--primary-color) 100%);
            border-radius: 10px;
            transition: width 0.5s ease;
        }

        /* 카테고리 카드 */
        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }

        .category-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
        }

        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
            border-color: var(--secondary-color);
        }

        .category-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        .category-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
        }

        .category-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }

        .category-progress {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border-color);
        }

        .category-stats {
            color: #6c757d;
            font-size: 0.9rem;
        }

        .category-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .category-badge.complete { background: #d1fae5; color: #059669; }
        .category-badge.in-progress { background: #fef3c7; color: #d97706; }
        .category-badge.not-started { background: #f3f4f6; color: #6b7280; }

        /* 질문 섹션 */
        .questions-section {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 30px;
        }

        .question-item {
            padding: 20px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        .question-item:hover {
            border-color: var(--secondary-color);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .question-item.level-1 {
            background: #f8fafc;
        }

        .question-item.level-2 {
            margin-left: 30px;
            background: white;
        }

        .question-header {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 15px;
        }

        .question-number {
            background: var(--primary-color);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .question-text {
            flex: 1;
            font-size: 1.05rem;
            color: var(--text-color);
            line-height: 1.6;
        }

        .question-help {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 15px;
            padding: 10px 15px;
            background: #f1f5f9;
            border-radius: 8px;
        }

        /* 입력 필드 스타일 */
        .answer-section {
            margin-top: 15px;
        }

        .yes-no-buttons {
            display: flex;
            gap: 15px;
        }

        .yes-no-btn {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            background: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .yes-no-btn:hover {
            border-color: var(--secondary-color);
        }

        .yes-no-btn.selected.yes {
            background: #d1fae5;
            border-color: #10b981;
            color: #059669;
        }

        .yes-no-btn.selected.no {
            background: #fee2e2;
            border-color: #ef4444;
            color: #dc2626;
        }

        .text-input, .number-input, .date-input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .text-input:focus, .number-input:focus, .date-input:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(var(--secondary-color-rgb), 0.1);
        }

        .checkbox-group, .select-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .checkbox-item, .radio-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 15px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .checkbox-item:hover, .radio-item:hover {
            border-color: var(--secondary-color);
        }

        .checkbox-item.selected, .radio-item.selected {
            background: #eff6ff;
            border-color: var(--secondary-color);
        }

        /* 증빙 자료 섹션 */
        .evidence-section {
            margin-top: 20px;
            padding: 15px;
            background: #fef3c7;
            border-radius: 8px;
        }

        .evidence-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #92400e;
            margin-bottom: 10px;
        }

        .evidence-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .evidence-item {
            padding: 5px 12px;
            background: white;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #78350f;
        }

        .evidence-upload-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 15px;
            background: #d97706;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.3s ease;
        }

        .evidence-upload-btn:hover {
            background: #b45309;
        }

        /* 버튼 스타일 */
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 40px;
        }

        .btn-primary-custom {
            padding: 12px 30px;
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-primary-custom:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .btn-secondary-custom {
            padding: 12px 30px;
            background: white;
            color: var(--primary-color);
            border: 2px solid var(--primary-color);
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-secondary-custom:hover {
            background: var(--primary-color);
            color: white;
        }

        /* 로딩 스피너 */
        .loading-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--secondary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* 알림 메시지 */
        .alert-custom {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .alert-success { background: #d1fae5; color: #059669; border: 1px solid #10b981; }
        .alert-warning { background: #fef3c7; color: #d97706; border: 1px solid #f59e0b; }
        .alert-error { background: #fee2e2; color: #dc2626; border: 1px solid #ef4444; }

        /* 토스트 메시지 */
        .toast-container {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .toast-message {
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 280px;
            max-width: 400px;
            animation: slideIn 0.3s ease, fadeOut 0.3s ease 2.7s forwards;
            font-weight: 500;
        }

        .toast-message.success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .toast-message.error {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }

        .toast-message.warning {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }

        .toast-message.info {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
        }

        .toast-message i {
            font-size: 1.2rem;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes fadeOut {
            from {
                opacity: 1;
            }
            to {
                opacity: 0;
            }
        }

        /* 반응형 */
        @media (max-width: 768px) {
            .disclosure-container {
                padding: 15px;
            }

            .page-title {
                font-size: 1.8rem;
            }

            .dashboard-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .category-grid {
                grid-template-columns: 1fr;
            }

            .question-item.level-2 {
                margin-left: 15px;
            }

            .yes-no-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>

<body>
    <!-- 네비게이션 -->
    {% include 'navi.jsp' %}

    <!-- 토스트 컨테이너 -->
    <div class="toast-container" id="toast-container"></div>

    <div class="disclosure-container">
        <!-- 페이지 헤더 -->
        <div class="page-header">
            <h1 class="page-title">
                <i class="fas fa-shield-alt"></i> 정보보호공시
            </h1>
            <p class="page-description">
                KISA 정보보호 공시를 위한 질문 응답 및 증빙 자료 관리 시스템
            </p>
        </div>

        <!-- 로그인 필요 알림 -->
        {% if not is_logged_in %}
        <div class="alert-custom alert-warning text-center">
            <i class="fas fa-exclamation-triangle"></i>
            정보보호공시 기능을 사용하려면 <a href="{{ url_for('login') }}">로그인</a>이 필요합니다.
        </div>
        {% endif %}

        <!-- 대시보드 뷰 (기본) -->
        <div id="dashboard-view">
            <!-- 진행률 섹션 -->
            <div class="progress-section">
                <div class="progress-header">
                    <span class="progress-title">전체 진행률</span>
                    <span class="progress-percentage" id="overall-percentage">0%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" id="overall-progress-bar" style="width: 0%"></div>
                </div>
                <div class="mt-3 text-muted text-center" id="progress-stats">
                    응답 완료: 0 / 65 질문
                </div>
            </div>

            <!-- 카테고리별 통계 카드 -->
            <div class="dashboard-grid">
                <div class="stat-card">
                    <div class="stat-icon investment">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="stat-value" id="stat-investment">0%</div>
                    <div class="stat-label">투자 현황 (13개)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon personnel">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-value" id="stat-personnel">0%</div>
                    <div class="stat-label">인력 현황 (15개)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon certification">
                        <i class="fas fa-certificate"></i>
                    </div>
                    <div class="stat-value" id="stat-certification">0%</div>
                    <div class="stat-label">인증 (8개)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon activity">
                        <i class="fas fa-tasks"></i>
                    </div>
                    <div class="stat-value" id="stat-activity">0%</div>
                    <div class="stat-label">활동 (29개)</div>
                </div>
            </div>

            <!-- 카테고리 카드 -->
            <h3 class="mb-4"><i class="fas fa-folder-open"></i> 카테고리별 질문</h3>
            <div class="category-grid" id="category-list">
                <!-- JavaScript로 동적 생성 -->
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p class="mt-3 text-muted">카테고리 로딩 중...</p>
                </div>
            </div>

            <!-- 액션 버튼 -->
            <div class="action-buttons">
                <button class="btn-secondary-custom" onclick="location.href='/link11/evidence'">
                    <i class="fas fa-file-alt"></i> 증빙자료 관리
                </button>
                <button class="btn-secondary-custom" onclick="generateReport()" id="generate-report-btn" disabled>
                    <i class="fas fa-file-pdf"></i> 공시자료 생성
                </button>
            </div>
        </div>

        <!-- 질문 응답 뷰 (카테고리 선택 시) -->
        <div id="questions-view" style="display: none;">
            <div class="mb-4">
                <button class="btn-secondary-custom" onclick="showDashboard()">
                    <i class="fas fa-arrow-left"></i> 대시보드로 돌아가기
                </button>
            </div>

            <div class="questions-section">
                <h3 class="mb-4" id="category-title">질문 목록</h3>
                <div id="questions-list">
                    <!-- JavaScript로 동적 생성 -->
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn-secondary-custom" onclick="saveDraft()">
                    <i class="fas fa-save"></i> 임시 저장
                </button>
                <button class="btn-primary-custom" onclick="saveAndNext()">
                    저장 후 다음 <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    </div>

    <!-- 파일 업로드 모달 -->
    <div class="modal fade" id="uploadModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">증빙자료 업로드</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="upload-form" enctype="multipart/form-data">
                        <input type="hidden" id="upload-question-id" name="question_id">
                        <div class="mb-3">
                            <label class="form-label">증빙 유형</label>
                            <select class="form-select" id="upload-evidence-type" name="evidence_type">
                                <option value="">선택하세요</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">파일 선택</label>
                            <input type="file" class="form-control" id="upload-file" name="file" required>
                            <small class="text-muted">최대 100MB, PDF/Word/Excel/이미지 형식 지원</small>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-primary" onclick="uploadFile()">업로드</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 스크립트 -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 전역 변수
        let currentYear = new Date().getFullYear();
        let companyId = '{{ user_info.company_name if user_info else "default" }}';
        let questions = [];
        let answers = {};
        let currentCategory = null;

        // 카테고리 아이콘 매핑
        const categoryIcons = {
            '정보보호 투자 현황': { icon: 'fas fa-chart-line', color: '#3b82f6' },
            '정보보호 인력 현황': { icon: 'fas fa-users', color: '#10b981' },
            '정보보호 관련 인증': { icon: 'fas fa-certificate', color: '#f59e0b' },
            '정보보호 관련 활동': { icon: 'fas fa-tasks', color: '#8b5cf6' }
        };

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            loadCategories();
            loadProgress();
        });

        // 카테고리 목록 로드
        async function loadCategories() {
            try {
                const response = await fetch('/link11/api/categories');
                const data = await response.json();

                if (data.success) {
                    renderCategories(data.categories);
                }
            } catch (error) {
                console.error('카테고리 로드 오류:', error);
                document.getElementById('category-list').innerHTML = `
                    <div class="alert-custom alert-error">
                        카테고리를 불러오는 중 오류가 발생했습니다.
                    </div>
                `;
            }
        }

        // 카테고리 렌더링
        function renderCategories(categories) {
            const container = document.getElementById('category-list');
            container.innerHTML = '';

            categories.forEach((cat, index) => {
                const iconInfo = categoryIcons[cat.name] || { icon: 'fas fa-folder', color: '#6b7280' };
                const card = document.createElement('div');
                card.className = 'category-card';
                card.onclick = () => showCategory(cat.name);

                card.innerHTML = `
                    <div class="category-header">
                        <div class="category-icon" style="background: ${iconInfo.color}">
                            <i class="${iconInfo.icon}"></i>
                        </div>
                        <h4 class="category-title">${cat.name}</h4>
                    </div>
                    <p class="text-muted mb-0">총 ${cat.total}개 질문 (1단계 ${cat.level1_count}개)</p>
                    <div class="category-progress">
                        <span class="category-stats">진행률: <span id="cat-progress-${index}">0%</span></span>
                        <span class="category-badge not-started" id="cat-badge-${index}">미시작</span>
                    </div>
                `;

                container.appendChild(card);
            });
        }

        // 진행률 로드
        async function loadProgress() {
            {% if is_logged_in %}
            try {
                const response = await fetch(`/link11/api/progress/${encodeURIComponent(companyId)}/${currentYear}`);
                const data = await response.json();

                if (data.success) {
                    updateProgressUI(data);
                }
            } catch (error) {
                console.error('진행률 로드 오류:', error);
            }
            {% endif %}
        }

        // 진행률 UI 업데이트
        function updateProgressUI(data) {
            const progress = data.progress;
            const categories = data.categories;

            // 전체 진행률
            document.getElementById('overall-percentage').textContent = `${progress.completion_rate}%`;
            document.getElementById('overall-progress-bar').style.width = `${progress.completion_rate}%`;
            document.getElementById('progress-stats').textContent =
                `응답 완료: ${progress.answered_questions} / ${progress.total_questions} 질문`;

            // 보고서 생성 버튼 활성화
            if (progress.completion_rate === 100) {
                document.getElementById('generate-report-btn').disabled = false;
            }

            // 카테고리별 진행률
            const categoryNames = Object.keys(categoryIcons);
            categoryNames.forEach((name, index) => {
                const catData = categories[name];
                if (catData) {
                    const progressEl = document.getElementById(`cat-progress-${index}`);
                    const badgeEl = document.getElementById(`cat-badge-${index}`);

                    if (progressEl) progressEl.textContent = `${catData.rate}%`;

                    if (badgeEl) {
                        if (catData.rate === 100) {
                            badgeEl.className = 'category-badge complete';
                            badgeEl.textContent = '완료';
                        } else if (catData.rate > 0) {
                            badgeEl.className = 'category-badge in-progress';
                            badgeEl.textContent = '진행중';
                        } else {
                            badgeEl.className = 'category-badge not-started';
                            badgeEl.textContent = '미시작';
                        }
                    }
                }
            });

            // 통계 카드 업데이트
            if (categories['정보보호 투자 현황']) {
                document.getElementById('stat-investment').textContent =
                    `${categories['정보보호 투자 현황'].rate}%`;
            }
            if (categories['정보보호 인력 현황']) {
                document.getElementById('stat-personnel').textContent =
                    `${categories['정보보호 인력 현황'].rate}%`;
            }
            if (categories['정보보호 관련 인증']) {
                document.getElementById('stat-certification').textContent =
                    `${categories['정보보호 관련 인증'].rate}%`;
            }
            if (categories['정보보호 관련 활동']) {
                document.getElementById('stat-activity').textContent =
                    `${categories['정보보호 관련 활동'].rate}%`;
            }
        }

        // 카테고리 질문 표시
        async function showCategory(categoryName) {
            currentCategory = categoryName;
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('questions-view').style.display = 'block';
            document.getElementById('category-title').textContent = categoryName;

            try {
                // 질문 로드
                const qResponse = await fetch(`/link11/api/questions?category=${encodeURIComponent(categoryName)}`);
                const qData = await qResponse.json();

                if (qData.success) {
                    questions = qData.questions;

                    // 기존 답변 로드
                    {% if is_logged_in %}
                    const aResponse = await fetch(`/link11/api/answers/${encodeURIComponent(companyId)}/${currentYear}`);
                    const aData = await aResponse.json();

                    if (aData.success) {
                        answers = {};
                        aData.answers.forEach(a => {
                            answers[a.question_id] = a.value;
                        });
                    }
                    {% endif %}

                    renderQuestions(questions);
                }
            } catch (error) {
                console.error('질문 로드 오류:', error);
            }
        }

        // 질문 렌더링
        function renderQuestions(questions) {
            const container = document.getElementById('questions-list');
            container.innerHTML = '';

            // 1단계 질문만 먼저 표시하고, 종속 질문은 답변에 따라 표시
            const level1Questions = questions.filter(q => q.level === 1);

            level1Questions.forEach(q => {
                const questionEl = createQuestionElement(q);
                container.appendChild(questionEl);

                // YES 응답 시 종속 질문 표시
                if (q.dependent_question_ids && answers[q.id] === 'YES') {
                    q.dependent_question_ids.forEach(depId => {
                        const depQ = questions.find(dq => dq.id === depId);
                        if (depQ) {
                            const depEl = createQuestionElement(depQ);
                            container.appendChild(depEl);
                        }
                    });
                }
            });
        }

        // 질문 요소 생성
        function createQuestionElement(q) {
            const div = document.createElement('div');
            div.className = `question-item level-${q.level}`;
            div.id = `question-${q.id}`;

            let answerHtml = '';
            const currentValue = answers[q.id] || '';

            switch (q.type) {
                case 'yes_no':
                    answerHtml = `
                        <div class="yes-no-buttons">
                            <button class="yes-no-btn yes ${currentValue === 'YES' ? 'selected' : ''}"
                                    onclick="selectYesNo('${q.id}', 'YES', this)">
                                <i class="fas fa-check"></i> 예
                            </button>
                            <button class="yes-no-btn no ${currentValue === 'NO' ? 'selected' : ''}"
                                    onclick="selectYesNo('${q.id}', 'NO', this)">
                                <i class="fas fa-times"></i> 아니오
                            </button>
                        </div>
                    `;
                    break;

                case 'text':
                    answerHtml = `
                        <textarea class="text-input" rows="3"
                                  placeholder="답변을 입력하세요..."
                                  onchange="updateAnswer('${q.id}', this.value)">${currentValue}</textarea>
                    `;
                    break;

                case 'number':
                    answerHtml = `
                        <input type="number" class="number-input"
                               placeholder="숫자를 입력하세요"
                               value="${currentValue}"
                               onchange="updateAnswer('${q.id}', this.value)">
                    `;
                    break;

                case 'date':
                    answerHtml = `
                        <input type="month" class="date-input"
                               value="${currentValue}"
                               onchange="updateAnswer('${q.id}', this.value)">
                    `;
                    break;

                case 'select':
                    const options = q.options || [];
                    answerHtml = `
                        <div class="select-group">
                            ${options.map(opt => `
                                <div class="radio-item ${currentValue === opt ? 'selected' : ''}"
                                     onclick="selectOption('${q.id}', '${opt}', this)">
                                    <i class="fas ${currentValue === opt ? 'fa-check-circle' : 'fa-circle'}"></i>
                                    ${opt}
                                </div>
                            `).join('')}
                        </div>
                    `;
                    break;

                case 'checkbox':
                    const checkOptions = q.options || [];
                    const selectedValues = Array.isArray(currentValue) ? currentValue : [];
                    answerHtml = `
                        <div class="checkbox-group">
                            ${checkOptions.map(opt => `
                                <div class="checkbox-item ${selectedValues.includes(opt) ? 'selected' : ''}"
                                     onclick="toggleCheckbox('${q.id}', '${opt}', this)">
                                    <i class="fas ${selectedValues.includes(opt) ? 'fa-check-square' : 'fa-square'}"></i>
                                    ${opt}
                                </div>
                            `).join('')}
                        </div>
                    `;
                    break;
            }

            // 증빙 자료 섹션
            let evidenceHtml = '';
            if (q.evidence_list && q.evidence_list.length > 0) {
                evidenceHtml = `
                    <div class="evidence-section">
                        <div class="evidence-title">
                            <i class="fas fa-paperclip"></i> 필요한 증빙 자료
                        </div>
                        <div class="evidence-list">
                            ${q.evidence_list.map(e => `<span class="evidence-item">${e}</span>`).join('')}
                        </div>
                        <button class="evidence-upload-btn" onclick="openUploadModal('${q.id}', ${JSON.stringify(q.evidence_list).replace(/"/g, '&quot;')})">
                            <i class="fas fa-upload"></i> 파일 업로드
                        </button>
                    </div>
                `;
            }

            div.innerHTML = `
                <div class="question-header">
                    <span class="question-number">${q.id}</span>
                    <span class="question-text">${q.text}</span>
                </div>
                ${q.help_text ? `<div class="question-help"><i class="fas fa-info-circle"></i> ${q.help_text}</div>` : ''}
                <div class="answer-section">
                    ${answerHtml}
                </div>
                ${evidenceHtml}
            `;

            return div;
        }

        // YES/NO 선택
        function selectYesNo(questionId, value, btn) {
            const buttons = btn.parentElement.querySelectorAll('.yes-no-btn');
            buttons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            updateAnswer(questionId, value);

            // 종속 질문 처리
            const question = questions.find(q => q.id === questionId);
            if (question && question.dependent_question_ids) {
                if (value === 'YES') {
                    // 종속 질문 표시
                    showDependentQuestions(question);
                } else {
                    // 종속 질문 숨기기
                    hideDependentQuestions(question);
                }
            }
        }

        // 종속 질문 표시
        function showDependentQuestions(parentQuestion) {
            const container = document.getElementById('questions-list');
            const parentEl = document.getElementById(`question-${parentQuestion.id}`);

            parentQuestion.dependent_question_ids.forEach(depId => {
                if (!document.getElementById(`question-${depId}`)) {
                    const depQ = questions.find(q => q.id === depId);
                    if (depQ) {
                        const depEl = createQuestionElement(depQ);
                        parentEl.after(depEl);
                    }
                }
            });
        }

        // 종속 질문 숨기기
        function hideDependentQuestions(parentQuestion) {
            parentQuestion.dependent_question_ids.forEach(depId => {
                const depEl = document.getElementById(`question-${depId}`);
                if (depEl) {
                    depEl.remove();
                    delete answers[depId];
                }
            });
        }

        // 옵션 선택 (라디오)
        function selectOption(questionId, value, el) {
            const items = el.parentElement.querySelectorAll('.radio-item');
            items.forEach(item => {
                item.classList.remove('selected');
                item.querySelector('i').className = 'fas fa-circle';
            });
            el.classList.add('selected');
            el.querySelector('i').className = 'fas fa-check-circle';
            updateAnswer(questionId, value);
        }

        // 체크박스 토글
        function toggleCheckbox(questionId, value, el) {
            el.classList.toggle('selected');
            const icon = el.querySelector('i');
            icon.className = el.classList.contains('selected') ? 'fas fa-check-square' : 'fas fa-square';

            // 현재 선택된 값들 수집
            const container = el.parentElement;
            const selectedValues = [];
            container.querySelectorAll('.checkbox-item.selected').forEach(item => {
                selectedValues.push(item.textContent.trim());
            });
            updateAnswer(questionId, selectedValues);
        }

        // 답변 업데이트
        function updateAnswer(questionId, value) {
            answers[questionId] = value;
            console.log(`Answer updated: ${questionId} = ${JSON.stringify(value)}`);
        }

        // 토스트 메시지 표시
        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast-message ${type}`;

            const icons = {
                success: 'fa-check-circle',
                error: 'fa-exclamation-circle',
                warning: 'fa-exclamation-triangle',
                info: 'fa-info-circle'
            };

            toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
            container.appendChild(toast);

            // 3초 후 자동 제거
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

        // 답변 저장
        async function saveAnswers() {
            {% if not is_logged_in %}
            showToast('로그인이 필요합니다.', 'warning');
            return false;
            {% endif %}

            try {
                for (const [questionId, value] of Object.entries(answers)) {
                    if (value !== undefined && value !== '' && value !== null) {
                        await fetch('/link11/api/answers', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                question_id: questionId,
                                value: value,
                                company_id: companyId,
                                year: currentYear
                            })
                        });
                    }
                }
                return true;
            } catch (error) {
                console.error('저장 오류:', error);
                return false;
            }
        }

        // 임시 저장
        async function saveDraft() {
            const success = await saveAnswers();
            if (success) {
                showToast('임시 저장되었습니다.', 'success');
                loadProgress();
            } else {
                showToast('저장 중 오류가 발생했습니다.', 'error');
            }
        }

        // 저장 후 다음 카테고리로 이동
        async function saveAndNext() {
            const success = await saveAnswers();
            if (success) {
                showToast('저장되었습니다.', 'success');
                loadProgress();
                goToNextCategory();
            } else {
                showToast('저장 중 오류가 발생했습니다.', 'error');
            }
        }

        // 다음 카테고리로 이동
        function goToNextCategory() {
            // 카테고리 순서 정의
            const categoryOrder = [
                '정보보호 투자 현황',
                '정보보호 인력 현황',
                '정보보호 관련 인증',
                '정보보호 관련 활동'
            ];

            if (!currentCategory) {
                showDashboard();
                return;
            }

            const currentIndex = categoryOrder.indexOf(currentCategory);

            if (currentIndex >= 0 && currentIndex < categoryOrder.length - 1) {
                // 다음 카테고리로 이동
                const nextCategory = categoryOrder[currentIndex + 1];
                showToast(`'${nextCategory}' 카테고리로 이동합니다.`, 'info');
                showCategory(nextCategory);
            } else {
                // 마지막 카테고리이면 대시보드로
                showToast('모든 카테고리를 완료했습니다!', 'success');
                showDashboard();
            }
        }

        // 대시보드 표시
        function showDashboard() {
            document.getElementById('dashboard-view').style.display = 'block';
            document.getElementById('questions-view').style.display = 'none';
            currentCategory = null;
            loadProgress();
        }

        // 업로드 모달 열기
        function openUploadModal(questionId, evidenceList) {
            document.getElementById('upload-question-id').value = questionId;

            const select = document.getElementById('upload-evidence-type');
            select.innerHTML = '<option value="">선택하세요</option>';
            evidenceList.forEach(e => {
                const option = document.createElement('option');
                option.value = e;
                option.textContent = e;
                select.appendChild(option);
            });

            const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
            modal.show();
        }

        // 파일 업로드
        async function uploadFile() {
            const form = document.getElementById('upload-form');
            const formData = new FormData(form);
            formData.append('company_id', companyId);
            formData.append('year', currentYear);

            try {
                const response = await fetch('/link11/api/evidence', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (data.success) {
                    showToast('파일이 업로드되었습니다.', 'success');
                    bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
                    form.reset();
                } else {
                    showToast('업로드 실패: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('업로드 오류:', error);
                showToast('업로드 중 오류가 발생했습니다.', 'error');
            }
        }

        // 보고서 생성
        async function generateReport() {
            try {
                const response = await fetch('/link11/api/report/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        company_id: companyId,
                        year: currentYear,
                        format: 'json'
                    })
                });

                const data = await response.json();
                if (data.success) {
                    // 보고서 데이터를 새 창에 표시하거나 다운로드
                    console.log('Report generated:', data.report);
                    showToast('보고서가 생성되었습니다.', 'success');
                } else {
                    showToast('보고서 생성 실패: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('보고서 생성 오류:', error);
                showToast('보고서 생성 중 오류가 발생했습니다.', 'error');
            }
        }
    </script>
</body>

</html>
