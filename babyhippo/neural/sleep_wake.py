"""
=============================================================================
Sleep-Wake Cycle: 동역학적 수면/각성 시스템
=============================================================================

🌊 철학:
    "수면은 단순한 휴식이 아니라 창조의 시간"
    "노이즈가 기억을 재구성한다"
    "꿈은 뇌의 자기조직화 과정"

📐 핵심 원리:

    1. 노이즈 기반 Replay (Sleep)
       - 깨어있을 때: 낮은 노이즈 → 입력 처리
       - 잠잘 때: 높은 노이즈 → 자발적 replay 유도
       - 노이즈가 약한 기억도 활성화시켜 consolidation
       
    2. STP/PTP 추적
       - 스파이크 활동 → S, PTP 변화
       - 높은 S/PTP를 가진 시냅스가 더 강화
       
    3. 시상하부 연동
       - 에너지 낮음 → 수면 욕구 증가
       - 수면 → 에너지 회복
       - 도파민(보상) 기반 기억 선택

생물학적 근거:
    - 해마 Sharp-Wave Ripple (SWR) 현상
    - 수면 중 기억 재생 (hippocampal replay)
    - 느린 파 수면(SWS)과 REM 수면의 역할
    - 시냅스 항상성 가설 (synaptic homeostasis)

물리학적 근거:
    - 열역학적 요동 (thermal fluctuation)
    - 확률적 공명 (stochastic resonance)
    - 자발적 대칭 깨짐

Author: GNJz (Qquarts)
Version: 1.0.0
=============================================================================
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time

# 동역학 엔진 임포트
from .dynamics import (
    DynamicNeuron, 
    DynamicSynapse, 
    NoiseGenerator,
    NeuronState,
    apply_wta,
)


class SleepStage(Enum):
    """수면 단계"""
    WAKE = "wake"           # 깨어있음
    LIGHT_SLEEP = "N1"      # 얕은 수면 (Stage 1)
    DEEP_SLEEP = "N2"       # 깊은 수면 (Stage 2)
    SWS = "N3"              # 느린 파 수면 (Slow Wave Sleep)
    REM = "REM"             # 급속 안구 운동 수면 (꿈)


@dataclass
class SleepConfig:
    """
    수면 설정
    
    생물학적 근거:
    - 수면 사이클: 약 90분
    - 밤 초반: SWS 많음 (기억 공고화)
    - 밤 후반: REM 많음 (기억 통합)
    """
    # 노이즈 레벨 (단계별)
    noise_wake: float = 0.05      # 깨어있을 때 (낮은 노이즈)
    noise_light: float = 0.15     # 얕은 수면
    noise_deep: float = 0.25      # 깊은 수면
    noise_sws: float = 0.35       # SWS (높은 노이즈 - replay 유도)
    noise_rem: float = 0.20       # REM (중간 노이즈 - 꿈)
    
    # 타이밍 (밀리초)
    cycle_duration: float = 1000.0   # 1 사이클 = 1초 (시뮬레이션)
    dt: float = 0.1                   # 시간 간격
    
    # Consolidation 파라미터
    # 🍪 v1.0: threshold 튜닝 (0.3 → 0.7)
    # 더 정확한 기억만 공고화하여 false recall 감소
    consolidation_threshold: float = 0.7  # 이 이상 활성화된 기억만 강화
    consolidation_rate: float = 0.05      # 강화율
    
    # 에너지 회복
    energy_recovery_rate: float = 0.1     # 사이클당 에너지 회복


@dataclass
class ReplayEvent:
    """
    Replay 이벤트 (수면 중 재생)
    
    Attributes:
        memory_id: 재생된 기억 ID
        stage: 수면 단계
        activation: 활성화 강도
        time: 발생 시간
        stp_level: S (단기 강화) 레벨
        ptp_level: PTP 레벨
    """
    memory_id: str
    stage: SleepStage
    activation: float
    time: float
    stp_level: float = 0.0
    ptp_level: float = 1.0


class SleepWakeCycle:
    """
    동역학적 수면/각성 사이클
    
    🌊 핵심 원리:
        1. Wake: 낮은 노이즈, 외부 입력 처리
        2. Sleep: 높은 노이즈, 자발적 replay
        3. Consolidation: 활성화된 기억 강화
        4. Energy: 수면으로 회복
    
    📐 수식:
        Wake: I = I_external + noise_wake
        Sleep: I = noise_sleep × importance  (자발적 활성화)
        
        Consolidation: 
        if activation > threshold:
            weight += consolidation_rate × S × PTP
    
    생물학적 의미:
        - 해마의 Sharp-Wave Ripple (SWR)
        - 느린 파 동기화
        - 기억 재생과 공고화
    """
    
    def __init__(self, 
                 config: Optional[SleepConfig] = None,
                 hypothalamus = None):
        """
        Args:
            config: 수면 설정
            hypothalamus: 시상하부 연결 (에너지 관리)
        """
        self.config = config or SleepConfig()
        self.hypothalamus = hypothalamus
        
        # 현재 상태
        self.stage = SleepStage.WAKE
        self.time = 0.0
        self.cycle_count = 0
        
        # 노이즈 생성기
        self.noise = NoiseGenerator()
        
        # Replay 기록
        self.replay_history: List[ReplayEvent] = []
        
        # 통계
        self.stats = {
            'total_sleep_time': 0.0,
            'total_wake_time': 0.0,
            'replay_count': 0,
            'consolidation_count': 0,
            'sws_cycles': 0,
            'rem_cycles': 0,
        }
        
    def get_noise_level(self) -> float:
        """현재 단계의 노이즈 레벨 반환"""
        noise_map = {
            SleepStage.WAKE: self.config.noise_wake,
            SleepStage.LIGHT_SLEEP: self.config.noise_light,
            SleepStage.DEEP_SLEEP: self.config.noise_deep,
            SleepStage.SWS: self.config.noise_sws,
            SleepStage.REM: self.config.noise_rem,
        }
        return noise_map.get(self.stage, self.config.noise_wake)
    
    def start_sleep(self):
        """
        수면 시작
        
        Returns:
            시작 메시지
        """
        if self.stage != SleepStage.WAKE:
            return "이미 자고 있어요..."
        
        self.stage = SleepStage.LIGHT_SLEEP
        print(f"💤 수면 시작 (N1: 얕은 수면)")
        
        return "수면 모드 시작..."
    
    def wake_up(self):
        """
        기상
        
        Returns:
            기상 메시지
        """
        self.stage = SleepStage.WAKE
        print(f"☀️ 기상!")
        
        return "좋은 아침이에요!"
    
    def run_sleep_cycle(self, 
                        memories: Dict[str, Any],
                        synapses: List[DynamicSynapse],
                        cycles: int = 10,
                        importance_scores: Dict[str, float] = None,
                        progress_callback: Callable = None) -> Dict[str, Any]:
        """
        수면 사이클 실행 (핵심 메서드)
        
        🌊 원리:
            1. 노이즈로 자발적 활성화 유도
            2. 활성화된 기억 재생 (replay)
            3. STP/PTP 기반 시냅스 강화
            4. 에너지 회복
        
        📐 수식:
            activation_prob = noise_level × importance × (1 + S) × PTP
            
        Args:
            memories: 기억 딕셔너리 {memory_id: info}
            synapses: 시냅스 리스트
            cycles: 수면 사이클 수
            importance_scores: 기억 중요도 {memory_id: score}
            progress_callback: 진행 콜백 함수
            
        Returns:
            결과 딕셔너리
        """
        if not memories:
            return {'status': 'no_memories', 'replays': 0}
        
        # 중요도 점수 초기화
        if importance_scores is None:
            importance_scores = {mid: 0.5 for mid in memories}
        
        # 수면 시작
        self.start_sleep()
        
        replayed_memories = []
        consolidated_synapses = []
        
        # 수면 단계 순서 (SWS → REM 반복)
        stage_sequence = [
            SleepStage.LIGHT_SLEEP,
            SleepStage.DEEP_SLEEP,
            SleepStage.SWS,
            SleepStage.SWS,  # SWS 2회
            SleepStage.LIGHT_SLEEP,
            SleepStage.REM,
        ]
        
        for cycle in range(cycles):
            # 단계 전환
            stage_idx = cycle % len(stage_sequence)
            self.stage = stage_sequence[stage_idx]
            noise_level = self.get_noise_level()
            
            if self.stage == SleepStage.SWS:
                self.stats['sws_cycles'] += 1
            elif self.stage == SleepStage.REM:
                self.stats['rem_cycles'] += 1
            
            # =================================================================
            # 🌊 노이즈 기반 자발적 Replay
            # =================================================================
            for memory_id, memory_info in memories.items():
                importance = importance_scores.get(memory_id, 0.5)
                
                # === 활성화 확률 계산 ===
                # 높은 노이즈 + 높은 중요도 = 높은 replay 확률
                # STP/PTP 반영: 최근 활성화된 기억이 더 잘 replay됨
                
                # 기본 활성화 확률
                base_prob = noise_level * importance
                
                # S/PTP 부스트 (해당 기억의 시냅스 평균)
                memory_synapses = self._get_memory_synapses(memory_id, synapses, memory_info)
                stp_boost = 1.0
                ptp_boost = 1.0
                
                if memory_synapses:
                    avg_s = np.mean([getattr(s, 'pre', None) and getattr(s.pre, 'S', 0) or 0 
                                    for s in memory_synapses])
                    avg_ptp = np.mean([getattr(s, 'pre', None) and getattr(s.pre, 'PTP', 1) or 1 
                                      for s in memory_synapses])
                    stp_boost = 1.0 + avg_s
                    ptp_boost = avg_ptp
                
                # 최종 활성화 확률
                activation_prob = base_prob * stp_boost * ptp_boost
                
                # 확률적 replay
                if np.random.random() < activation_prob:
                    # Replay 발생!
                    activation = noise_level + np.random.random() * 0.3
                    
                    replay_event = ReplayEvent(
                        memory_id=memory_id,
                        stage=self.stage,
                        activation=activation,
                        time=self.time,
                        stp_level=avg_s if memory_synapses else 0,
                        ptp_level=avg_ptp if memory_synapses else 1,
                    )
                    self.replay_history.append(replay_event)
                    replayed_memories.append(memory_id)
                    self.stats['replay_count'] += 1
                    
                    # =================================================================
                    # 🧠 Consolidation (시냅스 강화)
                    # 🍪 v1.0: replay count 가중치 추가
                    # =================================================================
                    if activation > self.config.consolidation_threshold:
                        for syn in memory_synapses:
                            # STP/PTP 반영 강화
                            base_factor = self.config.consolidation_rate * stp_boost * ptp_boost
                            
                            # 🍪 v1.0: replay count 가중치 (반복 replay 시 더 강화)
                            replay_boost = 1.0 + (syn.replay_count * 0.02)  # replay마다 2% 추가
                            factor = base_factor * replay_boost
                            
                            syn.consolidate(factor=factor)
                            consolidated_synapses.append(syn)
                        self.stats['consolidation_count'] += 1
            
            # 시간 진행
            self.time += self.config.cycle_duration
            self.stats['total_sleep_time'] += self.config.cycle_duration
            self.cycle_count += 1
            
            # 에너지 회복 (시상하부 연동)
            if self.hypothalamus:
                self.hypothalamus.receive_reward('sleep', self.config.energy_recovery_rate)
            
            # 진행 콜백
            if progress_callback:
                progress_callback(cycle + 1, cycles, self.stage.value)
        
        # 기상
        self.wake_up()
        
        return {
            'status': 'completed',
            'cycles': cycles,
            'replays': len(replayed_memories),
            'unique_replays': len(set(replayed_memories)),
            'consolidations': len(consolidated_synapses),
            'sws_cycles': self.stats['sws_cycles'],
            'rem_cycles': self.stats['rem_cycles'],
            'replay_history': self.replay_history[-20:],  # 최근 20개만
        }
    
    def _get_memory_synapses(self, 
                             memory_id: str, 
                             synapses: List,
                             memory_info: Dict) -> List:
        """특정 기억에 속한 시냅스 추출"""
        # memory_info에 시냅스 목록이 있으면 사용
        if 'synapses_dg_ca3' in memory_info:
            return (memory_info.get('synapses_dg_ca3', []) + 
                   memory_info.get('synapses_ca3_recurrent', []))
        
        # 아니면 이름으로 필터링
        return [s for s in synapses if memory_id in str(getattr(s, 'pre', ''))]
    
    def get_replay_statistics(self) -> Dict[str, Any]:
        """Replay 통계"""
        if not self.replay_history:
            return {'count': 0}
        
        # 단계별 replay 수
        stage_counts = {}
        for event in self.replay_history:
            stage = event.stage.value
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        # 평균 활성화 강도
        avg_activation = np.mean([e.activation for e in self.replay_history])
        
        return {
            'total_replays': len(self.replay_history),
            'stage_distribution': stage_counts,
            'avg_activation': avg_activation,
            'unique_memories': len(set(e.memory_id for e in self.replay_history)),
        }
    
    def reset(self):
        """상태 리셋"""
        self.stage = SleepStage.WAKE
        self.time = 0.0
        self.cycle_count = 0
        self.replay_history = []


# =============================================================================
# 통합 수면 매니저
# =============================================================================

class SleepManager:
    """
    수면 매니저 - BabyBrain/HippoMemory 통합용
    
    사용법:
        manager = SleepManager(hippo_memory, hypothalamus)
        result = manager.sleep(cycles=10)
    """
    
    def __init__(self, 
                 hippo_memory,
                 hypothalamus = None,
                 config: Optional[SleepConfig] = None):
        """
        Args:
            hippo_memory: HippoMemory 인스턴스
            hypothalamus: Hypothalamus 인스턴스 (선택)
            config: 수면 설정
        """
        self.hippo = hippo_memory
        self.hypothalamus = hypothalamus
        self.cycle = SleepWakeCycle(config, hypothalamus)
        
    def sleep(self, 
              cycles: int = 10,
              verbose: bool = True) -> Dict[str, Any]:
        """
        수면 실행
        
        Args:
            cycles: 수면 사이클 수
            verbose: 진행 상황 출력
            
        Returns:
            수면 결과
        """
        if not self.hippo.words:
            if verbose:
                print("💤 기억이 없어서 그냥 쉴게요...")
            return {'status': 'no_memories'}
        
        # 기억 중요도 계산 (MemoryRank)
        try:
            importance_scores = self.hippo.memory_ranker.calculate()
        except:
            importance_scores = {mid: 0.5 for mid in self.hippo.words}
        
        # 시냅스 수집
        all_synapses = (self.hippo.dg_to_ca3_synapses + 
                       self.hippo.ca3_recurrent_synapses)
        
        # 진행 콜백
        def progress(current, total, stage):
            if verbose:
                bar = "█" * (current * 20 // total) + "░" * (20 - current * 20 // total)
                print(f"\r💤 [{bar}] {current}/{total} ({stage})", end="", flush=True)
        
        if verbose:
            print(f"💤 수면 시작... ({cycles} 사이클)")
        
        # 수면 사이클 실행
        result = self.cycle.run_sleep_cycle(
            memories=self.hippo.words,
            synapses=all_synapses,
            cycles=cycles,
            importance_scores=importance_scores,
            progress_callback=progress if verbose else None
        )
        
        if verbose:
            print()  # 줄바꿈
            print(f"☀️ 기상! (replay: {result['replays']}회, 강화: {result['consolidations']})")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """통계"""
        return {
            'sleep_stats': self.cycle.stats,
            'replay_stats': self.cycle.get_replay_statistics(),
        }


# =============================================================================
# 테스트
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌊 Sleep-Wake Cycle Test")
    print("=" * 60)
    
    # 1. 기본 사이클 테스트
    print("\n1️⃣ SleepWakeCycle 테스트...")
    cycle = SleepWakeCycle()
    
    print(f"   현재 상태: {cycle.stage.value}")
    print(f"   노이즈 레벨: {cycle.get_noise_level()}")
    
    cycle.start_sleep()
    print(f"   수면 후 상태: {cycle.stage.value}")
    print(f"   노이즈 레벨: {cycle.get_noise_level()}")
    
    cycle.wake_up()
    print(f"   기상 후 상태: {cycle.stage.value}")
    
    # 2. 가상 메모리로 수면 테스트
    print("\n2️⃣ 가상 메모리 수면 테스트...")
    
    # 가상 메모리
    fake_memories = {
        'cat': {'synapses_dg_ca3': [], 'importance': 0.8},
        'dog': {'synapses_dg_ca3': [], 'importance': 0.6},
        'car': {'synapses_dg_ca3': [], 'importance': 0.4},
    }
    
    importance = {'cat': 0.8, 'dog': 0.6, 'car': 0.4}
    
    result = cycle.run_sleep_cycle(
        memories=fake_memories,
        synapses=[],
        cycles=5,
        importance_scores=importance
    )
    
    print(f"   결과: {result['status']}")
    print(f"   Replay: {result['replays']}회")
    print(f"   SWS 사이클: {result['sws_cycles']}")
    print(f"   REM 사이클: {result['rem_cycles']}")
    
    # 통계
    stats = cycle.get_replay_statistics()
    print(f"   Replay 분포: {stats.get('stage_distribution', {})}")
    
    print("\n" + "=" * 60)
    print("✅ Sleep-Wake Cycle 테스트 완료!")
    print("=" * 60)

