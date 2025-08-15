<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall Navigation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="{{ url_for('static', filename='img/logo.jpg')}}" class="logo" alt="SnowBall Logo" style="max-height: 40px; width: auto;">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <form action="/link1" method="POST" class="d-inline">
                            <a href="/link1" class="nav-link">
                                <i class="fas fa-clipboard-list me-1"></i>RCM
                            </a>
                        </form>
                    </li>
                    <li class="nav-item">
                        <form action="/link2" method="POST" class="d-inline">
                            <a href="/link2?reset=1" class="nav-link">
                                <i class="fas fa-user-tie me-1"></i>Interview
                            </a>
                        </form>
                    </li>
                    <li class="nav-item">
                        <form action="/link3" method="POST" class="d-inline">
                            <a href="/link3" class="nav-link">
                                <i class="fas fa-cogs me-1"></i>Operation
                            </a>
                        </form>
                    </li>
                    <li class="nav-item">
                        <form action="/link4" method="POST" class="d-inline">
                            <a href="/link4" class="nav-link">
                                <i class="fas fa-film me-1"></i>Video
                            </a>
                        </form>
                    </li>
                    {% if remote_addr == '127.0.0.1' or request.host == 'snowball.pythonanywhere.com' %}
                    <li class="nav-item">
                        <a href="/link5" class="nav-link">
                            <i class="fas fa-robot me-1"></i>AI
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/link6" class="nav-link">
                            <i class="fas fa-robot me-1"></i>AI+
                        </a>
                    </li>
                    {% endif %}
                    <li class="nav-item" style="display: none;">
                        <a href="/contact" class="nav-link">
                            <i class="fas fa-envelope me-1"></i>Contact Us
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>