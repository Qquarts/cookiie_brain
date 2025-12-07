"""
CortexNode: 대뇌 피질 영역 모델
Brain Graph v0.4

v0.4 주요 변경사항:
- 인접 리스트: activate() O(n) → O(k) 최적화
- 중복 저장 방지: allow_duplicate 옵션
- Consolidation 최적화: O(m²) → O(k)
- 감정 분석 개선: dominant_emotion 추가
- 년도 패턴 수정: 전체 년도 추출

v0.3 기능 유지:
- Soft Activation: sigmoid 기반 활성화 (saturation 방지)
- Self-loop 제거: cross-cortex 연결만 유효
- Feature 추출 고도화: entity/concept/relation 분리

각 피질 노드는 특정 유형의 정보를 분산 저장합니다:
- 시각 피질: 이미지, 형태, 색상
- 청각 피질: 소리, 언어, 음악
- 감정 피질: 느낌, 감정, 분위기
- 의미 피질: 개념, 관계, 카테고리
- 일화 피질: 사건, 경험, 시간
"""

import numpy as np
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set
import hashlib
import math


class CortexNode:
    """
    대뇌 피질 영역 - 특정 유형의 기억 조각 저장
    
    생물학적 배경:
    - 실제 뇌에서 기억은 피질 전체에 분산 저장됨
    - 각 영역은 특정 유형의 정보를 전문적으로 처리
    - 해마는 이 조각들을 연결하는 인덱스 역할
    """
    
    # 피질 영역 타입 정의
    CORTEX_TYPES = {
        'visual': '시각',      # 이미지, 형태
        'auditory': '청각',    # 소리, 언어
        'emotional': '감정',   # 느낌, 기분
        'semantic': '의미',    # 개념, 관계
        'episodic': '일화',    # 사건, 경험
    }
    
    def __init__(self, cortex_type: str, capacity: int = 10000):
        """
        피질 노드 초기화
        
        Args:
            cortex_type: 피질 유형 ('visual', 'auditory', 'emotional', 'semantic', 'episodic')
            capacity: 최대 저장 용량
        """
        if cortex_type not in self.CORTEX_TYPES:
            raise ValueError(f"Unknown cortex type: {cortex_type}. Must be one of {list(self.CORTEX_TYPES.keys())}")
        
        self.cortex_type = cortex_type
        self.name = self.CORTEX_TYPES[cortex_type]
        self.capacity = capacity
        
        # 기억 저장소: memory_id → fragment
        self.fragments: Dict[str, Any] = {}
        
        # v0.4: 내용 해시 → memory_id (중복 감지용)
        self.content_hash_map: Dict[str, str] = {}
        
        # 인덱스 매핑: hippo_index → [memory_ids]
        self.index_map: Dict[str, Set[str]] = defaultdict(set)
        
        # 활성화 수준: memory_id → activation_level
        self.activation: Dict[str, float] = defaultdict(float)
        
        # 연결 강도: (memory_id, memory_id) → strength
        self.connections: Dict[tuple, float] = {}
        
        # v0.4: 인접 리스트 (빠른 탐색용)
        # memory_id → [(connected_id, strength), ...]
        self.adjacency: Dict[str, List[tuple]] = defaultdict(list)
        
        # 통계
        self.access_count: Dict[str, int] = defaultdict(int)
        self.last_access: Dict[str, float] = {}
    
    def store(self, hippo_index: str, fragment: Any, 
              memory_id: Optional[str] = None,
              allow_duplicate: bool = False) -> str:
        """
        기억 조각 저장 (v0.4: 중복 감지)
        
        Args:
            hippo_index: 해마에서 생성된 인덱스 (연결 키)
            fragment: 저장할 기억 조각
            memory_id: 고유 ID (없으면 자동 생성)
            allow_duplicate: True면 중복 허용, False면 기존 ID 반환
        
        Returns:
            memory_id: 저장된 기억의 ID
        """
        # v0.4: 중복 감지
        if not allow_duplicate and memory_id is None:
            content_hash = self._content_hash(fragment)
            
            if content_hash in self.content_hash_map:
                # 기존 기억 활성화만 증가
                existing_id = self.content_hash_map[content_hash]
                if existing_id in self.fragments:
                    self._boost_activation(existing_id, amount=0.2)
                    self.index_map[hippo_index].add(existing_id)
                    return existing_id
        
        # 용량 체크
        if len(self.fragments) >= self.capacity:
            self._evict_oldest()
        
        # ID 생성
        if memory_id is None:
            memory_id = self._generate_id(fragment)
        
        # 저장
        self.fragments[memory_id] = fragment
        self.index_map[hippo_index].add(memory_id)
        self.activation[memory_id] = 1.0  # 초기 활성화
        self.last_access[memory_id] = self._current_time()
        
        # v0.4: 내용 해시 저장
        content_hash = self._content_hash(fragment)
        self.content_hash_map[content_hash] = memory_id
        
        return memory_id
    
    def _content_hash(self, fragment: Any) -> str:
        """내용 기반 해시 생성 (중복 감지용)"""
        content = str(fragment)
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def retrieve(self, hippo_indices: List[str]) -> List[Any]:
        """
        해마 인덱스로 기억 조각 검색
        
        Args:
            hippo_indices: 해마에서 반환된 인덱스 목록
        
        Returns:
            fragments: 검색된 기억 조각들
        """
        results = []
        
        for index in hippo_indices:
            memory_ids = self.index_map.get(index, set())
            for mem_id in memory_ids:
                if mem_id in self.fragments:
                    fragment = self.fragments[mem_id]
                    results.append({
                        'id': mem_id,
                        'index': index,
                        'fragment': fragment,
                        'activation': self.activation[mem_id]
                    })
                    
                    # 접근 기록 업데이트
                    self.access_count[mem_id] += 1
                    self.last_access[mem_id] = self._current_time()
                    
                    # 활성화 부스트
                    self._boost_activation(mem_id)
        
        # 활성화 수준으로 정렬
        results.sort(key=lambda x: x['activation'], reverse=True)
        return results
    
    def activate(self, memory_id: str, level: float = 0.5) -> float:
        """
        특정 기억 활성화 (same-cortex spreading only)
        
        v0.4: 인접 리스트 기반 O(k) 탐색
        v0.3: Soft Activation with sigmoid rescale
        - 전역 spreading은 BrainGraph가 담당
        - 이 함수는 피질 내부 전파만 수행
        
        Args:
            memory_id: 활성화할 기억 ID
            level: 활성화 수준 (0.0 ~ 1.0)
        
        Returns:
            new_activation: 새로운 활성화 수준 (0.0 ~ 1.0)
        """
        if memory_id not in self.fragments:
            return 0.0
        
        # v0.3: Soft Activation (sigmoid 기반, saturation 방지)
        current = self.activation[memory_id]
        raw_activation = current + level
        self.activation[memory_id] = self._soft_activation(raw_activation)
        
        # v0.4: 인접 리스트 기반 spreading (O(k) - k=이웃 수)
        for connected_id, strength in self.adjacency.get(memory_id, []):
            if connected_id in self.fragments:
                spread = level * strength * 0.3  # 30% 전파
                self.activation[connected_id] = self._soft_activation(
                    self.activation[connected_id] + spread
                )
        
        return self.activation[memory_id]
    
    def _soft_activation(self, x: float, scale: float = 2.0) -> float:
        """
        Soft activation function (v0.3)
        
        sigmoid(x * scale) 기반으로 saturation 완화
        - x가 커져도 1.0에 급격히 도달하지 않음
        - 활성화 차이가 유지됨
        
        Args:
            x: raw activation value
            scale: scaling factor (default: 2.0)
        
        Returns:
            soft activation (0.0 ~ 1.0)
        """
        # sigmoid: 1 / (1 + exp(-x))
        # scale 조정으로 곡선 기울기 제어
        try:
            return 1.0 / (1.0 + math.exp(-scale * (x - 0.5)))
        except OverflowError:
            return 1.0 if x > 0.5 else 0.0
    
    def connect(self, memory_id1: str, memory_id2: str, strength: float = 0.5):
        """
        두 기억 사이에 연결 생성/강화 (same-cortex only)
        
        v0.4: 인접 리스트 동시 업데이트
        v0.3: Self-loop 무시
        - cross-cortex 연결은 BrainGraph.global_graph가 담당
        - 이 함수는 피질 내부 연결만 관리
        
        Args:
            memory_id1, memory_id2: 연결할 기억 ID들
            strength: 연결 강도 (0.0 ~ 1.0)
        """
        # v0.3: Self-loop 무시 (의미 없는 연결 방지)
        if memory_id1 == memory_id2:
            return
        
        if memory_id1 not in self.fragments or memory_id2 not in self.fragments:
            return
        
        key = tuple(sorted([memory_id1, memory_id2]))
        
        # 기존 연결 강화 또는 새 연결 생성
        is_new = key not in self.connections
        
        if is_new:
            self.connections[key] = strength
            # v0.4: 인접 리스트에도 추가 (양방향)
            self.adjacency[memory_id1].append((memory_id2, strength))
            self.adjacency[memory_id2].append((memory_id1, strength))
        else:
            new_strength = min(1.0, self.connections[key] + strength * 0.2)
            self.connections[key] = new_strength
            # v0.4: 인접 리스트 업데이트
            self._update_adjacency(memory_id1, memory_id2, new_strength)
    
    def _update_adjacency(self, id1: str, id2: str, new_strength: float):
        """인접 리스트의 연결 강도 업데이트"""
        # id1 → id2 업데이트
        for i, (connected_id, _) in enumerate(self.adjacency[id1]):
            if connected_id == id2:
                self.adjacency[id1][i] = (id2, new_strength)
                break
        
        # id2 → id1 업데이트
        for i, (connected_id, _) in enumerate(self.adjacency[id2]):
            if connected_id == id1:
                self.adjacency[id2][i] = (id1, new_strength)
                break
    
    def consolidate(self, decay_rate: float = 0.05, max_new_connections: int = 50):
        """
        수면 공고화 - 연결 강화 및 약한 기억 정리
        
        v0.4: O(m²) → O(k) 최적화
        - 상위 N개 활성 기억만 연결
        - 최대 연결 수 제한
        
        Args:
            decay_rate: 활성화 감쇠율
            max_new_connections: 최대 새 연결 수 (기본: 50)
        """
        # 1. 활성화 감쇠
        for mem_id in self.activation:
            self.activation[mem_id] *= (1.0 - decay_rate)
            if self.activation[mem_id] < 0.01:
                self.activation[mem_id] = 0.01  # 최소값 유지
        
        # 2. v0.4: 고활성 기억만 연결 (상위 20개, O(k) 복잡도)
        active_memories = sorted(
            [(mem_id, act) for mem_id, act in self.activation.items() if act > 0.3],
            key=lambda x: x[1],
            reverse=True
        )[:20]  # 상위 20개만
        
        connections_made = 0
        for i, (mem1, act1) in enumerate(active_memories):
            if connections_made >= max_new_connections:
                break
            
            # 인접한 최대 5개만 연결 (이웃 제한)
            for mem2, act2 in active_memories[i+1:i+6]:
                strength = 0.1 * (act1 + act2) / 2  # 활성화 평균 반영
                self.connect(mem1, mem2, strength=strength)
                connections_made += 1
                
                if connections_made >= max_new_connections:
                    break
        
        # 3. 약한 연결 정리 (인접 리스트도 정리)
        weak_connections = [
            key for key, strength in self.connections.items()
            if strength < 0.05
        ]
        for key in weak_connections:
            del self.connections[key]
            # v0.4: 인접 리스트에서도 제거
            id1, id2 = key
            self.adjacency[id1] = [(cid, s) for cid, s in self.adjacency[id1] if cid != id2]
            self.adjacency[id2] = [(cid, s) for cid, s in self.adjacency[id2] if cid != id1]
    
    def get_stats(self) -> Dict:
        """피질 노드 통계 반환"""
        return {
            'type': self.cortex_type,
            'name': self.name,
            'fragments': len(self.fragments),
            'capacity': self.capacity,
            'usage': f"{len(self.fragments) / self.capacity * 100:.1f}%",
            'connections': len(self.connections),
            'avg_activation': np.mean(list(self.activation.values())) if self.activation else 0.0,
            'total_accesses': sum(self.access_count.values()),
        }
    
    def _generate_id(self, fragment: Any) -> str:
        """고유 ID 생성"""
        content = str(fragment) + str(self._current_time())
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _current_time(self) -> float:
        """현재 시간 (시뮬레이션용)"""
        import time
        return time.time()
    
    def _boost_activation(self, memory_id: str, amount: float = 0.1):
        """접근 시 활성화 부스트"""
        self.activation[memory_id] = min(1.0, self.activation[memory_id] + amount)
    
    def _evict_oldest(self):
        """가장 오래된/덜 중요한 기억 제거"""
        if not self.fragments:
            return
        
        # 활성화 * 접근 횟수로 중요도 계산
        scores = {}
        for mem_id in self.fragments:
            access = self.access_count.get(mem_id, 0) + 1
            activation = self.activation.get(mem_id, 0.1)
            scores[mem_id] = activation * np.log1p(access)
        
        # 가장 낮은 점수의 기억 제거
        victim = min(scores, key=scores.get)
        self._remove(victim)
    
    def _remove(self, memory_id: str):
        """기억 제거"""
        if memory_id in self.fragments:
            del self.fragments[memory_id]
        
        # 인덱스 맵에서도 제거
        for index, mem_ids in list(self.index_map.items()):
            mem_ids.discard(memory_id)
            if not mem_ids:
                del self.index_map[index]
        
        # 연결도 제거
        to_remove = [key for key in self.connections if memory_id in key]
        for key in to_remove:
            del self.connections[key]
        
        # 기타 정리
        self.activation.pop(memory_id, None)
        self.access_count.pop(memory_id, None)
        self.last_access.pop(memory_id, None)


class VisualCortex(CortexNode):
    """시각 피질 - 이미지, 형태, 색상 전문 (v0.3)"""
    
    def __init__(self, capacity: int = 10000):
        super().__init__('visual', capacity)
        
        # v0.3: 확장된 시각 어휘
        self.color_vocab = {
            'red': ['빨강', '빨간', '붉은', 'red', 'crimson', '주홍'],
            'blue': ['파랑', '파란', '푸른', 'blue', 'navy', '하늘색'],
            'yellow': ['노랑', '노란', 'yellow', '금색', 'gold'],
            'green': ['초록', '녹색', 'green', '연두'],
            'black': ['검정', '검은', 'black', '까만'],
            'white': ['하양', '하얀', '흰', 'white'],
            'orange': ['주황', 'orange', '오렌지'],
            'purple': ['보라', 'purple', '자주'],
            'pink': ['분홍', 'pink', '핑크'],
            'brown': ['갈색', 'brown', '밤색'],
        }
        
        self.object_vocab = {
            'animal': ['고양이', '강아지', '개', '새', '물고기', 'cat', 'dog', 'bird', 'fish', '동물'],
            'plant': ['꽃', '나무', '풀', 'flower', 'tree', '식물'],
            'food': ['음식', '밥', '과일', '야채', 'food', 'fruit'],
            'vehicle': ['차', '자동차', '비행기', '배', 'car', 'plane', 'ship'],
            'building': ['집', '건물', '아파트', '학교', 'house', 'building', 'school'],
        }
    
    def extract_features(self, content: str) -> Dict:
        """텍스트에서 시각적 특징 추출 (v0.3 고도화)"""
        features = {
            'colors': [],
            'color_categories': [],
            'shapes': [],
            'objects': [],
            'object_categories': [],
            'visual_intensity': 0.0,  # 시각적 풍부함 점수
        }
        
        content_lower = content.lower()
        
        # 색상 추출 (카테고리 포함)
        for category, keywords in self.color_vocab.items():
            for keyword in keywords:
                if keyword in content_lower:
                    features['colors'].append(keyword)
                    if category not in features['color_categories']:
                        features['color_categories'].append(category)
        
        # 형태 키워드
        shapes = ['동그란', '네모', '세모', '원형', '사각', '삼각', '길쭉', '둥근',
                  'round', 'square', 'triangle', 'circle', 'oval', 'rectangular']
        for shape in shapes:
            if shape in content_lower:
                features['shapes'].append(shape)
        
        # 객체 추출 (카테고리 포함)
        for category, keywords in self.object_vocab.items():
            for keyword in keywords:
                if keyword in content_lower:
                    features['objects'].append(keyword)
                    if category not in features['object_categories']:
                        features['object_categories'].append(category)
        
        # 시각적 풍부함 점수
        features['visual_intensity'] = min(1.0, 
            len(features['colors']) * 0.2 + 
            len(features['shapes']) * 0.2 + 
            len(features['objects']) * 0.3
        )
        
        return features


class AuditoryCortex(CortexNode):
    """청각 피질 - 소리, 언어, 음악 전문 (v0.3)"""
    
    def __init__(self, capacity: int = 10000):
        super().__init__('auditory', capacity)
        
        # v0.3: 확장된 청각 어휘
        self.sound_vocab = {
            'music': ['음악', '노래', '멜로디', '곡', 'music', 'song', 'melody', 'tune'],
            'voice': ['목소리', '말', '대화', '이야기', 'voice', 'speak', 'talk', 'say'],
            'nature': ['바람', '비', '천둥', '새소리', 'wind', 'rain', 'thunder', 'bird'],
            'emotion_sound': ['웃음', '울음', '한숨', '비명', 'laugh', 'cry', 'sigh', 'scream'],
            'noise': ['소음', '시끄러운', '조용한', 'noise', 'loud', 'quiet', 'silent'],
        }
    
    def extract_features(self, content: str) -> Dict:
        """텍스트에서 청각적 특징 추출 (v0.3 고도화)"""
        features = {
            'sounds': [],
            'sound_categories': [],
            'language_markers': [],
            'auditory_intensity': 0.0,
        }
        
        content_lower = content.lower()
        
        # 소리 추출 (카테고리 포함)
        for category, keywords in self.sound_vocab.items():
            for keyword in keywords:
                if keyword in content_lower:
                    features['sounds'].append(keyword)
                    if category not in features['sound_categories']:
                        features['sound_categories'].append(category)
        
        # 언어 마커 (인용, 대화 표시)
        language_markers = ['말했', '라고', '라며', '"', "'", 'said', 'told', 'asked']
        for marker in language_markers:
            if marker in content_lower:
                features['language_markers'].append(marker)
        
        # 청각적 풍부함 점수
        features['auditory_intensity'] = min(1.0,
            len(features['sounds']) * 0.3 +
            len(features['language_markers']) * 0.2
        )
        
        return features


class EmotionalCortex(CortexNode):
    """감정 피질 - 느낌, 감정, 분위기 전문 (v0.4)"""
    
    def __init__(self, capacity: int = 10000):
        super().__init__('emotional', capacity)
        
        # v0.3: Russell's Circumplex Model 기반 감정 분류
        # (valence: 긍정/부정, arousal: 활성화 수준)
        self.emotion_vocab = {
            # 긍정 + 고각성
            'excited': {'words': ['신나', '흥분', '설레', 'excited', 'thrilled'], 'valence': 0.8, 'arousal': 0.8},
            'happy': {'words': ['행복', '기쁨', '즐거', 'happy', 'joy', 'delighted'], 'valence': 0.7, 'arousal': 0.5},
            # 긍정 + 저각성
            'calm': {'words': ['평화', '편안', '안정', 'calm', 'peaceful', 'relaxed'], 'valence': 0.5, 'arousal': -0.3},
            'content': {'words': ['만족', '감사', '고마', 'content', 'grateful', 'thankful'], 'valence': 0.6, 'arousal': 0.0},
            # 부정 + 고각성
            'angry': {'words': ['화', '분노', '짜증', 'angry', 'furious', 'annoyed'], 'valence': -0.7, 'arousal': 0.8},
            'anxious': {'words': ['불안', '걱정', '초조', 'anxious', 'worried', 'nervous'], 'valence': -0.5, 'arousal': 0.6},
            'afraid': {'words': ['무서', '두려', '공포', 'afraid', 'scared', 'fear'], 'valence': -0.6, 'arousal': 0.7},
            # 부정 + 저각성
            'sad': {'words': ['슬픔', '슬퍼', '우울', 'sad', 'depressed', 'down'], 'valence': -0.6, 'arousal': -0.4},
            'bored': {'words': ['지루', '심심', 'bored', 'tired'], 'valence': -0.3, 'arousal': -0.5},
            # 중립
            'surprised': {'words': ['놀라', '깜짝', 'surprised', 'shocked'], 'valence': 0.0, 'arousal': 0.7},
        }
        
        # 사랑/관계 감정 (특별 처리)
        self.love_words = ['사랑', '좋아', '애정', 'love', 'like', 'adore', '귀여', 'cute']
        self.hate_words = ['싫어', '미워', 'hate', 'dislike', '혐오']
    
    def extract_features(self, content: str) -> Dict:
        """텍스트에서 감정적 특징 추출 (v0.4 가중 평균 + dominant_emotion)"""
        features = {
            'emotions': [],
            'emotion_categories': [],
            'valence': 0.0,           # -1 (부정) ~ +1 (긍정)
            'arousal': 0.0,           # -1 (저각성) ~ +1 (고각성)
            'emotional_intensity': 0.0,
            'dominant_emotion': None,  # v0.4: 지배적 감정
        }
        
        content_lower = content.lower()
        
        # v0.4: 감정별 점수 수집 (가중 평균용)
        emotion_scores = []
        
        # 감정 추출 (Circumplex 기반)
        for category, info in self.emotion_vocab.items():
            count = sum(1 for word in info['words'] if word in content_lower)
            if count > 0:
                # 감지된 단어들 추가
                for word in info['words']:
                    if word in content_lower:
                        features['emotions'].append(word)
                
                if category not in features['emotion_categories']:
                    features['emotion_categories'].append(category)
                
                # v0.4: 감정 강도 계산 (빈도 × 감정 크기)
                strength = count * (abs(info['valence']) + abs(info['arousal'])) / 2
                emotion_scores.append({
                    'category': category,
                    'valence': info['valence'],
                    'arousal': info['arousal'],
                    'count': count,
                    'strength': strength,
                })
        
        # 사랑/미움 (특별 처리)
        love_count = sum(1 for word in self.love_words if word in content_lower)
        if love_count > 0:
            for word in self.love_words:
                if word in content_lower:
                    features['emotions'].append(word)
            emotion_scores.append({
                'category': 'love',
                'valence': 0.6,
                'arousal': 0.3,
                'count': love_count,
                'strength': love_count * 0.5,
            })
        
        hate_count = sum(1 for word in self.hate_words if word in content_lower)
        if hate_count > 0:
            for word in self.hate_words:
                if word in content_lower:
                    features['emotions'].append(word)
            emotion_scores.append({
                'category': 'hate',
                'valence': -0.7,
                'arousal': 0.5,
                'count': hate_count,
                'strength': hate_count * 0.6,
            })
        
        # v0.4: 가중 평균 계산 (빈도 고려)
        if emotion_scores:
            total_count = sum(e['count'] for e in emotion_scores)
            features['valence'] = sum(
                e['valence'] * e['count'] for e in emotion_scores
            ) / total_count
            features['arousal'] = sum(
                e['arousal'] * e['count'] for e in emotion_scores
            ) / total_count
            
            # v0.4: 지배적 감정 (가장 강한 감정)
            dominant = max(emotion_scores, key=lambda x: x['strength'])
            features['dominant_emotion'] = dominant['category']
        
        features['valence'] = max(-1.0, min(1.0, features['valence']))
        features['arousal'] = max(-1.0, min(1.0, features['arousal']))
        
        # 감정 강도
        total_emotions = len(features['emotions'])
        features['emotional_intensity'] = min(1.0, total_emotions * 0.3)
        
        return features


class SemanticCortex(CortexNode):
    """의미 피질 - 개념, 관계, 카테고리 전문 (v0.3)"""
    
    def __init__(self, capacity: int = 10000):
        super().__init__('semantic', capacity)
        
        # v0.3: Entity/Concept/Relation 분리
        self.entity_patterns = {
            'person': ['이름', '나', '너', '사람', '친구', '가족', 'name', 'person', 'friend', 'family'],
            'place': ['장소', '집', '회사', '학교', '도시', '나라', 'place', 'home', 'city', 'country'],
            'organization': ['회사', '학교', '기관', '단체', 'company', 'school', 'organization'],
            'time': ['시간', '날짜', '년', '월', '일', '오늘', '어제', 'time', 'date', 'today', 'yesterday'],
        }
        
        self.concept_patterns = {
            'activity': ['하다', '하고', '했다', '일', '작업', 'do', 'work', 'activity'],
            'state': ['있다', '이다', '되다', 'is', 'are', 'be', 'become'],
            'possession': ['가지다', '있어', '소유', 'have', 'own', 'possess'],
            'preference': ['좋아', '싫어', '원하', 'like', 'hate', 'want', 'prefer'],
        }
        
        self.relation_patterns = {
            'is_a': ['이다', '이야', '입니다', 'is', 'am', 'are'],
            'has_a': ['있다', '가지고', '있어', 'have', 'has', 'got'],
            'located_in': ['살다', '있다', '위치', 'live', 'in', 'at', 'located'],
            'born_in': ['년생', '태어나', 'born', 'birth'],
            'works_at': ['일하', '근무', '직장', 'work', 'job', 'employed'],
        }
    
    def extract_features(self, content: str) -> Dict:
        """텍스트에서 의미적 특징 추출 (v0.3 Entity/Concept/Relation)"""
        features = {
            'entities': [],
            'entity_types': [],
            'concepts': [],
            'concept_types': [],
            'relations': [],
            'relation_types': [],
            'semantic_richness': 0.0,
        }
        
        content_lower = content.lower()
        
        # Entity 추출
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    features['entities'].append(pattern)
                    if entity_type not in features['entity_types']:
                        features['entity_types'].append(entity_type)
        
        # Concept 추출
        for concept_type, patterns in self.concept_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    features['concepts'].append(pattern)
                    if concept_type not in features['concept_types']:
                        features['concept_types'].append(concept_type)
        
        # Relation 추출
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    features['relations'].append(pattern)
                    if relation_type not in features['relation_types']:
                        features['relation_types'].append(relation_type)
        
        # 의미적 풍부함 점수
        features['semantic_richness'] = min(1.0,
            len(features['entity_types']) * 0.2 +
            len(features['concept_types']) * 0.2 +
            len(features['relation_types']) * 0.3
        )
        
        return features


class EpisodicCortex(CortexNode):
    """일화 피질 - 사건, 경험, 시간 전문 (v0.4)"""
    
    def __init__(self, capacity: int = 10000):
        super().__init__('episodic', capacity)
        
        # v0.3: 시간/사건/경험 분리
        self.temporal_patterns = {
            'relative': ['어제', '오늘', '내일', '지난', '다음', '전에', '후에', '최근',
                        'yesterday', 'today', 'tomorrow', 'last', 'next', 'before', 'after', 'recently'],
            'absolute': ['년', '월', '일', '시', '분', 'year', 'month', 'day', 'hour', 'minute'],
            'duration': ['동안', '부터', '까지', '사이', 'during', 'from', 'to', 'between'],
            'frequency': ['항상', '자주', '가끔', '매일', 'always', 'often', 'sometimes', 'daily'],
        }
        
        self.event_patterns = {
            'experience': ['경험', '겪다', '했다', '만났', 'experience', 'met', 'had'],
            'achievement': ['성공', '달성', '완료', '졸업', 'success', 'achieve', 'complete', 'graduate'],
            'transition': ['시작', '끝', '변화', '이사', 'start', 'end', 'change', 'move'],
            'social': ['만나', '결혼', '파티', '모임', 'meet', 'marry', 'party', 'gathering'],
        }
        
        self.context_markers = {
            'location': ['에서', '에', '로', '까지', 'in', 'at', 'to', 'from'],
            'companion': ['와', '과', '함께', '같이', 'with', 'together'],
            'reason': ['때문에', '위해', '덕분에', 'because', 'for', 'due to'],
        }
    
    def extract_features(self, content: str) -> Dict:
        """텍스트에서 일화적 특징 추출 (v0.4 년도 패턴 수정)"""
        import re
        
        features = {
            'temporal_markers': [],
            'temporal_types': [],
            'events': [],
            'event_types': [],
            'context_markers': [],
            'context_types': [],
            'years': [],
            'relative_years': [],  # v0.4: 상대적 년도 ("3년 전" 등)
            'episodic_richness': 0.0,
        }
        
        content_lower = content.lower()
        
        # 시간 마커 추출
        for temp_type, patterns in self.temporal_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    features['temporal_markers'].append(pattern)
                    if temp_type not in features['temporal_types']:
                        features['temporal_types'].append(temp_type)
        
        # 사건 추출
        for event_type, patterns in self.event_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    features['events'].append(pattern)
                    if event_type not in features['event_types']:
                        features['event_types'].append(event_type)
        
        # 맥락 마커 추출
        for ctx_type, patterns in self.context_markers.items():
            for pattern in patterns:
                if pattern in content_lower:
                    features['context_markers'].append(pattern)
                    if ctx_type not in features['context_types']:
                        features['context_types'].append(ctx_type)
        
        # v0.4: 년도 패턴 수정 (전체 년도 추출)
        # 한글 환경에서 word boundary 대신 직접 매칭
        year_pattern = r'((?:19|20)\d{2})년?'  # "1983" 또는 "1983년"
        year_matches = re.findall(year_pattern, content)
        features['years'] = sorted(set(year_matches))  # 정렬 + 중복 제거
        
        # v0.4: 상대적 년도 추출 ("3년 전", "2년차" 등)
        # 4자리 년도는 제외 (lookbehind로 앞에 숫자 없는 경우만)
        relative_pattern = r'(?<!\d)(\d{1,3})년'  # 1-3자리만
        relative_matches = re.findall(relative_pattern, content)
        features['relative_years'] = list(set(relative_matches))
        
        # 일화적 풍부함 점수
        features['episodic_richness'] = min(1.0,
            len(features['temporal_types']) * 0.2 +
            len(features['event_types']) * 0.3 +
            len(features['context_types']) * 0.2 +
            len(features['years']) * 0.3
        )
        
        return features

