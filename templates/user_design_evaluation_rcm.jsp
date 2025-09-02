<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 설계평가 - {{ rcm_info.rcm_name }}</title>
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
                    <h1><i class="fas fa-clipboard-check me-2"></i>RCM 설계평가</h1>
                    <div>
                        <a href="/user/design-evaluation" class="btn btn-secondary">
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
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
                        <h5><i class="fas fa-info-circle me-2"></i>RCM 기본 정보</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="40%">RCM명:</th>
                                        <td><strong>{{ rcm_info.rcm_name }}</strong></td>
                                    </tr>
                                    <tr>
                                        <th>회사명:</th>
                                        <td>{{ rcm_info.company_name }}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-4">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="40%">총 통제 수:</th>
                                        <td><span class="badge bg-primary">{{ rcm_details|length }}개</span></td>
                                    </tr>
                                    <tr>
                                        <th>핵심 통제:</th>
                                        <td>
                                            <span class="badge bg-danger">
                                                {{ rcm_details|selectattr('key_control', 'equalto', 'Y')|list|length }}개
                                            </span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center">
                                    <h6 class="text-success">설계평가 진행률</h6>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-success" id="evaluationProgress" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                    </div>
                                    <small class="text-muted">
                                        <span id="evaluatedCount">0</span> / {{ rcm_details|length }} 통제 평가 완료
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 설계평가 통제 목록 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-list me-2"></i>통제 설계평가</h5>
                        <div>
                            <button class="btn btn-sm btn-success me-2" onclick="evaluateAllControls()">
                                <i class="fas fa-check-double me-1"></i>전체 평가
                            </button>
                            <button class="btn btn-sm btn-warning me-2" onclick="resetAllEvaluations()">
                                <i class="fas fa-undo me-1"></i>평가 초기화
                            </button>
                            <button class="btn btn-sm btn-outline-primary" onclick="exportEvaluationResult()">
                                <i class="fas fa-file-excel me-1"></i>결과 다운로드
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        {% if rcm_details %}
                        <div class="table-responsive">
                            <table class="table table-striped" id="controlsTable">
                                <thead>
                                    <tr>
                                        <th width="8%">통제코드</th>
                                        <th width="15%">통제명</th>
                                        <th width="25%">통제활동설명</th>
                                        <th width="8%">핵심통제</th>
                                        <th width="8%">통제주기</th>
                                        <th width="8%">통제유형</th>
                                        <th width="10%">설계평가</th>
                                        <th width="10%">평가결과</th>
                                        <th width="8%">조치사항</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr id="control-row-{{ loop.index }}">
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td><strong>{{ detail.control_name }}</strong></td>
                                        <td>
                                            <span class="text-truncate" style="max-width: 150px; display: inline-block;" 
                                                  title="{{ detail.control_description or '-' }}">
                                                {{ detail.control_description or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            {% if detail.key_control and detail.key_control.upper() == 'Y' %}
                                                <span class="badge bg-danger">핵심</span>
                                            {% else %}
                                                <span class="badge bg-secondary">일반</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ detail.control_frequency or '-' }}</td>
                                        <td>{{ detail.control_type or '-' }}</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-success evaluate-btn" 
                                                    onclick="openEvaluationModal({{ loop.index }}, '{{ detail.control_code }}', '{{ detail.control_name }}')"
                                                    id="eval-btn-{{ loop.index }}">
                                                <i class="fas fa-clipboard-check me-1"></i>평가
                                            </button>
                                        </td>
                                        <td>
                                            <span class="evaluation-result" id="result-{{ loop.index }}">
                                                <span class="text-muted">미평가</span>
                                            </span>
                                        </td>
                                        <td>
                                            <span class="evaluation-action" id="action-{{ loop.index }}">
                                                <span class="text-muted">-</span>
                                            </span>
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
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 설계평가 모달 -->
    <div class="modal fade" id="evaluationModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-clipboard-check me-2"></i>통제 설계평가
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- 통제 기본 정보 -->
                    <div class="card mb-4">
                        <div class="card-header bg-light">
                            <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>통제 기본 정보</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <label class="form-label"><strong>통제코드:</strong></label>
                                    <p id="modalControlCode" class="text-primary fw-bold"></p>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label"><strong>통제명:</strong></label>
                                    <p id="modalControlName" class="fw-bold"></p>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label"><strong>핵심통제:</strong></label>
                                    <p id="modalKeyControl"></p>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-4">
                                    <label class="form-label"><strong>통제주기:</strong></label>
                                    <p id="modalControlFrequency" class="text-muted"></p>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label"><strong>통제유형:</strong></label>
                                    <p id="modalControlType" class="text-muted"></p>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label"><strong>통제구분:</strong></label>
                                    <p id="modalControlNature" class="text-muted"></p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 통제활동 설명 검토 -->
                    <div class="card mb-4">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0"><i class="fas fa-search me-2"></i>통제활동 설명 검토</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label"><strong>현재 통제활동 설명:</strong></label>
                                <div class="p-3 bg-light border rounded">
                                    <p id="modalControlDescription" class="mb-0"></p>
                                </div>
                            </div>
                            
                            <div class="alert alert-info">
                                <i class="fas fa-lightbulb me-2"></i>
                                <strong>평가 기준:</strong> 위의 통제활동 설명이 해당 통제의 목적과 절차를 명확하고 구체적으로 기술하고 있는지 평가하세요.
                            </div>
                            
                            <div class="mb-3">
                                <label for="descriptionAdequacy" class="form-label">통제활동 설명 적절성 *</label>
                                <select class="form-select" id="descriptionAdequacy" required>
                                    <option value="">평가 결과 선택</option>
                                    <option value="adequate">적절함 - 명확하고 구체적으로 기술됨</option>
                                    <option value="partially_adequate">부분적으로 적절함 - 일부 보완 필요</option>
                                    <option value="inadequate">부적절함 - 불명확하거나 불충분함</option>
                                    <option value="missing">누락 - 통제활동 설명이 없음</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="improvementSuggestion" class="form-label">개선 제안사항</label>
                                <textarea class="form-control" id="improvementSuggestion" rows="3" 
                                          placeholder="통제활동 설명이 부적절한 경우, 구체적인 개선 방향을 제안하세요..."></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- 설계 효과성 종합 평가 -->
                    <div class="card mb-3">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0"><i class="fas fa-check-circle me-2"></i>설계 효과성 종합 평가</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="overallEffectiveness" class="form-label">종합 설계 효과성 *</label>
                                <select class="form-select" id="overallEffectiveness" required>
                                    <option value="">평가 결과 선택</option>
                                    <option value="effective">효과적 - 위험을 적절히 완화할 수 있도록 설계됨</option>
                                    <option value="partially_effective">부분적으로 효과적 - 일부 개선이 필요함</option>
                                    <option value="ineffective">비효과적 - 위험 완화에 부족함</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="evaluationRationale" class="form-label">평가 근거</label>
                                <textarea class="form-control" id="evaluationRationale" rows="3" 
                                          placeholder="위 평가 결과를 선택한 구체적인 근거를 기술하세요..."></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <label for="recommendedActions" class="form-label">권고 조치사항</label>
                                <textarea class="form-control" id="recommendedActions" rows="2" 
                                          placeholder="설계 개선을 위한 구체적인 조치사항을 제안하세요..."></textarea>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-success" onclick="saveEvaluation()">
                        <i class="fas fa-save me-1"></i>평가 저장
                    </button>
                </div>
            </div>
        </div>
    </div>


    <!-- 샘플 업로드 모달 -->
    <div class="modal fade" id="sampleUploadModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-upload me-2"></i>설계평가 샘플 업로드
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>업로드 안내:</strong> 설계평가 결과가 포함된 CSV 또는 Excel 파일을 업로드하여 일괄 적용할 수 있습니다.
                    </div>
                    
                    <!-- 파일 업로드 -->
                    <div class="mb-4">
                        <label for="evaluationFile" class="form-label">평가 결과 파일 선택</label>
                        <input class="form-control" type="file" id="evaluationFile" accept=".csv,.xlsx,.xls">
                        <div class="form-text">지원 형식: CSV, Excel (.xlsx, .xls)</div>
                    </div>
                    
                    <!-- 파일 형식 가이드 -->
                    <div class="mb-4">
                        <h6><i class="fas fa-table me-2"></i>파일 형식 가이드</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered">
                                <thead>
                                    <tr class="table-light">
                                        <th>통제코드</th>
                                        <th>설명적절성</th>
                                        <th>개선제안</th>
                                        <th>종합효과성</th>
                                        <th>평가근거</th>
                                        <th>권고조치사항</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>C001</td>
                                        <td>adequate</td>
                                        <td>개선사항 없음</td>
                                        <td>effective</td>
                                        <td>통제가 적절히 설계됨</td>
                                        <td>현행 유지</td>
                                    </tr>
                                    <tr class="table-light">
                                        <td colspan="6" class="text-center small text-muted">
                                            설명적절성: adequate/partially_adequate/inadequate/missing<br>
                                            종합효과성: effective/partially_effective/ineffective
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- 샘플 파일 다운로드 -->
                    <div class="mb-3">
                        <h6><i class="fas fa-download me-2"></i>샘플 파일</h6>
                        <button class="btn btn-sm btn-outline-primary" onclick="downloadSampleTemplate()">
                            <i class="fas fa-file-csv me-1"></i>샘플 템플릿 다운로드
                        </button>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-info" onclick="uploadEvaluationFile()">
                        <i class="fas fa-upload me-1"></i>업로드 및 적용
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- 설계평가 JavaScript -->
    <script>
        let currentEvaluationIndex = null;
        let evaluationResults = {};
        const rcmId = {{ rcm_id }};
        
        // 페이지 로드 시 기존 평가 결과 불러오기
        document.addEventListener('DOMContentLoaded', function() {
            loadExistingEvaluations();
        });
        
        // 기존 평가 결과 불러오기
        function loadExistingEvaluations() {
            fetch(`/api/design-evaluation/load/${rcmId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.evaluations) {
                        // 컨트롤 코드를 인덱스로 매핑
                        {% for detail in rcm_details %}
                        const controlCode{{ loop.index }} = '{{ detail.control_code }}';
                        if (data.evaluations[controlCode{{ loop.index }}]) {
                            evaluationResults[{{ loop.index }}] = data.evaluations[controlCode{{ loop.index }}];
                            updateEvaluationUI({{ loop.index }}, data.evaluations[controlCode{{ loop.index }}]);
                        }
                        {% endfor %}
                        
                        updateProgress();
                    }
                })
                .catch(error => {
                    console.error('기존 평가 결과 불러오기 오류:', error);
                });
        }
        
        // 평가 모달 열기
        function openEvaluationModal(index, controlCode, controlName) {
            currentEvaluationIndex = index;
            
            // 해당 행의 데이터 가져오기
            const row = document.getElementById(`control-row-${index}`);
            const cells = row.querySelectorAll('td');
            
            // 모달에 기본 정보 설정
            document.getElementById('modalControlCode').textContent = controlCode;
            document.getElementById('modalControlName').textContent = controlName;
            
            // 통제 세부 정보 설정
            const description = cells[2].textContent.trim();
            const keyControl = cells[3].textContent.trim();
            const frequency = cells[4].textContent.trim();
            const type = cells[5].textContent.trim();
            
            document.getElementById('modalControlDescription').textContent = description || '통제활동 설명이 등록되지 않았습니다.';
            document.getElementById('modalKeyControl').innerHTML = keyControl.includes('핵심') ? 
                '<span class="badge bg-danger">핵심통제</span>' : '<span class="badge bg-secondary">일반통제</span>';
            document.getElementById('modalControlFrequency').textContent = frequency || '-';
            document.getElementById('modalControlType').textContent = type || '-';
            
            // RCM 세부 데이터에서 통제구분 찾기
            {% for detail in rcm_details %}
            if ({{ loop.index }} === index) {
                document.getElementById('modalControlNature').textContent = '{{ detail.control_nature or "-" }}';
            }
            {% endfor %}
            
            // 기존 평가 결과가 있다면 로드
            if (evaluationResults[index]) {
                const result = evaluationResults[index];
                document.getElementById('descriptionAdequacy').value = result.adequacy || '';
                document.getElementById('improvementSuggestion').value = result.improvement || '';
                document.getElementById('overallEffectiveness').value = result.effectiveness || '';
                document.getElementById('evaluationRationale').value = result.rationale || '';
                document.getElementById('recommendedActions').value = result.actions || '';
            } else {
                // 폼 초기화
                document.getElementById('descriptionAdequacy').value = '';
                document.getElementById('improvementSuggestion').value = '';
                document.getElementById('overallEffectiveness').value = '';
                document.getElementById('evaluationRationale').value = '';
                document.getElementById('recommendedActions').value = '';
            }
            
            const modal = new bootstrap.Modal(document.getElementById('evaluationModal'));
            modal.show();
        }
        
        // 평가 결과 저장
        function saveEvaluation() {
            const adequacy = document.getElementById('descriptionAdequacy').value;
            const effectiveness = document.getElementById('overallEffectiveness').value;
            
            if (!adequacy) {
                alert('통제활동 설명 적절성 평가는 필수 항목입니다.');
                return;
            }
            
            if (!effectiveness) {
                alert('종합 설계 효과성 평가는 필수 항목입니다.');
                return;
            }
            
            const evaluation = {
                adequacy: adequacy,
                improvement: document.getElementById('improvementSuggestion').value,
                effectiveness: effectiveness,
                rationale: document.getElementById('evaluationRationale').value,
                actions: document.getElementById('recommendedActions').value
            };
            
            // 서버에 결과 저장
            const controlCode = {% for detail in rcm_details %}
                {{ loop.index }} === currentEvaluationIndex ? '{{ detail.control_code }}' : 
            {% endfor %} null;
            
            if (controlCode) {
                fetch('/api/design-evaluation/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        rcm_id: rcmId,
                        control_code: controlCode,
                        evaluation_data: evaluation
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 로컬에 결과 저장
                        evaluationResults[currentEvaluationIndex] = evaluation;
                        
                        // UI 업데이트
                        updateEvaluationUI(currentEvaluationIndex, evaluation);
                        
                        // 진행률 업데이트
                        updateProgress();
                        
                        alert('설계평가 결과가 저장되었습니다.');
                    } else {
                        alert('저장 실패: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('저장 오류:', error);
                    alert('저장 중 오류가 발생했습니다.');
                });
            }
            
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('evaluationModal'));
            modal.hide();
        }
        
        // 평가 결과 UI 업데이트
        function updateEvaluationUI(index, evaluation) {
            const resultElement = document.getElementById(`result-${index}`);
            const actionElement = document.getElementById(`action-${index}`);
            const buttonElement = document.getElementById(`eval-btn-${index}`);
            
            // 결과 표시 (종합 효과성 기준)
            let resultClass = '';
            let resultText = '';
            switch(evaluation.effectiveness) {
                case 'effective':
                    resultClass = 'bg-success';
                    resultText = '효과적';
                    break;
                case 'partially_effective':
                    resultClass = 'bg-warning';
                    resultText = '부분적 효과적';
                    break;
                case 'ineffective':
                    resultClass = 'bg-danger';
                    resultText = '비효과적';
                    break;
            }
            
            // 설명 적절성도 함께 표시
            let adequacyText = '';
            switch(evaluation.adequacy) {
                case 'adequate':
                    adequacyText = '설명 적절';
                    break;
                case 'partially_adequate':
                    adequacyText = '설명 부분적';
                    break;
                case 'inadequate':
                    adequacyText = '설명 부적절';
                    break;
                case 'missing':
                    adequacyText = '설명 누락';
                    break;
            }
            
            resultElement.innerHTML = `
                <span class="badge ${resultClass}">${resultText}</span>
                <br><small class="text-muted">(${adequacyText})</small>
            `;
            
            actionElement.innerHTML = evaluation.actions || '<span class="text-muted">-</span>';
            
            // 버튼 상태 변경
            buttonElement.innerHTML = '<i class="fas fa-check me-1"></i>완료';
            buttonElement.classList.remove('btn-outline-success');
            buttonElement.classList.add('btn-success');
        }
        
        // 진행률 업데이트
        function updateProgress() {
            const totalControls = {{ rcm_details|length }};
            const evaluatedCount = Object.keys(evaluationResults).length;
            const progress = Math.round((evaluatedCount / totalControls) * 100);
            
            document.getElementById('evaluationProgress').style.width = `${progress}%`;
            document.getElementById('evaluationProgress').setAttribute('aria-valuenow', progress);
            document.getElementById('evaluationProgress').textContent = `${progress}%`;
            document.getElementById('evaluatedCount').textContent = evaluatedCount;
        }
        
        // 전체 평가 (샘플 데이터로 자동 평가)
        function evaluateAllControls() {
            if (!confirm('모든 통제에 대해 샘플 설계평가를 수행하시겠습니까?\n(실제 업무에서는 각 통제를 개별적으로 검토해야 합니다)')) {
                return;
            }
            
            const totalControls = {{ rcm_details|length }};
            const sampleAdequacies = ['adequate', 'partially_adequate', 'inadequate', 'missing'];
            const sampleEffectiveness = ['effective', 'partially_effective', 'ineffective'];
            
            for (let i = 1; i <= totalControls; i++) {
                if (!evaluationResults[i]) {
                    const adequacy = sampleAdequacies[Math.floor(Math.random() * sampleAdequacies.length)];
                    const effectiveness = sampleEffectiveness[Math.floor(Math.random() * sampleEffectiveness.length)];
                    
                    let improvementText = '';
                    let actionText = '';
                    
                    if (adequacy === 'inadequate' || adequacy === 'missing') {
                        improvementText = '통제활동 설명을 보다 구체적이고 명확하게 기술하여 실행 담당자가 이해하기 쉽도록 개선이 필요합니다.';
                    }
                    
                    if (effectiveness === 'partially_effective' || effectiveness === 'ineffective') {
                        actionText = '통제 설계의 효과성 개선을 위한 추가 검토 및 보완 조치가 필요합니다.';
                    }
                    
                    const evaluation = {
                        adequacy: adequacy,
                        improvement: improvementText,
                        effectiveness: effectiveness,
                        rationale: '자동 평가로 생성된 샘플 평가 근거입니다. 실제로는 상세한 검토가 필요합니다.',
                        actions: actionText
                    };
                    
                    evaluationResults[i] = evaluation;
                    updateEvaluationUI(i, evaluation);
                }
            }
            
            updateProgress();
            alert('전체 설계평가가 완료되었습니다.');
        }
        
        // 평가 초기화
        function resetAllEvaluations() {
            if (!confirm('모든 설계평가 결과를 초기화하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) {
                return;
            }
            
            // 서버에서 평가 데이터 삭제
            fetch('/api/design-evaluation/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rcm_id: rcmId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 로컬 데이터 초기화
                    evaluationResults = {};
                    
                    // UI 초기화
                    const totalControls = {{ rcm_details|length }};
                    for (let i = 1; i <= totalControls; i++) {
                        resetEvaluationUI(i);
                    }
                    
                    // 진행률 초기화
                    updateProgress();
                    
                    alert('모든 설계평가가 초기화되었습니다.');
                } else {
                    alert('초기화 실패: ' + data.message);
                }
            })
            .catch(error => {
                console.error('초기화 오류:', error);
                alert('초기화 중 오류가 발생했습니다.');
            });
        }
        
        // 개별 평가 UI 초기화
        function resetEvaluationUI(index) {
            const resultElement = document.getElementById(`result-${index}`);
            const actionElement = document.getElementById(`action-${index}`);
            const buttonElement = document.getElementById(`eval-btn-${index}`);
            
            // 결과 초기화
            resultElement.innerHTML = '<span class="text-muted">미평가</span>';
            actionElement.innerHTML = '<span class="text-muted">-</span>';
            
            // 버튼 초기화
            buttonElement.innerHTML = '<i class="fas fa-clipboard-check me-1"></i>평가';
            buttonElement.classList.remove('btn-success');
            buttonElement.classList.add('btn-outline-success');
        }
        
        // 평가 결과 다운로드
        function exportEvaluationResult() {
            if (Object.keys(evaluationResults).length === 0) {
                alert('다운로드할 평가 결과가 없습니다.');
                return;
            }
            
            // CSV 데이터 생성
            let csv = '통제코드,통제명,통제활동설명,설명적절성,개선제안,종합효과성,평가근거,권고조치사항\n';
            
            {% for detail in rcm_details %}
            const index{{ loop.index }} = {{ loop.index }};
            if (evaluationResults[index{{ loop.index }}]) {
                const result = evaluationResults[index{{ loop.index }}];
                
                const adequacyText = {
                    'adequate': '적절함',
                    'partially_adequate': '부분적으로 적절함',
                    'inadequate': '부적절함',
                    'missing': '누락'
                }[result.adequacy] || '';
                
                const effectivenessText = {
                    'effective': '효과적',
                    'partially_effective': '부분적으로 효과적',
                    'ineffective': '비효과적'
                }[result.effectiveness] || '';
                
                const controlDescription = `{{ detail.control_description or '없음' }}`.replace(/"/g, '""');
                const improvement = (result.improvement || '').replace(/"/g, '""');
                const rationale = (result.rationale || '').replace(/"/g, '""');
                const actions = (result.actions || '').replace(/"/g, '""');
                
                csv += `"{{ detail.control_code }}","{{ detail.control_name }}","${controlDescription}","${adequacyText}","${improvement}","${effectivenessText}","${rationale}","${actions}"\n`;
            }
            {% endfor %}
            
            // BOM 추가 (한글 깨짐 방지)
            const bom = '\uFEFF';
            const csvContent = bom + csv;
            
            // 다운로드
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', '{{ rcm_info.rcm_name }}_설계평가결과.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        

        // 샘플 업로드 모달 표시 (일괄 업로드용)
        function showSampleUploadModal() {
            const modal = new bootstrap.Modal(document.getElementById('sampleUploadModal'));
            modal.show();
        }
        
        // 샘플 템플릿 다운로드
        function downloadSampleTemplate() {
            // 현재 RCM의 통제 코드를 기반으로 샘플 템플릿 생성
            let csv = '통제코드,설명적절성,개선제안,종합효과성,평가근거,권고조치사항\n';
            
            {% for detail in rcm_details %}
            csv += `"{{ detail.control_code }}","adequate","","effective","",""\n`;
            {% endfor %}
            
            // BOM 추가 (한글 깨짐 방지)
            const bom = '\uFEFF';
            const csvContent = bom + csv;
            
            // 다운로드
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', '{{ rcm_info.rcm_name }}_설계평가_템플릿.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        // 평가 파일 업로드
        function uploadEvaluationFile() {
            const fileInput = document.getElementById('evaluationFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('업로드할 파일을 선택해주세요.');
                return;
            }
            
            // 파일 형식 확인
            const fileName = file.name.toLowerCase();
            if (!fileName.endsWith('.csv') && !fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
                alert('CSV 또는 Excel 파일만 업로드 가능합니다.');
                return;
            }
            
            // CSV 파일 처리
            if (fileName.endsWith('.csv')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        processCsvData(e.target.result);
                    } catch (error) {
                        console.error('CSV 파싱 오류:', error);
                        alert('CSV 파일 처리 중 오류가 발생했습니다.');
                    }
                };
                reader.readAsText(file, 'UTF-8');
            } else {
                // Excel 파일은 서버에서 처리 필요
                alert('Excel 파일 처리는 향후 지원 예정입니다. 현재는 CSV 파일만 사용해주세요.');
            }
        }
        
        // CSV 데이터 처리
        function processCsvData(csvText) {
            const lines = csvText.split('\n');
            if (lines.length < 2) {
                alert('파일에 데이터가 없습니다.');
                return;
            }
            
            // 헤더 확인
            const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
            const expectedHeaders = ['통제코드', '설명적절성', '개선제안', '종합효과성', '평가근거', '권고조치사항'];
            
            // 통제코드 인덱스 맵 생성
            const controlCodeToIndex = {};
            {% for detail in rcm_details %}
            controlCodeToIndex['{{ detail.control_code }}'] = {{ loop.index }};
            {% endfor %}
            
            let uploadedCount = 0;
            const promises = [];
            
            // 데이터 행 처리
            for (let i = 1; i < lines.length; i++) {
                const line = lines[i].trim();
                if (!line) continue;
                
                const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
                if (values.length < 6) continue;
                
                const controlCode = values[0];
                const index = controlCodeToIndex[controlCode];
                
                if (index) {
                    const evaluation = {
                        adequacy: values[1] || '',
                        improvement: values[2] || '',
                        effectiveness: values[3] || '',
                        rationale: values[4] || '',
                        actions: values[5] || ''
                    };
                    
                    // 서버에 저장
                    const promise = fetch('/api/design-evaluation/save', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            rcm_id: rcmId,
                            control_code: controlCode,
                            evaluation_data: evaluation
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // 로컬에 결과 저장
                            evaluationResults[index] = evaluation;
                            updateEvaluationUI(index, evaluation);
                            uploadedCount++;
                        }
                    });
                    
                    promises.push(promise);
                }
            }
            
            // 모든 업로드 완료 후 처리
            Promise.all(promises).then(() => {
                updateProgress();
                
                // 모달 닫기
                const modal = bootstrap.Modal.getInstance(document.getElementById('sampleUploadModal'));
                modal.hide();
                
                // 파일 입력 초기화
                document.getElementById('evaluationFile').value = '';
                
                alert(`${uploadedCount}개의 설계평가 결과가 업로드되었습니다.`);
            }).catch(error => {
                console.error('업로드 오류:', error);
                alert('일부 데이터 업로드 중 오류가 발생했습니다.');
            });
        }
    </script>
</body>
</html>