"""Check available RCM IDs in the database"""
from auth import get_db

with get_db() as conn:
    # Get RCM IDs and their details
    rcms = conn.execute('''
        SELECT rcm_id, rcm_name, control_category, is_active
        FROM sb_rcm
        WHERE is_active = 'Y'
        ORDER BY rcm_id DESC
        LIMIT 10
    ''').fetchall()

    print("Available Active RCMs in database:")
    print("=" * 60)
    for rcm in rcms:
        print(f"RCM ID: {rcm['rcm_id']}")
        print(f"  Name: {rcm['rcm_name']}")
        print(f"  Category: {rcm['control_category']}")
        print(f"  Active: {rcm['is_active']}")

        # Check if it has details
        details = conn.execute('''
            SELECT COUNT(*) as count, MIN(control_code) as first_code
            FROM sb_rcm_detail
            WHERE rcm_id = %s
        ''', (rcm['rcm_id'],)).fetchone()

        print(f"  Details: {details['count']} controls (first: {details['first_code']})")
        print()
