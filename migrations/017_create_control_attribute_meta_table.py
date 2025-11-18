"""
Migration 017: Create sb_control_attribute_meta table
"""

def upgrade(conn):
    """
    Creates the sb_control_attribute_meta table to store metadata for attribute columns.
    """
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sb_control_attribute_meta (
            meta_id INTEGER PRIMARY KEY AUTOINCREMENT,
            control_code TEXT NOT NULL,
            attribute_name TEXT NOT NULL,
            attribute_label TEXT NOT NULL,
            display_order INTEGER DEFAULT 0,
            UNIQUE(control_code, attribute_name)
        )
    ''')
    
    conn.commit()
    print("  - Created 'sb_control_attribute_meta' table.")

def downgrade(conn):
    """
    Drops the sb_control_attribute_meta table.
    """
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS sb_control_attribute_meta")
    conn.commit()
    print("  - Dropped 'sb_control_attribute_meta' table.")