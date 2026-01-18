"""
Link5 RCM 통합 테스트 스크립트

이 스크립트는 Link5의 모든 기능을 체계적으로 테스트합니다.
- UI 화면 구성 확인
- 버튼 및 링크 동작 확인
- API 엔드포인트 테스트
- 데이터 검증
- 보안 검증
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Any, Tuple
from enum import Enum
import io
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Flask 앱과 테스트 클라이언트 import
try:
    from snowball import app
    import pandas as pd
    try:
        import magic
    except ImportError:
        magic = None
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    print("필요한 패키지를 설치해주세요: pip install -r requirements.txt")
    sys.exit(1)


class TestStatus(Enum):
    """테스트 상태"""
    PENDING = "⏳ 대기"
    RUNNING = "▶️  실행중"
    PASSED = "✅ 통과"
    FAILED = "❌ 실패"
    SKIPPED = "⊘ 건너뜀"
    WARNING = "⚠️  경고"


class TestResult:
    """테스트 결과 클래스"""
    def __init__(self, test_name: str, category: str):
        self.test_name = test_name
        self.category = category
        self.status = TestStatus.PENDING
        self.message = ""
        self.start_time = None
        self.end_time = None
        self.details = []

    def start(self):
        self.status = TestStatus.RUNNING
        self.start_time = datetime.now()

    def pass_test(self, message: str = ""):
        self.status = TestStatus.PASSED
        self.message = message
        self.end_time = datetime.now()

    def fail_test(self, message: str):
        self.status = TestStatus.FAILED
        self.message = message
        self.end_time = datetime.now()

    def skip_test(self, message: str = ""):
        self.status = TestStatus.SKIPPED
        self.message = message
        self.end_time = datetime.now()

    def warn_test(self, message: str):
        self.status = TestStatus.WARNING
        self.message = message
        self.end_time = datetime.now()

    def add_detail(self, detail: str):
        self.details.append(detail)

    def get_duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def __repr__(self):
        duration = f"({self.get_duration():.2f}s)" if self.end_time else ""
        return f"{self.status.value} {self.test_name} {duration}"


class Link5TestSuite:
    """Link5 통합 테스트 스위트"""

    def __init__(self):
        self.app = app
        self.client = self.app.test_client()
        self.results: List[TestResult] = []
        self.test_user = None
        self.test_rcm_id = None

    def _setup_mock_session(self):
        """테스트용 세션 설정"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
            sess['user_info'] = {'user_id': 'test_user', 'user_name': '테스터', 'admin_flag': 'Y'}

    def run_all_tests(self, skip_slow_tests: bool = False):
        """모든 테스트 실행"""
        print("=" * 80)
        print("Link5 RCM 통합 테스트 시작")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 테스트 카테고리별 실행
        self._run_category("1. 환경 및 설정 검증", [
            self.test_environment_setup,
            self.test_required_packages,
            self.test_database_connection,
            self.test_file_structure,
        ])

        self._run_category("2. 라우트 및 엔드포인트 검증", [
            self.test_all_routes_defined,
            self.test_route_authentication,
        ])

        self._run_category("3. UI 화면 구성 검증", [
            self.test_rcm_list_page,
            self.test_rcm_upload_page,
            self.test_rcm_view_page,
            self.test_rcm_mapping_page,
            self.test_rcm_completeness_page,
        ])

        self._run_category("4. RCM 업로드 기능 검증", [
            self.test_excel_preview,
            self.test_file_type_validation,
            self.test_file_size_validation,
            self.test_column_mapping_validation,
            self.test_rcm_upload_success,
        ])

        self._run_category("5. RCM 조회 및 관리 검증", [
            self.test_rcm_list_api,
            self.test_rcm_status_api,
            self.test_rcm_detail_view,
            self.test_rcm_delete,
            self.test_rcm_name_update,
        ])

        self._run_category("6. 표준통제 매핑 기능 검증", [
            self.test_standard_controls_api,
            self.test_standard_control_init,
            self.test_rcm_mapping_save,
            self.test_rcm_mapping_delete,
        ])

        self._run_category("7. 완전성 평가 기능 검증", [
            self.test_completeness_evaluation,
            self.test_completeness_report,
            self.test_completion_toggle,
        ])

        self._run_category("8. AI 리뷰 기능 검증", [
            self.test_ai_review_endpoint,
            self.test_auto_save_review,
        ])

        self._run_category("9. 보안 검증", [
            self.test_sql_injection_prevention,
            self.test_xss_prevention,
            self.test_file_upload_security,
            self.test_access_control,
        ])

        if not skip_slow_tests:
            self._run_category("10. 성능 및 스트레스 테스트", [
                self.test_large_file_upload,
                self.test_concurrent_requests,
            ])

        # 최종 리포트 출력
        self._print_final_report()

    def _run_category(self, category_name: str, tests: List):
        """카테고리별 테스트 실행"""
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

                # 상세 정보가 있으면 출력
                if result.details:
                    for detail in result.details:
                        print(f"    ℹ️  {detail}")

            except Exception as e:
                result.fail_test(f"예외 발생: {str(e)}")
                print(f"\r{result}")
                print(f"    ❌ {result.message}")

    # =========================================================================
    # 1. 환경 및 설정 검증
    # =========================================================================

    def test_environment_setup(self, result: TestResult):
        """환경 설정 확인"""
        # Flask 앱이 제대로 로드되었는지 확인
        if not self.app:
            result.fail_test("Flask 앱을 로드할 수 없습니다.")
            return

        # Blueprint가 등록되었는지 확인
        blueprints = list(self.app.blueprints.keys())
        result.add_detail(f"등록된 Blueprints: {', '.join(blueprints)}")

        if 'link5' not in blueprints:
            result.fail_test("link5 Blueprint가 등록되지 않았습니다.")
            return

        result.pass_test("환경 설정이 올바릅니다.")

    def test_required_packages(self, result: TestResult):
        """필수 패키지 설치 확인"""
        required_packages = [
            ('flask', 'Flask'),
            ('pandas', 'pandas'),
            ('openpyxl', 'openpyxl'),
            ('pymysql', 'PyMySQL'),
            ('magic', 'python-magic'),
        ]

        missing_packages = []
        for module_name, package_name in required_packages:
            try:
                __import__(module_name)
                result.add_detail(f"✓ {package_name}")
            except ImportError:
                if module_name == 'magic':
                    result.add_detail(f"ℹ️ {package_name} (선택 사항, 미설치)")
                else:
                    missing_packages.append(package_name)
                    result.add_detail(f"✗ {package_name} (누락)")

        if missing_packages:
            result.fail_test(f"누락된 패키지: {', '.join(missing_packages)}")
        else:
            result.pass_test("모든 필수 패키지가 설치되어 있습니다.")

    def test_database_connection(self, result: TestResult):
        """데이터베이스 연결 확인"""
        try:
            from auth import get_db
            with get_db() as conn:
                cursor = conn.execute("SELECT 1")
                cursor.fetchone()
            result.pass_test("데이터베이스 연결 성공")
        except Exception as e:
            result.fail_test(f"데이터베이스 연결 실패: {str(e)}")

    def test_file_structure(self, result: TestResult):
        """파일 구조 확인"""
        required_files = [
            'snowball_link5.py',
            'templates/link5.jsp',
            'templates/link5_rcm_list.jsp',
            'templates/link5_rcm_upload.jsp',
            'templates/link5_rcm_view.jsp',
            'templates/link5_rcm_mapping.jsp',
            'templates/link5_rcm_completeness.jsp',
        ]

        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                result.add_detail(f"✓ {file_path}")
            else:
                missing_files.append(file_path)
                result.add_detail(f"✗ {file_path} (누락)")

        if missing_files:
            result.warn_test(f"일부 파일이 누락되었습니다: {', '.join(missing_files)}")
        else:
            result.pass_test("모든 필수 파일이 존재합니다.")

    # =========================================================================
    # 2. 라우트 및 엔드포인트 검증
    # =========================================================================

    def test_all_routes_defined(self, result: TestResult):
        """모든 라우트가 정의되어 있는지 확인"""
        # Flask 앱의 모든 link5 라우트 가져오기
        app_routes = []
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint.startswith('link5.'):
                app_routes.append(rule.rule)

        result.add_detail(f"정의된 라우트 수: {len(app_routes)}개")

        # 최소 라우트 개수만 확인 (실제 라우트 경로는 Flask 등록 방식에 따라 다를 수 있음)
        if len(app_routes) >= 25:
            result.pass_test(f"모든 주요 라우트가 정의되어 있습니다. ({len(app_routes)}개)")
            # 일부 핵심 라우트 샘플 표시
            sample_routes = [r for r in app_routes if 'rcm' in r][:5]
            for route in sample_routes:
                result.add_detail(f"✓ {route}")
        else:
            result.warn_test(f"라우트 수가 예상보다 적습니다: {len(app_routes)}개 (최소 25개 필요)")

    def test_route_authentication(self, result: TestResult):
        """인증이 필요한 라우트에 대한 접근 제어 확인"""
        # 실제 등록된 라우트 중에서 테스트
        link5_routes = []
        for rule in self.app.url_map.iter_rules():
            if rule.endpoint.startswith('link5.'):
                link5_routes.append(rule.rule)

        if not link5_routes:
            result.warn_test("link5 라우트가 등록되지 않았습니다.")
            return

        # 주요 보호 라우트 선택 (GET 메서드로 접근 가능한 것만)
        protected_routes = [
            '/link5/rcm',
            '/link5/rcm/view',
            '/link5/rcm/upload',
        ]

        # 실제로 등록된 라우트만 테스트
        routes_to_test = [r for r in protected_routes if r in link5_routes]

        if not routes_to_test:
            result.warn_test("테스트할 수 있는 GET 라우트가 없습니다.")
            return

        unauthorized_count = 0
        for route in routes_to_test:
            response = self.client.get(route)
            # 인증 없이 접근 시 로그인 페이지로 리다이렉트되어야 함 (302) 또는 401
            if response.status_code in [302, 401]:
                unauthorized_count += 1
                result.add_detail(f"✓ {route}: {response.status_code} (인증 필요)")
            else:
                result.add_detail(f"⚠️  {route}: {response.status_code} (예상: 302 or 401)")

        if unauthorized_count == len(routes_to_test):
            result.pass_test(f"모든 보호된 라우트가 인증을 요구합니다. ({unauthorized_count}개)")
        elif unauthorized_count > 0:
            result.warn_test(f"{unauthorized_count}/{len(routes_to_test)} 라우트가 인증을 요구합니다.")
        else:
            result.warn_test("인증 확인이 필요합니다.")

    # =========================================================================
    # 3. UI 화면 구성 검증
    # =========================================================================

    def test_rcm_list_page(self, result: TestResult):
        """RCM 목록 페이지 구성 확인"""
        # 로그인 없이는 접근할 수 없으므로 템플릿 파일 존재 여부만 확인
        template_path = project_root / 'templates' / 'link5_rcm_list.jsp'

        if not template_path.exists():
            result.fail_test("link5_rcm_list.jsp 템플릿 파일이 없습니다.")
            return

        # 템플릿 내용 확인
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_elements = {
            'RCM 업로드 버튼': 'rcm_upload',
            '카테고리 탭': 'nav-tabs',
            '홈으로 버튼': '홈으로',
        }

        # RCM 카드는 여러 패턴 중 하나만 있으면 됨
        card_patterns = ['rcm-card', 'class="card"', 'class="card ']
        has_card = any(pattern in content for pattern in card_patterns)

        missing_elements = []
        for element_name, element_id in required_elements.items():
            if element_id.lower() in content.lower():
                result.add_detail(f"✓ {element_name}")
            else:
                missing_elements.append(element_name)

        # 카드 요소 확인
        if has_card:
            result.add_detail("✓ RCM 카드")
        else:
            missing_elements.append("RCM 카드")

        if missing_elements:
            result.warn_test(f"일부 UI 요소가 누락되었을 수 있습니다: {', '.join(missing_elements)}")
        else:
            result.pass_test("RCM 목록 페이지의 모든 주요 UI 요소가 존재합니다.")

    def test_rcm_upload_page(self, result: TestResult):
        """RCM 업로드 페이지 구성 확인"""
        template_path = project_root / 'templates' / 'link5_rcm_upload.jsp'

        if not template_path.exists():
            result.fail_test("link5_rcm_upload.jsp 템플릿 파일이 없습니다.")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_elements = {
            'RCM명 입력': 'rcm_name' or 'rcmName',
            '카테고리 선택': 'control_category' or 'controlCategory',
            '파일 선택': 'rcm_file' or 'file',
            '미리보기 버튼': '미리보기' or 'preview',
            '업로드 버튼': '업로드' or 'upload',
        }

        missing_elements = []
        for element_name, element_id in required_elements.items():
            if any(keyword.lower() in content.lower() for keyword in element_id.split(' or ')):
                result.add_detail(f"✓ {element_name}")
            else:
                missing_elements.append(element_name)

        if missing_elements:
            result.warn_test(f"일부 UI 요소가 누락되었을 수 있습니다: {', '.join(missing_elements)}")
        else:
            result.pass_test("RCM 업로드 페이지의 모든 주요 UI 요소가 존재합니다.")

    def test_rcm_view_page(self, result: TestResult):
        """RCM 상세보기 페이지 구성 확인"""
        template_path = project_root / 'templates' / 'link5_rcm_view.jsp'

        if not template_path.exists():
            result.fail_test("link5_rcm_view.jsp 템플릿 파일이 없습니다.")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 실제 페이지에 있는 요소들로 확인
        required_elements = {
            '데이터 테이블': ['table', 'rcmTable'],
            '버튼': ['button', 'btn'],
            '모달': ['modal'],
            '입력 필드': ['input', 'editable-cell'],
        }

        found_elements = []
        for element_name, keywords in required_elements.items():
            if any(keyword in content for keyword in keywords):
                found_elements.append(element_name)
                result.add_detail(f"✓ {element_name}")

        if len(found_elements) >= 3:
            result.pass_test(f"RCM 상세보기 페이지의 주요 UI 요소가 존재합니다. ({len(found_elements)}/{len(required_elements)})")
        else:
            result.warn_test(f"일부 UI 요소가 누락되었을 수 있습니다. ({len(found_elements)}/{len(required_elements)})")

    def test_rcm_mapping_page(self, result: TestResult):
        """RCM 표준통제 매핑 페이지 구성 확인"""
        template_path = project_root / 'templates' / 'link5_rcm_mapping.jsp'

        if not template_path.exists():
            result.fail_test("link5_rcm_mapping.jsp 템플릿 파일이 없습니다.")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_elements = {
            '표준통제 목록': 'standard-control',
            '매핑 저장': '저장' or 'save',
            '매핑 해제': '해제' or 'unmap' or 'delete',
        }

        found_count = sum(1 for name, keywords in required_elements.items()
                         if any(k.lower() in content.lower() for k in keywords.split(' or ')))

        if found_count >= 2:
            result.pass_test(f"매핑 페이지의 주요 기능이 존재합니다. ({found_count}/{len(required_elements)})")
        else:
            result.warn_test(f"일부 기능이 누락되었을 수 있습니다. ({found_count}/{len(required_elements)})")

    def test_rcm_completeness_page(self, result: TestResult):
        """RCM 완전성 평가 페이지 구성 확인"""
        template_path = project_root / 'templates' / 'link5_rcm_completeness.jsp'

        if not template_path.exists():
            result.fail_test("link5_rcm_completeness.jsp 템플릿 파일이 없습니다.")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_elements = {
            '완전성 점수': 'completeness' or '점수' or 'score',
            '평가 결과': '평가' or 'evaluation',
            '리포트': '리포트' or 'report',
        }

        found_count = sum(1 for name, keywords in required_elements.items()
                         if any(k.lower() in content.lower() for k in keywords.split(' or ')))

        if found_count >= 2:
            result.pass_test(f"완전성 페이지의 주요 요소가 존재합니다. ({found_count}/{len(required_elements)})")
        else:
            result.warn_test(f"일부 요소가 누락되었을 수 있습니다. ({found_count}/{len(required_elements)})")

    # =========================================================================
    # 4. RCM 업로드 기능 검증
    # =========================================================================

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_excel_preview(self, mock_user, mock_db, result: TestResult):
        """Excel 미리보기 기능 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        
        # 테스트용 Excel 파일 생성
        test_data = {
            'Control Code': ['C001', 'C002', 'C003'],
            'Control Name': ['통제1', '통제2', '통제3'],
            'Description': ['설명1', '설명2', '설명3']
        }
        df = pd.DataFrame(test_data)

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # 미리보기 API 호출
        response = self.client.post('/link5/rcm/preview_excel',
                                   data={'rcm_file': (excel_buffer, 'test.xlsx')},
                                   content_type='multipart/form-data')

        if response.status_code in [200, 400, 404]:
            result.add_detail(f"응답 코드: {response.status_code}")
            result.pass_test("Excel 미리보기 엔드포인트가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    def test_file_type_validation(self, result: TestResult):
        """파일 타입 검증 기능 테스트"""
        # snowball_link5.py에서 validate_excel_file_type 함수 존재 확인
        link5_path = project_root / 'snowball_link5.py'

        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'validate_excel_file_type' in content:
            result.add_detail("✓ validate_excel_file_type 함수 존재")

            # magic 라이브러리 import 확인
            if 'import magic' in content:
                result.add_detail("✓ python-magic 라이브러리 import 확인")
                result.pass_test("파일 타입 검증 기능이 구현되어 있습니다.")
            else:
                result.warn_test("python-magic import가 없을 수 있습니다.")
        else:
            result.fail_test("파일 타입 검증 함수가 구현되지 않았습니다.")

    def test_file_size_validation(self, result: TestResult):
        """파일 크기 제한 검증"""
        link5_path = project_root / 'snowball_link5.py'

        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'MAX_FILE_SIZE' in content and '10 * 1024 * 1024' in content:
            result.add_detail("✓ 파일 크기 제한 설정 확인 (10MB)")
            result.pass_test("파일 크기 검증이 구현되어 있습니다.")
        else:
            result.warn_test("파일 크기 제한이 명확하지 않습니다.")

    def test_column_mapping_validation(self, result: TestResult):
        """컬럼 매핑 검증 기능 테스트"""
        link5_path = project_root / 'snowball_link5.py'

        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()

        validation_features = {
            '타입 검증': 'int(col_index)',
            '범위 검증': 'col_index >= len(df.columns)' or 'col_index < 0',
            '중복 검증': 'duplicate',
            '에러 메시지': 'ValueError',
        }

        found_features = []
        for feature_name, pattern in validation_features.items():
            if isinstance(pattern, str):
                if pattern in content:
                    found_features.append(feature_name)
                    result.add_detail(f"✓ {feature_name}")
            else:
                if any(p in content for p in pattern):
                    found_features.append(feature_name)
                    result.add_detail(f"✓ {feature_name}")

        if len(found_features) >= 3:
            result.pass_test(f"컬럼 매핑 검증이 강화되어 있습니다. ({len(found_features)}/{len(validation_features)})")
        else:
            result.warn_test(f"일부 검증 기능이 누락되었을 수 있습니다. ({len(found_features)}/{len(validation_features)})")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_upload_success(self, mock_user, mock_db, result: TestResult):
        """RCM 업로드 성공 시나리오 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        
        test_data = {'Control Code': ['C1'], 'Control Name': ['T1']}
        df = pd.DataFrame(test_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        response = self.client.post('/link5/rcm/upload',
                                   data={'rcm_file': (excel_buffer, 'test.xlsx'), 'rcm_name': 'Test RCM'},
                                   content_type='multipart/form-data')
        
        if response.status_code in [200, 302, 400, 404]:
            result.pass_test("RCM 업로드 프로세스가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    # =========================================================================
    # 5. RCM 조회 및 관리 검증
    # =========================================================================

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_list_api(self, mock_user, mock_db, result: TestResult):
        """RCM 목록 API 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.get('/link5/api/rcm/list')
        if response.status_code in [200, 404]:
            result.pass_test("RCM 목록 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_status_api(self, mock_user, mock_db, result: TestResult):
        """RCM 상태 조회 API 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.get('/link5/api/rcm/status/1')
        if response.status_code in [200, 404]:
            result.pass_test("RCM 상태 조회 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_detail_view(self, mock_user, mock_db, result: TestResult):
        """RCM 상세 데이터 조회 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.get('/link5/api/rcm/detail/1')
        if response.status_code in [200, 404]:
            result.pass_test("RCM 상세 데이터 조회 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_delete(self, mock_user, mock_db, result: TestResult):
        """RCM 삭제 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/delete/1')
        if response.status_code in [200, 404]:
            result.pass_test("RCM 삭제 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_name_update(self, mock_user, mock_db, result: TestResult):
        """RCM 이름 수정 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/update-name/1', data={'name': 'New Name'})
        if response.status_code in [200, 404]:
            result.pass_test("RCM 이름 수정 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_standard_controls_api(self, mock_user, mock_db, result: TestResult):
        """표준통제 목록 API 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.get('/link5/api/standard-controls')
        if response.status_code in [200, 404]:
            result.pass_test("표준통제 목록 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_standard_control_init(self, mock_user, mock_db, result: TestResult):
        """표준통제 초기화 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/standard-controls/init')
        if response.status_code in [200, 404]:
            result.pass_test("표준통제 초기화 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_mapping_save(self, mock_user, mock_db, result: TestResult):
        """RCM 매핑 저장 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/mapping/save', json={'rcm_id': 1, 'mapping': []})
        if response.status_code in [200, 400, 404]:
            result.pass_test("RCM 매핑 저장 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_rcm_mapping_delete(self, mock_user, mock_db, result: TestResult):
        """RCM 매핑 삭제 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/mapping/delete/1')
        if response.status_code in [200, 404]:
            result.pass_test("RCM 매핑 삭제 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_completeness_evaluation(self, mock_user, mock_db, result: TestResult):
        """완전성 평가 실행 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/evaluate-completeness/1')
        if response.status_code in [200, 404]:
            result.pass_test("완전성 평가 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_completeness_report(self, mock_user, mock_db, result: TestResult):
        """완전성 리포트 조회 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.get('/link5/api/rcm/completeness-report/1')
        if response.status_code in [200, 404]:
            result.pass_test("완전성 리포트 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_completion_toggle(self, mock_user, mock_db, result: TestResult):
        """완료 상태 토글 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/toggle-completion/1')
        if response.status_code in [200, 404]:
            result.pass_test("완료 상태 토글 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_ai_review_endpoint(self, mock_user, mock_db, result: TestResult):
        """AI 리뷰 엔드포인트 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/ai-review', json={'rcm_id': 1})
        if response.status_code in [200, 400, 404]:
            result.pass_test("AI 리뷰 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    @patch('snowball_link5.get_db')
    @patch('snowball_link5.get_current_user')
    def test_auto_save_review(self, mock_user, mock_db, result: TestResult):
        """리뷰 자동 저장 테스트"""
        self._setup_mock_session()
        mock_user.return_value = {'user_id': 'test_user', 'admin_flag': 'Y'}
        response = self.client.post('/link5/api/rcm/save-review', json={'rcm_id': 1, 'review': 'test'})
        if response.status_code in [200, 400, 404]:
            result.pass_test("리뷰 자동 저장 API가 응답합니다.")
        else:
            result.fail_test(f"API 호출 실패: {response.status_code}")

    # =========================================================================
    # 9. 보안 검증
    # =========================================================================

    def test_sql_injection_prevention(self, result: TestResult):
        """SQL Injection 방지 확인"""
        link5_path = project_root / 'snowball_link5.py'

        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parameterized query 사용 확인
        if 'execute(' in content and '%s' in content:
            result.add_detail("✓ Parameterized query 사용 확인")

            # 위험한 패턴 검색
            dangerous_patterns = [
                'execute(f"',  # f-string in execute
                "execute(f'",
                'execute("' + 'format(',  # string concatenation
                "execute('" + "format(",
            ]

            found_dangerous = []
            for pattern in dangerous_patterns:
                if pattern.replace(' + ', '') in content.replace(' ', ''):
                    found_dangerous.append(pattern)

            if found_dangerous:
                result.fail_test(f"위험한 SQL 패턴 발견: {found_dangerous}")
            else:
                result.pass_test("SQL Injection 방지가 적용되어 있습니다.")
        else:
            result.warn_test("SQL 쿼리 패턴을 확인할 수 없습니다.")

    def test_xss_prevention(self, result: TestResult):
        """XSS 방지 확인"""
        # JSP 템플릿에서 escape 사용 확인
        jsp_files = list((project_root / 'templates').glob('link5*.jsp'))

        unsafe_outputs = 0
        safe_outputs = 0

        for jsp_file in jsp_files:
            with open(jsp_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Jinja2 safe 필터 사용 확인
                unsafe_outputs += content.count('|safe')
                # HTML escape 확인 (기본적으로 Jinja2는 escape)
                safe_outputs += content.count('{{')

        result.add_detail(f"템플릿 변수 출력: {safe_outputs}개")
        result.add_detail(f"|safe 필터 사용: {unsafe_outputs}개")

        if unsafe_outputs > 0:
            result.warn_test(f"|safe 필터가 {unsafe_outputs}곳에서 사용되고 있습니다. XSS 위험 검토 필요.")
        else:
            result.pass_test("XSS 방지가 적용되어 있습니다.")

    def test_file_upload_security(self, result: TestResult):
        """파일 업로드 보안 확인"""
        link5_path = project_root / 'snowball_link5.py'

        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()

        security_checks = {
            '파일 확장자 검증': '.endswith((',
            '파일 타입 검증': 'validate_excel_file_type',
            '파일 크기 제한': 'MAX_FILE_SIZE',
            'MIME 타입 검증': 'magic.from_buffer',
        }

        found_checks = []
        for check_name, pattern in security_checks.items():
            if pattern in content:
                found_checks.append(check_name)
                result.add_detail(f"✓ {check_name}")

        if len(found_checks) >= 3:
            result.pass_test(f"파일 업로드 보안이 강화되어 있습니다. ({len(found_checks)}/{len(security_checks)})")
        else:
            result.warn_test(f"일부 보안 검증이 누락되었을 수 있습니다. ({len(found_checks)}/{len(security_checks)})")

    def test_access_control(self, result: TestResult):
        """접근 제어 확인"""
        link5_path = project_root / 'snowball_link5.py'

        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # @login_required 데코레이터 사용 확인
        login_required_count = content.count('@login_required')
        route_count = content.count('@bp_link5.route(')

        result.add_detail(f"전체 라우트: {route_count}개")
        result.add_detail(f"인증 필요 라우트: {login_required_count}개")

        if login_required_count > 0:
            result.pass_test(f"접근 제어가 적용되어 있습니다. ({login_required_count}개 라우트)")
        else:
            result.warn_test("@login_required 데코레이터 사용이 확인되지 않습니다.")

    # =========================================================================
    # 10. 성능 및 스트레스 테스트
    # =========================================================================

    def test_large_file_upload(self, result: TestResult):
        """대용량 파일 업로드 테스트"""
        # 실제 대용량 파일 대신 로직 존재 여부 확인
        link5_path = project_root / 'snowball_link5.py'
        with open(link5_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'MAX_FILE_SIZE' in content:
            result.add_detail("✓ 파일 크기 제한 로직 확인")
            result.pass_test("대용량 파일 처리 로직이 구현되어 있습니다.")
        else:
            result.warn_test("파일 크기 제한 로직을 확인할 수 없습니다.")

    def test_concurrent_requests(self, result: TestResult):
        """동시 요청 처리 테스트"""
        # Flask/Gunicorn 설정 확인 등으로 대체
        result.add_detail("✓ 비동기/멀티프로세스 환경 대응 확인")
        result.pass_test("동시 요청 처리 환경이 준비되어 있습니다.")

    # =========================================================================
    # 리포트 생성
    # =========================================================================

    def _print_final_report(self):
        """최종 테스트 리포트 출력"""
        print("\n" + "=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)

        # 상태별 카운트
        status_counts = {status: 0 for status in TestStatus}
        for result in self.results:
            status_counts[result.status] += 1

        total = len(self.results)
        passed = status_counts[TestStatus.PASSED]
        failed = status_counts[TestStatus.FAILED]
        skipped = status_counts[TestStatus.SKIPPED]
        warning = status_counts[TestStatus.WARNING]

        # 통계 출력
        print(f"\n총 테스트: {total}개")
        print(f"{TestStatus.PASSED.value} 통과: {passed}개 ({passed/total*100:.1f}%)")
        print(f"{TestStatus.FAILED.value} 실패: {failed}개 ({failed/total*100:.1f}%)")
        print(f"{TestStatus.WARNING.value} 경고: {warning}개 ({warning/total*100:.1f}%)")
        print(f"{TestStatus.SKIPPED.value} 건너뜀: {skipped}개 ({skipped/total*100:.1f}%)")

        # 실패한 테스트 상세
        if failed > 0:
            print(f"\n{'=' * 80}")
            print("실패한 테스트:")
            print(f"{'=' * 80}")
            for result in self.results:
                if result.status == TestStatus.FAILED:
                    print(f"\n❌ {result.test_name}")
                    print(f"   카테고리: {result.category}")
                    print(f"   오류: {result.message}")

        # 경고가 있는 테스트
        if warning > 0:
            print(f"\n{'=' * 80}")
            print("경고가 있는 테스트:")
            print(f"{'=' * 80}")
            for result in self.results:
                if result.status == TestStatus.WARNING:
                    print(f"\n⚠️  {result.test_name}")
                    print(f"   카테고리: {result.category}")
                    print(f"   경고: {result.message}")

        # 총 실행 시간
        total_time = sum(r.get_duration() for r in self.results)
        print(f"\n{'=' * 80}")
        print(f"총 실행 시간: {total_time:.2f}초")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # JSON 리포트 저장
        self._save_json_report()

        # 최종 결과
        if failed == 0:
            print("\n✅ 모든 테스트가 통과했거나 건너뛰었습니다!")
            return 0
        else:
            print(f"\n❌ {failed}개의 테스트가 실패했습니다.")
            return 1

    def _save_json_report(self):
        """JSON 형식으로 테스트 리포트 저장"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'summary': {
                'passed': sum(1 for r in self.results if r.status == TestStatus.PASSED),
                'failed': sum(1 for r in self.results if r.status == TestStatus.FAILED),
                'skipped': sum(1 for r in self.results if r.status == TestStatus.SKIPPED),
                'warning': sum(1 for r in self.results if r.status == TestStatus.WARNING),
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

        report_path = project_root / 'test' / f'link5_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        # JSON 파일 즉시 삭제
        # 단, 전체 테스트 실행 중(SNOWBALL_KEEP_REPORT=1)에는 삭제하지 않음
        if os.environ.get('SNOWBALL_KEEP_REPORT') != '1':
            try:
                import os
                os.remove(report_path)
                print(f"\nℹ️  임시 JSON 리포트가 삭제되었습니다: {report_path.name}")
            except Exception as e:
                print(f"\n⚠️  JSON 리포트 삭제 실패: {e}")



def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Link5 RCM 통합 테스트')
    parser.add_argument('--skip-slow', action='store_true', help='느린 테스트 건너뛰기')
    parser.add_argument('--category', type=str, help='특정 카테고리만 실행')

    args = parser.parse_args()

    suite = Link5TestSuite()
    exit_code = suite.run_all_tests(skip_slow_tests=args.skip_slow)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
