"""
Cerebellum: 소뇌 모듈 (반사 신경 + 미세 조정)

🧠 생물학적 소뇌의 역할:
    - 운동 학습 및 조정
    - 타이밍 및 리듬
    - 반사 신경 (자동화된 반응)
    - 오차 교정

💡 HippoLM 시스템에서의 역할:
    - 자주 쓰는 패턴 즉시 반환 (반사)
    - 문장 미세 조정 (오차 교정)
    - 타이밍 제어
    - CA3 계산 우회 → 속도 향상

구조:
    입력 → [소뇌 체크] → 반사 패턴 있으면 즉시 반환
                      → 없으면 HippoLM으로 전달
    
    HippoLM 출력 → [소뇌 교정] → 미세 조정된 출력

v1.1 변경사항:
- DNA 연동 (reflex_pack) 지원
- 성격별 말투 커스터마이징 가능

Author: GNJz (Qquarts)
Version: 1.1
"""

import time
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import re


class ReflexPattern:
    """반사 패턴 (자동화된 응답)"""
    
    def __init__(self, trigger: str, response: str, 
                 use_count: int = 0, success_rate: float = 1.0):
        self.trigger = trigger.lower()
        self.response = response
        self.use_count = use_count
        self.success_rate = success_rate  # 성공률 (피드백 기반)
        self.last_used = 0
        
        # 소뇌 학습: 사용할수록 강화
        self.strength = 1.0
    
    def use(self):
        """사용 시 강화"""
        self.use_count += 1
        self.last_used = time.time()
        # 사용할수록 반사 강도 증가 (최대 2.0)
        self.strength = min(2.0, self.strength + 0.1)
    
    def decay(self, rate: float = 0.01):
        """미사용 시 약화"""
        self.strength = max(0.1, self.strength - rate)
    
    def feedback(self, positive: bool):
        """피드백으로 학습"""
        if positive:
            self.success_rate = min(1.0, self.success_rate + 0.05)
            self.strength = min(2.0, self.strength + 0.2)
        else:
            self.success_rate = max(0.0, self.success_rate - 0.1)
            self.strength = max(0.1, self.strength - 0.3)


class ErrorCorrector:
    """오차 교정기 (미세 조정)"""
    
    # 자주 발생하는 오류 패턴
    CORRECTIONS = {
        # 반복 제거
        r'(.)\1{3,}': r'\1\1',  # aaaa → aa
        r'(\w+)\s+\1': r'\1',   # 단어 단어 → 단어
        
        # 공백 정리
        r'\s{2,}': ' ',         # 다중 공백 → 단일
        r'\s+([.,!?])': r'\1',  # 공백 + 구두점 → 구두점
        
        # 문장 시작 대문자 (영어)
        r'^([a-z])': lambda m: m.group(1).upper(),
    }
    
    # 한국어 종결 패턴
    KO_ENDINGS = ['요', '다', '까', '죠', '네', '야', '어', '아']
    
    @classmethod
    def correct(cls, text: str) -> str:
        """텍스트 교정"""
        if not text:
            return text
        
        result = text
        
        # 정규식 교정
        for pattern, replacement in cls.CORRECTIONS.items():
            if callable(replacement):
                result = re.sub(pattern, replacement, result)
            else:
                result = re.sub(pattern, replacement, result)
        
        # 앞뒤 공백 정리
        result = result.strip()
        
        return result
    
    @classmethod
    def smooth(cls, text: str) -> str:
        """문장 부드럽게"""
        if not text:
            return text
        
        # 불완전한 문장 완성
        if len(text) > 0 and text[-1] not in '.!?。':
            # 한국어면 종결어미 확인
            if any(text.endswith(e) for e in cls.KO_ENDINGS):
                text += '.'
        
        return text


class TimingController:
    """타이밍 제어기"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.target_time = 0.1  # 목표 응답 시간 (100ms)
    
    def record(self, response_time: float):
        """응답 시간 기록"""
        self.response_times.append(response_time)
        # 최근 100개만 유지
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
    
    def should_use_reflex(self) -> bool:
        """반사 사용 여부 (느리면 반사 우선)"""
        if not self.response_times:
            return True
        avg_time = sum(self.response_times) / len(self.response_times)
        return avg_time > self.target_time
    
    def get_stats(self) -> Dict:
        if not self.response_times:
            return {'avg': 0, 'min': 0, 'max': 0}
        return {
            'avg': sum(self.response_times) / len(self.response_times),
            'min': min(self.response_times),
            'max': max(self.response_times),
        }


class Cerebellum:
    """
    소뇌 모듈
    
    기능:
    1. 반사 패턴 (자주 쓰는 응답 즉시 반환)
    2. 오차 교정 (출력 미세 조정)
    3. 타이밍 제어 (응답 속도 최적화)
    """
    
    # 기본 반사 패턴 (인사, 감사 등)
    DEFAULT_REFLEXES = [
        ("안녕", "안녕하세요! 😊"),
        ("하이", "안녕하세요!"),
        ("hi", "Hello! 👋"),
        ("hello", "Hello! Nice to meet you!"),
        ("고마워", "천만에요! 😊"),
        ("감사", "천만에요!"),
        ("thanks", "You're welcome!"),
        ("뭐해", "대화하고 있어요!"),
        ("잘자", "좋은 밤 되세요! 🌙"),
        ("좋은 아침", "좋은 아침이에요! ☀️"),
        ("굿모닝", "Good morning! ☀️"),
        ("ㅎㅇ", "안녕! 👋"),
        ("ㄱㅅ", "천만에요!"),
        ("ㅂㅂ", "안녕히 가세요! 👋"),
    ]
    
    def __init__(self, reflex_threshold: float = 0.8, 
                 reflex_pack: Optional[List[Tuple[str, str]]] = None):
        """
        소뇌 초기화
        
        Args:
            reflex_threshold: 반사 발동 임계값 (강도가 이 이상이면 반사)
            reflex_pack: 성격별 초기 반사 패턴 (DNA/Config에서 주입)
                         예: [("안녕", "하이요! 🦛"), ("고마워", "별말씀을~")]
        
        Note:
            v1.1: DNA 연동 지원 (Stem Code 철학)
            - reflex_pack 없으면 → DEFAULT_REFLEXES 사용
            - reflex_pack 있으면 → 성격별 맞춤 반사
        """
        self.reflex_threshold = reflex_threshold
        
        # 반사 패턴 저장소
        self.reflexes: Dict[str, ReflexPattern] = {}
        
        # [v1.1] DNA에 따른 초기 패턴 로드
        initial_reflexes = reflex_pack if reflex_pack else self.DEFAULT_REFLEXES
        
        for trigger, response in initial_reflexes:
            self.add_reflex(trigger, response)
        
        # 오차 교정기
        self.corrector = ErrorCorrector()
        
        # 타이밍 제어기
        self.timing = TimingController()
        
        # 통계
        self.stats = {
            'reflex_hits': 0,
            'reflex_misses': 0,
            'corrections': 0,
        }
    
    def add_reflex(self, trigger: str, response: str):
        """반사 패턴 추가"""
        key = trigger.lower().strip()
        self.reflexes[key] = ReflexPattern(trigger, response)
    
    def check_reflex(self, input_text: str) -> Optional[str]:
        """
        반사 체크 (즉시 응답 가능하면 반환)
        
        Args:
            input_text: 입력 텍스트
            
        Returns:
            반사 응답 또는 None
        """
        key = input_text.lower().strip()
        
        # 정확히 일치
        if key in self.reflexes:
            reflex = self.reflexes[key]
            if reflex.strength >= self.reflex_threshold:
                reflex.use()
                self.stats['reflex_hits'] += 1
                return reflex.response
        
        # 부분 일치 (시작 부분)
        for trigger, reflex in self.reflexes.items():
            if key.startswith(trigger) or trigger.startswith(key):
                if reflex.strength >= self.reflex_threshold:
                    reflex.use()
                    self.stats['reflex_hits'] += 1
                    return reflex.response
        
        self.stats['reflex_misses'] += 1
        return None
    
    def correct_output(self, text: str) -> str:
        """
        출력 미세 조정 (오차 교정)
        
        Args:
            text: HippoLM 출력
            
        Returns:
            교정된 텍스트
        """
        if not text:
            return text
        
        # 1. 기본 교정
        corrected = self.corrector.correct(text)
        
        # 2. 부드럽게
        smoothed = self.corrector.smooth(corrected)
        
        if corrected != text or smoothed != corrected:
            self.stats['corrections'] += 1
        
        return smoothed
    
    def learn_reflex(self, trigger: str, response: str, 
                     auto_threshold: int = 3):
        """
        반복 패턴 자동 학습 (자주 나오면 반사로 등록)
        
        Args:
            trigger: 입력 패턴
            response: 응답
            auto_threshold: 이 횟수 이상 반복되면 자동 등록
        """
        key = trigger.lower().strip()
        
        if key in self.reflexes:
            # 이미 있으면 강화
            self.reflexes[key].use()
            # 응답이 다르면 업데이트 고려
            if self.reflexes[key].response != response:
                # 새 응답이 더 좋으면 업데이트
                self.reflexes[key].response = response
        else:
            # 새로 등록
            self.reflexes[key] = ReflexPattern(trigger, response)
    
    def process(self, input_text: str, 
                hippo_response: Optional[str] = None) -> Tuple[str, str]:
        """
        전체 처리 파이프라인
        
        Args:
            input_text: 입력
            hippo_response: HippoLM 응답 (없으면 반사만 체크)
            
        Returns:
            (최종 응답, 소스: 'reflex' 또는 'hippo')
        """
        start_time = time.time()
        
        # 1. 반사 체크 (빠른 응답)
        reflex_response = self.check_reflex(input_text)
        if reflex_response:
            self.timing.record(time.time() - start_time)
            return reflex_response, 'reflex'
        
        # 2. HippoLM 응답 교정
        if hippo_response:
            corrected = self.correct_output(hippo_response)
            
            # 3. 새로운 패턴 학습 (자주 나오면 반사로)
            self.learn_reflex(input_text, corrected)
            
            self.timing.record(time.time() - start_time)
            return corrected, 'hippo'
        
        # 4. 둘 다 없으면 기본 응답
        self.timing.record(time.time() - start_time)
        return "잘 모르겠어요.", 'default'
    
    def decay_all(self, rate: float = 0.01):
        """모든 반사 패턴 약화 (미사용 시)"""
        for reflex in self.reflexes.values():
            reflex.decay(rate)
    
    def get_stats(self) -> Dict:
        """통계"""
        total = self.stats['reflex_hits'] + self.stats['reflex_misses']
        hit_rate = (self.stats['reflex_hits'] / total * 100) if total > 0 else 0
        
        return {
            'reflex_patterns': len(self.reflexes),
            'reflex_hits': self.stats['reflex_hits'],
            'reflex_misses': self.stats['reflex_misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'corrections': self.stats['corrections'],
            'timing': self.timing.get_stats(),
        }
    
    def get_top_reflexes(self, n: int = 10) -> List[Dict]:
        """가장 많이 사용된 반사 패턴"""
        sorted_reflexes = sorted(
            self.reflexes.values(),
            key=lambda r: r.use_count,
            reverse=True
        )
        return [
            {
                'trigger': r.trigger,
                'response': r.response[:30],
                'uses': r.use_count,
                'strength': f"{r.strength:.2f}"
            }
            for r in sorted_reflexes[:n]
        ]


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Cerebellum Test - 소뇌 모듈")
    print("   (반사 신경 + 미세 조정)")
    print("=" * 60)
    
    # 소뇌 생성
    cb = Cerebellum()
    
    # 반사 테스트
    print("\n⚡ 반사 테스트:")
    test_inputs = ["안녕", "하이", "고마워", "뭐해", "날씨 어때"]
    
    for inp in test_inputs:
        response, source = cb.process(inp)
        print(f"  '{inp}' → '{response}' [{source}]")
    
    # 오차 교정 테스트
    print("\n🔧 오차 교정 테스트:")
    test_texts = [
        "안녕하세요요요요",
        "저는  babyhippo  입니다",
        "hello world",
        "기억이 먼저 이고",
    ]
    
    for text in test_texts:
        corrected = cb.correct_output(text)
        if corrected != text:
            print(f"  '{text}' → '{corrected}'")
        else:
            print(f"  '{text}' (변경 없음)")
    
    # 학습 테스트
    print("\n📚 반사 학습 테스트:")
    for _ in range(5):
        cb.learn_reflex("오늘 뭐해", "대화하고 있어요!")
    
    response, source = cb.process("오늘 뭐해")
    print(f"  '오늘 뭐해' → '{response}' [{source}]")
    
    # 통계
    print("\n📊 통계:")
    stats = cb.get_stats()
    for k, v in stats.items():
        if k != 'timing':
            print(f"  {k}: {v}")
    
    print("\n🏆 Top 반사 패턴:")
    for r in cb.get_top_reflexes(5):
        print(f"  '{r['trigger']}' → '{r['response']}' (사용: {r['uses']})")
    
    print("\n" + "=" * 60)
    print("✅ 소뇌 모듈 완성!")
    print("   - 반사 응답: 즉시! ⚡")
    print("   - 오차 교정: 자동! 🔧")
    print("=" * 60)

