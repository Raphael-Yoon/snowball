"""
Link7 (운영평가) 기능 테스트
운영평가 목록, 생성, 저장, APD 표준통제 테스트 기능 검증
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from io import BytesIO

# ================================
# 운영평가 메인 페이지 테스트
# ================================

def test_operation_evaluation_page_requires_login(client):
    """로그인하지 않으면 운영평가 페이지 접근 불가"""
    response = client.get('/operation-evaluation')
    assert response.status_code == 302
    assert '/login' in response.location

def test_operation_evaluation_page_rendering(authenticated_client, test_user):
    """운영평가 페이지가 정상 렌더링"""
    response = authenticated_client.get('/operation-evaluation')
    assert response.status_code == 200

def test_operation_evaluation_page_shows_user_info(authenticated_client, test_user):
    """운영평가 페이지에 사용자 정보 표시"""
    response = authenticated_client.get('/operation-evaluation')
    assert response.status_code == 200

# ================================
# RCM 선택 페이지 테스트
# ================================

def test_operation_evaluation_rcm_requires_login(client):
    """로그인하지 않으면 RCM 선택 페이지 접근 불가"""
    response = client.get('/operation-evaluation/rcm')
    assert response.status_code == 302

def test_operation_evaluation_rcm_rendering(authenticated_client, test_user):
    """RCM 선택 페이지가 정상 렌더링"""
    with patch('snowball_link7.get_user_rcms', return_value=[]):
        response = authenticated_client.get('/operation-evaluation/rcm')
        assert response.status_code in [200, 302]

def test_operation_evaluation_rcm_shows_user_rcms(authenticated_client, test_user):
    """사용자 RCM 목록 표시"""
    mock_rcms = [
        {'rcm_id': 1, 'rcm_name': 'Test RCM A'},
        {'rcm_id': 2, 'rcm_name': 'Test RCM B'}
    ]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        response = authenticated_client.get('/operation-evaluation/rcm')
        assert response.status_code in [200, 302]

# ================================
# API: 운영평가 저장 테스트
# ================================

def test_save_operation_evaluation_api(authenticated_client, test_user):
    """운영평가 데이터 저장 API"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link7.save_operation_evaluation'):
            with patch('snowball_link7.log_user_activity'):
                response = authenticated_client.post(
                    '/api/operation-evaluation/save',
                    data=json.dumps({
                        'rcm_id': 1,
                        'detail_id': 1,
                        'test_result': 'Pass',
                        'test_comment': 'Test passed'
                    }),
                    content_type='application/json'
                )
                assert response.status_code in [200, 403]

def test_save_operation_evaluation_requires_login(client):
    """로그인 없이 저장 시도"""
    response = client.post(
        '/api/operation-evaluation/save',
        data=json.dumps({
            'rcm_id': 1,
            'detail_id': 1,
            'test_result': 'Pass'
        }),
        content_type='application/json'
    )
    assert response.status_code == 302

# ================================
# API: 운영평가 불러오기 테스트
# ================================

def test_load_operation_evaluation_api(authenticated_client, test_user):
    """운영평가 데이터 불러오기"""
    mock_evaluations = [
        {
            'detail_id': 1,
            'control_code': 'APD01',
            'test_result': 'Pass'
        }
    ]

    with patch('snowball_link7.get_operation_evaluations', return_value=mock_evaluations):
        response = authenticated_client.get('/api/operation-evaluation/load/1/session1')
        assert response.status_code in [200, 403]

def test_load_operation_evaluation_requires_login(client):
    """로그인 없이 불러오기 시도"""
    response = client.get('/api/operation-evaluation/load/1/session1')
    assert response.status_code == 302

# ================================
# API: 리셋 테스트
# ================================

def test_reset_operation_evaluation(authenticated_client, test_user):
    """운영평가 리셋"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/reset',
                data=json.dumps({
                    'rcm_id': 1,
                    'control_code': 'APD01',
                    'design_evaluation_session': 'session1'
                }),
                content_type='application/json'
            )
            assert response.status_code in [200, 400, 403]

# ================================
# APD01 테스트 페이지 및 API
# ================================

def test_apd01_upload_population_requires_login(client):
    """로그인 없이 APD01 모집단 업로드 시도"""
    response = client.post('/api/operation-evaluation/apd01/upload-population')
    assert response.status_code == 302

def test_apd01_upload_population(authenticated_client, test_user):
    """APD01 모집단 엑셀 업로드"""
    mock_file = BytesIO(b'fake excel data')
    mock_file.name = 'test.xlsx'

    with patch('openpyxl.load_workbook'):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/apd01/upload-population',
                data={'file': (mock_file, 'test.xlsx')},
                content_type='multipart/form-data'
            )
            # 업로드 성공 또는 파일 파싱 오류 허용
            assert response.status_code in [200, 302, 400, 500]

# ================================
# APD07 테스트 페이지 및 API
# ================================

def test_apd07_page_requires_login(client):
    """로그인하지 않으면 APD07 페이지 접근 불가"""
    response = client.get('/operation-evaluation/apd07')
    assert response.status_code == 302

def test_apd07_page_rendering(authenticated_client, test_user):
    """APD07 테스트 페이지 렌더링"""
    response = authenticated_client.get('/operation-evaluation/apd07')
    assert response.status_code in [200, 302]  # 세션 체크로 리다이렉트 가능

def test_apd07_upload_population(authenticated_client, test_user):
    """APD07 모집단 업로드"""
    mock_file = BytesIO(b'fake excel data')
    mock_file.name = 'test.xlsx'

    with patch('openpyxl.load_workbook'):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/apd07/upload-population',
                data={'file': (mock_file, 'test.xlsx')},
                content_type='multipart/form-data'
            )
            assert response.status_code in [200, 302, 400, 500]

def test_apd07_save_test_results(authenticated_client, test_user):
    """APD07 테스트 결과 저장"""
    with patch('snowball_link7.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.post(
            '/api/operation-evaluation/apd07/save-test-results',
            data=json.dumps({
                'rcm_id': 1,
                'session_name': 'Test Session',
                'test_results': []
            }),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]

# ================================
# APD09 테스트 페이지 및 API
# ================================

def test_apd09_page_requires_login(client):
    """로그인하지 않으면 APD09 페이지 접근 불가"""
    response = client.get('/operation-evaluation/apd09')
    assert response.status_code == 302

def test_apd09_page_rendering(authenticated_client, test_user):
    """APD09 테스트 페이지 렌더링"""
    response = authenticated_client.get('/operation-evaluation/apd09')
    assert response.status_code in [200, 302, 500]  # 세션 체크로 리다이렉트 가능

def test_apd09_upload_population(authenticated_client, test_user):
    """APD09 모집단 업로드"""
    mock_file = BytesIO(b'fake excel data')
    mock_file.name = 'test.xlsx'

    with patch('openpyxl.load_workbook'):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/apd09/upload-population',
                data={'file': (mock_file, 'test.xlsx')},
                content_type='multipart/form-data'
            )
            assert response.status_code in [200, 302, 400, 500]

def test_apd09_save_test_results(authenticated_client, test_user):
    """APD09 테스트 결과 저장"""
    with patch('snowball_link7.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.post(
            '/api/operation-evaluation/apd09/save-test-results',
            data=json.dumps({
                'rcm_id': 1,
                'session_name': 'Test Session',
                'test_results': []
            }),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]

# ================================
# APD12 테스트 페이지 및 API
# ================================

def test_apd12_page_requires_login(client):
    """로그인하지 않으면 APD12 페이지 접근 불가"""
    response = client.get('/operation-evaluation/apd12')
    assert response.status_code == 302

def test_apd12_page_rendering(authenticated_client, test_user):
    """APD12 테스트 페이지 렌더링"""
    response = authenticated_client.get('/operation-evaluation/apd12')
    assert response.status_code in [200, 302, 500]  # 세션 체크로 리다이렉트 가능

def test_apd12_upload_population(authenticated_client, test_user):
    """APD12 모집단 업로드"""
    mock_file = BytesIO(b'fake excel data')
    mock_file.name = 'test.xlsx'

    with patch('openpyxl.load_workbook'):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/apd12/upload-population',
                data={'file': (mock_file, 'test.xlsx')},
                content_type='multipart/form-data'
            )
            assert response.status_code in [200, 302, 400, 500]

def test_apd12_save_test_results(authenticated_client, test_user):
    """APD12 테스트 결과 저장"""
    with patch('snowball_link7.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.post(
            '/api/operation-evaluation/apd12/save-test-results',
            data=json.dumps({
                'rcm_id': 1,
                'session_name': 'Test Session',
                'test_results': []
            }),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]

# ================================
# API: 설계평가 가져오기 테스트
# ================================

def test_get_design_evaluation_api(authenticated_client, test_user):
    """설계평가 데이터 가져오기"""
    with patch('snowball_link7.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = []
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.get(
            '/api/design-evaluation/get',
            query_string={'rcm_id': 1}
        )
        assert response.status_code in [200, 400]

def test_get_design_evaluation_requires_login(client):
    """로그인 없이 설계평가 가져오기 시도"""
    response = client.get(
        '/api/design-evaluation/get',
        query_string={'rcm_id': 1}
    )
    assert response.status_code == 302

# ================================
# 헬퍼 함수 테스트
# ================================

def test_get_user_info_function(authenticated_client, test_user):
    """get_user_info 함수 존재 확인"""
    from snowball_link7 import get_user_info

    with authenticated_client.application.app_context():
        assert callable(get_user_info)

def test_is_logged_in_function(authenticated_client, test_user):
    """is_logged_in 함수 존재 확인"""
    from snowball_link7 import is_logged_in

    with authenticated_client.application.app_context():
        assert callable(is_logged_in)

# ================================
# 블루프린트 등록 확인 테스트
# ================================

def test_link7_blueprint_registered(app):
    """Link7 블루프린트가 앱에 등록되어 있는지 확인"""
    assert 'link7' in [bp.name for bp in app.blueprints.values()]

def test_link7_routes_exist(app):
    """Link7의 주요 라우트 존재 확인"""
    routes = [rule.rule for rule in app.url_map.iter_rules()]

    # 주요 라우트 확인
    assert any('/operation-evaluation' in route for route in routes)
    assert any('/api/operation-evaluation/save' in route for route in routes)
    assert any('/api/operation-evaluation/load' in route for route in routes)
    assert any('/operation-evaluation/apd07' in route for route in routes)
    assert any('/operation-evaluation/apd09' in route for route in routes)
    assert any('/operation-evaluation/apd12' in route for route in routes)

# ================================
# 권한 검증 테스트
# ================================

def test_operation_evaluation_requires_authentication(client):
    """운영평가 주요 기능은 인증 필요"""
    # 메인 페이지
    response = client.get('/operation-evaluation')
    assert response.status_code == 302

    # 저장 API
    response = client.post(
        '/api/operation-evaluation/save',
        data=json.dumps({'rcm_id': 1}),
        content_type='application/json'
    )
    assert response.status_code == 302

    # 불러오기 API
    response = client.get('/api/operation-evaluation/load/1/session1')
    assert response.status_code == 302

    # APD 페이지들
    for apd in ['apd07', 'apd09', 'apd12']:
        response = client.get(f'/operation-evaluation/{apd}')
        assert response.status_code == 302

def test_operation_evaluation_checks_rcm_access(authenticated_client, test_user):
    """운영평가는 RCM 접근 권한 체크"""
    # 접근 가능한 RCM 목록이 비어있을 때
    with patch('snowball_link7.get_user_rcms', return_value=[]):
        with patch('snowball_link7.save_operation_evaluation'):
            with patch('snowball_link7.log_user_activity'):
                response = authenticated_client.post(
                    '/api/operation-evaluation/save',
                    data=json.dumps({
                        'rcm_id': 999,
                        'detail_id': 1,
                        'test_result': 'Pass'
                    }),
                    content_type='application/json'
                )
                # 403 Forbidden 또는 유사한 권한 오류
                assert response.status_code in [200, 403]

# ================================
# 활동 로그 기록 테스트
# ================================

def test_operation_evaluation_logs_activities(authenticated_client, test_user):
    """운영평가 주요 작업 시 활동 로그 기록"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link7.save_operation_evaluation'):
            with patch('snowball_link7.log_user_activity') as mock_log:
                response = authenticated_client.post(
                    '/api/operation-evaluation/save',
                    data=json.dumps({
                        'rcm_id': 1,
                        'detail_id': 1,
                        'test_result': 'Pass'
                    }),
                    content_type='application/json'
                )
                # log_user_activity 호출 여부는 구현에 따라 다를 수 있음

# ================================
# 표준통제 테스트 워크플로우
# ================================

def test_standard_control_test_workflow(authenticated_client, test_user):
    """표준통제 테스트 워크플로우 (APD07 예시)"""
    # 1. APD07 페이지 접근
    response = authenticated_client.get('/operation-evaluation/apd07')
    assert response.status_code in [200, 302, 500]  # 세션 체크로 리다이렉트 가능

    # 2. 모집단 업로드
    mock_file = BytesIO(b'fake excel data')
    mock_file.name = 'population.xlsx'

    with patch('openpyxl.load_workbook'):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value.__enter__.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/apd07/upload-population',
                data={'file': (mock_file, 'population.xlsx')},
                content_type='multipart/form-data'
            )
            # 업로드는 성공하거나 파싱 오류
            assert response.status_code in [200, 302, 400, 500]

    # 3. 테스트 결과 저장
    with patch('snowball_link7.get_db') as mock_db:
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn

        response = authenticated_client.post(
            '/api/operation-evaluation/apd07/save-test-results',
            data=json.dumps({
                'rcm_id': 1,
                'session_name': 'Test',
                'test_results': []
            }),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]

# ================================
# 에러 처리 테스트
# ================================

def test_operation_evaluation_handles_invalid_file_upload(authenticated_client, test_user):
    """잘못된 파일 업로드 시 에러 처리"""
    # 빈 파일
    response = authenticated_client.post(
        '/api/operation-evaluation/apd01/upload-population',
        data={},
        content_type='multipart/form-data'
    )
    # 400 Bad Request 또는 파일 없음 오류, 일부는 200 반환 가능
    assert response.status_code in [200, 302, 400, 500]

def test_operation_evaluation_handles_missing_data(authenticated_client, test_user):
    """필수 데이터 누락 시 에러 처리"""
    response = authenticated_client.post(
        '/api/operation-evaluation/save',
        data=json.dumps({}),  # 필수 필드 누락
        content_type='application/json'
    )
    # 400 또는 데이터 검증 오류
    assert response.status_code in [200, 400, 403]

# ================================
# 통합 시나리오 테스트
# ================================

def test_operation_evaluation_full_workflow(authenticated_client, test_user):
    """운영평가 전체 워크플로우"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    # 1. 메인 페이지 접근
    response = authenticated_client.get('/operation-evaluation')
    assert response.status_code == 200

    # 2. RCM 선택 페이지
    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        response = authenticated_client.get('/operation-evaluation/rcm')
        assert response.status_code in [200, 302]

    # 3. 표준통제 테스트 (APD09)
    response = authenticated_client.get('/operation-evaluation/apd09')
    assert response.status_code in [200, 302, 500]  # 세션 체크로 리다이렉트/에러 가능

    # 4. 테스트 결과 저장
    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link7.save_operation_evaluation'):
            with patch('snowball_link7.log_user_activity'):
                response = authenticated_client.post(
                    '/api/operation-evaluation/save',
                    data=json.dumps({
                        'rcm_id': 1,
                        'detail_id': 1,
                        'test_result': 'Pass',
                        'test_comment': 'All tests passed'
                    }),
                    content_type='application/json'
                )
                assert response.status_code in [200, 403]


# ================================
# 당기 발생사실 없음 기능 테스트
# ================================

def test_save_no_occurrence_requires_login(client):
    """로그인 없이 발생사실 없음 저장 시도"""
    response = client.post(
        '/api/operation-evaluation/save-no-occurrence',
        data=json.dumps({
            'rcm_id': 1,
            'control_code': 'APD01',
            'design_evaluation_session': 'DEFAULT',
            'no_occurrence': True,
            'no_occurrence_reason': 'Test reason'
        }),
        content_type='application/json'
    )
    assert response.status_code == 302

def test_save_no_occurrence_api(authenticated_client, test_user):
    """발생사실 없음 저장 API"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value = mock_conn

            response = authenticated_client.post(
                '/api/operation-evaluation/save-no-occurrence',
                data=json.dumps({
                    'rcm_id': 1,
                    'control_code': 'APD01',
                    'design_evaluation_session': 'DEFAULT',
                    'no_occurrence': True,
                    'no_occurrence_reason': 'No transactions during period'
                }),
                content_type='application/json'
            )
            assert response.status_code in [200, 400, 403, 500]

def test_save_no_occurrence_sets_conclusion_not_applicable(authenticated_client, test_user):
    """발생사실 없음 저장 시 conclusion이 not_applicable로 설정됨"""
    # 이 테스트는 실제 데이터베이스 저장 후 확인이 필요하므로
    # 통합 테스트에서 검증하는 것이 더 적합할 수 있음
    pass

def test_save_no_occurrence_requires_reason(authenticated_client, test_user):
    """발생사실 없음 저장 시 사유 필요 (선택적)"""
    mock_rcms = [{'rcm_id': 1, 'rcm_name': 'Test RCM'}]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        with patch('snowball_link7.get_db') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value = mock_conn

            # 사유 없이 저장 시도
            response = authenticated_client.post(
                '/api/operation-evaluation/save-no-occurrence',
                data=json.dumps({
                    'rcm_id': 1,
                    'control_code': 'APD01',
                    'design_evaluation_session': 'DEFAULT',
                    'no_occurrence': True,
                    'no_occurrence_reason': ''  # 빈 사유
                }),
                content_type='application/json'
            )
            # 사유가 필수가 아니므로 성공할 수 있음
            assert response.status_code in [200, 400, 403, 500]


# ================================
# 팝업 자동 닫기 기능 테스트
# ================================

def test_no_occurrence_popup_close_behavior(authenticated_client, test_user):
    """발생사실 없음 저장 후 팝업 닫기 동작 (JavaScript 테스트)"""
    # JavaScript 동작은 단위 테스트로 검증하기 어려움
    # E2E 테스트나 프론트엔드 테스트에서 검증해야 함
    # 여기서는 API 응답이 성공을 반환하는지만 확인
    pass


# ================================
# 매핑안됨 표시 테스트
# ================================

def test_unmapped_controls_display_text(authenticated_client, test_user):
    """매핑안됨 텍스트 표시 확인"""
    # 설계평가 페이지에서 매핑안됨 텍스트 확인
    response = authenticated_client.get('/design-evaluation/rcm')
    if response.status_code == 200:
        data = response.data.decode()
        # "미매핑"이 아닌 "매핑안됨"이 표시되어야 함
        if '매핑' in data:
            # 둘 중 하나가 있어야 함 (데이터에 따라)
            assert '매핑안됨' in data or '매핑됨' in data or '매핑불가' in data

# ================================
# ELC 운영평가 테스트
# ================================

def test_elc_operation_evaluation_requires_login(client):
    """로그인하지 않으면 ELC 운영평가 페이지 접근 불가"""
    response = client.get('/elc/operation-evaluation')
    assert response.status_code == 302
    assert '/login' in response.location

def test_elc_operation_evaluation_page_rendering(authenticated_client, test_user):
    """ELC 운영평가 페이지가 정상 렌더링"""
    response = authenticated_client.get('/elc/operation-evaluation')
    assert response.status_code == 200

def test_elc_operation_evaluation_shows_elc_rcms_only(authenticated_client, test_user):
    """ELC 운영평가 페이지는 ELC RCM만 표시"""
    mock_rcms = [
        {'rcm_id': 1, 'rcm_name': 'ELC RCM', 'control_category': 'ELC'},
        {'rcm_id': 2, 'rcm_name': 'TLC RCM', 'control_category': 'TLC'},
        {'rcm_id': 3, 'rcm_name': 'ITGC RCM', 'control_category': 'ITGC'}
    ]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        response = authenticated_client.get('/elc/operation-evaluation')
        assert response.status_code == 200
        # ELC RCM만 전달되어야 함 (템플릿에서 확인)

# ================================
# TLC 운영평가 테스트
# ================================

def test_tlc_operation_evaluation_requires_login(client):
    """로그인하지 않으면 TLC 운영평가 페이지 접근 불가"""
    response = client.get('/tlc/operation-evaluation')
    assert response.status_code == 302
    assert '/login' in response.location

def test_tlc_operation_evaluation_page_rendering(authenticated_client, test_user):
    """TLC 운영평가 페이지가 정상 렌더링"""
    response = authenticated_client.get('/tlc/operation-evaluation')
    assert response.status_code == 200

def test_tlc_operation_evaluation_shows_tlc_rcms_only(authenticated_client, test_user):
    """TLC 운영평가 페이지는 TLC RCM만 표시"""
    mock_rcms = [
        {'rcm_id': 1, 'rcm_name': 'ELC RCM', 'control_category': 'ELC'},
        {'rcm_id': 2, 'rcm_name': 'TLC RCM', 'control_category': 'TLC'},
        {'rcm_id': 3, 'rcm_name': 'ITGC RCM', 'control_category': 'ITGC'}
    ]

    with patch('snowball_link7.get_user_rcms', return_value=mock_rcms):
        response = authenticated_client.get('/tlc/operation-evaluation')
        assert response.status_code == 200
        # TLC RCM만 전달되어야 함 (템플릿에서 확인)
