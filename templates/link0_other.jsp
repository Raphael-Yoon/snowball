<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    <div class="container text-center" >
        <div class="row">
            <div class="col">
                <div class="card" style="width: 30rem;">
                    <a href="/link2"><img src="{{ url_for('static', filename='img/pwc.jpg')}}" class="card-img-top" alt="..."></a>
                    <div class="card-body">
                        <h5 class="card-title">설계평가</h5>
                    </div>
                </div>
            </div>
            <!-- 운영평가 카드 임시 숨김
            <div class="col">
                <div class="card" style="width: 30rem;">
                    <a href="/link3"><img src="{{ url_for('static', filename='img/nepes.jpg')}}" class="card-img-top" alt="..."></a>
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