# -*- coding: utf-8 -*-
import sys
import os
import json
import io
from datetime import datetime
from flask import Blueprint, render_template, jsonify, send_file, request, session

# Windows 콘솔 UTF-8 설정
if os.name == 'nt':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

bp_link10 = Blueprint('link10', __name__)

# 결과 파일 저장 디렉토리 (사용 안함 - 데이터베이스 저장)
# RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
# if not os.path.exists(RESULTS_DIR):
#     os.makedirs(RESULTS_DIR, exist_ok=True)

# ============================================================================
# Google Drive Integration Functions
# ============================================================================

def get_drive_service():
    """구글 드라이브 서비스 객체 생성 (읽기 전용)"""
    try:
        import pickle
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        # 읽기 전용 권한
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        creds = None

        # snowball 프로젝트의 token_link10.pickle 사용 (Gmail 토큰과 분리)
        snowball_dir = os.path.dirname(__file__)
        token_path = os.path.join(snowball_dir, 'token_link10.pickle')
        credentials_path = os.path.join(snowball_dir, 'credentials.json')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(f"credentials.json을 찾을 수 없습니다: {credentials_path}")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"구글 드라이브 인증 오류: {e}")
        return None

def get_or_create_folder(service, folder_name):
    """구글 드라이브에서 특정 이름의 폴더를 찾거나 생성"""
    try:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if items:
            return items[0]['id']
        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')
    except Exception as e:
        print(f"폴더 조회/생성 오류: {e}")
        return None

def list_drive_files(folder_name="Stock_Analysis_Results"):
    """구글 드라이브 특정 폴더의 파일 목록 가져오기"""
    try:
        service = get_drive_service()
        if not service:
            return []

        folder_id = get_or_create_folder(service, folder_name)
        if not folder_id:
            return []

        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, createdTime, webViewLink, size)",
            orderBy="createdTime desc"
        ).execute()

        return results.get('files', [])
    except Exception as e:
        print(f"구글 드라이브 목록 조회 오류: {e}")
        return []

def download_from_drive(file_id):
    """구글 드라이브에서 파일을 엑셀 형식으로 다운로드"""
    try:
        service = get_drive_service()
        if not service:
            return None

        # 구글 시트를 엑셀로 내보내기
        request = service.files().export_media(
            fileId=file_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        return request.execute()
    except Exception as e:
        print(f"구글 드라이브 다운로드 오류: {e}")
        return None

def get_google_doc_content(doc_id):
    """구글 문서의 텍스트 내용 가져오기"""
    try:
        from googleapiclient.discovery import build
        service = get_drive_service()
        if not service:
            return None

        # 구글 문서를 텍스트로 내보내기
        request = service.files().export_media(
            fileId=doc_id,
            mimeType='text/plain'
        )
        content = request.execute()
        return content.decode('utf-8')
    except Exception as e:
        print(f"구글 문서 조회 오류: {e}")
        return None

# ============================================================================
# Flask Helper Functions
# ============================================================================

def is_logged_in():
    """로그인 상태 확인"""
    return 'user_id' in session

def get_user_info():
    """현재 로그인한 사용자 정보 반환 (세션 우선)"""
    if is_logged_in():
        if 'user_info' in session:
            return session['user_info']
        try:
            from auth import get_current_user
            return get_current_user()
        except ImportError:
            pass
    return None

@bp_link10.route('/link10')
def index():
    """메인 페이지"""
    user_logged_in = is_logged_in()
    user_info = get_user_info()
    return render_template('link10.jsp',
                         is_logged_in=user_logged_in,
                         user_info=user_info)

@bp_link10.route('/link10/api/results', methods=['GET'])
def list_results():
    """구글 드라이브의 결과 파일 목록 조회"""
    try:
        drive_files = list_drive_files()

        # 스프레드시트와 문서를 매핑
        spreadsheets = {}  # {name: file_info}
        documents = {}     # {name: file_info}

        for file in drive_files:
            if file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                spreadsheets[file['name']] = file
            elif file['mimeType'] == 'application/vnd.google-apps.document':
                documents[file['name']] = file

        # 결과 리스트 생성
        results = []
        for name, sheet_file in spreadsheets.items():
            # 해당 스프레드시트에 대응하는 AI 리포트 찾기
            # 형식: "AI 분석 리포트 - kospi_top100_20251228_162053"
            doc_name = f"AI 분석 리포트 - {name}"
            has_ai = doc_name in documents
            doc_id = documents[doc_name]['id'] if has_ai else None

            results.append({
                'filename': f"{name}.xlsx",  # UI 표시용
                'spreadsheet_id': sheet_file['id'],
                'doc_id': doc_id,
                'size': int(sheet_file.get('size', 0)) if sheet_file.get('size') else 0,
                'created_at': sheet_file.get('createdTime'),
                'drive_link': sheet_file.get('webViewLink'),
                'has_ai': has_ai
            })

        # 최신순 정렬
        results.sort(key=lambda x: x['created_at'] if x['created_at'] else '', reverse=True)
        return jsonify(results)

    except Exception as e:
        print(f"결과 목록 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@bp_link10.route('/link10/api/ai_result/<filename>', methods=['GET'])
def get_ai_result(filename):
    """구글 문서에서 AI 분석 결과 조회"""
    try:
        # filename에서 .xlsx 제거하여 스프레드시트 이름 추출
        sheet_name = filename.replace('.xlsx', '')

        # 구글 드라이브에서 파일 목록 가져오기
        drive_files = list_drive_files()

        # AI 분석 리포트 문서 찾기
        doc_name = f"AI 분석 리포트 - {sheet_name}"
        doc_id = None
        doc_link = None

        for file in drive_files:
            if file['name'] == doc_name and file['mimeType'] == 'application/vnd.google-apps.document':
                doc_id = file['id']
                doc_link = file.get('webViewLink')
                break

        if not doc_id:
            return jsonify({'success': False, 'message': 'AI 분석 리포트를 찾을 수 없습니다.'}), 404

        # 구글 문서 내용 가져오기
        content = get_google_doc_content(doc_id)

        if content:
            return jsonify({
                'success': True,
                'result': content,
                'drive_link': doc_link
            })
        else:
            return jsonify({'success': False, 'message': '문서 내용을 불러올 수 없습니다.'}), 500

    except Exception as e:
        print(f"AI 결과 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'오류 발생: {str(e)}'}), 500

@bp_link10.route('/link10/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """구글 드라이브에서 파일 다운로드"""
    try:
        # filename에서 .xlsx 제거하여 스프레드시트 이름 추출
        sheet_name = filename.replace('.xlsx', '')

        # 구글 드라이브에서 파일 목록 가져오기
        drive_files = list_drive_files()

        # 스프레드시트 찾기
        spreadsheet_id = None
        for file in drive_files:
            if file['name'] == sheet_name and file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                spreadsheet_id = file['id']
                break

        if not spreadsheet_id:
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

        # 구글 시트를 엑셀로 다운로드
        file_content = download_from_drive(spreadsheet_id)

        if file_content:
            return send_file(
                io.BytesIO(file_content),
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({'error': '파일 다운로드에 실패했습니다.'}), 500

    except Exception as e:
        print(f"파일 다운로드 오류: {e}")
        return jsonify({'error': f'다운로드 중 오류: {str(e)}'}), 500

@bp_link10.route('/link10/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """삭제 기능 비활성화 (읽기 전용 모드)"""
    return jsonify({
        'success': False,
        'message': 'Link10은 읽기 전용 모드입니다. 파일 삭제는 Trade 프로젝트에서 수행해주세요.'
    }), 403
