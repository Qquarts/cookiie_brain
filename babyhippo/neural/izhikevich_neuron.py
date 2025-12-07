"""
Izhikevich Neuron Model (v3)
=============================

대규모 네트워크(10^5+)를 위한 최적화된 뉴런 모델

📐 수식:
    dv/dt = 0.04v² + 5v + 140 - u + I
    du/dt = a(bv - u)
    
    if v ≥ 30 mV:
        v ← c
        u ← u + d

특징:
    - 계산량: HH 대비 100배 빠름
    - 생물학적 유사도: 90-95%
    - 대규모 네트워크에 최적화

Author: GNJz (Qquarts)
Version: 3.0.0 (Izhikevich Edition)
"""

import numpy as np
from typing import Dict, Any, Optional


# Izhikevich 파라미터 프리셋
IZHIKEVICH_PRESETS = {
    "regular_spiking": {
        "a": 0.02,
        "b": 0.2,
        "c": -65.0,
        "d": 8.0,
        "v0": -70.0,
        "u0": -14.0,
    },
    "fast_spiking": {
        "a": 0.1,
        "b": 0.2,
        "c": -65.0,
        "d": 2.0,
        "v0": -70.0,
        "u0": -14.0,
    },
    "chattering": {
        "a": 0.02,
        "b": 0.2,
        "c": -50.0,
        "d": 2.0,
        "v0": -70.0,
        "u0": -14.0,
    },
    "intrinsically_bursting": {
        "a": 0.02,
        "b": 0.2,
        "c": -55.0,
        "d": 4.0,
        "v0": -70.0,
        "u0": -14.0,
    },
    "low_threshold": {
        "a": 0.02,
        "b": 0.25,
        "c": -65.0,
        "d": 2.0,
        "v0": -70.0,
        "u0": -14.0,
    },
}


class IzhikevichNeuron:
    """
    Izhikevich 뉴런 모델
    
    대규모 네트워크(10^5+ 뉴런)를 위한 최적화된 뉴런 모델
    - HH 대비 100배 빠른 계산 속도
    - 생물학적 유사도 90-95%
    - 다양한 발화 패턴 지원
    
    Attributes:
        v: 막전위 (mV)
        u: 회복 변수 (mV)
        a, b, c, d: Izhikevich 파라미터
        spike_flag: 스파이크 발생 여부
        spike_count: 총 스파이크 횟수
    """
    
    def __init__(self, 
                 name: str = "",
                 preset: Optional[str] = None,
                 a: Optional[float] = None,
                 b: Optional[float] = None,
                 c: Optional[float] = None,
                 d: Optional[float] = None,
                 v0: Optional[float] = None,
                 u0: Optional[float] = None):
        """
        Izhikevich 뉴런 초기화
        
        Parameters
        ----------
        name : str
            뉴런 이름
        preset : str, optional
            프리셋 이름 ("regular_spiking", "fast_spiking", etc.)
        a, b, c, d : float, optional
            Izhikevich 파라미터 (preset이 없을 때 사용)
        v0, u0 : float, optional
            초기 막전위 및 회복 변수
        """
        self.name = name
        
        # 프리셋 또는 커스텀 파라미터 사용
        if preset and preset in IZHIKEVICH_PRESETS:
            params = IZHIKEVICH_PRESETS[preset]
            self.a = params["a"]
            self.b = params["b"]
            self.c = params["c"]
            self.d = params["d"]
            self.v = params["v0"]
            self.u = params["u0"]
        else:
            # 커스텀 파라미터 (기본값: regular_spiking)
            self.a = a if a is not None else 0.02
            self.b = b if b is not None else 0.2
            self.c = c if c is not None else -65.0
            self.d = d if d is not None else 8.0
            self.v = v0 if v0 is not None else -70.0
            self.u = u0 if u0 is not None else -14.0
        
        # 상태 변수
        self.spike_flag = False
        self.spike_count = 0
        self.last_spike_time = None
        
        # 호환성을 위한 속성 (HHSomaQuick와 유사한 인터페이스)
        self.V = self.v  # 별칭
        self.m = 0.0  # HH 게이트 변수 (사용 안 함, 호환성만)
        self.h = 0.0
        self.n = 0.0
        self.ref_remaining = 0.0
        self.spike_thresh = 30.0  # Izhikevich 임계값
    
    def step(self, dt: float, I_ext: float = 0.0, **kwargs) -> Dict[str, Any]:
        """
        한 타임스텝 진행
        
        📐 수식:
            dv/dt = 0.04v² + 5v + 140 - u + I
            du/dt = a(bv - u)
            
            if v ≥ 30 mV:
                v ← c
                u ← u + d
        
        Parameters
        ----------
        dt : float
            시간 간격 (ms)
        I_ext : float
            외부 입력 전류 (pA 또는 μA)
        **kwargs
            추가 파라미터 (호환성용, 사용 안 함)
        
        Returns
        -------
        dict
            {
                "V": 막전위 (mV),
                "u": 회복 변수 (mV),
                "spike": 스파이크 발생 여부 (bool),
                "m": 0.0 (호환성),
                "h": 0.0 (호환성),
                "n": 0.0 (호환성),
            }
        """
        # 스파이크 리셋 처리
        if self.v >= self.spike_thresh:
            self.spike_flag = True
            self.spike_count += 1
            self.v = self.c
            self.u = self.u + self.d
        else:
            self.spike_flag = False
        
        # Izhikevich 미분 방정식 (Euler 방법)
        # dv/dt = 0.04v² + 5v + 140 - u + I
        dv_dt = 0.04 * (self.v ** 2) + 5.0 * self.v + 140.0 - self.u + I_ext
        
        # du/dt = a(bv - u)
        du_dt = self.a * (self.b * self.v - self.u)
        
        # 업데이트
        self.v += dv_dt * dt
        self.u += du_dt * dt
        
        # 막전위 클램프 (안정성)
        self.v = np.clip(self.v, -100.0, 50.0)
        
        # 호환성을 위한 별칭 업데이트
        self.V = self.v
        
        return {
            "V": self.v,
            "u": self.u,
            "spike": self.spike_flag,
            "m": 0.0,  # 호환성
            "h": 0.0,  # 호환성
            "n": 0.0,  # 호환성
        }
    
    def spiking(self) -> bool:
        """스파이크 발생 여부 반환"""
        return self.spike_flag
    
    def reset(self):
        """초기 상태로 리셋"""
        self.v = -70.0
        self.u = -14.0
        self.V = self.v
        self.spike_flag = False
        self.spike_count = 0
        self.last_spike_time = None
    
    def get_state(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "v": self.v,
            "u": self.u,
            "spike_count": self.spike_count,
            "spike_flag": self.spike_flag,
        }

