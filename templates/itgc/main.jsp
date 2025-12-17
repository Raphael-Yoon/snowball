<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Snowball - ITGC</title>
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
                    <i class="fas fa-server text-info me-2"></i>
                    ITGC (IT General Controls)
                </h2>
                <p class="text-muted">IT 일반 통제</p>
            </div>
        </div>

        <!-- RCM 목록 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-list me-2"></i>
                            ITGC RCM 목록 ({{ itgc_rcms|length }}개)
                        </h5>
                    </div>
                    <div class="card-body">
                        {% if itgc_rcms %}
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
                                    {% for rcm in itgc_rcms %}
                                    <tr>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('itgc.design_evaluation') }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-clipboard-check me-1"></i>설계평가
                                            </a>
                                            <a href="{{ url_for('itgc.operation_evaluation') }}" class="btn btn-sm btn-outline-success">
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
                            <p class="text-muted">등록된 ITGC RCM이 없습니다.</p>
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

        <!-- ITGC 5대 영역 -->
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-lock me-2"></i>
                            접근 통제 (Access Control)
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-primary me-2"></i>사용자 ID 관리</li>
                            <li><i class="fas fa-check text-primary me-2"></i>권한 부여 및 승인</li>
                            <li><i class="fas fa-check text-primary me-2"></i>패스워드 정책</li>
                            <li><i class="fas fa-check text-primary me-2"></i>접근 권한 검토</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-cogs me-2"></i>
                            변경 관리 (Change Management)
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-success me-2"></i>변경 요청 및 승인</li>
                            <li><i class="fas fa-check text-success me-2"></i>테스트 및 검증</li>
                            <li><i class="fas fa-check text-success me-2"></i>운영 이관</li>
                            <li><i class="fas fa-check text-success me-2"></i>긴급 변경 관리</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-warning text-dark">
                        <h5 class="mb-0">
                            <i class="fas fa-shield-alt me-2"></i>
                            시스템 개발 (System Development)
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-warning me-2"></i>개발 방법론</li>
                            <li><i class="fas fa-check text-warning me-2"></i>품질 보증</li>
                            <li><i class="fas fa-check text-warning me-2"></i>개발/운영 환경 분리</li>
                            <li><i class="fas fa-check text-warning me-2"></i>시스템 인수</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-database me-2"></i>
                            백업 및 복구 (Backup & Recovery)
                        </h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><i class="fas fa-check text-danger me-2"></i>백업 정책 및 절차</li>
                            <li><i class="fas fa-check text-danger me-2"></i>백업 수행 및 검증</li>
                            <li><i class="fas fa-check text-danger me-2"></i>복구 테스트</li>
                            <li><i class="fas fa-check text-danger me-2"></i>재해 복구 계획</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-server me-2"></i>
                            IT 운영 (IT Operations)
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <ul class="list-unstyled mb-0">
                                    <li><i class="fas fa-check text-secondary me-2"></i>작업 스케줄링</li>
                                    <li><i class="fas fa-check text-secondary me-2"></i>시스템 모니터링</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <ul class="list-unstyled mb-0">
                                    <li><i class="fas fa-check text-secondary me-2"></i>보안 패치 관리</li>
                                    <li><i class="fas fa-check text-secondary me-2"></i>성능 관리</li>
                                </ul>
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
