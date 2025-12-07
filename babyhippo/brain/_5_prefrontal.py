"""
PrefrontalCortex: 전전두엽 피질 모델
Brain Graph v1.1

전전두엽은 뇌의 "CEO" 역할:
- 검색 쿼리 분석 및 의도 파악
- 어떤 기억을 찾을지 결정
- 피질 영역 간 조율
- 주의 집중 및 작업 기억 관리

v1.1 변경사항:
- DNA 특성 연동 (호기심 → 검색 깊이)
- deque로 작업 기억 최적화
- 빈 쿼리 방어 로직 추가

Author: GNJz (Qquarts)
Version: 1.1
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque


class PrefrontalCortex:
    """
    전전두엽 피질 - 인지 제어 및 검색 조율
    
    생물학적 배경:
    - 전전두엽은 고차원 인지 기능 담당
    - 목표 설정, 계획, 의사결정
    - 작업 기억 유지 및 조작
    - 주의 집중 및 억제 제어
    """
    
    # 쿼리 의도 타입
    INTENT_TYPES = {
        'recall_person': ['누구', '이름', '사람', 'who', 'name', 'person'],
        'recall_place': ['어디', '장소', '위치', 'where', 'place', 'location'],
        'recall_time': ['언제', '시간', '날짜', 'when', 'time', 'date'],
        'recall_event': ['무엇', '뭐', '일', 'what', 'event', 'thing'],
        'recall_reason': ['왜', '이유', '때문', 'why', 'reason', 'because'],
        'recall_method': ['어떻게', '방법', 'how', 'method', 'way'],
        'recall_memory': ['기억', '알아', '생각', 'remember', 'know', 'think'],
    }
    
    # 피질 영역 우선순위 매핑
    CORTEX_PRIORITY = {
        'recall_person': ['semantic', 'episodic', 'emotional'],
        'recall_place': ['semantic', 'visual', 'episodic'],
        'recall_time': ['episodic', 'semantic'],
        'recall_event': ['episodic', 'semantic', 'emotional'],
        'recall_reason': ['semantic', 'episodic'],
        'recall_method': ['semantic', 'episodic'],
        'recall_memory': ['episodic', 'semantic', 'emotional', 'visual', 'auditory'],
    }
    
    def __init__(self, working_memory_size: int = 7, dna_traits: Optional[Dict] = None):
        """
        전전두엽 초기화 (DNA 특성 반영)
        
        Args:
            working_memory_size: 작업 기억 용량 (마법의 숫자 7±2)
            dna_traits: DNA 특성 (성격에 따른 지능 조절)
                        예: {'drive_weights': {'curiosity': 2.0}}
        
        Note:
            v1.1: DNA 특성 연동 (Stem Code 철학)
            - 호기심 높으면 → 검색 깊이↑, 작업 기억↑
            - 호기심 낮으면 → 검색 얕게, 빠른 판단
        """
        self.working_memory_size = working_memory_size
        self.search_depth_bias = 0  # 검색 깊이 보정값
        
        # [v1.1] DNA 특성에 따른 지능 설정
        if dna_traits:
            # 호기심이 많으면 검색을 더 깊게 함
            curiosity = dna_traits.get('drive_weights', {}).get('curiosity', 1.0)
            if curiosity > 1.5:
                self.working_memory_size += 2  # 작업 기억 확장
                self.search_depth_bias = 2     # 검색 깊이 증가
            elif curiosity < 0.8:
                self.working_memory_size = max(3, self.working_memory_size - 2)
                self.search_depth_bias = -1    # 검색 얕게
        
        # [v1.1] deque로 최적화 (O(1) 삽입)
        self.working_memory: deque = deque(maxlen=self.working_memory_size)
        
        # 목표 스택: 현재 수행 중인 목표들
        self.goal_stack: List[str] = []
        
        # 주의 집중: 어떤 피질에 집중할지
        self.attention_focus: Dict[str, float] = defaultdict(lambda: 0.5)
        
        # 최근 쿼리 기록 (컨텍스트 유지)
        self.query_history: List[Dict] = []
        self.max_history = 10
        
        # 검색 전략
        self.search_strategy = 'balanced'  # 'balanced', 'depth_first', 'breadth_first'
    
    def analyze_query(self, query: str) -> Dict:
        """
        쿼리 분석 - 의도, 키워드, 우선순위 파악
        
        Args:
            query: 사용자 쿼리
        
        Returns:
            analysis: 분석 결과
        """
        # [v1.1] 빈 쿼리 방어
        if not query or not query.strip():
            return {
                'query': '',
                'intents': ['recall_memory'],
                'keywords': [],
                'cortex_priority': ['semantic', 'episodic'],
                'search_depth': 3,
                'context': {'is_followup': False, 'related_queries': [], 'shared_keywords': []},
                'expanded_queries': [],
            }
        
        query_lower = query.lower()
        
        # 1. 의도 파악
        intents = []
        for intent_type, keywords in self.INTENT_TYPES.items():
            for keyword in keywords:
                if keyword in query_lower:
                    intents.append(intent_type)
                    break
        
        # 기본 의도
        if not intents:
            intents = ['recall_memory']
        
        # 2. 키워드 추출
        keywords = self._extract_keywords(query)
        
        # 3. 피질 우선순위 결정
        cortex_priority = self._determine_cortex_priority(intents)
        
        # 4. 검색 깊이 결정
        search_depth = self._determine_search_depth(query)
        
        # 5. 컨텍스트 분석 (이전 쿼리 참조)
        context = self._analyze_context(query)
        
        analysis = {
            'query': query,
            'intents': intents,
            'keywords': keywords,
            'cortex_priority': cortex_priority,
            'search_depth': search_depth,
            'context': context,
            'expanded_queries': self._expand_query(query, keywords),
        }
        
        # 쿼리 기록 저장
        self._record_query(analysis)
        
        return analysis
    
    def query_hippocampus(self, hippocampus, query: str, analysis: Dict = None) -> List[Dict]:
        """
        해마에 검색 요청
        
        Args:
            hippocampus: HippoMemory 인스턴스
            query: 검색 쿼리
            analysis: 쿼리 분석 결과 (없으면 자동 분석)
        
        Returns:
            results: 검색 결과
        """
        if analysis is None:
            analysis = self.analyze_query(query)
        
        all_results = []
        seen_ids = set()
        
        # 확장된 쿼리들로 검색
        queries = [query] + analysis.get('expanded_queries', [])
        
        for q in queries:
            try:
                results = hippocampus.recall(q, top_n=analysis['search_depth'])
                for word_id, score in results:
                    if word_id not in seen_ids:
                        all_results.append({
                            'word_id': word_id,
                            'score': score,
                            'query': q,
                        })
                        seen_ids.add(word_id)
            except Exception as e:
                continue
        
        # 점수로 정렬
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # 작업 기억에 저장
        self._update_working_memory(all_results[:self.working_memory_size])
        
        return all_results[:analysis['search_depth'] * 2]
    
    def coordinate_retrieval(self, cortex_nodes: Dict, hippo_results: List[Dict], analysis: Dict) -> Dict:
        """
        피질 검색 조율 - 어떤 피질에서 무엇을 가져올지 결정
        
        Args:
            cortex_nodes: 피질 노드들 {'visual': VisualCortex, ...}
            hippo_results: 해마 검색 결과
            analysis: 쿼리 분석 결과
        
        Returns:
            retrieval_plan: 검색 계획
        """
        retrieval_plan = {
            'cortex_order': analysis['cortex_priority'],
            'indices_per_cortex': {},
            'attention_weights': {},
        }
        
        # 해마 결과에서 인덱스 추출
        indices = [r['word_id'] for r in hippo_results]
        
        # 각 피질별 검색 계획
        for i, cortex_type in enumerate(analysis['cortex_priority']):
            if cortex_type in cortex_nodes:
                # 우선순위에 따른 가중치
                weight = 1.0 / (i + 1)
                retrieval_plan['attention_weights'][cortex_type] = weight
                
                # 검색할 인덱스 수 결정
                n_indices = max(1, int(len(indices) * weight))
                retrieval_plan['indices_per_cortex'][cortex_type] = indices[:n_indices]
        
        return retrieval_plan
    
    def filter_results(self, results: List[Dict], analysis: Dict) -> List[Dict]:
        """
        결과 필터링 및 정렬
        
        Args:
            results: 수집된 모든 결과
            analysis: 쿼리 분석 결과
        
        Returns:
            filtered: 필터링된 결과
        """
        if not results:
            return []
        
        keywords = set(analysis.get('keywords', []))
        
        # 관련성 점수 계산
        scored_results = []
        for result in results:
            relevance = self._calculate_relevance(result, keywords, analysis)
            result['relevance'] = relevance
            scored_results.append(result)
        
        # 관련성으로 정렬
        scored_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # 상위 결과만 반환
        return scored_results[:analysis['search_depth']]
    
    def integrate_fragments(self, fragments: Dict[str, List]) -> Dict:
        """
        여러 피질에서 가져온 조각들을 통합
        
        Args:
            fragments: {'visual': [...], 'semantic': [...], ...}
        
        Returns:
            integrated: 통합된 기억
        """
        integrated = {
            'content': [],
            'features': {},
            'sources': [],
            'confidence': 0.0,
        }
        
        total_weight = 0
        
        for cortex_type, frags in fragments.items():
            if not frags:
                continue
            
            weight = self.attention_focus.get(cortex_type, 0.5)
            
            for frag in frags:
                integrated['content'].append(frag.get('fragment', ''))
                integrated['sources'].append(cortex_type)
                integrated['confidence'] += frag.get('activation', 0.5) * weight
                total_weight += weight
        
        # 정규화
        if total_weight > 0:
            integrated['confidence'] /= total_weight
        
        return integrated
    
    def update_attention(self, cortex_type: str, success: bool):
        """
        주의 집중 업데이트 (학습)
        
        Args:
            cortex_type: 피질 유형
            success: 검색 성공 여부
        """
        if success:
            self.attention_focus[cortex_type] = min(1.0, self.attention_focus[cortex_type] + 0.1)
        else:
            self.attention_focus[cortex_type] = max(0.1, self.attention_focus[cortex_type] - 0.05)
    
    def set_goal(self, goal: str):
        """목표 설정"""
        self.goal_stack.append(goal)
    
    def complete_goal(self) -> Optional[str]:
        """목표 완료"""
        if self.goal_stack:
            return self.goal_stack.pop()
        return None
    
    def get_stats(self) -> Dict:
        """전전두엽 통계"""
        return {
            'working_memory_items': len(self.working_memory),
            'working_memory_capacity': self.working_memory_size,
            'active_goals': len(self.goal_stack),
            'query_history_size': len(self.query_history),
            'attention_focus': dict(self.attention_focus),
            'search_strategy': self.search_strategy,
        }
    
    # ===== Private Methods =====
    
    def _extract_keywords(self, query: str) -> List[str]:
        """쿼리에서 키워드 추출"""
        # 불용어 제거
        stopwords = {'은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로',
                     '와', '과', '도', '만', '뿐', '요', '죠', '네', '야',
                     'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', 'shall'}
        
        # 단어 분리 (한글 + 영어)
        words = re.findall(r'[가-힣]+|[a-zA-Z]+|\d+', query)
        
        # 불용어 제거 및 필터링
        keywords = [w for w in words if w.lower() not in stopwords and len(w) > 1]
        
        return keywords
    
    def _determine_cortex_priority(self, intents: List[str]) -> List[str]:
        """의도에 따른 피질 우선순위 결정"""
        priority_scores = defaultdict(float)
        
        for intent in intents:
            if intent in self.CORTEX_PRIORITY:
                for i, cortex in enumerate(self.CORTEX_PRIORITY[intent]):
                    priority_scores[cortex] += 1.0 / (i + 1)
        
        # 점수로 정렬
        sorted_cortex = sorted(priority_scores.keys(), 
                               key=lambda x: priority_scores[x], 
                               reverse=True)
        
        # 기본값 추가
        all_cortex = ['semantic', 'episodic', 'emotional', 'visual', 'auditory']
        for cortex in all_cortex:
            if cortex not in sorted_cortex:
                sorted_cortex.append(cortex)
        
        return sorted_cortex
    
    def _determine_search_depth(self, query: str) -> int:
        """
        검색 깊이 결정
        
        v1.1: DNA 보정값 적용
        """
        # 쿼리 길이에 따라 조정
        if len(query) < 10:
            depth = 3
        elif len(query) < 30:
            depth = 5
        else:
            depth = 7
        
        # [v1.1] DNA 성격에 따른 보정
        return max(1, depth + self.search_depth_bias)
    
    def _analyze_context(self, query: str) -> Dict:
        """이전 쿼리들과의 컨텍스트 분석"""
        context = {
            'is_followup': False,
            'related_queries': [],
            'shared_keywords': [],
        }
        
        if not self.query_history:
            return context
        
        current_keywords = set(self._extract_keywords(query))
        
        for prev in self.query_history[-3:]:  # 최근 3개만
            prev_keywords = set(prev.get('keywords', []))
            shared = current_keywords & prev_keywords
            
            if shared:
                context['is_followup'] = True
                context['related_queries'].append(prev['query'])
                context['shared_keywords'].extend(list(shared))
        
        return context
    
    def _expand_query(self, query: str, keywords: List[str]) -> List[str]:
        """쿼리 확장"""
        expanded = []
        
        # 키워드 기반 확장
        for keyword in keywords[:3]:  # 상위 3개 키워드
            if keyword not in query:
                expanded.append(keyword)
        
        # 컨텍스트 기반 확장
        if self.query_history:
            last_query = self.query_history[-1]
            for kw in last_query.get('keywords', [])[:2]:
                if kw not in expanded and kw not in keywords:
                    expanded.append(kw)
        
        return expanded
    
    def _record_query(self, analysis: Dict):
        """쿼리 기록"""
        self.query_history.append({
            'query': analysis['query'],
            'keywords': analysis['keywords'],
            'intents': analysis['intents'],
        })
        
        # 최대 기록 수 유지
        if len(self.query_history) > self.max_history:
            self.query_history.pop(0)
    
    def _update_working_memory(self, items: List[Dict]):
        """
        작업 기억 업데이트
        
        v1.1: deque 사용으로 O(1) 삽입
        """
        for item in items:
            # 중복 검사 (deque는 O(N)이지만 N이 작으므로(7) 괜찮음)
            exists = any(
                wm.get('word_id') == item.get('word_id') 
                for wm in self.working_memory
            )
            if not exists:
                # deque.appendleft는 O(1), maxlen이 자동으로 오래된 항목 제거
                self.working_memory.appendleft(item)
    
    def _calculate_relevance(self, result: Dict, keywords: set, analysis: Dict) -> float:
        """결과의 관련성 점수 계산"""
        relevance = result.get('score', 0.5)
        
        # 키워드 매칭 보너스 (v0.3: content 키 우선 사용)
        content = str(result.get('content', result.get('fragment', ''))).lower()
        for keyword in keywords:
            if keyword.lower() in content:
                relevance += 0.1
        
        # 활성화 수준 반영
        relevance *= (1 + result.get('activation', 0.5))
        
        return min(1.0, relevance)

