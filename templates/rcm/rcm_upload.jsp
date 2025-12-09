<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 업로드 - Snowball</title>
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
            <h1><i class="fas fa-upload me-2"></i>RCM 업로드</h1>
            <a href="{{ url_for('rcm.rcm_list') }}" class="btn btn-outline-secondary">
                <i class="fas fa-arrow-left me-1"></i>목록으로
            </a>
        </div>

        <div class="card">
            <div class="card-body">
                <form id="rcmUploadForm" enctype="multipart/form-data">
                    <div class="mb-3">
                        <label for="rcm_name" class="form-label">RCM 이름 <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="rcm_name" name="rcm_name" required>
                    </div>

                    <div class="mb-3">
                        <label for="control_category" class="form-label">통제 카테고리 <span class="text-danger">*</span></label>
                        <select class="form-select" id="control_category" name="control_category" required>
                            <option value="ELC">ELC - Entity Level Controls (전사적 통제)</option>
                            <option value="TLC">TLC - Transaction Level Controls (거래 수준 통제)</option>
                            <option value="ITGC" selected>ITGC - IT General Controls (IT 일반 통제)</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label for="description" class="form-label">설명</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>

                    <div class="mb-3">
                        <label for="rcm_file" class="form-label">Excel 파일 <span class="text-danger">*</span></label>
                        <input type="file" class="form-control" id="rcm_file" name="rcm_file" accept=".xlsx,.xls" required>
                        <div class="form-text">
                            <i class="fas fa-info-circle me-1"></i>
                            .xlsx 또는 .xls 형식의 Excel 파일만 업로드 가능합니다.
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">접근 권한 부여 (선택)</label>
                        <select class="form-select" id="access_users" name="access_users" multiple size="10">
                            {% for user in users %}
                            <option value="{{ user.user_id }}">
                                {{ user.company_name or '(회사명 없음)' }} - {{ user.user_name }} ({{ user.user_email }})
                            </option>
                            {% endfor %}
                        </select>
                        <div class="form-text">
                            <i class="fas fa-info-circle me-1"></i>
                            Ctrl(Cmd) + 클릭으로 여러 사용자를 선택할 수 있습니다. 선택하지 않으면 업로드한 관리자만 접근 가능합니다.
                        </div>
                    </div>

                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-gradient btn-lg">
                            <i class="fas fa-upload me-2"></i>업로드
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 업로드 안내 -->
        <div class="card mt-4">
            <div class="card-header bg-info text-white">
                <i class="fas fa-question-circle me-2"></i>업로드 안내
            </div>
            <div class="card-body">
                <h5>Excel 파일 형식</h5>
                <ul>
                    <li>첫 번째 행은 컬럼명으로 사용됩니다</li>
                    <li>각 행은 하나의 통제 항목을 나타냅니다</li>
                    <li>빈 행은 자동으로 제외됩니다</li>
                </ul>

                <h5 class="mt-3">카테고리 설명</h5>
                <ul>
                    <li><strong>ELC (Entity Level Controls)</strong>: 전사적 통제 - 조직 전체에 영향을 미치는 통제</li>
                    <li><strong>TLC (Transaction Level Controls)</strong>: 거래 수준 통제 - 개별 거래에 대한 통제</li>
                    <li><strong>ITGC (IT General Controls)</strong>: IT 일반 통제 - IT 시스템 및 인프라에 대한 통제</li>
                </ul>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('rcmUploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            // 선택된 사용자들을 배열로 변환
            const accessUsers = Array.from(document.getElementById('access_users').selectedOptions)
                                     .map(option => option.value);

            // 기존 access_users 제거 후 JSON 형태로 추가
            formData.delete('access_users');
            accessUsers.forEach(userId => {
                formData.append('access_users', userId);
            });

            try {
                const response = await fetch('{{ url_for("rcm.rcm_process_upload") }}', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    alert('RCM이 성공적으로 업로드되었습니다.');
                    window.location.href = '{{ url_for("rcm.rcm_list") }}';
                } else {
                    alert('업로드 실패: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('업로드 중 오류가 발생했습니다.');
            }
        });
    </script>
</body>
</html>
