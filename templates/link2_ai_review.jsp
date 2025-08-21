<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI 검토 옵션 선택</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    		<link href="{{ url_for('static', filename='css/common.css')}}" rel="stylesheet">
		<link href="{{ url_for('static', filename='css/style.css')}}" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container text-center mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow-lg">
                    <div class="card-header bg-primary text-white">
                        <h3><i class="fas fa-check-circle"></i> 인터뷰가 완료되었습니다!</h3>
                    </div>
                    <div class="card-body p-4">
                        <div class="alert alert-success mb-4">
                            <h5><i class="fas fa-clipboard-check"></i> 모든 질문에 답변해 주셔서 감사합니다</h5>
                            <p class="mb-0">이제 ITGC 설계평가 문서를 생성하여 메일로 전송해 드리겠습니다.</p>
                        </div>
                        
                        <div class="mb-4">
                            <h5 class="mb-3"><i class="fas fa-robot"></i> AI 검토 옵션</h5>
                            <p class="text-muted">AI가 답변을 분석하여 더 정확하고 완성도 높은 문서를 생성할 수 있습니다.</p>
                        </div>
                        
                        <div class="row g-3">
                            <div class="col-md-6">
                                <div class="card h-100 ai-option-card" data-option="yes">
                                    <div class="card-body d-flex flex-column justify-content-center">
                                        <i class="fas fa-brain fa-3x text-primary mb-3"></i>
                                        <h5 class="card-title">AI 검토 사용</h5>
                                        <ul class="list-unstyled text-start small mb-3">
                                            <li><i class="fas fa-check text-success me-2"></i>답변 내용 검토 및 개선</li>
                                            <li><i class="fas fa-check text-success me-2"></i>문장 다듬기 및 문법 교정</li>
                                            <li><i class="fas fa-check text-success me-2"></i>일관성 검증</li>
                                            <li><i class="fas fa-check text-success me-2"></i>전문적인 검토 의견 제공</li>
                                        </ul>
                                        <p class="text-muted small">처리 시간: 2-3분</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card h-100 ai-option-card" data-option="no">
                                    <div class="card-body d-flex flex-column justify-content-center">
                                        <i class="fas fa-file-alt fa-3x text-secondary mb-3"></i>
                                        <h5 class="card-title">기본 문서 생성</h5>
                                        <ul class="list-unstyled text-start small mb-3">
                                            <li><i class="fas fa-check text-success me-2"></i>빠른 문서 생성</li>
                                            <li><i class="fas fa-check text-success me-2"></i>입력한 답변 그대로 반영</li>
                                            <li><i class="fas fa-check text-success me-2"></i>즉시 처리</li>
                                            <li><i class="fas fa-times text-muted me-2"></i>AI 검토 없음</li>
                                        </ul>
                                        <p class="text-muted small">처리 시간: 30초 이내</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <form id="aiReviewForm" method="POST" action="/process_with_ai_option">
                                <input type="hidden" name="enable_ai_review" id="enableAiReview" value="">
                                <button type="submit" id="proceedBtn" class="btn btn-primary btn-lg disabled" disabled>
                                    <i class="fas fa-arrow-right"></i> 진행
                                </button>
                            </form>
                        </div>
                        
                        <div class="mt-3">
                            <p class="text-muted small">
                                <i class="fas fa-info-circle"></i> 
                                결과 문서는 <strong>{{ user_email }}</strong>로 전송됩니다.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const optionCards = document.querySelectorAll('.ai-option-card');
            const proceedBtn = document.getElementById('proceedBtn');
            const enableAiReviewInput = document.getElementById('enableAiReview');
            
            optionCards.forEach(card => {
                card.addEventListener('click', function() {
                    // 모든 카드에서 selected 클래스 제거
                    optionCards.forEach(c => c.classList.remove('selected'));
                    
                    // 클릭된 카드에 selected 클래스 추가
                    this.classList.add('selected');
                    
                    // 선택된 옵션 값 설정
                    const option = this.getAttribute('data-option');
                    enableAiReviewInput.value = option === 'yes' ? 'true' : 'false';
                    
                    // 버튼 활성화
                    proceedBtn.classList.remove('disabled');
                    proceedBtn.disabled = false;
                    
                    // 버튼 텍스트 업데이트
                    if (option === 'yes') {
                        proceedBtn.innerHTML = '<i class="fas fa-brain"></i> AI 검토 진행';
                    } else {
                        proceedBtn.innerHTML = '<i class="fas fa-file-alt"></i> 기본 생성 진행';
                    }
                });
            });
        });
    </script>
</body>
</html>