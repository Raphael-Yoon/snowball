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
            max-height: 300px;
            overflow-y: auto;
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
                        <button class="btn btn-success me-2" onclick="saveAllMappings()">
                            <i class="fas fa-save me-1"></i>매핑 저장
                        </button>
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
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>RCM 통제 목록</h5>
                    </div>
                    <div class="card-body" style="max-height: 70vh; overflow-y: auto;">
                        {% for detail in rcm_details %}
                        <div class="mapping-card p-3 {% set mapped = false %}{% for mapping in existing_mappings %}{% if mapping.control_code == detail.control_code %}mapped{% set mapped = true %}{% endif %}{% endfor %}{% if not mapped %}unmapped{% endif %}" 
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
                                            {% set current_mapping = none %}
                                            {% for mapping in existing_mappings %}
                                                {% if mapping.control_code == detail.control_code %}
                                                    {% set current_mapping = mapping %}
                                                {% endif %}
                                            {% endfor %}
                                            
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
                                    
                                    <button class="btn btn-sm btn-primary w-100" onclick="selectRcmControl('{{ detail.control_code }}', '{{ detail.control_name }}')">
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
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-bookmark me-2"></i>기준통제 목록</h5>
                        <small class="text-muted">RCM 통제를 선택한 후 적절한 기준통제를 클릭하세요</small>
                    </div>
                    <div class="card-body">
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
        let mappingChanges = {}; // 변경사항 추적
        
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
        
        // 기준통제에 매핑
        function mapToStandardControl(stdControlId, stdControlName) {
            if (!selectedRcmControlCode) {
                alert('먼저 RCM 통제를 선택해주세요.');
                return;
            }
            
            // 매핑 정보 저장
            mappingChanges[selectedRcmControlCode] = {
                std_control_id: stdControlId,
                std_control_name: stdControlName,
                action: 'add'
            };
            
            // UI 업데이트
            updateMappingUI(selectedRcmControlCode, stdControlName);
            
            // 선택 해제
            clearSelection();
            
            console.log('매핑 생성:', selectedRcmControlCode, '->', stdControlName);
        }
        
        // 매핑 해제
        function removeMapping(controlCode) {
            mappingChanges[controlCode] = {
                action: 'remove'
            };
            
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
            
            updateProgress();
            console.log('매핑 해제:', controlCode);
        }
        
        // 매핑 UI 업데이트
        function updateMappingUI(controlCode, stdControlName) {
            const card = document.querySelector(`[data-control-code="${controlCode}"]`);
            card.classList.remove('unmapped');
            card.classList.add('mapped');
            
            const mappedInfo = document.getElementById(`mapped-${controlCode}`);
            mappedInfo.innerHTML = `
                <div class="alert alert-success py-2">
                    <strong>매핑된 기준통제:</strong> ${stdControlName}
                    <button class="btn btn-sm btn-outline-danger float-end" onclick="removeMapping('${controlCode}')">
                        <i class="fas fa-times"></i> 해제
                    </button>
                </div>
            `;
            mappedInfo.style.display = 'block';
            
            // 배지 업데이트
            const badge = card.querySelector('.badge');
            badge.textContent = '매핑됨';
            badge.className = 'badge bg-success mb-1';
            
            const statusText = card.querySelector('small');
            statusText.innerHTML = `<i class="fas fa-link me-1"></i>${stdControlName}`;
            statusText.className = 'text-success';
            
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
        
        // 모든 매핑 저장
        function saveAllMappings() {
            if (Object.keys(mappingChanges).length === 0) {
                alert('저장할 변경사항이 없습니다.');
                return;
            }
            
            const savePromises = [];
            
            for (const [controlCode, change] of Object.entries(mappingChanges)) {
                if (change.action === 'add') {
                    // 매핑 추가
                    const promise = fetch(`/api/rcm/{{ rcm_info.rcm_id }}/mapping`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        credentials: 'same-origin',
                        body: JSON.stringify({
                            control_code: controlCode,
                            std_control_id: change.std_control_id,
                            confidence: 0.8,
                            mapping_type: 'manual'
                        })
                    });
                    savePromises.push(promise);
                } else if (change.action === 'remove') {
                    // 매핑 삭제는 별도 API 필요 (현재는 스킵)
                    console.log('매핑 삭제:', controlCode);
                }
            }
            
            if (savePromises.length > 0) {
                Promise.all(savePromises)
                    .then(responses => Promise.all(responses.map(r => r.json())))
                    .then(results => {
                        const allSuccess = results.every(result => result.success);
                        if (allSuccess) {
                            alert('매핑이 성공적으로 저장되었습니다.');
                            mappingChanges = {}; // 변경사항 초기화
                        } else {
                            alert('일부 매핑 저장에 실패했습니다.');
                        }
                    })
                    .catch(error => {
                        console.error('매핑 저장 오류:', error);
                        alert('매핑 저장 중 오류가 발생했습니다.');
                    });
            }
        }
    </script>
</body>
</html>