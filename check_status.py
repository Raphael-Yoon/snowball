import sqlite3

conn = sqlite3.connect('c:/Python/snowball/snowball.db')
conn.row_factory = sqlite3.Row

cursor = conn.execute('''
    SELECT
        dh.rcm_id,
        dh.evaluation_session,
        dh.evaluation_status,
        oh.evaluation_status as operation_status
    FROM sb_design_evaluation_header dh
    LEFT JOIN sb_operation_evaluation_header oh
        ON dh.rcm_id = oh.rcm_id
        AND dh.evaluation_session = oh.design_evaluation_session
        AND dh.user_id = oh.user_id
    WHERE dh.evaluation_status != 'ARCHIVED'
''')

rows = cursor.fetchall()
print('=' * 70)
print('현재 내부평가 상태:')
print('=' * 70)
for row in rows:
    print(f'RCM ID: {row[0]}, 세션: {row[1]}')
    print(f'  설계평가: {row[2]}')
    print(f'  운영평가: {row[3] if row[3] else "시작 전"}')
    print('-' * 70)

conn.close()
