<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    <form class = "grid" action = "/login" method = "POST" enctype="multipart/form-data">
        <div style="text-align: center;">
            <table style="margin: 0 auto;">
                <tr>
                    <td colspan="2"><img src="{{ url_for('static', filename='img/snowball.jpg')}}" class="responsive-image" alt="None"></td>
                </tr>
                <tr>
                    <td style="width: 150px;">회사명</td>
                    <td style="width: 150px;">
                        <select name="param1" id="param1">
                            {% for item in user_name %}
                                <option>{{ item }}</option>
                            {% endfor %}
                        </select>
                    </td>
                </tr>
                <tr>
                    <td>인증코드</td>
                    <td><input type="text" id="param2" name="param2" required></td>
                </tr>
                <tr>
					<td colspan="2"><input type="Submit" value="Login" formaction="/login"></td>
				</tr>
                {% if error_code == 1 %}
                <tr>
                    <td colspan="2" style="color: red;">로그인 실패</td>
                </tr>
                {% endif %}
            </table>
        </div>
    </form>
</body>
</html>

<script>
    function adjustImageSize(){
        var width = window.innerWidth || document.querySelector('.responsive-image');
        var image = document.querySelector('.responsive-image');
        if(width < 400){
            image.style.maxWidth = width + 'px';
        }
        else{
            image.style.maxWidth = '400px';
        }
    }
    window.addEventListener('resize', adjustImageSize);
    window.onload = adjustImageSize;
</script>