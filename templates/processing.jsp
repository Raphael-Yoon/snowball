<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>작업 진행 중</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container text-center mt-5">
        <div class="spinner-border text-primary mb-4" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        
        <h2 class="mb-4">AI 검토 및 문서 생성 중입니다</h2>
        
        <div class="processing-message">
            <p>인터뷰 내용을 분석하고 ITGC 설계평가 문서를 생성하고 있습니다.</p>
            <p class="text-muted">완료되면 <strong>{{ user_email }}</strong>로 결과를 전송해 드리겠습니다.</p>
        </div>
        
        <div class="progress-container">
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" 
                     style="width: 100%">
                </div>
            </div>
        </div>
        
        <div class="alert alert-info mt-4">
            <strong>잠시만 기다려 주세요.</strong><br>
            처리 시간은 인터뷰 내용에 따라 다를 수 있습니다.<br>
            화면을 닫지 마세요. 화면을 닫을 경우 메일 전송이 안될 수 있습니다.
        </div>
        
        <a href="/" class="btn btn-primary mt-3" id="mainPageBtn" style="display: none;">메인으로 이동</a>
    </div>

    <script>
        // 페이지 로드 후 자동으로 작업 시작
        document.addEventListener('DOMContentLoaded', function() {
            // 실제 작업을 시작하는 AJAX 요청
            fetch('/process_interview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 성공 시 메시지 업데이트
                    document.querySelector('h2').innerHTML = 'AI 검토 및 문서 생성이 완료되었습니다';
                    document.querySelector('.processing-message').innerHTML = 
                        '<p class="text-success"><strong>ITGC 설계평가 문서가 성공적으로 생성되어 메일로 전송되었습니다!</strong></p>' +
                        '<p>메일함을 확인해 주세요.</p>';
                    document.querySelector('.spinner-border').style.display = 'none';
                    document.querySelector('.progress-container').style.display = 'none';
                    document.querySelector('.alert').style.display = 'none';
                    // AI 검토 완료 후 메인으로 이동 버튼 표시
                    document.getElementById('mainPageBtn').style.display = 'inline-block';
                } else {
                    // 실패 시 메시지 업데이트
                    document.querySelector('.processing-message').innerHTML = 
                        '<p class="text-danger"><strong>처리 중 오류가 발생했습니다.</strong></p>' +
                        '<p>' + (data.error || '알 수 없는 오류가 발생했습니다.') + '</p>';
                    document.querySelector('.spinner-border').style.display = 'none';
                    document.querySelector('.progress-container').style.display = 'none';
                    // 오류 발생 시에도 메인으로 이동 버튼 표시
                    document.getElementById('mainPageBtn').style.display = 'inline-block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.querySelector('.processing-message').innerHTML = 
                    '<p class="text-danger"><strong>네트워크 오류가 발생했습니다.</strong></p>' +
                    '<p>페이지를 새로고침하거나 잠시 후 다시 시도해 주세요.</p>';
                document.querySelector('.spinner-border').style.display = 'none';
                document.querySelector('.progress-container').style.display = 'none';
                // 네트워크 오류 시에도 메인으로 이동 버튼 표시
                document.getElementById('mainPageBtn').style.display = 'inline-block';
            });
        });
    </script>
</body>
</html>