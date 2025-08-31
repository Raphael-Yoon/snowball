<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall Interview</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <!-- CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <!-- 진행률 표시 -->
        <div class="progress">
            <div class="progress-bar" role="progressbar" 
                 style="width: {{ (current_index + 1) / question_count * 100 }}%"
                 aria-valuenow="{{ current_index + 1 }}" 
                 aria-valuemin="0" 
                 aria-valuemax="{{ question_count }}">
                {{ "%.1f"|format((current_index + 1) / question_count * 100) }}%
            </div>
        </div>

        <!-- 섹션 제목 -->
        <div class="text-center mt-3">
            <h1 class="section-title">
                {% if actual_question_number %}
                    {% set q_num = actual_question_number - 1 %}
                {% else %}
                    {% set q_num = current_index %}
                {% endif %}
                
                {% if 0 <= q_num <= 5 %}
                    <i class="fas fa-server"></i> 공통사항
                {% elif 6 <= q_num <= 30 %}
                    <i class="fas fa-lock"></i> APD(Access to Program & Data)
                {% elif 31 <= q_num <= 37 %}
                    <i class="fas fa-laptop-code"></i> PC(Program Change)
                {% elif 38 <= q_num <= 46 %}
                    <i class="fas fa-cogs"></i> CO(Computer Operation)
                {% else %}
                    <i class="fas fa-check-circle"></i> 모든 질문이 완료되었습니다.
                {% endif %}
            </h1>
        </div>

        <div class="text-center mt-4">
            {% if remote_addr == '127.0.0.1' or (user_info and user_info.get('admin_flag') == 'Y') %}
            <button type="button" class="btn btn-outline-secondary me-2" onclick="fillSample({{ actual_question_number - 1 if actual_question_number else current_index }}, {{ current_index }})">
                <i class="fas fa-magic"></i> 샘플입력
            </button>
            <button type="button" class="btn btn-outline-warning me-2" onclick="fillSkipSample({{ actual_question_number - 1 if actual_question_number else current_index }}, {{ current_index }})">
                <i class="fas fa-fast-forward"></i> 스킵샘플
            </button>
            {% endif %}
        </div>

        <!-- 질문 폼 -->
        <form action="/link2" method="post">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">
                        <i class="fas fa-question-circle"></i>
                        {% if actual_question_number %}
                        질문 {{ actual_question_number }}/47
                        {% else %}
                        질문 {{ current_index + 1 }}/{{ question_count }}
                        {% endif %}
                    </h5>
                    <p class="card-text">{{ question.text }}</p>
                    <div class="mb-3">
                        <!-- 입력 필드 -->
                        {% if question.answer_type == '0' %}
                            <select class="form-select" name="a0" required>
                                <option value="">담당자를 선택하세요</option>
                                {# {% for i in range(0, users|length, 3) %}
                                    <option value="{{ users[i+2] }}" {% if answer[0] == users[i+2] %}selected{% endif %}>{{ users[i] }} - {{ users[i+1] }}</option>
                                {% endfor %} #}
                            </select>
                            <!-- 첫 번째 질문(이메일 입력) -->
                            {% if current_index == 0 %}
                            <div class="mt-2">
                                <input type="text" class="form-control{% if is_logged_in %} bg-light{% endif %}" name="a0_text" placeholder="e-Mail 주소를 입력하세요" value="{{ answer[0] }}" {% if is_logged_in %}readonly{% endif %} />
                                {% if is_logged_in %}
                                <small class="form-text text-muted">
                                    <i class="fas fa-lock me-1"></i>로그인된 계정의 이메일이 자동으로 사용됩니다.
                                </small>
                                {% endif %}
                            </div>
                            {% endif %}
                        {% elif question.answer_type == '2' %}
                            {% if current_index == 0 %}
                                <!-- 첫 번째 질문(이메일 입력) -->
                                <input type="text" class="form-control{% if is_logged_in %} bg-light{% endif %}" name="a{{ current_index }}" required placeholder="{{ question.text_help if question.text_help else 'e-Mail 주소를 입력하세요' }}" value="{{ answer[current_index] }}" {% if is_logged_in %}readonly{% endif %}>
                                {% if is_logged_in %}
                                <small class="form-text text-muted">
                                    <i class="fas fa-lock me-1"></i>로그인된 계정의 이메일이 자동으로 사용됩니다.
                                </small>
                                {% endif %}
                            {% else %}
                                <!-- 일반 텍스트 입력 -->
                                <input type="text" class="form-control" name="a{{ current_index }}" required placeholder="{{ question.text_help if question.text_help else '' }}" value="{{ answer[current_index] }}">
                            {% endif %}
                        {% elif question.answer_type == '3' %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" id="yes_{{ current_index }}" required {% if answer[current_index] == 'Y' %}checked{% endif %}>
                                <span class="form-check-label">예</span>
                            </label>
                            <input type="text" class="form-control mt-2" name="a{{ current_index }}_1" placeholder="{{ question.text_help if question.text_help else '제품명을 입력하세요' }}" onclick="selectYes({{ current_index }})" value="{{ textarea_answer[current_index] }}">
                            <label class="form-check mt-2">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N" {% if answer[current_index] == 'N' %}checked{% endif %}>
                                <span class="form-check-label">아니요</span>
                            </label>
                        {% elif question.answer_type == '4' %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required onchange="toggleTextarea({{ current_index }})" {% if answer[current_index] == 'Y' %}checked{% endif %}>
                                <span class="form-check-label">예</span>
                            </label>
                            <textarea class="form-control mt-2" name="a{{ current_index }}_1" id="textarea_{{ current_index }}" placeholder="{{ question.text_help if question.text_help else '관련 절차를 입력하세요.' }}" rows="5" {% if answer[current_index] != 'Y' %}readonly{% endif %} {% if answer[current_index] == 'Y' %}required{% endif %} onclick="selectYesAndEnableTextarea({{ current_index }})" style="cursor: pointer;">{{ textarea_answer[current_index] }}</textarea>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N" required onchange="toggleTextarea({{ current_index }})" {% if answer[current_index] == 'N' %}checked{% endif %}>
                                <span class="form-check-label">아니요</span>
                            </label>
                        {% elif question.answer_type == '5' %}
                            <textarea class="form-control" name="a{{ current_index }}" placeholder="{{ question.text_help if question.text_help else '관련 절차를 입력하세요.' }}" rows="5">{{ answer[current_index] }}</textarea>
                        {% elif question.answer_type == '1' %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="Y" required {% if answer[current_index] == 'Y' %}checked{% endif %}>
                                <span class="form-check-label">예</span>
                            </label>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N" {% if answer[current_index] == 'N' %}checked{% endif %}>
                                <span class="form-check-label">아니요</span>
                            </label>
                        {% elif question.answer_type == '6' %}
                            {% for option in question.text_help.split('|') %}
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="{{ option }}" required {% if answer[current_index] == option %}checked{% endif %}>
                                <span class="form-check-label">{{ option }}</span>
                            </label>
                            {% endfor %}
                        {% else %}
                            <input type="text" class="form-control" name="a{{ current_index }}" value="{{ answer[current_index] }}">
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- 도움말: s_questions의 help 필드를 활용하여 출력 -->
            {# 아래는 snowball.py의 s_questions 각 질문 딕셔너리의 help 필드를 그대로 출력합니다. #}
            {% if question.help %}
                <div class="help-text">
                    <i class="fas fa-info-circle me-2"></i>
                    {{ question.help|safe }}
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

    <!-- 메일 전송 안내 모달 (43번 질문 전용) -->
    <div class="modal fade" id="mailModal" tabindex="-1" aria-labelledby="mailModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="mailModalLabel">알림</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            곧 메일이 전송됩니다.
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" id="mailModalConfirmBtn">확인</button>
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
                textarea.style.cursor = 'text';
                console.log('Textarea enabled and required');
            } else if (noRadio.checked) {
                textarea.setAttribute('readonly', true);
                textarea.value = '';
                textarea.required = false;
                textarea.style.cursor = 'not-allowed';
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

        function fillSample(questionNumber, currentIndex) {
            console.log(`[SAMPLE] fillSample 호출됨 - questionNumber: ${questionNumber}, currentIndex: ${currentIndex}`);
            // 질문별 샘플값 정의
            const samples = {
                0: { type: 'text', value: 'snowball2727@naver.com' }, // 산출물을 전달받을 e-Mail 주소를 입력해주세요.
                1: { type: 'text', value: 'SAP ERP' }, // 시스템 이름을 적어주세요.
                2: { type: 'radio_text', radio: 'Y', text: 'SAP S/4HANA' }, // 사용하고 있는 시스템은 상용소프트웨어입니까?
                3: { type: 'radio', value: 'Y' }, // Cloud 서비스를 사용하고 있습니까?
                4: { type: 'radio', value: 'SaaS' }, // 어떤 종류의 Cloud입니까?
                5: { type: 'radio', value: 'Y' }, // Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?
                6: { type: 'radio', value: 'N' }, // 사용자 권한부여 이력이 시스템에 기록되고 있습니까? - 미비점 유발
                7: { type: 'radio', value: 'N' }, // 사용자 권한회수 이력이 시스템에 기록되고 있습니까? - 미비점 유발
                8: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM을 통해 요청서 작성 후 팀장 승인을 받아 IT팀에서 권한 부여' }, // 사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                9: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까? - 미비점 유발
                10: { type: 'radio_textarea', radio: 'Y', textarea: '인사팀 인사명령 전달 시 IT팀에서 즉시 접근권한 차단' }, // 퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?
                11: { type: 'textarea', value: 'IT운영팀 김○○ 책임, 시스템 관리자' }, // Application 관리자(Superuser) 권한을 보유한 인원에 대해 기술해 주세요.
                12: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까? - 미비점 유발
                13: { type: 'textarea', value: '최소 8자, 영문/숫자/특수문자 조합, 90일마다 변경' }, // 패스워드 설정사항을 기술해 주세요.
                14: { type: 'radio', value: 'N' }, // 데이터 변경 이력이 시스템에 기록되고 있습니까? - 미비점 유발
                15: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까? - 미비점 유발
                16: { type: 'textarea', value: 'IT운영팀 최○○ 책임, DBA' }, // 데이터 변경 권한을 보유한 인원에 대해 기술해 주세요.
                17: { type: 'radio', value: 'Y' }, // 회사에서 DB에 접속하여 필요한 작업을 수행하는 것이 가능하십니까?
                18: { type: 'text', value: 'Oracle Database 19c' }, // DB 종류와 버전을 작성해 주세요.
                19: { type: 'radio_text', radio: 'N', text: '' }, // DB 접근제어 Tool을 사용하고 있습니까? - 미비점 유발
                20: { type: 'radio', value: 'N' }, // DB 접근권한 부여 이력이 시스템에 기록되고 있습니까? - 미비점 유발
                21: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성 후 서버 책임자 승인을 받아 DB 권한 부여' }, // DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                22: { type: 'textarea', value: 'IT운영팀 이○○ 수석, DBA 권한 보유' }, // DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.
                23: { type: 'textarea', value: '최소 10자, 영문/숫자/특수문자 조합, 180일마다 변경' }, // DB 패스워드 설정사항을 기술해 주세요.
                24: { type: 'radio', value: 'Y' }, // 회사에서 OS서버에 접속하여 필요한 작업을 수행하는 것이 가능하십니까?
                25: { type: 'text', value: 'Windows Server 2019' }, // OS 종류와 버전을 작성해 주세요.
                26: { type: 'radio_text', radio: 'N', text: '' }, // OS 접근제어 Tool을 사용하고 있습니까? - 미비점 유발
                27: { type: 'radio', value: 'Y' }, // OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?
                28: { type: 'radio_textarea', radio: 'N', textarea: '' }, // OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까? - 미비점 유발
                29: { type: 'textarea', value: 'IT운영팀 정○○ 책임, 시스템 관리자' }, // OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.
                30: { type: 'textarea', value: '최소 12자, 영문/숫자/특수문자 조합, 60일마다 변경' }, // 질문 31번: OS 패스워드 설정사항을 기술해 주세요. (인덱스 30)
                31: { type: 'radio', value: 'Y' }, // 질문 32번: 주요 로직을 회사내부에서 수정하여 사용할 수 있습니까? (인덱스 31)
                32: { type: 'radio', value: 'N' }, // 질문 33번: 프로그램 변경 이력이 시스템에 기록되고 있습니까? - 미비점 유발 (인덱스 32)
                33: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성 후 부서장 승인을 받아 개발팀에서 프로그램 변경' }, // 질문 34번: 프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까? (인덱스 33)
                34: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 질문 35번: 프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까? - 미비점 유발 (인덱스 34)
                35: { type: 'radio_textarea', radio: 'Y', textarea: '테스트 완료 후 이관 요청서 작성하고 부서장 승인을 받아 배포' }, // 질문 36번: 프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까? (인덱스 35)
                36: { type: 'textarea', value: '인프라관리팀 박○○ 수석, 배포 담당자' }, // 질문 37번: 이관(배포)권한을 보유한 인원에 대해 기술해 주세요. (인덱스 36)
                37: { type: 'radio', value: 'N' }, // 질문 38번: 운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까? - 미비점 유발 (인덱스 37)
                38: { type: 'radio', value: 'N' }, // 질문 39번: 현재 실행중인 배치 스케줄이 있습니까? (인덱스 38)
                // 배치 관련 질문들은 38번='N'일 때 스킵됨 (39~43번)
                39: { type: 'radio_text', radio: 'N', text: '' }, // 별도의 Batch Schedule Tool을 사용하고 있습니까? - 스킵됨
                40: { type: 'radio', value: 'N' }, // 배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까? (스킵되지만 기본값 제공)
                41: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까? (스킵되지만 기본값 제공)
                42: { type: 'textarea', value: '없음' }, // 배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요. (스킵되지만 기본값 제공)
                43: { type: 'textarea', value: '자동 모니터링 시스템으로 배치 실행 상태 감시, 오류 발생시 관리자에게 즉시 알림' }, // 질문 44번: 배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요. (인덱스 43)
                44: { type: 'textarea', value: '장애 발생시 즉시 담당자에게 알림 후 원인 분석 및 복구 작업 수행, 조치내역 문서화' }, // 질문 45번: 장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요. (인덱스 44)
                45: { type: 'textarea', value: '매일 자동 백업 수행, 백업 성공/실패 여부 모니터링 및 주간 백업 상태 점검' }, // 질문 46번: 백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요. (인덱스 45)
                46: { type: 'textarea', value: '출입 카드 인증 후 출입대장 작성, 동반 출입시 사전 승인 필요' } // 질문 47번: 서버실 출입시의 절차에 대해 기술해 주세요. (인덱스 46)
            };
            
            // 인덱스와 질문 번호 매핑 확인을 위한 디버깅
            console.log(`[SAMPLE DEBUG] 현재 questionNumber: ${questionNumber}`);
            const sample = samples[questionNumber];
            console.log(`[SAMPLE] questionNumber: ${questionNumber}, sample:`, sample);
            if (!sample) {
                console.log(`[SAMPLE] 샘플 데이터가 없습니다: ${questionNumber} - 자동으로 다음 질문으로 넘어갑니다`);
                // 샘플 데이터가 없으면 자동으로 다음 질문으로 넘어가기
                setTimeout(function() {
                    const submitBtn = document.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        console.log(`[SAMPLE] 샘플 데이터 없음 - 자동 다음 질문 이동`);
                        submitBtn.click();
                    }
                }, 100);
                return;
            }
            // 텍스트 입력
            if (sample.type === 'text') {
                if (sample.value === '') {
                    console.log(`[SAMPLE] 텍스트 값이 비어있음 - 자동으로 다음 질문으로 넘어갑니다`);
                    setTimeout(function() {
                        const submitBtn = document.querySelector('button[type="submit"]');
                        if (submitBtn) submitBtn.click();
                    }, 100);
                    return;
                }
                const input = document.querySelector(`input[name='a${currentIndex}']`);
                if (input) input.value = sample.value;
            }
            // 라디오만
            if (sample.type === 'radio') {
                if (sample.value === '') {
                    console.log(`[SAMPLE] 라디오 값이 비어있음 - 자동으로 다음 질문으로 넘어갑니다`);
                    setTimeout(function() {
                        const submitBtn = document.querySelector('button[type="submit"]');
                        if (submitBtn) submitBtn.click();
                    }, 100);
                    return;
                }
                const radio = document.querySelector(`input[name='a${currentIndex}'][value='${sample.value}']`);
                if (radio) radio.checked = true;
            }
            // 라디오+텍스트
            if (sample.type === 'radio_text') {
                const radio = document.querySelector(`input[name='a${currentIndex}'][value='${sample.radio}']`);
                if (radio) radio.checked = true;
                const input = document.querySelector(`input[name='a${currentIndex}_1']`);
                if (input) input.value = sample.text;
            }
            // 라디오+textarea
            if (sample.type === 'radio_textarea') {
                const radio = document.querySelector(`input[name='a${currentIndex}'][value='${sample.radio}']`);
                if (radio) radio.checked = true;
                const textarea = document.getElementById(`textarea_${currentIndex}`);
                if (textarea) {
                    if (sample.radio === 'Y') {
                        // "예" 선택시: textarea 활성화하고 값 입력
                        textarea.removeAttribute('readonly');
                        textarea.value = sample.textarea;
                        textarea.required = true;
                        textarea.style.cursor = 'text';
                    } else {
                        // "아니요" 선택시: textarea 비활성화
                        textarea.setAttribute('readonly', true);
                        textarea.value = '';
                        textarea.required = false;
                        textarea.style.cursor = 'not-allowed';
                    }
                }
            }
            // textarea만
            if (sample.type === 'textarea') {
                const textarea = document.querySelector(`textarea[name='a${currentIndex}']`);
                if (textarea) textarea.value = sample.value;
            }
            // 자동으로 다음(제출) 버튼 클릭
            setTimeout(function() {
                const submitBtn = document.querySelector('button[type="submit"]');
                console.log(`[SAMPLE] 제출 버튼 찾음:`, submitBtn);
                if (submitBtn) {
                    console.log(`[SAMPLE] 제출 버튼 클릭 실행`);
                    submitBtn.click();
                } else {
                    console.log(`[SAMPLE] 제출 버튼을 찾을 수 없습니다`);
                }
            }, 100); // 입력 후 약간의 딜레이
        }

        function fillSkipSample(questionNumber, currentIndex) {
            console.log(`[SKIP SAMPLE] fillSkipSample 호출됨 - questionNumber: ${questionNumber}, currentIndex: ${currentIndex}`);
            
            // 스킵 조건을 만족하는 샘플값 정의 (모든 가능한 질문 스킵)
            const skipSamples = {
                0: { type: 'text', value: 'snowball2727@naver.com' }, // 이메일
                1: { type: 'text', value: 'SAP ERP' }, // 시스템 이름
                2: { type: 'radio_text', radio: 'Y', text: 'SAP S/4HANA' }, // 상용소프트웨어
                3: { type: 'radio', value: 'N' }, // Cloud 서비스 사용 안함 → 4~5번 스킵
                4: { type: 'radio', value: 'IaaS' }, // 어떤 종류의 Cloud입니까? (스킵되지만 기본값 제공)
                5: { type: 'radio', value: 'Y' }, // Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까? (스킵되지만 기본값 제공)
                6: { type: 'radio', value: 'N' }, // 권한부여 이력 미기록
                7: { type: 'radio', value: 'N' }, // 권한회수 이력 미기록
                8: { type: 'skip' }, // Cloud 서비스와 무관하므로 자동입력하지 않음
                9: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 권한 회수 절차 없음
                10: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 퇴사자 권한 차단 절차 없음
                11: { type: 'textarea', value: '' }, // Application 관리자
                12: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 권한 모니터링 절차 없음
                13: { type: 'textarea', value: '' }, // 패스워드 정책
                14: { type: 'radio', value: 'N' }, // DB 접속 불가 → 15~23번 스킵
                15: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 데이터 변경 절차 없음
                16: { type: 'textarea', value: '' }, // 데이터 변경 권한자
                17: { type: 'radio', value: 'Y' }, // DB 접속 가능
                18: { type: 'text', value: 'MySQL 8.0' }, // DB 종류와 버전 (스킵되지만 기본값 제공)
                19: { type: 'radio_text', radio: 'N', text: '' }, // DB 접근제어 Tool 미사용 (스킵되지만 기본값 제공)
                20: { type: 'radio', value: 'N' }, // DB 접근권한 부여 이력 미기록 (스킵되지만 기본값 제공)
                21: { type: 'radio_textarea', radio: 'N', textarea: '' }, // DB 접근권한 승인 절차 없음 (스킵되지만 기본값 제공)
                22: { type: 'textarea', value: '' }, // DB 관리자 권한자 (스킵되지만 기본값 제공)
                23: { type: 'textarea', value: '' }, // DB 패스워드 정책 (스킵되지만 기본값 제공)
                24: { type: 'radio', value: 'N' }, // OS 접속 불가 → 25~30번 스킵
                25: { type: 'text', value: 'Linux Ubuntu 20.04' }, // OS 종류와 버전 (스킵되지만 기본값 제공)
                26: { type: 'radio_text', radio: 'N', text: '' }, // OS 접근제어 Tool 미사용 (스킵되지만 기본값 제공)
                27: { type: 'radio', value: 'N' }, // OS 접근권한 부여 이력 미기록 (스킵되지만 기본값 제공)
                28: { type: 'radio_textarea', radio: 'N', textarea: '' }, // OS 접근권한 승인 절차 없음 (스킵되지만 기본값 제공)
                29: { type: 'textarea', value: '' }, // OS 관리자 권한자 (스킵되지만 기본값 제공)
                30: { type: 'textarea', value: '' }, // OS 패스워드 정책 (스킵되지만 기본값 제공)
                31: { type: 'radio', value: 'N' }, // 프로그램 변경 불가 → 32~37번 스킵
                32: { type: 'radio', value: 'N' }, // 프로그램 변경 이력 미기록 (스킵되지만 기본값 제공)
                33: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 프로그램 변경 승인 절차 없음 (스킵되지만 기본값 제공)
                34: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 사용자 테스트 절차 없음 (스킵되지만 기본값 제공)
                35: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 이관 승인 절차 없음 (스킵되지만 기본값 제공)
                36: { type: 'textarea', value: '' }, // 이관 권한자 (스킵되지만 기본값 제공)
                37: { type: 'radio', value: 'N' }, // 개발/테스트 서버 미운용 (스킵되지만 기본값 제공)
                38: { type: 'radio', value: 'N' }, // 배치 스케줄 없음 → 39~43번 스킵
                39: { type: 'radio_text', radio: 'N', text: '' }, // Batch Schedule Tool 미사용 (스킵되지만 기본값 제공)
                40: { type: 'radio', value: 'N' }, // 배치 스케줄 등록/변경 이력 미기록 (스킵되지만 기본값 제공)
                41: { type: 'radio_textarea', radio: 'N', textarea: '' }, // 배치 스케줄 승인 절차 없음 (스킵되지만 기본값 제공)
                42: { type: 'textarea', value: '' }, // 배치 스케줄 권한자 (스킵되지만 기본값 제공)
                43: { type: 'textarea', value: '' }, // 배치 모니터링 (스킵되지만 기본값 제공)
                44: { type: 'textarea', value: '' }, // 장애 대응 절차
                45: { type: 'textarea', value: '' }, // 백업 절차
                46: { type: 'textarea', value: '' } // 서버실 출입 절차
            };
            
            const sample = skipSamples[questionNumber];
            console.log(`[SKIP SAMPLE] questionNumber: ${questionNumber}, sample:`, sample);
            if (!sample) {
                console.log(`[SKIP SAMPLE] 스킵 샘플 데이터가 없습니다: ${questionNumber} - 자동으로 다음 질문으로 넘어갑니다`);
                // 샘플 데이터가 없으면 자동으로 다음 질문으로 넘어가기
                setTimeout(function() {
                    const submitBtn = document.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        console.log(`[SKIP SAMPLE] 샘플 데이터 없음 - 자동 다음 질문 이동`);
                        submitBtn.click();
                    }
                }, 100);
                return;
            }
            
            // fillSample과 동일한 입력 로직 사용 (빈 값 처리 포함)
            if (sample.type === 'text') {
                if (sample.value === '') {
                    console.log(`[SKIP SAMPLE] 텍스트 값이 비어있음 - 자동으로 다음 질문으로 넘어갑니다`);
                    setTimeout(function() {
                        const submitBtn = document.querySelector('button[type="submit"]');
                        if (submitBtn) submitBtn.click();
                    }, 100);
                    return;
                }
                const input = document.querySelector(`input[name='a${currentIndex}']`);
                if (input) input.value = sample.value;
            }
            if (sample.type === 'radio') {
                if (sample.value === '') {
                    console.log(`[SKIP SAMPLE] 라디오 값이 비어있음 - 자동으로 다음 질문으로 넘어갑니다`);
                    setTimeout(function() {
                        const submitBtn = document.querySelector('button[type="submit"]');
                        if (submitBtn) submitBtn.click();
                    }, 100);
                    return;
                }
                const radio = document.querySelector(`input[name='a${currentIndex}'][value='${sample.value}']`);
                if (radio) radio.checked = true;
            }
            if (sample.type === 'radio_text') {
                const radio = document.querySelector(`input[name='a${currentIndex}'][value='${sample.radio}']`);
                if (radio) radio.checked = true;
                const input = document.querySelector(`input[name='a${currentIndex}_1']`);
                if (input) input.value = sample.text;
            }
            if (sample.type === 'radio_textarea') {
                const radio = document.querySelector(`input[name='a${currentIndex}'][value='${sample.radio}']`);
                if (radio) radio.checked = true;
                const textarea = document.getElementById(`textarea_${currentIndex}`);
                if (textarea) {
                    if (sample.radio === 'Y') {
                        textarea.removeAttribute('readonly');
                        textarea.value = sample.textarea;
                        textarea.required = true;
                        textarea.style.cursor = 'text';
                    } else {
                        textarea.setAttribute('readonly', true);
                        textarea.value = '';
                        textarea.required = false;
                        textarea.style.cursor = 'not-allowed';
                    }
                }
            }
            if (sample.type === 'textarea') {
                const textarea = document.querySelector(`textarea[name='a${currentIndex}']`);
                if (textarea) textarea.value = sample.value;
            }
            if (sample.type === 'skip') {
                console.log(`[SKIP SAMPLE] 질문 ${questionNumber}번은 자동입력하지 않음`);
                return; // 자동입력하지 않고 종료
            }
            
            // 자동으로 다음(제출) 버튼 클릭
            setTimeout(function() {
                const submitBtn = document.querySelector('button[type="submit"]');
                console.log(`[SKIP SAMPLE] 제출 버튼 찾음:`, submitBtn);
                if (submitBtn) {
                    console.log(`[SKIP SAMPLE] 제출 버튼 클릭 실행`);
                    submitBtn.click();
                } else {
                    console.log(`[SKIP SAMPLE] 제출 버튼을 찾을 수 없습니다`);
                }
            }, 100);
        }

        // 단축키: Ctrl+Shift+S로 샘플입력, Ctrl+Shift+D로 스킵샘플 실행
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.shiftKey && (e.key === 's' || e.key === 'S')) {
                e.preventDefault();
                const questionNumber = {{ actual_question_number - 1 if actual_question_number else current_index }};
                const currentIndex = {{ current_index }};
                fillSample(questionNumber, currentIndex);
            }
            if (e.ctrlKey && e.shiftKey && (e.key === 'd' || e.key === 'D')) {
                e.preventDefault();
                const questionNumber = {{ actual_question_number - 1 if actual_question_number else current_index }};
                const currentIndex = {{ current_index }};
                fillSkipSample(questionNumber, currentIndex);
            }
        });

        // 마지막 질문 제출 시 서버에서 AI 검토 선택 페이지로 리디렉션됨
        // JavaScript 인터셉트 제거하여 정상적인 서버 처리 허용
    </script>
</body>
</html>