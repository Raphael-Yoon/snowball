<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    {% include 'navi.jsp' %}
    <div style="text-align: center;">
        <img src="{{ url_for('static', filename='img/snowball.jpg')}}" class="responsive-image" alt="None">
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
    </div>
</body>
</html>