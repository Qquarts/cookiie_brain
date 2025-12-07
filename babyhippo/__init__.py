"""
🧠 babyhippo - Bio-inspired AI Memory System
=============================================

생물학적 뇌 구조를 모방한 AI 기억 시스템

모듈 구조:
- brain/       : 뇌 구조 (전두엽, 시상, 편도체 등)
- memory/      : 기억 시스템 (해마, 기억순위 등)
- neural/      : 신경 기반 (뉴런, 시냅스, STDP)
- cortex/      : 피질 (감각 처리)
- body/        : 말초 신경계 (감각/행동 인터페이스) 🆕
- integration/ : 통합 시스템 (BabyBrain, LiteBrain 등)
- utils/       : 유틸리티

Author: GNJz (Qquarts)
Version: 4.3.0 (Cookiie v1.0 - 1st Cookiie Revolution)
"""

__version__ = "4.3.0"
__author__ = "GNJz (Qquarts)"

# ============================================================
# 🧬 Configuration (DNA 설정)
# ============================================================
from .config import (
    DNA,
    SpeciesType,
    FundamentalLaws,
    create_dna,
)

# ============================================================
# 🧠 Brain Structures (뇌 구조)
# ============================================================
from .brain import (
    # Prefrontal (전두엽)
    PrefrontalCortex,
    # Cingulate (대상피질)
    CingulateCortex,
    ErrorSignal,
    ConflictSignal,
    ControlSignal,
    # Thalamus (시상)
    Thalamus,
    SensoryInput,
    FilteredOutput,
    ModalityType,
    # Hypothalamus (시상하부)
    Hypothalamus,
    DriveType,
    InternalState,
    DriveSignal,
    # Basal Ganglia (기저핵)
    BasalGanglia,
    Action,
    ActionResult,
    ActionType,
    # Amygdala (편도체)
    Amygdala,
    EmotionState,
    ThreatSignal,
    FearMemory,
    # Cerebellum (소뇌)
    Cerebellum,
    # Brain Graph
    BrainGraph,
    create_brain,
)

# ============================================================
# 💾 Memory Systems (기억 시스템)
# ============================================================
from .memory import (
    HippoMemory,
    MemoryRank,
    apply_memory_rank,
    ConversationMemory,
    CoreMemory,
    detect_memory_request,
    detect_important_concept,
    PersistentWorkingMemory,
    create_working_memory,
    detect_code_in_message,
    PanoramaMemory,
    CodeBrain,
    create_code_brain,
)

# ============================================================
# ⚡ Neural Core (신경 기반)
# ============================================================
from .neural import (
    DGNeuron,
    CA3Neuron,
    CA1TimeCell,
    CA1NoveltyDetector,
    SubiculumGate,
    STDPSynapse,
    reset_all_synapses,
    HippoLM,
)

# ============================================================
# 👁️ Cortex (피질)
# ============================================================
from .cortex import (
    CortexNode,
    VisualCortex,
    AuditoryCortex,
    EmotionalCortex,
    SemanticCortex,
    EpisodicCortex,
)

# ============================================================
# 🤖 Body (말초 신경계) 🆕
# ============================================================
from .body import (
    Senses,
    EyeInput,
    EarInput,
    TextInput,
    SensorType,
    Actions,
    SpeechOutput,
    TextOutput,
    MotorOutput,
    ActionType as BodyActionType,  # brain.ActionType과 구분
    NervousSystem,
    BodyState,
)

# ============================================================
# 🎯 Integration (통합 시스템)
# ============================================================
from .integration import (
    BabyBrain,
    LiteBrain,
    CuriousBrain,
    LibraryConnector,
    BrainLLM,
    DreamManager,  # 🆕
)

# ============================================================
# 🔧 Utils (유틸리티)
# ============================================================
from .utils import (
    Storage,
    text_to_vector,
    cosine_similarity,
    simple_hash,
    generate_uid,
    korean_tokenize,
    extract_keywords,
    normalize_korean,
    smart_truncate,
    StimulusAccumulator,
)

# ============================================================
# Public API
# ============================================================
__all__ = [
    # Version
    "__version__",
    "__author__",
    
    # Brain Structures
    "PrefrontalCortex",
    "CingulateCortex",
    "ErrorSignal",
    "ConflictSignal",
    "ControlSignal",
    "Thalamus",
    "SensoryInput",
    "FilteredOutput",
    "ModalityType",
    "Hypothalamus",
    "DriveType",
    "InternalState",
    "DriveSignal",
    "BasalGanglia",
    "Action",
    "ActionResult",
    "ActionType",
    "Amygdala",
    "EmotionState",
    "ThreatSignal",
    "FearMemory",
    "Cerebellum",
    "BrainGraph",
    "create_brain",
    
    # Memory Systems
    "HippoMemory",
    "MemoryRank",
    "apply_memory_rank",
    "ConversationMemory",
    "CoreMemory",
    "detect_memory_request",
    "detect_important_concept",
    "PersistentWorkingMemory",
    "create_working_memory",
    "detect_code_in_message",
    "PanoramaMemory",
    "CodeBrain",
    "create_code_brain",
    
    # Neural Core
    "DGNeuron",
    "CA3Neuron",
    "CA1TimeCell",
    "CA1NoveltyDetector",
    "SubiculumGate",
    "STDPSynapse",
    "reset_all_synapses",
    "HippoLM",
    
    # Cortex
    "CortexNode",
    "VisualCortex",
    "AuditoryCortex",
    "EmotionalCortex",
    "SemanticCortex",
    "EpisodicCortex",
    
    # Body (말초 신경계) 🆕
    "Senses",
    "EyeInput",
    "EarInput",
    "TextInput",
    "SensorType",
    "Actions",
    "SpeechOutput",
    "TextOutput",
    "MotorOutput",
    "BodyActionType",
    "NervousSystem",
    "BodyState",
    
    # Integration
    "BabyBrain",
    "LiteBrain",
    "CuriousBrain",
    "LibraryConnector",
    "BrainLLM",
    "DreamManager",  # 🆕
    
    # Utils
    "Storage",
    "text_to_vector",
    "cosine_similarity",
    "simple_hash",
    "generate_uid",
    "korean_tokenize",
    "extract_keywords",
    "normalize_korean",
    "smart_truncate",
    "StimulusAccumulator",
    
    # Config (DNA)
    "DNA",
    "SpeciesType",
    "FundamentalLaws",
    "create_dna",
]


def get_version():
    """버전 정보 반환"""
    return __version__


def info():
    """패키지 정보 출력"""
    print(f"""
🧠 babyhippo v{__version__}
========================
Bio-inspired AI Memory System

📦 모듈 구조:
  - brain/       : 뇌 구조 (10개)
  - memory/      : 기억 시스템 (7개)
  - neural/      : 신경 기반 (3개)
  - cortex/      : 피질 (1개)
  - integration/ : 통합 (4개)
  - utils/       : 유틸 (3개)

🚀 시작하기:
  from babyhippo import BabyBrain
  brain = BabyBrain(name="MyAI")
  brain.chat("안녕!")

📖 문서: https://github.com/qquarts/babyhippo
""")
