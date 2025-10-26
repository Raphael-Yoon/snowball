#!/usr/bin/env python3
"""
실제 조건부 스킵 로직이 제대로 작동하는지 테스트
"""
import sys
sys.path.insert(0, '/Users/newsistraphael/Pythons/snowball')

from snowball_link2 import get_conditional_questions, s_questions, question_count

def test_skip_logic():
    print("=" * 80)
    print("조건부 질문 스킵 로직 동작 테스트")
    print("=" * 80)

    # 테스트 시나리오 1: Q3='N' (Cloud 사용 안함)
    print("\n[테스트 1] Q3='N' (Cloud 서비스 사용 안함)")
    print("-" * 80)

    answers = [''] * question_count
    answers[3] = 'N'  # Cloud 사용 안함

    filtered = get_conditional_questions(answers)
    question_indices = [q['index'] for q in filtered]

    print(f"전체 질문 수: {question_count}")
    print(f"필터링 후 질문 수: {len(filtered)}")
    print(f"\n스킵된 질문:")

    skipped = []
    for i in range(question_count):
        if i not in question_indices:
            skipped.append(i)
            print(f"  - Q{i}: {s_questions[i]['text'][:50]}...")

    # Q4, Q5가 스킵되는지 확인
    if 4 in skipped and 5 in skipped:
        print("\n✅ 정상: Q3='N'일 때 Q4, Q5가 스킵됨")
    else:
        print("\n❌ 오류: Q3='N'일 때 Q4, Q5가 스킵되지 않음!")
        if 4 not in skipped:
            print(f"   Q4는 스킵되지 않았습니다")
        if 5 not in skipped:
            print(f"   Q5는 스킵되지 않았습니다")

    # 테스트 시나리오 2: Q14='N' (DB 접속 불가)
    print("\n" + "=" * 80)
    print("[테스트 2] Q14='N' (DB 접속 불가)")
    print("-" * 80)

    answers = [''] * question_count
    answers[14] = 'N'  # DB 접속 불가

    filtered = get_conditional_questions(answers)
    question_indices = [q['index'] for q in filtered]

    skipped = []
    for i in range(question_count):
        if i not in question_indices:
            skipped.append(i)

    print(f"스킵된 질문: Q{min(skipped) if skipped else 'None'}~Q{max(skipped) if skipped else 'None'}")

    # Q15~Q23이 스킵되는지 확인
    expected_skip = list(range(15, 24))  # 15~23
    if all(q in skipped for q in expected_skip):
        print(f"✅ 정상: Q14='N'일 때 Q15~Q23이 스킵됨")
    else:
        print(f"❌ 오류: Q14='N'일 때 Q15~Q23이 제대로 스킵되지 않음!")

    # 테스트 시나리오 3: Q24='N' (OS 접속 불가)
    print("\n" + "=" * 80)
    print("[테스트 3] Q24='N' (OS 접속 불가)")
    print("-" * 80)

    answers = [''] * question_count
    answers[24] = 'N'  # OS 접속 불가

    filtered = get_conditional_questions(answers)
    question_indices = [q['index'] for q in filtered]

    skipped = []
    for i in range(question_count):
        if i not in question_indices:
            skipped.append(i)

    # Q25~Q30이 스킵되는지 확인
    expected_skip = list(range(25, 31))  # 25~30
    if all(q in skipped for q in expected_skip):
        print(f"✅ 정상: Q24='N'일 때 Q25~Q30이 스킵됨")
    else:
        print(f"❌ 오류: Q24='N'일 때 Q25~Q30이 제대로 스킵되지 않음!")

    # 테스트 시나리오 4: Q31='N' (프로그램 변경 불가)
    print("\n" + "=" * 80)
    print("[테스트 4] Q31='N' (프로그램 변경 불가)")
    print("-" * 80)

    answers = [''] * question_count
    answers[31] = 'N'  # 프로그램 변경 불가

    filtered = get_conditional_questions(answers)
    question_indices = [q['index'] for q in filtered]

    skipped = []
    for i in range(question_count):
        if i not in question_indices:
            skipped.append(i)

    # Q32~Q37이 스킵되는지 확인
    expected_skip = list(range(32, 38))  # 32~37
    if all(q in skipped for q in expected_skip):
        print(f"✅ 정상: Q31='N'일 때 Q32~Q37이 스킵됨")
    else:
        print(f"❌ 오류: Q31='N'일 때 Q32~Q37이 제대로 스킵되지 않음!")

    # 테스트 시나리오 5: Q38='N' (배치 스케줄 없음)
    print("\n" + "=" * 80)
    print("[테스트 5] Q38='N' (배치 스케줄 없음)")
    print("-" * 80)

    answers = [''] * question_count
    answers[38] = 'N'  # 배치 스케줄 없음

    filtered = get_conditional_questions(answers)
    question_indices = [q['index'] for q in filtered]

    skipped = []
    for i in range(question_count):
        if i not in question_indices:
            skipped.append(i)

    # Q39~Q43이 스킵되는지 확인
    expected_skip = list(range(39, 44))  # 39~43
    if all(q in skipped for q in expected_skip):
        print(f"✅ 정상: Q38='N'일 때 Q39~Q43이 스킵됨")
    else:
        print(f"❌ 오류: Q38='N'일 때 Q39~Q43이 제대로 스킵되지 않음!")

    print("\n" + "=" * 80)
    print("결론")
    print("=" * 80)
    print("조건부 스킵 로직이 제대로 작동하면, 스킵샘플의 답변은")
    print("단순히 '빠른 테스트용 샘플'일 뿐이며 논리적 모순이 아닙니다.")
    print("스킵될 질문에 기본값이 있어도 실제로는 표시되지 않습니다.")

if __name__ == '__main__':
    test_skip_logic()
