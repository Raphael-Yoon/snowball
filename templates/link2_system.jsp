<!DOCTYPE html>
<html>
<head>
    <!-- Bootstrap CSS 불러오기 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
          integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
    <title>SnowBall Interview</title>
</head>
<body>
    <!-- 네비게이션 포함 -->
    {% include 'navi.jsp' %}

    <div class="container mt-5">
        <h1>
            {% if 0 <= question_number <= 8 %}
                IT 시스템
            {% elif 9 <= question_number <= 26 %}
                APD(Access to Program & Data)
            {% elif 27 <= question_number <= 32 %}
                PC(Program Change)
            {% elif 33 <= question_number <= 39 %}
                CO(Computer Operation)
            {% else %}
                기타
            {% endif %}
        </h1>

        <!-- 퀴즈 폼 시작 -->
        <form action="/link2" method="post">
            <div class="mb-3">
                <label>
                    {% if question_number == 0 %}
                        {{ question }}
                    {% else %}
                        {{ question_number }}. {{ question }}
                    {% endif %}
                </label><br>
            
                {% if question_number == 0 %}
                    <input type="text" name="a0" required><br>
            
                {% elif question_number in [1, 4, 6, 7, 8] %}
                    <input type="radio" name="a{{ question_number }}" value="Y" required> 예
                    <input type="text" name="a{{ question_number }}_1" 
                           placeholder="{% if question_number == 1 %}시스템 종류(SAP ERP, Oracle ERP, 더존ERP 등)
                                        {% elif question_number == 4 %}Cloud 종류(SAP, Oracle 등)
                                        {% elif question_number == 6 %}Hiware, CyberArk 등
                                        {% elif question_number == 7 %}DB Safer, DBi 등
                                        {% elif question_number == 8 %}Waggle, JobScheduler 등{% endif %}" 
                           size="40"><br>
                    <input type="radio" name="a{{ question_number }}" value="N"> 아니요
            
                {% elif question_number in [2, 3, 5, 9, 10, 11, 15, 17, 18, 19, 20, 23, 24, 27, 28, 29, 30, 32, 33, 34] %}
                    <input type="radio" name="a{{ question_number }}" value="Y" required> 예<br>
                    <input type="radio" name="a{{ question_number }}" value="N"> 아니요
            
                {% elif question_number in [12, 13, 14, 16, 21, 22, 25, 26, 31, 35, 36, 37, 38, 39] %}
                    <textarea name="a{{ question_number }}" 
                              placeholder="{% if question_number == 16 %}최소자리, 복잡성, 변경주기 등
                                           {% elif question_number in [21, 25, 31, 35] %}권한 보유 인원의 부서, 직급, 직책 등
                                           {% else %}관련 절차를 입력하세요.{% endif %}" 
                              rows="5" cols="60"></textarea>
            
                {% else %}
                    <input type="radio" name="answer" value="Y" required> 예<br>
                    <input type="radio" name="answer" value="N"> 아니요
                {% endif %}
            </div>
            

            <div class="mt-3 p-3 bg-light border rounded">
                {% if question_number == 0 %}
                    <small>
                        ※ 시스템에 기록된다는 의미는 자동 로그 저장, DB 테이블 내 기록, 시스템 로그 파일 저장 등의 방법을 포함합니다.
                    </small>
                {% endif %}
            </div>

            <!-- 다음 버튼 -->
            <div class="mb-3"></div>
            <button type="submit" class="btn btn-primary">다음</button>
        </form>
    </div>
</body>
</html>
