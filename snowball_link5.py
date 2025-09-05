from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, save_operation_evaluation, get_operation_evaluations, count_design_evaluations, count_operation_evaluations, log_user_activity

def get_user_info():
    """현재 로그인한 사용자 정보 반환 (세션 우선)"""
    from snowball import is_logged_in
    if is_logged_in():
        # 세션에 저장된 user_info를 우선 사용
        if 'user_info' in session:
            return session['user_info']
        # 없으면 데이터베이스에서 조회
        return get_current_user()
    return None

def is_logged_in():
    """로그인 상태 확인"""
    from snowball import is_logged_in as main_is_logged_in
    return main_is_logged_in()

bp_link5 = Blueprint('link5', __name__)

# RCM 관련 기능들

@bp_link5.route('/rcm')
@login_required
def user_rcm():
    """사용자 RCM 조회 페이지"""
    user_info = get_user_info()
    
    # 사용자가 접근 권한을 가진 RCM 목록 조회
    user_rcms = get_user_rcms(user_info['user_id'])
    
    log_user_activity(user_info, 'PAGE_ACCESS', '사용자 RCM 조회', '/user/rcm', 
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'rcm_count': len(user_rcms)})
    
    return render_template('user_rcm.jsp', 
                         user_rcms=user_rcms,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link5.route('/rcm/<int:rcm_id>/view')
@login_required
def user_rcm_view(rcm_id):
    """사용자 RCM 상세 조회 페이지"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link5.user_rcm'))
    
    # RCM 기본 정보 조회
    rcm_info = None
    for rcm in user_rcms:
        if rcm['rcm_id'] == rcm_id:
            rcm_info = rcm
            break
    
    # RCM 상세 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    
    return render_template('user_rcm_view.jsp',
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link5.route('/design-evaluation/rcm/<int:rcm_id>')
@login_required  
def user_design_evaluation_rcm(rcm_id):
    """사용자 디자인 평가 페이지 (RCM별)"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link5.user_rcm'))
    
    # RCM 정보 조회
    rcm_info = None
    for rcm in user_rcms:
        if rcm['rcm_id'] == rcm_id:
            rcm_info = rcm
            break
    
    # RCM 세부 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    
    # 평가 내역은 사용자가 특정 평가를 선택했을 때만 로드 (빈 딕셔너리로 초기화)
    evaluation_dict = {}
    
    log_user_activity(user_info, 'PAGE_ACCESS', 'RCM 디자인 평가', f'/user/design-evaluation/rcm/{rcm_id}',
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('user_design_evaluation_rcm.jsp',
                         rcm_id=rcm_id,
                         rcm_info=rcm_info,
                         rcm_details=rcm_details, 
                         evaluation_dict=evaluation_dict,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link5.route('/api/design-evaluation/load/<int:rcm_id>')
@login_required
def load_design_evaluation(rcm_id):
    """디자인 평가 데이터 로드 API"""
    print("***** SNOWBALL_LINK5: load_design_evaluation API CALLED *****")
    header_id = request.args.get('header_id')
    session = request.args.get('session')
    print(f"***** SNOWBALL_LINK5: rcm_id={rcm_id}, header_id={header_id}, session={session} *****")
    user_info = get_user_info()
    
    try:
        # 권한 체크
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
        
        if rcm_id not in rcm_ids:
            return jsonify({'success': False, 'message': '접근 권한이 없습니다.'}), 403
        
        # header_id가 있으면 실제 데이터를 로드, 없으면 빈 결과 리턴
        if header_id:
            print(f"***** SNOWBALL_LINK5: Loading data with header_id={header_id} *****")
            evaluations = get_design_evaluations_by_header_id(rcm_id, user_info['user_id'], int(header_id))
            
            evaluation_dict = {}
            for eval_data in evaluations:
                control_code = eval_data['control_code']
                evaluation_dict[control_code] = {
                    'adequacy': eval_data['description_adequacy'],
                    'improvement': eval_data['improvement_suggestion'],
                    'effectiveness': eval_data['overall_effectiveness'],
                    'rationale': eval_data['evaluation_rationale'],
                    'actions': eval_data['recommended_actions'],
                    'evaluation_date': eval_data['evaluation_date']
                }
            
            return jsonify({'success': True, 'evaluations': evaluation_dict})
        else:
            # header_id가 없으면 빈 결과 리턴
            return jsonify({
                'success': True, 
                'evaluations': {},
                'message': '특정 평가를 선택하여 데이터를 로드하세요.'
            })
        
    except Exception as e:
        print(f"평가 데이터 로드 오류: {e}")
        return jsonify({'success': False, 'message': '데이터 로드 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/rcm-status')
@login_required
def user_rcm_status():
    """사용자 RCM 현황 조회 API"""
    user_info = get_user_info()
    
    try:
        # 사용자가 접근 권한을 가진 RCM 목록 조회
        user_rcms = get_user_rcms(user_info['user_id'])
        
        # 각 RCM의 평가 현황 조회
        rcm_status = []
        for rcm in user_rcms:
            rcm_id = rcm['rcm_id']
            
            # 디자인 평가 현황 (효율적인 카운팅)
            design_count = count_design_evaluations(rcm_id, user_info['user_id'])
            
            # 운영 평가 현황 (효율적인 카운팅)
            operation_count = count_operation_evaluations(rcm_id, user_info['user_id'])
            
            # RCM 총 통제 수 (rcm_details에서 가져오기)
            rcm_details = get_rcm_details(rcm_id)
            total_controls = len(rcm_details) if rcm_details else 0
            
            rcm_status.append({
                'rcm_id': rcm_id,
                'rcm_name': rcm['rcm_name'],
                'total_controls': total_controls,
                'design_evaluated': design_count,
                'operation_evaluated': operation_count,
                'design_progress': round(design_count / total_controls * 100, 1) if total_controls > 0 else 0,
                'operation_progress': round(operation_count / total_controls * 100, 1) if total_controls > 0 else 0
            })
        
        return jsonify({
            'success': True, 
            'rcm_status': rcm_status,
            'total_count': len(rcm_status)  # 설계평가 페이지에서 사용
        })
        
    except Exception as e:
        print(f"RCM 현황 조회 오류: {e}")
        return jsonify({'success': False, 'message': '현황 조회 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/rcm-list')
@login_required
def user_rcm_list():
    """사용자 RCM 목록 조회 API (빠른 접근용)"""
    user_info = get_user_info()
    
    try:
        user_rcms = get_user_rcms(user_info['user_id'])
        return jsonify({'success': True, 'rcms': user_rcms})
        
    except Exception as e:
        print(f"RCM 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': '목록 조회 중 오류가 발생했습니다.'}), 500
