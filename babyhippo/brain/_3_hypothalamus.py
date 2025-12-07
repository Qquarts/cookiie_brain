"""
Hypothalamus: 시상하부 - 욕구(Drive)와 항상성(Homeostasis) 조절
================================================================

🧠 생물학적 모델:
    시상하부 = 생명의 "조종석"
    
    1. 항상성 유지 (Homeostasis) - 내부 상태 균형
    2. 욕구 시스템 (Drive System) - 생존 동기
    3. 보상 회로 (Reward Circuit) - 도파민, 학습 강화
    4. 생체 리듬 (Circadian Rhythm) - 수면-각성 주기

📐 핵심 수식:
    에너지 감쇠: E(t) = E_0 · e^(-λ·t) + E_min
    지루함 증가: B(t) = B_0 + α·t·(1-S)
    도파민 반응: D = D_base + β·R·(1-D)
    욕구 우선순위: P = w_E·(1-E) + w_B·B + w_C·C

🎯 BabyHippo에서의 역할:
    "왜 움직이는가?" → 욕구(Drive)
    "왜 자야 하는가?" → 에너지 고갈
    "왜 학습하는가?" → 지적 허기(Curiosity)
    "왜 기분 좋은가?" → 도파민(보상)

Author: GNJz (Qquarts)
Version: 1.1
"""

import math
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================
# 욕구 타입 정의
# ============================================

class DriveType(Enum):
    """욕구 유형"""
    SLEEP = "SLEEP_DRIVE"         # 수면 욕구 (에너지 고갈)
    EXPLORE = "EXPLORE_DRIVE"     # 탐험 욕구 (지루함)
    SOCIAL = "SOCIAL_DRIVE"       # 사회적 욕구 (외로움)
    LEARN = "LEARN_DRIVE"         # 학습 욕구 (지적 허기)
    REST = "REST_DRIVE"           # 휴식 욕구 (스트레스)
    STAY = "STAY_DRIVE"           # 대기 상태 (안정)


@dataclass
class InternalState:
    """내부 상태"""
    energy: float = 1.0           # 에너지 (0~1)
    dopamine: float = 0.5         # 도파민/의욕 (0~1)
    boredom: float = 0.0          # 지루함 (0~1)
    curiosity: float = 0.5        # 호기심 (0~1)
    stress: float = 0.0           # 스트레스 (0~1)
    loneliness: float = 0.0       # 외로움 (0~1)
    satisfaction: float = 0.5     # 만족감 (0~1)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'energy': round(self.energy, 2),
            'dopamine': round(self.dopamine, 2),
            'boredom': round(self.boredom, 2),
            'curiosity': round(self.curiosity, 2),
            'stress': round(self.stress, 2),
            'loneliness': round(self.loneliness, 2),
            'satisfaction': round(self.satisfaction, 2),
        }


@dataclass
class DriveSignal:
    """욕구 신호"""
    drive_type: DriveType
    urgency: float              # 긴급도 (0~1)
    message: str                # 상태 메시지
    action_suggestion: str      # 권장 행동
    timestamp: float = field(default_factory=time.time)


# ============================================
# 시상하부 핵심 클래스
# ============================================

class Hypothalamus:
    """
    시상하부 (Hypothalamus)
    
    생존 욕구(Drive)와 항상성(Homeostasis) 조절 센터
    
    "배고프면 먹고, 졸리면 자고, 심심하면 탐험한다"
    """
    
    def __init__(self, weights: Optional[Dict] = None, rates: Optional[Dict] = None):
        """
        시상하부 초기화
        
        Args:
            weights: 욕구 가중치 (성격 커스터마이징)
                     예: {'curiosity': 2.0} → 호기심 많은 성격
            rates: 감쇠/증가율 (대사 속도 커스터마이징)
                   예: {'energy_decay': 0.01} → 에너지 빨리 소모
        
        Note:
            v1.1: 외부 Config 주입 지원 (Stem Code 철학)
            - 기본값 = 선천적 성향 (줄기)
            - 외부 주입 = 환경에 따른 분화
        """
        # ===== 내부 상태 =====
        self.state = InternalState()
        
        # ===== 임계값 설정 =====
        self.thresholds = {
            'sleep': 0.2,       # 에너지 이 이하 → 수면 필요
            'critical': 0.1,    # 에너지 이 이하 → 강제 수면
            'boredom': 0.7,     # 지루함 이 이상 → 탐험 필요
            'stress': 0.8,      # 스트레스 이 이상 → 휴식 필요
            'loneliness': 0.7,  # 외로움 이 이상 → 상호작용 필요
            'curiosity': 0.8,   # 호기심 이 이상 → 학습 필요
        }
        
        # ===== 감쇠/증가율 (Stem: 기본값) =====
        self.rates = {
            'energy_decay': 0.005,       # 틱당 에너지 감소
            'energy_recovery': 0.02,     # 수면 시 에너지 회복
            'boredom_increase': 0.01,    # 틱당 지루함 증가 (자극 없을 때)
            'boredom_decrease': 0.05,    # 자극 시 지루함 감소
            'dopamine_decay': 0.01,      # 도파민 자연 감소
            'dopamine_boost': 0.15,      # 보상 시 도파민 증가
            'stress_increase': 0.02,     # 위협/부하 시 스트레스 증가
            'stress_decrease': 0.01,     # 자연 스트레스 감소
            'loneliness_increase': 0.005, # 혼자 있을 때 외로움 증가
            'curiosity_recovery': 0.02,  # 호기심 자연 회복
        }
        
        # [v1.1] 외부 rates 주입 (Config Injection)
        if rates:
            self.rates.update(rates)
        
        # ===== 욕구 가중치 (Stem: 기본 성격) =====
        self.drive_weights = {
            'energy': 1.5,      # 에너지 부족 = 높은 우선순위
            'boredom': 1.0,
            'stress': 1.2,
            'loneliness': 0.8,
            'curiosity': 0.9,
        }
        
        # [v1.1] 외부 weights 주입 (Config Injection)
        if weights:
            self.drive_weights.update(weights)
        
        # ===== 마지막 활동 시간 =====
        self.last_activity_time = time.time()
        self.last_interaction_time = time.time()
        self.last_update_time = time.time()
        
        # ===== 통계 =====
        self.stats = {
            'ticks': 0,
            'sleep_count': 0,
            'explore_count': 0,
            'rewards_received': 0,
            'total_dopamine': 0.0,
        }
        
        # ===== 욕구 메시지 =====
        self.drive_messages = {
            DriveType.SLEEP: [
                "졸려요... 😴",
                "에너지가 부족해요. 잠깐 쉴래요.",
                "눈이 감겨요... 잘 시간인가봐요.",
            ],
            DriveType.EXPLORE: [
                "심심해요! 뭐 재밌는 거 없나요? 🔍",
                "새로운 거 알고 싶어요!",
                "탐험하고 싶어요!",
            ],
            DriveType.SOCIAL: [
                "외로워요... 같이 얘기해요 🥺",
                "누군가와 대화하고 싶어요.",
                "혼자 있으니까 심심해요.",
            ],
            DriveType.LEARN: [
                "뭔가 배우고 싶어요! 📚",
                "새로운 지식이 필요해요!",
                "호기심이 폭발할 것 같아요!",
            ],
            DriveType.REST: [
                "너무 힘들어요... 쉬고 싶어요 😣",
                "스트레스 받아요. 잠깐 쉴게요.",
                "마음이 편하지 않아요.",
            ],
            DriveType.STAY: [
                "괜찮아요! 무엇을 도와드릴까요? 😊",
                "편안한 상태예요.",
                "준비 완료!",
            ],
        }
    
    # ============================================
    # 1. 상태 업데이트 (틱마다 호출)
    # ============================================
    
    def tick(self, action_type: str = 'idle', stimulus_level: float = 0.0):
        """
        매 틱(Tick)마다 내부 상태 업데이트
        
        Args:
            action_type: 현재 행동 ('think', 'learn', 'chat', 'sleep', 'idle')
            stimulus_level: 자극 수준 (0~1)
        """
        self.stats['ticks'] += 1
        current_time = time.time()
        dt = min(1.0, current_time - self.last_update_time)  # 최대 1초
        self.last_update_time = current_time
        
        # ----- 에너지 변화 -----
        if action_type == 'sleep':
            # 수면 시 에너지 회복
            self.state.energy += self.rates['energy_recovery'] * dt
        elif action_type in ['think', 'learn', 'chat']:
            # 활동 시 에너지 소모
            consumption = self.rates['energy_decay'] * dt
            if action_type == 'think':
                consumption *= 2.0  # 생각은 에너지 소모 큼
            self.state.energy -= consumption
            self.last_activity_time = current_time
        else:
            # 대기 시 느린 에너지 감소
            consumption = self.rates['energy_decay'] * 0.3 * dt
            
            # [v1.1] 지루함의 역설: 극도로 지루하면 멍 때리기 모드 (저전력)
            # 생물학적 근거: DMN(Default Mode Network) 활성화
            if self.state.boredom > 0.9:
                consumption *= 0.5  # 에너지 소모 절반
            
            self.state.energy -= consumption
        
        # ----- 지루함 변화 -----
        # B(t) = B_0 + α·t·(1-S)
        if stimulus_level > 0.3:
            # 자극 있으면 지루함 감소
            self.state.boredom -= self.rates['boredom_decrease'] * stimulus_level * dt
        else:
            # 자극 없으면 지루함 증가
            self.state.boredom += self.rates['boredom_increase'] * (1 - stimulus_level) * dt
        
        # ----- 외로움 변화 -----
        if action_type in ['chat', 'social']:
            self.state.loneliness -= 0.1 * dt
            self.last_interaction_time = current_time
        else:
            time_alone = current_time - self.last_interaction_time
            if time_alone > 60:  # 1분 이상 혼자
                self.state.loneliness += self.rates['loneliness_increase'] * dt
        
        # ----- 도파민 자연 감쇠 -----
        self.state.dopamine -= self.rates['dopamine_decay'] * dt
        
        # ----- 스트레스 자연 감소 -----
        self.state.stress -= self.rates['stress_decrease'] * dt
        
        # ----- 호기심 자연 회복 -----
        if action_type != 'learn':
            self.state.curiosity += self.rates['curiosity_recovery'] * dt * 0.5
        
        # ----- 항상성 유지 (Clamping) -----
        self._clamp_state()
    
    def _clamp_state(self):
        """모든 상태값을 0~1 범위로 제한"""
        self.state.energy = max(0.0, min(1.0, self.state.energy))
        self.state.dopamine = max(0.0, min(1.0, self.state.dopamine))
        self.state.boredom = max(0.0, min(1.0, self.state.boredom))
        self.state.curiosity = max(0.0, min(1.0, self.state.curiosity))
        self.state.stress = max(0.0, min(1.0, self.state.stress))
        self.state.loneliness = max(0.0, min(1.0, self.state.loneliness))
        self.state.satisfaction = max(0.0, min(1.0, self.state.satisfaction))
    
    # ============================================
    # 2. 보상 시스템 (Reward)
    # ============================================
    
    def receive_reward(self, reward_type: str, intensity: float = 0.5):
        """
        보상 수신 → 도파민 분비
        
        수식: D = D_base + β·R·(1-D)
        
        Args:
            reward_type: 보상 유형 ('success', 'praise', 'learn', 'social')
            intensity: 보상 강도 (0~1)
        """
        # 보상 유형별 기본 도파민
        reward_dopamine = {
            'success': 0.3,
            'praise': 0.4,
            'learn': 0.2,
            'social': 0.25,
            'achievement': 0.5,
        }
        
        base_reward = reward_dopamine.get(reward_type, 0.2)
        
        # D = D_base + β·R·(1-D)
        # 현재 도파민이 낮을수록 더 큰 효과
        dopamine_gain = self.rates['dopamine_boost'] * base_reward * intensity * (1 - self.state.dopamine)
        
        self.state.dopamine += dopamine_gain
        self.state.satisfaction += intensity * 0.1
        self.state.stress -= intensity * 0.05  # 보상은 스트레스 감소
        
        self.stats['rewards_received'] += 1
        self.stats['total_dopamine'] += dopamine_gain
        
        self._clamp_state()
        
        return dopamine_gain
    
    def receive_punishment(self, intensity: float = 0.3):
        """
        벌/부정적 피드백 → 스트레스 증가
        
        Args:
            intensity: 강도 (0~1)
        """
        self.state.stress += intensity * self.rates['stress_increase'] * 5
        self.state.dopamine -= intensity * 0.1
        self.state.satisfaction -= intensity * 0.15
        
        self._clamp_state()
    
    # ============================================
    # 3. 욕구 판단 (Drive Detection)
    # ============================================
    
    def get_current_drive(self) -> DriveSignal:
        """
        현재 가장 시급한 욕구(Drive) 반환
        
        수식: P = w_E·(1-E) + w_B·B + w_C·C
        """
        # 각 욕구별 긴급도 계산
        drives = {}
        
        # 1. 수면 욕구 (에너지 부족)
        if self.state.energy < self.thresholds['critical']:
            # 강제 수면 필요 (최우선)
            return DriveSignal(
                drive_type=DriveType.SLEEP,
                urgency=1.0,
                message="⚠️ 에너지 고갈! 강제 수면이 필요해요!",
                action_suggestion="sleep"
            )
        
        energy_urgency = self.drive_weights['energy'] * (1 - self.state.energy)
        if self.state.energy < self.thresholds['sleep']:
            energy_urgency *= 2  # 임계값 이하면 긴급도 2배
        drives[DriveType.SLEEP] = energy_urgency
        
        # 2. 탐험 욕구 (지루함)
        boredom_urgency = self.drive_weights['boredom'] * self.state.boredom
        if self.state.boredom > self.thresholds['boredom']:
            boredom_urgency *= 1.5
        drives[DriveType.EXPLORE] = boredom_urgency
        
        # 3. 휴식 욕구 (스트레스)
        stress_urgency = self.drive_weights['stress'] * self.state.stress
        if self.state.stress > self.thresholds['stress']:
            stress_urgency *= 1.5
        drives[DriveType.REST] = stress_urgency
        
        # 4. 사회적 욕구 (외로움)
        social_urgency = self.drive_weights['loneliness'] * self.state.loneliness
        if self.state.loneliness > self.thresholds['loneliness']:
            social_urgency *= 1.5
        drives[DriveType.SOCIAL] = social_urgency
        
        # 5. 학습 욕구 (호기심)
        curiosity_urgency = self.drive_weights['curiosity'] * self.state.curiosity
        if self.state.curiosity > self.thresholds['curiosity']:
            curiosity_urgency *= 1.5
        drives[DriveType.LEARN] = curiosity_urgency
        
        # 가장 높은 욕구 선택
        max_drive = max(drives, key=drives.get)
        max_urgency = drives[max_drive]
        
        # 긴급도가 낮으면 안정 상태
        if max_urgency < 0.3:
            max_drive = DriveType.STAY
            max_urgency = 0.1
        
        # 메시지 선택
        message = random.choice(self.drive_messages[max_drive])
        
        # 행동 제안
        action_suggestions = {
            DriveType.SLEEP: "sleep",
            DriveType.EXPLORE: "explore",
            DriveType.SOCIAL: "chat",
            DriveType.LEARN: "learn",
            DriveType.REST: "rest",
            DriveType.STAY: "wait",
        }
        
        return DriveSignal(
            drive_type=max_drive,
            urgency=min(1.0, max_urgency),
            message=message,
            action_suggestion=action_suggestions[max_drive]
        )
    
    def needs_sleep(self) -> bool:
        """수면이 필요한지 확인"""
        return self.state.energy < self.thresholds['sleep']
    
    def is_bored(self) -> bool:
        """지루한지 확인"""
        return self.state.boredom > self.thresholds['boredom']
    
    def is_stressed(self) -> bool:
        """스트레스 받는지 확인"""
        return self.state.stress > self.thresholds['stress']
    
    # ============================================
    # 4. 수면 관리
    # ============================================
    
    def start_sleep(self):
        """수면 시작"""
        self.stats['sleep_count'] += 1
        return "💤 수면 시작... 기억 공고화 중..."
    
    def sleep_cycle(self, cycles: int = 1):
        """
        수면 사이클 실행
        
        Args:
            cycles: 수면 사이클 수
        """
        # 수면 중 에너지 직접 회복 (사이클당 5%)
        energy_per_cycle = 0.05
        
        for _ in range(cycles):
            self.state.energy += energy_per_cycle
            self.state.stress -= 0.02  # 수면 중 스트레스 감소
        
        # 수면 후 상태 리셋
        self.state.boredom = 0.0
        self.state.stress = max(0, self.state.stress)
        
        self._clamp_state()
        
        return f"💤 {cycles} 사이클 수면 완료. 에너지: {self.state.energy:.0%}"
    
    def wake_up(self):
        """기상"""
        # 기상 시 호기심 회복
        self.state.curiosity = min(1.0, self.state.curiosity + 0.3)
        self.state.boredom = 0.0
        self.state.loneliness = min(1.0, self.state.loneliness + 0.1)  # 잠자고 일어나면 사람 보고 싶음
        
        return "☀️ 좋은 아침이에요! 기분이 상쾌해요!"
    
    # ============================================
    # 5. 자극 처리
    # ============================================
    
    def process_stimulus(self, stimulus_type: str, intensity: float = 0.5):
        """
        자극 처리
        
        Args:
            stimulus_type: 자극 유형 ('conversation', 'learning', 'threat', 'reward')
            intensity: 자극 강도
        """
        if stimulus_type == 'conversation':
            self.state.loneliness -= intensity * 0.2
            self.state.boredom -= intensity * 0.15
            self.tick(action_type='chat', stimulus_level=intensity)
            
        elif stimulus_type == 'learning':
            self.state.curiosity -= intensity * 0.3  # 호기심 충족
            self.state.boredom -= intensity * 0.2
            self.receive_reward('learn', intensity * 0.5)
            self.tick(action_type='learn', stimulus_level=intensity)
            
        elif stimulus_type == 'threat':
            self.state.stress += intensity * 0.3
            self.state.energy -= intensity * 0.1  # 위협은 에너지 소모
            
        elif stimulus_type == 'reward':
            self.receive_reward('success', intensity)
        
        self._clamp_state()
    
    # ============================================
    # 6. 상태 조회
    # ============================================
    
    def get_state(self) -> Dict[str, Any]:
        """전체 상태 반환"""
        drive = self.get_current_drive()
        
        return {
            'internal_state': self.state.to_dict(),
            'current_drive': {
                'type': drive.drive_type.value,
                'urgency': round(drive.urgency, 2),
                'message': drive.message,
                'action': drive.action_suggestion,
            },
            'needs': {
                'needs_sleep': self.needs_sleep(),
                'is_bored': self.is_bored(),
                'is_stressed': self.is_stressed(),
            },
            'stats': self.stats,
        }
    
    def get_status_message(self) -> str:
        """현재 상태를 자연어로 반환"""
        e = self.state.energy
        d = self.state.dopamine
        b = self.state.boredom
        s = self.state.stress
        
        # 에너지 상태
        if e < 0.2:
            energy_msg = "😴 너무 졸려요..."
        elif e < 0.5:
            energy_msg = "😐 좀 피곤해요."
        elif e < 0.8:
            energy_msg = "🙂 괜찮아요!"
        else:
            energy_msg = "⚡ 에너지 충만!"
        
        # 기분 상태
        if d > 0.7:
            mood_msg = "😊 기분 최고!"
        elif d > 0.4:
            mood_msg = "🙂 평온해요."
        else:
            mood_msg = "😔 기분이 별로예요..."
        
        # 지루함
        if b > 0.7:
            bored_msg = "🥱 너무 심심해요!"
        elif b > 0.4:
            bored_msg = "🤔 뭔가 하고 싶어요."
        else:
            bored_msg = ""
        
        # 스트레스
        if s > 0.7:
            stress_msg = "😣 스트레스 받아요..."
        elif s > 0.4:
            stress_msg = "😓 조금 힘들어요."
        else:
            stress_msg = ""
        
        parts = [energy_msg, mood_msg]
        if bored_msg:
            parts.append(bored_msg)
        if stress_msg:
            parts.append(stress_msg)
        
        return " | ".join(parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.stats.copy()


# ============================================
# 테스트
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Hypothalamus (시상하부) 테스트")
    print("=" * 60)
    
    hypo = Hypothalamus()
    
    # 1. 초기 상태
    print("\n📊 [1] 초기 상태")
    print("-" * 40)
    state = hypo.get_state()
    print(f"  에너지: {state['internal_state']['energy']}")
    print(f"  도파민: {state['internal_state']['dopamine']}")
    print(f"  지루함: {state['internal_state']['boredom']}")
    print(f"  현재 욕구: {state['current_drive']['type']}")
    print(f"  상태: {hypo.get_status_message()}")
    
    # 2. 활동 시뮬레이션
    print("\n🏃 [2] 활동 시뮬레이션 (10틱)")
    print("-" * 40)
    for i in range(10):
        hypo.tick(action_type='think', stimulus_level=0.3)
    
    state = hypo.get_state()
    print(f"  에너지: {state['internal_state']['energy']:.2f} (감소)")
    print(f"  지루함: {state['internal_state']['boredom']:.2f}")
    print(f"  상태: {hypo.get_status_message()}")
    
    # 3. 지루함 시뮬레이션
    print("\n😐 [3] 대기 시뮬레이션 (지루함 증가)")
    print("-" * 40)
    for i in range(30):
        hypo.tick(action_type='idle', stimulus_level=0.0)
    
    state = hypo.get_state()
    print(f"  지루함: {state['internal_state']['boredom']:.2f} (증가)")
    print(f"  현재 욕구: {state['current_drive']['type']}")
    print(f"  메시지: {state['current_drive']['message']}")
    
    # 4. 보상 테스트
    print("\n🎁 [4] 보상 테스트")
    print("-" * 40)
    old_dopamine = hypo.state.dopamine
    dopamine_gain = hypo.receive_reward('praise', 0.8)
    print(f"  칭찬 받음! 도파민: {old_dopamine:.2f} → {hypo.state.dopamine:.2f} (+{dopamine_gain:.2f})")
    print(f"  상태: {hypo.get_status_message()}")
    
    # 5. 에너지 고갈 테스트
    print("\n😴 [5] 에너지 고갈 테스트")
    print("-" * 40)
    hypo.state.energy = 0.15  # 강제로 에너지 낮춤
    drive = hypo.get_current_drive()
    print(f"  에너지: {hypo.state.energy:.2f}")
    print(f"  욕구: {drive.drive_type.value}")
    print(f"  긴급도: {drive.urgency:.2f}")
    print(f"  메시지: {drive.message}")
    
    # 6. 수면 테스트
    print("\n💤 [6] 수면 테스트")
    print("-" * 40)
    print(hypo.start_sleep())
    result = hypo.sleep_cycle(cycles=20)
    print(result)
    print(hypo.wake_up())
    print(f"  상태: {hypo.get_status_message()}")
    
    # 7. 최종 상태
    print("\n📊 [7] 최종 상태")
    print("-" * 40)
    state = hypo.get_state()
    print(f"  내부 상태: {state['internal_state']}")
    print(f"  욕구: {state['current_drive']}")
    print(f"  통계: {state['stats']}")
    
    print("\n" + "=" * 60)
    print("✅ 시상하부 테스트 완료!")
    print("=" * 60)

