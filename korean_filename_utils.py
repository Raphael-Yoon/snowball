#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse
from datetime import datetime

def convert_korean_to_english_filename(korean_name):
    """
    한글 시스템명을 안전한 파일명으로 변환합니다.
    
    Args:
        korean_name (str): 한글 시스템명
        
    Returns:
        str: 안전한 파일명
    """
    if not korean_name or not korean_name.strip():
        return "System"
    
    # 파일명에 사용할 수 없는 문자들을 안전한 문자로 변경
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', korean_name.strip())
    # 공백을 언더스코어로 변경
    safe_name = re.sub(r'\s+', '_', safe_name)
    # 연속된 언더스코어를 하나로 변경
    safe_name = re.sub(r'_+', '_', safe_name)
    # 파일명 길이 제한 (Windows 파일명 길이 제한 고려)
    if len(safe_name) > 30:
        safe_name = safe_name[:30]
    
    # 빈 문자열이 되지 않도록 보장
    if not safe_name or safe_name == '_':
        safe_name = 'System'
    
    return safe_name

def generate_excel_filename(system_name, prefix="ITGC"):
    """
    시스템명을 기반으로 엑셀 파일명을 생성합니다.
    
    Args:
        system_name (str): 시스템명
        prefix (str): 파일명 접두사
        
    Returns:
        str: 생성된 파일명
    """
    today = datetime.today().strftime('%Y%m%d')
    safe_name = convert_korean_to_english_filename(system_name)
    return f"{safe_name}_{prefix}_{today}.xlsx"

def create_mime_filename(filename):
    """
    MIME 헤더용 파일명을 생성합니다.
    
    Args:
        filename (str): 원본 파일명
        
    Returns:
        tuple: (safe_filename, disposition_header)
    """
    try:
        # 파일명이 None인 경우 기본값 설정
        if filename is None:
            filename = "ITGC_System.xlsx"
        
        # 파일명을 안전하게 처리 (한글 유지)
        safe_filename = convert_korean_to_english_filename(filename)
        
        # MIME 헤더 설정 - RFC 2047 형식으로 한글 파일명 지원
        from email.header import Header
        
        # 한글이 포함된 경우 RFC 2047 형식으로 인코딩
        if re.search(r'[가-힣]', safe_filename):
            encoded_filename = Header(safe_filename, 'utf-8').encode()
            disposition = f'attachment; filename={encoded_filename}'
        else:
            disposition = f'attachment; filename="{safe_filename}"'
        
        return safe_filename, disposition
        
    except Exception as e:
        # 인코딩 실패 시 안전한 파일명 사용
        print(f"파일명 인코딩 오류: {e}")
        safe_filename = "ITGC_System.xlsx"
        disposition = f'attachment; filename="{safe_filename}"'
        return safe_filename, disposition

def validate_filename(filename):
    """
    파일명이 유효한지 검증합니다.
    
    Args:
        filename (str): 검증할 파일명
        
    Returns:
        bool: 유효한 파일명인지 여부
    """
    if not filename or not filename.strip():
        return False
    
    # Windows에서 사용할 수 없는 문자들
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    if re.search(invalid_chars, filename):
        return False
    
    # 파일명 길이 검증 (Windows 파일명 길이 제한)
    if len(filename) > 255:
        return False
    
    return True

# 테스트 함수
def test_korean_filename_utils():
    """한글 파일명 유틸리티 테스트"""
    test_cases = [
        "인사관리시스템",
        "재무회계시스템",
        "구매관리시스템",
        "영업관리시스템",
        "ERP시스템",
        "SAP ERP",
        "오라클 ERP",
        "더존 ERP",
        "인사재무시스템",
        "시스템관리도구",
        "운영관리시스템",
        "개발관리시스템",
        "네이버 클라우드",
        "카카오 시스템",
        "구글 워크스페이스"
    ]
    
    print("=== 한글 파일명 유틸리티 테스트 ===")
    print()
    
    for test_name in test_cases:
        print(f"원본: {test_name}")
        
        # 변환 테스트
        safe_name = convert_korean_to_english_filename(test_name)
        print(f"변환: {safe_name}")
        
        # 파일명 생성 테스트
        excel_filename = generate_excel_filename(test_name)
        print(f"엑셀파일명: {excel_filename}")
        
        # 유효성 검증 테스트
        is_valid = validate_filename(safe_name)
        print(f"유효성: {'✓' if is_valid else '✗'}")
        
        # MIME 파일명 생성 테스트
        mime_filename, disposition = create_mime_filename(test_name)
        print(f"MIME파일명: {mime_filename}")
        print(f"Disposition: {disposition}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_korean_filename_utils()
