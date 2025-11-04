<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall - ELC 설계평가</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
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
                    <h1><img src="{{ url_for('static', filename='img/elc.jpg') }}" alt="ELC" style="width: 40px; height: 40px; object-fit: cover; border-radius: 8px; margin-right: 12px;">ELC 설계평가</h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="fas fa-home me-1"></i>홈으로
                    </a>
                </div>
                <hr>
            </div>
        </div>

        <!-- 설계평가 소개 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
                        <h5><i class="fas fa-info-circle me-2"></i>설계평가란?</h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">
                            <strong>설계평가(Design Effectiveness Testing)</strong>는 RCM에 기록된 통제활동이 현재 실제 업무와 일치하는지를 확인하고, 실무적으로 효과적으로 운영되고 있는지를 평가하는 과정입니다.
                        </p>
                        <ul>
                            <li><strong>목적:</strong> 문서상 통제와 실제 수행되는 통제의 일치성 확인 및 실무 효과성 검증</li>
                            <li><strong>범위:</strong> 통제 절차의 현실 반영도, 실제 운영 상태, 위험 완화 효과 검토</li>
                            <li><strong>결과:</strong> 실무와 문서 간 차이점 식별 및 통제 운영 개선방안 도출</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- RCM 기반 설계평가 -->
        <div class="row g-4">
            <div class="col-lg-12 col-md-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="fas fa-database me-2"></i>RCM 기반 설계평가</h5>
                    </div>
                    <div class="card-body">
                        <p class="mb-4">귀하에게 할당된 RCM을 기반으로 체계적인 설계평가를 수행합니다. 통제의 설계 효과성을 검토하고 개선점을 도출할 수 있습니다.</p>
                        
                        <div class="row">
                            <div class="col-md-8">
                                <div class="row g-3 mb-3">
                                    <div class="col-sm-6">
                                        <div class="d-flex align-items-center">
                                            <div class="bg-success rounded-circle p-2 me-3" style="width: 40px; height: 40px;">
                                                <i class="fas fa-search text-white"></i>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">통제 설계 검토</h6>
                                                <small class="text-muted">통제의 설계 효과성 평가</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-sm-6">
                                        <div class="d-flex align-items-center">
                                            <div class="bg-info rounded-circle p-2 me-3" style="width: 40px; height: 40px;">
                                                <i class="fas fa-link text-white"></i>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">위험-통제 연계성</h6>
                                                <small class="text-muted">위험과 통제의 매핑 분석</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-sm-6">
                                        <div class="d-flex align-items-center">
                                            <div class="bg-warning rounded-circle p-2 me-3" style="width: 40px; height: 40px;">
                                                <i class="fas fa-bug text-white"></i>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">설계 결함 식별</h6>
                                                <small class="text-muted">통제 설계상의 문제점 발견</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-sm-6">
                                        <div class="d-flex align-items-center">
                                            <div class="bg-primary rounded-circle p-2 me-3" style="width: 40px; height: 40px;">
                                                <i class="fas fa-clipboard-check text-white"></i>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">구현 상태 확인</h6>
                                                <small class="text-muted">통제의 실제 구현 여부</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-4 text-center">
                                <div class="bg-light rounded p-3 mb-3">
                                    <i class="fas fa-tasks fa-3x text-success mb-2"></i>
                                    <h6>설계평가 현황</h6>
                                    <div class="row">
                                        <div class="col-12 mb-2">
                                            <div class="text-success">
                                                <strong id="availableRcmCount">
                                                    <span class="spinner-border spinner-border-sm" role="status"></span>
                                                </strong>
                                                <small class="d-block">평가 가능한 RCM</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button id="startDesignEvalBtn" class="btn btn-success" onclick="startDesignEvaluation()">
                                        <i class="fas fa-play me-1"></i>새로운 설계평가 시작
                                    </button>
                                    <button id="resumeDesignEvalBtn" class="btn btn-outline-primary" onclick="showResumeModal()">
                                        <i class="fas fa-history me-1"></i>기존 설계평가 이어하기
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 설계평가 히스토리 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-history me-2"></i>최근 설계평가 결과</h6>
                    </div>
                    <div class="card-body">
                        {% if recent_evaluations %}
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>평가 세션</th>
                                        <th>RCM</th>
                                        <th>평가 통제 수</th>
                                        <th>완료일</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for eval in recent_evaluations %}
                                    <tr>
                                        <td><strong>{{ eval.evaluation_session }}</strong></td>
                                        <td>{{ eval.rcm_name }}</td>
                                        <td>{{ eval.evaluated_controls }}/{{ eval.total_controls }}</td>
                                        <td>{{ eval.completed_date.split(' ')[0] if eval.completed_date else '-' }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="fas fa-clock fa-2x text-muted mb-2"></i>
                            <p class="text-muted">아직 수행된 설계평가가 없습니다.</p>
                            <small class="text-muted">설계평가를 시작하면 여기에 결과가 표시됩니다.</small>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <!-- 설계평가 가이드 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-question-circle me-2"></i>설계평가 가이드</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <h6 class="text-primary">1. 준비 단계</h6>
                                <ul class="small">
                                    <li>평가 대상 통제 식별</li>
                                    <li>관련 문서 준비</li>
                                    <li>평가 기준 검토</li>
                                </ul>
                            </div>
                            <div class="col-md-4">
                                <h6 class="text-success">2. 실행 단계</h6>
                                <ul class="small">
                                    <li>설계 효과성 검토</li>
                                    <li>구현 상태 확인</li>
                                    <li>문서화 수준 평가</li>
                                </ul>
                            </div>
                            <div class="col-md-4">
                                <h6 class="text-warning">3. 완료 단계</h6>
                                <ul class="small">
                                    <li>평가 결론 도출</li>
                                    <li>개선사항 식별</li>
                                    <li>보고서 작성</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- 설계평가 JavaScript -->
    <script>
        // 페이지 로드 시 RCM 현황 로드
        document.addEventListener('DOMContentLoaded', function() {
            loadAvailableRcmCount();
        });
        
        // 평가 가능한 RCM 수 로드
        function loadAvailableRcmCount() {
            fetch('/api/user/rcm-list')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // ELC RCM만 필터링하여 카운트
                        const elcRcms = data.rcms.filter(rcm => rcm.control_category === 'ELC');
                        const elcCount = elcRcms.length;

                        document.getElementById('availableRcmCount').textContent = elcCount;

                        // RCM이 없으면 버튼 비활성화
                        const startButton = document.getElementById('startDesignEvalBtn');
                        const resumeButton = document.getElementById('resumeDesignEvalBtn');
                        if (elcCount === 0) {
                            startButton.disabled = true;
                            startButton.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>평가 가능한 ELC RCM 없음';
                            startButton.classList.remove('btn-success');
                            startButton.classList.add('btn-secondary');

                            resumeButton.disabled = true;
                            resumeButton.classList.remove('btn-outline-primary');
                            resumeButton.classList.add('btn-outline-secondary');
                        }
                    } else {
                        document.getElementById('availableRcmCount').textContent = '0';
                        const startButton = document.getElementById('startDesignEvalBtn');
                        const resumeButton = document.getElementById('resumeDesignEvalBtn');

                        startButton.disabled = true;
                        startButton.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>평가 가능한 ELC RCM 없음';
                        startButton.classList.remove('btn-success');
                        startButton.classList.add('btn-secondary');

                        resumeButton.disabled = true;
                        resumeButton.classList.remove('btn-outline-primary');
                        resumeButton.classList.add('btn-outline-secondary');
                    }
                })
                .catch(error => {
                    console.error('RCM 현황 로드 오류:', error);
                    document.getElementById('availableRcmCount').textContent = '-';
                });
        }
        
        // 설계평가 시작
        function startDesignEvaluation() {
            fetch('/api/user/rcm-list')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.rcms.length > 0) {
                        // ELC RCM만 필터링
                        const elcRcms = data.rcms.filter(rcm => rcm.control_category === 'ELC');
                        if (elcRcms.length > 0) {
                            showRcmSelectionModal(elcRcms);
                        } else {
                            alert('평가할 수 있는 ELC RCM이 없습니다.');
                        }
                    } else {
                        alert('평가할 수 있는 RCM이 없습니다.');
                    }
                })
                .catch(error => {
                    console.error('RCM 목록 로드 오류:', error);
                    alert('RCM 목록을 불러오는 중 오류가 발생했습니다.');
                });
        }
        
        // RCM 선택 모달 표시
        function showRcmSelectionModal(rcms, isNew = true) {
            // 기존 모달이 있다면 제거
            const existingModal = document.getElementById('rcmSelectionModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            const titleText = isNew ? '새로운 설계평가할 RCM 선택' : '이어할 설계평가 RCM 선택';
            const buttonText = isNew ? '평가 시작' : '세션 선택';
            const buttonAction = isNew ? 'startNewEvaluation' : 'showSessionSelection';
            
            // 모달 HTML 생성
            const modalHtml = `
                <div class="modal fade" id="rcmSelectionModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-clipboard-check me-2"></i>${titleText}
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">설계평가를 수행할 RCM을 선택하세요.</p>
                                <div class="row g-3">
                                    ${rcms.map(rcm => `
                                        <div class="col-md-6">
                                            <div class="card border-success h-100">
                                                <div class="card-body">
                                                    <h6 class="card-title">${rcm.rcm_name}</h6>
                                                    <p class="card-text small text-muted">${rcm.company_name}</p>
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span class="badge bg-${rcm.permission_type === 'admin' ? 'danger' : 'success'}">
                                                            ${rcm.permission_type === 'admin' ? '관리자' : '읽기'}
                                                        </span>
                                                        <button class="btn btn-sm btn-success" onclick="${buttonAction}(${rcm.rcm_id}, '${rcm.rcm_name}')">
                                                            <i class="fas fa-${isNew ? 'play' : 'history'} me-1"></i>${buttonText}
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 모달을 body에 추가
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('rcmSelectionModal'));
            modal.show();
        }
        
        // 새로운 설계평가 시작
        function startNewEvaluation(rcmId, rcmName) {
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('rcmSelectionModal'));
            modal.hide();
            
            // 평가명 입력 모달 표시
            showEvaluationNameModal(rcmId, rcmName);
        }
        
        // 평가명 입력 모달
        function showEvaluationNameModal(rcmId, rcmName) {
            const today = new Date();
            const year = today.getFullYear();
            const defaultName = `FY${year.toString().slice(-2)}_내부평가`;

            const modalHtml = `
                <div class="modal fade" id="evaluationNameModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-edit me-2"></i>설계평가명 입력
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">RCM: <strong>${rcmName}</strong></p>
                                <div class="mb-3">
                                    <label for="evaluationNameInput" class="form-label">설계평가명</label>
                                    <input type="text" class="form-control" id="evaluationNameInput"
                                           value="${defaultName}" placeholder="예: FY25_내부평가">
                                    <div class="form-text">평가를 구분할 수 있는 이름을 입력하세요.</div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                                <button type="button" class="btn btn-success" onclick="confirmStartEvaluation(${rcmId})">
                                    <i class="fas fa-play me-1"></i>평가 시작
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('evaluationNameModal'));
            modal.show();
            
            // 모달이 닫힐 때 DOM에서 제거
            modal._element.addEventListener('hidden.bs.modal', function () {
                this.remove();
            });
        }
        
        // 평가 시작 확인
        function confirmStartEvaluation(rcmId) {
            const evaluationName = document.getElementById('evaluationNameInput').value.trim();
            
            if (!evaluationName) {
                alert('평가명을 입력해주세요.');
                return;
            }
            
            // 버튼 비활성화 (중복 클릭 방지)
            const confirmButton = document.querySelector('#evaluationNameModal .btn-success');
            confirmButton.disabled = true;
            confirmButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>생성 중...';
            
            // 서버에 설계평가 생성 요청 (Header + Line 구조 생성)
            fetch('/api/design-evaluation/create-evaluation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rcm_id: rcmId,
                    evaluation_session: evaluationName
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 평가 세션명과 헤더 ID를 세션 스토리지에 저장
                    sessionStorage.setItem('currentEvaluationSession', evaluationName);
                    sessionStorage.setItem('currentEvaluationHeaderId', data.header_id);
                    sessionStorage.setItem('isNewEvaluationSession', 'true'); // 새 세션임을 표시
                    
                    console.log('New evaluation created - header_id:', data.header_id);
                    
                    // 모달 닫기
                    const modal = bootstrap.Modal.getInstance(document.getElementById('evaluationNameModal'));
                    modal.hide();
                    
                    // 설계평가 페이지로 POST 방식으로 이동
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '/design-evaluation/rcm';

                    const rcmInput = document.createElement('input');
                    rcmInput.type = 'hidden';
                    rcmInput.name = 'rcm_id';
                    rcmInput.value = rcmId;

                    const evalTypeInput = document.createElement('input');
                    evalTypeInput.type = 'hidden';
                    evalTypeInput.name = 'evaluation_type';
                    evalTypeInput.value = 'ELC';

                    form.appendChild(rcmInput);
                    form.appendChild(evalTypeInput);
                    document.body.appendChild(form);
                    form.submit();
                } else {
                    alert(data.message);
                    
                    // 버튼 복원
                    confirmButton.disabled = false;
                    confirmButton.innerHTML = '<i class="fas fa-play me-1"></i>평가 시작';
                }
            })
            .catch(error => {
                console.error('평가 생성 오류:', error);
                alert('평가 생성 중 오류가 발생했습니다.');
                
                // 버튼 복원
                confirmButton.disabled = false;
                confirmButton.innerHTML = '<i class="fas fa-play me-1"></i>평가 시작';
            });
        }
        
        // 기존 평가 이어하기 모달
        function showResumeModal() {
            fetch('/api/user/rcm-list')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.rcms.length > 0) {
                        // ELC RCM만 필터링
                        const elcRcms = data.rcms.filter(rcm => rcm.control_category === 'ELC');
                        if (elcRcms.length > 0) {
                            showRcmSelectionModal(elcRcms, false);
                        } else {
                            alert('평가할 수 있는 ELC RCM이 없습니다.');
                        }
                    } else {
                        alert('평가할 수 있는 RCM이 없습니다.');
                    }
                })
                .catch(error => {
                    console.error('RCM 목록 로드 오류:', error);
                    alert('RCM 목록을 불러오는 중 오류가 발생했습니다.');
                });
        }
        
        // 평가 세션 선택
        function showSessionSelection(rcmId, rcmName) {
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('rcmSelectionModal'));
            modal.hide();
            
            // 세션 목록 조회
            fetch(`/api/design-evaluation/sessions/${rcmId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showSessionSelectionModal(rcmId, rcmName, data.sessions);
                    } else {
                        alert('세션 목록을 불러올 수 없습니다.');
                    }
                })
                .catch(error => {
                    console.error('세션 목록 조회 오류:', error);
                    alert('세션 목록을 불러오는 중 오류가 발생했습니다.');
                });
        }
        
        // 세션 선택 모달
        function showSessionSelectionModal(rcmId, rcmName, sessions) {
            const modalHtml = `
                <div class="modal fade" id="sessionSelectionModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-history me-2"></i>평가 세션 선택
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p class="text-muted mb-3">RCM: <strong>${rcmName}</strong></p>
                                ${sessions.length > 0 ?
                                    sessions.map(session => `
                                        <div class="card mb-3 ${session.evaluation_status === 'ARCHIVED' ? 'border-secondary' : (session.completed_date ? 'border-success' : 'border-warning')}">
                                            <div class="card-body">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <div class="d-flex align-items-center mb-1">
                                                            <h6 class="mb-0 me-2">${session.evaluation_session}</h6>
                                                            ${session.evaluation_status === 'ARCHIVED' ?
                                                                '<span class="badge bg-secondary"><i class="fas fa-archive me-1"></i>Archive</span>' :
                                                                (session.completed_date ?
                                                                    '<span class="badge bg-success"><i class="fas fa-check me-1"></i>완료</span>' :
                                                                    '<span class="badge bg-warning text-dark"><i class="fas fa-clock me-1"></i>진행중</span>')
                                                            }
                                                        </div>
                                                        <small class="text-muted">
                                                            시작: ${new Date(session.start_date).toLocaleDateString()} |
                                                            최종 수정: ${new Date(session.last_updated).toLocaleDateString()} |
                                                            평가된 통제: ${session.evaluated_controls}개
                                                            ${session.completed_date ?
                                                                ` | 완료일: ${new Date(session.completed_date).toLocaleDateString()}` :
                                                                ` | 진행률: ${session.progress_percentage.toFixed(1)}%`
                                                            }
                                                        </small>
                                                    </div>
                                                    <div class="btn-group">
                                                        ${session.evaluation_status === 'ARCHIVED' ?
                                                            `<button class="btn btn-sm btn-outline-secondary" onclick="unarchiveEvaluationSession(${rcmId}, '${session.evaluation_session}')">
                                                                <i class="fas fa-undo me-1"></i>복원
                                                            </button>` :
                                                            (session.completed_date ?
                                                                `<button class="btn btn-sm btn-success" onclick="resumeEvaluation(${rcmId}, '${session.evaluation_session}', ${session.header_id})">
                                                                    <i class="fas fa-eye me-1"></i>보기
                                                                </button>` :
                                                                `<button class="btn btn-sm btn-primary" onclick="resumeEvaluation(${rcmId}, '${session.evaluation_session}', ${session.header_id})">
                                                                    <i class="fas fa-play me-1"></i>이어하기
                                                                </button>`)
                                                        }
                                                        ${session.evaluation_status !== 'ARCHIVED' ?
                                                            `<button class="btn btn-sm btn-outline-danger" onclick="deleteEvaluationSession(${rcmId}, '${session.evaluation_session}')">
                                                                <i class="fas fa-trash me-1"></i>삭제
                                                            </button>` : ''}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    `).join('') 
                                    : '<div class="text-center py-4"><p class="text-muted">저장된 평가 세션이 없습니다.</p></div>'
                                }
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('sessionSelectionModal'));
            modal.show();
            
            // 모달이 닫힐 때 DOM에서 제거
            modal._element.addEventListener('hidden.bs.modal', function () {
                this.remove();
            });
        }
        
        // 평가 세션 이어하기
        function resumeEvaluation(rcmId, sessionName, headerId) {
            // 평가 세션명과 헤더 ID를 세션 스토리지에 저장
            sessionStorage.setItem('currentEvaluationSession', sessionName);
            sessionStorage.setItem('currentEvaluationHeaderId', headerId);
            
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('sessionSelectionModal'));
            modal.hide();
            
            // 설계평가 페이지로 POST 방식으로 이동
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/design-evaluation/rcm';

            const rcmInput = document.createElement('input');
            rcmInput.type = 'hidden';
            rcmInput.name = 'rcm_id';
            rcmInput.value = rcmId;

            const evalTypeInput = document.createElement('input');
            evalTypeInput.type = 'hidden';
            evalTypeInput.name = 'evaluation_type';
            evalTypeInput.value = 'ELC';

            form.appendChild(rcmInput);
            form.appendChild(evalTypeInput);
            document.body.appendChild(form);
            form.submit();
        }
        
        // 평가 세션 삭제
        function deleteEvaluationSession(rcmId, sessionName) {
            if (!confirm(`"${sessionName}" 세션을 삭제하시겠습니까?`)) {
                return;
            }
            
            fetch('/api/design-evaluation/delete-session', {
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
                    // 삭제 성공 - 알림 없이 모달만 닫기
                    const modal = bootstrap.Modal.getInstance(document.getElementById('sessionSelectionModal'));
                    modal.hide();
                } else {
                    alert(data.message || '삭제 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                console.error('세션 삭제 오류:', error);
                alert('세션 삭제 중 오류가 발생했습니다.');
            });
        }

        // Archive된 평가 세션 복원
        function unarchiveEvaluationSession(rcmId, sessionName) {
            if (!confirm(`"${sessionName}" 세션을 복원하시겠습니까?\n\n복원하면 다시 일반 설계평가 목록에 표시됩니다.`)) {
                return;
            }

            fetch('/api/design-evaluation/unarchive', {
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
                    alert('세션이 복원되었습니다.');
                    // 모달 새로고침을 위해 세션 목록 다시 로드
                    showSessionSelection(rcmId, ''); // rcmName은 비워도 됨
                } else {
                    alert(data.message || '복원 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                console.error('세션 복원 오류:', error);
                alert('세션 복원 중 오류가 발생했습니다.');
            });
        }
    </script>
</body>
</html>