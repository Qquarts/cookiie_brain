"""
Neural Core: 신경 기반 모듈
============================

🌊 철학:
    "실체는 입자(정지)가 아니라 파동(움직임)이다"
    "동역학(Dynamics)이 이 세계의 실체다"

모듈 구성:
- dynamics.py    - 동역학 엔진 (HH + STP/PTP) ⭐ NEW
- neuron_core.py - 기본 뉴런 모델
- synapse_core.py - STDP 시냅스
- hippo_lm.py    - STDP 언어 모델

Author: GNJz (Qquarts)
"""

# === 동역학 엔진 ===
from .dynamics import (
    # Configuration
    HHConfig,
    STPConfig,
    NoiseConfig,
    NeuronState,
    # Core Classes
    DynamicNeuron,
    DynamicSynapse,
    SubiculumIntegrator,
    NoiseGenerator,
    # Functions
    apply_wta,
    create_neuron_population,
    create_synapse_matrix,
)

# === 자기조직화 ===
from .self_organization import (
    Pattern,
    CompetitiveLearning,
    HebbianCluster,
    PatternMemory,
)

# === 수면/각성 사이클 (NEW) ===
from .sleep_wake import (
    SleepStage,
    SleepConfig,
    ReplayEvent,
    SleepWakeCycle,
    SleepManager,
)

# === 정확한 HH 뉴런 (v2: HHSomaQuick) ===
from .hh_soma_quick import HHSomaQuick

# === Izhikevich 뉴런 (v3: 대규모 네트워크용) ===
from .izhikevich_neuron import (
    IzhikevichNeuron,
    IZHIKEVICH_PRESETS,
)

# === HH LIF 뉴런 (v4: HH 기반 단순화) ===
from .hh_lif_neuron import (
    HHLIFNeuron,
    HH_LIF_CONFIG,
)

# === 도약전도 PDE Axon (v5: Saltatory Conduction) ===
from .myelinated_axon import (
    MyelinatedAxon,
    MYELINATED_AXON_CONFIG,
)

# === 기존 뉴런 (이제 HHSomaQuick 사용) ===
from .neuron_core import (
    DGNeuron, 
    CA3Neuron, 
    CA1TimeCell, 
    CA1NoveltyDetector, 
    SubiculumGate,
    BabyNeuron,  # 호환성 유지
    HH_CONFIG,   # HH 설정
)

# === 시냅스 ===
from .synapse_core import STDPSynapse, reset_all_synapses

# === 언어 모델 ===
from .hippo_lm import HippoLM

__all__ = [
    # === Dynamics Engine ===
    "HHConfig",
    "STPConfig", 
    "NoiseConfig",
    "NeuronState",
    "DynamicNeuron",
    "DynamicSynapse",
    "SubiculumIntegrator",
    "NoiseGenerator",
    "apply_wta",
    "create_neuron_population",
    "create_synapse_matrix",
    
    # === Self-Organization ===
    "Pattern",
    "CompetitiveLearning",
    "HebbianCluster",
    "PatternMemory",
    
    # === Sleep-Wake Cycle (NEW) ===
    "SleepStage",
    "SleepConfig",
    "ReplayEvent",
    "SleepWakeCycle",
    "SleepManager",
    
    # === 뉴런 모델 버전별 ===
    # v2: 정확한 HH 뉴런 (HHSomaQuick)
    "HHSomaQuick",
    "HH_CONFIG",
    
    # v3: Izhikevich 뉴런 (대규모 네트워크용)
    "IzhikevichNeuron",
    "IZHIKEVICH_PRESETS",
    
    # v4: HH LIF 뉴런 (HH 기반 단순화)
    "HHLIFNeuron",
    "HH_LIF_CONFIG",
    
    # v5: 도약전도 PDE Axon (Saltatory Conduction)
    "MyelinatedAxon",
    "MYELINATED_AXON_CONFIG",
    
    # === 해마 뉴런 (HHSomaQuick 사용) ===
    "DGNeuron",
    "CA3Neuron",
    "CA1TimeCell",
    "CA1NoveltyDetector",
    "SubiculumGate",
    "BabyNeuron",  # 호환성 유지
    
    # === Synapses ===
    "STDPSynapse",
    "reset_all_synapses",
    
    # === Language Model ===
    "HippoLM",
]

