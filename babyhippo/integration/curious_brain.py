"""
CuriousBrain: 모든 걸 알고 싶은 AI

🎯 철학:
    모든 걸 아는 AI ❌
    모든 걸 알고 싶은 AI ⭕
    
    대형 도서관(LLM)을 활용하면서
    자신만의 지식을 쌓아가는 구조

구조:
    1. 질문 발생
    2. 내 기억(해마) 먼저 검색
    3. 모르면 → 도서관(대형 LLM) 방문
    4. 배운 것 → 해마 저장 → 개인 LLM 전이
    5. 점점 성장 → 도서관 의존도 ↓

Author: GNJz (Qquarts)
Version: 1.0
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# 경로 설정
BABYHIPPO_PATH = Path(__file__).parent.parent
NANOGPT_PATH = BABYHIPPO_PATH.parent / "nanoGPT"

# 모듈 임포트 (새 구조)
from .brain_llm import BrainLLM, HippoToLLM
from .hippo_evolution import (
    HippoEvolutionSystem,
    EVOLUTION_STAGES,
    NetworkFeature,
    NeuronModel,
    create_evolution_system,
)
from .brain_capability import (
    BrainCapabilitySchema,
    CapabilityCategory,
    create_default_schema,
)

# 대형 LLM API (도서관)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class LearnedKnowledge:
    """학습한 지식"""
    question: str
    answer: str
    source: str  # 'memory', 'library', 'personal_llm'
    confidence: float
    learned_at: float = field(default_factory=time.time)
    access_count: int = 0


class LibraryConnector:
    """
    대형 도서관 연결 (외부 LLM API)
    
    세상의 거의 모든 지식에 접근
    """
    
    PROVIDERS = {
        'openai': {
            'models': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'env_key': 'OPENAI_API_KEY',
        },
        'anthropic': {
            'models': ['claude-sonnet-4-20250514', 'claude-3-haiku-20240307'],
            'env_key': 'ANTHROPIC_API_KEY',
        },
        'local': {
            'models': ['nanoGPT'],
            'env_key': 'NANOGPT_SERVER_URL',  # 예: http://192.168.1.100:5000
        },
    }
    
    def __init__(self, provider: str = 'openai', model: str = None):
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.client = None
        self._setup_client()
        
        # 사용 통계
        self.visit_count = 0
        self.total_tokens = 0
    
    def _get_default_model(self, provider: str) -> str:
        if provider == 'openai':
            return 'gpt-3.5-turbo'  # 저렴한 모델 기본
        elif provider == 'anthropic':
            return 'claude-3-haiku-20240307'
        elif provider == 'local':
            return 'nanoGPT'
        return 'gpt-3.5-turbo'
    
    def _setup_client(self):
        """API 클라이언트 설정"""
        if self.provider == 'openai' and HAS_OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)
        elif self.provider == 'anthropic' and HAS_ANTHROPIC:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
        elif self.provider == 'local':
            # 로컬 nanoGPT 서버 URL
            self.server_url = os.getenv('NANOGPT_SERVER_URL', 'http://localhost:5000')
            if HAS_REQUESTS:
                self.client = 'local'  # requests 사용
    
    def ask(self, question: str, context: str = "") -> Tuple[str, bool]:
        """
        도서관에 질문
        
        Args:
            question: 질문
            context: 추가 맥락
            
        Returns:
            (답변, 성공여부)
        """
        if not self.client:
            return "[도서관 연결 안됨]", False
        
        self.visit_count += 1
        
        # 프롬프트 구성
        system_prompt = """당신은 지식 도서관입니다. 
질문에 간결하고 정확하게 답변해주세요.
모르는 것은 모른다고 솔직히 말해주세요."""
        
        user_prompt = question
        if context:
            user_prompt = f"맥락: {context}\n\n질문: {question}"
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content
                self.total_tokens += response.usage.total_tokens
                return answer, True
                
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                answer = response.content[0].text
                return answer, True
            
            elif self.provider == 'local' and HAS_REQUESTS:
                # 로컬 nanoGPT 서버 호출
                response = requests.post(
                    f"{self.server_url}/generate",
                    json={
                        "prompt": user_prompt,
                        "max_tokens": 200,
                        "temperature": 0.8,
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('new_text', result.get('generated', ''))
                    return answer, True
                else:
                    return f"[서버 오류: {response.status_code}]", False
                
        except Exception as e:
            return f"[도서관 오류: {e}]", False
        
        return "[지원하지 않는 제공자]", False
    
    def get_stats(self) -> Dict:
        return {
            'provider': self.provider,
            'model': self.model,
            'connected': self.client is not None,
            'visit_count': self.visit_count,
            'total_tokens': self.total_tokens,
        }


class CuriousBrain:
    """
    호기심 있는 뇌 - 모든 걸 알고 싶은 AI
    
    구조:
        해마 (기억) + 개인 LLM + 대형 도서관
        
    학습 흐름:
        1. 내 기억에서 찾기
        2. 없으면 도서관 방문
        3. 배운 것 저장
        4. 수면 시 개인 LLM 전이
        5. 점점 성장!
    """
    
    def __init__(self, 
                 name: str = "curious",
                 library_provider: str = 'openai',
                 library_model: str = None,
                 personal_model_path: str = None):
        """
        Args:
            name: 뇌 이름
            library_provider: 도서관 제공자 ('openai', 'anthropic')
            library_model: 도서관 모델
            personal_model_path: 개인 LLM 체크포인트 경로
        """
        self.name = name
        
        # 1. 해마 + 개인 LLM
        model_path = personal_model_path
        if model_path is None:
            default_path = NANOGPT_PATH / "out-hippo" / "ckpt.pt"
            if default_path.exists():
                model_path = str(default_path)
        
        self.brain = BrainLLM(model_path=model_path)
        
        # 2. 대형 도서관 연결
        self.library = LibraryConnector(
            provider=library_provider,
            model=library_model
        )
        
        # 3. 학습 기록
        self.knowledge_base: Dict[str, LearnedKnowledge] = {}
        
        # 🍪 v1.1: 대화 맥락 관리
        self.conversation_context: List[Dict] = []  # 최근 대화 기록
        self.max_context = 10  # 최근 10턴 기억
        self.last_learning: Optional[str] = None  # 마지막 학습 내용
        self.last_question: Optional[str] = None  # 마지막 질문 (연속 질문 처리용)
        
        # 4. 설정
        # 🍪 저전력 모드: 라즈베리파이/엣지 디바이스 최적화
        # 기본적으로 개인 LLM 비활성화 (발열/전력 소비 최소화)
        self.config = {
            'memory_threshold': 0.6,  # 이 이상이면 기억에서 답변
            'learn_from_library': True,  # 도서관 답변 학습 여부
            'auto_consolidate': True,  # 자동 공고화
            'use_personal_llm': False,  # 🍪 저전력 모드: 개인 LLM 기본 비활성화 (발열/전력 절약)
        }
        
        # 5. 통계
        self.stats = {
            'questions_asked': 0,
            'answered_from_memory': 0,
            'answered_from_library': 0,
            'answered_from_personal_llm': 0,
            'answered_from_quick': 0,  # 💰 빠른 응답 (비용 절약)
        }
        
        # 🦛 6. 진화 시스템 및 내부 상태 플래그
        # 블록체인은 선택적 계층 (기본: False, 독립형 시스템)
        self.evolution_system = create_evolution_system(blockchain_enabled=False)
        
        # 🧩 BrainCapability Schema (확장 가능한 능력 플래그)
        self.capability_schema = create_default_schema()
        
        # 내부 상태 플래그 (기술적 요구사항 추적) - 하위 호환성
        self.internal_flags = {
            'neuron_count': 0,  # 실제 뉴런 수
            'fps': 0.0,  # 현재 FPS
            'axon_nodes': 0,  # Axon 노드 수
            'features': set(),  # 구현된 기능 플래그
            'models': set(),  # 사용 중인 뉴런 모델
            'stability_test_passed': False,
            'robustness_test_passed': False,
        }
        
        # 초기 상태 설정 (BabyHippo 기본)
        self._update_internal_flags()
        self._update_capability_schema()
    
    # 💰 비용 관리: 간단한 질문은 도서관(API) 안 감
    QUICK_RESPONSES = {
        # 인사
        '안녕': '안녕하세요! 😊',
        'hi': 'Hello! 😊',
        'hello': 'Hi there! 😊',
        # 감사
        '고마워': '천만에요! 😊',
        '감사': '별말씀을요! 😊',
        'thanks': "You're welcome! 😊",
        # 작별
        '잘 자': '잘 자요! 좋은 꿈 꿔요 💤',
        '잘자': '잘 자요! 💤',
        'bye': 'Goodbye! 👋',
        # 안부
        '뭐해': '공부하고 있어요! 📚',
        '뭐하고 있어': '열심히 배우고 있어요! 🧠',
        # 감탄
        '대단해': '헤헤, 감사해요! 😊',
        '잘했어': '고마워요! 더 열심히 할게요! 💪',
        # 확인
        '알겠어': '네! 😊',
        '그래': '네네~ 😊',
        'ok': 'Okay! 👍',
        # 호칭
        '누구야': '저는 babyhippo예요! 모든 걸 알고 싶은 AI랍니다 🦛',
        '이름이 뭐야': '저는 babyhippo예요! 🦛',
        # 🍪 v1.0: 추가 응답
        '쿠키': '네, 저예요! 🍪',
        '히포': '네, 저예요! 🦛',
    }
    
    def think(self, question: str) -> str:
        """
        생각하기 (질문에 답하기)
        
        순서:
        0. 🍪 v1.0: 자연어 학습 명령 자동 감지
        1. 간단한 질문 → 즉시 응답 (비용 절약) 💰
        2. 해마(기억)에서 검색
        3. 없으면 → 개인 LLM 시도
        4. 그래도 없으면 → 도서관 방문
        5. 배운 것 저장
        
        Args:
            question: 질문 또는 학습 명령
            
        Returns:
            답변
        """
        self.stats['questions_asked'] += 1
        
        # 0. 🍪 v1.2: 질문 감지 최우선 (학습보다 먼저)
        # 질문과 학습 명령을 정확히 구분
        
        question_clean = question.strip()
        
        # 🍪 v1.5: 질문 패턴 감지 강화 (최우선)
        # 질문이면 절대 학습으로 처리하지 않음
        
        # 1단계: 명확한 질문 마커 (최우선)
        has_question_marker = (
            '?' in question or
            question_clean.endswith('?') or
            question_clean.endswith('요?') or
            question_clean.endswith('야?')
        )
        
        # 2단계: 의문사 포함
        has_interrogative = any(word in question for word in [
            '뭐', '무엇', '어떻게', '언제', '어디', '누구', '왜', '기억나', '기억해'
        ])
        
        # 3단계: 질문 패턴
        is_question_pattern = (
            question_clean in ['나는?', '너는?', '나이는?', '이름은?', '이름이?', '내이름은?', '너이름은?', 
                              '나의 이름은?', '당신의 이름은?', '우리의 이름은?', '그대의 이름은?'] or
            question_clean.endswith('는?') or
            question_clean.endswith('은?') or
            question_clean.endswith('이가?') or
            question_clean.endswith('이가?') or
            question_clean.endswith('의 이름은?') or
            question_clean.endswith('의 이름이?')
        )
        
        # 4단계: "이름" + 질문 마커
        has_name_question = (
            '이름' in question and 
            (has_question_marker or has_interrogative or '기억나' in question)
        )
        
        # 5단계: "너", "당신", "쿠키" 포함 + 질문 마커
        has_you_question = (
            ('너' in question or '당신' in question or '쿠키' in question or '그대' in question or '우리' in question) and
            (has_question_marker or has_interrogative)
        )
        
        # 최종 질문 판단
        is_question = (
            has_question_marker or
            has_interrogative or
            is_question_pattern or
            has_name_question or
            has_you_question
        )
        
        # 🍪 v1.2: 질문이면 절대 학습으로 처리하지 않음
        if is_question:
            # 질문 처리로 넘어감 (아래 코드 계속)
            pass
        else:
            # 학습 명령 패턴 (명확한 자기소개만)
            learning_patterns = [
                '라고 해', '라고 해요', '라고 합니다',
            ]
            
            # 🍪 v1.2: "내 이름은 GNJz" 같은 패턴은 학습 명령
            # 하지만 질문이 아니고, 실제 내용이 있어야 함
            name_intro_patterns = ['내 이름은', '나는', '저는', '내가', '제가']
            has_name_intro = any(pattern in question for pattern in name_intro_patterns)
            
            # 실제 내용이 있는지 확인
            # "내 이름은 GNJz" (내용 있음) vs "내 이름은" (내용 없음)
            has_actual_content = False
            if has_name_intro:
                for pattern in name_intro_patterns:
                    if pattern in question:
                        after_pattern = question.split(pattern, 1)[-1].strip()
                        # 패턴 이후에 실제 내용이 있는지 (단어가 있고, 질문 마커가 아님)
                        if after_pattern and len(after_pattern) > 0:
                            # 질문 마커만 있으면 내용 없음
                            if after_pattern not in ['?', '뭐', '무엇', '뭐야', '무엇이야', '기억나', '기억해']:
                                # 실제 단어가 있는지 확인 (최소 1글자 이상)
                                if len(after_pattern.replace(' ', '')) > 0:
                                    has_actual_content = True
                        break
            
            # 학습 명령 감지 조건:
            # 1. "라고 해" 패턴이 있고 질문이 아니거나
            # 2. 이름 소개 패턴이 있고, 질문이 아니고, 실제 내용이 있을 때
            is_learning_command = (
                (any(pattern in question for pattern in learning_patterns) and not is_question) or
                (has_name_intro and not is_question and has_actual_content)
            )
            
            # 학습 명령으로 처리
            if is_learning_command:
                # 🛑 치명적 충돌 해결 #1: 질문 필터링 (이중 체크)
                if not self._is_question_strict(question):
                    # 학습 명령으로 처리
                    self.learn(question, importance=0.8)
                
                # 🍪 v1.1: 마지막 학습 내용 저장 (오류 수정용)
                self.last_learning = question
                
                # 🍪 v1.0: 학습 후 즉시 확인 가능하도록 응답 개선
                # 이름 추출 시도
                name = None
                if '라고 해' in question:
                    # "나는 GNJz라고 해" → "GNJz" 추출
                    parts = question.split('라고 해')
                    if parts:
                        name_part = parts[0].strip()
                        # "나는", "저는" 등 제거
                        for prefix in ['나는', '저는', '내가', '제가']:
                            if name_part.startswith(prefix):
                                name_part = name_part[len(prefix):].strip()
                        if name_part:
                            name = name_part
                elif '내 이름은' in question:
                    # "내 이름은 GNJz" → "GNJz" 추출
                    parts = question.split('내 이름은')
                    if len(parts) > 1:
                        name = parts[1].strip().replace('?', '').strip()
                
                # 🍪 v1.1: 맥락에 대화 기록 추가
                response = f"알겠어요! {name if name else '기억할게요'}! 😊"
                self._update_context(question, response, 'learning')
                
                # 적절한 응답 반환
                if name:
                    return f"알겠어요! {name}이라고 기억할게요! 😊"
                elif '이름' in question or '라고 해' in question:
                    return "알겠어요! 기억할게요! 😊"
                elif '기억' in question:
                    return "네, 기억할게요! 😊"
                else:
                    return "학습 완료! 😊"
        
        # 🍪 v1.1: 오류 수정 처리 ("아니야", "그게 아니야")
        correction_patterns = ['아니야', '그게 아니야', '틀렸어', '아니', '수정해']
        if any(pattern in question for pattern in correction_patterns):
            if self.last_learning:
                # 마지막 학습 내용 삭제/수정
                # (실제로는 기억에서 찾아서 삭제하거나 수정해야 함)
                self.last_learning = None
                return "알겠어요! 수정할게요. 다시 알려주세요! 😊"
            else:
                return "무엇을 수정하면 될까요?"
        
        # 🍪 v1.1: 특수 질문 처리 (맥락 기반)
        if question_clean == '너는?' or question_clean == '너는':
            # 쿠키 이름 답변
            return f"저는 {self.name}이에요! 😊"
        
        if '나이는?' in question or question_clean == '나이는?':
            # 나이 질문
            return "저는 아직 나이가 없어요. 하지만 계속 배우고 있어요! 😊"
        
        # 1. 💰 간단한 질문 필터 (도서관 비용 절약)
        question_lower = question.lower().strip()
        for pattern, response in self.QUICK_RESPONSES.items():
            if pattern in question_lower:
                self.stats['answered_from_quick'] += 1
                return response
        
        # 🍪 v1.3: 맥락 기반 질문 처리
        # 이전 대화를 참조하여 질문 이해
        contextual_question = self._enhance_with_context(question)
        
        # 1. 해마에서 검색
        # 🍪 v1.0: 키워드 추출 개선
        question_keywords = self._extract_keywords(contextual_question)
        
        # 🍪 v1.0: "내 이름 기억나?" 같은 질문 처리
        # "이름", "기억나" 같은 불용어 제거하고 실제 이름 찾기
        all_memories = []  # 초기화 (오류 방지)
        
        if '이름' in question or '기억나' in question:
            # 이름 관련 질문 → 모든 기억에서 이름 찾기
            # PanoramaMemory에서 이름 패턴 찾기
            name_results = self.brain.recall("이름", top_n=10)
            if name_results:
                if isinstance(name_results, list):
                    all_memories.extend(name_results)
                else:
                    all_memories.append({'source': 'hippo', 'content': name_results, 'score': 0.8})
            
            # "라고 해" 패턴으로도 검색
            if not all_memories:
                rago_results = self.brain.recall("라고 해", top_n=10)
                if rago_results:
                    if isinstance(rago_results, list):
                        all_memories.extend(rago_results)
                    else:
                        all_memories.append({'source': 'hippo', 'content': rago_results, 'score': 0.8})
        else:
            # 일반 검색
            for keyword in question_keywords:
                memories = self.brain.recall(keyword, top_n=5)
                if memories:
                    if isinstance(memories, list):
                        all_memories.extend(memories)
                    else:
                        all_memories.append({'source': 'hippo', 'content': memories, 'score': 0.8})
        
        # 중복 제거 및 점수 정렬
        seen = set()
        unique_memories = []
        for m in all_memories:
            content = str(m.get('content', ''))
            if content and content not in seen:
                seen.add(content)
                unique_memories.append(m)
        
        # 점수로 정렬
        unique_memories.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # 🍪 v1.0: all_memories 변수명 통일 (오류 방지)
        memories = unique_memories
        
        if memories:
            # 🍪 v1.0: Panorama 우선 (전체 문장 저장)
            panorama_memories = [m for m in memories if m.get('source') == 'panorama']
            if panorama_memories:
                best_memory = panorama_memories[0]
                confidence = best_memory.get('score', 0.5)
                
                # Panorama는 threshold 낮춤 (전체 문장이므로 더 정확)
                if confidence >= self.config['memory_threshold'] * 0.5:
                    self.stats['answered_from_memory'] += 1
                    best_content = best_memory.get('content', '')
                    if best_content:
                        # 📝 치명적 충돌 해결 #2: 출력 포맷팅 파이프라인 통과
                        raw_answer = str(best_content)
                        answer = self._format_output(raw_answer, question)
                        
                        # 질문이 아니고 완전한 문장인지 확인
                        if not self._is_question_strict(answer) and len(answer) > 5:
                            # 중복 제거
                            answer = self._clean_answer(answer, question_keywords)
                            self._record_knowledge(question, answer, 'memory', confidence)
                            return answer
            
            # HippoMemory 결과 사용
            best_memory = memories[0]
            confidence = best_memory.get('score', 0.5)
            
            if confidence >= self.config['memory_threshold']:
                # 충분히 확신 → 기억에서 답변
                self.stats['answered_from_memory'] += 1
                
                # 🍪 v1.0: 기억 기반 응답 문구 정리
                best_content = best_memory.get('content', '')
                if best_content:
                    # 🛑 치명적 충돌 해결 #1: 질문 필터링
                    content_str = str(best_content).strip()
                    if self._is_question_strict(content_str):
                        # 질문이면 다음 기억 찾기 또는 다른 처리
                        if len(memories) > 1:
                            # 다음 기억 시도
                            for next_memory in memories[1:]:
                                next_content = next_memory.get('content', '')
                                if next_content and not self._is_question_strict(str(next_content)):
                                    # 📝 치명적 충돌 해결 #2: 출력 포맷팅
                                    answer = self._format_output(str(next_content), question)
                                    if not self._is_question_strict(answer) and len(answer) > 5:
                                        answer = self._clean_answer(answer, question_keywords)
                                        self._record_knowledge(question, answer, 'memory', next_memory.get('score', 0.5))
                                        self._update_context(question, answer, 'memory')
                                        self.last_question = question
                                        return answer
                        # 질문만 있으면 모름
                        answer = "기억이 명확하지 않아요."
                    else:
                        # 📝 치명적 충돌 해결 #2: 출력 포맷팅 파이프라인 통과
                        answer = self._format_output(content_str, question)
                        if not self._is_question_strict(answer) and len(answer) > 5:
                            # 중복 제거
                            answer = self._clean_answer(answer, question_keywords)
                        else:
                            answer = "기억이 불완전합니다."
                else:
                    answer = "관련 기억이 있어요."
                
                # 최종 검증: 질문이 아니고 완전한 문장인지
                if not self._is_question_strict(answer) and len(answer) > 5:
                    self._record_knowledge(question, answer, 'memory', confidence)
                    # 🍪 v1.1: 맥락에 대화 기록 추가
                    self._update_context(question, answer, 'memory')
                    # 🍪 v1.3: 마지막 질문 저장
                    self.last_question = question
                    return answer
                else:
                    # 불완전한 답변이면 다음 단계로
                    pass
        
        # 2. 개인 LLM 시도 (간단한 응답 생성)
        if self.config.get('use_personal_llm', True) and self.brain.model is not None:
            # 개인 LLM으로 짧은 응답 생성
            try:
                personal_answer = self._generate_clean_response(question)
                
                if personal_answer:
                    self.stats['answered_from_personal_llm'] += 1
                    
                    # 기억에도 저장 (질문 제외)
                    # 🛑 치명적 충돌 해결 #1: 질문은 저장하지 않음
                    learning_content = f"A: {personal_answer[:100]}"
                    if not self._is_question_strict(learning_content):
                        self.brain.learn(
                            learning_content,
                            context="self_answer",
                            importance=0.6
                        )
                    
                    self._record_knowledge(question, personal_answer, 'personal_llm', 0.7)
                    return personal_answer
            except:
                pass
        
        # 3. 도서관 방문
        library_answer, success = self.library.ask(question)
        
        if success:
            self.stats['answered_from_library'] += 1
            
            # 배운 것 저장!
            if self.config['learn_from_library']:
                # 🛑 치명적 충돌 해결 #1: 질문은 저장하지 않음
                # Q: 질문 형식이 아닌, 답변만 저장
                learning_content = f"A: {library_answer[:300]}"
                if not self._is_question_strict(learning_content):
                    self.brain.learn(
                        learning_content,
                        context="library_learning",
                        importance=0.8  # 도서관 지식은 중요
                    )
            
            self._record_knowledge(question, library_answer, 'library', 0.9)
            
            # 자동 공고화
            if self.config['auto_consolidate']:
                self.brain.sleep(cycles=2)
            
            # 🍪 v1.1: 맥락에 대화 기록 추가
            self._update_context(question, library_answer, 'library')
            return f"📚 {library_answer}"
        
        # 4. 기억에서라도 뭔가 찾아보기
        # 🍪 v1.4: 실제 답변이 있을 때만 반환 (질문이나 빈 내용이면 도서관 가기)
        if memories and len(memories) > 0:
            contents = [m.get('content', '') for m in memories if m.get('content')]
            if contents:
                potential_answer = str(contents[0]).strip()
                # 🍪 v1.4: 질문이나 빈 내용이면 도서관 가기
                if potential_answer and len(potential_answer) > 0:
                    # 질문 패턴이 아니고, 실제 답변인지 확인
                    is_question = '?' in potential_answer or potential_answer.endswith('?') or '뭐' in potential_answer
                    is_empty = len(potential_answer.replace(' ', '').replace('?', '')) == 0
                    
                    if not is_question and not is_empty:
                        # 📝 치명적 충돌 해결 #2: 출력 포맷팅 파이프라인 통과
                        answer = self._format_output(potential_answer, question)
                        # 파편 필터링: 너무 짧거나 불완전한 답변 차단
                        if len(answer.strip()) < 3 or answer.strip() in ['나', '너', '그', '이', '저', '내', '다']:
                            # 파편이면 다음 단계로
                            pass
                        elif not self._is_question_strict(answer):
                            # 질문이 아니고 완전한 문장이면 반환
                            answer = self._clean_answer(answer, [])
                            self._update_context(question, answer, 'memory')
                            return answer
                # 질문이거나 빈 내용이면 도서관 가기 (아래 코드 계속)
        
        # 5. 아무것도 모름
        # 🍪 v1.3: 맥락 기반 fallback (이전 대화 참조)
        if self.conversation_context:
            # 최근 대화와 연관성 있는 답변 시도
            last_ctx = self.conversation_context[-1]
            if last_ctx.get('source') == 'learning':
                # 이전에 학습했으면 그것을 언급
                answer = "기억이 명확하지 않지만, 이전에 배운 내용이 있을 수 있어요."
            else:
                answer = "모르겠어요."
        else:
            answer = "모르겠어요."
        
        # 🍪 v1.1: 맥락에 대화 기록 추가
        self._update_context(question, answer, 'general')
        # 🍪 v1.3: 마지막 질문 저장
        self.last_question = question
        return answer
    
    def _format_output(self, raw_content: str, question: str = "") -> str:
        """
        📝 치명적 충돌 해결 #2: 출력 포맷팅 파이프라인
        
        해마에서 인출된 기억을 완전한 서술형 문장으로 변환
        
        예:
            "GNJz" → "당신의 이름은 GNJz입니다."
            "내" → "기억이 불완전합니다."
            "A" → "A는 알파벳 첫 글자입니다."
        """
        if not raw_content or len(raw_content.strip()) == 0:
            return "기억이 명확하지 않아요."
        
        content = raw_content.strip()
        
        # 1. 질문 필터링: 질문이면 변환하지 않음
        if self._is_question_strict(content):
            return "기억이 명확하지 않아요."
        
        # 2. 파편 필터링: 너무 짧거나 불완전한 내용
        if len(content) < 3:  # 최소 3글자 이상
            return "기억이 불완전합니다."
        
        # 3. 불완전한 단어 필터링 (강화)
        incomplete_words = [
            '내', '나', '너', '그', '이', '저', '다', '가', '를', '을', '는', '은',
            'di', 'is', 'the', 'a', 'an', 'it', 'he', 'she', 'we', 'you', 'they'
        ]
        if content.strip() in incomplete_words or content.strip().lower() in incomplete_words:
            return "기억이 불완전합니다."
        
        # 4. 단일 글자 필터링 (강화)
        if len(content.strip()) == 1:
            return "기억이 불완전합니다."
        
        # 6. 이미 완전한 문장인지 확인
        complete_endings = ['입니다', '이에요', '예요', '이야', '거야', '이다', 
                           '입니다.', '이에요.', '예요.', '이야.', '거야.', '이다.',
                           '.', '!', '?']
        if any(content.endswith(ending) for ending in complete_endings):
            # 이미 완전한 문장이면 그대로 반환 (중복 제거만)
            # 하지만 질문이면 필터링
            if self._is_question_strict(content):
                return "기억이 명확하지 않아요."
            return self._clean_answer(content, [])
        
        # 5. 학습 명령 형태의 기억 필터링 (Echo Effect 방지) - 강화
        # "나는GNJz 라고 해" 같은 날것 기억을 자연스러운 문장으로 변환
        learning_command_patterns = ['라고 해', '라고 해요', '라고 합니다', '라고해', '라고해요']
        for pattern in learning_command_patterns:
            if pattern in content:
                # 이름 추출
                name_part = content.split(pattern)[0].strip()
                # "나는", "저는" 등 제거
                for prefix in ['나는', '저는', '내가', '제가', '나는', '저는']:
                    if name_part.startswith(prefix):
                        name_part = name_part[len(prefix):].strip()
                # 띄어쓰기 제거 후 확인
                name_part_clean = name_part.replace(' ', '')
                if name_part_clean and len(name_part_clean) > 0:
                    # 질문이 아니고 실제 이름인지 확인
                    if not self._is_question_strict(name_part_clean):
                        return f"당신의 이름은 {name_part_clean}입니다."
                break
        
        # 7. 질문 키워드 기반 포맷팅
        question_lower = question.lower() if question else ""
        
        # 이름 관련 질문
        if '이름' in question_lower or 'name' in question_lower:
            if len(content) > 1 and content not in ['내', '나', '너', '그', '이', '저', '다']:
                # 이미 "당신의 이름은" 같은 형식이 아니면 추가
                if '이름' not in content and 'name' not in content.lower():
                    return f"당신의 이름은 {content}입니다."
                else:
                    # 이미 이름 정보가 포함되어 있으면 그대로 반환 (하지만 질문이면 필터링)
                    if self._is_question_strict(content):
                        return "기억이 명확하지 않아요."
                    return content
        
        # 8. 일반적인 답변 포맷팅
        # 기본: 그대로 반환하되, 완전한 문장으로 만들기
        if not any(content.endswith(ending) for ending in complete_endings):
            # 문장 종결어미가 없으면 추가
            return f"{content}입니다."
        
        # 최종 검증: 질문이면 필터링
        if self._is_question_strict(content):
            return "기억이 명확하지 않아요."
        
        return content
    
    def _clean_answer(self, answer: str, keywords: list) -> str:
        """
        🍪 v1.0: 답변 중복 제거
        
        예:
            "A는 A는 알파벳 첫 글자입니다." → "A는 알파벳 첫 글자입니다."
            "파이썬는 파이썬은..." → "파이썬은..."
        """
        if not answer:
            return answer
        
        # 일반적인 중복 패턴 제거
        import re
        
        # 키워드로 시작하는 중복 패턴 제거
        if keywords:
            for keyword in keywords:
                # "키워드는 키워드는" → "키워드는"
                patterns = [
                    (f"{keyword}는 {keyword}는", f"{keyword}는"),
                    (f"{keyword}은 {keyword}은", f"{keyword}은"),
                    (f"{keyword}가 {keyword}가", f"{keyword}가"),
                    (f"{keyword}이 {keyword}이", f"{keyword}이"),
                    (f"{keyword}는 {keyword}은", f"{keyword}은"),
                    (f"{keyword}은 {keyword}는", f"{keyword}는"),
                ]
                for pattern, replacement in patterns:
                    if pattern in answer:
                        answer = answer.replace(pattern, replacement)
        
        # 일반적인 중복 패턴 (키워드 없이도)
        # "단어는 단어는" → "단어는"
        answer = re.sub(r'(\w+는) \1', r'\1', answer)
        answer = re.sub(r'(\w+은) \1', r'\1', answer)
        answer = re.sub(r'(\w+가) \1', r'\1', answer)
        answer = re.sub(r'(\w+이) \1', r'\1', answer)
        
        return answer.strip()
    
    def _extract_keywords(self, question: str) -> list:
        """
        🍪 v1.0: 질문에서 핵심 키워드 추출
        
        예:
            "A가 무엇인가요?" → ["A"]
            "파이썬이 뭐야?" → ["파이썬"]
            "해마가 뭐야?" → ["해마"]
            "내 이름 기억나?" → ["이름", "기억나"] (하지만 실제로는 "GNJz" 찾아야 함)
        """
        # 🍪 v1.0: 질문 패턴별 키워드 추출 개선
        question_lower = question.lower()
        
        # "내 이름", "내가", "나는" 같은 패턴에서 실제 이름 추출 시도
        if '이름' in question or '기억나' in question or '기억해' in question:
            # 이름 관련 질문 → 학습된 이름 찾기
            # 일단 일반 키워드 추출 후, 기억에서 이름 찾기
            pass
        
        # 불용어 제거
        stopwords = {
            '가', '이', '은', '는', '을', '를', '의', '에', '와', '과', 
            '뭐', '무엇', '인가요', '야', '요', '기억나', '기억해', '기억해줘',
            '내', '나', '저', '제', '이름', '이름이', '이름은',
            '뭐야', '뭐예요', '무엇인가요', '무엇이야',
        }
        
        # 단어 분리
        words = question.split()
        keywords = []
        
        for word in words:
            # 불용어 제거
            cleaned = word.strip('가이은를을의에와과뭐무엇인가요야요?')
            if cleaned and len(cleaned) > 0 and cleaned not in stopwords:
                keywords.append(cleaned)
        
        # 🍪 v1.0: 첫 단어가 키워드일 가능성 높음 (하지만 불용어 제외)
        if keywords:
            # 불용어가 아닌 첫 번째 단어
            return keywords[:3]  # 최대 3개 키워드
        return [question]  # 키워드 없으면 전체 질문 사용
    
    def _update_context(self, question: str, answer: str, source: str = 'general'):
        """
        🍪 v1.1: 대화 맥락 업데이트
        
        Args:
            question: 사용자 질문
            answer: AI 답변
            source: 답변 출처 ('learning', 'memory', 'library', 'general')
        """
        self.conversation_context.append({
            'question': question,
            'answer': answer,
            'source': source,
        })
        
        # 최대 맥락 수 유지
        if len(self.conversation_context) > self.max_context:
            self.conversation_context.pop(0)
    
    def _enhance_with_context(self, question: str) -> str:
        """
        🍪 v1.3: 맥락 기반 질문 강화
        
        이전 대화를 참조하여 질문을 더 명확하게 만듦
        
        예:
            "그거" → 이전 대화의 주제
            "내 이름은?" → 이전에 학습한 이름 참조
        """
        if not self.conversation_context:
            return question
        
        # 지시어 처리 ("그거", "그건", "그것" 등)
        reference_words = ['그거', '그건', '그것', '그게', '그', '저거', '저건', '저것', '저게']
        has_reference = any(word in question for word in reference_words)
        
        if has_reference:
            # 최근 대화에서 주제 찾기
            for ctx in reversed(self.conversation_context[-3:]):  # 최근 3턴만
                prev_question = ctx.get('question', '')
                prev_answer = ctx.get('answer', '')
                
                # 이전 질문/답변에서 키워드 추출
                if prev_question:
                    # "그거"를 이전 질문의 주제로 대체
                    for ref_word in reference_words:
                        if ref_word in question:
                            # 이전 질문에서 핵심 키워드 추출
                            keywords = self._extract_keywords(prev_question)
                            if keywords:
                                question = question.replace(ref_word, keywords[0])
                                break
        
        # "내 이름은?" 같은 질문 → 이전 학습한 이름 참조
        if '내 이름' in question or '이름' in question:
            # 최근 대화에서 이름 학습 찾기
            for ctx in reversed(self.conversation_context[-5:]):  # 최근 5턴
                if ctx.get('source') == 'learning':
                    prev_q = ctx.get('question', '')
                    # "내 이름은 GNJz" 같은 패턴에서 이름 추출
                    if '내 이름은' in prev_q or '라고 해' in prev_q:
                        # 이름 추출 로직
                        if '내 이름은' in prev_q:
                            parts = prev_q.split('내 이름은')
                            if len(parts) > 1:
                                name = parts[1].strip().replace('?', '').strip()
                                if name and len(name) > 0:
                                    # 질문에 이름 추가하여 더 명확하게
                                    question = question.replace('내 이름', f'내 이름 {name}')
                                    break
        
        return question
    
    def _generate_clean_response(self, prompt: str) -> str:
        """깔끔한 응답 생성 (개인 LLM)"""
        if self.brain.model is None:
            return ""
        
        import torch
        
        # 짧은 프롬프트로 시작
        start = prompt[:20] if len(prompt) > 20 else prompt
        
        # 인코딩
        if not hasattr(self.brain, 'stoi') or not self.brain.stoi:
            return ""
        
        tokens = [self.brain.stoi.get(c) for c in start if c in self.brain.stoi]
        if not tokens:
            return ""
        
        x = torch.tensor([tokens], dtype=torch.long, device=self.brain.device)
        
        # 아주 짧게 생성 (20 토큰) - CPU 부하 감소
        with torch.no_grad():
            y = self.brain.model.generate(x, max_new_tokens=20, temperature=0.8, top_k=20)
        
        # 디코딩
        generated = ''.join([self.brain.itos.get(i, '') for i in y[0].tolist()])
        
        # 첫 문장만 추출 (. ! ? 에서 자르기)
        for end_char in ['.', '!', '?', '\n']:
            if end_char in generated:
                idx = generated.index(end_char)
                generated = generated[:idx+1]
                break
        
        # 너무 짧거나 이상하면 무시
        if len(generated) < 5 or generated == start:
            return ""
        
        return generated.strip()
    
    def _is_question_strict(self, text: str) -> bool:
        """
        🛑 치명적 충돌 해결 #1: 질문 필터링 v2 (Anti-Contamination Filter v2)
        
        V2: 질문 형태인지 강력하게 검사하여 학습 경로 진입을 막습니다.
        (띄어쓰기, 문장 끝에 붙는 의문형 종결어미 집중 검사)
        
        입력 텍스트가 질문 형태인지 검사합니다.
        (질문일 경우, 학습 저장소(Hippocampus)로의 진입을 차단합니다.)
        """
        import re
        
        if not text or len(text.strip()) == 0:
            return False
        
        text_clean = text.strip()
        
        # 1. 물음표(?) 검사 (가장 확실함)
        if text_clean.endswith('?'):
            return True
        
        # 2. 강력한 의문 패턴 검사 (띄어쓰기 무시)
        cleaned_text = text_clean.replace(" ", "")
        
        # [핵심 의문 패턴] ~이야, ~뭐야, ~어때, ~가요, ~누구야, ~니, ~해
        question_patterns = [
            r'뭐야$', r'누구야$', r'왜$', r'어때$', r'일까$', r'ㄴ가요$', r'ㄹ까$', r'니$',
            r'뭐예요$', r'뭐죠$', r'뭔가요$', r'뭔지$', r'무엇이야$', r'무엇인가요$', r'무엇인지$',
            r'어떻게$', r'어떤$', r'언제$', r'어디$', r'알아$', r'알지$',
            r'기억나$', r'기억해$', r'맞지$', r'아니야$', r'아니지$',
            r'이름이뭐야$', r'이름은뭐야$', r'이름이뭐$', r'이름은뭐$',
            r'너는$', r'나는$', r'당신은$', r'쿠키는$',
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, cleaned_text):
                return True
        
        # 3. 인삿말은 제외 (Reflex Path가 처리하도록)
        if cleaned_text in ["안녕", "안녕하세요", "안녕하세요", "안녕히가세요"]:
            return False
        
        # 4. 기억 인출 유도 문구 검사
        if re.search(r'(기억나|해봐|알려줘|무엇이|어떤|뭐|무엇)', cleaned_text):
            # 하지만 학습 명령 패턴은 제외
            learning_intro_patterns = ['내이름은', '나는', '저는', '라고해', '학습:', '기억해']
            has_learning_intro = any(pattern in cleaned_text for pattern in learning_intro_patterns)
            
            if not has_learning_intro:
                return True
        
        # 5. "이름" + 의문 패턴 조합
        if '이름' in cleaned_text:
            # "이름이뭐야", "이름은뭐야", "이름이뭐", "이름은뭐" 등
            if re.search(r'이름.*뭐', cleaned_text) or re.search(r'이름.*무엇', cleaned_text):
                return True
        
        return False
    
    def learn(self, content: str, importance: float = 0.7):
        """
        직접 학습
        
        🛑 치명적 충돌 해결 #1: 질문은 절대 저장하지 않음
        """
        # 질문 필터링: 질문이면 학습하지 않음
        if self._is_question_strict(content):
            # 질문은 학습하지 않음 (거울 효과 방지)
            return
        
        self.brain.learn(content, importance=importance)
    
    def sleep(self, cycles: int = 10):
        """수면 (공고화 + LLM 전이)"""
        self.brain.sleep(cycles=cycles)
    
    def grow(self):
        """
        성장 (개인 LLM 재학습)
        
        해마에 쌓인 기억을 개인 LLM으로 전이
        """
        output_path = self.brain.transfer_to_llm()
        print(f"📚 개인 LLM 학습 데이터 생성: {output_path}")
        print("   다음 단계: nanoGPT로 재학습 필요")
        return output_path
    
    def _record_knowledge(self, question: str, answer: str, 
                          source: str, confidence: float):
        """지식 기록"""
        key = question[:50]  # 질문 앞부분을 키로
        
        if key in self.knowledge_base:
            self.knowledge_base[key].access_count += 1
        else:
            self.knowledge_base[key] = LearnedKnowledge(
                question=question,
                answer=answer,
                source=source,
                confidence=confidence
            )
    
    def get_growth_stage(self) -> str:
        """
        🦛 성장 단계 계산
        
        기억 수와 학습 횟수에 따라 성장 단계 결정
        
        성장 흐름:
        - BabyHippo (베이비) → 현재 단계
        - TeenHippo (틴/유스)
        - Hippocampus (완전체, 어덜트는 필요 없음)
        - WisdomHippo (지혜)
        - MagicHippo (신의 경지)
        
        Returns:
            'BabyHippo', 'TeenHippo', 'Hippocampus', 'WisdomHippo', 'MagicHippo'
        """
        # 기억 수 확인
        brain_stats = self.brain.get_stats()
        memory_count = 0
        if 'hippo' in brain_stats:
            memory_count = brain_stats['hippo'].get('word_count', 0)
        
        # 학습 횟수 확인
        learning_count = len(self.knowledge_base)
        total_learning = memory_count + learning_count
        
        # 성장 단계 결정
        if total_learning < 100:
            return 'BabyHippo'  # 베이비 단계
        elif total_learning < 1000:
            return 'TeenHippo'  # 틴/유스
        elif total_learning < 10000:
            return 'Hippocampus'  # 완전체 (어덜트는 필요 없음)
        elif total_learning < 100000:
            return 'WisdomHippo'  # 지혜
        else:
            return 'MagicHippo'  # 신의 경지
    
    def _update_internal_flags(self):
        """내부 상태 플래그 업데이트"""
        # 뇌 통계에서 정보 가져오기
        brain_stats = self.brain.get_stats()
        
        # 뉴런 수 (해마에서)
        if 'hippo' in brain_stats:
            # 대략적 추정: word_count * 10 (각 기억당 평균 10개 뉴런)
            word_count = brain_stats['hippo'].get('word_count', 0)
            self.internal_flags['neuron_count'] = word_count * 10
        
        # 기능 플래그 (기본적으로 BASIC_STDP는 항상 있음)
        self.internal_flags['features'].add(NetworkFeature.BASIC_STDP)
        
        # 모델 플래그 (HHSomaQuick 기본 사용)
        self.internal_flags['models'].add(NeuronModel.HH_QUICK)
        
        # TODO: 실제 FPS, Axon 노드 수, 추가 기능/모델 측정
    
    def _update_capability_schema(self):
        """BrainCapability Schema 업데이트"""
        # Memory
        self.capability_schema.set_capability(
            CapabilityCategory.MEMORY, "short_term", 
            enabled=True, level=1.0
        )
        self.capability_schema.set_capability(
            CapabilityCategory.MEMORY, "working",
            enabled=True, level=1.0
        )
        
        # Plasticity
        self.capability_schema.set_capability(
            CapabilityCategory.PLASTICITY, "stdp",
            enabled=True, level=1.0
        )
        
        # TODO: 실제 구현 상태에 따라 업데이트
    
    def get_stats(self) -> Dict:
        """통계"""
        brain_stats = self.brain.get_stats()
        library_stats = self.library.get_stats()
        
        # 성장도 계산
        total_answered = (
            self.stats['answered_from_memory'] + 
            self.stats['answered_from_personal_llm']
        )
        total_questions = self.stats['questions_asked']
        
        independence = (total_answered / total_questions * 100) if total_questions > 0 else 0
        
        # 🦛 성장 단계 추가
        growth_stage = self.get_growth_stage()
        
        # 내부 상태 플래그 업데이트
        self._update_internal_flags()
        
        return {
            'name': self.name,
            'growth_stage': growth_stage,  # 🦛 성장 단계
            'questions': self.stats,
            'brain': brain_stats,
            'library': library_stats,
            'knowledge_count': len(self.knowledge_base),
            'independence': f"{independence:.1f}%",  # 도서관 독립도
            'internal_flags': {  # 🦛 내부 상태 플래그 (하위 호환성)
                'neuron_count': self.internal_flags['neuron_count'],
                'fps': self.internal_flags['fps'],
                'axon_nodes': self.internal_flags['axon_nodes'],
                'features': [f.value for f in self.internal_flags['features']],
                'models': [m.value for m in self.internal_flags['models']],
                'stability_test_passed': self.internal_flags['stability_test_passed'],
                'robustness_test_passed': self.internal_flags['robustness_test_passed'],
            },
            'capability_schema': self.capability_schema.to_dict(),  # 🧩 BrainCapability Schema
        }
    
    def __repr__(self):
        stats = self.get_stats()
        return f"CuriousBrain('{self.name}', independence={stats['independence']})"


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 CuriousBrain - 모든 걸 알고 싶은 AI")
    print("=" * 60)
    
    # 호기심 뇌 생성
    brain = CuriousBrain(name="baby")
    
    print(f"\n🔧 {brain}")
    print(f"   도서관: {brain.library.get_stats()}")
    
    # 직접 학습
    print("\n📝 직접 학습...")
    brain.learn("제 이름은 babyhippo입니다", importance=0.9)
    brain.learn("저는 호기심이 많은 AI입니다", importance=0.9)
    brain.learn("파이썬은 프로그래밍 언어입니다", importance=0.8)
    
    # 수면
    brain.sleep(cycles=5)
    
    # 질문 테스트
    print("\n🤔 질문 테스트:")
    
    questions = [
        "너의 이름이 뭐야?",  # 기억에 있음
        "파이썬이 뭐야?",     # 기억에 있음
        "오늘 날씨 어때?",    # 기억에 없음 → 도서관
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = brain.think(q)
        print(f"A: {answer[:150]}...")
    
    # 통계
    print("\n📊 통계:")
    stats = brain.get_stats()
    print(f"   질문 수: {stats['questions']['questions_asked']}")
    print(f"   기억 답변: {stats['questions']['answered_from_memory']}")
    print(f"   개인LLM 답변: {stats['questions']['answered_from_personal_llm']}")
    print(f"   도서관 답변: {stats['questions']['answered_from_library']}")
    print(f"   독립도: {stats['independence']}")
    
    print("\n" + "=" * 60)
    print("✅ 호기심 AI 테스트 완료!")
    print("   → 도서관 API 연결하면 진짜 학습 시작!")
    print("=" * 60)

