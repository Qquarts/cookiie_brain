"""
HH LIF Neuron Model (v4)
=========================

HH 기반 Leaky Integrate-and-Fire 뉴런 모델

📐 수식:
    C_m dV/dt = -g_L(V - E_L) - g_Na·m³h(V - E_Na) - g_K·n⁴(V - E_K) + I_ext
    
    if V ≥ V_th:
        V ← V_reset
        (불응기)

특징:
    - HH의 생물학적 정확도 + LIF의 계산 효율성
    - 중간 규모 네트워크(10^3~10^4)에 적합
    - HH보다 빠르고, Izhikevich보다 정확

Author: GNJz (Qquarts)
Version: 4.0.0 (HH LIF Edition)
"""

import numpy as np
import math
from typing import Dict, Any, Optional


# HH LIF 기본 설정
HH_LIF_CONFIG = {
    "V0": -70.0,
    "gNa": 120.0,  # HH보다 낮음 (LIF 특성)
    "gK": 36.0,
    "gL": 0.3,  # LIF 특성: 누설 전도도 증가
    "ENa": 50.0,
    "EK": -77.0,
    "EL": -54.4,
    "C_m": 1.0,  # 막용량 (μF/cm²)
    "V_th": -50.0,  # 발화 임계값
    "V_reset": -70.0,  # 리셋 전위
    "ref_period": 2.0,  # 불응기 (ms)
}


class HHLIFNeuron:
    """
    HH 기반 Leaky Integrate-and-Fire 뉴런 모델
    
    HH의 생물학적 정확도를 유지하면서 LIF의 계산 효율성을 결합
    - HH보다 빠른 계산 (게이트 변수 단순화)
    - Izhikevich보다 정확한 생물학적 모델링
    - 중간 규모 네트워크(10^3~10^4)에 최적
    
    Attributes:
        V: 막전위 (mV)
        m, h, n: 이온 채널 게이트 변수
        spike_flag: 스파이크 발생 여부
        ref_remaining: 남은 불응기 시간 (ms)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, name: str = ""):
        """
        HH LIF 뉴런 초기화
        
        Parameters
        ----------
        config : dict, optional
            뉴런 설정 (기본값: HH_LIF_CONFIG)
        name : str
            뉴런 이름
        """
        self.name = name
        
        # 설정 병합
        if config is None:
            config = HH_LIF_CONFIG.copy()
        else:
            cfg = HH_LIF_CONFIG.copy()
            cfg.update(config)
            config = cfg
        
        # 막전위 및 게이트 변수
        self.V = float(config["V0"])
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        
        # 이온 채널 파라미터
        self.gNa = float(config["gNa"])
        self.gK = float(config["gK"])
        self.gL = float(config["gL"])
        self.ENa = float(config["ENa"])
        self.EK = float(config["EK"])
        self.EL = float(config["EL"])
        self.C_m = float(config["C_m"])
        
        # LIF 특성 파라미터
        self.V_th = float(config["V_th"])
        self.V_reset = float(config["V_reset"])
        self.ref_period = float(config["ref_period"])
        self.ref_remaining = 0.0
        
        # 상태 변수
        self.spike_flag = False
        self.spike_count = 0
        self.last_spike_time = None
        
        # 호환성을 위한 속성
        self.spike_thresh = self.V_th
    
    @staticmethod
    def _alpha_m(V: float) -> float:
        """Na⁺ 활성화 (m 게이트) α(V)"""
        x = V + 40.0
        if abs(x) > 1e-5:
            return 0.1 * x / (1.0 - math.exp(-x / 10.0))
        return 1.0
    
    @staticmethod
    def _beta_m(V: float) -> float:
        """Na⁺ 활성화 (m 게이트) β(V)"""
        return 4.0 * math.exp(-(V + 65.0) / 18.0)
    
    @staticmethod
    def _alpha_h(V: float) -> float:
        """Na⁺ 비활성화 (h 게이트) α(V)"""
        return 0.07 * math.exp(-(V + 65.0) / 20.0)
    
    @staticmethod
    def _beta_h(V: float) -> float:
        """Na⁺ 비활성화 (h 게이트) β(V)"""
        return 1.0 / (1.0 + math.exp(-(V + 35.0) / 10.0))
    
    @staticmethod
    def _alpha_n(V: float) -> float:
        """K⁺ 활성화 (n 게이트) α(V)"""
        x = V + 55.0
        if abs(x) > 1e-5:
            return 0.01 * x / (1.0 - math.exp(-x / 10.0))
        return 0.1
    
    @staticmethod
    def _beta_n(V: float) -> float:
        """K⁺ 활성화 (n 게이트) β(V)"""
        return 0.125 * math.exp(-(V + 65.0) / 80.0)
    
    def step(self, dt: float, I_ext: float = 0.0, **kwargs) -> Dict[str, Any]:
        """
        한 타임스텝 진행
        
        📐 수식:
            C_m dV/dt = -g_L(V - E_L) - g_Na·m³h(V - E_Na) - g_K·n⁴(V - E_K) + I_ext
            
            dm/dt = α_m(1-m) - β_m·m
            dh/dt = α_h(1-h) - β_h·h
            dn/dt = α_n(1-n) - β_n·n
            
            if V ≥ V_th:
                V ← V_reset
                (불응기)
        
        Parameters
        ----------
        dt : float
            시간 간격 (ms)
        I_ext : float
            외부 입력 전류 (μA)
        **kwargs
            추가 파라미터 (호환성용)
        
        Returns
        -------
        dict
            {
                "V": 막전위 (mV),
                "m": Na⁺ 활성화 게이트,
                "h": Na⁺ 비활성화 게이트,
                "n": K⁺ 활성화 게이트,
                "spike": 스파이크 발생 여부 (bool),
            }
        """
        # 불응기 처리
        if self.ref_remaining > 0:
            self.ref_remaining -= dt
            self.spike_flag = False
            return {
                "V": self.V,
                "m": self.m,
                "h": self.h,
                "n": self.n,
                "spike": False,
            }
        
        # 게이트 변수 업데이트 (Euler 방법)
        am = self._alpha_m(self.V)
        bm = self._beta_m(self.V)
        ah = self._alpha_h(self.V)
        bh = self._beta_h(self.V)
        an = self._alpha_n(self.V)
        bn = self._beta_n(self.V)
        
        self.m += dt * (am * (1.0 - self.m) - bm * self.m)
        self.h += dt * (ah * (1.0 - self.h) - bh * self.h)
        self.n += dt * (an * (1.0 - self.n) - bn * self.n)
        
        # 게이트 범위 제한
        self.m = np.clip(self.m, 0.0, 1.0)
        self.h = np.clip(self.h, 0.0, 1.0)
        self.n = np.clip(self.n, 0.0, 1.0)
        
        # 이온 전류 계산
        I_Na = self.gNa * (self.m ** 3) * self.h * (self.ENa - self.V)
        I_K = self.gK * (self.n ** 4) * (self.EK - self.V)
        I_L = self.gL * (self.EL - self.V)
        
        # 막전위 업데이트
        dV_dt = (I_ext + I_Na + I_K + I_L) / self.C_m
        self.V += dV_dt * dt
        
        # 막전위 클램프
        self.V = np.clip(self.V, -100.0, 50.0)
        
        # 스파이크 감지 및 리셋 (LIF 특성)
        if self.V >= self.V_th:
            self.spike_flag = True
            self.spike_count += 1
            self.V = self.V_reset
            self.ref_remaining = self.ref_period
        else:
            self.spike_flag = False
        
        return {
            "V": self.V,
            "m": self.m,
            "h": self.h,
            "n": self.n,
            "spike": self.spike_flag,
        }
    
    def spiking(self) -> bool:
        """스파이크 발생 여부 반환"""
        return self.spike_flag
    
    def reset(self):
        """초기 상태로 리셋"""
        self.V = HH_LIF_CONFIG["V0"]
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.spike_flag = False
        self.spike_count = 0
        self.ref_remaining = 0.0
        self.last_spike_time = None
    
    def get_state(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "V": self.V,
            "m": self.m,
            "h": self.h,
            "n": self.n,
            "spike_count": self.spike_count,
            "spike_flag": self.spike_flag,
        }

