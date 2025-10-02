<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>APD01 운영평가</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h2><i class="fas fa-user-shield me-2"></i>APD01 운영평가</h2>
                        <p class="text-muted mb-0">사용자 권한 부여 승인 테스트</p>
                    </div>
                    <div>
                        <a href="/operation-evaluation/rcm" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-1"></i>돌아가기
                        </a>
                    </div>
                </div>
                <hr>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-info-circle me-2"></i>통제 정보</h5>
                    </div>
                    <div class="card-body">
                        <strong>통제코드:</strong> {{ control_code }} &nbsp;|&nbsp;
                        <strong>통제명:</strong> {{ control_name }}
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4" id="step1">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-upload me-2"></i>Step 1: 모집단 업로드</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <strong>필수 컬럼:</strong> 사용자ID, 사용자명, 부서명, 권한명, 권한부여일
                        </div>

                        <div class="mb-3">
                            <label class="form-label">모집단 엑셀 파일</label>
                            <input type="file" class="form-control" id="populationFile" accept=".xlsx,.xls">
                        </div>

                        <div class="mb-3">
                            <label class="form-label">필드 매핑 (0부터 시작, A열=0, B열=1...)</label>
                            <div class="row g-2">
                                <div class="col">
                                    <input type="number" class="form-control" id="col0" value="0">
                                    <small>사용자ID</small>
                                </div>
                                <div class="col">
                                    <input type="number" class="form-control" id="col1" value="1">
                                    <small>사용자명</small>
                                </div>
                                <div class="col">
                                    <input type="number" class="form-control" id="col2" value="2">
                                    <small>부서명</small>
                                </div>
                                <div class="col">
                                    <input type="number" class="form-control" id="col3" value="3">
                                    <small>권한명</small>
                                </div>
                                <div class="col">
                                    <input type="number" class="form-control" id="col4" value="4">
                                    <small>권한부여일</small>
                                </div>
                            </div>
                        </div>

                        <button type="button" class="btn btn-primary" onclick="uploadPopulation()">
                            <i class="fas fa-upload me-1"></i>업로드 및 표본 추출
                        </button>

                        <div id="uploadResult" class="mt-3" style="display: none;">
                            <div class="alert alert-success">
                                모집단: <span id="popCount"></span>건 | 표본: <span id="sampleCount"></span>건
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4" id="step2" style="display: none;">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5><i class="fas fa-clipboard-check me-2"></i>Step 2: 표본별 테스트</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered">
                                <thead class="table-light">
                                    <tr>
                                        <th>No</th>
                                        <th>사용자ID</th>
                                        <th>사용자명</th>
                                        <th>부서</th>
                                        <th>권한</th>
                                        <th>부여일</th>
                                        <th>승인자</th>
                                        <th>승인부서</th>
                                        <th>승인일</th>
                                        <th>예외</th>
                                    </tr>
                                </thead>
                                <tbody id="sampleTable"></tbody>
                            </table>
                        </div>

                        <div class="text-end mt-3">
                            <button class="btn btn-success" onclick="saveResults()">
                                <i class="fas fa-save me-1"></i>저장
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const rcmId = {{ rcm_id }};
        const controlCode = '{{ control_code }}';
        const designSession = '{{ design_evaluation_session }}';
        let samples = [];

        function uploadPopulation() {
            const file = document.getElementById('populationFile').files[0];
            if (!file) {
                alert('파일을 선택하세요.');
                return;
            }

            const formData = new FormData();
            formData.append('population_file', file);
            formData.append('rcm_id', rcmId);
            formData.append('control_code', controlCode);
            formData.append('design_evaluation_session', designSession);

            const mapping = {
                user_id: parseInt(document.getElementById('col0').value),
                user_name: parseInt(document.getElementById('col1').value),
                department: parseInt(document.getElementById('col2').value),
                permission: parseInt(document.getElementById('col3').value),
                grant_date: parseInt(document.getElementById('col4').value)
            };
            formData.append('field_mapping', JSON.stringify(mapping));

            fetch('/api/operation-evaluation/apd01/upload-population', {
                method: 'POST',
                body: formData
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('popCount').textContent = data.population_count;
                    document.getElementById('sampleCount').textContent = data.sample_size;
                    document.getElementById('uploadResult').style.display = 'block';
                    samples = data.samples;
                    renderSamples();
                    document.getElementById('step2').style.display = 'block';
                } else {
                    alert(data.message);
                }
            })
            .catch(e => alert('오류: ' + e));
        }

        function renderSamples() {
            const tbody = document.getElementById('sampleTable');
            tbody.innerHTML = '';

            samples.forEach((s, i) => {
                const d = s.data;
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${i+1}</td>
                    <td>${d.user_id}</td>
                    <td>${d.user_name}</td>
                    <td>${d.department}</td>
                    <td>${d.permission}</td>
                    <td>${d.grant_date}</td>
                    <td><input type="text" class="form-control form-control-sm" id="appr_${i}"></td>
                    <td><input type="text" class="form-control form-control-sm" id="dept_${i}"></td>
                    <td><input type="date" class="form-control form-control-sm" id="date_${i}"></td>
                    <td>
                        <select class="form-select form-select-sm" id="exc_${i}">
                            <option value="N">N</option>
                            <option value="Y">Y</option>
                        </select>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function saveResults() {
            const results = samples.map((s, i) => ({
                sample_index: i,
                population_data: s.data,
                approver: document.getElementById(`appr_${i}`).value,
                approver_department: document.getElementById(`dept_${i}`).value,
                approve_date: document.getElementById(`date_${i}`).value,
                has_exception: document.getElementById(`exc_${i}`).value === 'Y'
            }));

            fetch('/api/operation-evaluation/apd01/save-test-results', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    rcm_id: rcmId,
                    control_code: controlCode,
                    design_evaluation_session: designSession,
                    test_results: results
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('저장되었습니다.');
                    window.location.href = '/operation-evaluation/rcm';
                } else {
                    alert(data.message);
                }
            })
            .catch(e => alert('오류: ' + e));
        }
    </script>
</body>
</html>
