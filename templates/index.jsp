<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall</title>
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">

    <!-- 커스텀 툴팁 스타일 -->
    <style>
        .tooltip-inner {
            max-width: 350px;
            text-align: left !important;
            background-color: #2c3e50;
            border-radius: 8px;
            padding: 15px 18px;
            font-size: 14px;
            line-height: 1.5;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .tooltip.bs-tooltip-top .tooltip-arrow::before {
            border-top-color: #2c3e50;
        }

        .tooltip.bs-tooltip-bottom .tooltip-arrow::before {
            border-bottom-color: #2c3e50;
        }

        .tooltip.bs-tooltip-start .tooltip-arrow::before {
            border-left-color: #2c3e50;
        }

        .tooltip.bs-tooltip-end .tooltip-arrow::before {
            border-right-color: #2c3e50;
        }
    </style>
</head>
<body>
    <!-- 히어로 섹션 -->
    <section class="hero-section">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-2">
                    <img src="{{ url_for('static', filename='img/snowball.jpg')}}" alt="SnowBall" class="img-fluid" style="max-height: 80px; width: auto;">
                </div>
                <div class="col-lg-8 hero-content">
                    <h1 class="hero-title">SnowBall System</h1>
                    <p class="hero-subtitle">내부통제 평가와 IT감사 대응을 위한 종합 솔루션</p>
                </div>
                <div class="col-lg-2 text-end">
                    {% if user_name != 'Guest' %}
                        <div class="auth-info">
                            <span class="user-welcome">환영합니다, {{ user_name }}님!</span>
                            {% if session.get('original_admin_id') %}
                                <div class="mt-1">
                                    <small class="text-warning">
                                        <i class="fas fa-user-secret me-1"></i>관리자가 {{ user_name }} 사용자로 스위치 중
                                    </small>
                                </div>
                                <a href="/admin/switch_back" class="btn btn-sm btn-danger ms-2" title="관리자로 돌아가기">
                                    <i class="fas fa-undo me-1"></i>관리자로 돌아가기
                                </a>
                            {% elif user_info and user_info.get('admin_flag') == 'Y' %}
                                <a href="/admin" class="btn btn-sm btn-warning ms-2" title="관리자 메뉴">
                                    <i class="fas fa-user-shield me-1"></i>관리자
                                </a>
                            {% endif %}
                            <a href="{{ url_for('logout') }}" class="btn btn-sm btn-outline-secondary ms-2">로그아웃</a>
                        </div>
                    {% else %}
                        <div class="auth-links">
                            <a href="{{ url_for('login') }}" class="login-button">
                                <i class="fas fa-sign-in-alt"></i>
                                로그인
                            </a>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </section>
    

    <!-- 기능 섹션 -->
    <section id="features" class="py-4">
        <div class="container">
            <h2 class="section-title"><i class="fas fa-globe me-2"></i>Public</h2>
            <div class="row g-4">
                <!-- 기본 4개 카드 -->
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/rcm.jpg')}}" class="feature-img" alt="RCM">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">RCM 생성</h5>
                            <p class="feature-description">회사 정보를 입력하여 맞춤형 위험통제매트릭스(RCM)를 생성합니다.</p>
                            <div class="text-center">
                                <a href="/link1" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• 회사 정보 입력으로 맞춤형 RCM 템플릿 생성<br>• 회사 규모와 업종에 따른 통제 항목 구성<br>• 엑셀 파일로 즉시 다운로드 가능<br>• 이메일 발송으로 편리한 공유</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/interview.jpg')}}" class="feature-img" alt="Interview">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">인터뷰/설계평가</h5>
                            <p class="feature-description">AI와의 대화형 인터뷰를 통해 RCM을 분석하고 통제 설계를 평가합니다.</p>
                            <div class="text-center">
                                <a href="/link2?reset=1" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• AI 기반 대화형 RCM 분석 및 검토<br>• 업로드한 RCM 파일의 통제 설계 평가<br>• 통제 효과성 및 적절성 자동 분석<br>• 개선 방안 및 리포트 자동 생성</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/testing.jpg')}}" class="feature-img" alt="Operation Test">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">운영평가</h5>
                            <p class="feature-description">내부통제의 운영 효과성을 평가하고 실제 운용 상태를 점검합니다.</p>
                            <div class="text-center">
                                <a href="/link3" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• 내부통제의 운영 효과성 평가<br>• 통제 활동의 실제 수행 상태 점검<br>• 운영상 결함 및 예외사항 식별<br>• 개선 방안 및 권고사항 제시</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/video.jpg')}}" class="feature-img" alt="교육자료">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">가이드</h5>
                            <p class="feature-description">ITGC를 포함한 내부통제에 관련된 교육 영상 및 자료를 제공합니다.</p>
                            <div class="text-center">
                                <a href="/link4" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• ITGC(IT일반통제) 교육 영상<br>• 내부통제 기본 개념 및 실무 가이드<br>• 통제 설계 및 평가 방법론<br>• 실무 사례 및 베스트 프랙티스</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 툴팁 안내 메시지 (기본 서비스용) -->
            <div class="row mt-3">
                <div class="col-12">
                </div>
            </div>

            <!-- Private 서비스 -->
            <div class="row g-4 mt-3" id="private-services" {% if not is_logged_in %}style="opacity: 0.4;"{% endif %}>
                <div class="col-12">
                    <h2 class="section-title"><i class="fas fa-lock me-2"></i>Private</h2>
                    {% if not is_logged_in %}
                    <div class="alert alert-info text-center" style="opacity: 1; pointer-events: auto; position: relative; z-index: 10;">
                        <i class="fas fa-lock me-2"></i>
                        Private 서비스를 이용하시려면 <a href="/login" class="alert-link">로그인</a>이 필요합니다.
                    </div>
                    {% endif %}
                </div>
                
                <!-- RCM 조회 -->
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card border-primary h-100">
                        <img src="{{ url_for('static', filename='img/rcm_inquiry.jpg')}}" class="feature-img" alt="RCM 조회/평가" 
                             onerror="this.src='{{ url_for('static', filename='img/testing.jpg')}}'">
                        <div class="card-body p-4 d-flex flex-column">
                            <h5 class="feature-title text-center">RCM 조회/평가</h5>
                            <p class="feature-description">귀하에게 할당된 RCM 데이터를 조회하고 AI를 활용한 통제항목 검토를 수행할 수 있습니다.</p>
                            
                            <div class="text-center mt-auto">
                                <a href="/user/rcm" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• 위험통제매트릭스(RCM) 데이터 조회<br>• AI 기반 자동 검토 및 효과성 분석<br>• 내부통제 전문가 도움 없이도 신속·정확 검토<br>• 통제항목별 상세 리포트 제공</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 설계평가 -->
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card border-success h-100">
                        <img src="{{ url_for('static', filename='img/design_review.jpg')}}" class="feature-img" alt="설계평가" 
                             onerror="this.src='{{ url_for('static', filename='img/testing.jpg')}}'">
                        <div class="card-body p-4 d-flex flex-column">
                            <h5 class="feature-title text-center">설계평가</h5>
                            <p class="feature-description">통제가 효과적으로 설계되었는지를 평가하는 과정입니다.</p>
                            <div class="text-center mt-auto">
                                <a href="/user/design-evaluation" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• 통제의 이론적 효과성 평가<br>• 설명 적절성 및 전반적 효과성 검토<br>• 개선사항 및 권고사항 도출<br>• 평가 결과 엑셀 다운로드 지원</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 운영평가 -->
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card border-warning h-100">
                        <img src="{{ url_for('static', filename='img/operational_review.jpg')}}" class="feature-img" alt="운영평가" 
                             onerror="this.src='{{ url_for('static', filename='img/testing.jpg')}}'">
                        <div class="card-body p-4 d-flex flex-column">
                            <h5 class="feature-title text-center">운영평가</h5>
                            <p class="feature-description">통제가 실제로 의도된 대로 작동하고 있는지를 평가하는 과정입니다.</p>
                            <div class="text-center mt-auto">
                                <a href="/user/operation-evaluation" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• 통제의 실제 운영 효과성 평가<br>• 통제 수행 증거 업로드 및 검증<br>• 실제 운영 상황에서의 효과성 검증<br>• 증거 및 결과 엑셀 다운로드</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 내부평가 -->
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card border-danger h-100">
                        <img src="{{ url_for('static', filename='img/internal_assessment.jpg')}}" class="feature-img" alt="내부평가"
                             onerror="this.src='{{ url_for('static', filename='img/testing.jpg')}}'">
                        <div class="card-body p-4 d-flex flex-column">
                            <h5 class="feature-title text-center">내부평가</h5>
                            <p class="feature-description">RCM평가부터 운영평가까지 전체 프로세스를 순차적으로 진행하는 통합 워크플로우입니다.</p>
                            <div class="text-center mt-auto">
                                <a href="/user/internal-assessment" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• RCM 평가 → 설계평가 → 운영평가 순차 진행<br>• 전체 내부통제 평가 프로세스 관리<br>• 단계별 진행상황 추적 및 관리<br>• 통합 평가 결과 리포트 생성</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <!-- Contact Us (로그인 불필요) -->
            <div class="row g-4 mt-3">
                <div class="col-12">
                    <h2 class="section-title"><i class="fas fa-envelope me-2"></i>Support</h2>
                </div>
                <div class="col-lg-3 col-md-6 mx-auto">
                    <div class="feature-card border-info h-100">
                        <img src="{{ url_for('static', filename='img/contact_us.jpg')}}" class="feature-img" alt="Contact Us"
                             onerror="this.src='{{ url_for('static', filename='img/testing.jpg')}}'">
                        <div class="card-body p-4 d-flex flex-column">
                            <h5 class="feature-title text-center">서비스 문의</h5>
                            <p class="feature-description">문의사항이나 지원이 필요하시면 언제든지 연락주세요.</p>
                            <div class="text-center mt-auto">
                                <a href="/contact" class="feature-link"
                                   data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true"
                                   title="<div>• 내부통제 시스템 사용 문의<br>• 기술적 지원 및 전문 상담<br>• 최적의 솔루션 제안<br>• 24/7 고객 지원 서비스</div>">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 툴팁 안내 메시지 (비로그인 상태에서만 표시) -->
            {% if not is_logged_in %}
            <div class="row mt-4">
                <div class="col-12">
                    <div class="text-center">
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            각 서비스의 <strong>"자세히 보기"</strong> 버튼에 마우스를 올리시면 상세 설명을 확인하실 수 있습니다.
                        </small>
                    </div>
                </div>
            </div>
            {% endif %}

        </div>
    </section>

    <!-- Contact Us 바로가기 -->
    <section class="py-2" style="display: none;">
        <div class="container text-center">
            <a href="/contact" class="btn btn-outline-primary btn-lg">
                <i class="fas fa-envelope me-1"></i>Contact Us
            </a>
        </div>
    </section>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- 세션 관리 및 RCM 기능 -->
    <script>
        window.isLoggedIn = {{ 'true' if is_logged_in else 'false' }};

        // 툴팁 초기화
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    delay: { show: 500, hide: 100 },
                    container: 'body'
                });
            });
        });
        
        
        // 빠른 접근 모달 표시
        function showQuickAccess() {
            if (window.isLoggedIn) {
                fetch('/api/user/rcm-list')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.rcms.length > 0) {
                            showQuickAccessModal(data.rcms);
                        } else {
                            alert('접근 가능한 RCM이 없습니다.');
                        }
                    })
                    .catch(error => {
                        console.error('RCM 목록 로드 오류:', error);
                        alert('RCM 목록을 불러오는 중 오류가 발생했습니다.');
                    });
            } else {
                alert('로그인이 필요합니다.');
            }
        }
        
        // 빠른 접근 모달 생성 및 표시
        function showQuickAccessModal(rcms) {
            // 기존 모달이 있다면 제거
            const existingModal = document.getElementById('quickAccessModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // 모달 HTML 생성
            const modalHtml = `
                <div class="modal fade" id="quickAccessModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-bolt me-2"></i>RCM 빠른 접근
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row g-3">
                                    ${rcms.map(rcm => `
                                        <div class="col-md-6">
                                            <div class="card border-primary">
                                                <div class="card-body">
                                                    <h6 class="card-title">${rcm.rcm_name}</h6>
                                                    <p class="card-text small">${rcm.company_name}</p>
                                                    <div class="d-flex justify-content-between align-items-center">
                                                        <span class="badge bg-${rcm.permission_type === 'admin' ? 'danger' : 'success'}">
                                                            ${rcm.permission_type === 'admin' ? '관리자' : '읽기'}
                                                        </span>
                                                        <a href="/user/rcm/${rcm.rcm_id}/view" class="btn btn-sm btn-primary">
                                                            <i class="fas fa-eye me-1"></i>보기
                                                        </a>
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
            const modal = new bootstrap.Modal(document.getElementById('quickAccessModal'));
            modal.show();
        }
        
    </script>
    <!-- <script src="{{ url_for('static', filename='js/session-manager.js') }}"></script> -->
    
</body>
</html>