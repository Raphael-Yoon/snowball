<!DOCTYPE html>
<html>
<head>
    <!-- Bootstrap CSS 불러오기 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
          integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
    <title>SnowBall Quiz</title>
</head>
<body>
    <!-- 네비게이션 포함 -->
    {% include 'navi.jsp' %}

    <div class="container mt-5">
        <h1>IT 시스템</h1>

        <!-- 퀴즈 폼 시작 -->
        <form action="/link2" method="post">
            <div class="mb-3">
                <label>{{ question_number }}. {{ question }}</label><br>
                {% if question_number == 0 %}
                    <input type="text" name="a0" required><br>
                <!-- ✅ question_number가 1이면 특정 라디오 버튼 표시 -->
                {% elif question_number == 1 %}
                    <input type="radio" name="a1" value="Y" required> 예 (상용 소프트웨어)<br>
                    <input type="radio" name="a1" value="N"> 아니요 (자체개발 소스트웨어)<br>
				{% elif question_number == 2 %}
                    <input type="radio" name="a2" value="Y" required> 예 (수정 가능)<br>
                    <input type="radio" name="a2" value="N"> 아니요 (수정 불가능)<br>
				{% elif question_number == 3 %}
                    <input type="radio" name="a3" value="Y" required> 예(Cloud 사용)<br>
                    <input type="radio" name="a3" value="N"> 아니요 (Cloud 미사용)<br>
				{% elif question_number == 4 %}
                    <input type="radio" name="a4" value="Y" required> SaaS(SAP, Oracle 등)<br>
                    <input type="radio" name="a4" value="N"> IaaS(AWS, Azure 등)<br>
				{% elif question_number == 5 %}
                    <input type="radio" name="a5" value="Y" required> 예 (발행)<br>
                    <input type="radio" name="a5" value="N"> 아니요 (미발행)<br>
				{% elif question_number == 6 %}
                    <input type="radio" name="a6" value="Y" required> 예 (사용)<br>
                    <input type="radio" name="a6" value="N"> 아니요 (미사용)<br>
                {% elif question_number == 7 %}
                    <input type="radio" name="a7" value="Y" required> 예 (사용)<br>
                    <input type="radio" name="a7" value="N"> 아니요 (미사용)<br>
                {% elif question_number == 8 %}
                    <input type="radio" name="a8" value="Y" required> 예 (사용)<br>
                    <input type="radio" name="a8" value="N"> 아니요 (미사용)<br>
                {% else %}
                    <input type="radio" name="answer" value="Y" required> 예<br>
                    <input type="radio" name="answer" value="N"> 아니요
                {% endif %}
            </div>

            <!-- 다음 버튼 -->
            <button type="submit" class="btn btn-primary">다음</button>
        </form>
    </div>
</body>
</html>
