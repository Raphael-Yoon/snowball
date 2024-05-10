<!DOCTYPE html>
<html>
	<head>
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
		<title>SnowBall</title>
	</head>
	<body>
		<form class = "grid" action = "/register_request" method = "POST" enctype="multipart/form-data">
			<table>
				<tr>
					<td style="width: 150px;">회사명</td>
					<td style="width: 600px;"><input type="text" id="param1" name="param1"></td>
				</tr>
				<tr>
					<td>담당자이름</td>
					<td><input type="text" id="param2" name="param2"></td>
				</tr>
                <tr>
					<td>e-Mail</td>
					<td><input type="text" id="param3" name="param3"></td>
				</tr>
				<tr>
					<td><input type="Submit" value="등록신청"></td>
				</tr>
			</table>
		</form>
	</body>
</html>