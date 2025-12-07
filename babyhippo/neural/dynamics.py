"""
=============================================================================
babyhippo Dynamics Engine
=============================================================================

🌊 핵심 철학:
    "실체는 입자(정지)가 아니라 파동(움직임)이다"
    "동역학(Dynamics)이 이 세계의 실체다"
    "노이즈는 창조의 씨앗이다"

📐 구현된 핵심 수식:

    1. Hodgkin-Huxley Neuron Dynamics:
       C_m dV/dt = I_ext + I_syn - g_L(V-E_L) - g_Na·m³h(V-E_Na) - g_K·n⁴(V-E_K)
       
    2. Short-Term Plasticity (STP) & Post-Tetanic Potentiation (PTP):
       On spike: S ← S + ΔS, PTP ← PTP + ΔPTP
       Decay: S ← S · decay_S, PTP ← PTP · decay_PTP
       
    3. Noise-Driven Activation (창발의 씨앗):
       I_noise = N(0, σ) · noise_level
       
    4. Low-Pass Integration (Subiculum):
       y(t+dt) = (1-α)·y(t) + spike(t)
       where α = dt/τ

생물학적 타당성:
    - 실제 뉴런의 이온 채널 역학
    - 단기 시냅스 가소성 (STP)
    - 테타닉 후 강화 (PTP)
    - 노이즈를 통한 자발적 활동

물리학적 타당성:
    - 에너지 보존 (막전위 클램핑)
    - 정보 전달 지연 (시냅스 딜레이)
    - 확률적 요동 (양자적 노이즈 모사)

Author: GNJz (Qquarts)
Version: 1.0.0 (Dynamics Edition)
=============================================================================
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum


# =============================================================================
# Configuration (환경 설정 - 하드코딩 최소화)
# =============================================================================

@dataclass
class HHConfig:
    """
    Hodgkin-Huxley 파라미터 설정
    
    생물학적 근거:
    - 실제 뉴런의 이온 채널 특성에서 유래
    - 값들은 실험적으로 측정된 범위 내에서 조절 가능
    """
    # Membrane capacitance (μF/cm²)
    Cm: float = 1.0
    
    # Conductances (mS/cm²)
    gNa: float = 120.0   # Sodium
    gK: float = 36.0     # Potassium
    gL: float = 0.3      # Leak
    
    # Reversal potentials (mV)
    ENa: float = 50.0    # Sodium
    EK: float = -77.0    # Potassium
    EL: float = -54.4    # Leak (resting)
    
    # Spike detection
    spike_thresh: float = 0.0  # mV
    
    # Refractory period
    ref_period: float = 2.0    # ms


@dataclass  
class STPConfig:
    """
    Short-Term Plasticity 설정
    
    생물학적 근거:
    - 시냅스 소포체의 방출/재충전 역학
    - 칼슘 이온의 축적과 소멸
    """
    # STP (Short-Term Potentiation)
    S_increment: float = 0.3      # 스파이크 시 증가량
    S_decay: float = 0.99         # 시간당 감쇠 (1에 가까울수록 느린 감쇠)
    S_min: float = 0.0
    S_max: float = 1.0
    
    # PTP (Post-Tetanic Potentiation)
    PTP_increment: float = 0.05   # 스파이크 시 증가량
    PTP_decay: float = 0.999      # 시간당 감쇠 (더 느린 감쇠)
    PTP_min: float = 1.0
    PTP_max: float = 2.0


@dataclass
class NoiseConfig:
    """
    노이즈 설정 - 창발의 씨앗
    
    철학적 근거:
    - 양자역학의 불확실성이 통계적으로 누적되어 질서를 만든다
    - 노이즈 없이는 자발적 활동 없음
    - 노이즈가 있어야 탐색(exploration)이 가능
    """
    # 기본 노이즈 레벨
    base_level: float = 0.1
    
    # 상태별 노이즈 레벨
    wake_level: float = 0.05      # 깨어있을 때 (낮은 노이즈)
    sleep_level: float = 0.3      # 수면 중 (높은 노이즈 - replay 유도)
    explore_level: float = 0.2    # 탐색 중 (중간 노이즈)


class NeuronState(Enum):
    """뉴런 상태"""
    REST = "rest"
    ACTIVE = "active"
    REFRACTORY = "refractory"


# =============================================================================
# Dynamic Neuron (동역학적 뉴런)
# =============================================================================

class DynamicNeuron:
    """
    동역학적 뉴런 - Hodgkin-Huxley + STP/PTP
    
    🌊 핵심 원리:
        - 정지된 뉴런은 죽은 뉴런
        - 매 순간 변화하는 것이 실체
        - 노이즈가 있어야 창발이 가능
    
    📐 수식:
        1. HH Dynamics:
           dV/dt = (I_ext + I_syn + I_noise - I_ion) / Cm
           
        2. STP/PTP:
           Spike → S↑, PTP↑
           Time → S↓, PTP↓
    
    Attributes:
        V: 막전위 (mV)
        m, h, n: 이온 채널 게이트 변수
        S: Short-Term Potentiation (0~1)
        PTP: Post-Tetanic Potentiation (1~2)
        state: 뉴런 상태 (REST/ACTIVE/REFRACTORY)
    """
    
    def __init__(self, 
                 name: str = "",
                 hh_config: Optional[HHConfig] = None,
                 stp_config: Optional[STPConfig] = None,
                 noise_config: Optional[NoiseConfig] = None):
        
        self.name = name
        
        # Configuration (기본값 사용, 필요시 조절)
        self.hh = hh_config or HHConfig()
        self.stp = stp_config or STPConfig()
        self.noise = noise_config or NoiseConfig()
        
        # === HH State Variables ===
        self.V = -70.0       # 막전위 (mV)
        self.m = 0.05        # Na activation gate
        self.h = 0.60        # Na inactivation gate
        self.n = 0.32        # K activation gate
        
        # === STP/PTP Variables ===
        self.S = 0.0         # Short-term potentiation
        self.PTP = 1.0       # Post-tetanic potentiation
        
        # === State ===
        self.state = NeuronState.REST
        self.ref_remaining = 0.0
        self.spike_flag = False
        
        # === Synaptic Input ===
        self.I_syn = 0.0
        
        # === Statistics (관찰용, 하드코딩 아님) ===
        self.spike_count = 0
        self.last_spike_time = -100.0
        
    def _compute_alpha_beta(self, V: float) -> Dict[str, float]:
        """
        이온 채널 게이트 rate 계산
        
        📐 수식 (Hodgkin-Huxley 1952):
            α_m = 0.1(V+40) / (1 - exp(-(V+40)/10))
            β_m = 4·exp(-(V+65)/18)
            α_h = 0.07·exp(-(V+65)/20)
            β_h = 1 / (1 + exp(-(V+35)/10))
            α_n = 0.01(V+55) / (1 - exp(-(V+55)/10))
            β_n = 0.125·exp(-(V+65)/80)
        """
        # 수치 안정성을 위한 처리
        eps = 1e-7
        
        # m gate (Na activation)
        if abs(V + 40.0) > eps:
            am = 0.1 * (V + 40.0) / (1.0 - np.exp(-(V + 40.0) / 10.0))
        else:
            am = 1.0
        bm = 4.0 * np.exp(-(V + 65.0) / 18.0)
        
        # h gate (Na inactivation)
        ah = 0.07 * np.exp(-(V + 65.0) / 20.0)
        bh = 1.0 / (1.0 + np.exp(-(V + 35.0) / 10.0))
        
        # n gate (K activation)
        if abs(V + 55.0) > eps:
            an = 0.01 * (V + 55.0) / (1.0 - np.exp(-(V + 55.0) / 10.0))
        else:
            an = 0.1
        bn = 0.125 * np.exp(-(V + 65.0) / 80.0)
        
        return {'am': am, 'bm': bm, 'ah': ah, 'bh': bh, 'an': an, 'bn': bn}
    
    def step(self, dt: float, I_ext: float = 0.0, 
             noise_level: Optional[float] = None,
             t: Optional[float] = None) -> Tuple[bool, float, float]:
        """
        한 타임스텝 진행
        
        Args:
            dt: 시간 간격 (ms)
            I_ext: 외부 입력 전류 (pA)
            noise_level: 노이즈 레벨 (None이면 기본값)
            t: 현재 시간 (ms) - 스파이크 시간 기록용
        
        Returns:
            (spiked, S, PTP): 스파이크 여부, 현재 S, 현재 PTP
        
        📐 핵심 수식:
            C_m dV/dt = I_ext + I_syn + I_noise - I_ion
            
            where:
            I_ion = g_Na·m³h(V-E_Na) + g_K·n⁴(V-E_K) + g_L(V-E_L)
        """
        # === 불응기 처리 ===
        if self.ref_remaining > 0:
            self.ref_remaining -= dt
            self.spike_flag = False
            self._decay_stp(dt)
            return False, self.S, self.PTP
        
        # === 노이즈 추가 (창발의 씨앗) ===
        if noise_level is None:
            noise_level = self.noise.base_level
        I_noise = np.random.randn() * noise_level * 10.0
        
        # === 총 입력 전류 ===
        I_total = I_ext + self.I_syn + I_noise
        
        # === HH Dynamics ===
        V = self.V
        rates = self._compute_alpha_beta(V)
        
        # 게이트 변수 업데이트 (Euler method)
        self.m += dt * (rates['am'] * (1 - self.m) - rates['bm'] * self.m)
        self.h += dt * (rates['ah'] * (1 - self.h) - rates['bh'] * self.h)
        self.n += dt * (rates['an'] * (1 - self.n) - rates['bn'] * self.n)
        
        # 이온 전류 계산
        I_Na = self.hh.gNa * (self.m ** 3) * self.h * (self.hh.ENa - V)
        I_K = self.hh.gK * (self.n ** 4) * (self.hh.EK - V)
        I_L = self.hh.gL * (self.hh.EL - V)
        
        # 막전위 업데이트
        dV = (I_total + I_Na + I_K + I_L) / self.hh.Cm
        self.V = np.clip(V + dt * dV, -100.0, 60.0)
        
        # === 스파이크 감지 ===
        spiked = False
        if self.V > self.hh.spike_thresh and not self.spike_flag:
            spiked = True
            self.spike_flag = True
            self.ref_remaining = self.hh.ref_period
            self.state = NeuronState.REFRACTORY
            self.spike_count += 1
            if t is not None:
                self.last_spike_time = t
            
            # === STP/PTP 증가 (스파이크 시) ===
            self.S = min(self.stp.S_max, self.S + self.stp.S_increment)
            self.PTP = min(self.stp.PTP_max, self.PTP + self.stp.PTP_increment)
        else:
            self.spike_flag = False
            if self.ref_remaining <= 0:
                self.state = NeuronState.REST if self.V < -60 else NeuronState.ACTIVE
        
        # === STP/PTP 감쇠 (매 스텝) ===
        self._decay_stp(dt)
        
        # 시냅스 전류 리셋 (다음 스텝에서 새로 받음)
        self.I_syn = 0.0
        
        return spiked, self.S, self.PTP
    
    def _decay_stp(self, dt: float):
        """STP/PTP 감쇠 (동역학적 - 멈추지 않는 흐름)"""
        # S 감쇠
        self.S = max(self.stp.S_min, self.S * (self.stp.S_decay ** dt))
        # PTP 감쇠 (더 느림)
        self.PTP = max(self.stp.PTP_min, 
                       self.stp.PTP_min + (self.PTP - self.stp.PTP_min) * (self.stp.PTP_decay ** dt))
    
    def receive_synaptic_input(self, I_syn: float):
        """시냅스 입력 수신"""
        self.I_syn += I_syn
    
    def reset(self):
        """휴지 상태로 리셋"""
        self.V = -70.0
        self.m = 0.05
        self.h = 0.60
        self.n = 0.32
        self.state = NeuronState.REST
        self.ref_remaining = 0.0
        self.spike_flag = False
        self.I_syn = 0.0
        # Note: S, PTP, spike_count는 유지 (학습 이력)
    
    def hard_reset(self):
        """완전 리셋 (테스트용)"""
        self.reset()
        self.S = 0.0
        self.PTP = 1.0
        self.spike_count = 0
        self.last_spike_time = -100.0
    
    def get_state_dict(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'name': self.name,
            'V': self.V,
            'S': self.S,
            'PTP': self.PTP,
            'state': self.state.value,
            'spike_count': self.spike_count,
        }


# =============================================================================
# Dynamic Synapse (동역학적 시냅스)
# =============================================================================

class DynamicSynapse:
    """
    동역학적 시냅스 - STP/PTP 반영 + 지연 + STDP
    
    🌊 핵심 원리:
        - 시냅스 강도는 고정값이 아니라 흐름
        - 단기 가소성(STP)과 장기 가소성(STDP) 공존
        - 노이즈(PTP 변동)가 학습을 돕는다
    
    📐 수식:
        전달량 = Q_base × weight × S × PTP
        
        where:
        - Q_base: 기본 전달량
        - weight: 장기 가중치 (STDP로 변화)
        - S: 단기 강화 (최근 스파이크 이력)
        - PTP: 테타닉 후 강화 (연속 스파이크 이력)
    """
    
    def __init__(self,
                 pre_neuron: DynamicNeuron,
                 post_neuron: DynamicNeuron,
                 delay_ms: float = 1.5,
                 Q_base: float = 50.0,
                 tau_ms: float = 2.0):
        
        self.pre = pre_neuron
        self.post = post_neuron
        
        # 시냅스 파라미터
        self.delay_ms = delay_ms
        self.Q_base = Q_base
        self.tau_ms = tau_ms
        
        # 장기 가중치 (STDP로 변화)
        self.weight = 1.0
        
        # 이벤트 큐 (지연된 스파이크)
        self.spike_queue: List[Tuple[float, float]] = []  # (arrival_time, Q)
        
        # STDP 파라미터
        self.stdp_window = 20.0   # ms
        self.ltp_rate = 0.1       # Long-Term Potentiation
        self.ltd_rate = 0.05      # Long-Term Depression
        self.tau_stdp = 10.0      # ms
        
        # 스파이크 타이밍 기록
        self.last_pre_spike = -100.0
        self.last_post_spike = -100.0
        
        # 통계
        self.transmission_count = 0
        
    def on_pre_spike(self, t: float, S: float, PTP: float):
        """
        Pre-synaptic 스파이크 처리
        
        📐 수식:
            Q = Q_base × weight × (1 + S) × PTP
            
        Args:
            t: 스파이크 시간
            S: Pre 뉴런의 S 값
            PTP: Pre 뉴런의 PTP 값
        """
        # 전달량 계산 (STP/PTP 반영)
        Q = self.Q_base * self.weight * (1.0 + S) * PTP
        
        # 지연 후 도착 시간
        arrival_time = t + self.delay_ms
        
        # 큐에 추가
        self.spike_queue.append((arrival_time, Q))
        
        # STDP: LTD 체크 (post가 먼저 발화했으면)
        dt = t - self.last_post_spike
        if 0 < dt < self.stdp_window:
            # LTD: 시냅스 약화
            delta = self.ltd_rate * np.exp(-dt / self.tau_stdp)
            self.weight = max(0.1, self.weight - delta)
        
        self.last_pre_spike = t
        
    def on_post_spike(self, t: float):
        """
        Post-synaptic 스파이크 처리 (STDP용)
        
        📐 STDP 규칙:
            pre → post (정상 순서) → LTP (강화)
            post → pre (역순) → LTD (약화)
        """
        # STDP: LTP 체크 (pre가 먼저 발화했으면)
        dt = t - self.last_pre_spike
        if 0 < dt < self.stdp_window:
            # LTP: 시냅스 강화
            delta = self.ltp_rate * np.exp(-dt / self.tau_stdp)
            self.weight = min(10.0, self.weight + delta)
        
        self.last_post_spike = t
        
    def deliver(self, t: float) -> float:
        """
        도착한 스파이크 전달
        
        Args:
            t: 현재 시간
            
        Returns:
            전달된 시냅스 전류
        """
        I_delivered = 0.0
        delivered = []
        
        for arrival_time, Q in self.spike_queue:
            if arrival_time <= t:
                # 지수 감쇠 커널
                dt_since = t - arrival_time
                I = Q * np.exp(-dt_since / self.tau_ms)
                I_delivered += I
                delivered.append((arrival_time, Q))
                self.transmission_count += 1
        
        # 전달된 스파이크 제거
        for spike in delivered:
            self.spike_queue.remove(spike)
        
        # Post 뉴런에 전달
        if I_delivered > 0:
            self.post.receive_synaptic_input(I_delivered)
        
        return I_delivered
    
    def consolidate(self, factor: float = 0.05):
        """수면 중 강화"""
        self.weight = min(10.0, self.weight + factor)
    
    def decay(self, rate: float = 0.01):
        """시간에 따른 감쇠"""
        self.weight = max(0.1, self.weight * (1.0 - rate))
    
    def reset(self):
        """이벤트 큐만 리셋 (weight 유지)"""
        self.spike_queue = []
    
    def get_state_dict(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'weight': self.weight,
            'transmission_count': self.transmission_count,
            'pending_spikes': len(self.spike_queue),
        }


# =============================================================================
# Subiculum Integrator (해마체 통합기)
# =============================================================================

class SubiculumIntegrator:
    """
    해마체 (Subiculum) - 스파이크 통합기
    
    📐 수식 (1차 Low-pass Filter):
        y(t+dt) = (1-α)·y(t) + spike(t)
        where α = dt/τ
    
    역할:
        - CA1의 스파이크 패턴을 시간적으로 통합
        - 잡음 제거, 안정적인 신호 추출
        - 피질로 전달할 "요약 신호" 생성
    """
    
    def __init__(self, dt: float = 0.1, tau: float = 20.0):
        self.dt = dt
        self.tau = tau
        self.alpha = dt / tau
        self.y = 0.0  # 통합된 출력
        
    def step(self, spike: bool) -> float:
        """
        📐 수식: y(t+dt) = (1-α)·y(t) + spike(t)
        """
        self.y = (1.0 - self.alpha) * self.y + (1.0 if spike else 0.0)
        return self.y
    
    def reset(self):
        self.y = 0.0
    
    def get_output(self) -> float:
        return self.y


# =============================================================================
# Winner-Take-All (경쟁적 억제)
# =============================================================================

def apply_wta(neurons: List[DynamicNeuron], k: int = 3) -> List[int]:
    """
    Winner-Take-All: 상위 K개 뉴런만 유지
    
    📐 개념:
        1. 전압(V) 기준 정렬
        2. 상위 k개 선택 (winners)
        3. 나머지 억제 (losers)
    
    생물학적 의미:
        - Sparse coding (희소 표현)
        - 패턴 간 간섭 최소화
        - 에너지 효율적 표현
        
    Args:
        neurons: 뉴런 리스트
        k: 승자 수
        
    Returns:
        승자 인덱스 리스트
    """
    if len(neurons) <= k:
        return list(range(len(neurons)))
    
    # 전압 기준 정렬
    indexed_v = [(i, n.V) for i, n in enumerate(neurons)]
    indexed_v.sort(key=lambda x: x[1], reverse=True)
    
    # 승자와 패자 분리
    winners = [idx for idx, _ in indexed_v[:k]]
    losers = [idx for idx, _ in indexed_v[k:]]
    
    # 패자 억제
    for idx in losers:
        if neurons[idx].V > -60.0:
            neurons[idx].V = -70.0
            neurons[idx].spike_flag = False
            neurons[idx].state = NeuronState.REST
    
    return winners


# =============================================================================
# Noise Generator (노이즈 생성기 - 창발의 씨앗)
# =============================================================================

class NoiseGenerator:
    """
    노이즈 생성기 - 창발을 위한 확률적 요동
    
    🌊 철학:
        "양자역학의 불확실성이 통계적으로 누적되어 질서를 만든다"
        "노이즈 없이는 새로운 패턴의 발견 없음"
    
    용도:
        - 수면 중 자발적 replay 유도
        - 탐색(exploration) 촉진
        - 고착(local minimum) 탈출
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)
        self.base_level = 0.1
        
    def gaussian(self, level: Optional[float] = None) -> float:
        """가우시안 노이즈"""
        if level is None:
            level = self.base_level
        return np.random.randn() * level
    
    def uniform(self, low: float = -1.0, high: float = 1.0) -> float:
        """균일 노이즈"""
        return np.random.uniform(low, high)
    
    def poisson_spike(self, rate_hz: float, dt_ms: float) -> bool:
        """포아송 스파이크 (자발적 발화)"""
        prob = rate_hz * dt_ms / 1000.0
        return np.random.random() < prob
    
    def generate_pattern_noise(self, size: int, level: float = 0.1) -> np.ndarray:
        """패턴에 추가할 노이즈 벡터"""
        return np.random.randn(size) * level


# =============================================================================
# Factory Functions (팩토리 함수)
# =============================================================================

def create_neuron_population(n: int, 
                             prefix: str = "N",
                             config: Optional[HHConfig] = None) -> List[DynamicNeuron]:
    """뉴런 집단 생성"""
    return [DynamicNeuron(name=f"{prefix}{i}", hh_config=config) for i in range(n)]


def create_synapse_matrix(pre_neurons: List[DynamicNeuron],
                          post_neurons: List[DynamicNeuron],
                          connection_prob: float = 1.0,
                          Q_base: float = 50.0) -> List[DynamicSynapse]:
    """
    시냅스 행렬 생성
    
    Args:
        pre_neurons: Pre-synaptic 뉴런들
        post_neurons: Post-synaptic 뉴런들
        connection_prob: 연결 확률 (1.0 = 완전 연결)
        Q_base: 기본 전달량
    """
    synapses = []
    for pre in pre_neurons:
        for post in post_neurons:
            if pre != post and np.random.random() < connection_prob:
                syn = DynamicSynapse(pre, post, Q_base=Q_base)
                synapses.append(syn)
    return synapses


# =============================================================================
# Test (테스트)
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Dynamics Engine Test")
    print("=" * 60)
    
    # 뉴런 생성
    neuron = DynamicNeuron(name="test")
    print(f"\n1️⃣ 뉴런 생성: {neuron.name}")
    print(f"   초기 상태: V={neuron.V:.1f}mV, S={neuron.S:.2f}, PTP={neuron.PTP:.2f}")
    
    # 자극 인가
    print("\n2️⃣ 자극 인가 (I=200pA, 10ms)...")
    dt = 0.1
    spike_times = []
    for i in range(100):
        t = i * dt
        I = 200.0 if t < 10.0 else 0.0
        spiked, S, PTP = neuron.step(dt, I, noise_level=0.1, t=t)
        if spiked:
            spike_times.append(t)
    
    print(f"   스파이크 횟수: {len(spike_times)}")
    print(f"   최종 상태: V={neuron.V:.1f}mV, S={neuron.S:.2f}, PTP={neuron.PTP:.2f}")
    
    # 시냅스 테스트
    print("\n3️⃣ 시냅스 테스트...")
    pre = DynamicNeuron(name="pre")
    post = DynamicNeuron(name="post")
    syn = DynamicSynapse(pre, post, Q_base=80.0)
    
    # Pre 스파이크
    syn.on_pre_spike(t=5.0, S=0.5, PTP=1.2)
    print(f"   Pre spike at t=5.0, S=0.5, PTP=1.2")
    print(f"   Pending spikes: {len(syn.spike_queue)}")
    
    # 전달
    for i in range(20):
        t = 5.0 + i * dt
        I = syn.deliver(t)
        if I > 0:
            print(f"   Delivered at t={t:.1f}: I={I:.2f}pA")
    
    # 노이즈 테스트
    print("\n4️⃣ 노이즈 생성기 테스트...")
    noise_gen = NoiseGenerator(seed=42)
    samples = [noise_gen.gaussian(0.3) for _ in range(5)]
    print(f"   가우시안 샘플: {[f'{s:.3f}' for s in samples]}")
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)

