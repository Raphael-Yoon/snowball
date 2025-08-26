<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>운영평가</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-cogs me-2"></i>운영평가</h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="fas fa-home me-1"></i>홈으로
                    </a>
                </div>
                <hr>
            </div>
        </div>

        <!-- 운영평가 소개 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-info-circle me-2"></i>운영평가란?</h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">
                            <strong>운영평가(Operating Effectiveness Testing)</strong>는 통제가 실제로 의도된 대로 작동하고 있는지를 평가하는 과정입니다.
                        </p>
                        <ul>
                            <li><strong>목적:</strong> 통제가 일정 기간 동안 일관되게 효과적으로 운영되고 있는지 검증</li>
                            <li><strong>범위:</strong> 통제의 실행, 모니터링, 예외 처리 등 운영 현황 전반</li>
                            <li><strong>결과:</strong> 운영 효과성 결론 및 운영상 개선점 도출</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- 운영평가 기능들 -->
        <div class="row g-4">
            <!-- 표본 기반 운영평가 -->
            <div class="col-lg-6 col-md-12">
                <div class="card h-100">
                    <div class="card-header">
                        <h6><i class="fas fa-chart-bar me-2"></i>표본 기반 운영평가</h6>
                    </div>
                    <div class="card-body">
                        <p>통계적 표본 추출을 통한 체계적인 운영평가를 수행합니다.</p>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-warning me-2"></i>표본 크기 결정</li>
                            <li><i class="fas fa-check text-warning me-2"></i>무작위 표본 추출</li>
                            <li><i class="fas fa-check text-warning me-2"></i>통계적 결론 도출</li>
                        </ul>
                        <div class="d-grid">
                            <a href="/user/operation-evaluation/sampling" class="btn btn-warning">
                                <i class="fas fa-chart-line me-1"></i>표본 평가 시작
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 전수 검사 운영평가 -->
            <div class="col-lg-6 col-md-12">
                <div class="card h-100">
                    <div class="card-header">
                        <h6><i class="fas fa-list-check me-2"></i>전수 검사 운영평가</h6>
                    </div>
                    <div class="card-body">
                        <p>모든 거래나 사건에 대한 전수 검사를 통한 운영평가입니다.</p>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-check text-danger me-2"></i>100% 검사 수행</li>
                            <li><i class="fas fa-check text-danger me-2"></i>완전한 결론 도출</li>
                            <li><i class="fas fa-check text-danger me-2"></i>예외사항 완전 식별</li>
                        </ul>
                        <div class="d-grid">
                            <a href="/user/operation-evaluation/full" class="btn btn-danger">
                                <i class="fas fa-tasks me-1"></i>전수 평가 시작
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 평가 진행 현황 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-tasks me-2"></i>진행 중인 운영평가</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center py-4">
                            <i class="fas fa-hourglass-half fa-2x text-muted mb-2"></i>
                            <p class="text-muted">진행 중인 운영평가가 없습니다.</p>
                            <small class="text-muted">새로운 운영평가를 시작하면 여기에 진행 상황이 표시됩니다.</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 최근 평가 결과 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-history me-2"></i>최근 운영평가 결과</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center py-4">
                            <i class="fas fa-clipboard-list fa-2x text-muted mb-2"></i>
                            <p class="text-muted">완료된 운영평가가 없습니다.</p>
                            <small class="text-muted">운영평가를 완료하면 여기에 결과가 표시됩니다.</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 운영평가 방법론 -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-book me-2"></i>운영평가 방법론</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <h6 class="text-primary">관찰(Observation)</h6>
                                <p class="small">통제 활동이 실제로 수행되는 모습을 관찰</p>
                            </div>
                            <div class="col-md-3">
                                <h6 class="text-success">조회(Inquiry)</h6>
                                <p class="small">통제 담당자와의 면담을 통한 정보 수집</p>
                            </div>
                            <div class="col-md-3">
                                <h6 class="text-warning">검사(Inspection)</h6>
                                <p class="small">문서나 기록의 존재와 내용 검토</p>
                            </div>
                            <div class="col-md-3">
                                <h6 class="text-danger">재실행(Re-performance)</h6>
                                <p class="small">통제 절차의 독립적 재수행</p>
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