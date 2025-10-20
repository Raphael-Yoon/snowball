<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
</head>
<body>
    
    <div class="container text-center" >
        <div class="row">
            <div class="col">
                <div class="card" style="width: 20rem;">
                    <a href="/link1"><img src="{{ url_for('static', filename='img/rcm.jpg')}}" class="rounded" alt="..."></a>
                    <div class="card-body">
                        <h5 class="card-title">RCM</h5>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 20rem;">
                    <a href="/link2"><img src="{{ url_for('static', filename='img/design.jpg')}}" class="rounded" alt="..."></a>
                    <div class="card-body">
                        <h5 class="card-title">설계평가</h5>
                    </div>
                </div>
            </div>
            <!-- 운영평가 카드 임시 숨김
            <div class="col">
                <div class="card" style="width: 20rem;">
                    <a href="/link3"><img src="{{ url_for('static', filename='img/operation.jpg')}}" class="rounded" alt="..."></a>
                    <div class="card-body">
                        <h5 class="card-title">운영평가</h5>
                    </div>
                </div>
            </div>
            -->
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    </body>
</html>