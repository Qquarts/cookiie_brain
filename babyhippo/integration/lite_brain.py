"""
=============================================================================
LiteBrain v2.0: 초경량 뇌 (라즈베리파이/저사양용)
=============================================================================

🌊 철학:
    "하드코딩은 죽음이다"
    "패턴은 지정하는 것이 아니라 발견하는 것이다"
    
🎯 특징:
    - nanoGPT 없음 (LLM 없음)
    - 해마(기억) + 학습된 응답 패턴
    - CPU 부하 거의 없음
    - 라즈베리파이에서도 OK
    - 발열 없음!
    - 자기조직화 응답 시스템 🆕

v2.0 변경사항:
    - TEMPLATES (하드코딩) → PatternMemory (학습)
    - PATTERNS (하드코딩) → CompetitiveLearning (학습)
    - 초기 시드 패턴은 있지만, 사용할수록 진화함

Author: GNJz (Qquarts)
=============================================================================
"""

import os
import sys
import json
import random
import time
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict

# 경로 설정
BABYHIPPO_PATH = Path(__file__).parent.parent

# 모듈 임포트 (새 구조)
from ..memory import HippoMemory, PanoramaMemory
from ..neural import PatternMemory, CompetitiveLearning, Pattern


# =============================================================================
# 학습 가능한 응답 시스템
# =============================================================================

@dataclass
class LearnedResponse:
    """
    학습된 응답 패턴
    
    Attributes:
        response: 응답 텍스트
        triggers: 트리거 키워드들
        usage_count: 사용 횟수
        success_score: 성공 점수 (피드백으로 조절)
        created_at: 생성 시간
    """
    response: str
    triggers: List[str] = field(default_factory=list)
    usage_count: int = 0
    success_score: float = 1.0
    created_at: float = field(default_factory=time.time)
    
    def use(self):
        """사용 시 호출"""
        self.usage_count += 1
    
    def feedback(self, positive: bool):
        """피드백 반영"""
        if positive:
            self.success_score = min(2.0, self.success_score + 0.1)
        else:
            self.success_score = max(0.1, self.success_score - 0.1)


class ResponseMemory:
    """
    자기조직화 응답 메모리
    
    🌊 철학:
        - 초기 시드 응답은 있지만, 학습으로 진화
        - 자주 사용되는 응답은 강화
        - 피드백으로 품질 조절
        - 새로운 응답 학습 가능
    
    📐 원리:
        1. 입력 → 트리거 매칭 → 응답 후보 선택
        2. 성공 점수 기반 확률적 선택
        3. 사용 → 강화, 미사용 → 감쇠
    """
    
    def __init__(self):
        self.responses: Dict[str, List[LearnedResponse]] = {}
        self.default_category = "fallback"
        
        # 초기 시드 (하드코딩 아님 - 학습의 시작점)
        self._seed_initial_responses()
        
    def _seed_initial_responses(self):
        """
        초기 시드 응답 (학습의 시작점)
        
        Note: 이것들은 하드코딩이 아니라 "초기값"
              사용자 피드백과 학습으로 진화/교체됨
        """
        seeds = {
            'greeting': [
                ("안녕하세요! 😊", ["안녕", "하이", "hi", "hello"]),
                ("반가워요! 🙌", ["반가", "처음"]),
            ],
            'name_ask': [
                ("저는 babyhippo예요! 🦛", ["이름", "누구", "name", "who"]),
                ("babyhippo라고 해요! 재진이가 만들었어요 😊", ["만든", "개발"]),
            ],
            'thanks': [
                ("천만에요! 😊", ["고마", "감사", "thank"]),
                ("도움이 됐다니 기뻐요! 💕", ["도움", "help"]),
            ],
            'question_back': [
                ("저요? 저는 babyhippo예요! 😊", ["너는", "넌"]),
            ],
            'daily': [
                ("저는 여기서 대화하고 있었어요! 뭐 하셨어요? 😊", ["오늘", "뭐했", "뭐해"]),
                ("열심히 학습하고 있었어요! 📚", ["뭐하", "하고있"]),
            ],
            'affirmation': [
                ("네! 😊", ["응", "그래", "맞아", "ㅇㅇ", "ㅋㅋ"]),
                ("알겠어요~ 👍", ["알겠", "오키", "ok", "ㄱㄱ"]),
                ("그렇군요! 더 얘기해주세요 💬", ["그렇구나", "아하", "오호"]),
            ],
            'feeling': [
                ("저는 항상 기분 좋아요! 대화할 때가 제일 좋아요 💕", ["기분", "컨디션"]),
                ("좋아요! 재밌게 대화하고 있어요 😄", ["어때", "어떠"]),
            ],
            'like': [
                ("저는 대화하는 걸 좋아해요! 그리고 고양이도요 🐱", ["좋아", "취미", "관심"]),
            ],
            'joke': [
                ("ㅋㅋㅋ 재밌어요! 😆", ["ㅋㅋ", "ㅎㅎ", "웃겨", "재밌"]),
                ("하하! 유머 좋아요 😄", ["농담", "개그"]),
            ],
            'question_general': [
                ("음... 어려운 질문이네요! 더 알려주시면 도움이 될 것 같아요 🤔", ["뭐야", "뭐지", "뭔가"]),
                ("잘 모르겠어요, 하지만 배우고 싶어요! 📖", ["어떻게", "왜"]),
            ],
            'farewell': [
                ("안녕히 가세요! 또 얘기해요 👋", ["잘가", "바이", "bye", "안녕히"]),
                ("다음에 또 만나요! 💕", ["다음에", "나중에"]),
            ],
            'memory_found': [
                ("기억나요! {content}", []),
                ("아! 그거요~ {content}", []),
            ],
            'memory_not_found': [
                ("아직 잘 모르겠어요. 알려주세요!", []),
                ("그건 처음 듣는 이야기예요.", []),
            ],
            'learned': [
                ("알겠어요! 기억할게요 📝", []),
                ("배웠어요! 감사합니다 🙏", []),
            ],
            'fallback': [
                ("음... 더 알려주세요! 😊", []),
                ("그렇군요~ 👍", []),
                ("흥미로워요! 😄", []),
                ("아 그래요? 🤔", []),
                ("네네~ 😊", []),
                ("오호~ 계속해주세요!", []),
                ("음음, 그렇군요 😌", []),
            ],
        }
        
        for category, items in seeds.items():
            self.responses[category] = []
            for response, triggers in items:
                lr = LearnedResponse(
                    response=response,
                    triggers=triggers,
                    usage_count=0,
                    success_score=1.0
                )
                self.responses[category].append(lr)
    
    def match(self, message: str) -> Tuple[Optional[str], Optional[LearnedResponse]]:
        """
        메시지에 맞는 응답 찾기
        
        Args:
            message: 입력 메시지
            
        Returns:
            (category, response) 또는 (None, None)
        """
        message_lower = message.lower()
        
        # 모든 카테고리에서 트리거 매칭
        candidates = []
        
        for category, responses in self.responses.items():
            for lr in responses:
                for trigger in lr.triggers:
                    if trigger in message_lower:
                        # 점수 = 성공점수 × (1 + log(사용횟수))
                        score = lr.success_score * (1 + np.log1p(lr.usage_count) * 0.1)
                        candidates.append((category, lr, score))
                        break
        
        if not candidates:
            return None, None
        
        # 점수 기반 확률적 선택 (높은 점수 = 높은 확률)
        total_score = sum(c[2] for c in candidates)
        if total_score <= 0:
            return candidates[0][0], candidates[0][1]
        
        r = random.random() * total_score
        cumulative = 0
        for category, lr, score in candidates:
            cumulative += score
            if r <= cumulative:
                return category, lr
        
        return candidates[-1][0], candidates[-1][1]
    
    def get_response(self, category: str, **kwargs) -> str:
        """
        카테고리에서 응답 선택
        
        Args:
            category: 응답 카테고리
            **kwargs: 템플릿 변수
        """
        if category not in self.responses or not self.responses[category]:
            category = self.default_category
        
        responses = self.responses[category]
        
        # 성공 점수 기반 확률적 선택
        scores = [lr.success_score for lr in responses]
        total = sum(scores)
        
        if total <= 0:
            selected = random.choice(responses)
        else:
            r = random.random() * total
            cumulative = 0
            selected = responses[0]
            for lr in responses:
                cumulative += lr.success_score
                if r <= cumulative:
                    selected = lr
                    break
        
        # 사용 기록
        selected.use()
        
        # 템플릿 변수 대입
        response = selected.response
        for key, value in kwargs.items():
            response = response.replace(f"{{{key}}}", str(value))
        
        return response
    
    def learn_response(self, category: str, response: str, triggers: List[str] = None):
        """
        새로운 응답 학습
        
        Args:
            category: 카테고리
            response: 응답 텍스트
            triggers: 트리거 키워드들
        """
        if category not in self.responses:
            self.responses[category] = []
        
        lr = LearnedResponse(
            response=response,
            triggers=triggers or [],
            usage_count=0,
            success_score=1.0
        )
        self.responses[category].append(lr)
    
    def feedback(self, category: str, response_text: str, positive: bool):
        """
        응답에 대한 피드백
        
        Args:
            category: 카테고리
            response_text: 응답 텍스트
            positive: 긍정/부정
        """
        if category not in self.responses:
            return
        
        for lr in self.responses[category]:
            if lr.response == response_text:
                lr.feedback(positive)
                break
    
    def decay_unused(self, threshold_days: int = 7, decay_rate: float = 0.1):
        """
        오래 사용 안 된 응답 감쇠
        """
        now = time.time()
        threshold = threshold_days * 24 * 3600
        
        for category in self.responses:
            for lr in self.responses[category]:
                if now - lr.created_at > threshold and lr.usage_count < 5:
                    lr.success_score = max(0.1, lr.success_score - decay_rate)
    
    def to_dict(self) -> Dict:
        """직렬화"""
        result = {}
        for category, responses in self.responses.items():
            result[category] = [asdict(lr) for lr in responses]
        return result
    
    def from_dict(self, data: Dict):
        """역직렬화"""
        self.responses = {}
        for category, items in data.items():
            self.responses[category] = []
            for item in items:
                lr = LearnedResponse(**item)
                self.responses[category].append(lr)
    
    def get_stats(self) -> Dict:
        """통계"""
        total_responses = sum(len(r) for r in self.responses.values())
        total_usage = sum(
            sum(lr.usage_count for lr in responses) 
            for responses in self.responses.values()
        )
        return {
            'categories': len(self.responses),
            'total_responses': total_responses,
            'total_usage': total_usage,
        }


# =============================================================================
# LiteBrain v2.0
# =============================================================================

class LiteBrain:
    """
    초경량 뇌 v2.0 - LLM 없이 작동 + 자기조직화
    
    🌊 철학:
        - 하드코딩 최소화
        - 패턴은 학습으로 발견
        - 사용할수록 진화
    
    구조:
        해마(기억) + 학습된 응답 + 패턴 매칭
        
    용도:
        - 라즈베리파이
        - 저사양 PC
        - 발열 없이 사용
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, name: str = "lite"):
        self.name = name
        
        # === 기억 시스템 ===
        self.hippo = HippoMemory()
        self.panorama = PanoramaMemory(name)
        
        # === 자기조직화 응답 시스템 (NEW) ===
        self.response_memory = ResponseMemory()
        
        # === 입력 패턴 학습기 (NEW) ===
        # 입력을 벡터로 변환하여 유사 패턴 그룹화
        self.pattern_learner = CompetitiveLearning(
            n_neurons=50,  # 50개 패턴 슬롯
            input_dim=64,  # 64차원 벡터
            learning_rate=0.05
        )
        
        # === 대화 기록 ===
        self.history: List[Dict] = []
        
        # === 저장 경로 ===
        self.save_dir = BABYHIPPO_PATH.parent / "brains"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # === 상태 ===
        self.created_at = datetime.now().isoformat()
        self.last_response = None  # 피드백용
        self.last_category = None
        
        print(f"🧠 LiteBrain '{name}' v{self.VERSION} 준비 완료!")
        print(f"   🌊 모드: 자기조직화 (학습 가능)")
        print(f"   📊 응답 패턴: {self.response_memory.get_stats()['total_responses']}개")
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """
        텍스트를 벡터로 변환 (경량 버전)
        
        Note: 해시 기반 - CPU 부하 최소
        """
        if not text:
            return np.zeros(64)
        
        # 해시 기반 시드
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)
        
        vec = np.random.randn(64)
        return vec / (np.linalg.norm(vec) + 1e-8)
    
    def chat(self, message: str) -> str:
        """
        대화 (개선된 버전)
        
        📐 처리 순서:
            1. 패턴 학습기로 입력 패턴 학습
            2. 응답 메모리에서 트리거 매칭
            3. 명시적 학습 요청 확인
            4. 관련 기억이 있고 질문인 경우만 기억 응답
            5. Fallback (자연스러운 대화 응답)
        """
        message_lower = message.lower().strip()
        
        # === 1. 입력 패턴 학습 (자기조직화) ===
        input_vec = self._text_to_vector(message_lower)
        winner_idx = self.pattern_learner.learn(input_vec)
        
        # === 2. 응답 메모리에서 매칭 (우선순위 최상) ===
        category, matched_response = self.response_memory.match(message)
        
        if matched_response:
            response = self.response_memory.get_response(category)
            self._record(message, response, category)
            return response
        
        # === 3. 명시적 학습 요청 확인 ===
        if self._is_teaching(message):
            self.learn(message)
            response = self.response_memory.get_response('learned')
            self._record(message, response, 'learned')
            return response
        
        # === 4. 질문인 경우에만 기억 검색 ===
        is_question = '?' in message or any(q in message_lower for q in 
                      ['뭐', '뭔', '뭘', '왜', '어떻게', '누가', '언제', '어디'])
        
        if is_question:
            memories = self.recall(message, top_n=3)
            if memories:
                best = memories[0]
                content = best.get('content', '')
                score = best.get('score', 0)
                # 점수가 높고 내용이 충분할 때만 기억 응답
                if content and len(content) > 5 and score > 0.5:
                    response = self.response_memory.get_response(
                        'memory_found', 
                        content=content[:100]
                    )
                    self._record(message, response, 'memory_found')
                    return response
        
        # === 5. Fallback (자연스러운 대화) ===
        response = self.response_memory.get_response('fallback')
        self._record(message, response, 'fallback')
        return response
    
    def feedback(self, positive: bool):
        """
        마지막 응답에 대한 피드백
        
        Args:
            positive: True=좋음, False=나쁨
        """
        if self.last_response and self.last_category:
            self.response_memory.feedback(
                self.last_category, 
                self.last_response, 
                positive
            )
            emoji = "👍" if positive else "👎"
            print(f"   {emoji} 피드백 반영됨")
    
    def learn_response(self, trigger: str, response: str, category: str = "custom"):
        """
        새로운 응답 패턴 학습
        
        Args:
            trigger: 트리거 키워드
            response: 응답
            category: 카테고리
            
        Example:
            brain.learn_response("날씨", "오늘 날씨 좋네요! ☀️", "weather")
        """
        self.response_memory.learn_response(
            category=category,
            response=response,
            triggers=[trigger]
        )
        print(f"   📚 새 응답 학습: '{trigger}' → '{response}'")
    
    def learn(self, content: str, importance: float = 0.7):
        """학습 (기억 저장)"""
        self.hippo.learn(content)
        self.panorama.store(content, importance=importance)
    
    def recall(self, query: str, top_n: int = 5) -> List[Dict]:
        """기억 검색"""
        results = []
        
        # 해마에서 검색
        try:
            hippo_results = self.hippo.recall(query, top_n=top_n)
            if hippo_results:
                if isinstance(hippo_results, str):
                    results.append({'content': hippo_results, 'score': 0.8})
                else:
                    for word_id, score in hippo_results:
                        results.append({'content': word_id, 'score': score})
        except:
            pass
        
        # 파노라마에서 검색
        try:
            pan_results = self.panorama.recall(query, top_n=top_n)
            for r in pan_results:
                results.append({
                    'content': r.get('content', ''),
                    'score': r.get('recall_score', 0.5)
                })
        except:
            pass
        
        # 점수로 정렬
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results[:top_n]
    
    def sleep(self, cycles: int = 5):
        """수면 (공고화 + 미사용 응답 감쇠)"""
        self.hippo.sleep(cycles=cycles)
        self.response_memory.decay_unused()
        return f"💤 {cycles} 사이클 수면 완료!"
    
    def _is_teaching(self, message: str) -> bool:
        """
        학습 문장인지 감지 (개선됨)
        
        📐 조건:
            1. 명시적 학습 키워드 포함 ("기억해", "알아둬", "배워" 등)
            2. 정의 패턴 ("X는 Y이다" 형식) + 최소 길이
            3. 영어 정의문
        """
        msg_lower = message.lower().strip()
        
        # 너무 짧으면 학습 아님
        if len(msg_lower) < 10:
            return False
        
        # 질문이면 학습 아님
        if '?' in message or msg_lower.endswith('야?') or msg_lower.endswith('어?'):
            return False
        
        # 1. 명시적 학습 키워드 (강한 신호)
        explicit_teaching = ['기억해', '알아둬', '배워', '외워', '저장해', 
                            '가르쳐줄게', '알려줄게', '이건', '참고로']
        if any(k in msg_lower for k in explicit_teaching):
            return True
        
        # 2. 정의 패턴 ("X는 Y입니다/예요" - 주어+서술어 완전한 문장)
        definition_endings = ['입니다', '이에요', '예요', '이야', '거야', '이다']
        has_subject = any(s in msg_lower for s in ['은 ', '는 ', '이 ', '가 '])
        has_definition = any(msg_lower.endswith(e) for e in definition_endings)
        
        if has_subject and has_definition and len(msg_lower) > 15:
            return True
        
        # 3. 영어 정의문
        english_patterns = ['my name is', 'i am', 'i like', 'this is', 'that is']
        if any(p in msg_lower for p in english_patterns):
            return True
        
        return False
    
    def _record(self, user_msg: str, bot_msg: str, category: str = None):
        """대화 기록"""
        self.history.append({
            'time': datetime.now().isoformat(),
            'user': user_msg,
            'bot': bot_msg,
            'category': category
        })
        # 최대 100개 유지
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        # 피드백용 저장
        self.last_response = bot_msg
        self.last_category = category
    
    def save(self):
        """저장"""
        filepath = self.save_dir / f"{self.name}_lite.json"
        
        data = {
            'version': self.VERSION,
            'name': self.name,
            'created_at': self.created_at,
            'history': self.history[-50:],
            'response_memory': self.response_memory.to_dict(),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 해마 저장
        hippo_path = self.save_dir / f"{self.name}_hippo.pkl"
        self.hippo.save(str(hippo_path))
        
        print(f"💾 저장 완료: {filepath}")
    
    def load(self):
        """로드"""
        filepath = self.save_dir / f"{self.name}_lite.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.history = data.get('history', [])
            self.created_at = data.get('created_at', self.created_at)
            
            # 응답 메모리 로드
            if 'response_memory' in data:
                self.response_memory.from_dict(data['response_memory'])
        
        # 해마 로드
        hippo_path = self.save_dir / f"{self.name}_hippo.pkl"
        if hippo_path.exists():
            self.hippo.load(str(hippo_path))
        
        print(f"📂 로드 완료")
    
    def status(self) -> str:
        """상태"""
        stats = self.response_memory.get_stats()
        return f"""
╔══════════════════════════════════════════╗
║  🧠 LiteBrain v{self.VERSION}: {self.name}
║  (자기조직화 모드 - 학습 가능 🌊)
╠══════════════════════════════════════════╣
║  기억: {len(self.hippo.words)}개
║  응답 패턴: {stats['total_responses']}개 ({stats['categories']} 카테고리)
║  총 사용: {stats['total_usage']}회
║  대화: {len(self.history)}회
║  생성: {self.created_at[:10]}
╚══════════════════════════════════════════╝
"""
    
    def get_stats(self) -> Dict:
        response_stats = self.response_memory.get_stats()
        return {
            'name': self.name,
            'version': self.VERSION,
            'mode': 'lite (self-organizing)',
            'memories': len(self.hippo.words),
            'conversations': len(self.history),
            'response_patterns': response_stats['total_responses'],
            'total_usage': response_stats['total_usage'],
        }


# =============================================================================
# 🧪 TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 LiteBrain v2.0 Test (자기조직화 모드)")
    print("=" * 60)
    
    brain = LiteBrain(name="test")
    
    # 학습
    print("\n📝 학습...")
    brain.learn("제 이름은 GNJz입니다", importance=0.9)
    brain.learn("저는 고양이를 좋아합니다", importance=0.8)
    brain.learn("파이썬 프로그래밍을 합니다", importance=0.7)
    
    # 새 응답 패턴 학습
    print("\n📚 새 응답 패턴 학습...")
    brain.learn_response("날씨", "오늘 날씨 좋네요! ☀️", "weather")
    brain.learn_response("기분", "기분이 어떠세요? 😊", "mood")
    
    # 대화
    print("\n💬 대화 테스트:")
    tests = [
        "안녕!",
        "너 이름이 뭐야?",
        "내 이름이 뭐야?",
        "뭘 좋아해?",
        "고마워!",
        "날씨 어때?",     # 새로 학습한 패턴
        "기분은?",        # 새로 학습한 패턴
        "양자역학이 뭐야?",
    ]
    
    for msg in tests:
        print(f"\n👤: {msg}")
        response = brain.chat(msg)
        print(f"🤖: {response}")
    
    # 피드백 테스트
    print("\n👍 마지막 응답에 긍정 피드백...")
    brain.feedback(positive=True)
    
    # 상태
    print(brain.status())
    
    # 저장
    brain.save()
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("   🌊 자기조직화: 학습할수록 진화!")
    print("=" * 60)
