"""
BrainGraph: 전체 뇌 그래프 시스템
Brain Graph v0.4.1

v0.4 주요 변경사항:
- 인접 리스트: activate() O(n) → O(k) 최적화
- 중복 저장 방지: allow_duplicate 옵션
- Consolidation 최적화: O(m²) → O(k)
- 감정 분석 개선: dominant_emotion + 가중 평균
- 년도 패턴 수정: 전체 년도 추출

v0.3 기능 유지:
- Soft Activation: sigmoid 기반 활성화 (saturation 방지)
- Feature 추출 고도화: Entity/Concept/Relation, Circumplex 감정 모델

v0.2 기능 유지:
- Global Graph: 피질 간 연결 (Cross-Cortex Connections)
- Spreading Activation: 전체 뇌로 확장
- Sleep Replay: 실제 뇌처럼 activate → spread → reinforce
- 점진적 Pruning: 연결 감쇠 개선

실제 뇌처럼 기억을 분산 저장하고 그래프 검색으로 회상합니다:
- 해마 (HippoMemory): 인덱스 + PageRank
- 피질 (CortexNodes): 분산 저장 + 인접 리스트
- 전전두엽 (PrefrontalCortex): 검색 조율
- Global Graph: 피질 간 연결망

사용법:
    brain = BrainGraph()
    brain.store("고양이는 귀여운 동물이야")
    result = brain.recall("고양이")
    brain.sleep()  # 수면 공고화 (replay 포함)
"""

import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, deque

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from ..memory import HippoMemory
from ..cortex import (
    CortexNode,
    VisualCortex,
    AuditoryCortex,
    EmotionalCortex,
    SemanticCortex,
    EpisodicCortex,
)
from ._5_prefrontal import PrefrontalCortex


class BrainGraph:
    """
    전체 뇌 그래프 시스템 v0.4
    
    v0.2 핵심 개선:
    1. Global Graph - 피질 간 연결 (semantic ↔ visual ↔ emotional)
    2. Spreading Activation - 전체 뇌로 확장
    3. Sleep Replay - activate → spread → reinforce
    4. 점진적 Pruning
    
    생물학적 배경:
    - 기억은 뇌 전체에 분산 저장됨
    - 해마는 인덱스 역할 (어디에 무엇이 있는지)
    - 피질은 실제 내용 저장 (시각, 청각, 감정 등)
    - 피질 간 연결이 기억의 연합을 형성
    - 수면 중 replay가 기억을 공고화
    """
    
    VERSION = "0.4.1"
    
    def __init__(self, capacity: int = 10000, dna_traits: Optional[Dict] = None):
        """
        BrainGraph 초기화
        
        Args:
            capacity: 각 영역의 최대 용량
            dna_traits: DNA 특성 (기억력 조절)
                        예: {'drive_weights': {'curiosity': 2.0}}
        
        Note:
            v0.4.1: DNA 연동 지원 (Stem Code 철학)
            - 호기심 높으면 → 기억 용량↑
            - 호기심 낮으면 → 기본 용량
        """
        # [v0.4.1] DNA에 따른 기억 용량 보정
        final_capacity = capacity
        if dna_traits:
            curiosity = dna_traits.get('drive_weights', {}).get('curiosity', 1.0)
            if curiosity > 1.5:
                final_capacity = int(capacity * 1.5)  # 학자형: 50% 증가
            elif curiosity < 0.8:
                final_capacity = int(capacity * 0.8)  # 활동형: 20% 감소
        
        self.capacity = final_capacity
        
        # 해마: 인덱스 + PageRank (기존 babyHippo)
        self.hippocampus = HippoMemory(capacity=capacity)
        
        # 피질 영역들: 분산 저장
        self.cortex = {
            'visual': VisualCortex(capacity=capacity),
            'auditory': AuditoryCortex(capacity=capacity),
            'emotional': EmotionalCortex(capacity=capacity),
            'semantic': SemanticCortex(capacity=capacity),
            'episodic': EpisodicCortex(capacity=capacity),
        }
        
        # 전전두엽: 검색 조율
        self.prefrontal = PrefrontalCortex(working_memory_size=7)
        
        # ===== v0.2 NEW: Global Graph (피질 간 연결) =====
        if HAS_NETWORKX:
            self.global_graph = nx.DiGraph()
        else:
            self.global_graph = None
        
        # Cross-cortex 연결: (cortex_type, fragment_id) → (cortex_type, fragment_id) → weight
        self.cross_cortex_edges: Dict[Tuple[Tuple[str, str], Tuple[str, str]], float] = {}
        
        # Fragment → Cortex 매핑 (역방향 조회용)
        self.fragment_to_cortex: Dict[str, str] = {}
        
        # 기억 메타데이터
        self.memory_metadata: Dict[str, Dict] = {}
        
        # 통계
        self.total_stores = 0
        self.total_recalls = 0
        self.total_replays = 0
        self.last_sleep = time.time()
    
    def store(self, content: str, context: str = "", importance: float = 0.5) -> str:
        """
        기억 저장 (분산)
        
        Args:
            content: 저장할 내용
            context: 컨텍스트 (대화 상황 등)
            importance: 중요도 (0.0 ~ 1.0)
        
        Returns:
            memory_id: 생성된 기억 ID
        """
        # 1. 고유 ID 생성
        memory_id = self._generate_memory_id(content)
        
        # 2. 해마에 인덱스 생성 (키워드 추출 + 학습)
        keywords = self._extract_keywords(content)
        hippo_indices = []
        
        for keyword in keywords:
            try:
                self.hippocampus.learn(keyword)
                hippo_indices.append(keyword)
            except Exception:
                continue
        
        # 3. 기억 조각화
        fragments = self._fragment_memory(content, context)
        
        # 4. 각 피질에 분산 저장
        stored_locations = {}
        for cortex_type, fragment in fragments.items():
            if fragment and cortex_type in self.cortex:
                cortex = self.cortex[cortex_type]
                
                # 각 인덱스와 연결하여 저장
                for index in hippo_indices:
                    frag_id = cortex.store(index, fragment, memory_id=f"{memory_id}_{cortex_type}")
                    stored_locations[cortex_type] = frag_id
                    
                    # v0.2: Fragment → Cortex 매핑 저장
                    self.fragment_to_cortex[frag_id] = cortex_type
                    
                    # v0.2: Global Graph에 노드 추가
                    if self.global_graph is not None:
                        self.global_graph.add_node(frag_id, cortex=cortex_type, memory_id=memory_id)
        
        # 5. 메타데이터 저장
        self.memory_metadata[memory_id] = {
            'content': content,
            'context': context,
            'importance': importance,
            'keywords': keywords,
            'hippo_indices': hippo_indices,
            'cortex_locations': stored_locations,
            'created_at': time.time(),
            'access_count': 0,
        }
        
        # 6. v0.2: 피질 간 연결 생성 (Cross-Cortex Connections)
        self._create_cross_cortex_connections(memory_id, stored_locations)
        
        self.total_stores += 1
        
        return memory_id
    
    def recall(self, query: str, top_n: int = 5) -> List[Dict]:
        """
        기억 회상 (그래프 검색 + Spreading Activation)
        
        Args:
            query: 검색 쿼리
            top_n: 반환할 최대 결과 수
        
        Returns:
            results: 검색된 기억들
        """
        # 1. 전전두엽에서 쿼리 분석
        analysis = self.prefrontal.analyze_query(query)
        
        # 2. 해마에 검색 요청 (PageRank 적용)
        hippo_results = self.prefrontal.query_hippocampus(
            self.hippocampus, query, analysis
        )
        
        if not hippo_results:
            return []
        
        # 3. 검색 계획 수립
        retrieval_plan = self.prefrontal.coordinate_retrieval(
            self.cortex, hippo_results, analysis
        )
        
        # 4. 각 피질에서 조각 수집
        all_fragments = {}
        activated_fragments = []
        
        for cortex_type in retrieval_plan['cortex_order']:
            if cortex_type in self.cortex:
                indices = retrieval_plan['indices_per_cortex'].get(cortex_type, [])
                if indices:
                    cortex = self.cortex[cortex_type]
                    fragments = cortex.retrieve(indices)
                    all_fragments[cortex_type] = fragments
                    
                    # 활성화된 fragment 수집
                    for frag in fragments:
                        frag_id = frag['id']
                        cortex.activate(frag_id, level=0.3)
                        activated_fragments.append((cortex_type, frag_id))
        
        # 5. v0.2: 전체 뇌로 Spreading Activation
        for cortex_type, frag_id in activated_fragments:
            self.spread_activation(frag_id, depth=2, decay=0.5)
        
        # 6. 조각들을 기억으로 재구성
        reconstructed = self._reconstruct_memories(all_fragments, hippo_results)
        
        # 7. 필터링 및 정렬
        filtered = self.prefrontal.filter_results(reconstructed, analysis)
        
        # 8. 접근 기록 업데이트
        for result in filtered[:top_n]:
            mem_id = result.get('memory_id')
            if mem_id and mem_id in self.memory_metadata:
                self.memory_metadata[mem_id]['access_count'] += 1
        
        self.total_recalls += 1
        
        return filtered[:top_n]
    
    # ===== v0.2 NEW: Spreading Activation (전체 뇌) =====
    
    def spread_activation(self, start_id: str, depth: int = 3, decay: float = 0.5):
        """
        전체 뇌 그래프에서 활성화 전파 (Spreading Activation)
        
        v0.2 핵심 기능: 피질 경계를 넘어 활성화 전파
        
        Args:
            start_id: 시작 fragment ID
            depth: 전파 깊이
            decay: 감쇠율 (0.0 ~ 1.0)
        """
        if not self.global_graph or start_id not in self.global_graph:
            return
        
        # BFS로 활성화 전파
        queue = deque([(start_id, 1.0, 0)])  # (node_id, activation, current_depth)
        visited = set()
        
        while queue:
            node_id, activation, current_depth = queue.popleft()
            
            if node_id in visited or current_depth > depth:
                continue
            
            visited.add(node_id)
            
            # 해당 피질에서 활성화
            cortex_type = self.fragment_to_cortex.get(node_id)
            if cortex_type and cortex_type in self.cortex:
                self.cortex[cortex_type].activate(node_id, level=activation)
            
            # 연결된 노드로 전파
            if self.global_graph.has_node(node_id):
                for neighbor in self.global_graph.neighbors(node_id):
                    if neighbor not in visited:
                        edge_weight = self.global_graph[node_id][neighbor].get('weight', 0.5)
                        new_activation = activation * edge_weight * decay
                        
                        if new_activation > 0.01:  # 최소 임계값
                            queue.append((neighbor, new_activation, current_depth + 1))
    
    # ===== v0.2 NEW: Sleep Replay (수면 공고화) =====
    
    def sleep(self, duration: float = 1.0, n_replays: int = 10):
        """
        수면 공고화 - 기억 강화 및 정리
        
        v0.2 핵심 기능: 실제 뇌처럼 replay 수행
        - activate: 중요한 기억 활성화
        - spread: 전체 뇌로 전파
        - reinforce: co-activation된 연결 강화 (Hebbian)
        
        Args:
            duration: 수면 강도 (0.0 ~ 1.0)
            n_replays: replay 횟수
        """
        # 1. 해마 수면 공고화
        self.hippocampus.sleep()
        
        # 2. v0.2: Sleep Replay (activate → spread → reinforce)
        self._sleep_replay(n_replays=n_replays, duration=duration)
        
        # 3. 각 피질 공고화 (감쇠)
        decay_rate = 0.05 * duration
        for cortex in self.cortex.values():
            cortex.consolidate(decay_rate=decay_rate)
        
        # 4. v0.2: 점진적 Pruning (약한 연결 정리)
        self._gradual_pruning(threshold=0.05, decay=0.1)
        
        # 5. 약한 기억 정리 (선택적 망각)
        self._selective_forgetting(threshold=0.1)
        
        self.last_sleep = time.time()
    
    def _sleep_replay(self, n_replays: int = 10, duration: float = 1.0):
        """
        수면 중 기억 재생 (Sleep Replay)
        
        실제 뇌의 Slow-Wave Sleep replay 구조:
        1. 중요한 기억 선택
        2. 기억 활성화 (activate)
        3. 전체 뇌로 전파 (spread)
        4. co-activation된 연결 강화 (reinforce - Hebbian)
        """
        # 1. 중요한 기억 선택
        important_memories = self._get_high_importance_memories(n_replays)
        
        for memory_id in important_memories:
            # 2. Activate: 기억의 모든 조각 활성화
            locations = self.memory_metadata[memory_id].get('cortex_locations', {})
            activated_ids = []
            
            for cortex_type, frag_id in locations.items():
                if cortex_type in self.cortex:
                    self.cortex[cortex_type].activate(frag_id, level=0.8 * duration)
                    activated_ids.append(frag_id)
            
            # 3. Spread: 전체 뇌로 전파
            for frag_id in activated_ids:
                self.spread_activation(frag_id, depth=2, decay=0.6)
            
            # 4. Reinforce: co-activation된 연결 강화 (Hebbian)
            self._hebbian_reinforce(activated_ids, strength=0.1 * duration)
            
            self.total_replays += 1
    
    def _get_high_importance_memories(self, n: int) -> List[str]:
        """중요한 기억 선택 (replay 대상)"""
        scored_memories = []
        
        for mem_id, meta in self.memory_metadata.items():
            # 점수 = 중요도 + 접근 횟수 보너스 + 최근성 보너스
            importance = meta['importance']
            access_bonus = min(0.3, meta['access_count'] * 0.05)
            
            age_hours = (time.time() - meta['created_at']) / 3600
            recency_bonus = max(0, 0.2 - age_hours * 0.01)
            
            score = importance + access_bonus + recency_bonus
            scored_memories.append((mem_id, score))
        
        # 점수 순 정렬
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        return [mem_id for mem_id, _ in scored_memories[:n]]
    
    def _hebbian_reinforce(self, activated_ids: List[str], strength: float = 0.1):
        """
        Hebbian 학습: co-activation된 연결 강화
        "Neurons that fire together, wire together"
        """
        if not self.global_graph:
            return
        
        # 활성화된 노드들 사이의 연결 강화
        for i, id1 in enumerate(activated_ids):
            for id2 in activated_ids[i+1:]:
                if self.global_graph.has_edge(id1, id2):
                    # 기존 연결 강화
                    current_weight = self.global_graph[id1][id2].get('weight', 0.5)
                    new_weight = min(1.0, current_weight + strength)
                    self.global_graph[id1][id2]['weight'] = new_weight
                    
                    # 양방향
                    if self.global_graph.has_edge(id2, id1):
                        self.global_graph[id2][id1]['weight'] = new_weight
    
    # ===== v0.2 NEW: 점진적 Pruning =====
    
    def _gradual_pruning(self, threshold: float = 0.05, decay: float = 0.1):
        """
        점진적 연결 정리 (Pruning)
        
        v0.2 개선: 즉시 삭제 대신 점진적 감쇠
        w_new = w_old * (1 - decay)
        if w_new < threshold: prune
        """
        if not self.global_graph:
            return
        
        edges_to_remove = []
        
        for u, v, data in self.global_graph.edges(data=True):
            weight = data.get('weight', 0.5)
            
            # 감쇠 적용
            new_weight = weight * (1 - decay)
            
            if new_weight < threshold:
                edges_to_remove.append((u, v))
            else:
                self.global_graph[u][v]['weight'] = new_weight
        
        # 약한 연결 제거
        for u, v in edges_to_remove:
            self.global_graph.remove_edge(u, v)
        
        # Cross-cortex edges도 정리
        edges_to_remove = []
        for edge_key, weight in self.cross_cortex_edges.items():
            new_weight = weight * (1 - decay)
            if new_weight < threshold:
                edges_to_remove.append(edge_key)
            else:
                self.cross_cortex_edges[edge_key] = new_weight
        
        for edge_key in edges_to_remove:
            del self.cross_cortex_edges[edge_key]
    
    # ===== v0.2 IMPROVED: Cross-Cortex Connections =====
    
    def _create_cross_cortex_connections(self, memory_id: str, locations: Dict[str, str]):
        """
        피질 간 연결 생성 (Cross-Cortex Connections)
        
        v0.2 개선: 실제 피질 간 연결 생성
        semantic ↔ visual ↔ emotional ↔ episodic ↔ auditory
        """
        cortex_types = list(locations.keys())
        
        for i, type1 in enumerate(cortex_types):
            for type2 in cortex_types[i+1:]:
                id1 = locations[type1]
                id2 = locations[type2]
                
                # v0.2: 실제 피질 간 연결 (Global Graph)
                if self.global_graph is not None:
                    # 양방향 연결
                    self.global_graph.add_edge(id1, id2, weight=0.8, memory_id=memory_id)
                    self.global_graph.add_edge(id2, id1, weight=0.8, memory_id=memory_id)
                
                # Cross-cortex edge 저장
                edge_key = ((type1, id1), (type2, id2))
                self.cross_cortex_edges[edge_key] = 0.8
                
                # 역방향도 저장
                reverse_key = ((type2, id2), (type1, id1))
                self.cross_cortex_edges[reverse_key] = 0.8
                
                # 각 피질 내부에서도 연결 (self-connection 유지)
                if type1 in self.cortex:
                    self.cortex[type1].connect(id1, id1, strength=0.5)
                if type2 in self.cortex:
                    self.cortex[type2].connect(id2, id2, strength=0.5)
    
    def get_stats(self) -> Dict:
        """전체 통계 반환"""
        cortex_stats = {
            name: cortex.get_stats() 
            for name, cortex in self.cortex.items()
        }
        
        global_graph_stats = {}
        if self.global_graph:
            global_graph_stats = {
                'nodes': self.global_graph.number_of_nodes(),
                'edges': self.global_graph.number_of_edges(),
                'cross_cortex_edges': len(self.cross_cortex_edges),
            }
        
        return {
            'version': self.VERSION,
            'total_memories': len(self.memory_metadata),
            'total_stores': self.total_stores,
            'total_recalls': self.total_recalls,
            'total_replays': self.total_replays,
            'capacity': self.capacity,
            'hippocampus': {
                'version': self.hippocampus.version,
                'words': len(self.hippocampus.words),
                'neurons': len(self.hippocampus.dg_neurons) + len(self.hippocampus.ca3_neurons),
                'synapses': len(self.hippocampus.dg_to_ca3_synapses) + 
                           len(self.hippocampus.ca3_to_ca1_synapses) + 
                           len(self.hippocampus.ca3_recurrent_synapses),
            },
            'cortex': cortex_stats,
            'global_graph': global_graph_stats,
            'prefrontal': self.prefrontal.get_stats(),
            'last_sleep': self.last_sleep,
        }
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """특정 기억 조회"""
        return self.memory_metadata.get(memory_id)
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """키워드로 기억 검색"""
        results = []
        for mem_id, meta in self.memory_metadata.items():
            if keyword.lower() in [k.lower() for k in meta.get('keywords', [])]:
                results.append({
                    'memory_id': mem_id,
                    'content': meta['content'],
                    'importance': meta['importance'],
                    'access_count': meta['access_count'],
                })
        return sorted(results, key=lambda x: x['importance'], reverse=True)
    
    def get_cross_cortex_connections(self, memory_id: str = None) -> List[Dict]:
        """피질 간 연결 조회 (v0.2)"""
        connections = []
        
        for edge_key, weight in self.cross_cortex_edges.items():
            (type1, id1), (type2, id2) = edge_key
            
            # 특정 기억만 필터링
            if memory_id:
                if memory_id not in id1 and memory_id not in id2:
                    continue
            
            connections.append({
                'from_cortex': type1,
                'from_id': id1,
                'to_cortex': type2,
                'to_id': id2,
                'weight': weight,
            })
        
        return connections
    
    # ===== Private Methods =====
    
    def _generate_memory_id(self, content: str) -> str:
        """고유 기억 ID 생성"""
        timestamp = str(time.time())
        hash_input = content + timestamp
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """내용에서 키워드 추출"""
        import re
        
        # 불용어
        stopwords = {'은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로',
                     '와', '과', '도', '만', '요', '죠', '네', '야', '고', '하고',
                     'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your'}
        
        # 단어 추출
        words = re.findall(r'[가-힣]+|[a-zA-Z]+|\d+', content)
        
        # 필터링
        keywords = []
        for word in words:
            if word.lower() not in stopwords and len(word) > 1:
                keywords.append(word)
        
        # 중복 제거하면서 순서 유지
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        
        return unique_keywords[:10]  # 최대 10개
    
    def _fragment_memory(self, content: str, context: str) -> Dict[str, Any]:
        """
        기억을 피질별 조각으로 분리
        
        실제 뇌에서 기억은 여러 영역에 분산됨:
        - 시각적 요소 → 시각 피질
        - 소리/언어 → 청각 피질
        - 감정 → 감정 피질 (편도체)
        - 의미/개념 → 측두엽
        - 사건/경험 → 일화 기억
        """
        fragments = {}
        
        # 시각 피질: 시각적 특징
        visual_cortex = self.cortex['visual']
        visual_features = visual_cortex.extract_features(content)
        fragments['visual'] = {
            'raw': content,
            'features': visual_features,
            'type': 'visual',
        }
        
        # 청각 피질: 청각적 특징
        auditory_cortex = self.cortex['auditory']
        auditory_features = auditory_cortex.extract_features(content)
        fragments['auditory'] = {
            'raw': content,
            'features': auditory_features,
            'type': 'auditory',
        }
        
        # 감정 피질: 감정적 특징
        emotional_cortex = self.cortex['emotional']
        emotional_features = emotional_cortex.extract_features(content)
        fragments['emotional'] = {
            'raw': content,
            'features': emotional_features,
            'type': 'emotional',
        }
        
        # 의미 피질: 의미적 특징
        semantic_cortex = self.cortex['semantic']
        semantic_features = semantic_cortex.extract_features(content)
        fragments['semantic'] = {
            'raw': content,
            'features': semantic_features,
            'type': 'semantic',
        }
        
        # 일화 피질: 일화적 특징
        episodic_cortex = self.cortex['episodic']
        episodic_features = episodic_cortex.extract_features(content)
        fragments['episodic'] = {
            'raw': content,
            'features': episodic_features,
            'context': context,
            'timestamp': time.time(),
            'type': 'episodic',
        }
        
        return fragments
    
    def _strengthen_connections(self, locations: Dict[str, str], strength: float):
        """기억 조각들의 연결 강화"""
        for cortex_type, frag_id in locations.items():
            if cortex_type in self.cortex:
                cortex = self.cortex[cortex_type]
                cortex.activate(frag_id, level=strength)
    
    def _reconstruct_memories(self, fragments: Dict[str, List], hippo_results: List[Dict]) -> List[Dict]:
        """
        수집된 조각들로 기억 재구성
        
        여러 피질에서 가져온 조각들을 합쳐서 완전한 기억으로 만듦
        """
        reconstructed = []
        seen_contents = set()
        
        # 해마 결과의 키워드들
        hippo_keywords = {r['word_id'] for r in hippo_results}
        
        # 모든 조각에서 기억 재구성
        for cortex_type, frags in fragments.items():
            for frag in frags:
                fragment_data = frag.get('fragment', {})
                raw_content = fragment_data.get('raw', '')
                
                if raw_content and raw_content not in seen_contents:
                    seen_contents.add(raw_content)
                    
                    # 메타데이터에서 원본 찾기
                    memory_id = None
                    original_meta = None
                    
                    for mem_id, meta in self.memory_metadata.items():
                        if meta['content'] == raw_content:
                            memory_id = mem_id
                            original_meta = meta
                            break
                    
                    # 점수 계산
                    score = frag.get('activation', 0.5)
                    
                    # 해마 결과와 매칭되면 보너스
                    if original_meta:
                        matching_keywords = set(original_meta.get('keywords', [])) & hippo_keywords
                        score += len(matching_keywords) * 0.1
                    
                    reconstructed.append({
                        'memory_id': memory_id,
                        'content': raw_content,
                        'score': score,
                        'source_cortex': cortex_type,
                        'features': fragment_data.get('features', {}),
                        'activation': frag.get('activation', 0.5),
                        'importance': original_meta.get('importance', 0.5) if original_meta else 0.5,
                    })
        
        # 점수로 정렬
        reconstructed.sort(key=lambda x: x['score'], reverse=True)
        
        return reconstructed
    
    def _selective_forgetting(self, threshold: float = 0.1):
        """선택적 망각 - 중요하지 않은 기억 정리"""
        # 활성화가 매우 낮고 접근이 없는 기억 식별
        candidates = []
        
        for mem_id, meta in self.memory_metadata.items():
            # 중요하지 않고, 접근 횟수가 적고, 오래된 기억
            if (meta['importance'] < 0.3 and 
                meta['access_count'] < 2 and
                time.time() - meta['created_at'] > 86400):  # 1일 이상
                candidates.append(mem_id)
        
        # 상위 10%만 정리 (완전 삭제는 아님, 활성화만 낮춤)
        n_to_weaken = max(1, len(candidates) // 10)
        for mem_id in candidates[:n_to_weaken]:
            locations = self.memory_metadata[mem_id].get('cortex_locations', {})
            for cortex_type, frag_id in locations.items():
                if cortex_type in self.cortex:
                    # 활성화 크게 낮춤
                    self.cortex[cortex_type].activation[frag_id] *= 0.5


# ===== 편의 함수 =====

def create_brain(capacity: int = 10000) -> BrainGraph:
    """BrainGraph 인스턴스 생성 헬퍼"""
    return BrainGraph(capacity=capacity)
