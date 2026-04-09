# snowball_link2.py
# 섹션별(4페이지) ITGC 인터뷰 시스템
# 섹션(공통/APD/PC/CO) 단위로 한 페이지에 모아서 표시
# URL 노출 최소화 (Single URL 방식 적용: /itgc_interview)

from flask import Blueprint, render_template, request, session, redirect, url_for
from auth import log_user_activity

# ================================================================
# Blueprint
# ================================================================
bp_link2_1p = Blueprint('link2_1p', __name__)

# ================================================================
# 섹션 정의
# ================================================================
SECTIONS = {
    'common': {
        'name': '공통사항',
        'icon': 'fa-server',
        'q_start': 0,
        'q_end': 5,
    },
    'apd': {
        'name': 'APD (Access to Program & Data)',
        'icon': 'fa-lock',
        'q_start': 6,
        'q_end': 33,
    },
    'pc': {
        'name': 'PC (Program Change)',
        'icon': 'fa-laptop-code',
        'q_start': 34,
        'q_end': 40,
    },
    'co': {
        'name': 'CO (Computer Operation)',
        'icon': 'fa-cogs',
        'q_start': 41,
        'q_end': 51,
    },
}
SECTION_ORDER = ['common', 'apd', 'pc', 'co']

# ================================================================
# 기존 snowball_link2.py에서 공유 자원 import
# ================================================================
from snowball_link2_core import (
    s_questions, Q_ID, question_count,
    clear_skipped_answers,
)


# ================================================================
# 헬퍼 함수
# ================================================================
def is_logged_in():
    return 'user_id' in session


def get_user_info():
    if is_logged_in():
        if 'user_info' in session:
            return session['user_info']
        try:
            from auth import get_current_user
            return get_current_user()
        except ImportError:
            pass
    return None


def init_1p_session():
    """1page 인터뷰 세션 초기화 (미존재 시에만 실행)"""
    if 'link2_1p_answers' not in session:
        answers = [''] * question_count
        textarea = [''] * question_count
        textarea2 = [''] * question_count
        # 로그인 시 이메일 자동 입력
        user_info = get_user_info()
        if user_info and user_info.get('user_email'):
            answers[Q_ID['email']] = user_info['user_email']
        session['link2_1p_answers'] = answers
        session['link2_1p_textarea'] = textarea
        session['link2_1p_textarea2'] = textarea2
        session['link2_1p_section'] = 'common'
    elif 'link2_1p_textarea2' not in session:
        session['link2_1p_textarea2'] = [''] * question_count


def reset_1p_session():
    """1page 인터뷰 세션 완전 초기화"""
    for key in ['link2_1p_answers', 'link2_1p_textarea', 'link2_1p_textarea2', 'link2_1p_section']:
        session.pop(key, None)


# ================================================================
# 라우트 (통합 URL 적용)
# ================================================================
@bp_link2_1p.route('/itgc_interview', methods=['GET', 'POST'])
def link2_1p_start():
    """
    단일 URL(/itgc_interview)로 모든 섹션 처리.
    GET: session['link2_1p_section']에 저장된 섹션 표시.
    POST: 현재 섹션 답변 저장 후 다음 섹션으로 이동.
    """
    # 1. 초기 접속 처리 (리셋 요청 등)
    if request.method == 'GET' and request.args.get('reset') == '1':
        reset_1p_session()
        if is_logged_in():
            user_info = get_user_info()
            log_user_activity(
                user_info, 'FEATURE_START', 'Interview(섹션형) 리셋 및 시작',
                '/itgc_interview', request.remote_addr, request.headers.get('User-Agent')
            )
        return redirect(url_for('link2_1p.link2_1p_start'))

    init_1p_session()

    # 특정 색션으로 강제 이동 요청이 있는 경우 (주소창 파라미터로 명시할 때만 노출됨)
    requested_section = request.args.get('section')
    if requested_section in SECTIONS:
        session['link2_1p_section'] = requested_section
        return redirect(url_for('link2_1p.link2_1p_start'))

    # 현재 섹션 결정
    section_name = session.get('link2_1p_section', 'common')
    if section_name not in SECTIONS:
        section_name = 'common'
        session['link2_1p_section'] = 'common'

    # 2. POST 요청: 답변 저장 및 단계 이동
    if request.method == 'POST':
        answers = list(session.get('link2_1p_answers', [''] * question_count))
        textarea = list(session.get('link2_1p_textarea', [''] * question_count))
        textarea2 = list(session.get('link2_1p_textarea2', [''] * question_count))

        sec_info = SECTIONS[section_name]
        for idx in range(sec_info['q_start'], sec_info['q_end'] + 1):
            # 폼 필드명: q{idx} (메인), q{idx}_text (도구명/textarea), q{idx}_text2 (절차)
            answers[idx] = request.form.get(f'q{idx}', '')
            textarea[idx] = request.form.get(f'q{idx}_text', '')
            textarea2[idx] = request.form.get(f'q{idx}_text2', '')

        # 스킵 조건에 해당하는 답변 초기화
        clear_skipped_answers(answers, textarea)

        session['link2_1p_answers'] = answers
        session['link2_1p_textarea'] = textarea
        session['link2_1p_textarea2'] = textarea2

        # 진행 방향 결정 (prev_section이 명시된 경우 뒤로 가기)
        if request.form.get('action') == 'prev':
            cur_idx = SECTION_ORDER.index(section_name)
            if cur_idx > 0:
                prev_section = SECTION_ORDER[cur_idx - 1]
                session['link2_1p_section'] = prev_section
            return redirect(url_for('link2_1p.link2_1p_start'))

        # 다음 섹션으로 이동
        cur_idx = SECTION_ORDER.index(section_name)
        if cur_idx + 1 < len(SECTION_ORDER):
            next_section = SECTION_ORDER[cur_idx + 1]
            session['link2_1p_section'] = next_section
            return redirect(url_for('link2_1p.link2_1p_start'))
        else:
            # 마지막 섹션 완료 → 기존 세션 키에 복사 후 AI 검토 선택 페이지로
            session['answer'] = session['link2_1p_answers']
            session['textarea_answer'] = session['link2_1p_textarea']
            session['textarea2_answer'] = session['link2_1p_textarea2']
            return redirect(url_for('link2.ai_review_selection'))

    # 3. GET 요청: 렌더링
    answers = session.get('link2_1p_answers', [''] * question_count)
    textarea = session.get('link2_1p_textarea', [''] * question_count)
    textarea2 = session.get('link2_1p_textarea2', [''] * question_count)

    sec_info = SECTIONS[section_name]
    section_questions = s_questions[sec_info['q_start']:sec_info['q_end'] + 1]

    cur_idx = SECTION_ORDER.index(section_name)
    prev_section = SECTION_ORDER[cur_idx - 1] if cur_idx > 0 else None
    is_last = (cur_idx == len(SECTION_ORDER) - 1)

    return render_template(
        f'link2_{section_name}.jsp',
        section_name=section_name,
        section_info=sec_info,
        section_questions=section_questions,
        sections=SECTIONS,
        section_order=SECTION_ORDER,
        cur_section_idx=cur_idx,
        prev_section=prev_section,
        is_last=is_last,
        answers=answers,
        textarea_answers=textarea,
        textarea2_answers=textarea2,
        Q_ID=Q_ID,
        user_info=get_user_info(),
        is_logged_in=is_logged_in(),
        remote_addr=request.remote_addr,
    )


# 하위 호환성을 위한 기존 경로 리다이렉트
@bp_link2_1p.route('/link2_1p')
def old_link2_1p():
    return redirect(url_for('link2_1p.link2_1p_start'))

@bp_link2_1p.route('/link2_1p/section/<section_name>')
def old_section_view(section_name):
    # 명시적으로 섹션명이 포함된 경로로 오면 세션 업데이트 후 단일 URL로 보냄
    if section_name in SECTIONS:
        session['link2_1p_section'] = section_name
    return redirect(url_for('link2_1p.link2_1p_start'))
