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
                                        <div class="progress-bar bg-success" id="evaluationProgress" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
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
                        <div>
                            <button class="btn btn-sm btn-success me-2" onclick="evaluateAllControls()" title="임시 데이터를 생성하여 화면에만 표시 (실제 저장되지 않음)">
                                <i class="fas fa-check-double me-1"></i>전체 평가 (임시)
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
                                        <th width="6%">통제코드</th>
                                        <th width="12%">통제명</th>
                                        <th width="28%">통제활동설명</th>
                                        <th width="8%">통제주기</th>
                                        <th width="8%">통제유형</th>
                                        <th width="9%">설계평가</th>
                                        <th width="9%">평가결과</th>
                                        <th width="18%">조치사항</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr id="control-row-{{ loop.index }}">
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td><strong>{{ detail.control_name }}</strong></td>
                                        <td>
                                            <div style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; max-height: calc(1.4em * 2);" 
                                                 title="{{ detail.control_description or '-' }}">
                                                {{ detail.control_description or '-' }}
                                            </div>
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
                    <div class="card mb-3">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0"><i class="fas fa-check-circle me-2"></i>설계 효과성 종합 평가</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="overallEffectiveness" class="form-label">실제 통제 운영 효과성 *</label>
                                <select class="form-select" id="overallEffectiveness" required>
                                    <option value="">평가 결과 선택</option>
                                    <option value="effective">효과적 - 현재 실제로 효과적으로 운영되고 있음</option>
                                    <option value="partially_effective">부분적으로 효과적 - 실무 운영에 일부 개선이 필요함</option>
                                    <option value="ineffective">비효과적 - 실제 위험 완화 효과가 부족함</option>
                                </select>
                            </div>
                            
                            <div class="mb-3">
                                <label for="evaluationRationale" class="form-label">평가 근거</label>
                                <textarea class="form-control" id="evaluationRationale" rows="3" 
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
                alert('첨부된 이미지가 없습니다.');
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
            }
            
            // 평가명 화면에 표시
            updateEvaluationNameDisplay();
            
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
            
            let url;
            if (headerId && headerId !== 'null' && headerId !== 'undefined') {
                url = `/api/design-evaluation/load/${rcmId}?header_id=${headerId}`;
                console.log('Using header_id route');
            } else if (currentSession) {
                url = `/api/design-evaluation/load/${rcmId}?session=${encodeURIComponent(currentSession)}`;
                console.log('Using session route');
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
                document.getElementById('modalControlNature').textContent = '{{ detail.control_nature or "-" }}';
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
                
                document.getElementById('descriptionAdequacy').value = result.adequacy || '';
                document.getElementById('improvementSuggestion').value = result.improvement || '';
                document.getElementById('overallEffectiveness').value = result.effectiveness || '';
                document.getElementById('evaluationRationale').value = result.rationale || '';
                document.getElementById('recommendedActions').value = result.actions || '';
                
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
            
            const modal = new bootstrap.Modal(document.getElementById('evaluationModal'));
            modal.show();
        }
        
        // 평가 결과 저장
        function saveEvaluation() {
            // 세션 스토리지 전체 상태 확인
            console.log('=== SessionStorage Debug ===');
            console.log('sessionStorage length:', sessionStorage.length);
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                console.log(`${key}: ${sessionStorage.getItem(key)}`);
            }
            
            const currentSession = sessionStorage.getItem('currentEvaluationSession');
            console.log('Current evaluation session from storage:', currentSession);
            console.log('Type of currentSession:', typeof currentSession);
            console.log('currentSession is null:', currentSession === null);
            console.log('currentSession is empty string:', currentSession === '');
            
            if (!currentSession) {
                alert('평가 세션 정보를 찾을 수 없습니다. 설계평가 목록에서 다시 시작해주세요.');
                return;
            }
            
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
                // 이미지 데이터 준비
                const imageData = evaluationImages[currentEvaluationIndex] || [];
                const imageFileNames = imageData.map(file => file.name);
                
                const requestData = {
                    rcm_id: rcmId,
                    control_code: controlCode,
                    evaluation_data: evaluation,
                    evaluation_session: currentSession,
                    image_files: imageFileNames
                };
                
                console.log('=== API Request Debug ===');
                console.log('Sending evaluation data:', requestData);
                console.log('Request data stringified:', JSON.stringify(requestData, null, 2));
                console.log('evaluation_session in request:', requestData.evaluation_session);
                
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
                
                fetch('/api/design-evaluation/save', {
                    method: 'POST',
                    // Content-Type 헤더를 제거 (FormData가 자동으로 설정)
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        
                        // 서버에서 최신 데이터를 다시 로드하여 리스트 새로고침
                        loadExistingEvaluations();
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
            
            // 디버깅용 로그 추가
            console.log(`UpdateEvaluationUI - Index: ${index}, evaluation_date: ${evaluation.evaluation_date} (type: ${typeof evaluation.evaluation_date})`);
            
            // evaluation_date가 있을 때만 완료로 표시 (null, undefined, 빈 문자열 모두 제외)
            const hasValidEvaluationDate = evaluation.evaluation_date && 
                                         evaluation.evaluation_date !== '' && 
                                         evaluation.evaluation_date !== null &&
                                         evaluation.evaluation_date !== 'null';
            
            // 임시평가 데이터인지 확인 (evaluation_date는 없지만 평가 데이터는 있는 경우)
            const isTemporaryEvaluation = !hasValidEvaluationDate && 
                                        evaluation.adequacy && 
                                        evaluation.effectiveness;
            
            console.log(`Index ${index} - hasValidEvaluationDate: ${hasValidEvaluationDate}, isTemporaryEvaluation: ${isTemporaryEvaluation}`);
            
            if (hasValidEvaluationDate) {
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
                    <br><small class="text-muted">(${adequacyText})</small>
                    ${imageDisplay}
                `;
                
                actionElement.innerHTML = evaluation.actions || '<span class="text-muted">-</span>';
                
                // 버튼 상태 변경 - 완료
                buttonElement.innerHTML = '<i class="fas fa-check me-1"></i>완료';
                buttonElement.classList.remove('btn-outline-success');
                buttonElement.classList.add('btn-success');
            } else if (isTemporaryEvaluation) {
                // 임시평가 데이터 표시 (저장되지 않은 샘플 데이터)
                let resultClass = '';
                let resultText = '';
                switch(evaluation.effectiveness) {
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
                    <span class="badge ${resultClass}" title="임시 데이터 - 저장되지 않음">${resultText}</span>
                    <br><small class="text-muted">(${adequacyText})</small>
                `;
                
                // 조치사항도 (임시) 표시
                const actionText = evaluation.actions || '조치사항 없음';
                actionElement.innerHTML = `<span class="text-info" title="임시 데이터 - 저장되지 않음">${actionText} <small>(임시)</small></span>`;
                
                // 버튼 상태 - 임시평가 상태
                buttonElement.innerHTML = '<i class="fas fa-edit me-1"></i>실제평가';
                buttonElement.classList.remove('btn-success');
                buttonElement.classList.add('btn-outline-primary');
                buttonElement.title = '실제 평가를 수행하여 저장하세요';
            } else {
                // evaluation_date가 없고 임시평가도 아니면 미평가 상태로 표시
                resultElement.innerHTML = '<span class="badge bg-secondary">미평가</span>';
                actionElement.innerHTML = '<span class="text-muted">-</span>';
                
                // 버튼 상태 - 미완료
                buttonElement.innerHTML = '<i class="fas fa-edit me-1"></i>평가';
                buttonElement.classList.remove('btn-success');
                buttonElement.classList.add('btn-outline-success');
            }
        }
        
        // 진행률 업데이트 (evaluation_date 기반)
        function updateProgress() {
            const totalControls = {{ rcm_details|length }};
            let evaluatedCount = 0;
            
            // evaluation_date가 있는 항목만 완료로 계산
            Object.values(evaluationResults).forEach(evaluation => {
                if (evaluation.evaluation_date) {
                    evaluatedCount++;
                }
            });
            
            const progress = Math.round((evaluatedCount / totalControls) * 100);
            
            document.getElementById('evaluationProgress').style.width = `${progress}%`;
            document.getElementById('evaluationProgress').setAttribute('aria-valuenow', progress);
            document.getElementById('evaluationProgress').textContent = `${progress}%`;
            document.getElementById('evaluatedCount').textContent = evaluatedCount;
            
            // 상태 업데이트
            const statusElement = document.getElementById('evaluationStatus');
            if (evaluatedCount === 0) {
                statusElement.textContent = '준비 중';
                statusElement.className = 'badge bg-secondary';
            } else if (evaluatedCount < totalControls) {
                statusElement.textContent = '진행 중';
                statusElement.className = 'badge bg-warning';
            } else {
                statusElement.textContent = '완료';
                statusElement.className = 'badge bg-success';
            }
        }
        
        // 전체 평가 (샘플 데이터로 자동 평가 - 임시 데이터만 표시, 저장하지 않음)
        function evaluateAllControls() {
            if (!confirm('모든 통제에 대해 샘플 설계평가를 수행하시겠습니까?\n\n⚠️ 주의사항:\n- 이 기능은 임시 데이터를 생성하여 화면에만 표시합니다\n- 실제로 데이터베이스에 저장되지 않습니다\n- 실제 업무에서는 각 통제를 개별적으로 검토해야 합니다')) {
                return;
            }
            
            const totalControls = {{ rcm_details|length }};
            const sampleAdequacies = ['adequate', 'partially_adequate', 'inadequate', 'missing'];
            const sampleEffectiveness = ['effective', 'partially_effective', 'ineffective'];
            
            for (let i = 1; i <= totalControls; i++) {
                // evaluation_date가 없는 통제만 평가 (미완료 통제)
                if (!evaluationResults[i] || !evaluationResults[i].evaluation_date) {
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
                    
                    // 임시 데이터로만 화면에 표시 (서버에 저장하지 않음)
                    evaluationResults[i] = evaluation;
                    updateEvaluationUI(i, evaluation);
                    
                    // evaluation_date는 설정하지 않음 (저장되지 않은 임시 데이터이므로)
                }
            }
            
            alert('임시 설계평가 데이터가 생성되었습니다.\n\n📢 안내사항:\n- 화면에 표시된 데이터는 임시 데이터입니다\n- 실제로 저장되지 않았습니다\n- 개별 통제를 클릭하여 실제 평가를 수행해주세요');
            
            // 임시 데이터이므로 서버에서 다시 로드하지 않음
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
    </script>
</body>
</html>