<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ELC - Snowball</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col-12">
                <h2>
                    <i class="fas fa-building text-primary me-2"></i>
                    ELC (Entity Level Controls)
                </h2>
                <p class="text-muted">전사적 통제</p>
            </div>
        </div>

        <!-- RCM 목록 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-list me-2"></i>
                            ELC RCM 목록 ({{ elc_rcms|length }}개)
                        </h5>
                    </div>
                    <div class="card-body">
                        {% if elc_rcms %}
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>RCM 이름</th>
                                        <th>설명</th>
                                        <th>등록일</th>
                                        <th>작업</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in elc_rcms %}
                                    <tr>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('elc.design_evaluation') }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-clipboard-check me-1"></i>설계평가
                                            </a>
                                            <a href="{{ url_for('elc.operation_evaluation') }}" class="btn btn-sm btn-outline-success">
                                                <i class="fas fa-cogs me-1"></i>운영평가
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-5">
                            <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                            <p class="text-muted">등록된 ELC RCM이 없습니다.</p>
                            {% if user_info.admin_flag == 'Y' %}
                            <a href="{{ url_for('rcm.rcm_upload') }}" class="btn btn-gradient mt-2">
                                <i class="fas fa-upload me-1"></i>RCM 업로드
                            </a>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- COSO Framework 구성 요소 -->
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-shield-alt me-2"></i>
                            통제 환경
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-success me-2"></i>윤리 및 가치관</li>
                            <li><i class="fas fa-check text-success me-2"></i>이사회 및 감사위원회</li>
                            <li><i class="fas fa-check text-success me-2"></i>조직 구조</li>
                            <li><i class="fas fa-check text-success me-2"></i>권한 및 책임</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            위험 평가
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-info me-2"></i>목표 설정</li>
                            <li><i class="fas fa-check text-info me-2"></i>위험 식별</li>
                            <li><i class="fas fa-check text-info me-2"></i>위험 분석</li>
                            <li><i class="fas fa-check text-info me-2"></i>사기 위험</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>
                            정보 및 의사소통
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-warning me-2"></i>정보 시스템</li>
                            <li><i class="fas fa-check text-warning me-2"></i>내부 의사소통</li>
                            <li><i class="fas fa-check text-warning me-2"></i>외부 의사소통</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-eye me-2"></i>
                            모니터링 활동
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-primary me-2"></i>지속적 평가</li>
                            <li><i class="fas fa-check text-primary me-2"></i>독립적 평가</li>
                            <li><i class="fas fa-check text-primary me-2"></i>미비점 보고 및 개선</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
