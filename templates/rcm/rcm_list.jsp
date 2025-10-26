<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 목록 - SnowBall</title>
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
        <!-- 플래시 메시지 -->
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1><i class="fas fa-file-alt me-2"></i>RCM 목록</h1>
            {% if user_info.admin_flag == 'Y' %}
            <a href="{{ url_for('rcm.rcm_upload') }}" class="btn btn-gradient">
                <i class="fas fa-upload me-1"></i>RCM 업로드
            </a>
            {% endif %}
        </div>

        <!-- 카테고리 탭 -->
        <ul class="nav nav-tabs mb-4" id="rcmTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="all-tab" data-bs-toggle="tab" data-bs-target="#all" type="button">
                    전체 ({{ all_rcms|length }})
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="elc-tab" data-bs-toggle="tab" data-bs-target="#elc" type="button">
                    ELC ({{ rcms_by_category.ELC|length }})
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="tlc-tab" data-bs-toggle="tab" data-bs-target="#tlc" type="button">
                    TLC ({{ rcms_by_category.TLC|length }})
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="itgc-tab" data-bs-toggle="tab" data-bs-target="#itgc" type="button">
                    ITGC ({{ rcms_by_category.ITGC|length }})
                </button>
            </li>
        </ul>

        <!-- 탭 콘텐츠 -->
        <div class="tab-content" id="rcmTabsContent">
            <!-- 전체 탭 -->
            <div class="tab-pane fade show active" id="all" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>카테고리</th>
                                        <th>RCM 이름</th>
                                        <th>설명</th>
                                        <th>등록일</th>
                                        <th>작업</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in all_rcms %}
                                    <tr>
                                        <td>
                                            {% if rcm.control_category == 'ELC' %}
                                            <span class="badge bg-primary">ELC</span>
                                            {% elif rcm.control_category == 'TLC' %}
                                            <span class="badge bg-success">TLC</span>
                                            {% else %}
                                            <span class="badge bg-info">ITGC</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('rcm.rcm_view', rcm_id=rcm.rcm_id) }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-eye me-1"></i>조회
                                            </a>
                                            {% if user_info.admin_flag == 'Y' %}
                                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteRcm({{ rcm.rcm_id }}, '{{ rcm.rcm_name }}')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% if not all_rcms %}
                        <div class="text-center py-4">
                            <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                            <p class="text-muted">등록된 RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- ELC 탭 -->
            <div class="tab-pane fade" id="elc" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Entity Level Controls (전사적 통제)</h5>
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
                                    {% for rcm in rcms_by_category.ELC %}
                                    <tr>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('rcm.rcm_view', rcm_id=rcm.rcm_id) }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-eye me-1"></i>조회
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% if not rcms_by_category.ELC %}
                        <div class="text-center py-4">
                            <p class="text-muted">ELC RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- TLC 탭 -->
            <div class="tab-pane fade" id="tlc" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Transaction Level Controls (거래 수준 통제)</h5>
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
                                    {% for rcm in rcms_by_category.TLC %}
                                    <tr>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('rcm.rcm_view', rcm_id=rcm.rcm_id) }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-eye me-1"></i>조회
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% if not rcms_by_category.TLC %}
                        <div class="text-center py-4">
                            <p class="text-muted">TLC RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- ITGC 탭 -->
            <div class="tab-pane fade" id="itgc" role="tabpanel">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">IT General Controls (IT 일반 통제)</h5>
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
                                    {% for rcm in rcms_by_category.ITGC %}
                                    <tr>
                                        <td>{{ rcm.rcm_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_date[:10] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="{{ url_for('rcm.rcm_view', rcm_id=rcm.rcm_id) }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-eye me-1"></i>조회
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% if not rcms_by_category.ITGC %}
                        <div class="text-center py-4">
                            <p class="text-muted">ITGC RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function deleteRcm(rcmId, rcmName) {
            if (!confirm(`"${rcmName}" RCM을 삭제하시겠습니까?`)) {
                return;
            }

            fetch(`/rcm/${rcmId}/delete`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert('오류: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('RCM 삭제 중 오류가 발생했습니다.');
            });
        }
    </script>
</body>
</html>
