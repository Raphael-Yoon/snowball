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

# ================================
# 사용자 전환 API 테스트
# ================================

def test_api_get_users_requires_login(client):
    """로그인하지 않은 경우 사용자 목록 조회 불가"""
    response = client.get('/admin/api/admin/users')
    # 로그인 페이지로 리다이렉트되어야 함
    assert response.status_code in [302, 401]

def test_api_get_users_requires_admin(client, auth):
    """일반 사용자는 사용자 목록 조회 불가"""
    # 일반 사용자로 로그인
    auth.login('user@samil.com', 'test1234!')

    response = client.get('/admin/api/admin/users')
    data = json.loads(response.data)

    assert data['success'] == False
    assert '관리자 권한' in data['message']

def test_api_get_users_success(client, auth):
    """관리자는 사용자 목록 조회 가능"""
    # 관리자로 로그인
    auth.login('admin@snowball.com', 'test1234!')

    response = client.get('/admin/api/admin/users')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['success'] == True
    assert 'users' in data
    assert isinstance(data['users'], list)

    # 최소 2명 이상의 사용자가 있어야 함 (admin, user)
    assert len(data['users']) >= 2

    # 각 사용자는 필수 필드를 가져야 함
    for user in data['users']:
        assert 'user_id' in user
        assert 'user_email' in user
        assert 'company_name' in user
        assert 'admin_flag' in user

def test_api_switch_user_requires_login(client):
    """로그인하지 않은 경우 사용자 전환 불가"""
    response = client.post('/admin/api/admin/switch-user',
                          json={'user_id': 'user001'})
    # 로그인 페이지로 리다이렉트되어야 함
    assert response.status_code in [302, 401]

def test_api_switch_user_requires_admin(client, auth):
    """일반 사용자는 다른 사용자로 전환 불가"""
    # 일반 사용자로 로그인
    auth.login('user@samil.com', 'test1234!')

    response = client.post('/admin/api/admin/switch-user',
                          json={'user_id': 'admin001'})
    data = json.loads(response.data)

    assert data['success'] == False
    assert '관리자 권한' in data['message']

def test_api_switch_user_requires_user_id(client, auth):
    """사용자 ID가 없으면 전환 실패"""
    # 관리자로 로그인
    auth.login('admin@snowball.com', 'test1234!')

    response = client.post('/admin/api/admin/switch-user',
                          json={})
    data = json.loads(response.data)

    assert data['success'] == False
    assert 'ID가 필요' in data['message']

def test_api_switch_user_invalid_user(client, auth):
    """존재하지 않는 사용자로 전환 불가"""
    # 관리자로 로그인
    auth.login('admin@snowball.com', 'test1234!')

    response = client.post('/admin/api/admin/switch-user',
                          json={'user_id': 'nonexistent999'})
    data = json.loads(response.data)

    assert data['success'] == False
    assert '존재하지 않는 사용자' in data['message']

def test_api_switch_user_success(client, auth):
    """관리자가 다른 사용자로 전환 성공"""
    # 관리자로 로그인
    auth.login('admin@snowball.com', 'test1234!')

    # 먼저 사용자 목록 조회
    response = client.get('/admin/api/admin/users')
    data = json.loads(response.data)
    users = data['users']

    # 관리자가 아닌 일반 사용자 찾기
    target_user = next((u for u in users if u['admin_flag'] != 'Y'), None)
    assert target_user is not None

    # 사용자 전환
    response = client.post('/admin/api/admin/switch-user',
                          json={'user_id': target_user['user_id']})
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['success'] == True
    assert target_user['company_name'] in data['message']

    # 세션에 original_admin_id가 저장되었는지 확인
    with client.session_transaction() as sess:
        assert 'original_admin_id' in sess
        assert sess['user_id'] == target_user['user_id']

def test_admin_switch_back_requires_login(client):
    """로그인하지 않은 경우 관리자로 돌아가기 불가"""
    response = client.get('/admin/switch_back')
    # 로그인 페이지로 리다이렉트되어야 함
    assert response.status_code in [302, 401]

def test_admin_switch_back_without_original_admin(client, auth):
    """original_admin_id가 없는 경우"""
    # 일반 사용자로 로그인 (전환한 적 없음)
    auth.login('user@samil.com', 'test1234!')

    response = client.get('/admin/switch_back', follow_redirects=False)

    # 리다이렉트되어야 함
    assert response.status_code == 302

def test_admin_switch_back_success(client, auth):
    """관리자가 전환 후 다시 돌아오기 성공"""
    # 관리자로 로그인
    auth.login('admin@snowball.com', 'test1234!')

    # 세션에서 admin user_id 저장
    with client.session_transaction() as sess:
        admin_user_id = sess['user_id']

    # 사용자 목록 조회
    response = client.get('/admin/api/admin/users')
    data = json.loads(response.data)
    users = data['users']

    # 일반 사용자 찾기
    target_user = next((u for u in users if u['admin_flag'] != 'Y'), None)
    assert target_user is not None

    # 사용자 전환
    client.post('/admin/api/admin/switch-user',
               json={'user_id': target_user['user_id']})

    # 관리자로 돌아가기
    response = client.get('/admin/switch_back', follow_redirects=False)

    # 리다이렉트되어야 함
    assert response.status_code == 302

    # 세션에서 원래 관리자 ID로 복구되었는지 확인
    with client.session_transaction() as sess:
        assert sess['user_id'] == admin_user_id
        assert 'original_admin_id' not in sess
