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

        .stat-icon.investment {
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        }

        .stat-icon.personnel {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .stat-icon.certification {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        .stat-icon.activity {
            background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        }

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

        .category-badge.complete {
            background: #d1fae5;
            color: #059669;
        }

        .category-badge.in-progress {
            background: #fef3c7;
            color: #d97706;
        }

        .category-badge.not-started {
            background: #f3f4f6;
            color: #6b7280;
        }

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
            background: #ffffff;
            border-left: 6px solid #2563eb;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .question-item.level-2 {
            margin-left: 30px;
            background: #f8fafc;
            border-left: 4px solid #64748b;
        }

        .question-item.level-3 {
            margin-left: 60px;
            background: #ffffff;
            border-left: 3px dashed #94a3b8;
            border-top: 1px solid #f1f5f9;
        }

        .question-item.level-4 {
            margin-left: 90px;
            background: #ffffff;
            border-left: 2px dotted #cbd5e1;
        }

        /* Group 유형 질문의 안내 문구 스타일 */
        .group-header {
            padding: 12px 15px;
            background: #eff6ff;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            font-weight: 600;
            color: #1e40af;
            margin-top: 10px;
            font-size: 0.95rem;
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

        .question-reset-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }

        .question-reset-btn:hover {
            background: #dc2626;
            transform: scale(1.05);
        }

        .question-reset-btn i {
            font-size: 0.75rem;
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

        .text-input,
        .date-input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        /* 숫자 입력 필드 (오른쪽 정렬) */
        .number-input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 1.05rem;
            font-weight: 500;
            text-align: right;
            font-family: 'Consolas', 'Monaco', monospace;
            transition: all 0.3s ease;
        }

        .number-input::placeholder {
            text-align: left;
            font-weight: normal;
            font-size: 1rem;
        }

        /* 금액 입력 필드 (오른쪽 정렬, 쉼표 표시) */
        .currency-input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            text-align: right;
            font-family: 'Consolas', 'Monaco', monospace;
            transition: all 0.3s ease;
        }

        .currency-input:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(var(--secondary-color-rgb), 0.1);
        }

        .currency-input::placeholder {
            text-align: left;
            font-weight: normal;
            font-size: 1rem;
        }

        .text-input:focus,
        .date-input:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(var(--secondary-color-rgb), 0.1);
        }

        .number-input:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(var(--secondary-color-rgb), 0.1);
        }

        .checkbox-group,
        .select-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .checkbox-item,
        .radio-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 15px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }

        .checkbox-item:hover,
        .radio-item:hover {
            border-color: var(--secondary-color);
        }

        /* 툴팁 스타일 */
        .checkbox-item[title]:hover::after,
        .radio-item[title]:hover::after {
            content: attr(title);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            margin-bottom: 8px;
            padding: 8px 12px;
            background: #1f2937;
            color: white;
            font-size: 0.85rem;
            border-radius: 6px;
            white-space: nowrap;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .checkbox-item[title]:hover::before,
        .radio-item[title]:hover::before {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            margin-bottom: 2px;
            border: 6px solid transparent;
            border-top-color: #1f2937;
            z-index: 1000;
        }

        .checkbox-item.selected,
        .radio-item.selected {
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
            0% {
                transform: rotate(0deg);
            }

            100% {
                transform: rotate(360deg);
            }
        }

        /* 알림 메시지 */
        .alert-custom {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .alert-success {
            background: #d1fae5;
            color: #059669;
            border: 1px solid #10b981;
        }

        .alert-warning {
            background: #fef3c7;
            color: #d97706;
            border: 1px solid #f59e0b;
        }

        .alert-error {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #ef4444;
        }

        /* 가로 배치를 위한 그리드 스타일 */
        .question-row-container {
            display: flex;
            gap: 15px;
            margin-left: 30px;
            /* level-2 들여쓰기 유지 */
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .question-grid-item {
            flex: 1;
            min-width: 250px;
            padding: 15px;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            background: #f8fafc;
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }

        .question-grid-item:hover {
            border-color: var(--secondary-color);
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .question-grid-item.level-2 {
            margin-left: 0 !important;
            /* 그리드 내부에서는 개별 들여쓰기 제거 */
            margin-bottom: 0 !important;
        }

        .question-grid-item .question-header {
            margin-bottom: 10px;
            align-items: center;
        }

        .question-grid-item .question-number {
            padding: 2px 8px;
            font-size: 0.75rem;
        }

        .question-grid-item .question-text {
            font-size: 0.95rem;
            font-weight: 600;
        }

        .question-grid-item .question-help {
            font-size: 0.8rem;
            padding: 8px;
            margin-bottom: 12px;
            flex-grow: 1;
            /* 도움말 영역을 늘려 입력창 위치 통일 */
            display: flex;
            align-items: center;
        }

        .question-grid-item .number-input,
        .question-grid-item .currency-input {
            font-size: 1rem;
            padding: 8px 12px;
        }

        /* 모바일 대응 */
        @media (max-width: 992px) {
            .question-row-container {
                flex-direction: column;
                margin-left: 15px;
            }

            .question-grid-item {
                min-width: 100%;
            }
        }
    </style>
</head>

<body>
    <!-- 네비게이션 -->
    {% include 'navi.jsp' %}

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
                    응답 완료: 0 / 29 질문
                </div>
            </div>

            <!-- 비율 요약 대시보드 -->
            <div class="dashboard-grid mb-5">
                <div class="stat-card">
                    <div class="stat-icon investment">
                        <i class="fas fa-hand-holding-usd"></i>
                    </div>
                    <div class="stat-value" id="dashboard-inv-ratio">0.00%</div>
                    <div class="stat-label">정보보호 투자 비율 (B/A)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon personnel">
                        <i class="fas fa-user-shield"></i>
                    </div>
                    <div class="stat-value" id="dashboard-per-ratio">0.00%</div>
                    <div class="stat-label">정보보호 인력 비율 ((D1+D2)/C)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon certification">
                        <i class="fas fa-medal"></i>
                    </div>
                    <div class="stat-value" id="dashboard-cert-count">0</div>
                    <div class="stat-label">보유 인증 건수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon activity">
                        <i class="fas fa-rocket"></i>
                    </div>
                    <div class="stat-value" id="dashboard-act-score">--</div>
                    <div class="stat-label">보안 활동 지수</div>
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
                {% if is_logged_in %}
                <button class="btn-secondary-custom" onclick="showLoadFromYearModal()">
                    <i class="fas fa-history"></i> 이전 자료 불러오기
                </button>
                <button class="btn-secondary-custom" onclick="confirmReset()" style="color: #dc3545;">
                    <i class="fas fa-redo"></i> 새로하기
                </button>
                {% endif %}
                <button class="btn-secondary-custom" onclick="location.href='/link11/evidence'">
                    <i class="fas fa-file-alt"></i> 증빙자료 관리
                </button>
                <button class="btn-secondary-custom" onclick="location.href='/link11/report'">
                    <i class="fas fa-file-export"></i> 공시자료 생성
                </button>
            </div>
        </div>

        <!-- 질문 응답 뷰 (카테고리 선택 시) -->
        <div id="questions-view" style="display: none;">
            <div class="mb-4">
                <button class="btn-secondary-custom" onclick="showDashboard()">
                    <i class="fas fa-arrow-left"></i> 공시 현황으로 돌아가기
                </button>
            </div>

            <div class="questions-section">
                <h3 class="mb-4" id="category-title">질문 목록</h3>
                <div id="questions-list">
                    <!-- JavaScript로 동적 생성 -->
                </div>
            </div>

            <div class="action-buttons">
                <button class="btn-secondary-custom" onclick="showDashboard()">
                    <i class="fas fa-th-large"></i> 공시 현황
                </button>
                <button class="btn-secondary-custom" onclick="saveDraft()">
                    <i class="fas fa-save"></i> 임시 저장
                </button>
                <button class="btn-secondary-custom" onclick="saveAndNext()">
                    <i class="fas fa-arrow-right"></i> 저장 후 다음
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

    <!-- 이전 자료 불러오기 모달 -->
    <div class="modal fade" id="loadFromYearModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-history"></i> 이전 자료 불러오기</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p class="text-muted mb-3">이전 연도의 답변을 현재 연도로 복사합니다. 현재 작성 중인 내용은 덮어씌워집니다.</p>
                    <div class="mb-3">
                        <label class="form-label">불러올 연도 선택</label>
                        <select class="form-select" id="source-year-select">
                            <option value="">연도를 선택하세요</option>
                        </select>
                        <div id="no-previous-data" class="text-muted mt-2" style="display: none;">
                            <i class="fas fa-info-circle"></i> 이전 연도 자료가 없습니다.
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-primary" onclick="loadFromYear()"
                        id="load-from-year-btn">불러오기</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 토스트 컨테이너 (Bootstrap) -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1100;">
        <div id="saveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-info-circle me-2 toast-icon"></i>
                <strong class="me-auto toast-title">알림</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
            </div>
        </div>
    </div>

    <!-- 스크립트 -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 질문 ID 상수 (백엔드 QID 클래스와 동기화)
        const QID = {
            // 1. 정보보호 투자 현황 (8개)
            INV_HAS_INVESTMENT: "Q1",    // 정보보호 투자 발생 여부
            INV_IT_AMOUNT: "Q2",         // 정보기술부문 투자액 A
            INV_SEC_GROUP: "Q3",         // 정보보호부문 투자액 B Group
            INV_SEC_DEPRECIATION: "Q4",  // 감가상각비
            INV_SEC_SERVICE: "Q5",       // 서비스비용
            INV_SEC_LABOR: "Q6",         // 인건비
            INV_FUTURE_PLAN: "Q7",       // 향후 투자 계획
            INV_FUTURE_AMOUNT: "Q8",     // 예정 투자액

            // 2. 정보보호 인력 현황 (6개)
            PER_HAS_TEAM: "Q9",          // 전담 부서/인력 여부
            PER_TOTAL_EMP: "Q10",        // 총 임직원 수
            PER_INTERNAL: "Q11",         // 내부 전담인력 수
            PER_EXTERNAL: "Q12",         // 외주 전담인력 수
            PER_HAS_CISO: "Q13",         // CISO/CPO 지정 여부
            PER_CISO_DETAIL: "Q14",      // CISO/CPO 상세 현황

            // 3. 정보보호 인증 (2개)
            CERT_HAS_CERT: "Q15",        // 인증 보유 여부
            CERT_DETAIL: "Q16",          // 인증 보유 현황

            // 4. 정보보호 활동 (10개)
            ACT_HAS_ACTIVITY: "Q17",     // 이용자 보호 활동 여부
            ACT_ASSET_MGMT: "Q18",       // IT 자산 관리
            ACT_TRAINING: "Q19",         // 교육/훈련 실적
            ACT_GUIDELINES: "Q20",       // 지침/절차서
            ACT_VULN_ANALYSIS: "Q21",    // 취약점 분석
            ACT_ZERO_TRUST: "Q22",       // 제로트러스트
            ACT_SBOM: "Q23",             // SBOM
            ACT_CTAS: "Q24",             // C-TAS
            ACT_MOCK_DRILL: "Q25",       // 모의훈련
            ACT_INSURANCE: "Q26"         // 배상책임보험
        };

        // 전역 변수
        let currentYear = new Date().getFullYear();
        let userId = {{ user_info.user_id if user_info else 0 }};
        let companyName = '{{ user_info.company_name if user_info else "default" }}';
        let questions = [];
        let answers = {};

        // 보안 솔루션 용어 툴팁 매핑
        const securityTerms = {
            '방화벽': 'Firewall - 네트워크 트래픽을 IP/포트 기반으로 차단하는 보안 장비',
            'IDS/IPS': 'Intrusion Detection/Prevention System - 침입 탐지/방지 시스템',
            'SIEM': 'Security Information and Event Management - 보안 정보 및 이벤트 관리',
            'DLP': 'Data Loss Prevention - 데이터 유출 방지',
            'EDR': 'Endpoint Detection and Response - 엔드포인트 탐지 및 대응',
            'WAF': 'Web Application Firewall - 웹 공격(SQL Injection, XSS 등)을 차단하는 특수 방화벽',
            'VPN': 'Virtual Private Network - 가상 사설망',
            'CISSP': 'Certified Information Systems Security Professional - 국제 공인 정보 시스템 보안 전문가',
            'CEH': 'Certified Ethical Hacker - 공인 윤리적 해커',
            'ISO27001': 'International Organization for Standardization 27001 - 국제 정보보안 관리체계 인증',
            'ISO27018': 'ISO 27018 - 클라우드 개인정보보호 인증',
            'SOC2': 'Service Organization Control 2 - 서비스 조직 통제 보고서',
            'CSAP': 'Cloud Security Assurance Program - 클라우드 보안 인증',
            'ISMS': 'Information Security Management System - 정보보안 관리체계'
        };
        let currentCategory = null;
        let allCategories = []; // 서버에서 받아온 전체 카테고리 목록 저장

        // 질문 표시 번호 계산 함수
        function getDisplayQuestionNumber(question) {
            // display_number 컬럼 사용 (없으면 ID로 fallback)
            return question.display_number || question.id;
        }

        // 카테고리 아이콘 매핑
        const categoryIcons = {
            '정보보호 투자 현황': { icon: 'fas fa-chart-line', color: '#3b82f6' },
            '정보보호 인력 현황': { icon: 'fas fa-users', color: '#10b981' },
            '정보보호 관련 인증': { icon: 'fas fa-certificate', color: '#f59e0b' },
            '정보보호 관련 활동': { icon: 'fas fa-tasks', color: '#8b5cf6' }
        };

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', async function () {
            await loadCategories();  // 카테고리 로드 완료 후
            await loadProgress();    // 진행률 로드
        });

        // 카테고리 목록 로드
        async function loadCategories() {
            try {
                const response = await fetch('/link11/api/categories');
                const data = await response.json();

                if (data.success) {
                    allCategories = data.categories; // 전역 변수에 저장
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
                card.dataset.categoryId = cat.id;  // ID 저장
                card.onclick = () => showCategory(cat.id, cat.name);

                // 카테고리 이름을 안전한 ID로 변환 (공백과 특수문자 제거)
                const safeId = cat.name.replace(/\s+/g, '-');

                card.innerHTML = `
                    <div class="category-header">
                        <div class="category-icon" style="background: ${iconInfo.color}">
                            <i class="${iconInfo.icon}"></i>
                        </div>
                        <h4 class="category-title">${cat.name}</h4>
                    </div>
                    <p class="text-muted mb-0">총 ${cat.total}개 질문 (1단계 ${cat.level1_count}개)</p>
                    <div class="category-progress">
                        <span class="category-stats">진행률: <span id="cat-progress-${safeId}">0%</span></span>
                        <span class="category-badge not-started" id="cat-badge-${safeId}">미시작</span>
                    </div>
                `;

                container.appendChild(card);
            });
        }

        // 진행률 로드
        async function loadProgress() {
            {% if is_logged_in %}
            try {
                console.log('[진행률 로드] 시작...', { userId, currentYear });
                const response = await fetch(`/link11/api/progress/${userId}/${currentYear}`);
                const data = await response.json();
                console.log('[진행률 로드] 응답 데이터:', data);

                if (data.success) {
                    updateProgressUI(data);
                    if (data.ratios) {
                        updateRatioDashboard(data.ratios);
                    }
                    console.log('[진행률 로드] UI 업데이트 완료');
                } else {
                    console.error('[진행률 로드] 실패:', data.message);
                }
            } catch (error) {
                console.error('[진행률 로드] 오류:', error);
            }
            {% else %}
            console.warn('[진행률 로드] 로그인 필요');
            {% endif %}
        }

        // 진행률 UI 업데이트
        function updateProgressUI(data) {
            console.log('[진행률 UI 업데이트] 시작', data);
            const progress = data.progress;
            const categories = data.categories;

            // 전체 진행률
            document.getElementById('overall-percentage').textContent = `${progress.completion_rate}%`;
            document.getElementById('overall-progress-bar').style.width = `${progress.completion_rate}%`;
            document.getElementById('progress-stats').textContent =
                `응답 완료: ${progress.answered_questions} / ${progress.total_questions} 질문`;

            // 보고서 생성 버튼 활성화 (버튼이 있는 경우에만)
            const reportBtn = document.getElementById('generate-report-btn');
            if (reportBtn && progress.completion_rate === 100) {
                reportBtn.disabled = false;
            }

            // 카테고리별 진행률
            console.log('[진행률 UI 업데이트] 카테고리 데이터:', categories);
            for (const [name, catData] of Object.entries(categories)) {
                // 카테고리 이름을 안전한 ID로 변환 (공백과 특수문자 제거)
                const safeId = name.replace(/\s+/g, '-');
                console.log(`[진행률 UI 업데이트] ${name} -> ${safeId}, rate: ${catData.rate}%`);

                const progressEl = document.getElementById(`cat-progress-${safeId}`);
                const badgeEl = document.getElementById(`cat-badge-${safeId}`);

                if (progressEl) {
                    console.log(`[진행률 UI 업데이트] ✓ progressEl 발견: cat-progress-${safeId}`);
                    progressEl.textContent = `${catData.rate}%`;
                } else {
                    console.warn(`[진행률 UI 업데이트] ✗ progressEl 없음: cat-progress-${safeId}`);
                }

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
        }

        // 비율 요약 업데이트
        function updateRatioDashboard(ratios) {
            const invRatio = document.getElementById('dashboard-inv-ratio');
            const perRatio = document.getElementById('dashboard-per-ratio');
            if (invRatio) {
                invRatio.textContent = ratios.investment_ratio.toFixed(2) + '%';
                invRatio.style.color = ratios.investment_ratio > 0 ? '#0284c7' : '#94a3b8';
            }
            if (perRatio) {
                perRatio.textContent = ratios.personnel_ratio.toFixed(2) + '%';
                perRatio.style.color = ratios.personnel_ratio > 0 ? '#059669' : '#94a3b8';
            }

            // 보안 활동 지수 업데이트
            const actScore = document.getElementById('dashboard-act-score');
            if (actScore && ratios.activity_score !== undefined) {
                actScore.textContent = ratios.activity_score;
                // 점수에 따라 색상 변경 (0~30: 회색, 31~70: 주황색, 71~100: 초록색)
                if (ratios.activity_score >= 70) actScore.style.color = '#10b981';
                else if (ratios.activity_score >= 30) actScore.style.color = '#f59e0b';
                else actScore.style.color = '#94a3b8';
            }
        }

        // 카테고리 질문 표시
        let currentCategoryId = null;
        const GRID_QUESTION_GROUPS = {
            'Q9': ['Q10', 'Q28', 'Q11', 'Q12'], // 인력 현황 (총임직원, IT인력, 내부, 외주)
            'Q3': ['Q4', 'Q5', 'Q6']           // 투자액 상세 (감가, 서비스, 인건비)
        };

        function isGridQuestion(qid) {
            return Object.values(GRID_QUESTION_GROUPS).flat().includes(qid);
        }

        async function showCategory(categoryId, categoryName) {
            currentCategory = categoryName;
            currentCategoryId = categoryId;
            document.getElementById('dashboard-view').style.display = 'none';
            document.getElementById('questions-view').style.display = 'block';
            document.getElementById('category-title').textContent = categoryName;

            try {
                // 질문 로드 (카테고리 ID로 요청)
                const qResponse = await fetch(`/link11/api/questions?category=${categoryId}`);
                const qData = await qResponse.json();

                if (qData.success) {
                    questions = qData.questions;

                    // 기존 답변 로드
                    {% if is_logged_in %}
                    const aResponse = await fetch(`/link11/api/answers/${userId}/${currentYear}`);
                    const aData = await aResponse.json();

                    if (aData.success) {
                        answers = {};
                        aData.answers.forEach(a => {
                            answers[a.question_id] = a.value;
                        });
                    }
                    {% endif %}

                    renderQuestions(questions);

                    // 금액 필드 초기 포맷팅 및 비율 계산
                    setTimeout(() => {
                        const itAmountInput = document.getElementById(`input-${QID.INV_IT_AMOUNT}`);
                        const secGroupInput = document.getElementById(`input-${QID.INV_SEC_GROUP}`);
                        if (itAmountInput && itAmountInput.value) formatCurrencyOnBlur(itAmountInput);
                        if (secGroupInput && secGroupInput.value) formatCurrencyOnBlur(secGroupInput);
                        calculateInvestmentRatio();
                    }, 100);
                }
            } catch (error) {
                console.error('질문 로드 오류:', error);
            }
        }

        // 질문 렌더링
        function renderQuestions(questions) {
            const container = document.getElementById('questions-list');
            container.innerHTML = '';

            // 1단계 질문부터 재귀적으로 렌더링
            const level1Questions = questions.filter(q => q.level === 1);
            level1Questions.forEach(q => {
                appendQuestionRecursive(container, q);
            });
        }

        function appendQuestionRecursive(container, q) {
            const isGrid = isGridQuestion(q.id);
            const questionEl = createQuestionElement(q);

            if (isGrid) {
                questionEl.classList.add('question-grid-item');
            }

            container.appendChild(questionEl);

            if (q.dependent_question_ids && isQuestionTriggered(q, answers[q.id])) {
                const groupChildren = GRID_QUESTION_GROUPS[q.id];

                if (groupChildren) {
                    // 가로 배치를 위한 컨테이너 생성
                    const rowContainer = document.createElement('div');
                    rowContainer.className = 'question-row-container';
                    container.appendChild(rowContainer);

                    q.dependent_question_ids.forEach(depId => {
                        const depQ = questions.find(dq => dq.id === depId);
                        if (depQ) {
                            if (groupChildren.includes(depId)) {
                                appendQuestionRecursive(rowContainer, depQ);
                            } else {
                                appendQuestionRecursive(container, depQ);
                            }
                        }
                    });
                } else {
                    q.dependent_question_ids.forEach(depId => {
                        const depQ = questions.find(dq => dq.id === depId);
                        if (depQ) {
                            appendQuestionRecursive(container, depQ);
                        }
                    });
                }
            }
        }

        // 질문 의존성 트리거 여부 확인
        function isQuestionTriggered(question, answerValue) {
            // Group 유형은 부모가 보이면 항상 하위 항목을 트리거함
            if (question.type === 'group') return true;

            if (answerValue === undefined || answerValue === null || answerValue === '') return false;

            if (question.type === 'yes_no') {
                return answerValue === 'YES' || answerValue === 'yes' || answerValue === 'Yes';
            }
            return false;
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

                case 'group':
                    if (q.id === QID.INV_SEC_GROUP) {
                        const sum = parseFloat(currentValue) || 0;
                        answerHtml = `
                            <div class="group-header" style="margin-bottom: 10px;">
                                <i class="fas fa-layer-group"></i> 정보보호 투자액(B) - 다음 3개 항목의 합계
                            </div>
                            <div id="investment-total-display" class="total-display" style="margin-bottom: 8px; padding: 12px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; color: #475569;">정보보호 투자액 합계(B):</span>
                                <span id="input-${QID.INV_SEC_GROUP}-display" style="font-size: 1.1em; font-weight: 700; color: #1e293b;">${formatCurrency(sum)}원</span>
                                <input type="hidden" id="input-${QID.INV_SEC_GROUP}" value="${sum}" data-raw-value="${sum}">
                            </div>
                            <div id="investment-ratio-display" class="ratio-display" style="padding: 12px; background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%); border-radius: 8px; border-left: 4px solid #0ea5e9;">
                                <i class="fas fa-calculator" style="color: #0ea5e9; margin-right: 8px;"></i>
                                <span style="color: #0369a1; font-weight: 600;">IT 예산 대비 정보보호 투자 비율: </span>
                                <span id="ratio-value" style="color: #0ea5e9; font-weight: 700; font-size: 1.1em;">--%</span>
                            </div>
                        `;
                    } else {
                        answerHtml = `
                            <div class="group-header">
                                <i class="fas fa-layer-group"></i> 아래 상세 항목을 입력해 주세요.
                            </div>
                        `;
                    }
                    break;

                case 'table':
                    const tableOptions = q.options ? (typeof q.options === 'string' ? JSON.parse(q.options) : q.options) : [];
                    let tableData = [];
                    try {
                        tableData = currentValue ? (typeof currentValue === 'string' ? JSON.parse(currentValue) : currentValue) : [{}];
                        if (!Array.isArray(tableData)) tableData = [{}];
                    } catch (e) { tableData = [{}]; }

                    let tableRowsHtml = tableData.map((row, idx) => `
                        <tr>
                            ${tableOptions.map(opt => `
                                <td>
                                    <input type="text" class="table-input" 
                                           data-row-idx="${idx}" data-col-name="${opt}"
                                           value="${row[opt] || ''}"
                                           oninput="handleTableInput('${q.id}', this)"
                                           style="width: 100%; border: none; padding: 5px; outline: none;">
                                </td>
                            `).join('')}
                            <td style="width: 40px; text-align: center;">
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteTableRow('${q.id}', ${idx})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('');

                    answerHtml = `
                        <div class="table-container" style="overflow-x: auto; background: white; border: 1px solid #e2e8f0; border-radius: 8px;">
                            <table class="table table-bordered mb-0" style="min-width: 600px;">
                                <thead class="table-light">
                                    <tr>
                                        ${tableOptions.map(opt => `<th>${opt}</th>`).join('')}
                                        <th style="width: 50px;">삭제</th>
                                    </tr>
                                </thead>
                                <tbody id="table-body-${q.id}">
                                    ${tableRowsHtml}
                                </tbody>
                            </table>
                            <div class="p-2 bg-light text-end">
                                <button class="btn btn-sm btn-primary" onclick="addTableRow('${q.id}')">
                                    <i class="fas fa-plus"></i> 행 추가
                                </button>
                            </div>
                        </div>
                    `;
                    break;

                case 'text':
                case 'textarea':
                    answerHtml = `
                        <textarea class="text-input" rows="3"
                                  placeholder="상세 내용을 입력하세요..."
                                  onchange="updateAnswer('${q.id}', this.value)">${currentValue}</textarea>
                    `;
                    break;

                case 'number':
                    if (q.text.includes('(원)')) {
                        // 금액 관련 필드 (천 단위 콤마 + 원 단위 표시)
                        const formattedVal = currentValue ? formatCurrency(currentValue) : '';
                        answerHtml = `
                            <div class="currency-input-wrapper" style="position: relative;">
                                <input type="text" class="currency-input" id="input-${q.id}"
                                       placeholder="금액을 입력하세요"
                                       value="${formattedVal}"
                                       data-raw-value="${currentValue}"
                                       oninput="handleCurrencyInput(this, '${q.id}')"
                                       onblur="formatCurrencyOnBlur(this)"
                                       style="padding-right: 40px;">
                                <span style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%); color: #64748b; font-weight: 600;">원</span>
                            </div>
                        `;
                    } else {
                        // 일반 숫자 (인원 수, 횟수 등)
                        // Q4-17 (사고 건수) 등은 일반 숫자 처리
                        answerHtml = `
                            <input type="number" class="number-input" id="input-${q.id}"
                                   placeholder="숫자를 입력하세요"
                                   value="${currentValue}"
                                   data-raw-value="${currentValue}"
                                   oninput="handleNumberInput(this, '${q.id}')">
                        `;
                    }
                    break;

                case 'rank_composition':
                    let rankOptions = [];
                    try {
                        rankOptions = q.options ? JSON.parse(q.options) : [];
                    } catch (e) {
                        rankOptions = ["임원급", "팀장급", "실무자"];
                    }

                    let currentComp = {};
                    try {
                        if (typeof currentValue === 'string' && currentValue.startsWith('{')) {
                            currentComp = JSON.parse(currentValue);
                        } else if (typeof currentValue === 'object' && currentValue !== null) {
                            currentComp = currentValue;
                        }
                    } catch (e) {
                        console.error('JSON parse error for composition:', e);
                        currentComp = {};
                    }

                    let fieldsHtml = rankOptions.map(opt => `
                        <div class="composition-field" style="display: flex; align-items: center; margin-bottom: 8px; gap: 10px;">
                            <span style="flex: 0 0 100px; font-weight: 500; color: #475569;">${opt}</span>
                            <div style="flex: 1; display: flex; align-items: center; gap: 8px;">
                                <input type="number" class="number-input rank-input-${q.id}" 
                                       data-rank-name="${opt}"
                                       value="${(currentComp[opt] !== undefined && currentComp[opt] !== null) ? currentComp[opt] : ''}" 
                                       oninput="handleCompositionInput('${q.id}')"
                                       placeholder="0"
                                       style="padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; width: 120px; text-align: right; background: white; font-weight: 600;">
                                <span class="text-muted">명</span>
                            </div>
                        </div>
                    `).join('');

                    const totalComp = Object.values(currentComp).reduce((a, b) => (Number(a) || 0) + (Number(b) || 0), 0);

                    answerHtml = `
                        <div class="composition-container" style="background: #f1f5f9; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                            <div style="margin-bottom: 15px; font-size: 0.9rem; color: #64748b; display: flex; align-items: center; gap: 6px;">
                                <i class="fas fa-info-circle"></i> 각 항목에 숫자를 입력하면 합계가 자동 계산됩니다.
                            </div>
                            ${fieldsHtml}
                            <div class="composition-total" style="margin-top: 20px; padding-top: 15px; border-top: 2px dashed #cbd5e1; display: flex; align-items: center; justify-content: flex-end; gap: 15px;">
                                <span style="font-weight: 700; color: #1e293b; font-size: 1.1rem;">총 인원 합계:</span>
                                <div style="display: flex; align-items: baseline; gap: 4px;">
                                    <span id="total-${q.id}" style="font-size: 1.8rem; font-weight: 800; color: #3b82f6;">${totalComp}</span>
                                    <span style="font-weight: 700; color: #1e293b; font-size: 1.1rem;">명</span>
                                </div>
                            </div>
                        </div>
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
                            ${checkOptions.map(opt => {
                        const tooltip = securityTerms[opt] ? `title="${securityTerms[opt]}"` : '';
                        return `
                                <div class="checkbox-item ${selectedValues.includes(opt) ? 'selected' : ''}"
                                     data-value="${opt}"
                                     onclick="toggleCheckbox('${q.id}', '${opt}', this)"
                                     ${tooltip}>
                                    <i class="fas ${selectedValues.includes(opt) ? 'fa-check-square' : 'fa-square'}"></i>
                                    ${opt}
                                </div>
                            `}).join('')}
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

            const displayNumber = getDisplayQuestionNumber(q);

            const isGrid = isGridQuestion(q.id);
            let formattedText = q.text;
            if (isGrid && formattedText.includes(' (')) {
                // 공백 + 괄호 형태(상세 설명)만 줄바꿈하고 스타일에 적용
                // (C), (D1) 처럼 공백 없이 붙은 기호는 제목으로 취급하여 한 줄 유지
                formattedText = formattedText.replace(' (', '<br><small class="text-muted" style="font-weight: normal; font-size: 0.8rem; margin-top: 4px; display: inline-block;">(');
            }

            let formattedHelpText = q.help_text || '';
            if (isGrid && formattedHelpText.includes('(')) {
                // 부모 괄호와 내용 삭제 (중복 방지)
                formattedHelpText = formattedHelpText.replace(/\s*\(.*?\)/g, '').trim();
            }

            div.innerHTML = `
                <div class="question-header" style="align-items: flex-start;">
                    <span class="question-number">${displayNumber}</span>
                    <span class="question-text">${formattedText}</span>
                    ${(q.type !== 'number' && !isGrid) ? `
                    <button class="question-reset-btn" onclick="resetQuestion('${q.id}'); event.stopPropagation();" title="이 질문 초기화">
                        <i class="fas fa-undo"></i> 초기화
                    </button>
                    ` : ''}
                </div>
                ${formattedHelpText ? `<div class="question-help"><i class="fas fa-info-circle"></i> ${formattedHelpText}</div>` : ''}
                <div class="answer-section">
                    ${answerHtml}
                </div>
                ${evidenceHtml}
            `;

            return div;
        }

        // YES/NO 선택
        // YES/NO 선택
        async function selectYesNo(questionId, value, btn) {
            const question = questions.find(q => q.id === questionId);

            if (value === 'NO' && question && question.dependent_question_ids) {
                // 재귀적으로 모든 하위 답변이 존재하는지 확인
                const hasAnswers = checkAnyDependentAnswers(question);

                if (hasAnswers) {
                    if (!confirm('상위 질문을 "아니오"로 변경하면 이미 작성된 모든 하위 데이터가 삭제됩니다. 계속하시겠습니까?')) {
                        return;
                    }
                    // 로컬 및 DB에서 재귀적 삭제 (API 호출 포함)
                    recursiveClearAnswers(question);
                }
            }

            const buttons = btn.parentElement.querySelectorAll('.yes-no-btn');
            buttons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            updateAnswer(questionId, value, true);

            if (question && question.dependent_question_ids) {
                if (value === 'YES') {
                    showDependentQuestions(question);
                } else {
                    hideDependentQuestions(question);
                }
            }
        }

        // 재귀적으로 하위 답변 존재 여부 확인
        function checkAnyDependentAnswers(parentQ) {
            if (!parentQ.dependent_question_ids) return false;
            for (const depId of parentQ.dependent_question_ids) {
                if (answers[depId] !== undefined && answers[depId] !== null && answers[depId] !== '') return true;
                const depQ = questions.find(q => q.id === depId);
                if (depQ && checkAnyDependentAnswers(depQ)) return true;
            }
            return false;
        }

        // 재귀적으로 하위 답변 데이터 삭제
        function recursiveClearAnswers(parentQ) {
            if (!parentQ.dependent_question_ids) return;
            parentQ.dependent_question_ids.forEach(depId => {
                delete answers[depId];
                // DB에서도 삭제되도록 (백엔드에서 이미 처리하지만 동기화를 위해)
                const depQ = questions.find(q => q.id === depId);
                if (depQ) recursiveClearAnswers(depQ);
            });
        }

        // 종속 질문 표시
        function showDependentQuestions(parentQuestion) {
            console.log(`[showDependentQuestions] 부모 질문: ${parentQuestion.id}, 종속 질문:`, parentQuestion.dependent_question_ids);
            
            const parentEl = document.getElementById(`question-${parentQuestion.id}`);
            if (!parentEl) {
                console.error(`[showDependentQuestions] 부모 요소를 찾을 수 없음: question-${parentQuestion.id}`);
                return;
            }

            // 종속 질문을 역순으로 처리하여 부모 바로 아래에 올바른 순서로 삽입
            const reversedIds = [...parentQuestion.dependent_question_ids].reverse();
            reversedIds.forEach(depId => {
                const existingEl = document.getElementById(`question-${depId}`);
                if (!existingEl) {
                    const depQ = questions.find(dq => dq.id === depId);
                    if (depQ) {
                        console.log(`[showDependentQuestions] 종속 질문 생성 중: ${depId}`);
                        const depEl = createQuestionElement(depQ);
                        
                        if (isGridQuestion(depId)) {
                            depEl.classList.add('question-grid-item');
                            // 가로 배치 컨테이너가 없으면 생성 (동축 표시 대응)
                            let rowContainer = parentEl.nextElementSibling;
                            if (!rowContainer || !rowContainer.classList.contains('question-row-container')) {
                                rowContainer = document.createElement('div');
                                rowContainer.className = 'question-row-container';
                                parentEl.after(rowContainer);
                            }
                            rowContainer.prepend(depEl);
                        } else {
                            parentEl.after(depEl);
                        }

                        // DOM 삽입 확인
                        setTimeout(() => {
                            const inserted = document.getElementById(`question-${depId}`);
                            if (inserted) {
                                console.log(`[showDependentQuestions] ✓ 종속 질문 DOM 삽입 성공: ${depId}`);
                            } else {
                                console.error(`[showDependentQuestions] ✗ 종속 질문 DOM 삽입 실패: ${depId}`);
                            }
                        }, 100);

                        // 하위의 하위 질문도 트리거 여부 확인하여 표시 (재귀)
                        if (depQ.dependent_question_ids && isQuestionTriggered(depQ, answers[depId])) {
                            showDependentQuestions(depQ);
                        }
                    } else {
                        console.error(`[showDependentQuestions] 종속 질문을 찾을 수 없음: ${depId}`);
                    }
                } else {
                    console.log(`[showDependentQuestions] 종속 질문이 이미 존재함: ${depId}`);
                }
            });
        }

        // 종속 질문 숨기기
        function hideDependentQuestions(parentQuestion) {
            parentQuestion.dependent_question_ids.forEach(depId => {
                const depEl = document.getElementById(`question-${depId}`);
                if (depEl) {
                    // 재귀적으로 하위의 하위 질문들도 삭제
                    const depQ = questions.find(q => q.id === depId);
                    if (depQ && depQ.dependent_question_ids) {
                        hideDependentQuestions(depQ);
                    }
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

            // 옵션 선택은 즉시 저장
            updateAnswer(questionId, value, true);
        }

        // 체크박스 토글
        function toggleCheckbox(questionId, value, el) {
            console.log(`[toggleCheckbox] 질문: ${questionId}, 값: ${value}, 이전 상태:`, el.classList.contains('selected'));
            
            el.classList.toggle('selected');
            const icon = el.querySelector('i');
            icon.className = el.classList.contains('selected') ? 'fas fa-check-square' : 'fas fa-square';

            console.log(`[toggleCheckbox] 새 상태:`, el.classList.contains('selected'));

            // 현재 선택된 값들 수집
            const container = el.parentElement;
            const selectedValues = [];
            container.querySelectorAll('.checkbox-item.selected').forEach(item => {
                const val = item.getAttribute('data-value') || item.textContent.trim();
                selectedValues.push(val);
            });
            
            console.log(`[toggleCheckbox] 선택된 값들:`, selectedValues);
            updateAnswer(questionId, selectedValues);
        }

        let autoSaveTimer;
        // 답변 업데이트 (immediate가 true이면 즉시 DB 저장, 아니면 디바운스 적용)
        function updateAnswer(questionId, value, immediate = false) {
            answers[questionId] = value;

            if (immediate) {
                saveOneAnswer(questionId, value);
            } else {
                // 입력 중에는 1초 후 자동 저장
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    saveOneAnswer(questionId, value);
                }, 1000);
            }
        }

        // 개별 답변 DB 저장 및 진행률 갱신
        async function saveOneAnswer(questionId, value) {
            try {
                const response = await fetch('/link11/api/answers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        question_id: questionId,
                        value: value,
                        year: currentYear
                    })
                });

                const data = await response.json();
                if (data.success) {
                    loadProgress();
                } else if (data.message && data.message.includes('초과')) {
                    showToast(data.message, 'error');
                    // 입력값 원래대로 또는 강조? 
                }
            } catch (error) {
                console.error('실시간 저장 오류:', error);
            }
        }

        // 금액 포맷팅 (천 단위 쉼표)
        function formatCurrency(value) {
            if (!value && value !== 0) return '';
            const num = String(value).replace(/[^\d]/g, '');
            if (!num) return '';
            return parseInt(num, 10).toLocaleString('ko-KR');
        }

        // 금액 입력 처리
        function handleCurrencyInput(input, questionId) {
            // 숫자만 추출
            const rawValue = input.value.replace(/[^\d]/g, '');
            input.dataset.rawValue = rawValue;

            // 답변 업데이트
            updateAnswer(questionId, rawValue);

            // 비율 계산
            calculateInvestmentRatio();
        }

        // blur 시 포맷팅 적용
        function formatCurrencyOnBlur(input) {
            const rawValue = input.dataset.rawValue || input.value.replace(/[^\d]/g, '');
            if (rawValue) {
                input.value = formatCurrency(rawValue);
            }
        }

        // 구성 입력 처리 (Q2-4 등)
        function handleCompositionInput(questionId) {
            const inputs = document.querySelectorAll(`.rank-input-${questionId}`);
            let composition = {};
            let total = 0;

            inputs.forEach(input => {
                const val = parseInt(input.value) || 0;
                const name = input.dataset.rankName;
                composition[name] = val;
                total += val;
            });

            // 합계 표시 업데이트
            const totalEl = document.getElementById(`total-${questionId}`);
            if (totalEl) totalEl.textContent = total;

            // JSON 문자열로 저장
            updateAnswer(questionId, JSON.stringify(composition));
        }

        // 숫자 입력 처리
        function formatNumber(value) {
            if (!value && value !== 0) return '';
            const num = String(value).replace(/[^\d.]/g, '');
            if (!num) return '';

            // 소수점 처리
            const parts = num.split('.');
            parts[0] = parseInt(parts[0], 10).toLocaleString('ko-KR');

            return parts.length > 1 ? parts.join('.') : parts[0];
        }

        // 숫자 입력 처리
        function handleNumberInput(input, questionId) {
            // 숫자와 소수점만 추출
            let rawValue = input.value.replace(/[^\d.]/g, '');

            // 소수점이 여러 개 있으면 첫 번째만 유지
            const parts = rawValue.split('.');
            if (parts.length > 2) {
                rawValue = parts[0] + '.' + parts.slice(1).join('');
            }

            input.dataset.rawValue = rawValue;

            // 답변 업데이트 (raw value 사용)
            updateAnswer(questionId, rawValue);

            // 인력 관련 질문인 경우 검증
            const personnelRelatedItems = [QID.PER_TOTAL_EMP, QID.PER_INTERNAL, QID.PER_EXTERNAL];
            if (personnelRelatedItems.includes(questionId)) {
                calculatePersonnelValidation();
            }

            // 정보보호 투자액 하위 항목인 경우 상위 합계 계산 및 검증
            const securitySubItems = [QID.INV_SEC_DEPRECIATION, QID.INV_SEC_SERVICE, QID.INV_SEC_LABOR];
            if (securitySubItems.includes(questionId)) {
                calculateSecurityInvestmentSum();
            }
        }

        // blur 시 숫자 포맷팅 적용
        function formatNumberOnBlur(input) {
            const rawValue = input.dataset.rawValue || input.value.replace(/[^\d.]/g, '');
            if (rawValue) {
                input.value = formatNumber(rawValue);
            }
        }

        // 통화 입력 처리 (콤마 추가)
        function handleCurrencyInput(input, questionId) {
            let rawValue = input.value.replace(/[^\d]/g, '');
            input.dataset.rawValue = rawValue;

            // 답변 업데이트
            updateAnswer(questionId, rawValue);

            // 정보보호 투자액 하위 항목인 경우 상위 합계 계산
            const securitySubItems = [QID.INV_SEC_DEPRECIATION, QID.INV_SEC_SERVICE, QID.INV_SEC_LABOR];
            if (securitySubItems.includes(questionId)) {
                calculateSecurityInvestmentSum();
            }

            // 투자 비율 계산
            const investmentRelatedItems = [QID.INV_IT_AMOUNT, QID.INV_SEC_GROUP, ...securitySubItems];
            if (investmentRelatedItems.includes(questionId)) {
                calculateInvestmentRatio();
            }
        }

        function formatCurrencyOnBlur(input) {
            if (input.dataset.rawValue) {
                input.value = formatCurrency(input.dataset.rawValue);
            }
        }

        // 정보보호 투자액 합계 자동 계산 (Group = 감가상각비 + 서비스비용 + 인건비)
        function calculateSecurityInvestmentSum() {
            const v1 = parseFloat(document.getElementById(`input-${QID.INV_SEC_DEPRECIATION}`)?.dataset.rawValue || 0) || 0;
            const v2 = parseFloat(document.getElementById(`input-${QID.INV_SEC_SERVICE}`)?.dataset.rawValue || 0) || 0;
            const v3 = parseFloat(document.getElementById(`input-${QID.INV_SEC_LABOR}`)?.dataset.rawValue || 0) || 0;

            const sum = v1 + v2 + v3;

            // 정보기술부문 투자액(A) 가져오기
            const totalItInput = document.getElementById(`input-${QID.INV_IT_AMOUNT}`);
            const totalIt = parseFloat(totalItInput?.dataset.rawValue || 0) || 0;

            // 검증: 정보보호 투자액(B)이 정보기술 투자액(A)보다 클 수 없음
            if (sum > totalIt && totalIt > 0) {
                console.error(`[투자액 검증 실패] 정보보호 투자액(${sum.toLocaleString()})이 정보기술 투자액(${totalIt.toLocaleString()})을 초과했습니다.`);
                
                // 경고 메시지 표시
                alert(`⚠️ 투자액 오류\n\n정보보호 투자액(B): ${sum.toLocaleString()}원\n정보기술 투자액(A): ${totalIt.toLocaleString()}원\n\n정보보호 투자액은 정보기술 투자액을 초과할 수 없습니다.\n입력한 금액을 다시 확인해주세요.`);
                
                // 입력 필드 강조 표시
                [QID.INV_SEC_DEPRECIATION, QID.INV_SEC_SERVICE, QID.INV_SEC_LABOR].forEach(qid => {
                    const input = document.getElementById(`input-${qid}`);
                    if (input) {
                        input.style.borderColor = '#ef4444';
                        input.style.backgroundColor = '#fef2f2';
                    }
                });
                
                if (totalItInput) {
                    totalItInput.style.borderColor = '#ef4444';
                    totalItInput.style.backgroundColor = '#fef2f2';
                }
                
                // 에러 토스트 표시
                showToast('정보보호 투자액이 정보기술 투자액을 초과했습니다.', 'error');
                
                return; // 저장하지 않음
            } else {
                // 정상인 경우 강조 표시 제거
                [QID.INV_SEC_DEPRECIATION, QID.INV_SEC_SERVICE, QID.INV_SEC_LABOR].forEach(qid => {
                    const input = document.getElementById(`input-${qid}`);
                    if (input) {
                        input.style.borderColor = '';
                        input.style.backgroundColor = '';
                    }
                });
                
                if (totalItInput) {
                    totalItInput.style.borderColor = '';
                    totalItInput.style.backgroundColor = '';
                }
            }

            // 로컬 상태 업데이트
            answers[QID.INV_SEC_GROUP] = sum;

            // DB 저장 (Group 타입이라도 통계 및 보고서용으로 값이 필요함)
            saveOneAnswer(QID.INV_SEC_GROUP, sum);

            // 화면에 입력칸 또는 디스플레이가 있으면 업데이트
            const secGroupInput = document.getElementById(`input-${QID.INV_SEC_GROUP}`);
            const secGroupDisplay = document.getElementById(`input-${QID.INV_SEC_GROUP}-display`);
            
            if (secGroupInput) {
                secGroupInput.value = sum;
                secGroupInput.dataset.rawValue = sum;
            }
            if (secGroupDisplay) {
                secGroupDisplay.innerText = formatCurrency(sum) + '원';
            }

            // 비율 다시 계산
            calculateInvestmentRatio();
        }

        // 정보보호 투자 비율 자동 계산
        function calculateInvestmentRatio() {
            const totalItInput = document.getElementById(`input-${QID.INV_IT_AMOUNT}`);
            const ratioDisplay = document.getElementById('ratio-value');

            if (!totalItInput || !ratioDisplay) return;

            const totalIt = parseFloat((totalItInput.dataset.rawValue || totalItInput.value || '0').toString().replace(/[^\d.]/g, '')) || 0;

            // 정보보호 투자액 Group 입력 필드를 찾거나, 없으면 로컬 데이터 또는 하위 항목 합계 사용
            const secGroupInput = document.getElementById(`input-${QID.INV_SEC_GROUP}`);
            let security = 0;
            if (secGroupInput) {
                security = parseFloat((secGroupInput.dataset.rawValue || secGroupInput.value || '0').toString().replace(/[^\d.]/g, '')) || 0;
            } else {
                // 하위 항목 실시간 합산
                const v1 = parseFloat(document.getElementById(`input-${QID.INV_SEC_DEPRECIATION}`)?.dataset.rawValue || 0) || 0;
                const v2 = parseFloat(document.getElementById(`input-${QID.INV_SEC_SERVICE}`)?.dataset.rawValue || 0) || 0;
                const v3 = parseFloat(document.getElementById(`input-${QID.INV_SEC_LABOR}`)?.dataset.rawValue || 0) || 0;
                security = v1 + v2 + v3;
                if (security === 0 && answers[QID.INV_SEC_GROUP]) security = parseFloat(answers[QID.INV_SEC_GROUP]) || 0;
            }

            if (totalIt > 0) {
                const ratio = (security / totalIt) * 100;
                ratioDisplay.textContent = ratio.toFixed(2) + '%';

                // 유효성 체크 색상 변경 (B > A 인 경우 경고)
                if (security > totalIt) {
                    ratioDisplay.style.color = '#ef4444';
                    totalItInput.style.borderColor = '#ef4444';
                } else {
                    ratioDisplay.style.color = '#2563eb';
                    totalItInput.style.borderColor = '';
                }
            } else {
                ratioDisplay.textContent = '0.00%';
                ratioDisplay.style.color = '#94a3b8';
            }
        }

        // 정보보호 인력 검증 (내부+외주 <= 총 임직원)
        function calculatePersonnelValidation() {
            const totalEmpInput = document.getElementById(`input-${QID.PER_TOTAL_EMP}`);
            const internalInput = document.getElementById(`input-${QID.PER_INTERNAL}`);
            const externalInput = document.getElementById(`input-${QID.PER_EXTERNAL}`);

            if (!totalEmpInput) return;

            const totalEmp = parseFloat(totalEmpInput.dataset.rawValue || totalEmpInput.value || '0') || 0;
            const internal = parseFloat(internalInput?.dataset.rawValue || internalInput?.value || '0') || 0;
            const external = parseFloat(externalInput?.dataset.rawValue || externalInput?.value || '0') || 0;

            const securityPersonnel = internal + external;

            // 검증: 정보보호 인력(내부+외주)이 총 임직원 수보다 클 수 없음
            if (securityPersonnel > totalEmp && totalEmp > 0) {
                console.error(`[인력 검증 실패] 정보보호 인력(${securityPersonnel})이 총 임직원 수(${totalEmp})를 초과했습니다.`);
                
                // 경고 메시지 표시
                alert(`⚠️ 인력 수 오류\n\n정보보호 인력(내부+외주): ${securityPersonnel}명\n총 임직원 수: ${totalEmp}명\n\n정보보호 인력은 총 임직원 수를 초과할 수 없습니다.\n입력한 인원을 다시 확인해주세요.`);
                
                // 입력 필드 강조 표시
                if (internalInput) {
                    internalInput.style.borderColor = '#ef4444';
                    internalInput.style.backgroundColor = '#fef2f2';
                }
                if (externalInput) {
                    externalInput.style.borderColor = '#ef4444';
                    externalInput.style.backgroundColor = '#fef2f2';
                }
                if (totalEmpInput) {
                    totalEmpInput.style.borderColor = '#ef4444';
                    totalEmpInput.style.backgroundColor = '#fef2f2';
                }
                
                // 에러 토스트 표시
                showToast('정보보호 인력이 총 임직원 수를 초과했습니다.', 'error');
                
                return; // 저장하지 않음
            } else {
                // 정상인 경우 강조 표시 제거
                if (internalInput) {
                    internalInput.style.borderColor = '';
                    internalInput.style.backgroundColor = '';
                }
                if (externalInput) {
                    externalInput.style.borderColor = '';
                    externalInput.style.backgroundColor = '';
                }
                if (totalEmpInput) {
                    totalEmpInput.style.borderColor = '';
                    totalEmpInput.style.backgroundColor = '';
                }
            }
        }

        // 테이블 입력 처리
        function handleTableInput(questionId, input) {
            const idx = parseInt(input.dataset.rowIdx);
            const col = input.dataset.colName;

            if (!answers[questionId] || !Array.isArray(answers[questionId])) {
                answers[questionId] = [{}];
            }

            if (!answers[questionId][idx]) answers[questionId][idx] = {};
            answers[questionId][idx][col] = input.value;

            updateAnswer(questionId, answers[questionId]);
        }

        function addTableRow(questionId) {
            if (!answers[questionId] || !Array.isArray(answers[questionId])) {
                answers[questionId] = [];
            }
            answers[questionId].push({});
            // UI 갱신을 위해 해당 질문만 다시 렌더링하거나 전체 렌더링
            const q = questions.find(item => item.id === questionId);
            if (q) {
                const oldEl = document.getElementById(`question-${questionId}`);
                if (oldEl) {
                    const newEl = createQuestionElement(q);
                    oldEl.replaceWith(newEl);
                }
            }
        }

        function deleteTableRow(questionId, idx) {
            if (answers[questionId] && Array.isArray(answers[questionId])) {
                answers[questionId].splice(idx, 1);
                if (answers[questionId].length === 0) answers[questionId] = [{}];
                updateAnswer(questionId, answers[questionId]);

                const q = questions.find(item => item.id === questionId);
                if (q) {
                    const oldEl = document.getElementById(`question-${questionId}`);
                    if (oldEl) {
                        const newEl = createQuestionElement(q);
                        oldEl.replaceWith(newEl);
                    }
                }
            }
        }

        // 토스트 메시지 표시 (Bootstrap 방식)
        function showToast(message, type = 'info') {
            const toastEl = document.getElementById('saveToast');
            const toastBody = toastEl.querySelector('.toast-body');
            const toastHeader = toastEl.querySelector('.toast-header');
            const toastIcon = toastEl.querySelector('.toast-icon');
            const toastTitle = toastEl.querySelector('.toast-title');

            // 메시지 설정
            toastBody.textContent = message;

            // 타입에 따른 스타일 및 아이콘 설정
            toastHeader.className = 'toast-header';
            toastIcon.className = 'me-2 toast-icon';

            if (type === 'success') {
                toastHeader.classList.add('bg-success', 'text-white');
                toastIcon.classList.add('fas', 'fa-check-circle');
                toastTitle.textContent = '성공';
            } else if (type === 'error') {
                toastHeader.classList.add('bg-danger', 'text-white');
                toastIcon.classList.add('fas', 'fa-exclamation-circle');
                toastTitle.textContent = '오류';
            } else if (type === 'warning') {
                toastHeader.classList.add('bg-warning');
                toastIcon.classList.add('fas', 'fa-exclamation-triangle');
                toastTitle.textContent = '경고';
            } else {
                toastHeader.classList.add('bg-info', 'text-white');
                toastIcon.classList.add('fas', 'fa-info-circle');
                toastTitle.textContent = '알림';
            }

            // 토스트 표시
            const toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 3000
            });
            toast.show();
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
            showToast('저장 중입니다...', 'info');
            const success = await saveAnswers();
            if (success) {
                showToast('임시 저장되었습니다.', 'success');
                loadProgress();
            } else {
                showToast('저장 중 오류가 발생했습니다.', 'error');
            }
        }

        // 특정 질문 초기화
        async function resetQuestion(questionId) {
            if (!confirm('이 질문의 답변을 초기화하시겠습니까?')) {
                return;
            }

            {% if not is_logged_in %}
            showToast('로그인이 필요합니다.', 'warning');
            return;
            {% endif %}

            try {
                // 답변 삭제 API 호출
                const response = await fetch(`/link11/api/answers/${questionId}`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        year: currentYear
                    })
                });

                const data = await response.json();

                if (data.success) {
                    // 로컬 answers 객체에서 제거
                    delete answers[questionId];

                    // 화면 새로고침하여 초기 상태로 되돌림
                    const question = questions.find(q => q.id === questionId);
                    if (question) {
                        // 현재 카테고리 다시 로드
                        if (currentCategoryId && currentCategory) {
                            await showCategory(currentCategoryId, currentCategory);
                        }
                    }

                    showToast('답변이 초기화되었습니다.', 'success');
                    loadProgress();
                } else {
                    showToast('초기화 중 오류가 발생했습니다.', 'error');
                }
            } catch (error) {
                console.error('질문 초기화 오류:', error);
                showToast('초기화 중 오류가 발생했습니다.', 'error');
            }
        }

        // 저장 후 다음 카테고리를 이동
        async function saveAndNext() {
            showToast('저장 중입니다...', 'info');
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
            if (!currentCategoryId || allCategories.length === 0) {
                showDashboard();
                return;
            }

            const currentIndex = allCategories.findIndex(c => c.id === currentCategoryId);

            if (currentIndex >= 0 && currentIndex < allCategories.length - 1) {
                // 다음 카테고리로 이동
                const nextCategory = allCategories[currentIndex + 1];
                showToast(`'${nextCategory.name}' 카테고리로 이동합니다.`, 'info');
                showCategory(nextCategory.id, nextCategory.name);
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
            currentCategoryId = null;
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
                        company_id: companyName,
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

        // 새로하기 확인
        function confirmReset() {
            if (confirm(`${currentYear}년 데이터를 모두 삭제하고 새로 시작하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) {
                resetDisclosure();
            }
        }

        // 데이터 초기화
        async function resetDisclosure() {
            try {
                const response = await fetch('/link11/api/reset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        year: currentYear
                    })
                });

                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    // 페이지 새로고침
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('초기화 실패: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('초기화 오류:', error);
                showToast('초기화 중 오류가 발생했습니다.', 'error');
            }
        }

        // 이전 자료 불러오기 모달 표시
        async function showLoadFromYearModal() {
            const select = document.getElementById('source-year-select');
            const noDataMsg = document.getElementById('no-previous-data');
            const loadBtn = document.getElementById('load-from-year-btn');

            // 초기화
            select.innerHTML = '<option value="">연도를 선택하세요</option>';
            noDataMsg.style.display = 'none';
            loadBtn.disabled = false;

            try {
                const response = await fetch(`/link11/api/available-years/${userId}`);
                const data = await response.json();

                if (data.success && data.years.length > 0) {
                    data.years.forEach(y => {
                        const option = document.createElement('option');
                        option.value = y.year;
                        option.textContent = `${y.year}년 (${y.answer_count}개 답변)`;
                        select.appendChild(option);
                    });
                } else {
                    noDataMsg.style.display = 'block';
                    loadBtn.disabled = true;
                }

                const modal = new bootstrap.Modal(document.getElementById('loadFromYearModal'));
                modal.show();
            } catch (error) {
                console.error('연도 목록 조회 오류:', error);
                showToast('연도 목록을 불러오는 중 오류가 발생했습니다.', 'error');
            }
        }

        // 이전 자료 불러오기 실행
        async function loadFromYear() {
            const sourceYear = document.getElementById('source-year-select').value;

            if (!sourceYear) {
                showToast('연도를 선택해주세요.', 'warning');
                return;
            }

            if (!confirm(`${sourceYear}년 자료를 ${currentYear}년으로 복사하시겠습니까?\n\n현재 ${currentYear}년에 작성된 내용은 모두 덮어씌워집니다.`)) {
                return;
            }

            try {
                const response = await fetch('/link11/api/copy-from-year', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_year: parseInt(sourceYear),
                        target_year: currentYear
                    })
                });

                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    bootstrap.Modal.getInstance(document.getElementById('loadFromYearModal')).hide();
                    // 페이지 새로고침
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('복사 실패: ' + data.message, 'error');
                }
            } catch (error) {
                console.error('자료 복사 오류:', error);
                showToast('자료 복사 중 오류가 발생했습니다.', 'error');
            }
        }
    </script>
</body>

</html>