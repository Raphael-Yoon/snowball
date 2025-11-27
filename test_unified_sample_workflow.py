"""
Comprehensive test for unified sample storage with both design and operation evaluations
"""
import sys
import json
from auth import (
    save_design_evaluation, get_design_evaluations, get_design_evaluation_sample,
    save_operation_evaluation, get_operation_evaluation_samples,
    get_db
)

def test_unified_workflow():
    """Test complete workflow: design + operation evaluations with unified sample table"""

    print("=" * 70)
    print("Testing Unified Sample Storage Workflow")
    print("Design + Operation Evaluations")
    print("=" * 70)

    # Test configuration
    test_rcm_id = 2
    test_user_id = 'test_unified'
    test_control_code = 'APD01'
    design_session = '2024Q4_Design'
    operation_session = '2024Q4_Operation'

    # ====================================================================
    # STEP 1: Save Design Evaluation with sample data
    # ====================================================================
    print("\n[STEP 1] Saving Design Evaluation...")
    design_evaluation = {
        'description_adequacy': '적절',
        'improvement_suggestion': 'Design improvement',
        'overall_effectiveness': '효과적',
        'evaluation_rationale': 'Design rationale',
        'design_comment': 'Design comment',
        'recommended_actions': 'Design actions',
        'evaluation_evidence': json.dumps({
            'attribute0': '설계평가 증빙 내용',
            'attribute1': '설계평가 필드 1',
            'attribute2': '설계평가 필드 2'
        })
    }

    try:
        save_design_evaluation(
            test_rcm_id,
            test_control_code,
            test_user_id,
            design_evaluation,
            evaluation_session=design_session
        )
        print("  [OK] Design evaluation saved")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # ====================================================================
    # STEP 2: Verify design sample is stored with evaluation_type='design'
    # ====================================================================
    print("\n[STEP 2] Verifying design sample in database...")

    try:
        with get_db() as conn:
            # Get line_id for design evaluation
            line_record = conn.execute('''
                SELECT l.line_id
                FROM sb_design_evaluation_line l
                JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
                WHERE h.rcm_id = %s AND h.user_id = %s AND l.control_code = %s
                  AND h.evaluation_session = %s
            ''', (test_rcm_id, test_user_id, test_control_code, design_session)).fetchone()

            if not line_record:
                print("  [FAIL] Design line not found")
                return False

            design_line_id = line_record['line_id']
            print(f"  Design line_id: {design_line_id}")

            # Check design sample
            design_samples = conn.execute('''
                SELECT sample_id, sample_number, evaluation_type,
                       attribute0, attribute1, attribute2
                FROM sb_evaluation_sample
                WHERE line_id = %s AND evaluation_type = 'design'
            ''', (design_line_id,)).fetchall()

            if design_samples:
                sample = design_samples[0]
                print(f"  [OK] Design sample found:")
                print(f"      sample_id: {sample['sample_id']}")
                print(f"      evaluation_type: {sample['evaluation_type']}")
                print(f"      attribute0: {sample['attribute0']}")
            else:
                print("  [FAIL] No design sample found")
                return False

    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # ====================================================================
    # STEP 3: Save Operation Evaluation with multiple samples
    # ====================================================================
    print("\n[STEP 3] Saving Operation Evaluation...")

    # Note: Operation evaluation uses different line table and header
    # We need to get the operation evaluation line_id
    # For simplicity, let's directly insert operation samples

    operation_evaluation = {
        'sample_size': 3,
        'exception_count': 1,
        'mitigating_factors': 'Mitigation applied',
        'exception_details': 'Exception detail',
        'conclusion': '효과적',
        'improvement_plan': 'Improvement plan',
        'sample_lines': [
            {
                'sample_number': 1,
                'evidence': '운영평가 샘플 1',
                'result': 'no_exception',
                'mitigation': '',
                'attributes': {
                    'attribute0': '운영 샘플1 필드0',
                    'attribute1': '운영 샘플1 필드1'
                }
            },
            {
                'sample_number': 2,
                'evidence': '운영평가 샘플 2',
                'result': 'exception',
                'mitigation': '예외 완화조치',
                'attributes': {
                    'attribute0': '운영 샘플2 필드0',
                    'attribute1': '운영 샘플2 필드1'
                }
            },
            {
                'sample_number': 3,
                'evidence': '운영평가 샘플 3',
                'result': 'no_exception',
                'mitigation': '',
                'attributes': {
                    'attribute0': '운영 샘플3 필드0',
                    'attribute1': '운영 샘플3 필드1'
                }
            }
        ]
    }

    try:
        save_operation_evaluation(
            test_rcm_id,
            test_control_code,
            test_user_id,
            operation_session,
            design_session,
            operation_evaluation
        )
        print("  [OK] Operation evaluation saved")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # ====================================================================
    # STEP 4: Verify both design and operation samples coexist
    # ====================================================================
    print("\n[STEP 4] Verifying both sample types coexist...")

    try:
        with get_db() as conn:
            # Get operation line_id
            op_line_record = conn.execute('''
                SELECT l.line_id
                FROM sb_operation_evaluation_line l
                JOIN sb_operation_evaluation_header h ON l.header_id = h.header_id
                WHERE h.rcm_id = %s AND h.user_id = %s AND l.control_code = %s
                  AND h.evaluation_session = %s
            ''', (test_rcm_id, test_user_id, test_control_code, operation_session)).fetchone()

            if not op_line_record:
                print("  [FAIL] Operation line not found")
                return False

            operation_line_id = op_line_record['line_id']
            print(f"  Operation line_id: {operation_line_id}")

            # Check ALL samples for this line_id
            all_samples = conn.execute('''
                SELECT sample_id, sample_number, evaluation_type, attribute0
                FROM sb_evaluation_sample
                WHERE line_id = %s
                ORDER BY evaluation_type, sample_number
            ''', (operation_line_id,)).fetchall()

            print(f"  Total samples for operation line_id {operation_line_id}: {len(all_samples)}")

            design_count = 0
            operation_count = 0

            for sample in all_samples:
                print(f"    - sample_id={sample['sample_id']}, "
                      f"type={sample['evaluation_type']}, "
                      f"#={sample['sample_number']}, "
                      f"attr0={sample['attribute0'][:20]}...")

                if sample['evaluation_type'] == 'design':
                    design_count += 1
                elif sample['evaluation_type'] == 'operation':
                    operation_count += 1

            # Note: Design and operation use different line tables!
            # So we shouldn't expect design samples for operation_line_id
            print(f"\n  Design samples: {design_count}")
            print(f"  Operation samples: {operation_count}")

            if operation_count == 3:
                print("  [OK] Operation samples count correct (3)")
            else:
                print(f"  [FAIL] Expected 3 operation samples, got {operation_count}")
                return False

    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # ====================================================================
    # STEP 5: Test retrieving samples via API functions
    # ====================================================================
    print("\n[STEP 5] Testing sample retrieval via API...")

    # 5a. Get design samples
    print("  5a. Retrieving design evaluation sample...")
    try:
        design_sample = get_design_evaluation_sample(design_line_id)
        if design_sample:
            print(f"      [OK] Design sample retrieved:")
            print(f"          attributes: {design_sample['attributes']}")
        else:
            print("      [FAIL] No design sample retrieved")
            return False
    except Exception as e:
        print(f"      [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # 5b. Get operation samples
    print("  5b. Retrieving operation evaluation samples...")
    try:
        operation_samples = get_operation_evaluation_samples(operation_line_id)
        if operation_samples:
            print(f"      [OK] {len(operation_samples)} operation samples retrieved")
            for idx, sample in enumerate(operation_samples, 1):
                print(f"          Sample #{idx}: {sample['attributes'].get('attribute0', 'N/A')[:30]}...")
        else:
            print("      [FAIL] No operation samples retrieved")
            return False
    except Exception as e:
        print(f"      [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False

    # ====================================================================
    # STEP 6: Verify design sample is NOT deleted when saving operation
    # ====================================================================
    print("\n[STEP 6] Verifying design sample preservation...")

    try:
        with get_db() as conn:
            # Check design sample still exists
            design_sample_check = conn.execute('''
                SELECT COUNT(*) as count
                FROM sb_evaluation_sample
                WHERE line_id = %s AND evaluation_type = 'design'
            ''', (design_line_id,)).fetchone()

            if design_sample_check['count'] == 1:
                print(f"  [OK] Design sample preserved (count={design_sample_check['count']})")
            else:
                print(f"  [FAIL] Design sample count mismatch: {design_sample_check['count']}")
                return False

    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_unified_workflow()
    sys.exit(0 if success else 1)
