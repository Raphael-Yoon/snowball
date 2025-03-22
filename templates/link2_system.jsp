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
        <h1>IT 시스템</h1>

        <!-- 퀴즈 폼 시작 -->
        <form action="/link2" method="post">
            <div class="mb-3">
                {% if question_number == 0 %}
                    <label>{{ question }}</label><br>
                {% else %}
                    <label>{{ question_number }}. {{ question }}</label><br>
                {% endif %}
                {% if question_number == 0 %}
                    <input type="text" name="a0" required><br>
                <!-- ✅ question_number가 1이면 특정 라디오 버튼 표시 -->
                {% elif question_number == 1 %}
                    <input type="radio" name="a1" value="Y" required> 예 (상용 소프트웨어)
                    <input type="text" name="a1_1" placeholder="시스템 종류(SAP ERP, Oracle ERP, 더존ERP 등)" size="40"><br>
                    <input type="radio" name="a1" value="N"> 아니요 (자체개발 소스트웨어)<br>
				{% elif question_number == 2 %}
                    <input type="radio" name="a2" value="Y" required> 예 (수정 가능)<br>
                    <input type="radio" name="a2" value="N"> 아니요 (수정 불가능)<br>
				{% elif question_number == 3 %}
                    <input type="radio" name="a3" value="Y" required> 예(Cloud 사용)<br>
                    <input type="radio" name="a3" value="N"> 아니요 (Cloud 미사용)<br>
                    {% elif question_number == 4 %}
                    <input type="radio" name="a4" value="Y" required> SaaS
                    <input type="text" name="a4_1" placeholder="Cloud 종류(SAP, Oracle 등)" size="40"><br>
                    <small>※ SaaS(Software as a Service): 클라우드 기반의 소프트웨어 서비스로, 사용자는 설치 없이 웹에서 소프트웨어를 이용할 수 있습니다.</small><br>
                    <input type="radio" name="a4" value="N"> IaaS(AWS, Azure 등)
                    <input type="text" name="a4_2" placeholder="Cloud 종류(AWS, MS Azure 등)" size="40"><br>
                    <small>※ IaaS(Infrastructure as a Service): 가상 서버, 스토리지, 네트워크 등 IT 인프라를 제공하는 클라우드 서비스입니다.</small><br>                
				{% elif question_number == 5 %}
                    <input type="radio" name="a5" value="Y" required> 예 (발행)<br>
                    <input type="radio" name="a5" value="N"> 아니요 (미발행)<br>
				{% elif question_number == 6 %}
                    <input type="radio" name="a6" value="Y" required> 예 (사용)
                    <input type="text" name="a6_1" placeholder="Hiware, CyberArk 등 " size="40"><br>
                    <input type="radio" name="a6" value="N"> 아니요 (미사용)<br>
                {% elif question_number == 7 %}
                    <input type="radio" name="a7" value="Y" required> 예 (사용)
                    <input type="text" name="a7_1" placeholder="DB Safer, DBi 등" size="40"><br>
                    <input type="radio" name="a7" value="N"> 아니요 (미사용)<br>
                {% elif question_number == 8 %}
                    <input type="radio" name="a8" value="Y" required> 예 (사용)
                    <input type="text" name="a8_1" placeholder="Waggle, JobScheduler 등" size="40"><br>
                    <input type="radio" name="a8" value="N"> 아니요 (미사용)<br>
                {% elif question_number == 9 %}
                    <input type="radio" name="a9" required> 예 (기록됨)
                    <input type="radio" name="a9" value="N"> 아니요 (기록되지 않음(수기관리 포함))<br>
                {% elif question_number == 10 %}
                    <input type="radio" name="a10" required> 예 (기록됨)
                    <input type="radio" name="a10" value="N"> 아니요 (기록되지 않음(수기관리 포함))<br>
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
