import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    # APD06 RCM 상세 정보 확인
    result = conn.execute('''
        SELECT d.control_code, d.population_attribute_count,
               d.attribute0, d.attribute1, d.attribute2, d.attribute3, d.attribute4,
               d.attribute5, d.attribute6, d.attribute7, d.attribute8, d.attribute9
        FROM sb_rcm_detail d
        WHERE d.rcm_id = 2 AND d.control_code = 'APD06'
    ''').fetchone()

    if result:
        data = dict(result)
        print("=== APD06 RCM Detail ===")
        print(f"control_code: {data['control_code']}")
        print(f"population_attribute_count: {data['population_attribute_count']}")
        for i in range(10):
            attr_val = data.get(f'attribute{i}')
            if attr_val:
                print(f"  attribute{i}: {attr_val}")
    else:
        print("APD06 데이터를 찾을 수 없습니다.")
