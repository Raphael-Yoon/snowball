import os
import base64
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Gmail 인증 토큰 획득

def get_gmail_credentials():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# 텍스트 메일 전송

def send_gmail(to, subject, body):
    creds = get_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['Bcc'] = 'snowball1566@gmail.com'
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    send_message = service.users().messages().send(userId="me", body=message).execute()
    return send_message

# 첨부파일 포함 메일 전송

def send_gmail_with_attachment(to, subject, body, file_stream=None, file_path=None, file_name=None):
    creds = get_gmail_credentials()
    service = build('gmail', 'v1', credentials=creds)

    # 메일 생성
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message['Bcc'] = 'snowball2727@naver.com'
    message.attach(MIMEText(body, 'plain'))

    # 첨부파일 추가 (메모리 버퍼 우선, 없으면 파일 경로)
    part = MIMEBase('application', 'octet-stream')
    if file_stream is not None:
        file_stream.seek(0)
        part.set_payload(file_stream.read())
    elif file_path is not None:
        with open(file_path, 'rb') as f:
            part.set_payload(f.read())
    else:
        raise ValueError('첨부할 파일이 없습니다.')
    encoders.encode_base64(part)
    # 파일명 인코딩 처리 (한글 지원)
    import urllib.parse
    encoded_filename = urllib.parse.quote(file_name.encode('utf-8'))
    part.add_header('Content-Disposition', f'attachment; filename="{file_name}"; filename*=UTF-8\'\'{encoded_filename}')
    message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
    return send_message