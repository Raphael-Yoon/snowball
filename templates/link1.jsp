<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
		<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<title>SnowBall</title>
	</head>
	<body>
		{% include 'navi.jsp' %}
		<div class="form-container">
			<h1 class="section-title">
				<i class="fas fa-file-alt"></i> ITGC RCM 자동 생성
			</h1>
			<div class="card">
				<div class="card-body">
					<form action="/rcm_generate" method="POST">
						<div class="mb-4">
							<label class="form-label">e-Mail 주소</label>
							<input type="email" class="form-control" id="param1" name="param1" required placeholder="e-Mail 주소를 입력하세요">
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
							<div class="radio-group">
								<div class="radio-option">
									<input type="radio" id="select21" name="param4" value="UNIX" checked>
									<label for="select21">Unix</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select22" name="param4" value="WINDOWS">
									<label for="select22">Windows</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select23" name="param4" value="LINUX">
									<label for="select23">Linux</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select24" name="param4" value="ETC">
									<label for="select24">기타</label>
								</div>
							</div>
						</div>
						<div class="mb-4">
							<label class="form-label">DB</label>
							<div class="radio-group">
								<div class="radio-option">
									<input type="radio" id="select31" name="param5" value="ORACLE" checked>
									<label for="select31">Oracle</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select32" name="param5" value="MSSQL">
									<label for="select32">MS-SQL</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select33" name="param5" value="MYSQL">
									<label for="select33">MY-SQL</label>
								</div>
								<div class="radio-option">
									<input type="radio" id="select34" name="param5" value="ETC">
									<label for="select34">기타</label>
								</div>
							</div>
						</div>
						<!-- <button type="submit" class="submit-btn" onclick="event.preventDefault(); alert('더 좋은 서비스를 위해 공사중입니다');"> -->
						<button type="submit" class="submit-btn";">
							<i class="fas fa-download"></i> Download
						</button>
					</form>
				</div>
			</div>
		</div>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
	</body>
</html>