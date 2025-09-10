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

bp_link9 = Blueprint('link9', __name__)

# 내부평가 메인 페이지
@bp_link9.route('/internal-assessment')
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
@bp_link9.route('/internal-assessment/<int:rcm_id>')
@login_required  
def assessment_detail(rcm_id):
    """특정 RCM의 내부평가 상세 페이지"""
    user_info = get_user_info()
    
    # RCM 접근 권한 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_info = next((rcm for rcm in user_rcms if rcm['rcm_id'] == rcm_id), None)
    
    if not rcm_info:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link9.internal_assessment'))
    
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
@bp_link9.route('/internal-assessment/<int:rcm_id>/step/<int:step>')
@login_required
def assessment_step(rcm_id, step):
    """내부평가 단계별 페이지"""
    user_info = get_user_info()
    
    # RCM 접근 권한 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_info = next((rcm for rcm in user_rcms if rcm['rcm_id'] == rcm_id), None)
    
    if not rcm_info:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link9.internal_assessment'))
    
    # 단계 유효성 검사 (1-6단계)
    if step < 1 or step > 6:
        flash('유효하지 않은 평가 단계입니다.', 'error')
        return redirect(url_for('link9.assessment_detail', rcm_id=rcm_id))
    
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
@bp_link9.route('/api/internal-assessment/<int:rcm_id>/progress', methods=['POST'])
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
    
    # 6단계 진행상황 초기화
    progress = {
        'steps': [
            {'step': 1, 'name': '평가 계획 수립', 'status': 'pending'},
            {'step': 2, 'name': '통제 설계 평가', 'status': 'pending'},
            {'step': 3, 'name': '운영 효과성 평가', 'status': 'pending'},
            {'step': 4, 'name': '결함 식별 및 평가', 'status': 'pending'},
            {'step': 5, 'name': '개선 계획 수립', 'status': 'pending'},
            {'step': 6, 'name': '평가 보고서 작성', 'status': 'pending'}
        ],
        'overall_progress': 0,
        'current_step': 1
    }
    
    # 실제 데이터로 업데이트
    for step_data in steps_data:
        step_num, status, updated_date = step_data
        if 1 <= step_num <= 6:
            progress['steps'][step_num - 1]['status'] = status
            progress['steps'][step_num - 1]['updated_date'] = updated_date
    
    # 전체 진행률 계산
    completed_steps = sum(1 for step in progress['steps'] if step['status'] == 'completed')
    progress['overall_progress'] = int((completed_steps / 6) * 100)
    
    # 현재 진행 단계 찾기
    for i, step in enumerate(progress['steps']):
        if step['status'] in ['pending', 'in_progress']:
            progress['current_step'] = i + 1
            break
    else:
        progress['current_step'] = 6  # 모든 단계 완료
    
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