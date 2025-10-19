from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from auth import login_required, get_current_user, get_user_rcms, log_user_activity, get_db
import sqlite3
from datetime import datetime
import json

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

bp_link8 = Blueprint('link8', __name__)

# 내부평가 메인 페이지
@bp_link8.route('/internal-assessment')
@login_required
def internal_assessment():
    """내부평가 메인 페이지"""
    user_info = get_user_info()
    
    # 사용자의 RCM 목록 조회
    user_rcms = get_user_rcms(user_info['user_id'])
    
    # 각 RCM의 내부평가 진행 상황 조회
    assessment_progress = []
    db = get_db()
    
    for rcm in user_rcms:
        progress = get_assessment_progress(rcm['rcm_id'], user_info['user_id'])
        assessment_progress.append({
            'rcm_info': rcm,
            'progress': progress
        })
    
    log_user_activity(user_info, 'PAGE_ACCESS', '내부평가 메인 페이지', '/internal-assessment', 
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'rcm_count': len(user_rcms)})
    
    return render_template('internal_assessment_main.jsp',
                         assessment_progress=assessment_progress,
                         is_logged_in=is_logged_in(),
                         user_info=user_info)

# 특정 RCM의 내부평가 상세 페이지
@bp_link8.route('/internal-assessment/<int:rcm_id>')
@login_required  
def assessment_detail(rcm_id):
    """특정 RCM의 내부평가 상세 페이지"""
    user_info = get_user_info()
    
    # RCM 접근 권한 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_info = next((rcm for rcm in user_rcms if rcm['rcm_id'] == rcm_id), None)
    
    if not rcm_info:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link8.internal_assessment'))

    # 내부평가 진행 상황 조회
    progress = get_assessment_progress(rcm_id, user_info['user_id'])
    
    # 평가 단계별 데이터 조회
    assessment_data = get_assessment_data(rcm_id, user_info['user_id'])
    
    log_user_activity(user_info, 'PAGE_ACCESS', '내부평가 상세 페이지', f'/internal-assessment/{rcm_id}', 
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'rcm_id': rcm_id})
    
    return render_template('assessment_detail.jsp',
                         rcm_info=rcm_info,
                         progress=progress,
                         assessment_data=assessment_data,
                         is_logged_in=is_logged_in(),
                         user_info=user_info)

# 내부평가 단계별 페이지
@bp_link8.route('/internal-assessment/<int:rcm_id>/step/<int:step>')
@login_required
def assessment_step(rcm_id, step):
    """내부평가 단계별 페이지"""
    user_info = get_user_info()
    
    # RCM 접근 권한 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_info = next((rcm for rcm in user_rcms if rcm['rcm_id'] == rcm_id), None)
    
    if not rcm_info:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link8.internal_assessment'))

    # 단계 유효성 검사 (1-6단계)
    if step < 1 or step > 6:
        flash('유효하지 않은 평가 단계입니다.', 'error')
        return redirect(url_for('link8.assessment_detail', rcm_id=rcm_id))
    
    # 해당 단계의 데이터 조회
    step_data = get_step_data(rcm_id, user_info['user_id'], step)
    
    # 단계별 템플릿 매핑
    step_templates = {
        1: 'assessment_step1_planning.jsp',
        2: 'assessment_step2_design.jsp', 
        3: 'assessment_step3_operation.jsp',
        4: 'assessment_step4_defects.jsp',
        5: 'assessment_step5_improvement.jsp',
        6: 'assessment_step6_report.jsp'
    }
    
    template = step_templates.get(step, 'assessment_step_generic.jsp')
    
    log_user_activity(user_info, 'PAGE_ACCESS', f'내부평가 {step}단계', 
                     f'/internal-assessment/{rcm_id}/step/{step}', 
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'rcm_id': rcm_id, 'step': step})
    
    return render_template(template,
                         rcm_info=rcm_info,
                         step=step,
                         step_data=step_data,
                         is_logged_in=is_logged_in(),
                         user_info=user_info)

# API: 내부평가 진행 상황 저장
@bp_link8.route('/api/internal-assessment/<int:rcm_id>/progress', methods=['POST'])
@login_required
def save_assessment_progress(rcm_id):
    """내부평가 진행 상황 저장"""
    try:
        user_info = get_user_info()
        data = request.get_json()
        
        step = data.get('step')
        progress_data = data.get('data', {})
        status = data.get('status', 'in_progress')  # pending, in_progress, completed
        
        # 데이터베이스에 저장
        db = get_db()
        cursor = db.cursor()
        
        # 기존 데이터 확인 후 업데이트 또는 삽입
        cursor.execute('''
            SELECT assessment_id FROM sb_internal_assessment 
            WHERE rcm_id = ? AND user_id = ? AND step = ?
        ''', (rcm_id, user_info['user_id'], step))
        
        existing = cursor.fetchone()
        
        if existing:
            # 업데이트
            cursor.execute('''
                UPDATE sb_internal_assessment 
                SET progress_data = ?, status = ?, updated_date = ?
                WHERE assessment_id = ?
            ''', (json.dumps(progress_data), status, datetime.now(), existing[0]))
        else:
            # 신규 삽입
            cursor.execute('''
                INSERT INTO sb_internal_assessment 
                (rcm_id, user_id, step, progress_data, status, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (rcm_id, user_info['user_id'], step, json.dumps(progress_data), 
                  status, datetime.now(), datetime.now()))
        
        db.commit()
        
        log_user_activity(user_info, 'DATA_SAVE', f'내부평가 {step}단계 저장', 
                         f'/api/internal-assessment/{rcm_id}/progress',
                         request.remote_addr, request.headers.get('User-Agent'),
                         {'rcm_id': rcm_id, 'step': step, 'status': status})
        
        return jsonify({
            'success': True,
            'message': f'{step}단계 진행상황이 저장되었습니다.'
        })
        
    except Exception as e:
        print(f"내부평가 진행상황 저장 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'저장 중 오류가 발생했습니다: {str(e)}'
        }), 500

# 헬퍼 함수들
def get_assessment_progress(rcm_id, user_id):
    """특정 RCM의 내부평가 진행 상황 조회"""
    db = get_db()
    cursor = db.cursor()
    
    # 각 단계별 상태 조회
    cursor.execute('''
        SELECT step, status, updated_date 
        FROM sb_internal_assessment 
        WHERE rcm_id = ? AND user_id = ?
        ORDER BY step
    ''', (rcm_id, user_id))
    
    steps_data = cursor.fetchall()
    
    # 3단계 순차적 워크플로우 초기화
    progress = {
        'steps': [
            {'step': 1, 'name': 'RCM 평가', 'status': 'pending', 'description': 'RCM 데이터 조회 및 AI 검토'},
            {'step': 2, 'name': '설계평가', 'status': 'pending', 'description': '통제 설계의 적정성 평가'},
            {'step': 3, 'name': '운영평가', 'status': 'pending', 'description': '통제 운영의 효과성 평가'}
        ],
        'overall_progress': 0,
        'current_step': 1
    }
    
    # 실제 데이터로 업데이트 (3단계만 처리)
    for step_data in steps_data:
        step_num, status, updated_date = step_data
        if 1 <= step_num <= 3:
            progress['steps'][step_num - 1]['status'] = status
            progress['steps'][step_num - 1]['updated_date'] = updated_date

    # 각 단계별 실제 진행상황을 확인하여 자동 업데이트
    progress = update_progress_from_actual_data(rcm_id, user_id, progress)

    # 전체 진행률 계산
    completed_steps = sum(1 for step in progress['steps'] if step['status'] == 'completed')
    progress['overall_progress'] = int((completed_steps / 3) * 100)

    # 현재 진행 단계 찾기
    for i, step in enumerate(progress['steps']):
        if step['status'] in ['pending', 'in_progress']:
            progress['current_step'] = i + 1
            break
    else:
        progress['current_step'] = 3  # 모든 단계 완료
    
    return progress

def update_progress_from_actual_data(rcm_id, user_id, progress):
    """실제 데이터를 확인하여 진행상황 자동 업데이트"""
    from auth import get_completed_design_evaluation_sessions, get_operation_evaluations

    try:
        db = get_db()

        # 1단계: RCM 평가 (Link5) - 표준통제 매핑 완료율 계산
        cursor = db.execute('''
            SELECT COUNT(DISTINCT rd.detail_id) as total_controls,
                   COUNT(DISTINCT CASE WHEN sm.mapping_id IS NOT NULL THEN rd.detail_id END) as mapped_controls,
                   COUNT(DISTINCT CASE WHEN ce.eval_id IS NOT NULL THEN rd.detail_id END) as reviewed_controls
            FROM sb_rcm_detail rd
            LEFT JOIN sb_rcm_standard_mapping sm ON rd.rcm_id = sm.rcm_id AND rd.control_code = sm.control_code AND sm.is_active = 'Y'
            LEFT JOIN sb_rcm_completeness_eval ce ON rd.rcm_id = ce.rcm_id
            WHERE rd.rcm_id = ?
        ''', (rcm_id,))

        rcm_data = cursor.fetchone()
        total_controls = rcm_data[0] if rcm_data else 0
        mapped_controls = rcm_data[1] if rcm_data else 0
        reviewed_controls = rcm_data[2] if rcm_data else 0

        # RCM 평가 진행률 계산 (매핑 + 검토)
        if total_controls > 0:
            mapping_progress = (mapped_controls / total_controls) * 50  # 매핑 50%
            review_progress = (reviewed_controls / total_controls) * 50  # 검토 50%
            rcm_progress = int(mapping_progress + review_progress)

            progress['steps'][0]['details'] = {
                'total_controls': total_controls,
                'mapped_controls': mapped_controls,
                'reviewed_controls': reviewed_controls,
                'progress': rcm_progress
            }

            if rcm_progress >= 100:
                progress['steps'][0]['status'] = 'completed'
            elif rcm_progress > 0:
                progress['steps'][0]['status'] = 'in_progress'

        # 2단계: 설계평가 (Link6) - 세션별 완료율 계산
        completed_design_sessions = get_completed_design_evaluation_sessions(rcm_id, user_id)

        # 전체 설계평가 세션 수 조회
        cursor = db.execute('''
            SELECT COUNT(DISTINCT evaluation_session)
            FROM sb_design_evaluation
            WHERE rcm_id = ? AND user_id = ?
        ''', (rcm_id, user_id))
        total_sessions = cursor.fetchone()[0] if cursor.fetchone() else 0

        completed_count = len(completed_design_sessions) if completed_design_sessions else 0

        progress['steps'][1]['details'] = {
            'total_sessions': max(total_sessions, completed_count),
            'completed_sessions': completed_count,
            'progress': int((completed_count / max(total_sessions, 1)) * 100) if total_sessions > 0 else 0
        }

        if completed_design_sessions:
            progress['steps'][1]['status'] = 'completed'
        elif progress['steps'][0]['status'] in ['completed', 'in_progress']:
            progress['steps'][1]['status'] = 'in_progress'

        # 3단계: 운영평가 (Link7) - 통제별 완료율 계산
        if completed_design_sessions:
            total_operation_controls = 0
            completed_operation_controls = 0

            for session in completed_design_sessions:
                operation_session = f"OP_{session['evaluation_session']}"
                operations = get_operation_evaluations(rcm_id, user_id, operation_session, session['evaluation_session'])

                if operations:
                    # 운영평가 대상 통제 수 계산
                    for op in operations:
                        total_operation_controls += 1
                        # conclusion이 있으면 완료로 간주
                        if op.get('conclusion'):
                            completed_operation_controls += 1

            progress['steps'][2]['details'] = {
                'total_controls': total_operation_controls,
                'completed_controls': completed_operation_controls,
                'progress': int((completed_operation_controls / max(total_operation_controls, 1)) * 100) if total_operation_controls > 0 else 0
            }

            if total_operation_controls > 0 and completed_operation_controls == total_operation_controls:
                progress['steps'][2]['status'] = 'completed'
            elif total_operation_controls > 0:
                progress['steps'][2]['status'] = 'in_progress'
            elif progress['steps'][1]['status'] == 'completed':
                progress['steps'][2]['status'] = 'in_progress'

    except Exception as e:
        print(f"진행상황 업데이트 오류: {e}")
        import traceback
        traceback.print_exc()

    return progress

def get_assessment_data(rcm_id, user_id):
    """특정 RCM의 내부평가 데이터 조회"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT step, progress_data, status 
        FROM sb_internal_assessment 
        WHERE rcm_id = ? AND user_id = ?
        ORDER BY step
    ''', (rcm_id, user_id))
    
    data = {}
    for row in cursor.fetchall():
        step, progress_data, status = row
        try:
            data[step] = {
                'data': json.loads(progress_data) if progress_data else {},
                'status': status
            }
        except json.JSONDecodeError:
            data[step] = {'data': {}, 'status': status}
    
    return data

def get_step_data(rcm_id, user_id, step):
    """특정 단계의 데이터 조회"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT progress_data, status 
        FROM sb_internal_assessment 
        WHERE rcm_id = ? AND user_id = ? AND step = ?
    ''', (rcm_id, user_id, step))
    
    result = cursor.fetchone()
    if result:
        progress_data, status = result
        try:
            return {
                'data': json.loads(progress_data) if progress_data else {},
                'status': status
            }
        except json.JSONDecodeError:
            return {'data': {}, 'status': status}
    
    return {'data': {}, 'status': 'pending'}