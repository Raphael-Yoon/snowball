<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>설계평가</title>
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
                    <h1><i class="fas fa-drafting-compass me-2"></i>설계평가</h1>
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
                            <strong>설계평가(Design Effectiveness Testing)</strong>는 통제가 이론적으로 효과적으로 설계되었는지를 평가하는 과정입니다.
                        </p>
                        <ul>
                            <li><strong>목적:</strong> 통제의 설계가 식별된 위험을 적절히 완화할 수 있는지 평가</li>
                            <li><strong>범위:</strong> 통제의 설계, 구현 상태, 문서화 수준 검토</li>
                            <li><strong>결과:</strong> 설계 효과성 결론 및 개선점 도출</li>
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
                                
                                <div class="d-grid">
                                    <button id="startDesignEvalBtn" class="btn btn-success" onclick="startDesignEvaluation()">
                                        <i class="fas fa-play me-1"></i>RCM 설계평가 시작
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
                        <div class="text-center py-4">
                            <i class="fas fa-clock fa-2x text-muted mb-2"></i>
                            <p class="text-muted">아직 수행된 설계평가가 없습니다.</p>
                            <small class="text-muted">설계평가를 시작하면 여기에 결과가 표시됩니다.</small>
                        </div>
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
            fetch('/api/user/rcm-status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('availableRcmCount').textContent = data.total_count || 0;
                        
                        // RCM이 없으면 버튼 비활성화
                        const button = document.getElementById('startDesignEvalBtn');
                        if (data.total_count === 0) {
                            button.disabled = true;
                            button.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>평가 가능한 RCM 없음';
                            button.classList.remove('btn-success');
                            button.classList.add('btn-secondary');
                        }
                    } else {
                        document.getElementById('availableRcmCount').textContent = '0';
                        const button = document.getElementById('startDesignEvalBtn');
                        button.disabled = true;
                        button.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>평가 가능한 RCM 없음';
                        button.classList.remove('btn-success');
                        button.classList.add('btn-secondary');
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
                        showRcmSelectionModal(data.rcms);
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
        function showRcmSelectionModal(rcms) {
            // 기존 모달이 있다면 제거
            const existingModal = document.getElementById('rcmSelectionModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // 모달 HTML 생성
            const modalHtml = `
                <div class="modal fade" id="rcmSelectionModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-clipboard-check me-2"></i>설계평가할 RCM 선택
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
                                                        <button class="btn btn-sm btn-success" onclick="startRcmDesignEval(${rcm.rcm_id}, '${rcm.rcm_name}')">
                                                            <i class="fas fa-play me-1"></i>평가 시작
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
        
        // 특정 RCM의 설계평가 시작
        function startRcmDesignEval(rcmId, rcmName) {
            // 모달 닫기
            const modal = bootstrap.Modal.getInstance(document.getElementById('rcmSelectionModal'));
            modal.hide();
            
            // 설계평가 페이지로 이동
            window.location.href = `/user/design-evaluation/rcm/${rcmId}`;
        }
    </script>
</body>
</html>