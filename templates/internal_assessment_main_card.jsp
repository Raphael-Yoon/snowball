<!-- 재사용 가능한 RCM 카드 템플릿 (매크로) - 가로형 컴팩트 버전 -->
{% macro render_rcm_card(item, border_color='info') %}
<div class="assessment-card border-{{ border_color }}">
    <div class="card-body p-3">
        <!-- RCM 기본 정보 (한 줄) -->
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div style="flex: 1; min-width: 0;">
                <h6 class="card-title mb-0 text-truncate">{{ item.rcm_info.rcm_name }}</h6>
                <small class="text-muted">
                    세션: {{ item.evaluation_session }}
                    {% if item.evaluation_status == 'COMPLETED' and item.operation_status == 'COMPLETED' %}
                    <span class="badge bg-success ms-1" style="font-size: 0.65rem;">완료</span>
                    {% elif item.evaluation_status == 'IN_PROGRESS' or item.operation_status == 'IN_PROGRESS' %}
                    <span class="badge bg-primary ms-1" style="font-size: 0.65rem;">진행중</span>
                    {% else %}
                    <span class="badge bg-secondary ms-1" style="font-size: 0.65rem;">대기</span>
                    {% endif %}
                </small>
            </div>
            <div class="text-center ms-2">
                <!-- 진행률 원형 차트 (작게) -->
                <svg class="progress-ring" viewBox="0 0 100 100" style="width: 50px; height: 50px;">
                    <circle class="progress-ring-bg" cx="50" cy="50" r="42"></circle>
                    <circle class="progress-ring-fill" cx="50" cy="50" r="42"
                            style="stroke-dasharray: {{ (item.progress.overall_progress * 264) / 100 }} 264"></circle>
                </svg>
                <div style="font-size: 0.7rem; margin-top: -5px;">
                    <strong class="text-primary">{{ item.progress.overall_progress }}%</strong>
                </div>
            </div>
        </div>

        <!-- 통제 수 (작게) -->
        {% if item.category_counts %}
        <div class="mb-2">
            <div class="d-flex flex-wrap gap-1">
                {% for category, count in item.category_counts.items() %}
                <span class="badge
                    {% if category == 'ITGC' %}bg-info
                    {% elif category == 'ELC' %}bg-warning text-dark
                    {% elif category == 'TLC' %}bg-success
                    {% else %}bg-secondary{% endif %}" style="font-size: 0.65rem;">
                    {% if category == 'ITGC' %}<i class="fas fa-server"></i>
                    {% elif category == 'ELC' %}<i class="fas fa-building"></i>
                    {% elif category == 'TLC' %}<i class="fas fa-exchange-alt"></i>
                    {% endif %}
                    {{ count }}개
                </span>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- 버튼 (2개를 가로로) -->
        <div class="d-flex gap-1">
            <!-- 설계평가 버튼 -->
            {% if item.evaluation_status == 'COMPLETED' %}
                <a href="/user/design-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-outline-success btn-sm flex-fill" style="font-size: 0.75rem; padding: 0.25rem;">
                    <i class="fas fa-check-circle"></i> 설계
                </a>
            {% elif item.evaluation_status == 'IN_PROGRESS' %}
                <a href="/user/design-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-primary btn-sm flex-fill" style="font-size: 0.75rem; padding: 0.25rem;">
                    <i class="fas fa-clipboard-check"></i> 설계
                </a>
            {% else %}
                <a href="/user/design-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-outline-primary btn-sm flex-fill" style="font-size: 0.75rem; padding: 0.25rem;">
                    <i class="fas fa-clipboard-check"></i> 설계
                </a>
            {% endif %}

            <!-- 운영평가 버튼 -->
            {% if item.evaluation_status == 'COMPLETED' %}
                {% if item.operation_status == 'COMPLETED' %}
                    <a href="/user/operation-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-outline-success btn-sm flex-fill" style="font-size: 0.75rem; padding: 0.25rem;">
                        <i class="fas fa-check-circle"></i> 운영
                    </a>
                {% elif item.operation_status == 'IN_PROGRESS' %}
                    <a href="/user/operation-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-success btn-sm flex-fill" style="font-size: 0.75rem; padding: 0.25rem;">
                        <i class="fas fa-cogs"></i> 운영
                    </a>
                {% else %}
                    <a href="/user/operation-evaluation?rcm_id={{ item.rcm_info.rcm_id }}&session={{ item.evaluation_session }}" class="btn btn-outline-success btn-sm flex-fill" style="font-size: 0.75rem; padding: 0.25rem;">
                        <i class="fas fa-cogs"></i> 운영
                    </a>
                {% endif %}
            {% else %}
                <button class="btn btn-outline-secondary btn-sm flex-fill" disabled style="font-size: 0.75rem; padding: 0.25rem;">
                    <i class="fas fa-lock"></i> 운영
                </button>
            {% endif %}
        </div>
    </div>
</div>
{% endmacro %}
