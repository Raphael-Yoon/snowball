"""RCM 업로드 및 파싱 유틸리티"""
import pandas as pd
import re


# 컬럼명 매핑 딕셔너리 (다양한 컬럼명 변형 지원)
COLUMN_MAPPING = {
    'control_code': [
        'control_code', 'controlcode', 'control code',
        '통제코드', '코드', '통제 코드', 'code',
        'ctrl_code', 'ctrl code'
    ],
    'control_name': [
        'control_name', 'controlname', 'control name',
        '통제명', '통제이름', '통제 이름', '통제 명',
        'name', 'ctrl_name', 'ctrl name'
    ],
    'control_description': [
        'control_description', 'controldescription', 'control description',
        '통제설명', '설명', '통제 설명', 'description', 'desc',
        '통제내용', '통제 내용', 'control_detail', 'detail'
    ],
    'key_control': [
        'key_control', 'keycontrol', 'key control',
        '핵심통제', '핵심 통제', 'key', 'key_ctrl',
        '중요통제', '주요통제'
    ],
    'control_frequency': [
        'control_frequency', 'controlfrequency', 'control frequency',
        '통제빈도', '빈도', '통제 빈도', 'frequency', 'freq',
        '수행빈도', '실행빈도'
    ],
    'control_type': [
        'control_type', 'controltype', 'control type',
        '통제유형', '유형', '통제 유형', 'type',
        '통제타입', '통제 타입'
    ],
    'control_nature': [
        'control_nature', 'controlnature', 'control nature',
        '통제속성', '속성', '통제 속성', 'nature',
        '통제성격', '통제 성격'
    ],
    'population': [
        'population', 'pop',
        '모집단', '대상', '모집 단',
        '통제대상', '통제 대상'
    ],
    'population_completeness_check': [
        'population_completeness_check', 'populationcompletenesscheck',
        'population completeness check', 'completeness_check', 'completeness',
        '모집단완전성', '완전성확인', '완전성 확인', '모집단 완전성',
        '완전성검증', '완전성 검증'
    ],
    'population_count': [
        'population_count', 'populationcount', 'population count',
        '모집단건수', '건수', '모집단 건수', 'count',
        '대상건수', '대상 건수', '표본수'
    ],
    'test_procedure': [
        'test_procedure', 'testprocedure', 'test procedure',
        '검증절차', '절차', '검증 절차', 'procedure', 'test',
        '테스트절차', '테스트 절차', '검사절차', '검사 절차'
    ],
    'control_category': [
        'control_category', 'controlcategory', 'control category',
        '통제카테고리', '카테고리', '통제 카테고리', 'category',
        '분류', '구분'
    ]
}


def normalize_column_name(col_name):
    """컬럼명 정규화 (공백, 대소문자, 특수문자 처리)"""
    if pd.isna(col_name):
        return ''

    # 문자열로 변환
    col_name = str(col_name).strip()

    # 소문자 변환
    col_name = col_name.lower()

    # 여러 공백을 하나로
    col_name = re.sub(r'\s+', ' ', col_name)

    # 특수문자 제거 (한글, 영문, 숫자, 공백, 언더스코어만 남김)
    col_name = re.sub(r'[^\w\s가-힣]', '', col_name)

    return col_name


def map_columns(df):
    """데이터프레임의 컬럼명을 표준 컬럼명으로 매핑"""
    # 컬럼명 정규화
    normalized_columns = {col: normalize_column_name(col) for col in df.columns}

    # 매핑 결과 저장
    column_mapping_result = {}

    # 각 표준 컬럼에 대해 매핑 시도
    for target_col, possible_names in COLUMN_MAPPING.items():
        # 가능한 이름들도 정규화
        normalized_possible = [normalize_column_name(name) for name in possible_names]

        # 원본 컬럼에서 매칭되는 것 찾기
        for original_col, normalized_col in normalized_columns.items():
            if normalized_col in normalized_possible:
                column_mapping_result[original_col] = target_col
                break

    # 데이터프레임 컬럼명 변경
    df_mapped = df.rename(columns=column_mapping_result)

    return df_mapped, column_mapping_result


def parse_excel_file(file, header_row=0):
    """
    엑셀 파일 파싱 및 컬럼 매핑

    Args:
        file: 업로드된 파일 객체
        header_row: 헤더 행 번호 (기본값 0)

    Returns:
        tuple: (매핑된 데이터 리스트, 매핑 정보 딕셔너리)
    """
    # 엑셀 파일 읽기
    df = pd.read_excel(file, header=header_row)

    # 빈 행 제거
    df = df.dropna(how='all')

    # 컬럼명 매핑
    df_mapped, mapping_info = map_columns(df)

    # 데이터를 딕셔너리 리스트로 변환
    rcm_data = []
    for _, row in df_mapped.iterrows():
        # 모든 값이 NaN인 행은 제외
        if row.isna().all():
            continue

        record = {}
        for col in df_mapped.columns:
            # 표준 컬럼명인 경우에만 추가
            if col in COLUMN_MAPPING.keys():
                value = row[col]
                # NaN을 빈 문자열로 변환
                record[col] = '' if pd.isna(value) else str(value)

        # 최소한 control_code나 control_name이 있어야 유효한 레코드로 간주
        if record.get('control_code') or record.get('control_name'):
            rcm_data.append(record)

    return rcm_data, mapping_info


def validate_rcm_data(rcm_data):
    """
    RCM 데이터 유효성 검증

    Args:
        rcm_data: 파싱된 RCM 데이터 리스트

    Returns:
        tuple: (유효 여부, 에러 메시지)
    """
    if not rcm_data:
        return False, "엑셀 파일에서 유효한 데이터를 찾을 수 없습니다."

    # control_code 또는 control_name이 있는지 확인
    has_control_identifier = False
    for record in rcm_data:
        if record.get('control_code') or record.get('control_name'):
            has_control_identifier = True
            break

    if not has_control_identifier:
        return False, "통제코드 또는 통제명 컬럼을 찾을 수 없습니다. 엑셀 파일의 컬럼명을 확인해주세요."

    return True, ""


def get_mapping_summary(mapping_info):
    """
    매핑 정보를 사용자에게 보여줄 형태로 변환

    Args:
        mapping_info: 컬럼 매핑 정보 딕셔너리

    Returns:
        str: 매핑 요약 문자열
    """
    if not mapping_info:
        return "컬럼 매핑 정보 없음"

    lines = []
    for original, mapped in mapping_info.items():
        lines.append(f"'{original}' → '{mapped}'")

    return ", ".join(lines)
