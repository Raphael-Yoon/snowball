import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from auth import get_user_rcms

# 사용자 ID 1번으로 테스트 (관리자)
rcm_list = get_user_rcms(1)

print("=== RCM 목록 및 평가 상태 ===")
for rcm in rcm_list:
    print(f"\nRCM {rcm['rcm_id']}: {rcm['rcm_name']}")
    print(f"  회사: {rcm['company_name']}")
    print(f"  카테고리: {rcm['control_category']}")
    print(f"  평가 상태: [{rcm['evaluation_status']}] {rcm['evaluation_status_text']}")
