import sqlite3

conn = sqlite3.connect('snowball.db')

# 운영평가 헤더 조회 (rcm_id = 9, 쿠쿠홈시스 ELC)
print("=== Operation Evaluation Headers (rcm_id=9) ===")
cursor = conn.execute('''
    SELECT header_id, evaluation_session, design_evaluation_session,
           evaluation_status, evaluated_controls, total_controls
    FROM sb_operation_evaluation_header
    WHERE rcm_id = 9
''')
for row in cursor.fetchall():
    print(row)

# 해당 헤더의 라인 데이터 통계
print("\n=== Operation Evaluation Line Stats ===")
cursor = conn.execute('''
    SELECT
        header_id,
        COUNT(*) as total_lines,
        COUNT(CASE WHEN conclusion IS NOT NULL AND conclusion != '' THEN 1 END) as completed_lines
    FROM sb_operation_evaluation_line
    WHERE header_id IN (SELECT header_id FROM sb_operation_evaluation_header WHERE rcm_id = 9)
    GROUP BY header_id
''')
for row in cursor.fetchall():
    print(f"header_id={row[0]}, total={row[1]}, completed={row[2]}")

conn.close()
