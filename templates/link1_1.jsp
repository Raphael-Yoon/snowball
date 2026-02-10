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
										<label class="form-label fw-bold">OS</label>
										<select class="form-select" id="os" name="os">
											<option value="RHEL">Linux (RHEL/CentOS)</option>
											<option value="UBUNTU">Linux (Ubuntu/Debian)</option>
											<option value="WINDOWS">Windows Server</option>
											<option value="UNIX">Unix (AIX/HP-UX)</option>
											<option value="N/A">N/A (SaaS/PaaS)</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">DB</label>
										<select class="form-select" id="db" name="db">
											<option value="ORACLE">Oracle DB</option>
											<option value="TIBERO">Tibero (Tmax)</option>
											<option value="MSSQL">MS-SQL</option>
											<option value="MYSQL">MySQL/MariaDB</option>
											<option value="POSTGRES">PostgreSQL</option>
											<option value="NOSQL">NoSQL (MongoDB 등)</option>
											<option value="N/A">N/A (SaaS)</option>
										</select>
									</div>
									<div class="col-md-3 mb-3">
										<label class="form-label fw-bold">주요 SW</label>
										<select class="form-select" id="software" name="software">
											<option value="SAP">SAP ERP</option>
											<option value="ORACLE">Oracle ERP</option>
											<option value="DOUZONE">더존 (iU/iCUBE)</option>
											<option value="YOUNG">영림원 (K-System)</option>
											<option value="ETC">기타 / 자체개발</option>
										</select>
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
														<div class="mb-2"><strong><i class="fas fa-shield-alt me-1"></i>통제 활동</strong></div>
														<p class="small mb-0 text-dark" id="activity-detail-{{ control.id }}" style="white-space: pre-wrap;">{{ control.control_description }}</p>
													</div>
													
													<div class="pt-3 border-top">
														<div class="mb-2"><strong><i class="fas fa-clipboard-check me-1"></i>테스트 절차</strong></div>
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
			// CSRF 토큰 설정
			const csrfToken = "{{ csrf_token() }}";
			
			// 시스템 유형 변경 시 핸들러
			function handleSystemTypeChange() {
				const systemType = document.getElementById('system_type').value;
				const softwareSelect = document.getElementById('software');
				
				if (systemType === 'In-house') {
					softwareSelect.value = 'ETC';
					softwareSelect.disabled = true;
				} else {
					softwareSelect.disabled = false;
				}
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

			// 주기 변경 시 모집단 자동 설정
			function updatePopulationByFrequency(id) {
				const freqSelect = document.getElementById(`freq-${id}`);
				const populationInput = document.getElementById(`population-${id}`);
				const freq = freqSelect ? freqSelect.value : '수시';
				populationInput.value = FREQUENCY_POPULATION[freq] || 0;
				calculateSample(id);
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
			document.addEventListener('DOMContentLoaded', function() {
				// 시스템 유형 및 SW 상태 초기화
				handleSystemTypeChange();
				// Cloud 환경 초기화
				handleCloudEnvChange();

				const rows = document.querySelectorAll('.control-row');
				rows.forEach(row => {
					const id = row.dataset.id;
					// 초기 로드 시 자동/수동 로직을 한 번 실행하여 값과 활성화 상태를 맞춤
					handleTypeChange(id);
				});
			});
			
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

				const payload = {
					system_info: { 
						system_name: systemName,
						cloud_env: cloudEnv
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
