<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    {% include 'navi.jsp' %}
    <form class = "grid" action = "/paper_generate" method="post">
        <select name="param1" id="param1">
            <option value="APD" checked>Access Program & Data</option>
            <option value="PC">Program Change</option>
            <option value="CO">Computer Operation</option>
        </select>
        <select name="param2" id="param2" onchange="updateContent()">
            <option value="APD01">Application 권한부여 승인</option>
            <option value="APD02">Application 권한 회수</option> 
            <option value="APD03">Application 계정 삭제</option>
            <option value="APD04">Application 관리자 권한 제한</option>
            <option value="APD05">Application 패스워드</option>
            <option value="APD06">Application 권한 Monitoring</option>
            <option value="APD07">Data 직접변경 승인</option>
            <option value="APD08">Data 직접변경 권한 제한</option>
            <option value="APD09">DB 접근권한 승인</option>
            <option value="APD10">DB 패스워드</option>
            <option value="APD11">DB 관리자 권한 제한</option>
            <option value="APD12">OS 접근권한 승인</option>
            <option value="APD13">OS 패스워드</option>
            <option value="APD14">OS 관리자 권한 제한</option>
        </select>
        <input type="submit" value="Run!!!">
        <div id="contentContainer">
            <p>Select an option to see content.</p>
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
                {value: "APD05", text: "Application 패스워드"},
                {value: "APD06", text: "Application 권한 Monitoring"},
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
                {value: "PC04", text: "이관담당자 권한 제한"},
                {value: "PC05", text: "인프라 설정변경_DB"},
                {value: "PC06", text: "인프라 설정변경_OS"}
            ],
            CO: [
                { value: "CO01", text: "배치잡 스케줄 등록 승인" },
                { value: "CO02", text: "배치잡 스케줄 등록 권한 제한" },
                { value: "CO03", text: "배치잡 Monitoring" }
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
            });
        });

        function updateContent() {
            const listBox = document.getElementById("param2");
            const selectedValue = listBox.value;
            const contentContainer = document.getElementById("contentContainer");
            // Clear existing content
            contentContainer.innerHTML = "";

            // Add new content based on selected value
            switch (selectedValue) {
                case "APD01":
                    contentContainer.innerHTML = "<p>Option 1 content goes here.</p>";
                    break;
                case "APD02":
                    contentContainer.innerHTML = `
                        <p>Option 2 content goes here.</p>
                        <input type="text" placeholder="Edit Box 1">
                        <input type="text" placeholder="Edit Box 2">
                    `;
                    break;
                case "APD05":
                    contentContainer.innerHTML = `
                        <table>
                            <tr>
                                <td>최소자리</td>
                                <td><input type="text" id="param3" name="param3"></td>
                            </tr>
                            <tr>
                                <td>복잡성</td>
                                <td><input type="text" id="param4" name="param4"></td>
                            </tr>
                            <tr>
                                <td>변경주기</td>
                                <td><input type="text" id="param5" name="param5"></td>
                            </tr>
                        </table>
                    `;
                    break;
                default:
                    contentContainer.innerHTML = "<p>Select an option to see content.</p>";
            }
        }
    </script>

</body>
</html>