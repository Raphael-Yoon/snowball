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

            {% if question_number in [1, 4, 5, 9, 12, 13, 14, 16, 22, 26] %}
                <div class="mt-3 p-3 bg-light border rounded">
                    {% if question_number == 4 %}
                    <small>
                        SaaS (Software as a Service): 사용자가 직접 설치 및 관리할 필요 없이, 클라우드에서 제공되는 ERP 소프트웨어를 사용하는 방식.<br>
                        예: SAP S/4HANA Cloud, Oracle NetSuite, Microsoft Dynamics 365 → 기업이 재무, 인사, 회계, 공급망 관리 등을 클라우드에서 운영 가능.<br>
                        IaaS (Infrastructure as a Service): 기업이 자체적으로 ERP 시스템을 구축하고 운영할 수 있도록 서버, 스토리지, 네트워크 등의 인프라를 제공하는 방식.<br>
                        예: AWS EC2, Microsoft Azure Virtual Machines, Google Cloud Compute Engine → 기업이 SAP, Oracle ERP 등의 온프레미스 버전을 클라우드 환경에서 직접 운영.
                    </small>
                    {% elif question_number == 5 %}
                        <small>
                            SOC 1 Report (Service Organization Control 1 보고서)는 재무 보고와 관련된 내부 통제 사항을 검증하는 보고서입니다.
                        </small>
                    {% elif question_number == 1 %}
                        <small>
                            사용소프트웨어는 Package S/W를 의미하며 SAP, Oracle, 더존, 영림원 등의 시스템을 뜻합니다.
                        </small>
                    {% elif question_number == 9 %}
                        <small>
                            사용자A가 재무권한을 가지고 있었는데 당기에 구매권한을 추가로 받았을 경우 언제(날짜 등) 구매권한을 받았는지 시스템에서 관리되며 이를 리스트업할 수 있는 경우를 의미합니다.
                        </small>
                    {% elif question_number == 12 %}
                        <small>
                            예) 새로운 권한이 필요한 경우 ITSM을 통해 요청서를 작성하고 팀장의 승인을 받은 후 IT팀에서 해당 권한을 부여함.
                        </small>
                    {% elif question_number == 13 %}
                        <small>
                            예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 기존 권한을 회수함.<br>
                            예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 기존 권한을 회수함.
                        </small>
                    {% elif question_number == 14 %}
                        <small>
                            예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 접근권한을 차단함.<br>
                            예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 접근권한을 차단함.
                        </small>
                    {% elif question_number == 16 %}
                        <small>
                            예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등.
                        </small>
                    {% elif question_number == 22 %}
                        <small>
                            예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등.
                        </small>
                    {% elif question_number == 26 %}
                        <small>
                            예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등.
                        </small>
                    {% endif %}
                {% endif %}
            </div>

            <!-- 다음 버튼 -->
            <div class="mb-3"></div>
            <button type="submit" class="btn btn-primary">다음</button>
        </form>
    </div>
</body>
</html>
