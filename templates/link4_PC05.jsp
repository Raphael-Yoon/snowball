<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall - 개발/운영 환경 분리</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container mt-3">
        <!-- 이미지 섹션 -->
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">개발/운영 환경 분리</h5>
                <p class="card-text">개발/운영 환경을 분리하여 개발 환경에서 발생한 문제가 운영 환경에 영향을 주지 않도록 합니다.</p>
            </div>
            <img src="{{ url_for('static', filename='img/PC05.jpg')}}" class="card-img" alt="PC 백업 및 복구">
        </div>

        <!-- 유튜브 섹션 -->
        <div class="card">
            <div class="card-body">
                <h5 class="card-title mb-3">교육 영상</h5>
                <div class="ratio ratio-16x9">
                    <iframe src="https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal?autoplay=1&mute=1" 
                            title="개발/운영 환경 분리 교육 영상" 
                            allowfullscreen></iframe>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>