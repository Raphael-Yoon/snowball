import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from datetime import datetime
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

# 사용 예시
if __name__ == '__main__':
    # 받는 사람과 제목을 하드코딩
    to = 'snowball1566@gmail.com,daiyeolyoon@naver.com'
    subject = '계정 활성화 여부'

    service = get_gmail_service()
    result = send_gmail_with_today(
        service=service,
        to=to,
        subject=subject
    )
    if result:
        print('메일이 성공적으로 전송되었습니다.')
    else:
        print('메일 전송에 실패했습니다.')