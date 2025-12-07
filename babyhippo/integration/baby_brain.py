"""
BabyBrain: babyhippo 통합 시스템 v2.0

=============================================================================
🌊 철학:
    "실체는 입자(정지)가 아니라 파동(움직임)이다"
    "동역학(Dynamics)이 이 세계의 실체다"
    "노이즈는 창조의 씨앗이다"
=============================================================================

🧠 전체 뇌 구조 (피드백 루프):

    ┌─────────────────────────────────────────────────────────┐
    │                    Input (입력)                          │
    └─────────────────────┬───────────────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │  1️⃣  Thalamus (시상) - 감각 게이팅                       │
    │      "이 입력 중요해? 무시할까?"                          │
    └─────────────────────┬───────────────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │  2️⃣  Amygdala (편도체) - 위협 감지 ⚡ FAST PATH          │
    │      "위험해?! 도망가야 해?!"                             │
    │      → 즉각 반응 (생각 전에 몸이 먼저)                    │
    └───────────┬─────────────────────────┬───────────────────┘
                │ (위협!)                  │ (정상)
                ▼                          ▼
    ┌───────────────────┐    ┌────────────────────────────────┐
    │ 즉각 반응 반환     │    │  3️⃣  Hypothalamus (시상하부)    │
    │ (기억 강화)       │    │      "에너지는? 졸려? 심심해?"   │
    └───────────────────┘    └─────────────────┬──────────────┘
                                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │  4️⃣  Hippocampus (해마) - 기억 검색/저장                 │
    │      "이거 본 적 있나? 관련 기억은?"                      │
    └─────────────────────┬───────────────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │  5️⃣  Basal Ganglia (기저핵) - 행동 선택                  │
    │      "습관 있어? 자동 반응 가능?"                         │
    └───────────┬─────────────────────────┬───────────────────┘
                │ (습관!)                  │ (새로운 상황)
                ▼                          ▼
    ┌───────────────────┐    ┌────────────────────────────────┐
    │ 습관대로 반응      │    │  6️⃣  Prefrontal (전두엽)        │
    │ (빠른 처리)       │    │      "어떻게 대답하지?"         │
    └───────────────────┘    └─────────────────┬──────────────┘
                                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │  7️⃣  Cingulate (대상피질) - 오류 체크                    │
    │      "이 응답 맞아? 뭔가 이상한데?"                       │
    └─────────────────────┬───────────────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │  8️⃣  Cerebellum (소뇌) - 미세 조정                       │
    │      "말투 다듬기, 반복 제거"                             │
    └─────────────────────┬───────────────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    Output (출력)                         │
    └─────────────────────────────────────────────────────────┘
                          │
                          └──────────► 기억 저장 (해마)
                                       학습 (기저핵)
                                       피드백 (시상하부)

Author: GNJz (Qquarts)
Version: 2.1 (DNA Integration)
=============================================================================
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 경로 설정
BABYHIPPO_PATH = Path(__file__).parent.parent
PROJECT_PATH = BABYHIPPO_PATH.parent

# === 모듈 임포트 (새 구조 v2.1) ===

# 🧬 DNA 설정 (NEW v2.1)
from ..config import DNA, SpeciesType, FundamentalLaws, create_dna

# 기억 시스템
from ..memory import HippoMemory

# 호기심 뇌 (해마 + LLM + 도서관)
from .curious_brain import CuriousBrain, LibraryConnector

# 뇌 구조 - 전체 (피드백 루프용)
from ..brain import (
    # 전두엽 - 판단/계획
    PrefrontalCortex,
    # 편도체 - 감정/위협
    Amygdala,
    # 시상하부 - 욕구/동기
    Hypothalamus, DriveType,
    # 시상 - 감각 게이팅 (NEW)
    Thalamus, ModalityType,
    # 기저핵 - 행동 선택/습관 (NEW)
    BasalGanglia,
    # 대상피질 - 오류 감지 (NEW)
    CingulateCortex,
    # 소뇌 - 반사/미세조정
    Cerebellum,
)

# 동역학 엔진 (NEW)
from ..neural import (
    DynamicNeuron,
    NoiseGenerator,
    NeuronState,
)

# 피질
try:
    from ..cortex import VisualCortex, SemanticCortex, EmotionalCortex
    HAS_CORTEX = True
except ImportError:
    HAS_CORTEX = False

# 뇌 그래프
try:
    from ..brain import BrainGraph
    HAS_BRAIN_GRAPH = True
except ImportError:
    HAS_BRAIN_GRAPH = False


class BabyBrain:
    """
    babyhippo 통합 뇌 시스템 v2.0
    
    🌊 철학:
        - 동역학적 피드백 루프
        - 노이즈 기반 창발
        - 생물학적 타당성
    
    🧠 모듈 구성 (작용 순서):
        1. Thalamus (시상) - 입력 게이팅
        2. Amygdala (편도체) - 위협/감정 (FAST PATH)
        3. Hypothalamus (시상하부) - 욕구/동기
        4. Hippocampus (해마) - 기억 검색/저장
        5. BasalGanglia (기저핵) - 습관/행동 선택
        6. Prefrontal (전두엽) - 판단/계획
        7. Cingulate (대상피질) - 오류 감지
        8. Cerebellum (소뇌) - 미세 조정
    """
    
    VERSION = "2.1.0"
    
    def __init__(self, 
                 name: str = "baby",
                 species: str = "quokka",
                 library_provider: str = 'openai',
                 auto_save: bool = True,
                 save_dir: str = None,
                 noise_level: float = 0.1):
        """
        Args:
            name: 뇌 이름
            species: 성격 유형 ("quokka", "scholar", "butler", "athlete")
            library_provider: 도서관 제공자
            auto_save: 자동 저장 여부
            save_dir: 저장 디렉토리
            noise_level: 노이즈 레벨 (창발의 씨앗)
        
        Note:
            v2.1: DNA 시스템 통합
            - 성격(species)에 따라 각 뇌 모듈 파라미터 자동 조정
            - FundamentalLaws.TABOOS → 대상피질 연동
        """
        self.name = name
        self.auto_save = auto_save
        self.save_dir = Path(save_dir) if save_dir else PROJECT_PATH / "brains"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # 생성 시간
        self.created_at = datetime.now().isoformat()
        self.last_interaction = None
        
        # 노이즈 생성기 (창발의 씨앗)
        self.noise = NoiseGenerator()
        self.noise_level = noise_level
        
        # =============================================================
        # 🧬 DNA 로드 (v2.1 NEW)
        # =============================================================
        self.dna = create_dna(species)
        dna_traits = self.dna.traits
        
        print(f"🧠 BabyBrain '{name}' v{self.VERSION} 초기화 중...")
        print(f"   🧬 DNA: {self.dna.get_summary()}")
        print(f"   🌊 철학: 동역학 + 피드백 루프 + 노이즈")
        
        # =============================================================
        # 🧠 뇌 모듈 초기화 (DNA 주입)
        # =============================================================
        
        # 0. 호기심 뇌 (해마 + 개인LLM + 도서관)
        self.curious = CuriousBrain(
            name=name,
            library_provider=library_provider
        )
        
        # 1. 시상 (Thalamus) - 감각 게이팅
        self.thalamus = Thalamus()
        
        # 2. 편도체 (Amygdala) - 감정/위협
        self.amygdala = Amygdala()
        
        # 3. 시상하부 (Hypothalamus) - 욕구/동기 [DNA 주입]
        self.hypothalamus = Hypothalamus(
            weights=dna_traits.get('drive_weights')
        )
        
        # 4. 해마는 curious.brain.hippo에 있음
        
        # 5. 기저핵 (BasalGanglia) - 행동 선택/습관 [DNA 주입]
        self.basal_ganglia = BasalGanglia(
            bias=dna_traits.get('action_bias')
        )
        
        # 6. 전두엽 (Prefrontal) - 판단/계획 [DNA 주입]
        self.prefrontal = PrefrontalCortex(
            dna_traits=dna_traits
        )
        
        # 7. 대상피질 (Cingulate) - 오류 감지 [금기어 주입]
        self.cingulate = CingulateCortex(
            taboos=FundamentalLaws.TABOOS
        )
        
        # 8. 소뇌 (Cerebellum) - 반사/미세조정 [말투 주입]
        self.cerebellum = Cerebellum(
            reflex_pack=dna_traits.get('reflex_pack')
        )
        
        # =============================================================
        # 피질 (Cortex) - 감각 처리
        # =============================================================
        self.cortex = {}
        if HAS_CORTEX:
            try:
                self.cortex['visual'] = VisualCortex()
                self.cortex['semantic'] = SemanticCortex()
                self.cortex['emotional'] = EmotionalCortex()
            except Exception as e:
                print(f"   ⚠️ 피질 초기화 실패: {e}")
        
        # =============================================================
        # 상태 관리
        # =============================================================
        
        # 대화 기록
        self.conversation_history: List[Dict] = []
        self.max_history = 100
        
        # 성격/설정
        self.personality = {
            'name': name,
            'traits': ['curious', 'friendly', 'helpful'],
            'language': 'ko',
        }
        
        # 내부 상태 (피드백 루프용)
        self.state = {
            'awake': True,
            'mode': 'wake',           # wake / sleep / explore
            'mood': 'neutral',
            'energy': 1.0,
            'attention': 1.0,         # 🆕 시상 주의 레벨
            'last_emotion': None,
            'threat_level': 0.0,
            'current_drive': None,
            'last_action': None,      # 🆕 마지막 행동 (기저핵)
            'error_level': 0.0,       # 🆕 오류 레벨 (대상피질)
        }
        
        # =============================================================
        # 초기화 완료 출력
        # =============================================================
        print(f"   ✅ 초기화 완료!")
        print(f"   📊 모듈 현황 (🧬=DNA 적용):")
        print(f"      👁️ 시상: 활성화 (게이팅)")
        print(f"      🚨 편도체: 활성화 (위협/감정)")
        print(f"      🎯 시상하부: 활성화 🧬 (욕구 가중치)")
        print(f"      🧠 해마: {len(self.curious.brain.hippo.words)}개 기억")
        print(f"      ⚙️ 기저핵: 활성화 🧬 (행동 성향)")
        print(f"      🤔 전두엽: 활성화 🧬 (인지 성향)")
        print(f"      ⚠️ 대상피질: 활성화 🧬 (금기어 {len(FundamentalLaws.TABOOS)}개)")
        print(f"      🎯 소뇌: 활성화 🧬 (말투)")
        print(f"      🌊 노이즈: {self.noise_level} (창발의 씨앗)")
    
    # =========================================================================
    # 🌊 대화 (피드백 루프)
    # =========================================================================
    
    def chat(self, message: str) -> str:
        """
        대화하기 - 피드백 루프 버전
        
        📐 처리 순서:
            1. Thalamus (시상) - 입력 게이팅
            2. Amygdala (편도체) - 위협/감정 (FAST PATH)
            3. Hypothalamus (시상하부) - 욕구 체크
            4. Hippocampus (해마) - 기억 검색
            5. BasalGanglia (기저핵) - 습관 체크
            6. Prefrontal (전두엽) - 판단 (필요시)
            7. Cingulate (대상피질) - 오류 체크
            8. Cerebellum (소뇌) - 미세 조정
            → 출력 + 피드백 (기억 저장, 학습)
        
        Args:
            message: 사용자 메시지
            
        Returns:
            응답
        """
        self.last_interaction = datetime.now().isoformat()
        
        # 노이즈 추가 (창발의 씨앗)
        # TODO: 향후 curious.think(), 행동 선택 등에 가중치로 적용 예정
        noise = self.noise.gaussian(self.noise_level)
        self.state['current_noise'] = noise  # 상태에 저장 (디버깅/추후 사용)
        
        # =================================================================
        # 1️⃣ [시상] 입력 게이팅 - "이 입력 중요해?"
        # =================================================================
        # 시상이 입력의 중요도를 평가하고 필터링
        try:
            filtered_output = self.thalamus.relay_single(
                message, 
                ModalityType.SEMANTIC
            )
            if filtered_output and not filtered_output.passed_gate:
                # 중요하지 않은 입력은 간단히 처리
                self.state['attention'] = 0.3
            else:
                self.state['attention'] = filtered_output.attention_weight if filtered_output else 1.0
        except Exception:
            self.state['attention'] = 1.0
        
        # =================================================================
        # 2️⃣ [편도체] 위협/감정 감지 - FAST PATH ⚡
        # =================================================================
        threat = self.amygdala.detect_threat(message)
        emotion = self.amygdala.process_emotion(message)
        
        # 상태 업데이트
        self.state['last_emotion'] = emotion.dominant
        self.state['threat_level'] = threat.threat_level if threat else 0.0
        self.state['mood'] = emotion.dominant
        
        # 위협 시 시상하부에 알림 (스트레스 증가)
        if threat and threat.threat_level > 0.5:
            self.hypothalamus.process_stimulus('threat', threat.threat_level)
        
        # 🚨 FAST PATH: 위협 감지 → 즉각 반응 (이성 우회)
        fast_response = self.amygdala.fast_response(message)
        if fast_response:
            # 위험 상황 → 생각 전에 반응!
            self._record_conversation(message, fast_response)
            
            # 위협 상황은 강하게 기억 (트라우마)
            memory_result = self.amygdala.enhance_memory(message, base_importance=0.9)
            self.curious.learn(
                f"[위협] {message}", 
                importance=memory_result['enhanced_importance']
            )
            
            # 기저핵에 학습 (위협 회피 습관)
            self.basal_ganglia.learn(
                state=f"threat:{threat.threat_type if threat else 'unknown'}",
                action="avoid",
                reward=0.8  # 생존 = 보상
            )
            
            return fast_response
        
        # =================================================================
        # 3️⃣ [시상하부] 욕구 체크 - "에너지는? 졸려?"
        # =================================================================
        drive = self.hypothalamus.get_current_drive()
        self.state['current_drive'] = drive.drive_type.value
        self.state['energy'] = self.hypothalamus.state.energy
        
        # 강제 수면 필요 시
        if drive.drive_type == DriveType.SLEEP and drive.urgency >= 1.0:
            self._record_conversation(message, drive.message)
            return f"{drive.message} 💤"
        
        # =================================================================
        # 4️⃣ [해마] 기억 검색 - "이거 본 적 있어?"
        # =================================================================
        memories = self.curious.brain.recall(message, top_n=3)
        has_memory = len(memories) > 0 and memories[0].get('score', 0) > 0.5
        
        # =================================================================
        # 5️⃣ [기저핵] 습관 체크 - "자동 반응 가능?"
        # =================================================================
        # 현재 상황을 상태로 인코딩
        current_state = f"emotion:{emotion.dominant}|has_memory:{has_memory}"
        
        # 가능한 행동들
        possible_actions = ["respond_memory", "respond_think", "respond_library", "ask_clarify"]
        
        # 습관 체크
        action_result = self.basal_ganglia.select_action(current_state, possible_actions)
        self.state['last_action'] = action_result.action.name if action_result.action else None
        
        # 🔄 습관이 있으면 빠른 처리 (전두엽 우회)
        if action_result.is_automatic and action_result.action:
            response = self._execute_habitual_action(
                action_result.action.name, 
                message, 
                memories
            )
            if response:
                # 소뇌로 미세 조정
                response = self._refine_response(response)
                self._post_process(message, response, emotion, drive)
                return response
        
        # =================================================================
        # 6️⃣ [전두엽] 판단/계획 - "어떻게 대답하지?"
        # =================================================================
        # 전두엽 분석
        analysis = self.prefrontal.analyze_query(message)
        
        # 호기심 뇌로 생각 (해마 + LLM + 도서관)
        response = self.curious.think(message)
        
        # =================================================================
        # 7️⃣ [대상피질] 오류 체크 - "이 응답 맞아?"
        # =================================================================
        try:
            error = self.cingulate.check_response_error(response)
            if error and error.magnitude > 0.5:
                self.state['error_level'] = error.magnitude
                # 오류 감지 → 재처리 요청 가능
                # (현재는 로그만)
            else:
                self.state['error_level'] = 0.0
        except Exception:
            self.state['error_level'] = 0.0
        
        # =================================================================
        # 8️⃣ [소뇌] 미세 조정 - "말투 다듬기"
        # =================================================================
        response = self._refine_response(response)
        
        # =================================================================
        # 🔄 피드백 (기억 저장, 학습, 보상)
        # =================================================================
        self._post_process(message, response, emotion, drive)
        
        # 욕구 기반 응답 추가
        drive_after = self.hypothalamus.get_current_drive()
        if drive_after.urgency > 0.6 and drive_after.drive_type != DriveType.STAY:
            response += f"\n\n({drive_after.message})"
        
        return response
    
    def _execute_habitual_action(self, action: str, message: str, 
                                  memories: List[Dict]) -> Optional[str]:
        """
        습관적 행동 실행 (기저핵 → 전두엽 우회)
        
        Args:
            action: 행동 이름
            message: 원본 메시지
            memories: 검색된 기억들
        """
        if action == "respond_memory" and memories:
            # 기억 기반 응답 (v2.1: 'content' 키 사용)
            memory_content = memories[0].get('content', memories[0].get('word', message))
            return f"(기억에서) {memory_content}"
        elif action == "respond_think":
            # 짧은 생각 응답
            return self.curious.think(message)
        elif action == "ask_clarify":
            # 명확화 요청
            return "무슨 뜻이에요? 좀 더 설명해 주세요."
        return None
    
    def _refine_response(self, response: str) -> str:
        """
        소뇌: 응답 미세 조정
        
        - 반복 제거
        - 길이 조절
        - 말투 다듬기
        """
        try:
            # 소뇌 반사 체크
            reflex = self.cerebellum.check_reflex(response[:20])
            if reflex:
                return reflex
            
            # 출력 보정
            corrected = self.cerebellum.correct_output(response)
            return corrected
        except Exception:
            return response
    
    def _post_process(self, message: str, response: str, 
                      emotion, drive):
        """
        후처리: 피드백 루프
        
        - 대화 기록
        - 기억 저장 (감정 강화)
        - 기저핵 학습
        - 시상하부 업데이트
        """
        # 대화 기록
        self._record_conversation(message, response)
        
        # 감정적 대화는 더 강하게 기억
        if emotion.intensity > 0.5:
            memory_result = self.amygdala.enhance_memory(message, base_importance=0.5)
            boost = memory_result['enhancement_factor']
            if boost > 1.1:
                self.curious.learn(
                    f"[{emotion.dominant}] {message}", 
                    importance=min(0.9, 0.5 * boost)
                )
        
        # 시상하부 업데이트
        stimulus_level = min(1.0, emotion.intensity + 0.3)
        self.hypothalamus.process_stimulus('conversation', stimulus_level)
        self.hypothalamus.tick(action_type='chat', stimulus_level=stimulus_level)
        
        # 보상 (대화 성공)
        if len(response) > 10:
            self.hypothalamus.receive_reward('social', 0.3)
            # 기저핵에도 보상 (이 행동이 좋았다)
            if self.state.get('last_action'):
                current_state = f"emotion:{emotion.dominant}"
                self.basal_ganglia.learn(
                    state=current_state,
                    action=self.state['last_action'],
                    reward=0.5
                )
        
        # 에너지 동기화
        self.state['energy'] = self.hypothalamus.state.energy
        
        # 자동 저장
        if self.auto_save and len(self.conversation_history) % 10 == 0:
            self.save()
    
    def learn(self, content: str, importance: float = 0.7):
        """
        직접 학습 (편도체 감정 강화 적용)
        
        감정적/위협적 내용은 자동으로 기억 강화
        """
        # 편도체로 감정/위협 분석
        memory_result = self.amygdala.enhance_memory(content, base_importance=importance)
        enhanced_importance = memory_result['enhanced_importance']
        
        # 강화 로그
        if memory_result['enhancement_factor'] > 1.1:
            emotion = memory_result['emotion']['dominant']
            boost = memory_result['enhancement_factor']
            print(f"⚡ [{emotion}] 기억 강화: {importance:.2f} → {enhanced_importance:.2f} (x{boost:.2f})")
        
        # 학습
        self.curious.learn(content, importance=enhanced_importance)
    
    def recall(self, query: str, top_n: int = 5) -> List[Dict]:
        """기억 검색"""
        return self.curious.brain.recall(query, top_n=top_n)
    
    # ===== 생체 리듬 =====
    
    def sleep(self, hours: float = 8, verbose: bool = True):
        """
        수면 (동역학적 공고화 + 시상하부 회복)
        
        🌊 v2.0: 동역학적 수면 시스템
            - 노이즈 기반 자발적 replay
            - 수면 단계별 차등 노이즈 (SWS > REM > Light)
            - STP/PTP 반영 consolidation
        
        Args:
            hours: 수면 시간 (1시간 = 10 사이클)
            verbose: 진행 상황 출력
            
        Returns:
            수면 결과 메시지
        """
        if not self.state['awake']:
            return "이미 자고 있어요..."
        
        self.state['awake'] = False
        self.state['mode'] = 'sleep'
        cycles = int(hours * 10)
        
        if verbose:
            print(f"💤 {self.name} 수면 시작 ({hours}시간, {cycles}사이클)...")
            print(f"   🌊 동역학적 수면 모드 (노이즈 기반 replay)")
        
        # 시상하부 수면 시작
        try:
            print(self.hypothalamus.start_sleep())
        except:
            pass
        
        # 🌊 동역학적 수면 공고화 (해마)
        sleep_result = self.curious.sleep(cycles=cycles)
        
        # 수면 결과 출력
        if verbose and isinstance(sleep_result, dict):
            replays = sleep_result.get('replays', 0)
            consolidations = sleep_result.get('consolidations', 0)
            print(f"   📊 수면 결과:")
            print(f"      - Replay: {replays}회")
            print(f"      - 강화: {consolidations}개 시냅스")
            print(f"      - SWS: {sleep_result.get('sws_cycles', 0)}사이클")
            print(f"      - REM: {sleep_result.get('rem_cycles', 0)}사이클")
        
        # 시상하부 수면 사이클 (에너지 회복)
        try:
            result = self.hypothalamus.sleep_cycle(cycles=cycles)
            if verbose:
                print(result)
        except:
            pass
        
        # 기상
        try:
            wake_msg = self.hypothalamus.wake_up()
            if verbose:
                print(wake_msg)
        except:
            pass
        
        # 상태 동기화
        self.state['awake'] = True
        self.state['mode'] = 'wake'
        try:
            self.state['energy'] = self.hypothalamus.state.energy
        except:
            self.state['energy'] = 1.0
        
        if verbose:
            print(f"☀️ {self.name} 기상! 에너지: {self.state['energy']:.0%}")
        
        return f"잘 잤어요! ({hours}시간) 에너지: {self.state['energy']:.0%}"
    
    def grow(self) -> str:
        """
        성장 (개인 LLM 재학습 준비)
        
        해마 기억 → 학습 데이터 생성
        """
        output_path = self.curious.grow()
        return f"성장 준비 완료! 학습 데이터: {output_path}"
    
    # ===== 저장/로드 =====
    
    def save(self, filename: str = None):
        """뇌 상태 저장"""
        if filename is None:
            filename = f"{self.name}_brain.json"
        
        filepath = self.save_dir / filename
        
        data = {
            'version': self.VERSION,
            'name': self.name,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'personality': self.personality,
            'state': self.state,
            'conversation_history': self.conversation_history[-50:],  # 최근 50개만
            'stats': self.get_stats(),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 해마도 저장
        hippo_path = self.save_dir / f"{self.name}_hippo.pkl"
        self.curious.brain.hippo.save(str(hippo_path))
        
        print(f"💾 저장 완료: {filepath}")
    
    def load(self, filename: str = None):
        """뇌 상태 로드"""
        if filename is None:
            filename = f"{self.name}_brain.json"
        
        filepath = self.save_dir / filename
        
        if not filepath.exists():
            print(f"⚠️ 파일 없음: {filepath}")
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.created_at = data.get('created_at', self.created_at)
        self.last_interaction = data.get('last_interaction')
        self.personality = data.get('personality', self.personality)
        self.state = data.get('state', self.state)
        self.conversation_history = data.get('conversation_history', [])
        
        # 해마도 로드
        hippo_path = self.save_dir / f"{self.name}_hippo.pkl"
        if hippo_path.exists():
            self.curious.brain.hippo.load(str(hippo_path))
        
        print(f"📂 로드 완료: {filepath}")
        return True
    
    # ===== 정보 =====
    
    def get_stats(self) -> Dict:
        """통계"""
        curious_stats = self.curious.get_stats()
        
        return {
            'name': self.name,
            'version': self.VERSION,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'conversations': len(self.conversation_history),
            'energy': f"{self.state['energy']:.0%}",
            'awake': self.state['awake'],
            'curious': curious_stats,
        }
    
    def status(self) -> str:
        """상태 출력"""
        stats = self.get_stats()
        
        return f"""
╔══════════════════════════════════════════╗
║  🧠 BabyBrain: {self.name}
╠══════════════════════════════════════════╣
║  버전: {self.VERSION}
║  🧬 DNA: {self.dna.species.value}
║  생성: {self.created_at[:10]}
║  대화: {stats['conversations']}회
║  에너지: {stats['energy']}
║  상태: {'깨어있음 ☀️' if stats['awake'] else '수면중 💤'}
╠══════════════════════════════════════════╣
║  📊 기억
║  - 해마: {stats['curious']['brain']['hippo']['words']}개
║  - 독립도: {stats['curious']['independence']}
╠══════════════════════════════════════════╣
║  🤖 LLM
║  - 개인: {'로드됨 ✅' if stats['curious']['brain']['model_loaded'] else '없음 ❌'}
║  - 도서관: {stats['curious']['library']['provider']}
╚══════════════════════════════════════════╝
"""
    
    def _record_conversation(self, user_msg: str, bot_msg: str):
        """대화 기록"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_msg,
            'bot': bot_msg[:500],  # 500자 제한
        })
        
        # 최대 기록 수 유지
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def __repr__(self):
        return f"BabyBrain('{self.name}', energy={self.state['energy']:.0%})"


# =========================================================
# 🎮 Interactive Demo
# =========================================================

def interactive_demo():
    """인터랙티브 데모"""
    print("=" * 60)
    print("🧠 BabyBrain Interactive Demo v2.1")
    print("=" * 60)
    
    # 성격 선택
    print("\n🧬 성격을 선택하세요:")
    print("  1. quokka  - 친화력↑, 겁↑, 귀여움")
    print("  2. scholar - 호기심↑, 내향적, 분석적")
    print("  3. butler  - 효율적, 침착, 공손")
    print("  4. athlete - 활동적, 단순, 쾌활")
    
    species_input = input("\n선택 (1-4, 기본=1): ").strip()
    species_map = {'1': 'quokka', '2': 'scholar', '3': 'butler', '4': 'athlete'}
    species = species_map.get(species_input, 'quokka')
    
    # 뇌 생성
    brain = BabyBrain(name="demo", species=species)
    
    # 초기 학습
    print("\n📝 초기 학습...")
    brain.learn("저는 babyhippo입니다. 모든 걸 알고 싶은 AI예요.", importance=0.9)
    brain.learn("저는 호기심이 많고 친절해요.", importance=0.8)
    brain.learn("한국어와 영어 모두 할 수 있어요.", importance=0.7)
    
    print(brain.status())
    
    # 대화 루프
    print("\n💬 대화를 시작합니다! (종료: quit, 수면: sleep, 상태: status)")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # 명령어 처리
            if user_input.lower() == 'quit':
                print("\n👋 안녕히 가세요!")
                brain.save()
                break
            elif user_input.lower() == 'sleep':
                result = brain.sleep(hours=2)
                print(f"🤖 {brain.name}: {result}")
                continue
            elif user_input.lower() == 'status':
                print(brain.status())
                continue
            elif user_input.lower() == 'save':
                brain.save()
                continue
            elif user_input.lower() == 'grow':
                result = brain.grow()
                print(f"🤖 {brain.name}: {result}")
                continue
            
            # 대화
            response = brain.chat(user_input)
            
            # 응답 정리 (너무 길면 자르기)
            if len(response) > 300:
                response = response[:300] + "..."
            
            print(f"\n🤖 {brain.name}: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 안녕히 가세요!")
            brain.save()
            break
        except Exception as e:
            print(f"\n❌ 오류: {e}")


# =========================================================
# 🧪 TEST
# =========================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        interactive_demo()
    else:
        print("=" * 60)
        print("🧠 BabyBrain Test")
        print("=" * 60)
        
        # 뇌 생성
        brain = BabyBrain(name="test")
        
        # 학습
        print("\n📝 학습...")
        brain.learn("제 이름은 테스트입니다", importance=0.9)
        brain.learn("파이썬 프로그래밍을 좋아합니다", importance=0.8)
        
        # 대화
        print("\n💬 대화...")
        questions = [
            "안녕!",
            "너 이름이 뭐야?",
            "뭘 좋아해?",
        ]
        
        for q in questions:
            print(f"\n👤: {q}")
            response = brain.chat(q)
            print(f"🤖: {response[:150]}...")
        
        # 상태
        print(brain.status())
        
        # 수면
        brain.sleep(hours=1)
        
        # 저장
        brain.save()
        
        print("\n" + "=" * 60)
        print("✅ 테스트 완료!")
        print("   인터랙티브 모드: python baby_brain.py --demo")
        print("=" * 60)

