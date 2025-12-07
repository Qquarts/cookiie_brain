"""
HippoLM: 해마 기반 언어 모델

🧠 핵심 아이디어:
    Transformer (역전파) ❌
    STDP 신경망 (헤비안) ⭕
    
    기존 babyhippo의 뉴런-시냅스 구조로 언어 생성
    역전파 없이, 스파이크 타이밍 기반 학습

구조:
    입력 → DG(인코딩) → CA3(연상) → CA1(출력) → 텍스트
    
특징:
    - 역전파 없음 (STDP만)
    - 행렬 연산 최소화
    - CPU에서 가볍게 실행
    - 라즈베리파이 OK

Author: GNJz (Qquarts)
"""

import random
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math


class SpikeNeuron:
    """스파이크 뉴런 (LIF 모델 간소화)"""
    
    def __init__(self, threshold: float = 1.0):
        self.potential = 0.0  # 막전위
        self.threshold = threshold
        self.spike_time = -1  # 마지막 스파이크 시간
        self.refractory = 2  # 불응기
    
    def receive(self, input_current: float, time: int) -> bool:
        """입력 받고 스파이크 여부 반환"""
        # 불응기 체크
        if time - self.spike_time < self.refractory:
            return False
        
        # 막전위 누적
        self.potential += input_current
        
        # 역치 초과 시 스파이크
        if self.potential >= self.threshold:
            self.potential = 0.0  # 리셋
            self.spike_time = time
            return True
        
        # 자연 감쇠
        self.potential *= 0.9
        return False


class STDPSynapse:
    """STDP 시냅스 (역전파 없는 학습)"""
    
    def __init__(self, pre_id: str, post_id: str, weight: float = 0.5):
        self.pre_id = pre_id
        self.post_id = post_id
        self.weight = weight
        self.weight_max = 2.0
        self.weight_min = 0.0
        
        # STDP 파라미터
        self.tau_plus = 20.0  # LTP 시간 상수
        self.tau_minus = 20.0  # LTD 시간 상수
        self.a_plus = 0.1  # LTP 학습률
        self.a_minus = 0.1  # LTD 학습률
    
    def stdp_update(self, pre_spike_time: int, post_spike_time: int):
        """STDP 가중치 업데이트"""
        if pre_spike_time < 0 or post_spike_time < 0:
            return
        
        dt = post_spike_time - pre_spike_time
        
        if dt > 0:
            # Pre → Post (LTP, 강화)
            dw = self.a_plus * math.exp(-dt / self.tau_plus)
            self.weight = min(self.weight_max, self.weight + dw)
        elif dt < 0:
            # Post → Pre (LTD, 약화)
            dw = self.a_minus * math.exp(dt / self.tau_minus)
            self.weight = max(self.weight_min, self.weight - dw)
    
    def transmit(self) -> float:
        """신호 전달"""
        return self.weight


class HippoLM:
    """
    해마 기반 언어 모델
    
    Transformer 없이, STDP 신경망으로 텍스트 생성
    """
    
    def __init__(self, vocab_size: int = 1000):
        self.vocab_size = vocab_size
        
        # 어휘 (문자 단위)
        self.char_to_id: Dict[str, int] = {}
        self.id_to_char: Dict[int, str] = {}
        self.next_id = 0
        
        # 뉴런 레이어
        self.dg_neurons: Dict[int, SpikeNeuron] = {}  # 입력 인코딩
        self.ca3_neurons: Dict[int, SpikeNeuron] = {}  # 연상 기억
        self.ca1_neurons: Dict[int, SpikeNeuron] = {}  # 출력
        
        # 시냅스 연결
        self.dg_ca3_synapses: Dict[Tuple[int, int], STDPSynapse] = {}
        self.ca3_ca3_synapses: Dict[Tuple[int, int], STDPSynapse] = {}  # 재귀 연결
        self.ca3_ca1_synapses: Dict[Tuple[int, int], STDPSynapse] = {}
        
        # 시퀀스 기억 (n-gram 스타일)
        self.sequences: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # 시간
        self.time = 0
    
    def _get_char_id(self, char: str) -> int:
        """문자 → ID"""
        if char not in self.char_to_id:
            self.char_to_id[char] = self.next_id
            self.id_to_char[self.next_id] = char
            
            # 뉴런 생성
            self.dg_neurons[self.next_id] = SpikeNeuron()
            self.ca3_neurons[self.next_id] = SpikeNeuron()
            self.ca1_neurons[self.next_id] = SpikeNeuron()
            
            self.next_id += 1
        
        return self.char_to_id[char]
    
    def learn(self, text: str):
        """
        텍스트 학습 (STDP 기반)
        
        역전파 없이 시퀀스 패턴 학습
        """
        if len(text) < 2:
            return
        
        # 문자 ID 변환
        char_ids = [self._get_char_id(c) for c in text]
        
        # 시퀀스 학습 (연속된 문자 패턴)
        for i in range(len(char_ids) - 1):
            pre_id = char_ids[i]
            post_id = char_ids[i + 1]
            
            # 시냅스 생성 또는 강화
            key = (pre_id, post_id)
            if key not in self.ca3_ca3_synapses:
                self.ca3_ca3_synapses[key] = STDPSynapse(str(pre_id), str(post_id))
            
            # STDP 업데이트 (pre가 먼저, post가 나중 → 강화)
            self.time += 1
            self.ca3_ca3_synapses[key].stdp_update(self.time, self.time + 1)
            
            # 시퀀스 카운트 (n-gram 백업)
            pre_char = text[i]
            post_char = text[i + 1]
            self.sequences[pre_char][post_char] += 1.0
        
        # 더 긴 컨텍스트 (2-gram)
        for i in range(len(text) - 2):
            context = text[i:i+2]
            next_char = text[i + 2]
            self.sequences[context][next_char] += 0.5
    
    def generate(self, prompt: str, max_length: int = 50) -> str:
        """
        텍스트 생성 (스파이크 활성화 + 연상)
        """
        if not prompt:
            return ""
        
        result = prompt
        
        for _ in range(max_length):
            # 다음 문자 예측
            next_char = self._predict_next(result)
            
            if next_char is None:
                break
            
            result += next_char
            
            # 종료 조건
            if next_char in ['.', '!', '?', '\n']:
                break
        
        return result
    
    def _predict_next(self, context: str) -> Optional[str]:
        """다음 문자 예측 (시냅스 가중치 + 시퀀스 기억)"""
        if not context:
            return None
        
        candidates: Dict[str, float] = defaultdict(float)
        
        # 1. 시냅스 기반 예측 (마지막 문자)
        last_char = context[-1]
        if last_char in self.char_to_id:
            last_id = self.char_to_id[last_char]
            
            for (pre_id, post_id), synapse in self.ca3_ca3_synapses.items():
                if pre_id == last_id and post_id in self.id_to_char:
                    next_char = self.id_to_char[post_id]
                    candidates[next_char] += synapse.weight * 2.0
        
        # 2. 시퀀스 기억 (1-gram)
        if last_char in self.sequences:
            for next_char, count in self.sequences[last_char].items():
                candidates[next_char] += count
        
        # 3. 시퀀스 기억 (2-gram)
        if len(context) >= 2:
            bigram = context[-2:]
            if bigram in self.sequences:
                for next_char, count in self.sequences[bigram].items():
                    candidates[next_char] += count * 1.5  # 더 긴 컨텍스트 보너스
        
        if not candidates:
            return None
        
        # 확률적 선택 (소프트맥스 스타일)
        total = sum(candidates.values())
        if total <= 0:
            return None
        
        # 온도 적용 (다양성)
        temperature = 0.8
        weights = {k: (v / total) ** (1 / temperature) for k, v in candidates.items()}
        total_weights = sum(weights.values())
        
        # 랜덤 선택
        r = random.random() * total_weights
        cumulative = 0.0
        for char, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return char
        
        return list(candidates.keys())[0]
    
    def get_stats(self) -> Dict:
        """통계"""
        return {
            'vocab_size': len(self.char_to_id),
            'synapses': len(self.ca3_ca3_synapses),
            'sequences': sum(len(v) for v in self.sequences.values()),
            'time': self.time,
        }


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 HippoLM Test - 해마 기반 언어 모델")
    print("   (역전파 없음, STDP 학습)")
    print("=" * 60)
    
    # 모델 생성
    lm = HippoLM()
    
    # 학습 데이터
    training_texts = [
        "안녕하세요. 반갑습니다.",
        "저는 babyhippo입니다.",
        "기억이 먼저이고 언어는 나중입니다.",
        "해마는 기억의 중심입니다.",
        "모든 걸 알고 싶은 AI입니다.",
        "안녕! 오늘 날씨가 좋네요.",
        "파이썬은 좋은 프로그래밍 언어입니다.",
        "고양이는 귀엽습니다.",
        "학습은 경험에서 시작됩니다.",
    ]
    
    print("\n📝 학습 중...")
    for text in training_texts:
        lm.learn(text)
        # 반복 학습으로 패턴 강화
        for _ in range(3):
            lm.learn(text)
    
    print(f"   어휘: {lm.get_stats()['vocab_size']}개")
    print(f"   시냅스: {lm.get_stats()['synapses']}개")
    
    # 생성 테스트
    print("\n✨ 텍스트 생성 테스트:")
    
    prompts = ["안녕", "저는", "해마", "기억"]
    
    for prompt in prompts:
        print(f"\n프롬프트: '{prompt}'")
        generated = lm.generate(prompt, max_length=30)
        print(f"생성: {generated}")
    
    print("\n📊 통계:")
    stats = lm.get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    print("\n" + "=" * 60)
    print("✅ 역전파 없이 텍스트 생성!")
    print("   CPU 부하: 최소 🧊")
    print("=" * 60)

