"""
=============================================================================
Pattern Fine-Tuning: 학습된 패턴 기반 LLM 파인튜닝
=============================================================================

🌊 철학:
    "하드코딩은 죽음이다"
    "패턴은 발견되는 것이지 지정되는 것이 아님"
    "학습된 경험이 언어 모델의 성격이 된다"

📐 핵심 원리:

    1. 패턴 수집 (Pattern Collection)
       - HippoMemory의 공고화된 기억
       - ResponseMemory의 학습된 응답
       - PatternMemory의 발견된 패턴
       
    2. 데이터 변환 (Data Transformation)
       - 패턴 → 자연어 문장
       - 질문-응답 쌍 생성
       - 맥락 정보 포함
       
    3. 파인튜닝 데이터 생성 (Training Data Generation)
       - nanoGPT 형식 (char-level)
       - 중요도 기반 반복 (중요한 패턴 더 많이)
       - 노이즈 추가 (변형으로 일반화)

생물학적 근거:
    - Systems Consolidation Theory
    - 해마 → 대뇌피질 전이
    - 반복 노출로 장기 기억 형성

Author: GNJz (Qquarts)
Version: 1.0.0
=============================================================================
"""

import os
import sys
import json
import time
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

# 경로 설정
BABYHIPPO_PATH = Path(__file__).parent.parent
NANOGPT_PATH = BABYHIPPO_PATH.parent / "nanoGPT"


@dataclass
class TrainingSample:
    """
    학습 샘플
    
    Attributes:
        text: 학습 텍스트
        source: 출처 (hippo/response/pattern)
        importance: 중요도 (0~1)
        pattern_id: 관련 패턴 ID
        metadata: 추가 정보
    """
    text: str
    source: str = "unknown"
    importance: float = 0.5
    pattern_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class PatternCollector:
    """
    패턴 수집기
    
    여러 소스에서 학습된 패턴을 수집:
    - HippoMemory (공고화된 기억)
    - ResponseMemory (학습된 응답)
    - PatternMemory (발견된 패턴)
    """
    
    def __init__(self, 
                 hippo_memory=None,
                 response_memory=None,
                 pattern_memory=None):
        self.hippo = hippo_memory
        self.response_memory = response_memory
        self.pattern_memory = pattern_memory
        
    def collect_from_hippo(self, consolidation_threshold: float = 0.5) -> List[TrainingSample]:
        """
        HippoMemory에서 공고화된 기억 수집
        
        Args:
            consolidation_threshold: 공고화 임계값
            
        Returns:
            학습 샘플 리스트
        """
        samples = []
        
        if not self.hippo or not hasattr(self.hippo, 'words'):
            return samples
        
        for word_id, word_info in self.hippo.words.items():
            # 공고화 수준 확인
            synapses = word_info.get('synapses_dg_ca3', [])
            if not synapses:
                continue
            
            avg_consolidation = np.mean([
                getattr(syn, 'consolidation_level', 0) for syn in synapses
            ])
            
            if avg_consolidation >= consolidation_threshold:
                # 중요도 계산
                try:
                    importance = self.hippo.memory_ranker.get_score(word_id, default=0.5)
                except:
                    importance = 0.5
                
                context = self.hippo.contexts.get(word_id, '')
                frequency = self.hippo.word_frequencies.get(word_id, 1)
                
                # 텍스트 생성
                text = word_id
                if context:
                    text = f"[{context}] {text}"
                
                samples.append(TrainingSample(
                    text=text,
                    source="hippo",
                    importance=importance,
                    pattern_id=word_id,
                    metadata={
                        'consolidation': avg_consolidation,
                        'frequency': frequency,
                        'context': context,
                    }
                ))
        
        return samples
    
    def collect_from_response_memory(self, usage_threshold: int = 3) -> List[TrainingSample]:
        """
        ResponseMemory에서 자주 사용된 응답 패턴 수집
        
        Args:
            usage_threshold: 최소 사용 횟수
            
        Returns:
            학습 샘플 리스트
        """
        samples = []
        
        if not self.response_memory:
            return samples
        
        for category, responses in self.response_memory.responses.items():
            for lr in responses:
                if lr.usage_count >= usage_threshold:
                    # 트리거 + 응답 쌍으로 변환
                    triggers = lr.triggers or [category]
                    
                    for trigger in triggers:
                        # Q&A 형식
                        text = f"Q: {trigger}\nA: {lr.response}"
                        
                        samples.append(TrainingSample(
                            text=text,
                            source="response",
                            importance=min(1.0, lr.success_score * 0.5),
                            pattern_id=f"resp_{category}_{id(lr)}",
                            metadata={
                                'category': category,
                                'usage_count': lr.usage_count,
                                'success_score': lr.success_score,
                            }
                        ))
        
        return samples
    
    def collect_from_pattern_memory(self) -> List[TrainingSample]:
        """
        PatternMemory에서 학습된 패턴 수집
        
        Returns:
            학습 샘플 리스트
        """
        samples = []
        
        if not self.pattern_memory:
            return samples
        
        for pattern_id, pattern in self.pattern_memory.patterns.items():
            # 패턴의 연관 레이블로 텍스트 생성
            labels = pattern.associated_labels or [pattern_id]
            text = " ".join(labels)
            
            samples.append(TrainingSample(
                text=text,
                source="pattern",
                importance=min(1.0, pattern.strength / 5.0),
                pattern_id=pattern_id,
                metadata={
                    'activation_count': pattern.activation_count,
                    'strength': pattern.strength,
                }
            ))
        
        return samples
    
    def collect_all(self, 
                    hippo_threshold: float = 0.5,
                    response_threshold: int = 3) -> List[TrainingSample]:
        """
        모든 소스에서 패턴 수집
        
        Returns:
            통합된 학습 샘플 리스트
        """
        all_samples = []
        
        # HippoMemory
        hippo_samples = self.collect_from_hippo(hippo_threshold)
        all_samples.extend(hippo_samples)
        print(f"   📦 HippoMemory: {len(hippo_samples)}개")
        
        # ResponseMemory
        response_samples = self.collect_from_response_memory(response_threshold)
        all_samples.extend(response_samples)
        print(f"   📦 ResponseMemory: {len(response_samples)}개")
        
        # PatternMemory
        pattern_samples = self.collect_from_pattern_memory()
        all_samples.extend(pattern_samples)
        print(f"   📦 PatternMemory: {len(pattern_samples)}개")
        
        return all_samples


class TrainingDataGenerator:
    """
    학습 데이터 생성기
    
    수집된 패턴을 nanoGPT 학습 데이터로 변환
    """
    
    def __init__(self, noise_level: float = 0.1):
        self.noise_level = noise_level
        
    def augment_text(self, text: str) -> List[str]:
        """
        텍스트 증강 (변형으로 일반화)
        
        Args:
            text: 원본 텍스트
            
        Returns:
            변형된 텍스트들
        """
        variations = [text]  # 원본 포함
        
        # 1. 공백 변형
        if ' ' in text:
            variations.append(text.replace(' ', '  '))  # 더블 스페이스
        
        # 2. 대소문자 변형
        if any(c.isalpha() for c in text):
            variations.append(text.lower())
            variations.append(text.upper())
        
        # 3. 순서 셔플 (단어 단위)
        words = text.split()
        if len(words) > 2:
            shuffled = words.copy()
            random.shuffle(shuffled)
            variations.append(' '.join(shuffled))
        
        return variations
    
    def generate_training_text(self, 
                               samples: List[TrainingSample],
                               repeat_by_importance: bool = True,
                               augment: bool = True) -> str:
        """
        학습 데이터 텍스트 생성
        
        Args:
            samples: 학습 샘플들
            repeat_by_importance: 중요도 기반 반복
            augment: 데이터 증강 여부
            
        Returns:
            학습용 텍스트
        """
        lines = []
        
        for sample in samples:
            # 중요도 기반 반복 횟수 결정
            if repeat_by_importance:
                repeat_count = max(1, int(sample.importance * 5))
            else:
                repeat_count = 1
            
            # 텍스트 추가
            for _ in range(repeat_count):
                if augment:
                    variations = self.augment_text(sample.text)
                    lines.extend(variations)
                else:
                    lines.append(sample.text)
        
        # 셔플 (학습 안정성)
        random.shuffle(lines)
        
        return '\n'.join(lines)
    
    def export_to_nanogpt(self, 
                          samples: List[TrainingSample],
                          output_dir: str = None) -> Dict[str, str]:
        """
        nanoGPT 형식으로 내보내기
        
        Args:
            samples: 학습 샘플들
            output_dir: 출력 디렉토리
            
        Returns:
            생성된 파일 경로들
        """
        if output_dir is None:
            output_dir = NANOGPT_PATH / "data" / "hippo_patterns"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 학습 데이터 생성
        train_text = self.generate_training_text(
            samples, 
            repeat_by_importance=True,
            augment=True
        )
        
        # 파일 저장
        train_path = output_dir / "train.txt"
        with open(train_path, 'w', encoding='utf-8') as f:
            f.write(train_text)
        
        # 메타 정보 저장
        meta = {
            'created_at': datetime.now().isoformat(),
            'samples_count': len(samples),
            'total_lines': len(train_text.split('\n')),
            'sources': list(set(s.source for s in samples)),
        }
        
        meta_path = output_dir / "meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        return {
            'train': str(train_path),
            'meta': str(meta_path),
        }


class PatternFineTuner:
    """
    패턴 파인튜너
    
    학습된 패턴을 기반으로 LLM 파인튜닝
    """
    
    def __init__(self):
        self.collector = None
        self.generator = TrainingDataGenerator()
        self.samples: List[TrainingSample] = []
        
    def setup(self, 
              hippo_memory=None,
              response_memory=None,
              pattern_memory=None):
        """
        소스 설정
        
        Args:
            hippo_memory: HippoMemory 인스턴스
            response_memory: ResponseMemory 인스턴스
            pattern_memory: PatternMemory 인스턴스
        """
        self.collector = PatternCollector(
            hippo_memory=hippo_memory,
            response_memory=response_memory,
            pattern_memory=pattern_memory
        )
    
    def collect_patterns(self) -> int:
        """
        패턴 수집
        
        Returns:
            수집된 샘플 수
        """
        if not self.collector:
            print("⚠️ setup()을 먼저 호출하세요")
            return 0
        
        print("📊 패턴 수집 중...")
        self.samples = self.collector.collect_all()
        print(f"   총 {len(self.samples)}개 샘플 수집됨")
        
        return len(self.samples)
    
    def prepare_training_data(self, output_dir: str = None) -> Dict[str, str]:
        """
        학습 데이터 준비
        
        Args:
            output_dir: 출력 디렉토리
            
        Returns:
            생성된 파일 경로들
        """
        if not self.samples:
            print("⚠️ collect_patterns()를 먼저 호출하세요")
            return {}
        
        print("📝 학습 데이터 생성 중...")
        paths = self.generator.export_to_nanogpt(self.samples, output_dir)
        
        print(f"   ✅ 학습 데이터 생성 완료")
        print(f"      train: {paths['train']}")
        print(f"      meta: {paths['meta']}")
        
        return paths
    
    def generate_finetune_script(self, output_path: str = None) -> str:
        """
        파인튜닝 스크립트 생성
        
        Args:
            output_path: 스크립트 경로
            
        Returns:
            스크립트 경로
        """
        if output_path is None:
            output_path = NANOGPT_PATH / "finetune_patterns.sh"
        
        script = f"""#!/bin/bash
# =============================================================================
# babyhippo Pattern Fine-Tuning Script
# 학습된 패턴으로 nanoGPT 파인튜닝
# =============================================================================

cd {NANOGPT_PATH}

# 1. 데이터 준비
echo "📦 데이터 준비..."
python3 data/hippo_patterns/prepare.py

# 2. 파인튜닝 (기존 체크포인트 기반)
echo "🔧 파인튜닝 시작..."
python3 train.py \\
    --dataset=hippo_patterns \\
    --init_from=resume \\
    --out_dir=out-hippo-patterns \\
    --eval_interval=50 \\
    --max_iters=500 \\
    --learning_rate=1e-4 \\
    --batch_size=8

echo "✅ 파인튜닝 완료!"
echo "   모델 경로: out-hippo-patterns/ckpt.pt"
"""
        
        with open(output_path, 'w') as f:
            f.write(script)
        
        # 실행 권한 부여
        os.chmod(output_path, 0o755)
        
        return str(output_path)
    
    def run_pipeline(self, 
                     hippo_memory=None,
                     response_memory=None,
                     pattern_memory=None,
                     output_dir: str = None) -> Dict[str, Any]:
        """
        전체 파이프라인 실행
        
        Args:
            hippo_memory: HippoMemory 인스턴스
            response_memory: ResponseMemory 인스턴스
            pattern_memory: PatternMemory 인스턴스
            output_dir: 출력 디렉토리
            
        Returns:
            파이프라인 결과
        """
        print("=" * 60)
        print("🌊 Pattern Fine-Tuning Pipeline")
        print("=" * 60)
        
        # 1. 설정
        print("\n1️⃣ 설정...")
        self.setup(hippo_memory, response_memory, pattern_memory)
        
        # 2. 패턴 수집
        print("\n2️⃣ 패턴 수집...")
        sample_count = self.collect_patterns()
        
        if sample_count == 0:
            print("   ⚠️ 수집된 패턴이 없습니다")
            return {'status': 'no_patterns', 'samples': 0}
        
        # 3. 학습 데이터 준비
        print("\n3️⃣ 학습 데이터 준비...")
        paths = self.prepare_training_data(output_dir)
        
        # 4. 파인튜닝 스크립트 생성
        print("\n4️⃣ 파인튜닝 스크립트 생성...")
        script_path = self.generate_finetune_script()
        print(f"   스크립트: {script_path}")
        
        print("\n" + "=" * 60)
        print("✅ 파이프라인 완료!")
        print(f"   샘플 수: {sample_count}개")
        print(f"   학습 데이터: {paths.get('train', 'N/A')}")
        print(f"   파인튜닝 실행: bash {script_path}")
        print("=" * 60)
        
        return {
            'status': 'completed',
            'samples': sample_count,
            'paths': paths,
            'script': script_path,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """통계"""
        if not self.samples:
            return {'samples': 0}
        
        sources = {}
        for s in self.samples:
            sources[s.source] = sources.get(s.source, 0) + 1
        
        importances = [s.importance for s in self.samples]
        
        return {
            'samples': len(self.samples),
            'sources': sources,
            'avg_importance': np.mean(importances),
            'max_importance': max(importances),
            'min_importance': min(importances),
        }


# =============================================================================
# 테스트
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌊 Pattern Fine-Tuning Test")
    print("=" * 60)
    
    # 1. 가상 데이터로 테스트
    print("\n1️⃣ 가상 샘플 생성...")
    samples = [
        TrainingSample("안녕하세요", source="hippo", importance=0.9),
        TrainingSample("Q: 이름\nA: babyhippo입니다", source="response", importance=0.8),
        TrainingSample("고양이 강아지 동물", source="pattern", importance=0.7),
    ]
    
    # 2. 학습 데이터 생성
    print("\n2️⃣ 학습 데이터 생성...")
    generator = TrainingDataGenerator()
    text = generator.generate_training_text(samples, augment=True)
    print(f"   생성된 라인 수: {len(text.split(chr(10)))}")
    
    # 3. 파인튜너 테스트
    print("\n3️⃣ 파인튜너 테스트...")
    finetuner = PatternFineTuner()
    finetuner.samples = samples  # 직접 주입
    
    stats = finetuner.get_stats()
    print(f"   통계: {stats}")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)

