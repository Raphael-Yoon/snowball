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