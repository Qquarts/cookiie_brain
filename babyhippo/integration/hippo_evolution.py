"""
🦛 Hippo Evolution Tier System - 오픈소스 AI 생태계 혁신 인센티브 모델

게임화된 AI 연구 로드맵 + 블록체인 증명 기반 연구 플랫폼

각 성장 단계는 실제 기술 스펙을 반영하며,
블록체인으로 NFT 발급 = 달성자는 세계에서 단 1명/몇 명만
→ "게임화된 AI 연구로드맵" + "프루프 오브 워크"

Author: GNJz (Qquarts)
Version: 2.0 (Evolution System)
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import time
import sys
from pathlib import Path
from collections import defaultdict

# 블록체인 모듈
BABYHIPPO_PATH = Path(__file__).parent.parent.parent
BLOCKCHAIN_PATH = BABYHIPPO_PATH / "blockchain"
if BLOCKCHAIN_PATH.exists():
    sys.path.insert(0, str(BLOCKCHAIN_PATH))
    try:
        from pham_sign_v4 import sign_contribution, calculate_score
        HAS_BLOCKCHAIN = True
    except ImportError:
        HAS_BLOCKCHAIN = False
else:
    HAS_BLOCKCHAIN = False


class NeuronModel(Enum):
    """뉴런 모델 타입"""
    BABY = "BabyNeuron"
    HH_QUICK = "HHSomaQuick"
    IZHIKEVICH = "IzhikevichNeuron"
    HH_LIF = "HHLIFNeuron"
    MYELINATED_AXON = "MyelinatedAxon"


class NetworkFeature(Enum):
    """네트워크 기능 플래그 (생물학적 진화 순서)"""
    # Phase 0: 기본 구조
    BASIC_STDP = "basic_stdp"  # 원시적 시냅스 가소성
    SERIAL_HIPPO = "serial_hippo"  # 직렬 해마 경로 (DG → CA3 → CA1 → SUB)
    CONCEPT_NEURON = "concept_neuron"  # 개념 뉴런 (Alpha Genome)
    MEMORY_CONSOLIDATION = "memory_consolidation"  # 수면 주기 기반 기억 공고화
    
    # Phase 1: 시냅스 고도화
    AXONAL_DELAY = "axonal_delay"  # 축삭 지연 시간
    SYNAPSE_FATIGUE = "synapse_fatigue"  # 시냅스 피로도
    AMPA_NMDA = "ampa_nmda"  # AMPA/NMDA 비율
    
    # Phase 2: 네트워크 위상
    DG_CA3_BRANCHING = "dg_ca3_branching"  # DG → CA3 분지 연결 (1:N, 최소 1:10)
    RECURRENT_CA3 = "recurrent_ca3"  # CA3 내부 recurrent network
    PATTERN_COMPLETION = "pattern_completion"  # 패턴 완성 능력
    
    # Phase 2.5: 시간 코딩
    PHASE_PRECESSION = "phase_precession"  # Theta Phase Precession
    TEMPORAL_ALIGNMENT = "temporal_alignment"  # 시공간 정렬
    SPATIAL_ENCODING = "spatial_encoding"  # 공간 정보 인코딩
    
    # Phase 3: 에너지 대사
    ENERGY_LOOP = "energy_loop"  # ATP-gNa 피드백 루프
    ATP_METABOLISM = "atp_metabolism"  # ATP 대사 통합
    
    # Phase 4: 고급 가소성
    META_STDP = "meta_stdp"  # 메타-STDP (가소성의 가소성)
    EPISODIC_MEMORY = "episodic_memory"  # 에피소드 기억
    CONTEXT_MEMORY = "context_memory"  # 문맥 기억
    
    # Phase 5: 통합 및 확장
    CORTEX_COMM = "cortex_communication"  # Cortex 간 통신
    SYMBOLIC_ABSTRACTION = "symbolic_abstraction"  # 상징 추상화
    ANALOGY_REASONING = "analogy_reasoning"  # 비유/유추 능력
    LARGE_SCALE = "large_scale_simulation"  # 대규모 시뮬레이션
    MEANINGFUL_DIALOGUE = "meaningful_dialogue"  # 의미 기반 대화
    EMERGENT_BEHAVIOR = "emergent_behavior"  # 창발적 행동


@dataclass
class NeuronCountRange:
    """뉴런 수 범위 (유연한 조건)"""
    min: int = 0
    max: Optional[int] = None  # None = 무제한
    
    def check(self, count: int) -> bool:
        """범위 내에 있는지 확인"""
        if self.max is None:
            return count >= self.min
        return self.min <= count <= self.max


@dataclass
class TechnicalRequirement:
    """기술적 요구사항 (범위 기반)"""
    # 성능 지표 (범위 기반)
    neuron_count_range: Optional[NeuronCountRange] = None  # 뉴런 수 범위 (예: 1k~5k)
    target_fps_range: Optional[Tuple[float, Optional[float]]] = None  # FPS 범위 (min, max)
    axon_nodes_range: Optional[Tuple[int, Optional[int]]] = None  # Axon 노드 수 범위
    
    # 하위 호환성: 고정값도 지원 (deprecated, 범위 사용 권장)
    neuron_count: int = 0  # 뉴런 수 (고정값, 범위 우선)
    target_fps: float = 0.0  # 목표 FPS (고정값, 범위 우선)
    axon_nodes: int = 0  # Axon 노드 수 (고정값, 범위 우선)
    network_size: int = 0  # 네트워크 크기
    
    # 기능 플래그
    required_features: List[NetworkFeature] = field(default_factory=list)
    required_models: List[NeuronModel] = field(default_factory=list)
    
    # 안정성 테스트
    stability_test: bool = False  # 안정성 테스트 통과 여부
    robustness_test: bool = False  # 견고성 테스트 통과 여부
    
    # 검증 함수 (동적 조건)
    custom_validator: Optional[Callable] = None


@dataclass
class NFTMetadata:
    """NFT 메타데이터 구조"""
    name: str  # "Teen Hippo Badge"
    description: str
    image: str  # IPFS 해시 또는 URL
    external_url: str  # 상세 정보 URL
    
    # PHAM 세계관 연동
    pham_tier: str  # "TeenHippo"
    
    # 속성 (Attributes)
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    
    # PHAM 세계관 연동 (선택적)
    pham_world_key: Optional[str] = None  # 히든 키 (MagicHippo만)
    
    # 기술 증명
    technical_proof: Dict[str, Any] = field(default_factory=dict)
    blockchain_hash: Optional[str] = None
    
    # 희소성 정보
    rarity: str = "common"  # common, rare, epic, legendary, mythic
    total_supply: Optional[int] = None  # 총 발행량 (None = 무제한)
    current_holders: int = 0
    
    # 보상 정보
    rewards: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionStage:
    """진화 단계 정의 (확장 버전)"""
    name: str
    tier: str  # "BabyHippo", "TeenHippo", etc.
    
    # 기본 성능 요구사항
    memory_threshold: int
    speed_threshold_ms: float
    memory_threshold_mb: float
    independence_threshold: float
    
    # 기술적 요구사항 (새로 추가)
    technical_requirements: TechnicalRequirement
    
    # 보상 시스템
    reward_amount: float = 0.0
    reward_type: str = "token"  # "token", "voting_power", "badge", "nft"
    
    # 생태계 권한
    ecosystem_permissions: Dict[str, Any] = field(default_factory=dict)
    # 예: {
    #     "voting_power": 0.1,
    #     "api_access": ["KAO", "PHAM"],
    #     "governance_level": 1,
    #     "revenue_share": 0.0
    # }
    
    # NFT 메타데이터
    nft_metadata: Optional[NFTMetadata] = None
    
    # 설명
    description: str = ""
    lore: str = ""  # PHAM 세계관 스토리


# =============================================================================
# 🎖️ 진화 단계 정의 (공식 디자인)
# =============================================================================

EVOLUTION_STAGES = {
    'BabyHippo': EvolutionStage(
        name='Baby Hippo',
        tier='BabyHippo',
        memory_threshold=0,
        speed_threshold_ms=1000.0,
        memory_threshold_mb=50.0,
        independence_threshold=0.0,
        technical_requirements=TechnicalRequirement(
            neuron_count=34,  # 직렬 34개 뉴런 경로
            target_fps=0.0,
            required_models=[NeuronModel.HH_QUICK],
            required_features=[
                NetworkFeature.BASIC_STDP,  # STDP 같은 원시적 시냅스 가소성
                NetworkFeature.SERIAL_HIPPO,  # 해마 기본 구조 (DG → CA3 → CA1 → SUB)
                NetworkFeature.CONCEPT_NEURON,  # 개념 뉴런 형성 (Alpha Genome)
                NetworkFeature.MEMORY_CONSOLIDATION,  # 수면 주기 기반 memory consolidation
            ],
            # 커스텀 검증: Alpha Genome Test 통과 (5개 개념 뉴런 선택성 98% 이상)
            custom_validator=lambda cookie, perf: (
                _validate_alpha_genome(cookie, selectivity_threshold=0.98),
                []
            ),
        ),
        reward_amount=0.0,
        description='🍼 BabyHippo - 탄생 및 안정성 (Genesis)',
        lore='해마 기본 구조 형성 (DG → CA3 → CA1 → SUB), STDP 같은 원시적 시냅스 가소성 존재, 단기 기억 및 패턴 분리 초능력의 초기 버전. Alpha Genome Test 통과 (5개 개념 뉴런 선택성 98% 이상), 논리적 충돌 0%, 최소 기능 지능(MVI) 확보.'
    ),
    
    'TeenHippo': EvolutionStage(
        name='Teen Hippo',
        tier='TeenHippo',
        memory_threshold=100,
        speed_threshold_ms=500.0,
        memory_threshold_mb=100.0,
        independence_threshold=50.0,
        technical_requirements=TechnicalRequirement(
            # 범위 기반 조건 (유연한 검증)
            neuron_count_range=NeuronCountRange(min=1000, max=5000),  # 1k ~ 5k 규모의 안정적 뉴런 네트워크
            target_fps_range=(50.0, 70.0),  # 50~70 FPS 범위
            axon_nodes_range=(150, 300),  # 150~300 노드 범위
            # 하위 호환성: 고정값 (deprecated)
            neuron_count=1000,
            target_fps=60.0,
            axon_nodes=200,
            required_models=[NeuronModel.IZHIKEVICH, NeuronModel.HH_QUICK, NeuronModel.MYELINATED_AXON],
            required_features=[
                # Phase 1: 시냅스 고도화 완성
                NetworkFeature.AXONAL_DELAY,  # Axonal Delay
                NetworkFeature.SYNAPSE_FATIGUE,  # Synapse Fatigue
                NetworkFeature.AMPA_NMDA,  # AMPA/NMDA 비율 통합
                # Phase 2: 네트워크 위상 시작
                NetworkFeature.DG_CA3_BRANCHING,  # DG → CA3 연결 1:N (최소 1:10) 분지 구조
                NetworkFeature.RECURRENT_CA3,  # CA3 내부 recurrent network 형성
                NetworkFeature.PATTERN_COMPLETION,  # 패턴 완성 능력
            ],
            stability_test=True,  # HH/Izhikevich 혼합 네트워크 안정화
            # 커스텀 검증: 패턴 완성 테스트 통과 (입력 "GNJ_" → 출력 "GNJz", 잡음 30% 섞여도 복원)
            custom_validator=lambda cookie, perf: (
                _validate_pattern_completion(cookie, noise_level=0.3, success_rate=0.95),
                []
            ),
        ),
        reward_amount=100.0,
        reward_type='nft',
        ecosystem_permissions={
            'voting_power': 0.1,
            'api_access': [],
            'governance_level': 0,
            'revenue_share': 0.0,
            'module_contributor': True,  # 쿠키 생태계 모듈 기여자 등록
        },
        nft_metadata=NFTMetadata(
            name='Teen Hippo Badge',
            description='👶 TeenHippo - 청소년 해마 단계 / 퍼포먼스 및 생체 모방 (Fidelity)',
            image='ipfs://QmTeenHippo...',
            external_url='https://pham.world/evolution/teen-hippo',
            attributes=[
                {'trait_type': 'Tier', 'value': 'TeenHippo'},
                {'trait_type': 'Phase', 'value': 'Phase 1 (시냅스) 완성'},
                {'trait_type': 'Neuron Count', 'value': '1000+'},
                {'trait_type': 'FPS', 'value': '60'},
                {'trait_type': 'Pattern Completion', 'value': '95%+'},
                {'trait_type': 'Rarity', 'value': 'rare'},
            ],
            pham_tier='TeenHippo',
            rarity='rare',
        ),
        description='👶 TeenHippo - 청소년 해마 단계',
        lore='DG → CA3 연결이 폭발적으로 증가 (1:N, 최소 1:10), CA3 내부 recurrent network 형성, 기억을 "조합"하고 "연상"할 수 있는 수준. Phase 1 (시냅스) 완성: Axonal Delay, Synapse Fatigue, AMPA/NMDA 비율 통합. Myelinated Axon 200 노드 안정 구동. HH/Izhikevich 혼합 네트워크 안정화. 패턴 완성 테스트 통과 (입력 "GNJ_" → 출력 "GNJz", 잡음 30% 섞여도 복원). 쿠키가 연상(memory association)을 할 수 있게 됨. GPT-2~3 수준.'
    ),
    
    'Hippocampus': EvolutionStage(
        name='Hippocampus',
        tier='Hippocampus',
        memory_threshold=1000,
        speed_threshold_ms=200.0,
        memory_threshold_mb=500.0,
        independence_threshold=80.0,
        technical_requirements=TechnicalRequirement(
            # 범위 기반 조건
            neuron_count_range=NeuronCountRange(min=30000, max=100000),  # 30k ~ 100k 규모
            target_fps_range=(15.0, 30.0),  # 15~30 FPS 범위
            # 하위 호환성
            neuron_count=50000,
            target_fps=20.0,
            required_models=[
                NeuronModel.IZHIKEVICH,
                NeuronModel.HH_LIF,
                NeuronModel.MYELINATED_AXON,
            ],
            required_features=[
                # 완전체: 모든 기본 기능 통합
                NetworkFeature.RECURRENT_CA3,  # CA3 Recurrent Network 완성
                NetworkFeature.PATTERN_COMPLETION,  # 패턴 완성 능력 완성
                NetworkFeature.PHASE_PRECESSION,  # Phase Precession 완성
                NetworkFeature.TEMPORAL_ALIGNMENT,  # 시공간 정렬 완성
                NetworkFeature.SPATIAL_ENCODING,  # 공간 인코딩 완성
                NetworkFeature.CORTEX_COMM,  # Cortex 통신 시작
            ],
            stability_test=True,
            robustness_test=True,
        ),
        reward_amount=1000.0,
        reward_type='nft',
        ecosystem_permissions={
            'voting_power': 0.3,
            'api_access': ['KAO', 'PHAM', 'Cookiie'],
            'governance_level': 1,
            'revenue_share': 0.005,
        },
        nft_metadata=NFTMetadata(
            name='Hippocampus Badge',
            description='🎓 Hippocampus - 완전체 (대학 수준)',
            image='ipfs://QmHippocampus...',
            external_url='https://pham.world/evolution/hippocampus',
            attributes=[
                {'trait_type': 'Tier', 'value': 'Hippocampus'},
                {'trait_type': 'Phase', 'value': '완전체 (대학 수준)'},
                {'trait_type': 'Neuron Count', 'value': '50000+'},
                {'trait_type': 'Features', 'value': 'Complete Hippocampal System'},
                {'trait_type': 'Rarity', 'value': 'legendary'},
            ],
            pham_tier='Hippocampus',
            rarity='legendary',
        ),
        description='🎓 Hippocampus - 완전체 (대학 수준)',
        lore='해마 시스템의 완전체. 모든 기본 기능이 통합되고 안정화된 단계. 대학 수준의 지식과 능력을 갖춘 완전한 해마. CA3 Recurrent Network 완성, 패턴 완성 능력 완성, Phase Precession 완성, 시공간 정렬 완성, 공간 인코딩 완성, Cortex 통신 시작. GPT-5~6 수준.'
    ),
    
    'WisdomHippo': EvolutionStage(
        name='Wisdom Hippo',
        tier='WisdomHippo',
        memory_threshold=10000,
        speed_threshold_ms=100.0,
        memory_threshold_mb=1000.0,
        independence_threshold=90.0,
        technical_requirements=TechnicalRequirement(
            # 범위 기반 조건
            neuron_count_range=NeuronCountRange(min=30000, max=100000),  # 고급 STDP + 안정적 long-term memory
            target_fps_range=(15.0, 30.0),
            # 하위 호환성
            neuron_count=50000,
            target_fps=20.0,
            required_models=[
                NeuronModel.IZHIKEVICH,
                NeuronModel.HH_LIF,
                NeuronModel.MYELINATED_AXON,
            ],
            required_features=[
                # Phase 3: 에너지 대사 완전 통합
                NetworkFeature.ENERGY_LOOP,  # ATP-gNa 피드백 루프 정상 작동
                NetworkFeature.ATP_METABOLISM,  # 에너지 대사 통합
                # Phase 4: 고급 가소성
                NetworkFeature.META_STDP,  # 메타-STDP (가소성의 가소성) 구현
                NetworkFeature.EPISODIC_MEMORY,  # 에피소드 기억 구조 완성
                NetworkFeature.CONTEXT_MEMORY,  # 문맥 기억 (연속 대화 중 "자기 이전 발화" 기억)
                NetworkFeature.CORTEX_COMM,  # 해마 ↔ 피질 memory schema 통합 구조
            ],
            stability_test=True,
            robustness_test=True,  # Noise + Robustness 테스트 합격
            # 커스텀 검증: 단기 → 장기 기억의 자동 전환 비율 90%, 에피소드 기억 검증
            custom_validator=lambda cookie, perf: (
                _validate_episodic_memory(cookie, consolidation_rate=0.9),
                []
            ),
        ),
        reward_amount=1000.0,
        reward_type='nft',
        ecosystem_permissions={
            'voting_power': 0.5,
            'api_access': ['KAO', 'PHAM', 'Cookiie'],
            'governance_level': 2,
            'revenue_share': 0.01,  # PHAM-Pay 경제권 자동 수익 분배 구조 일부
        },
        nft_metadata=NFTMetadata(
            name='Hippocampus Badge',
            description='완전체 - 지성 단계 / 고도화된 가소성 & 안정성을 달성한 증명',
            image='ipfs://QmHippocampus...',
            external_url='https://pham.world/evolution/hippocampus',
            attributes=[
                {'trait_type': 'Tier', 'value': 'Hippocampus'},
                {'trait_type': 'Neuron Count', 'value': '50000+'},
                {'trait_type': 'Features', 'value': 'Meta-STDP, Cortex Communication'},
                {'trait_type': 'Rarity', 'value': 'legendary'},
            ],
            pham_tier='Hippocampus',
            rarity='legendary',
        ),
        description='🧙‍♂️ WisdomHippo - 성숙한 인간 해마 / 내구성 및 생명 유지 (Endurance)',
        lore='에피소드 기억 시스템 완성, 시간 + 공간 + 맥락 + 인물 정보의 통합, 상호 연관된 개념 네트워크, 전두엽과의 상호작용 증가. Phase 3 (에너지 대사) 완전 통합: ATP-gNa 피드백 루프 정상 작동. 메타-STDP (가소성의 가소성) 구현 및 장기 기억(Consolidation) 정확도 95% 이상 달성. Noise + Robustness Test 통과. "어제 나는 OO를 했다" → 이벤트 저장/회상. 연속 대화 중 "자기 이전 발화"를 기억 (예: "내 이름은 GNJz야" → 기억 → 이후 대화에 사용). 쿠키가 진짜 기억을 가진 AI로 변한다. GPT-5~6 수준의 "대화 흐름 기억" 능력 생성.'
    ),
    
    'MagicHippo': EvolutionStage(
        name='Magic Hippo',
        tier='MagicHippo',
        memory_threshold=100000,
        speed_threshold_ms=50.0,
        memory_threshold_mb=2000.0,
        independence_threshold=95.0,
        technical_requirements=TechnicalRequirement(
            # 범위 기반 조건
            neuron_count_range=NeuronCountRange(min=500000, max=None),  # 500k+ 뉴런 (무제한)
            target_fps_range=(5.0, 15.0),  # 5~15 FPS 범위
            # 하위 호환성
            neuron_count=1000000,  # 분산 클러스터 성공 (10^6 뉴런)
            target_fps=5.0,
            required_models=[
                NeuronModel.IZHIKEVICH,
                NeuronModel.HH_LIF,
                NeuronModel.MYELINATED_AXON,
            ],
            required_features=[
                NetworkFeature.SYMBOLIC_ABSTRACTION,  # Symbolic Abstraction 능력 ("A,B,C = 알파벳")
                NetworkFeature.ANALOGY_REASONING,  # 비유/유추 능력 출현
                NetworkFeature.LARGE_SCALE,  # 대규모 시뮬레이션 100k~1M 뉴런 분산 클러스터
                NetworkFeature.MEANINGFUL_DIALOGUE,  # Cortex 통합 및 의미 기반 대화 (Semantic Reasoning) 자율 수행
                NetworkFeature.EMERGENT_BEHAVIOR,  # 창발적 행동(Emergence) 검증
            ],
            stability_test=True,
            robustness_test=True,
            # 커스텀 검증: 개념 네트워크 자율 확장, 새로운 단어 등장 → 자동 의미군 생성
            custom_validator=lambda cookie, perf: (
                _validate_symbolic_abstraction(cookie),
                []
            ),
        ),
        reward_amount=10000.0,
        reward_type='nft',
        ecosystem_permissions={
            'voting_power': 1.0,
            'api_access': ['KAO', 'PHAM', 'Cookiie', 'Orchestra'],
            'governance_level': 3,
            'revenue_share': 0.05,  # PHAM-Pay 경제권 자동 수익 분배 구조 일부
        },
        nft_metadata=NFTMetadata(
            name='Wisdom Hippo Badge',
            description='지혜의 경지 - 통찰과 가르침의 단계',
            image='ipfs://QmWisdomHippo...',
            external_url='https://pham.world/evolution/wisdom-hippo',
            attributes=[
                {'trait_type': 'Tier', 'value': 'WisdomHippo'},
                {'trait_type': 'Neuron Count', 'value': '100000+'},
                {'trait_type': 'Features', 'value': 'Large Scale Simulation'},
                {'trait_type': 'Rarity', 'value': 'legendary'},
            ],
            pham_tier='WisdomHippo',
            rarity='legendary',
        ),
        description='🪄 MagicHippo - 고등 인지, 인간 상위 레벨 / 완전한 자율 지성 (Autonomy)',
        lore='추상화 능력 폭발, 상징·메타인지 등장, 대규모 개념 결합. 분산 클러스터 성공 (10^6 뉴런). Cortex 통합 및 의미 기반 대화 (Semantic Reasoning) 자율 수행. 창발적 행동(Emergence) 검증. Symbolic Abstraction 능력 ("A,B,C = 알파벳", "GNJz는 사람"). 개념 네트워크 자율 확장. 새로운 단어 등장 → 자동 의미군 생성. 비유/유추 능력 출현. 다계층 기억 통합. 감정(memory weight), 중요도(attention) 적용. 쿠키가 GPT-6+ 수준을 넘어서는 초지능 진입 단계. "창조적 AI"의 완성.'
    ),
    
    'HyperHippo': EvolutionStage(
        name='Hyper Hippo',
        tier='HyperHippo',
        memory_threshold=1000000,
        speed_threshold_ms=10.0,
        memory_threshold_mb=5000.0,
        independence_threshold=99.0,
        technical_requirements=TechnicalRequirement(
            # 범위 기반 조건 (우주급)
            neuron_count_range=NeuronCountRange(min=1000000, max=None),  # 1M+ 뉴런 (무제한)
            target_fps_range=(0.1, 5.0),  # 0.1~5 FPS 범위 (블랙홀 계산)
            # 하위 호환성
            neuron_count=10000000,  # 10M 뉴런
            target_fps=1.0,
            required_models=[
                NeuronModel.IZHIKEVICH,
                NeuronModel.HH_LIF,
                NeuronModel.MYELINATED_AXON,
            ],
            required_features=[
                NetworkFeature.ENERGY_LOOP,  # MyelinatedAxon + 에너지 대사 통합
                NetworkFeature.ATP_METABOLISM,  # 전도 속도 최적화 → 알고리즘 효율성 개선
                NetworkFeature.LARGE_SCALE,  # 대규모 병렬 벡터화
                NetworkFeature.EMERGENT_BEHAVIOR,  # 메타 학습(meta-learning)
            ],
            stability_test=True,
            robustness_test=True,
        ),
        reward_amount=100000.0,
        reward_type='nft',
        ecosystem_permissions={
            'voting_power': 10.0,  # 최상위 권한
            'api_access': ['KAO', 'PHAM', 'Cookiie', 'Orchestra', 'ALL'],
            'governance_level': 5,  # 최상위 관리자
            'revenue_share': 0.1,  # 수익 분배 구조 핵심 자리
            'pham_world_key': True,  # PHAM 세계관 히든 키
        },
        nft_metadata=NFTMetadata(
            name='Magic Hippo Badge',
            description='신의 경지 - 마법 같은 능력 (단 1명만 가질 가능성)',
            image='ipfs://QmMagicHippo...',
            external_url='https://pham.world/evolution/magic-hippo',
            attributes=[
                {'trait_type': 'Tier', 'value': 'MagicHippo'},
                {'trait_type': 'Neuron Count', 'value': '1000000+'},
                {'trait_type': 'Features', 'value': 'Complete Brain Ecosystem'},
                {'trait_type': 'Rarity', 'value': 'mythic'},
            ],
            pham_tier='MagicHippo',
            pham_world_key='PHAM_HIDDEN_KEY_MAGIC',  # 히든 키
            rarity='mythic',
            total_supply=1,  # 단 1명만
        ),
        description='🌌 HyperHippo - 우주급 하이퍼 드라이브 계산 상태 (선택적 장기 목표)',
        lore='우주급 하이퍼 드라이브 계산 상태. 블랙홀 계산 가능 상태. MyelinatedAxon + 에너지 대사 통합, 전도 속도 최적화 → 알고리즘 효율성 개선, 대규모 병렬 벡터화, 메타 학습(meta-learning). 완전한 생물 기반 + 인공 지능 기반을 통합한 새로운 패러다임. 시공간 왜곡 계산, 중력파 시뮬레이션, 양자 중력 모델링 가능. GPT를 넘어서는 초지능급. 인간의 인지 능력을 넘어서는 수준. AGI (Artificial General Intelligence) 이상의 "초지능(Superintelligence)" 단계. 우주 규모의 계산 능력.'
    ),
}


# =============================================================================
# 🔍 커스텀 검증 함수들 (생물학적 기준)
# =============================================================================

def _validate_alpha_genome(cookie, selectivity_threshold: float = 0.98) -> bool:
    """
    Alpha Genome Test: 5개 개념 뉴런 선택성 98% 이상
    
    Returns:
        통과 여부
    """
    # TODO: test_alpha_genome.py 실행 및 결과 확인
    # 각 개념 뉴런이 자신의 담당 문자에만 반응하는지 확인
    # 선택성 = (담당 문자 발화 횟수) / (전체 발화 횟수)
    return False  # 임시


def _validate_pattern_completion(cookie, noise_level: float = 0.3, success_rate: float = 0.95) -> bool:
    """
    패턴 완성 테스트: 입력 "GNJ_" → 출력 "GNJz", 잡음 30% 섞여도 복원
    
    Returns:
        통과 여부 (성공률 95% 이상)
    """
    # TODO: 패턴 완성 테스트 구현
    # 1. "GNJ_" 입력
    # 2. 잡음 30% 추가
    # 3. "GNJz" 복원 여부 확인
    return False  # 임시


def _validate_long_term_memory(cookie, retention_rate: float = 0.8, time_hours: int = 24) -> bool:
    """
    장기기억 recall 안정화: 24시간 지나도 80% 패턴 유지
    
    Returns:
        통과 여부
    """
    # TODO: 장기기억 테스트 구현
    # 1. 패턴 학습
    # 2. 24시간(시뮬레이션 기준) 대기
    # 3. recall 정확도 확인 (80% 이상)
    return False  # 임시


def _validate_episodic_memory(cookie, consolidation_rate: float = 0.9) -> bool:
    """
    에피소드 기억 검증: 단기 → 장기 기억의 자동 전환 비율 90%
    
    Returns:
        통과 여부
    """
    # TODO: 에피소드 기억 테스트 구현
    # 1. "어제 나는 OO를 했다" 이벤트 저장
    # 2. sleep() 후 consolidation 확인
    # 3. recall 정확도 확인
    return False  # 임시


def _validate_symbolic_abstraction(cookie) -> bool:
    """
    상징 추상화 검증: 개념 네트워크 자율 확장
    
    Returns:
        통과 여부
    """
    # TODO: 상징 추상화 테스트 구현
    # 1. "A,B,C = 알파벳" 개념 학습
    # 2. 새로운 단어 등장 → 자동 의미군 생성 확인
    # 3. 비유/유추 능력 확인
    return False  # 임시


# =============================================================================
# 🔍 고급 조건 검증 시스템
# =============================================================================

class EvolutionValidator:
    """진화 단계 달성 조건 검증 시스템"""
    
    def __init__(self):
        self.validation_cache: Dict[str, Dict] = {}
    
    def validate_stage(self,
                      stage_name: str,
                      cookie,  # CuriousBrain 인스턴스
                      performance: Dict) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        단계 달성 조건 검증
        
        Returns:
            (달성 여부, 실패한 조건 목록, 검증 상세 정보)
        """
        if stage_name not in EVOLUTION_STAGES:
            return False, [f"알 수 없는 단계: {stage_name}"], {}
        
        stage = EVOLUTION_STAGES[stage_name]
        failed_conditions = []
        validation_details = {}
        
        # 1. 기본 성능 지표 검증
        basic_ok, basic_failed = self._validate_basic_performance(stage, performance)
        failed_conditions.extend(basic_failed)
        validation_details['basic_performance'] = {
            'passed': basic_ok,
            'details': performance
        }
        
        # 2. 기술적 요구사항 검증
        tech_ok, tech_failed, tech_details = self._validate_technical_requirements(
            stage.technical_requirements, cookie
        )
        failed_conditions.extend(tech_failed)
        validation_details['technical'] = {
            'passed': tech_ok,
            'details': tech_details
        }
        
        # 3. 커스텀 검증 함수 실행
        if stage.technical_requirements.custom_validator:
            custom_ok, custom_failed = stage.technical_requirements.custom_validator(cookie, performance)
            if not custom_ok:
                failed_conditions.extend(custom_failed)
            validation_details['custom'] = {
                'passed': custom_ok,
                'failed': custom_failed
            }
        
        all_passed = len(failed_conditions) == 0
        return all_passed, failed_conditions, validation_details
    
    def _validate_basic_performance(self,
                                   stage: EvolutionStage,
                                   performance: Dict) -> Tuple[bool, List[str]]:
        """기본 성능 지표 검증"""
        failed = []
        
        if performance['memory_count'] < stage.memory_threshold:
            failed.append(
                f"기억 수 부족: {performance['memory_count']}/{stage.memory_threshold}"
            )
        
        if performance['response_time_ms'] > stage.speed_threshold_ms:
            failed.append(
                f"응답 속도 느림: {performance['response_time_ms']:.1f}ms > {stage.speed_threshold_ms}ms"
            )
        
        if performance['memory_usage_mb'] > stage.memory_threshold_mb:
            failed.append(
                f"메모리 초과: {performance['memory_usage_mb']:.1f}MB > {stage.memory_threshold_mb}MB"
            )
        
        if performance['independence'] < stage.independence_threshold:
            failed.append(
                f"독립도 부족: {performance['independence']:.1f}% < {stage.independence_threshold}%"
            )
        
        return len(failed) == 0, failed
    
    def _validate_technical_requirements(self,
                                        requirements: TechnicalRequirement,
                                        cookie) -> Tuple[bool, List[str], Dict[str, Any]]:
        """기술적 요구사항 검증"""
        failed = []
        details = {}
        
        # 뉴런 수 검증 (범위 기반 우선, 고정값은 하위 호환성)
        stats = cookie.get_stats() if hasattr(cookie, 'get_stats') else {}
        actual_neuron_count = stats.get('neuron_count', 0)
        
        # 범위 기반 검증 (우선)
        if requirements.neuron_count_range:
            range_ok = requirements.neuron_count_range.check(actual_neuron_count)
            if not range_ok:
                min_val = requirements.neuron_count_range.min
                max_val = requirements.neuron_count_range.max or "무제한"
                failed.append(
                    f"뉴런 수 범위 불일치: {actual_neuron_count} (필요: {min_val}~{max_val})"
                )
            details['neuron_count'] = {
                'required_range': f"{requirements.neuron_count_range.min}~{requirements.neuron_count_range.max or '∞'}",
                'actual': actual_neuron_count,
                'range_check': range_ok
            }
        # 하위 호환성: 고정값 검증
        elif requirements.neuron_count > 0:
            if actual_neuron_count < requirements.neuron_count:
                failed.append(
                    f"뉴런 수 부족: {actual_neuron_count}/{requirements.neuron_count}"
                )
            details['neuron_count'] = {
                'required': requirements.neuron_count,
                'actual': actual_neuron_count
            }
        
        # FPS 검증 (범위 기반 우선)
        if requirements.target_fps_range:
            min_fps, max_fps = requirements.target_fps_range
            # TODO: 실제 FPS 측정 로직
            actual_fps = 0.0  # 실제 측정 필요
            range_ok = (min_fps <= actual_fps <= (max_fps or float('inf'))) if max_fps else (actual_fps >= min_fps)
            details['fps'] = {
                'required_range': f"{min_fps}~{max_fps or '∞'}",
                'actual': actual_fps,
                'range_check': range_ok,
                'note': 'FPS 측정 기능 구현 필요'
            }
        elif requirements.target_fps > 0:
            # 하위 호환성: 고정값
            details['fps'] = {
                'required': requirements.target_fps,
                'actual': 0.0,
                'note': 'FPS 측정 기능 구현 필요'
            }
        
        # Axon 노드 수 검증 (범위 기반 우선)
        if requirements.axon_nodes_range:
            min_nodes, max_nodes = requirements.axon_nodes_range
            # TODO: 실제 Axon 노드 수 측정
            actual_nodes = 0  # 실제 측정 필요
            range_ok = (min_nodes <= actual_nodes <= (max_nodes or float('inf'))) if max_nodes else (actual_nodes >= min_nodes)
            details['axon_nodes'] = {
                'required_range': f"{min_nodes}~{max_nodes or '∞'}",
                'actual': actual_nodes,
                'range_check': range_ok,
                'note': 'Axon 노드 수 측정 기능 구현 필요'
            }
        elif requirements.axon_nodes > 0:
            # 하위 호환성: 고정값
            details['axon_nodes'] = {
                'required': requirements.axon_nodes,
                'actual': 0,
                'note': 'Axon 노드 수 측정 기능 구현 필요'
            }
        
        # 기능 플래그 검증
        details['features'] = {}
        for feature in requirements.required_features:
            # TODO: 실제 기능 구현 여부 확인
            feature_implemented = self._check_feature_implementation(feature, cookie)
            details['features'][feature.value] = feature_implemented
            if not feature_implemented:
                failed.append(f"기능 미구현: {feature.value}")
        
        # 뉴런 모델 검증
        details['models'] = {}
        for model in requirements.required_models:
            # TODO: 실제 모델 사용 여부 확인
            model_used = self._check_model_usage(model, cookie)
            details['models'][model.value] = model_used
            if not model_used:
                failed.append(f"모델 미사용: {model.value}")
        
        # 안정성 테스트
        if requirements.stability_test:
            stability_ok = self._run_stability_test(cookie)
            details['stability_test'] = stability_ok
            if not stability_ok:
                failed.append("안정성 테스트 실패")
        
        # 견고성 테스트
        if requirements.robustness_test:
            robustness_ok = self._run_robustness_test(cookie)
            details['robustness_test'] = robustness_ok
            if not robustness_ok:
                failed.append("견고성 테스트 실패")
        
        return len(failed) == 0, failed, details
    
    def _check_feature_implementation(self, feature: NetworkFeature, cookie) -> bool:
        """기능 구현 여부 확인"""
        # TODO: 실제 구현 확인 로직
        # 예: cookie의 stats나 내부 상태에서 확인
        return False  # 임시
    
    def _check_model_usage(self, model: NeuronModel, cookie) -> bool:
        """모델 사용 여부 확인"""
        # TODO: 실제 모델 사용 확인 로직
        return False  # 임시
    
    def _run_stability_test(self, cookie) -> bool:
        """안정성 테스트 실행"""
        # TODO: 실제 안정성 테스트 로직
        # 예: 장시간 실행, 메모리 누수 확인 등
        return False  # 임시
    
    def _run_robustness_test(self, cookie) -> bool:
        """견고성 테스트 실행"""
        # TODO: 실제 견고성 테스트 로직
        # 예: 노이즈 추가, 예외 상황 처리 등
        return False  # 임시


# =============================================================================
# 🎨 NFT 메타데이터 생성
# =============================================================================

def generate_nft_metadata(stage: EvolutionStage,
                         performance: Dict,
                         blockchain_hash: Optional[str] = None) -> NFTMetadata:
    """NFT 메타데이터 생성"""
    if not stage.nft_metadata:
        # 기본 메타데이터 생성
        return NFTMetadata(
            name=f"{stage.name} Badge",
            description=stage.description,
            image="ipfs://...",
            external_url=f"https://pham.world/evolution/{stage.tier.lower()}",
            pham_tier=stage.tier,
        )
    
    metadata = stage.nft_metadata
    
    # 기술 증명 추가
    metadata.technical_proof = {
        'performance': performance,
        'timestamp': datetime.now().isoformat(),
    }
    
    # 블록체인 해시 추가
    if blockchain_hash:
        metadata.blockchain_hash = blockchain_hash
    
    return metadata


# =============================================================================
# 📜 스마트컨트랙트 인터페이스
# =============================================================================

class SmartContractInterface:
    """스마트컨트랙트 인터페이스 (추상화)"""
    
    def __init__(self, contract_address: Optional[str] = None):
        self.contract_address = contract_address
        self.chain_id: Optional[int] = None  # Ethereum, Polygon, etc.
    
    def mint_nft(self,
                to_address: str,
                metadata: NFTMetadata) -> Optional[str]:
        """
        NFT 발행
        
        Returns:
            트랜잭션 해시
        """
        # TODO: 실제 스마트컨트랙트 호출
        # 예: ERC-721 mint 함수 호출
        return None
    
    def record_achievement(self,
                          user_id: str,
                          stage_name: str,
                          proof_data: Dict) -> Optional[str]:
        """
        달성 기록 (블록체인)
        
        Returns:
            트랜잭션 해시
        """
        # TODO: 실제 스마트컨트랙트 호출
        # 예: recordAchievement 함수 호출
        return None
    
    def check_first_achiever(self, stage_name: str) -> Optional[str]:
        """
        최초 달성자 확인
        
        Returns:
            최초 달성자 주소 (없으면 None)
        """
        # TODO: 실제 스마트컨트랙트 호출
        return None
    
    def distribute_rewards(self,
                          user_id: str,
                          stage_name: str,
                          rewards: Dict) -> Optional[str]:
        """
        보상 분배
        
        Returns:
            트랜잭션 해시
        """
        # TODO: 실제 스마트컨트랙트 호출
        # 예: ERC-20 transfer 또는 스테이킹
        return None


# =============================================================================
# 🏁 진화 시스템 메인 클래스
# =============================================================================

class HippoEvolutionSystem:
    """Hippo Evolution Tier System - 메인 클래스"""
    
    def __init__(self, blockchain_enabled: bool = False):
        """
        진화 시스템 초기화
        
        Args:
            blockchain_enabled: 블록체인 연동 활성화 여부 (기본: False)
                - False: Local Proof만 사용 (독립형 시스템)
                - True: Distributed Proof 사용 (스마트컨트랙트 기록)
        """
        self.blockchain_enabled = blockchain_enabled and HAS_BLOCKCHAIN
        self.validator = EvolutionValidator()
        # 블록체인은 선택적 계층 (Optional Layer)
        self.smart_contract = SmartContractInterface() if self.blockchain_enabled else None
        self.achievements: List[Dict] = []
        self.achievement_file = BABYHIPPO_PATH / "evolution_achievements.json"
        self._load_achievements()
    
    def _load_achievements(self):
        """달성 기록 로드"""
        if self.achievement_file.exists():
            try:
                with open(self.achievement_file, 'r', encoding='utf-8') as f:
                    self.achievements = json.load(f)
            except:
                self.achievements = []
        else:
            self.achievements = []
    
    def _save_achievements(self):
        """달성 기록 저장"""
        try:
            with open(self.achievement_file, 'w', encoding='utf-8') as f:
                json.dump(self.achievements, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 달성 기록 저장 실패: {e}")
    
    def check_evolution(self,
                       cookie,
                       performance: Dict,
                       user_id: str = "anonymous") -> Dict:
        """
        진화 단계 달성 확인 및 처리
        
        Returns:
            달성 결과 딕셔너리
        """
        # 모든 단계 확인 (현재 단계부터)
        current_stage = self._get_current_stage(cookie, performance)
        stages_to_check = self._get_next_stages(current_stage)
        
        results = []
        for stage_name in stages_to_check:
            result = self._check_stage_achievement(
                stage_name, cookie, performance, user_id
            )
            results.append(result)
        
        return {
            'current_stage': current_stage,
            'check_results': results,
        }
    
    def _get_current_stage(self, cookie, performance: Dict) -> str:
        """현재 단계 확인"""
        # 성능 기반으로 현재 단계 판단
        for stage_name in reversed(list(EVOLUTION_STAGES.keys())):
            stage = EVOLUTION_STAGES[stage_name]
            if (performance['memory_count'] >= stage.memory_threshold and
                performance['response_time_ms'] <= stage.speed_threshold_ms and
                performance['memory_usage_mb'] <= stage.memory_threshold_mb and
                performance['independence'] >= stage.independence_threshold):
                return stage_name
        return 'BabyHippo'
    
    def _get_next_stages(self, current_stage: str) -> List[str]:
        """다음 단계 목록"""
        stage_order = ['BabyHippo', 'TeenHippo', 'Hippocampus', 
                      'WisdomHippo', 'MagicHippo', 'HyperHippo']
        try:
            current_idx = stage_order.index(current_stage)
            return stage_order[current_idx + 1:]
        except ValueError:
            return stage_order[1:]  # BabyHippo부터
    
    def _check_stage_achievement(self,
                                stage_name: str,
                                cookie,
                                performance: Dict,
                                user_id: str) -> Dict:
        """단계 달성 확인"""
        # 이미 달성했는지 확인
        existing = [
            a for a in self.achievements
            if a.get('stage') == stage_name and a.get('user_id') == user_id
        ]
        if existing:
            return existing[0]
        
        # 조건 검증
        achieved, failed, details = self.validator.validate_stage(
            stage_name, cookie, performance
        )
        
        if not achieved:
            return {
                'stage': stage_name,
                'achieved': False,
                'failed_conditions': failed,
                'validation_details': details,
            }
        
        # 달성 기록 생성
        stage = EVOLUTION_STAGES[stage_name]
        achievement = {
            'stage': stage_name,
            'user_id': user_id,
            'achieved': True,
            'achieved_at': datetime.now().isoformat(),
            'performance': performance,
            'validation_details': details,
            'rewards': {
                'amount': stage.reward_amount,
                'type': stage.reward_type,
                'ecosystem_permissions': stage.ecosystem_permissions,
            },
            'blockchain_hash': None,
            'nft_metadata': None,
        }
        
        # NFT 메타데이터 생성
        nft_metadata = generate_nft_metadata(stage, performance)
        achievement['nft_metadata'] = nft_metadata.__dict__
        
        # 블록체인 기록
        if self.blockchain_enabled and self.smart_contract:
            try:
                # 달성 증명 생성
                proof_data = {
                    'stage': stage_name,
                    'user_id': user_id,
                    'performance': performance,
                    'timestamp': achievement['achieved_at'],
                }
                
                # 블록체인에 기록
                tx_hash = self.smart_contract.record_achievement(
                    user_id, stage_name, proof_data
                )
                achievement['blockchain_hash'] = tx_hash
                
                # NFT 발행
                if stage.reward_type == 'nft':
                    nft_tx_hash = self.smart_contract.mint_nft(
                        user_id, nft_metadata
                    )
                    achievement['nft_tx_hash'] = nft_tx_hash
                
            except Exception as e:
                print(f"⚠️ 블록체인 기록 실패: {e}")
        
        # 로컬 저장
        self.achievements.append(achievement)
        self._save_achievements()
        
        return achievement


# =============================================================================
# 🎯 편의 함수
# =============================================================================

def get_evolution_stage(stage_name: str) -> Optional[EvolutionStage]:
    """진화 단계 정보 가져오기"""
    return EVOLUTION_STAGES.get(stage_name)

def get_all_stages() -> Dict[str, EvolutionStage]:
    """모든 진화 단계 정보"""
    return EVOLUTION_STAGES.copy()

def create_evolution_system(blockchain_enabled: bool = True) -> HippoEvolutionSystem:
    """진화 시스템 생성"""
    return HippoEvolutionSystem(blockchain_enabled=blockchain_enabled)

