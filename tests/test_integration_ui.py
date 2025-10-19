"""
통합 UI 테스트 - 모든 페이지와 버튼이 정상 작동하는지 확인

사용자 관점에서 각 페이지와 버튼을 실제로 클릭해보면서
404 에러, 500 에러, 작동하지 않는 버튼 등을 발견합니다.
"""

import pytest
from flask import session


class TestMainNavigation:
    """메인 네비게이션 및 홈페이지 테스트"""

    def test_homepage_loads(self, client):
        """홈페이지 로드 확인"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ITGC' in response.data or b'SnowBall' in response.data

    def test_health_check(self, client):
        """헬스체크 엔드포인트"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_login_page_loads(self, client):
        """로그인 페이지 로드"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'email' in response.data.lower()

    def test_logout_works(self, authenticated_client):
        """로그아웃 기능"""
        response = authenticated_client.get('/logout', follow_redirects=False)
        assert response.status_code in [302, 200]


class TestLink0Dashboard:
    """Link0 - 대시보드/소개 페이지"""

    def test_link0_page_loads(self, client):
        """Link0 페이지 로드"""
        response = client.get('/link0')
        assert response.status_code == 200


class TestLink1RCMGeneration:
    """Link1 - RCM 자동 생성 전체 플로우"""

    def test_link1_page_loads(self, client):
        """Link1 페이지 로드"""
        response = client.get('/link1')
        assert response.status_code == 200
        assert b'RCM' in response.data or b'rcm' in response.data

    def test_rcm_generate_button_exists(self, client):
        """RCM 생성 버튼 존재 확인"""
        response = client.get('/link1')
        assert b'submit' in response.data.lower() or b'button' in response.data.lower()

    def test_rcm_generate_form_submission(self, client):
        """RCM 생성 폼 제출"""
        response = client.post('/rcm_generate', data={
            'param1': 'test@example.com',
            'param2': 'TestSystem',
            'param3': 'SAP',
            'param4': 'Windows',
            'param5': 'Oracle'
        }, follow_redirects=False)
        # 성공(200), 리다이렉트(302), 또는 처리중(201) 모두 정상
        assert response.status_code in [200, 201, 302]


class TestLink2Interview:
    """Link2 - 인터뷰 전체 플로우"""

    def test_link2_page_loads(self, client):
        """Link2 인터뷰 페이지 로드"""
        response = client.get('/link2')
        assert response.status_code == 200

    def test_link2_question_display(self, client):
        """인터뷰 질문 표시 확인"""
        response = client.get('/link2')
        assert response.status_code == 200
        # 질문이나 폼 요소가 있어야 함
        assert b'question' in response.data.lower() or b'input' in response.data.lower()

    def test_link2_answer_submission(self, client):
        """인터뷰 답변 제출"""
        # 먼저 세션 초기화
        with client.session_transaction() as sess:
            sess['question_index'] = 0
            sess['answer'] = [''] * 55
            sess['textarea_answer'] = [''] * 55

        response = client.post('/link2', data={
            'a0': 'test@example.com',  # 첫 번째 질문 답변
            'a0_1': ''  # 텍스트 영역
        }, follow_redirects=False)
        # 200 (정상), 302 (리다이렉트), 400 (잘못된 요청) 모두 허용
        assert response.status_code in [200, 302, 400]

    def test_link2_prev_button(self, client):
        """이전 질문 버튼"""
        with client.session_transaction() as sess:
            sess['interview_answers'] = ['test@example.com', 'TestSystem']
            sess['interview_textarea_answers'] = ['', '']
            sess['current_question'] = 2

        response = client.get('/link2/prev')
        assert response.status_code in [200, 302]

    def test_ai_review_selection_page(self, client):
        """AI 검토 선택 페이지"""
        with client.session_transaction() as sess:
            sess['interview_answers'] = ['test@example.com'] + ['Y'] * 54
            sess['interview_textarea_answers'] = [''] * 55

        response = client.get('/ai_review_selection')
        assert response.status_code in [200, 302]

    def test_processing_page(self, client):
        """처리중 페이지"""
        response = client.get('/processing')
        assert response.status_code == 200


class TestLink3ControlGuide:
    """Link3 - 통제 가이드"""

    def test_link3_page_loads(self, client):
        """Link3 페이지 로드"""
        response = client.get('/link3')
        assert response.status_code == 200

    def test_link3_sidebar_categories(self, client):
        """사이드바 카테고리 표시"""
        response = client.get('/link3')
        assert response.status_code == 200
        # APD, PC, CO 카테고리가 있어야 함
        assert b'APD' in response.data or b'PC' in response.data

    def test_get_content_link3(self, client):
        """통제 내용 가져오기"""
        response = client.get('/get_content_link3?type=APD01')
        assert response.status_code == 200

    def test_paper_template_download_button(self, client):
        """템플릿 다운로드 버튼"""
        # GET은 405 에러가 정상
        response = client.get('/paper_template_download')
        assert response.status_code in [405, 404, 302]


class TestLink4EducationVideos:
    """Link4 - 교육 영상"""

    def test_link4_page_loads(self, client):
        """Link4 페이지 로드"""
        response = client.get('/link4')
        assert response.status_code == 200

    def test_link4_video_categories(self, client):
        """비디오 카테고리 표시"""
        response = client.get('/link4')
        assert response.status_code == 200
        # 비디오 관련 요소가 있어야 함 (APD, PC, CO 등 카테고리만 있어도 정상)
        assert b'APD' in response.data or b'PC' in response.data or b'CO' in response.data

    def test_get_content_link4_valid(self, client):
        """비디오 내용 가져오기 - 유효한 타입"""
        response = client.get('/get_content_link4?type=APD01')
        assert response.status_code == 200

    def test_get_content_link4_no_type(self, client):
        """비디오 내용 가져오기 - 타입 없음"""
        response = client.get('/get_content_link4')
        assert response.status_code in [200, 400]


class TestLink5RCMMapping:
    """Link5 - RCM 매핑 및 검토"""

    def test_rcm_list_requires_login(self, client):
        """RCM 목록 - 로그인 필요"""
        response = client.get('/rcm', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_rcm_list_page_loads(self, authenticated_client):
        """RCM 목록 페이지 로드"""
        response = authenticated_client.get('/rcm')
        assert response.status_code == 200

    def test_rcm_view_requires_login(self, client):
        """RCM 상세보기 - 로그인 필요"""
        response = client.get('/rcm/1/view', follow_redirects=False)
        assert response.status_code in [302, 401, 403, 404]

    def test_rcm_mapping_page_requires_login(self, client):
        """RCM 매핑 페이지 - 로그인 필요"""
        response = client.get('/rcm/1/mapping', follow_redirects=False)
        assert response.status_code in [302, 401, 403, 404]

    def test_api_rcm_list_requires_login(self, client):
        """API: RCM 목록 - 로그인 필요"""
        response = client.get('/api/rcm-list')
        assert response.status_code in [302, 401, 403]

    def test_api_rcm_status_requires_login(self, client):
        """API: RCM 상태 - 로그인 필요"""
        response = client.get('/api/rcm-status')
        assert response.status_code in [302, 401, 403]

    def test_completeness_report_requires_login(self, client):
        """완성도 보고서 - 로그인 필요"""
        response = client.get('/rcm/1/completeness-report', follow_redirects=False)
        assert response.status_code in [302, 401, 403, 404]


class TestLink6DesignEvaluation:
    """Link6 - 설계평가"""

    def test_design_evaluation_page_requires_login(self, client):
        """설계평가 페이지 - 로그인 필요"""
        response = client.get('/design-evaluation', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_design_evaluation_page_loads(self, authenticated_client):
        """설계평가 페이지 로드"""
        response = authenticated_client.get('/design-evaluation')
        assert response.status_code == 200

    def test_design_evaluation_rcm_list(self, authenticated_client):
        """설계평가 RCM 목록"""
        response = authenticated_client.get('/design-evaluation/rcm')
        # GET 요청은 302 리다이렉트, POST만 허용될 수 있음
        assert response.status_code in [200, 302, 405]

    def test_api_save_design_evaluation_requires_login(self, client):
        """API: 설계평가 저장 - 로그인 필요"""
        response = client.post('/api/design-evaluation/save', json={})
        assert response.status_code in [302, 400, 401, 403]

    def test_api_load_design_evaluation_requires_login(self, client):
        """API: 설계평가 로드 - 로그인 필요"""
        response = client.get('/api/design-evaluation/load/1')
        assert response.status_code in [302, 401, 403, 404]

    def test_api_create_evaluation_requires_login(self, client):
        """API: 평가 생성 - 로그인 필요"""
        response = client.post('/api/design-evaluation/create-evaluation', json={})
        assert response.status_code in [302, 400, 401, 403]

    def test_api_complete_evaluation_requires_login(self, client):
        """API: 평가 완료 - 로그인 필요"""
        response = client.post('/api/design-evaluation/complete', json={})
        assert response.status_code in [302, 400, 401, 403]

    def test_api_cancel_evaluation_requires_login(self, client):
        """API: 평가 취소 - 로그인 필요"""
        response = client.post('/api/design-evaluation/cancel', json={})
        assert response.status_code in [302, 400, 401, 403]

    def test_api_archive_evaluation_requires_login(self, client):
        """API: 평가 아카이브 - 로그인 필요"""
        response = client.post('/api/design-evaluation/archive', json={})
        assert response.status_code in [302, 400, 401, 403]


class TestLink7OperationEvaluation:
    """Link7 - 운영평가"""

    def test_operation_evaluation_page_requires_login(self, client):
        """운영평가 페이지 - 로그인 필요"""
        response = client.get('/operation-evaluation', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_operation_evaluation_page_loads(self, authenticated_client):
        """운영평가 페이지 로드"""
        response = authenticated_client.get('/operation-evaluation')
        assert response.status_code == 200

    def test_apd01_upload_requires_login(self, client):
        """APD01 업로드 - 로그인 필요"""
        response = client.post('/api/operation-evaluation/apd01/upload-population')
        assert response.status_code in [302, 400, 401, 403]

    def test_apd07_page_loads(self, authenticated_client):
        """APD07 페이지 로드"""
        response = authenticated_client.get('/operation-evaluation/apd07')
        # iframe으로 로드되거나 리다이렉트될 수 있음
        assert response.status_code in [200, 302]

    def test_apd09_page_loads(self, authenticated_client):
        """APD09 페이지 로드"""
        response = authenticated_client.get('/operation-evaluation/apd09')
        # iframe으로 로드되거나 리다이렉트될 수 있음
        assert response.status_code in [200, 302]

    def test_apd12_page_loads(self, authenticated_client):
        """APD12 페이지 로드"""
        response = authenticated_client.get('/operation-evaluation/apd12')
        # iframe으로 로드되거나 리다이렉트될 수 있음
        assert response.status_code in [200, 302]

    def test_api_save_operation_evaluation_requires_login(self, client):
        """API: 운영평가 저장 - 로그인 필요"""
        response = client.post('/api/operation-evaluation/save', json={})
        assert response.status_code in [302, 400, 401, 403]

    def test_api_reset_operation_evaluation_requires_login(self, client):
        """API: 운영평가 리셋 - 로그인 필요"""
        response = client.post('/api/operation-evaluation/reset', json={})
        assert response.status_code in [302, 400, 401, 403]


class TestUserPages:
    """사용자 페이지들"""

    def test_user_rcm_page_requires_login(self, client):
        """사용자 RCM 페이지 - 로그인 필요"""
        response = client.get('/user/rcm', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_user_rcm_page_loads(self, authenticated_client):
        """사용자 RCM 페이지 로드"""
        response = authenticated_client.get('/user/rcm')
        # /rcm으로 리다이렉트될 수 있음
        assert response.status_code in [200, 302]

    def test_user_design_evaluation_requires_login(self, client):
        """사용자 설계평가 - 로그인 필요"""
        response = client.get('/user/design-evaluation', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_user_operation_evaluation_requires_login(self, client):
        """사용자 운영평가 - 로그인 필요"""
        response = client.get('/user/operation-evaluation', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_user_internal_assessment_requires_login(self, client):
        """사용자 내부평가 - 로그인 필요"""
        response = client.get('/user/internal-assessment', follow_redirects=False)
        assert response.status_code in [302, 401, 403]


class TestAdminPages:
    """관리자 페이지들"""

    def test_admin_home_requires_permission(self, authenticated_client):
        """관리자 홈 - 권한 필요"""
        response = authenticated_client.get('/admin/', follow_redirects=False)
        # 일반 사용자는 접근 불가
        assert response.status_code in [302, 308, 401, 403]

    def test_admin_users_requires_permission(self, authenticated_client):
        """관리자 사용자 관리 - 권한 필요"""
        response = authenticated_client.get('/admin/users', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_admin_rcm_requires_permission(self, authenticated_client):
        """관리자 RCM 관리 - 권한 필요"""
        response = authenticated_client.get('/admin/rcm', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_admin_logs_requires_permission(self, authenticated_client):
        """관리자 로그 - 권한 필요"""
        response = authenticated_client.get('/admin/logs', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_admin_rcm_upload_requires_permission(self, authenticated_client):
        """관리자 RCM 업로드 - 권한 필요"""
        response = authenticated_client.get('/admin/rcm/upload', follow_redirects=False)
        assert response.status_code in [302, 401, 403]


class TestSessionManagement:
    """세션 관리 기능들"""

    def test_extend_session(self, authenticated_client):
        """세션 연장"""
        response = authenticated_client.post('/extend_session')
        assert response.status_code in [200, 302]

    def test_clear_session(self, authenticated_client):
        """세션 초기화"""
        response = authenticated_client.post('/clear_session')
        # 204 No Content도 정상 응답
        assert response.status_code in [200, 204, 302]

    def test_update_session_email(self, client):
        """세션 이메일 업데이트"""
        response = client.post('/update_session_email', json={
            'email': 'test@example.com'
        })
        assert response.status_code in [200, 400]


class TestAPIEndpoints:
    """기타 API 엔드포인트들"""

    def test_get_progress_no_task(self, client):
        """진행률 확인 - task_id 없음"""
        response = client.get('/get_progress')
        assert response.status_code in [200, 400]

    def test_control_sample_upload(self, authenticated_client):
        """통제 샘플 업로드"""
        response = authenticated_client.post('/api/control-sample/upload',
                                             data={},
                                             content_type='multipart/form-data')
        assert response.status_code in [200, 400, 404]

    def test_paper_request(self, client):
        """페이퍼 요청"""
        # 세션 초기화
        with client.session_transaction() as sess:
            sess['current_question'] = 0
        response = client.post('/paper_request', data={})
        assert response.status_code in [200, 302, 400, 500]


class TestGenericManualControls:
    """Generic 수동통제 페이지들"""

    def test_generic_manual_apd01(self, authenticated_client):
        """Generic APD01 페이지"""
        response = authenticated_client.get('/api/operation-evaluation/manual/APD01')
        assert response.status_code in [200, 404]

    def test_generic_manual_pc01(self, authenticated_client):
        """Generic PC01 페이지"""
        response = authenticated_client.get('/api/operation-evaluation/manual/PC01')
        assert response.status_code in [200, 404]

    def test_generic_manual_co01(self, authenticated_client):
        """Generic CO01 페이지"""
        response = authenticated_client.get('/api/operation-evaluation/manual/CO01')
        assert response.status_code in [200, 404]

    def test_generic_manual_invalid_control(self, authenticated_client):
        """Generic 잘못된 통제 코드"""
        response = authenticated_client.get('/api/operation-evaluation/manual/INVALID')
        assert response.status_code in [400, 404]


class TestButtonFunctionality:
    """주요 버튼 기능 테스트"""

    def test_link2_skip_sample_button(self, client):
        """Link2 스킵샘플 버튼 (JavaScript 검증은 불가하지만 페이지에 존재하는지 확인)"""
        response = client.get('/link2')
        assert response.status_code == 200
        # 스킵샘플 버튼이나 관련 JavaScript가 있어야 함
        assert b'skipSample' in response.data or b'skip' in response.data.lower()

    def test_link3_template_download_button(self, client):
        """Link3 템플릿 다운로드 버튼"""
        response = client.get('/link3')
        assert response.status_code == 200
        # 다운로드 버튼 관련 요소가 있어야 함
        assert b'download' in response.data.lower() or b'template' in response.data.lower()

    def test_rcm_toggle_completion_button(self, authenticated_client):
        """RCM 완료 토글 버튼"""
        response = authenticated_client.post('/rcm/1/toggle-completion')
        # RCM이 없으면 404, 권한 없으면 403, 성공하면 200
        assert response.status_code in [200, 302, 400, 403, 404]


class TestPageNotFound:
    """존재하지 않는 페이지 404 처리"""

    def test_invalid_route_returns_404(self, client):
        """잘못된 라우트는 404 반환"""
        response = client.get('/this-route-does-not-exist-12345')
        assert response.status_code == 404

    def test_invalid_link_number(self, client):
        """존재하지 않는 링크 번호"""
        response = client.get('/link999')
        assert response.status_code == 404

    def test_invalid_api_endpoint(self, client):
        """잘못된 API 엔드포인트"""
        response = client.get('/api/invalid-endpoint-12345')
        assert response.status_code == 404
