"""
ELC 평가 관련 유틸리티 함수
status와 progress를 line 데이터 기반으로 실시간 계산
"""

def calculate_design_progress(conn, header_id):
    """
    설계평가 진행률 계산

    Returns:
        int: 진행률 (0-100)
    """
    # 전체 통제 수
    total = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ?
    ''', (header_id,)).fetchone()
    total_count = dict(total)['count'] if total else 0

    if total_count == 0:
        return 0

    # 설계평가 완료 통제 수 (design_conclusion이 NULL이 아닌 것)
    completed = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND design_conclusion IS NOT NULL
    ''', (header_id,)).fetchone()
    completed_count = dict(completed)['count'] if completed else 0

    return int((completed_count / total_count) * 100)


def calculate_operation_progress(conn, header_id):
    """
    운영평가 진행률 계산 (핵심통제 중 설계평가 결과가 '적정'인 통제만 대상)

    Returns:
        int: 진행률 (0-100)
    """
    # 설계평가 결과가 '적정'인 통제 수 (운영평가 대상)
    total = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND design_conclusion = '적정'
    ''', (header_id,)).fetchone()
    total_count = dict(total)['count'] if total else 0

    if total_count == 0:
        return 0

    # 운영평가 완료 통제 수 (conclusion이 NULL이 아닌 것)
    completed = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND design_conclusion = '적정' AND conclusion IS NOT NULL
    ''', (header_id,)).fetchone()
    completed_count = dict(completed)['count'] if completed else 0

    return int((completed_count / total_count) * 100)


def calculate_status(conn, header_id):
    """
    평가 상태 계산 (line 데이터 기반)

    Returns:
        int: status 값
            0: 설계평가 시작 (진행 중)
            1: 설계평가 완료
            2: 운영평가 시작
            3: 운영평가 진행 중
            4: 운영평가 완료
            5: 아카이브
    """
    # 아카이브 여부 확인
    header = conn.execute('''
        SELECT archived
        FROM sb_evaluation_header
        WHERE header_id = ?
    ''', (header_id,)).fetchone()

    if header and dict(header).get('archived', False):
        return 5

    design_progress = calculate_design_progress(conn, header_id)
    operation_progress = calculate_operation_progress(conn, header_id)

    # 운영평가가 완료되었는지 확인
    if operation_progress == 100:
        return 4

    # 운영평가가 시작되었는지 확인 (운영평가 데이터가 하나라도 있으면)
    operation_started = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND conclusion IS NOT NULL
    ''', (header_id,)).fetchone()
    operation_count = dict(operation_started)['count'] if operation_started else 0

    if operation_count > 0:
        return 3 if operation_progress < 100 else 4

    # 설계평가 완료 여부
    if design_progress == 100:
        return 1

    return 0


def get_evaluation_status(conn, header_id):
    """
    평가 상태 정보 조회 (status, design_progress, operation_progress 포함)

    Returns:
        dict: {
            'status': int,
            'design_progress': int,
            'operation_progress': int,
            'design_completed_count': int,
            'design_total_count': int,
            'operation_completed_count': int,
            'operation_total_count': int
        }
    """
    # 전체 통제 수
    total = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ?
    ''', (header_id,)).fetchone()
    design_total = dict(total)['count'] if total else 0

    # 설계평가 완료 통제 수
    design_completed = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND design_conclusion IS NOT NULL
    ''', (header_id,)).fetchone()
    design_completed_count = dict(design_completed)['count'] if design_completed else 0

    # 운영평가 대상 통제 수 (설계평가 결과가 '적정'인 것)
    operation_total = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND design_conclusion = '적정'
    ''', (header_id,)).fetchone()
    operation_total_count = dict(operation_total)['count'] if operation_total else 0

    # 운영평가 완료 통제 수
    operation_completed = conn.execute('''
        SELECT COUNT(*) as count
        FROM sb_evaluation_line
        WHERE header_id = ? AND design_conclusion = '적정' AND conclusion IS NOT NULL
    ''', (header_id,)).fetchone()
    operation_completed_count = dict(operation_completed)['count'] if operation_completed else 0

    design_progress = int((design_completed_count / design_total) * 100) if design_total > 0 else 0
    operation_progress = int((operation_completed_count / operation_total_count) * 100) if operation_total_count > 0 else 0

    status = calculate_status(conn, header_id)

    return {
        'status': status,
        'design_progress': design_progress,
        'operation_progress': operation_progress,
        'design_completed_count': design_completed_count,
        'design_total_count': design_total,
        'operation_completed_count': operation_completed_count,
        'operation_total_count': operation_total_count
    }
