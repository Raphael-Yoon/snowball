<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall - TLC 평가</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><img src="{{ url_for('static', filename='img/tlc.jpg') }}" alt="TLC" style="width: 40px; height: 40px; object-fit: cover; border-radius: 8px; margin-right: 12px;">TLC 평가</h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="fas fa-home me-1"></i>홈으로
                    </a>
                </div>
                <hr>
            </div>
        </div>

        <!-- 평가 소개 -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card border-success h-100">
                    <div class="card-header bg-success text-white" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#collapseDesignInfo">
                        <h5 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>설계평가
                            <i class="fas fa-chevron-down float-end"></i>
                        </h5>
                    </div>
                    <div id="collapseDesignInfo" class="collapse">
                        <div class="card-body">
                            <p class="card-text">
                                <strong>설계평가(Design Effectiveness Testing)</strong>는 RCM에 기록된 통제활동이 현재 실제 업무와 일치하는지를 확인하고, 실무적으로 효과적으로 운영되고 있는지를 평가하는 과정입니다.
                            </p>
                            <ul class="small">
                                <li><strong>목적:</strong> 문서상 통제와 실제 수행되는 통제의 일치성 확인 및 실무 효과성 검증</li>
                                <li><strong>범위:</strong> 통제 절차의 현실 반영도, 실제 운영 상태, 위험 완화 효과 검토</li>
                                <li><strong>결과:</strong> 실무와 문서 간 차이점 식별 및 통제 운영 개선방안 도출</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border-warning h-100">
                    <div class="card-header bg-warning text-dark" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#collapseOperationInfo">
                        <h5 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>운영평가
                            <i class="fas fa-chevron-down float-end"></i>
                        </h5>
                    </div>
                    <div id="collapseOperationInfo" class="collapse">
                        <div class="card-body">
                            <p class="card-text">
                                <strong>운영평가(Operating Effectiveness Testing)</strong>는 설계평가가 완료된 통제가 실제로 의도된 대로 작동하고 있는지를 평가하는 과정입니다.
                            </p>
                            <ul class="small">
                                <li><strong>전제조건:</strong> 설계평가가 완료되어 통제 설계가 적정하다고 평가된 통제만 대상</li>
                                <li><strong>목적:</strong> 통제가 일정 기간 동안 일관되게 효과적으로 운영되고 있는지 검증</li>
                                <li><strong>범위:</strong> 통제의 실행, 모니터링, 예외 처리 등 운영 현황 전반</li>
                                <li><strong>결과:</strong> 운영 효과성 결론 및 운영상 개선점 도출</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 설계평가 현황 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-clipboard-check me-2"></i>설계평가 현황</h5>
                    </div>
                    <div class="card-body">
                        {% if tlc_rcms %}
                        {% set has_design_sessions = tlc_rcms|selectattr('design_evaluation_completed')|list|length > 0 %}
                        {% if has_design_sessions %}
                        <div class="accordion" id="designEvaluationAccordion">
                            {% for rcm in tlc_rcms %}
                            {% if rcm.design_evaluation_completed %}
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="heading{{ rcm.rcm_id }}">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ rcm.rcm_id }}">
                                        <i class="fas fa-file-alt me-2"></i>{{ rcm.rcm_name }}
                                        <span class="badge bg-success ms-2">{{ rcm.completed_design_sessions|length }}개 세션 완료</span>
                                    </button>
                                </h2>
                                <div id="collapse{{ rcm.rcm_id }}" class="accordion-collapse collapse" data-bs-parent="#designEvaluationAccordion">
                                    <div class="accordion-body">
                                        <div class="table-responsive">
                                            <table class="table table-sm">
                                                <thead>
                                                    <tr>
                                                        <th>평가명</th>
                                                        <th>완료일</th>
                                                        <th>평가 대상 통제</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {% for session in rcm.completed_design_sessions %}
                                                    <tr>
                                                        <td><i class="fas fa-check-circle text-success me-1"></i>{{ session.evaluation_session }}</td>
                                                        <td>{{ session.completed_date[:10] if session.completed_date else '-' }}</td>
                                                        <td>{{ session.eligible_control_count }}개</td>
                                                    </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endif %}
                            {% endfor %}
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-clipboard fa-2x text-muted mb-2"></i>
                            <p class="text-muted">완료된 설계평가가 없습니다.</p>
                            <small class="text-muted">설계평가를 먼저 완료해주세요.</small>
                        </div>
                        {% endif %}
                        {% else %}
                        <div class="text-center py-4">
                            <p class="text-muted">접근 가능한 RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- 운영평가 현황 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0"><i class="fas fa-chart-line me-2"></i>운영평가 현황</h5>
                    </div>
                    <div class="card-body">
                        {% if tlc_rcms %}
                        {% set has_operation_sessions = tlc_rcms|selectattr('has_operation_sessions')|list|length > 0 %}
                        {% if has_operation_sessions %}
                        <div class="accordion" id="operationEvaluationAccordion">
                            {% for rcm in tlc_rcms %}
                            {% if rcm.has_operation_sessions %}
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="opheading{{ rcm.rcm_id }}">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#opcollapse{{ rcm.rcm_id }}">
                                        <i class="fas fa-file-alt me-2"></i>{{ rcm.rcm_name }}
                                        {% set completed_count = rcm.operation_sessions|selectattr('status', 'equalto', 4)|list|length %}
                                        {% set in_progress_count = rcm.operation_sessions|selectattr('status', 'equalto', 3)|list|length %}
                                        {% if completed_count > 0 %}
                                        <span class="badge bg-success ms-2">완료 {{ completed_count }}개</span>
                                        {% endif %}
                                        {% if in_progress_count > 0 %}
                                        <span class="badge bg-warning text-dark ms-2">진행중 {{ in_progress_count }}개</span>
                                        {% endif %}
                                    </button>
                                </h2>
                                <div id="opcollapse{{ rcm.rcm_id }}" class="accordion-collapse collapse" data-bs-parent="#operationEvaluationAccordion">
                                    <div class="accordion-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover">
                                                <thead>
                                                    <tr>
                                                        <th>평가명</th>
                                                        <th>진행률</th>
                                                        <th>작업</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {% for session in rcm.operation_sessions %}
                                                    <tr>
                                                        <td>
                                                            <i class="fas fa-clipboard-check me-2"></i>{{ session.evaluation_session }}
                                                        </td>
                                                        <td>
                                                            <div class="progress" style="width: 120px; height: 20px;">
                                                                <div class="progress-bar {% if session.progress == 100 %}bg-success{% else %}bg-warning{% endif %}"
                                                                     role="progressbar" style="width: {{ session.progress }}%">
                                                                    {{ session.progress }}%
                                                                </div>
                                                            </div>
                                                            <small class="text-muted">{{ session.operation_completed_count }}/{{ session.eligible_control_count }} 통제</small>
                                                        </td>
                                                        <td>
                                                            {% if session.status == 2 %}
                                                            <button class="btn btn-sm btn-success me-1" onclick="continueOperationEvaluation({{ rcm.rcm_id }}, '{{ session.evaluation_session }}')">
                                                                <i class="fas fa-play-circle me-1"></i>시작하기
                                                            </button>
                                                            {% elif session.status == 3 %}
                                                            <button class="btn btn-sm btn-warning me-1" onclick="continueOperationEvaluation({{ rcm.rcm_id }}, '{{ session.evaluation_session }}')">
                                                                <i class="fas fa-play me-1"></i>계속하기
                                                            </button>
                                                            {% else %}
                                                            <button class="btn btn-sm btn-outline-secondary me-1" onclick="viewOperationEvaluation({{ rcm.rcm_id }}, '{{ session.evaluation_session }}')">
                                                                <i class="fas fa-eye me-1"></i>보기
                                                            </button>
                                                            {% endif %}
                                                        </td>
                                                    </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endif %}
                            {% endfor %}
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-hourglass-half fa-2x text-muted mb-2"></i>
                            <p class="text-muted">운영평가가 시작된 세션이 없습니다.</p>
                            <small class="text-muted">설계평가를 완료한 후 '완료 처리' 버튼을 눌러 운영평가를 시작하세요.</small>
                        </div>
                        {% endif %}
                        {% else %}
                        <div class="text-center py-4">
                            <p class="text-muted">접근 가능한 RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function continueOperationEvaluation(rcmId, evaluationName) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/operation-evaluation/rcm';

            const rcmInput = document.createElement('input');
            rcmInput.type = 'hidden';
            rcmInput.name = 'rcm_id';
            rcmInput.value = rcmId;

            const sessionInput = document.createElement('input');
            sessionInput.type = 'hidden';
            sessionInput.name = 'design_evaluation_session';
            sessionInput.value = evaluationName;

            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'continue';

            form.appendChild(rcmInput);
            form.appendChild(sessionInput);
            form.appendChild(actionInput);
            document.body.appendChild(form);
            form.submit();
        }

        function viewOperationEvaluation(rcmId, evaluationName) {
            continueOperationEvaluation(rcmId, evaluationName);
        }
    </script>
</body>
</html>
