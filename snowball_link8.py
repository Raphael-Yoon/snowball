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
    """내부평가 메인 페이지 - 회사별 카테고리별(ITGC/ELC/TLC) 진행 현황 표시"""
    user_info = get_user_info()

    # 사용자의 RCM 목록 조회
    user_rcms = get_user_rcms(user_info['user_id'])

    # 회사별로 그룹화
    companies = {}
    db = get_db()

    for rcm in user_rcms:
        company_name = rcm.get('company_name', '알 수 없음')

        if company_name not in companies:
            companies[company_name] = {
                'company_name': company_name,
                'categories': {
                    'ITGC': [],
                    'ELC': [],
                    'TLC': []
                }
            }

        # 해당 RCM의 통제 카테고리별 개수 조회
        cursor = db.execute('''
            SELECT control_category, COUNT(*) as count
            FROM sb_rcm_detail
            WHERE rcm_id = %s
            GROUP BY control_category
        ''', (rcm['rcm_id'],))

        category_counts = {row[0]: row[1] for row in cursor.fetchall()}
        primary_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else 'ITGC'

        # 해당 RCM의 설계평가 세션 조회
        cursor = db.execute('''
            SELECT DISTINCT
                dh.evaluation_session,
                dh.evaluation_status,
                dh.start_date,
                dh.completed_date,
                oh.evaluation_status as operation_status
            FROM sb_design_evaluation_header dh
            LEFT JOIN sb_operation_evaluation_header oh
                ON dh.rcm_id = oh.rcm_id
                AND dh.evaluation_session = oh.design_evaluation_session
                AND dh.user_id = oh.user_id
            WHERE dh.rcm_id = %s AND dh.user_id = %s
            AND dh.evaluation_status != 'ARCHIVED'
            ORDER BY dh.start_date DESC
        ''', (rcm['rcm_id'], user_info['user_id']))

        sessions = cursor.fetchall()

        if sessions:
            for session_data in sessions:
                evaluation_session = session_data[0]
                evaluation_status = session_data[1]
                start_date = session_data[2]
                completed_date = session_data[3]
                operation_status = session_data[4]

                progress = get_assessment_progress(rcm['rcm_id'], user_info['user_id'], evaluation_session)

                rcm_data = {
                    'rcm_info': rcm,
                    'evaluation_session': evaluation_session,
                    'evaluation_status': evaluation_status,
                    'operation_status': operation_status,
                    'start_date': start_date,
                    'completed_date': completed_date,
                    'progress': progress,
                    'category_counts': category_counts
                }

                companies[company_name]['categories'][primary_category].append(rcm_data)
        else:
            progress = get_assessment_progress(rcm['rcm_id'], user_info['user_id'], 'DEFAULT')

            rcm_data = {
                'rcm_info': rcm,
                'evaluation_session': 'DEFAULT',
                'evaluation_status': 'NOT_STARTED',
                'start_date': None,
                'completed_date': None,
                'progress': progress,
                'category_counts': category_counts
            }

            companies[company_name]['categories'][primary_category].append(rcm_data)

    # 회사별 데이터를 리스트로 변환
    companies_list = list(companies.values())

    log_user_activity(user_info, 'PAGE_ACCESS', '내부평가 메인 페이지', '/internal-assessment',
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'company_count': len(companies_list)})

    return render_template('internal_assessment_main.jsp',
                         companies=companies_list,
                         is_logged_in=is_logged_in(),
                         user_info=user_info)

# 특정 RCM의 내부평가 상세 페이지 (세션별)
@bp_link8.route('/internal-assessment/<int:rcm_id>')
@bp_link8.route('/internal-assessment/<int:rcm_id>/<evaluation_session>')
@login_required
def assessment_detail(rcm_id, evaluation_session='DEFAULT'):
    """특정 RCM의 특정 설계평가 세션에 대한 내부평가 상세 페이지"""
    user_info = get_user_info()

    # RCM 접근 권한 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_info = next((rcm for rcm in user_rcms if rcm['rcm_id'] == rcm_id), None)

    if not rcm_info:
        flash('해당 RCM에 대한 접근 권한이 없습니다.', 'error')
        return redirect(url_for('link8.internal_assessment'))

    # 내부평가 진행 상황 조회 (세션별)
    progress = get_assessment_progress(rcm_id, user_info['user_id'], evaluation_session)

    # 평가 단계별 데이터 조회
    assessment_data = get_assessment_data(rcm_id, user_info['user_id'], evaluation_session)

    log_user_activity(user_info, 'PAGE_ACCESS', '내부평가 상세 페이지',
                     f'/internal-assessment/{rcm_id}/{evaluation_session}',
                     request.remote_addr, request.headers.get('User-Agent'),
                     {'rcm_id': rcm_id, 'evaluation_session': evaluation_session})

    return render_template('assessment_detail.jsp',
                         rcm_info=rcm_info,
                         evaluation_session=evaluation_session,
                         progress=progress,
                         assessment_data=assessment_data,
                         is_logged_in=is_logged_in(),
                         user_info=user_info)

# API: 내부평가 상세 정보 (JSON)
@bp_link8.route('/internal-assessment/api/detail/<int:rcm_id>/<evaluation_session>')
@login_required
def assessment_detail_api(rcm_id, evaluation_session='DEFAULT'):
    """내부평가 상세 정보를 JSON으로 반환하는 API"""
    user_info = get_user_info()

    # RCM 접근 권한 확인
    user_rcms = get_user_rcms(user_info['user_id'])
    rcm_info = next((rcm for rcm in user_rcms if rcm['rcm_id'] == rcm_id), None)

    if not rcm_info:
        return jsonify({'success': False, 'message': '해당 RCM에 대한 접근 권한이 없습니다.'}), 403

    # 내부평가 진행 상황 조회 (세션별)
    progress = get_assessment_progress(rcm_id, user_info['user_id'], evaluation_session)

    db = get_db()

    # 설계평가 상세 정보
    design_detail = {}
    cursor = db.execute('''
        SELECT header_id FROM sb_design_evaluation_header
        WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
    ''', (rcm_id, user_info['user_id'], evaluation_session))
    design_header = cursor.fetchone()

    if design_header:
        header_id = design_header[0]
        # 평가 결과별 통계
        cursor = db.execute('''
            SELECT
                overall_effectiveness,
                COUNT(*) as count
            FROM sb_design_evaluation_line
            WHERE header_id = %s AND overall_effectiveness IS NOT NULL AND overall_effectiveness != ''
            GROUP BY overall_effectiveness
        ''', (header_id,))
        effectiveness_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 미비점이 있는 통제 목록 (부적정)
        cursor = db.execute('''
            SELECT
                control_code,
                overall_effectiveness,
                evaluation_rationale
            FROM sb_design_evaluation_line
            WHERE header_id = %s
            AND overall_effectiveness IN ('부적정', '일부 미흡')
            ORDER BY control_code
        ''', (header_id,))
        inadequate_controls = [dict(row) for row in cursor.fetchall()]

        design_detail = {
            'effectiveness_stats': effectiveness_stats,
            'inadequate_controls': inadequate_controls,
            'total_inadequate': len(inadequate_controls)
        }

    # 운영평가 상세 정보
    operation_detail = {}
    operation_session = f"OP_{evaluation_session}"
    cursor = db.execute('''
        SELECT header_id FROM sb_operation_evaluation_header
        WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
    ''', (rcm_id, user_info['user_id'], operation_session))
    operation_header = cursor.fetchone()

    if operation_header:
        header_id = operation_header[0]
        # 전체 통제 수와 평가 완료된 통제 수 조회
        cursor = db.execute('''
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN conclusion IS NOT NULL AND conclusion != '' THEN 1 END) as evaluated
            FROM sb_operation_evaluation_line
            WHERE header_id = %s
        ''', (header_id,))
        counts = cursor.fetchone()
        total_controls = counts[0] if counts else 0
        evaluated_controls = counts[1] if counts else 0
        not_tested = total_controls - evaluated_controls

        # 결론별 통계 (Effective/Ineffective로 재분류)
        cursor = db.execute('''
            SELECT
                conclusion,
                COUNT(*) as count
            FROM sb_operation_evaluation_line
            WHERE header_id = %s AND conclusion IS NOT NULL AND conclusion != ''
            GROUP BY conclusion
        ''', (header_id,))
        raw_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # Effective/Ineffective로 재분류
        conclusion_stats = {
            'Effective': 0,
            'Ineffective': 0,
            'Not Tested': not_tested
        }

        for conclusion, count in raw_stats.items():
            if conclusion in ('not_applicable', '예외사항 없음', 'effective', '효과적'):
                # Effective로 분류
                conclusion_stats['Effective'] += count
            elif conclusion in ('예외사항 발견', 'ineffective', '비효과적'):
                # Ineffective로 분류
                conclusion_stats['Ineffective'] += count
            else:
                # 기타는 Ineffective로 처리 (안전한 쪽으로)
                conclusion_stats['Ineffective'] += count

        # Ineffective 통제 목록 (예외사항 발견 또는 exception_details 있는 경우)
        cursor = db.execute('''
            SELECT
                control_code,
                conclusion,
                exception_details
            FROM sb_operation_evaluation_line
            WHERE header_id = %s
            AND (conclusion IN ('예외사항 발견', 'ineffective', '비효과적')
                 OR (exception_details IS NOT NULL AND exception_details != ''))
            ORDER BY control_code
        ''', (header_id,))
        ineffective_controls = [dict(row) for row in cursor.fetchall()]

        operation_detail = {
            'conclusion_stats': conclusion_stats,
            'ineffective_controls': ineffective_controls,
            'total_ineffective': len(ineffective_controls),
            'total_controls': total_controls,
            'not_tested': not_tested
        }

    # JSON 응답 반환
    return jsonify({
        'success': True,
        'rcm_info': rcm_info,
        'evaluation_session': evaluation_session,
        'progress': progress,
        'design_detail': design_detail,
        'operation_detail': operation_detail
    })

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
    """내부평가 진행 상황 저장 (세션별)"""
    try:
        user_info = get_user_info()
        data = request.get_json()

        step = data.get('step')
        evaluation_session = data.get('evaluation_session', 'DEFAULT')
        progress_data = data.get('data', {})
        status = data.get('status', 'in_progress')  # pending, in_progress, completed

        # 데이터베이스에 저장
        db = get_db()

        # 기존 데이터 확인 후 업데이트 또는 삽입
        existing_cursor = db.execute('''
            SELECT assessment_id FROM sb_internal_assessment
            WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s AND step = %s
        ''', (rcm_id, user_info['user_id'], evaluation_session, step))

        existing = existing_cursor.fetchone()

        if existing:
            # 업데이트
            db.execute('''
                UPDATE sb_internal_assessment
                SET progress_data = %s, status = %s, updated_date = %s
                WHERE assessment_id = %s
            ''', (json.dumps(progress_data), status, datetime.now(), existing[0]))
        else:
            # 신규 삽입
            db.execute('''
                INSERT INTO sb_internal_assessment
                (rcm_id, user_id, evaluation_session, step, progress_data, status, created_date, updated_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (rcm_id, user_info['user_id'], evaluation_session, step, json.dumps(progress_data),
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
def get_assessment_progress(rcm_id, user_id, evaluation_session='DEFAULT'):
    """특정 RCM의 특정 설계평가 세션에 대한 내부평가 진행 상황 조회"""
    db = get_db()

    # 각 단계별 상태 조회 (세션별로)
    steps_cursor = db.execute('''
        SELECT step, status, updated_date
        FROM sb_internal_assessment
        WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
        ORDER BY step
    ''', (rcm_id, user_id, evaluation_session))
    
    steps_data = steps_cursor.fetchall()

    # 2단계 순차적 워크플로우 초기화 (설계평가 → 운영평가)
    progress = {
        'steps': [
            {'step': 1, 'name': '설계평가', 'status': 'pending', 'description': '통제 설계의 적정성 평가'},
            {'step': 2, 'name': '운영평가', 'status': 'pending', 'description': '통제 운영의 효과성 평가'}
        ],
        'overall_progress': 0,
        'current_step': 1
    }
    
    # 실제 데이터로 업데이트 (2단계만 처리)
    for step_data in steps_data:
        step_num, status, updated_date = step_data
        if 1 <= step_num <= 2:
            progress['steps'][step_num - 1]['status'] = status
            progress['steps'][step_num - 1]['updated_date'] = updated_date

    # 각 단계별 실제 진행상황을 확인하여 자동 업데이트
    progress = update_progress_from_actual_data(rcm_id, user_id, evaluation_session, progress)

    # 전체 진행률 계산 (각 단계의 실제 진행률 평균)
    total_progress = 0
    for step in progress['steps']:
        if step.get('details') and 'progress' in step['details']:
            total_progress += step['details']['progress']
    progress['overall_progress'] = int(total_progress / len(progress['steps']))

    # 현재 진행 단계 찾기
    # 규칙: 설계평가(1단계)가 완료되지 않으면 현재 단계는 1
    #       설계평가 완료 후 운영평가가 진행중/대기 → 현재 단계는 2
    if progress['steps'][0]['status'] != 'completed':
        # 설계평가가 완료되지 않았으면 무조건 1단계
        progress['current_step'] = 1
    elif progress['steps'][1]['status'] != 'completed':
        # 설계평가 완료, 운영평가 미완료 → 2단계
        progress['current_step'] = 2
    else:
        # 모두 완료
        progress['current_step'] = 2

    return progress

def update_progress_from_actual_data(rcm_id, user_id, evaluation_session, progress):
    """특정 설계평가 세션의 실제 데이터를 확인하여 진행상황 자동 업데이트"""

    try:
        db = get_db()

        # 통제 카테고리별 통계 조회
        cursor = db.execute('''
            SELECT control_category, COUNT(*) as total_count
            FROM sb_rcm_detail
            WHERE rcm_id = %s
            GROUP BY control_category
        ''', (rcm_id,))
        category_stats = {row[0]: row[1] for row in cursor.fetchall()}

        # 1단계: 설계평가 (Link6) - 특정 세션의 완료율 계산
        cursor = db.execute('''
            SELECT evaluation_status, total_controls, evaluated_controls, progress_percentage, header_id
            FROM sb_design_evaluation_header
            WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
        ''', (rcm_id, user_id, evaluation_session))

        design_eval = cursor.fetchone()

        # 기본값 설정 (설계평가 헤더가 없을 경우 대비)
        evaluation_status = None
        evaluated_controls = 0

        if design_eval:
            evaluation_status = design_eval[0]
            total_controls_header = design_eval[1] or 0
            evaluated_controls = design_eval[2] or 0
            design_progress = int(design_eval[3] or 0)
            header_id = design_eval[4]

            # 실제 라인 개수를 확인 (헤더의 total_controls가 부정확할 수 있음)
            cursor = db.execute('''
                SELECT COUNT(*) as actual_total,
                       COUNT(CASE WHEN overall_effectiveness IS NOT NULL AND overall_effectiveness != '' THEN 1 END) as actual_evaluated
                FROM sb_design_evaluation_line
                WHERE header_id = %s AND control_code IS NOT NULL AND control_code != ''
            ''', (header_id,))
            actual_counts = cursor.fetchone()
            total_controls = actual_counts[0] if actual_counts else total_controls_header
            evaluated_controls = actual_counts[1] if actual_counts else evaluated_controls

            # 실제 진행률 재계산
            design_progress = int((evaluated_controls / max(total_controls, 1)) * 100) if total_controls > 0 else 0

            # 카테고리별 설계평가 진행률 계산
            category_progress = {}
            for category in category_stats.keys():
                cursor = db.execute('''
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN overall_effectiveness IS NOT NULL AND overall_effectiveness != '' THEN 1 END) as evaluated
                    FROM sb_design_evaluation_line line
                    JOIN sb_rcm_detail detail ON line.control_code = detail.control_code AND detail.rcm_id = %s
                    WHERE line.header_id = %s AND detail.control_category = %s
                ''', (rcm_id, header_id, category))
                cat_data = cursor.fetchone()
                if cat_data and cat_data[0] > 0:
                    category_progress[category] = {
                        'total': cat_data[0],
                        'evaluated': cat_data[1],
                        'progress': int((cat_data[1] / cat_data[0]) * 100) if cat_data[0] > 0 else 0
                    }

            progress['steps'][0]['details'] = {
                'total_controls': total_controls,
                'evaluated_controls': evaluated_controls,
                'progress': design_progress,
                'category_progress': category_progress,
                'category_stats': category_stats
            }

            # evaluation_status가 COMPLETED일 때만 완료 처리
            if evaluation_status == 'COMPLETED':
                progress['steps'][0]['status'] = 'completed'
            elif evaluated_controls > 0:
                progress['steps'][0]['status'] = 'in-progress'
        else:
            progress['steps'][0]['status'] = 'pending'

        # 2단계: 운영평가 (Link7) - 특정 세션의 통제별 완료율 계산
        # 운영평가 데이터 확인 (헤더와 조인)
        operation_session = f"OP_{evaluation_session}"

        # 운영평가 헤더의 evaluation_status 조회
        cursor = db.execute('''
            SELECT evaluation_status
            FROM sb_operation_evaluation_header
            WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
        ''', (rcm_id, user_id, operation_session))

        operation_header = cursor.fetchone()
        operation_evaluation_status = operation_header[0] if operation_header else None

        cursor = db.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN line.conclusion IS NOT NULL AND line.conclusion != '' THEN 1 ELSE 0 END) as completed
            FROM sb_operation_evaluation_line line
            JOIN sb_operation_evaluation_header header ON line.header_id = header.header_id
            WHERE header.rcm_id = %s AND header.user_id = %s AND header.evaluation_session = %s
        ''', (rcm_id, user_id, operation_session))

        op_data = cursor.fetchone()
        total_operation_controls = op_data[0] if op_data else 0
        completed_operation_controls = op_data[1] if op_data else 0

        # 운영평가 진행 상황 업데이트 (설계평가 완료 후에만)
        if total_operation_controls > 0:
            # 카테고리별 운영평가 진행률 계산
            category_progress_op = {}
            for category in category_stats.keys():
                cursor = db.execute('''
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN line.conclusion IS NOT NULL AND line.conclusion != '' THEN 1 END) as completed
                    FROM sb_operation_evaluation_line line
                    JOIN sb_rcm_detail detail ON line.control_code = detail.control_code AND detail.rcm_id = %s
                    WHERE line.header_id = (
                        SELECT header_id FROM sb_operation_evaluation_header
                        WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
                    ) AND detail.control_category = %s
                ''', (rcm_id, rcm_id, user_id, operation_session, category))
                cat_data = cursor.fetchone()
                if cat_data and cat_data[0] > 0:
                    category_progress_op[category] = {
                        'total': cat_data[0],
                        'completed': cat_data[1],
                        'progress': int((cat_data[1] / cat_data[0]) * 100) if cat_data[0] > 0 else 0
                    }

            progress['steps'][1]['details'] = {
                'total_controls': total_operation_controls,
                'completed_controls': completed_operation_controls,
                'progress': int((completed_operation_controls / max(total_operation_controls, 1)) * 100),
                'category_progress': category_progress_op,
                'category_stats': category_stats
            }

            # 운영평가 상태 결정 로직
            # - 설계평가 완료 여부: evaluation_status == 'COMPLETED' (버튼 클릭 기준)
            # - 운영평가 완료 여부: 모든 통제의 conclusion이 입력되었는지 (completed_operation_controls == total_operation_controls)

            if evaluation_status == 'COMPLETED':
                # 설계평가 완료 상태
                if total_operation_controls > 0 and completed_operation_controls == total_operation_controls:
                    # 상태 5: 모든 통제 평가 완료 -> 운영평가 완료
                    progress['steps'][1]['status'] = 'completed'
                elif completed_operation_controls > 0:
                    # 상태 4: 일부 통제만 평가 완료 -> 운영평가 진행중
                    progress['steps'][1]['status'] = 'in-progress'
                else:
                    # 상태 3: 설계평가 완료, 운영평가 시작 전 (통제 평가 없음)
                    progress['steps'][1]['status'] = 'pending'
            else:
                # 상태 1, 2: 설계평가 미완료 시 운영평가는 비활성화
                progress['steps'][1]['status'] = 'pending'

    except Exception as e:
        print(f"진행상황 업데이트 오류: {e}")
        import traceback
        traceback.print_exc()

    return progress

def get_assessment_data(rcm_id, user_id, evaluation_session='DEFAULT'):
    """특정 RCM의 특정 세션에 대한 내부평가 데이터 조회"""
    db = get_db()

    data_cursor = db.execute('''
        SELECT step, progress_data, status
        FROM sb_internal_assessment
        WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s
        ORDER BY step
    ''', (rcm_id, user_id, evaluation_session))

    data = {}
    for row in data_cursor.fetchall():
        step, progress_data, status = row
        try:
            data[step] = {
                'data': json.loads(progress_data) if progress_data else {},
                'status': status
            }
        except json.JSONDecodeError:
            data[step] = {'data': {}, 'status': status}

    return data

def get_step_data(rcm_id, user_id, step, evaluation_session='DEFAULT'):
    """특정 단계의 데이터 조회"""
    db = get_db()

    result_cursor = db.execute('''
        SELECT progress_data, status
        FROM sb_internal_assessment
        WHERE rcm_id = %s AND user_id = %s AND evaluation_session = %s AND step = %s
    ''', (rcm_id, user_id, evaluation_session, step))
    
    result = result_cursor.fetchone()
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