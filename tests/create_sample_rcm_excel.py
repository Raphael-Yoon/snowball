"""샘플 RCM 엑셀 파일 생성"""
import pandas as pd
import os

# 샘플 데이터 1: 한글 컬럼명, 단일 헤더
sample_data_korean = {
    '통제코드': ['ITGC-001', 'ITGC-002', 'ITGC-003', 'ITGC-004', 'ITGC-005'],
    '통제명': [
        '사용자 접근 권한 관리',
        '시스템 변경 관리',
        '데이터 백업 절차',
        '비밀번호 정책',
        '로그 모니터링'
    ],
    '통제설명': [
        '시스템 접근 권한을 적절히 부여하고 정기적으로 검토',
        '시스템 변경 시 승인 절차를 거치고 테스트 수행',
        '중요 데이터를 정기적으로 백업하고 복구 테스트 실시',
        '강력한 비밀번호 정책 수립 및 주기적 변경 강제',
        '시스템 로그를 모니터링하고 이상 징후 탐지'
    ],
    '핵심통제': ['Y', 'Y', 'Y', 'N', 'N'],
    '통제빈도': ['매일', '매월', '매주', '연 1회', '매일'],
    '통제유형': ['예방', '탐지', '예방', '예방', '탐지'],
    '통제속성': ['자동', '수동', '자동', '자동', '자동'],
    '모집단': ['전체 사용자', '전체 시스템', '중요 데이터베이스', '전체 사용자', '전체 시스템'],
    '모집단건수': ['150', '50', '10', '150', '50'],
    '검증절차': [
        '권한 부여 내역 샘플링 검토',
        '변경 승인 문서 확인',
        '백업 로그 검토 및 복구 테스트',
        '비밀번호 정책 설정 확인',
        '로그 분석 보고서 검토'
    ]
}

# 샘플 데이터 2: 영문 컬럼명, 단일 헤더
sample_data_english = {
    'Control Code': ['ELC-001', 'ELC-002', 'ELC-003'],
    'Control Name': [
        'Code of Conduct',
        'Risk Assessment',
        'Internal Audit'
    ],
    'Control Description': [
        'Company maintains and communicates code of conduct to all employees',
        'Management performs comprehensive risk assessment annually',
        'Internal audit function reviews key business processes'
    ],
    'Key Control': ['Y', 'Y', 'N'],
    'Frequency': ['Annual', 'Annual', 'Quarterly'],
    'Type': ['Preventive', 'Preventive', 'Detective'],
    'Nature': ['Manual', 'Manual', 'Manual'],
    'Population': ['All Employees', 'All Risks', 'Key Processes'],
    'Population Count': ['200', '50', '20'],
    'Test Procedure': [
        'Review code of conduct and training records',
        'Review risk assessment documentation',
        'Review internal audit reports'
    ]
}

# 샘플 데이터 3: 멀티라인 헤더 (한글)
# 첫 2줄은 설명/부제목, 3번째 줄이 실제 컬럼명
multiline_header_data = pd.DataFrame({
    'A': ['IT 일반 통제 대장 (ITGC)', '2024년 회계연도', '통제코드', 'ITGC-001', 'ITGC-002'],
    'B': ['Information Technology', 'General Controls', '통제명', '접근 통제', '변경 관리'],
    'C': ['통제 설명서', 'Control Documentation', '통제설명', '사용자 접근권한 관리', '시스템 변경 승인'],
    'D': ['', '', '핵심통제', 'Y', 'Y'],
    'E': ['', '', '통제빈도', '매일', '매월'],
})


def create_sample_excel_files():
    """샘플 엑셀 파일 생성"""
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. 한글 컬럼명 파일
    file1 = os.path.join(output_dir, 'sample_rcm_korean.xlsx')
    df1 = pd.DataFrame(sample_data_korean)
    df1.to_excel(file1, index=False, engine='openpyxl')
    print(f"✓ 생성됨: {file1}")
    print(f"  - 레코드 수: {len(df1)}")
    print(f"  - 컬럼: {list(df1.columns)}")

    # 2. 영문 컬럼명 파일
    file2 = os.path.join(output_dir, 'sample_rcm_english.xlsx')
    df2 = pd.DataFrame(sample_data_english)
    df2.to_excel(file2, index=False, engine='openpyxl')
    print(f"\n✓ 생성됨: {file2}")
    print(f"  - 레코드 수: {len(df2)}")
    print(f"  - 컬럼: {list(df2.columns)}")

    # 3. 멀티라인 헤더 파일
    file3 = os.path.join(output_dir, 'sample_rcm_multiline_header.xlsx')
    multiline_header_data.to_excel(file3, index=False, header=False, engine='openpyxl')
    print(f"\n✓ 생성됨: {file3}")
    print(f"  - 특징: 멀티라인 헤더 (3번째 행이 실제 컬럼명)")
    print(f"  - 업로드 시 '데이터 시작 행'에 2를 입력하세요")

    # 4. 혼합 컬럼명 파일 (한글+영문)
    mixed_data = {
        'Control Code': ['TLC-001', 'TLC-002'],
        '통제명': ['매출 승인', '구매 승인'],
        'Description': ['Sales approval process', 'Purchase approval process'],
        '핵심통제': ['Y', 'Y'],
        'Frequency': ['Daily', 'Daily']
    }
    file4 = os.path.join(output_dir, 'sample_rcm_mixed.xlsx')
    df4 = pd.DataFrame(mixed_data)
    df4.to_excel(file4, index=False, engine='openpyxl')
    print(f"\n✓ 생성됨: {file4}")
    print(f"  - 레코드 수: {len(df4)}")
    print(f"  - 특징: 한글+영문 혼합 컬럼명")
    print(f"  - 컬럼: {list(df4.columns)}")

    print("\n" + "="*60)
    print("샘플 파일이 모두 생성되었습니다!")
    print("="*60)
    print("\n사용 방법:")
    print("1. 웹 브라우저에서 http://127.0.0.1:5001/rcm/upload 접속")
    print("2. 생성된 샘플 파일 중 하나를 업로드")
    print("3. 멀티라인 헤더 파일의 경우 '데이터 시작 행'에 2 입력")


if __name__ == '__main__':
    create_sample_excel_files()
