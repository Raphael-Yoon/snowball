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
            table-layout: fixed;
            width: 100%;
        }
        #rcmTable th, #rcmTable td {
            word-wrap: break-word;
            overflow-wrap: break-word;
            vertical-align: top;
        }
        .text-truncate-custom {
            display: block;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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
                                    <tr>
                                        <th>내 권한:</th>
                                        <td>
                                            <span class="badge bg-{{ 'danger' if rcm_info.permission_type == 'admin' else 'success' }}">
                                                {{ '관리자' if rcm_info.permission_type == 'admin' else '읽기' }}
                                            </span>
                                        </td>
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
                            <button class="btn btn-sm btn-outline-primary me-2" id="saveAllSampleSizesBtn" onclick="saveAllSampleSizes()">
                                <i class="fas fa-save me-1"></i>저장
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
                        <div class="table-responsive">
                            <table class="table table-striped table-hover" id="rcmTable">
                                <thead>
                                    <tr>
                                        <th width="6%">통제코드</th>
                                        <th width="11%">통제명</th>
                                        <th width="19%">통제활동 설명</th>
                                        <th width="8%">통제주기</th>
                                        <th width="8%">통제유형</th>
                                        <th width="8%">통제구분</th>
                                        <th width="7%">핵심통제</th>
                                        <th width="11%">모집단</th>
                                        <th width="15%">테스트절차</th>
                                        <th width="7%">표본수</th>
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
                                            <span class="text-truncate-custom" title="{{ detail.control_type_name or detail.control_type or '-' }}">
                                                {{ detail.control_type_name or detail.control_type or '-' }}
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
                                            {% if detail.test_procedure %}
                                                <span class="text-truncate-custom" title="{{ detail.test_procedure }}">
                                                    {{ detail.test_procedure }}
                                                </span>
                                            {% else %}
                                                <span class="text-muted">-</span>
                                            {% endif %}
                                        </td>
                                        <td class="text-center">
                                            <input type="text"
                                                   class="form-control form-control-sm text-center sample-size-input"
                                                   data-detail-id="{{ detail.detail_id if detail.detail_id is not none else '' }}"
                                                   data-control-code="{{ detail.control_code }}"
                                                   data-control-frequency="{{ detail.control_frequency or '' }}"
                                                   data-original-value="{{ detail.recommended_sample_size if detail.recommended_sample_size is not none else '' }}"
                                                   value="{{ detail.recommended_sample_size if detail.recommended_sample_size is not none else '' }}"
                                                   maxlength="3"
                                                   placeholder="자동"
                                                   title="0: 모집단 업로드 모드"
                                                   style="width: 60px;">
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

        // 일괄 저장 기능
        function saveAllSampleSizes() {
            const saveBtn = document.getElementById('saveAllSampleSizesBtn');
            const inputs = document.querySelectorAll('.sample-size-input');

            console.log(`[DEBUG] 총 ${inputs.length}개의 입력 필드 발견`);

            // 변경된 항목만 수집
            const changes = [];
            inputs.forEach((input, index) => {
                const detailId = input.getAttribute('data-detail-id');
                const originalValue = input.getAttribute('data-original-value') || '';
                const currentValue = input.value || '';
                const currentValueNum = parseInt(currentValue);

                console.log(`[DEBUG ${index}] detail_id: ${detailId}, originalValue: "${originalValue}", currentValue: "${currentValue}", parsedValue: ${currentValueNum}`);

                // detail_id 유효성 검증
                if (!detailId || detailId === 'None' || detailId === 'null' || detailId.trim() === '') {
                    console.error(`[DEBUG ${index}] 유효하지 않은 detail_id:`, detailId);
                    return;
                }

                // 값 정규화 (빈 문자열과 null을 동일하게 처리)
                const normalizedOriginal = originalValue.trim() === '' ? null : originalValue.trim();
                let normalizedCurrent;
                if (currentValue.trim() === '') {
                    normalizedCurrent = null;
                } else if (!isNaN(currentValueNum) && currentValueNum >= 0 && currentValueNum <= 100) {
                    // 0~100 사이의 숫자만 허용 (0 포함)
                    normalizedCurrent = String(currentValueNum);
                } else {
                    normalizedCurrent = currentValue.trim();
                }

                // 값이 변경된 경우만 추가
                if (normalizedOriginal !== normalizedCurrent) {
                    console.log(`[변경 감지 ${index}] detail_id: ${detailId}, 원본: "${normalizedOriginal}", 현재: "${normalizedCurrent}"`);
                    changes.push({
                        detail_id: detailId,
                        sample_size: normalizedCurrent !== null ? parseInt(normalizedCurrent) : null
                    });
                } else {
                    console.log(`[변경 없음 ${index}] detail_id: ${detailId}, 원본: "${normalizedOriginal}", 현재: "${normalizedCurrent}"`);
                }
            });

            console.log(`[DEBUG] 총 ${changes.length}개의 변경사항 발견`);

            if (changes.length === 0) {
                showToast('변경된 항목이 없습니다.', 'info');
                return;
            }

            // 버튼 비활성화 및 로딩 표시
            const originalHtml = saveBtn.innerHTML;
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>저장 중...';

            // 모든 변경사항을 순차적으로 저장
            let successCount = 0;
            let failCount = 0;
            const promises = changes.map(change => {
                return fetch(`/admin/rcm/detail/${change.detail_id}/sample-size`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        recommended_sample_size: change.sample_size
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            try {
                                return JSON.parse(text);
                            } catch (e) {
                                return {
                                    success: false,
                                    message: `서버 오류 (${response.status}): ${response.statusText}`
                                };
                            }
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        successCount++;
                        const input = document.querySelector(`.sample-size-input[data-detail-id="${change.detail_id}"]`);
                        if (input) {
                            input.setAttribute('data-original-value', change.sample_size || '');
                        }
                    } else {
                        failCount++;
                        console.error('저장 실패:', data.message || '알 수 없는 오류');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    failCount++;
                });
            });

            Promise.all(promises).then(() => {
                if (failCount === 0) {
                    saveBtn.classList.remove('btn-outline-primary');
                    saveBtn.classList.add('btn-success');
                    saveBtn.innerHTML = '<i class="fas fa-check me-1"></i>저장 완료';

                    showToast(`${successCount}개 항목이 성공적으로 저장되었습니다.`, 'success');

                    setTimeout(() => {
                        saveBtn.classList.remove('btn-success');
                        saveBtn.classList.add('btn-outline-primary');
                        saveBtn.innerHTML = originalHtml;
                        saveBtn.disabled = false;
                    }, 2000);
                } else {
                    showToast(`저장 완료: ${successCount}개 성공, ${failCount}개 실패`, 'warning');
                    saveBtn.innerHTML = originalHtml;
                    saveBtn.disabled = false;
                }
            });
        }

        // Excel 다운로드 기능
        function exportToExcel() {
            const table = document.getElementById('rcmTable');
            const wb = XLSX.utils.table_to_book(table, {sheet: "RCM 상세"});
            const fileName = '{{ rcm_info.rcm_name }}_상세보기.xlsx';
            XLSX.writeFile(wb, fileName);
        }

        // 툴팁 초기화
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
            var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            // 각 입력란에 이벤트 리스너 추가
            document.querySelectorAll('.sample-size-input').forEach(input => {
                // placeholder를 자동 계산된 값으로 설정
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
    </script>
</body>
</html>