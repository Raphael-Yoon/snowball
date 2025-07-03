<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/common.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
    {% include 'navi.jsp' %}
    
    <div class="container-fluid h-100">
        <div class="row h-100">
            <!-- 왼쪽 사이드바 -->
            <div class="col-md-3 col-lg-3 sidebar" style="padding:0;">
                <div id="categoryList"></div>
            </div>
            
            <!-- 오른쪽 컨텐츠 영역 -->
            <div class="col-md-9 col-lg-9 content-area d-flex align-items-stretch h-100" style="padding:0;">
                <div id="contentContainer" class="flex-grow-1 d-flex flex-column justify-content-center align-items-stretch h-100" style="padding:0;">
                    <div class="text-center text-muted">
                        <h3>항목을 선택해주세요</h3>
                        <p>왼쪽 메뉴에서 원하는 항목을 선택하시면 상세 내용이 표시됩니다.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const options = {
            APD: [
                {value: "APD01", text: "Application 권한부여 승인"},
                {value: "APD02", text: "Application 부서이동자 권한 회수"},
                {value: "APD03", text: "Application 퇴사자 접근권한 회수"},
                {value: "APD04", text: "Application 권한 Monitoring"},
                {value: "APD05", text: "Application 패스워드"},
                {value: "APD06", text: "Data 직접변경 승인"},
                {value: "APD07", text: "DB 접근권한 승인"},
                {value: "APD08", text: "DB 패스워드"},
                {value: "APD09", text: "DB 관리자 권한 제한"},
                {value: "APD10", text: "OS 접근권한 승인"},
                {value: "APD11", text: "OS 패스워드"},
                {value: "APD12", text: "OS 관리자 권한 제한"}
            ],
            PC: [
                {value: "PC01", text: "프로그램 변경"},
                {value: "PC04", text: "이관담당자 권한 제한"},
                {value: "PC05", text: "개발/운영 환경 분리"},
                {value: "PC06", text: "DB 설정 변경"},
                {value: "PC07", text: "OS 설정 변경"}
            ],
            CO: [
                {value: "CO01", text: "배치잡 스케줄 등록 승인"},
                {value: "CO02", text: "배치잡 스케줄 등록 권한 제한"},
                {value: "CO03", text: "배치잡 스케줄 등록 Monitoring"},
                {value: "CO04", text: "백업 Monitoring"},
                {value: "CO05", text: "장애관리"},
                {value: "CO06", text: "서버실 접근 제한"}
                
            ]
        };

        const categoryNames = {
            'APD': 'Access Program & Data',
            'PC': 'Program Changes',
            'CO': 'Computer Operations'
        };

        function initializeSidebar() {
            const categoryList = document.getElementById('categoryList');
            categoryList.innerHTML = '';

            Object.keys(options).forEach(category => {
                const categoryTitle = document.createElement('div');
                categoryTitle.className = 'category-title';
                categoryTitle.innerHTML = `
                    ${categoryNames[category]}
                    <i class="fas fa-chevron-down"></i>
                `;
                
                const optionList = document.createElement('div');
                optionList.className = 'option-list';
                
                options[category].forEach(option => {
                    const link = document.createElement('a');
                    link.href = '#';
                    link.className = 'nav-link';
                    link.dataset.value = option.value;
                    link.textContent = option.text;
                    
                    link.addEventListener('click', function(e) {
                        document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
                        this.classList.add('active');
                        updateContent(this.dataset.value);
                    });
                    
                    optionList.appendChild(link);
                });
                
                categoryTitle.addEventListener('click', function() {
                    this.classList.toggle('collapsed');
                    optionList.classList.toggle('show');
                });
                
                categoryList.appendChild(categoryTitle);
                categoryList.appendChild(optionList);
            });
        }

        document.addEventListener('DOMContentLoaded', initializeSidebar);

        function updateContent(selectedValue) {
            const contentContainer = document.getElementById('contentContainer');
            contentContainer.innerHTML = '';

            // 준비중 메시지를 보여줄 value 목록
            const preparingList = [];

            if (preparingList.includes(selectedValue)) {
                contentContainer.innerHTML = `
                    <div style="text-align: center; padding: 20px;">
                        <h3>준비 중입니다</h3>
                        <p>해당 항목은 현재 영상제작 중 입니다.</p>
                    </div>
                `;
                return;
            }

            // 모든 메뉴에 step-by-step SPA 적용
            fetch(`/get_content_link3?type=${selectedValue}`)
                .then(response => response.text())
                .then(html => {
                    contentContainer.innerHTML = `
                        <div class="step-card flex-grow-1">
                            <div id="step-img"></div>
                            <div id="step-title"></div>
                            <div id="step-desc"></div>
                            <div id="step-indicator"></div>
                            <div class="step-btns">
                                <button id="prev-btn" class="btn btn-primary me-2">이전</button>
                                <button id="next-btn" class="btn btn-primary">다음</button>
                            </div>
                        </div>
                    `;
                    enableStepByStep(selectedValue);
                });
        }

        // 모든 메뉴에 대해 step-by-step 로직
        function enableStepByStep(type) {
            // 각 항목별 step 데이터 정의
                const stepMap = {
                    APD01: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 확인", desc: "당기 신규 권한 부여 이력을 확인하세요.<br>모집단 갯수가 표시되는 화면을 함께 첨부하시면 좋습니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플링", desc: "모집단에서 샘플을 추출하세요.<br>샘플 갯수는 기준에 따라 결정되며, 예를 들어 모집단 수가 100이라면 Daily 기준이므로 20개의 샘플을 추출하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 증빙 확인", desc: "추출한 샘플에 대해 승인 여부를 확인하세요."},
                    {img: "/static/img/step4.jpg", title: "Step 4: 예외사항 확인", desc: "예외사항(승인 누락, 사후 승인 등)이 발생한 경우 충분한 양(일반적으로 선정한 샘플 수의 1/2)의 샘플을 추가로 검토하세요.<br>추가 샘플에 예외사항이 없는 경우 적정으로 결론내릴 수 있습니다."}
                ],
                APD02: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 부서이동자를 모집단으로 선정하세요.<br>부서이동자 명단을 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 권한 보유 내역 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플에 대해 부서이동일 이전에 보유하고 있던 모든 권한 내역을 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 회수 여부 점검", desc: "부서이동일 이후 해당 권한이 모두 회수되었는지 실제로 회수 내역을 점검하세요.<br>회수되지 않은 권한이 있다면 즉시 조치하시기 바랍니다."},
                    {img: "/static/img/step4.jpg", title: "Step 4: 예외 및 추가 검토", desc: "회수 누락, 사후 회수 등 예외사항이 있는 경우 추가로 샘플을 선정하여 검토하세요.<br>추가 검토 결과 문제가 없으면 적정으로 결론내릴 수 있습니다."}
                ],
                APD03: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 퇴사자를 모집단으로 선정하세요.<br>퇴사자 명단을 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 권한 보유 내역 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플에 대해 퇴사일 이전에 보유하고 있던 모든 접근권한 내역을 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 회수 여부 점검", desc: "퇴사일 이후 해당 권한이 모두 회수되었는지 실제로 회수 내역을 점검하세요.<br>회수되지 않은 권한이 있다면 즉시 조치하시기 바랍니다."},
                    {img: "/static/img/step4.jpg", title: "Step 4: 예외 및 추가 검토", desc: "회수 누락, 사후 회수 등 예외사항이 있는 경우 추가로 샘플을 선정하여 검토하세요.<br>추가 검토 결과 문제가 없으면 적정으로 결론내릴 수 있습니다."}
                ],
                APD04: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 권한 모니터링 문서 검토", desc: "당기 권한 모니터링 문서를 확보하여 검토를 시작하세요.<br>문서에 전체 사용자 및 모든 권한이 포함되어 있는지 확인하세요.<br>샘플 수는 통제 주기에 따라 결정하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 여부 확인", desc: "권한 모니터링 결과에 대해 적절한 승인(결재)이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 이상 권한 및 조치 내역 점검", desc: "이상 권한이 탐지된 경우 적절한 조치가 이루어졌는지, 그리고 그 내역이 문서에 기록되어 있는지 확인하세요."}
                ],
                APD05: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 보안규정 및 정책서 확인", desc: "회사의 보안규정 또는 정책서에 패스워드 관련 사항이 명시되어 있는지 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 정책 부합 여부 점검", desc: "패스워드 관련 규정이 있는 경우, 실제 시스템의 패스워드 설정이 정책서 기준(예: 최소 길이, 복잡성 등)에 부합하는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 기본 요건 점검", desc: "별도의 규정이 없는 경우, 최소 8자리 및 문자/숫자/특수문자 조합 등 기본적인 복잡성 요건이 적용되어 있는지 확인하세요."}
                ],
                APD06: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 데이터 변경 이력을 모집단으로 선정하세요.<br>변경 이력 전체를 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 사전 승인 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플 각각에 대해 사전 승인이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 내역 기록 점검", desc: "데이터 변경 내역이 적절하게 기록되어 있는지 확인하세요."}
                ],
                APD07: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 생성된 DB 접근권한을 모집단으로 선정하세요.<br>생성 이력 전체를 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 사전 승인 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플 각각에 대해 사전 승인이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 부여 내역 기록 점검", desc: "DB 접근권한 부여 내역이 적절하게 기록되어 있는지 확인하세요."}
                ],
                APD08: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 보안규정 및 정책서 확인", desc: "회사의 보안규정 또는 정책서에 DB 패스워드 관련 사항이 명시되어 있는지 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 정책 부합 여부 점검", desc: "DB 패스워드 관련 규정이 있는 경우, 실제 시스템의 패스워드 설정이 정책서 기준(예: 최소 길이, 복잡성 등)에 부합하는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 기본 요건 점검", desc: "별도의 규정이 없는 경우, 최소 8자리 및 문자/숫자/특수문자 조합 등 기본적인 복잡성 요건이 적용되어 있는지 확인하세요."}
                ],
                APD09: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 관리자 권한 사용자 추출", desc: "DB 관리자 권한을 보유한 사용자를 시스템에서 추출하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 부서/직무 등 검토", desc: "추출된 사용자의 부서, 직무, 담당 업무 등을 검토하여 관리자 권한 보유의 적정성을 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 적정성 판단 및 조치", desc: "불필요하거나 부적정한 관리자 권한이 확인될 경우 즉시 권한을 제한하고, 그 내역을 기록하세요."}
                ],
                APD10: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 생성된 OS 접근권한을 모집단으로 선정하세요.<br>생성 이력 전체를 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 사전 승인 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플 각각에 대해 사전 승인이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 부여 내역 기록 점검", desc: "OS 접근권한 부여 내역이 적절하게 기록되어 있는지 확인하세요."}
                ],
                APD11: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 보안규정 및 정책서 확인", desc: "회사의 보안규정 또는 정책서에 OS 패스워드 관련 사항이 명시되어 있는지 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 정책 부합 여부 점검", desc: "OS 패스워드 관련 규정이 있는 경우, 실제 시스템의 패스워드 설정이 정책서 기준(예: 최소 길이, 복잡성 등)에 부합하는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 기본 요건 점검", desc: "별도의 규정이 없는 경우, 최소 8자리 및 문자/숫자/특수문자 조합 등 기본적인 복잡성 요건이 적용되어 있는지 확인하세요."}
                ],
                APD12: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 관리자 권한 사용자 추출", desc: "OS 관리자 권한을 보유한 사용자를 시스템에서 추출하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 부서/직무 등 검토", desc: "추출된 사용자의 부서, 직무, 담당 업무 등을 검토하여 관리자 권한 보유의 적정성을 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 적정성 판단 및 조치", desc: "불필요하거나 부적정한 관리자 권한이 확인될 경우 즉시 권한을 제한하고, 그 내역을 기록하세요."}
                ],
                PC01: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정 및 샘플링", desc: "당기 프로그램 이관 이력을 모집단으로 선정하고, 모집단 수에 따라 샘플 수를 선정하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 프로그램 변경 요청 승인 검토", desc: "선정된 샘플 각각에 대해 프로그램 변경 요청에 대한 승인이 적정하게 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 사용자 테스트 및 이관 승인 검토", desc: "각 샘플에 대해 프로그램 변경 후 사용자의 테스트가 이루어졌는지, 그리고 프로그램 이관 요청에 대한 승인이 적정하게 이루어졌는지 확인하세요."}
                ],
                PC04: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 이관담당자 권한 사용자 추출", desc: "이관담당자 권한을 보유한 사용자를 시스템에서 추출하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 부서/직무 등 검토", desc: "추출된 사용자의 부서, 직무, 담당 업무 등을 검토하여 이관담당자 권한 보유의 적정성을 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 적정성 판단 및 조치", desc: "불필요하거나 부적정한 이관담당자 권한이 확인될 경우 즉시 권한을 제한하고, 그 내역을 기록하세요."}
                ],
                PC05: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 개발/운영 환경 분리 현황 확인", desc: "시스템이 운영환경과 별도의 개발환경을 보유하고 있는지 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 증빙 자료 확보", desc: "서버 구성도, IP 목록 등으로 개발환경과 운영환경이 분리되어 있는지 증빙 자료를 확보하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 환경 분리 적정성 검토", desc: "확보한 증빙 자료를 바탕으로 개발/운영 환경 분리가 적정하게 이루어졌는지 검토하세요."}
                ],
                PC06: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 DB 패치 이력을 모집단으로 선정하세요.<br>패치 이력 전체를 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 사전 승인 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플 각각에 대해 사전 승인이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 내역 기록 점검", desc: "DB 패치 변경 내역이 적절하게 기록되어 있는지 확인하세요."}
                ],
                PC07: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 OS 패치 이력을 모집단으로 선정하세요.<br>패치 이력 전체를 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 사전 승인 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플 각각에 대해 사전 승인이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 내역 기록 점검", desc: "OS 패치 변경 내역이 적절하게 기록되어 있는지 확인하세요."}
                ],
                CO01: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 모집단 선정", desc: "당기 배치잡 스케줄 등록 이력을 모집단으로 선정하세요.<br>등록 이력 전체를 확보하시기 바랍니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 샘플 선정 및 사전 승인 확인", desc: "모집단 수에 따라 샘플 수를 선정하세요.<br>선정된 샘플 각각에 대해 사전 승인이 이루어졌는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 등록 내역 기록 점검", desc: "배치잡 스케줄 등록 내역이 적절하게 기록되어 있는지 확인하세요."}
                ],
                CO02: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 배치잡 등록 권한 사용자 추출", desc: "배치잡 등록 권한을 보유한 사용자를 시스템에서 추출하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 부서/직무 등 검토", desc: "추출된 사용자의 부서, 직무, 담당 업무 등을 검토하여 배치잡 등록 권한 보유의 적정성을 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 적정성 판단 및 조치", desc: "불필요하거나 부적정한 배치잡 등록 권한이 확인될 경우 즉시 권한을 제한하고, 그 내역을 기록하세요."}
                ],
                CO03: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 스케줄 모니터링 시작", desc: "배치잡 스케줄 실행 상태를 모니터링하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 오류 탐지", desc: "오류 발생 시 원인을 탐지하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 조치 및 기록", desc: "오류에 대한 조치와 기록을 남기세요."}
                ],
                CO04: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 백업 정책 확인", desc: "백업 정책을 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 백업 수행", desc: "백업이 정상적으로 수행되는지 확인하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 백업 내역 기록", desc: "백업 내역을 기록하세요."}
                ],
                CO05: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 장애 발생 확인", desc: "장애 발생 시 원인을 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 장애 조치", desc: "장애에 대한 조치를 수행하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 장애 처리 기록", desc: "장애 처리 내역을 기록하세요."}
                ],
                CO06: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 서버실 출입 요청", desc: "서버실 출입 요청이 접수되었는지 확인하세요."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 출입", desc: "출입 요청에 대한 승인을 받고 출입하세요."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 출입 기록 관리", desc: "출입 내역을 기록하세요."}
                ]
            };
            const steps = stepMap[type];
            if (!steps) return;
            let currentStep = 0;
            const imgDiv = document.getElementById('step-img');
            const titleDiv = document.getElementById('step-title');
            const descDiv = document.getElementById('step-desc');
            const indicatorDiv = document.getElementById('step-indicator');
            const prevBtn = document.getElementById('prev-btn');
            const nextBtn = document.getElementById('next-btn');
            if (!imgDiv || !titleDiv || !descDiv || !indicatorDiv || !prevBtn || !nextBtn) return;
            function renderStep() {
                if (steps[currentStep].img) {
                    imgDiv.innerHTML = `<img src="${steps[currentStep].img}" alt="step image" class="step-img-el">`;
                } else {
                    imgDiv.textContent = steps[currentStep].title.split(':')[0].toUpperCase();
                }
                titleDiv.textContent = steps[currentStep].title;
                descDiv.innerHTML = steps[currentStep].desc;
                const indicator = steps.map((_, idx) => `<span class="${idx === currentStep ? 'active' : ''}"></span>`).join('');
                indicatorDiv.innerHTML = indicator;
                prevBtn.disabled = currentStep === 0;
                nextBtn.disabled = currentStep === steps.length - 1;
                resizeStepCard();
            }
            prevBtn.onclick = function() {
                if (currentStep > 0) {
                    currentStep--;
                    renderStep();
                }
            };
            nextBtn.onclick = function() {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    renderStep();
                }
            };
            renderStep();
            // step-card가 부모 영역을 무조건 꽉 채우도록 JS로 강제
            function resizeStepCard() {
                const area = document.querySelector('.content-area');
                const card = document.querySelector('.step-card');
                if (area && card) {
                    card.style.height = area.offsetHeight + 'px';
                }
            }
            window.addEventListener('resize', resizeStepCard);
            setTimeout(resizeStepCard, 100);
        }
    </script>
</body>
</html>