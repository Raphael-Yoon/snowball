import sqlite3

conn = sqlite3.connect('c:\\Pythons\\snowball\\snowball.db')
conn.row_factory = sqlite3.Row

# FY25_내부평가 정보 확인
print("=== FY25_내부평가 정보 ===")
header = conn.execute("""
    SELECT * FROM sb_evaluation_header
    WHERE evaluation_name = 'FY25_내부평가' AND rcm_id = 18
""").fetchone()
print(dict(header))

# 직접 쿼리 테스트 (evaluation_session 사용)
print("\n=== 직접 쿼리 테스트 ===")
query = '''
    SELECT v.detail_id, v.rcm_id, v.control_code, v.control_name, v.control_description,
           v.key_control, v.control_frequency, v.control_type, v.control_nature,
           v.population, v.population_completeness_check, v.population_count, v.test_procedure,
           v.mapped_std_control_id, v.mapped_date, v.mapped_by,
           v.ai_review_status, v.ai_review_recommendation, v.ai_reviewed_date, v.ai_reviewed_by,
           v.mapping_status, v.control_category, v.recommended_sample_size, v.population_attribute_count,
           v.attribute0, v.attribute1, v.attribute2, v.attribute3, v.attribute4,
           v.attribute5, v.attribute6, v.attribute7, v.attribute8, v.attribute9,
           v.control_frequency_code, v.control_type_code, v.control_nature_code,
           v.control_frequency_name, v.control_type_name, v.control_nature_name,
           line.line_id
    FROM sb_rcm_detail_v v
    INNER JOIN sb_evaluation_line line ON v.control_code = line.control_code
    INNER JOIN sb_evaluation_header h ON line.header_id = h.header_id
    WHERE v.rcm_id = ? AND h.evaluation_name = ? AND h.rcm_id = ?
'''

params = (18, 'FY25_내부평가', 18)
results = conn.execute(query, params).fetchall()
print(f"조회된 레코드 수: {len(results)}")

if results:
    print(f"\n첫 번째 레코드:")
    print(f"  control_code: {results[0]['control_code']}")
    print(f"  control_name: {results[0]['control_name']}")
    print(f"  line_id: {results[0]['line_id']}")

# control_category 필터 추가 테스트
print("\n=== control_category='ELC' 필터 추가 ===")
query_with_category = query + " AND v.control_category = ?"
params_with_category = (18, 'FY25_내부평가', 18, 'ELC')
results_elc = conn.execute(query_with_category, params_with_category).fetchall()
print(f"조회된 ELC 레코드 수: {len(results_elc)}")

conn.close()
