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
					<td style="width: 150px;">자가평가</td>
				</tr>
			</table>
		</form>
	</body>
</html>