"""
🧩 BrainCapability Schema - 확장 가능한 뇌 능력 플래그 시스템

OS나 딥러닝 프레임워크의 "Capability Flags"와 유사한 개념
커뮤니티 확장이 쉽고, 조건 검증이 강력하며, 충돌 없이 확장 가능

Author: GNJz (Qquarts)
Version: 1.0
"""

from typing import Dict, Any, Optional, Set, Tuple, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class CapabilityCategory(Enum):
    """능력 카테고리"""
    MEMORY = "memory"
    NETWORK = "network"
    PLASTICITY = "plasticity"
    PHYSIOLOGY = "physiology"
    COGNITION = "cognition"
    INTEGRATION = "integration"


@dataclass
class BrainCapability:
    """뇌 능력 플래그"""
    category: CapabilityCategory
    name: str  # 예: "short_term", "recurrent", "stdp"
    enabled: bool = False
    level: float = 0.0  # 0.0 ~ 1.0 (능력 수준)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"{self.category.value}.{self.name}"


class BrainCapabilitySchema:
    """
    뇌 능력 스키마
    
    구조화된 능력 플래그 시스템
    {
      "memory.short_term": true,
      "memory.long_term": false,
      "network.recurrent": false,
      "plasticity.stdp": true,
      "plasticity.meta_stdp": false,
      "physiology.axon_pde": true,
      "physiology.energy_loop": false
    }
    """
    
    def __init__(self):
        self.capabilities: Dict[str, BrainCapability] = {}
        self._initialize_default_capabilities()
    
    def _initialize_default_capabilities(self):
        """기본 능력 플래그 초기화"""
        # Memory
        self.set_capability(CapabilityCategory.MEMORY, "short_term", False)
        self.set_capability(CapabilityCategory.MEMORY, "long_term", False)
        self.set_capability(CapabilityCategory.MEMORY, "episodic", False)
        self.set_capability(CapabilityCategory.MEMORY, "semantic", False)
        self.set_capability(CapabilityCategory.MEMORY, "working", False)
        
        # Network
        self.set_capability(CapabilityCategory.NETWORK, "recurrent", False)
        self.set_capability(CapabilityCategory.NETWORK, "distributed", False)
        self.set_capability(CapabilityCategory.NETWORK, "branching", False)
        self.set_capability(CapabilityCategory.NETWORK, "vectorized", False)
        
        # Plasticity
        self.set_capability(CapabilityCategory.PLASTICITY, "stdp", False)
        self.set_capability(CapabilityCategory.PLASTICITY, "meta_stdp", False)
        self.set_capability(CapabilityCategory.PLASTICITY, "ltp", False)
        self.set_capability(CapabilityCategory.PLASTICITY, "ltd", False)
        
        # Physiology
        self.set_capability(CapabilityCategory.PHYSIOLOGY, "axon_pde", False)
        self.set_capability(CapabilityCategory.PHYSIOLOGY, "energy_loop", False)
        self.set_capability(CapabilityCategory.PHYSIOLOGY, "atp_metabolism", False)
        self.set_capability(CapabilityCategory.PHYSIOLOGY, "phase_precession", False)
        
        # Cognition
        self.set_capability(CapabilityCategory.COGNITION, "pattern_completion", False)
        self.set_capability(CapabilityCategory.COGNITION, "pattern_separation", False)
        self.set_capability(CapabilityCategory.COGNITION, "symbolic_abstraction", False)
        self.set_capability(CapabilityCategory.COGNITION, "analogy_reasoning", False)
        
        # Integration
        self.set_capability(CapabilityCategory.INTEGRATION, "cortex_comm", False)
        self.set_capability(CapabilityCategory.INTEGRATION, "llm_integration", False)
        self.set_capability(CapabilityCategory.INTEGRATION, "blockchain", False)
    
    def set_capability(self,
                     category: CapabilityCategory,
                     name: str,
                     enabled: bool = True,
                     level: float = 1.0,
                     metadata: Optional[Dict[str, Any]] = None):
        """능력 설정"""
        key = f"{category.value}.{name}"
        self.capabilities[key] = BrainCapability(
            category=category,
            name=name,
            enabled=enabled,
            level=level,
            metadata=metadata or {}
        )
    
    def get_capability(self, category: CapabilityCategory, name: str) -> Optional[BrainCapability]:
        """능력 가져오기"""
        key = f"{category.value}.{name}"
        return self.capabilities.get(key)
    
    def is_enabled(self, category: CapabilityCategory, name: str) -> bool:
        """능력 활성화 여부"""
        cap = self.get_capability(category, name)
        return cap.enabled if cap else False
    
    def get_level(self, category: CapabilityCategory, name: str) -> float:
        """능력 수준 가져오기"""
        cap = self.get_capability(category, name)
        return cap.level if cap else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {}
        for key, cap in self.capabilities.items():
            result[key] = {
                'enabled': cap.enabled,
                'level': cap.level,
                'metadata': cap.metadata
            }
        return result
    
    def from_dict(self, data: Dict[str, Any]):
        """딕셔너리에서 로드"""
        for key, value in data.items():
            if '.' in key:
                category_str, name = key.split('.', 1)
                try:
                    category = CapabilityCategory(category_str)
                    if isinstance(value, bool):
                        self.set_capability(category, name, enabled=value)
                    elif isinstance(value, dict):
                        self.set_capability(
                            category, name,
                            enabled=value.get('enabled', False),
                            level=value.get('level', 1.0),
                            metadata=value.get('metadata', {})
                        )
                except ValueError:
                    pass  # 알 수 없는 카테고리 무시
    
    def to_json(self) -> str:
        """JSON으로 변환"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def from_json(self, json_str: str):
        """JSON에서 로드"""
        data = json.loads(json_str)
        self.from_dict(data)
    
    def get_enabled_capabilities(self) -> Dict[str, BrainCapability]:
        """활성화된 능력만 반환"""
        return {k: v for k, v in self.capabilities.items() if v.enabled}
    
    def get_by_category(self, category: CapabilityCategory) -> Dict[str, BrainCapability]:
        """카테고리별 능력 반환"""
        return {k: v for k, v in self.capabilities.items() 
                if v.category == category}
    
    def check_requirements(self, required: Dict[str, bool]) -> Tuple[bool, List[str]]:
        """
        요구사항 확인
        
        Args:
            required: {"memory.short_term": True, "network.recurrent": False, ...}
        
        Returns:
            (만족 여부, 실패한 요구사항 목록)
        """
        failed = []
        for key, required_enabled in required.items():
            if '.' in key:
                category_str, name = key.split('.', 1)
                try:
                    category = CapabilityCategory(category_str)
                    actual_enabled = self.is_enabled(category, name)
                    if actual_enabled != required_enabled:
                        failed.append(f"{key}: required={required_enabled}, actual={actual_enabled}")
                except ValueError:
                    failed.append(f"{key}: unknown category")
        
        return len(failed) == 0, failed


def create_default_schema() -> BrainCapabilitySchema:
    """기본 스키마 생성"""
    return BrainCapabilitySchema()

