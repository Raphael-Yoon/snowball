import sqlite3

conn = sqlite3.connect('c:\\Pythons\\snowball\\snowball.db')
conn.row_factory = sqlite3.Row

# sb_evaluation_header 확인
print("=== sb_evaluation_header (FY25_내부평가) ===")
headers = conn.execute("SELECT * FROM sb_evaluation_header WHERE evaluation_name = 'FY25_내부평가'").fetchall()
for row in headers:
    print(dict(row))

# sb_evaluation_line 확인
if headers:
    print("\n=== sb_evaluation_line ===")
    for header in headers:
        header_id = header['header_id']
        count = conn.execute("SELECT COUNT(*) as cnt FROM sb_evaluation_line WHERE header_id = ?", (header_id,)).fetchone()['cnt']
        print(f"header_id={header_id}: {count} controls")

        if count > 0:
            lines = conn.execute("SELECT * FROM sb_evaluation_line WHERE header_id = ? LIMIT 3", (header_id,)).fetchall()
            for line in lines:
                print(f"  {dict(line)}")
else:
    print("FY25_내부평가를 찾을 수 없습니다.")

conn.close()
