"""
관리자 기능(snowball_admin.py) 통합 테스트 스크립트
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock
import io

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from snowball import app
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    sys.exit(1)

from test.link5_test import TestStatus, TestResult

class AdminTestSuite:
    """관리자 기능 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.results: List[TestResult] = []

    def run_all_tests(self):
        print("=" * 80)
        print("Admin 관리자 기능 통합 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
        ])

        self._run_category("2. 사용자 관리 검증", [
            self.test_admin_users_page,
            self.test_admin_add_user,
            self.test_admin_edit_user,
            self.test_admin_delete_user,
        ])

        self._run_category("3. RCM 관리 검증", [
            self.test_admin_rcm_page,
            self.test_admin_rcm_upload_process,
        ])

        self._run_category("4. 로그 및 작업 관리", [
            self.test_admin_logs_page,
            self.test_admin_work_log_page,
        ])

        return self._print_final_report()

    def _run_category(self, category_name: str, tests: List):
        print(f"\n{'=' * 80}")
        print(f"{category_name}")
        print(f"{'=' * 80}")

        for test_func in tests:
            result = TestResult(test_func.__name__, category_name)
            self.results.append(result)

            try:
                result.start()
                print(f"\n{TestStatus.RUNNING.value} {test_func.__name__}...", end=" ")
                test_func(result)
                if result.status == TestStatus.RUNNING:
                    result.pass_test()
                print(f"\r{result}")

                if result.details:
                    for detail in result.details:
                        print(f"    ℹ️  {detail}")

            except Exception as e:
                result.fail_test(f"예외 발생: {str(e)}")
                print(f"\r{result}")
                print(f"    ❌ {result.message}")

    def _setup_admin_session(self):
        """관리자 세션 설정"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_info'] = {'user_id': 1, 'user_name': '관리자', 'admin_flag': 'Y'}

    # =========================================================================
    # 1. 환경 및 설정 검증
    # =========================================================================

    def test_environment_setup(self, result: TestResult):
        """admin Blueprint 등록 확인"""
        if 'admin' in self.app.blueprints:
            result.pass_test("admin Blueprint가 정상적으로 등록되었습니다.")
        else:
            result.fail_test("admin Blueprint 등록 실패")

    # =========================================================================
    # 2. 사용자 관리 검증
    # =========================================================================

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.get_user_info')
    def test_admin_users_page(self, result: TestResult, mock_user_info, mock_get_user, mock_db):
        """사용자 관리 페이지 접근 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = {'count': 0}
        mock_conn.execute.return_value.fetchall.return_value = []

        response = self.client.get('/admin/users')
        if response.status_code == 200:
            result.pass_test("사용자 관리 페이지가 정상 응답합니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.get_user_info')
    def test_admin_add_user(self, result: TestResult, mock_user_info, mock_get_user, mock_db):
        """사용자 추가 기능 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        
        data = {
            'company_name': '테스트사',
            'user_name': '신규유저',
            'user_email': 'new@test.com',
            'admin_flag': 'N',
            'effective_start_date': '2024-01-01'
        }
        response = self.client.post('/admin/users/add', data=data, follow_redirects=True)
        if response.status_code == 200:
            result.pass_test("사용자 추가 요청이 정상 처리되었습니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.get_user_info')
    def test_admin_edit_user(self, result: TestResult, mock_user_info, mock_get_user, mock_db):
        """사용자 수정 기능 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        
        data = {'user_name': '수정된이름', 'admin_flag': 'Y'}
        response = self.client.post('/admin/users/edit/1', data=data, follow_redirects=True)
        if response.status_code == 200:
            result.pass_test("사용자 수정 요청이 정상 처리되었습니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.get_user_info')
    def test_admin_delete_user(self, result: TestResult, mock_user_info, mock_get_user, mock_db):
        """사용자 삭제 기능 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        
        response = self.client.post('/admin/users/delete/1', follow_redirects=True)
        if response.status_code == 200:
            result.pass_test("사용자 삭제 요청이 정상 처리되었습니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    # =========================================================================
    # 3. RCM 관리 검증
    # =========================================================================

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.get_user_info')
    def test_admin_rcm_page(self, result: TestResult, mock_user_info, mock_get_user, mock_db):
        """RCM 관리 페이지 접근 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        
        mock_conn = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = {'count': 0}
        mock_conn.execute.return_value.fetchall.return_value = []

        response = self.client.get('/admin/rcm')
        if response.status_code == 200:
            result.pass_test("RCM 관리 페이지가 정상 응답합니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.create_rcm')
    @patch('snowball_admin.get_user_info')
    def test_admin_rcm_upload_process(self, result: TestResult, mock_user_info, mock_create, mock_get_user, mock_db):
        """RCM 업로드 프로세스 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        mock_create.return_value = 100
        
        # 가짜 엑셀 파일 생성
        excel_content = b"fake excel content"
        data = {
            'rcm_name': '테스트 RCM',
            'target_user_id': '1',
            'excel_file': (io.BytesIO(excel_content), 'test.xlsx')
        }
        
        # process_upload는 내부적으로 openpyxl을 사용하므로 더 깊은 모킹이 필요할 수 있음
        # 여기서는 엔드포인트 호출 성공 여부 위주로 확인
        with patch('openpyxl.load_workbook') as mock_load:
            mock_ws = MagicMock()
            mock_ws.max_row = 10
            mock_ws.__getitem__.return_value = [MagicMock(value='Header1')]
            mock_load.return_value.active = mock_ws
            mock_load.return_value.sheetnames = ['Sheet1']
            
            response = self.client.post('/admin/rcm/process_upload', data=data, content_type='multipart/form-data')
            
            if response.status_code == 200:
                result.pass_test("RCM 업로드 프로세스가 정상 시작되었습니다.")
            else:
                result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    # =========================================================================
    # 4. 로그 및 작업 관리
    # =========================================================================

    @patch('snowball_admin.get_db')
    @patch('auth.get_current_user')
    @patch('snowball_admin.get_user_activity_logs')
    @patch('snowball_admin.get_activity_log_count')
    @patch('snowball_admin.get_user_info')
    def test_admin_logs_page(self, result: TestResult, mock_user_info, mock_count, mock_logs, mock_get_user, mock_db):
        """활동 로그 페이지 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        mock_count.return_value = 0
        mock_logs.return_value = []
        
        response = self.client.get('/admin/logs')
        if response.status_code == 200:
            result.pass_test("활동 로그 페이지가 정상 응답합니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    @patch('auth.get_current_user')
    @patch('snowball_admin.get_work_log_docs')
    @patch('snowball_admin.get_user_info')
    def test_admin_work_log_page(self, result: TestResult, mock_user_info, mock_work, mock_get_user):
        """작업 로그 페이지 확인"""
        mock_get_user.return_value = {'admin_flag': 'Y'}
        mock_user_info.return_value = {'admin_flag': 'Y'}
        self._setup_admin_session()
        mock_work.return_value = {'url': 'http://example.com'}
        
        response = self.client.get('/admin/work-log')
        if response.status_code == 200:
            result.pass_test("작업 로그 페이지가 정상 응답합니다.")
        else:
            result.fail_test(f"잘못된 응답 코드: {response.status_code}")

    # =========================================================================
    # 리포트 생성
    # =========================================================================

    def _print_final_report(self):
        print("\n" + "=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)

        status_counts = {status: 0 for status in TestStatus}
        for result in self.results:
            status_counts[result.status] += 1

        total = len(self.results)
        passed = status_counts[TestStatus.PASSED]
        failed = status_counts[TestStatus.FAILED]

        print(f"\n총 테스트: {total}개")
        print(f"{TestStatus.PASSED.value} 통과: {passed}개")
        print(f"{TestStatus.FAILED.value} 실패: {failed}개")

        self._save_json_report()

        return 0 if failed == 0 else 1

    def _save_json_report(self):
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'summary': {
                'passed': sum(1 for r in self.results if r.status == TestStatus.PASSED),
                'failed': sum(1 for r in self.results if r.status == TestStatus.FAILED),
            },
            'tests': [
                {
                    'name': r.test_name,
                    'category': r.category,
                    'status': r.status.name,
                    'message': r.message,
                    'duration': r.get_duration(),
                    'details': r.details,
                }
                for r in self.results
            ]
        }

        report_path = project_root / 'test' / f'admin_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        if os.environ.get('SNOWBALL_KEEP_REPORT') != '1':
            try:
                os.remove(report_path)
            except:
                pass

def main():
    suite = AdminTestSuite()
    sys.exit(suite.run_all_tests())

if __name__ == '__main__':
    main()
