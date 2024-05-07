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
					<td style="width: 150px;">클라이언트명</td>
					<td style="width: 600px;"><input type="text" id="param1" name="param1" required></td>
				</tr>
				<tr>
					<td>시스템명</td>
					<td><input type="text" id="param2" name="param2" required></td>
				</tr>
				<tr>
					<td><input type="Submit" value="Template Download" formaction="/design_template_download"></td>
				</tr>
				<tr>
					<td><input type="file" id="param3" name="param3"></td>
					<td><input type="Submit" value="Generate" formaction="/design_generate"></td>
				</tr>
			</table>
		</form>
	</body>
</html>