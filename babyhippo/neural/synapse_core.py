"""
babyHippo Synapse Core
STDP-based synaptic plasticity with consolidation
"""
import numpy as np

class BabySynapse:
    """
    Simplified event-driven synapse with STDP
    """
    def __init__(self, pre_neuron, post_neuron, delay_ms=1.5, Q_max=50.0, tau_ms=2.0):
        self.pre_neuron = pre_neuron
        self.post_neuron = post_neuron
        
        # Synaptic parameters
        self.delay_ms = delay_ms
        self.Q_max = Q_max
        self.tau_ms = tau_ms
        
        # Event queue
        self.spikes = []  # (time, quantum)
        self.I_syn = 0.0
        
    def on_pre_spike(self, t, Q):
        """Pre-synaptic spike arrives"""
        self.spikes.append((t + self.delay_ms, Q))
    
    def deliver(self, t):
        """Deliver spikes that have arrived"""
        self.I_syn = 0.0
        delivered = []
        
        for spike_t, Q in self.spikes:
            if spike_t <= t:
                # Exponential kernel
                dt_since = t - spike_t
                self.I_syn += Q * np.exp(-dt_since / self.tau_ms)
                delivered.append((spike_t, Q))
        
        # Remove delivered spikes
        for spike in delivered:
            self.spikes.remove(spike)
        
        return self.I_syn
    
    def reset(self):
        """Reset synapse"""
        self.spikes = []
        self.I_syn = 0.0


class STDPSynapse(BabySynapse):
    """
    STDP learning synapse with sleep consolidation
    
    Memory Persistence (영속성):
        - 기억은 완전히 사라지지 않음 (최소 floor 유지)
        - 중요한 기억일수록 더 높은 floor를 가짐
        - consolidation_level이 높을수록 decay 저항
        - 43살이 7살 기억을 가지고 있는 것처럼
    """
    def __init__(self, pre_neuron, post_neuron, delay_ms=1.5, Q_max=50.0, tau_ms=2.0):
        super().__init__(pre_neuron, post_neuron, delay_ms, Q_max, tau_ms)
        
        # STDP parameters
        self.weight = 1.0
        self.last_pre_time = -100.0
        self.last_post_time = -100.0
        self.replay_count = 0
        
        # STDP window
        self.stdp_window = 20.0
        self.ltp_rate = 0.15
        self.ltd_rate = 0.05
        self.tau_stdp = 10.0
        
        # === Memory Persistence (영속성) ===
        # consolidation_level: 0.0 ~ 1.0 (높을수록 영구적)
        # - sleep consolidation으로 증가
        # - 반복 학습으로 증가
        # - 절대 감소하지 않음 (한번 굳어진 기억)
        self.consolidation_level = 0.0
        
        # 최대 도달한 가중치 (peak weight)
        # - 한때 강했던 기억의 흔적
        self.peak_weight = 1.0
        
        # 생성 시간 (오래된 기억일수록 안정적)
        self.creation_time = 0  # will be set when first used
    
    def on_pre_spike(self, t, Q=None):
        """Pre-synaptic spike with STDP"""
        self.last_pre_time = t
        
        # LTD check (post fired before pre)
        dt_stdp = t - self.last_post_time
        if 0 < dt_stdp < self.stdp_window:
            # LTD: weaken synapse
            self.weight = max(0.1, self.weight - self.ltd_rate * np.exp(-dt_stdp / self.tau_stdp))
        
        # Deliver weighted quantum
        if Q is None:
            Q = self.Q_max * self.weight
        else:
            Q = Q * self.weight
        
        super().on_pre_spike(t, Q)
    
    def on_post_spike(self, t):
        """Post-synaptic spike with STDP"""
        self.last_post_time = t
        
        # LTP check (pre fired before post)
        dt = t - self.last_pre_time
        if 0 < dt < self.stdp_window:
            # LTP: strengthen synapse
            self.weight = min(50.0, self.weight + self.ltp_rate * np.exp(-dt / self.tau_stdp))
    
    def consolidate(self, factor=0.05):
        """
        Sleep consolidation - strengthen synapse AND increase persistence
        
        반복될수록:
        - weight 증가 (기억 강화)
        - consolidation_level 증가 (decay 저항 증가)
        - peak_weight 갱신 (최고점 기록)
        """
        self.weight = min(50.0, self.weight + factor)
        self.replay_count += 1
        
        # === 영속성 증가 ===
        # consolidation_level: 로그 스케일로 증가 (급격히 증가 후 안정)
        # 10회 = 0.5, 30회 = 0.75, 100회 ≈ 0.9
        self.consolidation_level = min(1.0, 
            self.consolidation_level + 0.05 * (1.0 - self.consolidation_level))
        
        # peak weight 갱신
        self.peak_weight = max(self.peak_weight, self.weight)
    
    def decay(self, rate=0.01, importance=0.5):
        """
        시간에 따른 기억 감쇠 (중요도 기반 보호)
        
        🍪 v1.0: low-importance memory decay 강화
        
        Args:
            rate: 기본 감쇠율 (0.01 = 1% 감소)
            importance: 기억 중요도 (0.0 ~ 1.0, MemoryRank 점수)
        
        핵심 원리:
        1. 중요한 기억 = 느리게 감쇠
        2. 공고화된 기억 = 더 느리게 감쇠
        3. 최소 floor 보장 = 완전히 잊지 않음
        4. 🍪 v1.0: 낮은 중요도 기억 = 빠르게 감쇠 (false recall 감소)
        
        인간 기억의 비유:
        - 7살 때 크리스마스 = 높은 importance, 높은 consolidation → 43살에도 기억
        - 어제 점심 = 낮은 importance, 낮은 consolidation → 빨리 흐릿해짐
        """
        # === Floor 계산 (최소 유지 가중치) ===
        # 기본 floor: 0.1 (완전히 0이 되지 않음)
        # 중요도 보너스: importance * 0.4 (중요하면 최대 0.5까지)
        # 공고화 보너스: consolidation * 0.3 (굳어지면 최대 0.3까지)
        # peak_weight 흔적: peak의 5% (한때 강했던 기억의 흔적)
        base_floor = 0.1
        importance_floor = importance * 0.4  # 중요도 0.8 → +0.32
        consolidation_floor = self.consolidation_level * 0.3  # 공고화 0.5 → +0.15
        peak_floor = self.peak_weight * 0.05  # peak가 10 → +0.5
        
        floor = base_floor + importance_floor + consolidation_floor + peak_floor
        
        # === Decay 저항 계산 ===
        # 중요하고 공고화된 기억 = 덜 감쇠
        # resistance: 0.0 ~ 0.95 (최대 95% 저항)
        resistance = min(0.95, 
            importance * 0.4 +           # 중요도 기여
            self.consolidation_level * 0.4 +  # 공고화 기여
            min(0.15, self.replay_count * 0.01))  # 반복 기여 (최대 0.15)
        
        # 🍪 v1.0: low-importance memory decay 강화
        # 중요도가 낮으면 (0.3 이하) 추가 감쇠
        if importance < 0.3:
            low_importance_penalty = (0.3 - importance) * 2.0  # 최대 0.6 추가 감쇠
            actual_decay = rate * (1.0 - resistance) * (1.0 + low_importance_penalty)
        else:
            actual_decay = rate * (1.0 - resistance)
        
        # 가중치 감쇠 (floor 아래로 내려가지 않음)
        self.weight = max(floor, self.weight - actual_decay)
        
        return self.weight
    
    def get_floor(self, importance=0.5):
        """현재 기억의 최소 유지 가중치 계산"""
        base_floor = 0.1
        importance_floor = importance * 0.4
        consolidation_floor = self.consolidation_level * 0.3
        peak_floor = self.peak_weight * 0.05
        return base_floor + importance_floor + consolidation_floor + peak_floor
    
    def get_weight(self):
        """Get current synaptic weight"""
        return self.weight
    
    def get_persistence_info(self):
        """기억 영속성 정보 반환"""
        return {
            'weight': self.weight,
            'consolidation_level': self.consolidation_level,
            'peak_weight': self.peak_weight,
            'replay_count': self.replay_count,
            'estimated_floor': self.get_floor(importance=0.5)
        }
    
    def reset(self):
        """Reset synapse (keep weight and persistence info)"""
        super().reset()
        # Note: we don't reset weight, last_times, replay_count, or persistence info
        # These persist across trials (영속성 유지)


def create_synapse_network(pre_neurons, post_neurons, synapse_type=STDPSynapse):
    """
    Create fully connected synapse network
    
    Args:
        pre_neurons: List of pre-synaptic neurons
        post_neurons: List of post-synaptic neurons
        synapse_type: Type of synapse to create
    
    Returns:
        List of synapses
    """
    synapses = []
    for pre in pre_neurons:
        for post in post_neurons:
            syn = synapse_type(pre, post)
            synapses.append(syn)
    return synapses


def reset_all_synapses(synapses):
    """Reset all synapses in a network"""
    for syn in synapses:
        syn.reset()


def get_average_weight(synapses):
    """Get average weight of STDP synapses"""
    if not synapses:
        return 0.0
    
    weights = []
    for syn in synapses:
        if isinstance(syn, STDPSynapse):
            weights.append(syn.get_weight())
    
    if not weights:
        return 0.0
    
    return np.mean(weights)
