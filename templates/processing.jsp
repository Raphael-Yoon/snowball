<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>작업 진행 중</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/processing.css')}}" rel="stylesheet">
</head>
<body>
    <div class="container text-center mt-5">
        <div class="mb-4">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="status-icon">🤖</div>
        </div>
        
        <h2 class="mb-4">✨ AI 검토 및 문서 생성 중입니다</h2>
        
        <div class="processing-message">
            <p>📋 인터뷰 내용을 분석하고 ITGC 설계평가 문서를 생성하고 있습니다.</p>
            <p class="text-muted">📧 완료되면 <strong>{{ user_email }}</strong>로 결과를 전송해 드리겠습니다.</p>
        </div>
        
        <div class="progress-container">
            <div class="progress mb-3">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" 
                     id="progressBar"
                     style="width: 0%"
                     aria-valuenow="0" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    <span id="progressText">0%</span>
                </div>
            </div>
            <div id="currentTask" class="text-muted">🔄 AI 검토를 준비하고 있습니다...</div>
        </div>
        
        <div class="alert alert-info mt-4">
            <strong>⏳ 잠시만 기다려 주세요.</strong><br>
            ⏱️ 처리 시간은 인터뷰 내용에 따라 다를 수 있습니다.<br>
            ⚠️ 화면을 닫지 마세요. 화면을 닫을 경우 메일 전송이 안될 수 있습니다.
        </div>
        
        <a href="/" class="btn btn-primary mt-3" id="mainPageBtn" style="display: none;">🏠 메인으로 이동</a>
    </div>

    <script>
        let progressInterval;
        
        // 진행률 업데이트 함수
        function updateProgress() {
            console.log('🔄 Requesting progress update...');
            fetch('/get_progress')
                .then(response => {
                    console.log('📡 Progress response:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('📊 Progress data:', data);
                    const progressBar = document.getElementById('progressBar');
                    const progressText = document.getElementById('progressText');
                    const currentTask = document.getElementById('currentTask');
                    
                    // 진행률 업데이트
                    progressBar.style.width = data.percentage + '%';
                    progressBar.setAttribute('aria-valuenow', data.percentage);
                    progressText.textContent = data.percentage + '%';
                    currentTask.textContent = data.current_task;
                    
                    // 브라우저 제목도 업데이트
                    document.title = `작업 진행 중 (${data.percentage}%) - ${data.current_task.substring(0, 20)}...`;
                    
                    console.log(`✅ Updated UI: ${data.percentage}% - ${data.current_task}`);
                    
                    // 처리 완료 또는 처리 중이 아닐 때 폴링 중단
                    if (!data.is_processing || data.percentage >= 100) {
                        console.log('🛑 Stopping progress polling:', data);
                        clearInterval(progressInterval);
                    }
                })
                .catch(error => {
                    console.error('❌ Progress update error:', error);
                });
        }
        
        // 페이지 로드 후 자동으로 작업 시작
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Page loaded, starting progress monitoring...');
            // 즉시 한 번 호출
            updateProgress();
            // 진행률 폴링 시작 (1초마다)
            progressInterval = setInterval(updateProgress, 1000);
            console.log('⏰ Progress polling started (every 1 second)');
            
            // 실제 작업을 시작하는 AJAX 요청 (브라우저 호환성 개선)
            console.log('Starting process_interview request...'); // 디버깅용 로그 추가
            var processXhr = new XMLHttpRequest();
            processXhr.open('POST', '/process_interview', true);
            processXhr.setRequestHeader('Content-Type', 'application/json');
            processXhr.onreadystatechange = function() {
                if (processXhr.readyState === 4) {
                    console.log('Process interview response status:', processXhr.status); // 디버깅용 로그 추가
                    // 진행률 폴링 중단
                    clearInterval(progressInterval);
                    
                    if (processXhr.status === 200) {
                        try {
                            var data = JSON.parse(processXhr.responseText);
                            console.log('Process interview data:', data); // 디버깅용 로그 추가
                            
                            if (data.success) {
                                // 성공 시 탭 제목과 메시지 업데이트
                                document.title = '작업 완료';
                                document.querySelector('h2').innerHTML = '✅ AI 검토 및 문서 생성이 완료되었습니다';
                                document.querySelector('.processing-message').innerHTML = 
                                    '<p class="text-success"><strong>🎉 ITGC 설계평가 문서가 성공적으로 생성되어 메일로 전송되었습니다!</strong></p>' +
                                    '<p>📮 메일함을 확인해 주세요.</p>';
                                document.querySelector('.spinner-border').style.display = 'none';
                                document.querySelector('.progress-container').style.display = 'none';
                                document.querySelector('.alert').style.display = 'none';
                                // AI 검토 완료 후 메인으로 이동 버튼 표시
                                document.getElementById('mainPageBtn').style.display = 'inline-block';
                            } else {
                                // 실패 시 탭 제목과 메시지 업데이트
                                document.title = '작업 오류';
                                document.querySelector('h2').innerHTML = '❌ 처리 중 오류가 발생했습니다';
                                document.querySelector('.processing-message').innerHTML = 
                                    '<p class="text-danger"><strong>⚠️ 처리 중 오류가 발생했습니다.</strong></p>' +
                                    '<p>🔧 ' + (data.error || '알 수 없는 오류가 발생했습니다.') + '</p>';
                                document.querySelector('.spinner-border').style.display = 'none';
                                document.querySelector('.progress-container').style.display = 'none';
                                // 오류 발생 시에도 메인으로 이동 버튼 표시
                                document.getElementById('mainPageBtn').style.display = 'inline-block';
                            }
                        } catch (e) {
                            console.error('JSON parsing error:', e);
                            // 파싱 오류 처리
                            document.title = '처리 오류';
                            document.querySelector('h2').innerHTML = '❌ 응답 처리 중 오류가 발생했습니다';
                            document.querySelector('.processing-message').innerHTML = 
                                '<p class="text-danger"><strong>⚠️ 서버 응답 처리 중 오류가 발생했습니다.</strong></p>' +
                                '<p>🔄 페이지를 새로고침하거나 잠시 후 다시 시도해 주세요.</p>';
                            document.querySelector('.spinner-border').style.display = 'none';
                            document.querySelector('.progress-container').style.display = 'none';
                            document.getElementById('mainPageBtn').style.display = 'inline-block';
                        }
                    } else {
                        // HTTP 오류 처리
                        console.error('HTTP Error:', processXhr.status);
                        document.title = '네트워크 오류';
                        document.querySelector('h2').innerHTML = '🌐 네트워크 오류 발생';
                        document.querySelector('.processing-message').innerHTML = 
                            '<p class="text-danger"><strong>📡 네트워크 오류가 발생했습니다.</strong></p>' +
                            '<p>🔄 페이지를 새로고침하거나 잠시 후 다시 시도해 주세요.</p>';
                        document.querySelector('.spinner-border').style.display = 'none';
                        document.querySelector('.progress-container').style.display = 'none';
                        document.getElementById('mainPageBtn').style.display = 'inline-block';
                    }
                }
            };
            processXhr.send();
        });
    </script>
</body>
</html>