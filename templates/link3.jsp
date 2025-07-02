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
    
    <div class="container-fluid">
        <div class="row">
            <!-- 왼쪽 사이드바 -->
            <div class="col-md-4 col-lg-3 sidebar">
                <div id="categoryList"></div>
            </div>
            
            <!-- 오른쪽 컨텐츠 영역 -->
            <div class="col-md-8 col-lg-9 content-area">
                <div id="contentContainer">
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
                    contentContainer.innerHTML = html;
                    enableStepByStep(selectedValue);
                });
        }

        // 모든 메뉴에 대해 step-by-step 로직
        function enableStepByStep(type) {
            // 각 항목별 step 데이터 정의
            const stepMap = {
                APD01: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 권한부여 요청", desc: "신규 사용자 권한부여 요청을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 절차", desc: "권한부여 요청에 대한 승인 절차를 진행합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 부여 완료", desc: "권한이 정상적으로 부여되었는지 확인합니다."}
                ],
                APD02: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 권한 회수 요청 확인", desc: "부서이동자에 대한 권한 회수 요청이 접수되었는지 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 권한 회수 승인", desc: "권한 회수 요청에 대해 적절한 승인이 이루어졌는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 회수 완료", desc: "권한 회수 절차가 실제로 완료되었는지 확인합니다."}
                ],
                APD03: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 퇴사자 확인", desc: "퇴사자 명단을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 접근권한 회수", desc: "퇴사자의 접근권한이 회수되었는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 기록 보관", desc: "권한 회수 기록이 보관되었는지 확인합니다."}
                ],
                APD04: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 권한 모니터링 시작", desc: "전체 사용자 권한 모니터링을 시작합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 이상 권한 탐지", desc: "이상 권한을 가진 사용자를 탐지합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 조치 및 기록", desc: "이상 권한에 대해 조치하고 기록을 남깁니다."}
                ],
                APD05: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 패스워드 정책 확인", desc: "패스워드 정책을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 정책 적용", desc: "패스워드 정책이 시스템에 적용되었는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 이력 점검", desc: "패스워드 변경 이력을 점검합니다."}
                ],
                APD06: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 데이터 변경 요청", desc: "데이터 변경 요청이 접수되었는지 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 변경", desc: "변경 요청에 대한 승인을 받고 데이터를 변경합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 내역 기록", desc: "변경 내역이 기록되었는지 확인합니다."}
                ],
                APD07: [
                    {img: "/static/img/step1.jpg", title: "Step 1: DB 접근권한 요청", desc: "DB 접근권한 요청이 접수되었는지 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 권한 부여", desc: "요청에 대한 승인을 받고 권한을 부여합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 부여 내역 기록", desc: "권한 부여 내역이 기록되었는지 확인합니다."}
                ],
                APD08: [
                    {img: "/static/img/step1.jpg", title: "Step 1: DB 패스워드 정책 확인", desc: "DB 패스워드 정책을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 정책 적용", desc: "정책이 적용되었는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 이력 점검", desc: "패스워드 변경 이력을 점검합니다."}
                ],
                APD09: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 관리자 권한 확인", desc: "DB 관리자 권한을 가진 사용자를 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 권한 제한 적용", desc: "불필요한 관리자 권한을 제한합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 변경 기록", desc: "권한 변경 내역을 기록합니다."}
                ],
                APD10: [
                    {img: "/static/img/step1.jpg", title: "Step 1: OS 접근권한 요청", desc: "OS 접근권한 요청이 접수되었는지 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 권한 부여", desc: "요청에 대한 승인을 받고 권한을 부여합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 부여 내역 기록", desc: "권한 부여 내역이 기록되었는지 확인합니다."}
                ],
                APD11: [
                    {img: "/static/img/step1.jpg", title: "Step 1: OS 패스워드 정책 확인", desc: "OS 패스워드 정책을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 정책 적용", desc: "정책이 적용되었는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 이력 점검", desc: "패스워드 변경 이력을 점검합니다."}
                ],
                APD12: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 관리자 권한 확인", desc: "OS 관리자 권한을 가진 사용자를 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 권한 제한 적용", desc: "불필요한 관리자 권한을 제한합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 변경 기록", desc: "권한 변경 내역을 기록합니다."}
                ],
                PC01: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 변경 요청 접수", desc: "프로그램 변경 요청이 접수되었는지 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 변경 승인", desc: "변경 요청에 대한 승인이 이루어졌는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 적용", desc: "변경이 정상적으로 적용되었는지 확인합니다."}
                ],
                PC04: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 이관 담당자 지정", desc: "이관 담당자를 지정합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 권한 제한", desc: "이관 담당자의 권한을 제한합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 기록 관리", desc: "이관 권한 변경 내역을 기록합니다."}
                ],
                PC05: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 환경 분리 계획", desc: "개발/운영 환경 분리 계획을 수립합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 환경 분리 적용", desc: "환경 분리 정책을 적용합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 분리 상태 점검", desc: "환경 분리 상태를 점검합니다."}
                ],
                PC06: [
                    {img: "/static/img/step1.jpg", title: "Step 1: DB 설정 변경 요청", desc: "DB 설정 변경 요청을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 변경", desc: "설정 변경에 대한 승인을 받고 변경을 적용합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 내역 기록", desc: "설정 변경 내역을 기록합니다."}
                ],
                PC07: [
                    {img: "/static/img/step1.jpg", title: "Step 1: OS 설정 변경 요청", desc: "OS 설정 변경 요청을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 변경", desc: "설정 변경에 대한 승인을 받고 변경을 적용합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 변경 내역 기록", desc: "설정 변경 내역을 기록합니다."}
                ],
                CO01: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 배치잡 요청", desc: "배치잡 스케줄 등록 요청을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 절차", desc: "배치잡 등록에 대한 승인 절차를 진행합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 등록 완료", desc: "배치잡이 정상적으로 등록되었는지 확인합니다."}
                ],
                CO02: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 권한 제한 요청", desc: "배치잡 등록 권한 제한 요청을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 적용", desc: "권한 제한에 대한 승인을 받고 적용합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 권한 변경 기록", desc: "권한 변경 내역을 기록합니다."}
                ],
                CO03: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 스케줄 모니터링 시작", desc: "배치잡 스케줄 실행 상태를 모니터링합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 오류 탐지", desc: "오류 발생 시 원인을 탐지합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 조치 및 기록", desc: "오류에 대한 조치와 기록을 남깁니다."}
                ],
                CO04: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 백업 정책 확인", desc: "백업 정책을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 백업 수행", desc: "백업이 정상적으로 수행되는지 확인합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 백업 내역 기록", desc: "백업 내역을 기록합니다."}
                ],
                CO05: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 장애 발생 확인", desc: "장애 발생 시 원인을 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 장애 조치", desc: "장애에 대한 조치를 수행합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 장애 처리 기록", desc: "장애 처리 내역을 기록합니다."}
                ],
                CO06: [
                    {img: "/static/img/step1.jpg", title: "Step 1: 서버실 출입 요청", desc: "서버실 출입 요청이 접수되었는지 확인합니다."},
                    {img: "/static/img/step2.jpg", title: "Step 2: 승인 및 출입", desc: "출입 요청에 대한 승인을 받고 출입합니다."},
                    {img: "/static/img/step3.jpg", title: "Step 3: 출입 기록 관리", desc: "출입 내역을 기록합니다."}
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
                    imgDiv.innerHTML = `<img src="${steps[currentStep].img}" alt="step image" style="max-width:100%;height:180px;object-fit:cover;border-radius:8px;margin-bottom:16px;">`;
                } else {
                    imgDiv.textContent = steps[currentStep].title.split(':')[0].toUpperCase();
                }
                titleDiv.textContent = steps[currentStep].title;
                descDiv.textContent = steps[currentStep].desc;
                const indicator = steps.map((_, idx) => `<span class="${idx === currentStep ? 'active' : ''}"></span>`).join('');
                indicatorDiv.innerHTML = indicator;
                prevBtn.disabled = currentStep === 0;
                nextBtn.disabled = currentStep === steps.length - 1;
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
        }
    </script>
</body>
</html>