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
										<select class="form-select" id="system_type" name="system_type" required>
											<option value="In-house">In-house (자체개발)</option>
											<option value="Package-Modifiable">Package - Modifiable (SAP, Oracle ERP 등)</option>
											<option value="Package-Non-modifiable">Package - Non-modifiable (더존, 영림원 등)</option>
										</select>
									</div>
								</div>
								
								<div class="row">
									<div class="col-md-4 mb-3">
										<label class="form-label fw-bold">주요 SW</label>
										<select class="form-select" id="software" name="software">
											<option value="SAP">SAP</option>
											<option value="ORACLE">Oracle ERP</option>
											<option value="DOUZONE">더존</option>
											<option value="YOUNG">영림원</option>
											<option value="CUSTOM">Custom/Java/Next.js</option>
											<option value="ETC">기타</option>
										</select>
									</div>
									<div class="col-md-4 mb-3">
										<label class="form-label fw-bold">OS</label>
										<select class="form-select" id="os" name="os">
											<option value="LINUX">Linux (RHEL/Ubuntu)</option>
											<option value="WINDOWS">Windows Server</option>
											<option value="UNIX">Unix (AIX/HP-UX)</option>
										</select>
									</div>
									<div class="col-md-4 mb-3">
										<label class="form-label fw-bold">DB</label>
										<select class="form-select" id="db" name="db">
											<option value="ORACLE">Oracle DB</option>
											<option value="MSSQL">MS-SQL</option>
											<option value="MYSQL">MySQL/MariaDB</option>
											<option value="POSTGRES">PostgreSQL</option>
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
							<h5 class="mb-0 fw-bold">ITGC Risk Control Matrix (목록)</h5>
							<div>
								<span class="badge mode-auto me-2">AI 자동 생성됨</span>
								<span class="badge mode-manual">수동 수정 가능</span>
							</div>
						</div>
						
						<div class="table-responsive">
							<table class="table align-middle">
								<thead class="table-light">
									<tr>
										<th style="width: 100px;">ID</th>
										<th style="width: 200px;">통제 항목</th>
										<th>통제 활동 & 테스트 절차 (AI Mapping)</th>
										<th style="width: 120px;">설계 방식</th>
									</tr>
								</thead>
								<tbody id="rcm-tbody">
									{% for control in master_controls %}
									<tr class="control-row" data-id="{{ control.id }}" data-name="{{ control.name }}" data-objective="{{ control.objective }}">
										<td class="fw-bold">{{ control.id }}</td>
										<td>
											<div class="fw-bold">{{ control.name }}</div>
											<small class="text-muted">{{ control.category }}</small>
										</td>
										<td>
											<div class="content-wrapper" id="content-{{ control.id }}">
												<div class="readonly-content mb-2" id="readonly-activity-{{ control.id }}">분석 전입니다. 상단에서 AI 분석을 시작하세요.</div>
												<div class="readonly-content text-muted small" id="readonly-procedure-{{ control.id }}"></div>
												
												<!-- Manual Edit Fields (Hidden by default) -->
												<div class="manual-edit d-none" id="manual-{{ control.id }}">
													<label class="small fw-bold">통제 활동</label>
													<textarea class="editable-content mb-2" id="edit-activity-{{ control.id }}"></textarea>
													<label class="small fw-bold">테스트 절차</label>
													<textarea class="editable-content" id="edit-procedure-{{ control.id }}"></textarea>
												</div>
											</div>
										</td>
										<td class="text-center">
											<span class="mode-badge mode-auto" id="badge-{{ control.id }}" onclick="toggleMode('{{ control.id }}')">Auto</span>
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
			
			// 모드 전환 함수 (Auto <-> Manual)
			function toggleMode(id) {
				const badge = document.getElementById(`badge-${id}`);
				const isAuto = badge.classList.contains('mode-auto');
				const manualDiv = document.getElementById(`manual-${id}`);
				const roActivity = id.startsWith('readonly-activity-') ? document.getElementById(id) : document.getElementById(`readonly-activity-${id}`);
				const roProcedure = document.getElementById(`readonly-procedure-${id}`);
				
				if (isAuto) {
					// Switch to Manual
					badge.classList.remove('mode-auto');
					badge.classList.add('mode-manual');
					badge.innerText = 'Manual';
					manualDiv.classList.remove('d-none');
					roActivity.classList.add('d-none');
					roProcedure.classList.add('d-none');
					
					// Sync manual textareas with last known AI content if empty
					const editAct = document.getElementById(`edit-activity-${id}`);
					const editProc = document.getElementById(`edit-procedure-${id}`);
					if (!editAct.value) editAct.value = roActivity.innerText;
					if (!editProc.value) editProc.value = roProcedure.innerText;
				} else {
					// Switch to Auto
					badge.classList.remove('mode-manual');
					badge.classList.add('mode-auto');
					badge.innerText = 'Auto';
					manualDiv.classList.add('d-none');
					roActivity.classList.remove('d-none');
					roProcedure.classList.remove('d-none');
				}
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
					const roActivity = document.getElementById(`readonly-activity-${id}`);
					const roProcedure = document.getElementById(`readonly-procedure-${id}`);
					const editAct = document.getElementById(`edit-activity-${id}`);
					const editProc = document.getElementById(`edit-procedure-${id}`);
					
					if (roActivity) {
						roActivity.innerText = item.activity;
						roActivity.classList.remove('text-muted');
					}
					if (roProcedure) roProcedure.innerText = "테스트 절차: " + item.procedure;
					
					// Update edit areas too
					if (editAct) editAct.value = item.activity;
					if (editProc) editProc.value = item.procedure;
				});
			}

			// 엑셀 다운로드
			document.getElementById('btn-export-excel').addEventListener('click', async function() {
				const rows = document.querySelectorAll('.control-row');
				const rcm_data = [];
				
				rows.forEach(row => {
					const id = row.dataset.id;
					const badge = document.getElementById(`badge-${id}`);
					const isManual = badge.classList.contains('mode-manual');
					
					let activity, procedure;
					if (isManual) {
						activity = document.getElementById(`edit-activity-${id}`).value;
						procedure = document.getElementById(`edit-procedure-${id}`).value;
					} else {
						activity = document.getElementById(`readonly-activity-${id}`).innerText;
						procedure = document.getElementById(`readonly-procedure-${id}`).innerText.replace("테스트 절차: ", "");
					}
					
					rcm_data.push({
						id: id,
						name: row.dataset.name,
						objective: row.dataset.objective,
						activity: activity,
						procedure: procedure
					});
				});
				
				const payload = {
					system_info: {
						system_name: document.getElementById('system_name').value
					},
					rcm_data: rcm_data
				};
				
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
						// Base64를 Blob으로 변환하여 파일 다운로드
						const byteCharacters = atob(result.file_data);
						const byteNumbers = new Array(byteCharacters.length);
						for (let i = 0; i < byteCharacters.length; i++) {
							byteNumbers[i] = byteCharacters.charCodeAt(i);
						}
						const byteArray = new Uint8Array(byteNumbers);
						const blob = new Blob([byteArray], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
						
						const link = document.createElement('a');
						link.href = window.URL.createObjectURL(blob);
						link.download = result.filename;
						link.click();
					} else {
						alert("엑셀 생성 오류: " + result.message);
					}
				} catch (error) {
					console.error(error);
					alert("다운로드 중 오류가 발생했습니다.");
				}
			});
		</script>
	</body>
</html>
