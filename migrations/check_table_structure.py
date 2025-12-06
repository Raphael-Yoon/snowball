import sys
import os
project_root = os.path.join(os.path.dirname(__file__), 'snowball')
sys.path.insert(0, project_root)
os.chdir(project_root)

from db_config import get_db

with get_db() as conn:
    print("=== sb_design_evaluation_header ===")
    result = conn.execute('PRAGMA table_info(sb_design_evaluation_header)').fetchall()
    for r in result:
        print(dict(r))

    print("\n=== sb_operation_evaluation_header ===")
    result = conn.execute('PRAGMA table_info(sb_operation_evaluation_header)').fetchall()
    for r in result:
        print(dict(r))
