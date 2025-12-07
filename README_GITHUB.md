# 🦛 BabyHippo - Bio-Inspired AI Memory System

<p align="center">
  <strong>생물학적으로 영감을 받은 AI 메모리 시스템</strong><br>
  <em>"실체는 입자가 아니라 파동이다. 동역학이 이 세계의 실체다."</em>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#evolution">Evolution</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-4.3.0-blue.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.9+-green.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/license-PHAM--OPEN-orange.svg" alt="License"/>
  <img src="https://img.shields.io/badge/blockchain-verified-purple.svg" alt="Blockchain"/>
</p>

---

## 🌟 What is BabyHippo?

BabyHippo is a **biologically-inspired AI memory system** that mimics the structure and function of the human brain. Unlike traditional AI systems that rely on massive datasets and compute, BabyHippo focuses on:

- **🧠 Brain-like Architecture**: 8 core brain modules (Thalamus, Amygdala, Hippocampus, etc.)
- **⚡ Dynamic Learning**: STDP (Spike-Timing Dependent Plasticity) without backpropagation
- **🔋 Low-Power Design**: Runs on Raspberry Pi and edge devices
- **🌙 Sleep Consolidation**: Memory strengthening during "sleep" cycles
- **🧬 DNA Personality**: Customizable personality traits
- **🦛 Evolution System**: Biological evolution-based growth stages

---

## 🚀 Quick Start

### Installation

```bash
pip install babyhippo
# 또는 전체 기능
pip install -e ".[all]"
```

### Basic Usage

```python
from babyhippo.integration import CuriousBrain

# Cookie 생성
cookie = CuriousBrain(name="Cookie")

# 학습
cookie.think("나는 GNJz라고 해")

# 질문
response = cookie.think("너 이름이 뭐야?")
print(response)  # "GNJz입니다!"
```

### Examples

```bash
# 기본 사용법
python examples/01_basic_usage.py

# Cookie v1.0 데모
python examples/04_cookie_v1_demo.py

# 대화형 인터페이스
python examples/05_cookie_interactive.py
```

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    Input (입력)                          │
                    └─────────────────────┬───────────────────────────────────┘
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🤖 BODY (body/)                                                              │
│  👁️ senses.py (Eyes, Ears, Text) → SensoryInput                               │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🧠 BRAIN (brain/) - 8 Core Modules                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ 1. Thalamus      - 감각 정보 라우팅                                      │ │
│  │ 2. Amygdala      - 감정 처리                                              │ │
│  │ 3. Hypothalamus  - 생명 유지 (수면, 각성)                                │ │
│  │ 4. Basal Ganglia - 행동 선택 (GO/NO-GO)                                  │ │
│  │ 5. Prefrontal    - 계획, 추론                                            │ │
│  │ 6. Cingulate     - 주의, 모니터링                                        │ │
│  │ 7. Cerebellum    - 운동 제어, 언어 생성                                   │ │
│  │ 8. Brain Graph   - 전체 연결망                                            │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ⚡ NEURAL (neural/) - 5 Neuron Models                                        │
│  • HHSomaQuick (Hodgkin-Huxley, Flyweight Pattern)                          │
│  • Izhikevich (Large-scale networks)                                         │
│  • HH LIF (Hybrid model)                                                     │
│  • MyelinatedAxon (Saltatory conduction)                                      │
│  • BabyNeuron (Basic model)                                                  │
│                                                                               │
│  💾 MEMORY (memory/) - Multi-tier Memory System                               │
│  • HippoMemory (Hippocampal memory)                                          │
│  • PanoramaMemory (Multi-tier: Archive, Timeline, Surface)                   │
│  • CoreMemory (Personality/knowledge)                                        │
│  • WorkingMemory (Short-term context)                                        │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🔗 INTEGRATION (integration/)                                                │
│  • BabyBrain - Full-featured brain                                           │
│  • CuriousBrain - Learning AI (Cookie) ⭐                                    │
│  • BrainLLM - Personal LLM (nanoGPT)                                          │
│  • DreamManager - Sleep consolidation                                        │
│  • HippoEvolution - Evolution system 🎖️                                     │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      ▼
                    Output (출력)
```

---

## 🦛 Evolution System

BabyHippo follows a **biological evolution-based growth system**:

```
🍼 BabyHippo (유아기) → 👶 TeenHippo (청소년) → 🎓 Hippocampus (완전체)
    → 🧙‍♂️ WisdomHippo (성숙기) → 🪄 MagicHippo (고등 인지) → 🌌 HyperHippo (우주급)
```

Each stage has **range-based requirements** (not fixed numbers) for flexibility:

- **TeenHippo**: 1k ~ 5k neurons, 50~70 FPS
- **Hippocampus**: 30k ~ 100k neurons, 15~30 FPS
- **MagicHippo**: 500k+ neurons, 5~15 FPS
- **HyperHippo**: 1M+ neurons, 0.1~5 FPS (black hole calculations!)

See [EVOLUTION_SYSTEM.md](docs/EVOLUTION_SYSTEM.md) for details.

---

## 🧩 BrainCapability Schema

Structured capability flags for extensibility:

```python
from babyhippo.integration import BrainCapabilitySchema, CapabilityCategory

schema = create_default_schema()
schema.set_capability(CapabilityCategory.MEMORY, "short_term", enabled=True)
schema.set_capability(CapabilityCategory.PLASTICITY, "stdp", enabled=True)
```

Categories: `memory`, `network`, `plasticity`, `physiology`, `cognition`, `integration`

---

## 📊 Performance

- **Memory Efficiency**: HHSomaQuick Flyweight Pattern (30GB → 50MB)
- **Real-time Processing**: 1,000 neurons @ 60 FPS
- **Scalability**: 10^5+ neuron networks supported

---

## 🔧 Key Features

### ✅ Range-based Requirements
- Flexible validation conditions
- Future-proof design
- Backward compatible

### ✅ Optional Blockchain Layer
- **Local Proof**: Works without blockchain (standalone)
- **Distributed Proof**: Optional smart contract integration
- Choose your network: EVM / Solana / Custom chain

### ✅ BrainCapability Schema
- Extensible capability flags
- Community-friendly expansion
- No conflicts with future features

---

## 📚 Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Full architecture
- [ARCHITECTURE_FINAL.md](docs/ARCHITECTURE_FINAL.md) - Final architecture review
- [EVOLUTION_SYSTEM.md](docs/EVOLUTION_SYSTEM.md) - Evolution system
- [EVOLUTION_TREE.md](docs/EVOLUTION_TREE.md) - Growth tree diagram
- [GROWTH_SYSTEM.md](docs/GROWTH_SYSTEM.md) - Growth system
- [API.md](docs/API.md) - API documentation

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

PHAM-OPEN-2.0

---

## 🙏 Acknowledgments

This project is built on the knowledge and inspiration from neuroscience, artificial intelligence, and open-source communities.

---

**Version**: 4.3.0 (Cookie v1.0 - 1st Cookie Revolution)  
**Author**: GNJz (Qquarts)  
**GitHub**: https://github.com/qquarts/babyhippo

