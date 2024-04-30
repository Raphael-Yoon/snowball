<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Homepage</title>
</head>
<body>
    {% include 'navi.jsp' %}
    <p><center>Monitoring 준비중...</center></p>
    <div style="text-align: center;">
        <img src="{{ url_for('static', filename='img/boot.jpg')}}" width="500" alt="None">
    </div>
</body>
</html>