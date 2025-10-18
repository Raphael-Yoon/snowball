#!/bin/bash
# Snowball 테스트 자동화 실행 스크립트

echo "=================================================="
echo "  Snowball 테스트 자동화 시작"
echo "=================================================="
echo ""

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 옵션 파싱
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    "all")
        echo -e "${GREEN}[INFO]${NC} 전체 테스트 실행 중..."
        pytest -v
        ;;

    "quick")
        echo -e "${GREEN}[INFO]${NC} 빠른 테스트 실행 중 (로그 최소화)..."
        pytest --tb=short -q
        ;;

    "coverage")
        echo -e "${GREEN}[INFO]${NC} 커버리지 리포트 생성 중..."
        pytest --cov=snowball --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}[SUCCESS]${NC} 커버리지 리포트가 생성되었습니다."
        echo -e "  📊 HTML 리포트: ${YELLOW}htmlcov/index.html${NC}"
        ;;

    "auth")
        echo -e "${GREEN}[INFO]${NC} 인증 관련 테스트만 실행 중..."
        pytest tests/test_auth.py -v
        ;;

    "routes")
        echo -e "${GREEN}[INFO]${NC} 라우팅 테스트만 실행 중..."
        pytest tests/test_routes.py -v
        ;;

    "interview")
        echo -e "${GREEN}[INFO]${NC} 인터뷰 기능 테스트만 실행 중..."
        pytest tests/test_link2_interview.py -v
        ;;

    "watch")
        echo -e "${GREEN}[INFO]${NC} Watch 모드로 실행 중 (변경사항 감지)..."
        echo -e "${YELLOW}[WARNING]${NC} pytest-watch가 설치되어 있지 않으면 설치해주세요: pip install pytest-watch"
        ptw -- -v
        ;;

    "failed")
        echo -e "${GREEN}[INFO]${NC} 이전에 실패한 테스트만 재실행 중..."
        pytest --lf -v
        ;;

    *)
        echo -e "${RED}[ERROR]${NC} 알 수 없는 옵션: $TEST_TYPE"
        echo ""
        echo "사용법: $0 [옵션]"
        echo ""
        echo "옵션:"
        echo "  all        - 전체 테스트 실행 (기본값)"
        echo "  quick      - 빠른 테스트 (간단한 출력)"
        echo "  coverage   - 커버리지 리포트 생성"
        echo "  auth       - 인증 관련 테스트만"
        echo "  routes     - 라우팅 테스트만"
        echo "  interview  - 인터뷰 기능 테스트만"
        echo "  watch      - 변경사항 감지 모드"
        echo "  failed     - 실패한 테스트만 재실행"
        echo ""
        exit 1
        ;;
esac

# 테스트 결과 확인
TEST_RESULT=$?

echo ""
echo "=================================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ 모든 테스트가 성공했습니다!${NC}"
else
    echo -e "${RED}✗ 일부 테스트가 실패했습니다.${NC}"
    echo -e "  자세한 내용은 위의 출력을 확인하세요."
fi
echo "=================================================="

exit $TEST_RESULT
