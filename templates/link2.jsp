<!DOCTYPE html>
<html>
	<head>
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
		<title>SnowBall</title>
	</head>
	<body>
		{% include 'navi.jsp' %}
		<form class = "grid" action = "/design_generate" method = "POST" enctype="multipart/form-data">
			<table>
				<tr>
					<td style="width: 150px;">회사 이름</td>
					<td style="width: 600px;"><input type="text" id="param1" name="param1" required></td>
				</tr>
				<tr>
					<td>시스템 이름</td>
					<td><input type="text" id="param2" name="param2" required></td>
				</tr>
				<tr>
					<td><input type="Submit" value="Template Download" formaction="/design_template_download"></td>
				</tr>
				<tr>
					<td><p>파일 Upload하고 검토 요청하기</p></td>
				</tr>
				<tr>
					<td><input type="file" id="param3" name="param3"></td>
					<td><input type="Submit" value="Generate" formaction="/design_generate"></td>
				</tr>
			</table>
		</form>
	</body>
</html>