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
                {% elif 11 <= current_index <= 27 %}
                    <i class="fas fa-lock"></i> APD(Access to Program & Data)
                {% elif 28 <= current_index <= 33 %}
                    <i class="fas fa-code"></i> PC(Program Change)
                {% elif 33 <= current_index <= 40 %}
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
                                                 {% elif current_index in [7, 9, 10] %}제품명을 입력하세요{% endif %}"
                                    onclick="selectYes({{ current_index }})">
                            <label class="form-check mt-2">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N">
                                <span class="form-check-label">아니요</span>
                            </label>
                        
                        {% elif current_index in [2, 3, 5, 11, 12, 16, 18, 20, 24, 28, 29, 30, 31, 33, 34] %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required>
                                <span class="form-check-label">예</span>
                            </label>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N">
                                <span class="form-check-label">아니요</span>
                            </label>
                        
                        {% elif current_index in [13, 14, 15, 19, 21, 25, 35] %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required 
                                       onchange="toggleTextarea({{ current_index }})">
                                <span class="form-check-label">예</span>
                            </label>
                            <textarea class="form-control mt-2" name="a{{ current_index }}_1" id="textarea_{{ current_index }}" 
                                    placeholder="관련 절차를 입력하세요." rows="5" disabled
                                    onclick="selectYesAndEnableTextarea({{ current_index }})"
                                    style="cursor: pointer;"></textarea>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N"
                                       onchange="toggleTextarea({{ current_index }})">
                                <span class="form-check-label">아니요</span>
                            </label>
                        
                        {% elif current_index in [17, 22, 23, 26, 27, 32, 36, 37, 38, 39, 40] %}
                            <textarea class="form-control" name="a{{ current_index }}" 
                                    placeholder="{% if current_index in [17, 23, 27] %}최소자리, 복잡성, 변경주기 등
                                              {% elif current_index in [22, 25, 29, 32, 39] %}권한 보유 인원의 부서, 직급, 직무 등
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
            {% if current_index in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 21, 25, 26, 29, 30, 31, 35, 36, 39, 40, 42, 43] %}
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
                    {% elif current_index == 17 %}
                        예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등
                    {% elif current_index == 18 %}
                        시스템의 기능을 이용하여 데이터를 변경한 것이 아닌 관리자 등이 DB에 접속하여 쿼리를 통해 데이터를 변경한 건이 대상이며 해당 변경건만 추출이 가능해야 합니다.
                    {% elif current_index == 19 %}
                        예) 데이터 변경 필요시 담당자는 ITSM을 통해 요청서를 작성하고 데이터 책임자(Data Owner)에게 승인을 득한 후 쿼리를 통해 데이터를 변경함
                    {% elif current_index == 21 %}
                        예) DB 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함
                    {% elif current_index == 22 %}
                        예) 인프라관리팀 김xx 과장, DBA
                    {% elif current_index == 23 %}
                        예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등
                    {% elif current_index == 25 %}
                        예) OS 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함
                    {% elif current_index == 26 %}
                        예) 인프라관리팀 이xx 책임, 보안관리자
                    {% elif current_index == 27 %}
                        예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등
                    {% elif current_index == 28 %}
                        변경에 대한 History가 시스템에 의해 기록되어야 합니다. A화면을 1, 3, 5월에 요청서를 받아 변경했다면 각각의 이관(배포)이력이 기록되어야 하며 자체기능, 배포툴, 형상관리툴 등을 사용할 수 있습니다.
                    {% elif current_index == 32 %}
                        예) 인프라관리팀 박xx 수석, 서버관리자
                    {% elif current_index == 33 %}
                        JSP, ASP 등으로 개발된 웹시스템의 경우 localhost 또는 127.0.0.1을 개발서버로도 볼 수 있습니다.
                    {% elif current_index == 34 %}
                        개발되어 등록된 배치 프로그램(Background Job)을 스케줄로 등록 또는 변경한 경우로 한정합니다. 배치 프로그램을 개발하여 운영서버에 반영하는 것은 이 경우에 포함되지 않습니다.
                    {% elif current_index == 35 %}
                        예) 배치 스케줄이 필요한 경우 ITSM을 통해 요청서를 작성하고 승인권자의 승인을 득한 후 적절한 담당자에 의해 스케줄이 등록된다
                    {% elif current_index == 36 %}
                        예) 시스템 운영팀 최xx 과장, 시스템운영자
                    {% elif current_index == 37 %}
                        예1) 매일 아침 배치수행결과를 확인하며 문서화하며 오류 발생시 원인파악 및 조치현황 등을 함께 기록함<br>
                        예2) 오류 발생시에만 점검결과를 작성하며 오류 발생 기록은 삭제하지 않고 유지됨
                    {% elif current_index == 39 %}
                        예) 백업은 시스템에 의해 매일/매주/매월 자동으로 수행되며 월단위로 모니터링하여 정상완료 여부를 문서로 작성함
                    {% elif current_index == 40 %}
                        예) 서버실 출입 필요시 사전에 승인권자에게 승인을 득하며 방명록을 작성하고 담당자 동행하에 함께 출입함
                    {% endif %}
                </div>
            {% endif %}

            <!-- 제출 버튼 -->
            <div class="text-center mt-4">
                {% if current_index > 0 %}
                <a href="/link2/prev" class="btn btn-secondary me-2">
                    <i class="fas fa-arrow-left"></i>
                    이전
                </a>
                {% endif %}
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
        
        function selectYesAndEnableTextarea(questionNumber) {
            console.log('selectYesAndEnableTextarea called for question:', questionNumber);
            
            // '예' 라디오 버튼 찾기
            const yesRadio = document.querySelector(`input[name="a${questionNumber}"][value="Y"]`);
            if (!yesRadio) {
                console.error('Yes radio button not found for question:', questionNumber);
                return;
            }
            
            // textarea 찾기
            const textarea = document.getElementById(`textarea_${questionNumber}`);
            if (!textarea) {
                console.error('Textarea not found for question:', questionNumber);
                return;
            }
            
            // '예' 선택
            yesRadio.checked = true;
            console.log('Yes radio button checked');
            
            // textarea 활성화
            textarea.disabled = false;
            textarea.required = true;
            console.log('Textarea enabled and required');
            
            // change 이벤트 발생
            const event = new Event('change', { bubbles: true });
            yesRadio.dispatchEvent(event);
        }
        
        function toggleTextarea(questionNumber) {
            console.log('toggleTextarea called for question:', questionNumber);
            
            const textarea = document.getElementById(`textarea_${questionNumber}`);
            const yesRadio = document.querySelector(`input[name="a${questionNumber}"][value="Y"]`);
            const noRadio = document.querySelector(`input[name="a${questionNumber}"][value="N"]`);
            
            if (!textarea || !yesRadio || !noRadio) {
                console.error('Required elements not found for question:', questionNumber);
                return;
            }
            
            if (yesRadio.checked) {
                textarea.disabled = false;
                textarea.required = true;
                console.log('Textarea enabled and required');
            } else if (noRadio.checked) {
                textarea.disabled = true;
                textarea.value = '';
                textarea.required = false;
                console.log('Textarea disabled and cleared');
            }
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
