import sqlite3

conn = sqlite3.connect('snowball.db')
cursor = conn.execute('''
    SELECT id, text, type, parent_question_id 
    FROM sb_disclosure_questions 
    WHERE category_id = 1 
    ORDER BY sort_order
''')

with open('questions_cat1.txt', 'w', encoding='utf-8') as f:
    f.write("카테고리 1: 정보보호 투자 질문 목록\n")
    f.write("=" * 100 + "\n\n")
    for row in cursor.fetchall():
        qid, text, qtype, parent = row
        parent_str = f"(부모: {parent})" if parent else ""
        f.write(f"{qid:10} | {qtype:12} | {text:60} {parent_str}\n")

conn.close()
print("questions_cat1.txt 파일에 저장 완료!")
