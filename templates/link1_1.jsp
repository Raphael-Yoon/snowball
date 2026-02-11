<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Snowball - AI RCM Builder</title>
		<!-- Favicon -->
		<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
		<link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
		<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
		<style>
			.rcm-table-container {
				margin-top: 2rem;
				background: white;
				padding: 1.5rem;
				border-radius: 12px;
				box-shadow: 0 4px 15px rgba(0,0,0,0.1);
			}
			.control-row {
				border-bottom: 1px solid #eee;
				transition: background 0.2s;
			}
			.control-row:hover {
				background-color: #f8f9fa;
			}
			.mode-badge {
				font-size: 0.75rem;
				padding: 0.25rem 0.5rem;
				border-radius: 4px;
				cursor: pointer;
			}
			.mode-auto { background: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }
			.mode-manual { background: #fff3e0; color: #ef6c00; border: 1px solid #ffe0b2; }
			.editable-content {
				width: 100%;
				min-height: 80px;
				border: 1px solid #ddd;
				border-radius: 4px;
				padding: 0.5rem;
				font-size: 0.9rem;
				resize: vertical;
			}
			.readonly-content {
				font-size: 0.9rem;
				color: #444;
				white-space: pre-wrap;
			}
			.sticky-bottom-bar {
				position: fixed;
				bottom: 0;
				left: 0;
				right: 0;
				background: rgba(255,255,255,0.9);
				backdrop-filter: blur(10px);
				padding: 1rem 2rem;
				box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
				z-index: 1000;
				display: flex;
				justify-content: flex-end;
				gap: 1rem;
			}
			.ai-loading-overlay {
				position: fixed;
				top: 0;
				left: 0;
				width: 100%;
				height: 100%;
				background: rgba(255,255,255,0.7);
				display: none;
				justify-content: center;
				align-items: center;
				z-index: 2000;
				flex-direction: column;
			}
			.spinner {
				width: 50px;
				height: 50px;
				border: 5px solid #f3f3f3;
				border-top: 5px solid #3498db;
				border-radius: 50%;
				animation: spin 1s linear infinite;
				margin-bottom: 1rem;
			}
			@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
			
			/* 클라우드 환경에 따른 제외 통제 스타일 */
			.excluded-control {
				background-color: #f8f9fa !important;
				color: #adb5bd !important;
			}
			.excluded-control .fw-bold { color: #adb5bd !important; }
			.excluded-control select { 
				background-color: #e9ecef !important; 
				color: #adb5bd !important;
				border-color: #dee2e6 !important;
			}
			.cloud-badge {
				font-size: 0.65rem;
				padding: 0.15rem 0.5rem;
				background: #f0f4ff;
				color: #3f51b5;
				border: 1px solid #d1d9ff;
				border-radius: 12px;
				margin-left: 8px;
				display: inline-flex;
				align-items: center;
				white-space: nowrap;
				font-weight: 600;
				letter-spacing: -0.02em;
			}
		</style>
	</head>
	<body class="bg-light" style="padding-bottom: 80px;">
		{% include 'navi.jsp' %}
		
		<div class="container py-5">
			<div class="row justify-content-center">
				<div class="col-lg-10">
					<h2 class="mb-4 text-primary"><i class="fas fa-robot me-2"></i>AI ITGC RCM Auto-Generator</h2>
					
					<!-- 1. Input Section -->
					<div class="card border-0 shadow-sm mb-4">
						<div class="card-header bg-white py-3">
							<h5 class="mb-0"><i class="fas fa-server me-2"></i>시스템 환경 설정</h5>
						</div>
						<div class="card-body">
							<form id="system-form">
								<div class="row">
									<div class="col-md-6 mb-3">
										<label class="form-label fw-bold">시스템 명칭</label>
										<input type="text" class="form-control" id="system_name" name="system_name" required placeholder="예: SAP ERP, 사내 인사시스템">
									</div>
									<div class="col-md-6 mb-3">
										<label class="form-label fw-bold">시스템 유형</label>
										<select class="form-select" id="system_type" name="system_type" required onchange="handleSystemTypeChange()">
											<option value="In-house">In-house (자체개발)</option>
											<option value="Package-Modifiable">Package - Modifiable (SAP, Oracle ERP 등)</option>
											<option value="Package-Non-modifiable">Package - Non-modifiable (더존, 영림원 등)</option>
										</select>
									</div>
								</div>
								
								<div class="row">
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">Cloud 환경</label>
										<select class="form-select" id="cloud_env" name="cloud_env" onchange="handleCloudEnvChange()">
											<option value="None">미사용 (On-Premise)</option>
											<option value="IaaS">IaaS (EC2, GCE 등)</option>
											<option value="PaaS">PaaS (RDS, Managed DB 등)</option>
											<option value="SaaS">SaaS (Salesforce, ERP 등)</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">주요 SW</label>
										<select class="form-select" id="software" name="software" onchange="handleSoftwareChange()">
											<option value="SAP">SAP ERP</option>
											<option value="ORACLE">Oracle ERP</option>
											<option value="DOUZONE">더존 ERP</option>
											<option value="YOUNG">영림원 ERP</option>
											<option value="ETC">기타 / 자체개발</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">SW 버전</label>
										<select class="form-select" id="sw_version" name="sw_version">
											<!-- SAP versions (default) -->
											<option value="ECC">ECC 6.0</option>
											<option value="S4HANA">S/4HANA</option>
											<option value="S4CLOUD">S/4HANA Cloud</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">OS</label>
										<select class="form-select" id="os" name="os" onchange="handleOsChange()">
											<option value="RHEL">Linux (RHEL/CentOS)</option>
											<option value="UBUNTU">Linux (Ubuntu/Debian)</option>
											<option value="WINDOWS">Windows Server</option>
											<option value="UNIX">Unix (AIX/HP-UX)</option>
											<option value="N/A">N/A (SaaS/PaaS)</option>
										</select>
									</div>
								</div>
								<div class="row">
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">OS 버전</label>
										<select class="form-select" id="os_version" name="os_version">
											<!-- RHEL versions (default) -->
											<option value="RHEL8">RHEL 8.x / CentOS 8</option>
											<option value="RHEL7">RHEL 7.x / CentOS 7</option>
											<option value="RHEL9">RHEL 9.x / Rocky 9</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">DB</label>
										<select class="form-select" id="db" name="db" onchange="handleDbChange()">
											<option value="ORACLE">Oracle DB</option>
											<option value="TIBERO">Tibero (Tmax)</option>
											<option value="MSSQL">MS-SQL</option>
											<option value="MYSQL">MySQL/MariaDB</option>
											<option value="POSTGRES">PostgreSQL</option>
											<option value="HANA">SAP HANA</option>
											<option value="N/A">N/A (SaaS)</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">DB 버전</label>
										<select class="form-select" id="db_version" name="db_version">
											<!-- Oracle versions (default) -->
											<option value="19C">Oracle 19c</option>
											<option value="12C">Oracle 12c</option>
											<option value="11G">Oracle 11g</option>
											<option value="21C">Oracle 21c</option>
										</select>
									</div>
									<div class="col-md-3 mb-3 d-flex align-items-end">
										<button type="button" class="btn btn-outline-secondary w-100" onclick="resetVersions()">
											<i class="fas fa-undo me-1"></i>기본값 복원
										</button>
									</div>
								</div>
								
								<div class="text-end mt-2">
									<button type="button" class="btn btn-primary btn-lg" id="btn-generate-ai">
										<i class="fas fa-magic me-2"></i>AI 통제 분석 시작
									</button>
								</div>
							</form>
						</div>
					</div>
					
					<!-- 2. RCM Table Section -->
					<div class="rcm-table-container">
						<div class="d-flex justify-content-between align-items-center mb-3">
							<h5 class="mb-0 fw-bold">ITGC Risk Control Matrix ({{ master_controls|length }}개 통제항목)</h5>
							<div>
								<span class="badge bg-info me-2">총 {{ master_controls|length }}개</span>
								<button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target=".detail-row">
									<i class="fas fa-eye me-1"></i>상세 펼치기/접기
								</button>
							</div>
						</div>

						<div class="table-responsive">
							<table class="table table-hover align-middle" id="rcm-table">
								<thead class="table-primary text-center">
									<tr>
										<th style="width: 70px;">ID</th>
										<th style="width: auto;" class="text-start ps-4">통제 항목</th>
										<th style="width: 110px;">구분</th>
										<th style="width: 110px;">주기</th>
										<th style="width: 110px;">성격</th>
									</tr>
								</thead>
								<tbody id="rcm-tbody">
									{% for control in master_controls %}
									<tr class="control-row" data-id="{{ control.id }}">
										<td class="fw-bold text-center text-primary" style="font-size: 0.9rem;">{{ control.id }}</td>
										<td class="ps-4">
											<div class="d-flex align-items-center mb-1">
												<span class="fw-bold me-2">{{ control.name }}</span>
												<span class="badge bg-secondary-subtle text-secondary" style="font-size: 0.7rem; font-weight: 500;">{{ control.category }}</span>
											</div>
											<div class="text-muted" style="font-size: 0.8rem; line-height: 1.2;">{{ control.objective }}</div>
										</td>
										<td class="px-2">
											<select class="form-select form-select-sm border-light-subtle" id="type-{{ control.id }}" onchange="handleTypeChange('{{ control.id }}')">
												<option value="Auto" {{ 'selected' if control.type == 'Auto' else '' }}>자동</option>
												<option value="Manual" {{ 'selected' if control.type == 'Manual' else '' }}>수동</option>
											</select>
										</td>
										<td class="px-2">
											<select class="form-select form-select-sm border-light-subtle" id="freq-{{ control.id }}"
												onchange="updatePopulationByFrequency('{{ control.id }}')"
												{{ 'disabled' if control.type == 'Auto' else '' }}>
												<option value="연" {{ 'selected' if control.frequency == '연' else '' }}>연</option>
												<option value="분기" {{ 'selected' if control.frequency == '분기' else '' }}>분기</option>
												<option value="월" {{ 'selected' if control.frequency == '월' else '' }}>월</option>
												<option value="주" {{ 'selected' if control.frequency == '주' else '' }}>주</option>
												<option value="일" {{ 'selected' if control.frequency == '일' else '' }}>일</option>
												<option value="수시" {{ 'selected' if control.frequency == '수시' else '' }}>수시</option>
												<option value="기타" {{ 'selected' if control.frequency == '기타' else '' }}>기타</option>
											</select>
										</td>
										<td class="px-2">
											<div class="d-flex align-items-center">
												<select class="form-select form-select-sm border-light-subtle" id="method-{{ control.id }}" {{ 'disabled' if control.type == 'Auto' else '' }}>
													<option value="예방" {{ 'selected' if control.method == '예방' else '' }}>예방</option>
													<option value="적발" {{ 'selected' if control.method == '적발' else '' }}>적발</option>
												</select>
												<!-- Hidden fields for logic -->
												<input type="hidden" id="population-{{ control.id }}">
												<input type="hidden" id="sample-{{ control.id }}">
											</div>
										</td>
									</tr>
									<!-- 상세 정보 행 (접기/펼치기) -->
									<tr class="detail-row collapse" id="detail-{{ control.id }}">
										<td colspan="5" class="bg-light p-3">
											<div class="row">
												<div class="col-md-5">
													<div class="mb-2">
														<span class="badge bg-danger me-1">{{ control.risk_code }}</span>
														<strong>Risk 설명</strong>
													</div>
													<p class="small text-muted mb-0">{{ control.risk_description }}</p>
												</div>
												<div class="col-md-7 border-start">
													<div class="mb-3">
														<div class="d-flex justify-content-between align-items-center mb-2">
															<strong><i class="fas fa-shield-alt me-1"></i>통제 활동</strong>
															<button class="btn btn-sm btn-link text-decoration-none p-0" onclick="copyToClipboard('activity-detail-{{ control.id }}')">
																<i class="far fa-copy me-1"></i>복사
															</button>
														</div>
														<p class="small mb-0 text-dark" id="activity-detail-{{ control.id }}" style="white-space: pre-wrap;">{{ control.control_description }}</p>
													</div>

													<!-- 모집단 / 모집단 완전성 / 표본수 -->
													<div class="pt-3 border-top mb-3">
														<div class="mb-2"><strong><i class="fas fa-database me-1"></i>모집단 정보</strong></div>
														<div class="row small mb-2">
															<div class="col-md-6">
																<span class="text-muted">모집단:</span>
																<span class="fw-bold ms-1" id="population-name-{{ control.id }}">-</span>
															</div>
															<div class="col-md-2">
																<span class="text-muted">수량:</span>
																<span class="fw-bold ms-1" id="population-count-{{ control.id }}">-</span>
															</div>
															<div class="col-md-2">
																<span class="text-muted">표본수:</span>
																<span class="fw-bold ms-1 text-primary" id="sample-count-{{ control.id }}">-</span>
															</div>
															<div class="col-md-2">
																<span class="text-muted">완전성:</span>
																<span class="fw-bold ms-1 text-success" id="completeness-{{ control.id }}">-</span>
															</div>
														</div>
														<!-- 완전성 상세 (테이블명, 쿼리, 메뉴경로 등) -->
														<div class="small text-muted bg-light p-2 border rounded" id="completeness-detail-{{ control.id }}"
															style="white-space: pre-wrap; display: none;"></div>
													</div>

													<div class="pt-3 border-top">
														<div class="d-flex justify-content-between align-items-center mb-2">
															<strong><i class="fas fa-clipboard-check me-1"></i>테스트 절차</strong>
															<button class="btn btn-sm btn-link text-decoration-none p-0" onclick="copyToClipboard('test-proc-detail-{{ control.id }}')">
																<i class="far fa-copy me-1"></i>복사
															</button>
														</div>
														<div class="small text-muted bg-white p-2 border rounded" id="test-proc-detail-{{ control.id }}"
															style="white-space: pre-wrap;"
															data-auto="{{ control.test_procedure_auto }}"
															data-manual="{{ control.test_procedure_manual }}">{{ control.test_procedure_auto if control.type == 'Auto' else control.test_procedure_manual }}</div>
													</div>
												</div>
											</div>
										</td>
									</tr>
									{% endfor %}
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</div>
		</div>
		
		<!-- Sticky Bottom Bar -->
		<div class="sticky-bottom-bar">
			<button class="btn btn-outline-secondary" onclick="window.location.reload()">
				<i class="fas fa-undo me-1"></i>초기화
			</button>
			<button class="btn btn-success px-4" id="btn-export-excel">
				<i class="fas fa-file-excel me-1"></i>최종 RCM 엑셀 다운로드
			</button>
		</div>
		
		<!-- Loading Overlay -->
		<div class="ai-loading-overlay" id="loading-overlay">
			<div class="spinner"></div>
			<h5 class="fw-bold">AI가 시스템 환경을 분석 중입니다...</h5>
			<p class="text-muted">기술적 증적(Technical Objects) 매핑 중 (약 10~20초 소요)</p>
		</div>

		<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
		<script>
			// 클립보드 복사 함수
			function copyToClipboard(elementId) {
				const element = document.getElementById(elementId);
				const text = element.innerText;
				
				navigator.clipboard.writeText(text).then(() => {
					// 성공 시 피드백 (간단한 alert 또는 토스트)
					const toastContainer = document.createElement('div');
					toastContainer.style.position = 'fixed';
					toastContainer.style.bottom = '100px';
					toastContainer.style.left = '50%';
					toastContainer.style.transform = 'translateX(-50%)';
					toastContainer.style.background = 'rgba(0,0,0,0.7)';
					toastContainer.style.color = 'white';
					toastContainer.style.padding = '0.5rem 1rem';
					toastContainer.style.borderRadius = '20px';
					toastContainer.style.zIndex = '3000';
					toastContainer.innerText = '클립보드에 복사되었습니다.';
					
					document.body.appendChild(toastContainer);
					setTimeout(() => toastContainer.remove(), 2000);
				}).catch(err => {
					console.error('Failed to copy: ', err);
				});
			}

			// CSRF 토큰 설정
			const csrfToken = "{{ csrf_token() }}";
			
			// 시스템 유형 변경 시 핸들러
			function handleSystemTypeChange() {
				const systemType = document.getElementById('system_type').value;
				const softwareSelect = document.getElementById('software');
				const etcOption = softwareSelect.querySelector('option[value="ETC"]');
				const sapOption = softwareSelect.querySelector('option[value="SAP"]');
				const oracleOption = softwareSelect.querySelector('option[value="ORACLE"]');
				const douzoneOption = softwareSelect.querySelector('option[value="DOUZONE"]');
				const youngOption = softwareSelect.querySelector('option[value="YOUNG"]');

				if (systemType === 'In-house') {
					// 자체개발: ETC만 표시
					softwareSelect.value = 'ETC';
					softwareSelect.disabled = true;
					if (etcOption) etcOption.style.display = '';
					if (sapOption) sapOption.style.display = 'none';
					if (oracleOption) oracleOption.style.display = 'none';
					if (douzoneOption) douzoneOption.style.display = 'none';
					if (youngOption) youngOption.style.display = 'none';
				} else if (systemType === 'Package-Modifiable') {
					// Package Modifiable: SAP, Oracle만 표시
					softwareSelect.disabled = false;
					if (etcOption) etcOption.style.display = 'none';
					if (sapOption) sapOption.style.display = '';
					if (oracleOption) oracleOption.style.display = '';
					if (douzoneOption) douzoneOption.style.display = 'none';
					if (youngOption) youngOption.style.display = 'none';
					if (softwareSelect.value === 'ETC' || softwareSelect.value === 'DOUZONE' || softwareSelect.value === 'YOUNG') {
						softwareSelect.value = 'SAP';
					}
				} else {
					// Package Non-modifiable: 더존, 영림원만 표시
					softwareSelect.disabled = false;
					if (etcOption) etcOption.style.display = 'none';
					if (sapOption) sapOption.style.display = 'none';
					if (oracleOption) oracleOption.style.display = 'none';
					if (douzoneOption) douzoneOption.style.display = '';
					if (youngOption) youngOption.style.display = '';
					if (softwareSelect.value === 'ETC' || softwareSelect.value === 'SAP' || softwareSelect.value === 'ORACLE') {
						softwareSelect.value = 'DOUZONE';
					}
				}
				// SW 변경에 따른 버전 갱신
				handleSoftwareChange();
			}

			// Cloud 환경 변경 시 핸들러
			function handleCloudEnvChange() {
				const cloudEnv = document.getElementById('cloud_env').value;
				const osSelect = document.getElementById('os');
				const dbSelect = document.getElementById('db');

				if (cloudEnv === 'SaaS') {
					osSelect.value = 'N/A';
					dbSelect.value = 'N/A';
					osSelect.disabled = true;
					dbSelect.disabled = true;
				} else if (cloudEnv === 'PaaS') {
					osSelect.value = 'N/A';
					osSelect.disabled = true;
					dbSelect.disabled = false;
					if (dbSelect.value === 'N/A') dbSelect.value = 'ORACLE';
				} else {
					osSelect.disabled = false;
					dbSelect.disabled = false;
					if (osSelect.value === 'N/A') osSelect.value = 'RHEL';
					if (dbSelect.value === 'N/A') dbSelect.value = 'ORACLE';
				}

				// 통제 항목 행 비활성화 시각화
				const allRows = document.querySelectorAll('.control-row');
				allRows.forEach(row => {
					const id = row.dataset.id;
					let isExcluded = false;

					// 1. 모든 Cloud 환경에서 데이터센터(CO06)는 CSP 책임
					if (cloudEnv !== 'None' && id === 'CO06') isExcluded = true;

					// 2. SaaS/PaaS에서는 OS 통제(APD09-APD11, PC06) 제외
					if ((cloudEnv === 'SaaS' || cloudEnv === 'PaaS') && 
						(['APD09', 'APD10', 'APD11', 'PC06'].includes(id))) isExcluded = true;

					// 3. SaaS에서는 DB 통제(APD12-APD14, PC07) 및 프로그램 변경 통제(PC01-PC05) 제외
					if (cloudEnv === 'SaaS' && 
						(['APD12', 'APD13', 'APD14', 'PC01', 'PC02', 'PC03', 'PC04', 'PC05', 'PC07'].includes(id))) isExcluded = true;

					const targetContainer = row.cells[1].querySelector('.d-flex');
					const testProcDetail = document.getElementById(`test-proc-detail-${id}`);
					
					if (isExcluded) {
						row.classList.add('excluded-control');
						row.querySelectorAll('select').forEach(s => s.disabled = true);
						
						if (targetContainer && !targetContainer.querySelector('.cloud-badge')) {
							const badge = document.createElement('span');
							badge.className = 'cloud-badge';
							badge.innerHTML = '<i class="fas fa-cloud me-1"></i>CSP Managed';
							targetContainer.appendChild(badge);
						}

						// 테스트 절차를 SOC 리포트용으로 변경
						if (testProcDetail) {
							// 기존값 백업 (최초 1회)
							if (!testProcDetail.dataset.origManual) {
								testProcDetail.dataset.origManual = testProcDetail.dataset.manual;
								testProcDetail.dataset.origAuto = testProcDetail.dataset.auto;
							}
							const cloudMsg = "[CSP Managed] 본 통제는 클라우드 서비스 제공자의 책임 영역에 해당하므로, 당해년도 CSP의 SOC 1/2 Type II 리포트 상의 물리적/환경적 보안 적정성 검토 결과로 갈음함.";
							testProcDetail.textContent = cloudMsg;
							// 엑셀 전송용 데이터셋도 임시 변경
							testProcDetail.dataset.manual = cloudMsg;
							testProcDetail.dataset.auto = cloudMsg;
						}
					} else {
						row.classList.remove('excluded-control');
						if (targetContainer) {
							const badge = targetContainer.querySelector('.cloud-badge');
							if (badge) badge.remove();
						}

						// 백업된 기존 절차 복구
						if (testProcDetail && testProcDetail.dataset.origManual) {
							testProcDetail.dataset.manual = testProcDetail.dataset.origManual;
							testProcDetail.dataset.auto = testProcDetail.dataset.origAuto;
						}

						// 원래 로직(자동/수동)에 따라 활성화 여부 및 텍스트 재결정
						handleTypeChange(id); 
					}
				});
			}

			// SW 버전 옵션 정의
			const SW_VERSION_OPTIONS = {
				'SAP': [
					{value: 'ECC', text: 'ECC 6.0'},
					{value: 'S4HANA', text: 'S/4HANA (On-Premise)'},
					{value: 'S4CLOUD', text: 'S/4HANA Cloud'}
				],
				'ORACLE': [
					{value: 'R12', text: 'E-Business Suite R12'},
					{value: 'FUSION', text: 'Oracle Fusion Cloud'},
					{value: 'JDE', text: 'JD Edwards'}
				],
				'DOUZONE': [
					{value: 'ICUBE', text: 'iCUBE'},
					{value: 'IU', text: 'iU ERP'},
					{value: 'WEHAGO', text: 'WEHAGO (Cloud)'},
					{value: 'AMARANTH', text: 'Amaranth 10'}
				],
				'YOUNG': [
					{value: 'KSYSTEM', text: 'K-System (Standard)'},
					{value: 'KSYSTEMPLUS', text: 'K-System Plus'},
					{value: 'SYSTEVER', text: 'SystemEver (Cloud)'}
				],
				'ETC': [
					{value: 'CUSTOM', text: '자체개발 시스템'},
					{value: 'OTHER', text: '기타 패키지'}
				]
			};

			// OS 버전 옵션 정의
			const OS_VERSION_OPTIONS = {
				'RHEL': [
					{value: 'RHEL9', text: 'RHEL 9.x / Rocky 9'},
					{value: 'RHEL8', text: 'RHEL 8.x / CentOS 8'},
					{value: 'RHEL7', text: 'RHEL 7.x / CentOS 7'}
				],
				'UBUNTU': [
					{value: 'U2204', text: 'Ubuntu 22.04 LTS'},
					{value: 'U2004', text: 'Ubuntu 20.04 LTS'},
					{value: 'U1804', text: 'Ubuntu 18.04 LTS'}
				],
				'WINDOWS': [
					{value: 'W2022', text: 'Windows Server 2022'},
					{value: 'W2019', text: 'Windows Server 2019'},
					{value: 'W2016', text: 'Windows Server 2016'}
				],
				'UNIX': [
					{value: 'AIX73', text: 'AIX 7.3'},
					{value: 'AIX72', text: 'AIX 7.2'},
					{value: 'HPUX', text: 'HP-UX 11i v3'}
				],
				'N/A': [
					{value: 'NA', text: 'N/A (CSP Managed)'}
				]
			};

			// DB 버전 옵션 정의
			const DB_VERSION_OPTIONS = {
				'ORACLE': [
					{value: '19C', text: 'Oracle 19c'},
					{value: '21C', text: 'Oracle 21c'},
					{value: '12C', text: 'Oracle 12c'},
					{value: '11G', text: 'Oracle 11g'}
				],
				'TIBERO': [
					{value: 'T7', text: 'Tibero 7'},
					{value: 'T6', text: 'Tibero 6'}
				],
				'MSSQL': [
					{value: 'SQL2022', text: 'SQL Server 2022'},
					{value: 'SQL2019', text: 'SQL Server 2019'},
					{value: 'SQL2017', text: 'SQL Server 2017'}
				],
				'MYSQL': [
					{value: 'MY8', text: 'MySQL 8.x'},
					{value: 'MARIA10', text: 'MariaDB 10.x'}
				],
				'POSTGRES': [
					{value: 'PG15', text: 'PostgreSQL 15'},
					{value: 'PG14', text: 'PostgreSQL 14'},
					{value: 'PG13', text: 'PostgreSQL 13'}
				],
				'HANA': [
					{value: 'HANA2', text: 'SAP HANA 2.0'},
					{value: 'HANACLOUD', text: 'SAP HANA Cloud'}
				],
				'N/A': [
					{value: 'NA', text: 'N/A (CSP Managed)'}
				]
			};

			// SW 변경 시 버전 옵션 갱신
			function handleSoftwareChange() {
				const sw = document.getElementById('software').value;
				const versionSelect = document.getElementById('sw_version');
				const options = SW_VERSION_OPTIONS[sw] || [];

				versionSelect.innerHTML = '';
				options.forEach(opt => {
					const option = document.createElement('option');
					option.value = opt.value;
					option.textContent = opt.text;
					versionSelect.appendChild(option);
				});

				// SAP S/4HANA 선택 시 DB를 HANA로 자동 변경
				if (sw === 'SAP' && versionSelect.value.includes('S4')) {
					const dbSelect = document.getElementById('db');
					if (dbSelect.value !== 'HANA') {
						dbSelect.value = 'HANA';
						handleDbChange();
					}
				}

				refreshAllPopulations();
			}

			// OS 변경 시 버전 옵션 갱신
			function handleOsChange() {
				const os = document.getElementById('os').value;
				const versionSelect = document.getElementById('os_version');
				const options = OS_VERSION_OPTIONS[os] || [];

				versionSelect.innerHTML = '';
				options.forEach(opt => {
					const option = document.createElement('option');
					option.value = opt.value;
					option.textContent = opt.text;
					versionSelect.appendChild(option);
				});

				refreshAllPopulations();
			}

			// DB 변경 시 버전 옵션 갱신
			function handleDbChange() {
				const db = document.getElementById('db').value;
				const versionSelect = document.getElementById('db_version');
				const options = DB_VERSION_OPTIONS[db] || [];

				versionSelect.innerHTML = '';
				options.forEach(opt => {
					const option = document.createElement('option');
					option.value = opt.value;
					option.textContent = opt.text;
					versionSelect.appendChild(option);
				});

				refreshAllPopulations();
			}

			// 기본값 복원
			function resetVersions() {
				document.getElementById('software').value = 'SAP';
				document.getElementById('os').value = 'RHEL';
				document.getElementById('db').value = 'ORACLE';
				handleSoftwareChange();
				handleOsChange();
				handleDbChange();
			}

			// 주기별 모집단 기준
			const FREQUENCY_POPULATION = {
				'연': 1,
				'분기': 4,
				'월': 12,
				'주': 52,
				'일': 250,
				'수시': 0,
				'기타': 0
			};

			// 주기별 모집단명
			const FREQUENCY_POPULATION_NAME = {
				'연': '연간 모니터링 문서',
				'분기': '분기별 모니터링 문서',
				'월': '월별 모니터링 문서',
				'주': '주별 모니터링 문서',
				'일': '일별 모니터링 문서',
				'수시': '수시 발생 건',
				'기타': '-'
			};

			// 주기 변경 시 모집단 자동 설정
			function updatePopulationByFrequency(id) {
				const freqSelect = document.getElementById(`freq-${id}`);
				const populationInput = document.getElementById(`population-${id}`);
				const freq = freqSelect ? freqSelect.value : '수시';
				const popCount = FREQUENCY_POPULATION[freq] || 0;
				populationInput.value = popCount;
				calculateSample(id);

				// 화면에 모집단 정보 표시
				updatePopulationDisplay(id, freq, popCount);
			}

			// 모집단 정보 화면 업데이트
			function updatePopulationDisplay(id, freq, popCount) {
				const typeSelect = document.getElementById(`type-${id}`);
				const isAuto = typeSelect && typeSelect.value === 'Auto';

				const popNameEl = document.getElementById(`population-name-${id}`);
				const popCountEl = document.getElementById(`population-count-${id}`);
				const sampleCountEl = document.getElementById(`sample-count-${id}`);
				const completenessEl = document.getElementById(`completeness-${id}`);
				const completenessDetailEl = document.getElementById(`completeness-detail-${id}`);

				let popName = FREQUENCY_POPULATION_NAME[freq] || '-';
				let completenessText = '';
				let completenessDetail = '';
				const sampleCount = isAuto || freq === '기타' ? 0 : (FREQUENCY_SAMPLE[freq] || 0);

				// 자동통제일 경우 - 시스템별 조회 방법 표시
				if (isAuto) {
					const template = getPopulationTemplate(id);
					if (template) {
						popName = template.population;
						completenessText = '자동통제';
						completenessDetail = template.completeness;
					} else {
						popName = "N/A (자동통제)";
						completenessText = '자동통제';
						completenessDetail = '자동통제이므로 모집단 완전성 확인 대상에서 제외함\n시스템별 확인 방법은 시스템 선택 후 확인';
					}
				}
				// 수시 통제일 경우 템플릿에서 모집단/완전성 가져오기
				else if (freq === '수시') {
					// APD02, APD03 수동 설정 시 예외 처리 (사용자 요청 사항)
					if (!isAuto && id === 'APD02') {
						popName = "부서이동자리스트";
						completenessText = '✓ 확인';
						completenessDetail = "인사시스템 상의 부서이동자 명단과 권한 회수 내역 전수 대사";
					} else if (!isAuto && id === 'APD03') {
						popName = "퇴사자리스트";
						completenessText = '✓ 확인';
						completenessDetail = "인사시스템 상의 퇴사자 명단과 계정 비활성화 내역 전수 대사";
					} else {
						const template = getPopulationTemplate(id);
						if (template) {
							popName = template.population;
							completenessText = '✓ 확인';
							completenessDetail = template.completeness;
						} else {
							completenessText = '확인 필요';
							completenessDetail = '수시 발생 건이므로 모집단 완전성을 별도로 확인해야 함';
						}
					}
				} else if (popCount > 0 && popName !== '-') {
					completenessText = '✓ 확인';
					completenessDetail = `${popName}이므로 ${popCount}건을 완전성 있는 것으로 확인함`;
				} else {
					completenessText = '-';
					completenessDetail = '';
				}

				if (popNameEl) popNameEl.textContent = popName;
				if (popCountEl) popCountEl.textContent = isAuto ? 'N/A' : (popCount > 0 ? `${popCount}건` : (freq === '수시' ? '조회 필요' : '-'));
				if (sampleCountEl) sampleCountEl.textContent = sampleCount > 0 ? `${sampleCount}건` : 'N/A';

				if (completenessEl) {
					completenessEl.textContent = completenessText;
				}

				// 완전성 상세 표시 (테이블명, 쿼리, 메뉴경로 등)
				if (completenessDetailEl) {
					if (completenessDetail) {
						completenessDetailEl.innerHTML = formatCompletenessDetail(completenessDetail);
						completenessDetailEl.style.display = 'block';
					} else {
						completenessDetailEl.style.display = 'none';
					}
				}
			}

			// 완전성 상세 정보 포맷팅 (쿼리, 메뉴 등 하이라이트)
			function formatCompletenessDetail(text) {
				if (!text) return '';
				// [자동통제 확인방법] 헤더 하이라이트
				let formatted = text.replace(/\[자동통제 확인방법\]/g, '<span class="badge bg-warning text-dark me-1">자동통제 확인방법</span>');
				// [버전별 참고] 헤더 하이라이트
				formatted = formatted.replace(/\[버전별 참고\]/g, '<br><span class="badge bg-info me-1 mt-2">버전별 참고</span>');
				// [Query] 부분 하이라이트
				formatted = formatted.replace(/\[Query\]/g, '<span class="badge bg-primary me-1">Query</span>');
				// [메뉴] 부분 하이라이트
				formatted = formatted.replace(/\[메뉴\]/g, '<span class="badge bg-success me-1">메뉴</span>');
				// SQL 키워드 강조 (SELECT, FROM, WHERE, BETWEEN, AND, OR)
				formatted = formatted.replace(/\b(SELECT|FROM|WHERE|BETWEEN|AND|OR)\b/g, '<span class="text-primary fw-bold">$1</span>');
				// 테이블명 (대문자+언더스코어 패턴) 강조
				formatted = formatted.replace(/\b(TB[A-Z_]+|TBSM_[A-Z_]+|FND_[A-Z_]+)\b/g, '<span class="text-danger fw-bold">$1</span>');
				// T-Code 강조
				formatted = formatted.replace(/T-Code:\s*([A-Z0-9]+)/g, 'T-Code: <span class="badge bg-secondary">$1</span>');
				// 버전명 강조 (• 로 시작하는 라인의 버전명)
				formatted = formatted.replace(/•\s*([\w\-\/\s]+):/g, '• <strong class="text-info">$1</strong>:');
				return formatted;
			}

			// 주기별 표본수 기준
			const FREQUENCY_SAMPLE = {
				'연': 1,
				'분기': 2,
				'월': 2,
				'주': 5,
				'일': 20,
				'수시': 25,
				'기타': 0
			};

			// 모집단/완전성 템플릿 (서버에서 로드)
			let populationTemplates = {
				sw: {},
				os: {},
				db: {}
			};

			// 템플릿 로드
			async function loadPopulationTemplates() {
				try {
					const response = await fetch('/api/rcm/population_templates');
					const result = await response.json();
					if (result.success) {
						populationTemplates.sw = result.sw_templates;
						populationTemplates.os = result.os_templates;
						populationTemplates.db = result.db_templates;
						console.log('모집단 템플릿 로드 완료');
					}
				} catch (error) {
					console.error('템플릿 로드 실패:', error);
				}
			}

			// 통제별 관련 영역 매핑
			const CONTROL_DOMAIN = {
				// SW 관련 통제 (수동)
				'APD01': 'sw', 'APD02': 'sw', 'APD03': 'sw', 'APD07': 'sw',
				'PC01': 'sw', 'PC02': 'sw', 'PC03': 'sw',
				'CO01': 'sw', 'ST03': 'sw',
				'PD01': 'sw', 'PD02': 'sw', 'PD03': 'sw', 'PD04': 'sw', 'CO05': 'sw',
				// SW 관련 통제 (자동)
				'APD04': 'sw', 'APD05': 'sw', 'APD06': 'sw',
				'PC04': 'sw', 'PC05': 'sw',
				'CO02': 'sw', 'CO03': 'sw', 'CO04': 'sw',
				'ST01': 'sw', 'ST02': 'sw',
				// OS 관련 통제
				'APD09': 'os', 'APD10': 'os', 'APD11': 'os', 'PC06': 'os',
				// DB 관련 통제
				'APD08': 'db', 'APD12': 'db', 'APD13': 'db', 'APD14': 'db', 'PC07': 'db'
			};

			// 현재 선택된 시스템 환경에서 템플릿 가져오기
			function getPopulationTemplate(controlId) {
				const domain = CONTROL_DOMAIN[controlId];
				if (!domain) return null;

				const sw = document.getElementById('software').value;
				const os = document.getElementById('os').value;
				const db = document.getElementById('db').value;

				let template = null;
				if (domain === 'sw' && populationTemplates.sw[sw]) {
					template = populationTemplates.sw[sw][controlId];
				} else if (domain === 'os' && populationTemplates.os[os]) {
					template = populationTemplates.os[os][controlId];
				} else if (domain === 'db' && populationTemplates.db[db]) {
					template = populationTemplates.db[db][controlId];
				}
				return template;
			}

			// 시스템 환경 변경 시 모든 통제의 모집단 정보 갱신 (자동통제 + 수시통제)
			function refreshAllPopulations() {
				const rows = document.querySelectorAll('.control-row');
				rows.forEach(row => {
					const id = row.dataset.id;
					const typeSelect = document.getElementById(`type-${id}`);
					const freqSelect = document.getElementById(`freq-${id}`);
					const isAuto = typeSelect && typeSelect.value === 'Auto';
					const freq = freqSelect ? freqSelect.value : '수시';

					// 자동통제이거나 수시 통제인 경우 갱신
					if (isAuto || freq === '수시') {
						const popCount = FREQUENCY_POPULATION[freq] || 0;
						updatePopulationDisplay(id, freq, popCount);
					}
				});
			}

			// 표본 수 계산
			function calculateSample(id) {
				const sampleInput = document.getElementById(`sample-${id}`);
				const typeSelect = document.getElementById(`type-${id}`);
				const freqSelect = document.getElementById(`freq-${id}`);
				
				const type = typeSelect ? typeSelect.value : 'Manual';
				const freq = freqSelect ? freqSelect.value : '수시';

				// 자동통제이거나 주기가 '기타'인 경우 표본수는 0
				if (type === 'Auto' || freq === '기타') {
					sampleInput.value = 0;
					return;
				}

				// 주기별 고정 표본수
				const sampleSize = FREQUENCY_SAMPLE[freq] || 0;
				sampleInput.value = sampleSize;
			}

			// 자동/수동 변경 시 핸들러
			function handleTypeChange(id) {
				const typeSelect = document.getElementById(`type-${id}`);
				const freqSelect = document.getElementById(`freq-${id}`);
				const methodSelect = document.getElementById(`method-${id}`);
				const testProcDetail = document.getElementById(`test-proc-detail-${id}`);
				const otherOption = freqSelect.querySelector('option[value="기타"]');

				if (typeSelect.value === 'Auto') {
					// 자동통제일 때 '기타' 옵션을 보이고 선택
					if (otherOption) otherOption.style.display = '';
					freqSelect.value = '기타';
					methodSelect.value = '예방';
					freqSelect.disabled = true;
					methodSelect.disabled = true;
					// 자동 테스트 절차로 변경
					if (testProcDetail) {
						testProcDetail.textContent = testProcDetail.dataset.auto;
					}
				} else {
					// 수동통제일 때 '기타' 옵션을 감춤
					if (otherOption) otherOption.style.display = 'none';
					freqSelect.disabled = false;
					methodSelect.disabled = false;
					
					// 현재 주기가 '기타'라면 수동통제의 기본값인 '수시'로 변경
					if (freqSelect.value === '기타') {
						freqSelect.value = '수시';
					}

					// 수동 테스트 절차로 변경
					if (testProcDetail) {
						testProcDetail.textContent = testProcDetail.dataset.manual;
					}
				}
				// 자동/수동 변경 시 모집단 및 표본수 재계산
				updatePopulationByFrequency(id);
			}

			// 페이지 로드 시 상태 초기화
			document.addEventListener('DOMContentLoaded', async function() {
				// 모집단 템플릿 로드
				await loadPopulationTemplates();

				// 시스템 유형 및 SW 상태 초기화
				handleSystemTypeChange();
				// Cloud 환경 초기화
				handleCloudEnvChange();
				// 버전 선택 초기화
				handleSoftwareChange();
				handleOsChange();
				handleDbChange();

				const rows = document.querySelectorAll('.control-row');
				rows.forEach(row => {
					const id = row.dataset.id;
					// 초기 로드 시 자동/수동 로직을 한 번 실행하여 값과 활성화 상태를 맞춤
					handleTypeChange(id);
				});

				// 초기 로드 후 모든 자동통제/수시통제의 모집단 정보 갱신
				refreshAllPopulations();

				// SW/OS/DB 변경 시 정보 갱신 (이미 onchange에서 처리)
				// 버전 변경 시에도 모집단 정보 갱신
				['sw_version', 'os_version', 'db_version'].forEach(selectId => {
					const selectEl = document.getElementById(selectId);
					if (selectEl) {
						selectEl.addEventListener('change', () => {
							refreshAllPopulations();
							refreshAllProcedures();
						});
					}
				});
			});

			// 모든 절차를 마스터(범용) 값으로 초기화
			function refreshAllProcedures() {
				// AI 분석 결과가 이미 적용된 경우 사용자에게 알림 (선택 사항)
				console.log('시스템 환경 변경으로 인해 기술 절차를 범용 값으로 초기화합니다.');
				
				const rows = document.querySelectorAll('.control-row');
				rows.forEach(row => {
					const id = row.dataset.id;
					const typeSelect = document.getElementById(`type-${id}`);
					const testProcDetail = document.getElementById(`test-proc-detail-${id}`);
					
					if (testProcDetail) {
						// 백업된 오리지널(범용) 데이터로 복구
						const origAuto = testProcDetail.dataset.origAuto || testProcDetail.dataset.auto;
						const origManual = testProcDetail.dataset.origManual || testProcDetail.dataset.manual;
						
						// 현재 타입에 맞춰 표시
						if (typeSelect && typeSelect.value === 'Auto') {
							testProcDetail.textContent = origAuto;
							testProcDetail.dataset.auto = origAuto; // AI 결과 덮어쓰기 방지 (초기화)
						} else {
							testProcDetail.textContent = origManual;
							testProcDetail.dataset.manual = origManual; // AI 결과 덮어쓰기 방지 (초기화)
						}
					}
				});
			}
			
			// AI 분석 실행
			document.getElementById('btn-generate-ai').addEventListener('click', async function() {
				const form = document.getElementById('system-form');
				if (!form.checkValidity()) {
					form.reportValidity();
					return;
				}
				
				const systemData = {
					system_name: document.getElementById('system_name').value,
					system_type: document.getElementById('system_type').value,
					software: document.getElementById('software').value,
					os: document.getElementById('os').value,
					db: document.getElementById('db').value
				};
				
				document.getElementById('loading-overlay').style.display = 'flex';
				
				try {
					const response = await fetch('/api/rcm/ai_generate', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
							'X-CSRFToken': csrfToken
						},
						body: JSON.stringify(systemData)
					});
					
					const result = await response.json();
					if (result.success) {
						updateRcmTable(result.data);
					} else {
						alert("AI 분석 오류: " + result.message);
					}
				} catch (error) {
					console.error(error);
					alert("시스템 오류가 발생했습니다.");
				} finally {
					document.getElementById('loading-overlay').style.display = 'none';
				}
			});
			
			function updateRcmTable(data) {
				data.forEach(item => {
					const id = item.id;
					const typeSelect = document.getElementById(`type-${id}`);
					const activityDetail = document.getElementById(`activity-detail-${id}`);
					const testProcDetail = document.getElementById(`test-proc-detail-${id}`);
					
					if (activityDetail) {
						activityDetail.innerText = item.activity;
					}
					
					if (testProcDetail) {
						// AI가 생성한 절차를 데이터셋에 저장
						const currentType = typeSelect ? typeSelect.value : 'Manual';
						if (currentType === 'Auto') {
							testProcDetail.dataset.auto = item.procedure;
							testProcDetail.textContent = item.procedure; // 즉시 반영
						} else {
							testProcDetail.dataset.manual = item.procedure;
							testProcDetail.textContent = item.procedure; // 즉시 반영
						}
					}
				});
			}

			// 엑셀 다운로드 - 화면에서 수정한 값만 전달 (나머지는 서버의 마스터 데이터 사용)
			document.getElementById('btn-export-excel').addEventListener('click', async function() {
				const rows = document.querySelectorAll('.control-row');
				const rcm_data = [];

				rows.forEach(row => {
					const id = row.dataset.id;
					const typeSelect = document.getElementById(`type-${id}`);
					const freqSelect = document.getElementById(`freq-${id}`);
					const methodSelect = document.getElementById(`method-${id}`);
					const activityDetail = document.getElementById(`activity-detail-${id}`);
					const testProcDetail = document.getElementById(`test-proc-detail-${id}`);

					if (typeSelect && freqSelect && methodSelect) {
						rcm_data.push({
							id: id,
							type: typeSelect.value === 'Auto' ? '자동' : '수동',
							frequency: freqSelect.value,
							method: methodSelect.value,
							activity: activityDetail ? activityDetail.textContent : '',
							procedure: testProcDetail ? testProcDetail.textContent : ''
						});
					}
				});

				const systemName = document.getElementById('system_name').value || 'ITGC';
				const cloudEnv = document.getElementById('cloud_env').value;
				const software = document.getElementById('software').value;
				const osType = document.getElementById('os').value;
				const dbType = document.getElementById('db').value;

				const payload = {
					system_info: { 
						system_name: systemName,
						cloud_env: cloudEnv,
						software: software,
						os: osType,
						db: dbType
					},
					rcm_data: rcm_data
				};

				this.disabled = true;
				this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>생성 중...';

				try {
					const response = await fetch('/api/rcm/export_excel', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
							'X-CSRFToken': csrfToken
						},
						body: JSON.stringify(payload)
					});

					const result = await response.json();
					if (result.success) {
						// Base64 -> Blob 변환 및 다운로드
						const byteCharacters = atob(result.file_data);
						const byteArray = new Uint8Array(byteCharacters.length);
						for (let i = 0; i < byteCharacters.length; i++) {
							byteArray[i] = byteCharacters.charCodeAt(i);
						}
						const blob = new Blob([byteArray], {
							type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
						});

						const link = document.createElement('a');
						link.href = window.URL.createObjectURL(blob);
						link.download = result.filename;
						document.body.appendChild(link);
						link.click();
						document.body.removeChild(link);
					} else {
						alert("엑셀 생성 오류: " + (result.message || '알 수 없는 오류'));
					}
				} catch (error) {
					console.error('Excel export error:', error);
					alert("다운로드 중 오류가 발생했습니다: " + error.message);
				} finally {
					this.disabled = false;
					this.innerHTML = '<i class="fas fa-file-excel me-1"></i>최종 RCM 엑셀 다운로드';
				}
			});
		</script>
	</body>
</html>
