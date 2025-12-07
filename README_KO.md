<p align="center">
  <img src="docs/logo.png" alt="BabyHippo Logo" width="200"/>
</p>

<h1 align="center">🧠 BabyHippo</h1>

<p align="center">
  <strong>생물학적 영감을 받은 AI 기억 시스템</strong><br>
  <em>"실체는 입자가 아니라 파동이다. 동역학이 이 세계의 실체다."</em>
</p>

<p align="center">
  <a href="#설치">설치</a> •
  <a href="#빠른-시작">빠른 시작</a> •
  <a href="#아키텍처">아키텍처</a> •
  <a href="#문서">문서</a> •
  <a href="#라이선스">라이선스</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/버전-4.2.0-blue.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/python-3.9+-green.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/라이선스-PHAM--OPEN-orange.svg" alt="License"/>
  <img src="https://img.shields.io/badge/블록체인-검증됨-purple.svg" alt="Blockchain"/>
</p>

---

## 🌟 BabyHippo란?

BabyHippo는 인간 뇌의 구조와 기능을 모방한 **생물학적 영감을 받은 AI 기억 시스템**입니다. 대규모 데이터셋과 컴퓨팅에 의존하는 기존 AI 시스템과 달리, BabyHippo는 다음에 집중합니다:

- **🧠 뇌 유사 아키텍처**: 8개의 핵심 뇌 모듈 (시상, 편도체, 해마 등)
- **⚡ 동적 학습**: 역전파 없는 STDP (스파이크 타이밍 의존 가소성)
- **🔋 저전력 설계**: 라즈베리파이 및 엣지 기기에서 실행 가능
- **🌙 수면 공고화**: "수면" 사이클 중 기억 강화
- **🧬 DNA 성격**: 커스터마이징 가능한 성격 특성 (쿼카, 학자, 집사, 운동선수)

---

## 🏗️ 아키텍처

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    입력 (Input)                          │
                    └─────────────────────┬───────────────────────────────────┘
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🤖 몸 (body/)                                                                │
│  👁️ senses.py (눈, 귀, 텍스트) → SensoryInput                                  │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🧠 뇌 (brain/)                                                               │
│                                                                               │
│  1️⃣ 시상 (Thalamus)         → 감각 게이팅                                      │
│  2️⃣ 편도체 (Amygdala)        → 감정 & 위협 감지                                 │
│  3️⃣ 시상하부 (Hypothalamus)  → 욕구 & 동기                                     │
│  4️⃣ 기저핵 (Basal Ganglia)   → 습관 & 행동 선택                                │
│  5️⃣ 전두엽 (Prefrontal)      → 계획 & 판단                                     │
│  6️⃣ 대상피질 (Cingulate)     → 오류 감지                                       │
│  7️⃣ 소뇌 (Cerebellum)        → 미세조정 & 반사                                 │
│  8️⃣ 해마 (Hippocampus)       → 기억 저장 & 회상                                │
│                                                                               │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  🤖 몸 (body/)                                                                │
│  🗣️ actions.py (말하기, 텍스트, 모터) → 출력                                    │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 설치

### 요구사항

- Python 3.9+
- NumPy

### 소스에서 설치

```bash
git clone https://github.com/qquarts/babyhippo.git
cd babyhippo-release
pip install -e .
```

### 의존성 설치

```bash
pip install numpy networkx
```

---

## 🚀 빠른 시작

### 기본 사용법

```python
from babyhippo import BabyBrain

# 성격을 가진 뇌 생성
brain = BabyBrain(name="나의AI", species="quokka")

# 학습
brain.learn("내 이름은 BabyHippo입니다")
brain.learn("저는 새로운 것을 배우는 걸 좋아해요")

# 대화
response = brain.chat("이름이 뭐야?")
print(response)

# 수면 (기억 공고화)
brain.sleep(hours=8)

# 상태 저장
brain.save()
```

### 성격 유형 (DNA)

```python
from babyhippo import BabyBrain, SpeciesType

# 🦛 쿼카 - 친화적, 호기심 많음, 약간 겁 많음
brain = BabyBrain(name="쿼카", species="quokka")

# 📚 학자 - 분석적, 내향적, 지식 추구
brain = BabyBrain(name="학자", species="scholar")

# 🎩 집사 - 효율적, 충성스러움, 과업 지향
brain = BabyBrain(name="집사", species="butler")

# 💪 운동선수 - 활동적, 에너지 넘침, 단순
brain = BabyBrain(name="운동선수", species="athlete")
```

### 저전력 모드 (라즈베리파이용)

```python
from babyhippo import LiteBrain

# 엣지 기기용 경량 뇌
brain = LiteBrain(name="엣지AI")
brain.chat("안녕!")
```

---

## 📐 수학적 기반

### STDP 학습 규칙

$$\Delta w = \begin{cases} A_+ e^{-\Delta t / \tau_+} & \text{if } \Delta t > 0 \\ -A_- e^{\Delta t / \tau_-} & \text{if } \Delta t < 0 \end{cases}$$

설명:
- $\Delta t = t_{post} - t_{pre}$ (시간 차이)
- $A_+ = 0.1$, $A_- = 0.12$ (학습률)
- $\tau_+ = \tau_- = 20$ ms (시간 상수)

### 기억 강화 (편도체)

$$M = 1 + \alpha \cdot E \cdot (1 - e^{-\beta \cdot T})$$

설명:
- $E = \sqrt{V^2 + A^2}$ (감정 강도)
- $T$ = 위협 수준
- $\alpha = 0.5$, $\beta = 2.0$

### 수면 공고화

수면 중 기억은 다양한 노이즈 수준으로 재생됩니다:

| 단계 | 노이즈 수준 | 기능 |
|------|------------|------|
| 얕은 수면 (N1/N2) | 0.1 | 최근 기억 정리 |
| 깊은 수면 (SWS) | 0.05 | 해마 → 피질 전이 |
| REM | 0.3 | 창의적 연결 |

---

## 📁 프로젝트 구조

```
babyhippo-release/
├── babyhippo/              # 코어 패키지
│   ├── brain/              # 8개 뇌 모듈
│   │   ├── _1_thalamus.py      # 시상
│   │   ├── _2_amygdala.py      # 편도체
│   │   ├── _3_hypothalamus.py  # 시상하부
│   │   ├── _4_basal_ganglia.py # 기저핵
│   │   ├── _5_prefrontal.py    # 전두엽
│   │   ├── _6_cingulate.py     # 대상피질
│   │   ├── _7_cerebellum.py    # 소뇌
│   │   └── _8_brain_graph.py   # 뇌 그래프
│   ├── body/               # 말초 신경계
│   │   ├── senses.py           # 감각
│   │   ├── actions.py          # 행동
│   │   └── nervous_system.py   # 신경계
│   ├── memory/             # 기억 시스템
│   ├── neural/             # 신경 동역학 (STDP, HH 모델)
│   ├── cortex/             # 감각 피질
│   ├── integration/        # 통합 뇌 시스템
│   ├── utils/              # 유틸리티
│   └── config.py           # DNA 설정
├── docs/                   # 문서
├── examples/               # 예제 코드
├── tests/                  # 테스트 스위트
├── blockchain/             # 블록체인 검증
└── pyproject.toml          # 패키지 설정
```

---

## 📚 문서

- [아키텍처 가이드](docs/ARCHITECTURE.md) - 상세한 뇌 구조
- [API 레퍼런스](docs/API.md) - 전체 API 문서
- [수학적 모델](docs/MATH.md) - 수식과 공식
- [기여 가이드](docs/CONTRIBUTING.md) - 기여 방법

---

## 🔗 블록체인 검증

이 프로젝트는 기여 추적 및 검증을 위해 **PHAM Sign**을 사용합니다.

```bash
# 기여 서명
python3 blockchain/pham_sign_v4.py babyhippo/brain/_1_thalamus.py \
    --author "당신의이름" \
    --desc "기여 설명"
```

모든 기여는 온체인에 기록됩니다. 프로젝트가 수익을 창출하면, 기여자들은 기여 점수에 비례하여 보상을 받습니다.

**원본 해시**: `[생성 예정]`

---

## ⚖️ 라이선스

### PHAM-OPEN LICENSE v2.0

**"코드는 자유롭다. 성공은 나눈다."**

1. **자유로운 사용**: 누구나 이 코드를 무료로 사용, 수정, 연구할 수 있습니다.
2. **수익 분배**: 이 코드를 사용하여 수익을 창출하면, 원작자에게 6%를 공유합니다.
3. **기여 기록**: 모든 수정사항은 블록체인에 기록됩니다.

자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

**창작자 지갑**: `0x99779F19376c4740d4F555083F6dcB2B47C76bF5`

---

## 🙏 감사의 말

- 해마 기억 시스템에 관한 신경과학 연구에서 영감을 받음
- Bi & Poo (1998)의 STDP 학습 기반
- GNJz (Qquarts Co.)가 ❤️로 제작

---

## 📞 연락처

- **저자**: GNJz (Qquarts)
- **이메일**: [contact@qquarts.com]
- **GitHub**: [@qquarts](https://github.com/qquarts)

---

<p align="center">
  <em>"실체는 입자가 아니라 파동이다. 동역학이 이 세계의 실체다."</em>
</p>

