#!/bin/bash
# =============================================================================
# BabyHippo 전체 패키지 블록체인 서명 스크립트
# =============================================================================
#
# 사용법:
#   ./scripts/sign_all.sh [author_name] [description]
#
# 예시:
#   ./scripts/sign_all.sh "GNJz" "Initial release v4.2.0"
#
# =============================================================================

set -e  # 에러 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 기본값
AUTHOR="${1:-GNJz}"
DESC="${2:-BabyHippo v4.2.0 Release}"

# 스크립트 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BLOCKCHAIN_DIR="$PROJECT_DIR/blockchain"
PHAM_SIGN="$BLOCKCHAIN_DIR/pham_sign_v4.py"

echo -e "${CYAN}"
echo "============================================================"
echo "🔗 BabyHippo Blockchain Signing"
echo "============================================================"
echo -e "${NC}"
echo "Author: $AUTHOR"
echo "Description: $DESC"
echo ""

# pham_sign_v4.py 존재 확인
if [ ! -f "$PHAM_SIGN" ]; then
    echo -e "${RED}Error: pham_sign_v4.py not found at $PHAM_SIGN${NC}"
    exit 1
fi

# 카운터
TOTAL=0
SUCCESS=0
FAILED=0

# 서명 함수
sign_file() {
    local file=$1
    local relative_path="${file#$PROJECT_DIR/}"
    
    TOTAL=$((TOTAL + 1))
    
    echo -e "${CYAN}[$TOTAL] Signing: $relative_path${NC}"
    
    if python3 "$PHAM_SIGN" "$file" --author "$AUTHOR" --desc "$DESC" 2>/dev/null; then
        SUCCESS=$((SUCCESS + 1))
        echo -e "${GREEN}    ✅ Success${NC}"
    else
        FAILED=$((FAILED + 1))
        echo -e "${YELLOW}    ⚠️ Skipped (no change or error)${NC}"
    fi
}

# 핵심 Brain 모듈 서명
echo -e "\n${YELLOW}=== Brain Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/brain/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Body 모듈 서명
echo -e "\n${YELLOW}=== Body Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/body/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Memory 모듈 서명
echo -e "\n${YELLOW}=== Memory Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/memory/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Neural 모듈 서명
echo -e "\n${YELLOW}=== Neural Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/neural/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Cortex 모듈 서명
echo -e "\n${YELLOW}=== Cortex Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/cortex/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Integration 모듈 서명
echo -e "\n${YELLOW}=== Integration Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/integration/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Utils 모듈 서명
echo -e "\n${YELLOW}=== Utils Modules ===${NC}"
for f in "$PROJECT_DIR"/babyhippo/utils/*.py; do
    [ -f "$f" ] && sign_file "$f"
done

# Config 서명
echo -e "\n${YELLOW}=== Config ===${NC}"
sign_file "$PROJECT_DIR/babyhippo/config.py"
sign_file "$PROJECT_DIR/babyhippo/__init__.py"

# 결과 출력
echo -e "\n${CYAN}"
echo "============================================================"
echo "📊 Signing Complete!"
echo "============================================================"
echo -e "${NC}"
echo -e "Total Files:    ${TOTAL}"
echo -e "${GREEN}Signed:         ${SUCCESS}${NC}"
echo -e "${YELLOW}Skipped/Failed: ${FAILED}${NC}"
echo ""
echo -e "Chain files saved to: ${BLOCKCHAIN_DIR}/"
echo ""
echo -e "${GREEN}🎉 All done!${NC}"

