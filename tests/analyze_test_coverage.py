#!/usr/bin/env python3
"""
테스트 커버리지 분석 스크립트
누락된 테스트 항목을 식별합니다.
"""
import os
import re
from collections import defaultdict

def extract_routes_from_file(filepath):
    """파일에서 라우트 추출"""
    routes = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # @bp_xxx.route('/path') 형태 찾기
            pattern = r'@\w+\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)'
            matches = re.finditer(pattern, content)
            for match in matches:
                path = match.group(1)
                methods = match.group(2) if match.group(2) else 'GET'
                routes.append({'path': path, 'methods': methods})
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return routes

def extract_tests_from_file(filepath):
    """테스트 파일에서 테스트 함수 추출"""
    tests = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # def test_xxx 형태 찾기
            pattern = r'def (test_\w+)\('
            matches = re.finditer(pattern, content)
            for match in matches:
                tests.append(match.group(1))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return tests

def analyze_coverage():
    """커버리지 분석"""
    base_dir = '/Users/newsistraphael/Pythons/snowball'

    print("=" * 80)
    print("테스트 커버리지 분석")
    print("=" * 80)

    # 1. 각 링크별 라우트 수집
    link_routes = {}
    for i in range(1, 10):
        link_file = f'{base_dir}/snowball_link{i}.py'
        if os.path.exists(link_file):
            routes = extract_routes_from_file(link_file)
            if routes:
                link_routes[f'link{i}'] = routes

    # admin, auth, mail 등 다른 모듈도 확인
    other_modules = ['snowball_admin.py', 'auth.py', 'snowball_mail.py', 'snowball.py']
    for module in other_modules:
        filepath = f'{base_dir}/{module}'
        if os.path.exists(filepath):
            routes = extract_routes_from_file(filepath)
            if routes:
                module_name = module.replace('snowball_', '').replace('.py', '')
                link_routes[module_name] = routes

    # 2. 테스트 파일에서 테스트 수집
    test_dir = f'{base_dir}/tests'
    test_files = {}
    for filename in os.listdir(test_dir):
        if filename.startswith('test_') and filename.endswith('.py'):
            filepath = os.path.join(test_dir, filename)
            tests = extract_tests_from_file(filepath)
            if tests:
                test_files[filename] = tests

    # 3. 결과 출력
    print("\n📊 모듈별 라우트 수:")
    total_routes = 0
    for module, routes in sorted(link_routes.items()):
        print(f"  - {module}: {len(routes)}개 라우트")
        total_routes += len(routes)
    print(f"\n  총 {total_routes}개 라우트")

    print("\n📊 테스트 파일별 테스트 수:")
    total_tests = 0
    for testfile, tests in sorted(test_files.items()):
        print(f"  - {testfile}: {len(tests)}개 테스트")
        total_tests += len(tests)
    print(f"\n  총 {total_tests}개 테스트")

    # 4. 누락된 테스트 식별
    print("\n" + "=" * 80)
    print("🔍 누락된 테스트 분석")
    print("=" * 80)

    missing_tests = []

    # Link8 확인
    if 'link8' in link_routes:
        if 'test_link8_buttons.py' not in test_files:
            missing_tests.append({
                'module': 'link8',
                'issue': 'Link8 테스트 파일 자체가 없음',
                'routes': len(link_routes['link8']),
                'priority': 'HIGH'
            })

    # Auth 상세 테스트 확인
    if 'test_auth.py' in test_files:
        auth_tests = test_files['test_auth.py']
        if not any('login' in t.lower() and 'flow' in t.lower() for t in auth_tests):
            missing_tests.append({
                'module': 'auth',
                'issue': '로그인 전체 플로우 테스트 부족',
                'detail': 'OTP 전송, 검증, 세션 유지 등 통합 테스트',
                'priority': 'MEDIUM'
            })

    # RCM 관련 통합 테스트
    has_rcm_integration = any('rcm' in f.lower() and 'integration' in f.lower() for f in test_files.keys())
    if not has_rcm_integration:
        missing_tests.append({
            'module': 'integration',
            'issue': 'RCM 생성부터 운영평가까지 전체 플로우 테스트 없음',
            'detail': 'Link1(생성) → Link5(검토) → Link6(설계평가) → Link7(운영평가)',
            'priority': 'LOW'
        })

    # 에러 핸들링 테스트
    has_error_tests = any('error' in f.lower() for f in test_files.keys())
    if not has_error_tests:
        missing_tests.append({
            'module': 'error_handling',
            'issue': '에러 핸들링 전용 테스트 없음',
            'detail': '404, 500, 권한 없음 등 에러 상황 테스트',
            'priority': 'MEDIUM'
        })

    # 데이터베이스 테스트
    has_db_tests = any('database' in f.lower() or 'db' in f.lower() for f in test_files.keys())
    if not has_db_tests:
        missing_tests.append({
            'module': 'database',
            'issue': '데이터베이스 CRUD 테스트 없음',
            'detail': 'RCM, User, OperationEvaluation 등 DB 테스트',
            'priority': 'MEDIUM'
        })

    # 결과 출력
    if missing_tests:
        print(f"\n⚠️  총 {len(missing_tests)}개의 누락된 테스트 영역 발견:\n")

        # 우선순위별로 정렬
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            items = [t for t in missing_tests if t.get('priority') == priority]
            if items:
                print(f"\n[{priority} 우선순위]")
                for i, item in enumerate(items, 1):
                    print(f"{i}. 모듈: {item['module']}")
                    print(f"   문제: {item['issue']}")
                    if 'detail' in item:
                        print(f"   상세: {item['detail']}")
                    if 'routes' in item:
                        print(f"   라우트 수: {item['routes']}개")
                    print()
    else:
        print("\n✅ 주요 테스트 영역이 모두 커버되어 있습니다!")

    # 5. 상세 라우트 정보
    print("=" * 80)
    print("📋 모듈별 상세 라우트 (샘플)")
    print("=" * 80)

    for module in ['link8', 'link1', 'link5']:
        if module in link_routes:
            print(f"\n{module}:")
            for route in link_routes[module][:5]:  # 처음 5개만
                print(f"  - {route['path']} ({route['methods']})")
            if len(link_routes[module]) > 5:
                print(f"  ... 외 {len(link_routes[module]) - 5}개")

    return missing_tests

if __name__ == '__main__':
    missing = analyze_coverage()

    print("\n" + "=" * 80)
    print("💡 권장사항")
    print("=" * 80)
    print("""
1. HIGH 우선순위 항목부터 테스트 추가를 권장합니다.
2. Link8 (내부평가) 테스트를 추가하면 전체 Link 시리즈가 완성됩니다.
3. 통합 테스트는 선택사항이지만, 실제 사용자 시나리오를 검증할 수 있습니다.
4. 에러 핸들링 테스트는 프로덕션 안정성을 높여줍니다.
""")
