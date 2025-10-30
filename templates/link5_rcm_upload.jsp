<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 업로드 - SnowBall</title>
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
            <a href="{{ url_for('link5.user_rcm') }}" class="btn btn-outline-secondary">
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
                        <label for="header_row" class="form-label">데이터 시작 행 (선택)</label>
                        <input type="number" class="form-control" id="header_row" name="header_row" value="0" min="0" max="20">
                        <div class="form-text">
                            <i class="fas fa-info-circle me-1"></i>
                            헤더가 있는 행 번호를 입력하세요 (0부터 시작). 기본값: 0 (첫 번째 행)
                        </div>
                    </div>

                    {% if users|length > 1 %}
                    <div class="mb-3">
                        <label class="form-label">접근 권한 부여 (선택)</label>
                        <select class="form-select" id="access_users" name="access_users" multiple size="10">
                            {% for user in users %}
                            <option value="{{ user.user_id }}">
                                {% if is_admin %}{{ user.company_name or '(회사명 없음)' }} - {% endif %}{{ user.user_name }} ({{ user.user_email }})
                            </option>
                            {% endfor %}
                        </select>
                        <div class="form-text">
                            <i class="fas fa-info-circle me-1"></i>
                            Ctrl(Cmd) + 클릭으로 여러 사용자를 선택할 수 있습니다.
                            {% if is_admin %}
                            선택하지 않으면 업로드한 관리자만 접근 가능합니다.
                            {% else %}
                            업로드한 사용자는 자동으로 관리 권한이 부여됩니다.
                            {% endif %}
                        </div>
                    </div>
                    {% endif %}

                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-gradient btn-lg">
                            <i class="fas fa-upload me-2"></i>업로드
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 중요 안내 -->
        <div class="alert alert-warning mt-4">
            <h5 class="alert-heading">
                <i class="fas fa-exclamation-triangle me-2"></i>RCM 수정 관련 안내
            </h5>
            <hr>
            <p class="mb-2">
                <strong>한번 업로드된 RCM은 수정할 수 없습니다.</strong>
            </p>
            <p class="mb-2">
                업로드된 RCM은 현재 진행 중인 평가에서 사용되고 있을 수 있으며, 수정 시 평가 데이터의 일관성이 깨질 수 있습니다.
            </p>
            <p class="mb-0">
                <i class="fas fa-lightbulb me-1 text-warning"></i>
                <strong>RCM 내용을 수정해야 하는 경우:</strong>
            </p>
            <ol class="mb-0 mt-2">
                <li>RCM 목록에서 기존 RCM을 <strong>삭제</strong>합니다</li>
                <li>수정된 내용으로 <strong>새로운 RCM을 업로드</strong>합니다</li>
            </ol>
            <div class="mt-3 p-2 bg-light border-start border-info border-3">
                <p class="mb-1"><strong>📋 평가 진행 중 RCM 변경 정책:</strong></p>
                <ul class="mb-0 small">
                    <li><strong class="text-danger">운영평가 진행 중</strong>: RCM 삭제 불가 ⛔</li>
                    <li><strong class="text-warning">설계평가 진행 중</strong>: 경고 후 삭제 가능 ⚠️ (평가 데이터 삭제됨)</li>
                    <li><strong class="text-success">평가 없음</strong>: 자유롭게 삭제 가능 ✅</li>
                </ul>
            </div>
            <p class="mb-0 mt-2">
                <small class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    본인이 업로드한 RCM은 자동으로 삭제 권한이 부여됩니다.
                </small>
            </p>
        </div>

        <!-- 업로드 안내 -->
        <div class="card mt-4">
            <div class="card-header bg-info text-white">
                <i class="fas fa-question-circle me-2"></i>업로드 안내
            </div>
            <div class="card-body">
                <h5>Excel 파일 형식</h5>
                <ul>
                    <li>기본적으로 첫 번째 행(0행)을 컬럼명으로 사용합니다</li>
                    <li>헤더가 여러 줄인 경우 "데이터 시작 행"을 지정하세요 (예: 헤더가 3줄이면 2를 입력)</li>
                    <li>각 행은 하나의 통제 항목을 나타냅니다</li>
                    <li>빈 행은 자동으로 제외됩니다</li>
                    <li>컬럼명은 영문/한글 모두 지원하며 자동으로 매핑됩니다</li>
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
                const response = await fetch('{{ url_for("link5.rcm_process_upload") }}', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    alert('RCM이 성공적으로 업로드되었습니다.');
                    window.location.href = '{{ url_for("link5.user_rcm") }}';
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
