"""
Basal Ganglia: 기저핵 - 행동 선택(Action Selection) & 습관 형성(Habit)
====================================================================

🧠 생물학적 모델:
    기저핵 = 뇌의 "행동 게이트키퍼"
    
    1. 행동 선택 (Action Selection)
       - 여러 행동 옵션 중 하나만 실행 (Go/NoGo)
       - 나머지는 억제
       
    2. 습관 형성 (Habit Formation)
       - 반복된 행동 → 자동화
       - 전두엽 우회 → 빠른 실행
       
    3. 보상 학습 (Reward Learning)
       - 도파민 신호 기반
       - Q-Learning과 유사

📐 핵심 수식:
    Q-value 업데이트: Q(s,a) ← Q(s,a) + α[R + γ·max(Q(s',a')) - Q(s,a)]
    행동 선택: P(a) = softmax(Q(s,a) / τ)
    습관 강도: H = H + β·(success - H)

📚 참고 논문:
    - Schultz (1997): Dopamine reward prediction
    - Graybiel (2008): Habits, rituals, and the evaluative brain
    - Frank (2005): Go/NoGo model of basal ganglia

Author: GNJz (Qquarts)
Version: 1.1
"""

import math
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum


# ============================================
# 데이터 클래스
# ============================================

class ActionType(Enum):
    """행동 타입"""
    GO = "GO"           # 실행
    NOGO = "NOGO"       # 억제
    EXPLORE = "EXPLORE" # 탐색 (새로운 시도)


@dataclass
class Action:
    """행동"""
    name: str
    context: str = ""           # 상황/맥락
    q_value: float = 0.0        # Q-값 (예상 보상)
    execution_count: int = 0    # 실행 횟수
    success_count: int = 0      # 성공 횟수
    habit_strength: float = 0.0 # 습관 강도 (0~1)
    last_executed: float = field(default_factory=time.time)
    
    @property
    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count
    
    @property
    def is_habit(self) -> bool:
        """습관화 여부 (강도 0.7 이상)"""
        return self.habit_strength >= 0.7


@dataclass
class ActionResult:
    """행동 결과"""
    action: Action
    decision: ActionType
    confidence: float           # 확신도
    is_automatic: bool          # 자동 실행 여부 (습관)
    reasoning: str              # 선택 이유


# ============================================
# 기저핵 핵심 클래스
# ============================================

class BasalGanglia:
    """
    기저핵 (Basal Ganglia)
    
    행동 선택 및 습관 형성 시스템
    
    구조:
        Striatum (선조체) - 입력, 상황-행동 매핑
        GPi/SNr (담창구) - 출력, Go/NoGo 결정
        STN (시상하핵) - 억제 조절
        
    학습:
        도파민 신호 기반 강화학습 (TD-Learning)
    """
    
    def __init__(self, bias: Optional[Dict] = None, use_hash: bool = False):
        """
        기저핵 초기화
        
        Args:
            bias: 행동 성향 (DNA 설정값으로 파라미터 미세 조정)
                  - impulsivity (0~1): 높으면 탐색↑, 습관 형성↑
                  - patience (0~1): 높으면 미래 보상 중시
            use_hash: 긴 컨텍스트를 해시로 저장 (메모리 최적화)
        
        Note:
            v1.1: 외부 Bias 주입 지원 (Stem Code 철학)
            - 기본값 = 선천적 성향 (줄기)
            - 외부 주입 = 환경에 따른 분화
        """
        # ===== Q-테이블 (상황 → 행동 → 가치) =====
        # {context: {action_name: Action}}
        self.q_table: Dict[str, Dict[str, Action]] = defaultdict(dict)
        
        # ===== 하이퍼파라미터 (Stem: 기본 성향) =====
        self.params = {
            'alpha': 0.1,           # 학습률
            'gamma': 0.9,           # 할인율 (미래 보상)
            'tau': 0.5,             # 소프트맥스 온도 (탐색 vs 활용)
            'habit_threshold': 0.7,  # 습관화 임계값
            'habit_beta': 0.1,      # 습관 강화율
            'decay_rate': 0.01,     # Q-값 감쇠율
            'exploration_bonus': 0.2, # 탐색 보너스
        }
        
        # [v1.1] DNA Bias 주입
        if bias:
            # 충동성(impulsivity) 높으면 → 탐색↑, 습관 형성↑
            if 'impulsivity' in bias:
                imp = max(0, min(1, bias['impulsivity']))  # 0~1로 클램프
                self.params['tau'] = 0.5 + (imp * 0.5)  # 0.5~1.0
                self.params['habit_threshold'] = 0.7 - (imp * 0.2)  # 0.5~0.7
            
            # 인내심(patience) 높으면 → 미래 보상 중시
            if 'patience' in bias:
                pat = max(0, min(1, bias['patience']))  # 0~1로 클램프
                self.params['gamma'] = 0.8 + (pat * 0.15)  # 0.8~0.95
        
        # [v1.1] 컨텍스트 해싱 모드
        self.use_hash = use_hash
        
        # ===== 도파민 상태 =====
        self.dopamine_level = 0.5  # 현재 도파민 (0~1)
        self.dopamine_baseline = 0.5
        
        # ===== 최근 행동 기록 =====
        self.recent_actions: List[Tuple[str, str, float]] = []  # (context, action, reward)
        self.max_history = 100
        
        # ===== 통계 =====
        self.stats = {
            'total_decisions': 0,
            'habit_executions': 0,
            'deliberate_executions': 0,
            'explorations': 0,
            'total_reward': 0.0,
        }
    
    # ============================================
    # 1. 행동 선택 (Action Selection)
    # ============================================
    
    def select_action(self, 
                      context: str, 
                      possible_actions: List[str],
                      allow_exploration: bool = True) -> ActionResult:
        """
        행동 선택 (Go/NoGo/Explore)
        
        1. 습관 체크 → 자동 실행
        2. Q-값 기반 선택 → 의식적 결정
        3. 탐색 → 새로운 시도
        
        Args:
            context: 현재 상황/맥락
            possible_actions: 가능한 행동 목록
            allow_exploration: 탐색 허용 여부
            
        Returns:
            ActionResult
        """
        self.stats['total_decisions'] += 1
        
        # 컨텍스트 정규화
        context = self._normalize_context(context)
        
        # 1. 습관 체크 (Fast Path)
        habit_action = self._check_habit(context, possible_actions)
        if habit_action:
            self.stats['habit_executions'] += 1
            return ActionResult(
                action=habit_action,
                decision=ActionType.GO,
                confidence=habit_action.habit_strength,
                is_automatic=True,
                reasoning=f"습관: '{habit_action.name}' (강도: {habit_action.habit_strength:.2f})"
            )
        
        # 2. Q-값 기반 선택 (Slow Path)
        actions = self._get_or_create_actions(context, possible_actions)
        
        if not actions:
            # 행동 없음
            return ActionResult(
                action=Action(name="none", context=context),
                decision=ActionType.NOGO,
                confidence=0.0,
                is_automatic=False,
                reasoning="가능한 행동 없음"
            )
        
        # 탐색 vs 활용 결정
        if allow_exploration and self._should_explore():
            # 탐색: 랜덤 또는 낮은 Q-값 행동
            self.stats['explorations'] += 1
            action = self._explore(actions)
            return ActionResult(
                action=action,
                decision=ActionType.EXPLORE,
                confidence=0.3,
                is_automatic=False,
                reasoning=f"탐색: '{action.name}' (새로운 시도)"
            )
        
        # 활용: Q-값 기반 소프트맥스 선택
        self.stats['deliberate_executions'] += 1
        action, confidence = self._exploit(actions)
        
        # Go/NoGo 결정
        decision = ActionType.GO if confidence > 0.3 else ActionType.NOGO
        
        return ActionResult(
            action=action,
            decision=decision,
            confidence=confidence,
            is_automatic=False,
            reasoning=f"선택: '{action.name}' (Q={action.q_value:.2f}, 확신: {confidence:.2f})"
        )
    
    def _check_habit(self, context: str, possible_actions: List[str]) -> Optional[Action]:
        """습관 체크"""
        if context not in self.q_table:
            return None
        
        for action_name in possible_actions:
            if action_name in self.q_table[context]:
                action = self.q_table[context][action_name]
                if action.is_habit:
                    return action
        
        return None
    
    def _get_or_create_actions(self, context: str, action_names: List[str]) -> List[Action]:
        """행동 객체 가져오기 또는 생성"""
        actions = []
        
        for name in action_names:
            if name in self.q_table[context]:
                actions.append(self.q_table[context][name])
            else:
                # 새 행동 생성
                action = Action(
                    name=name,
                    context=context,
                    q_value=self.params['exploration_bonus']  # 초기값에 탐색 보너스
                )
                self.q_table[context][name] = action
                actions.append(action)
        
        return actions
    
    def _should_explore(self) -> bool:
        """탐색할지 결정 (epsilon-greedy 유사)"""
        # 도파민 낮으면 탐색 증가 (새로운 보상 찾기)
        explore_prob = 0.1 + (1 - self.dopamine_level) * 0.2
        return random.random() < explore_prob
    
    def _explore(self, actions: List[Action]) -> Action:
        """탐색: 낮은 실행 횟수 행동 선호"""
        # 실행 횟수가 적은 행동에 가중치
        weights = [1.0 / (a.execution_count + 1) for a in actions]
        total = sum(weights)
        probs = [w / total for w in weights]
        
        return random.choices(actions, weights=probs)[0]
    
    def _exploit(self, actions: List[Action]) -> Tuple[Action, float]:
        """활용: Q-값 기반 소프트맥스 선택"""
        tau = self.params['tau']
        
        # 소프트맥스 확률 계산
        q_values = [a.q_value for a in actions]
        max_q = max(q_values) if q_values else 0
        
        # 수치 안정성을 위해 max 빼기
        exp_values = [math.exp((q - max_q) / tau) for q in q_values]
        total = sum(exp_values)
        probs = [e / total for e in exp_values]
        
        # 선택
        selected = random.choices(actions, weights=probs)[0]
        confidence = probs[actions.index(selected)]
        
        return selected, confidence
    
    def _normalize_context(self, context: str) -> str:
        """
        컨텍스트 정규화
        
        v1.1: use_hash=True 시 긴 문자열 해싱 (메모리 최적화)
        """
        normalized = context.lower().strip()
        
        if self.use_hash and len(normalized) > 50:
            # [v1.1] 긴 컨텍스트는 해시로 변환 (메모리 절약)
            import hashlib
            return hashlib.md5(normalized.encode()).hexdigest()
        
        # 기본: 50자로 자름 (디버깅 용이)
        return normalized[:50]
    
    # ============================================
    # 2. 학습 (Learning)
    # ============================================
    
    def learn(self, context: str, action_name: str, reward: float, 
              next_context: str = None):
        """
        보상 학습 (TD-Learning)
        
        Q(s,a) ← Q(s,a) + α[R + γ·max(Q(s',a')) - Q(s,a)]
        
        Args:
            context: 상황
            action_name: 실행한 행동
            reward: 받은 보상 (-1 ~ +1)
            next_context: 다음 상황 (None이면 종료 상태)
        """
        context = self._normalize_context(context)
        
        # 행동 가져오기
        if action_name not in self.q_table[context]:
            self.q_table[context][action_name] = Action(
                name=action_name, context=context
            )
        
        action = self.q_table[context][action_name]
        
        # 실행 기록
        action.execution_count += 1
        action.last_executed = time.time()
        
        if reward > 0:
            action.success_count += 1
        
        # TD 업데이트
        alpha = self.params['alpha']
        gamma = self.params['gamma']
        
        # 다음 상태의 최대 Q-값
        if next_context:
            next_context = self._normalize_context(next_context)
            next_q_values = [a.q_value for a in self.q_table[next_context].values()]
            max_next_q = max(next_q_values) if next_q_values else 0
        else:
            max_next_q = 0
        
        # Q-value 업데이트
        td_error = reward + gamma * max_next_q - action.q_value
        action.q_value += alpha * td_error
        
        # 도파민 업데이트 (TD error 기반)
        self._update_dopamine(td_error)
        
        # 습관 강화 (성공 시)
        if reward > 0:
            self._strengthen_habit(action)
        elif reward < 0:
            self._weaken_habit(action)
        
        # 기록
        self.recent_actions.append((context, action_name, reward))
        self.recent_actions = self.recent_actions[-self.max_history:]
        self.stats['total_reward'] += reward
    
    def _update_dopamine(self, td_error: float):
        """도파민 업데이트 (TD error 기반)"""
        # TD error > 0: 예상보다 좋음 → 도파민 증가
        # TD error < 0: 예상보다 나쁨 → 도파민 감소
        delta = td_error * 0.1
        self.dopamine_level = max(0, min(1, self.dopamine_level + delta))
        
        # 기준선으로 서서히 복귀
        decay = 0.05
        self.dopamine_level += decay * (self.dopamine_baseline - self.dopamine_level)
    
    def _strengthen_habit(self, action: Action):
        """습관 강화"""
        beta = self.params['habit_beta']
        # H = H + β·(1 - H) → 점진적으로 1에 접근
        action.habit_strength += beta * (1 - action.habit_strength)
    
    def _weaken_habit(self, action: Action):
        """습관 약화"""
        beta = self.params['habit_beta'] * 0.5  # 약화는 더 느리게
        action.habit_strength = max(0, action.habit_strength - beta)
    
    # ============================================
    # 3. 습관 관리
    # ============================================
    
    def get_habits(self) -> List[Action]:
        """모든 습관화된 행동 반환"""
        habits = []
        for context, actions in self.q_table.items():
            for action in actions.values():
                if action.is_habit:
                    habits.append(action)
        return habits
    
    def break_habit(self, context: str, action_name: str):
        """습관 깨기"""
        context = self._normalize_context(context)
        if context in self.q_table and action_name in self.q_table[context]:
            self.q_table[context][action_name].habit_strength = 0.0
    
    def decay_all(self):
        """모든 Q-값 감쇠 (사용하지 않는 행동 잊기)"""
        decay = self.params['decay_rate']
        for context, actions in self.q_table.items():
            for action in actions.values():
                action.q_value *= (1 - decay)
                # 너무 오래된 습관도 약화
                time_since = time.time() - action.last_executed
                if time_since > 3600:  # 1시간 이상
                    action.habit_strength *= 0.99
    
    # ============================================
    # 4. 상태 조회
    # ============================================
    
    def get_best_action(self, context: str) -> Optional[Action]:
        """특정 상황에서 최선의 행동"""
        context = self._normalize_context(context)
        if context not in self.q_table:
            return None
        
        actions = list(self.q_table[context].values())
        if not actions:
            return None
        
        return max(actions, key=lambda a: a.q_value)
    
    def get_state(self) -> Dict[str, Any]:
        """전체 상태 반환"""
        habits = self.get_habits()
        
        return {
            'dopamine': round(self.dopamine_level, 2),
            'total_contexts': len(self.q_table),
            'total_actions': sum(len(a) for a in self.q_table.values()),
            'habits': [
                {'context': h.context, 'action': h.name, 'strength': round(h.habit_strength, 2)}
                for h in habits[:5]  # 상위 5개
            ],
            'stats': self.stats,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.stats.copy()


# ============================================
# 테스트
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Basal Ganglia (기저핵) 테스트")
    print("=" * 60)
    
    bg = BasalGanglia()
    
    # 1. 행동 선택 테스트
    print("\n🎯 [1] 행동 선택 테스트")
    print("-" * 40)
    
    context = "인사 상황"
    actions = ["안녕하세요", "반갑습니다", "하이"]
    
    result = bg.select_action(context, actions)
    print(f"  상황: '{context}'")
    print(f"  가능한 행동: {actions}")
    print(f"  선택: {result.action.name}")
    print(f"  결정: {result.decision.value}")
    print(f"  이유: {result.reasoning}")
    
    # 2. 학습 테스트
    print("\n📚 [2] 학습 테스트 (보상 기반)")
    print("-" * 40)
    
    # 반복 학습
    for i in range(20):
        # "안녕하세요"에 높은 보상
        bg.learn(context, "안녕하세요", reward=0.8)
        # 다른 행동에 낮은 보상
        bg.learn(context, "하이", reward=0.2)
    
    print(f"  20회 학습 후:")
    for action_name in actions:
        if action_name in bg.q_table[bg._normalize_context(context)]:
            action = bg.q_table[bg._normalize_context(context)][action_name]
            print(f"    '{action_name}': Q={action.q_value:.2f}, 습관강도={action.habit_strength:.2f}")
    
    # 3. 습관 형성 테스트
    print("\n⚡ [3] 습관 형성 테스트")
    print("-" * 40)
    
    # 더 많은 반복
    for i in range(30):
        bg.learn(context, "안녕하세요", reward=0.9)
    
    habits = bg.get_habits()
    print(f"  형성된 습관: {len(habits)}개")
    for h in habits:
        print(f"    '{h.context}' → '{h.name}' (강도: {h.habit_strength:.2f})")
    
    # 4. 습관화 후 행동 선택
    print("\n🔄 [4] 습관화 후 행동 선택")
    print("-" * 40)
    
    result = bg.select_action(context, actions)
    print(f"  선택: {result.action.name}")
    print(f"  자동 실행: {result.is_automatic}")
    print(f"  이유: {result.reasoning}")
    
    # 5. 도파민 상태
    print("\n💊 [5] 도파민 상태")
    print("-" * 40)
    print(f"  현재 도파민: {bg.dopamine_level:.2f}")
    
    # 6. 전체 상태
    print("\n📊 [6] 전체 상태")
    print("-" * 40)
    state = bg.get_state()
    print(f"  총 컨텍스트: {state['total_contexts']}")
    print(f"  총 행동: {state['total_actions']}")
    print(f"  통계: {state['stats']}")
    
    print("\n" + "=" * 60)
    print("✅ 기저핵 테스트 완료!")
    print("=" * 60)

