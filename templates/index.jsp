<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall</title>
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --text-color: #333;
            --light-bg: #f8f9fa;
        }

        body {
            background: var(--light-bg);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .header {
            background: var(--primary-color);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }

        .header-title {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .header-subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .section-title {
            color: var(--primary-color);
            margin: 2rem 0;
            font-weight: 600;
            text-align: center;
            font-size: 1.5rem;
        }

        .card {
            border: none;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card-img-top {
            height: 200px;
            object-fit: cover;
        }

        .card-body {
            padding: 1.5rem;
        }

        .card-icon {
            font-size: 1.5rem;
            color: var(--secondary-color);
            margin-bottom: 1rem;
        }

        .card-title {
            color: var(--primary-color);
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }

        .card-description {
            color: #666;
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 1rem;
        }

        .card-link {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: var(--secondary-color);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9rem;
            transition: background-color 0.2s ease;
        }

        .card-link:hover {
            background: var(--primary-color);
            color: white;
        }

        .container {
            padding: 1rem;
        }

        @media (max-width: 768px) {
            .header {
                padding: 1.5rem 0;
            }
            .header-title {
                font-size: 1.5rem;
            }
            .header-subtitle {
                font-size: 1rem;
            }
            .card-img-top {
                height: 160px;
            }
            .card-body {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1 class="header-title">SnowBall System</h1>
            <p class="header-subtitle">내부통제 평가와 IT감사 대응을 위한 솔루션</p>
        </div>
    </div>

    <div class="container">
        <h2 class="section-title">주요 기능</h2>
        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <img src="{{ url_for('static', filename='img/rcm.jpg')}}" class="card-img-top" alt="RCM">
                    <div class="card-body">
                        <div class="card-icon">
                            <i class="fas fa-clipboard-list"></i>
                        </div>
                        <h5 class="card-title">RCM</h5>
                        <p class="card-description">신뢰성 중심 유지보수 시스템으로 장비의 안정성과 효율성을 최적화합니다.</p>
                        <a href="/link1" class="card-link">자세히 보기</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <img src="{{ url_for('static', filename='img/interview.jpg')}}" class="card-img-top" alt="Interview">
                    <div class="card-body">
                        <div class="card-icon">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <h5 class="card-title">Interview</h5>
                        <p class="card-description">전문가와의 인터뷰를 통해 시스템의 현재 상태와 개선점을 파악합니다.</p>
                        <a href="/link2" class="card-link">자세히 보기</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <img src="{{ url_for('static', filename='img/education.jpg')}}" class="card-img-top" alt="교육자료">
                    <div class="card-body">
                        <div class="card-icon">
                            <i class="fas fa-book"></i>
                        </div>
                        <h5 class="card-title">교육자료</h5>
                        <p class="card-description">시스템 운영과 관리에 필요한 교육 자료를 제공합니다.</p>
                        <a href="/link4" class="card-link">자세히 보기</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>