from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, get_key_rcm_details, save_operation_evaluation, get_operation_evaluations, log_user_activity, get_db, is_design_evaluation_completed, get_completed_design_evaluation_sessions
from snowball_link5 import get_user_info, is_logged_in

bp_link7 = Blueprint('link7', __name__)

# 운영평가 관련 기능들

@bp_link7.route('/operation-evaluation')
@login_required
def user_operation_evaluation():
    """운영평가 페이지"""
    user_info = get_user_info()

    # 사용자가 접근 가능한 RCM 목록 조회
    user_rcms = get_user_rcms(user_info['user_id'])

    # 각 RCM에 대해 완료된 설계평가 세션 조회 및 핵심통제 개수 확인
    for rcm in user_rcms:
        completed_sessions = get_completed_design_evaluation_sessions(rcm['rcm_id'], user_info['user_id'])

        # 각 설계평가 세션에 대해 운영평가 진행상황 조회
        for session in completed_sessions:
            operation_evaluation_session = f"OP_{session['evaluation_session']}"

            # 운영평가 진행 통제 수 조회
            from auth import count_operation_evaluations
            completed_count = count_operation_evaluations(
                rcm['rcm_id'],
                user_info['user_id'],
                operation_evaluation_session,
                session['evaluation_session']
            )
            session['operation_completed_count'] = completed_count

        rcm['completed_design_sessions'] = completed_sessions
        rcm['design_evaluation_completed'] = len(completed_sessions) > 0

        # 핵심통제 개수 조회
        key_controls = get_key_rcm_details(rcm['rcm_id'])
        rcm['key_control_count'] = len(key_controls)
        rcm['has_key_controls'] = len(key_controls) > 0

    log_user_activity(user_info, 'PAGE_ACCESS', '운영평가', '/user/operation-evaluation',
                     request.remote_addr, request.headers.get('User-Agent'))

    return render_template('user_operation_evaluation.jsp',
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         user_rcms=user_rcms,
                         remote_addr=request.remote_addr)

@bp_link7.route('/operation-evaluation/rcm', methods=['GET', 'POST'])
@login_required
def user_operation_evaluation_rcm():
    """RCM별 운영평가 페이지 (설계평가 세션 기반)"""
    user_info = get_user_info()

    # POST로 전달된 RCM ID와 설계평가 세션 정보 받기
    if request.method == 'POST':
        rcm_id = request.form.get('rcm_id')
        design_evaluation_session = request.form.get('design_evaluation_session')


        if not rcm_id:
            flash('RCM 정보가 없습니다.', 'error')
            return redirect(url_for('link7.user_operation_evaluation'))
        if not design_evaluation_session:
            flash('설계평가 세션 정보가 없습니다.', 'error')
            return redirect(url_for('link7.user_operation_evaluation'))

        # 세션에 저장
        session['current_operation_rcm_id'] = int(rcm_id)
        session['current_design_evaluation_session'] = design_evaluation_session

    # POST든 GET이든 세션에서 정수형 rcm_id를 가져옴
    rcm_id = session.get('current_operation_rcm_id')
    design_evaluation_session = session.get('current_design_evaluation_session')

    if not rcm_id:
        flash('RCM 정보가 없습니다. 다시 선택해주세요.', 'error')
        return redirect(url_for('link7.user_operation_evaluation'))
    if not design_evaluation_session:
        flash('설계평가 세션 정보가 없습니다. 다시 선택해주세요.', 'error')
        return redirect(url_for('link7.user_operation_evaluation'))

    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]

    if rcm_id not in rcm_ids:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link7.user_operation_evaluation'))


    # 해당 설계평가 세션이 완료되었는지 확인
    completed_sessions = get_completed_design_evaluation_sessions(rcm_id, user_info['user_id'])

    session_found = False
    for session_item in completed_sessions:
        if session_item['evaluation_session'] == design_evaluation_session:
            session_found = True
            break

    if not session_found:
        flash(f'설계평가 세션 "{design_evaluation_session}"이 완료되지 않아 운영평가를 수행할 수 없습니다.', 'warning')
        return redirect(url_for('link7.user_operation_evaluation'))
    
    # RCM 정보 조회
    rcm_info = None
    for rcm in user_rcms:
        if rcm['rcm_id'] == rcm_id:
            rcm_info = rcm
            break
    
    # RCM 핵심통제 데이터 조회 (운영평가는 핵심통제만 대상)
    rcm_details = get_key_rcm_details(rcm_id)

    # 핵심통제가 없는 경우 안내 메시지 표시
    if not rcm_details:
        flash('해당 RCM에 핵심통제가 없어 운영평가를 수행할 수 없습니다.', 'warning')
        return redirect(url_for('link7.user_operation_evaluation'))

    # 운영평가 세션명 생성 (설계평가 세션 기반)
    operation_evaluation_session = f"OP_{design_evaluation_session}"

    # 운영평가 Header/Line 데이터 초기화 (처음 진입시)
    try:
        # 기존 운영평가 헤더 확인
        from auth import get_or_create_operation_evaluation_header
        with get_db() as conn:
            header_id = get_or_create_operation_evaluation_header(conn, rcm_id, user_info['user_id'], operation_evaluation_session, design_evaluation_session)

            # 각 핵심통제에 대한 Line 데이터 초기화 (없는 경우에만)
            for idx, detail in enumerate(rcm_details):
                control_code = detail['control_code']

                # 기존 Line 데이터 확인
                existing_line = conn.execute('''
                    SELECT line_id FROM sb_operation_evaluation_line
                    WHERE header_id = ? AND control_code = ?
                ''', (header_id, control_code)).fetchone()

                if not existing_line:
                    # 새 Line 데이터 생성
                    conn.execute('''
                        INSERT INTO sb_operation_evaluation_line (
                            header_id, control_code, control_sequence
                        ) VALUES (?, ?, ?)
                    ''', (header_id, control_code, idx + 1))

            conn.commit()
    except Exception as e:
        pass

    # 기존 운영평가 내역 불러오기 (Header-Line 구조)
    try:
        evaluations = get_operation_evaluations(rcm_id, user_info['user_id'], operation_evaluation_session, design_evaluation_session)
        evaluation_dict = {}
        for eval_data in evaluations:
            control_code = eval_data['control_code']
            evaluation_dict[control_code] = {
                'operating_effectiveness': eval_data['operating_effectiveness'],
                'sample_size': eval_data['sample_size'],
                'exception_count': eval_data['exception_count'],
                'exception_details': eval_data['exception_details'],
                'conclusion': eval_data['conclusion'],
                'improvement_plan': eval_data['improvement_plan']
            }
    except Exception as e:
        evaluation_dict = {}

    log_user_activity(user_info, 'PAGE_ACCESS', 'RCM 운영평가', '/operation-evaluation/rcm',
                     request.remote_addr, request.headers.get('User-Agent'))

    return render_template('user_operation_evaluation_rcm.jsp',
                         rcm_id=rcm_id,
                         design_evaluation_session=design_evaluation_session,
                         operation_evaluation_session=operation_evaluation_session,
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         evaluation_dict=evaluation_dict,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link7.route('/api/operation-evaluation/save', methods=['POST'])
@login_required
def save_operation_evaluation_api():
    """운영평가 결과 저장 API"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    design_evaluation_session = data.get('design_evaluation_session')
    control_code = data.get('control_code')
    evaluation_data = data.get('evaluation_data')

    if not all([rcm_id, design_evaluation_session, control_code, evaluation_data]):
        return jsonify({
            'success': False,
            'message': '필수 데이터가 누락되었습니다.'
        })

    # 운영평가 세션명 생성
    operation_evaluation_session = f"OP_{design_evaluation_session}"
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인
        with get_db() as conn:
            access_check = conn.execute('''
                SELECT permission_type FROM sb_user_rcm
                WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
            ''', (user_info['user_id'], rcm_id)).fetchone()

            if not access_check:
                return jsonify({
                    'success': False,
                    'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                })

        # 해당 설계평가 세션이 완료되었는지 확인
        completed_sessions = get_completed_design_evaluation_sessions(rcm_id, user_info['user_id'])
        session_found = False
        for session in completed_sessions:
            if session['evaluation_session'] == design_evaluation_session:
                session_found = True
                break

        if not session_found:
            return jsonify({
                'success': False,
                'message': f'설계평가 세션 "{design_evaluation_session}"이 완료되지 않아 운영평가를 수행할 수 없습니다.'
            })

        # 운영평가 결과 저장 (Header-Line 구조)
        save_operation_evaluation(rcm_id, control_code, user_info['user_id'], operation_evaluation_session, design_evaluation_session, evaluation_data)
        
        # 활동 로그 기록
        log_user_activity(user_info, 'OPERATION_EVALUATION', f'운영평가 저장 - {control_code}', 
                         f'/api/operation-evaluation/save', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '운영평가 결과가 저장되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '저장 중 오류가 발생했습니다.'
        })

@bp_link7.route('/api/operation-evaluation/load/<int:rcm_id>/<design_evaluation_session>')
@login_required
def load_operation_evaluation(rcm_id, design_evaluation_session):
    """운영평가 데이터 로드 API (설계평가 세션별)"""
    user_info = get_user_info()

    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]

        if rcm_id not in rcm_ids:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403

        # 운영평가 세션명 생성
        operation_evaluation_session = f"OP_{design_evaluation_session}"

        evaluations = get_operation_evaluations(rcm_id, user_info['user_id'], operation_evaluation_session, design_evaluation_session)

        evaluation_dict = {}
        for eval_data in evaluations:
            control_code = eval_data['control_code']
            evaluation_dict[control_code] = {
                'operating_effectiveness': eval_data['operating_effectiveness'],
                'sample_size': eval_data['sample_size'],
                'exception_count': eval_data['exception_count'],
                'exception_details': eval_data['exception_details'],
                'conclusion': eval_data['conclusion'],
                'improvement_plan': eval_data['improvement_plan']
            }

        return jsonify({'success': True, 'evaluations': evaluation_dict})

    except Exception as e:
        return jsonify({'success': False, 'message': '데이터 로드 중 오류가 발생했습니다.'}), 500

@bp_link7.route('/api/operation-evaluation/reset', methods=['POST'])
@login_required
def reset_operation_evaluations_api():
    """운영평가 결과 초기화 API"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    design_evaluation_session = data.get('design_evaluation_session')

    if not all([rcm_id, design_evaluation_session]):
        return jsonify({
            'success': False,
            'message': 'RCM ID 또는 설계평가 세션이 누락되었습니다.'
        })

    # 운영평가 세션명 생성
    operation_evaluation_session = f"OP_{design_evaluation_session}"
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인
        with get_db() as conn:
            access_check = conn.execute('''
                SELECT permission_type FROM sb_user_rcm
                WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
            ''', (user_info['user_id'], rcm_id)).fetchone()
            
            if not access_check:
                return jsonify({
                    'success': False,
                    'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                })
            
            # 해당 사용자의 해당 세션 운영평가 결과 삭제 (Header-Line 구조)
            # 1. 먼저 line 레코드들 삭제
            conn.execute('''
                DELETE FROM sb_operation_evaluation_line
                WHERE header_id IN (
                    SELECT header_id FROM sb_operation_evaluation_header
                    WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ? AND design_evaluation_session = ?
                )
            ''', (rcm_id, user_info['user_id'], operation_evaluation_session, design_evaluation_session))

            # 2. header 레코드 삭제
            cursor = conn.execute('''
                DELETE FROM sb_operation_evaluation_header
                WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ? AND design_evaluation_session = ?
            ''', (rcm_id, user_info['user_id'], operation_evaluation_session, design_evaluation_session))
            deleted_count = cursor.rowcount
            
            conn.commit()
        
        # 활동 로그 기록
        log_user_activity(user_info, 'OPERATION_EVALUATION_RESET', f'운영평가 초기화 - RCM ID: {rcm_id}, 설계평가 세션: {design_evaluation_session}',
                         f'/api/operation-evaluation/reset',
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count}개의 운영평가 결과가 초기화되었습니다.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '초기화 중 오류가 발생했습니다.'
        })