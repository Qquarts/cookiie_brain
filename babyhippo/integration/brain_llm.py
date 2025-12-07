"""
BrainLLM: 해마 중심 LLM 통합 시스템

🧠 철학:
    LLM에 기억 붙이기 ❌ (거꾸로)
    해마에 LLM 붙이기 ⭕ (생물학적으로 맞음)
    
    기억이 먼저 → 언어는 나중
    해마가 중심 → LLM은 언어 피질 모듈

구조:
    Hippocampus (해마) = 기억의 중심
         ↓ 공고화 (consolidation)
    nanoGPT (언어 피질) = 언어 처리
    
    시간이 지나면 해마 기억 → LLM으로 전이
    아기가 자라면서 언어를 배우는 것처럼

Author: GNJz (Qquarts)
Version: 1.0
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import time

# nanoGPT 경로 추가
NANOGPT_PATH = Path(__file__).parent.parent.parent / "nanoGPT"
sys.path.insert(0, str(NANOGPT_PATH))

# 모듈 임포트 (새 구조)
from ..memory import HippoMemory, PanoramaMemory, MemoryRank
from ..utils import StimulusAccumulator


class HippoToLLM:
    """
    해마 → LLM 전이 메커니즘
    
    공고화된 기억을 LLM 학습 데이터로 변환
    실제 뇌에서 해마→대뇌피질 전이처럼
    """
    
    def __init__(self, hippocampus: HippoMemory, panorama: PanoramaMemory = None):
        self.hippo = hippocampus
        self.panorama = panorama or PanoramaMemory("brain_llm")
        self.accumulator = StimulusAccumulator("brain_llm")
        
        # 전이 임계값
        self.consolidation_threshold = 0.7  # 이 이상 공고화되면 전이
        
        # 전이된 기억 기록
        self.transferred_memories: List[str] = []
        
        # 학습 데이터 저장
        self.training_data: List[Dict] = []
    
    def collect_consolidated_memories(self) -> List[Dict]:
        """
        공고화된 기억 수집 (전이 대상)
        
        consolidation_level > threshold인 기억들
        """
        consolidated = []
        
        for word_id, word_info in self.hippo.words.items():
            # 이미 전이된 건 스킵
            if word_id in self.transferred_memories:
                continue
            
            # 시냅스의 평균 공고화 수준
            synapses = word_info.get('synapses_dg_ca3', [])
            if not synapses:
                continue
            
            avg_consolidation = sum(
                syn.consolidation_level for syn in synapses
            ) / len(synapses)
            
            if avg_consolidation >= self.consolidation_threshold:
                # 전이 대상
                importance = self.hippo.memory_ranker.get_score(word_id, default=0.5)
                
                consolidated.append({
                    'word_id': word_id,
                    'consolidation': avg_consolidation,
                    'importance': importance,
                    'context': self.hippo.contexts.get(word_id),
                    'frequency': self.hippo.word_frequencies.get(word_id, 1),
                })
        
        return consolidated
    
    def memory_to_training_text(self, memory: Dict) -> str:
        """
        기억을 학습 텍스트로 변환
        
        Args:
            memory: 공고화된 기억 정보
            
        Returns:
            학습용 텍스트
        """
        word_id = memory['word_id']
        context = memory.get('context', '')
        importance = memory.get('importance', 0.5)
        
        # 기본 텍스트
        text = word_id
        
        # 맥락 추가
        if context:
            text = f"{context}: {text}"
        
        # Panorama에서 관련 기억 찾기
        if self.panorama:
            related = self.panorama.recall(word_id, top_n=3, include_deep=True)
            for r in related:
                content = r.get('content', '')
                if content and content != word_id:
                    text += f" {content}"
        
        return text
    
    def prepare_training_data(self) -> List[str]:
        """
        LLM 학습 데이터 준비
        
        Returns:
            학습용 텍스트 리스트
        """
        consolidated = self.collect_consolidated_memories()
        
        training_texts = []
        for mem in consolidated:
            text = self.memory_to_training_text(mem)
            training_texts.append(text)
            
            # 전이 기록
            self.transferred_memories.append(mem['word_id'])
            self.training_data.append({
                'text': text,
                'memory': mem,
                'transferred_at': time.time()
            })
        
        return training_texts
    
    def export_for_nanogpt(self, output_path: str = None) -> str:
        """
        nanoGPT 학습용 데이터 파일 생성
        
        Args:
            output_path: 출력 경로 (기본: data/hippo/train.txt)
            
        Returns:
            생성된 파일 경로
        """
        if output_path is None:
            output_dir = NANOGPT_PATH / "data" / "hippo"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / "train.txt")
        
        # 학습 데이터 수집
        training_texts = self.prepare_training_data()
        
        # 파일 작성
        with open(output_path, 'w', encoding='utf-8') as f:
            for text in training_texts:
                f.write(text + '\n')
        
        return output_path
    
    def get_transfer_stats(self) -> Dict:
        """전이 통계"""
        return {
            'total_memories': len(self.hippo.words),
            'transferred': len(self.transferred_memories),
            'pending': len(self.hippo.words) - len(self.transferred_memories),
            'training_samples': len(self.training_data),
            'threshold': self.consolidation_threshold,
        }


class BrainLLM:
    """
    해마 중심 LLM 시스템
    
    해마(기억) + nanoGPT(언어) 통합
    기억을 참조하면서 언어 생성
    """
    
    def __init__(self, 
                 hippocampus: HippoMemory = None,
                 model_path: str = None,
                 device: str = 'auto'):
        """
        Args:
            hippocampus: HippoMemory 인스턴스 (없으면 새로 생성)
            model_path: 학습된 nanoGPT 모델 경로
            device: 'cpu' or 'cuda'
        """
        # 해마 (기억 중심)
        self.hippo = hippocampus or HippoMemory()
        self.panorama = PanoramaMemory("brain_llm")
        self.accumulator = StimulusAccumulator("brain_llm")
        
        # 전이 메커니즘
        self.transfer = HippoToLLM(self.hippo, self.panorama)
        
        # 디바이스 자동 선택
        # 🍪 저전력 모드: 기본적으로 CPU만 사용 (라즈베리파이/엣지 디바이스 최적화)
        if device == 'auto':
            # 저전력 모드: GPU 사용 안 함 (발열/전력 절약)
            self.device = 'cpu'
            print("💻 CPU 사용 (저전력 모드)")
            # GPU 사용이 필요한 경우에만 아래 주석 해제:
            # import torch
            # if torch.backends.mps.is_available():
            #     self.device = 'mps'  # Apple Silicon GPU
            #     print("🚀 Apple GPU (MPS) 사용")
            # elif torch.cuda.is_available():
            #     self.device = 'cuda'  # NVIDIA GPU
            #     print("🚀 NVIDIA GPU (CUDA) 사용")
            # else:
            #     self.device = 'cpu'
            #     print("💻 CPU 사용")
        else:
            self.device = device
        
        # nanoGPT 모델
        self.model = None
        self.model_path = model_path
        
        # 문자 인코딩 (char-level)
        self.stoi = {}
        self.itos = {}
        
        # 설정
        self.config = {
            'max_tokens': 100,
            'temperature': 0.8,
            'top_k': 40,
        }
        
        # 모델 로드
        # 🍪 저전력 모드: 기본적으로 모델 로드 안 함 (라즈베리파이/엣지 디바이스 최적화)
        # 모델이 필요하면 명시적으로 load_model() 호출
        # if model_path and os.path.exists(model_path):
        #     self.load_model(model_path)
    
    def load_model(self, path: str):
        """학습된 모델 로드"""
        try:
            import torch
            sys.path.insert(0, str(NANOGPT_PATH))
            from model import GPT, GPTConfig
            import pickle
            
            # 체크포인트 로드
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)
            
            # 모델 생성
            config = GPTConfig(**checkpoint['model_args'])
            self.model = GPT(config)
            
            # state dict 정리
            state_dict = checkpoint['model']
            unwanted_prefix = '_orig_mod.'
            for k, v in list(state_dict.items()):
                if k.startswith(unwanted_prefix):
                    state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
            
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            
            # 메타 정보 로드 (문자 인코딩)
            meta_path = NANOGPT_PATH / "data" / "hippo" / "meta.pkl"
            if meta_path.exists():
                with open(meta_path, 'rb') as f:
                    meta = pickle.load(f)
                self.stoi = meta['stoi']
                self.itos = meta['itos']
            
            print(f"✅ 모델 로드 완료: {path}")
            print(f"   파라미터: {sum(p.numel() for p in self.model.parameters()):,}")
            
        except Exception as e:
            print(f"⚠️ 모델 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
    
    def learn(self, text: str, context: str = None, importance: float = 0.5):
        """
        새로운 정보 학습 (해마에 저장)
        
        🍪 v1.0: 키워드 추출하여 저장
        
        Args:
            text: 학습할 텍스트
            context: 맥락
            importance: 중요도
        """
        # 🍪 v1.0: 키워드 추출 (첫 단어 또는 주요 단어)
        # 예: "A는 알파벳 첫 글자입니다." → "A"와 전체 문장 모두 저장
        keywords = []
        words = text.split()
        if words:
            # 첫 단어가 키워드일 가능성 높음
            first_word = words[0].strip('는은이가을를의에와과')
            if first_word:
                keywords.append(first_word)
        
        # 해마에 저장 (키워드와 전체 문장 모두)
        for keyword in keywords:
            self.hippo.learn(keyword, context=context)
        # 전체 문장도 저장
        self.hippo.learn(text, context=context)
        
        # Panorama에 저장
        self.panorama.store(
            content=text,
            context=context,
            importance=importance
        )
        
        # 자극 축적
        self.accumulator.receive(
            content=text,
            intensity=importance,
            valence=0.0,
            context=context
        )
    
    def recall(self, query: str, top_n: int = 5) -> List[Dict]:
        """
        기억 검색
        
        Args:
            query: 검색어
            top_n: 반환 개수
            
        Returns:
            관련 기억들
        """
        results = []
        
        # 해마에서 검색
        hippo_results = self.hippo.recall(query, top_n=top_n)
        if hippo_results:
            if isinstance(hippo_results, str):
                # 🍪 v1.0: 문자열이면 바로 사용 (이미 원본 텍스트)
                results.append({'source': 'hippo', 'content': hippo_results, 'score': 0.8})
            else:
                # 🍪 v1.0: (word_text, score) 튜플 리스트
                for word_text, score in hippo_results:
                    results.append({
                        'source': 'hippo',
                        'content': word_text,
                        'score': score
                    })
        
        # Panorama에서 검색
        panorama_results = self.panorama.recall(query, top_n=top_n)
        for r in panorama_results:
            results.append({
                'source': 'panorama',
                'content': r.get('content'),
                'score': r.get('recall_score', 0.5)
            })
        
        # 점수로 정렬
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results[:top_n]
    
    def generate(self, prompt: str, use_memory: bool = True) -> str:
        """
        텍스트 생성 (해마 참조)
        
        Args:
            prompt: 프롬프트
            use_memory: 기억 참조 여부
            
        Returns:
            생성된 텍스트
        """
        # 기억에서 관련 정보 검색
        memory_context = ""
        if use_memory:
            memories = self.recall(prompt, top_n=3)
            if memories:
                memory_context = "[기억] " + " | ".join(
                    m.get('content', '') for m in memories if m.get('content')
                ) + "\n\n"
        
        # nanoGPT로 생성
        if self.model is not None:
            return self._generate_with_model(memory_context + prompt)
        else:
            # 모델 없으면 기억만 반환
            return memory_context + f"[모델 없음] 프롬프트: {prompt}"
    
    def _generate_with_model(self, prompt: str) -> str:
        """nanoGPT 모델로 생성 (문자 단위)"""
        try:
            import torch
            
            # 문자 단위 인코딩 (학습 데이터와 동일)
            if hasattr(self, 'stoi') and self.stoi:
                encode = lambda s: [self.stoi[c] for c in s if c in self.stoi]
                decode = lambda l: ''.join([self.itos[i] for i in l])
            else:
                return f"[오류] 인코딩 메타 정보 없음"
            
            # 인코딩
            tokens = encode(prompt)
            if not tokens:
                return f"[오류] 인코딩 실패: '{prompt}'"
            
            x = torch.tensor([tokens], dtype=torch.long, device=self.device)
            
            # 생성
            with torch.no_grad():
                y = self.model.generate(
                    x,
                    max_new_tokens=self.config['max_tokens'],
                    temperature=self.config['temperature'],
                    top_k=self.config['top_k']
                )
            
            # 디코딩
            generated = decode(y[0].tolist())
            
            return generated
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"[생성 오류] {e}"
    
    def sleep(self, cycles: int = 10):
        """
        수면 공고화
        
        해마 기억 강화 + LLM 전이 준비
        """
        # 해마 공고화
        self.hippo.sleep(cycles=cycles)
        
        # 전이 가능한 기억 확인
        consolidated = self.transfer.collect_consolidated_memories()
        
        print(f"💤 수면 완료: {cycles} 사이클")
        print(f"   전이 준비된 기억: {len(consolidated)}개")
    
    def transfer_to_llm(self) -> str:
        """
        공고화된 기억을 LLM으로 전이
        
        Returns:
            생성된 학습 데이터 경로
        """
        output_path = self.transfer.export_for_nanogpt()
        stats = self.transfer.get_transfer_stats()
        
        print(f"🧠→📚 기억 전이 완료")
        print(f"   전이된 기억: {stats['transferred']}개")
        print(f"   학습 데이터: {output_path}")
        
        return output_path
    
    def get_stats(self) -> Dict:
        """통계"""
        return {
            'hippo': self.hippo.get_stats(),
            'panorama': self.panorama.get_stats(),
            'accumulator': self.accumulator.get_stats(),
            'transfer': self.transfer.get_transfer_stats(),
            'model_loaded': self.model is not None,
        }
    
    def __repr__(self):
        return f"BrainLLM(memories={len(self.hippo.words)}, model={'loaded' if self.model else 'none'})"


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 BrainLLM Test - 해마 중심 LLM 시스템")
    print("=" * 60)
    
    # 학습된 모델 경로
    model_path = NANOGPT_PATH / "out-hippo" / "ckpt.pt"
    
    # 시스템 생성 (학습된 모델 포함)
    print(f"\n🔧 시스템 생성 중...")
    if model_path.exists():
        brain = BrainLLM(model_path=str(model_path))
    else:
        print(f"   ⚠️ 모델 없음: {model_path}")
        brain = BrainLLM()
    
    # 학습 (해마에 저장)
    print("\n📝 해마에 기억 저장...")
    brain.learn("안녕하세요 저는 재진입니다", context="소개", importance=0.9)
    brain.learn("고양이를 좋아합니다", context="선호", importance=0.8)
    brain.learn("파이썬 프로그래밍을 합니다", context="기술", importance=0.7)
    brain.learn("서울에 살고 있습니다", context="위치", importance=0.6)
    
    # 수면 (공고화)
    print("\n💤 수면 공고화...")
    for _ in range(3):
        brain.sleep(cycles=5)
    
    # 기억 검색
    print("\n🔍 기억 검색 테스트:")
    memories = brain.recall("재진")
    for m in memories[:3]:
        print(f"  [{m['source']}] {m['content']}")
    
    # 생성 (모델 있으면 LLM 사용)
    print("\n✨ 텍스트 생성 (해마 + LLM):")
    
    prompts = [
        "안녕",
        "기억이란",
        "babyhippo",
    ]
    
    for prompt in prompts:
        print(f"\n프롬프트: '{prompt}'")
        response = brain.generate(prompt)
        # 첫 100자만 출력
        print(f"  → {response[:150]}...")
    
    # 통계
    print("\n📊 통계:")
    stats = brain.get_stats()
    print(f"  해마 기억: {stats['hippo']['words']}개")
    print(f"  LLM 모델: {'로드됨 ✅' if stats['model_loaded'] else '없음 ❌'}")
    
    print("\n" + "=" * 60)
    print("✅ babyhippo 해마 중심 LLM 시스템 완성!")
    print("=" * 60)

