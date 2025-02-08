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

                <!-- ✅ question_number가 1이면 특정 라디오 버튼 표시 -->
                {% if question_number == 1 %}
                    <input type="radio" name="s_q1" value="q1_1" required> SAP ERP<br>
                    <input type="radio" name="s_q1" value="q1_2"> Oracle ERP<br>
                    <input type="radio" name="s_q1" value="q1_3"> 더존 ERP<br>
                    <input type="radio" name="s_q1" value="q1_4"> 영림원 ERP<br>
                    <input type="radio" name="s_q1" value="q1_5"> 기타<br>
					<input type="radio" name="s_q1" value="q1_5"> 자체개발<br>
				{% elif question_number == 2 %}
                    <input type="radio" name="s_q2" value="q2_1" required> Unix<br>
                    <input type="radio" name="s_q2" value="q2_2"> Windows<br>
                    <input type="radio" name="s_q2" value="q2_3"> Linux<br>
                    <input type="radio" name="s_q2" value="q2_4"> 기타<br>
				{% elif question_number == 3 %}
                    <input type="radio" name="s_q3" value="q3_1" required> Oracle<br>
                    <input type="radio" name="s_q3" value="q3_2"> HANA<br>
                    <input type="radio" name="s_q3" value="q3_3"> MS-SQL<br>
                    <input type="radio" name="s_q3" value="q3_4"> 기타<br>
				{% elif question_number == 4 %}
                    <input type="radio" name="s_q4" value="q4_1" required> O<br>
                    <input type="radio" name="s_q4" value="q4_2"> X<br>
				{% elif question_number == 5 %}
                    <input type="radio" name="s_q5" value="q5_1" required> O<br>
                    <input type="radio" name="s_q5" value="q5_2"> X<br>
				{% elif question_number == 6 %}
                    <input type="radio" name="s_q6" value="q6_1" required> O<br>
                    <input type="radio" name="s_q6" value="q6_2"> X<br>
                {% else %}
                    <input type="radio" name="answer" value="O" required> O<br>
                    <input type="radio" name="answer" value="X"> X
                {% endif %}
            </div>

            <!-- 다음 버튼 -->
            <button type="submit" class="btn btn-primary">다음</button>
        </form>
    </div>
</body>
</html>
