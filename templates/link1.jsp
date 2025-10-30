<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>SnowBall</title>
		<!-- Favicon -->
		<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
		<link rel="shortcut icon" type="image/x-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
		<link rel="apple-touch-icon" href="{{ url_for('static', filename='img/favicon.ico') }}">
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
		<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
	</head>
	<body>
		{% include 'navi.jsp' %}
		<div class="form-container">
			<h1 class="section-title">
				<i class="fas fa-file-alt"></i> ITGC RCM Builder
			</h1>
			<div class="card">
				<div class="card-body">
					<form action="/rcm_generate" method="POST">
						<div class="mb-4">
							<label class="form-label">e-Mail 주소</label>
							<input type="email" class="form-control{% if is_logged_in %} bg-light{% endif %}" id="param1" name="param1" required placeholder="e-Mail 주소를 입력하세요" value="{{ user_email }}" {% if is_logged_in %}readonly{% endif %}>
							{% if is_logged_in %}
							<small class="form-text text-muted">
								<i class="fas fa-lock me-1"></i>로그인된 계정의 이메일이 자동으로 사용됩니다.
							</small>
							{% endif %}
						</div>
						{#
						<div class="mb-4">
							<label class="form-label">담당자</label>
							<select class="form-control" id="param1" name="param1" required>
								<option value="">담당자를 선택하세요</option>
								{% for i in range(0, users|length, 3) %}
									<option value="{{ users[i+2] }}">{{ users[i] }} - {{ users[i+1] }}</option>
								{% endfor %}
							</select>
						</div>
						#}
						<div class="mb-4">
							<label class="form-label">시스템명</label>
							<input type="text" class="form-control" id="param2" name="param2" required placeholder="시스템명을 입력하세요">
						</div>
						<div class="mb-4">
							<label class="form-label">Cloud</label>
							<div class="radio-group">
								<div class="radio-option">
									<input type="radio" id="cloud_onprem" name="param_cloud" value="ON-PREMISE" checked>
									<label for="cloud_onprem">On-Premise</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="cloud_saas" name="param_cloud" value="SAAS">
									<label for="cloud_saas">SaaS</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="cloud_paas" name="param_cloud" value="PAAS">
									<label for="cloud_paas">PaaS</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="cloud_iaas" name="param_cloud" value="IAAS">
									<label for="cloud_iaas">IaaS</label>
								</div>
							</div>
						</div>
						<div class="mb-4">
							<label class="form-label">System</label>
							<div class="radio-group">
								<div class="radio-option">
									<input type="radio" id="select11" name="param3" value="SAP" checked>
									<label for="select11">SAP</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select12" name="param3" value="ORACLE">
									<label for="select12">Oracle</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select13" name="param3" value="DOUZONE">
									<label for="select13">더존</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select14" name="param3" value="YOUNG">
									<label for="select14">영림원</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select15" name="param3" value="ETC">
									<label for="select15">기타</label>
								</div>
							</div>
						</div>
						<div class="mb-4">
							<label class="form-label">OS</label>

							<!-- OS 접근제어 Tool (Toggle Switch) - On-Premise일 때만 표시 -->
							<div class="mb-3" id="os-tool-section" style="display: none;">
								<div class="d-flex justify-content-between align-items-center p-3 border rounded bg-light">
									<label for="os_tool_switch" class="mb-0">
										<i class="fas fa-shield-alt me-2 text-primary"></i>OS 접근제어 Tool 사용
									</label>
									<div class="form-check form-switch mb-0">
										<input class="form-check-input" type="checkbox" id="os_tool_switch" name="use_os_tool" value="Y" role="switch">
									</div>
								</div>
							</div>

							<div class="radio-group">
								<div class="radio-option">
									<input type="radio" id="select21" name="param4" value="UNIX" class="os-main-option" checked>
									<label for="select21">Unix</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select22" name="param4" value="WINDOWS" class="os-main-option">
									<label for="select22">Windows</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select23" name="param4" value="LINUX" class="os-main-option">
									<label for="select23">Linux</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select24" name="param4" value="ETC" class="os-main-option">
									<label for="select24">기타</label>
								</div>
							</div>

							<!-- Linux 세부 선택 (동적으로 표시) -->
							<div id="linux-detail" class="ms-4 mt-3" style="display: none;">
								<label class="form-label text-muted">
									<i class="fas fa-chevron-right me-2"></i>Linux 배포판 선택
								</label>
								<div class="radio-group">
									<div class="radio-option">
										<input type="radio" id="linux_ubuntu" name="param4_detail" value="LINUX_UBUNTU">
										<label for="linux_ubuntu">Ubuntu/Debian 계열</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="linux_centos" name="param4_detail" value="LINUX_CENTOS">
										<label for="linux_centos">CentOS/RHEL 계열</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="linux_etc" name="param4_detail" value="LINUX_ETC">
										<label for="linux_etc">기타 Linux</label>
									</div>
								</div>
							</div>

							<!-- Unix 세부 선택 (동적으로 표시) -->
							<div id="unix-detail" class="ms-4 mt-3" style="display: none;">
								<label class="form-label text-muted">
									<i class="fas fa-chevron-right me-2"></i>Unix 종류 선택
								</label>
								<div class="radio-group">
									<div class="radio-option">
										<input type="radio" id="unix_aix" name="param4_detail" value="UNIX_AIX">
										<label for="unix_aix">AIX</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="unix_hpux" name="param4_detail" value="UNIX_HPUX">
										<label for="unix_hpux">HP-UX</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="unix_solaris" name="param4_detail" value="UNIX_SOLARIS">
										<label for="unix_solaris">Solaris</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="unix_etc" name="param4_detail" value="UNIX_ETC">
										<label for="unix_etc">기타 Unix</label>
									</div>
								</div>
							</div>

							<!-- Windows 세부 선택 (동적으로 표시) -->
							<div id="windows-detail" class="ms-4 mt-3" style="display: none;">
								<label class="form-label text-muted">
									<i class="fas fa-chevron-right me-2"></i>Windows 버전 선택
								</label>
								<div class="radio-group">
									<div class="radio-option">
										<input type="radio" id="win_2016plus" name="param4_detail" value="WINDOWS_2016PLUS">
										<label for="win_2016plus">Windows Server 2016+</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="win_legacy" name="param4_detail" value="WINDOWS_LEGACY">
										<label for="win_legacy">Windows Server 2012 이하</label>
									</div>
								</div>
							</div>
						</div>
						<div class="mb-4">
							<label class="form-label">DB</label>

							<!-- DB 접근제어 Tool (Toggle Switch) - On-Premise일 때만 표시 -->
							<div class="mb-3" id="db-tool-section" style="display: none;">
								<div class="d-flex justify-content-between align-items-center p-3 border rounded bg-light">
									<label for="db_tool_switch" class="mb-0">
										<i class="fas fa-shield-alt me-2 text-primary"></i>DB 접근제어 Tool 사용
									</label>
									<div class="form-check form-switch mb-0">
										<input class="form-check-input" type="checkbox" id="db_tool_switch" name="use_db_tool" value="Y" role="switch">
									</div>
								</div>
							</div>

							<div class="radio-group">
								<div class="radio-option">
									<input type="radio" id="select31" name="param5" value="ORACLE" class="db-main-option" checked>
									<label for="select31">Oracle</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select32" name="param5" value="MSSQL" class="db-main-option">
									<label for="select32">MS-SQL</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select33" name="param5" value="MYSQL" class="db-main-option">
									<label for="select33">MySQL</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select34" name="param5" value="ETC" class="db-main-option">
									<label for="select34">기타</label>
								</div>
							</div>

							<!-- Oracle DB 세부 선택 (동적으로 표시) -->
							<div id="oracle-db-detail" class="ms-4 mt-3" style="display: none;">
								<label class="form-label text-muted">
									<i class="fas fa-chevron-right me-2"></i>Oracle 버전 선택
								</label>
								<div class="radio-group">
									<div class="radio-option">
										<input type="radio" id="oracle_19c" name="param5_detail" value="ORACLE_19C">
										<label for="oracle_19c">Oracle 19c 이상</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="oracle_12c" name="param5_detail" value="ORACLE_12C">
										<label for="oracle_12c">Oracle 12c</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="oracle_11g" name="param5_detail" value="ORACLE_11G">
										<label for="oracle_11g">Oracle 11g 이하</label>
									</div>
								</div>
							</div>

							<!-- MySQL 세부 선택 (동적으로 표시) -->
							<div id="mysql-detail" class="ms-4 mt-3" style="display: none;">
								<label class="form-label text-muted">
									<i class="fas fa-chevron-right me-2"></i>MySQL 종류 선택
								</label>
								<div class="radio-group">
									<div class="radio-option">
										<input type="radio" id="mysql_mysql" name="param5_detail" value="MYSQL_MYSQL">
										<label for="mysql_mysql">MySQL</label>
									</div>
									<div class="radio-option">
										<input type="radio" id="mysql_mariadb" name="param5_detail" value="MYSQL_MARIADB">
										<label for="mysql_mariadb">MariaDB</label>
									</div>
								</div>
							</div>
						</div>

						<!-- <button type="submit" class="submit-btn" onclick="event.preventDefault(); alert('더 좋은 서비스를 위해 공사중입니다');"> -->
						<button type="submit" class="submit-btn">
							<i class="fas fa-envelope"></i> 메일로 보내기
						</button>
					</form>
				</div>
			</div>
		</div>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
		
		<!-- 세션 관리 -->
		<script>
			window.isLoggedIn = {{ 'true' if is_logged_in else 'false' }};
		</script>
		<!-- <script src="{{ url_for('static', filename='js/session-manager.js') }}"></script> -->

		<!-- 동적 선택 스크립트 (Cloud, System, OS, DB) -->
		<script>
			document.addEventListener('DOMContentLoaded', function() {
				// ===== Cloud 선택에 따른 Tool 섹션 표시/숨김 =====
				const cloudOptions = document.querySelectorAll('input[name="param_cloud"]');
				const osToolSection = document.getElementById('os-tool-section');
				const dbToolSection = document.getElementById('db-tool-section');

				// 초기 상태: On-Premise가 기본 선택이므로 Tool 섹션 표시
				if (document.getElementById('cloud_onprem').checked) {
					osToolSection.style.display = 'block';
					dbToolSection.style.display = 'block';
				}

				cloudOptions.forEach(option => {
					option.addEventListener('change', function() {
						if (this.value === 'ON-PREMISE') {
							// On-Premise 선택 시: Tool 섹션 표시
							osToolSection.style.display = 'block';
							dbToolSection.style.display = 'block';
						} else {
							// Cloud 서비스(SaaS/PaaS/IaaS) 선택 시: Tool 섹션 숨김
							osToolSection.style.display = 'none';
							dbToolSection.style.display = 'none';
							// 체크박스도 해제
							document.getElementById('os_tool_switch').checked = false;
							document.getElementById('db_tool_switch').checked = false;
						}
					});
				});

				// ===== System 동적 선택 =====
				const systemOptions = document.querySelectorAll('.system-main-option');
				const sapDetail = document.getElementById('sap-detail');
				const oracleDetail = document.getElementById('oracle-detail');
				const douzoneDetail = document.getElementById('douzone-detail');

				// 초기 상태: SAP가 기본 선택이므로 SAP 세부 선택 표시
				sapDetail.style.display = 'block';
				document.getElementById('sap_ecc').checked = true;

				systemOptions.forEach(option => {
					option.addEventListener('change', function() {
						// 모든 세부 선택 숨김
						sapDetail.style.display = 'none';
						oracleDetail.style.display = 'none';
						douzoneDetail.style.display = 'none';

						const selectedValue = this.value;
						if (selectedValue === 'SAP') {
							sapDetail.style.display = 'block';
							document.getElementById('sap_ecc').checked = true;
						} else if (selectedValue === 'ORACLE') {
							oracleDetail.style.display = 'block';
							document.getElementById('oracle_ebs').checked = true;
						} else if (selectedValue === 'DOUZONE') {
							douzoneDetail.style.display = 'block';
							document.getElementById('douzone_icube').checked = true;
						}
					});
				});

				// ===== OS 동적 선택 =====
				const osOptions = document.querySelectorAll('.os-main-option');
				const linuxDetail = document.getElementById('linux-detail');
				const unixDetail = document.getElementById('unix-detail');
				const windowsDetail = document.getElementById('windows-detail');

				// 초기 상태: Unix가 기본 선택이므로 Unix 세부 선택 표시
				unixDetail.style.display = 'block';
				document.getElementById('unix_aix').checked = true;

				osOptions.forEach(option => {
					option.addEventListener('change', function() {
						linuxDetail.style.display = 'none';
						unixDetail.style.display = 'none';
						windowsDetail.style.display = 'none';

						const selectedValue = this.value;
						if (selectedValue === 'LINUX') {
							linuxDetail.style.display = 'block';
							document.getElementById('linux_ubuntu').checked = true;
						} else if (selectedValue === 'UNIX') {
							unixDetail.style.display = 'block';
							document.getElementById('unix_aix').checked = true;
						} else if (selectedValue === 'WINDOWS') {
							windowsDetail.style.display = 'block';
							document.getElementById('win_2016plus').checked = true;
						}
					});
				});

				// ===== DB 동적 선택 =====
				const dbOptions = document.querySelectorAll('.db-main-option');
				const oracleDbDetail = document.getElementById('oracle-db-detail');
				const mysqlDetail = document.getElementById('mysql-detail');

				// 초기 상태: Oracle DB가 기본 선택이므로 Oracle 세부 선택 표시
				oracleDbDetail.style.display = 'block';
				document.getElementById('oracle_19c').checked = true;

				dbOptions.forEach(option => {
					option.addEventListener('change', function() {
						oracleDbDetail.style.display = 'none';
						mysqlDetail.style.display = 'none';

						const selectedValue = this.value;
						if (selectedValue === 'ORACLE') {
							oracleDbDetail.style.display = 'block';
							document.getElementById('oracle_19c').checked = true;
						} else if (selectedValue === 'MYSQL') {
							mysqlDetail.style.display = 'block';
							document.getElementById('mysql_mysql').checked = true;
						}
					});
				});

				// ===== 폼 제출 시 세부 선택 값 병합 =====
				document.querySelector('form').addEventListener('submit', function(e) {
					// System 세부 선택 처리
					const detailSystem = document.querySelector('input[name="param3_detail"]:checked');
					if (detailSystem && detailSystem.value) {
						const hiddenInput = document.createElement('input');
						hiddenInput.type = 'hidden';
						hiddenInput.name = 'param3';
						hiddenInput.value = detailSystem.value;
						this.appendChild(hiddenInput);
						document.querySelector('input[name="param3"]:checked').disabled = true;
					}

					// OS 세부 선택 처리
					const detailOs = document.querySelector('input[name="param4_detail"]:checked');
					if (detailOs && detailOs.value) {
						const hiddenInput = document.createElement('input');
						hiddenInput.type = 'hidden';
						hiddenInput.name = 'param4';
						hiddenInput.value = detailOs.value;
						this.appendChild(hiddenInput);
						document.querySelector('input[name="param4"]:checked').disabled = true;
					}

					// DB 세부 선택 처리
					const detailDb = document.querySelector('input[name="param5_detail"]:checked');
					if (detailDb && detailDb.value) {
						const hiddenInput = document.createElement('input');
						hiddenInput.type = 'hidden';
						hiddenInput.name = 'param5';
						hiddenInput.value = detailDb.value;
						this.appendChild(hiddenInput);
						document.querySelector('input[name="param5"]:checked').disabled = true;
					}
				});
			});
		</script>

	</body>
</html>