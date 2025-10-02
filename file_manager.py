"""
파일 업로드/다운로드 관리 모듈

평가 증빙 이미지, 모집단 엑셀 등 파일 관리 기능 제공
"""

import os
import time
from werkzeug.utils import secure_filename

# ===================================================================
# 파일 업로드 공통 함수
# ===================================================================

def save_evaluation_files(uploaded_images, excel_file, rcm_id, header_id, control_code, evaluation_type='design'):
    """
    평가 파일 저장 공통 함수
    
    Args:
        uploaded_images: 이미지 파일 리스트
        excel_file: 엑셀 파일 (모집단 데이터, None 가능)
        rcm_id: RCM ID
        header_id: 평가 헤더 ID
        control_code: 통제 코드
        evaluation_type: 'design' 또는 'operation'
    
    Returns:
        dict: {'images': [...], 'excel': None or {...}}
    """
    saved_files = {
        'images': [],
        'excel': None
    }
    
    # 이미지 파일 저장
    if uploaded_images:
        upload_dir = os.path.join('static', 'uploads', f'{evaluation_type}_evaluations', 
                                  str(rcm_id), str(header_id), control_code, 'images')
        os.makedirs(upload_dir, exist_ok=True)
        
        for i, image_file in enumerate(uploaded_images):
            if image_file and image_file.filename:
                # 확장자 분리
                original_name, original_ext = os.path.splitext(image_file.filename)
                
                # 안전한 파일명 생성
                safe_name = secure_filename(original_name)
                if not safe_name or safe_name.strip() == '' or safe_name == '_':
                    safe_name = 'evidence'
                
                # 타임스탬프 추가
                timestamp = str(int(time.time()))
                safe_filename = f"{safe_name}_{timestamp}_{i}{original_ext.lower()}"
                
                # 파일 저장
                file_path = os.path.join(upload_dir, safe_filename)
                image_file.save(file_path)
                
                # 상대 경로 저장
                relative_path = f"uploads/{evaluation_type}_evaluations/{rcm_id}/{header_id}/{control_code}/images/{safe_filename}"
                saved_files['images'].append({
                    'filename': safe_filename,
                    'original_name': image_file.filename,
                    'path': relative_path,
                    'url': f"/static/{relative_path}"
                })
    
    # 엑셀 파일 저장 (모집단 데이터)
    if excel_file and excel_file.filename:
        upload_dir = os.path.join('static', 'uploads', f'{evaluation_type}_evaluations', 
                                  str(rcm_id), str(header_id), control_code, 'excel')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 확장자 분리
        original_name, original_ext = os.path.splitext(excel_file.filename)
        
        # 안전한 파일명 생성
        safe_name = secure_filename(original_name)
        if not safe_name or safe_name.strip() == '' or safe_name == '_':
            safe_name = 'population_data'
        
        # 타임스탬프 추가
        timestamp = str(int(time.time()))
        safe_filename = f"{safe_name}_{timestamp}{original_ext.lower()}"
        
        # 파일 저장
        file_path = os.path.join(upload_dir, safe_filename)
        excel_file.save(file_path)
        
        # 상대 경로 저장
        relative_path = f"uploads/{evaluation_type}_evaluations/{rcm_id}/{header_id}/{control_code}/excel/{safe_filename}"
        saved_files['excel'] = {
            'filename': safe_filename,
            'original_name': excel_file.filename,
            'path': relative_path,
            'url': f"/static/{relative_path}"
        }
    
    return saved_files


def get_evaluation_files(rcm_id, header_id, control_code, evaluation_type='design'):
    """
    저장된 평가 파일 목록 조회
    
    Args:
        rcm_id: RCM ID
        header_id: 평가 헤더 ID
        control_code: 통제 코드
        evaluation_type: 'design' 또는 'operation'
    
    Returns:
        dict: {'images': [...], 'excel': None or {...}}
    """
    files = {
        'images': [],
        'excel': None
    }
    
    # 이미지 파일 조회
    image_dir = os.path.join('static', 'uploads', f'{evaluation_type}_evaluations', 
                             str(rcm_id), str(header_id), control_code, 'images')
    
    if os.path.exists(image_dir):
        for filename in sorted(os.listdir(image_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                relative_path = f"uploads/{evaluation_type}_evaluations/{rcm_id}/{header_id}/{control_code}/images/{filename}"
                files['images'].append({
                    'filename': filename,
                    'path': relative_path,
                    'url': f"/static/{relative_path}"
                })
    
    # 엑셀 파일 조회 (최신 파일 1개만)
    excel_dir = os.path.join('static', 'uploads', f'{evaluation_type}_evaluations', 
                             str(rcm_id), str(header_id), control_code, 'excel')
    
    if os.path.exists(excel_dir):
        excel_files = [f for f in os.listdir(excel_dir) 
                      if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
        if excel_files:
            # 최신 파일 선택
            latest_file = sorted(excel_files, reverse=True)[0]
            relative_path = f"uploads/{evaluation_type}_evaluations/{rcm_id}/{header_id}/{control_code}/excel/{latest_file}"
            files['excel'] = {
                'filename': latest_file,
                'path': relative_path,
                'url': f"/static/{relative_path}"
            }
    
    return files


def delete_evaluation_file(file_path):
    """
    평가 파일 삭제
    
    Args:
        file_path: 삭제할 파일의 상대 경로
    
    Returns:
        bool: 성공 여부
    """
    try:
        full_path = os.path.join('static', file_path.replace('uploads/', ''))
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        print(f"파일 삭제 실패: {e}")
        return False


def validate_image_file(file):
    """
    이미지 파일 검증
    
    Args:
        file: 업로드된 파일 객체
    
    Returns:
        tuple: (bool, str) - (유효성, 에러메시지)
    """
    if not file or not file.filename:
        return False, "파일이 선택되지 않았습니다."
    
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    _, ext = os.path.splitext(file.filename)
    
    if ext.lower() not in allowed_extensions:
        return False, f"지원하지 않는 이미지 형식입니다. ({', '.join(allowed_extensions)})"
    
    # 파일 크기 제한 (10MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        return False, "이미지 파일은 10MB 이하만 업로드 가능합니다."
    
    return True, ""


def validate_excel_file(file):
    """
    엑셀 파일 검증
    
    Args:
        file: 업로드된 파일 객체
    
    Returns:
        tuple: (bool, str) - (유효성, 에러메시지)
    """
    if not file or not file.filename:
        return False, "파일이 선택되지 않았습니다."
    
    allowed_extensions = {'.xlsx', '.xls', '.csv'}
    _, ext = os.path.splitext(file.filename)
    
    if ext.lower() not in allowed_extensions:
        return False, f"지원하지 않는 파일 형식입니다. ({', '.join(allowed_extensions)})"
    
    # 파일 크기 제한 (50MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 50 * 1024 * 1024:
        return False, "엑셀 파일은 50MB 이하만 업로드 가능합니다."
    
    return True, ""


# ===================================================================
# 표본 추출 관련 함수
# ===================================================================

def calculate_sample_size(population_count):
    """
    모집단 크기에 따른 표본 수 계산
    
    Args:
        population_count: 모집단 개수
    
    Returns:
        int: 표본 수
    
    Examples:
        >>> calculate_sample_size(0)
        0
        >>> calculate_sample_size(1)
        1
        >>> calculate_sample_size(3)
        2
        >>> calculate_sample_size(10)
        2
        >>> calculate_sample_size(30)
        5
        >>> calculate_sample_size(100)
        20
        >>> calculate_sample_size(300)
        25
    """
    if population_count == 0:
        return 0
    elif population_count == 1:
        return 1
    elif 2 <= population_count <= 4:
        return 2
    elif 5 <= population_count <= 12:
        return 2
    elif 13 <= population_count <= 52:
        return 5
    elif 53 <= population_count <= 250:
        return 20
    else:  # > 250
        return 25


def select_random_samples(population_list, sample_size):
    """
    모집단에서 무작위 표본 선택
    
    Args:
        population_list: 모집단 리스트
        sample_size: 선택할 표본 수
    
    Returns:
        list: 선택된 표본 리스트 (인덱스 포함)
    """
    import random
    
    if not population_list or sample_size <= 0:
        return []
    
    population_count = len(population_list)
    actual_sample_size = min(sample_size, population_count)
    
    # 랜덤 인덱스 선택
    selected_indices = random.sample(range(population_count), actual_sample_size)
    
    # 인덱스와 함께 반환
    samples = []
    for idx in sorted(selected_indices):
        samples.append({
            'index': idx,
            'data': population_list[idx]
        })
    
    return samples


# ===================================================================
# 엑셀 파싱 관련 함수 (표준통제 테스트용)
# ===================================================================

def parse_population_excel(file_path, field_mapping):
    """
    모집단 엑셀 파일 파싱
    
    Args:
        file_path: 엑셀 파일 경로
        field_mapping: 필드 매핑 정보
            {
                'user_id': 'A',  # 또는 컬럼명 '사용자ID'
                'user_name': 'B',
                'department': 'C',
                'permission': 'D',
                'grant_date': 'E'
            }
    
    Returns:
        list: 파싱된 데이터 리스트
        [
            {
                'user_id': 'U001',
                'user_name': '홍길동',
                'department': '재무팀',
                'permission': '관리자',
                'grant_date': '2024-01-15'
            },
            ...
        ]
    """
    from openpyxl import load_workbook
    from datetime import datetime
    
    try:
        workbook = load_workbook(file_path, data_only=True)
        sheet = workbook.active
        
        population_data = []
        
        # 첫 번째 행은 헤더로 가정, 2번째 행부터 읽기
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):  # 빈 행 스킵
                continue
            
            # 필드 매핑에 따라 데이터 추출
            record = {}
            for field_name, column_ref in field_mapping.items():
                # 컬럼 참조가 문자(A, B, C)인 경우
                if isinstance(column_ref, str) and len(column_ref) == 1 and column_ref.isalpha():
                    col_idx = ord(column_ref.upper()) - ord('A')
                    value = row[col_idx] if col_idx < len(row) else None
                # 컬럼 인덱스(0, 1, 2)인 경우
                elif isinstance(column_ref, int):
                    value = row[column_ref] if column_ref < len(row) else None
                else:
                    value = None
                
                # 날짜 타입 처리
                if value and isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d')
                
                record[field_name] = value if value is not None else ''
            
            population_data.append(record)
        
        workbook.close()
        return population_data
        
    except Exception as e:
        raise Exception(f"엑셀 파일 파싱 오류: {str(e)}")


def parse_apd01_population(file_path, field_mapping):
    """
    APD01 모집단 엑셀 파싱 (사용자 권한 부여)
    
    Args:
        file_path: 엑셀 파일 경로
        field_mapping: {
            'user_id': 컬럼_참조,
            'user_name': 컬럼_참조,
            'department': 컬럼_참조,
            'permission': 컬럼_참조,
            'grant_date': 컬럼_참조
        }
    
    Returns:
        dict: {
            'population': [...],  # 모집단 데이터
            'count': 100,  # 모집단 수
            'sample_size': 20  # 계산된 표본 수
        }
    """
    population = parse_population_excel(file_path, field_mapping)
    count = len(population)
    sample_size = calculate_sample_size(count)
    
    return {
        'population': population,
        'count': count,
        'sample_size': sample_size
    }
