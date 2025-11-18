<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall - RCM 상세보기 - {{ rcm_info.rcm_name }}</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        #rcmTable {
            table-layout: auto; /* 내용에 따라 너비 자동 조정 */
            width: 100%; /* 부모 요소에 맞춤 */
        }
        #rcmTable th, #rcmTable td {
            word-wrap: break-word;
            overflow-wrap: break-word;
            vertical-align: top;
        }
        .text-truncate-custom {
            /* 이 클래스는 더 이상 사용되지 않으므로 스타일을 제거하거나 비워둡니다. */
        }
        /* Chrome, Safari, Edge, Opera - 숫자 입력 필드 화살표 제거 */
        input[type=number]::-webkit-inner-spin-button,
        input[type=number]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        /* Firefox - 숫자 입력 필드 화살표 제거 */
        input[type=number] {
            -moz-appearance: textfield;
        }

        /* 인라인 편집 스타일 */
        .editable-cell:hover {
            border-color: #0d6efd !important;
            background-color: #f8f9fa;
            cursor: text;
        }

        .editable-cell:focus {
            outline: none;
            border-color: #0d6efd !important;
            background-color: #fff;
            box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
        }

        /* 컬럼 고정 스타일 */
        #rcmTable th:nth-child(1),
        #rcmTable td:nth-child(1) {
            position: sticky;
            left: 0;
            z-index: 2;
        }

        #rcmTable th:nth-child(2),
        #rcmTable td:nth-child(2) {
            position: sticky;
            left: 80px; /* 첫 번째 컬럼의 min-width와 동일하게 설정 */
            z-index: 2;
        }

        #rcmTable th:nth-child(9),
        #rcmTable td:nth-child(9) {
            position: sticky;
            right: 0;
            z-index: 2;
        }

        /* 고정된 헤더의 배경색을 지정하여 스크롤 시 내용이 비치지 않도록 함 */
        #rcmTable thead th {
            background-color: #f8f9fa; /* thead 배경색 */
        }

        /* 고정된 바디 셀의 배경색을 지정 (줄무늬 테이블 고려) */
        #rcmTable tbody tr td:nth-child(1), 
        #rcmTable tbody tr td:nth-child(2),
        #rcmTable tbody tr td:nth-child(9) { background-color: #fff; }
        #rcmTable tbody tr:nth-of-type(odd) td:nth-child(1), 
        #rcmTable tbody tr:nth-of-type(odd) td:nth-child(2),
        #rcmTable tbody tr:nth-of-type(odd) td:nth-child(9) { background-color: #f9f9f9; }

        .editable-cell.modified {
            background-color: #fff3cd !important;
            border-color: #ffc107 !important;
        }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}

    <!-- 토스트 컨테이너 -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1100;">
        <div id="saveToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-info-circle me-2 toast-icon"></i>
                <strong class="me-auto toast-title">알림</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
            </div>
        </div>
    </div>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-eye me-2"></i>RCM 상세보기</h1>
                    <div>
                        <a href="/user/rcm" class="btn btn-secondary">
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
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>RCM 기본 정보</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="30%">RCM명:</th>
                                        <td><strong>{{ rcm_info.rcm_name }}</strong></td>
                                    </tr>
                                    <tr>
                                        <th>회사명:</th>
                                        <td>{{ rcm_info.company_name }}</td>
                                    </tr>
                                    <tr>
                                        <th>설명:</th>
                                        <td>{{ rcm_info.description or '없음' }}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="30%">업로드자:</th>
                                        <td>{{ rcm_info.upload_user_name or '알 수 없음' }}</td>
                                    </tr>
                                    <tr>
                                        <th>업로드일:</th>
                                        <td>{{ rcm_info.upload_date.split(' ')[0] if rcm_info.upload_date else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <th>총 통제 수:</th>
                                        <td><span class="badge bg-primary">{{ rcm_details|length }}개</span></td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- RCM 상세 데이터 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-list me-2"></i>통제 상세 목록</h5>
                        <div>
                            <button class="btn btn-sm btn-success me-2" id="saveAllChangesBtn" onclick="saveAllChanges()">
                                <i class="fas fa-save me-1"></i>변경사항 저장
                            </button>
                            <button class="btn btn-sm btn-outline-secondary me-2" onclick="exportToExcel()">
                                <i class="fas fa-file-excel me-1"></i>Excel 다운로드
                            </button>
                            {% if rcm_info.control_category == 'ITGC' %}
                            <a href="/rcm/{{ rcm_info.rcm_id }}/mapping" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-link me-1"></i>기준통제 매핑
                            </a>
                            {% endif %}
                        </div>
                    </div>
                    <div class="card-body">
                        {% if rcm_details %}
                        <div class="table-responsive" style="overflow-x: auto;">
                            <table class="table table-striped table-hover" id="rcmTable" style="min-width: 1800px;">
                                <thead>
                                    <tr>
                                        <th style="min-width: 80px;">통제코드</th>
                                        <th style="min-width: 150px;">통제명</th>
                                        <th style="min-width: 200px;">통제활동 설명</th>
                                        <th style="min-width: 100px;">통제주기</th>
                                        <th style="min-width: 100px;">통제구분</th>
                                        <th style="min-width: 90px;">핵심통제</th>
                                        <th style="min-width: 120px;">모집단</th>
                                        <th style="min-width: 540px;">테스트절차</th>
                                        <th style="min-width: 80px;">표본수</th>
                                        <th style="min-width: 120px;">Attribute 설정</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr>
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_name }}">
                                                <strong>{{ detail.control_name }}</strong>
                                            </span>
                                        </td>
                                        <td>
                                            {% if detail.control_description %}
                                                <span class="text-truncate-custom" title="{{ detail.control_description }}">
                                                    {{ detail.control_description }}
                                                </span>
                                            {% else %}
                                                <span class="text-muted">-</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_frequency_name or detail.control_frequency or '-' }}">
                                                {{ detail.control_frequency_name or detail.control_frequency or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.control_nature_name or detail.control_nature or '-' }}">
                                                {{ detail.control_nature_name or detail.control_nature or '-' }}
                                            </span>
                                        </td>
                                        <td class="text-center">
                                            {% if detail.key_control == '핵심' %}
                                                <span class="badge bg-danger">핵심</span>
                                            {% elif detail.key_control == '비핵심' %}
                                                <span class="badge bg-secondary">비핵심</span>
                                            {% else %}
                                                <span class="badge bg-warning">미설정</span>
                                            {% endif %}
                                        </td>
                                        <td>
                                            <span class="text-truncate-custom" title="{{ detail.population or '-' }}">
                                                {{ detail.population or '-' }}
                                            </span>
                                        </td>
                                        <td>
                                            <div style="display: block; width: 100%; padding: 4px; min-height: 2.5em; white-space: pre-wrap; word-wrap: break-word; max-height: 150px; overflow-y: auto;">{{ detail.test_procedure or '-' }}</div>
                                        </td>
                                        <td class="text-center">
                                            <input type="text"
                                                   class="form-control form-control-sm text-center sample-size-input"
                                                   data-detail-id="{{ detail.detail_id if detail.detail_id is not none else '' }}"
                                                   data-field="recommended_sample_size"
                                                   data-control-code="{{ detail.control_code }}"
                                                   data-control-frequency="{{ detail.control_frequency or '' }}"
                                                   data-original-value="{{ detail.recommended_sample_size if detail.recommended_sample_size is not none else '' }}"
                                                   value="{{ detail.recommended_sample_size if detail.recommended_sample_size is not none else '' }}"
                                                   maxlength="3"
                                                   placeholder="자동"
                                                   title="0: 모집단 업로드 모드"
                                                   style="width: 60px;">
                                        </td>
                                        <td class="text-center">
                                            <button class="btn btn-sm btn-outline-primary"
                                                    onclick="openAttributeModal('{{ detail.detail_id }}', '{{ detail.control_code }}', '{{ detail.control_name }}')">
                                                <i class="fas fa-cog me-1"></i>설정
                                            </button>
                                            <div id="attribute-summary-{{ detail.detail_id }}" class="mt-1 small text-muted">
                                                {% set attr_count = 0 %}
                                                {% for i in range(10) %}
                                                    {% if detail['attribute' ~ i] %}
                                                        {% set attr_count = attr_count + 1 %}
                                                    {% endif %}
                                                {% endfor %}
                                                {% if attr_count > 0 %}
                                                    <span class="badge bg-info">{{ attr_count }}개 설정됨</span>
                                                {% endif %}
                                            </div>
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
                            <p class="text-muted">관리자에게 문의하여 RCM 데이터를 확인하세요.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Attribute 설정 모달 -->
    <div class="modal fade" id="attributeModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-cog me-2"></i>Attribute 설정
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <strong>통제코드:</strong> <code id="modal-control-code"></code><br>
                        <strong>통제명:</strong> <span id="modal-control-name"></span>
                    </div>
                    <hr>
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        증빙 항목으로 사용할 attribute 필드를 설정하세요. (예: 완료예정일, 완료여부, 승인자 등)
                    </div>
                    <div class="mb-3">
                        <label for="population-attr-count" class="form-label">
                            <strong>모집단 항목 수</strong>
                            <small class="text-muted">(attribute0부터 시작, 나머지는 증빙 항목)</small>
                        </label>
                        <input type="number"
                               class="form-control form-control-sm"
                               id="population-attr-count"
                               min="1"
                               max="10"
                               value="2"
                               style="width: 100px;"
                               placeholder="예: 2">
                        <small class="text-muted">
                            예: 2로 설정 시 attribute0~1은 모집단, attribute2~9는 증빙
                        </small>
                    </div>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th width="20%">Attribute</th>
                                <th width="80%">필드명</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for i in range(10) %}
                            <tr>
                                <td><strong>attribute{{ i }}</strong></td>
                                <td>
                                    <input type="text"
                                           class="form-control form-control-sm attribute-input"
                                           id="attr-input-{{ i }}"
                                           data-index="{{ i }}"
                                           placeholder="예: 완료예정일, 완료여부, 승인자 등"
                                           maxlength="100">
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-1"></i>취소
                    </button>
                    <button type="button" class="btn btn-primary" onclick="saveAttributes()">
                        <i class="fas fa-save me-1"></i>저장
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        // 통제주기별 기본 표본수 계산
        function getDefaultSampleSize(frequencyCode) {
            const frequencyMapping = {
                'A': 1,  // 년
                'S': 2,  // 반기
                'Q': 3,  // 분기
                'M': 4,  // 월
                'W': 5,  // 주
                'D': 20, // 일
                'O': 1,  // 기타
                'N': 1   // 필요시
            };
            return frequencyMapping[frequencyCode] || 1;
        }

        // 토스트 메시지 표시 함수
        function showToast(message, type = 'info') {
            const toastEl = document.getElementById('saveToast');
            const toastBody = toastEl.querySelector('.toast-body');
            const toastHeader = toastEl.querySelector('.toast-header');
            const toastIcon = toastEl.querySelector('.toast-icon');
            const toastTitle = toastEl.querySelector('.toast-title');

            // 메시지 설정
            toastBody.textContent = message;

            // 타입에 따른 스타일 및 아이콘 설정
            toastHeader.className = 'toast-header';
            toastIcon.className = 'me-2 toast-icon';

            if (type === 'success') {
                toastHeader.classList.add('bg-success', 'text-white');
                toastIcon.classList.add('fas', 'fa-check-circle');
                toastTitle.textContent = '성공';
            } else if (type === 'error') {
                toastHeader.classList.add('bg-danger', 'text-white');
                toastIcon.classList.add('fas', 'fa-exclamation-circle');
                toastTitle.textContent = '오류';
            } else if (type === 'warning') {
                toastHeader.classList.add('bg-warning');
                toastIcon.classList.add('fas', 'fa-exclamation-triangle');
                toastTitle.textContent = '경고';
            } else {
                toastHeader.classList.add('bg-info', 'text-white');
                toastIcon.classList.add('fas', 'fa-info-circle');
                toastTitle.textContent = '알림';
            }

            // 토스트 표시
            const toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: 3000
            });
            toast.show();
        }

        // Excel 다운로드 기능
        function exportToExcel() {
            const table = document.getElementById('rcmTable');
            const wb = XLSX.utils.table_to_book(table, {sheet: "RCM 상세"});
            const fileName = '{{ rcm_info.rcm_name }}_상세보기.xlsx';
            XLSX.writeFile(wb, fileName);
        }

        // 변경사항 통합 저장 기능
        // 툴팁 초기화
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
            var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            document.querySelectorAll('.editable-cell').forEach(cell => {
                cell.addEventListener('keydown', function(e) {
                    // Enter 키를 누르면 줄바꿈 문자를 삽입
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault(); // 기본 동작(div/p 태그 생성) 방지
                        document.execCommand('insertLineBreak');
                    }
                });
            });

            document.querySelectorAll('.editable-cell').forEach(cell => {
                cell.addEventListener('blur', function() {
                    if (this.textContent.trim() === '') {
                        this.textContent = '-';
                    }
                });

                cell.addEventListener('focus', function() {
                    if (this.textContent.trim() === '-') {
                        this.textContent = '';
                    }
                });
            });

            document.querySelectorAll('.sample-size-input').forEach(input => {
                if (!input.value) {
                    const controlFrequency = input.getAttribute('data-control-frequency');
                    const defaultSize = getDefaultSampleSize(controlFrequency);
                    input.setAttribute('placeholder', defaultSize);
                }

                // 숫자만 입력 가능하도록 제한 (입력 중)
                input.addEventListener('keypress', function(e) {
                    // 숫자(0-9)만 허용
                    if (e.key < '0' || e.key > '9') {
                        e.preventDefault();
                    }
                });

                // 붙여넣기 시 숫자만 허용
                input.addEventListener('paste', function(e) {
                    e.preventDefault();
                    const pastedText = (e.clipboardData || window.clipboardData).getData('text');
                    const numbersOnly = pastedText.replace(/\D/g, '');
                    if (numbersOnly) {
                        this.value = numbersOnly.slice(0, 3);  // 최대 3자리
                    }
                });

                // 입력 값 유효성 검사 (blur 이벤트에서만 체크)
                input.addEventListener('blur', function() {
                    const value = parseInt(this.value);
                    if (this.value.trim() !== '' && (isNaN(value) || value < 0 || value > 100)) {
                        alert('표본수는 0~100 사이의 값이거나 공란이어야 합니다. (0: 모집단 업로드 모드)');
                        this.value = '';  // 잘못된 값을 지움
                    }
                });
            });
        });

        async function saveAllChanges() {
            const saveBtn = document.getElementById('saveAllChangesBtn');
            const originalHtml = saveBtn.innerHTML;
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>저장 중...';

            try {
                const dataToSave = new Map();

                // 모든 '테스트 절차' 데이터 수집
                document.querySelectorAll('.editable-cell[data-field="test_procedure"]').forEach(cell => {
                    const detailId = cell.dataset.detailId;
                    const value = cell.textContent.trim() === '-' ? '' : cell.textContent.trim();
                    if (!dataToSave.has(detailId)) dataToSave.set(detailId, {});
                    dataToSave.get(detailId).test_procedure = value;
                });

                // 모든 '표본수' 데이터 수집
                document.querySelectorAll('.sample-size-input[data-field="recommended_sample_size"]').forEach(input => {
                    const detailId = input.dataset.detailId;
                    const value = input.value;
                    if (!dataToSave.has(detailId)) dataToSave.set(detailId, {});
                    dataToSave.get(detailId).recommended_sample_size = value;
                });

                const updates = [];
                dataToSave.forEach((fields, detailId) => {
                    updates.push({
                        detail_id: parseInt(detailId),
                        fields: fields
                    });
                });

                if (updates.length === 0) {
                    showToast('저장할 데이터가 없습니다.', 'info');
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = originalHtml;
                    return;
                }

                const response = await fetch('/api/rcm/update_controls', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ updates: updates })
                });

                const result = await response.json();

                if (result.success) {
                    showToast('변경사항이 저장되었습니다.', 'success');
                } else {
                    showToast(result.message || '저장에 실패했습니다.', 'error');
                }
            } catch (error) {
                console.error('Save error:', error);
                showToast('저장 중 오류가 발생했습니다.', 'error');
            } finally {
                saveBtn.disabled = false;
                saveBtn.innerHTML = originalHtml;
            }
        }

        // Attribute 설정 모달 관련 변수
        let currentDetailId = null;
        let attributeModalInstance = null;

        // Attribute 모달 열기
        function openAttributeModal(detailId, controlCode, controlName) {
            currentDetailId = detailId;

            // 모달 정보 표시
            document.getElementById('modal-control-code').textContent = controlCode;
            document.getElementById('modal-control-name').textContent = controlName;

            // 기존 attribute 값 로드
            loadAttributes(detailId);

            // 모달 표시
            const modalEl = document.getElementById('attributeModal');
            if (!attributeModalInstance) {
                attributeModalInstance = new bootstrap.Modal(modalEl);
            }
            attributeModalInstance.show();
        }

        // 기존 attribute 값 로드
        function loadAttributes(detailId) {
            fetch(`/api/rcm/detail/${detailId}/attributes`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const attributes = data.attributes || {};

                        // attribute 필드 로드
                        for (let i = 0; i < 10; i++) {
                            const input = document.getElementById(`attr-input-${i}`);
                            if (input) {
                                input.value = attributes[`attribute${i}`] || '';
                            }
                        }

                        // population_attribute_count 로드
                        const popCountInput = document.getElementById('population-attr-count');
                        if (popCountInput) {
                            popCountInput.value = data.population_attribute_count || 2;
                        }
                    } else {
                        console.error('Failed to load attributes:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error loading attributes:', error);
                });
        }

        // Attribute 저장
        function saveAttributes() {
            if (!currentDetailId) {
                showToast('오류: 통제 ID가 없습니다.', 'error');
                return;
            }

            // attribute 값 수집
            const attributes = {};
            for (let i = 0; i < 10; i++) {
                const input = document.getElementById(`attr-input-${i}`);
                if (input && input.value.trim()) {
                    attributes[`attribute${i}`] = input.value.trim();
                }
            }

            // population_attribute_count 수집
            const popCountInput = document.getElementById('population-attr-count');
            const populationAttributeCount = popCountInput ? parseInt(popCountInput.value) : 2;

            // 서버에 저장
            fetch(`/api/rcm/detail/${currentDetailId}/attributes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    attributes,
                    population_attribute_count: populationAttributeCount
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Attribute 설정이 저장되었습니다.', 'success');

                    // 모달 닫기
                    if (attributeModalInstance) {
                        attributeModalInstance.hide();
                    }

                    // 요약 업데이트
                    updateAttributeSummary(currentDetailId, attributes);
                } else {
                    showToast('저장 실패: ' + (data.message || '알 수 없는 오류'), 'error');
                }
            })
            .catch(error => {
                console.error('Error saving attributes:', error);
                showToast('저장 중 오류가 발생했습니다.', 'error');
            });
        }

        // Attribute 요약 업데이트
        function updateAttributeSummary(detailId, attributes) {
            const summaryEl = document.getElementById(`attribute-summary-${detailId}`);
            if (!summaryEl) return;

            const count = Object.keys(attributes).length;
            if (count > 0) {
                summaryEl.innerHTML = `<span class="badge bg-info">${count}개 설정됨</span>`;
            } else {
                summaryEl.innerHTML = '';
            }
        }

    </script>
</body>
</html>