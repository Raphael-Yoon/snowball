<!DOCTYPE html>
<html>
	<head>
		<!-- Bootstrap CSS 불러오기 -->
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet" />
		<title>SnowBall Quiz</title>
	</head>
	<body>
		<!-- 네비게이션 포함 -->
		{% include 'navi.jsp' %}

		<div class="container mt-5">
			<h1>OX 퀴즈</h1>
			
			<!-- 퀴즈 폼 시작 -->
			<form action="/link2" method="post">
				<div class="mb-3">
					<label>{{ question_number }}. {{ question }}</label><br>
					<input type="radio" name="answer" value="O" required> O
					<input type="radio" name="answer" value="X"> X
				</div>

				<!-- 다음 버튼 -->
				<button type="submit" class="btn btn-primary">다음</button>
			</form>
		</div>
	</body>
</html>
