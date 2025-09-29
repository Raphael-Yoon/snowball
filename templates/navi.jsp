<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall Navigation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="{{ url_for('static', filename='img/logo.jpg')}}" class="logo" alt="SnowBall Logo" style="max-height: 40px; width: auto;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a href="/link1" class="nav-link">
                            <i class="fas fa-clipboard-list me-1"></i>RCM 생성
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/link2?reset=1" class="nav-link">
                            <i class="fas fa-user-tie me-1"></i>인터뷰/설계평가
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/link3" class="nav-link">
                            <i class="fas fa-cogs me-1"></i>운영평가
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/link4" class="nav-link">
                            <i class="fas fa-film me-1"></i>가이드
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('link9.contact') }}" class="nav-link">
                            <i class="fas fa-envelope me-1"></i>Contact Us
                        </a>
                    </li>
                    {% if is_logged_in %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="premiumServicesDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-lock me-1"></i>Private
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="premiumServicesDropdown">
                            <li><a class="dropdown-item" href="{{ url_for('link5.user_rcm') }}">
                                <i class="fas fa-database me-2"></i>RCM 조회/평가
                            </a></li>
                            <li><a class="dropdown-item" href="{{ url_for('link6.user_design_evaluation') }}">
                                <i class="fas fa-clipboard-check me-2"></i>설계평가
                            </a></li>
                            <li><a class="dropdown-item" href="{{ url_for('link7.user_operation_evaluation') }}">
                                <i class="fas fa-cogs me-2"></i>운영평가
                            </a></li>
                            <li><a class="dropdown-item" href="{{ url_for('link8.internal_assessment') }}">
                                <i class="fas fa-tasks me-2"></i>내부평가
                            </a></li>
                        </ul>
                    </li>
                    {% if user_info and user_info.get('admin_flag') == 'Y' %}
                    <li class="nav-item">
                        <a href="/admin" class="nav-link">
                            <i class="fas fa-user-shield me-1"></i>Admin
                        </a>
                    </li>
                    {% endif %}
                    {% endif %}
                </ul>
                
                <ul class="navbar-nav">
                    {% if is_logged_in %}
                    {% if session.get('original_admin_id') %}
                    <li class="nav-item">
                        <a href="/admin/switch_back" class="nav-link text-danger" title="관리자로 돌아가기">
                            <i class="fas fa-undo me-1"></i>관리자로 돌아가기
                        </a>
                    </li>
                    {% endif %}
                    <li class="nav-item">
                        <span class="navbar-text company-info">
                            <i class="fas fa-building me-1"></i>{{ user_info.company_name if user_info.company_name else '회사명 미등록' }}
                        </span>
                    </li>
                    <li class="nav-item">
                        <a href="/logout" class="nav-link logout-link">
                            <i class="fas fa-sign-out-alt me-1"></i>로그아웃
                        </a>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a href="/login" class="nav-link login-nav-button">
                            <i class="fas fa-sign-in-alt me-1"></i>로그인
                        </a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 드롭다운 수동 구현
        document.addEventListener('DOMContentLoaded', function() {
            const dropdownToggle = document.getElementById('premiumServicesDropdown');
            const dropdownMenu = dropdownToggle ? dropdownToggle.nextElementSibling : null;
            
            if (dropdownToggle && dropdownMenu) {
                dropdownToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    dropdownMenu.classList.toggle('show');
                });
                
                // 다른 곳 클릭시 드롭다운 닫기
                document.addEventListener('click', function(e) {
                    if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                        dropdownMenu.classList.remove('show');
                    }
                });
            }
        });
    </script>
    
</body>
</html>