import sqlite3

conn = sqlite3.connect('c:\\Pythons\\snowball\\snowball.db')
conn.row_factory = sqlite3.Row

# rcm_id=18의 정보 확인
print("=== RCM ID 18 정보 ===")
rcm = conn.execute("SELECT * FROM sb_rcm WHERE rcm_id = 18").fetchone()
if rcm:
    print(dict(rcm))
else:
    print("RCM ID 18을 찾을 수 없습니다.")

# rcm_id=18의 통제 카테고리 확인
print("\n=== RCM ID 18의 통제 카테고리별 개수 ===")
categories = conn.execute("""
    SELECT control_category, COUNT(*) as count
    FROM sb_rcm_detail
    WHERE rcm_id = 18
    GROUP BY control_category
""").fetchall()
for cat in categories:
    print(f"{cat['control_category']}: {cat['count']}개")

# FY25_내부평가의 통제 카테고리 확인
print("\n=== FY25_내부평가의 통제 카테고리 ===")
eval_categories = conn.execute("""
    SELECT DISTINCT v.control_category, COUNT(*) as count
    FROM sb_rcm_detail_v v
    INNER JOIN sb_evaluation_line line ON v.control_code = line.control_code
    INNER JOIN sb_evaluation_header h ON line.header_id = h.header_id
    WHERE h.evaluation_name = 'FY25_내부평가' AND h.rcm_id = 18
    GROUP BY v.control_category
""").fetchall()
for cat in eval_categories:
    print(f"{cat['control_category']}: {cat['count']}개")

conn.close()
