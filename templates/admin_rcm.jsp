<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall - RCM 관리</title>
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
                    <h1><i class="fas fa-file-excel me-2"></i>RCM 관리</h1>
                    <a href="/admin/rcm/upload" class="btn btn-primary">
                        <i class="fas fa-plus me-2"></i>새 RCM 업로드
                    </a>
                </div>
                <hr>
            </div>
        </div>

        {% if rcms %}
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>등록된 RCM 목록</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>RCM명</th>
                                        <th>회사명</th>
                                        <th>설명</th>
                                        <th>업로드자</th>
                                        <th>업로드일</th>
                                        <th>관리</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rcm in rcms %}
                                    <tr>
                                        <td><strong>{{ rcm.rcm_name }}</strong></td>
                                        <td>{{ rcm.company_name }}</td>
                                        <td>{{ rcm.description or '-' }}</td>
                                        <td>{{ rcm.upload_user_name or '-' }}</td>
                                        <td>{{ rcm.upload_date.split(' ')[0] if rcm.upload_date else '-' }}</td>
                                        <td>
                                            <a href="/admin/rcm/{{ rcm.rcm_id }}/view" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-eye me-1"></i>보기
                                            </a>
                                            <a href="/admin/rcm/{{ rcm.rcm_id }}/users" class="btn btn-sm btn-outline-success">
                                                <i class="fas fa-users me-1"></i>사용자
                                            </a>
                                            <button class="btn btn-sm btn-outline-danger" onclick="deleteRcm({{ rcm.rcm_id }}, '{{ rcm.rcm_name }}')">
                                                <i class="fas fa-trash me-1"></i>삭제
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
                    <h5>등록된 RCM이 없습니다</h5>
                    <p>새로운 RCM을 업로드하여 시작하세요.</p>
                    <a href="/admin/rcm/upload" class="btn btn-primary">
                        <i class="fas fa-plus me-2"></i>첫 RCM 업로드
                    </a>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="row mt-4">
            <div class="col-12">
                <a href="/admin" class="btn btn-secondary">
                    <i class="fas fa-arrow-left me-2"></i>관리자 대시보드로 돌아가기
                </a>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // RCM 삭제 함수
        function deleteRcm(rcmId, rcmName) {
            if (!confirm(`'${rcmName}' RCM을 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없으며, 다음 항목들이 함께 삭제됩니다:\n- RCM 상세 데이터\n- 사용자 접근 권한\n\n정말로 삭제하시겠습니까?`)) {
                return;
            }
            
            const formData = new FormData();
            formData.append('rcm_id', rcmId);
            
            // 삭제 버튼 비활성화
            const deleteBtn = event.target.closest('button');
            deleteBtn.disabled = true;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>삭제 중...';
            
            fetch('/admin/rcm/delete', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('[ADMIN-005] 삭제 실패: ' + data.message);
                    deleteBtn.disabled = false;
                    deleteBtn.innerHTML = '<i class="fas fa-trash me-1"></i>삭제';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('[ADMIN-006] RCM 삭제 중 오류가 발생했습니다.');
                deleteBtn.disabled = false;
                deleteBtn.innerHTML = '<i class="fas fa-trash me-1"></i>삭제';
            });
        }
    </script>
</body>
</html>