<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RCM 운영평가 - {{ rcm_info.rcm_name }}</title>
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
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
                    <div>
                        <h1><i class="fas fa-cogs me-2"></i>RCM 운영평가</h1>
                        <div class="text-warning fw-bold fs-6 mt-1">
                            설계평가 세션: <span class="badge bg-warning text-dark">{{ evaluation_session }}</span>
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-info" onclick="viewDesignEvaluation()">
                            <i class="fas fa-drafting-compass me-1"></i>설계평가 보기
                        </button>
                        <a href="/user/operation-evaluation" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-1"></i>목록으로
                        </a>
                    </div>
                </div>
                <hr>
            </div>
        </div>

        <!-- RCM 기본 정보 -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-warning">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-info-circle me-2"></i>RCM 기본 정보</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="40%">RCM명:</th>
                                        <td><strong>{{ rcm_info.rcm_name }}</strong></td>
                                    </tr>
                                    <tr>
                                        <th>회사명:</th>
                                        <td>{{ rcm_info.company_name }}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-4">
                                <table class="table table-borderless">
                                    <tr>
                                        <th width="40%">총 통제 수:</th>
                                        <td><span class="badge bg-warning text-dark">{{ rcm_details|length }}개</span></td>
                                    </tr>
                                    <tr>
                                        <th>평가자:</th>
                                        <td><strong>{{ user_info.user_name }}</strong></td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center">
                                    <h6 class="text-warning">운영평가 진행률</h6>
                                    <div class="progress mb-2" style="height: 20px;">
                                        <div class="progress-bar bg-warning" id="evaluationProgress" role="progressbar" style="width: 0%; font-size: 12px;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                                    </div>
                                    <small class="text-muted">
                                        <span id="evaluatedCount">0</span> / <span id="totalControlCount">{{ rcm_details|length }}</span> 통제 평가 완료
                                        <br>상태: <span id="evaluationStatus" class="badge bg-secondary">준비 중</span>
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 운영평가 통제 목록 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-list me-2"></i>통제 운영평가</h5>
                        <div class="d-flex flex-wrap gap-2">
                            <button id="completeEvaluationBtn" class="btn btn-sm btn-warning" onclick="completeEvaluation()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;" title="운영평가를 완료 처리합니다" data-bs-toggle="tooltip">
                                <i class="fas fa-check me-1"></i>완료처리
                            </button>
                            <button id="downloadBtn" class="btn btn-sm btn-outline-warning" onclick="exportEvaluationResult()" style="display: none; height: 70%; padding: 0.2rem 0.5rem;">
                                <i class="fas fa-file-excel me-1"></i>다운로드
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        {% if rcm_details %}
                        <div class="table-responsive">
                            <table class="table table-striped" id="controlsTable">
                                <thead>
                                    <tr>
                                        <th width="8%">통제코드</th>
                                        <th width="14%">통제명</th>
                                        <th width="22%">통제활동설명</th>
                                        <th width="7%">통제주기</th>
                                        <th width="7%">통제유형</th>
                                        <th width="7%">통제구분</th>
                                        <th width="10%">운영평가</th>
                                        <th width="10%">평가결과</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for detail in rcm_details %}
                                    <tr id="control-row-{{ loop.index }}">
                                        <td><code>{{ detail.control_code }}</code></td>
                                        <td><strong>{{ detail.control_name }}</strong></td>
                                        <td>
                                            <div style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; max-height: calc(1.4em * 2);"
                                                 title="{{ detail.control_description or '-' }}" data-bs-toggle="tooltip">
                                                {{ detail.control_description or '-' }}
                                            </div>
                                        </td>
                                        <td>{{ detail.control_frequency_name or detail.control_frequency or '-' }}</td>
                                        <td>{{ detail.control_type_name or detail.control_type or '-' }}</td>
                                        <td>{{ detail.control_nature_name or detail.control_nature or '-' }}</td>
                                        <td>
                                            <button class="btn btn-warning btn-sm w-100"
                                                    data-control-code="{{ detail.control_code }}"
                                                    data-control-name="{{ detail.control_name }}"
                                                    data-control-frequency="{{ detail.control_frequency_name or detail.control_frequency|e }}"
                                                    data-control-type="{{ detail.control_type_name or detail.control_type|e }}"
                                                    data-control-nature="{{ detail.control_nature_name or detail.control_nature|e }}"
                                                    data-control-nature-code="{{ detail.control_nature|e }}"
                                                    data-test-procedure="{{ detail.test_procedure|e }}"
                                                    data-std-control-id="{{ detail.mapped_std_control_id|e }}"
                                                    data-std-control-code="{{ rcm_mappings.get(detail.control_code).std_control_code if rcm_mappings.get(detail.control_code) else '' }}"
                                                    data-row-index="{{ loop.index }}"
                                                    onclick="openOperationEvaluationModal(this)">
                                                <i class="fas fa-edit me-1"></i>평가
                                            </button>
                                        </td>
                                        <td>
                                            <span id="evaluation-result-{{ loop.index }}" class="badge bg-secondary">Not Evaluated</span>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                        {% else %}
                        <div class="text-center py-5">
                            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                            <h5>통제 데이터가 없습니다</h5>
                            <p class="text-muted">해당 RCM에 통제 데이터가 존재하지 않습니다.</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 설계평가 보기 모달 -->
    <div class="modal fade" id="designEvaluationViewModal" tabindex="-1" aria-labelledby="designEvaluationViewModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header bg-info text-white">
                    <h5 class="modal-title" id="designEvaluationViewModalLabel">
                        <i class="fas fa-drafting-compass me-2"></i>설계평가 결과 ({{ evaluation_session }})
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-bordered table-sm">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%">코드</th>
                                    <th width="20%">이름</th>
                                    <th width="42%">설명</th>
                                    <th width="5%">주기</th>
                                    <th width="5%">핵심</th>
                                    <th width="5%">구분</th>
                                    <th width="8%">기준통제</th>
                                    <th width="7%">결과</th>
                                </tr>
                            </thead>
                            <tbody id="designEvaluationTableBody">
                                <tr>
                                    <td colspan="8" class="text-center py-4">
                                        <i class="fas fa-spinner fa-spin me-2"></i>설계평가 데이터를 불러오는 중...
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 운영평가 모달 -->
    <div class="modal fade" id="operationEvaluationModal" tabindex="-1" aria-labelledby="operationEvaluationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-warning text-dark">
                    <h5 class="modal-title" id="operationEvaluationModalLabel">
                        <i class="fas fa-cogs me-2"></i>운영평가
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-bold">통제 정보</label>
                        <div class="p-3 bg-light rounded">
                            <div class="row">
                                <div class="col-md-3">
                                    <strong>통제코드:</strong> <span id="modal-control-code"></span>
                                </div>
                                <div class="col-md-3">
                                    <strong>통제주기:</strong> <span id="modal-control-frequency" class="text-muted">-</span>
                                </div>
                                <div class="col-md-6">
                                    <strong>통제명:</strong> <span id="modal-control-name"></span>
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-md-3">
                                    <strong>통제유형:</strong> <span id="modal-control-type" class="text-muted">-</span>
                                </div>
                                <div class="col-md-3">
                                    <strong>통제구분:</strong> <span id="modal-control-nature" class="text-muted">-</span>
                                </div>
                                <div class="col-md-6">
                                    <!-- 빈 공간 또는 추가 정보용 -->
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-12">
                                    <strong>테스트절차:</strong>
                                    <div class="mt-1 p-2 border rounded bg-white" style="max-height: 120px; overflow-y: auto;">
                                        <span id="modal-test-procedure" class="text-muted">-</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <form id="operationEvaluationForm">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="operating_effectiveness" class="form-label fw-bold">운영 효과성</label>
                                    <select class="form-select" id="operating_effectiveness" name="operating_effectiveness" required>
                                        <option value="">선택하세요</option>
                                        <option value="effective">효과적</option>
                                        <option value="deficient">미흡</option>
                                        <option value="ineffective">비효과적</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="sample_size" class="form-label fw-bold">표본 크기</label>
                                    <input type="number" class="form-control" id="sample_size" name="sample_size" min="1" placeholder="통제주기에 따라 자동 설정">
                                    <div class="form-text">
                                        <small>권장 표본수: 연간(1), 분기(2), 월(2), 주(5), 일(20), 기타(1)</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="exception_count" class="form-label fw-bold">예외 발견 수</label>
                                    <input type="number" class="form-control" id="exception_count" name="exception_count" min="0" placeholder="예: 0">
                                    <div class="form-text">
                                        <small>예외가 1건 이상이면 결론이 자동으로 "Exception"으로 설정됩니다</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="conclusion" class="form-label fw-bold">결론</label>
                                    <select class="form-select" id="conclusion" name="conclusion" required disabled>
                                        <option value="">-</option>
                                        <option value="effective">Effective</option>
                                        <option value="exception">Exception</option>
                                    </select>
                                    <div class="form-text">
                                        <small>예외 발견 수에 따라 자동 설정됩니다</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="exception_details" class="form-label fw-bold">예외사항 세부내용</label>
                            <textarea class="form-control" id="exception_details" name="exception_details" rows="3" placeholder="발견된 예외사항의 세부내용을 기록하세요"></textarea>
                        </div>

                        <div class="mb-3">
                            <label for="improvement_plan" class="form-label fw-bold">개선계획</label>
                            <textarea class="form-control" id="improvement_plan" name="improvement_plan" rows="3" placeholder="개선이 필요한 경우 개선계획을 작성하세요"></textarea>
                        </div>

                        <!-- 파일 첨부 섹션 -->
                        <div class="mb-3">
                            <label for="evaluationImages" class="form-label fw-bold">증빙 자료 (이미지)</label>
                            <input type="file" class="form-control" id="evaluationImages" accept="image/*" multiple>
                            <div class="form-text">현장 사진, 스크린샷, 문서 스캔본 등 평가 근거가 되는 이미지 파일을 첨부하세요. (다중 선택 가능)</div>
                            <div id="imagePreview" class="mt-2"></div>
                        </div>

                        <!-- 수동통제 전용: 엑셀 파일 업로드 -->
                        <div class="mb-3" id="excelUploadSection" style="display: none;">
                            <label for="sampleExcelFile" class="form-label fw-bold">표본 데이터 (엑셀)</label>
                            <input type="file" class="form-control" id="sampleExcelFile" accept=".xlsx,.xls,.csv">
                            <div class="form-text">표본 검토 내역이 포함된 엑셀 파일을 업로드하세요.</div>
                            <div id="excelPreview" class="mt-2"></div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-warning" onclick="saveOperationEvaluation()">
                        <i class="fas fa-save me-1"></i>저장
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- 자동통제 확인 모달 -->
    <div class="modal fade" id="autoControlCheckModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title"><i class="fas fa-robot me-2"></i>자동통제 운영평가</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info mb-3">
                        <strong><span id="auto-check-control-code"></span></strong> - <span id="auto-check-control-name"></span>
                    </div>
                    <div class="alert alert-warning">
                        <i class="fas fa-info-circle me-2"></i><strong>자동통제는 설계평가에서 이미 테스트되었습니다.</strong>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">설계평가 결과</label>
                        <div id="auto-check-design-result" class="p-3 bg-light rounded"></div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">운영평가 확인</label>
                        <select class="form-select" id="auto-check-status">
                            <option value="">선택하세요</option>
                            <option value="confirmed">설계평가 결과 확인 완료</option>
                            <option value="issue_found">운영 중 이상 발견</option>
                        </select>
                    </div>
                    <div class="mb-3" id="auto-check-issue-section" style="display: none;">
                        <label class="form-label fw-bold">발견된 이상 내용</label>
                        <textarea class="form-control" id="auto-check-issue-details" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">메모 (선택)</label>
                        <textarea class="form-control" id="auto-check-note" rows="2"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" style="padding: 0.375rem 0.75rem;">취소</button>
                    <button type="button" class="btn btn-success" onclick="saveAutoControlCheck()" style="padding: 0.375rem 0.75rem;">
                        <i class="fas fa-check me-1"></i>확인 완료
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- APD01 모달 -->
    <div class="modal fade" id="apd01Modal" tabindex="-1" aria-labelledby="apd01ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="apd01ModalLabel">APD01 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="apd01Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- APD07 모달 -->
    <div class="modal fade" id="apd07Modal" tabindex="-1" aria-labelledby="apd07ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="apd07ModalLabel">APD07 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="apd07Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- APD09 모달 -->
    <div class="modal fade" id="apd09Modal" tabindex="-1" aria-labelledby="apd09ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="apd09ModalLabel">APD09 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="apd09Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- APD12 모달 -->
    <div class="modal fade" id="apd12Modal" tabindex="-1" aria-labelledby="apd12ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="apd12ModalLabel">APD12 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="apd12Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- PC01 모달 -->
    <div class="modal fade" id="pc01Modal" tabindex="-1" aria-labelledby="pc01ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="pc01ModalLabel">PC01 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="pc01Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- PC02 모달 -->
    <div class="modal fade" id="pc02Modal" tabindex="-1" aria-labelledby="pc02ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="pc02ModalLabel">PC02 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="pc02Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- PC03 모달 -->
    <div class="modal fade" id="pc03Modal" tabindex="-1" aria-labelledby="pc03ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="pc03ModalLabel">PC03 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="pc03Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- CO01 모달 -->
    <div class="modal fade" id="co01Modal" tabindex="-1" aria-labelledby="co01ModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="co01ModalLabel">CO01 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="co01Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- PC01 선행 조건 알림 모달 -->
    <div class="modal fade" id="pc01RequiredModal" tabindex="-1" aria-labelledby="pc01RequiredModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-warning text-dark">
                    <h5 class="modal-title" id="pc01RequiredModalLabel">
                        <i class="fas fa-exclamation-triangle me-2"></i>선행 조건 필요
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-warning mb-3" role="alert">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong id="pc01RequiredControl">PC02</strong>는 <strong>PC01</strong>에서 표본이 추출된 후에 진행할 수 있습니다.
                    </div>
                    <div class="bg-light p-3 rounded">
                        <h6 class="fw-bold mb-2"><i class="fas fa-list-check me-2"></i>진행 순서</h6>
                        <ol class="mb-0">
                            <li class="mb-2">PC01 운영평가를 엽니다</li>
                            <li class="mb-2">모집단 파일을 업로드합니다</li>
                            <li class="mb-2">표본이 자동으로 추출됩니다</li>
                            <li>그 후 PC02/PC03 평가를 진행할 수 있습니다</li>
                        </ol>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-1"></i>닫기
                    </button>
                    <button type="button" class="btn btn-warning" onclick="goToPC01()">
                        <i class="fas fa-arrow-right me-1"></i>PC01 평가 시작
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Container -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
        <div id="successToast" class="toast align-items-center text-bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i><span id="successToastMessage"></span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
        <div id="errorToast" class="toast align-items-center text-bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-circle me-2"></i><span id="errorToastMessage"></span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
        <div id="warningToast" class="toast align-items-center text-bg-warning border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle me-2"></i><span id="warningToastMessage"></span>
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        // 전역 변수
        let currentRcmId = {{ rcm_id }};
        let currentEvaluationSession = '{{ evaluation_session }}';
        let currentControlCode = '';
        let currentRowIndex = 0;
        let evaluated_controls = {{ evaluated_controls | tojson }};

        // Toast 헬퍼 함수
        function showToast(type, message) {
            const toastElement = document.getElementById(`${type}Toast`);
            const messageElement = document.getElementById(`${type}ToastMessage`);

            if (toastElement && messageElement) {
                messageElement.textContent = message;
                const toast = new bootstrap.Toast(toastElement, {
                    autohide: true,
                    delay: 3000
                });
                toast.show();
            }
        }

        function showSuccessToast(message) {
            showToast('success', message);
        }

        function showErrorToast(message) {
            showToast('error', message);
        }

        function showWarningToast(message) {
            showToast('warning', message);
        }

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            initializeTooltips();
            updateAllEvaluationUI();
            updateProgress();

            // 스크롤 위치 복원
            const savedScrollPosition = sessionStorage.getItem('operationEvaluationScrollPosition');
            if (savedScrollPosition) {
                window.scrollTo(0, parseInt(savedScrollPosition));
                sessionStorage.removeItem('operationEvaluationScrollPosition');
            }
        });

        // 스크롤 위치를 저장하고 페이지 새로고침
        function reloadWithScrollPosition() {
            sessionStorage.setItem('operationEvaluationScrollPosition', window.scrollY);
            location.reload();
        }

        // 툴팁 초기화
        function initializeTooltips() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // 통제주기에 따른 기본 표본수 매핑 (코드값 기준)
        function getDefaultSampleSize(controlFrequency, controlType) {
            // 통제주기 코드에서 첫 글자만 추출 (lookup_name이 올 수도 있음)
            const frequencyCode = controlFrequency ? controlFrequency.charAt(0).toUpperCase() : '';

            const frequencyMapping = {
                'A': 1,  // 연간
                'Q': 2,  // 분기
                'M': 2,  // 월
                'W': 5,  // 주
                'D': 20, // 일
                'O': 1,  // 기타 (자동통제 포함)
                'N': 1   // 필요시
            };

            return frequencyMapping[frequencyCode] || 1;
        }

        // 자동통제 확인 모달 열기 (안전 장치 포함)
        function openAutoControlCheckModal(controlCode, controlName) {
            // 모달 요소가 존재하는지 먼저 확인
            const modal = document.getElementById('autoControlCheckModal');
            if (!modal) {
                console.error('autoControlCheckModal not found');
                return;
            }

            const codeEl = document.getElementById('auto-check-control-code');
            const nameEl = document.getElementById('auto-check-control-name');
            const resultEl = document.getElementById('auto-check-design-result');
            const statusEl = document.getElementById('auto-check-status');
            const issueSection = document.getElementById('auto-check-issue-section');

            // 필수 요소들이 모두 있는지 확인
            if (!codeEl || !nameEl || !resultEl || !statusEl || !issueSection) {
                console.error('Required elements not found');
                return;
            }

            codeEl.textContent = controlCode;
            nameEl.textContent = controlName;
            resultEl.innerHTML = '<p class="text-info mb-0"><i class="fas fa-check-circle me-2"></i>설계평가에서 정상 작동 확인됨</p>';

            statusEl.onchange = function() {
                issueSection.style.display = (this.value === 'issue_found') ? 'block' : 'none';
            };

            new bootstrap.Modal(modal).show();
        }

        // 자동통제 확인 저장 (안전 장치 포함)
        function saveAutoControlCheck() {
            const statusEl = document.getElementById('auto-check-status');
            if (!statusEl) return;

            const status = statusEl.value;
            if (!status) {
                showWarningToast('확인 상태를 선택해주세요.');
                return;
            }

            const issueEl = document.getElementById('auto-check-issue-details');
            const noteEl = document.getElementById('auto-check-note');

            const data = {
                control_code: currentControlCode,
                header_id: {{ header_id | default(0) }},
                operating_effectiveness: 'evaluated',
                conclusion: status === 'confirmed' ? 'effective' : 'ineffective',
                exception_details: issueEl ? issueEl.value : '',
                improvement_plan: noteEl ? noteEl.value : '',
                sample_size: 0,
                exception_count: status === 'issue_found' ? 1 : 0
            };

            fetch('/api/operation-evaluation/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rcm_id: currentRcmId,
                    design_evaluation_session: currentEvaluationSession,
                    control_code: data.control_code,
                    evaluation_data: {
                        operating_effectiveness: data.operating_effectiveness,
                        conclusion: data.conclusion,
                        exception_details: data.exception_details,
                        improvement_plan: data.improvement_plan,
                        sample_size: data.sample_size,
                        exception_count: data.exception_count
                    }
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('autoControlCheckModal'));
                    if (modal) modal.hide();
                    showSuccessToast('자동통제 확인이 완료되었습니다.');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showErrorToast('저장 실패: ' + (result.message || '알 수 없는 오류'));
                }
            })
            .catch(error => {
                console.error('저장 오류:', error);
                showErrorToast('저장 중 오류가 발생했습니다. 자세한 내용은 콘솔을 확인하세요.');
            });
        }

        // 운영평가 모달 열기
        function openOperationEvaluationModal(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');
            const controlFrequency = buttonElement.getAttribute('data-control-frequency');
            const controlType = buttonElement.getAttribute('data-control-type');
            const controlNature = buttonElement.getAttribute('data-control-nature');
            const controlNatureCode = buttonElement.getAttribute('data-control-nature-code');
            const testProcedure = buttonElement.getAttribute('data-test-procedure');
            const stdControlId = buttonElement.getAttribute('data-std-control-id');
            const stdControlCode = buttonElement.getAttribute('data-std-control-code');
            const rowIndex = parseInt(buttonElement.getAttribute('data-row-index'));

            console.log('Control Code:', controlCode);
            console.log('Standard Control Code:', stdControlCode);
            console.log('Standard Control Code Type:', typeof stdControlCode);
            console.log('Control Nature Code:', controlNatureCode);

            currentControlCode = controlCode;
            currentRowIndex = rowIndex;

            // 자동통제 판별
            if (controlNatureCode === 'A' || controlNatureCode === '자동') {
                console.log('Auto control detected:', controlCode);
                openAutoControlCheckModal(controlCode, controlName);
                return;
            }

            // 표준통제별 UI 분기
            if (stdControlCode && stdControlCode === 'APD01') {
                console.log('APD01 detected! Redirecting to APD01 page...');
                // APD01 전용 UI로 변경
                showAPD01UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'APD07') {
                console.log('APD07 detected! Redirecting to APD07 page...');
                // APD07 전용 UI로 변경
                showAPD07UI(buttonElement);
                return;
            }

            // stdControlCode 대신 실제 controlCode로 APD09/APD12 판별
            if (controlCode && controlCode === 'APD09') {
                console.log('APD09 detected! Redirecting to APD09 page...');
                showAPD09UI(buttonElement);
                return;
            }

            if (controlCode && controlCode === 'APD12') {
                console.log('APD12 detected! Redirecting to APD12 page...');
                showAPD12UI(buttonElement);
                return;
            }

            // 매핑된 표준통제코드로도 확인 (보조)
            if (stdControlCode && stdControlCode === 'APD09') {
                console.log('APD09 detected by stdControlCode! Redirecting to APD09 page...');
                showAPD09UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'APD12') {
                console.log('APD12 detected by stdControlCode! Redirecting to APD12 page...');
                showAPD12UI(buttonElement);
                return;
            }

            // PC01 판별
            if (controlCode && controlCode === 'PC01') {
                console.log('PC01 detected! Redirecting to PC01 page...');
                showPC01UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'PC01') {
                console.log('PC01 detected by stdControlCode! Redirecting to PC01 page...');
                showPC01UI(buttonElement);
                return;
            }

            // PC02 판별
            if (controlCode && controlCode === 'PC02') {
                console.log('PC02 detected! Redirecting to PC02 page...');
                showPC02UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'PC02') {
                console.log('PC02 detected by stdControlCode! Redirecting to PC02 page...');
                showPC02UI(buttonElement);
                return;
            }

            // PC03 판별
            if (controlCode && controlCode === 'PC03') {
                console.log('PC03 detected! Redirecting to PC03 page...');
                showPC03UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'PC03') {
                console.log('PC03 detected by stdControlCode! Redirecting to PC03 page...');
                showPC03UI(buttonElement);
                return;
            }

            // CO01 판별
            if (controlCode && controlCode === 'CO01') {
                console.log('CO01 detected! Redirecting to CO01 page...');
                showCO01UI(buttonElement);
                return;
            }

            if (stdControlCode && stdControlCode === 'CO01') {
                console.log('CO01 detected by stdControlCode! Redirecting to CO01 page...');
                showCO01UI(buttonElement);
                return;
            }

            console.log('Not APD01/APD07/APD09/APD12/PC01/PC02/PC03/CO01, showing standard modal');
            
            // 일반 운영평가 UI
            // 수동통제인 경우에만 엑셀 업로드 섹션 표시
            const excelSection = document.getElementById('excelUploadSection');
            if (controlNatureCode && controlNatureCode.toUpperCase() === 'M') {
                excelSection.style.display = 'block';
            } else {
                excelSection.style.display = 'none';
            }
            
            // 파일 입력 초기화
            document.getElementById('evaluationImages').value = '';
            document.getElementById('sampleExcelFile').value = '';
            document.getElementById('imagePreview').innerHTML = '';
            document.getElementById('excelPreview').innerHTML = '';

            document.getElementById('modal-control-code').textContent = controlCode;
            document.getElementById('modal-control-name').textContent = controlName;
            document.getElementById('modal-control-frequency').textContent = controlFrequency || '-';
            document.getElementById('modal-control-type').textContent = controlType || '-';
            document.getElementById('modal-control-nature').textContent = controlNature || '-';
            document.getElementById('modal-test-procedure').textContent = testProcedure || '-';

            // 기존 평가 데이터 로드
            if (evaluated_controls[controlCode]) {
                const data = evaluated_controls[controlCode];
                document.getElementById('operating_effectiveness').value = data.operating_effectiveness || '';
                document.getElementById('sample_size').value = data.sample_size || '';
                document.getElementById('exception_count').value = data.exception_count || '';
                document.getElementById('exception_details').value = data.exception_details || '';
                document.getElementById('conclusion').value = data.conclusion || '';
                document.getElementById('improvement_plan').value = data.improvement_plan || '';
            } else {
                // 폼 초기화
                document.getElementById('operationEvaluationForm').reset();

                // 예외 발견 수 기본값 0으로 설정
                document.getElementById('exception_count').value = 0;
            }

            // 기존 평가 데이터가 없거나 표본수가 비어있는 경우 자동 설정
            if (!evaluated_controls[controlCode] || !evaluated_controls[controlCode].sample_size) {
                const defaultSampleSize = getDefaultSampleSize(controlFrequency, controlType);
                document.getElementById('sample_size').value = defaultSampleSize;
            }

            // 예외 발견 수에 따른 결론 자동 업데이트
            updateConclusionBasedOnExceptions();

            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('operationEvaluationModal'));
            modal.show();
        }

        // 예외 발견 수 변경 시 결론 자동 업데이트
        function updateConclusionBasedOnExceptions() {
            const exceptionCountInput = document.getElementById('exception_count');
            const conclusionSelect = document.getElementById('conclusion');

            if (exceptionCountInput && conclusionSelect) {
                const exceptionCount = parseInt(exceptionCountInput.value) || 0;

                if (exceptionCount > 0) {
                    conclusionSelect.value = 'exception';
                } else {
                    conclusionSelect.value = 'effective';
                }
            }
        }

        // 예외 발견 수 입력 필드에 이벤트 리스너 추가 (페이지 로드 후)
        document.addEventListener('DOMContentLoaded', function() {
            const exceptionCountInput = document.getElementById('exception_count');
            if (exceptionCountInput) {
                exceptionCountInput.addEventListener('input', updateConclusionBasedOnExceptions);
                exceptionCountInput.addEventListener('change', updateConclusionBasedOnExceptions);
            }
        });

        // 이미지 파일 미리보기
        document.getElementById('evaluationImages').addEventListener('change', function(e) {
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = '';
            
            const files = e.target.files;
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const div = document.createElement('div');
                        div.className = 'd-inline-block position-relative me-2 mb-2';
                        div.innerHTML = `
                            <img src="${e.target.result}" style="max-width: 100px; max-height: 100px; border: 1px solid #ddd; border-radius: 4px;">
                            <small class="d-block text-muted text-center" style="max-width: 100px; overflow: hidden; text-overflow: ellipsis;">${file.name}</small>
                        `;
                        preview.appendChild(div);
                    };
                    reader.readAsDataURL(file);
                }
            }
        });

        // 엑셀 파일 미리보기
        document.getElementById('sampleExcelFile').addEventListener('change', function(e) {
            const preview = document.getElementById('excelPreview');
            preview.innerHTML = '';
            
            const file = e.target.files[0];
            if (file) {
                const div = document.createElement('div');
                div.className = 'alert alert-info d-flex align-items-center';
                div.innerHTML = `
                    <i class="fas fa-file-excel fa-2x me-3"></i>
                    <div>
                        <strong>${file.name}</strong><br>
                        <small>크기: ${(file.size / 1024).toFixed(2)} KB</small>
                    </div>
                `;
                preview.appendChild(div);
            }
        });

        // 운영평가 저장
        function saveOperationEvaluation() {
            const form = document.getElementById('operationEvaluationForm');
            const formData = new FormData(form);

            // 예외 발견 수에 따른 결론 자동 설정 (저장 전 재확인)
            const exceptionCount = parseInt(formData.get('exception_count')) || 0;
            const autoConclusion = exceptionCount > 0 ? 'exception' : 'effective';

            const evaluationData = {
                operating_effectiveness: formData.get('operating_effectiveness'),
                sample_size: parseInt(formData.get('sample_size')) || 0,
                exception_count: exceptionCount,
                exception_details: formData.get('exception_details'),
                conclusion: autoConclusion,  // 자동 설정된 결론 사용
                improvement_plan: formData.get('improvement_plan')
            };

            // 필수 필드 검증
            if (!evaluationData.operating_effectiveness) {
                showWarningToast('운영 효과성은 필수 입력 항목입니다.');
                return;
            }

            // FormData 생성 (파일 포함)
            const uploadData = new FormData();
            uploadData.append('rcm_id', currentRcmId);
            uploadData.append('design_evaluation_session', currentEvaluationSession);
            uploadData.append('control_code', currentControlCode);
            uploadData.append('evaluation_data', JSON.stringify(evaluationData));
            
            // 이미지 파일 추가
            const imageFiles = document.getElementById('evaluationImages').files;
            for (let i = 0; i < imageFiles.length; i++) {
                uploadData.append('evaluation_image_' + i, imageFiles[i]);
            }
            
            // 엑셀 파일 추가 (수동통제인 경우)
            const excelFile = document.getElementById('sampleExcelFile').files[0];
            if (excelFile) {
                uploadData.append('sample_excel', excelFile);
            }

            // 서버에 저장
            fetch('/api/operation-evaluation/save', {
                method: 'POST',
                body: uploadData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 로컬 데이터 업데이트
                    evaluated_controls[currentControlCode] = evaluationData;

                    // UI 업데이트
                    updateEvaluationUI(currentRowIndex, evaluationData);
                    updateProgress();

                    // 모달 닫기
                    bootstrap.Modal.getInstance(document.getElementById('operationEvaluationModal')).hide();

                    showSuccessToast('운영평가 결과가 저장되었습니다.');
                } else {
                    showErrorToast('저장 중 오류가 발생했습니다: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorToast('저장 중 오류가 발생했습니다.');
            });
        }

        // 개별 평가 UI 업데이트
        function updateEvaluationUI(rowIndex, data) {
            // 평가 결과 업데이트
            const resultElement = document.getElementById(`evaluation-result-${rowIndex}`);
            if (resultElement && data.conclusion) {
                const resultMap = {
                    'effective': { text: 'Effective', class: 'bg-success' },
                    'exception': { text: 'Exception', class: 'bg-danger' },
                    'ineffective': { text: 'Ineffective', class: 'bg-danger' }
                };
                const result = resultMap[data.conclusion];
                if (result) {
                    resultElement.textContent = result.text;
                    resultElement.className = `badge ${result.class}`;
                }
            }

            // 개선계획 업데이트
            const improvementElement = document.getElementById(`improvement-plan-${rowIndex}`);
            if (improvementElement) {
                improvementElement.textContent = data.improvement_plan || '-';
            }
        }

        // 모든 평가 UI 업데이트
        function updateAllEvaluationUI() {
            {% for detail in rcm_details %}
            if (evaluated_controls['{{ detail.control_code }}']) {
                updateEvaluationUI({{ loop.index }}, evaluated_controls['{{ detail.control_code }}']);
            }
            {% endfor %}
        }

        // 진행률 업데이트
        function updateProgress() {
            const totalControls = {{ rcm_details|length }};
            const evaluatedControls = Object.keys(evaluated_controls).length;
            const progress = totalControls > 0 ? Math.round((evaluatedControls / totalControls) * 100) : 0;

            document.getElementById('evaluationProgress').style.width = progress + '%';
            document.getElementById('evaluationProgress').textContent = progress + '%';
            document.getElementById('evaluatedCount').textContent = evaluatedControls;

            // 상태 업데이트
            const statusElement = document.getElementById('evaluationStatus');
            if (progress === 100) {
                statusElement.textContent = '완료';
                statusElement.className = 'badge bg-success';
                document.getElementById('completeEvaluationBtn').style.display = 'inline-block';
                document.getElementById('downloadBtn').style.display = 'inline-block';
            } else if (progress > 0) {
                statusElement.textContent = '진행중';
                statusElement.className = 'badge bg-warning text-dark';
                document.getElementById('completeEvaluationBtn').style.display = 'none';
                document.getElementById('downloadBtn').style.display = 'none';
            } else {
                statusElement.textContent = '준비중';
                statusElement.className = 'badge bg-secondary';
                document.getElementById('completeEvaluationBtn').style.display = 'none';
                document.getElementById('downloadBtn').style.display = 'none';
            }
        }


        // 평가 완료 처리
        function completeEvaluation() {
            alert('운영평가 완료 기능은 추후 구현 예정입니다.');
        }

        // 평가 결과 내보내기
        function exportEvaluationResult() {
            alert('운영평가 결과 내보내기 기능은 추후 구현 예정입니다.');
        }

        // ===================================================================
        // 설계평가 보기 함수
        // ===================================================================

        function viewDesignEvaluation() {
            // 모달 표시
            const modal = new bootstrap.Modal(document.getElementById('designEvaluationViewModal'));
            modal.show();

            // 설계평가 데이터 조회
            fetch(`/api/design-evaluation/get?rcm_id=${currentRcmId}&evaluation_session=${currentEvaluationSession}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderDesignEvaluationTable(data.evaluations);
                    } else {
                        document.getElementById('designEvaluationTableBody').innerHTML = `
                            <tr>
                                <td colspan="8" class="text-center text-danger py-4">
                                    <i class="fas fa-exclamation-triangle me-2"></i>${data.message || '설계평가 데이터를 불러올 수 없습니다.'}
                                </td>
                            </tr>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('designEvaluationTableBody').innerHTML = `
                        <tr>
                            <td colspan="8" class="text-center text-danger py-4">
                                <i class="fas fa-exclamation-triangle me-2"></i>설계평가 데이터를 불러오는 중 오류가 발생했습니다.
                            </td>
                        </tr>
                    `;
                });
        }

        function renderDesignEvaluationTable(evaluations) {
            const tbody = document.getElementById('designEvaluationTableBody');

            if (!evaluations || evaluations.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">
                            <i class="fas fa-info-circle me-2"></i>설계평가 데이터가 없습니다.
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = evaluations.map(item => {
                const adequacyMap = {
                    'adequate': { text: '적정', class: 'bg-success' },
                    'deficient': { text: '미흡', class: 'bg-warning text-dark' },
                    'inadequate': { text: '부적정', class: 'bg-danger' }
                };
                const adequacy = adequacyMap[item.design_adequacy] || { text: item.design_adequacy || '-', class: 'bg-secondary' };

                const stdControl = item.std_control_code
                    ? `<span class="badge bg-info">${item.std_control_code}</span>`
                    : '<span class="text-muted">-</span>';

                const isKey = item.key_control || '-';

                return `
                    <tr>
                        <td style="font-size: 0.85rem;"><code>${item.control_code || '-'}</code></td>
                        <td style="font-size: 0.85rem;">${item.control_name || '-'}</td>
                        <td>
                            <div style="max-height: 60px; overflow-y: auto; font-size: 0.85rem;">
                                ${item.control_description || '-'}
                            </div>
                        </td>
                        <td style="font-size: 0.85rem;">${item.control_frequency_name || item.control_frequency || '-'}</td>
                        <td style="font-size: 0.85rem;">${isKey}</td>
                        <td style="font-size: 0.85rem;">${item.control_nature_name || item.control_nature || '-'}</td>
                        <td style="font-size: 0.85rem;">${stdControl}</td>
                        <td style="font-size: 0.85rem;"><span class="badge ${adequacy.class}">${adequacy.text}</span></td>
                    </tr>
                `;
            }).join('');
        }

        // ===================================================================
        // APD01 표준통제 전용 함수
        // ===================================================================

        function showAPD01UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 APD01 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('apd01Iframe').src = `/operation-evaluation/manual/APD01?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('apd01Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('apd01Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // APD07 표준통제 전용 함수
        // ===================================================================

        function showAPD07UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 APD07 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('apd07Iframe').src = `/operation-evaluation/manual/APD07?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('apd07Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('apd07Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // APD09 표준통제 전용 함수
        // ===================================================================

        function showAPD09UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 APD09 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('apd09Iframe').src = `/operation-evaluation/manual/APD09?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('apd09Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('apd09Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // APD12 표준통제 전용 함수
        // ===================================================================

        function showAPD12UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 APD12 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('apd12Iframe').src = `/operation-evaluation/manual/APD12?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('apd12Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('apd12Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // PC01 표준통제 전용 함수
        // ===================================================================

        function showPC01UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 PC01 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('pc01Iframe').src = `/operation-evaluation/manual/PC01?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('pc01Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('pc01Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // PC01 진행 여부 체크 함수
        // ===================================================================

        function isPC01Completed() {
            // evaluated_controls에서 표준통제코드가 PC01인 통제를 찾아서 모집단 업로드 여부 확인
            for (const controlCode in evaluated_controls) {
                const evaluation = evaluated_controls[controlCode];
                // PC01인지 확인 (통제코드 또는 표준통제코드)
                const button = document.querySelector(`[data-control-code="${controlCode}"]`);
                if (button) {
                    const stdControlCode = button.getAttribute('data-std-control-code');
                    if (stdControlCode === 'PC01' || controlCode === 'PC01') {
                        // PC01의 모집단이 업로드되었는지 확인 (test_results_path 또는 samples_path가 있으면 진행 중)
                        if (evaluation && (evaluation.test_results_path || evaluation.samples_path)) {
                            return true;
                        }
                    }
                }
            }
            return false;
        }

        // PC01 선행 조건 모달 표시
        function showPC01RequiredModal(controlName) {
            document.getElementById('pc01RequiredControl').textContent = controlName;
            const modal = new bootstrap.Modal(document.getElementById('pc01RequiredModal'));
            modal.show();
        }

        // PC01 평가로 이동
        function goToPC01() {
            // PC01 버튼 찾기
            const buttons = document.querySelectorAll('[data-control-code]');
            for (const button of buttons) {
                const stdControlCode = button.getAttribute('data-std-control-code');
                const controlCode = button.getAttribute('data-control-code');
                if (stdControlCode === 'PC01' || controlCode === 'PC01') {
                    // 모달 닫기
                    const modal = bootstrap.Modal.getInstance(document.getElementById('pc01RequiredModal'));
                    if (modal) modal.hide();

                    // PC01 평가 모달 열기
                    button.click();
                    return;
                }
            }
            alert('PC01 통제를 찾을 수 없습니다.');
        }

        // ===================================================================
        // PC02 표준통제 전용 함수
        // ===================================================================

        function showPC02UI(buttonElement) {
            // PC01 진행 여부 체크 (모집단 업로드 및 표본 추출 완료 필요)
            if (!isPC01Completed()) {
                showPC01RequiredModal('PC02');
                return;
            }

            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 PC02 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('pc02Iframe').src = `/operation-evaluation/manual/PC02?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('pc02Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('pc02Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // PC03 표준통제 전용 함수
        // ===================================================================

        function showPC03UI(buttonElement) {
            // PC01 진행 여부 체크 (모집단 업로드 및 표본 추출 완료 필요)
            if (!isPC01Completed()) {
                showPC01RequiredModal('PC03');
                return;
            }

            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 PC03 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('pc03Iframe').src = `/operation-evaluation/manual/PC03?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('pc03Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('pc03Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // CO01 표준통제 전용 함수
        // ===================================================================

        function showCO01UI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 CO01 UI 표시 (Generic 경로 사용)
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로)
            document.getElementById('co01Iframe').src = `/operation-evaluation/manual/CO01?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('co01Modal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('co01Modal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }
    </script>
</body>
</html>