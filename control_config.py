"""
운영평가 통제 설정
새로운 통제 추가 시 이 파일에 설정만 추가하면 자동으로 기능이 구현됩니다.
"""

# 수동통제 설정 (APD01, APD07, APD09, APD12 등)
MANUAL_CONTROLS = {
    'APD01': {
        'name': '사용자 권한 부여 승인',
        'description': '사용자 권한 부여 승인 테스트',

        # 모집단 필드 매핑
        'population_fields': ['user_id', 'user_name', 'department', 'permission', 'grant_date'],
        'population_headers': ['사용자ID', '사용자명', '부서명', '권한명', '권한부여일'],

        # 엑셀 헤더 (한글)
        'excel_headers': {
            'population': ['사용자ID', '사용자명', '부서명', '권한명', '권한부여일'],
            'testing': ['No', '사용자ID', '사용자명', '부서', '권한', '부여일',
                       '요청번호', '요청자명', '요청자부서', '승인자', '승인자부서', '승인일자', '예외', '비고']
        },

        # 필드 매핑 UI 라벨
        'field_labels': ['사용자ID', '사용자명', '부서명', '권한명', '권한부여일'],

        # 필수 컬럼 (업로드 시 안내)
        'required_fields': ['사용자ID', '사용자명', '부서명', '권한명', '권한부여일'],

        # Sticky 컬럼 설정 (좌측 고정)
        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 120, 'left': 50},    # 사용자ID
            {'width': 100, 'left': 170},   # 사용자명
            {'width': 120, 'left': 270},   # 부서
            {'width': 150, 'left': 390},   # 권한
            {'width': 120, 'left': 540}    # 부여일
        ],

        # 일반 컬럼 설정
        'normal_columns': [
            {'label': '요청번호', 'width': 180},
            {'label': '요청자명', 'width': 150},
            {'label': '요청자부서', 'width': 180},
            {'label': '승인자', 'width': 150},
            {'label': '승인자부서', 'width': 180},
            {'label': '승인일자', 'width': 150},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'APD07': {
        'name': 'DB 변경 승인',
        'description': 'DB 변경 승인 테스트',

        'population_fields': ['change_id', 'change_date'],
        'population_headers': ['쿼리(변경내역)', '변경일자'],

        'excel_headers': {
            'population': ['쿼리(변경내역)', '변경일자', '변경유형', '테이블명', '변경자', '승인일자'],
            'testing': ['No', '쿼리', '실행일자',
                       '변경 요청서 번호', '요청자명', '요청부서', '승인자명', '승인자부서', '승인일자', '승인여부', '사전승인여부', '결론', '비고']
        },

        'field_labels': ['쿼리(변경내역)', '변경일자'],
        'required_fields': ['쿼리', '실행일자'],

        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 쿼리
            {'width': 150, 'left': 250}    # 실행일자
        ],

        'normal_columns': [
            {'label': '변경 요청서 번호', 'width': 180},
            {'label': '요청자명', 'width': 150},
            {'label': '요청부서', 'width': 180},
            {'label': '승인자명', 'width': 150},
            {'label': '승인자부서', 'width': 180},
            {'label': '승인일자', 'width': 150},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'APD09': {
        'name': 'OS 접근권한 부여 승인',
        'description': 'OS 접근권한 부여 승인 테스트',

        'population_fields': ['account', 'grant_date'],
        'population_headers': ['OS 접근권한명', '접근권한부여일'],

        'excel_headers': {
            'population': ['OS 접근권한명', '접근권한부여일'],
            'testing': ['No', 'OS 접근권한명', '접근권한부여일',
                       '권한 요청서 번호', '요청자명', '요청부서', '승인자명', '승인자부서', '승인일자', '승인여부', '사전승인여부', '결론', '비고']
        },

        'field_labels': ['접근권한 부여 계정', '권한부여일'],
        'required_fields': ['접근권한 부여 계정', '권한부여일'],

        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 접근권한명
            {'width': 150, 'left': 250}    # 권한부여일
        ],

        'normal_columns': [
            {'label': '요청번호', 'width': 180},
            {'label': '요청자명', 'width': 150},
            {'label': '요청자부서', 'width': 180},
            {'label': '승인자', 'width': 150},
            {'label': '승인자부서', 'width': 180},
            {'label': '승인일자', 'width': 150},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'APD12': {
        'name': 'DB 접근권한 부여 승인',
        'description': 'DB 접근권한 부여 승인 테스트',

        'population_fields': ['account', 'grant_date'],
        'population_headers': ['DB 접근권한명', '접근권한부여일'],

        'excel_headers': {
            'population': ['DB 접근권한명', '접근권한부여일'],
            'testing': ['No', 'DB 접근권한명', '접근권한부여일',
                       '권한 요청서 번호', '요청자명', '요청부서', '승인자명', '승인자부서', '승인일자', '승인여부', '사전승인여부', '결론', '비고']
        },

        'field_labels': ['접근권한 부여 계정', '권한부여일'],
        'required_fields': ['접근권한 부여 계정', '권한부여일'],

        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 접근권한명
            {'width': 150, 'left': 250}    # 권한부여일
        ],

        'normal_columns': [
            {'label': '요청번호', 'width': 180},
            {'label': '요청자명', 'width': 150},
            {'label': '요청자부서', 'width': 180},
            {'label': '승인자', 'width': 150},
            {'label': '승인자부서', 'width': 180},
            {'label': '승인일자', 'width': 150},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'PC01': {
        'name': '프로그램 변경 승인',
        'description': '프로그램 변경 승인 테스트',

        # 모집단 필드 매핑 (필수: 프로그램명, 반영일자)
        'population_fields': ['program_name', 'deploy_date'],
        'population_headers': ['프로그램명', '반영일자'],

        # 엑셀 헤더
        'excel_headers': {
            'population': ['프로그램명', '반영일자'],
            'testing': ['No', '프로그램명', '반영일자',
                       '요청번호', '요청자', '요청자부서', '승인자', '승인자부서', '승인일자',
                       '개발담당자', '배포담당자', '예외', '비고']
        },

        # 필드 매핑 UI 라벨
        'field_labels': ['프로그램명', '반영일자'],

        # 필수 컬럼 (업로드 시 안내)
        'required_fields': ['프로그램명', '반영일자'],

        # Sticky 컬럼 설정 (좌측 고정)
        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 프로그램명
            {'width': 120, 'left': 250}    # 반영일자
        ],

        # 일반 컬럼 설정
        'normal_columns': [
            {'label': '변경 요청서 번호', 'width': 180},
            {'label': '요청자', 'width': 120},
            {'label': '요청자부서', 'width': 150},
            {'label': '승인자', 'width': 120},
            {'label': '승인자부서', 'width': 150},
            {'label': '승인일자', 'width': 120},
            {'label': '개발담당자', 'width': 120},
            {'label': '배포담당자', 'width': 120},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'PC02': {
        'name': '사용자 테스트',
        'description': '사용자 테스트 수행 확인',

        # PC01과 동일한 모집단 필드 (PC01 데이터 참조)
        'population_fields': ['program_name', 'deploy_date'],
        'population_headers': ['프로그램명', '반영일자'],

        # 엑셀 헤더
        'excel_headers': {
            'population': ['프로그램명', '반영일자'],
            'testing': ['No', '프로그램명', '반영일자',
                       '사용자테스트 유무', '사용자테스트담당자', '사용자테스트일자', '예외', '비고']
        },

        # PC01 참조용 플래그
        'depends_on': 'PC01',
        'skip_upload': True,  # 모집단 업로드 스킵 (PC01 데이터 사용)

        # 필드 매핑 UI는 사용 안함
        'field_labels': [],
        'required_fields': [],

        # Sticky 컬럼 설정 (PC01과 동일)
        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 프로그램명
            {'width': 120, 'left': 250}    # 반영일자
        ],

        # 일반 컬럼 설정 (PC02 전용)
        'normal_columns': [
            {'label': '변경 요청서 번호', 'width': 180},
            {'label': '사용자테스트 유무', 'width': 150},
            {'label': '사용자테스트담당자', 'width': 150},
            {'label': '사용자테스트일자', 'width': 150},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'PC03': {
        'name': '배포 승인',
        'description': '배포 승인 확인',

        # PC01과 동일한 모집단 필드 (PC01 데이터 참조)
        'population_fields': ['program_name', 'deploy_date'],
        'population_headers': ['프로그램명', '반영일자'],

        # 엑셀 헤더
        'excel_headers': {
            'population': ['프로그램명', '반영일자'],
            'testing': ['No', '프로그램명', '반영일자',
                       '변경 요청서 번호', '배포요청자', '배포요청자부서', '배포승인자', '배포승인일자', '예외', '비고']
        },

        # PC01 참조용 플래그
        'depends_on': 'PC01',
        'skip_upload': True,  # 모집단 업로드 스킵 (PC01 데이터 사용)

        # 필드 매핑 UI는 사용 안함
        'field_labels': [],
        'required_fields': [],

        # Sticky 컬럼 설정 (PC01과 동일)
        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 프로그램명
            {'width': 120, 'left': 250}    # 반영일자
        ],

        # 일반 컬럼 설정 (PC03 전용)
        'normal_columns': [
            {'label': '변경 요청서 번호', 'width': 180},
            {'label': '배포요청자', 'width': 150},
            {'label': '배포요청자부서', 'width': 180},
            {'label': '배포승인자', 'width': 150},
            {'label': '배포승인자부서', 'width': 180},
            {'label': '배포승인일자', 'width': 150},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'CO01': {
        'name': '배치 스케줄 승인',
        'description': '배치 스케줄 등록 및 승인 확인',

        # 모집단 필드
        'population_fields': ['batch_schedule_name', 'register_date'],
        'population_headers': ['배치스케줄이름', '등록일자'],

        # 엑셀 헤더
        'excel_headers': {
            'population': ['배치스케줄이름', '등록일자'],
            'testing': ['No', '배치스케줄이름', '등록일자',
                       '요청번호', '요청자', '요청자부서', '승인자', '승인자부서', '승인일자', '예외', '비고']
        },

        # 필드 라벨 및 필수 필드
        'field_labels': {
            'batch_schedule_name': '배치스케줄이름',
            'register_date': '등록일자'
        },
        'required_fields': ['batch_schedule_name', 'register_date'],

        # Sticky 컬럼 설정
        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 250, 'left': 50},    # 배치스케줄이름
            {'width': 120, 'left': 300}    # 등록일자
        ],

        # 일반 컬럼 설정
        'normal_columns': [
            {'label': '요청번호', 'width': 180},
            {'label': '요청자', 'width': 120},
            {'label': '요청자부서', 'width': 150},
            {'label': '승인자', 'width': 120},
            {'label': '승인자부서', 'width': 150},
            {'label': '승인일자', 'width': 120},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    },

    'GENERIC': {
        'name': '일반 수동통제',
        'description': '범용 수동통제 운영평가',

        # 모집단 필드 (2개 필드만 요구 - 컬럼명은 사용자가 지정)
        'population_fields': ['field1', 'field2'],
        'population_headers': ['필드1', '필드2'],

        # 엑셀 헤더
        'excel_headers': {
            'population': ['필드1', '필드2'],
            'testing': ['No', '필드1', '필드2',
                       '증빙1', '증빙2', '증빙3', '증빙4', '증빙5', '예외', '비고']
        },

        # 필드 라벨 (사용자 정의)
        'field_labels': ['주요 필드1', '주요 필드2'],
        'required_fields': ['주요 필드1', '주요 필드2'],

        # Sticky 컬럼 설정
        'sticky_columns': [
            {'width': 50, 'left': 0},      # No
            {'width': 200, 'left': 50},    # 필드1
            {'width': 200, 'left': 250}    # 필드2
        ],

        # 일반 컬럼 설정 (범용 증빙 컬럼)
        'normal_columns': [
            {'label': '증빙1', 'width': 200},
            {'label': '증빙2', 'width': 200},
            {'label': '증빙3', 'width': 200},
            {'label': '증빙4', 'width': 200},
            {'label': '증빙5', 'width': 200},
            {'label': '예외', 'width': 80},
            {'label': '비고', 'width': 300}
        ]
    }
}


def get_control_config(control_code):
    """통제 코드로 설정 조회"""
    return MANUAL_CONTROLS.get(control_code)


def get_all_manual_controls():
    """모든 수동통제 목록 조회"""
    return list(MANUAL_CONTROLS.keys())


def is_manual_control(control_code):
    """수동통제 여부 확인"""
    return control_code in MANUAL_CONTROLS
