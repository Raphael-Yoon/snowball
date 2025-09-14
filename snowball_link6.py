from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, get_user_evaluation_sessions, delete_evaluation_session, create_evaluation_structure, log_user_activity, get_db, get_or_create_evaluation_header, get_rcm_detail_mappings
from snowball_link5 import get_user_info, is_logged_in
import sys
import os
import json
from werkzeug.utils import secure_filename
from flask import send_file
import tempfile
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from openpyxl.styles.colors import Color

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

@bp_link6.route('/design-evaluation/rcm/<int:rcm_id>')
@login_required  
def user_design_evaluation_rcm(rcm_id):
    """사용자 디자인 평가 페이지 (RCM별)"""
    user_info = get_user_info()
    
    # 사용자가 해당 RCM에 접근 권한이 있는지 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_ids = [rcm['rcm_id'] for rcm in user_rcms]
    
    if rcm_id not in rcm_ids:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link6.user_design_evaluation'))
    
    # RCM 정보 조회
    rcm_info = None
    for rcm in user_rcms:
        if rcm['rcm_id'] == rcm_id:
            rcm_info = rcm
            break
    
    # RCM 세부 데이터 조회
    rcm_details = get_rcm_details(rcm_id)
    
    # 매핑 정보 조회
    rcm_mappings = get_rcm_detail_mappings(rcm_id)
    
    log_user_activity(user_info, 'PAGE_ACCESS', 'RCM 디자인 평가', f'/user/design-evaluation/rcm/{rcm_id}',
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('user_design_evaluation_rcm.jsp',
                         rcm_id=rcm_id,
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
                         rcm_mappings=rcm_mappings,
                         is_logged_in=is_logged_in(),
                         user_info=user_info,
                         remote_addr=request.remote_addr)

@bp_link6.route('/api/design-evaluation/save', methods=['POST'])
@login_required
def save_design_evaluation_api():
    """설계평가 결과 저장 API"""
    user_info = get_user_info()
    
    # 요청 정보 로깅
    sys.stderr.write(f"[DEBUG] === SAVE API CALLED ===\n")
    sys.stderr.write(f"[DEBUG] Content-Type: {request.content_type}\n")
    sys.stderr.write(f"[DEBUG] User info: {user_info}\n")
    sys.stderr.write(f"[DEBUG] Request method: {request.method}\n")
    sys.stderr.write(f"[DEBUG] Request form keys: {list(request.form.keys())}\n")
    sys.stderr.write(f"[DEBUG] Request files keys: {list(request.files.keys())}\n")
    sys.stderr.flush()
    
    # FormData와 JSON 모두 처리
    if request.content_type and 'multipart/form-data' in request.content_type:
        # FormData 처리 (이미지 포함)
        sys.stderr.write(f"[DEBUG] Processing FormData request\n")
        rcm_id = request.form.get('rcm_id')
        control_code = request.form.get('control_code')
        evaluation_data_str = request.form.get('evaluation_data')
        evaluation_session = request.form.get('evaluation_session')
        
        sys.stderr.write(f"[DEBUG] FormData values:\n")
        sys.stderr.write(f"[DEBUG]   rcm_id: {rcm_id} (type: {type(rcm_id)})\n")
        sys.stderr.write(f"[DEBUG]   control_code: {control_code}\n")
        sys.stderr.write(f"[DEBUG]   evaluation_session: {evaluation_session}\n")
        sys.stderr.write(f"[DEBUG]   evaluation_data_str: {evaluation_data_str}\n")
        sys.stderr.flush()
        
        # JSON 문자열을 파싱
        evaluation_data = json.loads(evaluation_data_str) if evaluation_data_str else None
        sys.stderr.write(f"[DEBUG] Parsed evaluation_data: {evaluation_data}\n")
        sys.stderr.flush()
        
        # 이미지 파일 처리
        uploaded_images = []
        for key in request.files:
            if key.startswith('evaluation_image_'):
                file = request.files[key]
                if file and file.filename:
                    uploaded_images.append(file)
        
        sys.stderr.write(f"[DEBUG] FormData request - images: {len(uploaded_images)}\n")
    else:
        # 기존 JSON 처리
        sys.stderr.write(f"[DEBUG] Processing JSON request\n")
        data = request.get_json()
        sys.stderr.write(f"[DEBUG] JSON data: {data}\n")
        rcm_id = data.get('rcm_id') if data else None
        control_code = data.get('control_code') if data else None
        evaluation_data = data.get('evaluation_data') if data else None
        evaluation_session = data.get('evaluation_session') if data else None
        uploaded_images = []
        sys.stderr.write(f"[DEBUG] Extracted values from JSON:\n")
        sys.stderr.write(f"[DEBUG]   rcm_id: {rcm_id}\n")
        sys.stderr.write(f"[DEBUG]   control_code: {control_code}\n")
        sys.stderr.write(f"[DEBUG]   evaluation_session: {evaluation_session}\n")
        sys.stderr.write(f"[DEBUG]   evaluation_data: {evaluation_data}\n")
        sys.stderr.flush()
    
    sys.stderr.write(f"[DEBUG] Raw request data received\n")
    sys.stderr.write(f"[DEBUG] User info: {user_info}\n")
    sys.stderr.flush()
    
    # 디버깅용 로그
    sys.stderr.write(f"[DEBUG] Design evaluation save request: rcm_id={rcm_id}, control_code={control_code}, evaluation_session='{evaluation_session}'\n")
    sys.stderr.flush()
    
    # 필수 데이터 검증
    sys.stderr.write(f"[DEBUG] Validating required fields:\n")
    sys.stderr.write(f"[DEBUG]   rcm_id: {rcm_id} (valid: {bool(rcm_id)})\n")
    sys.stderr.write(f"[DEBUG]   control_code: {control_code} (valid: {bool(control_code)})\n")
    sys.stderr.write(f"[DEBUG]   evaluation_data: {evaluation_data} (valid: {bool(evaluation_data)})\n")
    sys.stderr.write(f"[DEBUG]   evaluation_session: {evaluation_session} (valid: {bool(evaluation_session)})\n")
    sys.stderr.flush()
    
    if not all([rcm_id, control_code, evaluation_data, evaluation_session]):
        missing_fields = []
        if not rcm_id: missing_fields.append('RCM ID')
        if not control_code: missing_fields.append('통제 코드')
        if not evaluation_data: missing_fields.append('평가 데이터')
        if not evaluation_session: missing_fields.append('세션명')
        
        error_msg = f'필수 데이터가 누락되었습니다: {", ".join(missing_fields)}'
        sys.stderr.write(f"[ERROR] {error_msg}\n")
        sys.stderr.flush()
        
        return jsonify({
            'success': False,
            'message': error_msg
        })
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user accessing RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
                    return jsonify({
                        'success': False,
                        'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                    })
        
        # 이미지 파일 저장
        saved_images = []
        if uploaded_images:
            # 헤더 ID 가져오기 (이미지 저장 폴더명으로 사용)
            with get_db() as conn:
                header_id = get_or_create_evaluation_header(conn, rcm_id, user_info['user_id'], evaluation_session)
            
            # 이미지 저장 디렉토리 생성 (header_id로 분리)
            upload_dir = os.path.join('static', 'uploads', 'design_evaluations', str(rcm_id), str(header_id), control_code)
            os.makedirs(upload_dir, exist_ok=True)
            
            for i, image_file in enumerate(uploaded_images):
                if image_file and image_file.filename:
                    # 디버깅 로그
                    sys.stderr.write(f"[DEBUG] Original filename: '{image_file.filename}'\n")
                    
                    # 확장자를 먼저 분리
                    original_name, original_ext = os.path.splitext(image_file.filename)
                    sys.stderr.write(f"[DEBUG] Original split - name: '{original_name}', ext: '{original_ext}'\n")
                    
                    # 안전한 파일명 생성 (확장자 제외)
                    safe_name = secure_filename(original_name)
                    sys.stderr.write(f"[DEBUG] Secure name: '{safe_name}'\n")
                    
                    # secure_filename이 빈 문자열을 반환하면 기본 이름 사용
                    if not safe_name or safe_name.strip() == '' or safe_name == '_':
                        safe_name = 'evaluation_image'
                        sys.stderr.write(f"[DEBUG] Using default name because secure_filename returned empty or underscore\n")
                    
                    # 중복 방지를 위해 타임스탬프 추가
                    import time
                    timestamp = str(int(time.time()))
                    
                    # 최종 파일명: 안전한이름_타임스탬프_인덱스.확장자
                    safe_filename = f"{safe_name}_{timestamp}_{i}{original_ext.lower()}"
                    sys.stderr.write(f"[DEBUG] Final safe filename: '{safe_filename}'\n")
                    sys.stderr.flush()
                    
                    # 파일 저장
                    file_path = os.path.join(upload_dir, safe_filename)
                    image_file.save(file_path)
                    
                    # 상대 경로로 저장 (DB 저장용)
                    relative_path = f"uploads/design_evaluations/{rcm_id}/{header_id}/{control_code}/{safe_filename}"
                    saved_images.append(relative_path)
            
            # 평가 데이터에 이미지 경로 추가
            if 'images' not in evaluation_data:
                evaluation_data['images'] = []
            evaluation_data['images'].extend(saved_images)
        
        # 설계평가 결과 저장
        sys.stderr.write(f"[DEBUG] Calling save_design_evaluation with: rcm_id={rcm_id}, control_code={control_code}, user_id={user_info['user_id']}, evaluation_session={evaluation_session}\n")
        sys.stderr.write(f"[DEBUG] Evaluation data: {evaluation_data}\n")
        sys.stderr.flush()
        
        save_design_evaluation(rcm_id, control_code, user_info['user_id'], evaluation_data, evaluation_session)
        
        sys.stderr.write(f"[DEBUG] save_design_evaluation completed successfully\n")
        sys.stderr.flush()
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION', f'설계평가 저장 - {control_code}', 
                         f'/api/design-evaluation/save', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '새로운 설계평가 결과가 저장되었습니다.'
        })
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"설계평가 저장 오류: {e}")
        print(f"오류 상세: {error_traceback}")
        sys.stderr.write(f"[ERROR] 설계평가 저장 오류: {e}\n")
        sys.stderr.write(f"[ERROR] 오류 상세: {error_traceback}\n")
        sys.stderr.flush()
        return jsonify({
            'success': False,
            'message': f'저장 중 오류가 발생했습니다: {str(e)}'
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
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user resetting RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
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
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user accessing sessions for RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
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
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user loading data for RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
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
            
            # 세션명으로 로드할 때 실제 header_id를 찾아서 반환
            if evaluations and evaluation_session:
                # 첫 번째 평가 데이터에서 header_id 추출
                actual_header_id = evaluations[0].get('header_id')
                print(f"***** SNOWBALL_LINK6: Found actual header_id={actual_header_id} for session='{evaluation_session}' *****")
        
        # 통제별로 정리
        evaluation_dict = {}
        for eval_data in evaluations:
            control_code = eval_data['control_code']
            evaluation_date = eval_data.get('evaluation_date')
            
            # 디버깅용 로그 추가
            print(f"Control {control_code}: evaluation_date = {evaluation_date} (type: {type(evaluation_date)})")
            
            # 해당 통제의 이미지 파일 찾기
            saved_images = []
            
            # header_id를 찾기 위해 현재 평가 데이터에서 확인
            current_header_id = header_id
            if not current_header_id and evaluation_session:
                # header_id가 없으면 세션명으로 찾기
                try:
                    with get_db() as conn:
                        result = conn.execute('''
                            SELECT header_id FROM sb_design_evaluation_header
                            WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
                        ''', (rcm_id, user_info['user_id'], evaluation_session)).fetchone()
                        if result:
                            current_header_id = result['header_id']
                except Exception as e:
                    print(f"Error finding header_id: {e}")
            
            if current_header_id:
                image_dir = os.path.join('static', 'uploads', 'design_evaluations', str(rcm_id), str(current_header_id), control_code)
                print(f"[DEBUG] Checking image directory: {image_dir}")
                if os.path.exists(image_dir):
                    for filename in os.listdir(image_dir):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                            relative_path = f"uploads/design_evaluations/{rcm_id}/{current_header_id}/{control_code}/{filename}"
                            saved_images.append({
                                'filename': filename,
                                'path': relative_path,
                                'url': f"/static/{relative_path}"
                            })
                    print(f"[DEBUG] Found {len(saved_images)} images for control {control_code}")
                    for img in saved_images:
                        print(f"[DEBUG] Image: {img}")
                else:
                    print(f"[DEBUG] Image directory does not exist: {image_dir}")
            else:
                print(f"[DEBUG] No header_id found for control {control_code}")
            
            evaluation_dict[control_code] = {
                'description_adequacy': eval_data['description_adequacy'],
                'improvement_suggestion': eval_data['improvement_suggestion'],
                'overall_effectiveness': eval_data['overall_effectiveness'],
                'evaluation_rationale': eval_data['evaluation_rationale'],
                'recommended_actions': eval_data['recommended_actions'],
                'evaluation_date': evaluation_date,
                'images': saved_images
            }
        
        response_data = {
            'success': True,
            'evaluations': evaluation_dict,
            'session_name': evaluation_session
        }
        
        # 세션명으로 로드할 때 실제 header_id를 응답에 포함
        if evaluations and evaluation_session and not header_id:
            actual_header_id = evaluations[0].get('header_id')
            response_data['header_id'] = actual_header_id
            print(f"***** SNOWBALL_LINK6: Including header_id={actual_header_id} in response *****")
        
        # header의 completed_date 정보도 포함
        try:
            with get_db() as conn:
                # header_id가 있으면 해당 header의 completed_date 조회
                if header_id:
                    print(f"***** DEBUG: Querying completed_date for header_id={header_id} *****")
                    result = conn.execute('''
                        SELECT completed_date FROM sb_design_evaluation_header
                        WHERE header_id = ?
                    ''', (int(header_id),)).fetchone()
                elif evaluation_session:
                    print(f"***** DEBUG: Querying completed_date for rcm_id={rcm_id}, user_id={user_info['user_id']}, session={evaluation_session} *****")
                    result = conn.execute('''
                        SELECT completed_date FROM sb_design_evaluation_header
                        WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
                    ''', (rcm_id, user_info['user_id'], evaluation_session)).fetchone()
                else:
                    result = None
                    print("***** DEBUG: No header_id or evaluation_session provided *****")
                
                print(f"***** DEBUG: Query result = {result} *****")
                
                if result:
                    response_data['header_completed_date'] = result['completed_date']
                    print(f"***** SNOWBALL_LINK6: Including header_completed_date={result['completed_date']} in response *****")
                else:
                    response_data['header_completed_date'] = None
                    print("***** SNOWBALL_LINK6: Setting header_completed_date=None in response *****")
        except Exception as e:
            print(f"Error fetching header completed_date: {e}")
            response_data['header_completed_date'] = None
        
        return jsonify(response_data)
        
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
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user deleting session for RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
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
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user creating evaluation for RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
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
            'message': '[EVAL-001] 평가 생성 중 오류가 발생했습니다.'
        })

@bp_link6.route('/api/design-evaluation/complete', methods=['POST'])
@login_required
def complete_design_evaluation_api():
    """설계평가 완료 처리 API - header 테이블에 완료일시 업데이트"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    evaluation_session = data.get('evaluation_session')
    
    if not rcm_id or not evaluation_session:
        return jsonify({
            'success': False,
            'message': 'RCM ID와 평가 세션이 필요합니다.'
        })
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user completing RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
                    return jsonify({
                        'success': False,
                        'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                    })
        
        # header 테이블에서 해당 평가 세션의 완료일시 업데이트
        with get_db() as conn:
            # 현재 평가 세션이 존재하는지 확인
            header = conn.execute('''
                SELECT header_id FROM sb_design_evaluation_header
                WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
            ''', (rcm_id, user_info['user_id'], evaluation_session)).fetchone()
            
            if not header:
                return jsonify({
                    'success': False,
                    'message': '해당 평가 세션을 찾을 수 없습니다.'
                })
            
            # completed_date를 현재 시간으로 업데이트
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            conn.execute('''
                UPDATE sb_design_evaluation_header
                SET completed_date = ?, evaluation_status = 'COMPLETED'
                WHERE header_id = ?
            ''', (current_time, header['header_id']))
            
            conn.commit()
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION_COMPLETE', 
                         f'설계평가 완료 - {evaluation_session}', 
                         f'/api/design-evaluation/complete', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '설계평가가 완료 처리되었습니다.',
            'completed_date': current_time
        })
        
    except Exception as e:
        print(f"평가 완료 처리 오류: {e}")
        return jsonify({
            'success': False,
            'message': '완료 처리 중 오류가 발생했습니다.'
        })

@bp_link6.route('/api/design-evaluation/cancel', methods=['POST'])
@login_required
def cancel_design_evaluation_api():
    """설계평가 완료 취소 API - header 테이블의 completed_date를 NULL로 설정"""
    user_info = get_user_info()
    data = request.get_json()
    
    rcm_id = data.get('rcm_id')
    evaluation_session = data.get('evaluation_session')
    
    if not rcm_id or not evaluation_session:
        return jsonify({
            'success': False,
            'message': 'RCM ID와 평가 세션이 필요합니다.'
        })
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user canceling RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
                    return jsonify({
                        'success': False,
                        'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                    })
        
        # header 테이블에서 해당 평가 세션의 완료일시를 NULL로 설정
        with get_db() as conn:
            # 현재 평가 세션이 존재하는지 확인
            header = conn.execute('''
                SELECT header_id, completed_date FROM sb_design_evaluation_header
                WHERE rcm_id = ? AND user_id = ? AND evaluation_session = ?
            ''', (rcm_id, user_info['user_id'], evaluation_session)).fetchone()
            
            if not header:
                return jsonify({
                    'success': False,
                    'message': '해당 평가 세션을 찾을 수 없습니다.'
                })
            
            if not header['completed_date']:
                return jsonify({
                    'success': False,
                    'message': '완료되지 않은 평가입니다.'
                })
            
            # completed_date를 NULL로 설정하고 status를 IN_PROGRESS로 변경
            conn.execute('''
                UPDATE sb_design_evaluation_header
                SET completed_date = NULL, evaluation_status = 'IN_PROGRESS'
                WHERE header_id = ?
            ''', (header['header_id'],))
            
            conn.commit()
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION_CANCEL', 
                         f'설계평가 완료 취소 - {evaluation_session}', 
                         f'/api/design-evaluation/cancel', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({
            'success': True,
            'message': '설계평가 완료가 취소되었습니다.'
        })
        
    except Exception as e:
        print(f"평가 완료 취소 오류: {e}")
        return jsonify({
            'success': False,
            'message': '완료 취소 중 오류가 발생했습니다.'
        })


@bp_link6.route('/api/design-evaluation/download-excel/<int:rcm_id>')
@login_required
def download_evaluation_excel(rcm_id):
    """설계평가 엑셀 다운로드 - 원본 파일의 Template 시트를 통제별로 복사해서 생성"""
    user_info = get_user_info()
    
    try:
        # 사용자가 해당 RCM에 접근 권한이 있는지 확인 (관리자 권한 포함)
        with get_db() as conn:
            # 관리자인지 먼저 확인
            if user_info.get('admin_flag') == 'Y':
                sys.stderr.write(f"[DEBUG] Admin user downloading excel for RCM {rcm_id}\n")
                sys.stderr.flush()
            else:
                # 일반 사용자는 명시적 권한 확인
                access_check = conn.execute('''
                    SELECT permission_type FROM sb_user_rcm
                    WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
                ''', (user_info['user_id'], rcm_id)).fetchone()
                
                if not access_check:
                    return jsonify({
                        'success': False,
                        'message': '해당 RCM에 대한 접근 권한이 없습니다.'
                    }), 403

            # RCM 정보 및 파일 경로 가져오기 (업로드한 사용자의 회사명, 최신 설계평가 세션명 포함)
            rcm_info = conn.execute('''
                SELECT r.rcm_name, r.original_filename, u.company_name
                FROM sb_rcm r
                LEFT JOIN sb_user u ON r.upload_user_id = u.user_id
                WHERE r.rcm_id = ?
            ''', (rcm_id,)).fetchone()
            
            # 현재 사용자의 가장 최신 설계평가 세션명 조회
            evaluation_session = None
            try:
                session_info = conn.execute('''
                    SELECT evaluation_session 
                    FROM sb_design_evaluation_header 
                    WHERE rcm_id = ? AND user_id = ? 
                    ORDER BY start_date DESC 
                    LIMIT 1
                ''', (rcm_id, user_info['user_id'])).fetchone()
                
                if session_info:
                    evaluation_session = session_info['evaluation_session']
            except:
                pass  # 설계평가 세션이 없는 경우 기본값 사용
            
            if not rcm_info or not rcm_info['original_filename']:
                return jsonify({
                    'success': False,
                    'message': '원본 엑셀 파일을 찾을 수 없습니다.'
                }), 404
            
            # RCM 상세 정보 가져오기
            rcm_details = conn.execute('''
                SELECT detail_id, control_code, control_name, control_frequency, control_type, 
                       test_procedure, control_description
                FROM sb_rcm_detail 
                WHERE rcm_id = ? 
                ORDER BY detail_id
            ''', (rcm_id,)).fetchall()
            
            if not rcm_details:
                return jsonify({
                    'success': False,
                    'message': 'RCM 상세 정보를 찾을 수 없습니다.'
                }), 404
            
            # 설계평가 데이터 조회 (평가 근거 및 첫부 이미지)
            evaluation_data = {}
            if evaluation_session:
                try:
                    # 해당 세션의 설계평가 결과 조회 (overall_effectiveness 포함)
                    eval_results = conn.execute('''
                        SELECT l.control_code, l.evaluation_rationale, l.overall_effectiveness, h.header_id
                        FROM sb_design_evaluation_line l
                        JOIN sb_design_evaluation_header h ON l.header_id = h.header_id
                        WHERE h.rcm_id = ? AND h.user_id = ? AND h.evaluation_session = ?
                        ORDER BY l.control_sequence, l.control_code
                    ''', (rcm_id, user_info['user_id'], evaluation_session)).fetchall()
                    
                    print(f"DEBUG: Found {len(eval_results)} evaluation results for session '{evaluation_session}'")
                    for eval_result in eval_results:
                        control_code = eval_result['control_code']
                        rationale = eval_result['evaluation_rationale'] or ''
                        effectiveness = eval_result['overall_effectiveness'] or ''
                        header_id = eval_result['header_id']
                        
                        # 파일 시스템에서 이미지 경로 찾기
                        images_info = ''
                        image_dir = os.path.join('static', 'uploads', 'design_evaluations', str(rcm_id), str(header_id), control_code)
                        if os.path.exists(image_dir):
                            image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                            if image_files:
                                images_info = json.dumps([{'file': f, 'path': os.path.join(image_dir, f)} for f in image_files])
                        
                        print(f"DEBUG: {control_code} - rationale: '{rationale}', effectiveness: '{effectiveness}', images_info: '{images_info}'")
                        evaluation_data[control_code] = {
                            'rationale': rationale,
                            'effectiveness': effectiveness,
                            'images': images_info
                        }
                except Exception as e:
                    print(f"DEBUG: 설계평가 데이터 조회 오류: {e}")
                    pass

        # 원본 엑셀 파일 로드 (회사별 폴더 구조 지원)
        # rcm_info['original_filename']이 이미 상대 경로(company_name/filename.xlsx)인 경우와
        # 기존 방식(filename.xlsx)인 경우 모두 지원
        if os.path.sep in rcm_info['original_filename'] or '/' in rcm_info['original_filename']:
            # 이미 회사별 경로가 포함된 경우
            original_file_path = os.path.join('uploads', rcm_info['original_filename'])
        else:
            # 기존 방식 - uploads 루트에서 찾기
            original_file_path = os.path.join('uploads', rcm_info['original_filename'])
        
        if not os.path.exists(original_file_path):
            return jsonify({
                'success': False,
                'message': f'원본 파일이 존재하지 않습니다: {original_file_path}'
            }), 404
            
        workbook = load_workbook(original_file_path)
        
        # Template 시트가 있는지 확인
        if 'Template' not in workbook.sheetnames:
            return jsonify({
                'success': False,
                'message': '원본 파일에 Template 시트가 없습니다.'
            }), 404
            
        template_sheet = workbook['Template']
        
        # 각 통제별로 Template 시트를 복사해서 새 시트 생성
        for detail in rcm_details:
            control_code = detail['control_code']
            
            # Template 시트 복사
            new_sheet = workbook.copy_worksheet(template_sheet)
            new_sheet.title = control_code
            
            # B3, B5, C7~C11 셀에 정보 입력
            new_sheet['B3'] = user_info.get('company_name', '')  # 회사명
            new_sheet['B5'] = user_info.get('user_name', '')  # 사용자명
            new_sheet['C7'] = detail['control_code']  # 통제코드
            new_sheet['C8'] = detail['control_name']  # 통제명
            new_sheet['C9'] = detail['control_frequency']  # 통제주기
            new_sheet['C10'] = detail['control_type']  # 통제구분
            new_sheet['C11'] = detail['test_procedure'] or ''  # 테스트 절차
            
            # C12에 평가 근거, C13에 첨부 이미지, C14에 효과성 추가
            eval_info = evaluation_data.get(control_code, {})
            rationale_value = eval_info.get('rationale', '')
            effectiveness_value = eval_info.get('effectiveness', '')
            
            new_sheet['C12'] = rationale_value  # 평가 근거
            
            # 여러 라인 텍스트가 있는 셀들의 높이 자동 조정
            # C11 (테스트 절차) 셀 설정
            c11_cell = new_sheet['C11']
            c11_cell.alignment = Alignment(wrap_text=True, vertical='top')
            
            # C12 (평가 근거) 셀 설정  
            c12_cell = new_sheet['C12']
            c12_cell.alignment = Alignment(wrap_text=True, vertical='top')
            
            # 텍스트 길이에 따라 행 높이 자동 조정
            test_procedure_text = detail['test_procedure'] or ''
            rationale_text = rationale_value or ''
            
            # 줄바꿈 개수와 텍스트 길이를 기준으로 높이 계산
            c11_lines = max(1, len(test_procedure_text.split('\n'))) if test_procedure_text else 1
            c12_lines = max(1, len(rationale_text.split('\n'))) if rationale_text else 1
            
            # 긴 텍스트의 경우 줄바꿈이 없어도 자동 줄바꿈으로 인해 여러 줄이 될 수 있음
            # 약 50자당 1줄로 가정 (엑셀 C열 기준)
            if test_procedure_text:
                estimated_c11_lines = max(c11_lines, (len(test_procedure_text) // 50) + 1)
            else:
                estimated_c11_lines = c11_lines
                
            if rationale_text:
                estimated_c12_lines = max(c12_lines, (len(rationale_text) // 50) + 1)
            else:
                estimated_c12_lines = c12_lines
            
            # 최소 높이는 25pt, 최대 높이는 150pt로 제한 (기본 20pt + 줄 수 * 18pt)
            c11_height = max(25, min(150, 20 + (estimated_c11_lines - 1) * 18))
            c12_height = max(25, min(150, 20 + (estimated_c12_lines - 1) * 18))
            
            new_sheet.row_dimensions[11].height = c11_height
            new_sheet.row_dimensions[12].height = c12_height
            
            # C14에 효과성 및 시트 탭 색상 설정
            if effectiveness_value == '효과적' or effectiveness_value.lower() == 'effective':
                new_sheet['C14'] = 'Effective'
                # 효과적인 경우 시트 탭을 연한 녹색으로 설정
                new_sheet.sheet_properties.tabColor = Color(rgb="90EE90")  # 연한 녹색
            elif effectiveness_value == '부분적으로 효과적' or effectiveness_value.lower() == 'partially_effective':
                new_sheet['C14'] = 'Partially Effective'
                # 부분적으로 효과적인 경우 시트 탭을 노란색으로 설정
                new_sheet.sheet_properties.tabColor = Color(rgb="FFD700")  # 금색/노란색
            else:
                new_sheet['C14'] = 'Ineffective'
                # 비효과적인 경우 시트 탭을 연한 빨간색으로 설정
                new_sheet.sheet_properties.tabColor = Color(rgb="FFA0A0")  # 연한 빨간색
            
            # 첫부 이미지 처리 (C13 셀에 이미지 삽입)
            images_info = eval_info.get('images', '')
            print(f"DEBUG: {control_code} - images_info: '{images_info}'")
            if images_info:
                try:
                    from openpyxl.drawing.image import Image as ExcelImage
                    from PIL import Image as PILImage
                    import io
                    
                    # JSON 형태로 저장된 이미지 정보 파싱
                    if images_info.startswith('['):
                        image_list = json.loads(images_info)
                        if image_list and len(image_list) > 0:
                            first_image_path = image_list[0].get('path', '')
                            if first_image_path and os.path.exists(first_image_path):
                                # 이미지를 엑셀에 삽입
                                img = ExcelImage(first_image_path)
                                
                                # 이미지 크기 조정 (셀 크기의 90%로 맞춤)
                                # C13 셀의 크기 정보 가져오기
                                cell = new_sheet['C13']
                                
                                # 기본 셀 크기 (Excel 기본값 기준)
                                # 열 너비 (문자 단위를 픽셀로 변환: 1문자 ≈ 7픽셀)
                                col_width = new_sheet.column_dimensions['C'].width or 8.43  # 기본 열 너비
                                cell_width_px = int(col_width * 7)  # 픽셀 변환
                                
                                # 행 높이 (포인트 단위를 픽셀로 변환: 1pt ≈ 1.33픽셀)
                                row_height = new_sheet.row_dimensions[13].height or 15  # 기본 행 높이
                                cell_height_px = int(row_height * 1.33)  # 픽셀 변환
                                
                                # 셀 크기의 90%로 최대 크기 설정
                                max_width = int(cell_width_px * 0.9)
                                max_height = int(cell_height_px * 0.9)
                                
                                # 최소 크기 보장 (너무 작지 않도록)
                                max_width = max(max_width, 150)
                                max_height = max(max_height, 150)
                                
                                # 원본 이미지 크기 비율 계산
                                original_width = img.width
                                original_height = img.height
                                
                                # 가로세로 비율 유지하며 크기 조정
                                width_ratio = max_width / original_width
                                height_ratio = max_height / original_height
                                
                                # 더 작은 비율을 사용해서 셀에 맞게 조정
                                scale_ratio = min(width_ratio, height_ratio)
                                
                                img.width = int(original_width * scale_ratio)
                                img.height = int(original_height * scale_ratio)
                                
                                new_sheet.add_image(img, 'C13')
                            else:
                                new_sheet['C13'] = f'이미지 파일 없음: {first_image_path}'
                    else:
                        # 단순 문자열 경우
                        new_sheet['C13'] = images_info
                except Exception as e:
                    print(f"DEBUG: 이미지 처리 오류 ({control_code}): {e}")
                    new_sheet['C13'] = f'이미지 처리 오류: {str(e)}'
            else:
                new_sheet['C13'] = ''
        
        # 원본 Template 시트 삭제
        workbook.remove(template_sheet)
        
        # downloads 폴더에 파일 저장
        company_name = rcm_info['company_name'] or '회사명없음'
        evaluation_name = evaluation_session or '설계평가'
        safe_filename = f"{company_name}_{evaluation_name}.xlsx"
        downloads_path = os.path.join('downloads', safe_filename)
        
        # 기존 파일이 있으면 삭제
        if os.path.exists(downloads_path):
            os.remove(downloads_path)
            
        workbook.save(downloads_path)
        workbook.close()
        
        def remove_download_file():
            try:
                if os.path.exists(downloads_path):
                    os.unlink(downloads_path)
            except:
                pass
        
        # 활동 로그 기록
        log_user_activity(user_info, 'DESIGN_EVALUATION_DOWNLOAD', 
                         f'설계평가 엑셀 다운로드 - {rcm_info["rcm_name"]}', 
                         f'/api/design-evaluation/download-excel/{rcm_id}', 
                         request.remote_addr, request.headers.get('User-Agent'))
        
        # 다운로드 파일 전송
        response = send_file(
            downloads_path,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # 요청 완료 후 다운로드 파일 삭제
        response.call_on_close(remove_download_file)
        
        return response
        
    except Exception as e:
        print(f"엑셀 다운로드 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.stderr.write(f"[ERROR] Excel download error: {str(e)}\n")
        sys.stderr.flush()
        
        # 구체적인 오류 메시지 반환
        error_msg = str(e)
        if "No such file or directory" in error_msg:
            error_msg = "원본 RCM 파일을 찾을 수 없습니다."
        elif "Template" in error_msg:
            error_msg = "원본 파일에 Template 시트가 없습니다."
        elif "Permission denied" in error_msg:
            error_msg = "파일 접근 권한이 없습니다."
        else:
            error_msg = f"엑셀 생성 중 오류 발생: {error_msg}"
            
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500