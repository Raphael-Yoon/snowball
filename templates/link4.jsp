<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/common.css" rel="stylesheet">
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
                {value: "APD04", text: "Application 관리자 권한 제한"},
                {value: "APD05", text: "Application 권한 Monitoring"},
                {value: "APD06", text: "Application 패스워드"},
                {value: "APD07", text: "Data 직접변경 승인"},
                {value: "APD08", text: "서버(OS/DB) 접근권한 승인"},
                {value: "APD09", text: "서버(OS/DB) 패스워드"},
                {value: "APD10", text: "서버(OS/DB) 관리자 권한 제한"},
            ],
            PC: [
                {value: "PC01", text: "프로그램 변경 승인"},
                {value: "PC02", text: "프로그램 변경 사용자 테스트"},
                {value: "PC03", text: "프로그램 이관 승인"},
                {value: "PC04", text: "이관담당자 권한 제한"},
                {value: "PC05", text: "개발/운영 환경 분리"},
                {value: "PC06", text: "인프라 설정변경"}
            ],
            CO: [
                {value: "CO01", text: "배치잡 스케줄 등록 승인"},
                {value: "CO02", text: "배치잡 스케줄 등록 권한 제한"},
                {value: "CO03", text: "배치잡 스케줄 Monitoring"}
            ]
        };

        const categoryNames = {
            'APD': 'Access Program & Data',
            'PC': 'Program Change',
            'CO': 'Computer Operation'
        };

        function initializeSidebar() {
            const categoryList = document.getElementById('categoryList');
            categoryList.innerHTML = '';

            Object.keys(options).forEach(category => {
                const categoryTitle = document.createElement('div');
                categoryTitle.className = 'category-title';
                categoryTitle.textContent = categoryNames[category];
                categoryList.appendChild(categoryTitle);

                const optionList = document.createElement('div');
                optionList.className = 'nav flex-column';
                
                options[category].forEach(option => {
                    const link = document.createElement('a');
                    link.href = '#';
                    link.className = 'nav-link';
                    link.dataset.value = option.value;
                    link.textContent = option.text;
                    
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
                        this.classList.add('active');
                        updateContent(this.dataset.value);
                    });
                    
                    optionList.appendChild(link);
                });
                
                categoryList.appendChild(optionList);
            });
        }

        function updateContent(selectedValue) {
            const contentContainer = document.getElementById('contentContainer');
            contentContainer.innerHTML = '';

            fetch(`/get_content?type=${selectedValue}`)
                .then(response => response.text())
                .then(html => {
                    contentContainer.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error:', error);
                    contentContainer.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            <h4 class="alert-heading">오류가 발생했습니다</h4>
                            <p>페이지를 불러오는 중 문제가 발생했습니다.</p>
                        </div>
                    `;
                });
        }

        document.addEventListener('DOMContentLoaded', initializeSidebar);
    </script>
</body>
</html>