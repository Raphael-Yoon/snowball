from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, get_user_evaluation_sessions, delete_evaluation_session, create_evaluation_structure, log_user_activity, get_db
from snowball_link5 import get_user_info, is_logged_in
import sys

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
    
    sys.stderr.write(f"[DEBUG] Raw request data received: {data}\n")
    sys.stderr.write(f"[DEBUG] User info: {user_info}\n")
    sys.stderr.flush()
    
    rcm_id = data.get('rcm_id') if data else None
    control_code = data.get('control_code') if data else None
    evaluation_data = data.get('evaluation_data') if data else None
    evaluation_session = data.get('evaluation_session') if data else None  # 평가 세션명
    
    # 디버깅용 로그
    sys.stderr.write(f"[DEBUG] Design evaluation save request: rcm_id={rcm_id}, control_code={control_code}, evaluation_session='{evaluation_session}'\n")
    sys.stderr.flush()
    
    if not all([rcm_id, control_code, evaluation_data, evaluation_session]):
        missing_fields = []
        if not rcm_id: missing_fields.append('RCM ID')
        if not control_code: missing_fields.append('통제 코드')
        if not evaluation_data: missing_fields.append('평가 데이터')
        if not evaluation_session: missing_fields.append('세션명')
        
        return jsonify({
            'success': False,
            'message': f'필수 데이터가 누락되었습니다: {", ".join(missing_fields)}'
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
        save_design_evaluation(rcm_id, control_code, user_info['user_id'], evaluation_data, evaluation_session)
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION', f'설계평가 저장 - {control_code}', 
                         f'/api/design-evaluation/save', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '새로운 설계평가 결과가 저장되었습니다.'
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
            
            # 해당 사용자의 모든 설계평가 결과 삭제 (Header-Line 구조)
            # 1. 먼저 line 레코드들 삭제
            conn.execute('''
                DELETE FROM sb_design_evaluation_line 
                WHERE header_id IN (
                    SELECT header_id FROM sb_design_evaluation_header 
                    WHERE rcm_id = ? AND user_id = ?
                )
            ''', (rcm_id, user_info['user_id']))
            
            # 2. header 레코드 삭제
            cursor = conn.execute('''
                DELETE FROM sb_design_evaluation_header 
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

# 임시 비활성화 - 테이블 구조 문제로 인해
# @bp_link6.route('/api/design-evaluation/versions/<int:rcm_id>/<control_code>')
# @login_required
# def get_evaluation_versions_api(rcm_id, control_code):
#     return jsonify({'success': False, 'message': '기능 준비 중입니다.'}), 503

@bp_link6.route('/api/design-evaluation/sessions/<int:rcm_id>')
@login_required
def get_evaluation_sessions_api(rcm_id):
    """사용자의 설계평가 세션 목록 조회 API"""
    user_info = get_user_info()
    
    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
        
        if rcm_id not in rcm_ids:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        # 평가 세션 목록 조회
        sessions = get_user_evaluation_sessions(rcm_id, user_info['user_id'])
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total_count': len(sessions)
        })
        
    except Exception as e:
        print(f"평가 세션 조회 오류: {e}")
        return jsonify({'success': False, 'message': '세션 조회 중 오류가 발생했습니다.'}), 500

@bp_link6.route('/api/design-evaluation/load/<int:rcm_id>')
@login_required
def load_evaluation_data_api(rcm_id):
    """특정 평가 세션의 데이터 로드 API"""
    print("***** SNOWBALL_LINK6: load_evaluation_data_api CALLED *****")
    user_info = get_user_info()
    evaluation_session = request.args.get('session')
    header_id = request.args.get('header_id')
    print(f"***** SNOWBALL_LINK6: rcm_id={rcm_id}, header_id={header_id}, session={evaluation_session} *****")
    
    print(f"Load evaluation data API called: rcm_id={rcm_id}, session='{evaluation_session}', header_id={header_id}, user_info={user_info}")
    print(f"***** REQUEST URL: {request.url} *****")
    print(f"***** RCM_ID from URL parameter: {rcm_id} (type: {type(rcm_id)}) *****")
    print(f"***** REQUEST ARGS: {dict(request.args)} *****")
    print(f"***** header_id type: {type(header_id)}, value: '{header_id}' *****")
    print(f"***** header_id is None: {header_id is None} *****")
    print(f"***** header_id is empty string: {header_id == ''} *****")
    
    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
        
        if rcm_id not in rcm_ids:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        # 평가 데이터 로드
        if header_id:
            print(f"***** SNOWBALL_LINK6: Using get_design_evaluations_by_header_id with header_id={header_id} *****")
            print(f"***** SNOWBALL_LINK6: Parameters - rcm_id={rcm_id}, user_id={user_info['user_id']}, header_id={int(header_id)} *****")
            evaluations = get_design_evaluations_by_header_id(rcm_id, user_info['user_id'], int(header_id))
            print(f"***** SNOWBALL_LINK6: Returned {len(evaluations)} evaluations *****")
        else:
            print(f"***** SNOWBALL_LINK6: Using get_design_evaluations with session='{evaluation_session}' *****")
            evaluations = get_design_evaluations(rcm_id, user_info['user_id'], evaluation_session)
            print(f"***** SNOWBALL_LINK6: Returned {len(evaluations)} evaluations *****")
        
        # 통제별로 정리
        evaluation_dict = {}
        for eval_data in evaluations:
            control_code = eval_data['control_code']
            evaluation_date = eval_data.get('evaluation_date')
            
            # 디버깅용 로그 추가
            print(f"Control {control_code}: evaluation_date = {evaluation_date} (type: {type(evaluation_date)})")
            
            evaluation_dict[control_code] = {
                'adequacy': eval_data['description_adequacy'],
                'improvement': eval_data['improvement_suggestion'],
                'effectiveness': eval_data['overall_effectiveness'],
                'rationale': eval_data['evaluation_rationale'],
                'actions': eval_data['recommended_actions'],
                'evaluation_date': evaluation_date
            }
        
        return jsonify({
            'success': True,
            'evaluations': evaluation_dict,
            'session_name': evaluation_session
        })
        
    except Exception as e:
        print(f"평가 데이터 로드 오류: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: rcm_id={rcm_id}, evaluation_session='{evaluation_session}', user_info={user_info}")
        return jsonify({'success': False, 'message': f'데이터 로드 중 오류가 발생했습니다: {str(e)}'}), 500

@bp_link6.route('/api/design-evaluation/delete-session', methods=['POST'])
@login_required
def delete_evaluation_session_api():
    """평가 세션 삭제 API"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    evaluation_session = data.get('evaluation_session')
    
    if not all([rcm_id, evaluation_session]):
        return jsonify({
            'success': False,
            'message': '필수 데이터가 누락되었습니다.'
        })
    
    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
        
        if rcm_id not in rcm_ids:
            return jsonify({
                'success': False,
                'message': '해당 RCM에 대한 접근 권한이 없습니다.'
            })
        
        # 세션 삭제
        deleted_count = delete_evaluation_session(rcm_id, user_info['user_id'], evaluation_session)
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION_DELETE', f'설계평가 세션 삭제 - {evaluation_session}', 
                         f'/api/design-evaluation/delete-session', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': f'평가 세션 "{evaluation_session}"이 삭제되었습니다.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        print(f"평가 세션 삭제 오류: {e}")
        return jsonify({
            'success': False,
            'message': '삭제 중 오류가 발생했습니다.'
        })

@bp_link6.route('/api/design-evaluation/create-evaluation', methods=['POST'])
@login_required
def create_design_evaluation_api():
    """새로운 설계평가 생성 API (Header + 모든 Line 생성)"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    evaluation_session = data.get('evaluation_session')
    
    if not all([rcm_id, evaluation_session]):
        return jsonify({
            'success': False,
            'message': '필수 데이터가 누락되었습니다.'
        })
    
    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
        
        if rcm_id not in rcm_ids:
            return jsonify({
                'success': False,
                'message': '해당 RCM에 대한 접근 권한이 없습니다.'
            })
        
        # 중복 세션명 체크
        existing_sessions = get_user_evaluation_sessions(rcm_id, user_info['user_id'])
        session_names = [session['evaluation_session'] for session in existing_sessions]
        
        if evaluation_session in session_names:
            return jsonify({
                'success': False,
                'message': f'"{evaluation_session}" 세션이 이미 존재합니다. 다른 이름을 사용해주세요.',
                'exists': True
            })
        
        # 평가 구조 생성 (Header + 모든 빈 Line 생성)
        header_id = create_evaluation_structure(rcm_id, user_info['user_id'], evaluation_session)
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION_CREATE', 
                         f'설계평가 생성 - {evaluation_session}', 
                         f'/api/design-evaluation/create-evaluation', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': f'설계평가 "{evaluation_session}"이 생성되었습니다.',
            'header_id': header_id,
            'evaluation_session': evaluation_session
        })
        
    except ValueError as ve:
        print(f"평가 생성 검증 오류: {ve}")
        return jsonify({
            'success': False,
            'message': str(ve)
        })
    except Exception as e:
        print(f"평가 생성 오류: {e}")
        return jsonify({
            'success': False,
            'message': '평가 생성 중 오류가 발생했습니다.'
        })