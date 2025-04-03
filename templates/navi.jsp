<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SnowBall Navigation</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .navbar {
            background-color: #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
        .logo {
            max-width: 200px;
            height: auto;
            transition: transform 0.3s ease;
        }
        .logo:hover {
            transform: scale(1.05);
        }
        .nav-link {
            color: #2c3e50;
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: color 0.3s ease;
        }
        .nav-link:hover {
            color: #3498db;
        }
        .nav-item {
            margin: 0 0.5rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="{{ url_for('static', filename='img/logo.jpg')}}" class="logo" alt="SnowBall Logo">
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
                            <a href="/link2" class="nav-link">
                                <i class="fas fa-user-tie me-1"></i>Interview
                            </a>
                        </form>
                    </li>
                    <li class="nav-item">
                        <form action="/link3" method="POST" class="d-inline">
                            <a href="/link3" class="nav-link">
                                <i class="fas fa-comments me-1"></i>Review
                            </a>
                        </form>
                    </li>
                    <li class="nav-item">
                        <form action="/link4" method="POST" class="d-inline">
                            <a href="/link4" class="nav-link">
                                <i class="fas fa-film me-1"></i>Movie
                            </a>
                        </form>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>