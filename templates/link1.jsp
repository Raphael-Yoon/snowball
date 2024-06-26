<!DOCTYPE html>
<html>
	<head>
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
		<title>SnowBall</title>
	</head>
	<body>
		{% include 'navi.jsp' %}
		<form class = "grid" action = "/rcm_generate" method = "POST">
			<table>
				<tr>
					<td style="width: 150px;">회사명</td>
					<td style="width: 600px;"><input type="text" id="param1" name="param1"></td>
					<td rowspan="7"><img src="{{ url_for('static', filename='img/rcm.jpg')}}" width="300" alt="None"></td>
				</tr>
				<tr>
					<td>시스템명</td>
					<td><input type="text" id="param2" name="param2"></td>
				</tr>
				<tr>
					<td>System</td>
					<td>
						<div class="select">
							<input type="radio" id="select11" name="param3" value="SAP" checked><label for="select11">SAP</label>
							<input type="radio" id="select12" name="param3" value="Oracle"><label for="select12">Oracle</label>
							<input type="radio" id="select13" name="param3" value="Douzone"><label for="select13">더존</label>
							<input type="radio" id="select14" name="param3" value="KSystem"><label for="select14">영림원</label>
							<input type="radio" id="select15" name="param3" value="ETC"><label for="select15">기타</label>
						</div>
					</td>
				</tr>
				<tr>
					<td>OS</td>
					<td>
						<div class="select">
							<input type="radio" id="select21" name="param4" value="Unix" checked><label for="select21">Unix</label>
							<input type="radio" id="select22" name="param4" value="Windows"><label for="select22">Windows</label>
							<input type="radio" id="select23" name="param4" value="Linux"><label for="select23">Linux</label>
							<input type="radio" id="select24" name="param4" value="ETC"><label for="select24">기타</label>
						</div>
					</td>
				</tr>
				<tr>
					<td>DB</td>
					<td>
						<div class="select">
							<input type="radio" id="select31" name="param5" value="Oracle" checked><label for="select31">Oracle</label>
							<input type="radio" id="select32" name="param5" value="MSSQL"><label for="select32">MS-SQL</label>
							<input type="radio" id="select33" name="param5" value="ETC"><label for="select33">기타</label>
						</div>
					</td>
				</tr>
				<tr>
					<td><input class="file_submit" type="Submit" value="Download"></td>
				</tr>
			</table>
		</form>
		<br>
		<hr style="width: 100%; margin: 0 auto;">
		<br>
		<form class = "grid" action = "/rcm_request" method="post" enctype="multipart/form-data">
			<table>
				<tr>
					<td colspan="2"><p>RCM Upload하고 검토 요청하기</p></td>
				</tr>
				<tr>
					<td style="width: 150px;">회사명</td>
					<td style="width: 600px;"><input type="text" id="param1" name="param1"></td>
				</tr>
				<tr>
					<td style="width: 150px;">회신 이메일주소</td>
					<td style="width: 600px;"><input type="email" id="param2" name="param2"></td>
				</tr>
				<tr>
					<td><input type="file" id="param3" name="param3"></td>
					<td><input type="submit" value="Request"></td>
				</tr>
				{% if return_code == 1 %}
				<tr>
					<td><p>검토 요청이 완료되었습니다.<br>확인 후 회신 드리겠습니다</p></td>
				</tr>
				{% endif %}
			</table>
		</form>
		<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
	</body>
</html>