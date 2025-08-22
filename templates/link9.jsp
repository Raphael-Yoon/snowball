<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <title>snowball</title>
</head>
<body>
    {% include 'navi.jsp' %}
    <p><center>준비중...</center></p>
    <div style="text-align: center;">
        <img src="{{ url_for('static', filename='img/boot.jpg')}}" width="500" alt="None">
    </div>
</body>
</html>