from flask import render_template, request, send_file
from datetime import datetime
import os
from openpyxl import load_workbook
from io import BytesIO
import snowball_db
from .snowball_mail import send_gmail_with_attachment

# 질문 리스트는 snowball_constants.py로 이동

def handle_interview():
    if request.method == 'GET':
        if request.args.get('reset') == '1':
            session.clear()
            if 1 <= START_QUESTION <= question_count:
                session['question_index'] = START_QUESTION - 1
            else:
                session['question_index'] = 0
            session['answer'] = [''] * question_count
            session['textarea_answer'] = [''] * question_count
        elif 'question_index' not in session:
            session['question_index'] = 0
            session['answer'] = [''] * question_count
            session['textarea_answer'] = [''] * question_count

        users = snowball_db.get_user_list()
        return render_template('link2.jsp', 
                            question=s_questions[session['question_index']], 
                            question_count=question_count, 
                            current_index=session['question_index'],
                            remote_addr=request.remote_addr,
                            users=users,
                            answer=session['answer'],
                            textarea_answer=session['textarea_answer'])

    question_index = session['question_index']

    if request.method == 'POST':
        form_data = request.form
        session['answer'][question_index] = form_data.get(f"a{question_index}", '')
        session['textarea_answer'][question_index] = form_data.get(f"a{question_index}_1", '')
        
        # Session data handling...
        
        next_question = {i: i + 1 for i in range(43)}
        conditional_routes = {
            4: 5 if session['answer'][question_index] == 'Y' else 7,
            3: 4 if session['answer'][question_index] == 'Y' else 6
        }
        next_question.update(conditional_routes)

        if question_index == question_count - 1:
            return save_to_excel()

        session['question_index'] = next_question.get(question_index, question_index)

        if session['question_index'] >= question_count:
            return redirect(url_for('index'))

    question = s_questions[session['question_index']]
    return render_template(
        'link2.jsp',
        question=question,
        question_count=question_count,
        current_index=session['question_index'],
        remote_addr=request.remote_addr,
        users=snowball_db.get_user_list(),
        answer=session['answer'],
        textarea_answer=session['textarea_answer']
    )

def handle_interview_prev():
    question_index = session.get('question_index', 0)
    if question_index > 0:
        session['question_index'] = question_index - 1
    return redirect(url_for('link2'))

def save_to_excel():
    # Excel 저장 관련 로직...
    pass
