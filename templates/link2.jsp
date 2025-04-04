<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall Interview</title>
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container">
        <!-- 진행률 표시 -->
        <div class="progress">
            <div class="progress-bar" role="progressbar" 
                 style="width: {{ (current_index + 1) / question_count * 100 }}%"
                 aria-valuenow="{{ current_index + 1 }}" 
                 aria-valuemin="0" 
                 aria-valuemax="{{ question_count }}">
            </div>
        </div>

        <!-- 섹션 제목 -->
        <div class="text-center">
            <h1 class="section-title">
                {% if 0 <= current_index <= 10 %}
                    <i class="fas fa-server"></i> 공통사항
                {% elif 11 <= current_index <= 30 %}
                    <i class="fas fa-lock"></i> APD(Access to Program & Data)
                {% elif 31 <= current_index <= 36 %}
                    <i class="fas fa-code"></i> PC(Program Change)
                {% elif 37 <= current_index <= 43 %}
                    <i class="fas fa-cogs"></i> CO(Computer Operation)
                {% else %}
                    <i class="fas fa-question-circle"></i> 기타
                {% endif %}
            </h1>
        </div>

        <!-- 질문 폼 -->
        <form action="/link2" method="post">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="fas fa-question-circle"></i>
                        질문 {{ current_index + 1 }}/{{ question_count }}
                    </h5>
                    <p class="card-text">{{ question.text }}</p>
                    <div class="mb-3">
                        <!-- 입력 필드 -->
                        {% if current_index in [0, 6, 8] %}
                            <input type="text" class="form-control" name="a{{ current_index }}" required>
                        
                        {% elif current_index == 4 %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required>
                                <span class="form-check-label">SaaS</span>
                            </label>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N">
                                <span class="form-check-label">IaaS</span>
                            </label>
                        
                        {% elif current_index in [1, 7, 9, 10] %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" id="yes_{{ current_index }}" required>
                                <span class="form-check-label">예</span>
                            </label>
                            <input type="text" class="form-control mt-2" name="a{{ current_index }}_1" 
                                   placeholder="{% if current_index == 1 %}시스템 종류(SAP ERP, Oracle ERP, 더존ERP 등)
                                             {% elif current_index == 7 %}Hiware, CyberArk 등
                                             {% elif current_index == 9 %}DB Safer, DBi 등
                                             {% elif current_index == 10 %}Waggle, JobScheduler 등{% endif %}" 
                                   onclick="selectYes({{ current_index }})">
                            <label class="form-check mt-2">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N">
                                <span class="form-check-label">아니요</span>
                            </label>
                        
                        {% elif current_index in [2, 3, 5, 11, 12, 13, 15, 17, 19, 21, 22, 23, 24, 27, 28, 31, 32, 33, 34, 36, 37, 38] %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required>
                                <span class="form-check-label">예</span>
                            </label>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N">
                                <span class="form-check-label">아니요</span>
                            </label>
                        
                        {% elif current_index in [14, 16, 18, 20, 25, 26, 29, 30, 35, 39, 40, 41, 42, 43] %}
                            <textarea class="form-control" name="a{{ current_index }}" 
                                    placeholder="{% if current_index in [20, 26, 30] %}최소자리, 복잡성, 변경주기 등
                                              {% elif current_index in [25, 29, 35, 39] %}권한 보유 인원의 부서, 직급, 직책 등
                                              {% else %}관련 절차를 입력하세요.{% endif %}" 
                                    rows="5"></textarea>
                        
                        {% else %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="answer" value="Y" required>
                                <span class="form-check-label">예</span>
                            </label>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="answer" value="N">
                                <span class="form-check-label">아니요</span>
                            </label>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- 도움말 -->
            {% if current_index in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 21, 25, 26, 29, 30, 31, 35, 36, 39, 40, 42, 43] %}
                <div class="help-text">
                    <i class="fas fa-info-circle me-2"></i>
                    {% if current_index == 4 %}
                        SaaS (Software as a Service): 사용자가 직접 설치 및 관리할 필요 없이, 클라우드에서 제공되는 ERP 소프트웨어를 사용하는 방식.<br>
                        예: SAP S/4HANA Cloud, Oracle NetSuite, Microsoft Dynamics 365 → 기업이 재무, 인사, 회계, 공급망 관리 등을 클라우드에서 운영 가능.<br>
                        IaaS (Infrastructure as a Service): 기업이 자체적으로 ERP 시스템을 구축하고 운영할 수 있도록 서버, 스토리지, 네트워크 등의 인프라를 제공하는 방식.<br>
                        예: AWS EC2, Microsoft Azure Virtual Machines, Google Cloud Compute Engine → 기업이 SAP, Oracle ERP 등의 온프레미스 버전을 클라우드 환경에서 직접 운영.
                    {% elif current_index == 5 %}
                        SOC 1 Report (Service Organization Control 1 보고서)는 재무 보고와 관련된 내부 통제 사항을 검증하는 보고서입니다.
                    {% elif current_index == 6 %}
                        예: 윈도우즈 서버 2012, Unix AIX, Linux Redhat 등
                    {% elif current_index == 7 %}
                        예: Hiware, CyberArk 등
                    {% elif current_index == 8 %}
                        예: Oracle R12, MS SQL Server 2008 등
                    {% elif current_index == 9 %}
                        예: DBi, DB Safer 등
                    {% elif current_index == 10 %}
                        예: Waggle, JobScheduler 등
                    {% elif current_index == 11 %}
                        사용자A가 재무권한을 가지고 있었는데 당기에 구매권한을 추가로 받았을 경우 언제(날짜 등) 구매권한을 받았는지 시스템에서 관리되며 이를 리스트업할 수 있는 경우를 의미합니다.
                    {% elif current_index == 12 %}
                        기존 권한 회수시 History를 관리하고 있는지를 확인합니다.<br>
                        Standard 기능을 기준으로 SAP ERP의 경우 권한회수이력을 별도로 저장하며 Oracle ERP의 경우 권한 데이터를 삭제하지 않고 Effective Date로 관리합니다
                    {% elif current_index == 13 %}
                        예) 새로운 권한이 필요한 경우 ITSM을 통해 요청서를 작성하고 팀장의 승인을 받은 후 IT팀에서 해당 권한을 부여함
                    {% elif current_index == 14 %}
                        예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 기존 권한을 회수함<br>
                        예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 기존 권한을 회수함
                    {% elif current_index == 15 %}
                        예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 접근권한을 차단함<br>
                        예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 접근권한을 차단함
                    {% elif current_index == 16 %}
                        예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등
                    {% elif current_index == 21 %}
                        시스템의 기능을 이용하여 데이터를 변경한 것이 아닌 관리자 등이 DB에 접속하여 쿼리를 통해 데이터를 변경한 건이 대상이며 해당 변경건만 추출이 가능해야 합니다.
                    {% elif current_index == 25 %}
                        부서, 성명, 직급, 직책, 직무 등
                    {% elif current_index == 26 %}
                        예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등
                    {% elif current_index == 29 %}
                        부서, 성명, 직급, 직책, 직무 등
                    {% elif current_index == 30 %}
                        예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등
                    {% elif current_index == 31 %}
                        변경에 대한 History가 시스템에 의해 기록되어야 합니다. A화면을 1, 3, 5월에 요청서를 받아 변경했다면 각각의 이관(배포)이력이 기록되어야 하며 자체기능, 배포툴, 형상관리툴 등을 사용할 수 있습니다.
                    {% elif current_index == 35 %}
                        부서, 성명, 직급, 직책, 직무 등
                    {% elif current_index == 36 %}
                        웹시스템의 경우 localhost 또는 127.0.0.1을 개발서버로도 볼 수 있습니다.
                    {% elif current_index == 39 %}
                        부서, 성명, 직급, 직책, 직무 등
                    {% elif current_index == 40 %}
                        예1) 매일 아침 배치수행결과를 확인하며 문서화하며 오류 발생시 원인파악 및 조치현황 등을 함께 기록함<br>
                        예2) 오류 발생시에만 점검결과를 작성하며 오류 발생 기록은 삭제하지 않고 유지됨
                    {% elif current_index == 42 %}
                        예) 백업은 시스템에 의해 매일/매주/매월 자동으로 수행되며 월단위로 모니터링하여 정상완료 여부를 문서로 작성함
                    {% elif current_index == 43 %}
                        예) 서버실 출입 필요시 사전에 승인권자에게 승인을 득하며 방명록을 작성하고 담당자 동행하에 함께 출입함
                    {% endif %}
                </div>
            {% endif %}

            <!-- 제출 버튼 -->
            <div class="text-center mt-4">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i>
                    다음
                </button>
            </div>
        </form>
    </div>

    <!-- JavaScript -->
    <script>
        function selectYes(questionNumber) {
            document.getElementById("yes_" + questionNumber).checked = true;
        }
        
        // 라디오 버튼 라벨 클릭 이벤트 처리
        document.addEventListener('DOMContentLoaded', function() {
            // 모든 라디오 버튼 라벨에 클릭 이벤트 추가
            const radioLabels = document.querySelectorAll('.form-check-label');
            
            radioLabels.forEach(function(label) {
                label.addEventListener('click', function(e) {
                    // 라벨에 연결된 라디오 버튼 찾기
                    const radioId = this.getAttribute('for');
                    if (radioId) {
                        const radio = document.getElementById(radioId);
                        if (radio) {
                            // 라디오 버튼 선택
                            radio.checked = true;
                            
                            // 이벤트 발생 (폼 제출 시 값이 전송되도록)
                            const event = new Event('change', { bubbles: true });
                            radio.dispatchEvent(event);
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>
