"""
Test the complete design evaluation save/load workflow
"""
import sys
import json
from auth import save_design_evaluation, get_design_evaluations, get_db

def test_save_load_workflow():
    """Test saving and loading design evaluation with sample data"""

    print("=" * 60)
    print("Testing Design Evaluation Save/Load Workflow")
    print("=" * 60)

    # Test data
    test_rcm_id = 2  # Test RCM (ITGC)
    test_user_id = 'test_user'
    test_control_code = 'APD01'  # First control code from RCM 2

    # Create test evaluation data
    test_evaluation = {
        'description_adequacy': '적절',
        'improvement_suggestion': 'Test improvement suggestion',
        'overall_effectiveness': '효과적',
        'evaluation_rationale': 'Test rationale',
        'design_comment': 'Test design comment',
        'recommended_actions': 'Test recommended actions',
        'evaluation_evidence': json.dumps({
            'attribute0': '기본 증빙 내용',
            'attribute1': '추가 필드 1',
            'attribute2': '추가 필드 2',
            'attribute3': '추가 필드 3'
        })
    }

    print("\n1. Saving design evaluation...")
    print(f"   RCM ID: {test_rcm_id}")
    print(f"   User ID: {test_user_id}")
    print(f"   Control Code: {test_control_code}")
    print(f"   Evidence Data: {test_evaluation['evaluation_evidence']}")

    try:
        # Save the evaluation
        save_design_evaluation(
            test_rcm_id,
            test_control_code,
            test_user_id,
            test_evaluation,
            evaluation_session='2024Q4'
        )
        print("   [OK] Save completed")
    except Exception as e:
        print(f"   [FAIL] Save failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n2. Verifying sample table...")
    # Check if data was saved to sample table
    try:
        with get_db() as conn:
            # Find the line_id
            line_record = conn.execute('''
                SELECT l.line_id
                FROM sb_design_evaluation_line l
                JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
                WHERE h.rcm_id = %s AND h.user_id = %s AND l.control_code = %s
            ''', (test_rcm_id, test_user_id, test_control_code)).fetchone()

            if line_record:
                line_id = line_record['line_id']
                print(f"   Found line_id: {line_id}")

                # Check sample table
                sample = conn.execute('''
                    SELECT sample_id, sample_number, evaluation_type,
                           attribute0, attribute1, attribute2, attribute3
                    FROM sb_evaluation_sample
                    WHERE line_id = %s AND evaluation_type = 'design'
                ''', (line_id,)).fetchone()

                if sample:
                    print(f"   [OK] Sample found in table")
                    print(f"       sample_id: {sample['sample_id']}")
                    print(f"       sample_number: {sample['sample_number']}")
                    print(f"       evaluation_type: {sample['evaluation_type']}")
                    print(f"       attribute0: {sample['attribute0']}")
                    print(f"       attribute1: {sample['attribute1']}")
                    print(f"       attribute2: {sample['attribute2']}")
                    print(f"       attribute3: {sample['attribute3']}")
                else:
                    print("   [FAIL] No sample found in table")
                    return False
            else:
                print("   [FAIL] Line record not found")
                return False

    except Exception as e:
        print(f"   [FAIL] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n3. Loading design evaluation...")
    try:
        # Load the evaluation
        evaluations = get_design_evaluations(test_rcm_id, test_user_id, '2024Q4')

        if evaluations:
            print(f"   [OK] Loaded {len(evaluations)} evaluation(s)")

            # Find our test evaluation
            test_eval = None
            for eval_record in evaluations:
                if eval_record['control_code'] == test_control_code:
                    test_eval = eval_record
                    break

            if test_eval:
                print(f"   Found test evaluation:")
                print(f"       Control Code: {test_eval['control_code']}")
                print(f"       Overall Effectiveness: {test_eval['overall_effectiveness']}")

                # Check if evaluation_evidence was reconstructed
                if 'evaluation_evidence' in test_eval and test_eval['evaluation_evidence']:
                    evidence = json.loads(test_eval['evaluation_evidence'])
                    print(f"   [OK] Evaluation evidence reconstructed:")
                    print(f"       {json.dumps(evidence, ensure_ascii=False, indent=8)}")

                    # Verify data integrity
                    expected = json.loads(test_evaluation['evaluation_evidence'])
                    if (evidence['attribute0'] == expected['attribute0'] and
                        evidence['attribute1'] == expected['attribute1'] and
                        evidence['attribute2'] == expected['attribute2'] and
                        evidence['attribute3'] == expected['attribute3']):
                        print("   [OK] Data integrity verified!")
                    else:
                        print("   [FAIL] Data mismatch!")
                        return False
                else:
                    print("   [FAIL] evaluation_evidence not found or empty")
                    return False
            else:
                print(f"   [FAIL] Test evaluation not found in results")
                return False
        else:
            print("   [FAIL] No evaluations loaded")
            return False

    except Exception as e:
        print(f"   [FAIL] Load failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_save_load_workflow()
    sys.exit(0 if success else 1)
