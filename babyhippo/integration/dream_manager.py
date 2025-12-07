"""
Dream Manager: 꿈의 관리자
===========================

🌙 수면 중 일어나는 모든 작업을 총괄

역할:
    1. 해마 기억 → 패턴 분석
    2. 기억 공고화 (STDP 강화)
    3. 약한 기억 가지치기
    4. LLM 학습 데이터 생성
    5. 성장 지표 계산

흐름 (밤샘 Batch Job):
    [Sleep Start]
         │
         ├── Stage 1: Light Sleep
         │   └── 최근 기억 정리
         │
         ├── Stage 2: Deep Sleep (SWS)
         │   └── 해마 → 피질 전이 (공고화)
         │
         ├── Stage 3: REM Sleep
         │   └── 패턴 분석 & 창의적 연결
         │
         └── Stage 4: Wake Prep
             └── LLM 학습 데이터 생성
    [Sleep End]

Author: GNJz (Qquarts)
Version: 1.0
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SleepStage(Enum):
    """수면 단계"""
    AWAKE = "awake"
    LIGHT = "light"         # N1/N2 - 얕은 수면
    DEEP = "deep"           # N3/SWS - 깊은 수면 (공고화)
    REM = "rem"             # REM - 꿈 (창의적 연결)
    WAKE_PREP = "wake_prep" # 기상 준비


@dataclass
class DreamReport:
    """꿈 보고서"""
    stage: SleepStage
    duration: float
    memories_processed: int
    patterns_found: int
    consolidations: int
    pruned: int
    insights: List[str] = field(default_factory=list)


@dataclass
class SleepReport:
    """수면 전체 보고서"""
    total_duration: float
    cycles: int
    stages: Dict[str, float] = field(default_factory=dict)
    memories_processed: int = 0
    patterns_found: int = 0
    consolidations: int = 0
    pruned: int = 0
    training_data_generated: int = 0
    growth_score: float = 0.0
    insights: List[str] = field(default_factory=list)


class DreamManager:
    """
    🌙 꿈의 관리자
    
    수면 중 기억 처리 파이프라인 총괄
    """
    
    def __init__(self, brain=None):
        """
        Args:
            brain: BabyBrain 인스턴스
        """
        self.brain = brain
        
        # 수면 설정
        self.config = {
            'cycle_duration': 90,       # 1 사이클 = 90분 (실제로는 틱)
            'light_ratio': 0.5,         # 얕은 수면 50%
            'deep_ratio': 0.25,         # 깊은 수면 25%
            'rem_ratio': 0.25,          # REM 25%
            'consolidation_threshold': 0.6,
            'pruning_threshold': 0.2,
            'noise_level': {
                SleepStage.LIGHT: 0.1,
                SleepStage.DEEP: 0.05,  # SWS = 노이즈 최소 (안정적 전이)
                SleepStage.REM: 0.3,    # REM = 노이즈 최대 (창의성)
            }
        }
        
        # 현재 상태
        self.current_stage = SleepStage.AWAKE
        self.is_sleeping = False
        
        # 수면 기록
        self.sleep_history: List[SleepReport] = []
        
        # 학습 데이터 버퍼
        self.training_buffer: List[Dict] = []
        
        # 통계
        self.stats = {
            'total_sleep_sessions': 0,
            'total_memories_processed': 0,
            'total_patterns_found': 0,
            'total_consolidations': 0,
        }
    
    def connect_brain(self, brain):
        """뇌 연결"""
        self.brain = brain
    
    # =========================================================================
    # 🌙 수면 사이클
    # =========================================================================
    
    def sleep(self, hours: float = 8) -> SleepReport:
        """
        수면 시작 (전체 사이클)
        
        Args:
            hours: 수면 시간
            
        Returns:
            SleepReport
        """
        if self.is_sleeping:
            return SleepReport(total_duration=0, cycles=0)
        
        self.is_sleeping = True
        self.stats['total_sleep_sessions'] += 1
        
        start_time = time.time()
        cycles = int(hours * 60 / self.config['cycle_duration'])
        cycles = max(1, cycles)
        
        print(f"🌙 수면 시작 ({hours}시간, {cycles}사이클)")
        
        # 보고서 초기화
        report = SleepReport(
            total_duration=0,
            cycles=cycles,
            stages={stage.value: 0 for stage in SleepStage}
        )
        
        # 사이클 반복
        for cycle_num in range(cycles):
            print(f"\n  💤 사이클 {cycle_num + 1}/{cycles}")
            
            # Stage 1: Light Sleep
            light_report = self._process_light_sleep()
            report.stages['light'] += light_report.duration
            report.memories_processed += light_report.memories_processed
            
            # Stage 2: Deep Sleep (SWS)
            deep_report = self._process_deep_sleep()
            report.stages['deep'] += deep_report.duration
            report.consolidations += deep_report.consolidations
            report.pruned += deep_report.pruned
            
            # Stage 3: REM Sleep
            rem_report = self._process_rem_sleep()
            report.stages['rem'] += rem_report.duration
            report.patterns_found += rem_report.patterns_found
            report.insights.extend(rem_report.insights)
        
        # Stage 4: Wake Prep (마지막)
        wake_report = self._process_wake_prep()
        report.stages['wake_prep'] = wake_report.duration
        report.training_data_generated = wake_report.memories_processed
        
        # 성장 점수 계산
        report.growth_score = self._calculate_growth(report)
        
        # 완료
        report.total_duration = time.time() - start_time
        
        self.is_sleeping = False
        self.current_stage = SleepStage.AWAKE
        self.sleep_history.append(report)
        
        # 통계 업데이트
        self.stats['total_memories_processed'] += report.memories_processed
        self.stats['total_patterns_found'] += report.patterns_found
        self.stats['total_consolidations'] += report.consolidations
        
        print(f"\n☀️ 기상! 성장 점수: {report.growth_score:.2f}")
        
        return report
    
    def _process_light_sleep(self) -> DreamReport:
        """
        얕은 수면 (N1/N2)
        - 최근 기억 정리
        - 중요도 재평가
        """
        self.current_stage = SleepStage.LIGHT
        start_time = time.time()
        
        memories_processed = 0
        
        if self.brain:
            try:
                # 최근 기억 가져오기
                hippo = self.brain.curious.brain.hippo
                recent_words = list(hippo.words.keys())[-20:]  # 최근 20개
                
                for word_id in recent_words:
                    # 빈도 기반 중요도 재평가
                    freq = hippo.word_frequencies.get(word_id, 1)
                    if freq > 3:
                        memories_processed += 1
                
            except Exception as e:
                print(f"    ⚠️ Light sleep 오류: {e}")
        
        return DreamReport(
            stage=SleepStage.LIGHT,
            duration=time.time() - start_time,
            memories_processed=memories_processed,
            patterns_found=0,
            consolidations=0,
            pruned=0
        )
    
    def _process_deep_sleep(self) -> DreamReport:
        """
        깊은 수면 (N3/SWS)
        - 해마 → 피질 전이 (공고화)
        - 시냅스 강화
        - 약한 기억 가지치기
        """
        self.current_stage = SleepStage.DEEP
        start_time = time.time()
        
        consolidations = 0
        pruned = 0
        
        if self.brain:
            try:
                hippo = self.brain.curious.brain.hippo
                
                # 1. 공고화: 중요한 시냅스 강화
                for word_id, word_info in hippo.words.items():
                    synapses = word_info.get('synapses_dg_ca3', [])
                    
                    for syn in synapses:
                        # 시냅스 강화 (STDP 기반)
                        if hasattr(syn, 'consolidate'):
                            if syn.weight > self.config['consolidation_threshold']:
                                syn.consolidate()
                                consolidations += 1
                
                # 2. 가지치기: 약한 시냅스 정리
                for syn in hippo.dg_to_ca3_synapses:
                    if hasattr(syn, 'weight') and syn.weight < self.config['pruning_threshold']:
                        # 약화 (완전 삭제는 하지 않음)
                        syn.weight *= 0.5
                        pruned += 1
                
            except Exception as e:
                print(f"    ⚠️ Deep sleep 오류: {e}")
        
        return DreamReport(
            stage=SleepStage.DEEP,
            duration=time.time() - start_time,
            memories_processed=0,
            patterns_found=0,
            consolidations=consolidations,
            pruned=pruned
        )
    
    def _process_rem_sleep(self) -> DreamReport:
        """
        REM 수면
        - 패턴 분석
        - 창의적 연결 (노이즈 기반)
        - 통찰 생성
        """
        self.current_stage = SleepStage.REM
        start_time = time.time()
        
        patterns_found = 0
        insights = []
        
        if self.brain:
            try:
                hippo = self.brain.curious.brain.hippo
                
                # 1. 컨텍스트 기반 패턴 찾기
                contexts = hippo.contexts
                context_groups = {}
                
                for word_id, ctx in contexts.items():
                    if ctx:
                        if ctx not in context_groups:
                            context_groups[ctx] = []
                        context_groups[ctx].append(word_id)
                
                # 2. 패턴 발견
                for ctx, words in context_groups.items():
                    if len(words) >= 3:
                        patterns_found += 1
                        insights.append(f"패턴: '{ctx}' 관련 기억 {len(words)}개")
                
                # 3. 노이즈 기반 창의적 연결 (REM의 특징)
                if hasattr(self.brain, 'noise'):
                    noise = self.brain.noise.gaussian(self.config['noise_level'][SleepStage.REM])
                    if noise > 0.2:
                        insights.append("💡 창의적 연결 발생!")
                
            except Exception as e:
                print(f"    ⚠️ REM sleep 오류: {e}")
        
        return DreamReport(
            stage=SleepStage.REM,
            duration=time.time() - start_time,
            memories_processed=0,
            patterns_found=patterns_found,
            consolidations=0,
            pruned=0,
            insights=insights
        )
    
    def _process_wake_prep(self) -> DreamReport:
        """
        기상 준비
        - LLM 학습 데이터 생성
        - 성장 준비
        """
        self.current_stage = SleepStage.WAKE_PREP
        start_time = time.time()
        
        training_data_count = 0
        
        if self.brain:
            try:
                # 학습 데이터 생성 (transfer_to_llm 활용)
                hippo = self.brain.curious.brain.hippo
                
                # 공고화된 기억만 학습 데이터로
                for word_id, word_info in hippo.words.items():
                    synapses = word_info.get('synapses_dg_ca3', [])
                    
                    if synapses:
                        avg_weight = sum(
                            getattr(s, 'weight', 0) for s in synapses
                        ) / len(synapses)
                        
                        if avg_weight > 0.7:
                            # 학습 데이터 버퍼에 추가
                            self.training_buffer.append({
                                'word_id': word_id,
                                'context': hippo.contexts.get(word_id),
                                'weight': avg_weight,
                            })
                            training_data_count += 1
                
            except Exception as e:
                print(f"    ⚠️ Wake prep 오류: {e}")
        
        return DreamReport(
            stage=SleepStage.WAKE_PREP,
            duration=time.time() - start_time,
            memories_processed=training_data_count,
            patterns_found=0,
            consolidations=0,
            pruned=0
        )
    
    def _calculate_growth(self, report: SleepReport) -> float:
        """성장 점수 계산"""
        # 가중치
        weights = {
            'memories': 0.2,
            'patterns': 0.3,
            'consolidations': 0.3,
            'training_data': 0.2,
        }
        
        # 정규화 (최대 100개 기준)
        memories_score = min(1.0, report.memories_processed / 100)
        patterns_score = min(1.0, report.patterns_found / 20)
        consolidation_score = min(1.0, report.consolidations / 50)
        training_score = min(1.0, report.training_data_generated / 30)
        
        growth = (
            weights['memories'] * memories_score +
            weights['patterns'] * patterns_score +
            weights['consolidations'] * consolidation_score +
            weights['training_data'] * training_score
        )
        
        return growth
    
    # =========================================================================
    # 📊 보고서
    # =========================================================================
    
    def get_last_report(self) -> Optional[SleepReport]:
        """마지막 수면 보고서"""
        if self.sleep_history:
            return self.sleep_history[-1]
        return None
    
    def get_stats(self) -> Dict:
        """통계"""
        return {
            'is_sleeping': self.is_sleeping,
            'current_stage': self.current_stage.value,
            'total_sessions': self.stats['total_sleep_sessions'],
            'total_memories': self.stats['total_memories_processed'],
            'total_patterns': self.stats['total_patterns_found'],
            'total_consolidations': self.stats['total_consolidations'],
            'training_buffer_size': len(self.training_buffer),
        }
    
    def export_training_data(self, output_path: str = None) -> str:
        """학습 데이터 내보내기"""
        if output_path is None:
            output_path = Path(__file__).parent.parent.parent / "data" / "dream_training.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.training_buffer, f, ensure_ascii=False, indent=2)
        
        print(f"📝 학습 데이터 저장: {output_path} ({len(self.training_buffer)}개)")
        
        return str(output_path)
    
    def get_report_summary(self, report: SleepReport) -> str:
        """보고서 요약 문자열"""
        return f"""
╔══════════════════════════════════════════╗
║  🌙 수면 보고서
╠══════════════════════════════════════════╣
║  총 시간: {report.total_duration:.1f}초
║  사이클: {report.cycles}회
╠══════════════════════════════════════════╣
║  📊 단계별 시간
║  - Light: {report.stages.get('light', 0):.1f}초
║  - Deep:  {report.stages.get('deep', 0):.1f}초
║  - REM:   {report.stages.get('rem', 0):.1f}초
╠══════════════════════════════════════════╣
║  📈 결과
║  - 기억 처리: {report.memories_processed}개
║  - 패턴 발견: {report.patterns_found}개
║  - 시냅스 강화: {report.consolidations}개
║  - 가지치기: {report.pruned}개
║  - 학습 데이터: {report.training_data_generated}개
╠══════════════════════════════════════════╣
║  🌟 성장 점수: {report.growth_score:.2f}
╚══════════════════════════════════════════╝
"""

