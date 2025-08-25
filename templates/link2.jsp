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
            </div>
        </div>

        <!-- 섹션 제목 -->
        <div class="text-center mt-3">
            <h1 class="section-title">
                {% if 0 <= current_index <= 11 %}
                    <i class="fas fa-server"></i> 공통사항
                {% elif 12 <= current_index <= 30 %}
                    <i class="fas fa-lock"></i> APD(Access to Program & Data)
                {% elif 31 <= current_index <= 36 %}
                    <i class="fas fa-laptop-code"></i> PC(Program Change)
                {% elif 37 <= current_index <= 43 %}
                    <i class="fas fa-cogs"></i> CO(Computer Operation)
                {% else %}
                    <i class="fas fa-check-circle"></i> 모든 질문이 완료되었습니다.
                {% endif %}
            </h1>
        </div>

        <div class="text-center mt-4">
            {% if remote_addr == '127.0.0.1' or (user_info and user_info.get('admin_flag') == 'Y') %}
            <button type="button" class="btn btn-outline-secondary me-2" onclick="fillSample({{ current_index }})">
                <i class="fas fa-magic"></i> 샘플입력
            </button>
            {% endif %}
            
            <!-- 디버그용: admin_flag 확인 버튼 -->
            <button type="button" class="btn btn-outline-info btn-sm" onclick="debugAdminFlag()">
                <i class="fas fa-bug"></i> 디버그
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
                        {% if question.answer_type == '0' %}
                            <select class="form-select" name="a0" required>
                                <option value="">담당자를 선택하세요</option>
                                {# {% for i in range(0, users|length, 3) %}
                                    <option value="{{ users[i+2] }}" {% if answer[0] == users[i+2] %}selected{% endif %}>{{ users[i] }} - {{ users[i+1] }}</option>
                                {% endfor %} #}
                                <input type="text" class="form-control" name="a0_text" placeholder="e-Mail 주소를 입력하세요" value="{{ answer[0] }}" />
                            </select>
                        {% elif question.answer_type == '2' %}
                            <input type="text" class="form-control" name="a{{ current_index }}" required placeholder="{{ question.text_help if question.text_help else '' }}" value="{{ answer[current_index] }}">
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
                            <textarea class="form-control mt-2" name="a{{ current_index }}_1" id="textarea_{{ current_index }}" placeholder="{{ question.text_help if question.text_help else '관련 절차를 입력하세요.' }}" rows="5" {% if answer[current_index] != 'Y' %}readonly{% endif %} onclick="selectYesAndEnableTextarea({{ current_index }})" style="cursor: pointer;">{{ textarea_answer[current_index] }}</textarea>
                            <label class="form-check">
                                <input type="radio" class="form-check-input" name="a{{ current_index }}" value="N" onchange="toggleTextarea({{ current_index }})" {% if answer[current_index] == 'N' %}checked{% endif %}>
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
                0: { type: 'text', value: 'snowball2727@naver.com' }, // 산출물을 전달받을 e-Mail 주소를 입력해주세요.
                1: { type: 'text', value: 'Amidas' }, // 시스템 이름을 적어주세요.
                2: { type: 'radio_text', radio: 'Y', text: 'SAP ERP' }, // 사용하고 있는 시스템은 상용소프트웨어입니까?
                3: { type: 'radio', value: 'Y' }, // 주요 로직을 회사내부에서 수정하여 사용할 수 있습니까?
                4: { type: 'radio', value: 'N' }, // Cloud 서비스를 사용하고 있습니까?
                5: { type: 'radio', value: 'Y' }, // 어떤 종류의 Cloud입니까?
                6: { type: 'radio', value: 'Y' }, // Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까?
                7: { type: 'text', value: 'Linux Redhat 8' }, // OS 종류와 버전을 작성해 주세요.
                8: { type: 'radio_text', radio: 'Y', text: 'Hiware' }, // OS 접근제어 Tool을 사용하고 있습니까?
                9: { type: 'text', value: 'Oracle 19c' }, // DB 종류와 버전을 작성해 주세요.
                10: { type: 'radio_text', radio: 'Y', text: 'DB Safer' }, // DB 접근제어 Tool을 사용하고 있습니까?
                11: { type: 'radio_text', radio: 'N', text: '' }, // 별도의 Batch Schedule Tool을 사용하고 있습니까?
                12: { type: 'radio', value: 'Y' }, // 사용자 권한부여 이력이 시스템에 기록되고 있습니까?
                13: { type: 'radio', value: 'Y' }, // 사용자 권한회수 이력이 시스템에 기록되고 있습니까?
                14: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM로 요청서 작성하고 부서장의 승인을 득함' }, // 사용자가 새로운 권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                15: { type: 'radio_textarea', radio: 'N', textarea: ' ' }, // 부서이동 등 기존권한의 회수가 필요한 경우 기존 권한을 회수하는 절차가 있습니까?
                16: { type: 'radio_textarea', radio: 'Y', textarea: '시스템에서 자동 권한 회수' }, // 퇴사자 발생시 접근권한을 차단하는 절차가 있습니까?
                17: { type: 'textarea', value: 'IT운영팀 조윤진 책임' }, // Application 관리자(Superuser) 권한을 보유한 인원에 대해 기술해 주세요.
                18: { type: 'radio_textarea', radio: 'Y', textarea: '분기별로 전체 사용자 권한에 대해 검토함' }, // 전체 사용자가 보유한 권한에 대한 적절성을 모니터링하는 절차가 있습니까?
                19: { type: 'textarea', value: '최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일' }, // 패스워드 설정사항을 기술해 주세요.
                20: { type: 'radio', value: 'Y' }, // 데이터 변경 이력이 시스템에 기록되고 있습니까?
                21: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성하고 부서장의 승인을 득함' }, // 데이터 변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                22: { type: 'textarea', value: 'IT운영팀 윤소영 책임' }, // 데이터 변경 권한을 보유한 인원에 대해 기술해 주세요.
                23: { type: 'radio', value: 'Y' }, // DB 접근권한 부여 이력이 시스템에 기록되고 있습니까?
                24: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성하고 부서장의 승인을 득함' }, // DB 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                25: { type: 'textarea', value: '인프라관리팀 심범석 차장' }, // DB 관리자 권한을 보유한 인원에 대해 기술해 주세요.
                26: { type: 'textarea', value: '최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일' }, // DB 패스워드 설정사항을 기술해 주세요.
                27: { type: 'radio', value: 'Y' }, // OS 접근권한 부여 이력이 시스템에 기록되고 있습니까?
                28: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성하고 부서장의 승인을 득함' }, // OS 접근권한이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                29: { type: 'textarea', value: '인프라관리팀 손현호 차장' }, // OS 관리자 권한을 보유한 인원에 대해 기술해 주세요.
                30: { type: 'textarea', value: '최소자리: 8, 복잡성: 영문/숫자/특수문자, 변경주기: 90일' }, // OS 패스워드 설정사항을 기술해 주세요.
                31: { type: 'radio', value: 'N' }, // 프로그램 변경 이력이 시스템에 기록되고 있습니까?
                32: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성하고 부서장의 승인을 득함' }, // 프로그램 변경이 필요한 경우 요청서를 작성하고 부서장의 승인을 득하는 절차가 있습니까?
                33: { type: 'radio_textarea', radio: 'Y', textarea: '요청자에 의해 사용자 테스트 완료 하고 결과를 문서화함' }, // 프로그램 변경시 사용자 테스트를 수행하고 그 결과를 문서화하는 절차가 있습니까?
                34: { type: 'radio_textarea', radio: 'Y', textarea: '이관 요청서 작성 후 부서장의 승인을 득함' }, // 프로그램 변경 완료 후 이관(배포)을 위해 부서장 등의 승인을 득하는 절차가 있습니까?
                35: { type: 'textarea', value: '인프라관리팀 윤대호 차장' }, // 이관(배포)권한을 보유한 인원에 대해 기술해 주세요.
                36: { type: 'radio', value: 'Y' }, // 운영서버 외 별도의 개발 또는 테스트 서버를 운용하고 있습니까?
                37: { type: 'radio', value: 'Y' }, // 배치 스케줄 등록/변경 이력이 시스템에 기록되고 있습니까?
                38: { type: 'radio_textarea', radio: 'Y', textarea: 'ITSM 요청서 작성 후 부서장의 승인을 득함' }, // 배치 스케줄 등록/변경이 필요한 경우 요청서를 작성하고 부서장 등의 승인을 득하는 절차가 있습니까?
                39: { type: 'textarea', value: '시스템 운영팀 신혁수 과장' }, // 배치 스케줄을 등록/변경할 수 있는 인원에 대해 기술해 주세요.
                40: { type: 'textarea', value: '매일 아침 배치수행결과 확인 및 문서화' }, // 배치 실행 오류 등에 대한 모니터링은 어떻게 수행되고 있는지 기술해 주세요.
                41: { type: 'textarea', value: '적당히 알아서 함' }, // 장애 발생시 이에 대응하고 조치하는 절차에 대해 기술해 주세요.
                42: { type: 'textarea', value: '내가 알아서 함' }, // 백업은 어떻게 수행되고 또 어떻게 모니터링되고 있는지 기술해 주세요.
                43: { type: 'textarea', value: '못들어가게 막음' } // 서버실 출입시의 절차에 대해 기술해 주세요.
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

        // 마지막 질문 제출 시 서버에서 AI 검토 선택 페이지로 리디렉션됨
        // JavaScript 인터셉트 제거하여 정상적인 서버 처리 허용
        
        // 디버그용 함수
        function debugAdminFlag() {
            const userInfo = {{ user_info | tojson if user_info else 'null' }};
            const remoteAddr = '{{ remote_addr }}';
            const isLoggedIn = {{ 'true' if is_logged_in else 'false' }};
            
            let debugMsg = '=== 디버그 정보 ===\n';
            debugMsg += `로그인 상태: ${isLoggedIn}\n`;
            debugMsg += `접속 IP: ${remoteAddr}\n`;
            
            if (userInfo) {
                debugMsg += `사용자 이름: ${userInfo.user_name}\n`;
                debugMsg += `이메일: ${userInfo.user_email}\n`;
                debugMsg += `관리자 플래그: ${userInfo.admin_flag}\n`;
                debugMsg += `회사명: ${userInfo.company_name || '없음'}\n`;
                
                const showSample = (remoteAddr === '127.0.0.1') || (userInfo.admin_flag === 'Y');
                debugMsg += `샘플 버튼 표시 조건: ${showSample}`;
            } else {
                debugMsg += '사용자 정보: 없음';
            }
            
            alert(debugMsg);
        }
    </script>
</body>
</html>