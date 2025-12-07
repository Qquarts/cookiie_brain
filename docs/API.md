# 📚 BabyHippo API Reference

## Table of Contents

- [BabyBrain](#babybrain)
- [LiteBrain](#litebrain)
- [CuriousBrain](#curiousbrain)
- [HippoMemory](#hippomemory)
- [Brain Modules](#brain-modules)
- [DNA Configuration](#dna-configuration)

---

## BabyBrain

메인 통합 뇌 시스템. 8개의 뇌 모듈을 통합하여 완전한 뇌를 구성합니다.

### Import

```python
from babyhippo import BabyBrain
```

### Constructor

```python
BabyBrain(
    name: str = "Quokka",
    species: str = "quokka",
    library_provider: str = "openai",
    auto_save: bool = True,
    save_dir: str = None,
    noise_level: float = 0.1
)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "Quokka" | AI의 이름 |
| `species` | str | "quokka" | 성격 유형 ("quokka", "scholar", "butler", "athlete") |
| `library_provider` | str | "openai" | LLM 제공자 ("openai", "anthropic", "local") |
| `auto_save` | bool | True | 자동 저장 활성화 |
| `save_dir` | str | None | 저장 디렉토리 경로 |
| `noise_level` | float | 0.1 | 노이즈 수준 (창발성) |

### Methods

#### chat(message: str) -> str

대화 처리

```python
brain = BabyBrain(name="MyAI")
response = brain.chat("안녕하세요!")
print(response)  # "안녕하세요! 😊"
```

#### learn(content: str, category: str = "general") -> bool

새로운 정보 학습

```python
brain.learn("파이썬은 프로그래밍 언어입니다")
brain.learn("서울은 대한민국의 수도입니다", category="geography")
```

#### recall(cue: str, top_k: int = 5) -> List[Dict]

기억 회상

```python
memories = brain.recall("파이썬")
for mem in memories:
    print(f"{mem['content']} (점수: {mem['score']:.2f})")
```

#### sleep(hours: float = 8, verbose: bool = True) -> str

수면 (기억 공고화)

```python
brain.sleep(hours=8)
# 출력: "☀️ MyAI 기상! 에너지: 100%"
```

#### save(path: str = None)

상태 저장

```python
brain.save()  # 기본 경로에 저장
brain.save("./my_brain_backup")  # 특정 경로에 저장
```

#### load(path: str = None) -> bool

상태 로드

```python
brain.load("./my_brain_backup")
```

#### get_status() -> Dict

현재 상태 조회

```python
status = brain.get_status()
print(f"에너지: {status['energy']:.0%}")
print(f"기분: {status['mood']}")
print(f"욕구: {status['drives']}")
```

---

## LiteBrain

엣지 디바이스용 경량 뇌. LLM 없이 작동합니다.

### Import

```python
from babyhippo import LiteBrain
```

### Constructor

```python
LiteBrain(
    name: str = "LiteBrain",
    capacity: int = 1000
)
```

### Methods

#### chat(message: str) -> str

```python
brain = LiteBrain(name="EdgeAI")
response = brain.chat("안녕!")
```

#### learn(trigger: str, response: str)

패턴 학습

```python
brain.learn("날씨 어때", "오늘은 맑아요!")
```

---

## CuriousBrain

LLM API와 통합된 호기심 많은 뇌

### Import

```python
from babyhippo import CuriousBrain
```

### Constructor

```python
CuriousBrain(
    name: str = "Curious",
    provider: str = "openai",
    model: str = "gpt-4o-mini"
)
```

### Methods

#### think(question: str) -> str

질문에 대해 생각하고 답변

```python
brain = CuriousBrain(provider="openai")
answer = brain.think("양자역학이란 무엇인가요?")
```

#### get_stats() -> Dict

통계 조회

```python
stats = brain.get_stats()
print(f"질문 수: {stats['questions_asked']}")
print(f"도서관 방문: {stats['library_visits']}")
```

---

## HippoMemory

해마 기억 시스템

### Import

```python
from babyhippo import HippoMemory
```

### Constructor

```python
HippoMemory(
    capacity: int = 10000
)
```

### Methods

#### store(word: str, context: str = "", importance: float = 1.0) -> str

기억 저장

```python
memory = HippoMemory()
word_id = memory.store("파이썬", context="프로그래밍")
```

#### recall(cue: str, top_k: int = 5) -> List[Dict]

기억 회상

```python
results = memory.recall("파이썬")
```

#### sleep() -> Dict

수면 공고화

```python
consolidation_stats = memory.sleep()
```

#### forget(word_id: str) -> bool

기억 삭제

```python
memory.forget("word_123")
```

---

## Brain Modules

### Thalamus (시상)

```python
from babyhippo import Thalamus, SensoryInput, ModalityType

thalamus = Thalamus()

# 감각 입력 생성
inputs = [
    SensoryInput(
        modality=ModalityType.TEXT,
        content="안녕하세요",
        intensity=0.8
    )
]

# 중계 (필터링)
outputs = thalamus.relay(inputs)
```

### Amygdala (편도체)

```python
from babyhippo import Amygdala

amygdala = Amygdala()

# 위협 감지
threat = amygdala.detect_threat("불이야! 도망쳐!")
if threat:
    print(f"위협 레벨: {threat.level}")
    print(f"유형: {threat.threat_type}")

# 감정 처리
emotion = amygdala.process_emotion("오늘 정말 기분 좋아!")
print(f"감정: {emotion.dominant}")
print(f"강도: {emotion.intensity}")
```

### Hypothalamus (시상하부)

```python
from babyhippo import Hypothalamus

hypothalamus = Hypothalamus()

# 틱 업데이트
hypothalamus.tick(action_type='chat')

# 우선 욕구 조회
top_drive = hypothalamus.get_top_drive()
print(f"최우선 욕구: {top_drive}")

# 보상 처리
hypothalamus.reward(amount=0.3)
```

### Basal Ganglia (기저핵)

```python
from babyhippo import BasalGanglia

bg = BasalGanglia()

# 행동 선택
action = bg.select_action(
    context="greeting",
    available_actions=["respond_memory", "generate_new", "ask_clarify"]
)
print(f"선택된 행동: {action.name}")
print(f"습관 여부: {action.is_habit}")

# 보상 업데이트
bg.update(context="greeting", action="respond_memory", reward=0.8)
```

### Prefrontal Cortex (전두엽)

```python
from babyhippo import PrefrontalCortex

pfc = PrefrontalCortex()

# 쿼리 분석
analysis = pfc.analyze_query("파이썬이 뭐야?")
print(f"의도: {analysis['intents']}")
print(f"키워드: {analysis['keywords']}")
print(f"검색 깊이: {analysis['search_depth']}")
```

### Cingulate Cortex (대상피질)

```python
from babyhippo import CingulateCortex

cingulate = CingulateCortex()

# 응답 오류 체크
error = cingulate.check_response_error(
    response="",  # 빈 응답
    context="질문에 대한 답변"
)
if error:
    print(f"오류 유형: {error.error_type}")
    print(f"심각도: {error.magnitude}")
```

### Cerebellum (소뇌)

```python
from babyhippo import Cerebellum

cerebellum = Cerebellum()

# 반사 체크
reflex = cerebellum.check_reflex("안녕")
if reflex:
    print(f"반사 응답: {reflex.response}")

# 출력 다듬기
refined = cerebellum.refine_output("안녕 안녕 안녕")
print(refined)  # "안녕"
```

---

## DNA Configuration

### SpeciesType

```python
from babyhippo import SpeciesType

# 사용 가능한 종
SpeciesType.QUOKKA   # 🦛 친화적, 호기심
SpeciesType.SCHOLAR  # 📚 분석적, 내향적
SpeciesType.BUTLER   # 🎩 효율적, 충성
SpeciesType.ATHLETE  # 💪 활동적, 에너지
```

### DNA

```python
from babyhippo import DNA, SpeciesType

# DNA 생성
dna = DNA(SpeciesType.QUOKKA)

# 특성 조회
print(dna.traits['drive_weights'])
print(dna.traits['emotional_bias'])
print(dna.traits['reflex_patterns'])

# DNA 정보 출력
print(dna.get_dna_info())
```

### FundamentalLaws

```python
from babyhippo import FundamentalLaws

# 금기어 목록
print(FundamentalLaws.TABOOS)

# 생존 우선순위
print(FundamentalLaws.SURVIVAL_PRIORITY)

# 생체 리듬
print(FundamentalLaws.CIRCADIAN_RHYTHM)
```

---

## Utility Functions

### Storage

```python
from babyhippo import save_memory, load_memory, list_memory_files

# 기억 저장
save_memory(brain.memory, "my_memory.pkl")

# 기억 로드
memory = load_memory("my_memory.pkl")

# 저장된 파일 목록
files = list_memory_files()
```

### Utils

```python
from babyhippo import normalize, cosine_similarity, text_to_vector

# 정규화
value = normalize(0.5, min_val=0.0, max_val=1.0)

# 텍스트 벡터화
vec1 = text_to_vector("안녕하세요")
vec2 = text_to_vector("반갑습니다")

# 유사도 계산
similarity = cosine_similarity(vec1, vec2)
```

---

## Error Handling

```python
from babyhippo import BabyBrain

try:
    brain = BabyBrain(species="invalid_species")
except ValueError as e:
    print(f"잘못된 종 유형: {e}")

try:
    brain = BabyBrain()
    brain.load("nonexistent_path")
except FileNotFoundError as e:
    print(f"파일 없음: {e}")
```

---

## Type Hints

모든 클래스와 함수는 타입 힌트를 지원합니다:

```python
from typing import List, Dict, Optional
from babyhippo import BabyBrain

def create_ai(name: str, personality: str) -> BabyBrain:
    return BabyBrain(name=name, species=personality)

def process_memories(memories: List[Dict]) -> Optional[str]:
    if memories:
        return memories[0].get('content')
    return None
```

---

<p align="center">
  <em>For more examples, see the <code>examples/</code> directory.</em>
</p>

