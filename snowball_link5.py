from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, save_operation_evaluation, get_operation_evaluations, count_design_evaluations, count_operation_evaluations, log_user_activity, initialize_standard_controls, get_standard_controls, save_rcm_standard_mapping, get_rcm_standard_mappings, get_rcm_detail_mappings, evaluate_rcm_completeness, save_rcm_review_result, get_rcm_review_result, save_rcm_mapping, delete_rcm_mapping, save_rcm_ai_review, get_control_review_result, save_control_review_result
import os
import json
from openai import OpenAI

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
        # RCM 상세 정보 조회 (AI 검토 대상)
        rcm_details = get_rcm_details(rcm_id)
        target_detail = None
        
        for detail in rcm_details:
            if detail['detail_id'] == detail_id:
                target_detail = detail
                break
        
        if not target_detail:
            return jsonify({'success': False, 'message': '통제를 찾을 수 없습니다.'}), 404
        
        # 통제 내용 구성 (AI 검토용)
        control_content = f"""
통제 코드: {target_detail['control_code']}
통제 명: {target_detail['control_name']}
통제 설명: {target_detail.get('control_description', '설명 없음')}
통제 유형: {target_detail.get('control_type', '미분류')}
담당자: {target_detail.get('responsible_party', '미지정')}
""".strip()
        
        # 실제 AI 검토 수행
        ai_recommendation = get_rcm_ai_review(
            control_content=control_content,
            control_code=target_detail['control_code'],
            control_name=target_detail['control_name']
        )
        
        # AI 검토 결과 저장
        save_rcm_ai_review(rcm_id, detail_id, ai_recommendation, user_info['user_id'])
        
        log_user_activity(user_info, 'AI_REVIEW', f'통제 AI 검토 - Detail ID {detail_id}', 
                         f'/api/rcm/{rcm_id}/detail/{detail_id}/ai-review', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True, 
            'message': 'AI 검토가 완료되었습니다.',
            'recommendation': ai_recommendation
        })
        
    except Exception as e:
        print(f"AI 검토 저장 오류: {e}")
        return jsonify({'success': False, 'message': 'AI 검토 저장 실패'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/detail/<int:detail_id>/mapping', methods=['POST', 'DELETE'])
@login_required
def control_mapping(rcm_id, detail_id):
    """개별 통제의 매핑 저장/삭제 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        if request.method == 'POST':
            # 매핑 저장
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
            
        elif request.method == 'DELETE':
            # 매핑 삭제
            delete_rcm_mapping(rcm_id, detail_id, user_info['user_id'])
            
            log_user_activity(user_info, 'MAPPING_DELETE', f'통제 매핑 해제 - Detail ID {detail_id}', 
                             f'/api/rcm/{rcm_id}/detail/{detail_id}/mapping', 
                             request.remote_addr, request.headers.get('User-Agent'))
            
            return jsonify({
                'success': True, 
                'message': '매핑이 해제되었습니다.'
            })
        
    except Exception as e:
        print(f"매핑 처리 오류: {e}")
        return jsonify({'success': False, 'message': '매핑 처리 실패'}), 500

# ================================
# RCM AI 검토 설정 및 함수
# ================================

# ================================================================
# 📝 RCM 기준통제별 AI 검토 프롬프트 설정 (여기서 수정하세요!)
# ================================================================
#
# 🎯 전체 31개 기준통제 코드에 대한 개별 프롬프트 정의
#
# 사용법:
# 1. 각 기준통제 코드별로 고유한 프롬프트를 작성할 수 있습니다
# 2. 통제 코드를 키로 사용하여 프롬프트를 정의합니다
# 3. {control_content} 변수는 자동으로 통제 정보로 치환됩니다
# 4. 주석처리(#)된 통제는 비활성화 상태이며, 주석을 제거하면 활성화됩니다
# 5. 각 통제별 프롬프트는 해당 통제의 특성에 맞게 맞춤형으로 작성되어 있습니다
#
# ================================================================

RCM_CONTROL_PROMPTS = {
    
    # ==================== 기본 프롬프트 ====================
    'default': """다음 RCM 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 통제의 설계와 운영 상태를 실질적으로 분석
- 위험 통제 효과성 평가
- 내부통제 설계 및 운영의 적절성 검토
- 명확한 통제 미비점이 확인되는 경우에만 개선사항 제시

응답형식:
개선권고사항: [구체적이고 실행가능한 개선방안을 서술형으로 제시. 적절한 경우 '현재 통제가 적절히 운영되고 있습니다'로 작성]""",

    # ================================================================
    # 🔐 APD 그룹 (Application 접근권한 및 데이터 관리)
    # ================================================================
    
    # 🔐 APD01 - Application 신규 권한 승인
    'APD01': """Application 신규 권한 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 신규 사용자 권한 요청 및 승인 절차의 적절성
- 업무 분장에 따른 최소 권한 부여 원칙 준수
- 승인권자의 명확성 및 승인 근거 문서화
- 권한 부여 전 신원 확인 및 업무 필요성 검토

응답형식:
개선권고사항: [신규 권한 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD02 - Application 부서이동자 권한 회수
    'APD02': """Application 부서이동자 권한 회수 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 부서이동 시 기존 권한의 즉시 회수 절차
- 새로운 부서 업무에 필요한 권한만 재부여하는 프로세스
- HR 시스템과 연계한 자동화된 권한 관리
- 부서이동자 권한 변경 내역의 기록 및 승인 체계

응답형식:
개선권고사항: [부서이동자 권한 관리 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD03 - Application 퇴사자 접근 권한 회수
    'APD03': """Application 퇴사자 접근 권한 회수 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 퇴사 즉시 모든 시스템 접근 권한의 완전 차단
- HR 시스템과 연계한 실시간 퇴사자 정보 연동
- 퇴사자 계정 비활성화 및 데이터 접근 차단 확인
- 퇴사자가 사용하던 공유 계정 및 서비스 계정 점검

응답형식:
개선권고사항: [퇴사자 권한 회수 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD04 - Application 관리자 권한 제한
    'APD04': """Application 관리자 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 관리자 권한의 최소화 및 업무 필요성에 따른 제한
- 관리자 계정의 별도 관리 및 강화된 인증 적용
- 관리자 활동에 대한 로깅 및 모니터링 체계
- 정기적인 관리자 권한 검토 및 갱신 절차

응답형식:
개선권고사항: [관리자 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD05 - Application 권한 Monitoring
    'APD05': """Application 권한 모니터링 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 사용자 권한 변경 및 접근 활동의 실시간 모니터링
- 비정상적 권한 사용 패턴 탐지 및 알림 체계
- 정기적인 권한 현황 보고서 작성 및 검토
- 미사용 권한 또는 중복 권한의 정리 프로세스

응답형식:
개선권고사항: [권한 모니터링 체계 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD06 - Application 패스워드
    'APD06': """Application 패스워드 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 패스워드 복잡성 정책 설정 및 강제 적용
- 정기적인 패스워드 변경 주기 및 이력 관리
- 패스워드 보관 및 전송 시 암호화 적용
- 패스워드 분실 시 안전한 재설정 절차

응답형식:
개선권고사항: [패스워드 보안 정책 관점에서 구체적인 개선방안 제시]""",

    # 💾 APD07 - Data 직접변경 승인
    'APD07': """데이터 직접변경 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 데이터 직접 변경 요청 시 사전 승인 절차의 적절성
- 변경 사유 및 영향 범위 분석 후 승인 여부 결정
- 데이터 변경 전후 백업 및 롤백 계획 수립
- 변경 내역의 상세 기록 및 사후 검토 체계

응답형식:
개선권고사항: [데이터 변경 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 💾 APD08 - Data 직접변경 권한 제한
    'APD08': """데이터 직접변경 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 데이터 직접 변경 권한의 최소화 및 업무상 필요성 검토
- 데이터베이스 직접 접근 권한자의 제한적 지정
- 변경 권한자의 정기적 검토 및 갱신
- 권한 분리 원칙에 따른 개발/운영 환경 접근 제한

응답형식:
개선권고사항: [데이터 변경 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD09 - DB 접근권한 승인
    'APD09': """DB 접근권한 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- DB 접근 권한 요청 시 업무 필요성 및 정당성 검토
- 데이터베이스별, 스키마별 세분화된 권한 부여
- 승인권자의 명확성 및 승인 기준의 일관성
- 임시 권한 부여 시 만료일 설정 및 자동 회수

응답형식:
개선권고사항: [DB 접근권한 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD10 - DB 관리자 권한 제한
    'APD10': """DB 관리자 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- DB 관리자 권한의 최소 필요 범위로 제한
- DBA 활동에 대한 로깅 및 모니터링 강화
- 프로덕션 DB 접근 시 추가 승인 및 감시 체계
- 개인 DBA 계정과 공용 계정의 분리 관리

응답형식:
개선권고사항: [DB 관리자 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD11 - DB 패스워드
    'APD11': """DB 패스워드 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- DB 계정 패스워드 복잡성 정책의 적절성
- 서비스 계정 및 시스템 계정 패스워드 관리
- DB 접속 시 암호화된 연결 강제 적용
- 패스워드 변경 주기 및 재사용 방지 정책

응답형식:
개선권고사항: [DB 패스워드 보안 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD12 - OS 접근권한 승인
    'APD12': """OS 접근권한 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 서버 OS 접근 권한 요청 시 업무 필요성 검증
- 최소 권한 원칙에 따른 권한 부여
- 서버별, 환경별 차별화된 접근 정책 적용
- 원격 접근 시 VPN 등 보안 연결 강제

응답형식:
개선권고사항: [OS 접근권한 승인 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD13 - OS 관리자 권한 제한
    'APD13': """OS 관리자 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- root 또는 administrator 권한의 제한적 사용
- sudo를 통한 세분화된 권한 관리 체계
- 관리자 활동에 대한 상세 로깅 및 감사 추적
- 특권 계정의 정기적 검토 및 권한 갱신

응답형식:
개선권고사항: [OS 관리자 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD14 - OS 패스워드
    'APD14': """OS 패스워드 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- OS 계정 패스워드 정책의 강도 및 적용 범위
- 시스템 계정 및 서비스 계정 패스워드 관리
- SSH 키 기반 인증 적용 및 패스워드 인증 제한
- 패스워드 파일의 암호화 저장 및 접근 제한

응답형식:
개선권고사항: [OS 패스워드 보안 관점에서 구체적인 개선방안 제시]""",

    # ================================================================
    # ⚙️ CO 그룹 (Computer Operations - 시스템 운영)
    # ================================================================
    
    # ⚙️ CO01 - 배치잡 스케줄 등록 승인
    'CO01': """배치잡 스케줄 등록 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 배치잡 등록 시 사전 승인 절차의 적절성
- 배치잡 실행 시간 및 자원 사용량 검토
- 배치잡 간 의존성 및 충돌 가능성 분석
- 배치잡 실행 결과 모니터링 및 실패 시 알림 체계

응답형식:
개선권고사항: [배치잡 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # ⚙️ CO02 - 배치잡 스케줄 등록 권한 제한
    'CO02': """배치잡 스케줄 등록 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 배치잡 스케줄러 접근 권한의 최소화
- 개발/운영 환경별 차별화된 권한 관리
- 배치잡 등록 권한자의 정기적 검토
- 임시 권한 부여 시 기간 제한 및 자동 만료

응답형식:
개선권고사항: [배치잡 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # ⚙️ CO03 - 배치잡 Monitoring
    'CO03': """배치잡 모니터링 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 배치잡 실행 상태의 실시간 모니터링 체계
- 배치잡 실패 시 즉시 알림 및 에스컬레이션 절차
- 배치잡 실행 이력 및 성능 통계 관리
- 정기적인 배치잡 성능 분석 및 최적화

응답형식:
개선권고사항: [배치잡 모니터링 체계 관점에서 구체적인 개선방안 제시]""",

    # ⚙️ CO04 - 장애처리
    'CO04': """장애처리 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 장애 발생 시 즉시 대응 및 에스컬레이션 절차
- 장애 원인 분석 및 근본 원인 해결 프로세스
- 장애 처리 과정의 문서화 및 이력 관리
- 장애 예방을 위한 사전 점검 및 개선 조치

응답형식:
개선권고사항: [장애처리 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 💾 CO05 - 백업관리
    'CO05': """백업관리 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 정기적인 데이터 백업 수행 및 백업 성공 여부 검증
- 백업 데이터의 무결성 검사 및 복원 테스트
- 오프사이트 백업 보관 및 보안 관리
- 재해 복구 계획 수립 및 정기적 훈련 실시

응답형식:
개선권고사항: [백업 관리 체계 관점에서 구체적인 개선방안 제시]""",

    # 🏢 CO06 - 데이터 센터 접근제한
    'CO06': """데이터 센터 접근제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 데이터센터 물리적 접근 통제 시설 및 절차
- 출입 기록 관리 및 방문자 관리 체계
- CCTV 등 보안 모니터링 시설 운영 상태
- 환경 제어(온습도, 화재 방지) 시설 관리

응답형식:
개선권고사항: [데이터센터 물리보안 관점에서 구체적인 개선방안 제시]""",

    # ================================================================
    # 🔧 PC 그룹 (Program Change - 프로그램 변경관리)
    # ================================================================
    
    # 🔧 PC01 - 프로그램 변경 승인
    'PC01': """프로그램 변경 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 프로그램 변경 요청 시 사전 승인 절차의 적절성
- 변경 영향도 분석 및 위험 평가 수행
- 변경 내용의 상세 검토 및 승인 기준 적용
- 변경 일정 및 롤백 계획의 사전 수립

응답형식:
개선권고사항: [프로그램 변경 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 🔧 PC02 - 프로그램 변경 사용자 테스트
    'PC02': """프로그램 변경 사용자 테스트 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 사용자 테스트 계획 수립 및 테스트 케이스 작성
- 업무 사용자 참여하는 UAT(User Acceptance Test) 수행
- 테스트 결과 문서화 및 이슈 사항 관리
- 테스트 완료 후 운영 반영 승인 절차

응답형식:
개선권고사항: [사용자 테스트 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 🔧 PC03 - 프로그램 이관 승인
    'PC03': """프로그램 이관 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 운영환경 이관 전 최종 승인 절차의 적절성
- 이관 대상 프로그램의 버전 관리 및 검증
- 이관 일정 조정 및 서비스 영향 최소화 방안
- 이관 후 정상 동작 확인 및 모니터링 체계

응답형식:
개선권고사항: [프로그램 이관 승인 관점에서 구체적인 개선방안 제시]""",

    # 🔧 PC04 - 이관담당자 권한 제한
    'PC04': """이관담당자 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 운영환경 이관 권한의 최소 필요 범위로 제한
- 이관 담당자의 지정 및 권한 부여 절차
- 이관 작업 시 이중 확인 및 승인 체계
- 이관 권한의 정기적 검토 및 갱신

응답형식:
개선권고사항: [이관 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # 🔧 PC05 - 개발/운영 환경 분리
    'PC05': """개발/운영 환경 분리 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 개발, 테스트, 운영 환경의 물리적/논리적 분리
- 환경별 접근 권한 및 데이터 접근 제한
- 환경 간 데이터 이동 시 민감정보 마스킹 처리
- 개발자의 운영환경 직접 접근 금지 정책

응답형식:
개선권고사항: [환경 분리 관점에서 구체적인 개선방안 제시]""",

    # ================================================================
    # 📋 PD 그룹 (Project Development - 프로젝트 개발관리)
    # ================================================================
    
    # 📋 PD01 - 타당성 검토 및 승인
    'PD01': """타당성 검토 및 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 프로젝트 타당성 분석의 객관성 및 충분성
- 비용 대비 효과 분석 및 위험 평가 수행
- 다양한 이해관계자의 의견 수렴 및 검토
- 승인 기준 및 절차의 명확성

응답형식:
개선권고사항: [타당성 검토 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 📋 PD02 - 요구사항 정의서 작성 및 검토
    'PD02': """요구사항 정의서 작성 및 검토 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 요구사항의 명확성 및 완전성 검증
- 업무 사용자와 개발자 간 요구사항 합의 과정
- 요구사항 변경 관리 절차 및 이력 추적
- 요구사항 검토 및 승인 단계별 체계

응답형식:
개선권고사항: [요구사항 관리 관점에서 구체적인 개선방안 제시]""",

    # 📋 PD03 - 단위 테스트 및 통합 테스트 진행
    'PD03': """단위 테스트 및 통합 테스트 진행 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 테스트 계획 수립 및 테스트 케이스 작성의 적절성
- 단위 테스트 및 통합 테스트의 충분한 커버리지 확보
- 테스트 결과 문서화 및 결함 관리 프로세스
- 테스트 환경 구성 및 테스트 데이터 관리

응답형식:
개선권고사항: [소프트웨어 테스트 관점에서 구체적인 개선방안 제시]""",

    # 📋 PD04 - 데이터 이관 계획서 작성 및 검토
    'PD04': """데이터 이관 계획서 작성 및 검토 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 데이터 이관 범위 및 방법의 적절성
- 이관 데이터 검증 및 무결성 확인 절차
- 이관 실패 시 롤백 계획 및 복구 방안
- 민감정보 보호를 위한 데이터 마스킹 적용

응답형식:
개선권고사항: [데이터 이관 관점에서 구체적인 개선방안 제시]""",

    # 📋 PD05 - 사용자 교육
    'PD05': """사용자 교육 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 사용자 교육 계획 수립 및 교육 대상자 식별
- 교육 내용의 충실성 및 실무 활용 가능성
- 교육 효과 측정 및 피드백 수집 체계
- 교육 자료 관리 및 지속적 업데이트

응답형식:
개선권고사항: [사용자 교육 관점에서 구체적인 개선방안 제시]""",

    # 📋 PD06 - 검수보고서 승인
    'PD06': """검수보고서 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 검수 기준 및 절차의 명확성
- 검수 결과의 객관성 및 충분성 검토
- 미완료 사항 또는 개선사항에 대한 후속 조치 계획
- 최종 인수 승인 전 모든 요구사항 충족 확인

응답형식:
개선권고사항: [프로젝트 검수 관점에서 구체적인 개선방안 제시]""",

}

def get_rcm_ai_review(control_content, control_code=None, control_name=None):
    """
    RCM 통제에 대한 AI 검토를 수행합니다.
    snowball_link2.py의 get_ai_review 함수를 참조하여 구현
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY 환경변수를 설정해주세요."
        
        client = OpenAI(api_key=api_key)
        
        # 통제별 맞춤형 프롬프트 선택
        if control_code and control_code in RCM_CONTROL_PROMPTS:
            prompt_template = RCM_CONTROL_PROMPTS[control_code]
        else:
            prompt_template = RCM_CONTROL_PROMPTS['default']
        
        # 프롬프트에 통제 내용 삽입
        prompt = prompt_template.format(
            control_content=control_content,
            control_code=control_code or '미지정',
            control_name=control_name or '미지정'
        )
        
        # OpenAI API 호출 (snowball_link2.py와 동일한 설정)
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # 기본값으로 gpt-4o-mini 사용
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "전문적인 내부통제 및 위험관리 전문가입니다. RCM(Risk Control Matrix) 통제의 효과성을 객관적으로 평가하고 실용적인 개선방안을 제시합니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,  # RCM 검토는 간결하게
            temperature=0.3  # 일관성 있는 전문 판정
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # "개선권고사항:" 접두사 제거
        if ai_response.startswith('개선권고사항:'):
            ai_response = ai_response.replace('개선권고사항:', '').strip()
        
        return ai_response
        
    except Exception as e:
        print(f"AI 검토 오류: {e}")
        return f"AI 검토 중 오류가 발생했습니다: {str(e)}"
