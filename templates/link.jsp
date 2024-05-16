<!DOCTYPE html>
<html>
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <meta charset="UTF-8">
    <title>SnowBall</title>
</head>
<body>
    {% include 'navi.jsp' %}
    <div style="text-align: center;">
        <form class = "grid" action="/set_regist" method = "POST" enctype="multipart/form-data">
            <table class="table">
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">회사명</th>
                    <th scope="col">담당자</th>
                    <th scope="col">이메일</th>
                    <th scope="col">확인 여부</th>
                    <th scope="col">날짜</th>
                </tr>
                {% for row in user_request %}
                <tr>
                    <td><input type="checkbox" id="regist_check" name="regist_check" {% if row[3] == "Y"%}disabled{% endif %}></td>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[2] }}</td>
                    <td>{{ row[3] }}</td>
                    <td>{{ row[4] }}</td>
                    <td><input type="text" id="request_id" name="request_id" value="{{ row[5] }}"{{ row[5] }}></td>
                </tr>
                {% endfor %}
            </table>
            <input type="Submit" class="btn btn-outline-primary" value="Apply" formaction="/set_regist" style="float:right" onclick="sendCheckedData()">
        </form>
        <script>
            function sendCheckedData() {
                const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
                const checkedData = Array.from(checkboxes).map(checkbox => {
                    const row = checkbox.closest('tr');
                    const company = row.querySelector('td:nth-child(2)').textContent;
                    const manager = row.querySelector('td:nth-child(3)').textContent;
                    const email = row.querySelector('td:nth-child(4)').textContent;
                    const date = row.querySelector('td:nth-child(5)').textContent;
                    const request_id = row.querySelector('td:nth-child(6)').textContent;
                    return { company, manager, email, date, request_id};
                });
            
                // 여기서 checkedData를 서버로 전송하거나 원하는 작업을 수행하세요.
                // 예를 들면 fetch API를 사용하여 서버로 POST 요청을 보낼 수 있습니다.
            }
        </script>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
</body>
</html>