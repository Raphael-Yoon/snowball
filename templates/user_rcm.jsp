<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>내 RCM 조회</title>
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
                    <h1><i class="fas fa-database me-2"></i>내 RCM 조회/평가</h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="fas fa-home me-1"></i>홈으로
                    </a>
                </div>
                <hr>
            </div>
        </div>

        {% if user_rcms %}
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>접근 가능한 RCM 목록</h5>
                    </div>
                    <div class="card-body">
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
                                    {% for rcm in user_rcms %}
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
                                            <button class="btn btn-sm btn-outline-info" onclick="evaluateCompleteness({{ rcm.rcm_id }})">
                                                <i class="fas fa-search me-1"></i>통제항목 검토
                                            </button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
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
        // 통제항목 검토 기능
        function evaluateCompleteness(rcmId) {
            // 로딩 표시
            const button = document.querySelector(`button[onclick="evaluateCompleteness(${rcmId})"]`);
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>검토 중...';
            button.disabled = true;
                
                // API 호출
                fetch(`/api/rcm/${rcmId}/evaluate-completeness`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    
                    if (data.success) {
                        // 바로 상세 보고서 페이지로 이동
                        window.open(`/rcm/${rcmId}/completeness-report`, '_blank');
                    } else {
                        alert('검토 중 오류가 발생했습니다: ' + data.message);
                    }
                })
                .catch(error => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    console.error('검토 오류:', error);
                    alert('검토 중 오류가 발생했습니다.');
                });
        }
    </script>
</body>
</html>