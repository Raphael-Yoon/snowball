{% extends 'link2_1p_base.jsp' %}

{# ================================================================
   CO 섹션 (Q41~Q51)  Computer Operation

   Q41: co_has_batch      (type 1, Y/N) ← 분기점
        N → Q42~Q45 숨김
   Q42: co01_batch_tool   (type 5)
   Q43: co01_batch_history(type 1)
   Q44: co01_procedure    (type 4)
   Q45: co02_batch_auth   (type 5)
   Q46: co03_monitoring   (type 5)
   Q47: co04_incident     (type 5) — Cloud+SOC1 시 숨김 가능
   Q48: co05_backup       (type 5) — Cloud+SOC1 시 숨김
   Q49: co06_server_room  (type 5) — Cloud+SOC1 시 숨김
   Q50: co07_security_patch(type 4) — Cloud+SOC1 시 숨김
   Q51: soc1_review       (type 1) — Cloud 없으면 숨김
================================================================ #}

{% macro yn_field(idx, answers) %}
<input type="hidden" id="q{{ idx }}_hidden" name="q{{ idx }}" value="{{ answers[idx] }}">
<div class="yn-wrap">
    <button type="button" id="q{{ idx }}_yes" onclick="setYN({{ idx }},'Y')"
            class="btn btn-sm {% if answers[idx]=='Y' %}btn-primary{% else %}btn-outline-primary{% endif %}">
        <i class="fas fa-check me-1"></i>예
    </button>
    <button type="button" id="q{{ idx }}_no" onclick="setYN({{ idx }},'N')"
            class="btn btn-sm {% if answers[idx]=='N' %}btn-danger{% else %}btn-outline-danger{% endif %}">
        <i class="fas fa-times me-1"></i>아니요
    </button>
</div>
{% endmacro %}

{% macro type4_field(idx, q, answers, textarea_answers) %}
<div class="mt-1">
    <div class="form-check mb-1">
        <input class="form-check-input" type="radio" name="q{{ idx }}" value="Y"
               id="q{{ idx }}_r_yes" onchange="toggleTextarea4({{ idx }})"
               {% if answers[idx]=='Y' %}checked{% endif %}>
        <label class="form-check-label" for="q{{ idx }}_r_yes">예</label>
    </div>
    <textarea class="form-control" name="q{{ idx }}_text" id="q{{ idx }}_ta"
              placeholder="{{ q.text_help or '관련 절차를 입력하세요.' }}" rows="5"
              {% if answers[idx] != 'Y' %}readonly{% endif %}
              {% if answers[idx] == 'Y' %}required{% endif %}
              style="cursor:{% if answers[idx]=='N' %}not-allowed{% else %}pointer{% endif %};{% if answers[idx]=='N' %}background-color:#e9ecef;{% endif %}"
              onclick="clickTextarea4({{ idx }})">{{ textarea_answers[idx] }}</textarea>
    <div class="form-check mt-1">
        <input class="form-check-input" type="radio" name="q{{ idx }}" value="N"
               id="q{{ idx }}_r_no" onchange="toggleTextarea4({{ idx }})"
               {% if answers[idx]=='N' %}checked{% endif %}>
        <label class="form-check-label" for="q{{ idx }}_r_no">아니요</label>
    </div>
</div>
{% endmacro %}

{% block section_content %}
{% set qs = section_questions %}

{# ── 배치 스케줄 그룹 ── #}
<div class="sub-section-title"><i class="fas fa-clock me-1"></i>배치 스케줄</div>

{# Q41: co_has_batch (type 1) ← 분기점 #}
{% set q = qs[0] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3 border-warning">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52 <span class="badge bg-warning text-dark ms-1">분기</span></div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        {{ yn_field(idx, answers) }}
    </div>
</div>

{# Q42: co01_batch_tool (type 5) #}
{% set q = qs[1] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        <textarea class="form-control" name="q{{ idx }}"
                  placeholder="{{ q.text_help or '사용 중인 배치 스케줄러 도구를 입력하세요.' }}" rows="3">{{ answers[idx] }}</textarea>
    </div>
</div>

{# Q43: co01_batch_history (type 1) #}
{% set q = qs[2] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        {{ yn_field(idx, answers) }}
    </div>
</div>

{# Q44: co01_procedure (type 4) #}
{% set q = qs[3] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        {{ type4_field(idx, q, answers, textarea_answers) }}
    </div>
</div>

{# Q45: co02_batch_auth (type 5) #}
{% set q = qs[4] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        <textarea class="form-control" name="q{{ idx }}"
                  placeholder="{{ q.text_help or '배치 스케줄 등록/변경 권한자를 입력하세요.' }}" rows="3">{{ answers[idx] }}</textarea>
    </div>
</div>

{# Q46: co03_monitoring (type 5) #}
{% set q = qs[5] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        <textarea class="form-control" name="q{{ idx }}" required
                  placeholder="{{ q.text_help or '배치 실행 모니터링 방법을 입력하세요.' }}" rows="4">{{ answers[idx] }}</textarea>
    </div>
</div>

{# ── 운영 통제 그룹 (Q47~Q50) ── Cloud+SOC1 시 숨길 수 있음 #}
<div class="section-divider">
    <div class="sub-section-title"><i class="fas fa-cog me-1"></i>운영 통제</div>
</div>

{# Q47: co04_incident (type 5) #}
{% set q = qs[6] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        <textarea class="form-control" name="q{{ idx }}" required
                  placeholder="{{ q.text_help or '장애 대응 절차를 입력하세요.' }}" rows="5">{{ answers[idx] }}</textarea>
    </div>
</div>

{# Q48: co05_backup (type 5) #}
{% set q = qs[7] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        <textarea class="form-control" name="q{{ idx }}" required
                  placeholder="{{ q.text_help or '백업 수행 및 모니터링 방법을 입력하세요.' }}" rows="4">{{ answers[idx] }}</textarea>
    </div>
</div>

{# Q49: co06_server_room (type 5) #}
{% set q = qs[8] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        <textarea class="form-control" name="q{{ idx }}" required
                  placeholder="{{ q.text_help or '서버실 출입 절차를 입력하세요.' }}" rows="4">{{ answers[idx] }}</textarea>
    </div>
</div>

{# Q50: co07_security_patch (type 4) #}
{% set q = qs[9] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        {{ type4_field(idx, q, answers, textarea_answers) }}
    </div>
</div>

{# ── SOC1 검토 (Q51) ── Cloud 사용 시만 표시 #}
<div class="section-divider">
    <div class="sub-section-title"><i class="fas fa-file-contract me-1"></i>SOC1 Report 검토</div>
</div>

{# Q51: soc1_review (type 1) #}
{% set q = qs[10] %}{% set idx = q.index %}
<div id="qblock_{{ idx }}" class="question-block card mb-3">
    <div class="card-body">
        <div class="q-num">Q{{ idx + 1 }}/52</div>
        <div class="q-text">{{ q.text }}</div>
        {% if q.help %}<div class="q-help mb-2">{{ q.help|safe }}</div>{% endif %}
        {{ yn_field(idx, answers) }}
    </div>
</div>

{% endblock %}


{% block section_scripts %}
<script>
const _cloudType = '{{ answers[Q_ID["cloud_type"]] }}';
const _soc1      = '{{ answers[Q_ID["soc1_report"]] }}';
const _useCloud  = '{{ answers[Q_ID["use_cloud"]] }}';

function applyConditions() {
    const hasSoc1Cond = ((_cloudType === 'IaaS' || _cloudType === 'PaaS' || _cloudType === 'SaaS') && _soc1 === 'Y');

    // ── 배치 분기 ──────────────────────────────────────────────────
    const hasBatch = getVal(41);
    toggleRange(42, 45, hasBatch === 'Y');

    // ── 운영 통제 (Q47~Q50): Cloud+SOC1 시 숨김 ───────────────────
    toggleRange(47, 50, !hasSoc1Cond);

    // ── SOC1 Review (Q51): Cloud 사용 시만 표시 ────────────────────
    toggleQ(51, _useCloud === 'Y');
}

function fillAllSamples() {
    setYN(41, 'Y');  // co_has_batch
    document.querySelector('textarea[name="q42"]').value = 'Control-M';
    setYN(43, 'Y');  // batch_history
    setYN(44, 'Y');  document.getElementById('q44_ta').value = 'IT팀장 승인 후 배치 등록';
    document.querySelector('textarea[name="q45"]').value = '배치운영팀 이몽룡 과장';
    document.querySelector('textarea[name="q46"]').value = '매일 오전 7시 배치 결과 확인 및 오류 시 담당자 알림';
    document.querySelector('textarea[name="q47"]').value = '장애 발생 시 에스컬레이션 절차에 따라 대응';
    document.querySelector('textarea[name="q48"]').value = '매일 자정 전체 백업, 완료 후 알림 메일 발송';
    document.querySelector('textarea[name="q49"]').value = '신분증 확인 및 출입자 명부 작성 후 출입 가능';
    setYN(50, 'Y');  document.getElementById('q50_ta').value = '월 1회 보안 패치 현황 점검 및 적용';
    setYN(51, 'N');  // soc1_review
    applyConditions();
}

document.addEventListener('DOMContentLoaded', applyConditions);
</script>
{% endblock %}
