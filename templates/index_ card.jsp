<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    <div class="container text-center">
        <div class="row">
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/pwc.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">PwC</h5>
                            <input type="hidden" id="param1" name="param1" value="snowball">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/nepes.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">네패스</h5>
                            <input type="hidden" id="param1" name="param1" value="nepes">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/doosan.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">두산</h5>
                            <input type="hidden" id="param1" name="param1" value="doosan">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/celltrion.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">celltrion</h5>
                            <input type="hidden" id="param1" name="param1" value="celltrion">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/asiana_airlines.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">아시아나항공</h5>
                            <input type="text" id="param1" name="param1" value="asiana_airlines">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/air_busan.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">에어부산</h5>
                            <input type="hidden" id="param1" name="param1" value="air_busan">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/ecopro.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">에코프로</h5>
                            <input type="hidden" id="param1" name="param1" value="eco_pro">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/hanwha_ocean.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">한화오션</h5>
                            <input type="hidden" id="param1" name="param1" value="hanwha_ocean">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <div class="card" style="width: 18rem;">
                    <form class = "grid" method = "POST" action="/login" enctype="multipart/form-data">
                        <img src="{{ url_for('static', filename='img/lig_nex1.jpg')}}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">LIG넥스원</h5>
                            <input type="hidden" id="param1" name="param1" value="asiana_airlines">
                            인증코드 <input type="password" id="param2" name="param2" style="width: 63%;">
                            <input type="Submit" class="btn btn-outline-primary" value="들어가기" formaction="/login">
                        </div>
                    </form>
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                </div>
            </div>
            <div class="col">
                <div class="card" style="width: 18rem;">
                </div>
            </div>
        </div>
    </div>

    <!--
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
    -->

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