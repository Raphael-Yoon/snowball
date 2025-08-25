<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>로그인 - Snowball</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/common.css') }}">
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="login-wrapper">
            <div class="login-container">
                <div class="login-header">
                    <a href="/" class="back-button">← 메인으로</a>
                    <h2>로그인</h2>
                </div>
            {% if error %}
                <div class="error-message">{{ error }}</div>
            {% endif %}
            {% if message %}
                <div class="success-message">{{ message }}</div>
            {% endif %}
            
            {% if not step or step != 'verify' %}
            <!-- 1단계: 이메일 입력 및 OTP 요청 -->
            <form method="POST" action="{{ url_for('login') }}">
                <input type="hidden" name="action" value="send_otp">
                <div class="form-group">
                    <label for="email">이메일:</label>
                    <input type="email" id="email" name="email" required 
                           placeholder="등록된 이메일 주소를 입력하세요">
                </div>
                <div class="form-group">
                    <label>인증 방법:</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="method" value="email" checked>
                            이메일로 받기
                        </label>
                        {% if remote_addr == '127.0.0.1' or (user_info and user_info.get('admin_flag') == 'Y') %}
                        <label class="radio-label">
                            <input type="radio" name="method" value="sms">
                            SMS로 받기 (테스트용: <a href="/sms_test_log" target="_blank">로그 확인</a>)
                        </label>
                        {% endif %}
                    </div>
                </div>
                <button type="submit" class="btn-primary">인증 코드 발송</button>
            </form>
            {% else %}
            <!-- 2단계: OTP 코드 입력 -->
            <div class="otp-info">
                <p><strong>{{ email }}</strong>로 인증 코드를 발송했습니다.</p>
                <p>이메일을 확인하고 6자리 인증 코드를 입력해주세요.</p>
            </div>
            <form method="POST" action="{{ url_for('login') }}">
                <input type="hidden" name="action" value="verify_otp">
                <div class="form-group">
                    <label for="otp_code">인증 코드:</label>
                    <input type="text" id="otp_code" name="otp_code" required 
                           placeholder="000000" maxlength="6" pattern="[0-9]{6}"
                           style="font-size: 20px; text-align: center; letter-spacing: 5px;">
                </div>
                <div class="button-group">
                    <button type="submit" class="btn-primary">로그인</button>
                    <a href="{{ url_for('login') }}" class="btn-secondary">다시 시작</a>
                </div>
            </form>
            {% endif %}
            </div>
            
            <div class="info-container">
                <div class="info-header">
                    <h3><i class="fas fa-star"></i> 프리미엄 서비스</h3>
                    <p class="info-subtitle">전문적인 내부통제 평가 솔루션</p>
                </div>
                
                <div class="feature-list">
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="feature-content">
                            <h4>AI 검토 기능</h4>
                            <p>인터뷰 결과를 AI가 분석하여 더욱 정확하고 상세한 평가 보고서를 제공합니다.</p>
                        </div>
                    </div>
                    
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-cogs"></i>
                        </div>
                        <div class="feature-content">
                            <h4>맞춤 RCM 기능</h4>
                            <p>각 회사의 특성에 맞는 신뢰성 중심 유지보수 시스템을 제공합니다.</p>
                        </div>
                    </div>
                    
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="feature-content">
                            <h4>고급 분석 도구</h4>
                            <p>상세한 분석 리포트와 개선 방안을 통해 내부통제 수준을 향상시킵니다.</p>
                        </div>
                    </div>
                    
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="fas fa-headset"></i>
                        </div>
                        <div class="feature-content">
                            <h4>전문가 지원</h4>
                            <p>숙련된 전문가들이 직접 지원하여 최고 품질의 서비스를 보장합니다.</p>
                        </div>
                    </div>
                </div>
                
                <div class="pricing-info">
                    <div class="pricing-badge" id="showInquiryBtn" style="cursor: pointer;">
                        <i class="fas fa-handshake"></i>
                        서비스 문의
                    </div>
                    <p class="pricing-description">
                        전문적인 내부통제 평가를 위한 프리미엄 서비스로 운영됩니다.
                    </p>
                </div>
            </div>
            
            <div class="inquiry-container" id="inquiryContainer" style="display: none;">
                <div class="service-inquiry-form">
                    <h4>서비스 문의</h4>
                    {% if service_inquiry_success %}
                        <div class="success-message">
                            <i class="fas fa-check-circle"></i> 서비스 문의가 성공적으로 접수되었습니다.<br>
                            빠른 시일 내에 연락드리겠습니다.
                        </div>
                    {% elif service_inquiry_error %}
                        <div class="error-message">
                            <i class="fas fa-exclamation-triangle"></i> 서비스 문의 접수에 실패했습니다.<br>
                            {{ service_inquiry_error }}
                        </div>
                    {% endif %}
                    <form method="POST" action="/service_inquiry" id="serviceInquiryForm">
                        <div class="form-group">
                            <label for="company_name">회사명</label>
                            <input type="text" id="company_name" name="company_name" required placeholder="회사명을 입력하세요">
                        </div>
                        <div class="form-group">
                            <label for="contact_name">담당자명</label>
                            <input type="text" id="contact_name" name="contact_name" required placeholder="담당자명을 입력하세요">
                        </div>
                        <div class="form-group">
                            <label for="contact_email">이메일</label>
                            <input type="email" id="contact_email" name="contact_email" required placeholder="이메일 주소를 입력하세요">
                        </div>
                        <button type="submit" class="btn-primary">
                            <i class="fas fa-paper-plane"></i> 서비스 문의
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const showInquiryBtn = document.getElementById('showInquiryBtn');
            const inquiryContainer = document.getElementById('inquiryContainer');
            
            showInquiryBtn.addEventListener('click', function() {
                if (inquiryContainer.style.display === 'none') {
                    inquiryContainer.style.display = 'block';
                    // 스크롤 효과로 폼으로 이동
                    inquiryContainer.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'nearest' 
                    });
                } else {
                    inquiryContainer.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>