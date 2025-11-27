"""
Test script for unified sample storage in sb_evaluation_sample table
"""
import sqlite3
import json

def test_table_structure():
    """Check if sb_evaluation_sample table has all required columns"""
    conn = sqlite3.connect('snowball.db')
    cursor = conn.cursor()

    # Get table info
    cursor.execute("PRAGMA table_info(sb_evaluation_sample)")
    columns = cursor.fetchall()

    print("=== sb_evaluation_sample Table Structure ===")
    for col in columns:
        print(f"  {col[1]}: {col[2]} (Default: {col[4]})")

    # Check for required columns
    column_names = [col[1] for col in columns]
    required_columns = [
        'sample_id', 'line_id', 'sample_number', 'evaluation_type',
        'attribute0', 'attribute1', 'attribute2', 'attribute3', 'attribute4',
        'attribute5', 'attribute6', 'attribute7', 'attribute8', 'attribute9'
    ]

    print("\n=== Column Check ===")
    for col in required_columns:
        status = "[OK]" if col in column_names else "[MISSING]"
        print(f"  {status} {col}")

    conn.close()

def test_sample_insert():
    """Test inserting a design evaluation sample"""
    conn = sqlite3.connect('snowball.db')
    cursor = conn.cursor()

    print("\n=== Test Sample Insert ===")

    # Create test data
    test_line_id = 999999  # Use a test line_id that won't conflict
    test_data = {
        'attribute0': '테스트 증빙 내용',
        'attribute1': '추가 정보 1',
        'attribute2': '추가 정보 2'
    }

    # Delete any existing test data
    cursor.execute('DELETE FROM sb_evaluation_sample WHERE line_id = ?', (test_line_id,))

    # Insert test sample
    try:
        cursor.execute('''
            INSERT INTO sb_evaluation_sample (
                line_id, sample_number, evaluation_type,
                attribute0, attribute1, attribute2, attribute3, attribute4,
                attribute5, attribute6, attribute7, attribute8, attribute9
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_line_id, 1, 'design',
            test_data.get('attribute0', ''),
            test_data.get('attribute1', ''),
            test_data.get('attribute2', ''),
            test_data.get('attribute3', ''),
            test_data.get('attribute4', ''),
            test_data.get('attribute5', ''),
            test_data.get('attribute6', ''),
            test_data.get('attribute7', ''),
            test_data.get('attribute8', ''),
            test_data.get('attribute9', '')
        ))
        conn.commit()
        print("  [OK] Insert successful")
    except Exception as e:
        print(f"  [FAIL] Insert failed: {e}")
        conn.rollback()
        conn.close()
        return False

    # Verify the insert
    cursor.execute('''
        SELECT sample_id, line_id, sample_number, evaluation_type,
               attribute0, attribute1, attribute2
        FROM sb_evaluation_sample
        WHERE line_id = ? AND evaluation_type = 'design'
    ''', (test_line_id,))

    row = cursor.fetchone()
    if row:
        print(f"  [OK] Retrieved sample_id: {row[0]}")
        print(f"    line_id: {row[1]}, sample_number: {row[2]}, type: {row[3]}")
        print(f"    attribute0: {row[4]}")
        print(f"    attribute1: {row[5]}")
        print(f"    attribute2: {row[6]}")
    else:
        print("  [FAIL] No data retrieved")

    # Clean up
    cursor.execute('DELETE FROM sb_evaluation_sample WHERE line_id = ?', (test_line_id,))
    conn.commit()
    conn.close()

    return True

def test_json_reconstruction():
    """Test reconstructing evaluation_evidence JSON from sample attributes"""
    conn = sqlite3.connect('snowball.db')
    cursor = conn.cursor()

    print("\n=== Test JSON Reconstruction ===")

    # Insert test data
    test_line_id = 999998
    cursor.execute('DELETE FROM sb_evaluation_sample WHERE line_id = ?', (test_line_id,))

    cursor.execute('''
        INSERT INTO sb_evaluation_sample (
            line_id, sample_number, evaluation_type,
            attribute0, attribute1, attribute2, attribute3, attribute4,
            attribute5, attribute6, attribute7, attribute8, attribute9
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_line_id, 1, 'design',
        'Test evidence',
        'Field 1',
        'Field 2',
        '', '', '', '', '', '', ''
    ))
    conn.commit()

    # Reconstruct JSON
    cursor.execute('''
        SELECT attribute0, attribute1, attribute2, attribute3, attribute4,
               attribute5, attribute6, attribute7, attribute8, attribute9
        FROM sb_evaluation_sample
        WHERE line_id = ? AND evaluation_type = 'design'
    ''', (test_line_id,))

    row = cursor.fetchone()
    if row:
        attr_data = {}
        for i, value in enumerate(row):
            if value:  # Only include non-empty attributes
                attr_data[f'attribute{i}'] = value

        json_str = json.dumps(attr_data, ensure_ascii=False)
        print(f"  Reconstructed JSON: {json_str}")

        # Parse back
        parsed = json.loads(json_str)
        print(f"  [OK] Parsed back: {parsed}")

    # Clean up
    cursor.execute('DELETE FROM sb_evaluation_sample WHERE line_id = ?', (test_line_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Testing unified sample storage implementation\n")
    print("=" * 60)

    test_table_structure()
    test_sample_insert()
    test_json_reconstruction()

    print("\n" + "=" * 60)
    print("Test complete!")
