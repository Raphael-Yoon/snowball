<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    {% include 'navi.jsp' %}
    <form class = "grid" action = "/paper_template_download" method="post">
        <select name="param1" id="param1">
            <option value="APD" selected>Access Program & Data</option>
            <option value="PC">Program Change</option>
            <option value="CO">Computer Operation</option>
        </select>
        <select name="param2" id="param2" onchange="updateContent()">
            <option value="APD01">Application 권한부여 승인</option>
            <option value="APD02">Application 권한 회수</option> 
            <option value="APD03">Application 계정 삭제</option>
            <option value="APD04">Application 관리자 권한 제한</option>
            <option value="APD05">Application 권한 Monitoring</option>
            <option value="APD06">Application 패스워드</option>
            <option value="APD07">Data 직접변경 승인</option>
            <option value="APD08">Data 직접변경 권한 제한</option>
            <option value="APD09">DB 접근권한 승인</option>
            <option value="APD10">DB 패스워드</option>
            <option value="APD11">DB 관리자 권한 제한</option>
            <option value="APD12">OS 접근권한 승인</option>
            <option value="APD13">OS 패스워드</option>
            <option value="APD14">OS 관리자 권한 제한</option>
        </select>
    </form>
    <form class = "grid" action = "/paper_generate" method="post" enctype="multipart/form-data">
        <div id="contentContainer">
            <br><br>
            {% include 'link3_APD01.jsp' %}
        </div>
    </form>

    <script>
        const categorySelect = document.getElementById("param1");
        const nameSelect = document.getElementById("param2");
        const options = {
            APD: [
                {value: "APD01", text: "Application 권한부여 승인"},
                {value: "APD02", text: "Application 권한 회수"},
                {value: "APD03", text: "Application 계정 삭제"},
                {value: "APD04", text: "Application 관리자 권한 제한"},
                {value: "APD05", text: "Application 권한 Monitoring"},
                {value: "APD06", text: "Application 패스워드"},
                {value: "APD07", text: "Data 직접변경 승인"},
                {value: "APD08", text: "Data 직접변경 권한 제한"},
                {value: "APD09", text: "DB 접근권한 승인"},
                {value: "APD10", text: "DB 패스워드"},
                {value: "APD11", text: "DB 관리자 권한 제한"},
                {value: "APD12", text: "OS 접근권한 승인"},
                {value: "APD13", text: "OS 패스워드"},
                {value: "APD14", text: "OS 관리자 권한 제한"}
            ],
            PC: [
                {value: "PC01", text: "프로그램 변경 승인"},
                {value: "PC02", text: "프로그램 변경 사용자 테스트"},
                {value: "PC03", text: "프로그램 이관 승인"},
                {value: "PC04", text: "개발/운영 환경 분리"},
                {value: "PC05", text: "이관담당자 권한 제한"},
                {value: "PC06", text: "인프라 설정변경_DB"},
                {value: "PC07", text: "인프라 설정변경_OS"}
            ],
            CO: [
                {value: "CO01", text: "배치잡 스케줄 등록 승인"},
                {value: "CO02", text: "배치잡 스케줄 등록 권한 제한"},
                {value: "CO03", text: "배치잡 스케줄 Monitoring"}
            ]
        };

        categorySelect.addEventListener("change", function () {
            const selectedCategory = categorySelect.value;
            nameSelect.innerHTML = "";

            options[selectedCategory].forEach(function (option) {
                const optionElement = document.createElement("option");
                optionElement.value = option.value;
                optionElement.text = option.text;
                nameSelect.appendChild(optionElement);
                updateContent();
            });
        });

        function updateContent() {
            const listBox = document.getElementById("param2");
            const selectedValue = listBox.value;
            const contentContainer = document.getElementById("contentContainer");
            // Clear existing content
            contentContainer.innerHTML = ``;

            if(selectedValue == "APD01") // Application 권한부여 승인
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_APD01.jsp' %}
                        `;
            }
            else if(selectedValue == "APD02") // Application 권한 회수
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_APD02.jsp' %}
                        `;
            }
            else if(selectedValue == "APD03") // Application 계정 삭제
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_APD03.jsp' %}
                        `;
            }
            else if(selectedValue == "APD04") // Application 관리자 권한 제한
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="APD04">
                        <br><br>
                        {% include 'link3_APD04.jsp' %}
                        `;
            }
            else if(selectedValue == "APD05") // Application 권한 Monitoring
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="APD05">
                        <br><br>
                        {% include 'link3_APD05.jsp' %}
                        `;
            }
            else if(selectedValue == "APD06") // Application 패스워드
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="APD06">
                        <br><br>
                        {% include 'link3_APD06.jsp' %}
                        `;
            }
            else if(selectedValue == "APD07") // Data 직접변경 승인
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_APD07.jsp' %}
                        `;
            }
            else if(selectedValue == "APD08") // Data 직접변경 권한 제한
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="APD08">
                        <br><br>
                        {% include 'link3_APD08.jsp' %}
                        `;
            }
            else if(selectedValue == "APD09") // DB 접근권한 승인
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_APD09.jsp' %}
                        `;
            }
            else if(selectedValue == "APD11") // DB 관리자 권한 제한
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="APD11">
                        <br><br>
                        {% include 'link3_APD11.jsp' %}
                        `;
            }
            else if(selectedValue == "APD12") // OS 접근권한 승인
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_APD12.jsp' %}
                        `;
            }
            else if(selectedValue == "APD14") // OS 관리자 권한 제한
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="APD14">
                        <br><br>
                        {% include 'link3_APD14.jsp' %}
                        `;
            }
            else if(selectedValue == "PC01") // 프로그램 변경 승인
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_PC01.jsp' %}
                        `;
            }
            else if(selectedValue == "PC02") // 프로그램 변경 사용자 테스트
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_PC02.jsp' %}
                        `;
            }
            else if(selectedValue == "PC03") // 프로그램 이관 승인
            {
                contentContainer.innerHTML = `
                        <br><br>
                        {% include 'link3_PC03.jsp' %}
                        `;
            }
            else if(selectedValue == "PC04") // 개발/운영 환경 분리
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="PC04">
                        <br><br>
                        {% include 'link3_PC04.jsp' %}
                        `;
            }
            else if(selectedValue == "PC05") // 이관담당자 권한 제한
            {
                contentContainer.innerHTML = `
                        <input type="hidden" id="param3" name="param3" value="PC05">
                        <br><br>
                        {% include 'link3_PC05.jsp' %}
                        `;
            }
            else{
                contentContainer.innerHTML = ``;
            }
        }
    </script>

</body>
</html>