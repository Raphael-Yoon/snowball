<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - SnowBall</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}
    <div class="container py-5">
        <div class="row">
            <div class="col-md-6 d-flex align-items-center justify-content-center" style="border-right:1px solid #eee; min-height:400px;">
                <div>
                    <h2 class="mb-4 text-primary"><i class="fas fa-snowflake me-2"></i>SnowBall 소개</h2>
                    <p style="font-size:1.1rem;">
                        SnowBall은 내부통제 평가와 IT감사 대응을 전문적으로 하고 있습니다.<br><br>
                        <b>주요 분야</b><br>
                        - ITGC RCM 구축<br>
                        - ITGC 설계 및 운영평가(PA)<br>
                        - ITGC 설명 및 교육<br>
                        - IT감사 대응<br>
                        - 회사 RCM에 맞춘 자동화 시스템 구축<br><br>
                        SnowBall은 기업의 IT 리스크를 최소화하고, 효율적인 내부통제 환경을 구축할 수 있도록 지원합니다.
                    </p>
                </div>
            </div>
            <div class="col-md-6">
                <h2 class="mb-4 text-center"><i class="fas fa-envelope me-2"></i>Contact Us</h2>
                {% if success is defined and success %}
                    <div class="alert alert-success text-center">문의가 성공적으로 접수되었습니다. 빠른 시일 내에 답변드리겠습니다.</div>
                {% elif success is defined and not success %}
                    <div class="alert alert-danger text-center">문의 접수에 실패했습니다.<br>{{ error }}</div>
                {% endif %}
                <form method="post" action="/contact" class="mx-auto" style="max-width: 400px;">
                    <div class="mb-3">
                        <label for="name" class="form-label">이름</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">이메일</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="message" class="form-label">문의 내용</label>
                        <textarea class="form-control" id="message" name="message" rows="6" required></textarea>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary btn-lg"><i class="fas fa-paper-plane me-1"></i>문의하기</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>