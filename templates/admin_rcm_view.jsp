<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 상세보기</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        #rcmTable {
            table-layout: fixed;
            width: 100%;
        }
        #rcmTable th, #rcmTable td {
            word-wrap: break-word;
            overflow-wrap: break-word;
            vertical-align: top;
        }
        .text-truncate-custom {
            display: block;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-eye me-2"></i>RCM 상세보기</h1>
                    <div>
                        <a href="/admin/rcm/{{ rcm_info.rcm_id }}/users" class="btn btn-success me-2">
                            <i class="fas fa-users me-1"></i>사용자 관리
                        </a>
                        <a href="/admin/rcm" class="btn btn-secondary">
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
                            <button class="btn btn-sm btn-outline-secondary" onclick="exportToExcel()">
                                <i class="fas fa-file-excel me-1"></i>Excel 다운로드
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        {% if rcm_details %}
                        <div class="table-responsive">
                            <table class="table table-striped table-hover" id="rcmTable">
                                <thead>
                                    <tr>
                                        <th width="7%">통제코드</th>
                                        <th width="7%">핵심통제</th>
                                        <th width="12%">통제명</th>
                                        <th width="20%">통제활동설명</th>
                                        <th width="8%">통제주기</th>
                                        <th width="8%">통제유형</th>
                                        <th width="8%">통제구분</th>
                                        <th width="12%">모집단</th>
                                        <th width="18%">테스트절차</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr>
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td class="text-center">
                                            {% if detail.key_control == '핵심' %}
                                                <span class="badge bg-danger">핵심</span>
                                            {% elif detail.key_control == '비핵심' %}
                                                <span class="badge bg-secondary">비핵심</span>
                                            {% else %}
                                                <span class="badge bg-warning">미설정</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_name }}">
                                                <strong>{{ detail.control_name }}</strong>
                                            </span>
                                        </td>
                                        <td>
                                            {% if detail.control_description %}
                                                <span class="text-truncate-custom" title="{{ detail.control_description }}">
                                                    {{ detail.control_description }}
                                                </span>
                                            {% else %}
                                                <span class="text-muted">-</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_frequency_name or detail.control_frequency or '-' }}">
                                                {{ detail.control_frequency_name or detail.control_frequency or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_type_name or detail.control_type or '-' }}">
                                                {{ detail.control_type_name or detail.control_type or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_nature_name or detail.control_nature or '-' }}">
                                                {{ detail.control_nature_name or detail.control_nature or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.population or '-' }}">
                                                {{ detail.population or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            {% if detail.test_procedure %}
                                                <span class="text-truncate-custom" title="{{ detail.test_procedure }}">
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
                            <p class="text-muted">Excel 파일을 업로드하여 통제 데이터를 추가해주세요.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Excel 다운로드 기능
        function exportToExcel() {
            const table = document.getElementById('rcmTable');
            if (!table) {
                alert('다운로드할 데이터가 없습니다.');
                return;
            }
            
            let csv = '';
            const rows = table.querySelectorAll('tr');
            
            for (let i = 0; i < rows.length; i++) {
                const cols = rows[i].querySelectorAll('td, th');
                const rowData = [];
                
                for (let j = 0; j < cols.length; j++) {
                    let cellData = cols[j].textContent.trim();
                    // CSV용 특수문자 처리
                    cellData = cellData.replace(/"/g, '""');
                    if (cellData.includes(',') || cellData.includes('"') || cellData.includes('\n')) {
                        cellData = '"' + cellData + '"';
                    }
                    rowData.push(cellData);
                }
                csv += rowData.join(',') + '\n';
            }
            
            // BOM 추가 (한글 깨짐 방지)
            const bom = '\uFEFF';
            const csvContent = bom + csv;
            
            // 다운로드
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', '{{ rcm_info.rcm_name }}_통제목록.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
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