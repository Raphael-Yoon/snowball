import sys
import os
sys.path.insert(0, 'c:/Pythons/snowball')

from db_config import get_db
from evaluation_utils import get_evaluation_status

with get_db() as conn:
    header = conn.execute('''
        SELECT header_id FROM sb_evaluation_header
        WHERE evaluation_name = ?
    ''', ('FY25_내부평가',)).fetchone()

    if header:
        status_info = get_evaluation_status(conn, header['header_id'])
        print(f"실시간 status: {status_info['status']}")
        print(f"설계평가: {status_info['design_completed_count']}/{status_info['design_total_count']}")
        print(f"운영평가: {status_info['operation_completed_count']}/{status_info['operation_total_count']}")
