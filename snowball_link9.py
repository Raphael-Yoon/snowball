from flask import Blueprint, request, render_template, redirect, url_for, session
from snowball_mail import send_gmail

bp_link9 = Blueprint('link9', __name__)

def is_logged_in():
    """로그인 상태 확인"""
    return 'user_id' in session

def get_user_info():
    """현재 로그인한 사용자 정보 반환 (세션 우선)"""
    from snowball import is_logged_in
    if is_logged_in():
        # 세션에 저장된 user_info를 우선 사용
        if 'user_info' in session:
            return session['user_info']
        # 없으면 데이터베이스에서 조회
        from auth import get_current_user
        db_user_info = get_current_user()
        return db_user_info
    return None

# Contact Us 관련 기능들

@bp_link9.route('/link9', methods=['GET', 'POST'])
def link9():
    """서비스 문의 페이지 (Contact Us)"""
    user_logged_in = is_logged_in()
    user_info = get_user_info()

    if request.method == 'POST':
        name = request.form.get('name')
        company_name = request.form.get('company_name')
        email = request.form.get('email')
        message = request.form.get('message')

        subject = f'Contact Us 문의: {name}'
        body = f'이름: {name}\n회사명: {company_name}\n이메일: {email}\n문의내용:\n{message}'
        try:
            send_gmail(
                to='snowball1566@gmail.com',
                subject=subject,
                body=body
            )
            return render_template('link9.jsp', success=True, remote_addr=request.remote_addr,
                                 is_logged_in=user_logged_in, user_info=user_info)
        except Exception as e:
            return render_template('link9.jsp', success=False, error=str(e), remote_addr=request.remote_addr,
                                 is_logged_in=user_logged_in, user_info=user_info)
    return render_template('link9.jsp', remote_addr=request.remote_addr,
                         is_logged_in=user_logged_in, user_info=user_info)

@bp_link9.route('/service_inquiry', methods=['POST'])
def service_inquiry():
    """서비스 문의 처리"""
    try:
        company_name = request.form.get('company_name')
        contact_name = request.form.get('contact_name')
        contact_email = request.form.get('contact_email')
        
        
        subject = f'SnowBall 서비스 가입 문의: {company_name}'
        body = f'''SnowBall 서비스 가입 문의가 접수되었습니다.

회사명: {company_name}
담당자명: {contact_name}
이메일: {contact_email}

내부통제 평가 및 ITGC 관련 서비스에 관심을 보여주셔서 감사합니다.
빠른 시일 내에 담당자가 연락드리겠습니다.'''
        
        send_gmail(
            to=f'{contact_email}, snowball1566@gmail.com',
            subject=subject,
            body=body
        )
        
        # 성공 메시지를 포함하여 로그인 페이지로 리다이렉트
        return render_template('login.jsp', 
                             service_inquiry_success=True,
                             remote_addr=request.remote_addr)
    except Exception as e:
        return render_template('login.jsp', 
                             service_inquiry_error=str(e),
                             remote_addr=request.remote_addr)

@bp_link9.route('/api/contact/send', methods=['POST'])
def send_contact_message():
    """Contact 메시지 전송 API"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject', '일반 문의')
        message = data.get('message')
        
        if not all([name, email, message]):
            return {
                'success': False,
                'message': '필수 정보가 누락되었습니다.'
            }, 400
        
        # 이메일 전송
        email_subject = f'[SnowBall] {subject} - {name}'
        email_body = f'''SnowBall 웹사이트를 통해 문의가 접수되었습니다.

■ 문의자 정보
이름: {name}
이메일: {email}
문의 유형: {subject}

■ 문의 내용
{message}

■ 기타 정보
접수 시간: {request.remote_addr}
IP 주소: {request.remote_addr}
User-Agent: {request.headers.get('User-Agent', 'Unknown')}
'''
        
        send_gmail(
            to='snowball1566@gmail.com',
            subject=email_subject,
            body=email_body
        )
        
        # 자동 응답 메일 (문의자에게)
        auto_reply_subject = '[SnowBall] 문의 접수 완료'
        auto_reply_body = f'''안녕하세요, {name}님.

SnowBall 서비스에 문의해 주셔서 감사합니다.
고객님의 문의가 정상적으로 접수되었습니다.

■ 접수된 문의 내용
문의 유형: {subject}
접수 내용: {message[:100]}{'...' if len(message) > 100 else ''}

담당자 검토 후 빠른 시일 내에 회신드리겠습니다.
일반적으로 1-2일 이내에 답변드리고 있습니다.

문의해 주셔서 다시 한 번 감사합니다.

SnowBall Team
snowball1566@gmail.com
'''
        
        send_gmail(
            to=email,
            subject=auto_reply_subject,
            body=auto_reply_body
        )
        
        return {
            'success': True,
            'message': '문의가 성공적으로 전송되었습니다. 빠른 시일 내에 답변드리겠습니다.'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': '메시지 전송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }, 500

@bp_link9.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """사용자 피드백 전송 API"""
    try:
        data = request.get_json()
        feedback_type = data.get('type', '일반 피드백')
        content = data.get('content')
        rating = data.get('rating')
        user_email = data.get('email', '익명')
        
        if not content:
            return {
                'success': False,
                'message': '피드백 내용을 입력해주세요.'
            }, 400
        
        # 피드백 이메일 전송
        email_subject = f'[SnowBall 피드백] {feedback_type}'
        email_body = f'''SnowBall 서비스에 대한 피드백이 접수되었습니다.

■ 피드백 정보
유형: {feedback_type}
평점: {rating}/5 {'★' * int(rating) if rating else 'N/A'}
이메일: {user_email}

■ 피드백 내용
{content}

■ 기술 정보
접수 시간: {request.remote_addr}
IP 주소: {request.remote_addr}
User-Agent: {request.headers.get('User-Agent', 'Unknown')}
'''
        
        send_gmail(
            to='snowball1566@gmail.com',
            subject=email_subject,
            body=email_body
        )
        
        return {
            'success': True,
            'message': '소중한 피드백 감사합니다. 서비스 개선에 적극 반영하겠습니다.'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': '피드백 전송 중 오류가 발생했습니다.'
        }, 500