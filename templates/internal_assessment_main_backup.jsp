<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>내부평가 - SnowBall</title>
{% from 'internal_assessment_main_card.jsp' import render_rcm_card %}
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .assessment-card {
            border: 1px solid #e9ecef;
            border-radius: 12px;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
        }
        .assessment-card:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .progress-ring {
            width: 80px;
            height: 80px;
        }
        .progress-ring-bg {
            fill: transparent;
            stroke: #e9ecef;
            stroke-width: 8;
        }
        .progress-ring-fill {
            fill: transparent;
            stroke: #28a745;
            stroke-width: 8;
            stroke-linecap: round;
            transition: stroke-dasharray 0.5s ease-in-out;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }
        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
            position: relative;
        }
        .step-item {
            flex: 1;
            text-align: center;
            position: relative;
        }
        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            font-weight: bold;
            position: relative;
            z-index: 2;
        }
        .step-item.completed .step-number {
            background-color: #28a745;
            color: white;
            box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.2);
        }
        .step-item.in-progress .step-number {
            background-color: #007bff;
            color: white;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.2);
        }
        .step-item.pending .step-number {
            background-color: #e9ecef;
            color: #6c757d;
            border: 2px solid #adb5bd;
        }
        .step-connector {
            position: absolute;
            top: 20px;
            left: 50%;
            right: -50%;
            height: 2px;
            background-color: #dee2e6;
            z-index: 1;
        }
        .step-item:last-child .step-connector {
            display: none;
        }
        .step-item.completed .step-connector {
            background-color: #28a745;
        }
        /* 버튼 높이 및 스타일 통일 */
        .d-grid .btn {
            min-height: 42px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border-radius: 0.375rem !important;
        }
        /* 모달 body 여백 제거 */
        #assessmentDetailContent {
            padding: 0 1rem !important;
        }
        /* 모달 header 하단 여백 및 border 제거 */
        #assessmentDetailModal .modal-header {
            padding-bottom: 0.75rem !important;
            margin-bottom: 0 !important;
            border-bottom: none !important;
        }
        /* 모달 footer 여백 줄이기 */
        #assessmentDetailModal .modal-footer {
            padding: 0.5rem 1rem !important;
        }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="mb-4">
                    <h1><i class="fas fa-tasks me-2 text-primary"></i>내부평가</h1>
                </div>
                <p class="text-muted mb-4">
                    RCM의 단계별 내부평가를 진행하여 통제 설계와 운영 효과성을 체계적으로 검토할 수 있습니다.
                </p>
            </div>
        </div>

        <!-- 내부평가 진행 현황 - 회사별/카테고리별 -->
        {% if companies %}
            {% for company in companies %}
            <div class="mb-5">
                <!-- 회사명 헤더 -->
                <div class="d-flex align-items-center mb-3 pb-2 border-bottom border-primary">
                    <h3 class="mb-0"><i class="fas fa-building me-2 text-primary"></i>{{ company.company_name }}</h3>
                </div>

                <!-- 3개 섹션을 가로로 배치 -->
                <div class="row">
                    <!-- ITGC 섹션 (1/3) -->
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 border-info" style="border-width: 2px;">
                            <div class="card-header bg-info text-white py-2">
                                <h6 class="mb-0"><i class="fas fa-server me-2"></i>IT 일반 통제 (ITGC)</h6>
                            </div>
                            <div class="card-body p-3">
                                {% if company.categories.ITGC %}
                                    {% set item = company.categories.ITGC[0] %}
                                    <div class="assessment-card border-0">
                                        <div class="p-2">
                                    <!-- RCM 기본 정보 -->
                                    <div class="d-flex justify-content-between align-items-start mb-3">
                                        <div style="flex: 1;">
                                            <h5 class="card-title mb-1">{{ item.rcm_info.rcm_name }}</h5>
                                            <small class="text-muted d-block">
                                                <i class="fas fa-clipboard-list me-1"></i>세션: {{ item.evaluation_session }}
                                        {% if item.evaluation_status == 'COMPLETED' and item.operation_status == 'COMPLETED' %}
                                        <span class="badge bg-success ms-1">완료</span>
                                        {% elif item.evaluation_status == 'IN_PROGRESS' or item.operation_status == 'IN_PROGRESS' %}
                                        <span class="badge bg-primary ms-1">진행중</span>
                                        {% else %}
                                        <span class="badge bg-secondary ms-1">대기</span>
                                        {% endif %}
                                    </small>

                                    <!-- 카테고리별 현황 -->
                                    {% if item.progress.steps and item.progress.steps[0].details and item.progress.steps[0].details.category_stats %}
                                    <div class="mt-2">
                                        <small class="text-muted d-block mb-1"><strong>통제 구분:</strong></small>
                                        <div class="d-flex flex-wrap gap-1">
                                            {% for category, count in item.progress.steps[0].details.category_stats.items() %}
                                            <span class="badge
                                                {% if category == 'ITGC' %}bg-info
                                                {% elif category == 'ELC' %}bg-warning text-dark
                                                {% elif category == 'TLC' %}bg-success
                                                {% else %}bg-secondary{% endif %}" style="font-size: 0.7rem;">
                                                {% if category == 'ITGC' %}<i class="fas fa-server"></i> ITGC
                                                {% elif category == 'ELC' %}<i class="fas fa-building"></i> ELC
                                                {% elif category == 'TLC' %}<i class="fas fa-exchange-alt"></i> TLC
                                                {% else %}{{ category }}{% endif %}
                                                : {{ count }}개
                                            </span>
                                            {% endfor %}
                                        </div>
                                    </div>
                                    {% endif %}
                                </div>
                                <div class="text-center">
                                    <!-- 진행률 원형 차트 -->
                                    <svg class="progress-ring" viewBox="0 0 100 100">
                                        <circle class="progress-ring-bg" cx="50" cy="50" r="42"></circle>
                                        <circle class="progress-ring-fill" cx="50" cy="50" r="42"
                                                style="stroke-dasharray: {{ (item.progress.overall_progress * 264) / 100 }} 264"></circle>
                                    </svg>
                                    <div class="mt-2">
                                        <strong class="text-primary">{{ item.progress.overall_progress }}%</strong>
                                        <br>
                                        <small class="text-muted">완료</small>
                                    </div>
                                </div>
                            </div>

                            <!-- 단계 진행 상황 표시 -->
                            <div class="step-indicator mb-3">
                                {% for step in item.progress.steps %}
                                <div class="step-item {{ step.status }}">
                                    <div class="step-number">
                                        {% if step.status == 'completed' %}
                                            <i class="fas fa-check"></i>
                                        {% elif step.status == 'in-progress' %}
                                            <i class="fas fa-play"></i>
                                        {% else %}
                                            <i class="fas fa-circle"></i>
                                        {% endif %}
                                    </div>
                                    <div class="step-connector"></div>
                                    <small class="text-muted">{{ step.name[:4] }}</small>
                                </div>
                                {% endfor %}
                            </div>

                            <!-- 상세 진행률 표시 -->
                            <div class="mb-3">
                                {% for step in item.progress.steps %}
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between align-items-center mb-1">
                                        <small class="text-muted">
                                            <strong>{{ step.name }}</strong>
                                            {% if step.details %}
                                                {% if step.step == 1 %}
                                                    (완료: {{ step.details.evaluated_controls }}/{{ step.details.total_controls }}통제)
                                                {% elif step.step == 2 %}
                                                    (완료: {{ step.details.completed_controls }}/{{ step.details.total_controls }}통제)
                                                {% endif %}
                                            {% else %}
                                                (시작 전)
                                            {% endif %}
                                        </small>
                                        <small class="text-primary"><strong>{{ step.details.progress if step.details and step.details.progress is defined else 0 }}%</strong></small>
                                    </div>
                                    <div class="progress" style="height: 5px;">
                                        <div class="progress-bar
                                            {% if step.status == 'completed' %}bg-success
                                            {% elif step.status == 'in-progress' %}bg-primary
                                            {% else %}bg-secondary{% endif %}"
                                            role="progressbar"
                                            style="width: {{ step.details.progress if step.details and step.details.progress is defined else 0 }}%"></div>
                                    </div>

                                    <!-- 카테고리별 진행률 표시 -->
                                    {% if step.details and step.details.category_stats %}
                                    <div class="ms-2 mt-1">
                                        {% for category in ['ITGC', 'ELC', 'TLC'] %}
                                            {% if step.details.category_stats.get(category) %}
                                            {% set cat_data = step.details.category_progress.get(category) if step.details.category_progress else None %}
                                            <div class="d-flex justify-content-between align-items-center" style="font-size: 0.75rem;">
                                                <span class="{% if cat_data and ((step.step == 1 and cat_data.evaluated > 0) or (step.step == 2 and cat_data.completed > 0)) %}text-primary{% else %}text-muted{% endif %}">
                                                    {% if category == 'ITGC' %}
                                                        <i class="fas fa-server" style="color: #17a2b8;"></i> ITGC
                                                    {% elif category == 'ELC' %}
                                                        <i class="fas fa-building" style="color: #ffc107;"></i> ELC
                                                    {% elif category == 'TLC' %}
                                                        <i class="fas fa-exchange-alt" style="color: #28a745;"></i> TLC
                                                    {% endif %}
                                                    {% if cat_data %}
                                                        {% if step.step == 1 %}
                                                            ({{ cat_data.evaluated }}/{{ cat_data.total }})
                                                        {% elif step.step == 2 %}
                                                            ({{ cat_data.completed }}/{{ cat_data.total }})
                                                        {% endif %}
                                                    {% else %}
                                                        (0/{{ step.details.category_stats.get(category) }})
                                                    {% endif %}
                                                </span>
                                                <span class="{% if cat_data and cat_data.progress > 0 %}text-primary{% else %}text-muted{% endif %}">
                                                    {% if cat_data %}{{ cat_data.progress }}%{% else %}시작 전{% endif %}
                                                </span>
                                            </div>
                                            {% endif %}
                                        {% endfor %}
                                    </div>
                                    {% endif %}
                                </div>
                                {% endfor %}
                            </div>

                            <!-- 현재 진행 단계 -->
                            <div class="mb-3">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="text-muted">현재 단계:</span>
                                    {% if item.evaluation_status == 'NOT_STARTED' %}
                                    <span class="badge bg-secondary">
                                        미진행
                                    </span>
                                    {% else %}
                                    <span class="badge {% if item.progress.current_step == 1 %}bg-primary{% else %}bg-success{% endif %}">
                                        {{ item.progress.steps[item.progress.current_step - 1].name }}
                                    </span>
                                    {% endif %}
                                </div>
                            </div>

                            <!-- 순차적 워크플로우 액션 버튼 -->
                            <div class="d-grid gap-2">
                                <!-- 설계평가 버튼 -->
                                {% if item.evaluation_status == 'COMPLETED' %}
                                    <!-- 설계평가 완료 → 확인 버튼 -->
                                    <a href="/user/design-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-outline-success">
                                        <i class="fas fa-check-circle me-1"></i>1단계: 설계평가 확인
                                    </a>
                                {% elif item.evaluation_status == 'IN_PROGRESS' %}
                                    <!-- 설계평가 진행중 → 계속 버튼 -->
                                    <a href="/user/design-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-primary">
                                        <i class="fas fa-clipboard-check me-1"></i>1단계: 설계평가 계속
                                    </a>
                                {% else %}
                                    <!-- 설계평가 미시작 → 시작 버튼 -->
                                    <a href="/user/design-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-primary">
                                        <i class="fas fa-clipboard-check me-1"></i>1단계: 설계평가 시작
                                    </a>
                                {% endif %}

                                <!-- 운영평가 버튼 (설계평가 완료 후에만 활성화) -->
                                {% if item.evaluation_status == 'COMPLETED' %}
                                    {% if item.operation_status == 'COMPLETED' %}
                                        <!-- 운영평가 완료 → 확인 버튼 -->
                                        <a href="/user/operation-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-outline-success">
                                            <i class="fas fa-check-circle me-1"></i>2단계: 운영평가 확인
                                        </a>
                                    {% elif item.operation_status == 'IN_PROGRESS' %}
                                        <!-- 운영평가 진행중 → 계속 버튼 -->
                                        <a href="/user/operation-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-success">
                                            <i class="fas fa-cogs me-1"></i>2단계: 운영평가 계속
                                        </a>
                                    {% else %}
                                        <!-- 운영평가 미시작 → 시작 버튼 -->
                                        <a href="/user/operation-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-success">
                                            <i class="fas fa-cogs me-1"></i>2단계: 운영평가 시작
                                        </a>
                                    {% endif %}
                                {% else %}
                                    <!-- 설계평가 미완료 → 운영평가 잠김 -->
                                    <button class="btn btn-outline-secondary" disabled>
                                        <i class="fas fa-lock me-1"></i>2단계: 운영평가
                                    </button>
                                {% endif %}

                                <!-- 진행 상황 보기 버튼 -->
                                <button class="btn btn-outline-info btn-sm"
                                        onclick="showAssessmentDetail({{ item.rcm_info.rcm_id }}, '{{ item.evaluation_session }}', '{{ item.rcm_info.rcm_name }}')">
                                    <i class="fas fa-eye me-1"></i>상세 진행 상황 보기
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
                    </div>
                    {% else %}
                    <div class="text-center py-4 text-muted">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p class="mb-0">IT 일반 통제(ITGC) RCM이 없습니다</p>
                    </div>
                    {% endif %}
                </div>

                <!-- ELC 섹션 -->
                <div class="mb-4">
                    <h5 class="text-warning mb-3"><i class="fas fa-building me-2"></i>전사 수준 통제 (ELC)</h5>
                    {% if company.categories.ELC %}
                    <div class="row">
                        {% for item in company.categories.ELC %}
                        <div class="col-lg-6 col-xl-4 mb-4">
                            {{ render_rcm_card(item, 'warning') }}
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="text-center py-4 text-muted">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p class="mb-0">전사 수준 통제(ELC) RCM이 없습니다</p>
                    </div>
                    {% endif %}
                </div>

                <!-- TLC 섹션 -->
                <div class="mb-4">
                    <h5 class="text-success mb-3"><i class="fas fa-exchange-alt me-2"></i>거래 수준 통제 (TLC)</h5>
                    {% if company.categories.TLC %}
                    <div class="row">
                        {% for item in company.categories.TLC %}
                        <div class="col-lg-6 col-xl-4 mb-4">
                            {{ render_rcm_card(item, 'success') }}
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="text-center py-4 text-muted">
                        <i class="fas fa-inbox fa-2x mb-2"></i>
                        <p class="mb-0">거래 수준 통제(TLC) RCM이 없습니다</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <!-- 빈 상태 -->
            <div class="text-center py-5">
                <div class="mb-4">
                    <i class="fas fa-tasks text-muted" style="font-size: 4rem;"></i>
                </div>
                <h4 class="text-muted mb-3">내부평가할 RCM이 없습니다</h4>
                <p class="text-muted mb-4">
                    내부평가를 진행하려면 먼저 RCM을 등록하고 접근 권한을 받아야 합니다.
                </p>
                    <a href="{{ url_for('link5.user_rcm') }}" class="btn btn-primary">
                <i class="fas fa-database me-1"></i>RCM 관리로 이동
            </a>
            </div>
        {% endif %}

        <!-- 내부평가 가이드 -->
        <div class="row mt-5">
            <div class="col-12">
                <div class="card border-info">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>내부평가 단계별 가이드</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-12 col-md-6 col-lg-4 mb-3">
                                <h6 class="text-primary">📋 1단계: 평가 계획 수립</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check-circle text-success me-2"></i>평가 범위 및 목적 정의</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>평가 일정 및 담당자 지정</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>평가 방법론 및 기준 설정</li>
                                </ul>
                            </div>

                            <div class="col-12 col-md-6 col-lg-4 mb-3">
                                <h6 class="text-primary">🎯 2단계: 통제 설계 평가</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제 설계의 적절성 검토</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제 목적과 실제 설계 일치성 확인</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제 환경 및 전제조건 검토</li>
                                </ul>
                            </div>

                            <div class="col-12 col-md-6 col-lg-4 mb-3">
                                <h6 class="text-primary">⚡ 3단계: 운영 효과성 평가</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제의 실제 운영 상태 확인</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>운영 빈도 및 일관성 검토</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>운영 증거 및 문서화 상태 평가</li>
                                </ul>
                            </div>

                            <div class="col-12 col-md-6 col-lg-4 mb-3">
                                <h6 class="text-danger">🔍 4단계: 결함 식별 및 평가</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-exclamation-triangle text-warning me-2"></i>통제 결함 및 예외사항 식별</li>
                                    <li><i class="fas fa-exclamation-triangle text-warning me-2"></i>결함의 중요도 및 영향도 평가</li>
                                    <li><i class="fas fa-exclamation-triangle text-warning me-2"></i>근본 원인 분석 수행</li>
                                </ul>
                            </div>

                            <div class="col-12 col-md-6 col-lg-4 mb-3">
                                <h6 class="text-warning">📈 5단계: 개선 계획 수립</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-lightbulb text-warning me-2"></i>결함 해결을 위한 개선 방안 도출</li>
                                    <li><i class="fas fa-lightbulb text-warning me-2"></i>개선 우선순위 및 일정 수립</li>
                                    <li><i class="fas fa-lightbulb text-warning me-2"></i>개선 효과 측정 방법 정의</li>
                                </ul>
                            </div>

                            <div class="col-12 col-md-6 col-lg-4 mb-3">
                                <h6 class="text-secondary">📄 6단계: 평가 보고서 작성</h6>
                                <ul class="list-unstyled mb-0">
                                    <li><i class="fas fa-file-alt text-secondary me-2"></i>평가 결과 종합 및 정리</li>
                                    <li><i class="fas fa-file-alt text-secondary me-2"></i>경영진 보고용 요약 작성</li>
                                    <li><i class="fas fa-file-alt text-secondary me-2"></i>후속 조치 및 모니터링 계획</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 내부평가 상세 모달 -->
    <div class="modal fade" id="assessmentDetailModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header bg-gradient-primary text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-chart-line me-2"></i>
                        <span id="modalRcmName"></span>
                        <small class="d-block mt-1 opacity-75">
                            <i class="fas fa-clipboard-list me-1"></i>
                            세션: <span id="modalSessionName"></span>
                        </small>
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="assessmentDetailContent">
                    <div class="text-center py-5">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">로딩 중...</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;">
                        <i class="fas fa-times me-1"></i>닫기
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showAssessmentDetail(rcmId, evaluationSession, rcmName) {
            // 모달 타이틀 설정
            document.getElementById('modalRcmName').textContent = rcmName;
            document.getElementById('modalSessionName').textContent = evaluationSession;

            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('assessmentDetailModal'));
            modal.show();

            // 로딩 상태로 초기화
            document.getElementById('assessmentDetailContent').innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">로딩 중...</span>
                    </div>
                </div>
            `;

            // AJAX로 상세 데이터 가져오기
            fetch(`/internal-assessment/api/detail/${rcmId}/${evaluationSession}`)
                .then(response => response.json())
                .then(data => {
                    renderAssessmentDetail(data);
                })
                .catch(error => {
                    document.getElementById('assessmentDetailContent').innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            데이터를 불러오는 중 오류가 발생했습니다.
                        </div>
                    `;
                    console.error('Error:', error);
                });
        }

        function renderAssessmentDetail(data) {
            const content = document.getElementById('assessmentDetailContent');

            let html = `
                <!-- 세션 정보 -->
                <div class="mb-3 pb-2 border-bottom">
                    <h6 class="text-muted mb-0">
                        <i class="fas fa-clipboard-list me-2"></i>
                        평가 세션: <strong class="text-dark">${data.evaluation_session}</strong>
                    </h6>
                </div>

                <!-- 전체 진행률 -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0 text-muted">전체 진행률</h6>
                        <h4 class="mb-0 text-primary">${data.progress.overall_progress}%</h4>
                    </div>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-success" role="progressbar"
                             style="width: ${data.progress.overall_progress}%">
                            ${data.progress.overall_progress}%
                        </div>
                    </div>
                </div>

                <!-- 평가 단계별 상세 -->
                <div class="card">
                    <div class="card-header bg-light">
                        <h6 class="mb-0"><i class="fas fa-tasks me-2"></i>평가 진행 단계</h6>
                    </div>
                    <div class="card-body">
            `;

            // 각 단계별 정보
            data.progress.steps.forEach((step, index) => {
                const statusBadge = step.status === 'completed' ?
                    '<span class="badge bg-success">완료</span>' :
                    step.status === 'in-progress' ?
                    '<span class="badge bg-primary">진행중</span>' :
                    '<span class="badge bg-secondary">대기</span>';

                const progressPercent = step.details ? step.details.progress : 0;
                const progressBarClass = step.status === 'completed' ? 'bg-success' :
                                        step.status === 'in-progress' ? 'bg-primary' : 'bg-secondary';

                html += `
                    <div class="mb-4 ${index < data.progress.steps.length - 1 ? 'border-bottom pb-3' : ''}">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <h6 class="mb-1">
                                    ${step.step}. ${step.name}
                                    ${statusBadge}
                                </h6>
                                <p class="text-muted small mb-0">${step.description}</p>
                            </div>
                        </div>
                `;

                if (step.details) {
                    const totalControls = step.step === 1 ?
                        step.details.total_controls :
                        step.details.total_controls;
                    const completedControls = step.step === 1 ?
                        step.details.evaluated_controls :
                        step.details.completed_controls;

                    html += `
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <small class="text-muted">총 통제 수: <strong>${totalControls}개</strong></small>
                            </div>
                            <div class="col-md-6">
                                <small class="text-muted">완료: <strong>${completedControls}개</strong></small>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar ${progressBarClass}"
                                     role="progressbar" style="width: ${progressPercent}%"></div>
                            </div>
                            <small class="text-muted">진행률: ${progressPercent}%</small>
                        </div>
                    `;

                    // 설계평가 상세 정보
                    if (step.step === 1 && data.design_detail && Object.keys(data.design_detail).length > 0) {
                        const stats = data.design_detail.effectiveness_stats || {};
                        if (Object.keys(stats).length > 0) {
                            html += `
                                <div class="mt-3">
                                    <small class="text-muted d-block mb-2"><strong>평가 결과 분포:</strong></small>
                                    <div class="d-flex gap-2 flex-wrap">
                            `;
                            for (const [effectiveness, count] of Object.entries(stats)) {
                                let badgeClass = 'bg-secondary';
                                if (effectiveness === '적정' || effectiveness === 'effective' || effectiveness === '효과적') {
                                    badgeClass = 'bg-success';
                                } else if (effectiveness === '일부 미흡' || effectiveness === 'partially_effective' || effectiveness.includes('부분')) {
                                    badgeClass = 'bg-warning';
                                } else if (effectiveness === '부적정' || effectiveness === 'ineffective' || effectiveness === '비효과적') {
                                    badgeClass = 'bg-danger';
                                }
                                html += `<span class="badge ${badgeClass}">${effectiveness}: ${count}개</span>`;
                            }
                            html += `</div></div>`;
                        }

                        // 미비점이 있는 통제
                        if (data.design_detail.total_inadequate > 0) {
                            html += `
                                <div class="mt-3">
                                    <div class="alert alert-warning mb-0 py-2">
                                        <small><strong><i class="fas fa-exclamation-triangle me-1"></i>미비점 ${data.design_detail.total_inadequate}건</strong></small>
                                        <div class="mt-2">
                            `;
                            data.design_detail.inadequate_controls.forEach(ctrl => {
                                html += `
                                    <div class="mb-2">
                                        <code class="text-dark">${ctrl.control_code}</code>
                                        <span class="badge bg-danger ms-1">${ctrl.overall_effectiveness}</span>
                                        ${ctrl.evaluation_rationale ? `<br><small class="text-muted ms-3">${ctrl.evaluation_rationale}</small>` : ''}
                                    </div>
                                `;
                            });
                            html += `</div></div></div>`;
                        }
                    }

                    // 운영평가 상세 정보
                    if (step.step === 2 && data.operation_detail && Object.keys(data.operation_detail).length > 0) {
                        const stats = data.operation_detail.conclusion_stats || {};
                        if (Object.keys(stats).length > 0) {
                            html += `
                                <div class="mt-3">
                                    <small class="text-muted d-block mb-2"><strong>평가 결과 분포:</strong></small>
                                    <div class="d-flex gap-2 flex-wrap">
                            `;

                            // Effective, Ineffective, Not Tested 순서로 표시
                            const order = ['Effective', 'Ineffective', 'Not Tested'];
                            order.forEach(key => {
                                if (stats[key] !== undefined && stats[key] > 0) {
                                    let badgeClass = 'bg-secondary';
                                    if (key === 'Effective') {
                                        badgeClass = 'bg-success';
                                    } else if (key === 'Ineffective') {
                                        badgeClass = 'bg-danger';
                                    } else if (key === 'Not Tested') {
                                        badgeClass = 'bg-secondary';
                                    }
                                    html += `<span class="badge ${badgeClass}">${key}: ${stats[key]}개</span>`;
                                }
                            });

                            html += `</div></div>`;
                        }
                    }
                } else {
                    html += '<p class="text-muted fst-italic small mt-2">아직 시작되지 않았습니다.</p>';
                }

                html += '</div>';
            });

            html += `
                    </div>
                </div>
            `;

            content.innerHTML = html;
        }
    </script>
</body>
</html>