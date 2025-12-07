#!/bin/bash
# 🍪 Cookie 학습 시뮬레이션 실행 스크립트

# 경로 설정
PROJECT_ROOT="/Users/jazzin/Desktop/babyhippo-release"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🍪 Cookie 학습 시뮬레이션 실행 스크립트                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 옵션 확인
if [ "$1" == "simple" ] || [ -z "$1" ]; then
    echo -e "${GREEN}1️⃣ 간단한 데모 실행${NC}"
    echo ""
    python3 "$PROJECT_ROOT/examples/07_simple_learning_demo.py"
elif [ "$1" == "full" ]; then
    echo -e "${GREEN}2️⃣ 전체 시뮬레이션 실행${NC}"
    echo ""
    python3 "$PROJECT_ROOT/examples/06_cookie_learning_simulation.py"
elif [ "$1" == "interactive" ]; then
    echo -e "${GREEN}3️⃣ 대화형 인터페이스 실행${NC}"
    echo ""
    python3 "$PROJECT_ROOT/examples/05_cookie_interactive.py"
else
    echo -e "${YELLOW}사용법:${NC}"
    echo "  ./run_cookie_demo.sh [simple|full|interactive]"
    echo ""
    echo "  simple      - 간단한 데모 (기본값)"
    echo "  full        - 전체 시뮬레이션"
    echo "  interactive - 대화형 인터페이스"
fi

