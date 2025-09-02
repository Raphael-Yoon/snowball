from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_operation_evaluation, get_operation_evaluations, log_user_activity, get_db
from snowball_link5 import get_user_info, is_logged_in

bp_link7 = Blueprint('link7', __name__)

# 운영평가 관련 기능들

@bp_link7.route('/operation-evaluation')
@login_required
def user_operation_evaluation():
    """운영평가 페이지"""
    user_info = get_user_info()
    
    log_user_activity(user_info, 'PAGE_ACCESS', '운영평가', '/user/operation-evaluation', 
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('user_operation_evaluation.jsp',
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link7.route('/operation-evaluation/rcm/<int:rcm_id>')
@login_required  
def user_operation_evaluation_rcm(rcm_id):
    """RCM별 운영평가 페이지"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link7.user_operation_evaluation'))
    
    # RCM 정보 조회
    rcm_info = None
    for rcm in user_rcms:
        if rcm['rcm_id'] == rcm_id:
            rcm_info = rcm
            break
    
    # RCM 세부 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    
    # 기존 운영평가 내역 불러오기
    try:
        evaluations = get_operation_evaluations(rcm_id, user_info['user_id'])
        evaluation_dict = {}
        for eval_data in evaluations:
            control_id = eval_data['control_id']
            evaluation_dict[control_id] = {
                'operating_effectiveness': eval_data['operating_effectiveness'],
                'sample_size': eval_data['sample_size'],
                'exception_count': eval_data['exception_count'],
                'exception_details': eval_data['exception_details'], 
                'conclusion': eval_data['conclusion'],
                'improvement_plan': eval_data['improvement_plan']
            }
    except Exception as e:
        evaluation_dict = {}
        print(f"운영평가 데이터 로드 오류: {e}")
    
    log_user_activity(user_info, 'PAGE_ACCESS', 'RCM 운영평가', f'/user/operation-evaluation/rcm/{rcm_id}',
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('user_operation_evaluation_rcm.jsp',
                         rcm_id=rcm_id,
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
    control_code = data.get('control_code')
    evaluation_data = data.get('evaluation_data')
    
    if not all([rcm_id, control_code, evaluation_data]):
        return jsonify({
            'success': False,
            'message': '필수 데이터가 누락되었습니다.'
        })
    
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
        
        # 운영평가 결과 저장
        save_operation_evaluation(rcm_id, control_code, user_info['user_id'], evaluation_data)
        
        # 활동 로그 기록
        log_user_activity(user_info, 'OPERATION_EVALUATION', f'운영평가 저장 - {control_code}', 
                         f'/api/operation-evaluation/save', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '운영평가 결과가 저장되었습니다.'
        })
        
    except Exception as e:
        print(f"운영평가 저장 오류: {e}")
        return jsonify({
            'success': False,
            'message': '저장 중 오류가 발생했습니다.'
        })

@bp_link7.route('/api/operation-evaluation/load/<int:rcm_id>')
@login_required
def load_operation_evaluation(rcm_id):
    """운영평가 데이터 로드 API"""
    user_info = get_user_info()
    
    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
        
        if rcm_id not in rcm_ids:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        evaluations = get_operation_evaluations(rcm_id, user_info['user_id'])
        
        evaluation_dict = {}
        for eval_data in evaluations:
            control_id = eval_data['control_id']
            evaluation_dict[control_id] = {
                'operating_effectiveness': eval_data['operating_effectiveness'],
                'sample_size': eval_data['sample_size'],
                'exception_count': eval_data['exception_count'],
                'exception_details': eval_data['exception_details'],
                'conclusion': eval_data['conclusion'],
                'improvement_plan': eval_data['improvement_plan']
            }
        
        return jsonify({'success': True, 'evaluations': evaluation_dict})
        
    except Exception as e:
        print(f"운영평가 데이터 로드 오류: {e}")
        return jsonify({'success': False, 'message': '데이터 로드 중 오류가 발생했습니다.'}), 500

@bp_link7.route('/api/operation-evaluation/reset', methods=['POST'])
@login_required
def reset_operation_evaluations_api():
    """운영평가 결과 초기화 API"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    
    if not rcm_id:
        return jsonify({
            'success': False,
            'message': 'RCM ID가 누락되었습니다.'
        })
    
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
            
            # 해당 사용자의 모든 운영평가 결과 삭제
            cursor = conn.execute('''
                DELETE FROM sb_operation_evaluation 
                WHERE rcm_id = ? AND user_id = ?
            ''', (rcm_id, user_info['user_id']))
            deleted_count = cursor.rowcount
            
            conn.commit()
        
        # 활동 로그 기록
        log_user_activity(user_info, 'OPERATION_EVALUATION_RESET', f'운영평가 초기화 - RCM ID: {rcm_id}', 
                         f'/api/operation-evaluation/reset', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count}개의 운영평가 결과가 초기화되었습니다.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"운영평가 초기화 오류: {e}")
        return jsonify({
            'success': False,
            'message': '초기화 중 오류가 발생했습니다.'
        })