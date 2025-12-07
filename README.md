<p align="center">
  <img src="docs/logo.png" alt="BabyHippo Logo" width="200"/>
</p>

<h1 align="center">🧠 BabyHippo</h1>

<p align="center">
  <strong>Bio-Inspired AI Memory System</strong><br>
  <em>"실체는 입자가 아니라 파동이다. 동역학이 이 세계의 실체다."</em>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
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
- **🧬 DNA Personality**: Customizable personality traits (Quokka, Scholar, Butler, Athlete)

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
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🧠 BRAIN (brain/)                                                            │
│                                                                               │
│  1️⃣ Thalamus (시상)        → Sensory Gating                                   │
│  2️⃣ Amygdala (편도체)       → Emotion & Threat Detection                       │
│  3️⃣ Hypothalamus (시상하부) → Drives & Motivation                              │
│  4️⃣ Basal Ganglia (기저핵)  → Habit & Action Selection                         │
│  5️⃣ Prefrontal (전두엽)     → Planning & Decision                              │
│  6️⃣ Cingulate (대상피질)    → Error Detection                                  │
│  7️⃣ Cerebellum (소뇌)       → Fine-tuning & Reflexes                           │
│  8️⃣ Hippocampus (해마)      → Memory Storage & Recall                          │
│                                                                               │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🤖 BODY (body/)                                                              │
│  🗣️ actions.py (Speech, Text, Motor) → Output                                 │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Requirements

- Python 3.9+
- NumPy

### Install from source

```bash
git clone https://github.com/qquarts/babyhippo.git
cd babyhippo-release
pip install -e .
```

### Install dependencies

```bash
pip install numpy networkx
```

---

## 🚀 Quick Start

### Basic Usage

```python
from babyhippo import BabyBrain

# Create a brain with personality
brain = BabyBrain(name="MyAI", species="quokka")

# Learn something
brain.learn("My name is BabyHippo")
brain.learn("I love learning new things")

# Chat
response = brain.chat("What's your name?")
print(response)

# Sleep (memory consolidation)
brain.sleep(hours=8)

# Save state
brain.save()
```

### Personality Types (DNA)

```python
from babyhippo import BabyBrain, SpeciesType

# 🦛 Quokka - Friendly, curious, slightly timid
brain = BabyBrain(name="Quokka", species="quokka")

# 📚 Scholar - Analytical, introverted, knowledge-seeking
brain = BabyBrain(name="Scholar", species="scholar")

# 🎩 Butler - Efficient, loyal, task-oriented
brain = BabyBrain(name="Butler", species="butler")

# 💪 Athlete - Energetic, active, straightforward
brain = BabyBrain(name="Athlete", species="athlete")
```

### Low-Power Mode (for Raspberry Pi)

```python
from babyhippo import LiteBrain

# Lightweight brain for edge devices
brain = LiteBrain(name="EdgeAI")
brain.chat("Hello!")
```

---

## 📐 Mathematical Foundation

### STDP Learning Rule

$$\Delta w = \begin{cases} A_+ e^{-\Delta t / \tau_+} & \text{if } \Delta t > 0 \\ -A_- e^{\Delta t / \tau_-} & \text{if } \Delta t < 0 \end{cases}$$

Where:
- $\Delta t = t_{post} - t_{pre}$ (timing difference)
- $A_+ = 0.1$, $A_- = 0.12$ (learning rates)
- $\tau_+ = \tau_- = 20$ ms (time constants)

### Memory Enhancement (Amygdala)

$$M = 1 + \alpha \cdot E \cdot (1 - e^{-\beta \cdot T})$$

Where:
- $E = \sqrt{V^2 + A^2}$ (emotional intensity)
- $T$ = threat level
- $\alpha = 0.5$, $\beta = 2.0$

### Sleep Consolidation

During sleep, memories are replayed with varying noise levels:

| Stage | Noise Level | Function |
|-------|-------------|----------|
| Light (N1/N2) | 0.1 | Recent memory sorting |
| Deep (SWS) | 0.05 | Hippocampus → Cortex transfer |
| REM | 0.3 | Creative connections |

---

## 📁 Project Structure

```
babyhippo-release/
├── babyhippo/              # Core package
│   ├── brain/              # 8 brain modules
│   │   ├── _1_thalamus.py
│   │   ├── _2_amygdala.py
│   │   ├── _3_hypothalamus.py
│   │   ├── _4_basal_ganglia.py
│   │   ├── _5_prefrontal.py
│   │   ├── _6_cingulate.py
│   │   ├── _7_cerebellum.py
│   │   └── _8_brain_graph.py
│   ├── body/               # Peripheral nervous system
│   │   ├── senses.py
│   │   ├── actions.py
│   │   └── nervous_system.py
│   ├── memory/             # Memory systems
│   ├── neural/             # Neural dynamics (STDP, HH model)
│   ├── cortex/             # Sensory cortex
│   ├── integration/        # Integrated brain systems
│   ├── utils/              # Utilities
│   └── config.py           # DNA configuration
├── docs/                   # Documentation
├── examples/               # Example code
├── tests/                  # Test suite
├── blockchain/             # Blockchain verification
└── pyproject.toml          # Package configuration
```

---

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Detailed brain structure
- [API Reference](docs/API.md) - Complete API documentation
- [Mathematical Models](docs/MATH.md) - Equations and formulas
- [Contributing Guide](docs/CONTRIBUTING.md) - How to contribute

---

## 🔗 Blockchain Verification

This project uses **PHAM Sign** for contribution tracking and verification.

```bash
# Sign your contribution
python3 blockchain/pham_sign_v4.py babyhippo/brain/_1_thalamus.py \
    --author "YourName" \
    --desc "Your contribution description"
```

All contributions are recorded on-chain. When the project generates revenue, contributors receive rewards proportional to their contribution score.

**Original Hash**: `[TO BE GENERATED]`

---

## ⚖️ License

### PHAM-OPEN LICENSE v2.0

**"Code is Free. Success is Shared."**

1. **Free Usage**: Anyone can use, modify, and study this code for free.
2. **Revenue Sharing**: If you generate profit using this code, share 6% with the original creator.
3. **Contribution Recording**: All modifications are recorded on blockchain.

See [LICENSE](LICENSE) for full details.

**Creator Wallet**: `0x99779F19376c4740d4F555083F6dcB2B47C76bF5`

---

## 🙏 Acknowledgments

- Inspired by neuroscience research on hippocampal memory systems
- STDP learning based on Bi & Poo (1998)
- Built with ❤️ by GNJz (Qquarts Co.)

---

## 📞 Contact

- **Author**: GNJz (Qquarts)
- **Email**: [contact@qquarts.com]
- **GitHub**: [@qquarts](https://github.com/qquarts)

---

<p align="center">
  <em>"The essence is not the particle, but the wave. Dynamics is the reality of this world."</em>
</p>

