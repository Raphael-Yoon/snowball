<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall - 배치잡 스케줄 Monotoring</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container mt-3">
        <!-- 이미지 섹션 -->
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">배치잡 스케줄 Monotoring</h5>
                <p class="card-text">배치잡 스케줄 실행 상태를 모니터링하고 오류를 처리합니다.</p>
            </div>
            <img src="{{ url_for('static', filename='img/CO03.jpg')}}" class="card-img" alt="배치잡 스케줄 Monotoring">
        </div>

        <!-- 유튜브 섹션 -->
        <div class="card">
            <div class="card-body">
                <h5 class="card-title mb-3">교육 영상</h5>
                <div class="ratio ratio-16x9">
                    <iframe src="https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal?autoplay=1&mute=1" 
                            title="배치잡 스케줄 Monotoring 교육 영상" 
                            allowfullscreen></iframe>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html> 