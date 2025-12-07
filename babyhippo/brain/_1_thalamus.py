"""
Thalamus: 시상 - 감각 중계 & 주의 게이팅
========================================

🧠 생물학적 모델:
    시상 = 뇌의 "중앙 교환대"
    
    1. 감각 중계 (Sensory Relay)
       - 거의 모든 감각이 시상 → 피질로 전달
       - 후각만 예외 (직접 피질로)
       
    2. 주의 게이팅 (Attention Gating)
       - "어떤 정보에 집중할지" 필터링
       - 관련 없는 정보 억제
       
    3. 의식 스위치 (Consciousness Gate)
       - 각성 상태 조절
       - 수면 시 감각 차단

📐 실제 구현 수식:
    현저성 계산:
        S = base_salience × pattern_boost × intensity × arousal
        (위협 감지 시 boost × 2)
    
    주의 가중치:
        W = attention_weight[modality] × focus_boost × (1 + salience)
        (focus_boost = 1.5 if focused else 1.0)
    
    게이팅 (임계값 기반):
        pass = (W ≥ threshold)
        threshold = 0.3 (default)
    
    채널 제한:
        output = top_k(passed_inputs, k=max_channels)

📚 참고 논문:
    - Sherman & Guillery (2006): Thalamus
    - Crick (1984): Thalamus as gateway to consciousness

Author: GNJz (Qquarts)
Version: 1.1
"""

import math
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque  # [보완 2] deque 추가
from enum import Enum


# ============================================
# 데이터 클래스
# ============================================

class ModalityType(Enum):
    """감각 양식"""
    VISUAL = "visual"           # 시각
    AUDITORY = "auditory"       # 청각
    SEMANTIC = "semantic"       # 의미
    EMOTIONAL = "emotional"     # 감정
    EPISODIC = "episodic"       # 에피소드
    MOTOR = "motor"             # 운동
    INTERNAL = "internal"       # 내부 상태


@dataclass
class SensoryInput:
    """감각 입력"""
    content: Any                # 내용
    modality: ModalityType      # 감각 양식
    intensity: float = 1.0      # 강도 (0~1)
    salience: float = 0.5       # 현저성 (0~1) - 주의 끌기 정도
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


@dataclass
class FilteredOutput:
    """필터링된 출력"""
    content: Any
    modality: ModalityType
    attention_weight: float     # 주의 가중치
    passed_gate: bool           # 게이트 통과 여부
    priority: int               # 우선순위 (낮을수록 높음)


# ============================================
# 시상 핵심 클래스
# ============================================

class Thalamus:
    """
    시상 (Thalamus)
    
    감각 중계 및 주의 게이팅 시스템
    
    구조:
        LGN (외측슬상핵) - 시각 중계
        MGN (내측슬상핵) - 청각 중계
        Pulvinar - 주의 조절
        Reticular Nucleus - 게이팅 제어
    """
    
    def __init__(self):
        # ===== 주의 상태 =====
        self.attention_focus: Optional[ModalityType] = None
        self.attention_weights: Dict[ModalityType, float] = {
            m: 0.5 for m in ModalityType
        }
        
        # ===== 게이팅 파라미터 =====
        self.params = {
            'gate_threshold': 0.3,      # 게이트 통과 임계값
            'salience_boost': 1.5,      # 현저성 부스트
            'attention_decay': 0.1,     # 주의 감쇠율
            'max_channels': 3,          # 동시 처리 가능한 채널 수
            'novelty_bonus': 0.3,       # 새로운 자극 보너스
        }
        
        # ===== 각성 상태 =====
        self.arousal_level = 1.0        # 각성 수준 (0=수면, 1=완전 각성)
        self.consciousness_gate = True  # 의식 게이트 (True=열림)
        
        # ===== 최근 입력 기록 =====
        # [보완 2] deque 사용으로 메모리/성능 최적화
        # - 리스트 슬라이싱은 매번 새 객체 생성
        # - deque(maxlen=N)은 자동으로 오래된 것 제거 (O(1))
        self.recent_inputs: deque = deque(maxlen=50)
        
        # ===== 현저성 키워드 (주의를 끄는 것들) =====
        self.salient_patterns = {
            'threat': ['위험', '죽', '공격', 'danger', 'kill', 'attack'],
            'name': ['이름', '너', '당신', 'name', 'you'],
            'question': ['?', '뭐', '왜', '어떻게', 'what', 'why', 'how'],
            'reward': ['좋아', '칭찬', '감사', 'good', 'thanks', 'great'],
        }
        
        # ===== 통계 =====
        self.stats = {
            'total_inputs': 0,
            'passed_gate': 0,
            'blocked': 0,
            'attention_shifts': 0,
        }
    
    # ============================================
    # 1. 감각 중계 (Sensory Relay)
    # ============================================
    
    def relay(self, inputs: List[SensoryInput]) -> List[FilteredOutput]:
        """
        감각 입력 중계 및 필터링
        
        Args:
            inputs: 감각 입력 목록
            
        Returns:
            필터링된 출력 목록
            
        📐 처리 순서:
            1. 의식 게이트 확인
            2. [보완 1] 주의력 자연 감쇠
            3. 현저성 계산
            4. 주의 가중치 적용
            5. 게이팅 (임계값 기반)
            6. 우선순위 정렬
            7. 채널 제한
        """
        if not self.consciousness_gate:
            # 의식 게이트 닫힘 (수면 등)
            return []
        
        self.stats['total_inputs'] += len(inputs)
        
        # [보완 1] 주의력 자연 감쇠 (시간이 지나면 주의 집중이 풀림)
        # 매 입력 처리마다 조금씩 균형 상태(0.5)로 복귀
        self._auto_decay_attention()
        
        # 1. 현저성 계산
        for inp in inputs:
            inp.salience = self._calculate_salience(inp)
        
        # 2. 주의 가중치 적용
        weighted_inputs = self._apply_attention(inputs)
        
        # 3. 게이팅 (임계값 기준)
        outputs = self._gate(weighted_inputs)
        
        # 4. 우선순위 정렬
        outputs.sort(key=lambda x: x.priority)
        
        # 5. 채널 제한 (동시 처리 한계)
        outputs = outputs[:self.params['max_channels']]
        
        # 기록 (deque는 extend시 자동으로 maxlen 유지)
        self.recent_inputs.extend(inputs)
        
        return outputs
    
    def relay_single(self, content: Any, modality: ModalityType, 
                     intensity: float = 1.0) -> Optional[FilteredOutput]:
        """단일 입력 중계"""
        inp = SensoryInput(
            content=content,
            modality=modality,
            intensity=intensity
        )
        
        outputs = self.relay([inp])
        return outputs[0] if outputs else None
    
    def _calculate_salience(self, inp: SensoryInput) -> float:
        """
        현저성(Salience) 계산
        
        📐 수식:
            S = base_salience × boost × intensity × arousal
            
        ⚠️ [보완 3] 성능 노트:
            현재는 모든 키워드를 순회 (O(N×M), N=키워드수, M=텍스트길이)
            키워드가 100개 이상이면 Aho-Corasick 알고리즘 고려
            (Edge AI 환경에서는 키워드가 적으므로 현재 방식 유지)
        """
        base_salience = inp.salience
        
        # 텍스트인 경우 패턴 매칭
        if isinstance(inp.content, str):
            content_lower = inp.content.lower()
            
            for category, patterns in self.salient_patterns.items():
                for pattern in patterns:
                    if pattern in content_lower:
                        # 현저성 부스트
                        boost = self.params['salience_boost']
                        if category == 'threat':
                            boost *= 2  # 위협은 더 높은 우선순위
                        base_salience = min(1.0, base_salience * boost)
                        break
        
        # 강도 반영
        base_salience *= inp.intensity
        
        # 각성 수준 반영
        base_salience *= self.arousal_level
        
        return min(1.0, base_salience)
    
    def _apply_attention(self, inputs: List[SensoryInput]) -> List[Tuple[SensoryInput, float]]:
        """주의 가중치 적용"""
        weighted = []
        
        for inp in inputs:
            # 기본 가중치
            weight = self.attention_weights.get(inp.modality, 0.5)
            
            # 포커스된 양식이면 부스트
            if self.attention_focus == inp.modality:
                weight *= 1.5
            
            # 현저성 반영
            weight *= (1 + inp.salience)
            
            weighted.append((inp, min(1.0, weight)))
        
        return weighted
    
    def _gate(self, weighted_inputs: List[Tuple[SensoryInput, float]]) -> List[FilteredOutput]:
        """게이팅 (필터링)"""
        outputs = []
        threshold = self.params['gate_threshold']
        
        for inp, weight in weighted_inputs:
            passed = weight >= threshold
            
            if passed:
                self.stats['passed_gate'] += 1
            else:
                self.stats['blocked'] += 1
            
            outputs.append(FilteredOutput(
                content=inp.content,
                modality=inp.modality,
                attention_weight=weight,
                passed_gate=passed,
                priority=int((1 - weight) * 10)  # 가중치 높을수록 낮은 우선순위 번호
            ))
        
        # 통과한 것만 반환
        return [o for o in outputs if o.passed_gate]
    
    # ============================================
    # 2. 주의 조절 (Attention Control)
    # ============================================
    
    def set_attention_focus(self, modality: ModalityType):
        """주의 포커스 설정"""
        if self.attention_focus != modality:
            self.attention_focus = modality
            self.stats['attention_shifts'] += 1
    
    def shift_attention(self, target: str):
        """
        주의 전환 (텍스트 기반 자동 감지)
        
        Args:
            target: 주의 대상
        """
        target_lower = target.lower()
        
        # 키워드 기반 양식 감지
        if any(w in target_lower for w in ['보', '시각', '이미지', 'see', 'look', 'image']):
            self.set_attention_focus(ModalityType.VISUAL)
        elif any(w in target_lower for w in ['듣', '소리', '음악', 'hear', 'sound', 'music']):
            self.set_attention_focus(ModalityType.AUDITORY)
        elif any(w in target_lower for w in ['느낌', '감정', '기분', 'feel', 'emotion']):
            self.set_attention_focus(ModalityType.EMOTIONAL)
        elif any(w in target_lower for w in ['기억', '예전', '과거', 'remember', 'past']):
            self.set_attention_focus(ModalityType.EPISODIC)
        else:
            self.set_attention_focus(ModalityType.SEMANTIC)
    
    def boost_attention(self, modality: ModalityType, amount: float = 0.2):
        """특정 양식 주의 부스트"""
        current = self.attention_weights.get(modality, 0.5)
        self.attention_weights[modality] = min(1.0, current + amount)
    
    def decay_attention(self):
        """주의 자연 감쇠 (외부 호출용)"""
        decay = self.params['attention_decay']
        for modality in self.attention_weights:
            current = self.attention_weights[modality]
            # 0.5 (기본값)으로 서서히 복귀
            self.attention_weights[modality] = current + decay * (0.5 - current)
    
    def _auto_decay_attention(self):
        """
        [보완 1] 내부 호출용 주의 감쇠
        
        relay() 호출시 자동 실행되어 주의력이 서서히 균형 상태로 복귀
        
        📐 원리:
            - 틱당 감쇠율 = attention_decay × 0.1
            - 목표값(0.5)과의 차이 × 감쇠율만큼 복귀
            - 충분히 균형에 가까워지면(0.01 미만) 정확히 0.5로 설정
            - 포커스된 모달리티가 균형에 도달하면 포커스 해제
        """
        decay = self.params['attention_decay'] * 0.1  # 틱당 감쇠율 조절
        
        for modality in self.attention_weights:
            current = self.attention_weights[modality]
            
            # 0.5 (기본값)으로 서서히 복귀
            if abs(current - 0.5) > 0.01:
                self.attention_weights[modality] = current + decay * (0.5 - current)
            else:
                self.attention_weights[modality] = 0.5
                # 포커스 해제 (균형 상태에 도달한 경우)
                if modality == self.attention_focus:
                    self.attention_focus = None
    
    # ============================================
    # 3. 각성 조절 (Arousal Control)
    # ============================================
    
    def set_arousal(self, level: float):
        """각성 수준 설정"""
        self.arousal_level = max(0.0, min(1.0, level))
        
        # 낮은 각성 = 게이트 닫힘 (수면)
        if self.arousal_level < 0.2:
            self.consciousness_gate = False
        else:
            self.consciousness_gate = True
    
    def sleep_mode(self):
        """수면 모드 (감각 차단)"""
        self.arousal_level = 0.0
        self.consciousness_gate = False
        return "💤 시상: 감각 게이트 닫힘 (수면 모드)"
    
    def wake_up(self):
        """각성"""
        self.arousal_level = 1.0
        self.consciousness_gate = True
        return "☀️ 시상: 감각 게이트 열림 (각성)"
    
    def alert(self, reason: str = ""):
        """경계 상태 (주의 최대화)"""
        self.arousal_level = 1.0
        self.consciousness_gate = True
        # 모든 감각 주의 증가
        for modality in self.attention_weights:
            self.attention_weights[modality] = min(1.0, self.attention_weights[modality] + 0.3)
        
        return f"🚨 시상: 경계 모드! {reason}"
    
    # ============================================
    # 4. 상태 조회
    # ============================================
    
    def get_state(self) -> Dict[str, Any]:
        """전체 상태 반환"""
        return {
            'arousal_level': round(self.arousal_level, 2),
            'consciousness_gate': self.consciousness_gate,
            'attention_focus': self.attention_focus.value if self.attention_focus else None,
            'attention_weights': {k.value: round(v, 2) for k, v in self.attention_weights.items()},
            'recent_inputs': len(self.recent_inputs),
            'stats': self.stats,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.stats.copy()
    
    def is_awake(self) -> bool:
        """각성 상태 확인"""
        return self.consciousness_gate and self.arousal_level > 0.2


# ============================================
# 테스트
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Thalamus (시상) 테스트")
    print("=" * 60)
    
    thalamus = Thalamus()
    
    # 1. 감각 중계 테스트
    print("\n📡 [1] 감각 중계 테스트")
    print("-" * 40)
    
    inputs = [
        SensoryInput("오늘 날씨가 좋네요", ModalityType.SEMANTIC, intensity=0.5),
        SensoryInput("위험해! 조심해!", ModalityType.SEMANTIC, intensity=0.9),
        SensoryInput("배경 음악", ModalityType.AUDITORY, intensity=0.3),
    ]
    
    outputs = thalamus.relay(inputs)
    
    print(f"  입력: {len(inputs)}개")
    print(f"  통과: {len(outputs)}개")
    for out in outputs:
        print(f"    - '{out.content[:20]}...' (가중치: {out.attention_weight:.2f})")
    
    # 2. 주의 포커스 테스트
    print("\n🎯 [2] 주의 포커스 테스트")
    print("-" * 40)
    
    thalamus.shift_attention("그 소리 들어봐")
    print(f"  '그 소리 들어봐' → 포커스: {thalamus.attention_focus.value}")
    
    thalamus.shift_attention("기분이 어때?")
    print(f"  '기분이 어때?' → 포커스: {thalamus.attention_focus.value}")
    
    # 3. 현저성 테스트 (위협)
    print("\n⚠️ [3] 현저성 테스트 (위협 감지)")
    print("-" * 40)
    
    normal_input = SensoryInput("평범한 문장입니다", ModalityType.SEMANTIC)
    threat_input = SensoryInput("위험! 공격이다!", ModalityType.SEMANTIC)
    
    normal_out = thalamus.relay_single(normal_input.content, normal_input.modality)
    threat_out = thalamus.relay_single(threat_input.content, threat_input.modality)
    
    if normal_out:
        print(f"  평범: 가중치 {normal_out.attention_weight:.2f}")
    else:
        print(f"  평범: 게이트 차단")
    
    if threat_out:
        print(f"  위협: 가중치 {threat_out.attention_weight:.2f} (우선 통과!)")
    
    # 4. 수면 모드 테스트
    print("\n💤 [4] 수면 모드 테스트")
    print("-" * 40)
    
    print(thalamus.sleep_mode())
    outputs = thalamus.relay(inputs)
    print(f"  수면 중 입력 처리: {len(outputs)}개 (감각 차단)")
    
    print(thalamus.wake_up())
    outputs = thalamus.relay(inputs)
    print(f"  각성 후 입력 처리: {len(outputs)}개")
    
    # 5. 상태 확인
    print("\n📊 [5] 전체 상태")
    print("-" * 40)
    state = thalamus.get_state()
    print(f"  각성 수준: {state['arousal_level']}")
    print(f"  의식 게이트: {'열림' if state['consciousness_gate'] else '닫힘'}")
    print(f"  주의 포커스: {state['attention_focus']}")
    print(f"  통계: {state['stats']}")
    
    print("\n" + "=" * 60)
    print("✅ 시상 테스트 완료!")
    print("=" * 60)

