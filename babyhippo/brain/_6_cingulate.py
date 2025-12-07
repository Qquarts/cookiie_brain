"""
Cingulate Cortex: 대상피질 - 오류 감지 & 갈등 모니터링
=====================================================

🧠 생물학적 모델:
    대상피질 = 뇌의 "품질 관리자"
    
    1. 오류 감지 (Error Detection)
       - "뭔가 잘못됐다!" 신호 (ERN)
       - 예상과 결과의 불일치
       
    2. 갈등 모니터링 (Conflict Monitoring)
       - 여러 반응 간 충돌 감지
       - "어느 쪽이 맞지?"
       
    3. 인지 제어 (Cognitive Control)
       - 전두엽에 "더 집중해!" 신호
       - 행동 조절 트리거

📐 핵심 수식:
    오류 신호: E = |expected - actual|
    갈등 신호: C = Σ(p_i · p_j · |r_i - r_j|)
    제어 신호: Control = σ(w_e·E + w_c·C - θ)

📚 참고 논문:
    - Botvinick (2001): Conflict monitoring and cognitive control
    - Gehring (1993): Error-related negativity (ERN)
    - Holroyd & Coles (2002): Reinforcement learning theory of ACC

v1.1 변경사항:
- 금기어(Taboo) 검열 기능 추가
- 외부 금기어 리스트 주입 지원

Author: GNJz (Qquarts)
Version: 1.1
"""

import math
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum


# ============================================
# 데이터 클래스
# ============================================

class ErrorType(Enum):
    """오류 유형"""
    PREDICTION = "prediction_error"     # 예측 오류
    RESPONSE = "response_error"         # 응답 오류
    CONFLICT = "conflict_error"         # 갈등/충돌
    PERFORMANCE = "performance_error"   # 성능 저하
    INCONSISTENCY = "inconsistency"     # 불일치


@dataclass
class ErrorSignal:
    """오류 신호"""
    error_type: ErrorType
    magnitude: float            # 오류 크기 (0~1)
    source: str                 # 오류 출처
    description: str            # 설명
    requires_attention: bool    # 주의 필요 여부
    timestamp: float = field(default_factory=time.time)


@dataclass
class ConflictSignal:
    """갈등 신호"""
    options: List[str]          # 충돌하는 옵션들
    conflict_level: float       # 갈등 수준 (0~1)
    recommendation: str         # 권장 해결책
    timestamp: float = field(default_factory=time.time)


@dataclass
class ControlSignal:
    """제어 신호 (전두엽으로 전송)"""
    action: str                 # 권장 행동
    urgency: float              # 긴급도 (0~1)
    reason: str                 # 이유
    adjustments: Dict[str, Any] # 권장 조정사항


# ============================================
# 대상피질 핵심 클래스
# ============================================

class CingulateCortex:
    """
    대상피질 (Cingulate Cortex)
    
    오류 감지, 갈등 모니터링, 인지 제어 시스템
    
    구조:
        ACC (전대상피질) - 오류/갈등 감지
        MCC (중대상피질) - 운동 제어
        PCC (후대상피질) - 자기 참조, 기억
    """
    
    def __init__(self, taboos: Optional[List[str]] = None):
        """
        대상피질 초기화
        
        Args:
            taboos: 금기어 리스트 (DNA/Config에서 주입)
                    예: ["공격", "자해", "욕설", "혐오"]
        
        Note:
            v1.1: 금기어 검열 기능 추가 (Stem Code 철학)
            - 빈 리스트 = 검열 없음 (기본)
            - 외부 주입 = config.py의 FundamentalLaws.TABOOS 연동
        """
        # ===== 오류 기록 =====
        self.error_history: deque = deque(maxlen=100)
        self.conflict_history: deque = deque(maxlen=50)
        
        # ===== 기대값 저장 =====
        self.expectations: Dict[str, Any] = {}
        
        # [v1.1] 금기어 리스트 (외부 주입)
        self.taboos: List[str] = taboos if taboos else []
        
        # ===== 파라미터 =====
        self.params = {
            'error_threshold': 0.3,     # 오류 감지 임계값
            'conflict_threshold': 0.5,  # 갈등 감지 임계값
            'control_threshold': 0.6,   # 제어 신호 발생 임계값
            'sensitivity': 1.0,         # 민감도 (높을수록 작은 오류도 감지)
            'adaptation_rate': 0.1,     # 적응율 (오류 후 기대값 조정)
        }
        
        # ===== 상태 =====
        self.current_error_level = 0.0
        self.current_conflict_level = 0.0
        self.vigilance_mode = False  # 경계 모드
        
        # ===== 통계 =====
        self.stats = {
            'errors_detected': 0,
            'conflicts_detected': 0,
            'control_signals_sent': 0,
            'corrections_made': 0,
            'taboo_violations': 0,  # [v1.1] 금기 위반 횟수
        }
    
    # ============================================
    # 1. 오류 감지 (Error Detection)
    # ============================================
    
    def detect_error(self, 
                     expected: Any, 
                     actual: Any,
                     context: str = "") -> Optional[ErrorSignal]:
        """
        오류 감지
        
        E = |expected - actual| (정규화)
        
        Args:
            expected: 기대값
            actual: 실제값
            context: 맥락
            
        Returns:
            ErrorSignal if error detected, None otherwise
        """
        # 오류 크기 계산
        magnitude = self._calculate_error_magnitude(expected, actual)
        
        # 임계값 체크
        threshold = self.params['error_threshold'] / self.params['sensitivity']
        
        if magnitude >= threshold:
            error = ErrorSignal(
                error_type=ErrorType.PREDICTION,
                magnitude=magnitude,
                source=context,
                description=f"예상: {expected}, 실제: {actual}",
                requires_attention=magnitude > 0.5
            )
            
            self.error_history.append(error)
            self.current_error_level = magnitude
            self.stats['errors_detected'] += 1
            
            # 기대값 적응
            self._adapt_expectation(context, expected, actual)
            
            return error
        
        return None
    
    def _calculate_error_magnitude(self, expected: Any, actual: Any) -> float:
        """오류 크기 계산"""
        # 숫자인 경우
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            max_val = max(abs(expected), abs(actual), 1)
            return min(1.0, abs(expected - actual) / max_val)
        
        # 문자열인 경우 (유사도 기반)
        if isinstance(expected, str) and isinstance(actual, str):
            return 1.0 - self._string_similarity(expected, actual)
        
        # 불리언인 경우
        if isinstance(expected, bool) and isinstance(actual, bool):
            return 0.0 if expected == actual else 1.0
        
        # 리스트인 경우
        if isinstance(expected, list) and isinstance(actual, list):
            if not expected and not actual:
                return 0.0
            common = len(set(expected) & set(actual))
            total = len(set(expected) | set(actual))
            return 1.0 - (common / total if total > 0 else 0)
        
        # 기타: 단순 동등 비교
        return 0.0 if expected == actual else 1.0
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """문자열 유사도 (간단한 구현)"""
        if not s1 or not s2:
            return 0.0
        
        s1_lower = s1.lower()
        s2_lower = s2.lower()
        
        # 완전 일치
        if s1_lower == s2_lower:
            return 1.0
        
        # 포함 관계
        if s1_lower in s2_lower or s2_lower in s1_lower:
            return 0.7
        
        # 공통 단어
        words1 = set(s1_lower.split())
        words2 = set(s2_lower.split())
        common = len(words1 & words2)
        total = len(words1 | words2)
        
        return common / total if total > 0 else 0.0
    
    def _adapt_expectation(self, context: str, expected: Any, actual: Any):
        """기대값 적응 (학습)"""
        if not context:
            return
        
        rate = self.params['adaptation_rate']
        
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # 숫자: 이동 평균
            old = self.expectations.get(context, expected)
            self.expectations[context] = old + rate * (actual - old)
    
    def check_taboo(self, text: str) -> Optional[ErrorSignal]:
        """
        [v1.1] 금기어 검열 (사회적/윤리적 모니터링)
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            ErrorSignal if taboo detected, None otherwise
        """
        if not text or not self.taboos:
            return None
        
        text_lower = text.lower()
        
        for taboo in self.taboos:
            if taboo.lower() in text_lower:
                error = ErrorSignal(
                    error_type=ErrorType.INCONSISTENCY,
                    magnitude=1.0,  # 심각한 오류
                    source="ethical_filter",
                    description=f"금기어 감지: '{taboo}'",
                    requires_attention=True
                )
                
                self.error_history.append(error)
                self.stats['errors_detected'] += 1
                self.stats['taboo_violations'] += 1
                
                return error
        
        return None
    
    def check_response_error(self, 
                             response: str,
                             context: str = "") -> Optional[ErrorSignal]:
        """
        응답 오류 체크 (품질 검사)
        
        Args:
            response: 생성된 응답
            context: 맥락
            
        Returns:
            ErrorSignal if error detected
        """
        # [v1.1] 금기어 체크 (최우선)
        taboo_error = self.check_taboo(response)
        if taboo_error:
            return taboo_error
        
        errors = []
        
        # 1. 빈 응답
        if not response or len(response.strip()) == 0:
            errors.append(("빈 응답", 0.8))
        
        # 2. 너무 짧은 응답
        elif len(response) < 5:
            errors.append(("응답 너무 짧음", 0.5))
        
        # 3. 반복 감지
        if self._detect_repetition(response):
            errors.append(("반복 감지", 0.6))
        
        # 4. 깨진 문자 감지
        if self._detect_broken_chars(response):
            errors.append(("깨진 문자", 0.7))
        
        # 가장 심각한 오류 반환
        if errors:
            worst = max(errors, key=lambda x: x[1])
            
            error = ErrorSignal(
                error_type=ErrorType.RESPONSE,
                magnitude=worst[1],
                source=context,
                description=worst[0],
                requires_attention=worst[1] > 0.5
            )
            
            self.error_history.append(error)
            self.stats['errors_detected'] += 1
            
            return error
        
        return None
    
    def _detect_repetition(self, text: str) -> bool:
        """반복 감지"""
        if len(text) < 10:
            return False
        
        # 연속 반복 패턴 (예: "안녕안녕안녕")
        for length in range(2, min(10, len(text) // 3)):
            pattern = text[:length]
            if text.count(pattern) >= 3:
                return True
        
        return False
    
    def _detect_broken_chars(self, text: str) -> bool:
        """깨진 문자 감지"""
        # 연속된 특수문자
        import re
        if re.search(r'[\x00-\x1f]{2,}', text):
            return True
        
        # 너무 많은 물음표/느낌표
        if text.count('?') > 5 or text.count('!') > 5:
            return True
        
        return False
    
    # ============================================
    # 2. 갈등 모니터링 (Conflict Monitoring)
    # ============================================
    
    def detect_conflict(self, 
                        options: List[Tuple[str, float]]) -> Optional[ConflictSignal]:
        """
        갈등 감지
        
        C = Σ(p_i · p_j · |r_i - r_j|)
        
        비슷한 확률의 옵션이 여러 개 있으면 갈등
        
        Args:
            options: [(옵션명, 확률/점수), ...]
            
        Returns:
            ConflictSignal if conflict detected
        """
        if len(options) < 2:
            return None
        
        # 확률 정규화
        total = sum(score for _, score in options)
        if total == 0:
            return None
        
        probs = [(name, score / total) for name, score in options]
        
        # 갈등 수준 계산
        # 상위 2개 옵션 간 확률 차이가 작으면 갈등
        sorted_options = sorted(probs, key=lambda x: x[1], reverse=True)
        
        if len(sorted_options) >= 2:
            top1_name, top1_prob = sorted_options[0]
            top2_name, top2_prob = sorted_options[1]
            
            # 확률 차이가 작으면 갈등
            diff = top1_prob - top2_prob
            conflict_level = 1.0 - diff  # 차이 작을수록 갈등 높음
            
            # 두 옵션 모두 의미 있는 확률이어야 함
            if top2_prob > 0.2:
                conflict_level *= (top2_prob / top1_prob)
            else:
                conflict_level *= 0.3
            
            if conflict_level > self.params['conflict_threshold']:
                conflict = ConflictSignal(
                    options=[top1_name, top2_name],
                    conflict_level=conflict_level,
                    recommendation=f"'{top1_name}'이 약간 우세 ({top1_prob:.2f} vs {top2_prob:.2f})"
                )
                
                self.conflict_history.append(conflict)
                self.current_conflict_level = conflict_level
                self.stats['conflicts_detected'] += 1
                
                return conflict
        
        return None
    
    # ============================================
    # 3. 인지 제어 (Cognitive Control)
    # ============================================
    
    def generate_control_signal(self) -> Optional[ControlSignal]:
        """
        제어 신호 생성 (전두엽으로 전송)
        
        Control = σ(w_e·E + w_c·C - θ)
        """
        # 가중 합산
        combined = 0.6 * self.current_error_level + 0.4 * self.current_conflict_level
        
        if combined < self.params['control_threshold']:
            return None
        
        # 제어 신호 생성
        adjustments = {}
        action = "monitor"
        reason = ""
        
        if self.current_error_level > 0.5:
            action = "correct"
            reason = "오류 수준 높음"
            adjustments['reduce_temperature'] = True
            adjustments['increase_caution'] = True
        
        if self.current_conflict_level > 0.5:
            if action == "monitor":
                action = "deliberate"
            reason += " / 갈등 상태" if reason else "갈등 상태"
            adjustments['take_more_time'] = True
            adjustments['consider_alternatives'] = True
        
        control = ControlSignal(
            action=action,
            urgency=combined,
            reason=reason,
            adjustments=adjustments
        )
        
        self.stats['control_signals_sent'] += 1
        
        return control
    
    def request_correction(self, original: str, error: ErrorSignal) -> Dict[str, Any]:
        """
        수정 요청 생성
        
        Args:
            original: 원본
            error: 감지된 오류
            
        Returns:
            수정 요청 정보
        """
        self.stats['corrections_made'] += 1
        
        return {
            'original': original,
            'error_type': error.error_type.value,
            'error_description': error.description,
            'suggestion': self._get_correction_suggestion(error),
            'urgency': error.magnitude,
        }
    
    def _get_correction_suggestion(self, error: ErrorSignal) -> str:
        """수정 제안 생성"""
        suggestions = {
            ErrorType.PREDICTION: "기대값을 재조정하거나 입력을 확인하세요.",
            ErrorType.RESPONSE: "응답을 다시 생성하거나 다른 방식을 시도하세요.",
            ErrorType.CONFLICT: "우선순위를 명확히 하거나 추가 정보를 수집하세요.",
            ErrorType.PERFORMANCE: "처리 속도나 리소스를 확인하세요.",
            ErrorType.INCONSISTENCY: "데이터 일관성을 확인하세요.",
        }
        
        return suggestions.get(error.error_type, "상황을 재검토하세요.")
    
    # ============================================
    # 4. 경계 모드 (Vigilance)
    # ============================================
    
    def enter_vigilance_mode(self):
        """경계 모드 진입 (민감도 증가)"""
        self.vigilance_mode = True
        self.params['sensitivity'] = 1.5
        return "🔍 대상피질: 경계 모드 - 오류 감지 민감도 증가"
    
    def exit_vigilance_mode(self):
        """경계 모드 해제"""
        self.vigilance_mode = False
        self.params['sensitivity'] = 1.0
        return "✅ 대상피질: 정상 모드 복귀"
    
    # ============================================
    # 5. 상태 조회
    # ============================================
    
    def get_state(self) -> Dict[str, Any]:
        """전체 상태 반환"""
        return {
            'current_error_level': round(self.current_error_level, 2),
            'current_conflict_level': round(self.current_conflict_level, 2),
            'vigilance_mode': self.vigilance_mode,
            'recent_errors': len(self.error_history),
            'recent_conflicts': len(self.conflict_history),
            'stats': self.stats,
        }
    
    def get_recent_errors(self, n: int = 5) -> List[ErrorSignal]:
        """최근 오류 반환"""
        return list(self.error_history)[-n:]
    
    def reset_levels(self):
        """오류/갈등 수준 리셋"""
        self.current_error_level = 0.0
        self.current_conflict_level = 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        return self.stats.copy()


# ============================================
# 테스트
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Cingulate Cortex (대상피질) 테스트")
    print("=" * 60)
    
    acc = CingulateCortex()
    
    # 1. 오류 감지 테스트
    print("\n⚠️ [1] 오류 감지 테스트")
    print("-" * 40)
    
    # 예측 오류
    error = acc.detect_error(expected=100, actual=50, context="점수 예측")
    if error:
        print(f"  예측 오류 감지!")
        print(f"    크기: {error.magnitude:.2f}")
        print(f"    설명: {error.description}")
    
    # 문자열 비교
    error = acc.detect_error(expected="안녕하세요", actual="안녕!", context="인사")
    if error:
        print(f"  문자열 불일치!")
        print(f"    크기: {error.magnitude:.2f}")
    
    # 2. 응답 오류 체크
    print("\n📝 [2] 응답 품질 체크")
    print("-" * 40)
    
    responses = [
        "좋은 응답입니다.",
        "",
        "Hi",
        "안녕안녕안녕안녕안녕안녕",
    ]
    
    for resp in responses:
        error = acc.check_response_error(resp)
        if error:
            print(f"  '{resp[:20]}...' → ❌ {error.description}")
        else:
            print(f"  '{resp[:20]}...' → ✅ OK")
    
    # 3. 갈등 감지 테스트
    print("\n🤔 [3] 갈등 감지 테스트")
    print("-" * 40)
    
    # 갈등 없음 (명확한 우위)
    options1 = [("옵션A", 0.8), ("옵션B", 0.2)]
    conflict = acc.detect_conflict(options1)
    print(f"  {options1} → {'갈등!' if conflict else '명확'}")
    
    # 갈등 있음 (비슷한 점수)
    options2 = [("옵션A", 0.52), ("옵션B", 0.48)]
    conflict = acc.detect_conflict(options2)
    if conflict:
        print(f"  {options2} → 갈등! (수준: {conflict.conflict_level:.2f})")
        print(f"    권장: {conflict.recommendation}")
    
    # 4. 제어 신호 생성
    print("\n🎮 [4] 제어 신호 생성")
    print("-" * 40)
    
    # 오류 수준 높이기
    acc.current_error_level = 0.7
    acc.current_conflict_level = 0.6
    
    control = acc.generate_control_signal()
    if control:
        print(f"  행동: {control.action}")
        print(f"  긴급도: {control.urgency:.2f}")
        print(f"  이유: {control.reason}")
        print(f"  조정: {control.adjustments}")
    
    # 5. 경계 모드
    print("\n🔍 [5] 경계 모드")
    print("-" * 40)
    print(f"  {acc.enter_vigilance_mode()}")
    print(f"  민감도: {acc.params['sensitivity']}")
    print(f"  {acc.exit_vigilance_mode()}")
    
    # 6. 상태 확인
    print("\n📊 [6] 전체 상태")
    print("-" * 40)
    state = acc.get_state()
    print(f"  오류 수준: {state['current_error_level']}")
    print(f"  갈등 수준: {state['current_conflict_level']}")
    print(f"  통계: {state['stats']}")
    
    print("\n" + "=" * 60)
    print("✅ 대상피질 테스트 완료!")
    print("=" * 60)

