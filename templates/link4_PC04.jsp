<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall - 이관담당자 권한 제한</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container mt-3">
        <!-- 이미지 섹션 -->
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">이관담당자 권한 제한</h5>
                <p class="card-text">이관담당자는 개발업무를 수행하지 않은 별도의 인원으로 제한합니다.</p>
            </div>
            <img src="{{ url_for('static', filename='img/PC04.jpg')}}" class="card-img" alt="이관담당자 권한 제한">
        </div>

        <!-- 유튜브 섹션 -->
        <div class="card">
            <div class="card-body">
                <h5 class="card-title mb-3">교육 영상</h5>
                <div class="ratio ratio-16x9">
                    <iframe src="https://www.youtube.com/embed/dzSoIaQTxmQ?si=B-m43fe5W-oEIWal?autoplay=1&mute=1" 
                            title="이관담당자 권한 제한 교육 영상" 
                            allowfullscreen></iframe>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>