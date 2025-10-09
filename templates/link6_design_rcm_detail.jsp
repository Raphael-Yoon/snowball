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
                    <div>
                        <h1><i class="fas fa-clipboard-check me-2"></i>RCM 설계평가</h1>
                        <div id="evaluationNameDisplay" class="text-primary fw-bold fs-6 mt-1" style="display: none;">
                            평가명: <span id="currentEvaluationName"></span>
                        </div>
                    </div>
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
                                        <th>평가자:</th>
                                        <td><strong>{{ user_info.user_name }}</strong></td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center">
                                    <h6 class="text-success">설계평가 진행률</h6>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-success" id="evaluationProgress" role="progressbar" style="width: 0%; font-size: 12px;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
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

        <!-- 설계평가 통제 목록 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-list me-2"></i>통제 설계평가</h5>
                        <div class="d-flex flex-wrap gap-2">
                            {% if user_info.admin_flag == 'Y' %}
                            <button class="btn btn-sm btn-outline-success" onclick="evaluateAllControls()" title="[관리자 전용] 임시 데이터를 생성하여 화면에만 표시 (실제 저장되지 않음)" data-bs-toggle="tooltip" style="height: 70%; padding: 0.2rem 0.5rem; border: 2px dashed #198754;">
                                <i class="fas fa-user-shield me-1"></i><i class="fas fa-check-double me-1"></i>임시평가
                            </button>
                            <button class="btn btn-sm btn-outline-primary" onclick="saveAllAsAdequate()" title="[관리자 전용] 모든 통제를 '적정' 값으로 실제 저장" data-bs-toggle="tooltip" style="height: 70%; padding: 0.2rem 0.5rem; border: 2px dashed #0d6efd;">
                                <i class="fas fa-user-shield me-1"></i><i class="fas fa-check-circle me-1"></i>적정저장
                            </button>
                            <button class="btn btn-sm btn-outline-warning" onclick="resetAllEvaluations()" title="[관리자 전용] 모든 설계평가 데이터 초기화" data-bs-toggle="tooltip" style="height: 70%; padding: 0.2rem 0.5rem; border: 2px dashed #ffc107;">
                                <i class="fas fa-user-shield me-1"></i><i class="fas fa-undo me-1"></i>초기화
                            </button>
                            {% endif %}
                            <button id="completeEvaluationBtn" class="btn btn-sm btn-success" onclick="completeEvaluation()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;" title="설계평가를 완료 처리합니다" data-bs-toggle="tooltip">
                                <i class="fas fa-check me-1"></i>완료처리
                            </button>
                            <button id="archiveEvaluationBtn" class="btn btn-sm btn-secondary" onclick="archiveEvaluation()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;" title="완료된 설계평가를 Archive 처리합니다" data-bs-toggle="tooltip">
                                <i class="fas fa-archive me-1"></i>Archive
                            </button>
                            <button id="downloadBtn" class="btn btn-sm btn-outline-primary" onclick="exportEvaluationResult()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;">
                                <i class="fas fa-file-excel me-1"></i>다운로드
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="refreshEvaluationList()" style="height: 70%; padding: 0.2rem 0.5rem;" title="평가 목록 새로고침" data-bs-toggle="tooltip">
                                <i class="fas fa-sync-alt me-1"></i>새로고침
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        {% if rcm_details %}
                        <div class="table-responsive">
                            <table class="table table-striped" id="controlsTable">
                                <thead>
                                    <tr>
                                        <th width="6%">통제코드</th>
                                        <th width="12%">통제명</th>
                                        <th width="23%">통제활동설명</th>
                                        <th width="7%">통제주기</th>
                                        <th width="7%">통제유형</th>
                                        <th width="6%">핵심통제</th>
                                        <th width="8%">기준통제 매핑</th>
                                        <th width="8%">설계평가</th>
                                        <th width="9%">평가결과</th>
                                        <th width="14%">조치사항</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    {% set mapping_info = rcm_mappings|selectattr('control_code', 'equalto', detail.control_code)|first %}
                                    <tr id="control-row-{{ loop.index }}" {% if not mapping_info %}class="table-warning"{% endif %}>
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
                                        <td>
                                            {{ detail.key_control or '비핵심' }}
                                        </td>
                                        <td>
                                            {% if mapping_info %}
                                                <a href="/rcm/{{ rcm_id }}/mapping" class="badge bg-success text-white text-decoration-none" title="{{ mapping_info.std_control_name or mapping_info.std_control_code or '기준통제 매핑됨' }}" data-bs-toggle="tooltip">
                                                    <i class="fas fa-link me-1"></i>매핑
                                                </a>
                                            {% else %}
                                                <a href="/rcm/{{ rcm_id }}/mapping" class="badge bg-warning text-dark fw-bold text-decoration-none" style="border: 2px solid #fd7e14;" title="클릭하여 기준통제 매핑하기" data-bs-toggle="tooltip">
                                                    <i class="fas fa-exclamation-triangle me-1"></i>미매핑
                                                </a>
                                            {% endif %}
                                        </td>
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
                                <div class="col-md-6">
                                    <table class="table table-borderless mb-0">
                                        <tr>
                                            <th style="width: 100px; white-space: nowrap; vertical-align: top;">통제코드:</th>
                                            <td style="vertical-align: top;">
                                                <span id="modalControlCode" class="text-primary fw-bold"></span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <th style="width: 100px; white-space: nowrap; vertical-align: top;">통제명:</th>
                                            <td style="vertical-align: top;">
                                                <span id="modalControlName" class="fw-bold"></span>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <table class="table table-borderless mb-0">
                                        <tr>
                                            <th style="width: 100px; white-space: nowrap; vertical-align: top;">통제주기:</th>
                                            <td style="vertical-align: top;">
                                                <span id="modalControlFrequency" class="text-muted"></span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <th style="width: 100px; white-space: nowrap; vertical-align: top;">통제유형:</th>
                                            <td style="vertical-align: top;">
                                                <span id="modalControlType" class="text-muted"></span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <th style="width: 100px; white-space: nowrap; vertical-align: top;">통제구분:</th>
                                            <td style="vertical-align: top;">
                                                <span id="modalControlNature" class="text-muted"></span>
                                            </td>
                                        </tr>
                                    </table>
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
                                <strong>평가 기준:</strong> 위에 기술된 통제활동이 현재 실제로 수행되고 있는 통제 절차와 일치하는지, 그리고 해당 통제가 실무적으로 효과적으로 작동하고 있는지 평가하세요.
                            </div>
                            
                            <div class="mb-3">
                                <label for="descriptionAdequacy" class="form-label">통제활동 현실 반영도 *</label>
                                <select class="form-select" id="descriptionAdequacy" required>
                                    <option value="">평가 결과 선택</option>
                                    <option value="adequate">적절함 - 실제 수행 절차와 완전히 일치함</option>
                                    <option value="partially_adequate">부분적으로 적절함 - 실제와 일부 차이가 있음</option>
                                    <option value="inadequate">부적절함 - 실제 절차와 상당한 차이가 있음</option>
                                    <option value="missing">누락 - 통제활동이 실제로 수행되지 않음</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="improvementSuggestion" class="form-label">개선 제안사항</label>
                                <textarea class="form-control" id="improvementSuggestion" rows="3" 
                                          placeholder="실제 업무와 차이가 있는 경우, RCM 문서 업데이트 방향이나 실무 개선 방안을 제안하세요..."></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- 설계 효과성 종합 평가 -->
                    <div class="card mb-3" id="effectivenessSection">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0"><i class="fas fa-check-circle me-2"></i>설계 효과성 종합 평가</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="overallEffectiveness" class="form-label">실제 통제 설계 효과성 *</label>
                                <select class="form-select" id="overallEffectiveness" required disabled>
                                    <option value="">평가 결과 선택</option>
                                    <option value="effective">효과적 - 통제 설계가 적절하고 위험을 효과적으로 완화함</option>
                                    <option value="partially_effective">부분적으로 효과적 - 통제 설계에 일부 보완이 필요함</option>
                                    <option value="ineffective">비효과적 - 통제 설계가 위험을 충분히 완화하지 못함</option>
                                </select>
                                <div class="form-text text-muted" id="effectivenessHelpText">
                                    통제활동 설명 적절성이 "적절함"으로 평가된 경우에만 입력 가능합니다.
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="evaluationRationale" class="form-label">평가 근거</label>
                                <textarea class="form-control" id="evaluationRationale" rows="3" disabled
                                          placeholder="현재 실무 상황을 관찰한 내용이나 담당자 면담 결과 등 구체적인 평가 근거를 기술하세요..."></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <label for="recommendedActions" class="form-label">권고 조치사항</label>
                                <textarea class="form-control" id="recommendedActions" rows="2" 
                                          placeholder="실무와 문서 간 차이 해소나 통제 운영 개선을 위한 구체적인 조치사항을 제안하세요..."></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <label for="evaluationImages" class="form-label">평가 증빙 자료 (이미지)</label>
                                <input type="file" class="form-control" id="evaluationImages" 
                                       accept="image/*" multiple>
                                <div class="form-text">현장 사진, 스크린샷, 문서 스캔본 등 평가 근거가 되는 이미지 파일을 첨부하세요. (다중 선택 가능)</div>
                                <div id="imagePreview" class="mt-2"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-sm btn-outline-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-1"></i>취소
                    </button>
                    <button type="button" id="saveEvaluationBtn" class="btn btn-sm btn-success" onclick="saveEvaluation()">
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
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-1"></i>취소
                    </button>
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
        let evaluationImages = {}; // 평가별 이미지 저장
        const rcmId = {{ rcm_id }};
        
        console.log('***** JavaScript rcmId value:', rcmId, '(type:', typeof rcmId, ') *****');
        
        // SessionStorage 디버깅 함수
        function debugSessionStorage() {
            console.log('=== SessionStorage Debug ===');
            console.log('sessionStorage.length:', sessionStorage.length);
            console.log('All sessionStorage items:');
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                const value = sessionStorage.getItem(key);
                console.log(`  "${key}": "${value}" (type: ${typeof value})`);
            }
            console.log('Direct access:');
            console.log('  currentEvaluationSession:', `"${sessionStorage.getItem('currentEvaluationSession')}"`);
            console.log('  currentEvaluationHeaderId:', `"${sessionStorage.getItem('currentEvaluationHeaderId')}"`);
            console.log('========================');
        }

        // SessionStorage 수동 설정 함수 (디버깅용)
        function setManualSessionStorage() {
            console.log('Setting manual sessionStorage values...');
            sessionStorage.setItem('currentEvaluationSession', 'FY25_설계평가');
            sessionStorage.setItem('currentEvaluationHeaderId', '8');
            console.log('Manual values set. Current sessionStorage:');
            debugSessionStorage();
        }

        // SessionStorage 초기화 함수 (디버깅용)  
        function clearSessionStorage() {
            console.log('Clearing all sessionStorage...');
            sessionStorage.clear();
            console.log('SessionStorage cleared:');
            debugSessionStorage();
        }

        // 이미지 업로드 설정
        function setupImageUpload() {
            const imageInput = document.getElementById('evaluationImages');
            if (imageInput) {
                imageInput.addEventListener('change', handleImageSelection);
            }
        }
        
        // 이미지 선택 처리
        function handleImageSelection(event) {
            const files = event.target.files;
            const previewContainer = document.getElementById('imagePreview');
            
            if (!previewContainer) return;
            
            // 기존 미리보기 초기화
            previewContainer.innerHTML = '';
            
            // 선택된 이미지가 없으면 종료
            if (!files || files.length === 0) return;
            
            // 각 파일에 대해 미리보기 생성
            Array.from(files).forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const imagePreview = createImagePreview(e.target.result, file.name, index);
                        previewContainer.appendChild(imagePreview);
                    };
                    reader.readAsDataURL(file);
                }
            });
            
            // 현재 평가의 이미지 저장
            if (currentEvaluationIndex !== null) {
                evaluationImages[currentEvaluationIndex] = Array.from(files);
            }
        }
        
        // 이미지 미리보기 엘리먼트 생성
        function createImagePreview(src, fileName, index) {
            const div = document.createElement('div');
            div.className = 'image-preview-item d-inline-block me-2 mb-2 position-relative';
            div.style.maxWidth = '150px';
            
            div.innerHTML = `
                <img src="${src}" class="img-thumbnail" style="max-width: 100%; max-height: 100px;" alt="${fileName}">
                <div class="small text-muted text-truncate" style="max-width: 150px;">${fileName}</div>
                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle" 
                        style="width: 20px; height: 20px; padding: 0; margin: 2px;"
                        onclick="removeImagePreview(${index}, this.parentElement)">×</button>
            `;
            
            return div;
        }
        
        // 이미지 미리보기 제거
        function removeImagePreview(index, element) {
            element.remove();
            
            // 파일 입력에서도 제거 (HTML5 FileList는 수정할 수 없으므로 새로운 파일 리스트 생성)
            const imageInput = document.getElementById('evaluationImages');
            if (imageInput && currentEvaluationIndex !== null) {
                const currentFiles = evaluationImages[currentEvaluationIndex] || [];
                const newFiles = currentFiles.filter((_, i) => i !== index);
                evaluationImages[currentEvaluationIndex] = newFiles;
                
                // 미리보기 컨테이너의 모든 이미지 다시 인덱싱
                updateImageIndices();
            }
        }
        
        // 이미지 인덱스 업데이트
        function updateImageIndices() {
            const previewContainer = document.getElementById('imagePreview');
            if (!previewContainer) return;
            
            const imageItems = previewContainer.querySelectorAll('.image-preview-item');
            imageItems.forEach((item, newIndex) => {
                const button = item.querySelector('button');
                if (button) {
                    button.setAttribute('onclick', `removeImagePreview(${newIndex}, this.parentElement)`);
                }
            });
        }
        
        // 기존 이미지 표시
        function displayExistingImages(images) {
            const previewContainer = document.getElementById('imagePreview');
            if (!previewContainer) return;
            
            // 기존 미리보기 초기화
            previewContainer.innerHTML = '';
            
            // 기존 이미지들을 미리보기에 표시
            if (images && images.length > 0) {
                images.forEach((imageInfo, index) => {
                    const div = document.createElement('div');
                    div.className = 'image-preview-item d-inline-block me-2 mb-2 position-relative';
                    div.style.maxWidth = '150px';
                    
                    div.innerHTML = `
                        <img src="${imageInfo.url}" class="img-thumbnail" style="max-width: 100%; max-height: 100px;" alt="${imageInfo.filename}">
                        <div class="small text-muted text-truncate" style="max-width: 150px;">${imageInfo.filename}</div>
                        <div class="small text-success">저장됨</div>
                    `;
                    
                    previewContainer.appendChild(div);
                });
            }
        }
        
        // 평가 이미지 보기 모달
        function showEvaluationImages(index) {
            const evaluation = evaluationResults[index];
            if (!evaluation || !evaluation.images || evaluation.images.length === 0) {
                alert('[DESIGN-001] 첨부된 이미지가 없습니다.');
                return;
            }
            
            // 이미지 갤러리 모달 생성
            let modalHtml = `
                <div class="modal fade" id="imageGalleryModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">평가 첨부 이미지 (${evaluation.images.length}개)</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
            `;
            
            evaluation.images.forEach((imageInfo, imgIndex) => {
                modalHtml += `
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <img src="${imageInfo.url}" class="card-img-top" style="max-height: 300px; object-fit: contain;" alt="${imageInfo.filename}">
                            <div class="card-body p-2">
                                <small class="text-muted">${imageInfo.filename}</small>
                                <br>
                                <a href="${imageInfo.url}" class="btn btn-sm btn-outline-primary mt-1">
                                    <i class="fas fa-external-link-alt me-1"></i>원본 보기
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            modalHtml += `
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 기존 모달 제거
            const existingModal = document.getElementById('imageGalleryModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // 새 모달 추가 및 표시
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('imageGalleryModal'));
            modal.show();
            
            // 모달이 닫히면 DOM에서 제거
            document.getElementById('imageGalleryModal').addEventListener('hidden.bs.modal', function () {
                this.remove();
            });
        }

        // 통제활동 설명 적절성에 따른 효과성 평가 활성화/비활성화
        function setupAdequacyControl() {
            const adequacySelect = document.getElementById('descriptionAdequacy');
            const effectivenessSelect = document.getElementById('overallEffectiveness');
            const effectivenessSection = document.getElementById('effectivenessSection');
            const evaluationRationale = document.getElementById('evaluationRationale');
            const recommendedActionsField = document.getElementById('recommendedActions');

            if (adequacySelect && effectivenessSelect) {
                // 초기 상태 설정
                toggleEffectivenessSection(adequacySelect.value);

                // 이벤트 리스너 추가
                adequacySelect.addEventListener('change', function() {
                    toggleEffectivenessSection(this.value);
                });
            }

            function toggleEffectivenessSection(adequacyValue) {
                if (adequacyValue === 'adequate') {
                    // 적절함인 경우 활성화
                    effectivenessSelect.disabled = false;
                    evaluationRationale.disabled = false;
                    effectivenessSection.style.opacity = '1';
                    document.getElementById('effectivenessHelpText').style.display = 'none';
                } else {
                    // 적절함이 아닌 경우 비활성화 및 초기화
                    effectivenessSelect.disabled = true;
                    effectivenessSelect.value = '';
                    evaluationRationale.value = '';
                    evaluationRationale.disabled = true;
                    recommendedActionsField.value = '';
                    recommendedActionsField.disabled = true;
                    effectivenessSection.style.opacity = '0.5';
                    document.getElementById('effectivenessHelpText').style.display = 'block';
                }
            }
        }

        // 권고 조치사항 필드 조건부 활성화 설정
        function setupRecommendedActionsField() {
            const effectivenessSelect = document.getElementById('overallEffectiveness');
            const recommendedActionsField = document.getElementById('recommendedActions');

            if (effectivenessSelect && recommendedActionsField) {
                // 초기 상태 설정
                toggleRecommendedActions(effectivenessSelect.value);

                // 이벤트 리스너 추가
                effectivenessSelect.addEventListener('change', function() {
                    toggleRecommendedActions(this.value);
                });
            }
        }
        
        // 권고 조치사항 필드 활성화/비활성화
        function toggleRecommendedActions(effectivenessValue) {
            const recommendedActionsField = document.getElementById('recommendedActions');
            const container = recommendedActionsField.closest('.mb-3');
            
            if (effectivenessValue === 'effective') {
                // 효과적인 경우 비활성화 및 숨김
                recommendedActionsField.disabled = true;
                recommendedActionsField.value = '';
                recommendedActionsField.placeholder = '효과적인 통제는 조치사항이 필요하지 않습니다.';
                if (container) {
                    container.style.opacity = '0.5';
                }
            } else {
                // 부분적으로 효과적이거나 비효과적인 경우 활성화
                recommendedActionsField.disabled = false;
                recommendedActionsField.placeholder = '통제 설계 개선을 위한 구체적인 조치사항을 제안하세요...';
                if (container) {
                    container.style.opacity = '1';
                }
            }
        }
        
        // 개선 제안사항 필드 조건부 활성화 설정
        function setupImprovementSuggestionField() {
            const adequacySelect = document.getElementById('descriptionAdequacy');
            const improvementField = document.getElementById('improvementSuggestion');
            
            if (adequacySelect && improvementField) {
                // 초기 상태 설정
                toggleImprovementSuggestion(adequacySelect.value);
                
                // 이벤트 리스너 추가
                adequacySelect.addEventListener('change', function() {
                    toggleImprovementSuggestion(this.value);
                });
            }
        }
        
        // 개선 제안사항 필드 활성화/비활성화
        function toggleImprovementSuggestion(adequacyValue) {
            const improvementField = document.getElementById('improvementSuggestion');
            const container = improvementField.closest('.mb-3');
            
            if (adequacyValue === 'adequate') {
                // 적절한 경우 비활성화
                improvementField.disabled = true;
                improvementField.value = '';
                improvementField.placeholder = '현실 반영도가 적절하므로 개선사항이 필요하지 않습니다.';
                if (container) {
                    container.style.opacity = '0.5';
                }
            } else {
                // 부분적으로 적절, 부적절, 누락인 경우 활성화
                improvementField.disabled = false;
                improvementField.placeholder = '실제 업무와 차이가 있는 경우, RCM 문서 업데이트 방향이나 실무 개선 방안을 제안하세요...';
                if (container) {
                    container.style.opacity = '1';
                }
            }
        }

        // 성공 메시지 표시 함수
        function showSuccessMessage(message) {
            const alertHtml = `
                <div class="alert alert-success alert-dismissible fade show position-fixed" 
                     style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" 
                     role="alert" id="successAlert">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>${message}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            // 기존 성공 알림 제거
            const existingAlert = document.getElementById('successAlert');
            if (existingAlert) {
                existingAlert.remove();
            }
            
            // 새 알림 추가
            document.body.insertAdjacentHTML('beforeend', alertHtml);
            
            // 3초 후 자동으로 알림 제거
            setTimeout(() => {
                const alert = document.getElementById('successAlert');
                if (alert) {
                    alert.remove();
                }
            }, 3000);
        }

        // 전역으로 함수 노출 (브라우저 콘솔에서 호출 가능)
        window.debugSessionStorage = debugSessionStorage;
        window.setManualSessionStorage = setManualSessionStorage;
        window.clearSessionStorage = clearSessionStorage;

        // 페이지 로드 시 기존 평가 결과 불러오기
        document.addEventListener('DOMContentLoaded', function() {
            // SessionStorage 상태 확인
            debugSessionStorage();
            
            // 새 세션인지 확인
            const isNewSession = sessionStorage.getItem('isNewEvaluationSession') === 'true';
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            
            console.log('Page loaded - Current session:', currentSession);
            console.log('Is new session:', isNewSession);
            
            if (!currentSession) {
                // 세션 정보가 없으면 기본 세션명 설정
                const defaultSession = `평가_${new Date().getTime()}`;
                sessionStorage.setItem('currentEvaluationSession', defaultSession);
                console.log('No session found, created default session:', defaultSession);
                
                // 새 세션이므로 평가 구조 생성
                createEvaluationStructure(defaultSession);
            }
            
            // 평가명 화면에 표시
            updateEvaluationNameDisplay();

            // 통제활동 설명 적절성에 따른 효과성 평가 활성화/비활성화 설정
            setupAdequacyControl();

            // 권고 조치사항 필드 조건부 활성화 설정
            setupRecommendedActionsField();

            // 개선 제안사항 필드 조건부 활성화 설정
            setupImprovementSuggestionField();
            
            if (isNewSession && currentSession) {
                // 새 세션 알림 표시
                showNewSessionAlert(currentSession);
                // 플래그 제거 (다시 새로고침해도 메시지 안 나오도록)
                sessionStorage.removeItem('isNewEvaluationSession');
            }
            
            loadExistingEvaluations();
        });
        
        // 평가명 화면에 표시
        function updateEvaluationNameDisplay() {
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            if (currentSession) {
                document.getElementById('currentEvaluationName').textContent = currentSession;
                document.getElementById('evaluationNameDisplay').style.display = 'block';
            } else {
                document.getElementById('evaluationNameDisplay').style.display = 'none';
            }
        }
        
        // 평가 구조 생성
        function createEvaluationStructure(sessionName) {
            console.log('Creating evaluation structure for session:', sessionName);
            
            fetch('/api/design-evaluation/create-evaluation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rcm_id: rcmId,
                    evaluation_session: sessionName
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Evaluation structure created successfully');
                    // 새 평가 생성 시 이전 완료 상태 정리
                    sessionStorage.removeItem('headerCompletedDate');
                    console.log('Cleared previous headerCompletedDate for new evaluation');
                } else {
                    console.error('Failed to create evaluation structure:', data.message);
                }
            })
            .catch(error => {
                console.error('Error creating evaluation structure:', error);
            });
        }

        // 새 세션 알림 표시
        function showNewSessionAlert(sessionName) {
            const alertHtml = `
                <div class="alert alert-success alert-dismissible fade show" role="alert" id="newSessionAlert">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>새로운 설계평가가 생성되었습니다!</strong>
                    <br>평가 세션명: <strong>"${sessionName}"</strong>
                    <br>모든 통제에 대한 평가 틀이 준비되었습니다. 각 통제별로 평가를 수행하고 저장하세요.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            // RCM 기본 정보 카드 다음에 알림 삽입
            const rcmInfoCard = document.querySelector('.card.border-success');
            if (rcmInfoCard && rcmInfoCard.parentNode) {
                rcmInfoCard.insertAdjacentHTML('afterend', alertHtml);
                
                // 10초 후 자동으로 알림 제거
                setTimeout(() => {
                    const alert = document.getElementById('newSessionAlert');
                    if (alert) {
                        alert.remove();
                    }
                }, 10000);
            }
        }
        
        // 기존 평가 결과 불러오기
        function loadExistingEvaluations() {
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            const headerId = sessionStorage.getItem('currentEvaluationHeaderId');
            
            console.log('DEBUG - SessionStorage values:');
            console.log('currentEvaluationSession:', currentSession);
            console.log('currentEvaluationHeaderId:', headerId);
            console.log('headerId type:', typeof headerId);
            console.log('headerId is null:', headerId === null);
            console.log('headerId is undefined:', headerId === undefined);
            
            // 항상 세션명으로 로드하여 최신 header_id를 사용
            let url;
            if (currentSession) {
                url = `/api/design-evaluation/load/${rcmId}?session=${encodeURIComponent(currentSession)}`;
                console.log('Using session route to get latest header_id');
            } else {
                url = `/api/design-evaluation/load/${rcmId}`;
                console.log('Using default route');
            }
                
            console.log('Loading evaluations from URL:', url);
                
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.log('Full API response:', data);
                    
                    if (data.success && data.evaluations) {
                        console.log('Evaluation data received:', data.evaluations);
                        
                        // 응답에서 header_id와 completed_date를 받으면 sessionStorage에 저장
                        if (data.header_id) {
                            sessionStorage.setItem('currentEvaluationHeaderId', data.header_id);
                            console.log('Updated currentEvaluationHeaderId to:', data.header_id);
                        }
                        
                        // header의 completed_date 저장 및 정리
                        if (data.header_completed_date && data.header_completed_date !== 'null' && data.header_completed_date !== null) {
                            sessionStorage.setItem('headerCompletedDate', data.header_completed_date);
                            console.log('Header completed_date saved to session:', data.header_completed_date);
                        } else {
                            // header_completed_date가 null이면 sessionStorage 정리
                            sessionStorage.removeItem('headerCompletedDate');
                            console.log('Header completed_date is null, removed from sessionStorage');
                        }
                        
                        // 컨트롤 코드를 인덱스로 매핑
                        {% for detail in rcm_details %}
                        const controlCode{{ loop.index }} = '{{ detail.control_code }}';
                        if (data.evaluations[controlCode{{ loop.index }}]) {
                            const evaluationData = data.evaluations[controlCode{{ loop.index }}];
                            console.log(`Control ${controlCode{{ loop.index }}} data:`, evaluationData);
                            
                            evaluationResults[{{ loop.index }}] = evaluationData;
                            updateEvaluationUI({{ loop.index }}, evaluationData);
                        }
                        {% endfor %}
                        
                        updateProgress();
                    }
                })
                .catch(error => {
                    console.error('기존 평가 결과 불러오기 오류:', error);
                });
            
            // 이미지 업로드 처리
            setupImageUpload();
        }
        
        // 평가 모달 열기
        function openEvaluationModal(index, controlCode, controlName) {
            console.log('=== openEvaluationModal called ===');
            console.log('Parameters:', {index, controlCode, controlName});
            
            // 헤더 완료 상태 확인 (더 엄격한 체크)
            const headerCompletedDate = sessionStorage.getItem('headerCompletedDate');
            const isHeaderCompleted = headerCompletedDate && 
                                    headerCompletedDate !== 'null' && 
                                    headerCompletedDate !== null && 
                                    headerCompletedDate !== 'undefined' &&
                                    headerCompletedDate.trim() !== '' &&
                                    headerCompletedDate.trim() !== 'null';
            
            console.log('Modal open check - headerCompletedDate:', `'${headerCompletedDate}'`, 'isHeaderCompleted:', isHeaderCompleted);
            
            if (isHeaderCompleted) {
                // 완료된 상태에서는 조회만 가능하도록 처리 (alert 제거)
                console.log('Header completed, opening in view-only mode');
            }
            
            currentEvaluationIndex = index;
            
            // 해당 행의 데이터 가져오기
            const row = document.getElementById(`control-row-${index}`);
            const cells = row.querySelectorAll('td');
            
            // 모달에 기본 정보 설정
            document.getElementById('modalControlCode').textContent = controlCode;
            document.getElementById('modalControlName').textContent = controlName;
            
            // 통제 세부 정보 설정
            const description = cells[2].textContent.trim();
            const frequency = cells[3].textContent.trim();
            const type = cells[4].textContent.trim();
            
            document.getElementById('modalControlDescription').textContent = description || '통제활동 설명이 등록되지 않았습니다.';
            document.getElementById('modalControlFrequency').textContent = frequency || '-';
            document.getElementById('modalControlType').textContent = type || '-';
            
            // RCM 세부 데이터에서 통제구분 찾기
            {% for detail in rcm_details %}
            if ({{ loop.index }} === index) {
                document.getElementById('modalControlNature').textContent = '{{ detail.control_nature_name or detail.control_nature or "-" }}';
            }
            {% endfor %}
            
            // 기본 디버깅
            console.log('DEBUG - Modal opened for index:', index);
            console.log('DEBUG - evaluationResults:', evaluationResults);
            console.log('DEBUG - evaluationResults[index]:', evaluationResults[index]);
            
            // 기존 평가 결과가 있다면 로드
            if (evaluationResults[index]) {
                const result = evaluationResults[index];
                console.log('DEBUG - Full result data:', result);
                
                document.getElementById('descriptionAdequacy').value = result.description_adequacy || '';
                document.getElementById('improvementSuggestion').value = result.improvement_suggestion || '';
                document.getElementById('overallEffectiveness').value = result.overall_effectiveness || '';
                document.getElementById('evaluationRationale').value = result.evaluation_rationale || '';
                document.getElementById('recommendedActions').value = result.recommended_actions || '';
                
                // 기존 이미지 표시
                console.log('DEBUG - Images data:', result.images);
                displayExistingImages(result.images || []);
            } else {
                // 폼 초기화
                document.getElementById('descriptionAdequacy').value = '';
                document.getElementById('improvementSuggestion').value = '';
                document.getElementById('overallEffectiveness').value = '';
                document.getElementById('evaluationRationale').value = '';
                document.getElementById('recommendedActions').value = '';
                
                // 이미지 초기화
                displayExistingImages([]);
            }
            
            // 이미지 입력 필드 초기화
            const imageInput = document.getElementById('evaluationImages');
            if (imageInput) imageInput.value = '';
            
            // 완료 상태 확인하여 저장 버튼 제어
            const saveButton = document.getElementById('saveEvaluationBtn');
            if (saveButton) {
                if (isHeaderCompleted) {
                    saveButton.disabled = true;
                    saveButton.innerHTML = '<i class="fas fa-lock me-1"></i>완료된 평가';
                    saveButton.title = '평가가 완료되어 수정할 수 없습니다';
                    saveButton.classList.remove('btn-success');
                    saveButton.classList.add('btn-secondary');
                } else {
                    saveButton.disabled = false;
                    saveButton.innerHTML = '<i class="fas fa-save me-1"></i>평가 저장';
                    saveButton.title = '평가 결과를 저장합니다';
                    saveButton.classList.remove('btn-secondary');
                    saveButton.classList.add('btn-success');
                }
            }
            
            const modal = new bootstrap.Modal(document.getElementById('evaluationModal'));
            modal.show();
        }
        
        // 평가 결과 저장
        function saveEvaluation() {
            console.log('saveEvaluation function called');
            
            // 완료 상태 확인 - 완료된 평가는 저장할 수 없음
            const headerCompletedDate = sessionStorage.getItem('headerCompletedDate');
            const isHeaderCompleted = headerCompletedDate && 
                                    headerCompletedDate !== 'null' && 
                                    headerCompletedDate !== null && 
                                    headerCompletedDate !== 'undefined' &&
                                    headerCompletedDate.trim() !== '' &&
                                    headerCompletedDate.trim() !== 'null';
            
            if (isHeaderCompleted) {
                console.log('Header completed, save blocked');
                return; // alert 없이 조용히 함수 종료
            }
            
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            console.log('Current evaluation session from storage:', currentSession);
            
            if (!currentSession) {
                alert('[DESIGN-003] 평가 세션 정보를 찾을 수 없습니다. 설계평가 목록에서 다시 시작해주세요.');
                return;
            }
            
            const adequacy = document.getElementById('descriptionAdequacy').value;
            const effectiveness = document.getElementById('overallEffectiveness').value;
            
            console.log('Form validation - adequacy:', adequacy, 'effectiveness:', effectiveness);
            
            if (!adequacy) {
                alert('[DESIGN-004] 통제활동 설명 적절성 평가는 필수 항목입니다.');
                return;
            }

            // 적절함인 경우에만 효과성 평가 필수
            if (adequacy === 'adequate' && !effectiveness) {
                alert('[DESIGN-005] 종합 설계 효과성 평가는 필수 항목입니다.');
                return;
            }
            
            const evaluation = {
                description_adequacy: adequacy,
                improvement_suggestion: document.getElementById('improvementSuggestion').value,
                overall_effectiveness: effectiveness,
                evaluation_rationale: document.getElementById('evaluationRationale').value,
                recommended_actions: document.getElementById('recommendedActions').value
            };
            
            // 서버에 결과 저장
            const controlCode = {% for detail in rcm_details %}
                {{ loop.index }} === currentEvaluationIndex ? '{{ detail.control_code }}' : 
            {% endfor %} null;
            
            console.log('Control code:', controlCode);
            
            if (!controlCode) {
                alert('[DESIGN-006] 통제 코드를 찾을 수 없습니다. 다시 시도해주세요.');
                return;
            }
            
            // 저장 버튼 비활성화 (중복 저장 방지)
            const saveButton = document.getElementById('saveEvaluationBtn') ||
                             document.querySelector('#evaluationModal .btn-success') || 
                             document.querySelector('#evaluationModal .btn-primary') || 
                             document.querySelector('#evaluationModal button[onclick="saveEvaluation()"]');
            
            console.log('Save button found:', saveButton);
            
            if (!saveButton) {
                console.error('Save button not found!');
                alert('[DESIGN-007] 저장 버튼을 찾을 수 없습니다.');
                return;
            }
            
            const originalText = saveButton.innerHTML;
            saveButton.disabled = true;
            saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>저장 중...';
            
            // 이미지 데이터 준비
            const imageData = evaluationImages[currentEvaluationIndex] || [];
            
            // FormData를 사용하여 이미지 파일과 함께 전송
            const formData = new FormData();
            formData.append('rcm_id', rcmId);
            formData.append('control_code', controlCode);
            formData.append('evaluation_data', JSON.stringify(evaluation));
            formData.append('evaluation_session', currentSession);
            
            // 이미지 파일들 추가
            if (imageData.length > 0) {
                imageData.forEach((file, index) => {
                    formData.append(`evaluation_image_${index}`, file);
                });
            }
            
            console.log('=== SENDING EVALUATION DATA ===');
            console.log('RCM ID:', rcmId);
            console.log('Control Code:', controlCode);
            console.log('Current Session:', currentSession);
            console.log('Evaluation Data:', evaluation);
            console.log('FormData contents:');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + (pair[1] instanceof File ? `File(${pair[1].name})` : pair[1]));
            }
            
            fetch('/api/design-evaluation/save', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.success) {
                    // 로컬 평가 결과에 evaluation_date 설정 (정식 평가 완료 표시)
                    evaluation.evaluation_date = new Date().toISOString();
                    evaluationResults[currentEvaluationIndex] = evaluation;
                    
                    // UI 즉시 업데이트
                    updateEvaluationUI(currentEvaluationIndex, evaluation);
                    updateProgress();
                    
                    // 서버에서 최신 데이터를 다시 로드하여 리스트 새로고침
                    // 저장 후에는 현재 세션의 최신 header_id를 사용하여 로드
                    loadExistingEvaluations();
                    
                    // 성공 메시지 표시
                    showSuccessMessage('평가가 성공적으로 저장되었습니다.');
                    
                    // 모달 닫기
                    const modal = bootstrap.Modal.getInstance(document.getElementById('evaluationModal'));
                    modal.hide();
                } else {
                    throw new Error(data.message || '저장에 실패했습니다.');
                }
            })
            .catch(error => {
                console.error('=== SAVE ERROR ===');
                console.error('Error type:', error.constructor.name);
                console.error('Error message:', error.message);
                console.error('Full error:', error);
                alert('[DESIGN-008] 저장 중 오류가 발생했습니다: ' + error.message);
            })
            .finally(() => {
                // 저장 버튼 복원
                saveButton.disabled = false;
                saveButton.innerHTML = originalText;
            });
        }
        
        // 평가 결과 UI 업데이트
        function updateEvaluationUI(index, evaluation) {
            const resultElement = document.getElementById(`result-${index}`);
            const actionElement = document.getElementById(`action-${index}`);
            const buttonElement = document.getElementById(`eval-btn-${index}`);
            
            // 헤더 완료 상태 확인
            const headerCompletedDate = sessionStorage.getItem('headerCompletedDate');
            const isHeaderCompleted = headerCompletedDate && headerCompletedDate !== 'null' && headerCompletedDate !== null && headerCompletedDate.trim() !== '';
            
            // 디버깅용 로그 추가
            console.log(`UpdateEvaluationUI - Index: ${index}, evaluation_date: ${evaluation.evaluation_date} (type: ${typeof evaluation.evaluation_date}), headerCompleted: ${isHeaderCompleted}, headerCompletedDate: '${headerCompletedDate}'`);
            
            // evaluation_date가 있을 때만 완료로 표시 (null, undefined, 빈 문자열 모두 제외)
            const hasValidEvaluationDate = evaluation.evaluation_date && 
                                         evaluation.evaluation_date !== '' && 
                                         evaluation.evaluation_date !== null &&
                                         evaluation.evaluation_date !== 'null';
            
            // 임시평가 데이터인지 확인 (evaluation_date는 없지만 평가 데이터는 있는 경우)
            const isTemporaryEvaluation = !hasValidEvaluationDate && 
                                        evaluation.description_adequacy && 
                                        evaluation.overall_effectiveness;
            
            console.log(`Index ${index} - hasValidEvaluationDate: ${hasValidEvaluationDate}, isTemporaryEvaluation: ${isTemporaryEvaluation}`);
            
            if (hasValidEvaluationDate) {
                // 결과 표시
                let resultClass = '';
                let resultText = '';

                // overall_effectiveness가 있으면 표시
                if (evaluation.overall_effectiveness) {
                    if (evaluation.overall_effectiveness === 'effective') {
                        resultClass = 'bg-success';
                        resultText = '적정';
                    } else {
                        // partially_effective, ineffective 모두 부적정
                        resultClass = 'bg-danger';
                        resultText = '부적정';
                    }
                } else if (evaluation.description_adequacy) {
                    // overall_effectiveness가 없으면 description_adequacy로 판단
                    if (evaluation.description_adequacy === 'adequate') {
                        resultClass = 'bg-success';
                        resultText = '적정';
                    } else {
                        // inadequate, missing, partially_adequate 모두 부적정
                        resultClass = 'bg-danger';
                        resultText = '부적정';
                    }
                }
                
                // 이미지가 있는지 확인
                let imageDisplay = '';
                if (evaluation.images && evaluation.images.length > 0) {
                    const imageCount = evaluation.images.length;
                    imageDisplay = `<br><small class="text-primary">
                        <i class="fas fa-image me-1"></i>${imageCount}개 첨부파일
                        <a href="#" onclick="showEvaluationImages(${index})" class="text-decoration-none ms-1">보기</a>
                    </small>`;
                }

                resultElement.innerHTML = `
                    <span class="badge ${resultClass}">${resultText}</span>
                    ${imageDisplay}
                `;
                
                actionElement.innerHTML = evaluation.recommended_actions || '<span class="text-muted">-</span>';
                
                // 버튼 상태 변경 - 완료
                if (isHeaderCompleted) {
                    // 헤더 완료 시 버튼 상태 변경 (조회용으로 활성화)
                    buttonElement.innerHTML = '<i class="fas fa-eye me-1"></i>조회';
                    buttonElement.classList.remove('btn-outline-success', 'btn-success', 'btn-secondary');
                    buttonElement.classList.add('btn-sm', 'btn-outline-info');
                    buttonElement.disabled = false;
                    buttonElement.title = '평가 결과를 조회합니다 (완료된 상태)';
                    buttonElement.setAttribute('data-bs-toggle', 'tooltip');
                } else {
                    buttonElement.innerHTML = '<i class="fas fa-check me-1"></i>완료';
                    buttonElement.classList.remove('btn-outline-success', 'btn-secondary', 'btn-outline-secondary');
                    buttonElement.classList.add('btn-sm', 'btn-success');
                    buttonElement.disabled = false;
                    buttonElement.title = '평가 결과를 수정합니다';
                    buttonElement.setAttribute('data-bs-toggle', 'tooltip');
                }
            } else if (isTemporaryEvaluation) {
                // 임시평가 데이터 표시 (저장되지 않은 샘플 데이터)
                let resultClass = '';
                let resultText = '';
                switch(evaluation.overall_effectiveness) {
                    case 'effective':
                        resultClass = 'bg-info';  // 파란색으로 임시 데이터 구분
                        resultText = '효과적 (임시)';
                        break;
                    case 'partially_effective':
                        resultClass = 'bg-info';
                        resultText = '부분적 효과적 (임시)';
                        break;
                    case 'ineffective':
                        resultClass = 'bg-info';
                        resultText = '비효과적 (임시)';
                        break;
                }
                
                resultElement.innerHTML = `
                    <span class="badge ${resultClass}" title="임시 데이터 - 저장되지 않음" data-bs-toggle="tooltip">${resultText}</span>
                `;
                
                // 조치사항도 (임시) 표시
                const actionText = evaluation.recommended_actions || '조치사항 없음';
                actionElement.innerHTML = `<span class="text-info" title="임시 데이터 - 저장되지 않음" data-bs-toggle="tooltip">${actionText} <small>(임시)</small></span>`;
                
                // 버튼 상태 - 임시평가 상태
                if (isHeaderCompleted) {
                    // 헤더 완료 시 버튼 상태 변경 (조회용으로 활성화)
                    buttonElement.innerHTML = '<i class="fas fa-eye me-1"></i>조회';
                    buttonElement.classList.remove('btn-success', 'btn-outline-primary', 'btn-secondary');
                    buttonElement.classList.add('btn-sm', 'btn-outline-info');
                    buttonElement.disabled = false;
                    buttonElement.title = '실제 평가 결과를 조회합니다 (완료된 상태)';
                    buttonElement.setAttribute('data-bs-toggle', 'tooltip');
                } else {
                    buttonElement.innerHTML = '<i class="fas fa-edit me-1"></i>실제평가';
                    buttonElement.classList.remove('btn-success', 'btn-secondary', 'btn-outline-secondary');
                    buttonElement.classList.add('btn-sm', 'btn-outline-primary');
                    buttonElement.disabled = false;
                    buttonElement.title = '실제 평가를 수행하여 저장하세요';
                    buttonElement.setAttribute('data-bs-toggle', 'tooltip');
                }
            } else {
                // evaluation_date가 없고 임시평가도 아니면 미평가 상태로 표시
                resultElement.innerHTML = '<span class="badge bg-secondary">미평가</span>';
                actionElement.innerHTML = '<span class="text-muted">-</span>';
                
                // 버튼 상태 - 미완료
                if (isHeaderCompleted) {
                    // 헤더 완료 시 버튼 상태 변경 (조회용으로 활성화)
                    buttonElement.innerHTML = '<i class="fas fa-eye me-1"></i>조회';
                    buttonElement.classList.remove('btn-success', 'btn-outline-success', 'btn-secondary');
                    buttonElement.classList.add('btn-sm', 'btn-outline-info');
                    buttonElement.disabled = false;
                    buttonElement.title = '평가 결과를 조회합니다 (완료된 상태)';
                    buttonElement.setAttribute('data-bs-toggle', 'tooltip');
                } else {
                    buttonElement.innerHTML = '<i class="fas fa-edit me-1"></i>평가';
                    buttonElement.classList.remove('btn-success', 'btn-secondary', 'btn-outline-secondary');
                    buttonElement.classList.add('btn-sm', 'btn-outline-success');
                    buttonElement.disabled = false;
                    buttonElement.title = '평가를 시작합니다';
                    buttonElement.setAttribute('data-bs-toggle', 'tooltip');
                }
            }
            
            // 툴팁 다시 초기화 (동적으로 변경된 버튼들을 위해)
            if (window.initializeTooltips) {
                window.initializeTooltips();
            }
            
            // 동적으로 생성된 버튼에 툴팁 속성 추가
            if (buttonElement.title) {
                buttonElement.setAttribute('data-bs-toggle', 'tooltip');
            }
        }
        
        // 진행률 업데이트 (header completed_date 기반)
        function updateProgress() {
            const totalControls = {{ rcm_details|length }};
            let evaluatedCount = 0;
            
            // evaluation_date가 있는 항목만 개별 완료로 계산 (완료 버튼 표시용)
            Object.values(evaluationResults).forEach(evaluation => {
                if (evaluation.evaluation_date) {
                    evaluatedCount++;
                }
            });
            
            // 간단한 디버깅 로그
            console.log(`평가 결과: 총 ${Object.keys(evaluationResults).length}개 중 ${evaluatedCount}개 완료`);
            
            // header의 completed_date가 있으면 전체 완료 상태
            const headerCompletedDate = sessionStorage.getItem('headerCompletedDate');
            const isCompleted = headerCompletedDate && headerCompletedDate !== 'null' && headerCompletedDate !== null && headerCompletedDate.trim() !== '';
            
            let progress, statusText, statusClass;
            
            if (isCompleted) {
                // 헤더에 완료일이 있으면 100% 완료
                progress = 100;
                statusText = '완료';
                statusClass = 'bg-success';
            } else {
                // 개별 평가 진행률로 표시
                progress = Math.round((evaluatedCount / totalControls) * 100);
                statusText = '진행중';
                statusClass = 'bg-primary';
            }
            
            document.getElementById('evaluationProgress').style.width = `${progress}%`;
            document.getElementById('evaluationProgress').setAttribute('aria-valuenow', progress);
            document.getElementById('evaluationProgress').textContent = `${progress}%`;
            document.getElementById('evaluatedCount').textContent = evaluatedCount;
            
            // 상태 업데이트
            const statusElement = document.getElementById('evaluationStatus');
            const completeBtn = document.getElementById('completeEvaluationBtn');
            const archiveBtn = document.getElementById('archiveEvaluationBtn');
            const downloadBtn = document.getElementById('downloadBtn');

            // 상태 표시 및 버튼 표시 로직
            statusElement.textContent = statusText;
            statusElement.className = `badge ${statusClass}`;

            // 버튼 표시 및 텍스트 설정
            if (isCompleted) {
                // 완료 상태면 완료취소 버튼 표시
                completeBtn.style.display = 'block';
                completeBtn.innerHTML = '<i class="fas fa-undo me-1"></i>완료취소';
                completeBtn.className = 'btn btn-sm btn-outline-warning';
                completeBtn.style.height = '70%';
                completeBtn.style.padding = '0.2rem 0.5rem';
                completeBtn.title = '설계평가 완료를 취소합니다';
                completeBtn.disabled = false;  // 명시적으로 활성화
                completeBtn.setAttribute('data-bs-toggle', 'tooltip');

                // 완료 상태에서만 Archive 버튼과 다운로드 버튼 표시
                archiveBtn.style.display = 'block';
                downloadBtn.style.display = 'block';
            } else if (evaluatedCount === totalControls) {
                // 모든 개별 평가가 완료되었지만 헤더 완료가 안된 경우
                completeBtn.style.display = 'block';
                completeBtn.innerHTML = '<i class="fas fa-check me-1"></i>완료처리';
                completeBtn.className = 'btn btn-sm btn-success';
                completeBtn.style.height = '70%';
                completeBtn.style.padding = '0.2rem 0.5rem';
                completeBtn.title = '설계평가를 완료 처리합니다';
                completeBtn.disabled = false;  // 명시적으로 활성화
                completeBtn.setAttribute('data-bs-toggle', 'tooltip');

                // 아직 완료되지 않았으므로 Archive 버튼과 다운로드 버튼 숨김
                archiveBtn.style.display = 'none';
                downloadBtn.style.display = 'none';
            } else {
                completeBtn.style.display = 'none';
                archiveBtn.style.display = 'none';
                downloadBtn.style.display = 'none';
            }
        }
        
        // 전체 평가 (샘플 데이터로 자동 평가 - 임시 데이터만 표시, 저장하지 않음)
        function evaluateAllControls() {
            if (!confirm('모든 통제에 대해 샘플 설계평가를 수행하시겠습니까?\n\n⚠️ 주의사항:\n- 이 기능은 임시 데이터를 생성하여 화면에만 표시합니다\n- 실제로 데이터베이스에 저장되지 않습니다\n- 실제 업무에서는 각 통제를 개별적으로 검토해야 합니다')) {
                return;
            }
            
            const totalControls = {{ rcm_details|length }};
            
            for (let i = 1; i <= totalControls; i++) {
                // evaluation_date가 없는 통제만 평가 (미완료 통제)
                if (!evaluationResults[i] || !evaluationResults[i].evaluation_date) {
                    // 현실적인 분포로 적정도 선택 (적절함 60%, 부분적으로 적절함 25%, 부적절함 10%, 누락 5%)
                    const adequacyRand = Math.random();
                    let adequacy;
                    if (adequacyRand < 0.6) {
                        adequacy = 'adequate';
                    } else if (adequacyRand < 0.85) {
                        adequacy = 'partially_adequate';
                    } else if (adequacyRand < 0.95) {
                        adequacy = 'inadequate';
                    } else {
                        adequacy = 'missing';
                    }
                    
                    // 현실적인 분포로 효과성 선택 (효과적 55%, 부분적으로 효과적 35%, 비효과적 10%)
                    const effectivenessRand = Math.random();
                    let effectiveness;
                    if (effectivenessRand < 0.55) {
                        effectiveness = 'effective';
                    } else if (effectivenessRand < 0.9) {
                        effectiveness = 'partially_effective';
                    } else {
                        effectiveness = 'ineffective';
                    }
                    
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
                    
                    // 임시 데이터로만 화면에 표시 (서버에 저장하지 않음)
                    evaluationResults[i] = evaluation;
                    updateEvaluationUI(i, evaluation);
                    
                    // evaluation_date는 설정하지 않음 (저장되지 않은 임시 데이터이므로)
                }
            }
            
            alert('[DESIGN-009] 임시 설계평가 데이터가 생성되었습니다.\n\n📢 안내사항:\n- 화면에 표시된 데이터는 임시 데이터입니다\n- 실제로 저장되지 않았습니다\n- 개별 통제를 클릭하여 실제 평가를 수행해주세요');
            
            // 임시 데이터이므로 서버에서 다시 로드하지 않음
        }
        
        // 전체 통제를 "적정" 값으로 실제 저장
        function saveAllAsAdequate() {
            if (!confirm('모든 통제를 "적절함 + 효과적"으로 실제 저장하시겠습니까?\n\n⚠️ 주의사항:\n- 이 작업은 실제로 데이터베이스에 저장됩니다\n- 이미 평가된 통제는 덮어쓰여집니다\n- 모든 통제가 "적절함 + 효과적"으로 저장됩니다')) {
                return;
            }
            
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            if (!currentSession) {
                alert('[DESIGN-010] 평가 세션을 먼저 생성해주세요.');
                return;
            }
            
            const totalControls = {{ rcm_details|length }};
            let savedCount = 0;
            let errors = [];
            
            // 각 통제에 대해 순차적으로 적정 값으로 저장
            function saveNext(index) {
                if (index > totalControls) {
                    // 모든 저장 완료
                    if (errors.length > 0) {
                        alert(`[DESIGN-011] 저장 완료!\n성공: ${savedCount}개\n실패: ${errors.length}개\n\n실패 목록:\n${errors.join('\n')}`);
                    } else {
                        alert(`[DESIGN-012] 모든 통제가 "적절함 + 효과적"으로 저장되었습니다!\n총 ${savedCount}개 통제 저장 완료`);
                    }
                    
                    // UI 업데이트 및 데이터 다시 로드
                    loadEvaluationData();
                    return;
                }
                
                // 통제 코드 찾기
                let controlCode = null;
                {% for detail in rcm_details %}
                if ({{ loop.index }} === index) {
                    controlCode = '{{ detail.control_code }}';
                }
                {% endfor %}
                
                if (!controlCode) {
                    saveNext(index + 1);
                    return;
                }
                
                // 모든 통제를 "적절함 + 효과적"으로 저장
                const evaluationData = {
                    description_adequacy: 'adequate',
                    improvement_suggestion: '',
                    overall_effectiveness: 'effective',
                    evaluation_rationale: '',
                    recommended_actions: ''
                };
                
                // 서버에 저장
                fetch('/api/design-evaluation/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        rcm_id: {{ rcm_id }},
                        control_code: controlCode,
                        evaluation_data: evaluationData,
                        evaluation_session: currentSession
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(`${controlCode} 저장 결과:`, data);
                    if (data.success) {
                        savedCount++;
                    } else {
                        const errorMsg = `${controlCode}: ${data.message || '알 수 없는 오류'}`;
                        console.error(errorMsg);
                        errors.push(errorMsg);
                    }
                    // 다음 통제 저장
                    saveNext(index + 1);
                })
                .catch(error => {
                    const errorMsg = `${controlCode}: ${error.message || '네트워크 오류'}`;
                    console.error('저장 실패:', errorMsg, error);
                    errors.push(errorMsg);
                    // 다음 통제 저장
                    saveNext(index + 1);
                });
            }
            
            // 첫 번째 통제부터 시작
            saveNext(1);
        }
        
        // 평가 완료/완료취소 처리
        function completeEvaluation() {
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            if (!currentSession) {
                alert('[DESIGN-013] 평가 세션 정보를 찾을 수 없습니다.');
                return;
            }
            
            const headerCompletedDate = sessionStorage.getItem('headerCompletedDate');
            const isCompleted = headerCompletedDate && headerCompletedDate !== 'null' && headerCompletedDate !== null && headerCompletedDate.trim() !== '';
            const completeBtn = document.getElementById('completeEvaluationBtn');
            
            if (isCompleted) {
                // 완료취소 처리 - 기본 확인 메시지 (운영평가 여부는 서버에서 확인)
                if (!confirm('설계평가 완료를 취소하시겠습니까?\n\n완료 취소 후에는 평가 상태가 "진행중"으로 변경됩니다.')) {
                    return;
                }

                const originalText = completeBtn.innerHTML;
                completeBtn.disabled = true;
                completeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>취소 중...';

                fetch('/api/design-evaluation/cancel', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        rcm_id: {{ rcm_id }},
                        evaluation_session: currentSession
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 운영평가가 있는 경우 추가 알림
                        if (data.has_operation_evaluation) {
                            alert('⚠️ 참고: 이 설계평가를 기반으로 한 운영평가가 진행중입니다.\n\n설계평가를 다시 완료처리해야 운영평가를 이어서 진행할 수 있습니다.');
                        }
                        // sessionStorage에서 완료일 제거 (더 확실하게)
                        sessionStorage.removeItem('headerCompletedDate');
                        sessionStorage.setItem('headerCompletedDate', '');
                        sessionStorage.removeItem('headerCompletedDate');
                        console.log('HeaderCompletedDate removed from sessionStorage');
                        console.log('SessionStorage check after removal:', sessionStorage.getItem('headerCompletedDate'));
                        
                        // 진행률 업데이트
                        updateProgress();
                        
                        // 모든 개별 평가 항목의 UI 업데이트 (버튼 상태 변경)
                        console.log('완료 취소 후 UI 업데이트 시작');
                        Object.keys(evaluationResults).forEach(index => {
                            if (evaluationResults[index]) {
                                console.log(`Index ${index} UI 업데이트 중...`);
                                updateEvaluationUI(index, evaluationResults[index]);
                                
                                // 버튼 상태 재확인
                                const btn = document.getElementById(`eval-btn-${index}`);
                                console.log(`Button ${index} 상태 - disabled: ${btn.disabled}, innerHTML: ${btn.innerHTML}`);
                            }
                        });
                        console.log('완료 취소 후 UI 업데이트 완료');

                    } else {
                        alert('[DESIGN-014] 완료 취소 중 오류가 발생했습니다: ' + data.message);
                        // 버튼 원복
                        completeBtn.disabled = false;
                        completeBtn.innerHTML = originalText;
                    }
                })
                .catch(error => {
                    console.error('완료 취소 오류:', error);
                    alert('[DESIGN-015] 완료 취소 중 오류가 발생했습니다: ' + error.message);
                    // 버튼 원복
                    completeBtn.disabled = false;
                    completeBtn.innerHTML = originalText;
                });
            } else {
                // 완료 처리 전 효과적이지 않은 통제 확인
                const ineffectiveControls = [];
                Object.keys(evaluationResults).forEach(index => {
                    const evaluation = evaluationResults[index];
                    if (evaluation && evaluation.overall_effectiveness) {
                        if (evaluation.overall_effectiveness === 'partially_effective' ||
                            evaluation.overall_effectiveness === 'ineffective') {
                            // 통제 코드 찾기
                            const controlCode = {% for detail in rcm_details %}
                                {{ loop.index }} === parseInt(index) ? '{{ detail.control_code }}' :
                            {% endfor %} null;

                            if (controlCode) {
                                const effectivenessText = evaluation.overall_effectiveness === 'partially_effective'
                                    ? '부분적으로 효과적'
                                    : '비효과적';
                                ineffectiveControls.push(`${controlCode} (${effectivenessText})`);
                            }
                        }
                    }
                });

                // 효과적이지 않은 통제가 있는 경우 경고 메시지
                let confirmMessage = '설계평가를 완료 처리하시겠습니까?\n\n완료 처리 후에는 평가 상태가 "완료"로 변경되며,\n완료일시가 기록됩니다.';

                if (ineffectiveControls.length > 0) {
                    confirmMessage = `⚠️ 효과적이지 않은 통제가 있습니다:\n\n${ineffectiveControls.join('\n')}\n\n그래도 완료 처리하시겠습니까?`;
                }

                if (!confirm(confirmMessage)) {
                    return;
                }
                
                const originalText = completeBtn.innerHTML;
                completeBtn.disabled = true;
                completeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>처리 중...';
                
                fetch('/api/design-evaluation/complete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        rcm_id: {{ rcm_id }},
                        evaluation_session: currentSession
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // sessionStorage에 완료일 저장
                        sessionStorage.setItem('headerCompletedDate', data.completed_date);
                        
                        // 진행률 업데이트 (새로운 로직 사용)
                        updateProgress();
                        
                        // 모든 개별 평가 항목의 UI 즉시 업데이트 (버튼을 "완료됨"으로 변경)
                        Object.keys(evaluationResults).forEach(index => {
                            if (evaluationResults[index]) {
                                updateEvaluationUI(index, evaluationResults[index]);
                            }
                        });
                        
                    } else {
                        alert('[DESIGN-016] 완료 처리 중 오류가 발생했습니다: ' + data.message);
                        // 버튼 원복
                        completeBtn.disabled = false;
                        completeBtn.innerHTML = originalText;
                    }
                })
                .catch(error => {
                    console.error('완료 처리 오류:', error);
                    alert('[DESIGN-017] 완료 처리 중 오류가 발생했습니다: ' + error.message);
                    // 버튼 원복
                    completeBtn.disabled = false;
                    completeBtn.innerHTML = originalText;
                });
            }
        }

        // 평가 Archive 처리
        function archiveEvaluation() {
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            if (!currentSession) {
                alert('[DESIGN-018] 평가 세션 정보를 찾을 수 없습니다.');
                return;
            }

            const headerCompletedDate = sessionStorage.getItem('headerCompletedDate');
            const isCompleted = headerCompletedDate && headerCompletedDate !== 'null' && headerCompletedDate !== null && headerCompletedDate.trim() !== '';

            if (!isCompleted) {
                alert('[DESIGN-019] 완료된 설계평가만 Archive 처리할 수 있습니다.');
                return;
            }

            if (!confirm(`설계평가 세션 "${currentSession}"을 Archive 처리하시겠습니까?\n\nArchive 처리하면 해당 세션이 목록에서 숨겨지며,\n필요시 복원할 수 있습니다.`)) {
                return;
            }

            const archiveBtn = document.getElementById('archiveEvaluationBtn');
            const originalText = archiveBtn.innerHTML;
            archiveBtn.disabled = true;
            archiveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>처리 중...';

            fetch('/api/design-evaluation/archive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    rcm_id: {{ rcm_id }},
                    evaluation_session: currentSession
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Archive 처리가 완료되었습니다.');
                    // 설계평가 목록 페이지로 이동
                    window.location.href = '/user/design-evaluation';
                } else {
                    alert('[DESIGN-020] Archive 처리 중 오류가 발생했습니다: ' + data.message);
                    // 버튼 원복
                    archiveBtn.disabled = false;
                    archiveBtn.innerHTML = originalText;
                }
            })
            .catch(error => {
                console.error('Archive 처리 오류:', error);
                alert('[DESIGN-021] Archive 처리 중 오류가 발생했습니다: ' + error.message);
                // 버튼 원복
                archiveBtn.disabled = false;
                archiveBtn.innerHTML = originalText;
            });
        }

        // 서버에 평가 결과 저장 (전체 평가용)
        function saveEvaluationToServer(controlIndex, evaluation) {
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            if (!currentSession) {
                console.error('평가 세션 정보가 없습니다.');
                return;
            }
            
            // 컨트롤 코드 찾기
            let controlCode = null;
            {% for detail in rcm_details %}
            if ({{ loop.index }} === controlIndex) {
                controlCode = '{{ detail.control_code }}';
            }
            {% endfor %}
            
            if (!controlCode) {
                console.error('통제 코드를 찾을 수 없습니다.');
                return;
            }
            
            const requestData = {
                rcm_id: rcmId,
                control_code: controlCode,
                evaluation_data: evaluation,
                evaluation_session: currentSession
            };
            
            fetch('/api/design-evaluation/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error(`통제 ${controlCode} 저장 실패:`, data.message);
                }
            })
            .catch(error => {
                console.error(`통제 ${controlCode} 저장 오류:`, error);
            });
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
                    
                    alert('[DESIGN-018] 모든 설계평가가 초기화되었습니다.');
                } else {
                    alert('[DESIGN-019] 초기화 실패: ' + data.message);
                }
            })
            .catch(error => {
                console.error('초기화 오류:', error);
                alert('[DESIGN-020] 초기화 중 오류가 발생했습니다.');
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
            // 새로운 엑셀 다운로드 API 호출
            const downloadUrl = `/api/design-evaluation/download-excel/{{ rcm_id }}`;
            
            // 로딩 표시
            const downloadBtn = document.getElementById('downloadBtn');
            const originalText = downloadBtn.innerHTML;
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>생성 중...';
            
            // 새 창에서 다운로드 실행
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.target = '_blank';
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // 버튼 상태 복원 (약간의 딜레이 후)
            setTimeout(() => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = originalText;
            }, 2000);
        }
        

        // 평가 목록 새로고침
        function refreshEvaluationList() {
            console.log('평가 목록 새로고침 시작...');

            // 버튼 찾기
            const refreshBtn = event.target.closest('button');
            if (!refreshBtn) {
                console.error('새로고침 버튼을 찾을 수 없습니다.');
                return;
            }

            // 버튼 상태 변경
            const originalHTML = refreshBtn.innerHTML;
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>로딩 중...';

            // 아이콘 회전 애니메이션
            const icon = refreshBtn.querySelector('i');
            if (icon) {
                icon.classList.add('fa-spin');
            }

            // 기존 평가 데이터 다시 로드
            loadExistingEvaluations();

            // 진행률 업데이트
            updateProgress();

            // 버튼 복원 (1초 후)
            setTimeout(() => {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = originalHTML;
                showSuccessMessage('평가 목록이 새로고침되었습니다.');
            }, 1000);
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
                            evaluation_data: evaluation,
                            evaluation_session: sessionStorage.getItem('currentEvaluationSession')
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
        
        // Bootstrap 툴팁 초기화
        document.addEventListener('DOMContentLoaded', function() {
            // 기존 툴팁 초기화
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            // 동적으로 생성되는 요소들을 위한 툴팁 초기화 함수
            window.initializeTooltips = function() {
                // 기존 툴팁 제거
                tooltipList.forEach(function(tooltip) {
                    tooltip.dispose();
                });
                
                // 새로운 툴팁 초기화 - data-bs-toggle="tooltip" 속성이 있는 요소들만
                var newTooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                newTooltipTriggerList.forEach(function(el) {
                    new bootstrap.Tooltip(el);
                });
                
                // tooltipList 업데이트
                tooltipList = newTooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            };
        });
    </script>
</body>
</html>