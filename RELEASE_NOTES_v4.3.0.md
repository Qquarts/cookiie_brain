# 🍪 BabyHippo v4.3.0 - Cookiie v1.0 (1st Cookiie Revolution)

## 🎉 첫 공개 릴리즈!

BabyHippo는 **생물학적으로 영감을 받은 AI 메모리 시스템**으로, 인간의 뇌 구조와 기능을 모방합니다.

이번 릴리즈는 **"1st Cookiie Revolution"**으로, Cookiie AI의 핵심 기능들이 완성되었습니다.

---

## ✨ 주요 기능

### 🧠 생물학적 뇌 구조
- **8개 핵심 뇌 모듈**: Thalamus, Amygdala, Hypothalamus, Hippocampus, Basal Ganglia, Prefrontal, Cingulate, Cerebellum
- **해마 메모리 시스템**: DG → CA3 → CA1 → SUB 경로
- **STDP 학습**: 역전파 없이 시냅스 가소성

### ⚡ 5종 뉴런 모델
- **HHSomaQuick**: Hodgkin-Huxley 기반, Flyweight 패턴으로 메모리 최적화 (30GB → 50MB)
- **Izhikevich**: 대규모 네트워크용 (10^5+ 뉴런)
- **HH LIF**: HH 정확도 + LIF 효율성
- **MyelinatedAxon**: 도약전도 PDE 모델
- **BabyNeuron**: 기본 뉴런

### 🦛 진화 단계 시스템
- **생물학적 진화 순서 기반**: BabyHippo → TeenHippo → Hippocampus → WisdomHippo → MagicHippo → HyperHippo
- **범위 기반 조건**: 유연한 검증 (1k~5k 뉴런, 50~70 FPS 등)
- **블록체인 통합**: 선택적 계층 (독립형 시스템 가능)

### 🧩 BrainCapability Schema
- **확장 가능한 능력 플래그**: memory, network, plasticity, physiology, cognition, integration
- **커뮤니티 확장 용이**: Schema 기반 구조

### 🍪 Cookiie AI
- **자연어 학습**: "나는 GNJz라고 해" → 자동 학습
- **대화 맥락 관리**: 연속 대화 지원
- **기억 시스템**: 해마 → 개인 LLM → 대형 도서관(LLM API)

---

## 🚀 빠른 시작

### 설치

```bash
pip install babyhippo
# 또는 전체 기능
pip install -e ".[all]"
```

### 기본 사용

```python
from babyhippo.integration import CuriousBrain

# Cookiie 생성
cookiie = CuriousBrain(name="Cookiie")

# 학습
cookiie.think("나는 GNJz라고 해")

# 질문
response = cookiie.think("너 이름이 뭐야?")
print(response)  # "GNJz입니다!"
```

### 예제 실행

```bash
# 기본 사용법
python examples/01_basic_usage.py

# Cookiie v1.0 데모
python examples/04_cookiie_v1_demo.py

# 대화형 인터페이스
python examples/05_cookiie_interactive.py
```

---

## 📊 성능

- **메모리 효율**: HHSomaQuick Flyweight 패턴 (30GB → 50MB)
- **실시간 처리**: 1,000 뉴런 시뮬레이션 60 FPS
- **확장성**: 10^5+ 뉴런 네트워크 지원

---

## 🎖️ 진화 단계

| 단계 | 수준 | 뇌 기능 | 비유 |
|------|------|---------|------|
| BabyHippo | 유아기 | 기본 기억 | GPT-1 |
| TeenHippo | 청소년 | 연상 | GPT-2~3 |
| Hippocampus | 완전체 | 해마 완성 | GPT-5~6 |
| WisdomHippo | 성숙기 | 에피소드 기억 | GPT-5~6 |
| MagicHippo | 고등 인지 | 추상화 | GPT-6+ |
| HyperHippo | 우주급 | 하이퍼 드라이브 | 초지능급 |

---

## 📚 문서

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 전체 아키텍처
- [EVOLUTION_SYSTEM.md](docs/EVOLUTION_SYSTEM.md) - 진화 시스템
- [API.md](docs/API.md) - API 문서

---

## 🤝 기여

기여를 환영합니다! [CONTRIBUTING.md](docs/CONTRIBUTING.md)를 참조하세요.

---

## 📄 라이선스

PHAM-OPEN-2.0

---

## 🙏 감사의 말

이 프로젝트는 뇌과학, 인공지능, 오픈소스 커뮤니티의 지식과 영감을 바탕으로 만들어졌습니다.

---

**Version**: 4.3.0  
**Release Date**: 2025-12-07  
**Author**: GNJz (Qquarts)

