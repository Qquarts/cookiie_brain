# 🚀 Cookie 학습 시뮬레이션 빠른 시작

## 실행 방법

```bash
# 방법 1: 간단한 데모
PYTHONPATH=/Users/jazzin/Desktop/babyhippo-release:$PYTHONPATH \
  python3 examples/07_simple_learning_demo.py

# 방법 2: 전체 시뮬레이션
PYTHONPATH=/Users/jazzin/Desktop/babyhippo-release:$PYTHONPATH \
  python3 examples/06_cookie_learning_simulation.py
```

## Python 코드로 직접 실행

```python
import sys
from pathlib import Path

# 경로 설정
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from babyhippo.integration import CuriousBrain

# Cookie 생성
cookie = CuriousBrain(name="Cookie")

# 1. 개념 뉴런 생성
cookie.learn("사과", importance=0.8)
cookie.learn("빨간색", importance=0.8)
cookie.learn("달다", importance=0.8)

# 2. 연결 형성
cookie.learn("사과는 빨간색", importance=0.8)
cookie.learn("사과는 달다", importance=0.8)

# 3. 수면
cookie.sleep(cycles=5)

# 4. 회상 테스트
answer1 = cookie.think("사과는 무슨 색이야?")
answer2 = cookie.think("사과는 어떤 맛이야?")

print(f"답변 1: {answer1}")
print(f"답변 2: {answer2}")
```

## 4단계 요약

1. **개념 뉴런 생성**: `cookie.learn("사과")`
2. **연결 형성**: `cookie.learn("사과는 빨간색")`
3. **수면 공고화**: `cookie.sleep(cycles=5)`
4. **회상 테스트**: `cookie.think("사과는 무슨 색이야?")`

