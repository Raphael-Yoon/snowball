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
    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="{{ url_for('static', filename='img/logo.jpg')}}" class="logo" alt="SnowBall Logo" style="max-height: 40px; width: auto;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if is_logged_in %}
                    <!-- 로그인 상태: 주요 메뉴 직접 표시 -->
                    <li class="nav-item">
                        <a href="{{ url_for('link8.internal_assessment') }}" class="nav-link">
                            <i class="fas fa-chart-pie me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('link5.user_rcm') }}" class="nav-link">
                            <i class="fas fa-database me-1"></i>RCM
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('link6.elc_design_evaluation') }}" class="nav-link">
                            <i class="fas fa-building me-1"></i>ELC 평가
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('link6.tlc_evaluation') }}" class="nav-link">
                            <i class="fas fa-exchange-alt me-1"></i>TLC 평가
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('link6.itgc_evaluation') }}" class="nav-link">
                            <i class="fas fa-server me-1"></i>ITGC 평가
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="javascript:void(0);" id="publicMenuDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="fas fa-globe me-1"></i>Public
                        </a>
                        <ul class="dropdown-menu" aria-labelledby="publicMenuDropdown">
                            <li><a class="dropdown-item" href="/link1">
                                <i class="fas fa-clipboard-list me-2"></i>RCM 생성
                            </a></li>
                            <li><a class="dropdown-item" href="/link2?reset=1">
                                <i class="fas fa-user-tie me-2"></i>인터뷰/설계평가
                            </a></li>
                            <li><a class="dropdown-item" href="/link3">
                                <i class="fas fa-cogs me-2"></i>운영평가 가이드
                            </a></li>
                            <li><a class="dropdown-item" href="/link4">
                                <i class="fas fa-film me-2"></i>영상 가이드
                            </a></li>
                            <li><a class="dropdown-item" href="{{ url_for('link9.contact') }}">
                                <i class="fas fa-envelope me-2"></i>서비스 문의
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
                    {% else %}
                    <!-- 비로그인 상태: Public 메뉴 표시 -->
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
                            <i class="fas fa-cogs me-1"></i>운영평가 가이드
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/link4" class="nav-link">
                            <i class="fas fa-film me-1"></i>영상 가이드
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('link9.contact') }}" class="nav-link">
                            <i class="fas fa-envelope me-1"></i>서비스 문의
                        </a>
                    </li>
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
                        {% if user_info and user_info.get('admin_flag') == 'Y' %}
                        <a href="#" class="nav-link company-info" onclick="showUserSwitchModal(); return false;" style="cursor: pointer;" title="사용자 전환">
                            <i class="fas fa-user-cog me-1"></i>{{ user_info.company_name if user_info.company_name else '회사명 미등록' }}
                        </a>
                        {% else %}
                        <span class="navbar-text company-info">
                            <i class="fas fa-building me-1"></i>{{ user_info.company_name if user_info.company_name else '회사명 미등록' }}
                        </span>
                        {% endif %}
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

    <script>
        // 사용자 전환 모달 표시
        function showUserSwitchModal() {
            fetch('/admin/api/admin/users')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.users.length > 0) {
                        const modalHtml = `
                            <div class="modal fade" id="userSwitchModal" tabindex="-1">
                                <div class="modal-dialog modal-lg">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title">
                                                <i class="fas fa-user-cog me-2"></i>사용자 전환
                                            </h5>
                                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                        </div>
                                        <div class="modal-body">
                                            <p class="text-muted mb-3">전환할 사용자를 선택하세요.</p>
                                            <div class="list-group">
                                                ${data.users.map(user => `
                                                    <a href="#" class="list-group-item list-group-item-action" onclick="switchToUser(${user.user_id}, '${user.company_name}'); return false;">
                                                        <div class="d-flex w-100 justify-content-between align-items-center">
                                                            <div>
                                                                <h6 class="mb-1">${user.company_name}</h6>
                                                                <small class="text-muted">${user.user_email}</small>
                                                            </div>
                                                            <div>
                                                                ${user.admin_flag === 'Y' ? '<span class="badge bg-danger">관리자</span>' : '<span class="badge bg-secondary">일반</span>'}
                                                            </div>
                                                        </div>
                                                    </a>
                                                `).join('')}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;

                        // 기존 모달 제거
                        const existingModal = document.getElementById('userSwitchModal');
                        if (existingModal) {
                            existingModal.remove();
                        }

                        document.body.insertAdjacentHTML('beforeend', modalHtml);
                        const modal = new bootstrap.Modal(document.getElementById('userSwitchModal'));
                        modal.show();

                        // 모달이 닫힐 때 DOM에서 제거
                        modal._element.addEventListener('hidden.bs.modal', function () {
                            this.remove();
                        });
                    } else {
                        alert('사용자 목록을 불러올 수 없습니다.');
                    }
                })
                .catch(error => {
                    console.error('사용자 목록 로드 오류:', error);
                    alert('사용자 목록을 불러오는 중 오류가 발생했습니다.');
                });
        }

        // 사용자로 전환
        function switchToUser(userId, companyName) {
            if (!confirm(`"${companyName}" 계정으로 전환하시겠습니까?`)) {
                return;
            }

            fetch('/admin/api/admin/switch-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 모달 닫기
                    const modal = bootstrap.Modal.getInstance(document.getElementById('userSwitchModal'));
                    if (modal) {
                        modal.hide();
                    }
                    // 페이지 새로고침
                    window.location.reload();
                } else {
                    alert('사용자 전환에 실패했습니다: ' + data.message);
                }
            })
            .catch(error => {
                console.error('사용자 전환 오류:', error);
                alert('사용자 전환 중 오류가 발생했습니다.');
            });
        }
    </script>

</body>
</html>