"""RCM 유틸리티 테스트"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from io import BytesIO
from rcm_utils import (
    normalize_column_name,
    map_columns,
    parse_excel_file,
    validate_rcm_data,
    get_mapping_summary
)


def test_normalize_column_name():
    """컬럼명 정규화 테스트"""
    print("=== 컬럼명 정규화 테스트 ===")

    test_cases = [
        ("Control Code", "control code"),
        ("통제코드", "통제코드"),
        ("Control_Code", "control_code"),
        ("  Control   Code  ", "control code"),
        ("Control-Code!", "controlcode"),
    ]

    for original, expected in test_cases:
        result = normalize_column_name(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{original}' → '{result}' (expected: '{expected}')")


def test_map_columns():
    """컬럼 매핑 테스트"""
    print("\n=== 컬럼 매핑 테스트 ===")

    # 테스트 데이터프레임 생성 (다양한 컬럼명)
    test_data = {
        '통제코드': ['ITGC-001', 'ITGC-002'],
        '통제 이름': ['접근통제', '변경관리'],
        'Control Description': ['사용자 접근 권한 관리', '시스템 변경 승인'],
        'KEY CONTROL': ['Y', 'N'],
        '통제빈도': ['매일', '매월'],
        'Unknown Column': ['test1', 'test2']  # 매핑되지 않을 컬럼
    }

    df = pd.DataFrame(test_data)
    print(f"원본 컬럼: {list(df.columns)}")

    df_mapped, mapping_info = map_columns(df)
    print(f"매핑된 컬럼: {list(df_mapped.columns)}")
    print(f"매핑 정보: {mapping_info}")

    # 표준 컬럼이 제대로 매핑되었는지 확인
    assert 'control_code' in df_mapped.columns
    assert 'control_name' in df_mapped.columns
    assert 'control_description' in df_mapped.columns
    assert 'key_control' in df_mapped.columns
    assert 'control_frequency' in df_mapped.columns

    print("✓ 컬럼 매핑 성공")


def test_parse_excel_file_basic():
    """기본 엑셀 파일 파싱 테스트 (header_row=0)"""
    print("\n=== 기본 엑셀 파싱 테스트 (header_row=0) ===")

    # 테스트용 엑셀 파일 생성
    test_data = {
        '통제코드': ['ITGC-001', 'ITGC-002', 'ITGC-003'],
        '통제명': ['접근통제', '변경관리', '백업관리'],
        '통제설명': ['사용자 접근 권한 관리', '시스템 변경 승인', '데이터 백업 절차'],
        '핵심통제': ['Y', 'N', 'Y'],
        '통제빈도': ['매일', '매월', '매주']
    }

    df = pd.DataFrame(test_data)

    # BytesIO로 메모리에서 엑셀 파일 생성
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    # 파싱
    rcm_data, mapping_info = parse_excel_file(excel_buffer, header_row=0)

    print(f"파싱된 레코드 수: {len(rcm_data)}")
    print(f"매핑 정보: {mapping_info}")
    print(f"첫 번째 레코드: {rcm_data[0]}")

    assert len(rcm_data) == 3
    assert rcm_data[0].get('control_code') == 'ITGC-001'
    assert rcm_data[0].get('control_name') == '접근통제'

    print("✓ 기본 파싱 성공")


def test_parse_excel_file_multiline_header():
    """멀티라인 헤더 엑셀 파일 파싱 테스트 (header_row=2)"""
    print("\n=== 멀티라인 헤더 파싱 테스트 (header_row=2) ===")

    # 멀티라인 헤더가 있는 엑셀 파일 생성
    # 첫 2줄은 설명, 3번째 줄(index 2)이 실제 헤더
    test_data = {
        'A': ['통제 관리 대장', 'Control Management', '통제코드', 'ITGC-001', 'ITGC-002'],
        'B': ['2024년', 'Year 2024', '통제명', '접근통제', '변경관리'],
        'C': ['설명', 'Description', '통제설명', '접근 권한 관리', '변경 승인 절차'],
    }

    df = pd.DataFrame(test_data)

    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, header=False, engine='openpyxl')
    excel_buffer.seek(0)

    # header_row=2로 파싱 (3번째 행이 헤더)
    rcm_data, mapping_info = parse_excel_file(excel_buffer, header_row=2)

    print(f"파싱된 레코드 수: {len(rcm_data)}")
    print(f"매핑 정보: {mapping_info}")
    if rcm_data:
        print(f"첫 번째 레코드: {rcm_data[0]}")

    assert len(rcm_data) == 2
    assert rcm_data[0].get('control_code') == 'ITGC-001'
    assert rcm_data[0].get('control_name') == '접근통제'

    print("✓ 멀티라인 헤더 파싱 성공")


def test_validate_rcm_data():
    """RCM 데이터 유효성 검증 테스트"""
    print("\n=== 데이터 유효성 검증 테스트 ===")

    # 유효한 데이터
    valid_data = [
        {'control_code': 'ITGC-001', 'control_name': '접근통제'},
        {'control_code': 'ITGC-002', 'control_name': '변경관리'},
    ]

    is_valid, message = validate_rcm_data(valid_data)
    assert is_valid
    print(f"✓ 유효한 데이터 검증 성공: {message or '(메시지 없음)'}")

    # 빈 데이터
    empty_data = []
    is_valid, message = validate_rcm_data(empty_data)
    assert not is_valid
    print(f"✓ 빈 데이터 검증 실패 (예상대로): {message}")

    # control_code와 control_name이 모두 없는 데이터
    invalid_data = [
        {'description': '설명만 있음'},
        {'key_control': 'Y'},
    ]
    is_valid, message = validate_rcm_data(invalid_data)
    assert not is_valid
    print(f"✓ 무효한 데이터 검증 실패 (예상대로): {message}")


def test_get_mapping_summary():
    """매핑 요약 테스트"""
    print("\n=== 매핑 요약 테스트 ===")

    mapping_info = {
        '통제코드': 'control_code',
        '통제명': 'control_name',
        'Control Description': 'control_description'
    }

    summary = get_mapping_summary(mapping_info)
    print(f"매핑 요약: {summary}")

    assert '통제코드' in summary
    assert 'control_code' in summary

    print("✓ 매핑 요약 생성 성공")


def test_english_columns():
    """영문 컬럼명 테스트"""
    print("\n=== 영문 컬럼명 테스트 ===")

    test_data = {
        'Control Code': ['ITGC-001', 'ITGC-002'],
        'Control Name': ['Access Control', 'Change Management'],
        'Description': ['User access rights', 'System change approval'],
        'Key Control': ['Y', 'N'],
        'Frequency': ['Daily', 'Monthly']
    }

    df = pd.DataFrame(test_data)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    rcm_data, mapping_info = parse_excel_file(excel_buffer, header_row=0)

    print(f"파싱된 레코드 수: {len(rcm_data)}")
    print(f"매핑 정보: {mapping_info}")
    print(f"첫 번째 레코드: {rcm_data[0]}")

    assert len(rcm_data) == 2
    assert rcm_data[0].get('control_code') == 'ITGC-001'
    assert rcm_data[0].get('control_name') == 'Access Control'

    print("✓ 영문 컬럼명 파싱 성공")


if __name__ == '__main__':
    print("RCM 유틸리티 테스트 시작\n")

    try:
        test_normalize_column_name()
        test_map_columns()
        test_parse_excel_file_basic()
        test_parse_excel_file_multiline_header()
        test_validate_rcm_data()
        test_get_mapping_summary()
        test_english_columns()

        print("\n" + "="*50)
        print("✓ 모든 테스트 통과!")
        print("="*50)

    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
