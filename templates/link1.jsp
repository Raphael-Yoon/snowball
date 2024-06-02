<!DOCTYPE html>
<html>
	<head>
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
		<title>SnowBall</title>
	</head>
	<body>
		{% include 'navi.jsp' %}
		<form class = "grid" action = "/pbc_generate" method = "POST">
			<table>
				<tr>
					<td style="width: 150px;">클라이언트명</td>
					<td style="width: 600px;"><input type="text" id="param1" name="param1"></td>
					<td rowspan="7"><img src="{{ url_for('static', filename='img/RCM.jpg')}}" width="300" alt="None"></td>
				</tr>
				<tr>
					<td>시스템명</td>
					<td><input type="text" id="param2" name="param2"></td>
				</tr>
				<tr>
					<td>System</td>
					<td>
						<div class="select">
							<input type="radio" id="select11" name="param4" value="SAP" checked><label for="select11">SAP</label>
							<input type="radio" id="select12" name="param4" value="Oracle"><label for="select12">Oracle</label>
							<input type="radio" id="select13" name="param4" value="Douzone"><label for="select13">더존</label>
							<input type="radio" id="select14" name="param4" value="KSystem"><label for="select14">영림원</label>
							<input type="radio" id="select15" name="param4" value="ETC"><label for="select15">기타</label>
						</div>
					</td>
				</tr>
				<tr>
					<td>OS</td>
					<td>
						<div class="select">
							<input type="radio" id="select21" name="param5" value="Unix" checked><label for="select21">Unix</label>
							<input type="radio" id="select22" name="param5" value="Windows"><label for="select22">Windows</label>
							<input type="radio" id="select23" name="param5" value="Linux"><label for="select23">Linux</label>
							<input type="radio" id="select24" name="param5" value="ETC"><label for="select24">기타</label>
						</div>
					</td>
				</tr>
				<tr>
					<td>DB</td>
					<td>
						<div class="select">
							<input type="radio" id="select31" name="param6" value="Oracle" checked><label for="select31">Oracle</label>
							<input type="radio" id="select32" name="param6" value="MSSQL"><label for="select32">MS-SQL</label>
							<input type="radio" id="select33" name="param6" value="ETC"><label for="select33">기타</label>
						</div>
					</td>
				</tr>
				<tr>
					<td><input class="file_submit" type="Submit" value="Download"></td>
				</tr>
			</table>
		</form>
		<form class = "grid" action = "/rcm_request" method="post" enctype="multipart/form-data">
			<div id="contentContainer">
				<p>파일 Upload하고 검토 요청하기</p>
				<input type="file" id="param4" name="param4">
				<input type="submit" value="Request">
			</div>
		</form>
	</body>
</html>