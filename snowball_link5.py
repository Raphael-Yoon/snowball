from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, save_operation_evaluation, get_operation_evaluations, count_design_evaluations, count_operation_evaluations, log_user_activity, initialize_standard_controls, get_standard_controls, save_rcm_standard_mapping, get_rcm_standard_mappings, get_rcm_detail_mappings, evaluate_rcm_completeness, save_rcm_review_result, get_rcm_review_result, save_rcm_mapping, save_rcm_ai_review, get_control_review_result, save_control_review_result

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

# RCM 완성도 평가 관련 API

@bp_link5.route('/api/init-standard-controls', methods=['POST'])
@login_required
def init_standard_controls():
    """기준통제 초기 데이터 삽입 API (관리자용)"""
    user_info = get_user_info()
    
    # 관리자 권한 체크
    if user_info.get('admin_flag') != 'Y':
        return jsonify({'success': False, 'message': '관리자 권한이 필요합니다.'}), 403
    
    try:
        initialize_standard_controls()
        return jsonify({'success': True, 'message': '기준통제 초기 데이터가 성공적으로 삽입되었습니다.'})
    except Exception as e:
        print(f"기준통제 초기화 오류: {e}")
        return jsonify({'success': False, 'message': '초기화 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/standard-controls')
@login_required
def get_standard_controls_api():
    """기준통제 목록 조회 API"""
    try:
        controls = get_standard_controls()
        return jsonify({'success': True, 'controls': controls})
    except Exception as e:
        print(f"기준통제 조회 오류: {e}")
        return jsonify({'success': False, 'message': '기준통제 조회 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/mapping', methods=['GET', 'POST'])
@login_required
def rcm_mapping_api(rcm_id):
    """RCM 기준통제 매핑 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '해당 RCM에 대한 접근 권한이 없습니다.'}), 403
    
    if request.method == 'GET':
        # 매핑 조회 (개별 통제 방식으로 변경)
        try:
            mappings = get_rcm_detail_mappings(rcm_id)
            return jsonify({'success': True, 'mappings': mappings})
        except Exception as e:
            print(f"매핑 조회 오류: {e}")
            return jsonify({'success': False, 'message': '매핑 조회 중 오류가 발생했습니다.'}), 500
    
    elif request.method == 'POST':
        # 매핑 저장
        try:
            data = request.get_json()
            control_code = data.get('control_code')
            std_control_id = data.get('std_control_id')
            confidence = data.get('confidence', 0.8)
            mapping_type = data.get('mapping_type', 'manual')
            
            if not all([control_code, std_control_id]):
                return jsonify({'success': False, 'message': '필수 데이터가 누락되었습니다.'}), 400
            
            save_rcm_standard_mapping(rcm_id, control_code, std_control_id, 
                                    confidence, mapping_type, user_info['user_id'])
            
            log_user_activity(user_info, 'RCM_MAPPING', f'RCM 기준통제 매핑 - {control_code}', 
                             f'/api/rcm/{rcm_id}/mapping', 
                             request.remote_addr, request.headers.get('User-Agent'))
            
            return jsonify({'success': True, 'message': '매핑이 저장되었습니다.'})
            
        except Exception as e:
            print(f"매핑 저장 오류: {e}")
            return jsonify({'success': False, 'message': '매핑 저장 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/evaluate-completeness', methods=['POST'])
@login_required
def evaluate_completeness_api(rcm_id):
    """RCM 완성도 평가 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '해당 RCM에 대한 접근 권한이 없습니다.'}), 403
    
    try:
        print(f"[DEBUG] 평가 시작: RCM ID {rcm_id}, User ID {user_info['user_id']}")
        
        # 단계별 디버깅
        rcm_details = get_rcm_details(rcm_id)
        print(f"[DEBUG] RCM 상세 데이터 개수: {len(rcm_details)}")
        
        standard_controls = get_standard_controls()
        print(f"[DEBUG] 기준통제 개수: {len(standard_controls)}")
        
        mappings = get_rcm_standard_mappings(rcm_id)
        print(f"[DEBUG] 기존 매핑 개수: {len(mappings)}")
        
        eval_result = evaluate_rcm_completeness(rcm_id, user_info['user_id'])
        print(f"[DEBUG] 평가 결과: {eval_result}")
        
        log_user_activity(user_info, 'RCM_COMPLETENESS_EVAL', f'RCM 완성도 평가 실행', 
                         f'/api/rcm/{rcm_id}/evaluate-completeness', 
                         request.remote_addr, request.headers.get('User-Agent'),
                         f'완성도: {eval_result["completeness_score"]}%')
        
        return jsonify({
            'success': True, 
            'message': '완성도 평가가 완료되었습니다.',
            'result': eval_result
        })
        
    except Exception as e:
        print(f"완성도 평가 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'완성도 평가 중 오류가 발생했습니다: {str(e)}'}), 500

@bp_link5.route('/rcm/<int:rcm_id>/mapping')
@login_required
def rcm_mapping_page(rcm_id):
    """RCM 기준통제 매핑 화면"""
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
    
    # RCM 상세 데이터 조회 (매핑할 통제 목록)
    rcm_details = get_rcm_details(rcm_id)
    
    # 기준통제 목록 조회
    standard_controls = get_standard_controls()
    
    # 기존 매핑 조회
    existing_mappings = get_rcm_standard_mappings(rcm_id)
    
    return render_template('rcm_mapping.jsp',
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         standard_controls=standard_controls,
                         existing_mappings=existing_mappings,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link5.route('/rcm/<int:rcm_id>/completeness-report')
@login_required
def completeness_report(rcm_id):
    """RCM 완성도 평가 보고서 페이지"""
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
    
    # 완성도 평가 실행
    try:
        eval_result = evaluate_rcm_completeness(rcm_id, user_info['user_id'])
    except Exception as e:
        print(f"완성도 평가 오류: {e}")
        eval_result = {
            'completeness_score': 0.0,
            'total_controls': 0,
            'mapped_controls': 0,
            'missing_fields_count': 0,
            'details': []
        }
    
    return render_template('rcm_completeness_report.jsp',
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         eval_result=eval_result,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

# RCM 검토 결과 저장/조회 API

@bp_link5.route('/api/rcm/<int:rcm_id>/detail/<int:detail_id>/review', methods=['GET', 'POST'])
@login_required
def control_review_api(rcm_id, detail_id):
    """개별 통제 검토 결과 저장/조회 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '해당 RCM에 대한 접근 권한이 없습니다.'}), 403
    
    if request.method == 'GET':
        # 개별 통제 검토 결과 조회
        try:
            review_result = get_control_review_result(rcm_id, detail_id)
            
            if review_result:
                return jsonify({
                    'success': True, 
                    'review_result': review_result,
                    'has_saved_review': True
                })
            else:
                return jsonify({
                    'success': True, 
                    'review_result': None,
                    'has_saved_review': False
                })
                
        except Exception as e:
            print(f"통제 검토 결과 조회 오류: {e}")
            return jsonify({'success': False, 'message': '통제 검토 결과 조회 중 오류가 발생했습니다.'}), 500
    
    elif request.method == 'POST':
        # 개별 통제 검토 결과 저장
        try:
            data = request.get_json()
            std_control_id = data.get('std_control_id')
            ai_review_recommendation = data.get('ai_review_recommendation', '')
            status = data.get('status', 'completed')
            
            if not std_control_id:
                return jsonify({'success': False, 'message': '기준통제 ID가 필요합니다.'}), 400
            
            save_control_review_result(
                rcm_id, detail_id, std_control_id, 
                ai_review_recommendation, user_info['user_id'], status
            )
            
            log_user_activity(user_info, 'CONTROL_REVIEW_SAVE', f'통제 검토 결과 저장 - Detail ID {detail_id}', 
                             f'/api/rcm/{rcm_id}/detail/{detail_id}/review', 
                             request.remote_addr, request.headers.get('User-Agent'),
                             f'상태: {status}')
            
            return jsonify({
                'success': True, 
                'message': '통제 검토 결과가 저장되었습니다.'
            })
            
        except Exception as e:
            print(f"통제 검토 결과 저장 오류: {e}")
            return jsonify({'success': False, 'message': '통제 검토 결과 저장 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/review/auto-save', methods=['POST'])
@login_required
def rcm_review_auto_save(rcm_id):
    """RCM 검토 결과 자동 저장 (실시간 저장용) - 기존 호환성 유지"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        mapping_data = data.get('mapping_data', {})
        ai_review_data = data.get('ai_review_data', {})
        
        # 자동 저장은 항상 draft 상태로 저장 (RCM 단위)
        review_id = save_rcm_review_result(
            rcm_id, user_info['user_id'], 
            mapping_data, ai_review_data, 'draft', ''
        )
        
        return jsonify({
            'success': True, 
            'message': '자동 저장되었습니다.',
            'review_id': review_id
        })
        
    except Exception as e:
        print(f"자동 저장 오류: {e}")
        return jsonify({'success': False, 'message': '자동 저장 실패'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/detail/<int:detail_id>/ai-review', methods=['POST'])
@login_required
def control_ai_review(rcm_id, detail_id):
    """개별 통제의 AI 검토 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        recommendation = data.get('recommendation', '')
        
        if not recommendation:
            return jsonify({'success': False, 'message': 'AI 검토 의견이 필요합니다.'}), 400
        
        # 개별 통제의 AI 검토 결과 저장
        save_rcm_ai_review(rcm_id, detail_id, recommendation, user_info['user_id'])
        
        log_user_activity(user_info, 'AI_REVIEW', f'통제 AI 검토 - Detail ID {detail_id}', 
                         f'/api/rcm/{rcm_id}/detail/{detail_id}/ai-review', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True, 
            'message': 'AI 검토가 저장되었습니다.'
        })
        
    except Exception as e:
        print(f"AI 검토 저장 오류: {e}")
        return jsonify({'success': False, 'message': 'AI 검토 저장 실패'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/detail/<int:detail_id>/mapping', methods=['POST'])
@login_required
def control_mapping(rcm_id, detail_id):
    """개별 통제의 매핑 저장 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        data = request.get_json()
        std_control_id = data.get('std_control_id')
        
        if not std_control_id:
            return jsonify({'success': False, 'message': '매핑할 기준통제를 선택해주세요.'}), 400
        
        # 개별 통제의 매핑 저장
        save_rcm_mapping(rcm_id, detail_id, std_control_id, user_info['user_id'])
        
        log_user_activity(user_info, 'MAPPING', f'통제 매핑 - Detail ID {detail_id}', 
                         f'/api/rcm/{rcm_id}/detail/{detail_id}/mapping', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True, 
            'message': '매핑이 저장되었습니다.'
        })
        
    except Exception as e:
        print(f"매핑 저장 오류: {e}")
        return jsonify({'success': False, 'message': '매핑 저장 실패'}), 500
