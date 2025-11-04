from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, save_operation_evaluation, get_operation_evaluations, count_design_evaluations, count_operation_evaluations, log_user_activity, initialize_standard_controls, get_standard_controls, save_rcm_standard_mapping, get_rcm_standard_mappings, get_rcm_detail_mappings, evaluate_rcm_completeness, save_rcm_review_result, get_rcm_review_result, save_rcm_mapping, delete_rcm_mapping, save_rcm_ai_review, get_control_review_result, save_control_review_result, get_db, clear_rcm_completion, has_rcm_access
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

def check_ongoing_evaluations(rcm_id, user_id=None):
    """
    진행 중인 평가 확인
    Args:
        rcm_id: RCM ID
        user_id: 사용자 ID (None이면 모든 사용자 체크)
    Returns: {
        'has_design': bool,
        'has_operation': bool,
        'design_sessions': list,
        'operation_sessions': list
    }
    """
    with get_db() as conn:
        # 진행 중인 설계평가 확인 (NOT COMPLETED)
        if user_id is not None:
            # 특정 사용자만 체크
            design_cursor = conn.execute('''
                SELECT evaluation_session, evaluation_status, total_controls, evaluated_controls, user_id
                FROM sb_design_evaluation_header
                WHERE rcm_id = ? AND user_id = ?
                AND evaluation_status != 'COMPLETED'
                AND evaluation_status != 'ARCHIVED'
            ''', (rcm_id, user_id))
        else:
            # 모든 사용자 체크 (RCM 삭제 시)
            design_cursor = conn.execute('''
                SELECT evaluation_session, evaluation_status, total_controls, evaluated_controls, user_id
                FROM sb_design_evaluation_header
                WHERE rcm_id = ?
                AND evaluation_status != 'COMPLETED'
                AND evaluation_status != 'ARCHIVED'
            ''', (rcm_id,))
        design_sessions = [dict(row) for row in design_cursor.fetchall()]

        # 진행 중인 운영평가 확인 (IN_PROGRESS 또는 완료되지 않은 것)
        if user_id is not None:
            # 특정 사용자만 체크
            operation_cursor = conn.execute('''
                SELECT evaluation_session, evaluation_status, user_id
                FROM sb_operation_evaluation_header
                WHERE rcm_id = ? AND user_id = ?
                AND evaluation_status IN ('IN_PROGRESS', 'NOT_STARTED')
            ''', (rcm_id, user_id))
        else:
            # 모든 사용자 체크 (RCM 삭제 시)
            operation_cursor = conn.execute('''
                SELECT evaluation_session, evaluation_status, user_id
                FROM sb_operation_evaluation_header
                WHERE rcm_id = ?
                AND evaluation_status IN ('IN_PROGRESS', 'NOT_STARTED')
            ''', (rcm_id,))
        operation_sessions = [dict(row) for row in operation_cursor.fetchall()]

        return {
            'has_design': len(design_sessions) > 0,
            'has_operation': len(operation_sessions) > 0,
            'design_sessions': design_sessions,
            'operation_sessions': operation_sessions
        }

bp_link5 = Blueprint('link5', __name__)

# RCM 관련 기능들

@bp_link5.route('/rcm')
@login_required
def user_rcm():
    """사용자 RCM 조회 페이지 - 카테고리별 분류"""
    user_info = get_user_info()

    # 사용자가 접근 권한을 가진 RCM 목록 조회
    all_rcms = get_user_rcms(user_info['user_id'])

    # 각 RCM의 설계평가 상태 조회
    with get_db() as conn:
        for rcm in all_rcms:
            # 진행 중인 설계평가가 있는지 확인
            ongoing = conn.execute('''
                SELECT evaluation_session, evaluation_status
                FROM sb_design_evaluation_header
                WHERE rcm_id = ? AND user_id = ?
                AND evaluation_status NOT IN ('COMPLETED', 'ARCHIVED')
                ORDER BY start_date DESC
                LIMIT 1
            ''', (rcm['rcm_id'], user_info['user_id'])).fetchone()

            if ongoing:
                rcm['has_ongoing_evaluation'] = True
                rcm['ongoing_session'] = ongoing['evaluation_session']
            else:
                rcm['has_ongoing_evaluation'] = False
                rcm['ongoing_session'] = None

    # 카테고리별로 분류
    rcms_by_category = {
        'ELC': [rcm for rcm in all_rcms if rcm.get('control_category') == 'ELC'],
        'TLC': [rcm for rcm in all_rcms if rcm.get('control_category') == 'TLC'],
        'ITGC': [rcm for rcm in all_rcms if rcm.get('control_category') == 'ITGC']
    }

    log_user_activity(user_info, 'PAGE_ACCESS', '사용자 RCM 조회', '/user/rcm',
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'rcm_count': len(all_rcms)})

    return render_template('link5_rcm_list.jsp',
                         user_rcms=all_rcms,
                         rcms_by_category=rcms_by_category,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link5.route('/rcm/<int:rcm_id>/view')
@login_required
def user_rcm_view(rcm_id):
    """사용자 RCM 상세 조회 페이지"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자는 모든 RCM 접근 가능)
    if not has_rcm_access(user_info['user_id'], rcm_id):
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link5.user_rcm'))
    
    # 사용자 RCM 목록 조회 (RCM 정보 포함)
    user_rcms = get_user_rcms(user_info['user_id'])
    
    # RCM 기본 정보 조회
    rcm_info = None
    for rcm in user_rcms:
        if rcm['rcm_id'] == rcm_id:
            rcm_info = rcm
            break
    
    # RCM 상세 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    
    return render_template('link5_rcm_view.jsp',
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

# RCM 업로드 기능
@bp_link5.route('/rcm/upload')
@login_required
def rcm_upload():
    """RCM 업로드 페이지 (일반 사용자는 본인 회사, 관리자는 모든 회사)"""
    user_info = get_user_info()
    is_admin = user_info.get('admin_flag') == 'Y'

    # 사용자 목록 조회 (권한 부여용)
    with get_db() as conn:
        if is_admin:
            # 관리자: 모든 활성 사용자 조회
            users = conn.execute('''
                SELECT user_id, user_name, user_email, company_name
                FROM sb_user
                WHERE effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP
                ORDER BY company_name, user_name
            ''').fetchall()
        else:
            # 일반 사용자: 본인 회사 사용자만 조회
            users = conn.execute('''
                SELECT user_id, user_name, user_email, company_name
                FROM sb_user
                WHERE (effective_end_date IS NULL OR effective_end_date > CURRENT_TIMESTAMP)
                  AND company_name = ?
                ORDER BY user_name
            ''', (user_info.get('company_name', ''),)).fetchall()

    return render_template('link5_rcm_upload.jsp',
                         users=[dict(u) for u in users],
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         is_admin=is_admin)

@bp_link5.route('/rcm/column_config', methods=['GET'])
@login_required
def rcm_column_config():
    """RCM 컬럼 설정 정보 조회 (필수 컬럼, 라벨 등)"""
    from rcm_utils import REQUIRED_COLUMNS, COLUMN_LABELS, ALL_STANDARD_COLUMNS

    return jsonify({
        'success': True,
        'required_columns': REQUIRED_COLUMNS,
        'column_labels': COLUMN_LABELS,
        'all_columns': ALL_STANDARD_COLUMNS
    })

@bp_link5.route('/rcm/preview_excel', methods=['POST'])
@login_required
def rcm_preview_excel():
    """엑셀 파일 미리보기 (처음 10행) + 컬럼 정보"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '파일을 선택해주세요.'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '파일을 선택해주세요.'})

        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': 'Excel 파일만 업로드 가능합니다.'})

        # 엑셀 파일 읽기 (헤더 없이 처음 10행)
        import pandas as pd
        df = pd.read_excel(file, header=None, nrows=10)

        # 데이터를 리스트로 변환 (NaN을 빈 문자열로)
        preview_data = []
        for idx, row in df.iterrows():
            row_data = ['' if pd.isna(val) else str(val) for val in row]
            preview_data.append({
                'row_index': int(idx),
                'cells': row_data
            })

        # 컬럼 정보 (인덱스 기반)
        column_info = []
        for col_idx in range(len(df.columns)):
            column_info.append({
                'index': col_idx,
                'label': f'컬럼 {col_idx + 1}'  # A, B, C 대신 숫자 사용
            })

        return jsonify({
            'success': True,
            'data': preview_data,
            'total_columns': len(df.columns),
            'columns': column_info
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'파일 미리보기 중 오류가 발생했습니다: {str(e)}'
        })

@bp_link5.route('/rcm/process_upload', methods=['POST'])
@login_required
def rcm_process_upload():
    """RCM 업로드 처리 (일반 사용자는 본인 회사, 관리자는 모든 회사)"""
    user_info = get_user_info()
    is_admin = user_info.get('admin_flag') == 'Y'

    try:
        rcm_name = request.form.get('rcm_name', '').strip()
        control_category = request.form.get('control_category', 'ITGC').strip()
        description = request.form.get('description', '').strip()
        access_users = request.form.getlist('access_users')
        header_row = int(request.form.get('header_row', 0))

        # 컬럼 매핑 정보 받기
        column_mapping_str = request.form.get('column_mapping', '{}')
        try:
            column_mapping = json.loads(column_mapping_str) if column_mapping_str else None
        except:
            column_mapping = None

        # 유효성 검사
        if not rcm_name:
            return jsonify({'success': False, 'message': 'RCM명은 필수입니다.'})

        if control_category not in ['ELC', 'TLC', 'ITGC']:
            return jsonify({'success': False, 'message': '유효한 카테고리를 선택해주세요.'})

        if 'rcm_file' not in request.files:
            return jsonify({'success': False, 'message': 'Excel 파일을 선택해주세요.'})

        file = request.files['rcm_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Excel 파일을 선택해주세요.'})

        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({'success': False, 'message': 'Excel 파일(.xlsx, .xls)만 업로드 가능합니다.'})

        if header_row < 0 or header_row > 20:
            return jsonify({'success': False, 'message': '데이터 시작 행은 0~20 사이의 값이어야 합니다.'})

        # 일반 사용자는 선택된 사용자들이 모두 본인 회사 소속인지 확인
        if not is_admin and access_users:
            user_company = user_info.get('company_name', '')
            with get_db() as conn:
                for user_id in access_users:
                    if user_id:
                        check_user = conn.execute(
                            'SELECT company_name FROM sb_user WHERE user_id = ?',
                            (int(user_id),)
                        ).fetchone()
                        if check_user and check_user[0] != user_company:
                            return jsonify({
                                'success': False,
                                'message': '본인 회사 사용자에게만 권한을 부여할 수 있습니다.'
                            })

        # RCM 생성
        from auth import create_rcm, grant_rcm_access
        rcm_id = create_rcm(
            rcm_name=rcm_name,
            description=description,
            upload_user_id=user_info['user_id'],
            original_filename=file.filename,
            control_category=control_category
        )

        # Excel 파일 파싱 (개선된 방식 + 사용자 매핑)
        from rcm_utils import parse_excel_file, validate_rcm_data, get_mapping_summary
        rcm_details, mapping_info = parse_excel_file(file, header_row, column_mapping)

        # 데이터 유효성 검증
        is_valid, error_message = validate_rcm_data(rcm_details)
        if not is_valid:
            # RCM 생성 롤백 (실패 시 삭제)
            with get_db() as conn:
                conn.execute('DELETE FROM sb_rcm WHERE rcm_id = ?', (rcm_id,))
                conn.commit()
            return jsonify({'success': False, 'message': error_message})

        # RCM 상세 데이터 저장
        save_rcm_details(rcm_id, rcm_details, control_category)

        # 업로드한 사용자에게 admin 권한 자동 부여
        grant_rcm_access(user_info['user_id'], rcm_id, 'admin', user_info['user_id'])

        # 선택된 사용자들에게 접근 권한 부여
        for user_id in access_users:
            if user_id and int(user_id) != user_info['user_id']:  # 본인 제외
                grant_rcm_access(int(user_id), rcm_id, 'read', user_info['user_id'])

        # 로그 기록
        mapping_summary = get_mapping_summary(mapping_info)
        log_user_activity(user_info, 'RCM_UPLOAD',
                         f'RCM 업로드 - {rcm_name} ({control_category}) - 매핑: {mapping_summary}',
                         '/rcm/process_upload', request.remote_addr, request.headers.get('User-Agent'))

        return jsonify({
            'success': True,
            'message': f'RCM "{rcm_name}"이(가) 성공적으로 업로드되었습니다. (총 {len(rcm_details)}개 통제)',
            'rcm_id': rcm_id,
            'record_count': len(rcm_details),
            'mapping_info': mapping_info
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'업로드 중 오류가 발생했습니다: {str(e)}'
        })

@bp_link5.route('/rcm/<int:rcm_id>/delete', methods=['POST'])
@login_required
def rcm_delete(rcm_id):
    """RCM 물리적 삭제 - admin 권한을 가진 사용자만 가능"""
    user_info = get_user_info()
    is_admin = user_info.get('admin_flag') == 'Y'

    # force 파라미터: 설계평가 진행 중에도 강제 삭제 (사용자 확인 후)
    force_delete = request.json.get('force', False) if request.is_json else False

    try:
        with get_db() as conn:
            # RCM 정보 및 사용자 권한 조회
            rcm = conn.execute('SELECT rcm_name, upload_user_id FROM sb_rcm WHERE rcm_id = ?', (rcm_id,)).fetchone()
            if not rcm:
                return jsonify({'success': False, 'message': 'RCM을 찾을 수 없습니다.'})

            # 권한 확인: 시스템 관리자 또는 RCM에 대한 admin 권한이 있는 사용자
            if not is_admin:
                # 사용자의 RCM 권한 확인
                user_permission = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()

                if not user_permission or user_permission[0] != 'admin':
                    return jsonify({'success': False, 'message': 'RCM 삭제 권한이 없습니다. (admin 권한 필요)'})

            # 진행 중인 평가 확인 (모든 사용자 체크)
            ongoing = check_ongoing_evaluations(rcm_id, user_id=None)

            if ongoing['has_operation']:
                # 운영평가 진행 중 - 삭제 불가
                session_info = ', '.join([s['evaluation_session'] for s in ongoing['operation_sessions']])
                return jsonify({
                    'success': False,
                    'message': f'⛔ 운영평가가 진행 중이므로 RCM을 삭제할 수 없습니다.\n\n진행 중인 운영평가: {session_info}\n\n운영평가를 먼저 삭제해주세요.',
                    'ongoing_operation': True
                })

            if ongoing['has_design']:
                # 설계평가 진행 중 - 삭제 불가
                session_info = ', '.join([s['evaluation_session'] for s in ongoing['design_sessions']])
                return jsonify({
                    'success': False,
                    'message': f'⛔ 설계평가가 진행 중이므로 RCM을 삭제할 수 없습니다.\n\n진행 중인 설계평가: {session_info}\n\n설계평가를 먼저 완료하거나 삭제해주세요.',
                    'ongoing_design': True
                })

            # 물리적 삭제 (Hard delete)
            # 1. 설계평가 데이터 삭제
            # 1-1. 설계평가 라인 삭제
            conn.execute('''
                DELETE FROM sb_design_evaluation_line
                WHERE header_id IN (SELECT header_id FROM sb_design_evaluation_header WHERE rcm_id = ?)
            ''', (rcm_id,))
            # 1-2. 설계평가 헤더 삭제
            conn.execute('DELETE FROM sb_design_evaluation_header WHERE rcm_id = ?', (rcm_id,))

            # 2. 운영평가 데이터 삭제
            # 2-1. 운영평가 라인 삭제
            conn.execute('''
                DELETE FROM sb_operation_evaluation_line
                WHERE header_id IN (SELECT header_id FROM sb_operation_evaluation_header WHERE rcm_id = ?)
            ''', (rcm_id,))
            # 2-2. 운영평가 헤더 삭제
            conn.execute('DELETE FROM sb_operation_evaluation_header WHERE rcm_id = ?', (rcm_id,))

            # 3. RCM 상세 데이터 삭제
            conn.execute('DELETE FROM sb_rcm_detail WHERE rcm_id = ?', (rcm_id,))

            # 4. 사용자-RCM 매핑 삭제
            conn.execute('DELETE FROM sb_user_rcm WHERE rcm_id = ?', (rcm_id,))

            # 5. RCM 마스터 삭제
            conn.execute('DELETE FROM sb_rcm WHERE rcm_id = ?', (rcm_id,))

            conn.commit()

            # 로그 기록
            log_user_activity(user_info, 'RCM_DELETE',
                            f'RCM 삭제 - {rcm["rcm_name"]} (ID: {rcm_id})',
                            f'/rcm/{rcm_id}/delete', request.remote_addr,
                            request.headers.get('User-Agent'))

            return jsonify({
                'success': True,
                'message': f'RCM "{rcm["rcm_name"]}"이(가) 삭제되었습니다.'
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'삭제 중 오류가 발생했습니다: {str(e)}'
        })


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
        return jsonify({'success': False, 'message': '초기화 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/standard-controls')
@login_required
def get_standard_controls_api():
    """기준통제 목록 조회 API"""
    try:
        controls = get_standard_controls()
        return jsonify({'success': True, 'controls': controls})
    except Exception as e:
        return jsonify({'success': False, 'message': '기준통제 조회 중 오류가 발생했습니다.'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/mapping', methods=['GET', 'POST', 'DELETE'])
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
            return jsonify({'success': False, 'message': '매핑 조회 중 오류가 발생했습니다.'}), 500
    
    elif request.method == 'POST':
        # 매핑 저장 (개별 통제 방식으로 변경)
        try:
            data = request.get_json()
            control_code = data.get('control_code')
            std_control_id = data.get('std_control_id')
            
            if not all([control_code, std_control_id]):
                return jsonify({'success': False, 'message': '필수 데이터가 누락되었습니다.'}), 400
            
            # control_code로 detail_id 찾기
            with get_db() as conn:
                result = conn.execute('''
                    SELECT detail_id FROM sb_rcm_detail 
                    WHERE rcm_id = ? AND control_code = ?
                ''', (rcm_id, control_code)).fetchone()
                
                if not result:
                    return jsonify({'success': False, 'message': f'통제코드 {control_code}를 찾을 수 없습니다.'}), 400
                
                detail_id = result['detail_id']
            
            # 개별 통제의 매핑 저장
            save_rcm_mapping(rcm_id, detail_id, std_control_id, user_info['user_id'])
            
            log_user_activity(user_info, 'RCM_MAPPING', f'RCM 기준통제 매핑 - {control_code}', 
                             f'/api/rcm/{rcm_id}/mapping', 
                             request.remote_addr, request.headers.get('User-Agent'))
            
            return jsonify({'success': True, 'message': '매핑이 저장되었습니다.'})
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'매핑 저장 중 오류가 발생했습니다: {str(e)}'}), 500
    
    elif request.method == 'DELETE':
        # 매핑 삭제
        try:
            data = request.get_json()
            control_code = data.get('control_code')
            
            if not control_code:
                return jsonify({'success': False, 'message': '통제코드가 누락되었습니다.'}), 400
            
            # control_code로 detail_id 찾기
            with get_db() as conn:
                result = conn.execute('''
                    SELECT detail_id FROM sb_rcm_detail 
                    WHERE rcm_id = ? AND control_code = ?
                ''', (rcm_id, control_code)).fetchone()
                
                if not result:
                    return jsonify({'success': False, 'message': f'통제코드 {control_code}를 찾을 수 없습니다.'}), 400
                
                detail_id = result['detail_id']
            
            # 매핑 삭제 (mapped_std_control_id를 NULL로 설정)
            with get_db() as conn:
                conn.execute('''
                    UPDATE sb_rcm_detail
                    SET mapped_std_control_id = NULL,
                        mapped_date = NULL,
                        mapped_by = NULL
                    WHERE rcm_id = ? AND detail_id = ?
                ''', (rcm_id, detail_id))
                conn.commit()
            
            log_user_activity(user_info, 'RCM_MAPPING_DELETE', f'RCM 기준통제 매핑 삭제 - {control_code}', 
                             f'/api/rcm/{rcm_id}/mapping', 
                             request.remote_addr, request.headers.get('User-Agent'))
            
            return jsonify({'success': True, 'message': '매핑이 삭제되었습니다.'})
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'매핑 삭제 중 오류가 발생했습니다: {str(e)}'}), 500

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
        
        # 단계별 디버깅
        rcm_details = get_rcm_details(rcm_id)
        
        standard_controls = get_standard_controls()
        
        mappings = get_rcm_standard_mappings(rcm_id)
        
        eval_result = evaluate_rcm_completeness(rcm_id, user_info['user_id'])
        
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
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'완성도 평가 중 오류가 발생했습니다: {str(e)}'}), 500

@bp_link5.route('/rcm/<int:rcm_id>/mapping')
@login_required
def rcm_mapping_page(rcm_id):
    """RCM 기준통제 매핑 화면 (ITGC만 가능)"""
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

    # ITGC가 아닌 경우 접근 차단
    if rcm_info and rcm_info.get('control_category') != 'ITGC':
        flash('기준통제 매핑은 ITGC 카테고리에서만 사용할 수 있습니다.', 'error')
        return redirect(url_for('link5.user_rcm_view', rcm_id=rcm_id))
    
    # RCM 상세 데이터 조회 (매핑할 통제 목록)
    rcm_details = get_rcm_details(rcm_id)
    
    # 기준통제 목록 조회
    standard_controls = get_standard_controls()
    
    # 기존 매핑 조회 (개별 통제 방식으로 변경)
    existing_mappings = get_rcm_detail_mappings(rcm_id)
    
    return render_template('link5_rcm_mapping.jsp',
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
        eval_result = {
            'completeness_score': 0.0,
            'total_controls': 0,
            'mapped_controls': 0,
            'details': []
        }
    
    return render_template('link5_rcm_completeness.jsp',
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         eval_result=eval_result,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link5.route('/rcm/<int:rcm_id>/toggle-completion', methods=['POST'])
@login_required
def toggle_rcm_completion(rcm_id):
    """RCM 완료 상태 토글"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '해당 RCM에 대한 접근 권한이 없습니다.'})
    
    try:
        data = request.get_json()
        complete = data.get('complete', False)
        
        with get_db() as conn:
            if complete:
                # 완료 상태로 변경 - 현재 날짜 설정
                conn.execute('''
                    UPDATE sb_rcm 
                    SET completion_date = CURRENT_TIMESTAMP 
                    WHERE rcm_id = ?
                ''', (rcm_id,))
                
                # 활동 로그 기록
                log_user_activity(user_info, 'RCM_COMPLETE', f'RCM 검토 완료', f'/rcm/{rcm_id}/completeness-report', 
                                success=True, return_code=0, remote_addr=request.remote_addr)
                
                return jsonify({'success': True, 'message': 'RCM 검토가 완료되었습니다.'})
            else:
                # 완료 해제 - completion_date를 NULL로 설정
                conn.execute('''
                    UPDATE sb_rcm 
                    SET completion_date = NULL 
                    WHERE rcm_id = ?
                ''', (rcm_id,))
                
                # 활동 로그 기록
                log_user_activity(user_info, 'RCM_UNCOMPLETE', f'RCM 검토 완료 해제', f'/rcm/{rcm_id}/completeness-report', 
                                success=True, return_code=0, remote_addr=request.remote_addr)
                
                return jsonify({'success': True, 'message': 'RCM 검토 완료가 해제되었습니다.'})
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

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
        
        # 매핑된 기준통제 확인 (없으면 검토 불가)
        std_control_id = target_detail.get('mapped_std_control_id')
        if not std_control_id:
            return jsonify({'success': False, 'message': '먼저 기준통제 매핑을 완료하세요.'}), 400

        # 기준통제 코드/명 조회
        standard_controls = get_standard_controls()
        std_control = next((sc for sc in standard_controls if sc.get('std_control_id') == std_control_id), None)
        if not std_control:
            return jsonify({'success': False, 'message': '기준통제 정보를 찾을 수 없습니다.'}), 404

        std_control_name = std_control.get('control_name')

        # 통제 내용 구성 (AI 검토용) - 매핑된 기준통제 정보 포함
        control_content = f"""
[RCM 통제]
코드: {target_detail['control_code']}
명칭: {target_detail['control_name']}
설명: {target_detail.get('control_description', '설명 없음')}
유형: {target_detail.get('control_type', '미분류')}
담당자: {target_detail.get('responsible_party', '미지정')}

[매핑된 기준통제]
명칭: {std_control_name}
설명: {std_control.get('control_description', '설명 없음')}
""".strip()

        # 실제 AI 검토 수행 (코드가 아닌 내용 중심 판단)
        ai_recommendation = get_rcm_ai_review(
            control_content=control_content,
            std_control_name=std_control_name
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
        return jsonify({'success': False, 'message': '매핑 처리 실패'}), 500

@bp_link5.route('/api/rcm/<int:rcm_id>/standard-control/<int:std_control_id>/mappings', methods=['DELETE'])
@login_required
def delete_standard_control_mappings(rcm_id, std_control_id):
    """특정 기준통제에 매핑된 모든 통제 매핑 해제 API"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    try:
        # 해당 기준통제에 매핑된 모든 통제의 매핑을 해제
        with get_db() as conn:
            result = conn.execute('''
                UPDATE sb_rcm_detail
                SET mapped_std_control_id = NULL,
                    mapped_date = NULL,
                    mapped_by = NULL
                WHERE rcm_id = ? AND mapped_std_control_id = ?
            ''', (rcm_id, std_control_id))
            
            affected_rows = result.rowcount
            conn.commit()
        
        # 완료 상태 해제 (매핑 변경 시)
        clear_rcm_completion(rcm_id)
        
        log_user_activity(user_info, 'STANDARD_CONTROL_MAPPING_DELETE', 
                         f'기준통제 {std_control_id} 매핑 해제 ({affected_rows}건)', 
                         f'/api/rcm/{rcm_id}/standard-control/{std_control_id}/mappings', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True, 
            'message': f'{affected_rows}개 매핑이 해제되었습니다.',
            'affected_count': affected_rows
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'매핑 해제 중 오류가 발생했습니다: {str(e)}'}), 500

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
    'default': """매핑 검토: {control_code} 기준통제에 다음 통제를 매핑했습니다.

통제 내용: {control_content}

먼저 업무영역이 일치하는지 확인하세요:
- 일치하지 않으면: "해당 기준통제와 매핑이 부적절합니다"
- 일치하면서 개선 필요: 구체적인 개선방안
- 일치하고 적절함: "현재 통제 설계가 적정합니다\"""",

    # ================================================================
    # 🔐 APD 그룹 (Application 접근권한 및 데이터 관리)
    # ================================================================
    
    # 🔐 APD01 - Application 신규 권한 승인
    'APD01': """Application 신규 권한 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 Application 신규 권한 승인과 관련된 내용인지 확인 (배치작업, 시스템운영, 데이터처리 등은 부적절한 매핑)
- 통제 영역이 권한 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 권한 요청에 대해 부서장 등의 명시적인 승인을 득하는지 확인
- 모든 사용자가 보유하고 있는 공통 권한은 검토 대상에서 제외
- 시스템에 의해 자동으로 부여되는 권한은 제외하고 수기로 부여되는 권한만 대상으로 함
- 명시적인 승인만 인정하며 참조/전달/회람 등은 승인으로 인정하지 않음
- 자가승인(본인이 본인 권한을 승인)은 승인으로 인정하지 않음
- 승인권자와 권한 요청자 간의 명확한 분리 확인
- 승인 근거 및 사유의 문서화 여부

응답형식:
개선권고사항: [APD01 신규 권한 승인 기준에 따른 구체적인 개선방안 제시]""",

    # 🔐 APD02 - Application 부서이동자 권한 회수
    'APD02': """Application 부서이동자 권한 회수 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 부서이동 시 권한 회수와 관련된 내용인지 확인 (신규 권한 생성, 시스템 운영 등은 부적절한 매핑)
- 통제 영역이 인사이동 관리와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 퇴사자 계정/권한 회수와 관련된 내용인지 확인 (신규 가입, 데이터 백업 등은 부적절한 매핑)
- 통제 영역이 퇴사 후 접근권한 관리와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 애플리케이션 관리자 권한 제한과 관련된 내용인지 확인 (일반 사용자 권한, 데이터 처리 등은 부적절한 매핑)
- 통제 영역이 관리자 권한 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 관리자권한(Superuser 권한)은 IT담당자로 제한되는지 확인
- 현업 사용자는 인정하지 않음을 확인

응답형식:
개선권고사항: [관리자 권한 제한 기준에 따른 구체적인 개선방안 제시]""",

    # 🔐 APD05 - Application 권한 Monitoring
    'APD05': """Application 권한 모니터링 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 애플리케이션 권한 모니터링과 관련된 내용인지 확인 (시스템 성능, 데이터 백업 등은 부적절한 매핑)
- 통제 영역이 접근권한 모니터링과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 애플리케이션 패스워드 정책과 관련된 내용인지 확인 (네트워크 보안, 데이터 암호화 등은 부적절한 매핑)
- 통제 영역이 사용자 인증/패스워드 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 최소 자릿수가 8자리 이상으로 설정되어 있는지 확인
- 영문, 숫자, 특수문자 조합이 포함되어 있는지 확인  
- 추가 설정사항은 평가하지 않음
- 영문/숫자/특수문자 조합이 부족한 경우 자릿수를 늘리는 권고 가능

응답형식:
개선권고사항: [패스워드 8자리 및 조합 기준에서 구체적인 개선방안 제시]""",

    # 💾 APD07 - Data 직접변경 승인
    'APD07': """데이터 직접변경 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 데이터베이스 직접 변경 승인과 관련된 내용인지 확인 (사용자 계정 관리, 시스템 모니터링 등은 부적절한 매핑)
- 통제 영역이 DB 데이터 수정과 관련 없는 경우 '매핑이 부적절함' 지적
- 데이터 변경에 대해 적절한 승인권자의 승인을 받는지 확인
- 자가승인은 승인으로 인정하지 않음

응답형식:
개선권고사항: [데이터 변경 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # 💾 APD08 - Data 직접변경 권한 제한
    'APD08': """데이터 직접변경 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 데이터 직접변경 권한 제한과 관련된 내용인지 확인 (일반 애플리케이션 사용, 보고서 작성 등은 부적절한 매핑)
- 통제 영역이 DB 직접접근 권한관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 데이터 변경은 IT운영자가 수행하는지 확인
- 겸직이 아닌 이상 DBA 등의 수행은 지양하는지 확인
- 현업사용자 등의 직접 데이터 변경은 인정되지 않음을 확인

응답형식:
개선권고사항: [데이터 변경 권한 제한 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD09 - DB 접근권한 승인
    'APD09': """DB 접근권한 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 데이터베이스 접근권한 승인과 관련된 내용인지 확인 (웹 애플리케이션 사용, 배치작업 등은 부적절한 매핑)
- 통제 영역이 DB 접근권한 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 권한 요청에 대해 부서장 등 적절한 승인권자가 승인하는지 확인
- 자가 승인은 인정되지 않음을 확인
- 승인권자는 IT팀장 또는 인프라팀장이 가능함을 확인

응답형식:
개선권고사항: [DB 접근권한 승인 기준에 따른 구체적인 개선방안 제시]""",

    # 🔐 APD10 - DB 관리자 권한 제한
    'APD10': """DB 관리자 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 데이터베이스 관리자 권한 제한과 관련된 내용인지 확인 (애플리케이션 사용자, 비즈니스 프로세스 등은 부적절한 매핑)
- 관리자 권한과 Superuser 권한은 동일한 권한으로 판단
- 통제 영역이 DB 관리자 권한관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 관리자권한(Superuser 권한)은 IT담당자로 제한되는지 확인
- 현업 사용자는 인정하지 않음을 확인

응답형식:
개선권고사항: [DB 관리자 권한 제한 기준에 따른 구체적인 개선방안 제시]""",

    # 🔐 APD11 - DB 패스워드
    'APD11': """DB 패스워드 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 데이터베이스 패스워드 정책과 관련된 내용인지 확인 (애플리케이션 UI, 비즈니스 로직 등은 부적절한 매핑)
- 통제 영역이 DB 인증/패스워드 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- DB 계정 패스워드 최소 길이가 8자리 이상으로 설정되어 있는지 확인
- 영문, 숫자, 특수문자 조합 정책이 적용되어 있는지 확인
- 영문/숫자/특수문자 조합이 부족한 경우 최소 길이를 더 늘려 보완하는 방안 검토
- 서비스 계정 및 시스템 계정도 동일한 패스워드 정책 적용 여부
- DB 접속 시 암호화된 연결 강제 적용 여부
- 기타 추가 설정사항(변경주기, 재사용방지 등)은 현재 운영 상태에 따라 판단

응답형식:
개선권고사항: [DB 패스워드 길이 및 복잡성 정책 관점에서 구체적인 개선방안 제시]""",

    # 🔐 APD12 - OS 접근권한 승인
    'APD12': """OS 접근권한 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 운영체제 접근권한 승인과 관련된 내용인지 확인 (데이터 처리, 비즈니스 승인 등은 부적절한 매핑)
- 통제 영역이 OS 접근권한 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 권한 요청에 대해 부서장 등 적절한 승인권자가 승인하는지 확인
- 자가 승인은 인정되지 않음을 확인
- 승인권자는 IT팀장 또는 인프라팀장이 가능함을 확인

응답형식:
개선권고사항: [OS 접근권한 승인 기준에 따른 구체적인 개선방안 제시]""",

    # 🔐 APD13 - OS 관리자 권한 제한
    'APD13': """OS 관리자 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 운영체제 관리자 권한 제한과 관련된 내용인지 확인 (애플리케이션 기능, 데이터 검증 등은 부적절한 매핑)
- 통제 영역이 OS 관리자 권한관리와 관련 없는 경우 '매핑이 부적절함' 지적
- 관리자 권한과 Superuser 권한은 동일한 권한으로 판단
- 관리자권한(Superuser 권한)은 IT담당자로 제한되는지 확인
- 현업 사용자는 인정하지 않음을 확인

응답형식:
개선권고사항: [OS 관리자 권한 제한 기준에 따른 구체적인 개선방안 제시]""",

    # 🔐 APD14 - OS 패스워드
    'APD14': """OS 패스워드 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 운영체제 패스워드 정책과 관련된 내용인지 확인 (애플리케이션 로그인, 데이터 암호화 등은 부적절한 매핑)
- 통제 영역이 OS 인증/패스워드 관리와 관련 없는 경우 '매핑이 부적절함' 지적
- OS 계정 패스워드 최소 길이가 8자리 이상으로 설정되어 있는지 확인
- 영문, 숫자, 특수문자 조합 정책이 적용되어 있는지 확인
- 영문/숫자/특수문자 조합이 부족한 경우 최소 길이를 더 늘려 보완하는 방안 검토
- 시스템 계정 및 서비스 계정도 동일한 패스워드 정책 적용 여부
- SSH 키 기반 인증 적용 및 패스워드 인증 제한 여부
- 패스워드 파일의 암호화 저장 및 접근 제한 여부
- 기타 추가 설정사항은 현재 운영 상태에 따라 판단

응답형식:
개선권고사항: [OS 패스워드 길이 및 복잡성 정책 관점에서 구체적인 개선방안 제시]""",

    # ================================================================
    # ⚙️ CO 그룹 (Computer Operations - 시스템 운영)
    # ================================================================
    
    # ⚙️ CO01 - 배치잡 스케줄 등록 승인
    'CO01': """배치잡 스케줄 등록 승인 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 배치잡/스케줄 등록과 관련된 내용인지 확인 (사용자 권한관리, 데이터 보안 등은 부적절한 매핑)
- 통제 영역이 시스템 운영/배치 작업과 관련 없는 경우 '매핑이 부적절함' 지적
- 권한 요청에 대해 부서장 등 적절한 승인권자가 승인하는지 확인
- 자가 승인은 인정되지 않음을 확인

응답형식:
개선권고사항: [배치잡 승인 프로세스 관점에서 구체적인 개선방안 제시]""",

    # ⚙️ CO02 - 배치잡 스케줄 등록 권한 제한
    'CO02': """배치잡 스케줄 등록 권한 제한 통제에 대해 검토해주세요:

통제 내용: {control_content}

검토 기준:
- 먼저 통제 내용이 배치작업 등록 권한 제한과 관련된 내용인지 확인 (사용자 계정관리, 데이터 조회 등은 부적절한 매핑)
- 통제 영역이 배치작업 권한관리와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 배치작업 모니터링/감시와 관련된 내용인지 확인 (사용자 접근권한, 데이터 변경 등은 부적절한 매핑)
- 통제 영역이 배치작업 실행상태 모니터링과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 시스템 장애처리/대응과 관련된 내용인지 확인 (사용자 관리, 데이터 입력 등은 부적절한 매핑)
- 통제 영역이 장애발생 시 대응체계와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 데이터/시스템 백업과 관련된 내용인지 확인 (사용자 인증, 배치작업 승인 등은 부적절한 매핑)
- 통제 영역이 데이터 복원/연속성과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 데이터센터/서버룸 물리접근 제한과 관련된 내용인지 확인 (네트워크 접근, 애플리케이션 사용 등은 부적절한 매핑)
- 통제 영역이 물리적 보안과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 프로그램/소스코드 변경과 관련된 내용인지 확인 (데이터 처리, 사용자 권한, 배치작업 등은 부적절한 매핑)
- 통제 영역이 개발/변경관리와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 프로그램 변경 시 사용자 테스트와 관련된 내용인지 확인 (배치작업, 데이터 변경 등은 부적절한 매핑)
- 통제 영역이 개발 테스트 프로세스와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 개발서버에서 운영서버로 이관 승인과 관련된 내용인지 확인 (사용자 구인, 데이터 조회 등은 부적절한 매핑)
- 통제 영역이 소스코드 배포과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 프로그램 이관 담당자 권한 제한과 관련된 내용인지 확인 (일반 애플리케이션 사용, 데이터 업로드 등은 부적절한 매핑)
- 통제 영역이 운영배포 권한관리와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 개발과 운영 환경 분리와 관련된 내용인지 확인 (사용자 권한관리, 데이터 백업 등은 부적절한 매핑)
- 통제 영역이 시스템 환경 구분과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 프로젝트/업무 타당성 검토와 관련된 내용인지 확인 (기술적 운영, 데이터 처리, 시스템 권한 등은 부적절한 매핑)
- 통제 영역이 사업타당성/기획과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 요구사항 정의/분석과 관련된 내용인지 확인 (시스템 운영, 사용자 관리 등은 부적절한 매핑)
- 통제 영역이 요구사항 분석/문서화와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 개발테스트 수행과 관련된 내용인지 확인 (데이터 백업, 사용자 권한 등은 부적절한 매핑)
- 통제 영역이 소프트웨어 테스트와 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 데이터 이관 계획/준비와 관련된 내용인지 확인 (사용자 계정관리, 시스템 모니터링 등은 부적절한 매핑)
- 통제 영역이 데이터 마이그레이션과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 사용자 교육/트레이닝과 관련된 내용인지 확인 (시스템 개발, 데이터 백업 등은 부적절한 매핑)
- 통제 영역이 사용자 교육과 관련 없는 경우 '매핑이 부적절함' 지적
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
- 먼저 통제 내용이 검수/검증 보고서 승인과 관련된 내용인지 확인 (운영 모니터링, 사용자 권한 등은 부적절한 매핑)
- 통제 영역이 프로젝트 결과물 검수와 관련 없는 경우 '매핑이 부적절함' 지적
- 검수 기준 및 절차의 명확성
- 검수 결과의 객관성 및 충분성 검토
- 미완료 사항 또는 개선사항에 대한 후속 조치 계획
- 최종 인수 승인 전 모든 요구사항 충족 확인

응답형식:
개선권고사항: [프로젝트 검수 관점에서 구체적인 개선방안 제시]""",

}

def get_rcm_ai_review(control_content, std_control_name=None):
    """
    RCM 통제에 대한 AI 검토를 수행합니다.
    snowball_link2.py의 get_ai_review 함수를 참조하여 구현
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY 환경변수를 설정해주세요."
        
        client = OpenAI(api_key=api_key)
        
        # 내용 중심 판단: 기본 프롬프트 사용 (이름 힌트만 제공)
        prompt_template = RCM_CONTROL_PROMPTS['default']
        
        # 프롬프트에 통제 내용 삽입
        prompt = prompt_template.format(
            control_content=control_content,
            control_code='미지정',
            control_name=std_control_name or '미지정'
        )
        
        # OpenAI API 호출 (snowball_link2.py와 동일한 설정)
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # 기본값으로 gpt-4o-mini 사용
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "매핑 검토 전문가입니다. 코드 표기(예: PC02, CO01)나 내부 코드명은 무시하고, 통제 '내용'과 '업무영역'으로만 판단하세요. [매핑된 기준통제]의 의미(개념/업무영역)와 [RCM 통제] 내용이 다르면 반드시 '매핑이 부적절합니다'라는 정확한 문구를 포함해 답변하세요. 의미가 일치하고 적정하면 '현재 통제 설계가 적정합니다'라는 정확한 문구를 포함하세요. 중요: 다음 용어들은 동일한 의미로 인식하세요 - OS 관리자 권한 = OS Super User = 시스템 관리자 = root 권한, DB 관리자 권한 = DB Super User = DBA = 데이터베이스 관리자 권한, 애플리케이션 관리자 = 앱 관리자 = Application Admin, 네트워크 관리자 = 망 관리자 = Network Admin, 데이터 = Data, 시스템 = System, 서버 = Server, 프로그램 = Program, 사용자 = User, 관리 = Management, 접근 = Access, 권한 = Authority = Permission, 보안 = Security, 백업 = Backup, 변경 = Change = Modification, 직접변경 = 변경 = 수정 = 갱신 = 업데이트, 담당자 = 지정된 담당자 = 적절한 담당자 = 승인된 담당자, 제한 = 한정 = 통제"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # RCM 검토는 간결하게 (300→150으로 단축)
            temperature=0.3  # 일관성 있는 전문 판정
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # "개선권고사항:" 접두사 제거
        if ai_response.startswith('개선권고사항:'):
            ai_response = ai_response.replace('개선권고사항:', '').strip()
        
        return ai_response

    except Exception as e:
        return f"AI 검토 중 오류가 발생했습니다: {str(e)}"

@bp_link5.route('/rcm/update-name', methods=['POST'])
@login_required
def update_rcm_name():
    """RCM 이름 수정"""
    user_info = get_user_info()

    try:
        rcm_id = int(request.form.get('rcm_id'))
        rcm_name = request.form.get('rcm_name', '').strip()

        if not rcm_name:
            return jsonify({'success': False, 'message': 'RCM 이름은 필수 항목입니다.'})

        # 사용자가 해당 RCM에 접근 권한이 있는지 확인
        user_rcms = get_user_rcms(user_info['user_id'])
        rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]

        if rcm_id not in rcm_ids:
            return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

        # RCM 이름 업데이트
        with get_db() as conn:
            conn.execute('''
                UPDATE sb_rcm
                SET rcm_name = ?
                WHERE rcm_id = ?
            ''', (rcm_name, rcm_id))
            conn.commit()

        return jsonify({
            'success': True,
            'message': 'RCM 이름이 성공적으로 수정되었습니다.'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'오류가 발생했습니다: {str(e)}'})

