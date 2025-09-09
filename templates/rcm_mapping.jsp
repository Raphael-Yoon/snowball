<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>기준통제 매핑 - {{ rcm_info.rcm_name }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .mapping-card {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 1rem;
            transition: border-color 0.3s;
        }
        .mapping-card.mapped {
            border-color: #28a745;
            background-color: #f8fff9;
        }
        .mapping-card.unmapped {
            border-color: #dc3545;
            background-color: #fff5f5;
        }
        .standard-control-list {
            /* 스크롤 제거로 모든 기준통제를 한번에 볼 수 있도록 개선 */
        }
        .standard-control-item {
            cursor: pointer;
            padding: 10px;
            border: 1px solid #e9ecef;
            margin-bottom: 5px;
            border-radius: 4px;
            transition: all 0.3s;
        }
        .standard-control-item:hover {
            background-color: #f8f9fa;
            border-color: #007bff;
        }
        .standard-control-item.selected {
            background-color: #e3f2fd;
            border-color: #2196f3;
            font-weight: bold;
        }
        .progress-bar-custom {
            height: 8px;
        }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-link me-2"></i>기준통제 매핑</h1>
                    <div>
                        <a href="/rcm/{{ rcm_info.rcm_id }}/view" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-1"></i>상세보기로
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- RCM 기본 정보 및 진행상황 -->
        <div class="row mb-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <h5>{{ rcm_info.rcm_name }}</h5>
                        <p class="text-muted mb-0">{{ rcm_info.company_name }} | 총 {{ rcm_details|length }}개 통제</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body text-center">
                        <h6>매핑 진행률</h6>
                        <div class="h4 mb-2">
                            <span id="mappingProgress">{{ existing_mappings|length }}/{{ rcm_details|length }}</span>
                        </div>
                        <div class="progress progress-bar-custom">
                            <div class="progress-bar bg-info" id="progressBar" 
                                 style="width: {{ (existing_mappings|length / rcm_details|length * 100) if rcm_details|length > 0 else 0 }}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- RCM 통제 목록 (왼쪽) -->
            <div class="col-md-7">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="mb-1"><i class="fas fa-list me-2"></i>RCM 통제 목록</h5>
                        <small class="text-muted">매핑할 RCM 통제를 선택하세요</small>
                    </div>
                    <div class="card-body" style="max-height: 70vh; overflow-y: auto; padding: 1rem;">
                        {% for detail in rcm_details %}
                        {% set matching_mappings = existing_mappings|selectattr('control_code', 'equalto', detail.control_code)|list %}
                        <div class="mapping-card p-3 {{ 'mapped' if matching_mappings else 'unmapped' }}" 
                             data-control-code="{{ detail.control_code }}">
                            <div class="row">
                                <div class="col-md-12">
                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                        <div>
                                            <h6 class="mb-1">
                                                <code class="me-2">{{ detail.control_code }}</code>
                                                <strong>{{ detail.control_name }}</strong>
                                            </h6>
                                            <p class="text-muted small mb-2">{{ detail.control_description[:100] }}{% if detail.control_description|length > 100 %}...{% endif %}</p>
                                        </div>
                                        <div class="text-end">
                                            {% set current_mapping = matching_mappings[0] if matching_mappings else none %}
                                            
                                            {% if current_mapping %}
                                                <span class="badge bg-success mb-1">매핑됨</span>
                                                <br>
                                                <small class="text-success">
                                                    <i class="fas fa-link me-1"></i>{{ current_mapping.std_control_name }}
                                                </small>
                                            {% else %}
                                                <span class="badge bg-danger mb-1">미매핑</span>
                                                <br>
                                                <small class="text-danger">기준통제 선택 필요</small>
                                            {% endif %}
                                        </div>
                                    </div>
                                    
                                    <!-- 매핑된 기준통제 정보 표시 -->
                                    <div class="mapped-info" id="mapped-{{ detail.control_code }}" style="display: {% if current_mapping %}block{% else %}none{% endif %};">
                                        {% if current_mapping %}
                                        <div class="alert alert-success py-2">
                                            <strong>매핑된 기준통제:</strong> {{ current_mapping.std_control_name }}
                                            <button class="btn btn-sm btn-outline-danger float-end" onclick="removeMapping('{{ detail.control_code }}')">
                                                <i class="fas fa-times"></i> 해제
                                            </button>
                                        </div>
                                        {% endif %}
                                    </div>
                                    
                                    <button class="btn btn-sm btn-primary w-100 select-btn" id="select-{{ detail.control_code }}" onclick="selectRcmControl('{{ detail.control_code }}', '{{ detail.control_name }}')" style="display: {% if current_mapping %}none{% else %}block{% endif %};">
                                        <i class="fas fa-hand-pointer me-1"></i>기준통제 선택
                                    </button>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- 기준통제 목록 (오른쪽) -->
            <div class="col-md-5">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="mb-1"><i class="fas fa-bookmark me-2"></i>기준통제 목록</h5>
                        <small class="text-muted">RCM 통제를 선택한 후 적절한 기준통제를 클릭하세요</small>
                    </div>
                    <div class="card-body" style="max-height: 70vh; overflow-y: auto; padding: 1rem;">
                        <div id="selectedRcmControl" class="alert alert-info" style="display: none;">
                            <strong>선택된 RCM 통제:</strong> <span id="selectedControlName"></span>
                            <button class="btn btn-sm btn-outline-secondary float-end" onclick="clearSelection()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <!-- 카테고리별 기준통제 -->
                        {% set categories = standard_controls|groupby('control_category') %}
                        {% set category_order = ['APD', 'PC', 'CO', 'PD'] %}
                        {% for category_name in category_order %}
                            {% for category, controls in categories %}
                                {% if category == category_name %}
                        <div class="mb-3">
                            <h6 class="text-primary border-bottom pb-2">
                                <i class="fas fa-folder-open me-2"></i>{{ category }}
                            </h6>
                            <div class="standard-control-list">
                                {% for control in controls %}
                                <div class="standard-control-item" 
                                     data-std-control-id="{{ control.std_control_id }}"
                                     data-control-name="{{ control.control_name }}"
                                     onclick="mapToStandardControl({{ control.std_control_id }}, '{{ control.control_name }}')">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <strong>{{ control.control_code }}</strong>
                                            <br>
                                            <span class="small">{{ control.control_name }}</span>
                                        </div>
                                        <div class="text-end">
                                            <span class="badge bg-info">
                                                {{ control.control_category }}
                                            </span>
                                        </div>
                                    </div>
                                    {% if control.control_description %}
                                    <p class="small text-muted mb-0 mt-1">{{ control.control_description[:80] }}{% if control.control_description|length > 80 %}...{% endif %}</p>
                                    {% endif %}
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                                {% endif %}
                            {% endfor %}
                        {% endfor %}
                        
                        <!-- 정의되지 않은 카테고리들 표시 -->
                        {% for category, controls in categories %}
                            {% if category not in category_order %}
                        <div class="mb-3">
                            <h6 class="text-primary border-bottom pb-2">
                                <i class="fas fa-folder-open me-2"></i>{{ category }}
                            </h6>
                            <div class="standard-control-list">
                                {% for control in controls %}
                                <div class="standard-control-item" 
                                     data-std-control-id="{{ control.std_control_id }}"
                                     data-control-name="{{ control.control_name }}"
                                     onclick="mapToStandardControl({{ control.std_control_id }}, '{{ control.control_name }}')">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <strong>{{ control.control_code }}</strong>
                                            <br>
                                            <span class="small">{{ control.control_name }}</span>
                                        </div>
                                        <div class="text-end">
                                            <span class="badge bg-info">
                                                {{ control.control_category }}
                                            </span>
                                        </div>
                                    </div>
                                    {% if control.control_description %}
                                    <p class="small text-muted mb-0 mt-1">{{ control.control_description[:80] }}{% if control.control_description|length > 80 %}...{% endif %}</p>
                                    {% endif %}
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let selectedRcmControlCode = null;
        
        // 성공 토스트 알림 함수
        function showSuccessToast(message) {
            // 기존 토스트가 있다면 제거
            const existingToast = document.getElementById('successToast');
            if (existingToast) {
                existingToast.remove();
            }
            
            // 새 토스트 생성
            const toast = document.createElement('div');
            toast.id = 'successToast';
            toast.className = 'position-fixed top-0 end-0 p-3';
            toast.style.zIndex = '9999';
            toast.innerHTML = `
                <div class="toast show" role="alert">
                    <div class="toast-header">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        <strong class="me-auto">저장 완료</strong>
                        <button type="button" class="btn-close" onclick="this.closest('#successToast').remove()"></button>
                    </div>
                    <div class="toast-body">
                        ${message}
                    </div>
                </div>
            `;
            
            document.body.appendChild(toast);
            
            // 3초 후 자동 제거
            setTimeout(() => {
                if (document.getElementById('successToast')) {
                    document.getElementById('successToast').remove();
                }
            }, 3000);
        }
        
        // RCM 통제 선택
        function selectRcmControl(controlCode, controlName) {
            selectedRcmControlCode = controlCode;
            
            // UI 업데이트
            document.getElementById('selectedRcmControl').style.display = 'block';
            document.getElementById('selectedControlName').textContent = controlName + ' (' + controlCode + ')';
            
            // 기존 선택 해제
            document.querySelectorAll('.standard-control-item').forEach(item => {
                item.classList.remove('selected');
            });
        }
        
        // 선택 해제
        function clearSelection() {
            selectedRcmControlCode = null;
            document.getElementById('selectedRcmControl').style.display = 'none';
            
            document.querySelectorAll('.standard-control-item').forEach(item => {
                item.classList.remove('selected');
            });
        }
        
        // 기준통제에 매핑 (자동 저장)
        function mapToStandardControl(stdControlId, stdControlName) {
            if (!selectedRcmControlCode) {
                alert('먼저 RCM 통제를 선택해주세요.');
                return;
            }
            
            // 현재 선택된 통제코드를 저장 (clearSelection 전에)
            const currentControlCode = selectedRcmControlCode;
            
            // 즉시 서버에 저장
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/mapping`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    control_code: currentControlCode,
                    std_control_id: stdControlId,
                    confidence: 0.8,
                    mapping_type: 'manual'
                })
            })
            .then(response => {
                console.log('서버 응답 상태:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(result => {
                console.log('서버 응답:', result);
                if (result.success) {
                    // UI 업데이트
                    updateMappingUI(currentControlCode, stdControlName);
                    
                    // 성공 알림 (간단한 토스트 형태)
                    showSuccessToast(`${currentControlCode} 매핑이 저장되었습니다.`);
                    
                    // 선택 해제 (성공 후)
                    clearSelection();
                    
                    console.log('매핑 자동 저장 완료:', currentControlCode, '->', stdControlName);
                } else {
                    console.error('저장 실패 응답:', result);
                    alert('매핑 저장 실패: ' + (result.message || '알 수 없는 오류'));
                }
            })
            .catch(error => {
                console.error('매핑 저장 오류 상세:', error);
                alert('매핑 저장 중 오류가 발생했습니다: ' + error.message);
            });
        }
        
        // 매핑 해제 (자동 삭제)
        function removeMapping(controlCode) {
            // 즉시 서버에서 삭제
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/mapping`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    control_code: controlCode
                })
            })
            .then(response => {
                console.log('삭제 응답 상태:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(result => {
                console.log('삭제 응답:', result);
                if (result.success) {
                    // UI 업데이트
                    const card = document.querySelector(`[data-control-code="${controlCode}"]`);
                    card.classList.remove('mapped');
                    card.classList.add('unmapped');
                    
                    const mappedInfo = document.getElementById(`mapped-${controlCode}`);
                    mappedInfo.style.display = 'none';
                    mappedInfo.innerHTML = '';
                    
                    // 배지 업데이트
                    const badge = card.querySelector('.badge');
                    badge.textContent = '미매핑';
                    badge.className = 'badge bg-danger mb-1';
                    
                    const statusText = card.querySelector('small');
                    statusText.innerHTML = '<i class="fas fa-times me-1"></i>기준통제 선택 필요';
                    statusText.className = 'text-danger';
                    
                    // '기준통제 선택' 버튼 다시 보이기
                    const selectButton = document.getElementById(`select-${controlCode}`);
                    if (selectButton) {
                        selectButton.style.display = 'block';
                    }
                    
                    updateProgress();
                    
                    // 성공 알림
                    showSuccessToast(`${controlCode} 매핑이 해제되었습니다.`);
                    
                    console.log('매핑 자동 삭제 완료:', controlCode);
                } else {
                    console.error('삭제 실패 응답:', result);
                    alert('매핑 삭제 실패: ' + (result.message || '알 수 없는 오류'));
                }
            })
            .catch(error => {
                console.error('매핑 삭제 오류 상세:', error);
                alert('매핑 삭제 중 오류가 발생했습니다: ' + error.message);
            });
        }
        
        // 매핑 UI 업데이트
        function updateMappingUI(controlCode, stdControlName) {
            const card = document.querySelector(`[data-control-code="${controlCode}"]`);
            if (!card) {
                console.error(`카드를 찾을 수 없습니다: ${controlCode}`);
                return;
            }
            card.classList.remove('unmapped');
            card.classList.add('mapped');
            
            const mappedInfo = document.getElementById(`mapped-${controlCode}`);
            if (mappedInfo) {
                mappedInfo.innerHTML = `
                    <div class="alert alert-success py-2">
                        <strong>매핑된 기준통제:</strong> ${stdControlName}
                        <button class="btn btn-sm btn-outline-danger float-end" onclick="removeMapping('${controlCode}')">
                            <i class="fas fa-times"></i> 해제
                        </button>
                    </div>
                `;
                mappedInfo.style.display = 'block';
            }
            
            // 배지 업데이트
            const badge = card.querySelector('.badge');
            if (badge) {
                badge.textContent = '매핑됨';
                badge.className = 'badge bg-success mb-1';
            }
            
            const statusText = card.querySelector('small');
            if (statusText) {
                statusText.innerHTML = `<i class="fas fa-link me-1"></i>${stdControlName}`;
                statusText.className = 'text-success';
            }
            
            // '기준통제 선택' 버튼 숨기기
            const selectButton = document.getElementById(`select-${controlCode}`);
            if (selectButton) {
                selectButton.style.display = 'none';
            }
            
            updateProgress();
        }
        
        // 진행률 업데이트
        function updateProgress() {
            const mappedCount = document.querySelectorAll('.mapping-card.mapped').length;
            const totalCount = {{ rcm_details|length }};
            const percentage = totalCount > 0 ? (mappedCount / totalCount * 100) : 0;
            
            document.getElementById('mappingProgress').textContent = `${mappedCount}/${totalCount}`;
            document.getElementById('progressBar').style.width = `${percentage}%`;
        }
    </script>
</body>
</html>