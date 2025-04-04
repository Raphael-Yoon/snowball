<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall</title>
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("{{ url_for('static', filename='img/pattern.png')}}") repeat;
            opacity: 0.1;
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .hero-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin-bottom: 0;
        }
        
        .feature-card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            overflow: hidden;
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .feature-img {
            height: 150px;
            object-fit: cover;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            color: #3498db;
            margin-bottom: 20px;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .feature-description {
            color: #666;
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .feature-link {
            display: inline-block;
            padding: 10px 25px;
            background-color: #3498db;
            color: white;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 500;
            transition: background-color 0.3s ease;
        }
        
        .feature-link:hover {
            background-color: #2980b9;
            color: white;
        }
        
        .section-title {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
            padding-bottom: 15px;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, #3498db, #2c3e50);
            border-radius: 2px;
        }
        
        .login-section {
            background-color: #f8f9fa;
            padding: 60px 0;
            margin-top: 60px;
        }
        
        .login-form {
            max-width: 400px;
            margin: 0 auto;
            padding: 30px;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        }
        
        .login-title {
            text-align: center;
            margin-bottom: 30px;
            color: #2c3e50;
        }
        
        .form-control {
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        .btn-login {
            background: linear-gradient(90deg, #3498db, #2c3e50);
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: 500;
            width: 100%;
        }
        
        .btn-login:hover {
            background: linear-gradient(90deg, #2980b9, #1a252f);
        }
        
        .register-link {
            text-align: center;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .hero-title {
                font-size: 1.8rem;
            }
            
            .hero-subtitle {
                font-size: 0.9rem;
            }
            
            .hero-section {
                padding: 15px 0;
            }
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
                <div class="col-lg-10 hero-content">
                    <h1 class="hero-title" style="font-size: 1.8rem;">SnowBall System</h1>
                    <p class="hero-subtitle" style="font-size: 0.9rem;">내부통제 평가와 IT감사 대응을 위한 종합 솔루션</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 기능 섹션 -->
    <section id="features" class="py-4">
        <div class="container">
            <h2 class="section-title">주요 기능</h2>
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/rcm.jpg')}}" class="feature-img" alt="RCM">
                        <div class="card-body p-4">
                            <div class="feature-icon text-center">
                                <i class="fas fa-clipboard-list"></i>
                            </div>
                            <h5 class="feature-title text-center">RCM</h5>
                            <p class="feature-description">신뢰성 중심 유지보수 시스템으로 장비의 안정성과 효율성을 최적화합니다.</p>
                            <div class="text-center">
                                <a href="/link1" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/interview.jpg')}}" class="feature-img" alt="Interview">
                        <div class="card-body p-4">
                            <div class="feature-icon text-center">
                                <i class="fas fa-user-tie"></i>
                            </div>
                            <h5 class="feature-title text-center">Interview</h5>
                            <p class="feature-description">전문가와의 인터뷰를 통해 시스템의 현재 상태와 개선점을 파악합니다.</p>
                            <div class="text-center">
                                <a href="/link2" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <img src="{{ url_for('static', filename='img/education.jpg')}}" class="feature-img" alt="교육자료">
                        <div class="card-body p-4">
                            <div class="feature-icon text-center">
                                <i class="fas fa-book"></i>
                            </div>
                            <h5 class="feature-title text-center">교육자료</h5>
                            <p class="feature-description">시스템 운영과 관리에 필요한 교육 자료를 제공합니다.</p>
                            <div class="text-center">
                                <a href="/link4" class="feature-link">자세히 보기</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>