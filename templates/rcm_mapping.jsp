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
            <!-- 기준통제 목록 (왼쪽) -->
            <div class="col-md-5">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="mb-1"><i class="fas fa-bookmark me-2"></i>기준통제 목록</h5>
                        <small class="text-muted">매핑할 기준통제를 클릭하세요</small>
                    </div>
                    <div class="card-body" style="max-height: 70vh; overflow-y: auto; padding: 1rem;">
                        <div id="selectedStandardControl" class="alert alert-info" style="display: none;">
                            <strong>선택된 기준통제:</strong> <span id="selectedStdControlName"></span>
                            <button class="btn btn-sm btn-outline-secondary float-end" onclick="clearStdSelection()">
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
                                {% set std_mappings = existing_mappings|selectattr('std_control_id', 'equalto', control.std_control_id)|list %}
                                <div class="standard-control-item {{ 'mapped' if std_mappings else '' }}" 
                                     data-std-control-id="{{ control.std_control_id }}"
                                     data-control-name="{{ control.control_name }}"
                                     onclick="selectStandardControl({{ control.std_control_id }}, '{{ control.control_name }}', '{{ control.control_code }}')">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <strong>{{ control.control_code }}</strong>
                                            <br>
                                            <span class="small">{{ control.control_name }}</span>
                                            {% if std_mappings %}
                                            <br>
                                            <small class="text-success">
                                                <i class="fas fa-link me-1"></i>
                                                {% for mapping in std_mappings %}
                                                {{ mapping.control_code }}{% if not loop.last %}, {% endif %}
                                                {% endfor %}
                                                에 매핑됨
                                            </small>
                                            {% endif %}
                                        </div>
                                        <div class="text-end">
                                            <span class="badge {{ 'bg-success' if std_mappings else 'bg-info' }}">
                                                {{ control.control_category }}
                                            </span>
                                            {% if std_mappings %}
                                            <br>
                                            <button class="btn btn-sm btn-outline-danger mt-1" onclick="event.stopPropagation(); removeStandardControlMappings({{ control.std_control_id }}, '{{ control.control_code }}')">
                                                <i class="fas fa-times"></i> 해제
                                            </button>
                                            {% endif %}
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
                                {% set std_mappings = existing_mappings|selectattr('std_control_id', 'equalto', control.std_control_id)|list %}
                                <div class="standard-control-item {{ 'mapped' if std_mappings else '' }}" 
                                     data-std-control-id="{{ control.std_control_id }}"
                                     data-control-name="{{ control.control_name }}"
                                     onclick="selectStandardControl({{ control.std_control_id }}, '{{ control.control_name }}', '{{ control.control_code }}')">
                                    <div class="d-flex justify-content-between">
                                        <div>
                                            <strong>{{ control.control_code }}</strong>
                                            <br>
                                            <span class="small">{{ control.control_name }}</span>
                                            {% if std_mappings %}
                                            <br>
                                            <small class="text-success">
                                                <i class="fas fa-link me-1"></i>
                                                {% for mapping in std_mappings %}
                                                {{ mapping.control_code }}{% if not loop.last %}, {% endif %}
                                                {% endfor %}
                                                에 매핑됨
                                            </small>
                                            {% endif %}
                                        </div>
                                        <div class="text-end">
                                            <span class="badge {{ 'bg-success' if std_mappings else 'bg-info' }}">
                                                {{ control.control_category }}
                                            </span>
                                            {% if std_mappings %}
                                            <br>
                                            <button class="btn btn-sm btn-outline-danger mt-1" onclick="event.stopPropagation(); removeStandardControlMappings({{ control.std_control_id }}, '{{ control.control_code }}')">
                                                <i class="fas fa-times"></i> 해제
                                            </button>
                                            {% endif %}
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

            <!-- RCM 통제 목록 (오른쪽) -->
            <div class="col-md-7">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="mb-1"><i class="fas fa-list me-2"></i>RCM 통제 목록</h5>
                        <small class="text-muted">기준통제를 선택한 후 적절한 RCM 통제를 클릭하여 매핑하세요</small>
                    </div>
                    <div class="card-body" style="max-height: 70vh; overflow-y: auto; padding: 1rem;">
                        {% for detail in rcm_details %}
                        {% set matching_mappings = existing_mappings|selectattr('control_code', 'equalto', detail.control_code)|list %}
                        <div class="mapping-card p-3 {{ 'mapped' if matching_mappings else 'unmapped' }}" 
                             data-control-code="{{ detail.control_code }}"
                             onclick="mapRcmToStandardControl('{{ detail.control_code }}', '{{ detail.control_name }}')">
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
                                                <small class="text-danger">기준통제와 매핑 필요</small>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let selectedStdControlId = null;
        let selectedStdControlName = null;
        let selectedStdControlCode = null;
        
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
        
        // 기준통제 선택
        function selectStandardControl(stdControlId, stdControlName, stdControlCode) {
            selectedStdControlId = stdControlId;
            selectedStdControlName = stdControlName;
            selectedStdControlCode = stdControlCode;
            
            // UI 업데이트
            document.getElementById('selectedStandardControl').style.display = 'block';
            document.getElementById('selectedStdControlName').textContent = stdControlName + ' (' + stdControlCode + ')';
            
            // 기존 선택 해제
            document.querySelectorAll('.standard-control-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            // 현재 항목 선택 표시
            event.target.closest('.standard-control-item').classList.add('selected');
        }
        
        // 기준통제 선택 해제
        function clearStdSelection() {
            selectedStdControlId = null;
            selectedStdControlName = null;
            selectedStdControlCode = null;
            document.getElementById('selectedStandardControl').style.display = 'none';
            
            document.querySelectorAll('.standard-control-item').forEach(item => {
                item.classList.remove('selected');
            });
        }
        
        // RCM 통제를 기준통제에 매핑 (자동 저장)
        function mapRcmToStandardControl(rcmControlCode, rcmControlName) {
            if (!selectedStdControlId) {
                alert('먼저 기준통제를 선택해주세요.');
                return;
            }
            
            // 즉시 서버에 저장
            fetch(`/api/rcm/{{ rcm_info.rcm_id }}/mapping`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    control_code: rcmControlCode,
                    std_control_id: selectedStdControlId,
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
                    // RCM 통제 UI 업데이트
                    updateRcmControlUI(rcmControlCode, true, selectedStdControlName);
                    
                    // 기준통제 UI 업데이트 - 이미 매핑된 RCM 통제들을 포함하여 업데이트
                    const currentMappedControls = [rcmControlCode];
                    // 같은 기준통제에 이미 매핑된 다른 RCM 통제들이 있는지 확인하고 추가
                    document.querySelectorAll('.mapping-card.mapped').forEach(card => {
                        const controlCode = card.getAttribute('data-control-code');
                        if (controlCode !== rcmControlCode) {
                            const statusText = card.querySelector('.text-success');
                            if (statusText && statusText.textContent.includes(selectedStdControlName)) {
                                currentMappedControls.push(controlCode);
                            }
                        }
                    });
                    updateStandardControlUI(selectedStdControlId, true, currentMappedControls);
                    
                    // 성공 알림
                    showSuccessToast(`${rcmControlCode} ← ${selectedStdControlCode} 매핑이 저장되었습니다.`);
                    
                    // 진행률 업데이트
                    updateProgress();
                    
                    // 선택 해제 (성공 후)
                    clearStdSelection();
                    
                    console.log('매핑 자동 저장 완료:', rcmControlCode, '->', selectedStdControlName);
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
        
        // 기준통제의 모든 매핑 해제
        function removeStandardControlMappings(stdControlId, stdControlCode) {
            if (!confirm(`${stdControlCode} 기준통제의 모든 매핑을 해제하시겠습니까?`)) {
                return;
            }
            
            // 해당 기준통제와 연결된 모든 RCM 통제 찾기
            const mappedRcmControls = [];
            document.querySelectorAll('[data-control-code]').forEach(card => {
                if (card.classList.contains('mapped')) {
                    const controlCode = card.getAttribute('data-control-code');
                    mappedRcmControls.push(controlCode);
                }
            });
            
            // 각각에 대해 삭제 요청
            const deletePromises = [];
            mappedRcmControls.forEach(controlCode => {
                deletePromises.push(
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
                );
            });
            
            Promise.all(deletePromises)
                .then(responses => {
                    return Promise.all(responses.map(r => r.json()));
                })
                .then(results => {
                    let successCount = 0;
                    results.forEach((result, index) => {
                        if (result.success) {
                            successCount++;
                            const controlCode = mappedRcmControls[index];
                            updateRcmControlUI(controlCode, false);
                        }
                    });
                    
                    if (successCount > 0) {
                        showSuccessToast(`${stdControlCode} 기준통제의 ${successCount}개 매핑이 해제되었습니다.`);
                        updateStandardControlUI(stdControlId, false);
                        updateProgress();
                    }
                })
                .catch(error => {
                    console.error('매핑 해제 오류:', error);
                    alert('매핑 해제 중 오류가 발생했습니다: ' + error.message);
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
                    statusText.innerHTML = '<i class="fas fa-times me-1"></i>기준통제와 매핑 필요';
                    statusText.className = 'text-danger';
                    
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
        
        // RCM 통제 UI 업데이트
        function updateRcmControlUI(controlCode, isMapped, stdControlName = '') {
            const card = document.querySelector(`[data-control-code="${controlCode}"]`);
            if (!card) {
                console.error(`카드를 찾을 수 없습니다: ${controlCode}`);
                return;
            }
            
            if (isMapped) {
                card.classList.remove('unmapped');
                card.classList.add('mapped');
                
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
            } else {
                card.classList.remove('mapped');
                card.classList.add('unmapped');
                
                // 배지 업데이트
                const badge = card.querySelector('.badge');
                if (badge) {
                    badge.textContent = '미매핑';
                    badge.className = 'badge bg-danger mb-1';
                }
                
                const statusText = card.querySelector('small');
                if (statusText) {
                    statusText.innerHTML = '<i class="fas fa-times me-1"></i>기준통제와 매핑 필요';
                    statusText.className = 'text-danger';
                }
            }
        }

        // 기준통제 UI 업데이트
        function updateStandardControlUI(stdControlId, isMapped, rcmControlCodes = []) {
            const stdItem = document.querySelector(`[data-std-control-id="${stdControlId}"]`);
            if (!stdItem) {
                console.error(`기준통제를 찾을 수 없습니다: ${stdControlId}`);
                return;
            }
            
            if (isMapped) {
                stdItem.classList.add('mapped');
                
                // 배지 색상 변경
                const badge = stdItem.querySelector('.badge');
                if (badge) {
                    badge.className = badge.className.replace('bg-info', 'bg-success');
                }
                
                // 매핑 정보와 해제 버튼 추가
                const controlNameDiv = stdItem.querySelector('div > div');
                let mappingInfo = controlNameDiv.querySelector('.text-success');
                if (!mappingInfo) {
                    mappingInfo = document.createElement('small');
                    mappingInfo.className = 'text-success';
                    controlNameDiv.appendChild(document.createElement('br'));
                    controlNameDiv.appendChild(mappingInfo);
                }
                mappingInfo.innerHTML = `<i class="fas fa-link me-1"></i>${rcmControlCodes.join(', ')}에 매핑됨`;
                
                // 해제 버튼 추가
                const buttonDiv = stdItem.querySelector('div > div.text-end');
                let removeButton = buttonDiv.querySelector('.btn-outline-danger');
                if (!removeButton) {
                    removeButton = document.createElement('button');
                    removeButton.className = 'btn btn-sm btn-outline-danger mt-1';
                    removeButton.onclick = (e) => {
                        e.stopPropagation();
                        const stdControlCode = stdItem.textContent.split('\n')[0].trim();
                        removeStandardControlMappings(stdControlId, stdControlCode);
                    };
                    removeButton.innerHTML = '<i class="fas fa-times"></i> 해제';
                    buttonDiv.appendChild(document.createElement('br'));
                    buttonDiv.appendChild(removeButton);
                }
            } else {
                stdItem.classList.remove('mapped');
                
                // 배지 색상 원복
                const badge = stdItem.querySelector('.badge');
                if (badge) {
                    badge.className = badge.className.replace('bg-success', 'bg-info');
                }
                
                // 매핑 정보와 해제 버튼 제거
                const mappingInfo = stdItem.querySelector('.text-success');
                if (mappingInfo) {
                    mappingInfo.remove();
                }
                const removeButton = stdItem.querySelector('.btn-outline-danger');
                if (removeButton) {
                    removeButton.remove();
                }
                
                // br 태그들도 정리
                const brs = stdItem.querySelectorAll('br');
                brs.forEach(br => {
                    if (br.nextSibling && br.nextSibling.classList && br.nextSibling.classList.contains('text-success')) {
                        br.remove();
                    }
                });
            }
        }

        // 매핑 UI 업데이트 (기존 함수명 유지 - 호환성)
        function updateMappingUI(controlCode, stdControlName) {
            updateRcmControlUI(controlCode, true, stdControlName);
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