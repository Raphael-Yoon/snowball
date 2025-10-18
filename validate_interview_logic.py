#!/usr/bin/env python3
"""
인터뷰 질문의 조건부 로직과 스킵샘플 데이터의 논리적 일관성을 검증하는 스크립트
"""

# 조건부 질문 스킵 로직 (snowball_link2.py에서 복사)
def get_skip_ranges(answers):
    """답변에 따른 스킵 범위 반환"""
    skip_ranges = []

    # 3번 답변이 N이면 4~5번, 47번 질문 생략 (Cloud 미사용)
    if len(answers) > 3 and answers[3] and str(answers[3]).upper() == 'N':
        skip_ranges.append((4, 5))
        skip_ranges.append((47, 47))

    # Cloud 스킵 조건
    has_soc1_report = len(answers) > 5 and answers[5] and str(answers[5]).upper() == 'Y'

    # 4번 답변이 SaaS이고 5번 답변이 Y이면
    if len(answers) > 4 and answers[4] and str(answers[4]) == 'SaaS' and has_soc1_report:
        skip_ranges.append((11, 11))
        skip_ranges.append((14, 46))

    # 4번 답변이 IaaS이고 5번 답변이 Y이면
    elif len(answers) > 4 and answers[4] and str(answers[4]) == 'IaaS' and has_soc1_report:
        skip_ranges.append((22, 22))
        skip_ranges.append((29, 29))
        skip_ranges.append((44, 46))

    # 4번 답변이 PaaS이고 5번 답변이 Y이면
    elif len(answers) > 4 and answers[4] and str(answers[4]) == 'PaaS' and has_soc1_report:
        skip_ranges.append((14, 31))
        skip_ranges.append((44, 46))

    # 14번 답변이 N이면 15~23번 질문 생략 (DB 접속 불가)
    if len(answers) > 14 and answers[14] and str(answers[14]).upper() == 'N':
        skip_ranges.append((15, 23))

    # 24번 답변이 N이면 25~30번 질문 생략 (OS 접속 불가)
    if len(answers) > 24 and answers[24] and str(answers[24]).upper() == 'N':
        skip_ranges.append((25, 30))

    # 31번 답변이 N이면 32~37번 질문 생략 (프로그램 변경 불가)
    if len(answers) > 31 and answers[31] and str(answers[31]).upper() == 'N':
        skip_ranges.append((32, 37))

    # 38번 답변이 N이면 39~43번 질문 생략 (배치 스케줄 없음)
    if len(answers) > 38 and answers[38] and str(answers[38]).upper() == 'N':
        skip_ranges.append((39, 43))

    return skip_ranges

def is_skipped(question_index, skip_ranges):
    """특정 질문이 스킵되는지 확인"""
    for start, end in skip_ranges:
        if start <= question_index <= end:
            return True
    return False

# 스킵샘플 데이터 (link2.jsp에서 복사)
skip_samples = {
    0: {'type': 'text', 'value': 'snowball2727@naver.com', 'comment': '이메일'},
    1: {'type': 'text', 'value': 'SAP ERP', 'comment': '시스템 이름'},
    2: {'type': 'radio_text', 'radio': 'Y', 'text': 'SAP S/4HANA', 'comment': '상용소프트웨어'},
    3: {'type': 'radio', 'value': 'N', 'comment': 'Cloud 서비스 사용 안함 → 4~5번 스킵'},
    4: {'type': 'radio', 'value': 'IaaS', 'comment': '어떤 종류의 Cloud입니까? (스킵되지만 기본값 제공)'},
    5: {'type': 'radio', 'value': 'Y', 'comment': 'Cloud 서비스 업체에서는 SOC1 Report를 발행하고 있습니까? (스킵되지만 기본값 제공)'},
    6: {'type': 'radio', 'value': 'N', 'comment': '권한부여 이력 미기록'},
    7: {'type': 'radio', 'value': 'N', 'comment': '권한회수 이력 미기록'},
    8: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '권한 승인 절차 없음'},
    9: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '권한 회수 절차 없음'},
    10: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '퇴사자 권한 차단 절차 없음'},
    11: {'type': 'textarea', 'value': '', 'comment': 'Application 관리자'},
    12: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '권한 모니터링 절차 없음'},
    13: {'type': 'textarea', 'value': '', 'comment': '패스워드 정책'},
    14: {'type': 'radio', 'value': 'N', 'comment': 'DB 접속 불가 → 15~23번 스킵'},
    15: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '데이터 변경 절차 없음 (스킵됨)'},
    16: {'type': 'textarea', 'value': '', 'comment': '데이터 변경 권한자 (스킵됨)'},
    17: {'type': 'radio', 'value': 'Y', 'comment': 'DB 접속 가능 (논리적 모순!)'},
    18: {'type': 'text', 'value': 'MySQL 8.0', 'comment': 'DB 종류와 버전 (스킵됨)'},
    19: {'type': 'radio_text', 'radio': 'N', 'text': '', 'comment': 'DB 접근제어 Tool 미사용 (스킵됨)'},
    20: {'type': 'radio', 'value': 'N', 'comment': 'DB 접근권한 부여 이력 미기록 (스킵됨)'},
    21: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': 'DB 접근권한 승인 절차 없음 (스킵됨)'},
    22: {'type': 'textarea', 'value': '', 'comment': 'DB 관리자 권한자 (스킵됨)'},
    23: {'type': 'textarea', 'value': '', 'comment': 'DB 패스워드 정책 (스킵됨)'},
    24: {'type': 'radio', 'value': 'N', 'comment': 'OS 접속 불가 → 25~30번 스킵'},
    25: {'type': 'text', 'value': 'Linux Ubuntu 20.04', 'comment': 'OS 종류와 버전 (스킵됨)'},
    26: {'type': 'radio_text', 'radio': 'N', 'text': '', 'comment': 'OS 접근제어 Tool 미사용 (스킵됨)'},
    27: {'type': 'radio', 'value': 'N', 'comment': 'OS 접근권한 부여 이력 미기록 (스킵됨)'},
    28: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': 'OS 접근권한 승인 절차 없음 (스킵됨)'},
    29: {'type': 'textarea', 'value': '', 'comment': 'OS 관리자 권한자 (스킵됨)'},
    30: {'type': 'textarea', 'value': '', 'comment': 'OS 패스워드 정책 (스킵됨)'},
    31: {'type': 'radio', 'value': 'N', 'comment': '프로그램 변경 불가 → 32~37번 스킵'},
    32: {'type': 'radio', 'value': 'N', 'comment': '프로그램 변경 이력 미기록 (스킵됨)'},
    33: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '프로그램 변경 승인 절차 없음 (스킵됨)'},
    34: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '사용자 테스트 절차 없음 (스킵됨)'},
    35: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '이관 승인 절차 없음 (스킵됨)'},
    36: {'type': 'textarea', 'value': '', 'comment': '이관 권한자 (스킵됨)'},
    37: {'type': 'radio', 'value': 'N', 'comment': '개발/테스트 서버 미운용 (스킵됨)'},
    38: {'type': 'radio', 'value': 'N', 'comment': '배치 스케줄 없음 → 39~43번 스킵'},
    39: {'type': 'radio_text', 'radio': 'N', 'text': '', 'comment': 'Batch Schedule Tool 미사용 (스킵됨)'},
    40: {'type': 'radio', 'value': 'N', 'comment': '배치 스케줄 등록/변경 이력 미기록 (스킵됨)'},
    41: {'type': 'radio_textarea', 'radio': 'N', 'textarea': '', 'comment': '배치 스케줄 승인 절차 없음 (스킵됨)'},
    42: {'type': 'textarea', 'value': '', 'comment': '배치 스케줄 권한자 (스킵됨)'},
    43: {'type': 'textarea', 'value': '', 'comment': '배치 모니터링 (스킵됨)'},
    44: {'type': 'textarea', 'value': '', 'comment': '장애 대응 절차'},
    45: {'type': 'textarea', 'value': '', 'comment': '백업 절차'},
    46: {'type': 'textarea', 'value': '', 'comment': '서버실 출입 절차'},
}

def extract_answers_from_skip_samples():
    """스킵샘플 데이터에서 답변 추출"""
    answers = [''] * 48
    for idx, sample in skip_samples.items():
        if sample['type'] == 'text':
            answers[idx] = sample['value']
        elif sample['type'] == 'radio':
            answers[idx] = sample['value']
        elif sample['type'] == 'radio_text':
            answers[idx] = sample['radio']
        elif sample['type'] == 'radio_textarea':
            answers[idx] = sample['radio']
        elif sample['type'] == 'textarea':
            answers[idx] = sample['value']
    return answers

def validate():
    """검증 실행"""
    print("=" * 80)
    print("인터뷰 조건부 로직 및 스킵샘플 일관성 검증")
    print("=" * 80)

    # 스킵샘플에서 답변 추출
    answers = extract_answers_from_skip_samples()

    # 조건부 로직에 따른 스킵 범위 계산
    skip_ranges = get_skip_ranges(answers)

    print("\n📋 스킵샘플 답변 요약:")
    print(f"  - Q3 (Cloud 사용): {answers[3]}")
    print(f"  - Q4 (Cloud 종류): {answers[4]}")
    print(f"  - Q5 (SOC1 Report): {answers[5]}")
    print(f"  - Q14 (DB 접속): {answers[14]}")
    print(f"  - Q24 (OS 접속): {answers[24]}")
    print(f"  - Q31 (프로그램 변경): {answers[31]}")
    print(f"  - Q38 (배치 스케줄): {answers[38]}")

    print(f"\n🔍 조건부 로직에 따른 스킵 범위:")
    for start, end in skip_ranges:
        if start == end:
            print(f"  - Q{start}")
        else:
            print(f"  - Q{start}~Q{end}")

    print("\n" + "=" * 80)
    print("논리적 오류 검증")
    print("=" * 80)

    errors = []

    # 1. Q3='N'이면 Q4, Q5는 스킵되어야 하는데 답변이 있는지 확인
    if answers[3] == 'N':
        if answers[4] or answers[5]:
            errors.append({
                'type': 'CRITICAL',
                'message': 'Q3에서 Cloud를 사용하지 않는다고 했는데, Q4(Cloud 종류) 또는 Q5(SOC1 Report)에 답변이 있습니다.',
                'detail': f'Q4={answers[4]}, Q5={answers[5]}'
            })

    # 2. Q14='N'이면 Q15~Q23은 스킵되어야 함
    if answers[14] == 'N':
        for q in range(15, 24):
            if q == 17 and answers[q] == 'Y':
                errors.append({
                    'type': 'CRITICAL',
                    'message': f'Q14에서 DB 접속 불가라고 했는데, Q17에서 DB 접속 가능(Y)로 답변했습니다.',
                    'detail': f'Q14={answers[14]}, Q17={answers[17]}'
                })

    # 3. Q24='N'이면 Q25~Q30은 스킵되어야 함
    if answers[24] == 'N':
        has_content = False
        for q in range(25, 31):
            if answers[q]:
                has_content = True
        if has_content:
            errors.append({
                'type': 'WARNING',
                'message': f'Q24에서 OS 접속 불가라고 했는데, Q25~Q30에 답변이 있습니다.',
                'detail': f'스킵될 질문에 기본값이 설정되어 있을 수 있습니다.'
            })

    # 4. Q31='N'이면 Q32~Q37은 스킵되어야 함
    if answers[31] == 'N':
        has_content = False
        for q in range(32, 38):
            if answers[q]:
                has_content = True
        if has_content:
            errors.append({
                'type': 'WARNING',
                'message': f'Q31에서 프로그램 변경 불가라고 했는데, Q32~Q37에 답변이 있습니다.',
                'detail': f'스킵될 질문에 기본값이 설정되어 있을 수 있습니다.'
            })

    # 5. Q38='N'이면 Q39~Q43은 스킵되어야 함
    if answers[38] == 'N':
        has_content = False
        for q in range(39, 44):
            if answers[q]:
                has_content = True
        if has_content:
            errors.append({
                'type': 'WARNING',
                'message': f'Q38에서 배치 스케줄 없음이라고 했는데, Q39~Q43에 답변이 있습니다.',
                'detail': f'스킵될 질문에 기본값이 설정되어 있을 수 있습니다.'
            })

    # 결과 출력
    if errors:
        print(f"\n⚠️  총 {len(errors)}개의 논리적 이슈가 발견되었습니다:\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. [{error['type']}] {error['message']}")
            print(f"   상세: {error['detail']}\n")
    else:
        print("\n✅ 논리적 오류가 발견되지 않았습니다!")

    print("=" * 80)

    # 권장사항
    print("\n💡 권장사항:")
    print("1. CRITICAL 오류는 반드시 수정이 필요합니다.")
    print("2. WARNING은 스킵될 질문에 기본값을 제공하는 것일 수 있으나,")
    print("   실제 인터뷰에서는 해당 질문이 표시되지 않으므로 문제없습니다.")
    print("3. 스킵샘플은 빠른 테스트용이므로, 실제 답변과 다를 수 있습니다.")

    return errors

if __name__ == '__main__':
    errors = validate()
    exit(0 if not errors else 1)
