<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
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
                            {% elif user_info and user_info.admin_flag == 'Y' %}
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
            <h2 class="section-title">주요 기능</h2>
            <div class="row g-4">
                <!-- 기본 4개 카드 -->
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/rcm.jpg')}}" class="feature-img" alt="RCM">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">RCM</h5>
                            <p class="feature-description">신뢰성 중심 유지보수 시스템으로 장비의 안정성과 효율성을 최적화합니다.</p>
                            <div class="text-center">
                                <a href="/link1" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/interview.jpg')}}" class="feature-img" alt="Interview">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">Interview</h5>
                            <p class="feature-description">전문가와의 인터뷰를 통해 시스템의 현재 상태와 개선점을 파악합니다.</p>
                            <div class="text-center">
                                <a href="/link2?reset=1" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/testing.jpg')}}" class="feature-img" alt="Operation Test">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">Operation Test</h5>
                            <p class="feature-description">운영 테스트를 통해 시스템의 실제 운용 상태를 점검합니다.</p>
                            <div class="text-center">
                                <a href="/link3" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/video.jpg')}}" class="feature-img" alt="교육자료">
                        <div class="card-body p-4">
                            <h5 class="feature-title text-center">영상자료</h5>
                            <p class="feature-description">시스템 운영과 관리에 필요한 영상 자료를 제공합니다.</p>
                            <div class="text-center">
                                <a href="/link4" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
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
    
    <!-- 세션 관리 -->
    <script>
        window.isLoggedIn = {{ 'true' if is_logged_in else 'false' }};
    </script>
    <script src="{{ url_for('static', filename='js/session-manager.js') }}"></script>
    
</body>
</html>