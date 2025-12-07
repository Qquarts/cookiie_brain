"""
Stimulus Accumulator: 자극 축적 시스템

🧠 개념:
    기억 = 단순 저장 ❌
    기억 = 자극의 축적 → 패턴 형성 → (성격 emergence)
    
    성격 자체를 구현하는 게 아니라,
    성격이 "형성될 수 있는" 구조를 만드는 것.
    
    실제 성격 형성은 관찰/실험 영역.

구조:
    1. Stimulus (자극): 개별 입력과 그 강도
    2. Accumulation (축적): 자극이 쌓이는 과정
    3. Pattern (패턴): 축적된 자극의 분포/경향
    4. Trace (흔적): 패턴이 남긴 잔상 (성격 형성의 재료)

사용:
    accumulator = StimulusAccumulator()
    accumulator.receive("고양이", intensity=0.8, valence=1.0)  # 긍정 자극
    accumulator.receive("고양이", intensity=0.5, valence=1.0)  # 반복
    patterns = accumulator.get_patterns()  # 축적된 패턴 관찰
    
Author: GNJz (Qquarts)
Version: 1.0
"""

import time
import json
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class Stimulus:
    """
    개별 자극
    
    Attributes:
        content: 자극 내용 (키워드, 주제, 개념 등)
        intensity: 자극 강도 (0.0 ~ 1.0)
        valence: 감정가 (-1.0=부정, 0=중립, +1.0=긍정)
        timestamp: 발생 시간
        context: 맥락
    """
    def __init__(self, 
                 content: str,
                 intensity: float = 0.5,
                 valence: float = 0.0,
                 context: str = None):
        self.content = content
        self.intensity = max(0.0, min(1.0, intensity))
        self.valence = max(-1.0, min(1.0, valence))
        self.context = context
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'intensity': self.intensity,
            'valence': self.valence,
            'context': self.context,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Stimulus':
        s = cls(
            content=data['content'],
            intensity=data.get('intensity', 0.5),
            valence=data.get('valence', 0.0),
            context=data.get('context')
        )
        s.timestamp = data.get('timestamp', time.time())
        return s


class AccumulatedTrace:
    """
    축적된 흔적 (특정 주제/개념에 대한 누적 자극)
    
    이것이 성격 형성의 "재료"가 됨.
    직접 성격을 정의하지 않고, 관찰 가능한 데이터를 제공.
    """
    def __init__(self, key: str):
        self.key = key  # 주제/개념/키워드
        
        # === 축적 데이터 ===
        self.total_intensity = 0.0      # 총 자극 강도
        self.total_valence = 0.0        # 총 감정가
        self.exposure_count = 0         # 노출 횟수
        self.first_exposure = None      # 첫 노출 시간
        self.last_exposure = None       # 마지막 노출 시간
        
        # === 분포 데이터 ===
        self.intensity_history = []     # 강도 이력 (최근 N개)
        self.valence_history = []       # 감정가 이력
        self.interval_history = []      # 노출 간격 이력
        
        # === 파생 지표 (관찰용) ===
        # 이것들이 "성격"으로 해석될 수 있는 데이터
        self.avg_intensity = 0.0        # 평균 강도
        self.avg_valence = 0.0          # 평균 감정가 (좋아함/싫어함)
        self.consistency = 0.0          # 일관성 (항상 비슷한 반응?)
        self.recency_weight = 0.0       # 최근성 가중치
        
        # 설정
        self.history_limit = 100        # 이력 보관 수
    
    def accumulate(self, stimulus: Stimulus):
        """자극 축적"""
        now = stimulus.timestamp
        
        # 첫 노출 기록
        if self.first_exposure is None:
            self.first_exposure = now
        
        # 간격 기록
        if self.last_exposure is not None:
            interval = now - self.last_exposure
            self.interval_history.append(interval)
            if len(self.interval_history) > self.history_limit:
                self.interval_history.pop(0)
        
        self.last_exposure = now
        
        # 축적
        self.total_intensity += stimulus.intensity
        self.total_valence += stimulus.valence * stimulus.intensity  # 강도 가중
        self.exposure_count += 1
        
        # 이력 추가
        self.intensity_history.append(stimulus.intensity)
        self.valence_history.append(stimulus.valence)
        
        if len(self.intensity_history) > self.history_limit:
            self.intensity_history.pop(0)
        if len(self.valence_history) > self.history_limit:
            self.valence_history.pop(0)
        
        # 파생 지표 업데이트
        self._update_derived_metrics()
    
    def _update_derived_metrics(self):
        """파생 지표 계산"""
        if self.exposure_count == 0:
            return
        
        # 평균 강도
        self.avg_intensity = self.total_intensity / self.exposure_count
        
        # 평균 감정가 (강도 가중 평균)
        if self.total_intensity > 0:
            self.avg_valence = self.total_valence / self.total_intensity
        
        # 일관성 (표준편차의 역수 기반)
        if len(self.valence_history) > 1:
            import statistics
            try:
                std = statistics.stdev(self.valence_history)
                self.consistency = 1.0 / (1.0 + std)  # 0~1, 높을수록 일관
            except:
                self.consistency = 1.0
        
        # 최근성 가중치 (최근 노출이 더 영향력 있음)
        if self.last_exposure and self.first_exposure:
            time_span = self.last_exposure - self.first_exposure
            if time_span > 0:
                # 최근 노출들의 비중
                recent_weight = sum(self.intensity_history[-10:]) / max(1, len(self.intensity_history[-10:]))
                old_weight = sum(self.intensity_history[:10]) / max(1, len(self.intensity_history[:10])) if len(self.intensity_history) > 10 else recent_weight
                if old_weight > 0:
                    self.recency_weight = recent_weight / old_weight
                else:
                    self.recency_weight = 1.0
    
    def get_observation_data(self) -> Dict:
        """
        관찰용 데이터 반환
        
        이 데이터를 가지고 "성격"을 관찰/실험/조정할 수 있음
        """
        return {
            'key': self.key,
            
            # 기본 축적 데이터
            'exposure_count': self.exposure_count,
            'total_intensity': self.total_intensity,
            'total_valence': self.total_valence,
            'first_exposure': self.first_exposure,
            'last_exposure': self.last_exposure,
            
            # 파생 지표 (성격 형성 재료)
            'avg_intensity': self.avg_intensity,
            'avg_valence': self.avg_valence,        # -1~+1: 싫어함~좋아함
            'consistency': self.consistency,         # 0~1: 반응 일관성
            'recency_weight': self.recency_weight,   # 최근 관심도 변화
            
            # 해석 힌트 (실험자가 참고)
            'interpretation_hints': {
                'interest_level': self.avg_intensity,  # 관심도
                'preference': self.avg_valence,        # 선호도
                'stability': self.consistency,         # 안정성
                'trend': 'increasing' if self.recency_weight > 1.2 else 
                        'decreasing' if self.recency_weight < 0.8 else 'stable'
            }
        }
    
    def to_dict(self) -> Dict:
        return {
            'key': self.key,
            'total_intensity': self.total_intensity,
            'total_valence': self.total_valence,
            'exposure_count': self.exposure_count,
            'first_exposure': self.first_exposure,
            'last_exposure': self.last_exposure,
            'intensity_history': self.intensity_history,
            'valence_history': self.valence_history,
            'interval_history': self.interval_history,
            'avg_intensity': self.avg_intensity,
            'avg_valence': self.avg_valence,
            'consistency': self.consistency,
            'recency_weight': self.recency_weight,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AccumulatedTrace':
        trace = cls(data['key'])
        trace.total_intensity = data.get('total_intensity', 0.0)
        trace.total_valence = data.get('total_valence', 0.0)
        trace.exposure_count = data.get('exposure_count', 0)
        trace.first_exposure = data.get('first_exposure')
        trace.last_exposure = data.get('last_exposure')
        trace.intensity_history = data.get('intensity_history', [])
        trace.valence_history = data.get('valence_history', [])
        trace.interval_history = data.get('interval_history', [])
        trace.avg_intensity = data.get('avg_intensity', 0.0)
        trace.avg_valence = data.get('avg_valence', 0.0)
        trace.consistency = data.get('consistency', 0.0)
        trace.recency_weight = data.get('recency_weight', 0.0)
        return trace


class StimulusAccumulator:
    """
    자극 축적기
    
    기억이 쌓이는 과정 = 성격이 형성되는 과정
    의 "구조"를 제공함.
    
    성격 자체는 구현하지 않음 (관찰/실험 영역)
    성격이 형성될 수 있는 인프라를 제공.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.created_at = time.time()
        
        # === Storage ===
        # 모든 자극 로그 (시간순)
        self._stimulus_log: List[Stimulus] = []
        
        # 축적된 흔적 (key -> AccumulatedTrace)
        self._traces: Dict[str, AccumulatedTrace] = {}
        
        # 맥락별 인덱스
        self._context_index: Dict[str, List[int]] = defaultdict(list)
        
        # 설정
        self.log_limit = 10000  # 자극 로그 최대 크기
    
    # =========================================================
    # 📥 INPUT: 자극 수신
    # =========================================================
    
    def receive(self,
                content: str,
                intensity: float = 0.5,
                valence: float = 0.0,
                context: str = None) -> Stimulus:
        """
        자극 수신 및 축적
        
        Args:
            content: 자극 내용 (키워드, 주제 등)
            intensity: 강도 (0.0~1.0)
            valence: 감정가 (-1.0=부정, +1.0=긍정)
            context: 맥락
        
        Returns:
            생성된 Stimulus 객체
        
        예시:
            # 고양이를 보고 기분 좋음
            acc.receive("고양이", intensity=0.7, valence=0.8)
            
            # 개한테 물림 (강한 부정 자극)
            acc.receive("개", intensity=0.95, valence=-0.9)
        """
        stimulus = Stimulus(content, intensity, valence, context)
        
        # 로그에 추가
        log_idx = len(self._stimulus_log)
        self._stimulus_log.append(stimulus)
        
        # 용량 관리
        if len(self._stimulus_log) > self.log_limit:
            self._stimulus_log.pop(0)
        
        # 맥락 인덱스
        if context:
            self._context_index[context].append(log_idx)
        
        # 흔적에 축적
        if content not in self._traces:
            self._traces[content] = AccumulatedTrace(content)
        
        self._traces[content].accumulate(stimulus)
        
        return stimulus
    
    def receive_batch(self, stimuli: List[Dict]):
        """
        여러 자극 일괄 수신
        
        Args:
            stimuli: [{'content': ..., 'intensity': ..., 'valence': ...}, ...]
        """
        for s in stimuli:
            self.receive(
                content=s.get('content', ''),
                intensity=s.get('intensity', 0.5),
                valence=s.get('valence', 0.0),
                context=s.get('context')
            )
    
    # =========================================================
    # 📊 OBSERVE: 패턴 관찰 (실험자용)
    # =========================================================
    
    def get_trace(self, key: str) -> Optional[Dict]:
        """
        특정 주제의 축적 흔적 조회
        
        Returns:
            관찰용 데이터 (성격 형성 재료)
        """
        if key not in self._traces:
            return None
        return self._traces[key].get_observation_data()
    
    def get_all_traces(self) -> Dict[str, Dict]:
        """모든 흔적 조회"""
        return {
            key: trace.get_observation_data()
            for key, trace in self._traces.items()
        }
    
    def get_patterns(self, 
                     min_exposure: int = 2,
                     sort_by: str = 'total_intensity') -> List[Dict]:
        """
        형성된 패턴들 조회
        
        Args:
            min_exposure: 최소 노출 횟수 필터
            sort_by: 정렬 기준 
                    ('total_intensity', 'avg_valence', 'exposure_count', 'consistency')
        
        Returns:
            패턴 리스트 (정렬됨)
        
        이 데이터로 "성격이 어떻게 형성되고 있는지" 관찰
        """
        patterns = []
        
        for trace in self._traces.values():
            if trace.exposure_count >= min_exposure:
                data = trace.get_observation_data()
                patterns.append(data)
        
        # 정렬
        if sort_by in ['total_intensity', 'avg_valence', 'exposure_count', 'consistency']:
            patterns.sort(key=lambda x: abs(x.get(sort_by, 0)), reverse=True)
        
        return patterns
    
    def get_top_interests(self, n: int = 10) -> List[Dict]:
        """
        가장 관심 있는 주제들 (높은 intensity)
        
        → "이 AI가 무엇에 관심 있는지" 관찰
        """
        return self.get_patterns(min_exposure=1, sort_by='total_intensity')[:n]
    
    def get_preferences(self, n: int = 10) -> Tuple[List[Dict], List[Dict]]:
        """
        선호/비선호 주제들 (valence 기준)
        
        Returns:
            (좋아하는 것들, 싫어하는 것들)
        
        → "이 AI가 무엇을 좋아하고 싫어하는지" 관찰
        """
        patterns = self.get_patterns(min_exposure=2)
        
        likes = sorted([p for p in patterns if p['avg_valence'] > 0.2],
                      key=lambda x: x['avg_valence'], reverse=True)[:n]
        
        dislikes = sorted([p for p in patterns if p['avg_valence'] < -0.2],
                         key=lambda x: x['avg_valence'])[:n]
        
        return likes, dislikes
    
    def get_stable_traits(self, consistency_threshold: float = 0.7) -> List[Dict]:
        """
        안정적인 특성들 (높은 consistency)
        
        → "굳어진 성격적 특성" 관찰
        """
        patterns = self.get_patterns(min_exposure=5)
        return [p for p in patterns if p['consistency'] >= consistency_threshold]
    
    # =========================================================
    # 🔧 ADJUST: 실험/조정용 함수
    # =========================================================
    
    def adjust_trace(self, 
                     key: str, 
                     intensity_delta: float = 0.0,
                     valence_delta: float = 0.0):
        """
        흔적 수동 조정 (실험용)
        
        Args:
            key: 조정할 주제
            intensity_delta: 강도 변화량
            valence_delta: 감정가 변화량
        
        실험자가 특정 조건을 만들어 관찰할 때 사용
        """
        if key not in self._traces:
            return
        
        trace = self._traces[key]
        trace.total_intensity += intensity_delta
        trace.total_valence += valence_delta * abs(intensity_delta) if intensity_delta else valence_delta
        trace._update_derived_metrics()
    
    def inject_experience(self,
                          key: str,
                          intensity: float,
                          valence: float,
                          count: int = 1):
        """
        경험 주입 (실험용)
        
        특정 경험을 여러 번 반복한 것처럼 주입
        성격 형성 과정을 가속하거나 특정 조건 만들기
        """
        for _ in range(count):
            self.receive(key, intensity=intensity, valence=valence)
    
    def reset_trace(self, key: str):
        """특정 흔적 초기화 (실험용)"""
        if key in self._traces:
            del self._traces[key]
    
    def decay_all(self, rate: float = 0.01):
        """
        전체 흔적 감쇠 (시간 경과 시뮬레이션)
        
        오래된 자극의 영향력이 줄어드는 것을 시뮬레이션
        하지만 완전히 사라지지는 않음 (인간처럼)
        """
        for trace in self._traces.values():
            # intensity 감쇠 (최소값 유지)
            decay_amount = trace.total_intensity * rate
            trace.total_intensity = max(
                trace.total_intensity * 0.1,  # 최소 10% 유지
                trace.total_intensity - decay_amount
            )
            
            # valence는 감쇠하지 않음 (좋아함/싫어함은 잘 안 변함)
            
            trace._update_derived_metrics()
    
    # =========================================================
    # 💾 PERSISTENCE: 저장/로드
    # =========================================================
    
    def save(self, path: str = None) -> str:
        """저장"""
        if path is None:
            save_dir = Path.home() / ".babyhippo" / "accumulator"
            save_dir.mkdir(parents=True, exist_ok=True)
            path = str(save_dir / f"{self.name}.json")
        
        data = {
            'version': self.VERSION,
            'name': self.name,
            'created_at': self.created_at,
            'saved_at': time.time(),
            
            'stimulus_log': [s.to_dict() for s in self._stimulus_log],
            'traces': {k: v.to_dict() for k, v in self._traces.items()},
            'context_index': dict(self._context_index),
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return path
    
    def load(self, path: str = None):
        """로드"""
        if path is None:
            path = str(Path.home() / ".babyhippo" / "accumulator" / f"{self.name}.json")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.name = data.get('name', self.name)
        self.created_at = data.get('created_at', time.time())
        
        self._stimulus_log = [Stimulus.from_dict(s) for s in data.get('stimulus_log', [])]
        self._traces = {k: AccumulatedTrace.from_dict(v) for k, v in data.get('traces', {}).items()}
        self._context_index = defaultdict(list, data.get('context_index', {}))
    
    # =========================================================
    # 📈 STATS
    # =========================================================
    
    def get_stats(self) -> Dict:
        """통계"""
        patterns = self.get_patterns(min_exposure=1)
        
        return {
            'version': self.VERSION,
            'name': self.name,
            'total_stimuli': len(self._stimulus_log),
            'unique_topics': len(self._traces),
            'contexts': list(self._context_index.keys()),
            
            # 전체 경향 (성격 형성 방향)
            'overall_tendency': {
                'avg_interest': sum(p['avg_intensity'] for p in patterns) / max(1, len(patterns)),
                'avg_sentiment': sum(p['avg_valence'] for p in patterns) / max(1, len(patterns)),
                'most_exposed': patterns[0]['key'] if patterns else None,
            }
        }
    
    def __repr__(self):
        return f"StimulusAccumulator('{self.name}', {len(self._traces)} traces)"
    
    def __len__(self):
        return len(self._stimulus_log)


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Stimulus Accumulator Test")
    print("   (성격 형성 기반 구조)")
    print("=" * 60)
    
    acc = StimulusAccumulator("test_personality")
    
    # === 자극 수신 시뮬레이션 ===
    print("\n📥 Receiving stimuli...")
    
    # 고양이에 대한 반복적 긍정 경험
    for i in range(5):
        acc.receive("고양이", intensity=0.7 + i*0.05, valence=0.8)
    
    # 개에 대한 강한 부정 경험 (한번 물림)
    acc.receive("개", intensity=0.95, valence=-0.9)
    # 이후 조심스러운 부정 경험들
    for _ in range(3):
        acc.receive("개", intensity=0.3, valence=-0.3)
    
    # 프로그래밍에 대한 중립적이지만 꾸준한 노출
    for _ in range(10):
        acc.receive("프로그래밍", intensity=0.6, valence=0.2)
    
    # 음악에 대한 가끔 긍정 경험
    acc.receive("음악", intensity=0.8, valence=0.9)
    acc.receive("음악", intensity=0.5, valence=0.7)
    
    # === 패턴 관찰 ===
    print("\n📊 Observing patterns (성격 형성 재료):")
    print("-" * 50)
    
    patterns = acc.get_patterns()
    for p in patterns:
        hints = p['interpretation_hints']
        print(f"\n  [{p['key']}]")
        print(f"    노출 횟수: {p['exposure_count']}")
        print(f"    관심도: {hints['interest_level']:.2f}")
        print(f"    선호도: {hints['preference']:.2f} ({'좋아함' if hints['preference'] > 0.3 else '싫어함' if hints['preference'] < -0.3 else '중립'})")
        print(f"    안정성: {hints['stability']:.2f}")
        print(f"    추세: {hints['trend']}")
    
    # === 선호/비선호 ===
    print("\n" + "-" * 50)
    print("❤️  좋아하는 것들:")
    likes, dislikes = acc.get_preferences()
    for p in likes:
        print(f"    • {p['key']} (선호도: {p['avg_valence']:.2f})")
    
    print("\n💔 싫어하는 것들:")
    for p in dislikes:
        print(f"    • {p['key']} (선호도: {p['avg_valence']:.2f})")
    
    # === 통계 ===
    print("\n" + "-" * 50)
    print("📈 Stats:")
    stats = acc.get_stats()
    for k, v in stats.items():
        print(f"    {k}: {v}")
    
    print("\n" + "=" * 60)
    print("✅ 이 데이터를 가지고 '성격 형성'을 관찰/실험/조정 가능")
    print("✅ 성격 자체는 구현하지 않음 - emergence를 관찰하는 것")
    print("=" * 60)

