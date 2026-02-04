from datetime import datetime

def test_conditional_questions(s_questions, get_conditional_questions):
    """
    조건부 질문 생략 로직을 테스트하는 함수
    """
    # 테스트 케이스들
    test_cases = [
        {
            'name': '모든 질문 표시 (기본)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 47
        },
        {
            'name': '3번 답변이 N (프로그램 변경 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'N', 'Y', 'Y', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 41
        },
        {
            'name': '4번 SaaS + 5번 SOC1 Report 발행 (11, 14~46번 질문 생략)',
            'answers': ['test@example.com', 'Test System', 'Y', 'Y', 'SaaS', 'Y', 'Y', 'Y'] + ['N'] * 40,
            'expected_count': 13
        }
    ]
    
    for test_case in test_cases:
        conditional_questions = get_conditional_questions(test_case['answers'])
        actual_count = len(conditional_questions)
        print(f"Test [{test_case['name']}]: Expected {test_case['expected_count']}, Actual {actual_count}")
    
    return True

def test_ai_review_feature(get_text_itgc, get_ai_review):
    """
    AI 검토 기능을 테스트하는 함수
    """
    test_answers = ['test@example.com', 'Test System', 'Y'] + ['N'] * 40
    test_textarea_answers = [''] * 43

    result = get_text_itgc(test_answers, 'APD01', test_textarea_answers, enable_ai_review=True)
    
    if 'AI_Review' in result:
        print("AI Review test passed")
        
    # 직접 AI 검토 함수 테스트
    test_content = "사용자 권한 부여 이력이 시스템에 기록되지 않아 모집단 확보가 불가합니다."
    direct_ai_result = get_ai_review(test_content, 'APD01')
    
    if direct_ai_result:
        print("Direct AI Review test passed")

    return result
