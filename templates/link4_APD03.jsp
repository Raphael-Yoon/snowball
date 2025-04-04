<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall - Access Program & Data</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container mt-3">
        <!-- 이미지 섹션 -->
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Application 권한 승인</h5>
                <p class="card-text">신규 권한 요청서에 대한 승인 절차를 진행합니다.</p>
            </div>
            <img src="{{ url_for('static', filename='img/APD03.jpg')}}" class="card-img" alt="Access Program & Data">
        </div>

        <!-- 유튜브 섹션 -->
        <div class="card">
            <div class="card-body">
                <h5 class="card-title mb-3">교육 영상</h5>
                <div class="ratio ratio-16x9">
                    <iframe src="https://www.youtube.com/embed/EdbB7ymq5Ic?si=fbqej2uATkJxYBh6?autoplay=1&mute=1" 
                            title="Access Program & Data 교육 영상" 
                            allowfullscreen></iframe>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>