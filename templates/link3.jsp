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
		<form class = "grid" action = "/design_generate" method = "POST" enctype="multipart/form-data">
			<table>
				<tr>
					<td style="width: 150px;">회사 이름</td>
					<td style="width: 1000px;"><input type="text" id="param1" name="param1" required></td>
				</tr>
				<tr>
					<td>이메일 주소</td>
					<td><input type="text" id="param2" name="param2" required></td>
				</tr>
				<tr>
					<td>요청 내용</td>
					<td><textarea name="param3" id="param3" rows="10"></textarea></td>
				</tr>
				<tr>
					<td><input type="file" id="param4" name="param4"></td>
					<td><input type="Submit" value="검토요청하기" formaction="/paper_request"></td>
				</tr>
				<!--
				<tr>
					<td colspan="2">파일 업로드에 어려움이 있는 경우 newsist@naver.com으로 보내주세요</td>
				</tr>
				-->
				{% if return_code == 1 %}
                <tr>
                    <td colspan="2" style="color: red;">업로드 실패</td>
                </tr>
                {% endif %}
                {% if return_code == 2 %}
                <tr>
                    <td colspan="2">검토 요청이 완료되었습니다.<br>내용 확인 후 등록하신 이메일 주소로 회신합니다.</td>
                </tr>
                {% endif %}
			</table>
		</form>
	</body>
</html>