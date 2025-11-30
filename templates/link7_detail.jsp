<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>SnowBall - {{ rcm_info.control_category or 'RCM' }} 운영평가 - {{ rcm_info.rcm_name }}</title>
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* 모달이 navbar 위에 표시되도록 z-index 강제 조정 */
        .modal {
            z-index: 1060 !important;
        }

        .modal-backdrop {
            z-index: 1055 !important;
        }

        /* 모달이 화면을 벗어나지 않도록 높이 제한 및 스크롤 추가 */
        #operationEvaluationModal .modal-content {
            max-height: 90vh;
            display: flex;
            flex-direction: column;
        }

        #operationEvaluationModal .modal-body {
            overflow-y: auto;
            flex: 1 1 auto;
        }

        #operationEvaluationModal .modal-footer {
            flex-shrink: 0;
        }
    </style>
</head>

<body>
    {% include 'navi.jsp' %}

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h1><i class="fas fa-cogs me-2"></i>{{ rcm_info.control_category or 'RCM' }} 운영평가</h1>
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
                                        <td><span class="badge bg-warning text-dark">{{ rcm_details|length }}개</span>
                                        </td>
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
                                        {% set init_progress = operation_header['progress_percentage']|int if operation_header else 0 %}
                                        <div class="progress-bar bg-warning" id="evaluationProgress" role="progressbar"
                                            style="width: {{ init_progress }}%; font-size: 12px;" aria-valuenow="{{ init_progress }}" aria-valuemin="0"
                                            aria-valuemax="100">{{ init_progress }}%</div>
                                    </div>
                                    <small class="text-muted">
                                        {% set init_evaluated = operation_header['evaluated_controls']|int if operation_header else 0 %}
                                        {% set init_total = operation_header['total_controls']|int if operation_header else rcm_details|length %}
                                        <span id="evaluatedCount">{{ init_evaluated }}</span> / <span id="totalControlCount">{{ init_total }}</span> 통제 평가 완료
                                        <br>상태:
                                        {% if operation_header and operation_header['evaluation_status'] == 'COMPLETED' %}
                                        <span id="evaluationStatus" class="badge bg-success">완료</span>
                                        {% elif init_progress > 0 %}
                                        <span id="evaluationStatus" class="badge bg-warning text-dark">진행중</span>
                                        {% else %}
                                        <span id="evaluationStatus" class="badge bg-secondary">준비 중</span>
                                        {% endif %}
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
                            <button id="completeEvaluationBtn" class="btn btn-sm btn-warning"
                                onclick="completeEvaluation()"
                                style="display: none; height: 70%; padding: 0.2rem 0.5rem;" title="운영평가를 완료 처리합니다"
                                data-bs-toggle="tooltip">
                                <i class="fas fa-check me-1"></i>완료처리
                            </button>
                            <button id="downloadBtn" class="btn btn-sm btn-outline-warning"
                                onclick="exportEvaluationResult()"
                                style="display: none; height: 70%; padding: 0.2rem 0.5rem;">
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
                                                title="{{ detail.control_description or '-' }}"
                                                data-bs-toggle="tooltip">
                                                {{ detail.control_description or '-' }}
                                            </div>
                                        </td>
                                        <td>{{ detail.control_frequency_name or detail.control_frequency or '-' }}</td>
                                        <td>{{ detail.control_type_name or detail.control_type or '-' }}</td>
                                        <td>{{ detail.control_nature_name or detail.control_nature or '-' }}</td>
                                        <td>
                                            <button class="btn btn-warning btn-sm w-100"
                                                data-detail-id="{{ detail.detail_id }}"
                                                data-control-code="{{ detail.control_code }}"
                                                data-control-name="{{ detail.control_name }}"
                                                data-control-frequency="{{ detail.control_frequency_name or detail.control_frequency|e }}"
                                                data-control-type="{{ detail.control_type_name or detail.control_type|e }}"
                                                data-control-nature="{{ detail.control_nature_name or detail.control_nature|e }}"
                                                data-control-nature-code="{{ detail.control_nature|e }}"
                                                data-test-procedure="{{ detail.test_procedure|e }}"
                                                data-std-control-id="{{ detail.mapped_std_control_id|e }}"
                                                data-std-control-code="{% if detail['control_code'] in rcm_mappings %}{{ rcm_mappings[detail['control_code']].std_control_code }}{% else %}{% endif %}"
                                                data-design-evaluation-evidence="{{ (detail.evaluation_evidence or '')|e }}"
                                                data-recommended-sample-size="{{ detail.recommended_sample_size if detail.recommended_sample_size is not none else '' }}"
                                                data-row-index="{{ loop.index }}"
                                                onclick="openOperationEvaluationModal(this)">
                                                <i class="fas fa-edit me-1"></i>평가
                                            </button>
                                        </td>
                                        <td>
                                            <span id="evaluation-result-{{ loop.index }}" class="badge bg-secondary">Not
                                                Evaluated</span>
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
    <div class="modal fade" id="designEvaluationViewModal" tabindex="-1"
        aria-labelledby="designEvaluationViewModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header bg-info text-white">
                    <h5 class="modal-title" id="designEvaluationViewModalLabel">
                        <i class="fas fa-drafting-compass me-2"></i>설계평가 결과 ({{ evaluation_session }})
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"
                        aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="table-responsive">
                        <table class="table table-bordered table-sm">
                            <thead class="table-light">
                                <tr>
                                    <th width="5%">코드</th>
                                    <th width="20%">이름</th>
                                    <th width="50%">설명</th>
                                    <th width="5%">주기</th>
                                    <th width="5%">핵심</th>
                                    <th width="5%">구분</th>
                                    <th width="10%">결과</th>
                                </tr>
                            </thead>
                            <tbody id="designEvaluationTableBody">
                                <tr>
                                    <td colspan="7" class="text-center py-4">
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
    <div class="modal fade" id="operationEvaluationModal" tabindex="-1" aria-labelledby="operationEvaluationModalLabel"
        aria-hidden="true">
        <div class="modal-dialog" style="max-width: 1200px;">
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
                                    <strong>통제주기:</strong> <span id="modal-control-frequency"
                                        class="text-muted">-</span>
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
                                    <div class="mt-1 p-2 border rounded bg-white"
                                        style="max-height: 120px; overflow-y: auto;">
                                        <span id="modal-test-procedure" class="text-muted"
                                            style="white-space: pre-line;">-</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <form id="operationEvaluationForm">
                        <!-- 당기 발생사실 없음 옵션 (표본수가 0일 때만 표시) -->
                        <div class="mb-3" id="no-occurrence-section" style="display: none;">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="no_occurrence" name="no_occurrence">
                                <label class="form-check-label" for="no_occurrence">
                                    <strong>당기 발생사실 없음</strong>
                                    <small class="text-muted d-block">해당 통제활동이 평가 기간 동안 발생하지 않은 경우 체크하세요</small>
                                </label>
                            </div>
                        </div>

                        <!-- 모집단 업로드 섹션 (표본수 0인 경우) -->
                        <div id="population-upload-section" style="display: none;">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>모집단 업로드 모드</strong>: 표본 크기가 0으로 설정되어 있습니다.
                                모집단 엑셀 파일을 업로드하면 자동으로 표본이 추출됩니다.
                            </div>

                            <div class="mb-3">
                                <label for="populationFile" class="form-label fw-bold">
                                    <i class="fas fa-upload me-1"></i>모집단 엑셀 파일
                                </label>
                                <input type="file" class="form-control" id="populationFile" accept=".xlsx,.xlsm"
                                    onchange="handlePopulationFileSelected()">
                                <div class="form-text">
                                    <strong>.xlsx 또는 .xlsm</strong> 형식의 엑셀 파일을 업로드하세요. (.xls 파일은 Excel에서 .xlsx로 변환 후
                                    업로드)
                                </div>
                            </div>

                            <div id="populationFieldMapping" style="display: none;">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">필드 매핑</label>
                                    <div class="form-text mb-2">엑셀 파일의 컬럼을 매핑하세요</div>
                                    <div id="fieldMappingContainer"></div>
                                </div>
                                <button type="button" class="btn btn-primary" onclick="uploadPopulationFile()">
                                    <i class="fas fa-upload me-1"></i>업로드 및 표본 추출
                                </button>
                            </div>
                        </div>

                        <div id="evaluation-fields">
                            <!-- 표본 크기 입력 -->
                            <div class="row mb-3">
                                <div class="col-md-3">
                                    <label for="sample_size" class="form-label fw-bold">표본 크기</label>
                                    <input type="number" class="form-control text-end" id="sample_size"
                                        name="sample_size" min="0" max="100" placeholder="공란: 모집단 크기 기반 자동 결정"
                                        onchange="generateSampleLines()"
                                        onkeyup="if(event.key === 'Enter') generateSampleLines()">
                                    <div id="sampleSizeMessage" class="mt-1" style="display: none;"></div>
                                </div>
                                <div class="col-md-9 d-flex align-items-end">
                                    <div class="form-text">
                                        <small>권장 표본수: 연간(1), 분기(2), 월(2), 주(5), 일(20), 기타(1). 입력 후 자동으로 표본 라인이 생성됩니다.</small>
                                    </div>
                                </div>
                            </div>

                            <!-- 표본 라인 테이블 -->
                            <div id="sample-lines-container" style="display: none;">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">표본별 테스트 결과</label>
                                    <div class="table-responsive">
                                        <table class="table table-bordered table-sm" id="sample-lines-table">
                                            <thead class="table-light" id="sample-lines-thead">
                                                <tr>
                                                    <th width="10%">표본 #</th>
                                                    <th width="70%">증빙 내용</th>
                                                    <th width="20%">결과</th>
                                                </tr>
                                            </thead>
                                            <tbody id="sample-lines-tbody">
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                <!-- 전체 결론 -->
                                <div class="row">
                                    <div class="col-md-12">
                                        <div class="alert alert-info">
                                            <strong>전체 결론:</strong>
                                            <span id="overall-conclusion" class="badge bg-secondary ms-2">-</span>
                                            <div class="mt-2">
                                                <small id="conclusion-summary">표본별 결과를 입력하면 자동으로 계산됩니다.</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="mb-3" id="exception-details-section" style="display: none;">
                            <label for="exception_details" class="form-label fw-bold">예외사항 세부내용</label>
                            <textarea class="form-control" id="exception_details" name="exception_details" rows="3"
                                placeholder="발견된 예외사항의 세부내용을 기록하세요"></textarea>
                        </div>

                        <div class="mb-3" id="improvement-plan-section" style="display: none;">
                            <label for="improvement_plan" class="form-label fw-bold">개선계획</label>
                            <textarea class="form-control" id="improvement_plan" name="improvement_plan" rows="3"
                                placeholder="개선이 필요한 경우 개선계획을 작성하세요"></textarea>
                        </div>

                        <!-- 설계평가 이미지 표시 섹션 -->
                        <div class="mb-3" id="designEvaluationImagesSection" style="display: none;">
                            <label class="form-label fw-bold">
                                <i class="fas fa-clipboard-check me-1"></i>설계평가 증빙 이미지
                            </label>
                            <div id="designEvaluationImagesPreview" class="border rounded p-2 bg-light"></div>
                            <div class="form-text">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle me-1"></i>
                                    설계평가 시 업로드된 이미지입니다. 클릭하면 원본 크기로 볼 수 있습니다.
                                </small>
                            </div>
                        </div>

                        <!-- 수동통제 전용: 엑셀 파일 업로드 -->
                        <div class="mb-3" id="excelUploadSection" style="display: none;">
                            <label for="sampleExcelFile" class="form-label fw-bold">표본 데이터 (엑셀)</label>
                            <input type="file" class="form-control" id="sampleExcelFile" accept=".xlsx,.xls,.csv">
                            <div class="form-text">표본 검토 내역이 포함된 엑셀 파일을 업로드하세요.</div>
                            <div id="excelPreview" class="mt-2"></div>
                        </div>

                        <!-- 당기 발생사실 없음 사유 -->
                        <div class="mb-3" id="no-occurrence-reason-section" style="display: none;">
                            <label for="no_occurrence_reason" class="form-label fw-bold">
                                비고 (선택사항)
                            </label>
                            <textarea class="form-control" id="no_occurrence_reason" name="no_occurrence_reason"
                                rows="3"
                                placeholder="필요한 경우 추가 설명을 입력하세요&#10;예) 당기 중 신규 직원 채용이 없었음, 시스템 변경이 발생하지 않았음 등"></textarea>
                            <div class="form-text">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle me-1"></i>
                                    발생하지 않은 이유가 명확하거나 추가 설명이 필요한 경우에만 입력하세요
                                </small>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal"
                        style="min-width: auto; padding: 0.375rem 0.75rem;">닫기</button>
                    <button type="button" id="resetPopulationBtn" class="btn btn-danger"
                        onclick="resetPopulationUpload();" style="display: none;">
                        <i class="fas fa-redo me-1"></i>초기화
                    </button>
                    <!-- 운영평가 다운로드 버튼 (평가 완료 시 표시) -->
                    <a id="downloadOperationBtn" href="#" class="btn btn-success" style="display: none;">
                        <i class="fas fa-download me-1"></i>엑셀 다운로드
                    </a>
                    <button type="button" id="saveOperationEvaluationBtn" class="btn btn-warning"
                        onclick="saveOperationEvaluation();">
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
                        <strong><span id="auto-check-control-code"></span></strong> - <span
                            id="auto-check-control-name"></span>
                    </div>
                    <div class="alert alert-warning mb-3">
                        <div class="mb-2">
                            <i class="fas fa-info-circle me-2"></i><strong>자동통제는 설계평가에서 이미 테스트되었습니다.</strong>
                        </div>
                        <hr class="my-2" style="border-color: rgba(0,0,0,0.1);">
                        <div class="mt-2" style="font-size: 0.9rem;">
                            <p class="mb-2"><strong>자동통제란?</strong></p>
                            <ul class="mb-2 ps-3" style="font-size: 0.85rem;">
                                <li>시스템이나 프로그램에 의해 자동으로 수행되는 통제</li>
                                <li>사람의 개입 없이 일관되게 작동하는 통제 활동</li>
                            </ul>
                            <p class="mb-2 mt-3"><strong>운영평가가 별도로 필요하지 않은 이유:</strong></p>
                            <ul class="mb-0 ps-3" style="font-size: 0.85rem;">
                                <li><strong>일관성:</strong> 설계된 대로 작동하면 운영 기간 내내 동일하게 작동</li>
                                <li><strong>변동성 없음:</strong> 수동통제와 달리 사람의 실수나 변동성이 없음</li>
                                <li><strong>설계평가 충분:</strong> 시스템 로직이 적절하게 설계되었는지만 확인하면 됨</li>
                                <li><strong>효율성:</strong> 매번 샘플을 추출하여 테스트할 필요가 없음</li>
                            </ul>
                            <p class="mb-0 mt-3 text-muted" style="font-size: 0.8rem;">
                                <i class="fas fa-lightbulb me-1"></i>
                                <em>단, 시스템 변경이나 업그레이드가 있었다면 재평가가 필요할 수 있습니다.</em>
                            </p>
                        </div>
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
                    <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">취소</button>
                    <button type="button" class="btn btn-sm btn-success" onclick="saveAutoControlCheck()">
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
                    <h5 class="modal-title" id="apd01ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="apd07ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="apd09ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="apd12ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="pc01ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="pc02ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="pc03ModalLabel">수동통제 운영평가</h5>
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
                    <h5 class="modal-title" id="co01ModalLabel">수동통제 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="co01Iframe" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
            </div>
        </div>
    </div>

    <!-- PC01 선행 조건 알림 모달 -->
    <div class="modal fade" id="pc01RequiredModal" tabindex="-1" aria-labelledby="pc01RequiredModalLabel"
        aria-hidden="true">
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
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal"
                        style="min-width: auto; padding: 0.375rem 0.75rem;">
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
        <div id="successToast" class="toast align-items-center text-bg-success border-0" role="alert"
            aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i><span id="successToastMessage"></span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"
                    aria-label="Close"></button>
            </div>
        </div>
        <div id="errorToast" class="toast align-items-center text-bg-danger border-0" role="alert" aria-live="assertive"
            aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-circle me-2"></i><span id="errorToastMessage"></span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"
                    aria-label="Close"></button>
            </div>
        </div>
        <div id="warningToast" class="toast align-items-center text-bg-warning border-0" role="alert"
            aria-live="assertive" aria-atomic="true">
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
        let currentDesignEvaluationEvidence = '';  // 설계평가 증빙
        let currentRecommendedSampleSize = null;  // RCM 권장 표본수 (모집단 업로드 모드 확인용)
        let evaluated_controls = {{ evaluated_controls | tojson }};
        // 통제별 설계평가 이미지 데이터 저장 (control_code를 키로 사용)
        let designEvaluationImagesData = {
            {% if rcm_details %}
        {% for detail in rcm_details %}
        "{{ detail.control_code }}": {{ (detail.design_evaluation_images | tojson if detail.design_evaluation_images else '[]')| safe }}{% if not loop.last %},{% endif %}
        {% endfor %}
        {% endif %}
        };

        // 통제별 attribute 정보 저장 (control_code를 키로 사용)
        let rcmAttributesData = {};
        {% if rcm_details %}
        {% for detail in rcm_details %}
        rcmAttributesData[{{ detail['control_code'] | tojson }}] = {
            detailId: {{ detail['detail_id'] | int }},
            populationAttributeCount: {{ detail['population_attribute_count'] | int if detail['population_attribute_count'] is not none else 2 }},
            attributes: {
                attribute0: {{ detail['attribute0'] | tojson if detail['attribute0'] else 'null' }},
                attribute1: {{ detail['attribute1'] | tojson if detail['attribute1'] else 'null' }},
                attribute2: {{ detail['attribute2'] | tojson if detail['attribute2'] else 'null' }},
                attribute3: {{ detail['attribute3'] | tojson if detail['attribute3'] else 'null' }},
                attribute4: {{ detail['attribute4'] | tojson if detail['attribute4'] else 'null' }},
                attribute5: {{ detail['attribute5'] | tojson if detail['attribute5'] else 'null' }},
                attribute6: {{ detail['attribute6'] | tojson if detail['attribute6'] else 'null' }},
                attribute7: {{ detail['attribute7'] | tojson if detail['attribute7'] else 'null' }},
                attribute8: {{ detail['attribute8'] | tojson if detail['attribute8'] else 'null' }},
                attribute9: {{ detail['attribute9'] | tojson if detail['attribute9'] else 'null' }}
            }
        };
        {% endfor %}
        {% endif %}

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
        document.addEventListener('DOMContentLoaded', function () {
            console.log('=== 페이지 로드 시 evaluated_controls ===');
            console.log(evaluated_controls);

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

            statusEl.onchange = function () {
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
                header_id: {{ header_id | default (0)
        }},
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

        // 설계평가 이미지 표시 함수
        function displayDesignEvaluationImages(images) {
            const section = document.getElementById('designEvaluationImagesSection');
            const preview = document.getElementById('designEvaluationImagesPreview');

            console.log('[displayDesignEvaluationImages] Called with images:', images);
            console.log('[displayDesignEvaluationImages] Images type:', typeof images);
            console.log('[displayDesignEvaluationImages] Images length:', images?.length);

            if (!section || !preview) {
                console.error('Design evaluation images section not found');
                return;
            }

            // 이미지가 없으면 섹션 숨김
            if (!images || images.length === 0) {
                console.log('[displayDesignEvaluationImages] No images to display, hiding section');
                section.style.display = 'none';
                preview.innerHTML = '';
                return;
            }

            // 이미지가 있으면 섹션 표시
            console.log('[displayDesignEvaluationImages] Displaying images, showing section');
            section.style.display = 'block';

            // 이미지 미리보기 생성
            preview.innerHTML = '';
            images.forEach((imagePath, index) => {
                console.log(`[displayDesignEvaluationImages] Image ${index + 1}:`, imagePath);

                const imageContainer = document.createElement('div');
                imageContainer.className = 'd-block position-relative mb-3';

                const img = document.createElement('img');
                const fullPath = `/static/${imagePath}`;
                console.log(`[displayDesignEvaluationImages] Full image path:`, fullPath);
                img.src = fullPath;
                img.className = 'img-thumbnail';
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                img.style.display = 'block';
                img.style.cursor = 'pointer';
                img.alt = `설계평가 이미지 ${index + 1}`;

                // 이미지 로드 성공/실패 이벤트
                img.onload = () => {
                    console.log(`[displayDesignEvaluationImages] Image loaded successfully:`, fullPath);
                };
                img.onerror = () => {
                    console.error(`[displayDesignEvaluationImages] Image failed to load:`, fullPath);
                };

                // 클릭 시 새 창에서 원본 이미지 보기
                img.onclick = () => {
                    window.open(fullPath, '_blank');
                };

                imageContainer.appendChild(img);
                preview.appendChild(imageContainer);
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
            const designEvaluationEvidence = buttonElement.getAttribute('data-design-evaluation-evidence');
            const recommendedSampleSizeStr = buttonElement.getAttribute('data-recommended-sample-size');
            const rowIndex = parseInt(buttonElement.getAttribute('data-row-index'));

            // 전역 변수로 권장 표본수와 통제주기 저장
            // 1순위: RCM에 설정된 권장 표본수 (0 포함)
            // 2순위: 통제 주기에 따른 기본값
            const rcmRecommendedSize = (recommendedSampleSizeStr && recommendedSampleSizeStr !== '') ? parseInt(recommendedSampleSizeStr) : null;
            recommendedSampleSize = rcmRecommendedSize !== null ? rcmRecommendedSize : getDefaultSampleSize(controlFrequency, controlType);

            // JavaScript 객체에서 설계평가 이미지 데이터 가져오기
            let designEvaluationImages = [];
            if (designEvaluationImagesData[controlCode]) {
                designEvaluationImages = Array.isArray(designEvaluationImagesData[controlCode])
                    ? designEvaluationImagesData[controlCode]
                    : [];
            }

            console.log('Control Code:', controlCode);
            console.log('Standard Control Code:', stdControlCode);
            console.log('Standard Control Code Type:', typeof stdControlCode);
            console.log('Control Nature Code:', controlNatureCode);
            console.log('Design Evaluation Evidence:', designEvaluationEvidence);
            console.log('Design Evaluation Images:', designEvaluationImages);
            console.log('Design Evaluation Images (type):', typeof designEvaluationImages);
            console.log('Design Evaluation Images (length):', designEvaluationImages?.length);

            currentControlCode = controlCode;
            currentRowIndex = rowIndex;
            currentDesignEvaluationEvidence = designEvaluationEvidence || '';
            currentRecommendedSampleSize = rcmRecommendedSize;  // RCM 권장 표본수 저장

            // RCM attribute 정보 조회 (전역 변수에 저장)
            const detailId = buttonElement.getAttribute('data-detail-id');
            const rcmAttrs = (typeof rcmAttributesData !== 'undefined' && rcmAttributesData[controlCode]) || {};
            window.currentPopulationAttributeCount = rcmAttrs.populationAttributeCount || 0;
            window.currentAttributeNames = rcmAttrs.attributes || {};

            console.log('[Attribute Info] Detail ID:', detailId);
            console.log('[Attribute Info] Population Attribute Count:', window.currentPopulationAttributeCount);
            console.log('[Attribute Info] Attribute Names:', window.currentAttributeNames);

            // 자동통제 판별
            if (controlNatureCode && (controlNatureCode === 'A' || controlNatureCode === '자동' || controlNatureCode === 'Automated')) {
                console.log('Auto control detected:', controlCode);
                openAutoControlCheckModal(controlCode, controlName);
                return;
            }

            // 표준통제별 UI 분기
            if (stdControlCode && stdControlCode === 'APD01') {
                console.log('APD01 detected! Redirecting to APD01 page...');
                // APD01은 특별히 모집단 업로드 기능이 필요하므로, 이 경우에도 operationEvaluationModal을 사용하되,
                // 모집단 업로드 섹션이 기본으로 보이도록 처리 (rcmRecommendedSize=0과 동일하게)
                // 이 부분은 아래 UI 분기 로직에서 처리될 것임.
            }

            // 기존에 iframe으로 열리던 모든 표준 통제(APD01, APD07, APD09, APD12, PC01, PC02, PC03, CO01)
            // 그리고 일반 수동 통제 모두 이제 operationEvaluationModal을 사용합니다.
            // 따라서 별도의 분기 로직은 필요 없습니다.

            // 파일 입력 초기화 (요소 존재 확인)
            const excelSection = document.getElementById('excelUploadSection');
            if (excelSection) {
                excelSection.style.display = 'none';
            }

            // 파일 입력 초기화 (요소 존재 확인)
            const sampleExcelFile = document.getElementById('sampleExcelFile');
            const excelPreview = document.getElementById('excelPreview');

            if (sampleExcelFile) sampleExcelFile.value = '';
            if (excelPreview) excelPreview.innerHTML = '';

            const modalControlCode = document.getElementById('modal-control-code');
            const modalControlName = document.getElementById('modal-control-name');
            const modalControlFrequency = document.getElementById('modal-control-frequency');
            const modalControlType = document.getElementById('modal-control-type');
            const modalControlNature = document.getElementById('modal-control-nature');
            const modalTestProcedure = document.getElementById('modal-test-procedure');

            if (modalControlCode) modalControlCode.textContent = controlCode;
            if (modalControlName) modalControlName.textContent = controlName;
            if (modalControlFrequency) modalControlFrequency.textContent = controlFrequency || '-';
            if (modalControlType) modalControlType.textContent = controlType || '-';
            if (modalControlNature) modalControlNature.textContent = controlNature || '-';
            if (modalTestProcedure) modalTestProcedure.textContent = testProcedure || '-';
            console.log('[권장 표본수] RCM 설정값:', rcmRecommendedSize);
            console.log('[권장 표본수] 통제주기 기본값:', getDefaultSampleSize(controlFrequency, controlType));
            console.log('[권장 표본수] 최종 사용값:', recommendedSampleSize);

            // UI 분기: 표본수 0 vs 0 이상
            const populationUploadSection = document.getElementById('population-upload-section');
            const evaluationFields = document.getElementById('evaluation-fields');

            // 이미 저장된 데이터가 있는지 확인
            const hasSavedData = evaluated_controls[controlCode] &&
                (evaluated_controls[controlCode].line_id ||
                    (evaluated_controls[controlCode].sample_lines && evaluated_controls[controlCode].sample_lines.length > 0));

            const resetBtn = document.getElementById('resetPopulationBtn');

            if (recommendedSampleSize === 0 && !hasSavedData) {
                // 표본수가 0이고 저장된 데이터가 없으면 모집단 업로드 UI 표시
                if (populationUploadSection) populationUploadSection.style.display = 'block';
                if (evaluationFields) evaluationFields.style.display = 'none';
                if (resetBtn) resetBtn.style.display = 'none';
                console.log('[UI 분기] 모집단 업로드 섹션 표시 (권장 표본수 0, 저장 데이터 없음)');
            } else if (recommendedSampleSize === 0 && hasSavedData) {
                // 표본수가 0이고 저장된 데이터가 있으면 평가 UI + 초기화 버튼 표시
                if (populationUploadSection) populationUploadSection.style.display = 'none';
                if (evaluationFields) evaluationFields.style.display = 'block';
                if (resetBtn) resetBtn.style.display = 'inline-block';
                console.log('[UI 분기] 평가 필드 + 초기화 버튼 표시 (권장 표본수 0, 저장 데이터 있음)');
            } else {
                // 표본수가 0이 아니면 평가 UI만 표시
                if (populationUploadSection) populationUploadSection.style.display = 'none';
                if (evaluationFields) evaluationFields.style.display = 'block';
                if (resetBtn) resetBtn.style.display = 'none';
                console.log('[UI 분기] 평가 필드 섹션 표시 (권장 표본수:', recommendedSampleSize, ', 저장 데이터:', hasSavedData, ')');
            }


            // 설계평가 대체 옵션 표시 여부 결정 (연간 통제 또는 자동 통제만)
            const useDesignEvaluationSection = document.getElementById('use-design-evaluation-section');
            const isAnnually = controlFrequency && (controlFrequency === 'Annually' || controlFrequency === 'A' || controlFrequency === '연간');
            const isAutomated = controlNatureCode && (controlNatureCode === 'A' || controlNatureCode === '자동' || controlNature === 'Automated');

            if (useDesignEvaluationSection) {
                if (isAnnually || isAutomated) {
                    useDesignEvaluationSection.style.display = 'block';
                } else {
                    useDesignEvaluationSection.style.display = 'none';
                    // 체크박스도 초기화
                    const useDesignEvaluationEl = document.getElementById('use_design_evaluation');
                    if (useDesignEvaluationEl) {
                        useDesignEvaluationEl.checked = false;
                    }
                }
            }

            // 기존 평가 데이터 로드
            const noOccurrenceEl = document.getElementById('no_occurrence');
            const noOccurrenceReasonEl = document.getElementById('no_occurrence_reason');
            const sampleSizeEl = document.getElementById('sample_size');
            const exceptionCountEl = document.getElementById('exception_count');
            const mitigatingFactorsEl = document.getElementById('mitigating_factors');
            const exceptionDetailsEl = document.getElementById('exception_details');
            const conclusionEl = document.getElementById('conclusion');
            const improvementPlanEl = document.getElementById('improvement_plan');
            const evaluationFieldsEl = document.getElementById('evaluation-fields');
            const noOccurrenceReasonSectionEl = document.getElementById('no-occurrence-reason-section');
            const operationEvaluationFormEl = document.getElementById('operationEvaluationForm');

            if (evaluated_controls[controlCode]) {
                const data = evaluated_controls[controlCode];

                // 당기 발생사실 없음 여부 확인
                if (data.no_occurrence) {
                    if (noOccurrenceEl) noOccurrenceEl.checked = true;
                    if (noOccurrenceReasonEl) noOccurrenceReasonEl.value = data.no_occurrence_reason || '';
                    if (typeof toggleNoOccurrenceFields === 'function') toggleNoOccurrenceFields();
                } else {
                    if (noOccurrenceEl) noOccurrenceEl.checked = false;
                    if (sampleSizeEl) sampleSizeEl.value = data.sample_size || '';
                    if (exceptionCountEl) exceptionCountEl.value = data.exception_count || '';
                    if (mitigatingFactorsEl) mitigatingFactorsEl.value = data.mitigating_factors || '';
                    if (exceptionDetailsEl) exceptionDetailsEl.value = data.exception_details || '';
                    if (conclusionEl) conclusionEl.value = data.conclusion || '';
                    if (improvementPlanEl) improvementPlanEl.value = data.improvement_plan || '';

                    // 설계평가 대체 체크박스 복원
                    const useDesignEvaluationEl = document.getElementById('use_design_evaluation');
                    if (useDesignEvaluationEl) {
                        useDesignEvaluationEl.checked = data.use_design_evaluation || false;
                        // 체크되어 있으면 필드 비활성화
                        if (data.use_design_evaluation) {
                            disableEvaluationFields(true);
                            const designEvaluationInfoSection = document.getElementById('design-evaluation-info-section');
                            if (designEvaluationInfoSection) {
                                designEvaluationInfoSection.style.display = 'block';
                                // 설계평가 정보 재표시
                                const infoDiv = document.getElementById('design-evaluation-info');
                                if (infoDiv) {
                                    infoDiv.innerHTML = '<div class="alert alert-info"><small>설계평가 결과로 운영평가를 대체하였습니다.</small></div>';
                                }
                            }
                        }
                    }
                }
            } else {
                // 폼 초기화
                if (operationEvaluationFormEl) operationEvaluationFormEl.reset();
                if (noOccurrenceEl) noOccurrenceEl.checked = false;

                // 예외 발견 수 기본값 0으로 설정
                if (exceptionCountEl) exceptionCountEl.value = 0;

                // 필드 표시 초기화
                if (evaluationFieldsEl) evaluationFieldsEl.style.display = 'block';
                if (noOccurrenceReasonSectionEl) noOccurrenceReasonSectionEl.style.display = 'none';
                if (typeof disableEvaluationFields === 'function') disableEvaluationFields(false);

                // 예외사항 관련 필드 숨기기 (초기 상태)
                toggleExceptionFields(false);
            }

            // 표본수 우선순위 설정
            // 1순위: 운영평가 라인에 저장된 sample_size (사용자가 조정한 값, 0 포함)
            // 2순위: RCM detail의 recommended_sample_size (관리자 설정, 0 포함)
            // 3순위: 통제주기 기반 기본값
            if (!evaluated_controls[controlCode] || ((evaluated_controls[controlCode].sample_size === null || evaluated_controls[controlCode].sample_size === undefined) && !evaluated_controls[controlCode].no_occurrence)) {
                let displaySampleSize;

                if (recommendedSampleSize !== null && recommendedSampleSize !== undefined) {
                    // RCM에 설정된 권장 표본수 사용 (0 포함)
                    displaySampleSize = recommendedSampleSize;
                    console.log('[표본수] RCM 권장 표본수 사용:', displaySampleSize);
                } else {
                    // 통제주기 기반 기본값
                    displaySampleSize = getDefaultSampleSize(controlFrequency, controlType);
                    console.log('[표본수] 통제주기 기반 기본값 사용:', displaySampleSize);
                }

                if (sampleSizeEl) sampleSizeEl.value = displaySampleSize;
            } else if (evaluated_controls[controlCode] && (evaluated_controls[controlCode].sample_size !== null && evaluated_controls[controlCode].sample_size !== undefined)) {
                // 운영평가 라인에 이미 저장된 값이 있으면 그대로 표시 (0 포함)
                const savedSampleSize = evaluated_controls[controlCode].sample_size;
                if (sampleSizeEl) sampleSizeEl.value = savedSampleSize;
                console.log('[표본수] 운영평가 라인 저장값 사용:', savedSampleSize);
            }

            // 먼저 기존 샘플 테이블 완전히 비우기 (다른 통제의 데이터가 보이는 것 방지)
            const tbody = document.getElementById('sample-lines-tbody');
            if (tbody) {
                tbody.innerHTML = '';
            }
            const container = document.getElementById('sample-lines-container');
            if (container) {
                container.style.display = 'none';
            }

            // 평가 버튼 클릭할 때마다 line_id로 샘플 데이터 조회 (캐시 사용 안 함)
            console.log('[openOperationEvaluationModal] evaluated_controls[controlCode]:', evaluated_controls[controlCode]);
            console.log('[openOperationEvaluationModal] line_id 존재?', evaluated_controls[controlCode] && evaluated_controls[controlCode].line_id);

            if (evaluated_controls[controlCode] && evaluated_controls[controlCode].line_id) {
                const lineId = evaluated_controls[controlCode].line_id;
                console.log('[openOperationEvaluationModal] ✓ line_id 있음 - 샘플 데이터 조회 시작 - line_id:', lineId, '(매번 새로 조회)');

                // 먼저 기존 샘플 데이터 제거
                evaluated_controls[controlCode].sample_lines = [];

                // API 호출하여 샘플 데이터 조회 (평가 버튼 클릭할 때마다 실행)
                fetch(`/api/operation-evaluation/samples/${lineId}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('[API 응답 전체]', data);
                        console.log('[API 응답] data.success:', data.success);
                        console.log('[API 응답] data.samples:', data.samples);
                        console.log('[API 응답] data.samples.length:', data.samples ? data.samples.length : 'undefined');

                        if (data.success) {
                            // 샘플이 0개여도 빈 배열로 업데이트 (기존 데이터 제거)
                            evaluated_controls[controlCode].sample_lines = data.samples || [];

                            if (data.samples && data.samples.length > 0) {
                                console.log('[openOperationEvaluationModal] 샘플 데이터 조회 성공:', data.samples);
                                // 현재 표본수 확인
                                const currentSampleSizeEl = document.getElementById('sample_size');
                                const currentSampleSize = currentSampleSizeEl ? currentSampleSizeEl.value : 'undefined';
                                console.log('[openOperationEvaluationModal] 현재 표본수:', currentSampleSize);
                                // 샘플 라인 자동 생성 (순차 실행)
                                generateSampleLines();
                            } else {
                                console.log('[openOperationEvaluationModal] 샘플 데이터 없음 (0개)');
                                // 샘플이 없으면 빈 라인 자동 생성
                                console.log('[openOperationEvaluationModal] 권장 표본수:', recommendedSampleSize, '- 빈 라인 생성');

                                // recommendedSampleSize가 있으면 DOM에 설정하고 change 이벤트 발생
                                if (recommendedSampleSize > 0) {
                                    const sampleSizeEl = document.getElementById('sample_size');
                                    if (sampleSizeEl) {
                                        sampleSizeEl.value = recommendedSampleSize;
                                        console.log('[openOperationEvaluationModal] sample_size 필드에 설정:', recommendedSampleSize);

                                        // change 이벤트 발생시켜 onchange 핸들러 실행 (generateSampleLines() 호출)
                                        const event = new Event('change', { bubbles: true });
                                        sampleSizeEl.dispatchEvent(event);
                                        console.log('[openOperationEvaluationModal] change 이벤트 발생 완료');
                                    } else {
                                        console.error('[openOperationEvaluationModal] sample_size 요소를 찾을 수 없음!');
                                    }
                                } else {
                                    console.log('[openOperationEvaluationModal] 권장 표본수가 0이므로 라인 생성 안 함');
                                }
                            }
                        } else {
                            console.error('[openOperationEvaluationModal] API 응답 실패:', data.message);
                        }
                    })
                    .catch(error => {
                        console.error('[openOperationEvaluationModal] 샘플 데이터 조회 실패:', error);
                    });
            } else {
                // line_id가 없는 경우 (아직 평가 안 한 통제)
                // 표본 크기가 설정되어 있으면 빈 테이블 생성
                console.log('[openOperationEvaluationModal] line_id 없음 - 신규 평가');
                console.log('[openOperationEvaluationModal] recommendedSampleSize:', recommendedSampleSize);

                if (recommendedSampleSize > 0) {
                    console.log('[openOperationEvaluationModal] 권장 표본수 > 0, 빈 라인 생성');
                    // DOM에 값 설정
                    const sampleSizeEl = document.getElementById('sample_size');
                    if (sampleSizeEl) {
                        sampleSizeEl.value = recommendedSampleSize;
                        console.log('[openOperationEvaluationModal] sample_size 필드에 설정:', recommendedSampleSize);
                    }
                    // 순차적으로 라인 생성
                    generateSampleLines();
                } else {
                    console.log('[openOperationEvaluationModal] 권장 표본수 = 0, 테이블 비우기');
                    const tbody = document.getElementById('sample-lines-tbody');
                    if (tbody) {
                        tbody.innerHTML = '';
                    }
                    const container = document.getElementById('sample-lines-container');
                    if (container) {
                        container.style.display = 'none';
                    }
                }
            }

            // 예외 발견 수에 따른 결론 자동 업데이트 (발생사실 없음이 아닐 때만)
            if (noOccurrenceEl && !noOccurrenceEl.checked) {
                if (typeof updateConclusionBasedOnExceptions === 'function') updateConclusionBasedOnExceptions();
            }

            // 표본수 입력 필드에 change 이벤트 리스너 등록
            const sampleSizeInput = document.getElementById('sample_size');
            if (sampleSizeInput) {
                // 기존 이벤트 리스너 제거 후 새로 등록 (중복 방지)
                sampleSizeInput.removeEventListener('change', validateSampleSize);
                sampleSizeInput.addEventListener('change', validateSampleSize);

                // 표본 크기 변경 시 자동으로 라인 생성
                sampleSizeInput.removeEventListener('change', autoGenerateSampleLines);
                sampleSizeInput.addEventListener('change', autoGenerateSampleLines);
            }

            // 예외 발견 수 입력 필드에 이벤트 리스너 등록 (표본 크기 초과 시 자동 조정)
            const exceptionCountInput = document.getElementById('exception_count');
            if (exceptionCountInput && sampleSizeInput) {
                // 예외 발견 수의 최대값을 표본 크기로 설정
                const currentSampleSize = parseInt(sampleSizeInput.value) || 0;
                if (currentSampleSize > 0) {
                    exceptionCountInput.setAttribute('max', currentSampleSize);
                }

                // 기존 이벤트 리스너 제거 후 새로 등록 (중복 방지)
                exceptionCountInput.removeEventListener('input', validateExceptionCount);
                exceptionCountInput.removeEventListener('change', validateExceptionCount);
                exceptionCountInput.removeEventListener('input', updateConclusionBasedOnExceptions);
                exceptionCountInput.removeEventListener('change', updateConclusionBasedOnExceptions);
                // input 이벤트로 실시간 검증 및 결론 업데이트
                exceptionCountInput.addEventListener('input', validateExceptionCount);
                exceptionCountInput.addEventListener('change', validateExceptionCount);
                exceptionCountInput.addEventListener('input', updateConclusionBasedOnExceptions);
                exceptionCountInput.addEventListener('change', updateConclusionBasedOnExceptions);
            }

            // 경감요소 입력 필드에 이벤트 리스너 등록
            const mitigatingFactorsInput = document.getElementById('mitigating_factors');
            if (mitigatingFactorsInput) {
                mitigatingFactorsInput.removeEventListener('input', updateConclusionBasedOnExceptions);
                mitigatingFactorsInput.addEventListener('input', updateConclusionBasedOnExceptions);
            }

            // 초기 결론 상태 설정
            if (typeof updateConclusionBasedOnExceptions === 'function') {
                updateConclusionBasedOnExceptions();
            }

            // 설계평가 이미지 표시
            displayDesignEvaluationImages(designEvaluationImages);

            // 다운로드 버튼 업데이트
            updateDownloadButton(controlCode, evaluated_controls[controlCode]);

            // 모달 표시
            const operationEvaluationModalEl = document.getElementById('operationEvaluationModal');
            if (operationEvaluationModalEl) {
                const modal = new bootstrap.Modal(operationEvaluationModalEl);
                modal.show();

                // 모달이 완전히 열린 후 표본 라인 자동 생성 (표본수가 설정되어 있고 샘플이 없는 경우)
                operationEvaluationModalEl.addEventListener('shown.bs.modal', function onModalShown() {
                    const sampleSizeEl = document.getElementById('sample_size');
                    const sampleSizeValue = sampleSizeEl ? sampleSizeEl.value.trim() : '';
                    const sampleSizeInt = parseInt(sampleSizeValue) || 0;
                    const tbody = document.getElementById('sample-lines-tbody');
                    const existingRows = tbody ? tbody.querySelectorAll('tr:not([id^="mitigation-row"])').length : 0;
                    const noOccurrenceSection = document.getElementById('no-occurrence-section');

                    console.log('[shown.bs.modal] 표본 크기:', sampleSizeValue, ', 기존 행 수:', existingRows);

                    // 당기 발생사실 없음 섹션 표시/숨김
                    if (noOccurrenceSection) {
                        if (sampleSizeValue === '0' || sampleSizeValue === '') {
                            noOccurrenceSection.style.display = 'block';
                        } else {
                            noOccurrenceSection.style.display = 'none';
                        }
                    }

                    // 표본 크기가 설정되어 있고, 기존 라인이 없으면 자동 생성
                    if (sampleSizeInt > 0 && existingRows === 0) {
                        console.log('[shown.bs.modal] 표본 라인 자동 생성 실행');
                        generateSampleLines();
                    }

                    // 이벤트 리스너 제거 (한 번만 실행)
                    operationEvaluationModalEl.removeEventListener('shown.bs.modal', onModalShown);
                }, { once: true });
            } else {
                console.error('operationEvaluationModal element not found');
                alert('운영평가 모달을 찾을 수 없습니다. 페이지를 새로고침 해주세요.');
            }
        }

        // 예외 발견 수 및 경감요소 변경 시 결론 필드 업데이트
        function updateConclusionBasedOnExceptions() {
            const exceptionCountInput = document.getElementById('exception_count');
            const mitigatingFactorsInput = document.getElementById('mitigating_factors');
            const conclusionSelect = document.getElementById('conclusion');
            const helpText = document.getElementById('conclusion-help-text');

            if (exceptionCountInput && conclusionSelect && mitigatingFactorsInput && helpText) {
                const exceptionCount = parseInt(exceptionCountInput.value) || 0;
                const hasMitigatingFactors = mitigatingFactorsInput.value.trim().length > 0;

                // 예외 발견 수가 0이면 경감요소 필드 비활성화
                if (exceptionCount === 0) {
                    mitigatingFactorsInput.disabled = true;
                    mitigatingFactorsInput.value = '';  // 값도 초기화
                    conclusionSelect.disabled = true;
                    conclusionSelect.value = 'effective';
                    helpText.textContent = '예외 발견 수에 따라 자동 설정됩니다';
                }
                // 예외가 있는 경우 경감요소 필드 활성화
                else {
                    mitigatingFactorsInput.disabled = false;

                    // 경감요소가 입력된 경우 결론을 수동 선택 가능하게
                    if (hasMitigatingFactors) {
                        conclusionSelect.disabled = false;
                        helpText.textContent = '경감요소가 있으므로 결론을 선택할 수 있습니다';
                        // 기본값은 exception이지만 사용자가 변경 가능
                        if (conclusionSelect.value === '') {
                            conclusionSelect.value = 'exception';
                        }
                    } else {
                        // 경감요소가 없으면 자동 설정
                        conclusionSelect.disabled = true;
                        conclusionSelect.value = 'exception';
                        helpText.textContent = '예외 발견 수에 따라 자동 설정됩니다';
                    }
                }
            }
        }

        // ===================================================================
        // 표본별 라인 입력 관련 함수들
        // ===================================================================

        // 표본 크기 변경 시 자동으로 라인 생성
        function autoGenerateSampleLines() {
            const sampleSizeInput = document.getElementById('sample_size');
            const sampleSizeValue = sampleSizeInput?.value?.trim() || '';

            // 공란, 0이거나 유효한 숫자인 경우 자동 생성
            if (sampleSizeValue === '' || sampleSizeValue === '0') {
                generateSampleLines(); // 공란/0 처리 (모집단 업로드 모드)
            } else {
                const sampleSize = parseInt(sampleSizeValue);
                if (!isNaN(sampleSize) && sampleSize >= 1 && sampleSize <= 100) {
                    generateSampleLines();
                }
            }
        }

        // 표본 라인 생성
        function generateSampleLines() {
            const sampleSizeInput = document.getElementById('sample_size');
            const sampleSizeValue = sampleSizeInput.value.trim();
            const tbody = document.getElementById('sample-lines-tbody');
            const thead = document.getElementById('sample-lines-thead');
            const noOccurrenceSection = document.getElementById('no-occurrence-section');

            // 표본 크기에 따라 "당기 발생사실 없음" 섹션 표시/숨김
            if (noOccurrenceSection) {
                if (sampleSizeValue === '0' || sampleSizeValue === '') {
                    // 표본 크기가 0이거나 공란인 경우에만 표시
                    noOccurrenceSection.style.display = 'block';
                } else {
                    // 표본이 있는 경우 숨김
                    noOccurrenceSection.style.display = 'none';
                    const noOccurrenceCheckbox = document.getElementById('no_occurrence');
                    if (noOccurrenceCheckbox) {
                        noOccurrenceCheckbox.checked = false;
                    }
                }
            }

            // 전역 변수에서 RCM attribute 정보 가져오기
            const popAttrCount = window.currentPopulationAttributeCount || 0;
            const attributes = window.currentAttributeNames || {};

            // 설정된 attribute가 있는지 확인
            const hasAttributes = Object.values(attributes).some(v => v);

            // 테이블 헤더 동적 생성
            let headerHtml = '<tr><th width="5%">표본 #</th>';

            if (hasAttributes) {
                // attribute 컬럼 추가 (모집단/증빙 구분 표시)
                for (let i = 0; i < 10; i++) {
                    const attrName = attributes[`attribute${i}`];
                    if (attrName) {
                        const isPopulation = i < popAttrCount;
                        const badge = isPopulation
                            ? '<span class="badge bg-primary ms-1" style="font-size: 0.7em;">모집단</span>'
                            : '<span class="badge bg-success ms-1" style="font-size: 0.7em;">증빙</span>';
                        headerHtml += `<th>${attrName}${badge}</th>`;
                    }
                }
            } else {
                // 기본 컬럼
                headerHtml += '<th width="70%">증빙 내용</th>';
            }

            headerHtml += '<th width="15%">결과</th></tr>';
            thead.innerHTML = headerHtml;

            // 공란 또는 0인 경우: 업로드된 샘플이 있으면 표시, 없으면 비우기
            if (sampleSizeValue === '' || sampleSizeValue === '0') {
                // evaluated_controls에서 업로드된 샘플 확인
                const existingData = evaluated_controls[currentControlCode];
                const existingSampleLines = existingData?.sample_lines || [];

                console.log('[generateSampleLines] currentControlCode:', currentControlCode);
                console.log('[generateSampleLines] existingData:', existingData);
                console.log('[generateSampleLines] existingSampleLines:', existingSampleLines);

                if (existingSampleLines.length > 0) {
                    // 업로드된 샘플이 있으면 표시
                    console.log(`[generateSampleLines] 업로드된 샘플 ${existingSampleLines.length}개 표시`);
                    tbody.innerHTML = '';

                    existingSampleLines.forEach((sample, index) => {
                        const row = document.createElement('tr');
                        const sampleNum = sample.sample_number || index + 1;

                        console.log(`[generateSampleLines] Sample #${sampleNum}:`, sample);
                        console.log(`[generateSampleLines] Sample attributes:`, sample.attributes);

                        let rowHtml = `<td class="text-center align-middle">#${sampleNum}</td>`;

                        // 표본 크기 확인 (0인 경우 모집단 업로드 모드)
                        const sampleSizeEl = document.getElementById('sample_size');
                        const currentSampleSize = sampleSizeEl ? parseInt(sampleSizeEl.value) || 0 : 0;
                        const isPopulationUploadMode = currentSampleSize === 0;

                        // attribute 컬럼들 추가
                        for (let i = 0; i < 10; i++) {
                            const attrName = attributes[`attribute${i}`];
                            if (attrName) {
                                const isPopulation = i < popAttrCount;
                                const attrValue = sample.attributes?.[`attribute${i}`] || '';

                                console.log(`[generateSampleLines] attr${i}: name="${attrName}", isPopulation=${isPopulation}, value="${attrValue}", uploadMode=${isPopulationUploadMode}`);

                                // 모집단 업로드 모드(표본수=0)에서는 모집단 필드를 readonly로
                                // 수동 선택 모드(표본수>0)에서는 모든 필드를 입력 가능하게
                                if (isPopulation && isPopulationUploadMode) {
                                    // 모집단 업로드 모드: 모집단 attribute - 텍스트로 표시
                                    rowHtml += `<td class="align-middle bg-light" style="padding: 0.5rem;">
                                        <span id="sample-attr${i}-${sampleNum}" style="display: block; min-height: 31px; line-height: 31px;">${attrValue}</span>
                                    </td>`;
                                } else {
                                    // 수동 선택 모드 또는 증빙 attribute - 입력 가능
                                    const bgClass = isPopulation ? 'bg-light' : '';
                                    rowHtml += `<td class="align-middle ${bgClass}">
                                        <input type="text" class="form-control form-control-sm"
                                               id="sample-attr${i}-${sampleNum}"
                                               value="${attrValue}"
                                               placeholder="${attrName}">
                                    </td>`;
                                }
                            }
                        }

                        // 결과 컬럼
                        rowHtml += `<td class="align-middle">
                            <select class="form-select form-select-sm"
                                    id="sample-result-${sampleNum}"
                                    onchange="handleSampleResultChange(${sampleNum})">
                                <option value="no_exception" ${sample.result !== 'exception' ? 'selected' : ''}>No Exception</option>
                                <option value="exception" ${sample.result === 'exception' ? 'selected' : ''}>Exception</option>
                            </select>
                        </td>`;

                        row.innerHTML = rowHtml;
                        tbody.appendChild(row);

                        // Exception인 경우 완화조치 행 추가
                        if (sample.result === 'exception') {
                            const mitigationRow = document.createElement('tr');
                            mitigationRow.id = `mitigation-row-${sampleNum}`;

                            // colspan 계산: 표본# + attribute 컬럼 수 + 결과
                            const attrCount = Object.keys(attributes).filter(k => attributes[k]).length;
                            const totalCols = 1 + attrCount + 1;

                            mitigationRow.innerHTML = `
                                <td colspan="${totalCols}" class="bg-light">
                                    <label class="form-label fw-bold mb-1">완화조치:</label>
                                    <textarea class="form-control form-control-sm"
                                           id="sample-mitigation-${sampleNum}"
                                           rows="2"
                                           placeholder="완화조치 내용 입력">${sample.mitigation || ''}</textarea>
                                </td>
                            `;
                            tbody.appendChild(mitigationRow);
                        }
                    });
                    return;
                } else {
                    // 업로드된 샘플이 없으면 테이블 비우기
                    tbody.innerHTML = '';
                    return;
                }
            }

            const sampleSize = parseInt(sampleSizeValue);

            if (isNaN(sampleSize) || sampleSize < 1 || sampleSize > 100) {
                alert('표본 크기는 1에서 100 사이여야 합니다.');
                return;
            }

            // ⭐ 기존 라인을 초기화하기 전에 현재 화면의 입력값을 먼저 수집
            const currentInputData = [];
            const existingRows = tbody.querySelectorAll('tr:not([id^="mitigation-row"])');
            existingRows.forEach((row, index) => {
                const sampleNumber = index + 1;
                const evidenceEl = document.getElementById(`sample-evidence-${sampleNumber}`);
                const resultEl = document.getElementById(`sample-result-${sampleNumber}`);
                const mitigationEl = document.getElementById(`sample-mitigation-${sampleNumber}`);

                // attribute 데이터 수집
                const attributeData = {};
                for (let i = 0; i < 10; i++) {
                    const attrEl = document.getElementById(`sample-attr${i}-${sampleNumber}`);
                    if (attrEl) {
                        // input/select인 경우 value, span인 경우 textContent
                        if (attrEl.tagName === 'SPAN') {
                            attributeData[`attribute${i}`] = attrEl.textContent.trim() || '';
                        } else {
                            attributeData[`attribute${i}`] = attrEl.value || '';
                        }
                    }
                }

                // resultEl이 있으면 데이터 저장 (evidenceEl이나 attribute 중 하나라도 있으면)
                if (resultEl && (evidenceEl || Object.keys(attributeData).length > 0)) {
                    currentInputData.push({
                        sample_number: sampleNumber,
                        evidence: evidenceEl ? (evidenceEl.value || '') : '',
                        result: resultEl.value || 'no_exception',
                        mitigation: mitigationEl ? (mitigationEl.value || '') : '',
                        attributes: attributeData
                    });
                }
            });

            // 이제 기존 라인 초기화
            tbody.innerHTML = '';

            // 기존 샘플 데이터 가져오기 (DB에서 로드된 데이터)
            console.log('===========================================');
            console.log('[generateSampleLines] START');
            console.log('[generateSampleLines] currentControlCode:', currentControlCode);
            console.log('[generateSampleLines] evaluated_controls 전체:', evaluated_controls);
            console.log('[generateSampleLines] evaluated_controls[currentControlCode]:', evaluated_controls[currentControlCode]);

            const existingData = evaluated_controls[currentControlCode];
            console.log('[generateSampleLines] existingData:', existingData);

            const existingSampleLines = existingData?.sample_lines || [];
            console.log('[generateSampleLines] existingSampleLines:', existingSampleLines);
            console.log('[generateSampleLines] existingSampleLines.length:', existingSampleLines.length);
            console.log('[generateSampleLines] currentInputData:', currentInputData);
            console.log('[generateSampleLines] currentInputData.length:', currentInputData.length);
            console.log('[generateSampleLines] currentDesignEvaluationEvidence:', currentDesignEvaluationEvidence);

            // SQL 쿼리 시뮬레이션 출력
            if (existingData && existingData.line_id) {
                console.log(`[SQL Query 시뮬레이션]
                    SELECT sample_id, sample_number, evidence, has_exception, mitigation
                    FROM sb_evaluation_sample
                    WHERE line_id = ${existingData.line_id}
                    ORDER BY sample_number
                `);
            }
            console.log('===========================================');

            // 표본 크기만큼 라인 생성
            for (let i = 1; i <= sampleSize; i++) {
                // 우선순위: 1) 현재 화면 입력값, 2) DB에서 로드된 데이터, 3) 설계평가 증빙 (신규 생성 시)
                const currentInput = currentInputData.find(s => s.sample_number === i);
                const existingSample = existingSampleLines.find(s => s.sample_number === i);

                // 현재 화면에 입력된 값이 있으면 우선 사용, 없으면 DB 데이터 사용, 첫 번째 라인(#1)만 설계평가 증빙 사용
                const evidence = currentInput?.evidence || existingSample?.evidence || (i === 1 ? currentDesignEvaluationEvidence : '') || '';
                const result = currentInput?.result || existingSample?.result || 'no_exception';
                const mitigation = currentInput?.mitigation || existingSample?.mitigation || '';

                const row = document.createElement('tr');
                let rowHtml = `<td class="text-center align-middle">#${i}</td>`;

                // attribute 컬럼들 추가
                if (hasAttributes) {
                    // 업로드된 표본 개수 확인
                    const uploadedSampleCount = existingSampleLines.length;

                    // 설계평가 attribute 데이터 파싱 (sample #1에만 적용)
                    let designEvaluationAttrs = {};
                    if (i === 1 && currentDesignEvaluationEvidence) {
                        try {
                            designEvaluationAttrs = JSON.parse(currentDesignEvaluationEvidence);
                        } catch (e) {
                            // JSON이 아니면 빈 객체 유지
                            console.log('[generateSampleLines] Design evaluation evidence is not JSON:', currentDesignEvaluationEvidence);
                        }
                    }

                    for (let attrIdx = 0; attrIdx < 10; attrIdx++) {
                        const attrName = attributes[`attribute${attrIdx}`];
                        if (attrName) {
                            // 우선순위: 현재 입력 > DB 데이터 > 설계평가 데이터 (sample #1만) > 빈 값
                            const attrValue = currentInput?.attributes?.[`attribute${attrIdx}`] ||
                                existingSample?.attributes?.[`attribute${attrIdx}`] ||
                                (i === 1 ? designEvaluationAttrs[`attribute${attrIdx}`] || '' : '') || '';

                            // 모집단 필드인지 확인
                            const isPopulation = attrIdx < popAttrCount;

                            // 표본수 확인 (0인 경우 모집단 업로드 모드)
                            const currentSampleSize = parseInt(sampleSizeValue) || 0;
                            const isPopulationUploadMode = currentSampleSize === 0;

                            // 업로드된 표본 범위 내이고 모집단 필드이며 모집단 업로드 모드인 경우에만 읽기 전용
                            const isFromUpload = i <= uploadedSampleCount;
                            const isReadonly = isPopulation && isFromUpload && isPopulationUploadMode;

                            if (isReadonly) {
                                // 모집단 업로드 모드: 모집단 필드 - 텍스트로 표시
                                rowHtml += `<td class="align-middle bg-light" style="padding: 0.5rem;">
                                    <span id="sample-attr${attrIdx}-${i}" style="display: block; min-height: 31px; line-height: 31px;">${attrValue}</span>
                                </td>`;
                            } else {
                                // 수동 선택 모드 또는 증빙 필드 - 입력 가능
                                const bgClass = isPopulation ? 'bg-light' : '';
                                rowHtml += `<td class="align-middle ${bgClass}">
                                    <input type="text" class="form-control form-control-sm"
                                           id="sample-attr${attrIdx}-${i}"
                                           placeholder="${attrName}"
                                           value="${attrValue}"
                                           oninput="updateOverallConclusion()"
                                           style="height: 31px;" />
                                </td>`;
                            }
                        }
                    }
                } else {
                    // 기본 증빙 컬럼
                    rowHtml += `<td class="align-middle">
                        <input type="text" class="form-control form-control-sm"
                               id="sample-evidence-${i}"
                               placeholder="예: 증빙서류 확인"
                               value="${evidence}"
                               oninput="updateOverallConclusion()"
                               style="height: 31px;" />
                    </td>`;
                }

                // 결과 컬럼
                rowHtml += `<td class="align-middle">
                    <select class="form-select form-select-sm"
                            id="sample-result-${i}"
                            onchange="handleSampleResultChange(${i})"
                            style="height: 31px;">
                        <option value="no_exception" ${result === 'no_exception' ? 'selected' : ''}>No Exception</option>
                        <option value="exception" ${result === 'exception' ? 'selected' : ''}>Exception</option>
                    </select>
                </td>`;

                row.innerHTML = rowHtml;
                tbody.appendChild(row);

                // Exception 선택 시 경감요소 입력란을 행 아래에 추가
                if (result === 'exception') {
                    // colspan 계산: 표본# + attribute 컬럼 수 (또는 증빙 컬럼) + 결과
                    const attrCount = hasAttributes ? Object.keys(attributes).filter(k => attributes[k]).length : 1;
                    const totalCols = 1 + attrCount + 1;

                    const mitigationRow = document.createElement('tr');
                    mitigationRow.id = `mitigation-row-${i}`;
                    mitigationRow.innerHTML = `
                        <td colspan="${totalCols}" class="bg-light">
                            <div class="p-2">
                                <label class="form-label fw-bold mb-1" style="font-size: 0.875rem;">경감요소:</label>
                                <input type="text" class="form-control form-control-sm"
                                       id="sample-mitigation-${i}"
                                       placeholder="경감요소를 입력하세요"
                                       value="${mitigation}"
                                       oninput="updateOverallConclusion()"
                                       style="height: 31px;" />
                            </div>
                        </td>
                    `;
                    tbody.appendChild(mitigationRow);
                }
            }

            // 컨테이너 표시
            document.getElementById('sample-lines-container').style.display = 'block';

            // 전체 결론 업데이트
            updateOverallConclusion();
        }

        // 표본 결과 변경 처리
        function handleSampleResultChange(sampleNumber) {
            const resultSelect = document.getElementById(`sample-result-${sampleNumber}`);
            const existingMitigationRow = document.getElementById(`mitigation-row-${sampleNumber}`);

            if (resultSelect.value === 'exception') {
                // Exception 선택 시 경감요소 행 추가
                // 경감요소 행이 없으면 추가
                if (!existingMitigationRow) {
                    const tbody = document.getElementById('sample-lines-tbody');
                    const currentRow = resultSelect.closest('tr');

                    // 현재 행의 컬럼 수 계산
                    const colCount = currentRow.cells.length;

                    const mitigationRow = document.createElement('tr');
                    mitigationRow.id = `mitigation-row-${sampleNumber}`;
                    mitigationRow.innerHTML = `
                        <td colspan="${colCount}" class="bg-light">
                            <div class="p-2">
                                <label class="form-label fw-bold mb-1" style="font-size: 0.875rem;">경감요소:</label>
                                <input type="text" class="form-control form-control-sm"
                                       id="sample-mitigation-${sampleNumber}"
                                       placeholder="경감요소를 입력하세요"
                                       value=""
                                       oninput="updateOverallConclusion()"
                                       style="height: 31px;" />
                            </div>
                        </td>
                    `;
                    currentRow.insertAdjacentElement('afterend', mitigationRow);
                }
            } else {
                // No Exception 선택 시 경감요소 행 제거
                if (existingMitigationRow) {
                    existingMitigationRow.remove();
                }
            }

            // 전체 결론 업데이트
            updateOverallConclusion();
        }

        // 전체 결론 자동 계산
        function updateOverallConclusion() {
            const sampleSizeInput = document.getElementById('sample_size');
            const sampleSize = parseInt(sampleSizeInput.value) || 0;
            const conclusionSpan = document.getElementById('overall-conclusion');
            const summaryDiv = document.getElementById('conclusion-summary');

            if (sampleSize === 0) {
                // 표본 크기가 0이면 결론을 표시하지 않음
                conclusionSpan.textContent = '-';
                conclusionSpan.className = 'badge bg-secondary ms-2';
                summaryDiv.innerHTML = `<small>표본별 결과를 입력하면 자동으로 계산됩니다.</small>`;
                return;
            }

            let noExceptionCount = 0;
            let exceptionWithMitigationCount = 0;
            let exceptionWithoutMitigationCount = 0;
            let evidenceFilledCount = 0;  // 증빙 내용이 입력된 표본 수

            // 표본 크기만큼 각 표본 확인
            for (let i = 1; i <= sampleSize; i++) {
                const resultSelect = document.getElementById(`sample-result-${i}`);
                if (!resultSelect) continue;

                const resultValue = resultSelect.value;
                if (resultValue === 'no_exception') {
                    noExceptionCount++;
                } else if (resultValue === 'exception') {
                    // Exception인 경우 경감요소 확인
                    const mitigationInput = document.getElementById(`sample-mitigation-${i}`);
                    const hasMitigation = mitigationInput && mitigationInput.value.trim().length > 0;
                    if (hasMitigation) {
                        exceptionWithMitigationCount++;
                    } else {
                        exceptionWithoutMitigationCount++;
                    }
                }
            }

            // 결론 계산
            if (exceptionWithoutMitigationCount > 0) {
                conclusionSpan.textContent = 'Ineffective';
                conclusionSpan.className = 'badge bg-danger ms-2';
                summaryDiv.innerHTML = `
                    <small>
                        <i class="fas fa-times-circle text-danger me-1"></i>
                        경감요소 없는 예외 ${exceptionWithoutMitigationCount}건 발견
                    </small>
                `;
            } else {
                // 모든 Exception에 경감요소가 있거나 Exception이 없으면 Effective
                conclusionSpan.textContent = 'Effective';
                conclusionSpan.className = 'badge bg-success ms-2';
                summaryDiv.innerHTML = `
                    <small>
                        <i class="fas fa-check-circle text-success me-1"></i>
                        No Exception: ${noExceptionCount}건, 경감요소 있는 Exception: ${exceptionWithMitigationCount}건
                    </small>
                `;
            }
        }

        // 예외사항 관련 필드 표시/숨기기
        function toggleExceptionFields(show) {
            const exceptionDetailsSection = document.getElementById('exception-details-section');
            const improvementPlanSection = document.getElementById('improvement-plan-section');

            if (exceptionDetailsSection) {
                exceptionDetailsSection.style.display = show ? 'block' : 'none';
            }
            if (improvementPlanSection) {
                improvementPlanSection.style.display = show ? 'block' : 'none';
            }

            // Exception이 없을 때는 필드 내용도 초기화
            if (!show) {
                const exceptionDetailsTextarea = document.getElementById('exception_details');
                const improvementPlanTextarea = document.getElementById('improvement_plan');
                if (exceptionDetailsTextarea) exceptionDetailsTextarea.value = '';
                if (improvementPlanTextarea) improvementPlanTextarea.value = '';
            }
        }

        // ===================================================================
        // 기존 함수들
        // ===================================================================

        document.addEventListener('DOMContentLoaded', function () {
            // 당기 발생사실 없음 체크박스 이벤트 리스너 (모달 외부의 체크박스용)
            const noOccurrenceCheckbox = document.getElementById('no_occurrence');
            if (noOccurrenceCheckbox) {
                noOccurrenceCheckbox.addEventListener('change', toggleNoOccurrenceFields);
            }
        });

        // 표본 크기 검증 함수
        function validateSampleSize() {
            const sampleSizeInput = document.getElementById('sample_size');
            const exceptionCountInput = document.getElementById('exception_count');
            const messageDiv = document.getElementById('sampleSizeMessage');
            const inputValue = parseInt(sampleSizeInput.value) || 0;

            // RCM에 설정된 권장 표본수보다 작은지 확인
            if (recommendedSampleSize > 0 && inputValue < recommendedSampleSize) {
                showWarningToast(`표본 크기는 권장 표본수인 ${recommendedSampleSize}개 이상이어야 합니다.`);
                sampleSizeInput.value = recommendedSampleSize;
                // 자동으로 라인 재생성
                setTimeout(generateSampleLines, 100);
                return; // 유효성 검사 실패 시 아래 로직은 실행하지 않음
            }

            // 예외 발견 수의 최대값을 새로운 표본 크기로 업데이트
            if (exceptionCountInput && inputValue > 0) {
                exceptionCountInput.setAttribute('max', inputValue);
                // 현재 예외 발견 수가 새로운 표본 크기를 초과하면 자동 조정
                validateExceptionCount();
            }

            // 통제주기 기반 권장 표본수와 비교
            if (recommendedSampleSize > 0 && inputValue !== recommendedSampleSize) {
                let messageClass = 'text-warning';
                let icon = 'fa-info-circle';
                let message = '';

                if (inputValue < recommendedSampleSize) {
                    messageClass = 'text-danger';
                    icon = 'fa-exclamation-triangle';
                    message = `권장(${recommendedSampleSize}개)보다 적습니다`;
                } else if (inputValue > recommendedSampleSize) {
                    messageClass = 'text-info';
                    icon = 'fa-info-circle';
                    message = `권장(${recommendedSampleSize}개)보다 많습니다`;
                }

                messageDiv.innerHTML = `
                    <small class="${messageClass}">
                        <i class="fas ${icon} me-1"></i>${message}
                    </small>
                `;
                messageDiv.style.display = 'block';
            } else {
                // 권장 표본수와 일치하면 메시지 숨김
                messageDiv.style.display = 'none';
            }
        }

        // 통제주기 코드를 이름으로 변환
        function getFrequencyName(controlFrequency) {
            if (!controlFrequency) return '알 수 없음';
            const frequencyCode = controlFrequency.charAt(0).toUpperCase();
            const frequencyNames = {
                'A': '연간',
                'Q': '분기',
                'M': '월',
                'W': '주',
                'D': '일',
                'O': '기타',
                'N': '필요시'
            };
            return frequencyNames[frequencyCode] || controlFrequency;
        }

        // 예외 발견 수가 표본 크기를 초과하지 않도록 자동 조정
        function validateExceptionCount() {
            const sampleSizeInput = document.getElementById('sample_size');
            const exceptionCountInput = document.getElementById('exception_count');

            const sampleSize = parseInt(sampleSizeInput.value) || 0;
            const exceptionCount = parseInt(exceptionCountInput.value) || 0;

            // 표본 크기를 초과하면 자동으로 표본 크기로 변경 (메시지 없이)
            if (exceptionCount > sampleSize) {
                exceptionCountInput.value = sampleSize;
            }
            return true;
        }


        // 당기 발생사실 없음 체크 시 필드 토글
        function toggleNoOccurrenceFields() {
            const noOccurrenceCheckbox = document.getElementById('no_occurrence');
            const useDesignEvaluationCheckbox = document.getElementById('use_design_evaluation');
            const evaluationFields = document.getElementById('evaluation-fields');
            const noOccurrenceReasonSection = document.getElementById('no-occurrence-reason-section');

            if (noOccurrenceCheckbox.checked) {
                // 설계평가 대체 체크박스 해제
                if (useDesignEvaluationCheckbox) {
                    useDesignEvaluationCheckbox.checked = false;
                }

                // 평가 필드 숨기고 비활성화
                evaluationFields.style.display = 'none';
                disableEvaluationFields(true);

                // 발생하지 않은 사유 입력란 표시
                noOccurrenceReasonSection.style.display = 'block';
            } else {
                // 평가 필드 표시하고 활성화
                evaluationFields.style.display = 'block';
                disableEvaluationFields(false);

                // 발생하지 않은 사유 입력란 숨김
                noOccurrenceReasonSection.style.display = 'none';
            }
        }

        // 평가 필드 활성화/비활성화
        function disableEvaluationFields(disable) {
            const fields = [
                'sample_size',
                'exception_count',
                'mitigating_factors',
                'exception_details',
                'improvement_plan',
                'sampleExcelFile'
            ];

            fields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    if (disable) {
                        field.disabled = true;
                        field.removeAttribute('required');
                    } else {
                        field.disabled = false;
                    }
                }
            });
        }

        // 엑셀 파일 미리보기
        document.getElementById('sampleExcelFile').addEventListener('change', function (e) {
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
            console.log('===== saveOperationEvaluation 호출됨 =====');

            // 변수 선언을 함수 최상단으로 이동
            let formData;

            try {
                console.log('=== saveOperationEvaluation 시작 ===');
                console.log('currentRcmId:', currentRcmId, '(type:', typeof currentRcmId, ')');
                console.log('currentEvaluationSession:', currentEvaluationSession, '(type:', typeof currentEvaluationSession, ')');
                console.log('currentControlCode:', currentControlCode, '(type:', typeof currentControlCode, ')');

                // 필수 변수 검증
                if (!currentRcmId) {
                    console.error('❌ RCM ID가 설정되지 않음');
                    alert('RCM ID가 설정되지 않았습니다.');
                    throw new Error('RCM ID가 설정되지 않았습니다.');
                }
                if (!currentEvaluationSession) {
                    console.error('❌ 평가 세션이 설정되지 않음');
                    alert('평가 세션이 설정되지 않았습니다.');
                    throw new Error('평가 세션이 설정되지 않았습니다.');
                }
                if (!currentControlCode) {
                    console.error('❌ 통제 코드가 설정되지 않음');
                    alert('통제 코드가 설정되지 않았습니다.');
                    throw new Error('통제 코드가 설정되지 않았습니다.');
                }

                const form = document.getElementById('operationEvaluationForm');
                console.log('폼 요소 검색 결과:', form);
                if (!form) {
                    console.error('❌ 폼을 찾을 수 없음');
                    alert('폼을 찾을 수 없습니다.');
                    return;
                }

                formData = new FormData(form);
                console.log('✅ FormData 생성 완료');
            } catch (error) {
                console.error('❌ saveOperationEvaluation 초기화 오류:', error);
                alert('저장 초기화 중 오류 발생: ' + error.message);
                return;
            }

            try {
                // 당기 발생사실 없음 체크 확인
                const noOccurrenceEl = document.getElementById('no_occurrence');
                const noOccurrence = noOccurrenceEl ? noOccurrenceEl.checked : false;

                // 설계평가 대체 체크 확인
                const useDesignEvaluationEl = document.getElementById('use_design_evaluation');
                const useDesignEvaluation = useDesignEvaluationEl ? useDesignEvaluationEl.checked : false;

                let evaluationData;

                if (noOccurrence) {
                    // 당기 발생사실 없음인 경우
                    const noOccurrenceReason = formData.get('no_occurrence_reason') || '';

                    evaluationData = {
                        sample_size: 0,
                        exception_count: 0,
                        exception_details: '',
                        conclusion: 'effective',
                        improvement_plan: '',
                        no_occurrence: true,
                        no_occurrence_reason: noOccurrenceReason.trim(),
                        use_design_evaluation: false
                    };
                } else {
                    // 일반 평가인 경우
                    // 표본 라인별 데이터 수집
                    const sampleSize = parseInt(formData.get('sample_size')) || 0;
                    const sampleLines = [];
                    let exceptionCount = 0;
                    let exceptionWithoutMitigationCount = 0;

                    for (let i = 1; i <= sampleSize; i++) {
                        const evidenceEl = document.getElementById(`sample-evidence-${i}`);
                        const resultEl = document.getElementById(`sample-result-${i}`);
                        const mitigationEl = document.getElementById(`sample-mitigation-${i}`);

                        // attribute 데이터 수집
                        const attributes = {};
                        for (let attrIdx = 0; attrIdx < 10; attrIdx++) {
                            const attrEl = document.getElementById(`sample-attr${attrIdx}-${i}`);
                            if (attrEl) {
                                attributes[`attribute${attrIdx}`] = attrEl.value || '';
                            }
                        }

                        // 표본 행이 있으면 무조건 저장 (증빙값 없어도 저장)
                        const result = resultEl ? (resultEl.value || 'no_exception') : 'no_exception';
                        const mitigation = mitigationEl ? (mitigationEl.value || '') : '';

                        const sampleData = {
                            sample_number: i,
                            evidence: evidenceEl ? (evidenceEl.value || '') : '',
                            result: result,
                            mitigation: mitigation
                        };

                        // attribute 데이터가 있으면 추가
                        if (Object.keys(attributes).length > 0) {
                            sampleData.attributes = attributes;
                        }

                        sampleLines.push(sampleData);

                        // Exception 카운트 계산
                        if (result === 'exception') {
                            exceptionCount++;
                            // 경감요소 없는 Exception 카운트
                            if (!mitigation.trim()) {
                                exceptionWithoutMitigationCount++;
                            }
                        }
                    }

                    // 결론 결정: 표본별 결과를 기반으로 자동 계산
                    // 경감요소 없는 Exception이 하나라도 있으면 'exception' (Ineffective)
                    // 그 외에는 'effective' (Effective)
                    const finalConclusion = exceptionWithoutMitigationCount > 0 ? 'exception' : 'effective';

                    evaluationData = {
                        sample_size: sampleSize,
                        exception_count: exceptionCount,  // 표본별로 계산된 값
                        mitigating_factors: '',  // 더 이상 사용 안 함 (표본별로 관리)
                        exception_details: formData.get('exception_details'),
                        conclusion: finalConclusion,  // 표본별 결과 기반 자동 계산
                        improvement_plan: formData.get('improvement_plan'),
                        no_occurrence: false,
                        no_occurrence_reason: '',
                        use_design_evaluation: useDesignEvaluation,  // 설계평가 대체 여부
                        sample_lines: sampleLines  // 표본 라인 데이터 추가
                    };
                }

                // FormData 생성 (파일 포함)
                const uploadData = new FormData();
                uploadData.append('rcm_id', currentRcmId);
                uploadData.append('design_evaluation_session', currentEvaluationSession);
                uploadData.append('control_code', currentControlCode);
                uploadData.append('evaluation_data', JSON.stringify(evaluationData));

                // 엑셀 파일 추가 (수동통제인 경우, 요소 존재 확인)
                const sampleExcelFileEl = document.getElementById('sampleExcelFile');
                if (sampleExcelFileEl && sampleExcelFileEl.files && sampleExcelFileEl.files[0]) {
                    uploadData.append('sample_excel', sampleExcelFileEl.files[0]);
                }

                console.log('저장 요청 전송 시작');
                console.log('evaluationData:', evaluationData);
                console.log('Uploading to /api/operation-evaluation/save');

                // 서버에 저장 (세션 쿠키 포함)
                fetch('/api/operation-evaluation/save', {
                    method: 'POST',
                    body: uploadData,
                    credentials: 'same-origin'  // 세션 쿠키를 포함하여 전송
                })
                    .then(response => {
                        console.log('응답 상태:', response.status, response.statusText);
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('응답 데이터:', data);
                        if (data.success) {
                            // 성공 메시지 먼저 표시
                            showSuccessToast('운영평가 결과가 저장되었습니다.');

                            // 로컬 데이터 업데이트 (서버 응답의 line_id와 sample_lines 포함)
                            evaluated_controls[currentControlCode] = {
                                ...evaluationData,
                                line_id: data.line_id,  // 서버에서 반환된 line_id
                                sample_lines: evaluationData.sample_lines || []  // 저장한 sample_lines
                            };
                            console.log('[saveOperationEvaluation] evaluated_controls 업데이트:', evaluated_controls[currentControlCode]);

                            // UI 업데이트
                            updateEvaluationUI(currentRowIndex, evaluationData);
                            updateProgress();

                            // 다운로드 버튼 업데이트 (저장 후)
                            updateDownloadButton(currentControlCode, evaluationData);

                            // 모달은 약간 지연 후 닫기 (토스트가 보이도록)
                            setTimeout(() => {
                                const modalEl = document.getElementById('operationEvaluationModal');
                                if (modalEl) {
                                    const modalInstance = bootstrap.Modal.getInstance(modalEl);
                                    if (modalInstance) {
                                        modalInstance.hide();
                                    }
                                }
                            }, 500);
                        } else {
                            console.error('저장 실패:', data.message);
                            showErrorToast('저장 실패: ' + (data.message || '알 수 없는 오류'));
                        }
                    })
                    .catch(error => {
                        console.error('저장 요청 오류:', error);
                        showErrorToast('저장 중 네트워크 오류 발생: ' + error.message);
                    });
            } catch (error) {
                console.error('saveOperationEvaluation 데이터 처리 오류:', error);
                showErrorToast('데이터 처리 중 오류 발생: ' + error.message);
            }
        }

        // 개별 평가 UI 업데이트
        function updateEvaluationUI(rowIndex, data) {
            // 평가 결과 업데이트
            const resultElement = document.getElementById(`evaluation-result-${rowIndex}`);
            if (resultElement && data.conclusion) {
                const resultMap = {
                    'effective': { text: 'Effective', class: 'bg-success' },
                    'exception': { text: 'Exception', class: 'bg-danger' }
                };

                const result = resultMap[data.conclusion];
                if (result) {
                    // no_occurrence가 true인 경우 아이콘 추가
                    if (data.no_occurrence) {
                        resultElement.innerHTML = `${result.text} <i class="fas fa-info-circle ms-1" title="당기 발생사실 없음"></i>`;
                        resultElement.title = '당기 발생사실 없음';
                    } else {
                        resultElement.textContent = result.text;
                    }
                    resultElement.className = `badge ${result.class}`;
                }
            }

            // 개선계획 업데이트
            const improvementElement = document.getElementById(`improvement-plan-${rowIndex}`);
            if (improvementElement) {
                improvementElement.textContent = data.improvement_plan || '-';
            }
        }

        // 다운로드 버튼 업데이트
        function updateDownloadButton(controlCode, evaluationData) {
            console.log('[updateDownloadButton] controlCode:', controlCode);
            console.log('[updateDownloadButton] evaluationData:', evaluationData);

            const downloadBtn = document.getElementById('downloadOperationBtn');
            if (!downloadBtn) {
                console.log('[updateDownloadButton] downloadBtn not found');
                return;
            }

            // 평가가 완료되었는지 확인 (conclusion이 있으면 완료)
            if (evaluationData && evaluationData.conclusion) {
                // 다운로드 URL 설정
                const rcmId = {{ rcm_id }};
                const evaluationSession = {{ operation_evaluation_session | tojson }};
                const designEvaluationSession = {{ design_evaluation_session | tojson }};
                const downloadUrl = `/operation-evaluation/download?rcm_id=${rcmId}&evaluation_session=${encodeURIComponent(evaluationSession)}&design_evaluation_session=${encodeURIComponent(designEvaluationSession)}&control_code=${encodeURIComponent(controlCode)}`;

                console.log('[updateDownloadButton] Download URL:', downloadUrl);
                downloadBtn.href = downloadUrl;
                downloadBtn.style.display = 'inline-block';
            } else {
                // 평가 미완료 시 버튼 숨김
                console.log('[updateDownloadButton] Evaluation not completed, hiding button');
                downloadBtn.style.display = 'none';
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
            // 평가 완료된 통제 수 계산 (conclusion이 있는 경우만 완료로 간주)
            const evaluatedControls = Object.values(evaluated_controls).filter(control => {
                return control.conclusion && control.conclusion.trim() !== '';
            }).length;

            // 서버에서 계산한 total_controls 사용 (설계평가에서 효과적으로 평가된 핵심통제만 카운트)
            const totalControls = parseInt(document.getElementById('totalControlCount').textContent) || {{ rcm_details|length }};
            const progress = totalControls > 0 ? Math.round((evaluatedControls / totalControls) * 100) : 0;

            // 진행률 업데이트
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
            fetch(`/api/design-evaluation/get?rcm_id=${currentRcmId}&design_evaluation_session=${currentEvaluationSession}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderDesignEvaluationTable(data.evaluations);
                    } else {
                        document.getElementById('designEvaluationTableBody').innerHTML = `
                            <tr>
                                <td colspan="7" class="text-center text-danger py-4">
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
                            <td colspan="7" class="text-center text-danger py-4">
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
                        <td colspan="7" class="text-center text-muted py-4">
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

                const isKey = item.key_control === 'Y' ? '핵심통제' : '-';

                return `
                    <tr>
                        <td style="font-size: 0.85rem;"><code>${item.control_code || '-'}</code></td>
                        <td style="font-size: 0.85rem;">${item.control_name || '-'}</td>
                        <td>
                            <div style="max-height: 60px; overflow-y: auto; font-size: 0.85rem;">
                                ${item.control_description || '-'}
                            </div>
                        </td>
                        <td style="font-size: 0.85rem;">${item.control_frequency || '-'}</td>
                        <td style="font-size: 0.85rem;">${isKey}</td>
                        <td style="font-size: 0.85rem;">${item.control_nature || '-'}</td>
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
            document.getElementById('apd01Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('apd07Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('apd09Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('apd12Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('pc01Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('pc02Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('pc03Modal').addEventListener('hidden.bs.modal', function () {
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
            document.getElementById('co01Modal').addEventListener('hidden.bs.modal', function () {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // Generic 수동통제 전용 함수
        // ===================================================================

        function showGenericManualControlUI(buttonElement, forceControlCode) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달 제목 설정
            const modalTitle = document.getElementById('genericManualModalLabel');
            if (modalTitle) {
                modalTitle.innerHTML = `<i class="fas fa-edit me-2"></i>수동 통제 운영평가`;
            }

            const targetControlCode = forceControlCode || controlCode;
            // 모달로 Generic 수동통제 UI 표시
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정
            document.getElementById('genericManualIframe').src = `/operation-evaluation/manual/${targetControlCode}?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('genericManualModal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('genericManualModal').addEventListener('hidden.bs.modal', function () {
                reloadWithScrollPosition();
            }, { once: true });
        }

        // ===================================================================
        // 모집단 업로드 함수 (표본수 0인 경우)
        // ===================================================================

        let excelHeaders = [];
        let excelData = [];
        let uploadedLineId = null;
        let uploadedPopulationCount = 0;
        let uploadedSampleSize = 0;

        function handlePopulationFileSelected() {
            const file = document.getElementById('populationFile').files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

                if (jsonData.length > 0) {
                    excelHeaders = jsonData[0];
                    excelData = jsonData.slice(1);

                    // 필드 매핑 UI 표시
                    showFieldMapping(excelHeaders);
                } else {
                    alert('엑셀 파일에 데이터가 없습니다.');
                }
            };
            reader.readAsArrayBuffer(file);
        }

        function showFieldMapping(headers) {
            const container = document.getElementById('fieldMappingContainer');
            container.innerHTML = '';

            // 기본 필드 정의 (번호, 설명)
            const requiredFields = [
                { name: 'number', label: '번호' },
                { name: 'description', label: '설명' }
            ];

            let html = '<div class="table-responsive"><table class="table table-sm table-bordered">';
            html += '<thead><tr><th style="width: 30%;">필수 필드</th><th>엑셀 컬럼 선택</th></tr></thead><tbody>';

            requiredFields.forEach(field => {
                html += `<tr><td><strong>${field.label}</strong></td><td>`;
                html += `<select class="form-select form-select-sm" id="mapping_${field.name}">`;
                html += '<option value="">선택하세요</option>';
                headers.forEach((header, idx) => {
                    html += `<option value="${idx}">${header}</option>`;
                });
                html += '</select></td></tr>';
            });

            html += '</tbody></table></div>';
            container.innerHTML = html;

            // 필드 매핑 섹션 표시
            document.getElementById('populationFieldMapping').style.display = 'block';
        }

        function uploadPopulationFile() {
            const file = document.getElementById('populationFile').files[0];
            if (!file) {
                alert('파일을 선택하세요.');
                return;
            }

            // 기존 데이터가 있는지 확인
            const existingData = evaluated_controls[currentControlCode];
            if (existingData && existingData.sample_lines && existingData.sample_lines.length > 0) {
                if (!confirm('⚠️ 경고\n\n모집단을 업로드하면 기존에 작성한 모든 표본 데이터(증빙 포함)가 삭제됩니다.\n\n계속하시겠습니까?')) {
                    return;
                }
            }

            // 필드 매핑 확인
            const numberCol = document.getElementById('mapping_number').value;
            const descriptionCol = document.getElementById('mapping_description').value;

            if (!numberCol || !descriptionCol) {
                alert('필수 필드를 모두 매핑해주세요.');
                return;
            }

            // FormData 생성
            const formData = new FormData();
            formData.append('population_file', file);
            formData.append('control_code', currentControlCode);
            formData.append('rcm_id', currentRcmId);
            formData.append('design_evaluation_session', currentEvaluationSession);

            const fieldMapping = {
                number: parseInt(numberCol),
                description: parseInt(descriptionCol)
            };
            formData.append('field_mapping', JSON.stringify(fieldMapping));

            // 업로드 중 표시
            const uploadBtn = event.target;
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>업로드 중...';

            // API 호출
            fetch('/api/operation-evaluation/upload-population', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    console.log('Response status:', response.status);
                    console.log('Response headers:', response.headers);

                    // 응답이 JSON인지 확인
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        return response.text().then(text => {
                            console.error('Non-JSON response:', text.substring(0, 500));
                            throw new Error('서버가 JSON 응답을 반환하지 않았습니다. 로그인이 필요하거나 서버 오류가 발생했습니다.');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // 업로드 성공 - 모집단 업로드 섹션 숨기고 평가 필드 표시
                        console.log('[uploadPopulationFile] 업로드 성공:', data);
                        console.log('[uploadPopulationFile] sample_lines:', JSON.stringify(data.sample_lines, null, 2));

                        // evaluated_controls에 저장
                        if (!evaluated_controls[currentControlCode]) {
                            evaluated_controls[currentControlCode] = {};
                        }
                        evaluated_controls[currentControlCode].line_id = data.line_id;
                        evaluated_controls[currentControlCode].sample_lines = data.sample_lines || [];

                        console.log('[uploadPopulationFile] evaluated_controls 저장 완료:', evaluated_controls[currentControlCode]);

                        // 모집단 업로드 섹션 숨기기
                        const populationUploadSection = document.getElementById('population-upload-section');
                        if (populationUploadSection) {
                            populationUploadSection.style.display = 'none';
                        }

                        // 초기화 버튼 섹션 표시
                        const resetSection = document.getElementById('populationResetSection');
                        if (resetSection) {
                            resetSection.style.display = 'block';
                        }

                        // 평가 필드 섹션 표시
                        document.getElementById('evaluation-fields').style.display = 'block';

                        // 표본 크기 설정
                        const sampleSizeEl = document.getElementById('sample_size');
                        if (sampleSizeEl) {
                            sampleSizeEl.value = data.sample_size;
                        }

                        // 표본 테이블 생성
                        generateSampleLines();
                    } else {
                        alert('업로드 실패: ' + (data.error || '알 수 없는 오류'));
                    }
                })
                .catch(error => {
                    console.error('Upload error:', error);
                    alert('업로드 중 오류가 발생했습니다: ' + error.message);
                })
                .finally(() => {
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = '<i class="fas fa-upload me-1"></i>업로드 및 표본 추출';
                });
        }

        // 모집단 업로드 초기화 함수 (표본수 0인 통제만 해당)
        function resetPopulationUpload() {
            // RCM 권장 표본수 확인 (0인 경우만 초기화 가능)
            if (currentRecommendedSampleSize !== 0) {
                alert('모집단 업로드 초기화는 RCM에서 권장 표본수가 0으로 설정된 통제에만 적용됩니다.');
                return;
            }

            if (!confirm('모집단 업로드를 초기화하시겠습니까?\n\n업로드된 모집단 파일과 데이터베이스의 모집단/표본 데이터가 모두 삭제됩니다.')) {
                return;
            }

            // 백엔드 API 호출하여 파일 및 DB 데이터 삭제
            fetch(`/api/operation-evaluation/reset-population`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    control_code: currentControlCode,
                    line_id: evaluated_controls[currentControlCode]?.line_id
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 현재 통제의 데이터 초기화
                    if (evaluated_controls[currentControlCode]) {
                        delete evaluated_controls[currentControlCode].sample_lines;
                        delete evaluated_controls[currentControlCode].line_id;
                    }

                    // UI 초기화
                    const populationUploadSection = document.getElementById('population-upload-section');
                    const resetBtn = document.getElementById('resetPopulationBtn');
                    const evaluationFields = document.getElementById('evaluation-fields');
                    const populationFile = document.getElementById('populationFile');
                    const populationFieldMapping = document.getElementById('populationFieldMapping');

                    // 모집단 업로드 섹션 다시 표시
                    if (populationUploadSection) {
                        populationUploadSection.style.display = 'block';
                    }

                    // 초기화 버튼 숨김
                    if (resetBtn) {
                        resetBtn.style.display = 'none';
                    }

                    // 평가 필드 섹션 숨김
                    if (evaluationFields) {
                        evaluationFields.style.display = 'none';
                    }

                    // 파일 입력 초기화
                    if (populationFile) {
                        populationFile.value = '';
                    }

                    // 필드 매핑 섹션 숨김
                    if (populationFieldMapping) {
                        populationFieldMapping.style.display = 'none';
                    }

                    // 표본 테이블 초기화
                    const tbody = document.getElementById('sample-lines-tbody');
                    if (tbody) {
                        tbody.innerHTML = '';
                    }

                    alert('모집단 업로드가 초기화되었습니다.');
                } else {
                    alert('초기화 실패: ' + (data.message || '알 수 없는 오류'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('초기화 중 오류가 발생했습니다.');
            });
        }


        function generateSampleLinesWithAttributes(attributes, sampleSize) {
            console.log('[generateSampleLinesWithAttributes] attributes:', attributes);
            console.log('[generateSampleLinesWithAttributes] sampleSize:', sampleSize);

            // 샘플 데이터 가져오기
            const existingData = evaluated_controls[currentControlCode];
            const existingSampleLines = existingData?.sample_lines || [];
            console.log('[generateSampleLinesWithAttributes] existingSampleLines:', existingSampleLines);

            // 테이블 헤더 동적 생성
            const table = document.getElementById('sample-lines-table');
            const thead = table.querySelector('thead');
            const tbody = table.querySelector('tbody');

            // 헤더 재생성 (모집단/증빙 구분 표시)
            let headerHtml = '<tr><th width="8%">표본 #</th><th width="30%">증빙 내용</th>';
            const popAttrCount = window.currentPopulationAttributeCount || 0;
            attributes.forEach((attr, index) => {
                const isPopulation = index < popAttrCount;
                const badge = isPopulation
                    ? '<span class="badge bg-primary ms-1" style="font-size: 0.7em;">모집단</span>'
                    : '<span class="badge bg-success ms-1" style="font-size: 0.7em;">증빙</span>';
                headerHtml += `<th width="${Math.floor(50 / attributes.length)}%">${attr.name}${badge}</th>`;
            });
            headerHtml += '<th width="12%">결과</th></tr>';
            thead.innerHTML = headerHtml;

            // 테이블 바디 생성
            tbody.innerHTML = '';

            const samplesToDisplay = sampleSize || existingSampleLines.length;

            for (let i = 1; i <= samplesToDisplay; i++) {
                const sample = existingSampleLines.find(s => s.sample_number === i);

                const row = document.createElement('tr');

                // 표본 번호
                let rowHtml = `<td class="text-center align-middle">#${i}</td>`;

                // 증빙 내용
                const evidence = sample?.evidence || '';
                rowHtml += `
                    <td class="align-middle">
                        <textarea class="form-control form-control-sm"
                               id="sample-evidence-${i}"
                               placeholder="증빙 내용"
                               rows="2"
                               readonly>${evidence}</textarea>
                    </td>`;

                // Attribute 필드들
                attributes.forEach(attr => {
                    rowHtml += `
                        <td class="align-middle">
                            <input type="text" class="form-control form-control-sm"
                                   id="sample-${i}-${attr.attribute}"
                                   placeholder="${attr.name}">
                        </td>`;
                });

                // 결과
                rowHtml += `
                    <td class="align-middle">
                        <select class="form-select form-select-sm"
                                id="sample-result-${i}"
                                onchange="handleSampleResultChange(${i})">
                            <option value="no_exception" selected>No Exception</option>
                            <option value="exception">Exception</option>
                        </select>
                    </td>`;

                row.innerHTML = rowHtml;
                tbody.appendChild(row);
            }

            // 전역 변수에 attribute 정보 저장 (저장 시 사용)
            window.currentAttributes = attributes;

            console.log('[generateSampleLinesWithAttributes] 테이블 생성 완료');
        }
    </script>
</body>

</html>