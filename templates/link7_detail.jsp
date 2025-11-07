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
                        <!-- 당기 발생사실 없음 옵션 -->
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="no_occurrence" name="no_occurrence">
                                <label class="form-check-label" for="no_occurrence">
                                    <strong>당기 발생사실 없음</strong>
                                    <small class="text-muted d-block">해당 통제활동이 평가 기간 동안 발생하지 않은 경우 체크하세요</small>
                                </label>
                            </div>
                        </div>

                        <div id="evaluation-fields">
                            <!-- 표본 크기 입력 -->
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label for="sample_size" class="form-label fw-bold">표본 크기</label>
                                    <input type="number" class="form-control" id="sample_size" name="sample_size" min="1" max="100" placeholder="통제주기에 따라 자동 설정" onchange="generateSampleLines()" onkeyup="if(event.key === 'Enter') generateSampleLines()">
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
                                            <thead class="table-light">
                                                <tr>
                                                    <th width="10%">표본 #</th>
                                                    <th width="70%">증빙 내용</th>
                                                    <th width="15%">결과</th>
                                                    <th width="5%">결론</th>
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

                        <!-- 당기 발생사실 없음 사유 -->
                        <div class="mb-3" id="no-occurrence-reason-section" style="display: none;">
                            <label for="no_occurrence_reason" class="form-label fw-bold">
                                비고 (선택사항)
                            </label>
                            <textarea class="form-control" id="no_occurrence_reason" name="no_occurrence_reason" rows="3" placeholder="필요한 경우 추가 설명을 입력하세요&#10;예) 당기 중 신규 직원 채용이 없었음, 시스템 변경이 발생하지 않았음 등"></textarea>
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
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal" style="min-width: auto; padding: 0.375rem 0.75rem;">취소</button>
                    <button type="button" id="saveOperationEvaluationBtn" class="btn btn-warning" onclick="saveOperationEvaluation();">
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

    <!-- Generic 수동통제 모달 -->
    <div class="modal fade" id="genericManualModal" tabindex="-1" aria-labelledby="genericManualModalLabel" aria-hidden="true">
        <div class="modal-dialog" style="max-width: 90%; height: 90vh; margin: 5vh auto;">
            <div class="modal-content" style="height: 100%;">
                <div class="modal-header">
                    <h5 class="modal-title" id="genericManualModalLabel">수동통제 운영평가</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body p-0" style="height: calc(100% - 60px); overflow: hidden;">
                    <iframe id="genericManualIframe" style="width: 100%; height: 100%; border: none;"></iframe>
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
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal" style="min-width: auto; padding: 0.375rem 0.75rem;">
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

            console.log('Not APD01/APD07/APD09/APD12/PC01/PC02/PC03/CO01, using standard modal...');

            // 수동통제 판별: 표준통제 코드가 없는 수동통제만 Generic UI 사용
            // ELC 일반 수동통제는 기본 모달 사용 (통제 주기 기반 표본 수 자동 설정)
            // if (controlNatureCode && (controlNatureCode.toUpperCase() === 'M' || controlNatureCode === '수동' || controlNatureCode.toUpperCase() === 'MANUAL')) {
            //     console.log('Manual control detected! Redirecting to Generic evaluation page...');
            //     showGenericManualControlUI(buttonElement);
            //     return;
            // }

            console.log('Showing standard evaluation modal with auto sample size...');

            // 일반 운영평가 UI (수동통제가 아닌 경우 - 거의 사용되지 않음)
            const excelSection = document.getElementById('excelUploadSection');
            if (excelSection) {
                excelSection.style.display = 'none';
            }

            // 파일 입력 초기화 (요소 존재 확인)
            const evaluationImages = document.getElementById('evaluationImages');
            const sampleExcelFile = document.getElementById('sampleExcelFile');
            const imagePreview = document.getElementById('imagePreview');
            const excelPreview = document.getElementById('excelPreview');

            if (evaluationImages) evaluationImages.value = '';
            if (sampleExcelFile) sampleExcelFile.value = '';
            if (imagePreview) imagePreview.innerHTML = '';
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

            // 권장 표본수 계산 및 저장 (표본수 검증을 위해)
            currentControlFrequency = controlFrequency;
            recommendedSampleSize = getDefaultSampleSize(controlFrequency, controlType);

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
            }

            // 기존 평가 데이터가 없거나 표본수가 비어있는 경우 자동 설정
            if (!evaluated_controls[controlCode] || (!evaluated_controls[controlCode].sample_size && !evaluated_controls[controlCode].no_occurrence)) {
                const defaultSampleSize = getDefaultSampleSize(controlFrequency, controlType);
                if (sampleSizeEl) sampleSizeEl.value = defaultSampleSize;
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
            if (evaluated_controls[controlCode] && evaluated_controls[controlCode].line_id) {
                const lineId = evaluated_controls[controlCode].line_id;
                console.log('[openOperationEvaluationModal] 샘플 데이터 조회 시작 - line_id:', lineId, '(매번 새로 조회)');

                // 먼저 기존 샘플 데이터 제거
                evaluated_controls[controlCode].sample_lines = [];

                // API 호출하여 샘플 데이터 조회 (평가 버튼 클릭할 때마다 실행)
                fetch(`/api/operation-evaluation/samples/${lineId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // 샘플이 0개여도 빈 배열로 업데이트 (기존 데이터 제거)
                            evaluated_controls[controlCode].sample_lines = data.samples || [];

                            if (data.samples && data.samples.length > 0) {
                                console.log('[openOperationEvaluationModal] 샘플 데이터 조회 성공:', data.samples);
                                // 샘플 라인 자동 생성
                                setTimeout(() => {
                                    generateSampleLines();
                                }, 100);
                            } else {
                                console.log('[openOperationEvaluationModal] 샘플 데이터 없음 (0개) - 테이블 비우기');
                                // 샘플이 없으면 기존 테이블 완전히 비우기
                                const tbody = document.getElementById('sample-lines-tbody');
                                if (tbody) {
                                    tbody.innerHTML = '';
                                }
                                const container = document.getElementById('sample-lines-container');
                                if (container) {
                                    container.style.display = 'none';
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
                // line_id가 없어도 표본 크기가 설정되어 있으면 테이블 생성
                const sampleSizeEl = document.getElementById('sample_size');
                if (sampleSizeEl && sampleSizeEl.value && parseInt(sampleSizeEl.value) > 0) {
                    console.log('[openOperationEvaluationModal] line_id 없지만 표본 크기 있음, 테이블 생성');
                    setTimeout(() => {
                        generateSampleLines();
                    }, 100);
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

            // 모달 표시
            const operationEvaluationModalEl = document.getElementById('operationEvaluationModal');
            if (operationEvaluationModalEl) {
                const modal = new bootstrap.Modal(operationEvaluationModalEl);
                modal.show();
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
            const sampleSize = parseInt(sampleSizeInput?.value) || 0;

            // 유효한 표본 크기인 경우에만 자동 생성
            if (sampleSize >= 1 && sampleSize <= 100) {
                generateSampleLines();
            }
        }

        // 표본 라인 생성
        function generateSampleLines() {
            const sampleSizeInput = document.getElementById('sample_size');
            const sampleSize = parseInt(sampleSizeInput.value) || 0;

            if (sampleSize < 1 || sampleSize > 100) {
                alert('표본 크기는 1에서 100 사이여야 합니다.');
                return;
            }

            const tbody = document.getElementById('sample-lines-tbody');
            tbody.innerHTML = ''; // 기존 라인 초기화

            // 기존 샘플 데이터 가져오기
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

            // SQL 쿼리 시뮬레이션 출력
            if (existingData && existingData.line_id) {
                console.log(`[SQL Query 시뮬레이션]
                    SELECT sample_id, sample_number, evidence, has_exception, mitigation
                    FROM sb_operation_evaluation_sample
                    WHERE line_id = ${existingData.line_id}
                    ORDER BY sample_number
                `);
            }
            console.log('===========================================');

            // 표본 크기만큼 라인 생성
            for (let i = 1; i <= sampleSize; i++) {
                // 기존 데이터에서 해당 표본 번호의 데이터 찾기
                const existingSample = existingSampleLines.find(s => s.sample_number === i);

                const evidence = existingSample?.evidence || '';
                const result = existingSample?.result || 'no_exception';
                const mitigation = existingSample?.mitigation || '';

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="text-center align-middle">#${i}</td>
                    <td class="align-middle">
                        <input type="text" class="form-control form-control-sm"
                               id="sample-evidence-${i}"
                               placeholder="예: 증빙서류 확인"
                               value="${evidence}"
                               style="height: 31px;" />
                    </td>
                    <td class="align-middle">
                        <select class="form-select form-select-sm"
                                id="sample-result-${i}"
                                onchange="handleSampleResultChange(${i})"
                                style="height: 31px;">
                            <option value="no_exception" ${result === 'no_exception' ? 'selected' : ''}>No Exception</option>
                            <option value="exception" ${result === 'exception' ? 'selected' : ''}>Exception</option>
                        </select>
                    </td>
                    <td class="text-center align-middle">
                        <span id="sample-conclusion-${i}" class="badge ${result === 'exception' ? 'bg-danger' : 'bg-success'}">
                            ${result === 'exception' ? 'Exception' : 'OK'}
                        </span>
                    </td>
                `;
                tbody.appendChild(row);

                // Exception 선택 시 경감요소 입력란을 행 아래에 추가
                if (result === 'exception') {
                    const mitigationRow = document.createElement('tr');
                    mitigationRow.id = `mitigation-row-${i}`;
                    mitigationRow.innerHTML = `
                        <td colspan="4" class="bg-light">
                            <div class="p-2">
                                <label class="form-label fw-bold mb-1" style="font-size: 0.875rem;">경감요소:</label>
                                <input type="text" class="form-control form-control-sm"
                                       id="sample-mitigation-${i}"
                                       placeholder="경감요소를 입력하세요"
                                       value="${mitigation}"
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
            const conclusionBadge = document.getElementById(`sample-conclusion-${sampleNumber}`);
            const existingMitigationRow = document.getElementById(`mitigation-row-${sampleNumber}`);

            if (resultSelect.value === 'exception') {
                // Exception 선택 시 경감요소 행 추가
                conclusionBadge.textContent = 'Exception';
                conclusionBadge.className = 'badge bg-danger';

                // 경감요소 행이 없으면 추가
                if (!existingMitigationRow) {
                    const tbody = document.getElementById('sample-lines-tbody');
                    const currentRow = resultSelect.closest('tr');
                    const mitigationRow = document.createElement('tr');
                    mitigationRow.id = `mitigation-row-${sampleNumber}`;
                    mitigationRow.innerHTML = `
                        <td colspan="4" class="bg-light">
                            <div class="p-2">
                                <label class="form-label fw-bold mb-1" style="font-size: 0.875rem;">경감요소:</label>
                                <input type="text" class="form-control form-control-sm"
                                       id="sample-mitigation-${sampleNumber}"
                                       placeholder="경감요소를 입력하세요"
                                       value=""
                                       style="height: 31px;" />
                            </div>
                        </td>
                    `;
                    currentRow.insertAdjacentElement('afterend', mitigationRow);
                }
            } else {
                // No Exception 선택 시 경감요소 행 제거
                conclusionBadge.textContent = 'OK';
                conclusionBadge.className = 'badge bg-success';

                if (existingMitigationRow) {
                    existingMitigationRow.remove();
                }
            }

            // 전체 결론 업데이트
            updateOverallConclusion();
        }

        // 개별 표본 결론 업데이트
        function updateSampleConclusion(sampleNumber) {
            const resultSelect = document.getElementById(`sample-result-${sampleNumber}`);
            const mitigationTextarea = document.getElementById(`sample-mitigation-${sampleNumber}`);
            const conclusionBadge = document.getElementById(`sample-conclusion-${sampleNumber}`);

            if (resultSelect.value === 'exception') {
                const hasMitigation = mitigationTextarea.value.trim().length > 0;
                if (hasMitigation) {
                    // 경감요소가 있으면 조건부 OK
                    conclusionBadge.textContent = 'OK*';
                    conclusionBadge.className = 'badge bg-warning';
                } else {
                    // 경감요소 없으면 Exception
                    conclusionBadge.textContent = 'EX';
                    conclusionBadge.className = 'badge bg-danger';
                }
            }

            // 전체 결론 업데이트
            updateOverallConclusion();
        }

        // 전체 결론 자동 계산
        function updateOverallConclusion() {
            const tbody = document.getElementById('sample-lines-tbody');
            const rows = tbody.querySelectorAll('tr');

            if (rows.length === 0) {
                return;
            }

            let noExceptionCount = 0;
            let exceptionWithMitigationCount = 0;
            let exceptionWithoutMitigationCount = 0;

            rows.forEach((row, index) => {
                const sampleNumber = index + 1;
                const resultSelect = document.getElementById(`sample-result-${sampleNumber}`);
                const mitigationTextarea = document.getElementById(`sample-mitigation-${sampleNumber}`);

                if (resultSelect.value === 'no_exception') {
                    noExceptionCount++;
                } else if (resultSelect.value === 'exception') {
                    const hasMitigation = mitigationTextarea.value.trim().length > 0;
                    if (hasMitigation) {
                        exceptionWithMitigationCount++;
                    } else {
                        exceptionWithoutMitigationCount++;
                    }
                }
            });

            const conclusionSpan = document.getElementById('overall-conclusion');
            const summaryDiv = document.getElementById('conclusion-summary');

            // 경감요소 없는 Exception이 하나라도 있으면 전체 Exception
            if (exceptionWithoutMitigationCount > 0) {
                conclusionSpan.textContent = 'Exception';
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

        // ===================================================================
        // 기존 함수들
        // ===================================================================

        // 전역 변수로 권장 표본수와 통제주기 저장
        let recommendedSampleSize = 0;
        let currentControlFrequency = '';

        document.addEventListener('DOMContentLoaded', function() {
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
            const inputValue = parseInt(sampleSizeInput.value) || 0;

            console.log('validateSampleSize 호출됨');
            console.log('입력값:', inputValue);
            console.log('권장 표본수:', recommendedSampleSize);
            console.log('통제주기:', currentControlFrequency);

            // 예외 발견 수의 최대값을 새로운 표본 크기로 업데이트
            if (exceptionCountInput && inputValue > 0) {
                exceptionCountInput.setAttribute('max', inputValue);
                // 현재 예외 발견 수가 새로운 표본 크기를 초과하면 자동 조정
                validateExceptionCount();
            }

            // 통제주기 기반 권장 표본수와 비교
            if (recommendedSampleSize > 0 && inputValue !== recommendedSampleSize) {
                const frequencyName = getFrequencyName(currentControlFrequency);
                alert(`ℹ️ 안내\n\n통제주기: ${frequencyName}\n권장 표본수: ${recommendedSampleSize}개\n입력한 표본수: ${inputValue}개\n\n필요에 따라 조정하셨다면 그대로 진행하시면 됩니다.`);
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
            const evaluationFields = document.getElementById('evaluation-fields');
            const noOccurrenceReasonSection = document.getElementById('no-occurrence-reason-section');

            if (noOccurrenceCheckbox.checked) {
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
                'evaluationImages',
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
                        no_occurrence_reason: noOccurrenceReason.trim()
                    };
                } else {
                    // 일반 평가인 경우
                    const exceptionCount = parseInt(formData.get('exception_count')) || 0;
                    const mitigatingFactors = formData.get('mitigating_factors') || '';
                    const userConclusion = formData.get('conclusion');

                    // 결론 결정: 경감요소가 있으면 사용자 선택, 없으면 자동
                    let finalConclusion;
                    if (exceptionCount > 0 && mitigatingFactors.trim().length > 0) {
                        // 경감요소가 있는 경우 사용자가 선택한 결론 사용
                        finalConclusion = userConclusion;
                    } else {
                        // 자동 결정
                        finalConclusion = exceptionCount > 0 ? 'exception' : 'effective';
                    }

                    // 표본 라인별 데이터 수집
                    const sampleSize = parseInt(formData.get('sample_size')) || 0;
                    const sampleLines = [];

                    for (let i = 1; i <= sampleSize; i++) {
                        const evidenceEl = document.getElementById(`sample-evidence-${i}`);
                        const resultEl = document.getElementById(`sample-result-${i}`);
                        const mitigationEl = document.getElementById(`sample-mitigation-${i}`);

                        if (evidenceEl && resultEl) {
                            sampleLines.push({
                                sample_number: i,
                                evidence: evidenceEl.value || '',
                                result: resultEl.value || 'no_exception',
                                mitigation: mitigationEl ? mitigationEl.value || '' : ''
                            });
                        }
                    }

                    evaluationData = {
                        sample_size: sampleSize,
                        exception_count: exceptionCount,
                        mitigating_factors: mitigatingFactors,
                        exception_details: formData.get('exception_details'),
                        conclusion: finalConclusion,
                        improvement_plan: formData.get('improvement_plan'),
                        no_occurrence: false,
                        no_occurrence_reason: '',
                        sample_lines: sampleLines  // 표본 라인 데이터 추가
                    };
                }

                // FormData 생성 (파일 포함)
                const uploadData = new FormData();
                uploadData.append('rcm_id', currentRcmId);
                uploadData.append('design_evaluation_session', currentEvaluationSession);
                uploadData.append('control_code', currentControlCode);
                uploadData.append('evaluation_data', JSON.stringify(evaluationData));

                // 이미지 파일 추가 (요소 존재 확인)
                const evaluationImagesEl = document.getElementById('evaluationImages');
                if (evaluationImagesEl && evaluationImagesEl.files) {
                    const imageFiles = evaluationImagesEl.files;
                    for (let i = 0; i < imageFiles.length; i++) {
                        uploadData.append('evaluation_image_' + i, imageFiles[i]);
                    }
                }

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

                        // 로컬 데이터 업데이트
                        evaluated_controls[currentControlCode] = evaluationData;

                        // UI 업데이트
                        updateEvaluationUI(currentRowIndex, evaluationData);
                        updateProgress();

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

        // ===================================================================
        // Generic 수동통제 전용 함수
        // ===================================================================

        function showGenericManualControlUI(buttonElement) {
            const controlCode = buttonElement.getAttribute('data-control-code');
            const controlName = buttonElement.getAttribute('data-control-name');

            // 모달로 Generic 수동통제 UI 표시
            const params = new URLSearchParams({
                rcm_id: currentRcmId,
                control_code: controlCode,
                control_name: controlName,
                design_evaluation_session: currentEvaluationSession
            });

            // iframe에 URL 설정 (Generic 경로 - 통제코드를 GENERIC으로 설정)
            document.getElementById('genericManualIframe').src = `/operation-evaluation/manual/GENERIC?${params.toString()}`;

            // 모달 열기
            const modal = new bootstrap.Modal(document.getElementById('genericManualModal'));
            modal.show();

            // 모달이 닫힐 때 페이지 새로고침 (스크롤 위치 유지)
            document.getElementById('genericManualModal').addEventListener('hidden.bs.modal', function() {
                reloadWithScrollPosition();
            }, { once: true });
        }
    </script>
</body>
</html>