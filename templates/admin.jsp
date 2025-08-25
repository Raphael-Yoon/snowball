<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall 관리자</title>
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
                <h1><i class="fas fa-user-shield me-2"></i>관리자 대시보드</h1>
                <hr>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-3x text-primary mb-3"></i>
                        <h5 class="card-title">사용자 관리</h5>
                        <p class="card-text">시스템 사용자 계정을 관리합니다.</p>
                        <a href="/admin/users" class="btn btn-primary">
                            <i class="fas fa-arrow-right me-1"></i>사용자 관리
                        </a>
                    </div>
                </div>
            </div>

            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-cogs fa-3x text-secondary mb-3"></i>
                        <h5 class="card-title">시스템 설정</h5>
                        <p class="card-text">시스템 전반적인 설정을 관리합니다.</p>
                        <button class="btn btn-secondary" disabled>
                            <i class="fas fa-wrench me-1"></i>준비중
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-bar fa-3x text-success mb-3"></i>
                        <h5 class="card-title">활동 로그</h5>
                        <p class="card-text">사용자 활동 로그를 조회합니다.</p>
                        <a href="/admin/logs" class="btn btn-success">
                            <i class="fas fa-list me-1"></i>로그 조회
                        </a>
                    </div>
                </div>
            </div>

            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-database fa-3x text-warning mb-3"></i>
                        <h5 class="card-title">데이터베이스 관리</h5>
                        <p class="card-text">데이터베이스 백업 및 유지보수를 수행합니다.</p>
                        <button class="btn btn-warning" disabled>
                            <i class="fas fa-database me-1"></i>준비중
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>안내:</strong> 관리자 권한으로 로그인하셨습니다. 시스템 관리 기능을 신중하게 사용해주세요.
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>