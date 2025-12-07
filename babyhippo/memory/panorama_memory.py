"""
Panorama Memory: 인생의 파노라마 기억 시스템

🎬 개념:
    사람의 기억은 개별 아이템이 아니라 "인생의 필름"
    주마등처럼 전체 파노라마를 가지고 있고
    거기서 "더듬어" 찾아보는 것
    
    "그때 어땠었지?"

🤖 AI 기억의 원칙:
    - 사람의 뇌 구조를 모방하되
    - 성능은 사람보다 월등히 좋아야 함
    - 사람처럼 "잊어버리면" AI 만드는 의미 없음
    - 우리가 할 수 없는 일을 해야 함

구조:
    1. Archive (영구 저장소): 모든 기억 완벽 보관, 절대 손실 없음
    2. Timeline (파노라마): 시간순 연결된 기억의 흐름
    3. Surface (표면): 현재 떠오르기 쉬운 정도 (decay 대상)
    4. Search (검색): 파노라마를 더듬어 찾는 기능

Author: GNJz (Qquarts)
Version: 2.0 (Panorama Edition)
"""

import time
import json
import numpy as np
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class PanoramaMemory:
    """
    파노라마 기억 시스템
    
    🎬 인생의 필름처럼 모든 기억을 시간순으로 연결
    🔍 파노라마를 "더듬어" 검색
    💾 완벽한 영구 보관 (AI는 잊지 않음)
    ⚡ 사람보다 월등한 recall 성능
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, name: str = "default"):
        """
        Args:
            name: 파노라마 이름 (저장/로드용)
        """
        self.name = name
        self.created_at = time.time()
        
        # === 1. Archive (영구 저장소) ===
        # 모든 기억의 완벽한 사본. 절대 수정/삭제 안 됨.
        # key: memory_id, value: 원본 기억 데이터
        self._archive: Dict[str, Dict] = {}
        
        # === 2. Timeline (파노라마) ===
        # 시간순으로 연결된 기억의 흐름
        # List of memory_ids in chronological order
        self._timeline: List[str] = []
        
        # 시간대별 인덱스 (빠른 검색용)
        self._time_index: Dict[str, List[str]] = defaultdict(list)
        
        # === 3. Surface (표면 접근성) ===
        # 현재 얼마나 쉽게 떠오르는가 (0.0 ~ 1.0)
        # decay 대상이지만, 기억 자체는 archive에 영구 보관
        self._surface: Dict[str, float] = {}
        
        # === 4. Connections (연결) ===
        # 기억 간의 연상 연결 (PageRank 계산용)
        self._connections: Dict[str, List[str]] = defaultdict(list)
        
        # === 5. Context Layers (맥락 레이어) ===
        # 같은 맥락의 기억들을 그룹화
        self._contexts: Dict[str, List[str]] = defaultdict(list)
        
        # === 6. Metadata ===
        self._access_count: Dict[str, int] = defaultdict(int)
        self._last_access: Dict[str, float] = {}
        self._importance: Dict[str, float] = {}  # PageRank 기반 중요도
        
        # 내부 카운터
        self._memory_counter = 0
    
    def _generate_id(self) -> str:
        """고유 memory_id 생성"""
        self._memory_counter += 1
        return f"mem_{self._memory_counter:08d}_{int(time.time()*1000)}"
    
    # =========================================================
    # 📝 STORE: 기억 저장
    # =========================================================
    
    def store(self, 
              content: Any,
              context: str = None,
              tags: List[str] = None,
              links: List[str] = None,
              importance: float = 0.5) -> str:
        """
        새 기억 저장
        
        Args:
            content: 기억 내용 (어떤 타입이든 OK)
            context: 맥락 (예: "childhood", "work", "2024")
            tags: 태그 리스트
            links: 연결할 기존 memory_id 리스트
            importance: 초기 중요도 (0.0 ~ 1.0)
        
        Returns:
            memory_id
        
        🔒 Archive에 영구 저장됨. 절대 손실 없음.
        """
        memory_id = self._generate_id()
        now = time.time()
        
        # === Archive에 완벽한 사본 저장 ===
        memory_data = {
            'id': memory_id,
            'content': content,
            'context': context,
            'tags': tags or [],
            'created_at': now,
            'original_importance': importance,
            # 메타데이터
            'store_version': self.VERSION,
        }
        self._archive[memory_id] = memory_data
        
        # === Timeline에 추가 ===
        self._timeline.append(memory_id)
        
        # 시간 인덱스
        time_key = time.strftime("%Y-%m-%d", time.localtime(now))
        self._time_index[time_key].append(memory_id)
        
        # === Surface 초기화 (처음엔 쉽게 떠오름) ===
        self._surface[memory_id] = 1.0
        
        # === Connections 설정 ===
        if links:
            for link_id in links:
                if link_id in self._archive:
                    self._connections[memory_id].append(link_id)
                    self._connections[link_id].append(memory_id)
        
        # 이전 기억과 자동 연결 (시간적 근접성)
        if len(self._timeline) > 1:
            prev_id = self._timeline[-2]
            self._connections[memory_id].append(prev_id)
            self._connections[prev_id].append(memory_id)
        
        # === Context 레이어 ===
        if context:
            self._contexts[context].append(memory_id)
        
        # === Importance 초기화 ===
        self._importance[memory_id] = importance
        
        # === Access 기록 ===
        self._access_count[memory_id] = 0
        self._last_access[memory_id] = now
        
        return memory_id
    
    # =========================================================
    # 🔍 RECALL: 기억 검색 (파노라마를 더듬어 찾기)
    # =========================================================
    
    def recall(self, 
               query: str = None,
               context: str = None,
               time_range: Tuple[float, float] = None,
               top_n: int = 10,
               include_deep: bool = True) -> List[Dict]:
        """
        파노라마에서 기억 검색
        
        Args:
            query: 검색어 (내용 매칭)
            context: 맥락 필터
            time_range: (start_time, end_time) 시간 범위
            top_n: 반환할 개수
            include_deep: True면 surface 낮은 것도 포함 (AI 우월성)
        
        Returns:
            List of memory dicts with scores
        
        🔍 사람처럼 "더듬어" 찾지만, AI는 완벽히 기억함
        """
        candidates = []
        
        # Step 1: 후보 수집
        for memory_id in self._timeline:
            memory = self._archive[memory_id]
            
            # Context 필터
            if context and memory.get('context') != context:
                continue
            
            # Time range 필터
            if time_range:
                created = memory['created_at']
                if not (time_range[0] <= created <= time_range[1]):
                    continue
            
            candidates.append(memory_id)
        
        # Step 2: 점수 계산
        scored = []
        for memory_id in candidates:
            memory = self._archive[memory_id]
            
            # 기본 점수
            score = 0.0
            
            # Query 매칭 (완벽한 recall - AI 우월성)
            # 🍪 v1.0: 키워드 매칭 강화
            if query:
                content_str = str(memory['content']).lower()
                query_lower = query.lower()
                
                # 정확히 포함되면 높은 점수
                if query_lower in content_str:
                    score += 2.0  # 🍪 v1.0: 점수 증가 (1.0 → 2.0)
                # 부분 매칭
                else:
                    # 단어 단위 매칭
                    query_words = set(query_lower.split())
                    content_words = set(content_str.split())
                    overlap = len(query_words & content_words)
                    if overlap > 0:
                        # 🍪 v1.0: 매칭 비율에 따라 점수 증가
                        match_ratio = overlap / len(query_words)
                        score += match_ratio * 1.0  # 0.5 → 1.0
                    
                    # 🍪 v1.0: 첫 단어 매칭 보너스
                    query_first_word = query_lower.split()[0] if query_lower.split() else ""
                    if query_first_word and query_first_word in content_str:
                        score += 0.5
            else:
                score = 0.5  # 쿼리 없으면 기본 점수
            
            # Surface 가중치 (떠오르기 쉬운 정도)
            surface = self._surface.get(memory_id, 0.5)
            
            if include_deep:
                # AI 모드: surface와 관계없이 완벽히 recall
                # surface는 정렬 우선순위에만 약간 영향
                score = score * 0.9 + surface * 0.1
            else:
                # 사람 모드: surface 낮으면 recall 어려움
                score = score * surface
            
            # Importance 가중치
            importance = self._importance.get(memory_id, 0.5)
            score *= (1.0 + importance * 0.5)
            
            # 접근 빈도 가중치
            access = self._access_count.get(memory_id, 0)
            score *= (1.0 + min(0.3, access * 0.01))
            
            if score > 0:
                scored.append((memory_id, score))
        
        # Step 3: 정렬 및 반환
        scored.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for memory_id, score in scored[:top_n]:
            memory = self._archive[memory_id].copy()
            memory['recall_score'] = score
            memory['surface'] = self._surface.get(memory_id, 0.5)
            memory['importance'] = self._importance.get(memory_id, 0.5)
            memory['access_count'] = self._access_count.get(memory_id, 0)
            
            # Access 기록 업데이트
            self._access_count[memory_id] += 1
            self._last_access[memory_id] = time.time()
            
            # Surface 상승 (recall되면 더 떠오르기 쉬워짐)
            self._surface[memory_id] = min(1.0, 
                self._surface.get(memory_id, 0.5) + 0.1)
            
            results.append(memory)
        
        return results
    
    def recall_exact(self, memory_id: str) -> Optional[Dict]:
        """
        ID로 정확히 recall (AI 우월성 - 100% 정확)
        
        Returns:
            완벽한 원본 기억 (Archive에서)
        """
        if memory_id not in self._archive:
            return None
        
        # Access 기록
        self._access_count[memory_id] += 1
        self._last_access[memory_id] = time.time()
        self._surface[memory_id] = min(1.0, 
            self._surface.get(memory_id, 0.5) + 0.1)
        
        memory = self._archive[memory_id].copy()
        memory['surface'] = self._surface.get(memory_id, 0.5)
        memory['importance'] = self._importance.get(memory_id, 0.5)
        
        return memory
    
    # =========================================================
    # 🎬 BROWSE: 파노라마 탐색 (주마등)
    # =========================================================
    
    def browse_timeline(self, 
                        start_idx: int = 0, 
                        count: int = 20,
                        reverse: bool = True) -> List[Dict]:
        """
        타임라인 탐색 (파노라마 스크롤)
        
        Args:
            start_idx: 시작 인덱스
            count: 가져올 개수
            reverse: True면 최신순 (기본)
        
        Returns:
            시간순 기억 리스트
        
        🎬 인생의 필름을 스크롤하듯이
        """
        timeline = self._timeline[::-1] if reverse else self._timeline
        
        results = []
        for memory_id in timeline[start_idx:start_idx + count]:
            memory = self._archive[memory_id].copy()
            memory['surface'] = self._surface.get(memory_id, 0.5)
            memory['importance'] = self._importance.get(memory_id, 0.5)
            results.append(memory)
        
        return results
    
    def browse_context(self, context: str, top_n: int = 20) -> List[Dict]:
        """
        특정 맥락의 기억들 탐색
        
        Args:
            context: 맥락 (예: "childhood", "2024")
            top_n: 최대 개수
        
        🎬 "어린 시절" 필름만 따로 보기
        """
        memory_ids = self._contexts.get(context, [])
        
        results = []
        for memory_id in memory_ids[-top_n:]:
            memory = self._archive[memory_id].copy()
            memory['surface'] = self._surface.get(memory_id, 0.5)
            memory['importance'] = self._importance.get(memory_id, 0.5)
            results.append(memory)
        
        return results
    
    def browse_date(self, date_str: str) -> List[Dict]:
        """
        특정 날짜의 기억들
        
        Args:
            date_str: "YYYY-MM-DD" 형식
        
        🎬 "2020년 크리스마스" 찾아보기
        """
        memory_ids = self._time_index.get(date_str, [])
        
        results = []
        for memory_id in memory_ids:
            memory = self._archive[memory_id].copy()
            memory['surface'] = self._surface.get(memory_id, 0.5)
            results.append(memory)
        
        return results
    
    # =========================================================
    # 🔗 ASSOCIATE: 연상 (기억 간 연결)
    # =========================================================
    
    def associate(self, memory_id: str, top_n: int = 5) -> List[Dict]:
        """
        연관된 기억들 찾기
        
        Args:
            memory_id: 기준 기억
            top_n: 반환 개수
        
        Returns:
            연결된 기억들
        
        🔗 "이 기억과 연결된 다른 기억들"
        """
        if memory_id not in self._connections:
            return []
        
        connected_ids = self._connections[memory_id]
        
        # 점수 계산 (접근 빈도, importance 고려)
        scored = []
        for conn_id in connected_ids:
            if conn_id not in self._archive:
                continue
            
            score = 1.0
            score *= (1.0 + self._importance.get(conn_id, 0.5))
            score *= (1.0 + min(0.3, self._access_count.get(conn_id, 0) * 0.01))
            scored.append((conn_id, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for conn_id, score in scored[:top_n]:
            memory = self._archive[conn_id].copy()
            memory['association_score'] = score
            results.append(memory)
        
        return results
    
    def link(self, memory_id1: str, memory_id2: str):
        """두 기억을 연결"""
        if memory_id1 in self._archive and memory_id2 in self._archive:
            if memory_id2 not in self._connections[memory_id1]:
                self._connections[memory_id1].append(memory_id2)
            if memory_id1 not in self._connections[memory_id2]:
                self._connections[memory_id2].append(memory_id1)
    
    # =========================================================
    # ⏰ SURFACE DYNAMICS: 표면 접근성 변화
    # =========================================================
    
    def surface_decay(self, rate: float = 0.01):
        """
        표면 접근성 감쇠
        
        ⚠️ 중요: Archive의 기억은 절대 손상되지 않음!
        Surface만 감쇠 = "떠오르기 어려워질 뿐"
        AI는 include_deep=True로 언제든 완벽히 recall 가능
        
        Args:
            rate: 감쇠율
        """
        for memory_id in self._surface:
            importance = self._importance.get(memory_id, 0.5)
            access = self._access_count.get(memory_id, 0)
            
            # 중요하고 자주 접근한 기억은 덜 감쇠
            resistance = min(0.9, importance * 0.5 + min(0.4, access * 0.01))
            actual_rate = rate * (1.0 - resistance)
            
            # Surface 감쇠 (최소 0.01 유지 - 완전히 0은 안 됨)
            self._surface[memory_id] = max(0.01, 
                self._surface[memory_id] - actual_rate)
    
    def surface_boost(self, memory_id: str, amount: float = 0.2):
        """특정 기억의 surface 상승"""
        if memory_id in self._surface:
            self._surface[memory_id] = min(1.0, 
                self._surface[memory_id] + amount)
    
    # =========================================================
    # 📊 IMPORTANCE: 중요도 계산 (PageRank 스타일)
    # =========================================================
    
    def calculate_importance(self, iterations: int = 10):
        """
        모든 기억의 중요도 재계산
        
        PageRank 원리:
        - 많이 연결된 기억 = 중요
        - 중요한 기억과 연결된 기억 = 중요
        - 자주 접근된 기억 = 중요
        """
        if not self._archive:
            return
        
        # 초기화
        n = len(self._archive)
        scores = {mid: 1.0 / n for mid in self._archive}
        
        # PageRank iteration
        damping = 0.85
        for _ in range(iterations):
            new_scores = {}
            for memory_id in self._archive:
                # 연결된 기억들로부터 점수 받기
                incoming_score = 0.0
                for conn_id in self._connections.get(memory_id, []):
                    if conn_id in scores:
                        out_degree = len(self._connections.get(conn_id, [])) or 1
                        incoming_score += scores[conn_id] / out_degree
                
                new_scores[memory_id] = (1 - damping) / n + damping * incoming_score
            
            scores = new_scores
        
        # 정규화 및 저장
        max_score = max(scores.values()) if scores else 1.0
        for memory_id, score in scores.items():
            # PageRank + 접근 빈도 + 기존 importance 혼합
            normalized = score / max_score
            access_bonus = min(0.3, self._access_count.get(memory_id, 0) * 0.01)
            
            self._importance[memory_id] = min(1.0, 
                normalized * 0.6 + 
                self._importance.get(memory_id, 0.5) * 0.3 +
                access_bonus)
    
    # =========================================================
    # 💾 PERSISTENCE: 저장/로드
    # =========================================================
    
    def save(self, path: str = None):
        """파노라마 저장"""
        if path is None:
            save_dir = Path.home() / ".babyhippo" / "panorama"
            save_dir.mkdir(parents=True, exist_ok=True)
            path = str(save_dir / f"{self.name}.json")
        
        data = {
            'version': self.VERSION,
            'name': self.name,
            'created_at': self.created_at,
            'saved_at': time.time(),
            
            # 핵심 데이터
            'archive': self._archive,
            'timeline': self._timeline,
            'time_index': dict(self._time_index),
            'surface': self._surface,
            'connections': dict(self._connections),
            'contexts': dict(self._contexts),
            
            # 메타데이터
            'access_count': dict(self._access_count),
            'last_access': self._last_access,
            'importance': self._importance,
            'memory_counter': self._memory_counter,
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return path
    
    def load(self, path: str = None):
        """파노라마 로드"""
        if path is None:
            path = str(Path.home() / ".babyhippo" / "panorama" / f"{self.name}.json")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.name = data.get('name', self.name)
        self.created_at = data.get('created_at', time.time())
        
        self._archive = data.get('archive', {})
        self._timeline = data.get('timeline', [])
        self._time_index = defaultdict(list, data.get('time_index', {}))
        self._surface = data.get('surface', {})
        self._connections = defaultdict(list, data.get('connections', {}))
        self._contexts = defaultdict(list, data.get('contexts', {}))
        
        self._access_count = defaultdict(int, data.get('access_count', {}))
        self._last_access = data.get('last_access', {})
        self._importance = data.get('importance', {})
        self._memory_counter = data.get('memory_counter', 0)
    
    # =========================================================
    # 📈 STATS: 통계
    # =========================================================
    
    def get_stats(self) -> Dict:
        """파노라마 통계"""
        if not self._archive:
            return {
                'total_memories': 0,
                'contexts': [],
                'timeline_span': None,
            }
        
        # 시간 범위
        times = [m['created_at'] for m in self._archive.values()]
        
        return {
            'version': self.VERSION,
            'name': self.name,
            'total_memories': len(self._archive),
            'contexts': list(self._contexts.keys()),
            'num_contexts': len(self._contexts),
            'num_connections': sum(len(c) for c in self._connections.values()) // 2,
            'timeline_span': {
                'start': min(times),
                'end': max(times),
                'days': (max(times) - min(times)) / 86400
            },
            'avg_surface': np.mean(list(self._surface.values())) if self._surface else 0,
            'avg_importance': np.mean(list(self._importance.values())) if self._importance else 0,
            'total_accesses': sum(self._access_count.values()),
        }
    
    def __repr__(self):
        return f"PanoramaMemory('{self.name}', {len(self._archive)} memories)"
    
    def __len__(self):
        return len(self._archive)


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Panorama Memory Test")
    print("=" * 60)
    
    # 파노라마 생성
    panorama = PanoramaMemory("my_life")
    
    # 기억 저장
    print("\n📝 Storing memories...")
    
    m1 = panorama.store(
        content="7살 크리스마스, 산타 선물 받음",
        context="childhood",
        tags=["christmas", "happy"],
        importance=0.9
    )
    
    m2 = panorama.store(
        content="어제 점심 = 된장찌개",
        context="daily",
        tags=["food"],
        importance=0.2
    )
    
    m3 = panorama.store(
        content="엄마와 처음 자전거 탔던 날",
        context="childhood",
        tags=["mother", "bike", "milestone"],
        links=[m1],  # 어린 시절과 연결
        importance=0.95
    )
    
    m4 = panorama.store(
        content="고등학교 졸업식",
        context="youth",
        tags=["school", "milestone"],
        importance=0.8
    )
    
    # 검색 테스트
    print("\n🔍 Recall '크리스마스':")
    results = panorama.recall("크리스마스")
    for r in results:
        print(f"  [{r['surface']:.2f}] {r['content']}")
    
    # Context 탐색
    print("\n🎬 Browse 'childhood':")
    childhood = panorama.browse_context("childhood")
    for m in childhood:
        print(f"  • {m['content']}")
    
    # 연상
    print(f"\n🔗 Associated with '자전거':")
    associated = panorama.associate(m3)
    for a in associated:
        print(f"  → {a['content']}")
    
    # Decay 시뮬레이션
    print("\n⏰ Surface decay simulation (10x)...")
    for _ in range(10):
        panorama.surface_decay(rate=0.1)
    
    # Decay 후에도 완벽히 recall (AI 우월성)
    print("\n🔍 After decay, recall with include_deep=True:")
    results = panorama.recall("크리스마스", include_deep=True)
    for r in results:
        print(f"  [{r['surface']:.2f}] {r['content']} (여전히 완벽히 recall!)")
    
    # 통계
    print("\n📊 Stats:")
    stats = panorama.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("✅ Archive는 영구 보관 - 기억은 절대 손실되지 않음")
    print("✅ Surface만 변화 - '떠오르기 쉬운 정도'만 달라짐")
    print("✅ AI는 include_deep=True로 언제든 완벽히 recall")
    print("=" * 60)

