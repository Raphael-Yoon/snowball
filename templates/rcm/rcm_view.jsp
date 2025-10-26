<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ rcm_info.rcm_name }} - SnowBall</title>
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
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1><i class="fas fa-file-alt me-2"></i>{{ rcm_info.rcm_name }}</h1>
            <a href="{{ url_for('rcm.rcm_list') }}" class="btn btn-outline-secondary">
                <i class="fas fa-arrow-left me-1"></i>목록으로
            </a>
        </div>

        <!-- RCM 기본 정보 -->
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <i class="fas fa-info-circle me-2"></i>RCM 기본 정보
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>카테고리:</strong>
                            {% if rcm_info.control_category == 'ELC' %}
                            <span class="badge bg-primary">ELC - Entity Level Controls</span>
                            {% elif rcm_info.control_category == 'TLC' %}
                            <span class="badge bg-success">TLC - Transaction Level Controls</span>
                            {% else %}
                            <span class="badge bg-info">ITGC - IT General Controls</span>
                            {% endif %}
                        </p>
                        <p><strong>등록일:</strong> {{ rcm_info.upload_date[:10] if rcm_info.upload_date else '-' }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>설명:</strong> {{ rcm_info.description or '-' }}</p>
                        <p><strong>파일명:</strong> {{ rcm_info.original_filename or '-' }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- RCM 상세 데이터 -->
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <i class="fas fa-table me-2"></i>통제 항목 목록 (총 {{ rcm_details|length }}개)
            </div>
            <div class="card-body">
                {% if rcm_details %}
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>번호</th>
                                {% for key in rcm_details[0].keys() if key != 'detail_id' and key != 'rcm_id' %}
                                <th>{{ key }}</th>
                                {% endfor %}
                            </tr>
                        </thead>
                        <tbody>
                            {% for detail in rcm_details %}
                            <tr>
                                <td>{{ loop.index }}</td>
                                {% for key, value in detail.items() if key != 'detail_id' and key != 'rcm_id' %}
                                <td>{{ value or '-' }}</td>
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-4">
                    <i class="fas fa-table fa-3x text-muted mb-3"></i>
                    <p class="text-muted">등록된 통제 항목이 없습니다.</p>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- 액션 버튼 -->
        <div class="mt-4 d-flex gap-2">
            <a href="{{ url_for('rcm.rcm_list') }}" class="btn btn-outline-secondary">
                <i class="fas fa-list me-1"></i>목록으로
            </a>
            {% if user_info.admin_flag == 'Y' %}
            <button type="button" class="btn btn-outline-danger" onclick="deleteRcm()">
                <i class="fas fa-trash me-1"></i>삭제
            </button>
            {% endif %}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function deleteRcm() {
            if (!confirm('이 RCM을 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.')) {
                return;
            }

            fetch('{{ url_for("rcm.rcm_delete", rcm_id=rcm_info.rcm_id) }}', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    window.location.href = '{{ url_for("rcm.rcm_list") }}';
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
