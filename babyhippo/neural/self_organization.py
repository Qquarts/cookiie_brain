"""
=============================================================================
Self-Organization Module: 자기조직화 시스템
=============================================================================

🌊 철학:
    "하드코딩은 죽음이다"
    "패턴은 지정하는 것이 아니라 발견하는 것이다"
    "클러스터는 스스로 형성된다"

📐 핵심 원리:
    1. 경쟁적 학습 (Competitive Learning)
       - 입력에 가장 잘 반응하는 뉴런이 승리
       - 승리한 뉴런이 입력 패턴을 더 잘 표현하도록 학습
       
    2. 측면 억제 (Lateral Inhibition)
       - 승리한 뉴런 주변의 뉴런들은 억제
       - 희소 표현 (Sparse Coding) 형성
       
    3. 헤비안 학습 (Hebbian Learning)
       - "함께 발화하는 뉴런은 함께 연결된다"
       - 자연스럽게 패턴 클러스터 형성
       
    4. 노이즈 기반 탐색 (Noise-Driven Exploration)
       - 노이즈가 새로운 패턴 발견을 촉진
       - 고착(local minimum) 탈출

생물학적 근거:
    - 시각 피질의 방향 선택성 (Orientation Selectivity)
    - 해마의 장소 세포 (Place Cells)
    - 소뇌의 운동 패턴 학습

물리학적 근거:
    - 열역학적 평형으로의 수렴
    - 에너지 최소화 원리
    - 자발적 대칭 깨짐

Author: GNJz (Qquarts)
Version: 1.0.0
=============================================================================
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class Pattern:
    """
    학습된 패턴 (자기조직화로 발견됨)
    
    Attributes:
        id: 패턴 고유 ID
        vector: 패턴 벡터 (프로토타입)
        activation_count: 활성화 횟수
        last_activation: 마지막 활성화 시간
        associated_labels: 연관된 레이블들
        strength: 패턴 강도 (반복으로 증가)
    """
    id: str
    vector: np.ndarray
    activation_count: int = 0
    last_activation: float = 0.0
    associated_labels: List[str] = field(default_factory=list)
    strength: float = 1.0
    
    def __post_init__(self):
        if isinstance(self.vector, list):
            self.vector = np.array(self.vector)


class CompetitiveLearning:
    """
    경쟁적 학습 네트워크
    
    📐 원리:
        1. 입력이 들어오면 모든 뉴런과 유사도 계산
        2. 가장 유사한 뉴런(승자)이 입력을 학습
        3. 주변 뉴런은 억제 (WTA)
        
    📐 수식:
        유사도: sim(x, w) = x · w / (|x| |w|)
        학습: w ← w + η(x - w)  (승자만)
    
    생물학적 의미:
        - 특정 자극에 선택적으로 반응하는 뉴런 형성
        - 시각 피질의 방향 선택성과 유사
    """
    
    def __init__(self, 
                 n_neurons: int = 100,
                 input_dim: int = 128,
                 learning_rate: float = 0.1):
        """
        Args:
            n_neurons: 뉴런 수
            input_dim: 입력 차원
            learning_rate: 학습률
        """
        self.n_neurons = n_neurons
        self.input_dim = input_dim
        self.lr = learning_rate
        
        # 가중치 행렬 (무작위 초기화 - 노이즈가 다양성의 씨앗)
        self.weights = np.random.randn(n_neurons, input_dim)
        self._normalize_weights()
        
        # 활성화 기록
        self.activations = np.zeros(n_neurons)
        
        # 학습 통계
        self.stats = {
            'total_inputs': 0,
            'winner_history': [],
        }
        
    def _normalize_weights(self):
        """가중치 정규화"""
        norms = np.linalg.norm(self.weights, axis=1, keepdims=True)
        self.weights = self.weights / (norms + 1e-8)
    
    def forward(self, x: np.ndarray) -> Tuple[int, float]:
        """
        순전파 - 승자 선택
        
        📐 수식:
            sim_i = x · w_i / (|x| |w_i|)
            winner = argmax(sim)
        
        Args:
            x: 입력 벡터
            
        Returns:
            (winner_idx, similarity): 승자 인덱스와 유사도
        """
        x = np.array(x).flatten()
        if len(x) != self.input_dim:
            raise ValueError(f"입력 차원 불일치: {len(x)} != {self.input_dim}")
        
        # 정규화
        x_norm = x / (np.linalg.norm(x) + 1e-8)
        
        # 유사도 계산 (코사인 유사도)
        similarities = self.weights @ x_norm
        
        # 승자 선택
        winner = np.argmax(similarities)
        similarity = similarities[winner]
        
        # 활성화 기록
        self.activations[winner] += 1
        self.stats['total_inputs'] += 1
        self.stats['winner_history'].append(winner)
        
        return int(winner), float(similarity)
    
    def learn(self, x: np.ndarray, winner: Optional[int] = None) -> int:
        """
        학습 - 승자가 입력을 향해 이동
        
        📐 수식:
            w_winner ← w_winner + η(x - w_winner)
        
        Args:
            x: 입력 벡터
            winner: 승자 인덱스 (None이면 자동 선택)
            
        Returns:
            winner_idx: 승자 인덱스
        """
        x = np.array(x).flatten()
        x_norm = x / (np.linalg.norm(x) + 1e-8)
        
        # 승자 선택
        if winner is None:
            winner, _ = self.forward(x)
        
        # 학습: w ← w + η(x - w)
        self.weights[winner] += self.lr * (x_norm - self.weights[winner])
        
        # 정규화
        self.weights[winner] /= np.linalg.norm(self.weights[winner]) + 1e-8
        
        return winner
    
    def get_most_activated(self, top_k: int = 5) -> List[Tuple[int, int]]:
        """가장 많이 활성화된 뉴런들"""
        indices = np.argsort(self.activations)[::-1][:top_k]
        return [(int(i), int(self.activations[i])) for i in indices]


class HebbianCluster:
    """
    헤비안 클러스터링
    
    📐 원리:
        "함께 발화하는 뉴런은 함께 연결된다"
        (Neurons that fire together wire together)
        
    📐 수식:
        Δw_ij = η · x_i · x_j  (동시 활성화)
        
    생물학적 의미:
        - 자연스러운 패턴 그룹화
        - 연관 기억 형성
    """
    
    def __init__(self, n_neurons: int = 100, 
                 learning_rate: float = 0.01,
                 decay_rate: float = 0.001):
        """
        Args:
            n_neurons: 뉴런 수
            learning_rate: 학습률
            decay_rate: 감쇠율
        """
        self.n_neurons = n_neurons
        self.lr = learning_rate
        self.decay = decay_rate
        
        # 연결 가중치 행렬 (대칭)
        self.connections = np.zeros((n_neurons, n_neurons))
        
        # 활성화 기록
        self.active_history = []
        
    def activate(self, neurons: List[int]):
        """
        뉴런 집합 활성화 (동시 발화)
        
        📐 수식:
            모든 (i, j) 쌍에 대해:
            w_ij ← w_ij + η  (i, j ∈ active_neurons)
        """
        self.active_history.append(set(neurons))
        
        # 헤비안 학습: 동시 활성화된 뉴런 간 연결 강화
        for i in neurons:
            for j in neurons:
                if i != j:
                    self.connections[i, j] += self.lr
                    
    def decay_connections(self):
        """연결 감쇠"""
        self.connections *= (1 - self.decay)
        
    def get_clusters(self, threshold: float = 0.5) -> List[List[int]]:
        """
        클러스터 추출 (강하게 연결된 그룹)
        
        Returns:
            클러스터 리스트 (각 클러스터는 뉴런 인덱스 리스트)
        """
        # 연결이 threshold 이상인 것만 고려
        strong = self.connections > threshold
        
        # Union-Find로 클러스터 찾기
        visited = set()
        clusters = []
        
        for i in range(self.n_neurons):
            if i in visited:
                continue
            
            # BFS로 연결된 뉴런 찾기
            cluster = []
            queue = [i]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                cluster.append(node)
                
                # 강하게 연결된 이웃 추가
                for j in range(self.n_neurons):
                    if strong[node, j] and j not in visited:
                        queue.append(j)
            
            if len(cluster) > 1:  # 단일 뉴런은 클러스터 아님
                clusters.append(sorted(cluster))
        
        return clusters


class PatternMemory:
    """
    자기조직화 패턴 메모리
    
    📐 원리:
        1. 새로운 패턴이 들어오면 기존 패턴과 비교
        2. 유사한 패턴이 있으면 병합 (일반화)
        3. 새로운 패턴이면 저장 (분화)
        4. 오래 사용 안 된 패턴은 약화 (망각)
        
    🌊 철학:
        - 하드코딩된 패턴 대신 학습된 패턴 사용
        - 패턴은 발견되는 것이지 지정되는 것이 아님
    """
    
    def __init__(self, 
                 pattern_dim: int = 128,
                 similarity_threshold: float = 0.8,
                 max_patterns: int = 1000):
        """
        Args:
            pattern_dim: 패턴 차원
            similarity_threshold: 병합 임계값
            max_patterns: 최대 패턴 수
        """
        self.pattern_dim = pattern_dim
        self.threshold = similarity_threshold
        self.max_patterns = max_patterns
        
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_count = 0
        
    def _generate_id(self) -> str:
        """고유 ID 생성"""
        self.pattern_count += 1
        return f"P{self.pattern_count:04d}"
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """코사인 유사도"""
        a = np.array(a).flatten()
        b = np.array(b).flatten()
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-8 or norm_b < 1e-8:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def find_similar(self, vector: np.ndarray) -> Optional[Pattern]:
        """
        가장 유사한 패턴 찾기
        
        Args:
            vector: 입력 벡터
            
        Returns:
            가장 유사한 패턴 (임계값 이상일 때만)
        """
        best_pattern = None
        best_similarity = 0.0
        
        for pattern in self.patterns.values():
            sim = self._cosine_similarity(vector, pattern.vector)
            if sim > best_similarity and sim >= self.threshold:
                best_similarity = sim
                best_pattern = pattern
        
        return best_pattern
    
    def learn(self, vector: np.ndarray, label: Optional[str] = None) -> Pattern:
        """
        패턴 학습 (자기조직화)
        
        📐 규칙:
            1. 유사한 패턴 있음 → 병합 (프로토타입 업데이트)
            2. 유사한 패턴 없음 → 새 패턴 생성
        
        Args:
            vector: 입력 벡터
            label: 레이블 (선택)
            
        Returns:
            학습된/병합된 패턴
        """
        vector = np.array(vector).flatten()
        now = time.time()
        
        # 유사한 패턴 찾기
        similar = self.find_similar(vector)
        
        if similar:
            # 병합: 프로토타입 업데이트 (이동 평균)
            alpha = 0.1  # 학습률
            similar.vector = (1 - alpha) * similar.vector + alpha * vector
            similar.activation_count += 1
            similar.last_activation = now
            similar.strength = min(10.0, similar.strength + 0.1)
            
            if label and label not in similar.associated_labels:
                similar.associated_labels.append(label)
            
            return similar
        else:
            # 새 패턴 생성
            pattern_id = self._generate_id()
            pattern = Pattern(
                id=pattern_id,
                vector=vector.copy(),
                activation_count=1,
                last_activation=now,
                associated_labels=[label] if label else [],
                strength=1.0
            )
            self.patterns[pattern_id] = pattern
            
            # 최대 패턴 수 초과 시 가장 약한 패턴 제거
            if len(self.patterns) > self.max_patterns:
                self._prune_weakest()
            
            return pattern
    
    def _prune_weakest(self):
        """가장 약한 패턴 제거"""
        if not self.patterns:
            return
        
        weakest_id = min(self.patterns.keys(), 
                        key=lambda k: self.patterns[k].strength)
        del self.patterns[weakest_id]
    
    def decay(self, rate: float = 0.01):
        """패턴 강도 감쇠"""
        for pattern in self.patterns.values():
            pattern.strength = max(0.1, pattern.strength - rate)
    
    def get_strongest(self, top_k: int = 10) -> List[Pattern]:
        """가장 강한 패턴들"""
        sorted_patterns = sorted(self.patterns.values(), 
                                 key=lambda p: p.strength, 
                                 reverse=True)
        return sorted_patterns[:top_k]
    
    def get_stats(self) -> Dict[str, Any]:
        """통계"""
        return {
            'total_patterns': len(self.patterns),
            'avg_strength': np.mean([p.strength for p in self.patterns.values()]) if self.patterns else 0,
            'avg_activations': np.mean([p.activation_count for p in self.patterns.values()]) if self.patterns else 0,
        }


# =============================================================================
# 유틸리티 함수
# =============================================================================

def text_to_vector(text: str, dim: int = 128) -> np.ndarray:
    """
    텍스트를 벡터로 변환 (간단한 해시 기반)
    
    Note: 실제로는 Word2Vec, BERT 등 사용 권장
    """
    import hashlib
    
    if not text:
        return np.zeros(dim)
    
    # 해시 기반 시드 생성
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    np.random.seed(seed)
    
    # 랜덤 벡터 생성 및 정규화
    vec = np.random.randn(dim)
    return vec / (np.linalg.norm(vec) + 1e-8)


# =============================================================================
# 테스트
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌊 Self-Organization Test")
    print("=" * 60)
    
    # 1. 경쟁적 학습
    print("\n1️⃣ Competitive Learning...")
    cl = CompetitiveLearning(n_neurons=10, input_dim=8)
    
    # 몇 가지 패턴 학습
    patterns = [
        np.array([1, 1, 0, 0, 0, 0, 0, 0]),
        np.array([0, 0, 1, 1, 0, 0, 0, 0]),
        np.array([0, 0, 0, 0, 1, 1, 0, 0]),
    ]
    
    for _ in range(50):
        for p in patterns:
            cl.learn(p + np.random.randn(8) * 0.1)  # 노이즈 추가
    
    print(f"   가장 활성화된 뉴런: {cl.get_most_activated(3)}")
    
    # 2. 헤비안 클러스터
    print("\n2️⃣ Hebbian Clustering...")
    hc = HebbianCluster(n_neurons=10)
    
    # 동시 활성화 패턴
    for _ in range(20):
        hc.activate([0, 1, 2])  # 클러스터 1
        hc.activate([5, 6, 7])  # 클러스터 2
    
    clusters = hc.get_clusters(threshold=0.1)
    print(f"   발견된 클러스터: {clusters}")
    
    # 3. 패턴 메모리
    print("\n3️⃣ Pattern Memory...")
    pm = PatternMemory(pattern_dim=8)
    
    # 패턴 학습
    for i in range(10):
        vec = patterns[i % 3] + np.random.randn(8) * 0.1
        pm.learn(vec, label=f"pattern_{i % 3}")
    
    print(f"   저장된 패턴 수: {pm.get_stats()['total_patterns']}")
    print(f"   가장 강한 패턴: {pm.get_strongest(2)}")
    
    print("\n" + "=" * 60)
    print("✅ 자기조직화 테스트 완료!")
    print("=" * 60)

