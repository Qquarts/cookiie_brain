"""
babyHippo: Biologically-Inspired Memory System
Single, complete product with all features built-in

Features:
- Hippocampal neural architecture (DG → CA3 → CA1)
- STDP learning with sleep consolidation
- PageRank-based importance scoring
- Optimized for real-world use

Author: GNJz (Qquarts)
Version: 1.0 (Complete Edition)
"""
import numpy as np

# 모듈 임포트 (새 구조)
from ..neural import DGNeuron, CA3Neuron, CA1TimeCell, CA1NoveltyDetector, SubiculumGate
from ..neural import STDPSynapse, reset_all_synapses
from ..neural import SleepManager, SleepConfig  # 동역학적 수면 🆕
from ..utils import Storage
from ..utils import text_to_vector, cosine_similarity, simple_hash
from .memory_rank import MemoryRank, apply_memory_rank

# Storage helper functions
def save_memory(data, filename):
    return Storage.save(data, filename)

def load_memory(filename):
    return Storage.load(filename)

def compute_similarity(v1, v2):
    return cosine_similarity(v1, v2)

def create_word_id(word):
    return simple_hash(word)


class HippoMemory:
    """
    babyHippo: Complete hippocampal memory system
    
    Architecture:
        Input → DG (sparse coding)
              → CA3 (associative memory with recurrence)
              → CA1 (temporal + novelty detection)
              → Subiculum (context gating)
              → Output
    
    Capacity: ~1,000 words (adjustable)
    
    Usage:
        hippo = HippoMemory()
        hippo.learn("cat", context="animal")
        hippo.sleep()
        result = hippo.recall("ca")
    """
    
    def __init__(self, capacity=10000):
        """
        Initialize babyHippo memory system
        
        Args:
            capacity: Maximum number of words to store (default: 10000)
        """
        self.version = "1.0.0"
        self.capacity = capacity
        
        # Neural parameters (optimized for balance)
        self.ca3_size = 30  # 30 neurons per word
        
        # Memory storage
        self.words = {}  # word_id -> word_info
        self.word_texts = {}  # word_id -> original word text (🍪 v1.0)
        self.contexts = {}
        self.word_frequencies = {}
        
        # Network components
        self.dg_neurons = []
        self.ca3_neurons = []
        self.ca1_time_cells = []
        self.ca1_novelty = CA1NoveltyDetector("Novelty")
        self.subiculum_gates = []
        
        # Synapses
        self.dg_to_ca3_synapses = []
        self.ca3_recurrent_synapses = []  # CA3↔CA3 for PageRank
        self.ca3_to_ca1_synapses = []
        
        # MemoryRank (PageRank for memory importance)
        self.memory_ranker = MemoryRank(self, cache_enabled=True)
        
        # Simulation parameters
        self.dt = 0.1
        self.T_learn = 80.0
        self.T_recall = 60.0
    
    def learn(self, word, context=None):
        """
        Learn a new word
        
        Args:
            word: Word to learn (string)
            context: Optional context label (string)
        """
        word_id = create_word_id(word)
        
        # Check capacity
        if word_id not in self.words and len(self.words) >= self.capacity:
            print(f"⚠️  Memory full ({self.capacity} words). Use sleep() to consolidate.")
            return
        
        # 🍪 v1.0: 원본 단어 텍스트 저장
        self.word_texts[word_id] = word
        
        # Already learned? Strengthen it
        if word_id in self.words:
            self._strengthen_word(word_id)
            self.word_frequencies[word_id] += 1
            return
        
        # Create neurons
        dg_idx = len(self.dg_neurons)
        ca3_idx = len(self.ca3_neurons)
        ca1_idx = len(self.ca1_time_cells)
        sub_idx = len(self.subiculum_gates)
        
        # DG: 2 neurons (sparse coding)
        dg_a = DGNeuron(f"DG_{word_id}_0")
        dg_b = DGNeuron(f"DG_{word_id}_1")
        self.dg_neurons.extend([dg_a, dg_b])
        
        # CA3: 30 neurons (associative memory)
        ca3_neurons_word = []
        for i in range(self.ca3_size):
            ca3_n = CA3Neuron(f"CA3_{word_id}_{i}")
            ca3_neurons_word.append(ca3_n)
            self.ca3_neurons.append(ca3_n)
        
        # CA1: 1 time cell
        ca1_time = CA1TimeCell(delay_ms=ca1_idx*10, name=f"CA1_Time_{word_id}")
        self.ca1_time_cells.append(ca1_time)
        
        # Subiculum: 1 gate
        sub_gate = SubiculumGate(f"Sub_{word_id}")
        self.subiculum_gates.append(sub_gate)
        
        # Create synapses DG → CA3
        word_synapses_dg_ca3 = []
        for dg_n in [dg_a, dg_b]:
            for ca3_n in ca3_neurons_word:
                syn = STDPSynapse(dg_n, ca3_n, delay_ms=2.0, Q_max=50.0)
                word_synapses_dg_ca3.append(syn)
                self.dg_to_ca3_synapses.append(syn)
        
        # Create CA3 recurrent connections (for PageRank!)
        # ~20% connectivity
        word_synapses_ca3_recurrent = []
        n_connections = int(self.ca3_size * self.ca3_size * 0.2)
        for _ in range(n_connections):
            pre_idx = np.random.randint(0, len(ca3_neurons_word))
            post_idx = np.random.randint(0, len(ca3_neurons_word))
            if pre_idx != post_idx:
                syn = STDPSynapse(
                    ca3_neurons_word[pre_idx], 
                    ca3_neurons_word[post_idx], 
                    delay_ms=3.0, 
                    Q_max=30.0
                )
                word_synapses_ca3_recurrent.append(syn)
                self.ca3_recurrent_synapses.append(syn)
        
        # Create synapses CA3 → CA1 (sampled)
        word_synapses_ca3_ca1 = []
        n_ca3_to_ca1 = max(3, int(self.ca3_size * 0.3))
        sampled_ca3 = np.random.choice(ca3_neurons_word, n_ca3_to_ca1, replace=False)
        for ca3_n in sampled_ca3:
            syn = STDPSynapse(ca3_n, ca1_time, delay_ms=2.0, Q_max=50.0)
            word_synapses_ca3_ca1.append(syn)
            self.ca3_to_ca1_synapses.append(syn)
        
        # Store word info
        self.words[word_id] = {
            'dg': [dg_idx, dg_idx + 1],
            'ca3': list(range(ca3_idx, ca3_idx + self.ca3_size)),
            'ca1': ca1_idx,
            'sub': sub_idx,
            'synapses_dg_ca3': word_synapses_dg_ca3,
            'synapses_ca3_recurrent': word_synapses_ca3_recurrent,
            'synapses_ca3_ca1': word_synapses_ca3_ca1
        }
        
        # Store context
        if context:
            self.contexts[word_id] = context
            sub_gate.learn_context_association(context, word_id)
        
        # Run learning simulation
        self._run_learning_trial(word_id)
        
        # Learn as familiar
        self.ca1_novelty.learn_pattern(word_id)
        
        # Initialize frequency
        self.word_frequencies[word_id] = 1
    
    def _strengthen_word(self, word_id):
        """Re-learn existing word"""
        self._run_learning_trial(word_id)
    
    def _run_learning_trial(self, word_id):
        """Run learning trial"""
        word_info = self.words[word_id]
        
        # Get neurons
        dg_neurons = [self.dg_neurons[i] for i in word_info['dg']]
        ca3_neurons = [self.ca3_neurons[i] for i in word_info['ca3']]
        
        # Reset
        for n in dg_neurons + ca3_neurons:
            n.reset()
        
        # Get all synapses
        synapses = (word_info['synapses_dg_ca3'] + 
                   word_info['synapses_ca3_recurrent'] + 
                   word_info['synapses_ca3_ca1'])
        
        for syn in synapses:
            syn.reset()
        
        # Learning simulation
        steps = int(self.T_learn / self.dt)
        for k in range(steps):
            t = k * self.dt
            
            # DG input
            I_dg = 350.0 if 5.0 < t < 15.0 else 0.0
            
            # DG update
            for dg_n in dg_neurons:
                dg_n.step(self.dt, I_dg)
            
            # CA3 update (with recurrence)
            for ca3_n in ca3_neurons:
                # DG input
                I_dg_syn = sum(syn.deliver(t) for syn in word_info['synapses_dg_ca3'] 
                              if syn.post_neuron == ca3_n)
                
                # CA3 recurrent input
                I_ca3_syn = sum(syn.deliver(t) for syn in word_info['synapses_ca3_recurrent']
                               if syn.post_neuron == ca3_n)
                
                spike = ca3_n.step(self.dt, I_dg_syn + I_ca3_syn * 0.5)
                
                # STDP
                if spike:
                    for syn in word_info['synapses_dg_ca3']:
                        if syn.post_neuron == ca3_n:
                            syn.on_post_spike(t)
                    for syn in word_info['synapses_ca3_recurrent']:
                        if syn.post_neuron == ca3_n:
                            syn.on_post_spike(t)
            
            # Trigger pre-spikes
            for syn in word_info['synapses_dg_ca3']:
                if syn.pre_neuron.spike_flag:
                    syn.on_pre_spike(t)
            for syn in word_info['synapses_ca3_recurrent']:
                if syn.pre_neuron.spike_flag:
                    syn.on_pre_spike(t)
    
    def sleep(self, cycles=15, use_dynamic=True, verbose=True):
        """
        Sleep consolidation - strengthen important memories
        
        🌊 v2.0: 동역학적 수면 시스템 사용
        
        Args:
            cycles: Number of consolidation cycles (default: 15)
            use_dynamic: 동역학적 수면 사용 여부 (default: True)
            verbose: 진행 상황 출력
        
        동역학적 수면 특징:
            - 노이즈 기반 자발적 replay
            - STP/PTP 반영 consolidation
            - 수면 단계별 차등 노이즈 (SWS > REM > Light)
        
        영속성 효과:
            - 반복 consolidate → consolidation_level 증가
            - 중요한 기억 → 더 자주 replay → 더 공고화
            - 공고화된 기억 → decay에 강함
        """
        if not self.words:
            return {'status': 'no_memories', 'replays': 0}
        
        # =================================================================
        # 🌊 동역학적 수면 (NEW)
        # =================================================================
        if use_dynamic:
            manager = SleepManager(self)
            result = manager.sleep(cycles=cycles, verbose=verbose)
            return result
        
        # =================================================================
        # 기존 수면 (fallback)
        # =================================================================
        word_ids = list(self.words.keys())
        frequencies = [self.word_frequencies.get(w, 1) for w in word_ids]
        total_freq = sum(frequencies)
        probabilities = [f / total_freq for f in frequencies]
        
        for cycle in range(cycles):
            selected_word = np.random.choice(word_ids, p=probabilities)
            word_info = self.words[selected_word]
            
            # Get neurons
            dg_neurons = [self.dg_neurons[i] for i in word_info['dg']]
            ca3_neurons = [self.ca3_neurons[i] for i in word_info['ca3']]
            
            # Reset
            for n in dg_neurons + ca3_neurons:
                n.reset()
            
            # Get synapses
            synapses = (word_info['synapses_dg_ca3'] + 
                       word_info['synapses_ca3_recurrent'])
            
            for syn in synapses:
                syn.reset()
            
            # Weak replay
            steps = int(self.T_learn / self.dt)
            for k in range(steps):
                t = k * self.dt
                I_dg = 150.0 if 5.0 < t < 15.0 else 0.0
                
                for dg_n in dg_neurons:
                    dg_n.step(self.dt, I_dg)
                
                for ca3_n in ca3_neurons:
                    I_syn = sum(syn.deliver(t) for syn in word_info['synapses_dg_ca3'] 
                               if syn.post_neuron == ca3_n)
                    I_rec = sum(syn.deliver(t) for syn in word_info['synapses_ca3_recurrent']
                               if syn.post_neuron == ca3_n)
                    ca3_n.step(self.dt, I_syn + I_rec * 0.3)
                
                for syn in synapses:
                    if syn.pre_neuron.spike_flag:
                        syn.on_pre_spike(t)
            
            # Consolidate (이제 영속성도 증가함!)
            for syn in word_info['synapses_dg_ca3']:
                syn.consolidate(factor=0.03)
            for syn in word_info['synapses_ca3_recurrent']:
                syn.consolidate(factor=0.02)
        
        return {'status': 'completed', 'cycles': cycles, 'replays': cycles}
    
    def decay(self, rate=0.01):
        """
        시간에 따른 기억 감쇠 (중요도 기반 보호)
        
        Args:
            rate: 기본 감쇠율 (0.01 = 1%)
        
        🧠 인간 기억의 원리:
            - 7살 때 크리스마스 → 감정적으로 중요 → 43살에도 기억
            - 어제 점심 → 별로 중요하지 않음 → 빨리 흐릿해짐
            - 반복 회상한 기억 → 더 공고화 → 더 오래 유지
        
        시스템:
            1. MemoryRank로 중요도 계산 (PageRank)
            2. 중요한 기억 = 느리게 감쇠
            3. 공고화된 기억 = 더 느리게 감쇠  
            4. 최소 floor 보장 = 완전히 잊지 않음
        """
        if not self.words:
            return
        
        # MemoryRank로 중요도 계산
        importance_scores = self.memory_ranker.calculate()
        
        for word_id, word_info in self.words.items():
            # 이 기억의 중요도
            importance = importance_scores.get(word_id, 0.5)
            
            # 모든 시냅스에 decay 적용
            for syn in word_info['synapses_dg_ca3']:
                syn.decay(rate=rate, importance=importance)
            
            for syn in word_info['synapses_ca3_recurrent']:
                syn.decay(rate=rate, importance=importance)
            
            for syn in word_info['synapses_ca3_ca1']:
                syn.decay(rate=rate, importance=importance)
        
        # MemoryRank 캐시 초기화 (다음 계산 시 새로 계산)
        self.memory_ranker.clear_cache()
    
    def get_memory_persistence(self, word):
        """
        특정 기억의 영속성 정보 조회
        
        Returns:
            Dict with:
            - weight: 현재 가중치
            - importance: MemoryRank 중요도
            - consolidation_level: 공고화 수준
            - estimated_floor: 예상 최소 가중치
            - persistence_score: 종합 영속성 점수
        """
        word_id = create_word_id(word)
        
        if word_id not in self.words:
            return None
        
        word_info = self.words[word_id]
        importance = self.memory_ranker.get_score(word_id, default=0.5)
        
        # 시냅스들의 평균값
        synapses = word_info['synapses_dg_ca3']
        if not synapses:
            return None
        
        avg_weight = np.mean([syn.get_weight() for syn in synapses])
        avg_consolidation = np.mean([syn.consolidation_level for syn in synapses])
        avg_peak = np.mean([syn.peak_weight for syn in synapses])
        avg_replay = np.mean([syn.replay_count for syn in synapses])
        
        # Floor 계산
        floor = 0.1 + importance * 0.4 + avg_consolidation * 0.3 + avg_peak * 0.05
        
        # 종합 영속성 점수 (0~1)
        persistence_score = min(1.0,
            importance * 0.3 +
            avg_consolidation * 0.4 +
            min(0.3, avg_weight / 10.0))
        
        return {
            'word': word,
            'word_id': word_id,
            'weight': avg_weight,
            'importance': importance,
            'consolidation_level': avg_consolidation,
            'peak_weight': avg_peak,
            'replay_count': avg_replay,
            'estimated_floor': floor,
            'persistence_score': persistence_score,
            'will_persist': persistence_score > 0.5  # 영구적으로 유지될 것인가?
        }
    
    def recall(self, cue, top_n=1):
        """
        Recall memories matching the cue
        
        Args:
            cue: Query string
            top_n: Number of results (default: 1)
        
        Returns:
            Single word (if top_n=1) or list of (word, score) tuples
        """
        if not self.words:
            return None if top_n == 1 else []
        
        # Basic scoring: similarity × synapse strength
        # 🍪 v1.0: 문자열을 벡터로 변환
        cue_vector = text_to_vector(cue)
        
        scores = {}
        for word_id in self.words.keys():
            word_vector = text_to_vector(word_id)
            similarity = compute_similarity(cue_vector, word_vector)
            if similarity > 0:
                word_info = self.words[word_id]
                avg_weight = np.mean([syn.get_weight() for syn in word_info['synapses_dg_ca3']])
                scores[word_id] = similarity * avg_weight
        
        if not scores:
            return None if top_n == 1 else []
        
        # Apply MemoryRank boost (PageRank)
        try:
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            sorted_results = apply_memory_rank(self, sorted_results, boost_factor=1.5)
        except:
            # Fallback to basic sorting
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 🍪 v1.0: word_id 대신 원본 단어 텍스트 반환
        if top_n == 1:
            word_id = sorted_results[0][0]
            return self.word_texts.get(word_id, word_id)  # 원본 텍스트 또는 word_id
        else:
            # (word_text, score) 튜플 리스트 반환
            return [(self.word_texts.get(word_id, word_id), score) 
                    for word_id, score in sorted_results[:top_n]]
    
    def novelty(self, word):
        """Check if word is novel (0=familiar, 1=novel)"""
        word_id = create_word_id(word)
        return self.ca1_novelty.compute_novelty(word_id)
    
    def get_memory_rank(self, word):
        """
        Get PageRank importance score for a memory
        
        Args:
            word: Word to check
            
        Returns:
            Importance score (0.0 ~ 1.0)
        """
        word_id = create_word_id(word)
        return self.memory_ranker.get_score(word_id, default=0.5)
    
    def get_top_memories(self, n=10):
        """
        Get top N most important memories by PageRank
        
        Args:
            n: Number of memories to return
            
        Returns:
            List of (word_id, importance_score) tuples
        """
        return self.memory_ranker.get_top_memories(n)
    
    def save(self, path):
        """Save memory to file (including persistence info)"""
        data = {
            'version': self.version,
            'capacity': self.capacity,
            'words': list(self.words.keys()),
            'contexts': self.contexts,
            'frequencies': self.word_frequencies,
            'weights': {},
            'persistence': {}  # 영속성 정보 추가
        }
        
        for word_id, word_info in self.words.items():
            weights = {
                'dg_ca3': [syn.get_weight() for syn in word_info['synapses_dg_ca3']],
                'ca3_recurrent': [syn.get_weight() for syn in word_info['synapses_ca3_recurrent']],
                'ca3_ca1': [syn.get_weight() for syn in word_info['synapses_ca3_ca1']]
            }
            data['weights'][word_id] = weights
            
            # 영속성 정보 저장
            persistence = {
                'dg_ca3': [{
                    'consolidation_level': syn.consolidation_level,
                    'peak_weight': syn.peak_weight,
                    'replay_count': syn.replay_count
                } for syn in word_info['synapses_dg_ca3']],
                'ca3_recurrent': [{
                    'consolidation_level': syn.consolidation_level,
                    'peak_weight': syn.peak_weight,
                    'replay_count': syn.replay_count
                } for syn in word_info['synapses_ca3_recurrent']],
                'ca3_ca1': [{
                    'consolidation_level': syn.consolidation_level,
                    'peak_weight': syn.peak_weight,
                    'replay_count': syn.replay_count
                } for syn in word_info['synapses_ca3_ca1']]
            }
            data['persistence'][word_id] = persistence
        
        save_memory(data, path)
    
    def load(self, path):
        """Load memory from file (including persistence info)"""
        data = load_memory(path)
        
        # Clear
        self.__init__(capacity=data.get('capacity', 1000))
        
        # Restore words
        for word_id in data['words']:
            context = data['contexts'].get(word_id)
            self.learn(word_id, context=context)
            
            if 'frequencies' in data and word_id in data['frequencies']:
                self.word_frequencies[word_id] = data['frequencies'][word_id]
            
            if word_id in data['weights']:
                word_info = self.words[word_id]
                weights = data['weights'][word_id]
                
                for i, syn in enumerate(word_info['synapses_dg_ca3']):
                    if i < len(weights['dg_ca3']):
                        syn.weight = weights['dg_ca3'][i]
                
                for i, syn in enumerate(word_info['synapses_ca3_recurrent']):
                    if i < len(weights.get('ca3_recurrent', [])):
                        syn.weight = weights['ca3_recurrent'][i]
                
                for i, syn in enumerate(word_info['synapses_ca3_ca1']):
                    if i < len(weights['ca3_ca1']):
                        syn.weight = weights['ca3_ca1'][i]
            
            # 영속성 정보 복원
            if 'persistence' in data and word_id in data['persistence']:
                word_info = self.words[word_id]
                persistence = data['persistence'][word_id]
                
                for i, syn in enumerate(word_info['synapses_dg_ca3']):
                    if i < len(persistence.get('dg_ca3', [])):
                        p = persistence['dg_ca3'][i]
                        syn.consolidation_level = p.get('consolidation_level', 0.0)
                        syn.peak_weight = p.get('peak_weight', syn.weight)
                        syn.replay_count = p.get('replay_count', 0)
                
                for i, syn in enumerate(word_info['synapses_ca3_recurrent']):
                    if i < len(persistence.get('ca3_recurrent', [])):
                        p = persistence['ca3_recurrent'][i]
                        syn.consolidation_level = p.get('consolidation_level', 0.0)
                        syn.peak_weight = p.get('peak_weight', syn.weight)
                        syn.replay_count = p.get('replay_count', 0)
                
                for i, syn in enumerate(word_info['synapses_ca3_ca1']):
                    if i < len(persistence.get('ca3_ca1', [])):
                        p = persistence['ca3_ca1'][i]
                        syn.consolidation_level = p.get('consolidation_level', 0.0)
                        syn.peak_weight = p.get('peak_weight', syn.weight)
                        syn.replay_count = p.get('replay_count', 0)
    
    def __repr__(self):
        return f"babyHippo v{self.version} ({len(self.words)}/{self.capacity} words)"
    
    def get_stats(self):
        """Get memory statistics (including persistence info)"""
        if not self.words:
            return {
                'words': 0,
                'capacity': self.capacity,
                'neurons': 0,
                'synapses': 0,
                'avg_weight': 0.0,
                'memory_mb': 0.0,
                'avg_consolidation': 0.0,
                'persistent_memories': 0
            }
        
        all_weights = []
        all_consolidation = []
        persistent_count = 0
        
        for word_info in self.words.values():
            for syn in word_info['synapses_dg_ca3']:
                all_weights.append(syn.get_weight())
                all_consolidation.append(syn.consolidation_level)
            
            # 영구 기억 카운트 (consolidation > 0.5)
            avg_cons = np.mean([syn.consolidation_level for syn in word_info['synapses_dg_ca3']])
            if avg_cons > 0.5:
                persistent_count += 1
        
        # Estimate memory usage
        n_neurons = len(self.dg_neurons) + len(self.ca3_neurons) + len(self.ca1_time_cells)
        n_synapses = (len(self.dg_to_ca3_synapses) + 
                     len(self.ca3_recurrent_synapses) + 
                     len(self.ca3_to_ca1_synapses))
        memory_mb = (n_neurons * 0.0002 + n_synapses * 0.0001)
        
        return {
            'words': len(self.words),
            'capacity': self.capacity,
            'neurons': n_neurons,
            'synapses': n_synapses,
            'avg_weight': np.mean(all_weights) if all_weights else 0.0,
            'memory_mb': memory_mb,
            # 영속성 관련 통계
            'avg_consolidation': np.mean(all_consolidation) if all_consolidation else 0.0,
            'persistent_memories': persistent_count,  # 영구 기억 수
            'persistence_ratio': persistent_count / max(1, len(self.words))  # 영구화 비율
        }


# Quick test
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 babyHippo Test")
    print("=" * 60)
    
    # Create memory
    hippo = HippoMemory()
    
    # Learn
    print("\n📝 Learning...")
    hippo.learn("cat", context="animal")
    hippo.learn("dog", context="animal")
    hippo.learn("car", context="vehicle")
    
    # Sleep
    print("💤 Consolidating...")
    hippo.sleep(cycles=10)
    
    # Recall
    print("\n🔍 Recall:")
    print(f"  'ca' → {hippo.recall('ca')}")
    
    # Stats
    print("\n📊 Stats:")
    stats = hippo.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)

