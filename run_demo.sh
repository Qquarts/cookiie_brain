#!/bin/bash
# 🍪 Cookie 데모 실행 스크립트

cd /Users/jazzin/Desktop/babyhippo-release
export PYTHONPATH="/Users/jazzin/Desktop/babyhippo-release:$PYTHONPATH"

case "$1" in
    simple|"")
        echo "🍪 간단한 학습 데모 실행..."
        python3 examples/07_simple_learning_demo.py
        ;;
    full)
        echo "🍪 전체 시뮬레이션 실행..."
        python3 examples/06_cookie_learning_simulation.py
        ;;
    interactive)
        echo "🍪 대화형 인터페이스 실행..."
        python3 examples/05_cookie_interactive.py
        ;;
    v1)
        echo "🍪 Cookie v1.0 데모 실행..."
        python3 examples/04_cookie_v1_demo.py
        ;;
    *)
        echo "사용법: ./run_demo.sh [simple|full|interactive|v1]"
        echo ""
        echo "  simple      - 간단한 학습 데모 (기본값)"
        echo "  full        - 전체 시뮬레이션"
        echo "  interactive - 대화형 인터페이스"
        echo "  v1          - Cookie v1.0 데모"
        ;;
esac
