<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>이미지 업로드</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/common.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}
    <div class="container mt-4">
        <h4>이미지 업로드</h4>
        <form action="/link5" method="POST" enctype="multipart/form-data">
            <div class="mb-3">
                <input class="form-control" type="file" name="files" accept="image/*" multiple required>
            </div>
            <button type="submit" class="btn btn-primary">업로드</button>
        </form>
        {% if message %}
            <div class="alert alert-info mt-3">{{ message }}</div>
        {% endif %}
        {% if ocr_results %}
            <div class="mt-4">
                <h5>OCR 추출 결과</h5>
                {% for result in ocr_results %}
                    <div class="card mb-3">
                        <div class="card-header">{{ result.filename }}</div>
                        <div class="card-body">
                            <pre style="white-space: pre-wrap;">{{ result.text }}</pre>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>