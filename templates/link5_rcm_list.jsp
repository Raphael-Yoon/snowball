<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>내 RCM 조회</title>
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
                    <h1><img src="{{ url_for('static', filename='img/rcm.jpg') }}" alt="RCM" style="width: 40px; height: 40px; object-fit: cover; border-radius: 8px; margin-right: 12px;">내 RCM 조회/평가</h1>
                    <div>
                        {% if user_info and user_info.get('admin_flag') == 'Y' %}
                        <a href="{{ url_for('link5.rcm_upload') }}" class="btn btn-gradient me-2">
                            <i class="fas fa-upload me-1"></i>RCM 업로드
                        </a>
                        {% endif %}
                        <a href="/" class="btn btn-secondary">
                            <i class="fas fa-home me-1"></i>홈으로
                        </a>
                    </div>
                </div>
                <hr>
            </div>
        </div>

        {% if user_rcms %}
        <!-- 카테고리 탭 -->
        <ul class="nav nav-tabs mb-4" id="rcmTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="all-tab" data-bs-toggle="tab" data-bs-target="#all" type="button">
                    전체 ({{ user_rcms|length }})
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
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>접근 가능한 RCM 목록 (전체)</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>카테고리</th>
                                        <th>RCM명</th>
                                        <th>회사명</th>
                                        <th>설명</th>
                                        <th>내 권한</th>
                                        <th>업로드일</th>
                                        <th>관리</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in user_rcms %}
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
                                        <td><strong>{{ rcm.rcm_name }}</strong></td>
                                        <td>{{ rcm.company_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>
                                            <span class="badge bg-{{ 'danger' if rcm.permission_type == 'admin' else 'success' }}">
                                                {{ '관리자' if rcm.permission_type == 'admin' else '읽기' }}
                                            </span>
                                        </td>
                                        <td>{{ rcm.upload_date.split(' ')[0] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="/rcm/{{ rcm.rcm_id }}/view" class="btn btn-sm btn-outline-primary me-1">
                                                <i class="fas fa-eye me-1"></i>상세보기
                                            </a>
                                            {% if user_info and user_info.get('admin_flag') == 'Y' %}
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
                    </div>
                </div>
            </div>

            <!-- ELC 탭 -->
            <div class="tab-pane fade" id="elc" role="tabpanel">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="fas fa-building me-2"></i>ELC - Entity Level Controls (전사적 통제)</h5>
                    </div>
                    <div class="card-body">
                        {% if rcms_by_category.ELC %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>RCM명</th>
                                        <th>회사명</th>
                                        <th>설명</th>
                                        <th>내 권한</th>
                                        <th>업로드일</th>
                                        <th>관리</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in rcms_by_category.ELC %}
                                    <tr>
                                        <td><strong>{{ rcm.rcm_name }}</strong></td>
                                        <td>{{ rcm.company_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>
                                            <span class="badge bg-{{ 'danger' if rcm.permission_type == 'admin' else 'success' }}">
                                                {{ '관리자' if rcm.permission_type == 'admin' else '읽기' }}
                                            </span>
                                        </td>
                                        <td>{{ rcm.upload_date.split(' ')[0] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="/rcm/{{ rcm.rcm_id }}/view" class="btn btn-sm btn-outline-primary me-1">
                                                <i class="fas fa-eye me-1"></i>상세보기
                                            </a>
                                            {% if user_info and user_info.get('admin_flag') == 'Y' %}
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
                        {% else %}
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
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-exchange-alt me-2"></i>TLC - Transaction Level Controls (거래 수준 통제)</h5>
                    </div>
                    <div class="card-body">
                        {% if rcms_by_category.TLC %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>RCM명</th>
                                        <th>회사명</th>
                                        <th>설명</th>
                                        <th>내 권한</th>
                                        <th>업로드일</th>
                                        <th>관리</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in rcms_by_category.TLC %}
                                    <tr>
                                        <td><strong>{{ rcm.rcm_name }}</strong></td>
                                        <td>{{ rcm.company_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>
                                            <span class="badge bg-{{ 'danger' if rcm.permission_type == 'admin' else 'success' }}">
                                                {{ '관리자' if rcm.permission_type == 'admin' else '읽기' }}
                                            </span>
                                        </td>
                                        <td>{{ rcm.upload_date.split(' ')[0] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="/rcm/{{ rcm.rcm_id }}/view" class="btn btn-sm btn-outline-primary me-1">
                                                <i class="fas fa-eye me-1"></i>상세보기
                                            </a>
                                            {% if user_info and user_info.get('admin_flag') == 'Y' %}
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
                        {% else %}
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
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="fas fa-server me-2"></i>ITGC - IT General Controls (IT 일반 통제)</h5>
                    </div>
                    <div class="card-body">
                        {% if rcms_by_category.ITGC %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>RCM명</th>
                                        <th>회사명</th>
                                        <th>설명</th>
                                        <th>내 권한</th>
                                        <th>업로드일</th>
                                        <th>관리</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in rcms_by_category.ITGC %}
                                    <tr>
                                        <td><strong>{{ rcm.rcm_name }}</strong></td>
                                        <td>{{ rcm.company_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>
                                            <span class="badge bg-{{ 'danger' if rcm.permission_type == 'admin' else 'success' }}">
                                                {{ '관리자' if rcm.permission_type == 'admin' else '읽기' }}
                                            </span>
                                        </td>
                                        <td>{{ rcm.upload_date.split(' ')[0] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="/rcm/{{ rcm.rcm_id }}/view" class="btn btn-sm btn-outline-primary me-1">
                                                <i class="fas fa-eye me-1"></i>상세보기
                                            </a>
                                            {% if user_info and user_info.get('admin_flag') == 'Y' %}
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
                        {% else %}
                        <div class="text-center py-4">
                            <p class="text-muted">ITGC RCM이 없습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% else %}
        <div class="row">
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle fa-2x mb-3"></i>
                    <h5>접근 가능한 RCM이 없습니다</h5>
                    <p>현재 귀하에게 할당된 RCM이 없습니다. 관리자에게 문의하여 필요한 RCM에 대한 접근 권한을 요청하세요.</p>
                    <hr>
                    <small class="text-muted">
                        <i class="fas fa-question-circle me-1"></i>
                        RCM 접근 권한 관련 문의는 시스템 관리자에게 연락하세요.
                    </small>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 관리자만 안내사항 표시 -->
        {% if user_info and user_info.get('admin_flag') == 'Y' %}
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h6><i class="fas fa-info-circle me-2"></i>안내사항</h6>
                        <ul class="list-unstyled small">
                            <li><i class="fas fa-eye text-success me-2"></i><strong>읽기 권한:</strong> RCM 데이터 조회 및 Excel 다운로드</li>
                            <li><i class="fas fa-user-shield text-danger me-2"></i><strong>관리자 권한:</strong> RCM 데이터 조회, 다운로드 및 관리</li>
                            <li><i class="fas fa-shield-alt text-info me-2"></i>모든 RCM 접근은 로그로 기록됩니다.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function deleteRcm(rcmId, rcmName) {
            if (!confirm(`"${rcmName}" RCM을 삭제하시겠습니까?\n\n삭제된 RCM은 목록에서 제거됩니다.`)) {
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