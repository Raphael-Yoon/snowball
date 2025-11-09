import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from datetime import datetime
import subprocess
import sys
# argparse import 및 관련 코드 제거

# 필요한 권한 범위 설정
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Gmail API 서비스 객체 생성"""
    creds = None
    
    # 토큰이 이미 있으면 사용
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # 다운로드한 credentials.json 파일
            creds = flow.run_local_server(port=8080)
        
        # 나중에 사용하기 위해 토큰 저장
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to, subject, body):
    """이메일 보내기"""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    
    # base64로 인코딩하여 Gmail API 형식에 맞춤
    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')
    
    try:
        sent_message = service.users().messages().send(
            userId='me', 
            body={'raw': raw_message}
        ).execute()
        print(f'메시지 ID: {sent_message["id"]}')
        return sent_message
    except Exception as e:
        print(f'에러 발생: {e}')
        return None

def send_gmail_with_today(service, to, subject):
    """오늘 날짜와 시간이 본문에 포함된 이메일 보내기"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    body = f'현재 일시: {now} 입니다.'
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')
    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        print(f'메시지 ID: {sent_message["id"]}')
        return sent_message
    except Exception as e:
        print(f'에러 발생: {e}')
        return None

def run_mysql_sync():
    """sync_mysql_to_sqlite.py 스크립트 실행 및 결과 반환"""
    script_path = os.path.join(os.path.dirname(__file__), 'sync_mysql_to_sqlite.py')

    try:
        # Python 인터프리터 경로 가져오기
        python_executable = sys.executable

        # subprocess로 스크립트 실행
        result = subprocess.run(
            [python_executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5분 타임아웃
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': '스크립트 실행 시간 초과 (5분)',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'스크립트 실행 중 에러: {str(e)}',
            'returncode': -1
        }

def send_sync_result_email(service, to, subject, sync_result):
    """MySQL 동기화 결과를 포함한 이메일 보내기"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 이메일 본문 구성
    body_lines = [
        f'MySQL to SQLite 동기화 실행 결과',
        f'실행 일시: {now}',
        f'',
        f'=' * 60,
        f'상태: {"성공" if sync_result["success"] else "실패"}',
        f'반환 코드: {sync_result["returncode"]}',
        f'=' * 60,
        f'',
    ]

    # 표준 출력 추가
    if sync_result['stdout']:
        body_lines.append('[ 실행 로그 ]')
        body_lines.append(sync_result['stdout'])
        body_lines.append('')

    # 에러 출력 추가
    if sync_result['stderr']:
        body_lines.append('[ 에러 로그 ]')
        body_lines.append(sync_result['stderr'])
        body_lines.append('')

    body = '\n'.join(body_lines)

    # 이메일 전송
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')

    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        print(f'메시지 ID: {sent_message["id"]}')
        return sent_message
    except Exception as e:
        print(f'에러 발생: {e}')
        return None

# 사용 예시
if __name__ == '__main__':
    # 받는 사람과 제목 설정
    to = 'snowball1566@gmail.com'
    subject = 'MySQL to SQLite 동기화 결과'

    print('Gmail 서비스 인증 중...')
    service = get_gmail_service()

    print('MySQL to SQLite 동기화 실행 중...')
    sync_result = run_mysql_sync()

    print('\n동기화 완료. 결과 메일 전송 중...')
    result = send_sync_result_email(
        service=service,
        to=to,
        subject=subject,
        sync_result=sync_result
    )

    if result:
        print('메일이 성공적으로 전송되었습니다.')
        print(f'동기화 상태: {"성공" if sync_result["success"] else "실패"}')
    else:
        print('메일 전송에 실패했습니다.')