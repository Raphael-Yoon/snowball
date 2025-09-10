<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>내부평가 - SnowBall</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .assessment-card {
            border: 1px solid #e9ecef;
            border-radius: 12px;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
        }
        .assessment-card:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .progress-ring {
            width: 80px;
            height: 80px;
        }
        .progress-ring-bg {
            fill: transparent;
            stroke: #e9ecef;
            stroke-width: 8;
        }
        .progress-ring-fill {
            fill: transparent;
            stroke: #28a745;
            stroke-width: 8;
            stroke-linecap: round;
            transition: stroke-dasharray 0.5s ease-in-out;
        }
        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
            position: relative;
        }
        .step-item {
            flex: 1;
            text-align: center;
            position: relative;
        }
        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            font-weight: bold;
            position: relative;
            z-index: 2;
        }
        .step-item.completed .step-number {
            background-color: #28a745;
            color: white;
        }
        .step-item.in-progress .step-number {
            background-color: #007bff;
            color: white;
        }
        .step-item.pending .step-number {
            background-color: #f8f9fa;
            color: #6c757d;
            border: 2px solid #dee2e6;
        }
        .step-connector {
            position: absolute;
            top: 20px;
            left: 50%;
            right: -50%;
            height: 2px;
            background-color: #dee2e6;
            z-index: 1;
        }
        .step-item:last-child .step-connector {
            display: none;
        }
        .step-item.completed .step-connector {
            background-color: #28a745;
        }
    </style>
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-tasks me-2 text-primary"></i>내부평가</h1>
                    <div>
                        <a href="{{ url_for('link5.user_rcm') }}" class="btn btn-outline-secondary">
                            <i class="fas fa-arrow-left me-1"></i>RCM 목록으로
                        </a>
                    </div>
                </div>
                <p class="text-muted mb-4">
                    RCM의 단계별 내부평가를 진행하여 통제 설계와 운영 효과성을 체계적으로 검토할 수 있습니다.
                </p>
            </div>
        </div>

        <!-- 내부평가 진행 현황 -->
        <div class="row">
            {% if assessment_progress %}
                {% for item in assessment_progress %}
                <div class="col-lg-6 col-xl-4 mb-4">
                    <div class="assessment-card">
                        <div class="card-body p-4">
                            <!-- RCM 기본 정보 -->
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                    <h5 class="card-title mb-1">{{ item.rcm_info.rcm_name }}</h5>
                                    <small class="text-muted">
                                        <i class="fas fa-building me-1"></i>{{ item.rcm_info.company_name }}
                                    </small>
                                </div>
                                <div class="text-center">
                                    <!-- 진행률 원형 차트 -->
                                    <svg class="progress-ring" viewBox="0 0 100 100">
                                        <circle class="progress-ring-bg" cx="50" cy="50" r="42"></circle>
                                        <circle class="progress-ring-fill" cx="50" cy="50" r="42"
                                                style="stroke-dasharray: {{ (item.progress.overall_progress * 264) / 100 }} 264"></circle>
                                    </svg>
                                    <div class="mt-2">
                                        <strong class="text-primary">{{ item.progress.overall_progress }}%</strong>
                                        <br>
                                        <small class="text-muted">완료</small>
                                    </div>
                                </div>
                            </div>

                            <!-- 단계 진행 상황 표시 -->
                            <div class="step-indicator mb-3">
                                {% for step in item.progress.steps[:3] %}
                                <div class="step-item {{ step.status }}">
                                    <div class="step-number">{{ step.step }}</div>
                                    <div class="step-connector"></div>
                                    <small class="text-muted">{{ step.name[:4] }}</small>
                                </div>
                                {% endfor %}
                            </div>

                            <!-- 현재 진행 단계 -->
                            <div class="mb-3">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="text-muted">현재 단계:</span>
                                    <span class="badge bg-primary">
                                        {{ item.progress.steps[item.progress.current_step - 1].name }}
                                    </span>
                                </div>
                            </div>

                            <!-- 액션 버튼 -->
                            <div class="d-grid gap-2">
                                <a href="{{ url_for('link9.assessment_detail', rcm_id=item.rcm_info.rcm_id) }}" 
                                   class="btn btn-primary">
                                    <i class="fas fa-chart-line me-1"></i>평가 진행하기
                                </a>
                                {% if item.progress.overall_progress > 0 %}
                                <a href="{{ url_for('link9.assessment_detail', rcm_id=item.rcm_info.rcm_id) }}" 
                                   class="btn btn-outline-info btn-sm">
                                    <i class="fas fa-eye me-1"></i>진행 상황 보기
                                </a>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <!-- 빈 상태 -->
                <div class="col-12">
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i class="fas fa-tasks text-muted" style="font-size: 4rem;"></i>
                        </div>
                        <h4 class="text-muted mb-3">내부평가할 RCM이 없습니다</h4>
                        <p class="text-muted mb-4">
                            내부평가를 진행하려면 먼저 RCM을 등록하고 접근 권한을 받아야 합니다.
                        </p>
                        <a href="{{ url_for('link5.user_rcm') }}" class="btn btn-primary">
                            <i class="fas fa-database me-1"></i>RCM 관리로 이동
                        </a>
                    </div>
                </div>
            {% endif %}
        </div>

        <!-- 내부평가 가이드 -->
        <div class="row mt-5">
            <div class="col-12">
                <div class="card border-info">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>내부평가 단계별 가이드</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="text-primary">📋 1단계: 평가 계획 수립</h6>
                                <ul class="list-unstyled mb-3">
                                    <li><i class="fas fa-check-circle text-success me-2"></i>평가 범위 및 목적 정의</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>평가 일정 및 담당자 지정</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>평가 방법론 및 기준 설정</li>
                                </ul>

                                <h6 class="text-primary">🎯 2단계: 통제 설계 평가</h6>
                                <ul class="list-unstyled mb-3">
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제 설계의 적절성 검토</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제 목적과 실제 설계 일치성 확인</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제 환경 및 전제조건 검토</li>
                                </ul>

                                <h6 class="text-primary">⚡ 3단계: 운영 효과성 평가</h6>
                                <ul class="list-unstyled mb-3">
                                    <li><i class="fas fa-check-circle text-success me-2"></i>통제의 실제 운영 상태 확인</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>운영 빈도 및 일관성 검토</li>
                                    <li><i class="fas fa-check-circle text-success me-2"></i>운영 증거 및 문서화 상태 평가</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-danger">🔍 4단계: 결함 식별 및 평가</h6>
                                <ul class="list-unstyled mb-3">
                                    <li><i class="fas fa-exclamation-triangle text-warning me-2"></i>통제 결함 및 예외사항 식별</li>
                                    <li><i class="fas fa-exclamation-triangle text-warning me-2"></i>결함의 중요도 및 영향도 평가</li>
                                    <li><i class="fas fa-exclamation-triangle text-warning me-2"></i>근본 원인 분석 수행</li>
                                </ul>

                                <h6 class="text-warning">📈 5단계: 개선 계획 수립</h6>
                                <ul class="list-unstyled mb-3">
                                    <li><i class="fas fa-lightbulb text-warning me-2"></i>결함 해결을 위한 개선 방안 도출</li>
                                    <li><i class="fas fa-lightbulb text-warning me-2"></i>개선 우선순위 및 일정 수립</li>
                                    <li><i class="fas fa-lightbulb text-warning me-2"></i>개선 효과 측정 방법 정의</li>
                                </ul>

                                <h6 class="text-secondary">📄 6단계: 평가 보고서 작성</h6>
                                <ul class="list-unstyled mb-0">
                                    <li><i class="fas fa-file-alt text-secondary me-2"></i>평가 결과 종합 및 정리</li>
                                    <li><i class="fas fa-file-alt text-secondary me-2"></i>경영진 보고용 요약 작성</li>
                                    <li><i class="fas fa-file-alt text-secondary me-2"></i>후속 조치 및 모니터링 계획</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>