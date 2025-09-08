<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 검토 - {{ rcm_info.rcm_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .completeness-score {
            font-size: 3rem;
            font-weight: bold;
        }
        .score-excellent { color: #28a745; }
        .score-good { color: #17a2b8; }
        .score-average { color: #ffc107; }
        .score-poor { color: #dc3545; }
        
        .control-item {
            border-left: 4px solid #e9ecef;
            margin-bottom: 1rem;
        }
        .control-item.mapped { border-left-color: #28a745; }
        .control-item.unmapped { border-left-color: #dc3545; }
        
        .progress-custom {
            height: 25px;
        }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-chart-bar me-2"></i>RCM 검토</h1>
                    <div>
                        <a href="/rcm/{{ rcm_info.rcm_id }}/view" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-1"></i>상세보기로
                        </a>
                    </div>
                </div>
                <hr>
            </div>
        </div>

        <!-- 평가 개요 -->
        <div class="row mb-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>평가 개요</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-borderless">
                            <tr>
                                <th width="25%">RCM명:</th>
                                <td><strong>{{ rcm_info.rcm_name }}</strong></td>
                            </tr>
                            <tr>
                                <th>회사명:</th>
                                <td>{{ rcm_info.company_name }}</td>
                            </tr>
                            <tr>
                                <th>총 통제 수:</th>
                                <td>{{ eval_result.total_controls }}개</td>
                            </tr>
                            <tr>
                                <th>기준통제 매핑:</th>
                                <td>
                                    {{ eval_result.mapped_controls }}개 
                                    <small class="text-muted">
                                        ({{ "%.1f"|format((eval_result.mapped_controls / eval_result.total_controls * 100) if eval_result.total_controls > 0 else 0) }}%)
                                    </small>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-header">
                        <h5><i class="fas fa-trophy me-2"></i>전체 완성도</h5>
                    </div>
                    <div class="card-body">
                        <div class="completeness-score 
                            {% if eval_result.completeness_score >= 90 %}score-excellent
                            {% elif eval_result.completeness_score >= 70 %}score-good
                            {% elif eval_result.completeness_score >= 50 %}score-average
                            {% else %}score-poor{% endif %}">
                            {{ eval_result.completeness_score }}%
                        </div>
                        <div class="progress progress-custom mt-3">
                            <div class="progress-bar 
                                {% if eval_result.completeness_score >= 90 %}bg-success
                                {% elif eval_result.completeness_score >= 70 %}bg-info
                                {% elif eval_result.completeness_score >= 50 %}bg-warning
                                {% else %}bg-danger{% endif %}" 
                                style="width: {{ eval_result.completeness_score }}%"></div>
                        </div>
                        <small class="text-muted mt-2 d-block">
                            {% if eval_result.completeness_score >= 90 %}우수
                            {% elif eval_result.completeness_score >= 70 %}양호
                            {% elif eval_result.completeness_score >= 50 %}보통
                            {% else %}개선 필요{% endif %}
                        </small>
                    </div>
                </div>
            </div>
        </div>

        <!-- 기준통제별 매핑 결과 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list-check me-2"></i>기준통제별 매핑 현황</h5>
                        <div class="float-end">
                            <button id="autoSaveIndicator" class="btn btn-sm btn-success me-2" disabled title="모든 매핑과 AI 검토 결과가 실시간으로 자동 저장됩니다" style="display: none;">
                                <i class="fas fa-check me-1"></i>자동 저장됨
                            </button>
                            <button class="btn btn-sm btn-primary" onclick="bulkAiReview()" title="매핑된 항목 중 AI 검토가 완료되지 않은 항목을 모두 처리합니다">
                                <i class="fas fa-magic me-1"></i>AI 전체 검토
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="standardControlsTables">
                            <!-- JavaScript로 동적 생성 -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 개선 권고사항 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card border-info">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="fas fa-lightbulb me-2"></i>개선 권고사항</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            {% if eval_result.mapped_controls < eval_result.total_controls %}
                                <li class="mb-2">
                                    <i class="fas fa-arrow-right text-primary me-2"></i>
                                    <strong>기준통제 매핑:</strong> 
                                    {{ eval_result.total_controls - eval_result.mapped_controls }}개의 통제가 기준통제에 매핑되지 않았습니다. 
                                    각 통제를 적절한 기준통제에 매핑하여 평가 범위를 확대하세요.
                                </li>
                            {% endif %}
                            
                            
                            {% if eval_result.completeness_score < 70 %}
                                <li class="mb-2">
                                    <i class="fas fa-arrow-right text-danger me-2"></i>
                                    <strong>전체적인 품질 향상:</strong> 
                                    완성도가 70% 미만입니다. 통제 설명, 절차, 테스트 방법 등을 더 구체적으로 작성하세요.
                                </li>
                            {% endif %}
                            
                            {% if eval_result.completeness_score >= 90 %}
                                <li class="mb-2">
                                    <i class="fas fa-arrow-right text-success me-2"></i>
                                    <strong>우수한 완성도:</strong> 
                                    RCM 문서가 잘 작성되어 있습니다. 정기적인 검토를 통해 품질을 유지하세요.
                                </li>
                            {% endif %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- RCM 통제 상세정보 모달 -->
    <div class="modal fade" id="rcmDetailModal" tabindex="-1" aria-labelledby="rcmDetailModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="rcmDetailModalLabel">
                        <i class="fas fa-info-circle me-2"></i>통제 상세정보
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div id="rcmDetailContent">
                        <!-- 동적으로 생성될 내용 -->
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let standardControls = [];
        let rcmControls = [];
        let existingMappings = {};
        let aiReviewResults = {}; // AI 검토 결과 저장용
        let autoSaveTimeout;
        
        document.addEventListener('DOMContentLoaded', function() {
            loadStandardControls();
            loadRcmControls();
            // loadPreviousResultOnStart(); // 개별 통제 API로 변경 후 재활성화 예정
        });
        
        // control_code로 detail_id 찾기
        function findDetailId(controlCode) {
            if (!controlCode) return '';
            const rcmControl = rcmControls.find(rc => rc.control_code === controlCode);
            return rcmControl ? rcmControl.detail_id : '';
        }
        
        // 기준통제 목록 로드
        function loadStandardControls() {
            fetch('/api/standard-controls')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        standardControls = data.controls;
                        loadExistingMappings();
                    }
                })
                .catch(error => console.error('기준통제 로드 오류:', error));
        }
        
        // RCM 통제 목록 로드
        function loadRcmControls() {
            // 평가 결과에서 RCM 통제 목록 추출
            rcmControls = {{ rcm_details|tojson }};
        }
        
        // 기존 매핑 정보 및 AI 검토 결과 로드 (rcm_details에서 직접 구성)
        function loadExistingMappings() {
            // rcm_details에서 매핑 및 AI 검토 결과 구성
            rcmControls.forEach(rcmControl => {
                // 매핑 정보 복원
                if (rcmControl.mapped_std_control_id) {
                    const stdControlId = parseInt(rcmControl.mapped_std_control_id);
                    existingMappings[stdControlId] = {
                        control_code: rcmControl.control_code,
                        rcm_control_name: rcmControl.control_name
                    };
                    
                    // 해당 통제의 AI 검토 결과도 복원
                    if (rcmControl.ai_review_status === 'completed' && rcmControl.ai_review_recommendation) {
                        aiReviewResults[stdControlId] = {
                            status: rcmControl.ai_review_status,
                            recommendation: rcmControl.ai_review_recommendation,
                            reviewed_date: rcmControl.ai_reviewed_date,
                            reviewed_by: rcmControl.ai_reviewed_by
                        };
                    }
                }
            });
            
            renderStandardControlsList();
        }
        
        // 기준통제 테이블 렌더링
        function renderStandardControlsList() {
            const container = document.getElementById('standardControlsTables');
            const groupedControls = {};
            
            // 카테고리별로 그룹화
            standardControls.forEach(control => {
                if (!groupedControls[control.control_category]) {
                    groupedControls[control.control_category] = [];
                }
                groupedControls[control.control_category].push(control);
            });
            
            let html = '';
            // 카테고리 정렬 순서 정의
            const categoryOrder = ['APD', 'PC', 'CO', 'PD'];
            const sortedCategories = categoryOrder.filter(cat => groupedControls[cat]);
            // 정의되지 않은 카테고리도 추가
            Object.keys(groupedControls).forEach(cat => {
                if (!categoryOrder.includes(cat)) {
                    sortedCategories.push(cat);
                }
            });
            
            sortedCategories.forEach(category => {
                html += `<div class="mb-4">`;
                html += `<h6 class="text-primary border-bottom pb-2 mb-3">`;
                html += `<i class="fas fa-folder-open me-2"></i>${category}`;
                html += `</h6>`;
                
                // 테이블 시작
                html += `<div class="table-responsive">`;
                html += `<table class="table table-hover">`;
                html += `<thead class="table-light">`;
                html += `<tr>`;
                html += `<th width="16%">통제명</th>`;
                html += `<th width="30%">통제설명</th>`;
                html += `<th width="18%">RCM 통제 선택</th>`;
                html += `<th width="13%">AI 검토</th>`;
                html += `<th width="5%">상태</th>`;
                html += `<th width="18%">개선권고사항</th>`;
                html += `</tr>`;
                html += `</thead>`;
                html += `<tbody>`;
                
                groupedControls[category].forEach(control => {
                    const mapping = existingMappings[control.std_control_id];
                    const isMapped = !!mapping;
                    
                    html += `<tr class="${isMapped ? 'table-success' : ''}">`;
                    
                    // 통제명
                    html += `<td>`;
                    html += `<strong>${control.control_name}</strong>`;
                    html += `</td>`;
                    
                    // 통제설명
                    html += `<td>`;
                    if (control.control_description) {
                        html += `<div style="max-height: 60px; overflow-y: auto; font-size: 0.9rem;">`;
                        html += control.control_description;
                        html += `</div>`;
                    } else {
                        html += `<span class="text-muted">설명 없음</span>`;
                    }
                    html += `</td>`;
                    
                    // RCM 통제 선택
                    html += `<td>`;
                    html += `<select class="form-select form-select-sm" 
                              onchange="updateMapping(${control.std_control_id}, this.value, '${control.control_name.replace(/'/g, "\\'")}', findDetailId(this.value))"
                              id="select_${control.std_control_id}">`;
                    html += `<option value="">통제 선택...</option>`;
                    
                    rcmControls.forEach(rcmControl => {
                        const isSelected = mapping && mapping.control_code === rcmControl.control_code;
                        const controlName = rcmControl.control_name.replace(/"/g, '&quot;');
                        html += `<option value="${rcmControl.control_code}" ${isSelected ? 'selected' : ''}>`;
                        html += `${rcmControl.control_code} - ${controlName}`;
                        html += `</option>`;
                    });
                    
                    html += `</select>`;
                    html += `</td>`;
                    
                    // AI 검토 버튼
                    html += `<td class="text-center">`;
                    const aiResult = aiReviewResults[control.std_control_id];
                    if (isMapped) {
                        // RCM 컨트롤의 detail_id 찾기
                        const rcmControl = rcmControls.find(rc => rc.control_code === mapping.control_code);
                        const detailId = rcmControl ? rcmControl.detail_id : '';
                        
                        // 상세보기 버튼 먼저 배치 (작은 사이즈)
                        html += `<button class="btn btn-xs btn-outline-info me-1" 
                                  onclick="showRcmDetail('${mapping.control_code}')"
                                  title="RCM 통제 상세정보 보기"
                                  style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">
                                  <i class="fas fa-eye"></i>
                                  </button>`;
                        
                        if (aiResult && aiResult.status === 'completed') {
                            // AI 검토 완료된 상태
                            html += `<button class="btn btn-xs btn-success" 
                                      onclick="startAiReview(${control.std_control_id}, '${control.control_name.replace(/'/g, "\\'")}', '${mapping.control_code}', ${detailId})"
                                      id="ai_btn_${control.std_control_id}"
                                      style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">`;
                            html += `<i class="fas fa-check me-1"></i>완료`;
                            html += `</button>`;
                        } else {
                            // AI 검토 대기 상태
                            html += `<button class="btn btn-xs btn-outline-primary" 
                                      onclick="startAiReview(${control.std_control_id}, '${control.control_name.replace(/'/g, "\\'")}', '${mapping.control_code}', ${detailId})"
                                      id="ai_btn_${control.std_control_id}"
                                      style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">`;
                            html += `<i class="fas fa-brain me-1"></i>AI 검토`;
                            html += `</button>`;
                        }
                    } else {
                        html += `<span class="text-muted small">매핑 필요</span>`;
                    }
                    html += `</td>`;
                    
                    // 상태
                    html += `<td class="text-center">`;
                    if (isMapped) {
                        html += `<i class="fas fa-check-circle text-success" title="매핑됨"></i>`;
                    } else {
                        html += `<i class="fas fa-times-circle text-muted" title="미매핑"></i>`;
                    }
                    html += `</td>`;
                    
                    // 개선권고사항
                    html += `<td>`;
                    if (isMapped) {
                        if (aiResult && aiResult.status === 'completed' && aiResult.recommendation) {
                            html += `<span class="text-dark small" id="recommendation_${control.std_control_id}" style="color: #212529 !important;">`;
                            html += `<i class="fas fa-lightbulb me-1 text-warning"></i>${aiResult.recommendation}`;
                            html += `</span>`;
                        } else {
                            html += `<span class="text-muted small" id="recommendation_${control.std_control_id}">AI 검토 후 표시</span>`;
                        }
                    } else {
                        html += `<span class="text-muted small">-</span>`;
                    }
                    html += `</td>`;
                    
                    html += `</tr>`;
                });
                
                html += `</tbody>`;
                html += `</table>`;
                html += `</div>`;
                html += `</div>`;
            });
            
            container.innerHTML = html;
        }
        
        // 매핑 업데이트
        function updateMapping(stdControlId, rcmControlCode, stdControlName, detailId) {
            // 기준통제 ID를 숫자형으로 확실히 변환
            const numericStdControlId = parseInt(stdControlId);
            
            if (!rcmControlCode) {
                // 매핑 해제 - 서버에서도 삭제해야 함
                const existingMapping = existingMappings[numericStdControlId];
                if (existingMapping) {
                    const detailId = findDetailId(existingMapping.control_code);
                    if (detailId) {
                        // 서버에서 매핑 삭제
                        fetch(`/api/rcm/{{ rcm_info.rcm_id }}/detail/${detailId}/mapping`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            credentials: 'same-origin'
                        })
                        .then(response => response.json())
                        .then(result => {
                            if (result.success) {
                                // 클라이언트에서도 삭제
                                delete existingMappings[numericStdControlId];
                                
                                // UI 업데이트
                                const selectElement = document.getElementById(`select_${stdControlId}`);
                                const row = selectElement.closest('tr');
                                row.classList.remove('table-success');
                                
                                // AI 검토 버튼 제거
                                const aiCell = row.querySelector('td:nth-child(4)');
                                aiCell.innerHTML = '<span class="text-muted small">매핑 후 이용 가능</span>';
                                
                                // 개선권고사항 초기화
                                const recommendationCell = row.querySelector('td:nth-child(6)');
                                recommendationCell.innerHTML = '<span class="text-muted small">-</span>';
                                
                                // 상태 아이콘 업데이트
                                const statusCell = row.querySelector('td:nth-child(5)');
                                statusCell.innerHTML = '<i class="fas fa-circle text-muted" title="매핑 안됨"></i>';
                                
                                // AI 검토 결과도 삭제
                                delete aiReviewResults[numericStdControlId];
                                
                                // 저장 완료 알림 표시
                                showAutoSaveIndicator();
                            } else {
                                alert('매핑 해제에 실패했습니다: ' + result.message);
                            }
                        })
                        .catch(error => {
                            console.error('매핑 해제 오류:', error);
                            alert('매핑 해제 중 오류가 발생했습니다.');
                        });
                    }
                } else {
                    // 이미 해제된 상태이면 UI만 업데이트
                    delete existingMappings[numericStdControlId];
                }
                return;
            }
            
            if (!detailId || detailId === rcmControlCode) {
                alert(`매핑 오류: detail_id를 찾을 수 없거나 잘못된 값입니다. (${detailId})`);
                return;
            }
            
            // 새로운 매핑 저장
            const data = {
                control_code: rcmControlCode,
                std_control_id: numericStdControlId,  // 숫자형으로 전송
                confidence: 0.8,
                mapping_type: 'manual'
            };
            
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/detail/${detailId}/mapping`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    std_control_id: numericStdControlId
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // 매핑 정보 업데이트 (숫자형 ID로 저장)
                    existingMappings[numericStdControlId] = {
                        control_code: rcmControlCode,
                        rcm_control_name: rcmControlCode
                    };
                    
                    // UI 업데이트
                    const selectElement = document.getElementById(`select_${stdControlId}`);
                    const row = selectElement.closest('tr');
                    row.classList.add('table-success');
                    
                    // AI 검토 버튼 추가 (detail_id 계산)
                    const rcmControl = rcmControls.find(rc => rc.control_code === rcmControlCode);
                    const mappingDetailId = rcmControl ? rcmControl.detail_id : '';
                    
                    const aiCell = row.querySelector('td:nth-child(4)'); // AI 검토 컬럼
                    aiCell.innerHTML = `
                        <button class="btn btn-xs btn-outline-info me-1" 
                                onclick="showRcmDetail('${rcmControlCode}')"
                                title="RCM 통제 상세정보 보기"
                                style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-xs btn-outline-primary" 
                                onclick="startAiReview(${stdControlId}, '${stdControlName.replace(/'/g, "\\'")}', '${rcmControlCode}', ${mappingDetailId})"
                                id="ai_btn_${stdControlId}"
                                style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">
                            <i class="fas fa-brain me-1"></i>AI 검토
                        </button>
                    `;
                    
                    // 개선권고사항 컬럼 업데이트
                    const recommendationCell = row.querySelector('td:nth-child(6)'); // 개선권고사항 컬럼
                    recommendationCell.innerHTML = '<span class="text-muted small" id="recommendation_' + stdControlId + '">AI 검토 후 표시</span>';
                    
                    // 상태 아이콘 업데이트 (마지막에서 두 번째 컬럼)
                    const statusCell = row.querySelector('td:nth-child(5)');
                    statusCell.innerHTML = '<i class="fas fa-check-circle text-success" title="매핑됨"></i>';
                    
                    // 저장 완료 알림 표시
                    showAutoSaveIndicator();
                } else {
                    alert('매핑 저장에 실패했습니다: ' + result.message);
                }
            })
            .catch(error => {
                console.error('매핑 저장 오류:', error);
                alert('매핑 저장 중 오류가 발생했습니다.');
            });
        }
        
        // AI 검토 시작
        function startAiReview(stdControlId, stdControlName, rcmControlCode, detailId) {
            const button = document.getElementById(`ai_btn_${stdControlId}`);
            const originalText = button.innerHTML;
            
            // 로딩 상태로 변경
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>검토 중...';
            button.disabled = true;
            
            // 실제 AI 검토 API 호출 (모의 데이터 제거)
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/detail/${detailId}/ai-review`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 검토 완료 후 결과 표시
                    button.innerHTML = '<i class="fas fa-check me-1"></i>완료';
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-success');
                    button.disabled = false;
                    
                    // AI 검토 결과에서 개선권고사항 추출
                    const aiRecommendation = data.recommendation || '검토 완료';
                    
                    // 개선권고사항 업데이트
                    const recommendationElement = document.getElementById(`recommendation_${stdControlId}`);
                    if (recommendationElement) {
                        recommendationElement.innerHTML = `<i class="fas fa-lightbulb me-1 text-warning"></i>${aiRecommendation}`;
                        recommendationElement.className = "text-dark small";
                        recommendationElement.style.color = "#212529 !important";
                    }
                    
                    console.log(`AI 검토 완료: ${stdControlName} -> ${rcmControlCode}`);
                    
                    // AI 검토 결과 저장 (숫자형 ID로 저장)
                    const numericStdControlId = parseInt(stdControlId);
                    aiReviewResults[numericStdControlId] = {
                        status: 'completed',
                        recommendation: aiRecommendation,
                        reviewed_date: new Date().toISOString(),
                        std_control_name: stdControlName,
                        rcm_control_code: rcmControlCode
                    };
                    
                    // 저장 완료 알림 표시
                    showAutoSaveIndicator();
                } else {
                    // 오류 처리
                    button.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>오류';
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-danger');
                    button.disabled = false;
                    console.error('AI 검토 오류:', data.message);
                }
            })
            .catch(error => {
                console.error('AI 검토 API 호출 오류:', error);
                button.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>오류';
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-danger');
                button.disabled = false;
            });
        }
        
        // 자동 저장 스케줄링
        function scheduleAutoSave() {
            if (autoSaveTimeout) {
                clearTimeout(autoSaveTimeout);
            }
            
            autoSaveTimeout = setTimeout(() => {
                autoSaveReviewResult();
            }, 3000); // 3초 후 자동 저장
        }
        
        // 자동 저장 완료 표시 함수
        function showAutoSaveIndicator() {
            // 헤더의 자동 저장됨 버튼을 잠시 표시
            const autoSaveBtn = document.getElementById('autoSaveIndicator');
            if (autoSaveBtn) {
                autoSaveBtn.style.display = 'inline-block';
                
                // 3초 후 다시 숨김
                setTimeout(() => {
                    autoSaveBtn.style.display = 'none';
                }, 3000);
            }
            
            // 기존 알림도 유지 (우측 상단)
            const indicator = document.createElement('div');
            indicator.className = 'position-fixed top-0 end-0 m-3 alert alert-success alert-dismissible fade show';
            indicator.style.zIndex = '9999';
            indicator.innerHTML = `
                <i class="fas fa-check-circle me-1"></i>자동 저장됨
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(indicator);
            
            // 3초 후 자동 제거
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.remove();
                }
            }, 3000);
        }
        
        // 자동 저장 (임시 비활성화)
        function autoSaveReviewResult() {
            console.log('자동 저장 호출됨 (현재 비활성화)');
            console.log('기존 매핑:', existingMappings);
            console.log('AI 검토 결과:', aiReviewResults);
            
            // 자동저장 임시 비활성화 - 개별 통제 API로 변경 후 재활성화 예정
            /*
            const reviewData = {
                mapping_data: existingMappings,
                ai_review_data: aiReviewResults
            };
            
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/review/auto-save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify(reviewData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('자동 저장 완료');
                    showAutoSaveIndicator();
                }
            })
            .catch(error => {
                console.error('자동 저장 오류:', error);
            });
            */
        }
        
        // 검토 결과 수동 저장 (현재 비활성화)
        function saveReviewResult() {
            console.log('수동 저장 호출됨 (현재 비활성화)');
            alert('수동 저장은 개별 통제 API로 변경 예정입니다.');
            
            // 개별 통제 API로 변경 후 재구현 예정
            /*
            const reviewData = {
                mapping_data: existingMappings,
                ai_review_data: aiReviewResults,
                status: 'draft',
                notes: ''
            };
            
            // 로딩 표시
            const saveButton = document.querySelector('button[onclick="saveReviewResult()"]');
            const originalText = saveButton.innerHTML;
            saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>저장 중...';
            saveButton.disabled = true;
            
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/review`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify(reviewData)
            })
            .then(response => response.json())
            .then(data => {
                saveButton.innerHTML = originalText;
                saveButton.disabled = false;
                
                if (data.success) {
                    alert('검토 결과가 저장되었습니다.');
                } else {
                    alert('저장 실패: ' + data.message);
                }
            })
            .catch(error => {
                saveButton.innerHTML = originalText;
                saveButton.disabled = false;
                console.error('저장 오류:', error);
                alert('저장 중 오류가 발생했습니다.');
            });
            */
        }
        
        // 페이지 로드시 이전 결과 자동 불러오기
        function loadPreviousResultOnStart_DISABLED() {
            console.log('이전 검토 결과 로드 (현재 비활성화 - 함수명 변경)');
            
            // 개별 통제 API로 변경 후 재구현 예정
            /*
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/review`, {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.has_saved_review) {
                    const result = data.review_result;
                    console.log('이전 검토 결과 발견:', result);
                    
                    // 매핑 데이터 복원 (키를 숫자형으로 변환)
                    if (result.mapping_data) {
                        for (const [stdControlId, mappingInfo] of Object.entries(result.mapping_data)) {
                            const numericId = parseInt(stdControlId);
                            existingMappings[numericId] = mappingInfo;
                        }
                    }
                    
                    // AI 검토 결과 복원 (키를 숫자형으로 변환)
                    if (result.ai_review_data) {
                        for (const [stdControlId, aiInfo] of Object.entries(result.ai_review_data)) {
                            const numericId = parseInt(stdControlId);
                            aiReviewResults[numericId] = aiInfo;
                        }
                    }
                    
                    console.log('이전 결과가 복원되었습니다.');
                }
            })
            .catch(error => {
                console.error('이전 결과 불러오기 오류:', error);
            });
            */
        }
        
        // AI 전체 검토 기능
        function bulkAiReview() {
            // 매핑된 항목 중 AI 검토가 완료되지 않은 항목들 찾기
            const pendingReviews = [];
            
            // existingMappings에서 매핑된 항목들 확인
            for (const [stdControlId, mapping] of Object.entries(existingMappings)) {
                const numericStdControlId = parseInt(stdControlId);
                
                // 해당 항목이 AI 검토 완료되지 않았는지 확인
                if (!aiReviewResults[numericStdControlId] || aiReviewResults[numericStdControlId].status !== 'completed') {
                    // 매핑 정보에서 필요한 데이터 추출
                    const detailId = findDetailId(mapping.control_code);
                    if (detailId) {
                        pendingReviews.push({
                            stdControlId: numericStdControlId,
                            stdControlName: getStandardControlName(numericStdControlId),
                            rcmControlCode: mapping.control_code,
                            detailId: detailId
                        });
                    }
                }
            }
            
            if (pendingReviews.length === 0) {
                alert('모든 매핑된 항목의 AI 검토가 이미 완료되었습니다.');
                return;
            }
            
            const confirmMessage = `매핑된 ${pendingReviews.length}개 항목의 AI 검토를 시작하시겠습니까?`;
            if (!confirm(confirmMessage)) {
                return;
            }
            
            // 일괄 검토 버튼 상태 변경
            const bulkButton = document.querySelector('button[onclick="bulkAiReview()"]');
            const originalText = bulkButton.innerHTML;
            bulkButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>검토 중... (0/' + pendingReviews.length + ')';
            bulkButton.disabled = true;
            
            let completedCount = 0;
            let hasErrors = false;
            
            // 순차적으로 AI 검토 실행 (서버 부하 방지)
            async function processNextReview(index) {
                if (index >= pendingReviews.length) {
                    // 모든 검토 완료
                    bulkButton.innerHTML = originalText;
                    bulkButton.disabled = false;
                    
                    const message = hasErrors 
                        ? `일괄 검토 완료: ${completedCount}/${pendingReviews.length}개 성공 (일부 오류 발생)`
                        : `일괄 검토 완료: ${completedCount}/${pendingReviews.length}개 모두 성공`;
                    alert(message);
                    return;
                }
                
                const review = pendingReviews[index];
                
                try {
                    // 개별 AI 검토 실행
                    await performSingleAiReview(review);
                    completedCount++;
                } catch (error) {
                    console.error('AI 검토 오류:', error);
                    hasErrors = true;
                }
                
                // 진행상황 업데이트
                const progress = index + 1;
                bulkButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>검토 중... (' + progress + '/' + pendingReviews.length + ')';
                
                // 다음 항목 처리 (1초 지연)
                setTimeout(() => processNextReview(index + 1), 1000);
            }
            
            // 첫 번째 검토 시작
            processNextReview(0);
        }
        
        // 단일 AI 검토 실행 함수
        async function performSingleAiReview(reviewData) {
            return new Promise((resolve, reject) => {
                const { stdControlId, stdControlName, rcmControlCode, detailId } = reviewData;
                
                // 실제 AI 검토 API 호출
                fetch(`/api/rcm/{{ rcm_info.rcm_id }}/detail/${detailId}/ai-review`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // 해당 버튼 상태 업데이트
                        const button = document.getElementById(`ai_btn_${stdControlId}`);
                        if (button) {
                            button.innerHTML = '<i class="fas fa-check me-1"></i>완료';
                            button.classList.remove('btn-outline-primary');
                            button.classList.add('btn-success');
                            button.disabled = false;
                        }
                        
                        // AI 검토 결과에서 개선권고사항 추출
                        const aiRecommendation = data.recommendation || '검토 완료';
                        
                        // 개선권고사항 업데이트
                        const recommendationElement = document.getElementById(`recommendation_${stdControlId}`);
                        if (recommendationElement) {
                            recommendationElement.innerHTML = `<i class="fas fa-lightbulb me-1 text-warning"></i>${aiRecommendation}`;
                            recommendationElement.className = "text-dark small";
                            recommendationElement.style.color = "#212529 !important";
                        }
                        
                        // AI 검토 결과 저장
                        aiReviewResults[stdControlId] = {
                            status: 'completed',
                            recommendation: aiRecommendation,
                            reviewed_date: new Date().toISOString(),
                            std_control_name: stdControlName,
                            rcm_control_code: rcmControlCode
                        };
                        
                        resolve(data);
                    } else {
                        reject(new Error(data.message));
                    }
                })
                .catch(error => {
                    reject(error);
                });
            });
        }
        
        // 기준통제 이름 조회 함수
        function getStandardControlName(stdControlId) {
            // standardControls 배열에서 해당 ID의 이름 찾기
            const control = standardControls.find(ctrl => ctrl.std_control_id === stdControlId);
            return control ? control.control_name : `기준통제 ${stdControlId}`;
        }

        // RCM 통제 상세정보 모달 표시
        function showRcmDetail(controlCode) {
            try {
                // rcmControls에서 해당 통제 찾기
                const rcmControl = rcmControls.find(rc => rc.control_code === controlCode);
                if (!rcmControl) {
                    alert('통제 정보를 찾을 수 없습니다.');
                    return;
                }

                // 모달 제목 설정
                document.getElementById('rcmDetailModalLabel').textContent = `${controlCode} - ${rcmControl.control_name}`;

                // 모달 내용 설정
                const content = `
                    <table class="table table-borderless">
                        <tr>
                            <th width="20%" class="text-muted">통제 코드:</th>
                            <td><strong>${controlCode}</strong></td>
                        </tr>
                        <tr>
                            <th class="text-muted">통제명:</th>
                            <td>${rcmControl.control_name}</td>
                        </tr>
                        <tr>
                            <th class="text-muted">통제 설명:</th>
                            <td>${rcmControl.control_description || '<span class="text-muted">설명 없음</span>'}</td>
                        </tr>
                        <tr>
                            <th class="text-muted">통제 유형:</th>
                            <td>${rcmControl.control_type || '<span class="text-muted">미분류</span>'}</td>
                        </tr>
                        <tr>
                            <th class="text-muted">담당자:</th>
                            <td>${rcmControl.responsible_party || '<span class="text-muted">미지정</span>'}</td>
                        </tr>
                    </table>
                `;

                document.getElementById('rcmDetailContent').innerHTML = content;

                // 모달 표시
                const modal = new bootstrap.Modal(document.getElementById('rcmDetailModal'));
                modal.show();

            } catch (error) {
                console.error('모달 표시 오류:', error);
                alert('통제 정보를 표시하는 중 오류가 발생했습니다.');
            }
        }
        
        
        // 이전 결과 수동 불러오기 (현재 비활성화)
        function loadPreviousResult() {
            console.log('수동 불러오기 호출됨 (현재 비활성화)');
            alert('수동 불러오기는 개별 통제 API로 변경 예정입니다.');
            
            // 개별 통제 API로 변경 후 재구현 예정
            /*
            if (confirm('현재 작업 중인 내용을 덮어쓰고 이전에 저장된 결과를 불러오시겠습니까?')) {
                fetch(`/api/rcm/{{ rcm_info.rcm_id }}/review`, {
                    method: 'GET',
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.has_saved_review) {
                        const result = data.review_result;
                        
                        // 매핑 데이터 복원 (키를 숫자형으로 변환)
                        existingMappings = {};
                        if (result.mapping_data) {
                            for (const [stdControlId, mappingInfo] of Object.entries(result.mapping_data)) {
                                const numericId = parseInt(stdControlId);
                                existingMappings[numericId] = mappingInfo;
                            }
                        }
                        
                        // AI 검토 결과 복원 (키를 숫자형으로 변환)
                        aiReviewResults = {};
                        if (result.ai_review_data) {
                            for (const [stdControlId, aiInfo] of Object.entries(result.ai_review_data)) {
                                const numericId = parseInt(stdControlId);
                                aiReviewResults[numericId] = aiInfo;
                            }
                        }
                        
                        // UI 새로고침
                        renderStandardControlsList();
                        
                        let lastModifiedInfo = `저장일: ${new Date(result.last_modified_date).toLocaleDateString()}`;
                        if (result.user_name) {
                            lastModifiedInfo += ` (수정자: ${result.user_name})`;
                        }
                        
                        alert(`저장된 결과를 불러왔습니다. (${lastModifiedInfo})`);
                    } else {
                        alert('저장된 검토 결과가 없습니다.');
                    }
                })
                .catch(error => {
                    console.error('결과 불러오기 오류:', error);
                    alert('결과 불러오기 중 오류가 발생했습니다.');
                });
            }
            */
        }
    </script>
</body>
</html>