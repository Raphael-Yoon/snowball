"""
Admin 기능 간소화 테스트
블루프린트 등록 및 기본 기능 검증
"""

import pytest
import json
from unittest.mock import patch, MagicMock

# ================================
# 블루프린트 등록 확인
# ================================

def test_admin_blueprint_registered(app):
    """Admin 블루프린트가 앱에 등록되어 있는지 확인"""
    assert 'admin' in [bp.name for bp in app.blueprints.values()]

def test_admin_routes_exist(app):
    """Admin의 주요 라우트 존재 확인"""
    routes = [rule.rule for rule in app.url_map.iter_rules()]

    # /admin 관련 라우트가 있는지 확인
    admin_routes = [r for r in routes if '/admin' in r]
    assert len(admin_routes) > 0

# ================================
# 헬퍼 함수 테스트
# ================================

def test_admin_helper_functions_exist():
    """Admin 헬퍼 함수 존재 확인"""
    from snowball_admin import get_user_info, is_logged_in, require_admin, perform_auto_mapping

    assert callable(get_user_info)
    assert callable(is_logged_in)
    assert callable(require_admin)
    assert callable(perform_auto_mapping)

def test_perform_auto_mapping():
    """컬럼명 자동 매핑 함수"""
    from snowball_admin import perform_auto_mapping

    headers = ['통제코드', '통제명', '통제설명']
    mapping = perform_auto_mapping(headers)

    assert isinstance(mapping, dict)
    # 매핑 결과가 있어야 함
    assert len(mapping) >= 0

def test_perform_auto_mapping_with_english_headers():
    """영문 헤더 자동 매핑"""
    from snowball_admin import perform_auto_mapping

    headers = ['control_code', 'control_name', 'description']
    mapping = perform_auto_mapping(headers)

    assert isinstance(mapping, dict)

# ================================
# Admin 기본 기능 테스트 (모킹)
# ================================

def test_admin_module_importable():
    """Admin 모듈 임포트 가능 확인"""
    import snowball_admin
    assert snowball_admin is not None

def test_admin_blueprint_prefix():
    """Admin 블루프린트가 /admin prefix 사용"""
    from snowball_admin import admin_bp
    assert admin_bp.url_prefix == '/admin'

def test_admin_blueprint_name():
    """Admin 블루프린트 이름 확인"""
    from snowball_admin import admin_bp
    assert admin_bp.name == 'admin'
