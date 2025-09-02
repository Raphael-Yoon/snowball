from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_design_evaluation, get_design_evaluations, log_user_activity, get_db
from snowball_link5 import get_user_info, is_logged_in

bp_link6 = Blueprint('link6', __name__)

# 설계평가 관련 기능들

@bp_link6.route('/design-evaluation')
@login_required
def user_design_evaluation():
    """설계평가 페이지"""
    user_info = get_user_info()
    
    log_user_activity(user_info, 'PAGE_ACCESS', '설계평가', '/user/design-evaluation', 
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('user_design_evaluation.jsp',
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link6.route('/api/design-evaluation/save', methods=['POST'])
@login_required
def save_design_evaluation_api():
    """설계평가 결과 저장 API"""
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
        
        # 설계평가 결과 저장
        save_design_evaluation(rcm_id, control_code, user_info['user_id'], evaluation_data)
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION', f'설계평가 저장 - {control_code}', 
                         f'/api/design-evaluation/save', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '설계평가 결과가 저장되었습니다.'
        })
        
    except Exception as e:
        print(f"설계평가 저장 오류: {e}")
        return jsonify({
            'success': False,
            'message': '저장 중 오류가 발생했습니다.'
        })

@bp_link6.route('/api/design-evaluation/reset', methods=['POST'])
@login_required
def reset_design_evaluations_api():
    """설계평가 결과 초기화 API"""
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
            
            # 해당 사용자의 모든 설계평가 결과 삭제
            cursor = conn.execute('''
                DELETE FROM sb_design_evaluation 
                WHERE rcm_id = ? AND user_id = ?
            ''', (rcm_id, user_info['user_id']))
            deleted_count = cursor.rowcount
            
            conn.commit()
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION_RESET', f'설계평가 초기화 - RCM ID: {rcm_id}', 
                         f'/api/design-evaluation/reset', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count}개의 설계평가 결과가 초기화되었습니다.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"설계평가 초기화 오류: {e}")
        return jsonify({
            'success': False,
            'message': '초기화 중 오류가 발생했습니다.'
        })