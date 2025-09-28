<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>운영평가</title>
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
                    <h1><i class="fas fa-cogs me-2"></i>운영평가</h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="fas fa-home me-1"></i>홈으로
                    </a>
                </div>
                <hr>
            </div>
        </div>

        <!-- 운영평가 소개 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-info-circle me-2"></i>운영평가란?</h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">
                            <strong>운영평가(Operating Effectiveness Testing)</strong>는 설계평가가 완료된 통제가 실제로 의도된 대로 작동하고 있는지를 평가하는 과정입니다.
                        </p>
                        <ul>
                            <li><strong>전제조건:</strong> 설계평가가 완료되어 통제 설계가 적정하다고 평가된 통제만 대상</li>
                            <li><strong>목적:</strong> 통제가 일정 기간 동안 일관되게 효과적으로 운영되고 있는지 검증</li>
                            <li><strong>범위:</strong> 통제의 실행, 모니터링, 예외 처리 등 운영 현황 전반</li>
                            <li><strong>결과:</strong> 운영 효과성 결론 및 운영상 개선점 도출</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- 접근 가능한 RCM 목록 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-folder-open me-2"></i>보유 RCM 목록</h6>
                    </div>
                    <div class="card-body">
                        {% if user_rcms %}
                        <div class="row g-3">
                            {% for rcm in user_rcms %}
                            <div class="col-lg-6 col-md-12">
                                <div class="card {% if rcm.design_evaluation_completed %}border-warning{% else %}border-secondary{% endif %} h-100">
                                    <div class="card-body">
                                        <h6 class="card-title text-truncate" title="{{ rcm.rcm_name }}">
                                            <i class="fas fa-file-alt me-2 {% if rcm.design_evaluation_completed %}text-warning{% else %}text-muted{% endif %}"></i>{{ rcm.rcm_name }}
                                        </h6>
                                        <p class="card-text">
                                            <small class="text-muted">
                                                <i class="fas fa-building me-1"></i>{{ rcm.company_name }}<br>
                                                <i class="fas fa-calendar me-1"></i>{{ rcm.created_date.strftime('%Y-%m-%d') if rcm.created_date else '-' }}
                                            </small>
                                        </p>

                                        {% if rcm.design_evaluation_completed %}
                                        <div class="mb-3">
                                            <small class="text-muted fw-bold">완료된 설계평가 세션:</small>
                                            {% for session in rcm.completed_design_sessions %}
                                            <div class="d-grid mt-2">
                                                <form method="POST" action="/operation-evaluation/rcm/{{ rcm.rcm_id }}" style="display: inline;">
                                                    <input type="hidden" name="design_evaluation_session" value="{{ session.evaluation_session }}">
                                                    <button type="submit" class="btn {% if session.operation_completed_count > 0 %}btn-warning{% else %}btn-outline-warning{% endif %} btn-sm w-100">
                                                        <i class="fas fa-chart-line me-1"></i>{{ session.evaluation_session }}
                                                        <small class="ms-2 text-muted">({{ session.completed_date[:10] if session.completed_date else '-' }})</small>
                                                        {% if session.operation_completed_count > 0 %}
                                                        <br><small class="text-dark">진행중: {{ session.operation_completed_count }}/{{ rcm.key_control_count }}</small>
                                                        {% else %}
                                                        <br><small class="text-muted">시작하기</small>
                                                        {% endif %}
                                                    </button>
                                                </form>
                                            </div>
                                            {% endfor %}
                                        </div>
                                        {% else %}
                                        <div class="d-grid">
                                            <button class="btn btn-secondary btn-sm" disabled title="설계평가 완료 후 이용 가능">
                                                <i class="fas fa-lock me-1"></i>설계평가 필요
                                            </button>
                                        </div>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                            <p class="text-muted">접근 가능한 RCM이 없습니다.</p>
                            <small class="text-muted">관리자에게 RCM 접근 권한을 요청하세요.</small>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- 평가 진행 현황 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-tasks me-2"></i>진행 중인 운영평가</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center py-4">
                            <i class="fas fa-hourglass-half fa-2x text-muted mb-2"></i>
                            <p class="text-muted">진행 중인 운영평가가 없습니다.</p>
                            <small class="text-muted">새로운 운영평가를 시작하면 여기에 진행 상황이 표시됩니다.</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 최근 평가 결과 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-history me-2"></i>최근 운영평가 결과</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center py-4">
                            <i class="fas fa-clipboard-list fa-2x text-muted mb-2"></i>
                            <p class="text-muted">완료된 운영평가가 없습니다.</p>
                            <small class="text-muted">운영평가를 완료하면 여기에 결과가 표시됩니다.</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 운영평가 방법론 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-book me-2"></i>운영평가 방법론</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <h6 class="text-primary">관찰(Observation)</h6>
                                <p class="small">통제 활동이 실제로 수행되는 모습을 관찰</p>
                            </div>
                            <div class="col-md-3">
                                <h6 class="text-success">조회(Inquiry)</h6>
                                <p class="small">통제 담당자와의 면담을 통한 정보 수집</p>
                            </div>
                            <div class="col-md-3">
                                <h6 class="text-warning">검사(Inspection)</h6>
                                <p class="small">문서나 기록의 존재와 내용 검토</p>
                            </div>
                            <div class="col-md-3">
                                <h6 class="text-danger">재실행(Re-performance)</h6>
                                <p class="small">통제 절차의 독립적 재수행</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>