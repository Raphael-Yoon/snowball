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
                    <i class="fas fa-laptop-code"></i> PC(Program Change)
                {% elif 33 <= current_index <= 40 %}
                    <i class="fas fa-cogs"></i> CO(Computer Operation)
                {% else %}
                    <i class="fas fa-question-circle"></i> 기타
                {% endif %}
            </h1>
        </div>

        <div class="text-center mt-4">
            <button type="button" class="btn btn-outline-secondary me-2" onclick="fillSample({{ current_index }})">
                <i class="fas fa-magic"></i> 샘플입력
            </button>
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
                        
                        {% elif current_index in [13, 14, 15, 19, 21, 25, 29, 30, 31, 35] %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required 
                                       onchange="toggleTextarea({{ current_index }})">
                                <span class="form-check-label">예</span>
                            </label>
                            <textarea class="form-control mt-2" name="a{{ current_index }}_1" id="textarea_{{ current_index }}" 
                                    placeholder="관련 절차를 입력하세요." rows="5" readonly
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
                                              {% elif current_index in [22, 25, 26, 29, 32] %}권한 보유 인원의 부서, 직급, 직무 등
                                              {% else %}관련 절차를 입력하세요.{% endif %}" 
                                    rows="5"></textarea>
                        
                        {% elif current_index in [2, 3, 5, 11, 12, 16, 18, 20, 24, 28, 33, 34] %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required>
                                <span class="form-check-label">예</span>
                            </label>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N">
                                <span class="form-check-label">아니요</span>
                            </label>
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
            {% set help_texts = {
                4: "SaaS (Software as a Service): 사용자가 직접 설치 및 관리할 필요 없이, 클라우드에서 제공되는 ERP 소프트웨어를 사용하는 방식.<br>예: SAP S/4HANA Cloud, Oracle NetSuite, Microsoft Dynamics 365 → 기업이 재무, 인사, 회계, 공급망 관리 등을 클라우드에서 운영 가능.<br>IaaS (Infrastructure as a Service): 기업이 자체적으로 ERP 시스템을 구축하고 운영할 수 있도록 서버, 스토리지, 네트워크 등의 인프라를 제공하는 방식.<br>예: AWS EC2, Microsoft Azure Virtual Machines, Google Cloud Compute Engine → 기업이 SAP, Oracle ERP 등의 온프레미스 버전을 클라우드 환경에서 직접 운영.",
                5: "SOC 1 Report (Service Organization Control 1 보고서)는 재무 보고와 관련된 내부 통제 사항을 검증하는 보고서입니다.",
                6: "예: 윈도우즈 서버 2012, Unix AIX, Linux Redhat 등",
                7: "예: Hiware, CyberArk 등",
                8: "예: Oracle R12, MS SQL Server 2008 등",
                9: "예: DBi, DB Safer 등",
                10: "예: Waggle, JobScheduler 등",
                11: "사용자A가 재무권한을 가지고 있었는데 당기에 구매권한을 추가로 받았을 경우 언제(날짜 등) 구매권한을 받았는지 시스템에서 관리되는 경우를 의미합니다.",
                12: "기존 권한 회수시 History를 관리하고 있는지를 확인합니다.<br>Standard 기능을 기준으로 SAP ERP의 경우 권한회수이력을 별도로 저장하며 Oracle ERP의 경우 권한 데이터를 삭제하지 않고 Effective Date로 관리합니다",
                13: "예) 새로운 권한이 필요한 경우 ITSM을 통해 요청서를 작성하고 팀장의 승인을 받은 후 IT팀에서 해당 권한을 부여함",
                14: "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 기존 권한을 회수함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 기존 권한을 회수함",
                15: "예1) 인사팀에서 인사시스템에 인사명령을 입력하면 시스템에서 자동으로 접근권한을 차단함<br>예2) 인사팀에서 인사명령을 IT팀으로 전달하면 IT팀에서 해당 인원의 접근권한을 차단함",
                17: "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등",
                18: "시스템의 기능을 이용하여 데이터를 변경한 것이 아닌 관리자 등이 DB에 접속하여 쿼리를 통해 데이터를 변경한 건이 대상이며 해당 변경건만 추출이 가능해야 합니다",
                19: "예) 데이터 변경 필요시 담당자는 ITSM을 통해 요성서를 작성하고 책임자의 승인을 받은 후 IT담당자가 데이터를 변경함",
                21: "예) DB 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함",
                22: "예) 인프라관리팀 김xx 과장, DBA",
                23: "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등",
                25: "예) OS 접근권한 필요시 담당자는 ITSM을 통해 요청서를 작성하고 서버 책임자에게 승인을 받은 후 서버 관리자가 접근 권한을 부여함",
                26: "예) 인프라관리팀 이xx 책임, 보안관리자",
                27: "예) 최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일 등",
                28: "변경에 대한 History가 시스템에 의해 기록되어야 합니다. A화면을 1, 3, 5월에 요청서를 받아 변경했다면 각각의 이관(배포)이력이 기록되어야 하며 자체기능, 배포툴, 형상관리툴 등을 사용할 수 있습니다.",
                29: "예) 프로그램 기능 변경 필요시 ITSM을 통해 요청서를 작성하고 부서장의 승인을 득함",
                30: "예) 프로그램 기능 변경 완료 후 요청자에 의해 사용자 테스트가 수행되고 그 결과가 문서화됨",
                31: "예) 프로그램 기능 변경 및 사용자 테스트 완료 후 변경담당자로부터 이관 요청서가 작성되고 부서장의 승인을 득함",
                32: "예) 인프라관리팀 박xx 수석, 서버관리자",
                33: "JSP, ASP 등으로 개발된 웹시스템의 경우 localhost 또는 127.0.0.1을 개발서버로도 볼 수 있습니다",
                34: "개발되어 등록된 배치 프로그램(Background Job)을 스케줄로 등록 또는 변경한 경우로 한정합니다. 배치 프로그램을 개발하여 운영서버에 반영하는 것은 이 경우에 포함되지 않습니다",
                35: "예) 배치 스케줄이 필요한 경우 ITSM을 통해 요청서를 작성하고 승인권자의 승인을 득한 후 적절한 담당자에 의해 스케줄이 등록됨",
                36: "예) 시스템 운영팀 최xx 과장, 시스템운영자",
                37: "예1) 매일 아침 배치수행결과를 확인하며 문서화하며 오류 발생시 원인파악 및 조치현황 등을 함께 기록함<br>예2) 오류 발생시에만 점검결과를 작성하며 오류 발생 기록은 삭제하지 않고 유지됨",
                39: "예) 백업은 시스템에 의해 매일/매주/매월 자동으로 수행되며 월단위로 모니터링하여 정상완료 여부를 문서로 작성함",
                40: "예) 서버실 출입 필요시 사전에 승인권자에게 승인을 득하며 방명록을 작성하고 담당자 동행하에 함께 출입함",
            } %}
            
            {% if current_index in help_texts %}
                <div class="help-text">
                    <i class="fas fa-info-circle me-2"></i>
                    {{ help_texts[current_index]|safe }}
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
                <button type="submit" class="btn btn-primary" id="submitBtn">
                    <i class="fas fa-arrow-right"></i>
                    {% if current_index + 1 == question_count %}제출{% else %}다음{% endif %}
                </button>
            </div>
        </form>
    </div>

    <!-- 완료 모달 -->
    <div class="modal fade" id="completeModal" tabindex="-1" aria-labelledby="completeModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="completeModalLabel">알림</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            완료
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" id="modalConfirmBtn">확인</button>
          </div>
        </div>
      </div>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
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
            textarea.removeAttribute('readonly');
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
                textarea.removeAttribute('readonly');
                textarea.required = true;
                console.log('Textarea enabled and required');
            } else if (noRadio.checked) {
                textarea.setAttribute('readonly', true);
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

        function fillSample(questionNumber) {
            // 질문별 샘플값 정의
            const samples = {
                0: { type: 'text', value: 'Amidas' }, // 0: 시스템 이름을 적어주세요.
                1: { type: 'radio_text', radio: 'Y', text: 'SAP ERP' }, // 1: 사용하고 있는 시스템은 상용소프트웨어입니까?
                2: { type: 'radio', value: 'Y' }, // 2: 기능을 회사내부에서 수정하여 사용할 수 있습니까?(SAP, Oracle ERP 등등)
                3: { type: 'radio', value: 'N' }, // 3: Cloud 서비스를 사용하고 있습니까?
                4: { type: 'radio', value: 'Y' }, // 4: 어떤 종류의 Cloud입니까?
                5: { type: 'radio', value: 'Y' }, // 5: Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?
                6: { type: 'text', value: 'Linux Redhat 8' }, // 6: OS 종류와 버전을 작성해 주세요.
                7: { type: 'radio_text', radio: 'Y', text: 'Hiware' }, // 7: OS 접근제어 Tool을 사용하고 있습니까?
                8: { type: 'text', value: 'Oracle 19c' }, // 8: DB 종류와 버전을 작성해 주세요.
                9: { type: 'radio_text', radio: 'Y', text: 'DB Safer' }, // 9: DB 접근제어 Tool을 사용하고 있습니까?
                10: { type: 'radio_text', radio: 'N', text: '' }, // 10: 별도의 Batch Schedule Tool을 사용하고 있습니까?
                11: { type: 'radio', value: 'Y' }, // 11: 사용자 권한부여 이력이 시스템에 기록되고 있습니까?
                12: { type: 'radio', value: 'Y' }, // 12: 사용자 권한회수 이력이 시스템에 기록되고 있습니까?
                13: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성 및 승인' }, // 13: 사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                14: { type: 'radio_textarea', radio: 'Y', textarea: '인사명령 후 권한 회수' }, // 14: 부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?
                15: { type: 'radio_textarea', radio: 'Y', textarea: '퇴사자 접근권한 차단' }, // 15: 퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?
                16: { type: 'radio', value: 'Y' }, // 16: 전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?
                17: { type: 'textarea', value: '최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일' }, // 17: 패스워드 설정사항을 기술해 주세요.
                18: { type: 'radio', value: 'Y' }, // 18: 데이터 변경 이력이 시스템에 기록되고 있습니까?
                19: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 및 승인' }, // 19: 데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                20: { type: 'radio', value: 'Y' }, // 20: DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?
                21: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 및 승인' }, // 21: DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                22: { type: 'textarea', value: '인프라관리팀 김xx 과장' }, // 22: DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.
                23: { type: 'textarea', value: '최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일' }, // 23: DB 패스워드 설정사항을 기술해 주세요.
                24: { type: 'radio', value: 'Y' }, // 24: OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?
                25: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 및 승인' }, // 25: OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                26: { type: 'textarea', value: '인프라관리팀 이xx 책임' }, // 26: OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.
                27: { type: 'textarea', value: '최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일' }, // 27: OS 패스워드 설정사항을 기술해 주세요.
                28: { type: 'radio', value: 'Y' }, // 28: 프로그램 변경 이력이 시스템에 기록되고 있습니까?
                29: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 및 승인' }, // 29: 프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?
                30: { type: 'radio_textarea', radio: 'Y', textarea: '사용자 테스트 및 결과 문서화' }, // 30: 프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?
                31: { type: 'radio_textarea', radio: 'Y', textarea: '이관 요청서 및 승인' }, // 31: 프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?
                32: { type: 'textarea', value: '인프라관리팀 박xx 수석' }, // 32: 이관(배포)권한을 보유한 인원에 대해 기술해 주세요.
                33: { type: 'radio', value: 'Y' }, // 33: 운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?
                34: { type: 'radio', value: 'Y' }, // 34: 배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?
                35: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 및 승인' }, // 35: 배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                36: { type: 'textarea', value: '시스템 운영팀 최xx 과장' }, // 36: 배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.
                37: { type: 'textarea', value: '매일 아침 배치수행결과 확인 및 문서화' }, // 37: 배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.
                38: { type: 'textarea', value: '장애 발생시 원인파악 및 조치' }, // 38: 장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.
                39: { type: 'textarea', value: '백업 자동 수행 및 월단위 모니터링' }, // 39: 백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.
                40: { type: 'textarea', value: '사전 승인 및 방명록 작성' }, // 40: 서버실 출입시의 절차에 대해 기술해 주세요.
            };
            const sample = samples[questionNumber];
            if (!sample) return;
            // 텍스트 입력
            if (sample.type === 'text') {
                const input = document.querySelector(`input[name='a${questionNumber}']`);
                if (input) input.value = sample.value;
            }
            // 라디오만
            if (sample.type === 'radio') {
                const radio = document.querySelector(`input[name='a${questionNumber}'][value='${sample.value}']`);
                if (radio) radio.checked = true;
            }
            // 라디오+텍스트
            if (sample.type === 'radio_text') {
                const radio = document.querySelector(`input[name='a${questionNumber}'][value='${sample.radio}']`);
                if (radio) radio.checked = true;
                const input = document.querySelector(`input[name='a${questionNumber}_1']`);
                if (input) input.value = sample.text;
            }
            // 라디오+textarea
            if (sample.type === 'radio_textarea') {
                const radio = document.querySelector(`input[name='a${questionNumber}'][value='${sample.radio}']`);
                if (radio) radio.checked = true;
                const textarea = document.getElementById(`textarea_${questionNumber}`);
                if (textarea) {
                    textarea.removeAttribute('readonly');
                    textarea.value = sample.textarea;
                    textarea.required = true;
                }
            }
            // textarea만
            if (sample.type === 'textarea') {
                const textarea = document.querySelector(`textarea[name='a${questionNumber}']`);
                if (textarea) textarea.value = sample.value;
            }
            // 자동으로 다음(제출) 버튼 클릭
            setTimeout(function() {
                const submitBtn = document.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.click();
            }, 100); // 입력 후 약간의 딜레이
        }

        // 단축키: Ctrl+Shift+S로 샘플입력 실행
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.shiftKey && (e.key === 's' || e.key === 'S')) {
                e.preventDefault();
                fillSample(current_index);
            }
        });

        // 마지막 질문 제출 시 엑셀 다운로드 + 완료 메시지 + 메인 이동
        document.addEventListener('DOMContentLoaded', function() {
            var form = document.querySelector('form[action="/link2"]');
            var isLast = {{ 'true' if current_index + 1 == question_count else 'false' }};
            if (form && isLast) {
                var completeModal = new bootstrap.Modal(document.getElementById('completeModal'));
                var modalConfirmBtn = document.getElementById('modalConfirmBtn');
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    completeModal.show();
                });
                modalConfirmBtn.addEventListener('click', function() {
                    completeModal.hide();
                    form.submit();
                });
            }
        });
    </script>
</body>
</html>