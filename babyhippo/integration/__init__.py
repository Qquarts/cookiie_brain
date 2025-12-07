"""
Integration: 통합 시스템 모듈
==============================

🌊 철학:
    "동역학 + 피드백 루프 + 자기조직화"

모든 뇌 구조를 통합하는 시스템들:
- BabyBrain - 풀기능 뇌 (피드백 루프 v2.0)
- LiteBrain - 경량 뇌 (자기조직화 v2.0)
- CuriousBrain - 도서관 연결 (외부 API)
- BrainLLM - nanoGPT 연동
- PatternFineTuner - 패턴 파인튜닝
- DreamManager - 꿈의 관리자 (수면 파이프라인) 🆕

Author: GNJz (Qquarts)
"""

from .baby_brain import BabyBrain
from .lite_brain import LiteBrain, ResponseMemory, LearnedResponse
from .curious_brain import CuriousBrain, LibraryConnector
from .growth_achievement import GrowthAchievement, GROWTH_STAGES, benchmark_performance
from .hippo_evolution import (
    HippoEvolutionSystem,
    EVOLUTION_STAGES,
    EvolutionStage,
    NFTMetadata,
    TechnicalRequirement,
    NeuronCountRange,
    NetworkFeature,
    NeuronModel,
    EvolutionValidator,
    SmartContractInterface,
    create_evolution_system,
    get_evolution_stage,
    get_all_stages,
)
from .brain_capability import (
    BrainCapabilitySchema,
    BrainCapability,
    CapabilityCategory,
    create_default_schema,
)
from .brain_llm import BrainLLM, HippoToLLM
from .pattern_finetune import (
    PatternFineTuner,
    PatternCollector,
    TrainingDataGenerator,
    TrainingSample,
)
from .dream_manager import DreamManager, SleepStage, SleepReport, DreamReport  # 🆕

__all__ = [
    # Brain Systems
    "BabyBrain",
    "LiteBrain",
    "CuriousBrain",
    "LibraryConnector",
    "BrainLLM",
    "HippoToLLM",
    
    # Self-Organization (LiteBrain v2.0)
    "ResponseMemory",
    "LearnedResponse",
    
    # Pattern Fine-Tuning
    "PatternFineTuner",
    "PatternCollector",
    "TrainingDataGenerator",
    "TrainingSample",
    
    # Dream Manager 🆕
    "DreamManager",
    "SleepStage",
    "SleepReport",
    "DreamReport",
    
    # Growth Achievement System 🦛
    "GrowthAchievement",
    "GROWTH_STAGES",
    "benchmark_performance",
    
    # Hippo Evolution System 🎖️
    "HippoEvolutionSystem",
    "EVOLUTION_STAGES",
    "EvolutionStage",
    "NFTMetadata",
    "TechnicalRequirement",
    "NeuronCountRange",
    "NetworkFeature",
    "NeuronModel",
    "EvolutionValidator",
    "SmartContractInterface",
    "create_evolution_system",
    "get_evolution_stage",
    "get_all_stages",
    
    # Brain Capability Schema 🧩
    "BrainCapabilitySchema",
    "BrainCapability",
    "CapabilityCategory",
    "create_default_schema",
]

