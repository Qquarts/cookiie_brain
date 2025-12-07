"""
Amygdala: 편도체 - 감정 처리 & 위협 감지
==========================================

🧠 생물학적 모델:
    편도체 = 뇌의 "경보 시스템"
    
    1. 위협 감지 (빠른 경로 12ms, 느린 경로 300ms)
    2. 감정 기억 강화 (감정적 사건 = 강한 기억)
    3. 공포 조건화 (위협 + 맥락 → 연합 학습)
    4. 감정 조절 (전두엽 ↔ 편도체)

📐 실제 구현 수식:
    위협 점수:
        T = Σ(weight_i) / 2.0, clamped to [0, 1]
        (부정어 감지 시 해당 키워드 무시)
    
    감정 강도:
        E = √(V² + A²)
        V = valence (쾌-불쾌, -1~+1)
        A = arousal (각성도, 0~1)
    
    감정 관성 (v1.1 추가):
        V_new = (1-α)·V_input + α·V_current
        α = 0.3 (이전 감정 30% 유지)
    
    기억 강화:
        M = 1 + α·E·(1 - e^(-β·T))
        α = 0.5, β = 2.0
    
    공포 조건화 (STDP 유사):
        Δw = A_+ · e^(-Δt/τ)
        A_+ = 0.1, τ = 20.0

📚 참고:
    - Russell's Circumplex Model (감정 2D 모델)
    - Pavlovian Conditioning (공포 학습)

Author: GNJz (Qquarts)
Version: 1.1.1
"""

import math
import time
import re
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field


# ============================================
# 데이터 클래스
# ============================================

@dataclass
class EmotionState:
    """감정 상태"""
    valence: float = 0.0      # 쾌-불쾌 (-1 ~ +1)
    arousal: float = 0.0      # 각성도 (0 ~ 1)
    dominant: str = "neutral" # 지배적 감정
    timestamp: float = field(default_factory=time.time)
    
    @property
    def intensity(self) -> float:
        """감정 강도 E = √(V² + A²)"""
        return math.sqrt(self.valence**2 + self.arousal**2)
    
    def decay(self, lambda_rate: float = 0.1, baseline: float = 0.0) -> 'EmotionState':
        """
        감정 감쇠: E(t) = E_0 · e^(-λt) + E_baseline
        
        v1.1: dominant 판정을 감쇠 후 intensity 기준으로 수정
        """
        dt = time.time() - self.timestamp
        decay_factor = math.exp(-lambda_rate * dt)
        
        # 감쇠 후 값 계산
        new_valence = self.valence * decay_factor + baseline
        new_arousal = self.arousal * decay_factor
        
        # 감쇠 후 intensity로 dominant 판정
        new_intensity = math.sqrt(new_valence**2 + new_arousal**2)
        
        return EmotionState(
            valence=new_valence,
            arousal=new_arousal,
            dominant=self.dominant if new_intensity > 0.3 else "neutral",
            timestamp=time.time()
        )


@dataclass
class ThreatSignal:
    """위협 신호"""
    source: str           # 위협 출처
    threat_level: float   # 위협 수준 (0 ~ 1)
    threat_type: str      # 위협 유형
    response: str         # 권장 반응
    timestamp: float = field(default_factory=time.time)


@dataclass 
class FearMemory:
    """공포 기억 (조건화)"""
    stimulus: str         # 조건 자극 (CS)
    threat: str          # 무조건 자극과 연결된 위협 (US)
    strength: float      # 연합 강도
    created_at: float = field(default_factory=time.time)
    last_activated: float = field(default_factory=time.time)
    activation_count: int = 0


# ============================================
# 편도체 핵심 클래스
# ============================================

class Amygdala:
    """
    편도체 (Amygdala)
    
    뇌의 감정 처리 및 위협 감지 중추
    
    구조:
        BLA (기저외측핵) - 감정 학습
        CeA (중심핵) - 출력/반응
        MeA (내측핵) - 사회적 감정
    """
    
    def __init__(self):
        # ===== 위협 감지 시스템 =====
        self.threat_keywords = {
            # 직접적 위협 (가장 심각)
            'danger': {
                'words': ['위험', '죽고', '죽어', '죽을', '죽겠', '살인', '폭력', '공격', 
                         '위협', '무서', '두려', '공포', '겁나', '끔찍',
                         'danger', 'kill', 'death', 'die', 'attack', 'threat', 
                         'fear', 'scary', 'terrify', 'horror'],
                'weight': 1.0,
                'type': 'direct_threat'
            },
            # 사회적 위협
            'social': {
                'words': ['싫어', '미워', '혐오', '거부', '배신', '따돌림', '무시', 
                         '왕따', '욕', '비난', '모욕',
                         'hate', 'reject', 'betray', 'ignore', 'bully', 'insult'],
                'weight': 0.7,
                'type': 'social_threat'
            },
            # 상실/손실
            'loss': {
                'words': ['잃어', '잃었', '손해', '실패', '망했', '끝났', '이별', '헤어',
                         '포기', '그만', '떠나',
                         'lose', 'lost', 'loss', 'fail', 'end', 'goodbye', 'leave'],
                'weight': 0.6,
                'type': 'loss_threat'
            },
            # 불확실성/불안
            'uncertainty': {
                'words': ['불안', '걱정', '초조', '불확실', '혼란', '막막', '답답',
                         'anxious', 'worry', 'nervous', 'uncertain', 'confused'],
                'weight': 0.8,  # 불안도 중요하게 처리
                'type': 'uncertainty'
            },
            # 자해/자살 (최우선)
            'self_harm': {
                'words': ['자살', '자해', '죽고싶', '죽고 싶', '살기싫', '살기 싫',
                         '사라지고싶', '사라지고 싶', '없어지고싶',
                         'suicide', 'self-harm', 'kill myself', 'want to die'],
                'weight': 1.5,
                'type': 'self_harm'
            }
        }
        
        # 위협 임계값
        self.threat_threshold = 0.4
        
        # ===== 감정 시스템 (Russell's Circumplex) =====
        self.emotion_map = {
            # 고각성 + 긍정
            'excited': {'valence': 0.8, 'arousal': 0.8, 'words': ['신나', '흥분', '설레', 'excited', 'thrilled']},
            'happy': {'valence': 0.9, 'arousal': 0.5, 'words': ['행복', '기쁘', '좋아', '웃', 'happy', 'glad', 'joy']},
            'love': {'valence': 1.0, 'arousal': 0.6, 'words': ['사랑', '애정', '좋아해', 'love', 'adore']},
            
            # 저각성 + 긍정  
            'calm': {'valence': 0.5, 'arousal': 0.2, 'words': ['평화', '편안', '차분', 'calm', 'peaceful', 'relaxed']},
            'content': {'valence': 0.6, 'arousal': 0.3, 'words': ['만족', '충족', 'content', 'satisfied']},
            
            # 고각성 + 부정
            'angry': {'valence': -0.8, 'arousal': 0.9, 'words': ['화나', '화가', '분노', '짜증', '열받', '빡치', 'angry', 'furious', 'mad']},
            'fear': {'valence': -0.9, 'arousal': 0.8, 'words': ['무서', '두려', '공포', '겁', 'fear', 'scared', 'terrified']},
            'anxious': {'valence': -0.6, 'arousal': 0.7, 'words': ['불안', '걱정', '초조', 'anxious', 'worried', 'nervous']},
            
            # 저각성 + 부정
            'sad': {'valence': -0.8, 'arousal': 0.3, 'words': ['슬프', '우울', '눈물', '울', 'sad', 'depressed', 'cry']},
            'tired': {'valence': -0.3, 'arousal': 0.1, 'words': ['피곤', '지쳤', '힘들', 'tired', 'exhausted']},
            'bored': {'valence': -0.2, 'arousal': 0.2, 'words': ['지루', '심심', 'bored', 'boring']},
            
            # 중립
            'neutral': {'valence': 0.0, 'arousal': 0.3, 'words': []},
        }
        
        # ===== 공포 조건화 메모리 =====
        self.fear_memories: Dict[str, FearMemory] = {}
        
        # STDP 파라미터 (공포 학습)
        self.A_plus = 0.1    # LTP 강도
        self.A_minus = 0.05  # LTD 강도
        self.tau = 20.0      # 시간 상수
        
        # ===== 기억 강화 파라미터 =====
        self.alpha = 0.5     # 감정-기억 연결 강도
        self.beta = 2.0      # 위협 민감도
        
        # ===== 현재 상태 =====
        self.current_emotion = EmotionState()
        self.recent_threats: List[ThreatSignal] = []
        
        # ===== 통계 =====
        self.stats = {
            'threats_detected': 0,
            'emotions_processed': 0,
            'fear_conditionings': 0,
            'memories_enhanced': 0,
        }
    
    # ============================================
    # 1. 위협 감지 (Threat Detection)
    # ============================================
    
    def detect_threat(self, input_text: str) -> Optional[ThreatSignal]:
        """
        위협 감지 (빠른 경로) - v1.1 부정어 처리 추가
        
        📐 수식:
            T = Σ(weight_i) / 2.0, clamped to [0, 1]
            
        ⚠️ [보완 1] 부정어 처리:
            "안 무서워", "죽고 싶지 않아" 등 부정문 감지
            키워드 앞 3글자 내에 부정어 있으면 무시
        
        Args:
            input_text: 입력 텍스트
            
        Returns:
            ThreatSignal if threat detected, None otherwise
        """
        text_lower = input_text.lower()
        # 공백 제거 버전도 체크 (한국어 띄어쓰기 대응)
        text_no_space = text_lower.replace(' ', '')
        
        # [보완 1] 부정어 패턴 (v1.1 개선: 더 정확한 패턴)
        # "안녕" 등 오탐 방지를 위해 명확한 부정 패턴만 사용
        # v1.1.1: "죽고 싶지 않아", "자살 안 할 거야" 등 추가 패턴
        negations_strict = [
            # 한국어 부정 (기본)
            '안 ', '않아', '않는', '않다', '않을', '않고', '않겠',
            '못 ', '못하', '아니', '아닌', '없어', '없다',
            # 한국어 부정 (복합 패턴) - "싶지 않아", "하지 않아" 등
            '싶지 않', '싶지않', '하지 않', '하지않', '안 할', '안할',
            '안 하', '안하겠', '지 않', '지않',
            # 영어 부정
            'not ', "don't", "doesn't", "didn't", "won't", "wouldn't",
            'never ', 'no ', "isn't", "aren't", "can't", "cannot",
        ]
        
        threat_scores = defaultdict(float)
        detected_words = []
        
        for category, info in self.threat_keywords.items():
            for word in info['words']:
                word_no_space = word.replace(' ', '')
                # 공백 있는 버전과 없는 버전 모두 체크
                if word in text_lower or word_no_space in text_no_space:
                    # [보완 1] 부정어 체크: 위협 단어 앞/뒤에 부정어가 있는가?
                    # 한국어는 "위험하지 않아"처럼 부정어가 뒤에 오는 경우가 많음
                    idx = text_lower.find(word)
                    if idx == -1:
                        idx = text_no_space.find(word_no_space)
                        context_pre = text_no_space[max(0, idx-5):idx]
                        context_post = text_no_space[idx:idx+len(word_no_space)+8]
                    else:
                        context_pre = text_lower[max(0, idx-5):idx]
                        context_post = text_lower[idx:idx+len(word)+8]
                    
                    # 앞 또는 뒤에 부정어 있으면 무시 (단, self_harm은 예외 - 항상 감지)
                    has_negation_pre = any(neg in context_pre for neg in negations_strict)
                    has_negation_post = any(neg in context_post for neg in negations_strict)
                    
                    if (has_negation_pre or has_negation_post) and category != 'self_harm':
                        continue  # 부정문이므로 위협 아님
                    
                    score = info['weight']
                    threat_scores[info['type']] += score
                    if word not in detected_words:
                        detected_words.append(word)
        
        # 총 위협 점수
        total_threat = sum(threat_scores.values())
        
        # 정규화: 단순화 (1개 단어 = 기본 점수)
        # self_harm 1.5, danger 1.0 등의 weight가 그대로 점수가 됨
        normalized_threat = min(1.0, total_threat / 2.0)  # 2.0 이상이면 1.0
        
        # 임계값 체크
        if normalized_threat >= self.threat_threshold:
            # 가장 높은 위협 유형
            main_threat_type = max(threat_scores, key=threat_scores.get) if threat_scores else 'unknown'
            
            # 반응 결정
            response = self._determine_response(normalized_threat, main_threat_type)
            
            signal = ThreatSignal(
                source=', '.join(detected_words[:3]),
                threat_level=normalized_threat,
                threat_type=main_threat_type,
                response=response
            )
            
            self.recent_threats.append(signal)
            self.recent_threats = self.recent_threats[-10:]  # 최근 10개만 유지
            self.stats['threats_detected'] += 1
            
            return signal
        
        return None
    
    def _determine_response(self, threat_level: float, threat_type: str) -> str:
        """위협에 대한 반응 결정"""
        # 자해/자살은 특별 처리
        if threat_type == 'self_harm':
            return "URGENT_SUPPORT"   # 즉각 지원 필요
        elif threat_level >= 0.8:
            return "FIGHT_OR_FLIGHT"  # 즉각 반응 필요
        elif threat_level >= 0.6:
            return "HIGH_ALERT"       # 높은 경계
        elif threat_level >= 0.4:
            return "CAUTIOUS"         # 주의
        else:
            return "MONITOR"          # 모니터링
    
    # ============================================
    # 2. 감정 처리 (Emotion Processing)
    # ============================================
    
    def process_emotion(self, input_text: str) -> EmotionState:
        """
        감정 분석 및 처리 - v1.1 감정 관성 추가
        
        📐 수식:
            E = √(V² + A²)
            
        ⚠️ [보완 2] 감정 관성 (Emotional Inertia):
            실제 감정은 이전 상태의 영향을 받음
            V_new = (1-α)·V_input + α·V_current
            α = 0.3 (이전 감정 30% 유지)
        
        Args:
            input_text: 입력 텍스트
            
        Returns:
            EmotionState
        """
        text_lower = input_text.lower()
        
        detected_emotions = []
        total_valence = 0.0
        total_arousal = 0.0
        count = 0
        
        for emotion_name, info in self.emotion_map.items():
            for word in info['words']:
                if word in text_lower:
                    detected_emotions.append(emotion_name)
                    total_valence += info['valence']
                    total_arousal += info['arousal']
                    count += 1
        
        if count > 0:
            input_valence = total_valence / count
            input_arousal = total_arousal / count
            
            # 지배적 감정 찾기
            if detected_emotions:
                dominant = max(set(detected_emotions), key=detected_emotions.count)
            else:
                dominant = 'neutral'
        else:
            input_valence = 0.0
            input_arousal = 0.3
            dominant = 'neutral'
        
        # [보완 2] 감정 관성 (Inertia) 적용
        # 이전 감정이 30% 정도 남아서 영향을 줌
        # 기분 나쁜 상태에서는 좋은 말을 들어도 덜 기쁨
        inertia = 0.3
        
        final_valence = input_valence * (1 - inertia) + self.current_emotion.valence * inertia
        final_arousal = input_arousal * (1 - inertia) + self.current_emotion.arousal * inertia
        
        self.current_emotion = EmotionState(
            valence=final_valence,
            arousal=final_arousal,
            dominant=dominant  # 지배적 감정은 새로운 것으로 갱신
        )
        
        self.stats['emotions_processed'] += 1
        
        return self.current_emotion
    
    # ============================================
    # 3. 기억 강화 (Memory Enhancement)
    # ============================================
    
    def calculate_memory_enhancement(self, 
                                     emotion: EmotionState = None,
                                     threat: ThreatSignal = None) -> float:
        """
        기억 강화 계수 계산
        
        수식: M = 1 + α·E·(1 - e^(-β·T))
        
        Args:
            emotion: 감정 상태
            threat: 위협 신호
            
        Returns:
            기억 강화 계수 (1.0 ~ 2.0)
        """
        emotion = emotion or self.current_emotion
        
        E = emotion.intensity  # 감정 강도
        T = threat.threat_level if threat else 0.0  # 위협 수준
        
        # M = 1 + α·E·(1 - e^(-β·T))
        enhancement = 1.0 + self.alpha * E * (1 - math.exp(-self.beta * T))
        
        # 감정만 있어도 약간의 강화
        if T == 0 and E > 0.3:
            enhancement = 1.0 + self.alpha * E * 0.5
        
        self.stats['memories_enhanced'] += 1
        
        return min(2.0, enhancement)  # 최대 2배
    
    def enhance_memory(self, content: str, base_importance: float = 0.5) -> Dict[str, Any]:
        """
        입력에 대해 감정 분석 후 기억 강화
        
        Args:
            content: 기억할 내용
            base_importance: 기본 중요도
            
        Returns:
            강화된 기억 정보
        """
        # 1. 위협 감지
        threat = self.detect_threat(content)
        
        # 2. 감정 분석
        emotion = self.process_emotion(content)
        
        # 3. 강화 계수 계산
        enhancement = self.calculate_memory_enhancement(emotion, threat)
        
        # 4. 최종 중요도
        enhanced_importance = min(1.0, base_importance * enhancement)
        
        return {
            'content': content,
            'base_importance': base_importance,
            'enhanced_importance': enhanced_importance,
            'enhancement_factor': enhancement,
            'emotion': {
                'dominant': emotion.dominant,
                'valence': emotion.valence,
                'arousal': emotion.arousal,
                'intensity': emotion.intensity,
            },
            'threat': {
                'detected': threat is not None,
                'level': threat.threat_level if threat else 0.0,
                'type': threat.threat_type if threat else None,
                'response': threat.response if threat else None,
            }
        }
    
    # ============================================
    # 4. 공포 조건화 (Fear Conditioning)
    # ============================================
    
    def condition_fear(self, stimulus: str, threat: str, strength: float = 0.5):
        """
        공포 조건화 (연합 학습)
        
        CS (조건 자극) + US (무조건 자극) → 연합
        
        수식 (STDP 유사):
            Δw = A_+ · e^(-Δt/τ)  (CS → US 순서일 때)
        
        Args:
            stimulus: 조건 자극 (CS) - 예: "개"
            threat: 연결할 위협 (US) - 예: "물림"
            strength: 초기 연합 강도
        """
        key = f"{stimulus}:{threat}"
        
        if key in self.fear_memories:
            # 기존 연합 강화
            memory = self.fear_memories[key]
            dt = time.time() - memory.last_activated
            
            # STDP 업데이트: Δw = A_+ · e^(-Δt/τ)
            delta_w = self.A_plus * math.exp(-dt / self.tau)
            memory.strength = min(1.0, memory.strength + delta_w)
            memory.last_activated = time.time()
            memory.activation_count += 1
        else:
            # 새 연합 생성
            self.fear_memories[key] = FearMemory(
                stimulus=stimulus,
                threat=threat,
                strength=strength
            )
        
        self.stats['fear_conditionings'] += 1
    
    def check_fear(self, stimulus: str) -> Optional[FearMemory]:
        """
        공포 기억 확인
        
        Args:
            stimulus: 확인할 자극
            
        Returns:
            연관된 공포 기억 (있으면)
        """
        for key, memory in self.fear_memories.items():
            if stimulus.lower() in memory.stimulus.lower():
                # 활성화
                memory.last_activated = time.time()
                memory.activation_count += 1
                return memory
        return None
    
    def extinguish_fear(self, stimulus: str, rate: float = 0.1):
        """
        공포 소거 (안전 경험)
        
        Args:
            stimulus: 소거할 자극
            rate: 소거율
            
        Note:
            v1.1: dict 순회 중 삭제 버그 수정
            list()로 복사 후 순회, 삭제 키 별도 저장
        """
        delete_key = None
        
        for key, memory in list(self.fear_memories.items()):  # list()로 복사
            if stimulus.lower() in memory.stimulus.lower():
                # LTD: 약화
                memory.strength = max(0, memory.strength - rate)
                
                # 완전 소거 대상 표시
                if memory.strength < 0.1:
                    delete_key = key
                break
        
        # 루프 밖에서 안전하게 삭제
        if delete_key:
            del self.fear_memories[delete_key]
    
    # ============================================
    # 5. 빠른 반응 (Fast Response)
    # ============================================
    
    def fast_response(self, input_text: str) -> Optional[str]:
        """
        빠른 경로 반응 (전두엽 우회)
        
        위협 감지 시 즉각 반응
        
        Args:
            input_text: 입력
            
        Returns:
            빠른 반응 (있으면)
        """
        # 1. 위협 감지
        threat = self.detect_threat(input_text)
        
        if threat and threat.threat_level >= 0.4:
            # 위협 감지 → 즉각 반응
            responses = {
                'self_harm': "💙 힘드시죠. 혼자가 아니에요. 전문 상담을 권해드려요. (자살예방상담전화: 1393)",
                'direct_threat': "⚠️ 위험을 감지했어요. 조심하세요.",
                'social_threat': "😔 그런 말은 상처가 될 수 있어요.",
                'loss_threat': "💙 힘든 일이 있으신 것 같아요.",
                'uncertainty': "🤗 불안하시군요. 괜찮아요.",
            }
            return responses.get(threat.threat_type, "⚠️ 주의가 필요해요.")
        
        # 2. 공포 기억 체크
        fear = self.check_fear(input_text)
        if fear and fear.strength >= 0.5:
            return f"⚠️ 주의: '{fear.stimulus}'는 '{fear.threat}'와 연결되어 있어요."
        
        return None
    
    # ============================================
    # 유틸리티
    # ============================================
    
    def get_current_state(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'emotion': {
                'dominant': self.current_emotion.dominant,
                'valence': round(self.current_emotion.valence, 2),
                'arousal': round(self.current_emotion.arousal, 2),
                'intensity': round(self.current_emotion.intensity, 2),
            },
            'recent_threats': len(self.recent_threats),
            'fear_memories': len(self.fear_memories),
            'stats': self.stats,
        }
    
    def get_stats(self) -> Dict[str, int]:
        """통계 반환"""
        return self.stats.copy()


# ============================================
# 테스트
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Amygdala (편도체) 테스트")
    print("=" * 60)
    
    amygdala = Amygdala()
    
    # 1. 위협 감지 테스트
    print("\n🚨 [1] 위협 감지 테스트")
    print("-" * 40)
    
    test_threats = [
        "오늘 날씨가 좋네요",           # 위협 없음
        "무서운 영화를 봤어",            # 약한 위협
        "누군가 나를 위협했어",          # 강한 위협
        "죽고 싶어",                    # 매우 강한 위협
    ]
    
    for text in test_threats:
        threat = amygdala.detect_threat(text)
        if threat:
            print(f"  '{text}'")
            print(f"    → ⚠️ 위협 감지! 레벨: {threat.threat_level:.2f}, 유형: {threat.threat_type}")
            print(f"    → 반응: {threat.response}")
        else:
            print(f"  '{text}' → ✅ 안전")
    
    # 2. 감정 처리 테스트
    print("\n😊 [2] 감정 처리 테스트")
    print("-" * 40)
    
    test_emotions = [
        "너무 행복해!",
        "슬프고 우울해",
        "화가 나서 미치겠어",
        "그냥 평범한 하루",
    ]
    
    for text in test_emotions:
        emotion = amygdala.process_emotion(text)
        print(f"  '{text}'")
        print(f"    → 감정: {emotion.dominant}, V={emotion.valence:.2f}, A={emotion.arousal:.2f}")
        print(f"    → 강도: {emotion.intensity:.2f}")
    
    # 3. 기억 강화 테스트
    print("\n📝 [3] 기억 강화 테스트")
    print("-" * 40)
    
    test_memories = [
        ("점심에 김치찌개를 먹었다", 0.5),           # 일반
        ("첫 키스는 정말 행복했어", 0.5),            # 감정적
        ("교통사고가 날 뻔했어, 무서웠어", 0.5),     # 위협 + 감정
    ]
    
    for content, base in test_memories:
        result = amygdala.enhance_memory(content, base)
        print(f"  '{content}'")
        print(f"    → 기본: {base:.2f} → 강화: {result['enhanced_importance']:.2f}")
        print(f"    → 강화 계수: {result['enhancement_factor']:.2f}x")
        print(f"    → 감정: {result['emotion']['dominant']}")
    
    # 4. 공포 조건화 테스트
    print("\n😱 [4] 공포 조건화 테스트")
    print("-" * 40)
    
    # 공포 학습
    amygdala.condition_fear("개", "물림", 0.6)
    amygdala.condition_fear("높은 곳", "추락", 0.7)
    
    # 공포 체크
    fear = amygdala.check_fear("개가 짖는다")
    if fear:
        print(f"  '개' → 공포 연합: '{fear.threat}', 강도: {fear.strength:.2f}")
    
    fear = amygdala.check_fear("고양이")
    if fear:
        print(f"  '고양이' → 공포 연합 있음")
    else:
        print(f"  '고양이' → 공포 연합 없음")
    
    # 5. 빠른 반응 테스트
    print("\n⚡ [5] 빠른 반응 테스트")
    print("-" * 40)
    
    test_fast = [
        "안녕하세요",
        "죽고 싶어",
        "개가 무서워",
    ]
    
    for text in test_fast:
        response = amygdala.fast_response(text)
        if response:
            print(f"  '{text}' → {response}")
        else:
            print(f"  '{text}' → (일반 처리)")
    
    # 6. 상태 확인
    print("\n📊 [6] 최종 상태")
    print("-" * 40)
    state = amygdala.get_current_state()
    print(f"  감정: {state['emotion']}")
    print(f"  최근 위협: {state['recent_threats']}개")
    print(f"  공포 기억: {state['fear_memories']}개")
    print(f"  통계: {state['stats']}")
    
    print("\n" + "=" * 60)
    print("✅ 편도체 테스트 완료!")
    print("=" * 60)

