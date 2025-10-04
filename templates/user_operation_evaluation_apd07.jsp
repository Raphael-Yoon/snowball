<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>APD07 운영평가</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>

    <div class="container mt-4">
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h2><i class="fas fa-database me-2"></i>APD07 운영평가</h2>
                        <p class="text-muted mb-0">데이터 직접변경 승인 테스트</p>
                    </div>
                    <div>
                        <button type="button" class="btn btn-secondary" onclick="goBack()">
                            <i class="fas fa-arrow-left me-1"></i>돌아가기
                        </button>
                    </div>
                </div>
                <hr>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
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
                    <div class="card-header bg-primary text-white">
                        <h5><i class="fas fa-upload me-2"></i>Step 1: 모집단 업로드</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <strong>필수 컬럼:</strong> 쿼리(변경내역), 변경일자
                        </div>

                        <div class="mb-3">
                            <label class="form-label">모집단 엑셀 파일</label>
                            <input type="file" class="form-control" id="populationFile" accept=".xlsx,.xls" onchange="readExcelHeaders()">
                        </div>

                        <div id="fieldMappingSection" class="mb-3" style="display: none;">
                            <label class="form-label">필드 매핑 (엑셀 컬럼을 선택하세요)</label>
                            <div class="row g-2">
                                <div class="col-md-6">
                                    <label class="form-label small">쿼리(변경내역)</label>
                                    <select class="form-select" id="col0"></select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label small">변경일자</label>
                                    <select class="form-select" id="col1"></select>
                                </div>
                            </div>
                        </div>

                        <button type="button" class="btn btn-primary" id="uploadBtn" onclick="uploadPopulation()" style="display: none;">
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
                                        <th>쿼리(변경내역)</th>
                                        <th>변경일자</th>
                                        <th>승인자</th>
                                        <th>승인일(검증)</th>
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        const rcmId = {{ rcm_id }};
        const controlCode = '{{ control_code }}';
        const designSession = '{{ design_evaluation_session }}';
        let samples = [];
        let excelHeaders = [];

        function goBack() {
            // 팝업인 경우 팝업 닫기
            if (window.opener) {
                window.close();
            } else {
                // 팝업이 아닌 경우 RCM 페이지로 이동
                window.location.href = '/operation-evaluation/rcm';
            }
        }

        function readExcelHeaders() {
            const file = document.getElementById('populationFile').files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, {type: 'array'});
                    const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                    const jsonData = XLSX.utils.sheet_to_json(firstSheet, {header: 1});

                    if (jsonData.length > 0) {
                        excelHeaders = jsonData[0];

                        // 드롭다운에 헤더 채우기
                        const selects = ['col0', 'col1'];
                        selects.forEach((selectId, idx) => {
                            const select = document.getElementById(selectId);
                            select.innerHTML = '';
                            excelHeaders.forEach((header, headerIdx) => {
                                const option = document.createElement('option');
                                option.value = headerIdx;
                                option.textContent = `${header} (${String.fromCharCode(65 + headerIdx)}열)`;
                                if (headerIdx === idx) option.selected = true;
                                select.appendChild(option);
                            });
                        });

                        // 매핑 섹션과 업로드 버튼 표시
                        document.getElementById('fieldMappingSection').style.display = 'block';
                        document.getElementById('uploadBtn').style.display = 'inline-block';
                    }
                } catch (err) {
                    alert('엑셀 파일 읽기 오류: ' + err.message);
                }
            };
            reader.readAsArrayBuffer(file);
        }

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
                change_id: parseInt(document.getElementById('col0').value),
                change_date: parseInt(document.getElementById('col1').value)
            };
            formData.append('field_mapping', JSON.stringify(mapping));

            fetch('/api/operation-evaluation/apd07/upload-population', {
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

                    // Step2로 부드럽게 스크롤
                    setTimeout(() => {
                        document.getElementById('step2').scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
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
                    <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;" title="${d.change_id || ''}">${d.change_id || ''}</td>
                    <td>${d.change_date || ''}</td>
                    <td><input type="text" class="form-control form-control-sm" id="appr_${i}" placeholder="승인자명"></td>
                    <td><input type="date" class="form-control form-control-sm" id="apprdate_${i}"></td>
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
                approval_date_verified: document.getElementById(`apprdate_${i}`).value,
                has_exception: document.getElementById(`exc_${i}`).value === 'Y'
            }));

            fetch('/api/operation-evaluation/apd07/save-test-results', {
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
                    // 팝업인 경우 부모 창 새로고침 후 팝업 닫기
                    if (window.opener) {
                        window.opener.location.reload();
                        window.close();
                    } else {
                        // 팝업이 아닌 경우 RCM 페이지로 이동
                        window.location.href = '/operation-evaluation/rcm';
                    }
                } else {
                    alert(data.message);
                }
            })
            .catch(e => alert('오류: ' + e));
        }
    </script>
</body>
</html>
