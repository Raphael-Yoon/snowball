from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, get_rcm_details, save_design_evaluation, get_design_evaluations, get_design_evaluations_by_header_id, get_user_evaluation_sessions, delete_evaluation_session, create_evaluation_structure, log_user_activity, get_db, get_or_create_evaluation_header
from snowball_link5 import get_user_info, is_logged_in
import sys
import os
import json
from werkzeug.utils import secure_filename

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
    
    log_user_activity(user_info, 'PAGE_ACCESS', 'RCM 디자인 평가', f'/user/design-evaluation/rcm/{rcm_id}',
                     request.remote_addr, request.headers.get('User-Agent'))
    
    return render_template('user_design_evaluation_rcm.jsp',
                         rcm_id=rcm_id,
                         rcm_info=rcm_info,
                         rcm_details=rcm_details,
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
                'adequacy': eval_data['description_adequacy'],
                'improvement': eval_data['improvement_suggestion'],
                'effectiveness': eval_data['overall_effectiveness'],
                'rationale': eval_data['evaluation_rationale'],
                'actions': eval_data['recommended_actions'],
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