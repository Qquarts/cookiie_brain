# 🤝 Contributing to BabyHippo

감사합니다! BabyHippo에 기여하는 데 관심을 가져주셔서 감사합니다.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Blockchain Signing](#blockchain-signing)
- [Style Guide](#style-guide)

---

## 🌟 Code of Conduct

이 프로젝트는 모든 참여자가 존중받는 환경을 추구합니다.

- ✅ 건설적인 피드백을 제공하세요
- ✅ 다양한 관점을 존중하세요
- ✅ 커뮤니티에 긍정적으로 기여하세요
- ❌ 괴롭힘, 차별, 공격적인 언어는 허용되지 않습니다

---

## 🛠️ How to Contribute

### 1. Issues

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출하세요.

**버그 리포트 시 포함할 내용:**
- 재현 단계
- 예상 동작 vs 실제 동작
- 환경 정보 (Python 버전, OS 등)
- 관련 에러 메시지

**기능 요청 시 포함할 내용:**
- 문제 설명
- 제안하는 해결책
- 대안적 접근법
- 추가 컨텍스트

### 2. Pull Requests

1. 저장소를 Fork 합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치를 Push 합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

---

## 💻 Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/qquarts/babyhippo.git
cd babyhippo
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Run tests

```bash
pytest tests/ -v
```

---

## 🔗 Blockchain Signing

### 중요! 기여도 기록

BabyHippo는 블록체인을 통해 모든 기여를 추적합니다.  
수익이 발생하면 기여도에 따라 분배됩니다.

### 기여 서명 방법

```bash
cd blockchain

# 단일 파일 서명
python3 pham_sign_v4.py ../babyhippo/brain/_1_thalamus.py \
    --author "YourName" \
    --desc "Your contribution description"

# 모든 변경 파일 서명
cd ..
./scripts/sign_all.sh "YourName" "Your contribution description"
```

### 기여도 점수

| 등급 | 점수 범위 | 의미 |
|------|-----------|------|
| ⭐ A_HIGH | 0.80-1.00 | 주요 기능 추가, 대규모 리팩토링 |
| ✅ B_MEDIUM | 0.50-0.79 | 버그 수정, 기능 개선 |
| ⚠️ C_LOW | 0.12-0.49 | 문서화, 작은 수정 |
| 🚫 SPAM | 0.00-0.11 | 의미없는 변경 |

---

## 📝 Style Guide

### Python Code Style

- **Formatter**: Black (line-length=100)
- **Import Sorter**: isort
- **Type Checker**: mypy

```bash
# 코드 포맷팅
black babyhippo/
isort babyhippo/

# 타입 체크
mypy babyhippo/
```

### Docstring Style

Google style docstring을 사용합니다:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    함수에 대한 짧은 설명.
    
    더 자세한 설명이 필요하면 여기에 작성합니다.
    
    Args:
        param1: 첫 번째 파라미터 설명
        param2: 두 번째 파라미터 설명 (기본값: 0)
    
    Returns:
        반환값에 대한 설명
    
    Raises:
        ValueError: 잘못된 값일 때 발생
    
    Example:
        >>> example_function("hello", 42)
        True
    """
    pass
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**예시:**
```
feat(brain): add new emotion processing in amygdala

- Implement Russell's Circumplex Model
- Add fear conditioning with STDP
- Improve threat detection accuracy

Closes #123
```

---

## 🧪 Testing

### 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 커버리지와 함께
pytest tests/ --cov=babyhippo --cov-report=html

# 특정 모듈만
pytest tests/test_brain.py -v
```

### 테스트 작성 가이드

```python
import pytest
from babyhippo import BabyBrain

class TestBabyBrain:
    """BabyBrain 테스트 클래스"""
    
    def test_basic_chat(self):
        """기본 대화 테스트"""
        brain = BabyBrain()
        response = brain.chat("안녕")
        assert response is not None
        assert len(response) > 0
    
    def test_learning(self):
        """학습 기능 테스트"""
        brain = BabyBrain()
        brain.learn("테스트 데이터")
        memories = brain.recall("테스트")
        assert len(memories) > 0
```

---

## 🎯 Priority Areas

현재 기여가 필요한 영역:

1. **Documentation** - 문서화 개선
2. **Tests** - 테스트 커버리지 향상
3. **Performance** - 메모리 최적화
4. **Examples** - 예제 코드 추가
5. **Translations** - 다국어 지원

---

## 📞 Contact

- **Email**: opensource@qquarts.com
- **GitHub Issues**: https://github.com/qquarts/babyhippo/issues
- **Discussions**: https://github.com/qquarts/babyhippo/discussions

---

## 🙏 Thank You!

모든 기여자분들께 감사드립니다.  
여러분의 기여가 BabyHippo를 더 좋게 만듭니다! 🦛

---

> **"Code is Free. Success is Shared. Your contribution matters."**

