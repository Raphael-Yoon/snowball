<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    <form class = "grid" method = "POST" enctype="multipart/form-data">
        <div style="text-align: center;">
            <table style="margin: 0 auto;">
                <tr>
                    <td colspan="2"><img src="{{ url_for('static', filename='img/snowball.jpg')}}" class="responsive-image" alt="None"></td>
                </tr>
                <tr>
                    <td style="width: 150px;">회사명</td>
                    <td style="width: 150px;">
                        <select name="param1" id="param1" style="width: 100%;">
                            {% for item in user_name %}
                                <option>{{ item }}</option>
                            {% endfor %}
                        </select>
                    </td>
                </tr>
                <tr>
                    <td>인증코드</td>
                    <td><input type="password" id="param2" name="param2" style="width: 100%;"></td>
                </tr>
                <tr>
                    <td><input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login"></td>
                    <td><input type="Submit" class="btn btn-outline-primary" value="등록하기" formaction="/register"></td>
				</tr>
                {% if return_code == 1 %}
                <tr>
                    <td colspan="2" style="color: red;">로그인 실패</td>
                </tr>
                {% endif %}
                {% if return_code == 2 %}
                <tr>
                    <td colspan="2">사용 신청이 완료되었습니다.<br>관리자 확인 후 등록됩니다</td>
                </tr>
                {% endif %}
            </table>
        </div>
    </form>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
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