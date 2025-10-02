<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 운영평가 - {{ rcm_info.rcm_name }}</title>
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
                    <div>
                        <h1><i class="fas fa-cogs me-2"></i>RCM 운영평가</h1>
                        <div class="text-warning fw-bold fs-6 mt-1">
                            설계평가 세션: <span class="badge bg-warning text-dark">{{ evaluation_session }}</span>
                        </div>
                    </div>
                    <div>
                        <a href="/user/operation-evaluation" class="btn btn-secondary">
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
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark">
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
                                        <td><span class="badge bg-warning text-dark">{{ rcm_details|length }}개</span></td>
                                    </tr>
                                    <tr>
                                        <th>평가자:</th>
                                        <td><strong>{{ user_info.user_name }}</strong></td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center">
                                    <h6 class="text-warning">운영평가 진행률</h6>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-warning" id="evaluationProgress" role="progressbar" style="width: 0%; font-size: 12px;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                    </div>
                                    <small class="text-muted">
                                        <span id="evaluatedCount">0</span> / <span id="totalControlCount">{{ rcm_details|length }}</span> 통제 평가 완료
                                        <br>상태: <span id="evaluationStatus" class="badge bg-secondary">준비 중</span>
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 운영평가 통제 목록 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-list me-2"></i>통제 운영평가</h5>
                        <div class="d-flex flex-wrap gap-2">
                            <button id="completeEvaluationBtn" class="btn btn-sm btn-warning" onclick="completeEvaluation()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;" title="운영평가를 완료 처리합니다" data-bs-toggle="tooltip">
                                <i class="fas fa-check me-1"></i>완료처리
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="resetAllEvaluations()" style="height: 70%; padding: 0.2rem 0.5rem;">
                                <i class="fas fa-undo me-1"></i>초기화
                            </button>
                            <button id="downloadBtn" class="btn btn-sm btn-outline-warning" onclick="exportEvaluationResult()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;">
                                <i class="fas fa-file-excel me-1"></i>다운로드
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
                                        <th width="14%">통제명</th>
                                        <th width="22%">통제활동설명</th>
                                        <th width="7%">통제주기</th>
                                        <th width="7%">통제유형</th>
                                        <th width="7%">통제구분</th>
                                        <th width="10%">운영평가</th>
                                        <th width="10%">평가결과</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr id="control-row-{{ loop.index }}">
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td><strong>{{ detail.control_name }}</strong></td>
                                        <td>
                                            <div style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; max-height: calc(1.4em * 2);"
                                                 title="{{ detail.control_description or '-' }}" data-bs-toggle="tooltip">
                                                {{ detail.control_description or '-' }}
                                            </div>
                                        </td>
                                        <td>{{ detail.control_frequency_name or detail.control_frequency or '-' }}</td>
                                        <td>{{ detail.control_type_name or detail.control_type or '-' }}</td>
                                        <td>{{ detail.control_nature_name or detail.control_nature or '-' }}</td>
                                        <td>
                                            <button class="btn btn-warning btn-sm w-100"
                                                    data-control-code="{{ detail.control_code }}"
                                                    data-control-name="{{ detail.control_name }}"
                                                    data-control-frequency="{{ detail.control_frequency_name or detail.control_frequency|e }}"
                                                    data-control-type="{{ detail.control_type_name or detail.control_type|e }}"
                                                    data-control-nature="{{ detail.control_nature_name or detail.control_nature|e }}"
                                                    data-test-procedure="{{ detail.test_procedure|e }}"
                                                    data-row-index="{{ loop.index }}"
                                                    onclick="openOperationEvaluationModal(this)">
                                                <i class="fas fa-edit me-1"></i>평가
                                            </button>
                                        </td>
                                        <td>
                                            <span id="evaluation-result-{{ loop.index }}" class="badge bg-secondary">미평가</span>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-5">
                            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                            <h5>통제 데이터가 없습니다</h5>
                            <p class="text-muted">해당 RCM에 통제 데이터가 존재하지 않습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 운영평가 모달 -->
    <div class="modal fade" id="operationEvaluationModal" tabindex="-1" aria-labelledby="operationEvaluationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-warning text-dark">
                    <h5 class="modal-title" id="operationEvaluationModalLabel">
                        <i class="fas fa-cogs me-2"></i>운영평가
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-bold">통제 정보</label>
                        <div class="p-3 bg-light rounded">
                            <div class="row">
                                <div class="col-md-3">
                                    <strong>통제코드:</strong> <span id="modal-control-code"></span>
                                </div>
                                <div class="col-md-3">
                                    <strong>통제주기:</strong> <span id="modal-control-frequency" class="text-muted">-</span>
                                </div>
                                <div class="col-md-6">
                                    <strong>통제명:</strong> <span id="modal-control-name"></span>
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-md-3">
                                    <strong>통제유형:</strong> <span id="modal-control-type" class="text-muted">-</span>
                                </div>
                                <div class="col-md-3">
                                    <strong>통제구분:</strong> <span id="modal-control-nature" class="text-muted">-</span>
                                </div>
                                <div class="col-md-6">
                                    <!-- 빈 공간 또는 추가 정보용 -->
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-12">
                                    <strong>테스트절차:</strong>
                                    <div class="mt-1 p-2 border rounded bg-white" style="max-height: 120px; overflow-y: auto;">
                                        <span id="modal-test-procedure" class="text-muted">-</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <form id="operationEvaluationForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="operating_effectiveness" class="form-label fw-bold">운영 효과성</label>
                                    <select class="form-select" id="operating_effectiveness" name="operating_effectiveness" required>
                                        <option value="">선택하세요</option>
                                        <option value="effective">효과적</option>
                                        <option value="deficient">미흡</option>
                                        <option value="ineffective">비효과적</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="sample_size" class="form-label fw-bold">표본 크기</label>
                                    <input type="number" class="form-control" id="sample_size" name="sample_size" min="1" placeholder="통제주기에 따라 자동 설정">
                                    <div class="form-text">
                                        <small>권장 표본수: 연간(1), 분기(2), 월(2), 주(5), 일(20), 기타(1)</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="exception_count" class="form-label fw-bold">예외 발견 수</label>
                                    <input type="number" class="form-control" id="exception_count" name="exception_count" min="0" placeholder="예: 0">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="conclusion" class="form-label fw-bold">결론</label>
                                    <select class="form-select" id="conclusion" name="conclusion" required>
                                        <option value="">선택하세요</option>
                                        <option value="satisfactory">만족</option>
                                        <option value="deficiency">결함</option>
                                        <option value="material_weakness">중요한 결함</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="exception_details" class="form-label fw-bold">예외사항 세부내용</label>
                            <textarea class="form-control" id="exception_details" name="exception_details" rows="3" placeholder="발견된 예외사항의 세부내용을 기록하세요"></textarea>
                        </div>

                        <div class="mb-3">
                            <label for="improvement_plan" class="form-label fw-bold">개선계획</label>
                            <textarea class="form-control" id="improvement_plan" name="improvement_plan" rows="3" placeholder="개선이 필요한 경우 개선계획을 작성하세요"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-warning" onclick="saveOperationEvaluation()">
                        <i class="fas fa-save me-1"></i>저장
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 전역 변수
        let currentRcmId = {{ rcm_id }};
        let currentEvaluationSession = '{{ evaluation_session }}';
        let currentControlCode = '';
        let currentRowIndex = 0;
        let evaluationDict = {{ evaluation_dict | tojson }};

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            initializeTooltips();
            updateAllEvaluationUI();
            updateProgress();
        });

        // 툴팁 초기화
        function initializeTooltips() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // 통제주기에 따른 기본 표본수 매핑 (코드값 기준)
        function getDefaultSampleSize(controlFrequency, controlType) {
            // 통제주기 코드에서 첫 글자만 추출 (lookup_name이 올 수도 있음)
            const frequencyCode = controlFrequency ? controlFrequency.charAt(0).toUpperCase() : '';

            const frequencyMapping = {
                'A': 1,  // 연간
                'Q': 2,  // 분기
                'M': 2,  // 월
                'W': 5,  // 주
                'D': 20, // 일
                'O': 1,  // 기타 (자동통제 포함)
                'N': 1   // 필요시
            };

            return frequencyMapping[frequencyCode] || 1;
        }


        // 운영평가 모달 열기
        function openOperationEvaluationModal(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');
            const controlFrequency = buttonElement.getAttribute('data-control-frequency');
            const controlType = buttonElement.getAttribute('data-control-type');
            const controlNature = buttonElement.getAttribute('data-control-nature');
            const testProcedure = buttonElement.getAttribute('data-test-procedure');
            const rowIndex = parseInt(buttonElement.getAttribute('data-row-index'));

            currentControlCode = controlCode;
            currentRowIndex = rowIndex;

            document.getElementById('modal-control-code').textContent = controlCode;
            document.getElementById('modal-control-name').textContent = controlName;
            document.getElementById('modal-control-frequency').textContent = controlFrequency || '-';
            document.getElementById('modal-control-type').textContent = controlType || '-';
            document.getElementById('modal-control-nature').textContent = controlNature || '-';
            document.getElementById('modal-test-procedure').textContent = testProcedure || '-';

            // 기존 평가 데이터 로드
            if (evaluationDict[controlCode]) {
                const data = evaluationDict[controlCode];
                document.getElementById('operating_effectiveness').value = data.operating_effectiveness || '';
                document.getElementById('sample_size').value = data.sample_size || '';
                document.getElementById('exception_count').value = data.exception_count || '';
                document.getElementById('exception_details').value = data.exception_details || '';
                document.getElementById('conclusion').value = data.conclusion || '';
                document.getElementById('improvement_plan').value = data.improvement_plan || '';
            } else {
                // 폼 초기화
                document.getElementById('operationEvaluationForm').reset();

                // 예외 발견 수 기본값 0으로 설정
                document.getElementById('exception_count').value = 0;
            }

            // 기존 평가 데이터가 없거나 표본수가 비어있는 경우 자동 설정
            if (!evaluationDict[controlCode] || !evaluationDict[controlCode].sample_size) {
                const defaultSampleSize = getDefaultSampleSize(controlFrequency, controlType);
                document.getElementById('sample_size').value = defaultSampleSize;
            }

            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('operationEvaluationModal'));
            modal.show();
        }

        // 운영평가 저장
        function saveOperationEvaluation() {
            const formData = new FormData(document.getElementById('operationEvaluationForm'));
            const evaluationData = {
                operating_effectiveness: formData.get('operating_effectiveness'),
                sample_size: parseInt(formData.get('sample_size')) || 0,
                exception_count: parseInt(formData.get('exception_count')) || 0,
                exception_details: formData.get('exception_details'),
                conclusion: formData.get('conclusion'),
                improvement_plan: formData.get('improvement_plan')
            };

            // 필수 필드 검증
            if (!evaluationData.operating_effectiveness || !evaluationData.conclusion) {
                alert('운영 효과성과 결론은 필수 입력 항목입니다.');
                return;
            }

            // 서버에 저장
            fetch('/api/operation-evaluation/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rcm_id: currentRcmId,
                    evaluation_session: currentEvaluationSession,
                    control_code: currentControlCode,
                    evaluation_data: evaluationData
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 로컬 데이터 업데이트
                    evaluationDict[currentControlCode] = evaluationData;

                    // UI 업데이트
                    updateEvaluationUI(currentRowIndex, evaluationData);
                    updateProgress();

                    // 모달 닫기
                    bootstrap.Modal.getInstance(document.getElementById('operationEvaluationModal')).hide();

                    alert('운영평가 결과가 저장되었습니다.');
                } else {
                    alert('저장 중 오류가 발생했습니다: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('저장 중 오류가 발생했습니다.');
            });
        }

        // 개별 평가 UI 업데이트
        function updateEvaluationUI(rowIndex, data) {
            // 평가 결과 업데이트
            const resultElement = document.getElementById(`evaluation-result-${rowIndex}`);
            if (data.conclusion) {
                const resultMap = {
                    'satisfactory': { text: '만족', class: 'bg-success' },
                    'deficiency': { text: '결함', class: 'bg-warning text-dark' },
                    'material_weakness': { text: '중요한 결함', class: 'bg-danger' }
                };
                const result = resultMap[data.conclusion];
                resultElement.textContent = result.text;
                resultElement.className = `badge ${result.class}`;
            }

            // 개선계획 업데이트
            const improvementElement = document.getElementById(`improvement-plan-${rowIndex}`);
            improvementElement.textContent = data.improvement_plan || '-';
        }

        // 모든 평가 UI 업데이트
        function updateAllEvaluationUI() {
            {% for detail in rcm_details %}
            if (evaluationDict['{{ detail.control_code }}']) {
                updateEvaluationUI({{ loop.index }}, evaluationDict['{{ detail.control_code }}']);
            }
            {% endfor %}
        }

        // 진행률 업데이트
        function updateProgress() {
            const totalControls = {{ rcm_details|length }};
            const evaluatedControls = Object.keys(evaluationDict).length;
            const progress = totalControls > 0 ? Math.round((evaluatedControls / totalControls) * 100) : 0;

            document.getElementById('evaluationProgress').style.width = progress + '%';
            document.getElementById('evaluationProgress').textContent = progress + '%';
            document.getElementById('evaluatedCount').textContent = evaluatedControls;

            // 상태 업데이트
            const statusElement = document.getElementById('evaluationStatus');
            if (progress === 100) {
                statusElement.textContent = '완료';
                statusElement.className = 'badge bg-success';
                document.getElementById('completeEvaluationBtn').style.display = 'inline-block';
                document.getElementById('downloadBtn').style.display = 'inline-block';
            } else if (progress > 0) {
                statusElement.textContent = '진행중';
                statusElement.className = 'badge bg-warning text-dark';
                document.getElementById('completeEvaluationBtn').style.display = 'none';
                document.getElementById('downloadBtn').style.display = 'none';
            } else {
                statusElement.textContent = '준비중';
                statusElement.className = 'badge bg-secondary';
                document.getElementById('completeEvaluationBtn').style.display = 'none';
                document.getElementById('downloadBtn').style.display = 'none';
            }
        }

        // 모든 평가 초기화
        function resetAllEvaluations() {
            if (!confirm('모든 운영평가 결과를 초기화하시겠습니까?')) {
                return;
            }

            fetch('/api/operation-evaluation/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rcm_id: currentRcmId,
                    evaluation_session: currentEvaluationSession
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 로컬 데이터 초기화
                    evaluationDict = {};

                    // UI 초기화
                    {% for detail in rcm_details %}
                    document.getElementById('evaluation-result-{{ loop.index }}').textContent = '미평가';
                    document.getElementById('evaluation-result-{{ loop.index }}').className = 'badge bg-secondary';
                    document.getElementById('improvement-plan-{{ loop.index }}').textContent = '-';
                    {% endfor %}

                    updateProgress();
                    alert('운영평가 결과가 초기화되었습니다.');
                } else {
                    alert('초기화 중 오류가 발생했습니다: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('초기화 중 오류가 발생했습니다.');
            });
        }

        // 평가 완료 처리
        function completeEvaluation() {
            alert('운영평가 완료 기능은 추후 구현 예정입니다.');
        }

        // 평가 결과 내보내기
        function exportEvaluationResult() {
            alert('운영평가 결과 내보내기 기능은 추후 구현 예정입니다.');
        }
    </script>
</body>
</html>