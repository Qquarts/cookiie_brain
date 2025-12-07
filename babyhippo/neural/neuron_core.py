"""
babyHippo Neuron Core
정확한 HH 뉴런 모델 사용 (HHSomaQuick)
========================================

✅ v4.3.0 업그레이드: 정확한 HH 뉴런 통합
- HHSomaQuick 사용 (생리학적 정확도)
- Lookup Table 기반 정확한 α/β 함수
- 실제 뇌 모델링을 위한 정확도 확보

Author: GNJz (Qquarts)
Version: 4.3.0 (Accurate HH Integration)
"""
import numpy as np
from .hh_soma_quick import HHSomaQuick

# HH 기본 설정 (정확한 HH 뉴런용)
HH_CONFIG = {
    "V0": -70.0,
    "gNa": 220.0,
    "gK": 26.0,
    "gL": 0.02,
    "ENa": 50.0,
    "EK": -77.0,
    "EL": -54.4,
    "spike_thresh": -15.0,
}

class BabyNeuron:
    """
    ✅ v4.3.0: 정확한 HH 뉴런 사용 (HHSomaQuick)
    
    생리학적으로 정확한 Hodgkin-Huxley 뉴런 모델
    - Lookup Table 기반 정확한 α/β 함수
    - 실제 뇌 모델링을 위한 정확도 확보
    """
    def __init__(self, name=""):
        self.name = name
        
        # ✅ 정확한 HH 뉴런 사용
        self.soma = HHSomaQuick(HH_CONFIG)
        
        # 호환성을 위한 속성 (기존 코드와의 호환)
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.ref_remaining = 0.0
        self.V_th = 0.0
        self.ref_period = 2.0
        
    def step(self, dt, I_ext=0.0):
        """
        한 스텝 진행 (정확한 HH 뉴런 사용)
        
        Returns
        -------
        bool
            스파이크 발생 여부
        """
        # ✅ 정확한 HH 뉴런으로 계산
        result = self.soma.step(dt, I_ext=I_ext)
        
        # 상태 동기화 (호환성)
        self.V = result["V"]
        self.m = result["m"]
        self.h = result["h"]
        self.n = result["n"]
        self.spike_flag = result["spike"]
        
        return result["spike"]
    
    def reset(self):
        """Reset to resting state"""
        self.soma.reset()
        # 상태 동기화
        self.V = self.soma.V
        self.m = self.soma.m
        self.h = self.soma.h
        self.n = self.soma.n
        self.spike_flag = False
        self.ref_remaining = 0.0


class DGNeuron:
    """
    Dentate Gyrus neuron - high threshold, sparse activation (Pattern Separation)
    
    ✅ v4.3.0: 정확한 HH 뉴런 사용 (HHSomaQuick)
    """
    def __init__(self, name="", activation_threshold=0.8):
        self.name = name
        self.activation_threshold = activation_threshold  # High threshold for pattern separation
        
        # ✅ 정확한 HH 뉴런 사용
        self.soma = HHSomaQuick(HH_CONFIG)
        
        # 호환성을 위한 속성
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.ref_remaining = 0.0
    
    def step(self, dt, I_ext=0.0):
        """
        한 스텝 진행 (정확한 HH 뉴런 사용)
        
        Pattern Separation: 높은 역치에서만 활성화
        """
        # Only activate above threshold
        if I_ext > self.activation_threshold * 300.0:
            result = self.soma.step(dt, I_ext=I_ext)
        else:
            result = self.soma.step(dt, I_ext=0.0)  # Inhibit
        
        # 상태 동기화
        self.V = result["V"]
        self.m = result["m"]
        self.h = result["h"]
        self.n = result["n"]
        self.spike_flag = result["spike"]
        
        return result["spike"]
    
    def reset(self):
        """Reset to resting state"""
        self.soma.reset()
        self.V = self.soma.V
        self.m = self.soma.m
        self.h = self.soma.h
        self.n = self.soma.n
        self.spike_flag = False
        self.ref_remaining = 0.0


class CA3Neuron:
    """
    CA3 neuron - associative memory
    
    ✅ v4.3.0: 정확한 HH 뉴런 사용 (HHSomaQuick)
    """
    def __init__(self, name=""):
        self.name = name
        self.wake_spike_count = 0
        
        # ✅ 정확한 HH 뉴런 사용
        self.soma = HHSomaQuick(HH_CONFIG)
        
        # 호환성을 위한 속성
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.ref_remaining = 0.0
    
    def step(self, dt, I_ext=0.0):
        """
        한 스텝 진행 (정확한 HH 뉴런 사용)
        """
        result = self.soma.step(dt, I_ext=I_ext)
        
        # 상태 동기화
        self.V = result["V"]
        self.m = result["m"]
        self.h = result["h"]
        self.n = result["n"]
        self.spike_flag = result["spike"]
        
        if result["spike"]:
            self.wake_spike_count += 1
        
        return result["spike"]
    
    def reset(self):
        """Reset to resting state"""
        self.soma.reset()
        self.V = self.soma.V
        self.m = self.soma.m
        self.h = self.soma.h
        self.n = self.soma.n
        self.spike_flag = False
        self.ref_remaining = 0.0
        self.wake_spike_count = 0


class CA1TimeCell:
    """
    CA1 time cell - temporal encoding
    
    ✅ v4.3.0: 정확한 HH 뉴런 사용 (HHSomaQuick)
    """
    def __init__(self, delay_ms, name=""):
        self.name = name
        self.delay_ms = delay_ms
        self.trigger_time = None
        
        # ✅ 정확한 HH 뉴런 사용
        self.soma = HHSomaQuick(HH_CONFIG)
        
        # 호환성을 위한 속성
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.ref_remaining = 0.0
    
    def trigger(self, t):
        """Start timer when signal received from CA3"""
        if self.trigger_time is None:
            self.trigger_time = t
    
    def step(self, dt, t, I_ext=0.0):
        """
        Auto-fire when time arrives (정확한 HH 뉴런 사용)
        """
        if self.trigger_time is not None:
            elapsed = t - self.trigger_time
            if abs(elapsed - self.delay_ms) < 2.0:
                I_ext += 200.0
        
        result = self.soma.step(dt, I_ext=I_ext)
        
        # 상태 동기화
        self.V = result["V"]
        self.m = result["m"]
        self.h = result["h"]
        self.n = result["n"]
        self.spike_flag = result["spike"]
        
        return result["spike"]
    
    def reset(self):
        """Reset to resting state"""
        self.soma.reset()
        self.V = self.soma.V
        self.m = self.soma.m
        self.h = self.soma.h
        self.n = self.soma.n
        self.spike_flag = False
        self.ref_remaining = 0.0
        self.trigger_time = None


class CA1NoveltyDetector:
    """
    CA1 novelty detector
    
    ✅ v4.3.0: 정확한 HH 뉴런 사용 (HHSomaQuick)
    """
    def __init__(self, name=""):
        self.name = name
        self.expected_patterns = []
        self.novelty_threshold = 0.5
        
        # ✅ 정확한 HH 뉴런 사용
        self.soma = HHSomaQuick(HH_CONFIG)
        
        # 호환성을 위한 속성
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.ref_remaining = 0.0
    
    def learn_pattern(self, pattern_name):
        """Learn pattern as familiar"""
        if pattern_name not in self.expected_patterns:
            self.expected_patterns.append(pattern_name)
    
    def compute_novelty(self, pattern_name):
        """Compute novelty score (0=familiar, 1=novel)"""
        if pattern_name in self.expected_patterns:
            return 0.0
        else:
            return 1.0
    
    def step(self, dt, t, pattern_name, I_ext=0.0):
        """
        Fire proportional to novelty (정확한 HH 뉴런 사용)
        """
        novelty_score = self.compute_novelty(pattern_name)
        if novelty_score > self.novelty_threshold:
            I_ext += 200.0 * novelty_score
        
        result = self.soma.step(dt, I_ext=I_ext)
        
        # 상태 동기화
        self.V = result["V"]
        self.m = result["m"]
        self.h = result["h"]
        self.n = result["n"]
        self.spike_flag = result["spike"]
        
        return result["spike"], novelty_score
    
    def reset(self):
        """Reset to resting state"""
        self.soma.reset()
        self.V = self.soma.V
        self.m = self.soma.m
        self.h = self.soma.h
        self.n = self.soma.n
        self.spike_flag = False
        self.ref_remaining = 0.0


class SubiculumGate:
    """
    Subiculum gate - context-based output control
    
    ✅ v4.3.0: 정확한 HH 뉴런 사용 (HHSomaQuick)
    """
    def __init__(self, name=""):
        self.name = name
        self.context_memory = {}
        self.current_context = None
        
        # ✅ 정확한 HH 뉴런 사용
        self.soma = HHSomaQuick(HH_CONFIG)
        
        # 호환성을 위한 속성
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.ref_remaining = 0.0
    
    def set_context(self, context):
        """Set current context"""
        self.current_context = context
    
    def learn_context_association(self, context, word):
        """Learn context-word association"""
        if context not in self.context_memory:
            self.context_memory[context] = []
        if word not in self.context_memory[context]:
            self.context_memory[context].append(word)
    
    def compute_relevance(self, word):
        """Compute context relevance (0=irrelevant, 1=relevant)"""
        if self.current_context is None:
            return 0.5
        
        if self.current_context in self.context_memory:
            relevant_words = self.context_memory[self.current_context]
            if word in relevant_words:
                return 1.0
            else:
                return 0.0
        
        return 0.5
    
    def gate(self, word, ca_input):
        """Output gating based on context"""
        relevance = self.compute_relevance(word)
        return ca_input * relevance
    
    def step(self, dt, I_ext=0.0):
        """
        한 스텝 진행 (정확한 HH 뉴런 사용, 호환성용)
        """
        result = self.soma.step(dt, I_ext=I_ext)
        
        # 상태 동기화
        self.V = result["V"]
        self.m = result["m"]
        self.h = result["h"]
        self.n = result["n"]
        self.spike_flag = result["spike"]
        
        return result["spike"]
    
    def reset(self):
        """Reset to resting state"""
        self.soma.reset()
        self.V = self.soma.V
        self.m = self.soma.m
        self.h = self.soma.h
        self.n = self.soma.n
        self.spike_flag = False
        self.ref_remaining = 0.0
