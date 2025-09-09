<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 상세보기 - {{ rcm_info.rcm_name }}</title>
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
                    <h1><i class="fas fa-eye me-2"></i>RCM 상세보기</h1>
                    <div>
                        <a href="/user/rcm" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-1"></i>목록으로
                        </a>
                    </div>
                </div>
                <hr>
            </div>
        </div>

        <!-- RCM 기본 정보 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>RCM 기본 정보</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="30%">RCM명:</th>
                                        <td><strong>{{ rcm_info.rcm_name }}</strong></td>
                                    </tr>
                                    <tr>
                                        <th>회사명:</th>
                                        <td>{{ rcm_info.company_name }}</td>
                                    </tr>
                                    <tr>
                                        <th>설명:</th>
                                        <td>{{ rcm_info.description or '없음' }}</td>
                                    </tr>
                                    <tr>
                                        <th>내 권한:</th>
                                        <td>
                                            <span class="badge bg-{{ 'danger' if rcm_info.permission_type == 'admin' else 'success' }}">
                                                {{ '관리자' if rcm_info.permission_type == 'admin' else '읽기' }}
                                            </span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="30%">업로드자:</th>
                                        <td>{{ rcm_info.upload_user_name or '알 수 없음' }}</td>
                                    </tr>
                                    <tr>
                                        <th>업로드일:</th>
                                        <td>{{ rcm_info.upload_date.split(' ')[0] if rcm_info.upload_date else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <th>총 통제 수:</th>
                                        <td><span class="badge bg-primary">{{ rcm_details|length }}개</span></td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RCM 상세 데이터 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-list me-2"></i>통제 상세 목록</h5>
                        <div>
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="evaluateCompleteness()">
                                <i class="fas fa-search me-1"></i>통제항목 검토
                            </button>
                            <a href="/rcm/{{ rcm_info.rcm_id }}/mapping" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-link me-1"></i>기준통제 매핑
                            </a>
                        </div>
                    </div>
                    <div class="card-body">
                        {% if rcm_details %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover" id="rcmTable">
                                <thead>
                                    <tr>
                                        <th>통제코드</th>
                                        <th>통제명</th>
                                        <th>통제활동 설명</th>
                                        <th>통제주기</th>
                                        <th>통제유형</th>
                                        <th>통제구분</th>
                                        <th>모집단</th>
                                        <th>테스트절차</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr>
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td><strong>{{ detail.control_name }}</strong></td>
                                        <td>
                                            {% if detail.control_description %}
                                                <div style="max-width: 400px; max-height: 80px; overflow-y: auto; font-size: 0.9rem; line-height: 1.4;" 
                                                     title="{{ detail.control_description }}">
                                                    {{ detail.control_description }}
                                                </div>
                                            {% else %}
                                                <span class="text-muted">-</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ detail.control_frequency or '-' }}</td>
                                        <td>{{ detail.control_type or '-' }}</td>
                                        <td>{{ detail.control_nature or '-' }}</td>
                                        <td>{{ detail.population or '-' }}</td>
                                        <td>
                                            {% if detail.test_procedure %}
                                                <span class="text-truncate" style="max-width: 150px; display: inline-block;" 
                                                      title="{{ detail.test_procedure }}">
                                                    {{ detail.test_procedure }}
                                                </span>
                                            {% else %}
                                                <span class="text-muted">-</span>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-5">
                            <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                            <h5 class="text-muted">등록된 통제 데이터가 없습니다</h5>
                            <p class="text-muted">관리자에게 문의하여 RCM 데이터를 확인하세요.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>

        // RCM 완성도 평가 기능
        function evaluateCompleteness() {
            // 로딩 표시
            const button = document.querySelector('button[onclick="evaluateCompleteness()"]');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>검토 중...';
            button.disabled = true;
                
                // API 호출
                fetch(`/api/rcm/{{ rcm_info.rcm_id }}/evaluate-completeness`, {
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
                        window.location.href = `/rcm/{{ rcm_info.rcm_id }}/completeness-report`;
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

        // 툴팁 초기화
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
            var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        });
    </script>
</body>
</html>