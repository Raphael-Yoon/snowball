@bp_link7.route('/api/operation-evaluation/save', methods=['POST'])
@login_required
def save_operation_evaluation_api():
    """운영평가 결과 저장 API"""
    import json
    user_info = get_user_info()
    
    # FormData 처리 (파일 포함)
    rcm_id = request.form.get('rcm_id')
    design_evaluation_session = request.form.get('design_evaluation_session')
    control_code = request.form.get('control_code')
    evaluation_data_str = request.form.get('evaluation_data')
    
    # JSON 문자열 파싱
    try:
        evaluation_data = json.loads(evaluation_data_str) if evaluation_data_str else None
    except:
        return jsonify({'success': False, 'message': '평가 데이터 형식이 올바르지 않습니다.'})
    
    # 이미지 파일 수집
    uploaded_images = []
    for key in request.files:
        if key.startswith('evaluation_image_'):
            file = request.files[key]
            if file and file.filename:
                is_valid, error_msg = file_manager.validate_image_file(file)
                if not is_valid:
                    return jsonify({'success': False, 'message': f'이미지 오류: {error_msg}'})
                uploaded_images.append(file)
    
    # 엑셀 파일 (수동통제용)
    excel_file = request.files.get('sample_excel')
    if excel_file and excel_file.filename:
        is_valid, error_msg = file_manager.validate_excel_file(excel_file)
        if not is_valid:
            return jsonify({'success': False, 'message': f'엑셀 오류: {error_msg}'})

    if not all([rcm_id, design_evaluation_session, control_code, evaluation_data]):
        return jsonify({'success': False, 'message': '필수 데이터가 누락되었습니다.'})

    operation_evaluation_session = f"OP_{design_evaluation_session}"
    
    try:
        # 권한 확인
        with get_db() as conn:
            access_check = conn.execute('''
                SELECT permission_type FROM sb_user_rcm
                WHERE user_id = ? AND rcm_id = ? AND is_active = 'Y'
            ''', (user_info['user_id'], rcm_id)).fetchone()
            if not access_check:
                return jsonify({'success': False, 'message': '접근 권한이 없습니다.'})

        # 설계평가 완료 확인
        completed_sessions = get_completed_design_evaluation_sessions(rcm_id, user_info['user_id'])
        if not any(s['evaluation_session'] == design_evaluation_session for s in completed_sessions):
            return jsonify({'success': False, 'message': '설계평가가 완료되지 않았습니다.'})
        
        # 헤더 ID 가져오기
        from auth import get_or_create_operation_evaluation_header
        with get_db() as conn:
            header_id = get_or_create_operation_evaluation_header(
                conn, int(rcm_id), user_info['user_id'], 
                operation_evaluation_session, design_evaluation_session
            )

        # 파일 저장
        saved_files = file_manager.save_evaluation_files(
            uploaded_images=uploaded_images,
            excel_file=excel_file if excel_file and excel_file.filename else None,
            rcm_id=rcm_id,
            header_id=header_id,
            control_code=control_code,
            evaluation_type='operation'
        )
        
        # 평가 데이터에 파일 정보 추가
        if saved_files['images']:
            evaluation_data['images'] = saved_files['images']
        if saved_files['excel']:
            evaluation_data['excel'] = saved_files['excel']

        # 운영평가 저장
        save_operation_evaluation(rcm_id, control_code, user_info['user_id'], 
                                 operation_evaluation_session, design_evaluation_session, evaluation_data)
        
        log_user_activity(user_info, 'OPERATION_EVALUATION', f'운영평가 저장 - {control_code}', 
                         '/api/operation-evaluation/save', request.remote_addr, request.headers.get('User-Agent'))
        
        return jsonify({'success': True, 'message': '저장되었습니다.', 'saved_files': saved_files})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'저장 오류: {str(e)}'})
