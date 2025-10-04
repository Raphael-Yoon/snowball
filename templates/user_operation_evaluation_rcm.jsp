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
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-info" onclick="viewDesignEvaluation()">
                            <i class="fas fa-drafting-compass me-1"></i>설계평가 보기
                        </button>
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
                                                    data-control-nature-code="{{ detail.control_nature|e }}"
                                                    data-test-procedure="{{ detail.test_procedure|e }}"
                                                    data-std-control-id="{{ detail.mapped_std_control_id|e }}"
                                                    data-std-control-code="{{ rcm_mappings.get(detail.control_code).std_control_code if rcm_mappings.get(detail.control_code) else '' }}"
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

    <!-- 설계평가 보기 모달 -->
    <div class="modal fade" id="designEvaluationViewModal" tabindex="-1" aria-labelledby="designEvaluationViewModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header bg-info text-white">
                    <h5 class="modal-title" id="designEvaluationViewModalLabel">
                        <i class="fas fa-drafting-compass me-2"></i>설계평가 결과 ({{ evaluation_session }})
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-bordered table-sm">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%">코드</th>
                                    <th width="20%">이름</th>
                                    <th width="42%">설명</th>
                                    <th width="5%">주기</th>
                                    <th width="5%">핵심</th>
                                    <th width="5%">구분</th>
                                    <th width="8%">기준통제</th>
                                    <th width="7%">결과</th>
                                </tr>
                            </thead>
                            <tbody id="designEvaluationTableBody">
                                <tr>
                                    <td colspan="8" class="text-center py-4">
                                        <i class="fas fa-spinner fa-spin me-2"></i>설계평가 데이터를 불러오는 중...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
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

                        <!-- 파일 첨부 섹션 -->
                        <div class="mb-3">
                            <label for="evaluationImages" class="form-label fw-bold">증빙 자료 (이미지)</label>
                            <input type="file" class="form-control" id="evaluationImages" accept="image/*" multiple>
                            <div class="form-text">현장 사진, 스크린샷, 문서 스캔본 등 평가 근거가 되는 이미지 파일을 첨부하세요. (다중 선택 가능)</div>
                            <div id="imagePreview" class="mt-2"></div>
                        </div>

                        <!-- 수동통제 전용: 엑셀 파일 업로드 -->
                        <div class="mb-3" id="excelUploadSection" style="display: none;">
                            <label for="sampleExcelFile" class="form-label fw-bold">표본 데이터 (엑셀)</label>
                            <input type="file" class="form-control" id="sampleExcelFile" accept=".xlsx,.xls,.csv">
                            <div class="form-text">표본 검토 내역이 포함된 엑셀 파일을 업로드하세요.</div>
                            <div id="excelPreview" class="mt-2"></div>
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
            const controlNatureCode = buttonElement.getAttribute('data-control-nature-code');
            const testProcedure = buttonElement.getAttribute('data-test-procedure');
            const stdControlId = buttonElement.getAttribute('data-std-control-id');
            const stdControlCode = buttonElement.getAttribute('data-std-control-code');
            const rowIndex = parseInt(buttonElement.getAttribute('data-row-index'));

            console.log('Control Code:', controlCode);
            console.log('Standard Control Code:', stdControlCode);
            console.log('Standard Control Code Type:', typeof stdControlCode);

            currentControlCode = controlCode;
            currentRowIndex = rowIndex;

            // 표준통제별 UI 분기
            if (stdControlCode && stdControlCode === 'APD01') {
                console.log('APD01 detected! Redirecting to APD01 page...');
                // APD01 전용 UI로 변경
                showAPD01UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'APD07') {
                console.log('APD07 detected! Redirecting to APD07 page...');
                // APD07 전용 UI로 변경
                showAPD07UI(buttonElement);
                return;
            }

            console.log('Not APD01 or APD07, showing standard modal');
            
            // 일반 운영평가 UI
            // 수동통제인 경우에만 엑셀 업로드 섹션 표시
            const excelSection = document.getElementById('excelUploadSection');
            if (controlNatureCode && controlNatureCode.toUpperCase() === 'M') {
                excelSection.style.display = 'block';
            } else {
                excelSection.style.display = 'none';
            }
            
            // 파일 입력 초기화
            document.getElementById('evaluationImages').value = '';
            document.getElementById('sampleExcelFile').value = '';
            document.getElementById('imagePreview').innerHTML = '';
            document.getElementById('excelPreview').innerHTML = '';

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

        // 이미지 파일 미리보기
        document.getElementById('evaluationImages').addEventListener('change', function(e) {
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = '';
            
            const files = e.target.files;
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const div = document.createElement('div');
                        div.className = 'd-inline-block position-relative me-2 mb-2';
                        div.innerHTML = `
                            <img src="${e.target.result}" style="max-width: 100px; max-height: 100px; border: 1px solid #ddd; border-radius: 4px;">
                            <small class="d-block text-muted text-center" style="max-width: 100px; overflow: hidden; text-overflow: ellipsis;">${file.name}</small>
                        `;
                        preview.appendChild(div);
                    };
                    reader.readAsDataURL(file);
                }
            }
        });

        // 엑셀 파일 미리보기
        document.getElementById('sampleExcelFile').addEventListener('change', function(e) {
            const preview = document.getElementById('excelPreview');
            preview.innerHTML = '';
            
            const file = e.target.files[0];
            if (file) {
                const div = document.createElement('div');
                div.className = 'alert alert-info d-flex align-items-center';
                div.innerHTML = `
                    <i class="fas fa-file-excel fa-2x me-3"></i>
                    <div>
                        <strong>${file.name}</strong><br>
                        <small>크기: ${(file.size / 1024).toFixed(2)} KB</small>
                    </div>
                `;
                preview.appendChild(div);
            }
        });

        // 운영평가 저장
        function saveOperationEvaluation() {
            const form = document.getElementById('operationEvaluationForm');
            const formData = new FormData(form);
            
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

            // FormData 생성 (파일 포함)
            const uploadData = new FormData();
            uploadData.append('rcm_id', currentRcmId);
            uploadData.append('design_evaluation_session', currentEvaluationSession);
            uploadData.append('control_code', currentControlCode);
            uploadData.append('evaluation_data', JSON.stringify(evaluationData));
            
            // 이미지 파일 추가
            const imageFiles = document.getElementById('evaluationImages').files;
            for (let i = 0; i < imageFiles.length; i++) {
                uploadData.append('evaluation_image_' + i, imageFiles[i]);
            }
            
            // 엑셀 파일 추가 (수동통제인 경우)
            const excelFile = document.getElementById('sampleExcelFile').files[0];
            if (excelFile) {
                uploadData.append('sample_excel', excelFile);
            }

            // 서버에 저장
            fetch('/api/operation-evaluation/save', {
                method: 'POST',
                body: uploadData
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

        // ===================================================================
        // 설계평가 보기 함수
        // ===================================================================

        function viewDesignEvaluation() {
            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('designEvaluationViewModal'));
            modal.show();

            // 설계평가 데이터 조회
            fetch(`/api/design-evaluation/get?rcm_id=${currentRcmId}&evaluation_session=${currentEvaluationSession}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderDesignEvaluationTable(data.evaluations);
                    } else {
                        document.getElementById('designEvaluationTableBody').innerHTML = `
                            <tr>
                                <td colspan="8" class="text-center text-danger py-4">
                                    <i class="fas fa-exclamation-triangle me-2"></i>${data.message || '설계평가 데이터를 불러올 수 없습니다.'}
                                </td>
                            </tr>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('designEvaluationTableBody').innerHTML = `
                        <tr>
                            <td colspan="8" class="text-center text-danger py-4">
                                <i class="fas fa-exclamation-triangle me-2"></i>설계평가 데이터를 불러오는 중 오류가 발생했습니다.
                            </td>
                        </tr>
                    `;
                });
        }

        function renderDesignEvaluationTable(evaluations) {
            const tbody = document.getElementById('designEvaluationTableBody');

            if (!evaluations || evaluations.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">
                            <i class="fas fa-info-circle me-2"></i>설계평가 데이터가 없습니다.
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = evaluations.map(item => {
                const adequacyMap = {
                    'adequate': { text: '적정', class: 'bg-success' },
                    'deficient': { text: '미흡', class: 'bg-warning text-dark' },
                    'inadequate': { text: '부적정', class: 'bg-danger' }
                };
                const adequacy = adequacyMap[item.design_adequacy] || { text: item.design_adequacy || '-', class: 'bg-secondary' };

                const stdControl = item.std_control_code
                    ? `<span class="badge bg-info">${item.std_control_code}</span>`
                    : '<span class="text-muted">-</span>';

                const isKey = item.key_control || '-';

                return `
                    <tr>
                        <td style="font-size: 0.85rem;"><code>${item.control_code || '-'}</code></td>
                        <td style="font-size: 0.85rem;">${item.control_name || '-'}</td>
                        <td>
                            <div style="max-height: 60px; overflow-y: auto; font-size: 0.85rem;">
                                ${item.control_description || '-'}
                            </div>
                        </td>
                        <td style="font-size: 0.85rem;">${item.control_frequency_name || item.control_frequency || '-'}</td>
                        <td style="font-size: 0.85rem;">${isKey}</td>
                        <td style="font-size: 0.85rem;">${item.control_nature_name || item.control_nature || '-'}</td>
                        <td style="font-size: 0.85rem;">${stdControl}</td>
                        <td style="font-size: 0.85rem;"><span class="badge ${adequacy.class}">${adequacy.text}</span></td>
                    </tr>
                `;
            }).join('');
        }

        // ===================================================================
        // APD01 표준통제 전용 함수
        // ===================================================================

        function showAPD01UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');
            
            // 팝업으로 APD01 UI 표시
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            const popupWidth = 1400;
            const popupHeight = 900;
            const left = (window.screen.width - popupWidth) / 2;
            const top = (window.screen.height - popupHeight) / 2;

            window.open(
                `/operation-evaluation/apd01?${params.toString()}`,
                'APD01_Popup',
                `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=yes,resizable=yes`
            );
        }

        // ===================================================================
        // APD07 표준통제 전용 함수
        // ===================================================================

        function showAPD07UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 팝업으로 APD07 UI 표시
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            const popupWidth = 1600;
            const popupHeight = 900;
            const left = (window.screen.width - popupWidth) / 2;
            const top = (window.screen.height - popupHeight) / 2;

            window.open(
                `/operation-evaluation/apd07?${params.toString()}`,
                'APD07_Popup',
                `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=yes,resizable=yes`
            );
        }
    </script>
</body>
</html>