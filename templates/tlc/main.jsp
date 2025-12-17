<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Snowball - TLC</title>
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
                    <i class="fas fa-exchange-alt text-success me-2"></i>
                    TLC (Transaction Level Controls)
                </h2>
                <p class="text-muted">거래 수준 통제</p>
            </div>
        </div>

        <!-- RCM 목록 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-list me-2"></i>
                            TLC RCM 목록 ({{ tlc_rcms|length }}개)
                        </h5>
                    </div>
                    <div class="card-body">
                        {% if tlc_rcms %}
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
                                    {% for rcm in tlc_rcms %}
                                    <tr>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('tlc.design_evaluation') }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-clipboard-check me-1"></i>설계평가
                                            </a>
                                            <a href="{{ url_for('tlc.operation_evaluation') }}" class="btn btn-sm btn-outline-success">
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
                            <p class="text-muted">등록된 TLC RCM이 없습니다.</p>
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

        <!-- 거래 수준 통제 설명 -->
        <div class="row g-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>
                            TLC란?
                        </h5>
                    </div>
                    <div class="card-body">
                        <p>거래 수준 통제(Transaction Level Controls)는 특정 비즈니스 프로세스나 거래 유형에 대해 설계되고 운영되는 통제입니다.</p>
                        <h6 class="mt-3">주요 특징:</h6>
                        <ul>
                            <li>개별 거래나 거래 유형에 대한 직접적인 통제</li>
                            <li>재무제표 오류를 방지하거나 탐지하는 구체적인 통제</li>
                            <li>자동화된 통제 또는 수동 통제로 구성</li>
                            <li>주요 회계 프로세스(매출, 구매, 급여 등)에 적용</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
