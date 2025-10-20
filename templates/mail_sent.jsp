<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>메일 전송 완료</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container text-center mt-5">
        <h1>메일이 성공적으로 전송되었습니다.</h1>
        <p>입력하신 이메일: <strong>{{ user_email }}</strong></p>
        <a href="/" class="btn btn-primary mt-3">메인으로 이동</a>
    </div>
</body>
</html> 