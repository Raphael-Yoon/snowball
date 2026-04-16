<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snowball - ITGC interview ({{ section_info.name }})</title>
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
    <style>
        .section-steps { display: flex; justify-content: center; gap: 0.5rem; margin: 1.5rem 0 2rem; flex-wrap: wrap; }
        .step { display: flex; flex-direction: column; align-items: center; padding: 0.6rem 1.2rem; border-radius: 0.5rem; border: 2px solid #dee2e6; color: #adb5bd; min-width: 120px; font-size: 0.85rem; transition: all 0.2s; text-decoration: none; }
        .step i { font-size: 1.3rem; margin-bottom: 0.2rem; }
        .step.completed { border-color: #198754; color: #198754; background: #d1e7dd; cursor: pointer; }
        .step.active { border-color: #0d6efd; color: #0d6efd; background: #e7f1ff; font-weight: 600; }
        .question-block { margin-bottom: 1.2rem; }
        .question-block.hidden { display: none !important; }
        .q-num { color: #6c757d; font-size: 0.8rem; font-weight: 500; margin-bottom: 0.25rem; }
        .q-text { font-weight: 600; font-size: 0.98rem; margin-bottom: 0.5rem; }
        .yn-wrap { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem; }
        .yn-wrap .btn { width: 80px !important; }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}
    <div class="container mt-4">
        <div class="section-steps">
            {% for s_key in section_order %}
                {% set s = sections[s_key] %}
                <a href="{{ url_for('link2.itgc_interview', section=s_key) }}" 
                   class="step {% if s_key == section_name %}active{% elif loop.index0 < cur_section_idx %}completed{% endif %}">
                    <i class="fas {{ s.icon }}"></i>
                    <span>{{ s.name }}</span>
                </a>
            {% endfor %}
        </div>


        <h2><i class="fas {{ section_info.icon }} me-2"></i>{{ section_info.name }}</h2>
        
        <!-- 관리자용 샘플 입력 -->
        {% if remote_addr == '127.0.0.1' or (user_info and user_info.get('admin_flag') == 'Y') %}
        <div class="mb-3">
            <button type="button" class="btn btn-outline-secondary btn-sm me-2" onclick="fillAllSamples()">
                <i class="fas fa-magic"></i> 샘플입력
            </button>
        </div>
        {% endif %}
        

        <form id="sectionForm" action="{{ url_for('link2.itgc_interview', section=section_name) }}" method="post">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
            
            <div id="questions-container">
                {% for q in section_questions %}
                    {% set idx = q.index %}
                    <div id="qblock_{{ idx }}" class="card mb-3 question-block shadow-sm">
                        <div class="card-body">
                            <div class="q-num text-primary">Q{{ idx + 1 }}</div>
                            <div class="q-text h5 mb-3">{{ q.text }}</div>
                            
                            {% if q.type == 1 %}
                                {# Y/N buttons #}
                                <input type="hidden" id="q{{ idx }}_hidden" name="q{{ idx }}" value="{{ answers[idx] }}">
                                <div class="yn-wrap">
                                    <button type="button" id="q{{ idx }}_yes" onclick="setYN({{ idx }},'Y')"
                                            class="btn btn-sm {% if answers[idx]=='Y' %}btn-primary{% else %}btn-outline-secondary{% endif %}">
                                        <i class="fas fa-check me-1"></i>예
                                    </button>
                                    <button type="button" id="q{{ idx }}_no" onclick="setYN({{ idx }},'N')"
                                            class="btn btn-sm {% if answers[idx]=='N' %}btn-primary{% else %}btn-outline-secondary{% endif %}">
                                        <i class="fas fa-times me-1"></i>아니요
                                    </button>
                                </div>
                            {% elif q.type == 2 %}
                                {# Text input #}
                                <input type="text" name="q{{ idx }}" id="q{{ idx }}" class="form-control" value="{{ answers[idx] }}" 
                                       placeholder="{{ q.text_help or '' }}" {% if idx==0 and is_logged_in %}readonly{% endif %}>
                            {% elif q.type == 4 %}
                                {# Y/N radio + text area #}
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="q{{ idx }}" value="Y" 
                                           id="q{{ idx }}_ry" onchange="toggleTA({{ idx }}, true)" {% if answers[idx]=='Y' %}checked{% endif %}>
                                    <label class="form-check-label" for="q{{ idx }}_ry">예</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="q{{ idx }}" value="N" 
                                           id="q{{ idx }}_rn" onchange="toggleTA({{ idx }}, false)" {% if answers[idx]=='N' %}checked{% endif %}>
                                    <label class="form-check-label" for="q{{ idx }}_rn">아니요</label>
                                </div>
                                <div id="ta_wrap_{{ idx }}" class="mt-2 {% if answers[idx]!='Y' %}d-none{% endif %}">
                                    <textarea name="q{{ idx }}_text" class="form-control" rows="3">{{ textarea_answers[idx] }}</textarea>
                                </div>
                            {% elif q.type == 5 %}
                                {# Long text area #}
                                <textarea name="q{{ idx }}" id="q{{ idx }}" class="form-control" rows="4">{{ answers[idx] }}</textarea>
                            {% elif q.type == 6 %}
                                {# Radio options #}
                                {% for opt in q.text_help.split('|') %}
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="q{{ idx }}" value="{{ opt }}" 
                                               id="q{{ idx }}_{{ opt }}" {% if answers[idx]==opt %}checked{% endif %}>
                                        <label class="form-check-label" for="q{{ idx }}_{{ opt }}">{{ opt }}</label>
                                    </div>
                                {% endfor %}
                            {% endif %}

                            {% if q.help %}
                                <div class="alert alert-light mt-3 py-2 small border-start border-4 border-info">
                                    <i class="fas fa-info-circle text-info me-2"></i>{{ q.help|safe }}
                                </div>
                            {% endif %}
                        </div>
                    </div>
                {% endfor %}
            </div>

            <div class="d-flex justify-content-between mt-4">
                <button type="submit" name="action" value="prev" class="btn btn-outline-secondary">이전</button>
                <button type="submit" name="action" value="next" class="btn btn-primary">
                    {{ '완료 및 제출' if is_last else '다음' }}
                </button>
            </div>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function getVal(idx) {
            const hidden = document.getElementById(`q${idx}_hidden`);
            if (hidden) return hidden.value;
            const checked = document.querySelector(`input[name="q${idx}"]:checked`);
            if (checked) return checked.value;
            const el = document.querySelector(`input[name="q${idx}"]`);
            return el ? el.value : '';
        }

        function setYN(idx, value) {
            const hidden = document.getElementById(`q${idx}_hidden`);
            if (hidden) hidden.value = value;
            const yes = document.getElementById(`q${idx}_yes`);
            const no = document.getElementById(`q${idx}_no`);
            if (yes) {
                yes.classList.toggle('btn-primary', value === 'Y');
                yes.classList.toggle('btn-outline-secondary', value !== 'Y');
            }
            if (no) {
                no.classList.toggle('btn-primary', value === 'N');
                no.classList.toggle('btn-outline-secondary', value !== 'N');
            }
            if (typeof applyConditions === 'function') applyConditions();
        }

        function toggleQ(idx, show) {
            const el = document.getElementById(`qblock_${idx}`);
            if (el) el.classList.toggle('hidden', !show);
        }

        function toggleRange(start, end, show) {
            for (let i = start; i <= end; i++) toggleQ(i, show);
        }

        function toggleTA(idx, show) {
            const wrap = document.getElementById(`ta_wrap_${idx}`);
            if (wrap) wrap.classList.toggle('d-none', !show);
        }

        function fillAllSamples() {
            const sn = "{{ section_name }}";
            if (sn === 'common') {
                document.querySelector('input[name="q0"]').value = 'test@example.com';
                document.querySelector('input[name="q1"]').value = '테스트 시스템';
                setYN(2, 'Y');
                setYN(3, 'Y');
                const r4 = document.getElementById('q4_IaaS'); if(r4) r4.checked = true;
                const r5n = document.getElementById('q5_rn'); if(r5n) { r5n.checked = true; toggleTA(5, false); }
            } else if (sn === 'apd') {
                setYN(6, 'Y');
                document.querySelector('input[name="q7"][value="N"]').checked = true;
            }
            // Add other sections as needed...
            if (typeof applyConditions === 'function') applyConditions();
        }

        function applyConditions() {
            const sn = '{{ section_name }}';
            
            // Clean URL for better UX (hide /section/ in address bar if present)
            if (window.location.pathname.includes('/section/')) {
                const baseUrl = "{{ url_for('link2.itgc_interview') }}";
                window.history.replaceState({}, '', baseUrl);
            }

            if (sn === 'common') {
                const useCloud = getVal(3);
                toggleQ(4, useCloud === 'Y');
                toggleQ(5, useCloud === 'Y');
            } else if (sn === 'apd') {
                const q6 = getVal(6);
                toggleQ(9, q6 === 'N');
                toggleRange(10, 12, q6 === 'Y');
                
                const q16 = getVal(16);
                toggleRange(17, 25, q16 === 'Y');
                
                const q26 = getVal(26);
                toggleRange(27, 32, q26 === 'Y');
            }
        }

        document.addEventListener('DOMContentLoaded', applyConditions);
    </script>
</body>
</html>
