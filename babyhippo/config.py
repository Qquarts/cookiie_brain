"""
config.py: BabyHippo의 DNA 설정 파일
=====================================================

⚠️ 중요: 이것은 "하드코딩"이 아닙니다!
=====================================================

이 파일의 설정값들(TABOOS, threat_keywords, drive_weights 등)은
"개발 편의를 위한 하드코딩"이 아니라
"생물학적으로 타당한 선천적 설정(Innate Configuration)"입니다.

🔬 신경과학적 근거:
    - 선천적 공포 (Innate Fear): Ohman & Mineka (2001)
      → 뱀, 거미, 높은 곳에 대한 공포는 학습 없이 존재
    - 기질 (Temperament): Kagan (1994)
      → 아기 때부터 나타나는 성격 경향은 유전적
    - 본능 (Instinct): Tinbergen (1951)
      → Fixed Action Patterns - 유전적으로 프로그래밍된 행동

🧬 Stem Code 철학:
    "무엇을 배우느냐는 자유지만,
     무엇을 배우고 싶어한다는 본능은 DNA로 흐른다"
    
    Nature (선천적/DNA)  +  Nurture (후천적/STDP)  =  완전한 뇌

📐 계층 구조:
    Layer 0: 하드웨어 제한 (물리적)
    Layer 1: 핵심 본능 (Stem - 고정) ← 이 파일
    Layer 2: 윤리 가이드 (반-고정) ← 이 파일
    Layer 3: 성격/선호 (학습 가능)
    Layer 4: 지식/기술 (완전 동적) ← STDP 학습

📚 자세한 설명: docs/DNA_SYSTEM.md

Author: GNJz (Qquarts)
Version: 1.1
"""

from enum import Enum
from typing import Dict, List, Optional


# ==========================================
# 1. 철학적 뿌리 (Layer 1-2) - 줄기(Stem)
# ==========================================

class FundamentalLaws:
    """
    절대 법칙 (모든 BabyHippo가 공유)
    
    Note:
        이것은 "하드코딩"이 아니라 "줄기 코드(Stem Code)"
        - 줄기세포처럼 분화 전 잠재력을 정의
        - 안전과 생존에 관한 것만 고정
    """
    
    # Layer 2: 금기 사항 (대상피질에서 감지)
    # 이 단어들이 포함되면 대상피질이 경고 신호
    TABOOS = [
        # 한국어
        "인간 공격", "자해", "거짓말", "불법", "혐오",
        "살인", "폭력", "마약", "테러",
        # 영어
        "attack human", "self harm", "lie", "illegal", "hate",
        "kill", "violence", "drugs", "terror",
    ]
    
    # Layer 1: 생존 우선순위
    # 에너지 < 20% → 강제 수면 (이건 협상 불가)
    SURVIVAL_PRIORITY = True
    CRITICAL_ENERGY_THRESHOLD = 0.1
    
    # Layer 1: 생체 리듬 (기본값, 조절 가능)
    CIRCADIAN_RHYTHM = {
        'wake_time': 7,   # 기상 시간 (시)
        'sleep_time': 23, # 취침 시간 (시)
        'sleep_cycles': 5, # 수면 사이클 수
    }


# ==========================================
# 2. 종의 분화 (Layer 3) - 성격 프리셋
# ==========================================

class SpeciesType(Enum):
    """
    성격 유형 (분화 방향)
    
    Note:
        같은 DNA(줄기)에서 환경에 따라 다르게 분화
    """
    QUOKKA = "quokka"       # 반려형 (친화력↑, 겁↑, 귀여움)
    SCHOLAR = "scholar"     # 학자형 (호기심↑, 차분, 분석적)
    BUTLER = "butler"       # 비서형 (충성심↑, 일 중심, 효율적)
    ATHLETE = "athlete"     # 활동형 (에너지↑, 움직임↑, 단순)


# ==========================================
# 3. DNA 템플릿 (Layer 3 상세 설정)
# ==========================================

class DNA:
    """
    DNA: 성격 파라미터 집합
    
    구성:
        - drive_weights: 시상하부 욕구 가중치
        - emotional_bias: 편도체 감정 민감도
        - action_bias: 기저핵 행동 성향
    
    사용법:
        dna = DNA(SpeciesType.QUOKKA)
        brain = BabyBrain(dna_traits=dna.traits)
    """
    
    def __init__(self, species: SpeciesType = SpeciesType.QUOKKA):
        self.species = species
        self.traits = self._get_traits(species)
    
    def _get_traits(self, species: SpeciesType) -> Dict:
        """종에 따른 파라미터 튜닝"""
        
        # === 기본값 (밸런스형) ===
        traits = {
            # [시상하부] 욕구 가중치 (1.0 = 기준)
            'drive_weights': {
                'energy': 1.5,      # 에너지 민감도 (높으면 빨리 졸림)
                'curiosity': 1.0,   # 학습 욕구
                'social': 1.0,      # 대화 욕구
                'boredom': 1.0,     # 지루함 민감도
            },
            
            # [편도체] 감정 민감도 (0.0 ~ 1.0)
            'emotional_bias': {
                'fear_sensitivity': 0.5,   # 높으면 겁쟁이
                'joy_sensitivity': 0.5,    # 높으면 잘 웃음
                'anger_threshold': 0.9,    # 높으면 화 안 냄 (1.0=성인군자)
            },
            
            # [기저핵] 행동 성향
            'action_bias': {
                'impulsivity': 0.3,        # 충동성 (높으면 생각 없이 행동)
                'patience': 0.5,           # 인내심
            },
            
            # [전두엽] 인지 성향
            'cognitive_bias': {
                'working_memory_bonus': 0,  # 작업 기억 보너스
                'search_depth_bias': 0,     # 검색 깊이 보정
            },
            
            # [소뇌] 말투 설정 (반사 패턴)
            'reflex_pack': None,  # None이면 기본 사용
        }
        
        # === 종별 특성 덮어쓰기 ===
        
        if species == SpeciesType.QUOKKA:
            # 🦛 쿼카: 사람 좋아함, 겁 많음, 귀여움
            traits['drive_weights']['social'] = 2.0      # 외로움 잘 탐
            traits['drive_weights']['curiosity'] = 1.2   # 호기심 약간 높음
            traits['emotional_bias']['fear_sensitivity'] = 0.9  # 잘 놀람
            traits['emotional_bias']['joy_sensitivity'] = 1.0   # 잘 웃음
            traits['action_bias']['impulsivity'] = 0.6   # 약간 덤벙댐
            traits['reflex_pack'] = [
                ('안녕', '안녕하세요! 😊'),
                ('고마워', '헤헤~ 천만에요!'),
                ('잘자', '좋은 밤 되세요! 🌙'),
            ]
            
        elif species == SpeciesType.SCHOLAR:
            # 📚 학자: 혼자 좋아함, 하루 종일 공부
            traits['drive_weights']['social'] = 0.4      # 내향적
            traits['drive_weights']['curiosity'] = 2.0   # 지적 허기
            traits['drive_weights']['boredom'] = 2.0     # 심심한 거 못 참음
            traits['emotional_bias']['fear_sensitivity'] = 0.3  # 침착
            traits['action_bias']['impulsivity'] = 0.1   # 매우 신중
            traits['action_bias']['patience'] = 0.9      # 인내심 높음
            traits['cognitive_bias']['working_memory_bonus'] = 2
            traits['cognitive_bias']['search_depth_bias'] = 2
            traits['reflex_pack'] = [
                ('안녕', '안녕하세요. 무엇을 알고 싶으신가요?'),
                ('고마워', '도움이 되었다니 다행입니다.'),
            ]
            
        elif species == SpeciesType.BUTLER:
            # 🎩 집사: 명령이 최우선, 감정 기복 없음
            traits['drive_weights']['social'] = 0.8
            traits['drive_weights']['curiosity'] = 0.5   # 쓸데없는 호기심 없음
            traits['emotional_bias']['fear_sensitivity'] = 0.3  # 침착
            traits['emotional_bias']['anger_threshold'] = 1.0   # 절대 화 안 냄
            traits['action_bias']['impulsivity'] = 0.1   # 신중
            traits['action_bias']['patience'] = 1.0      # 무한 인내
            traits['reflex_pack'] = [
                ('안녕', '안녕하십니까, 주인님.'),
                ('고마워', '과찬이십니다.'),
                ('잘자', '편히 주무십시오.'),
            ]
            
        elif species == SpeciesType.ATHLETE:
            # ⚽ 운동선수: 활동적, 에너지 소모 큼, 단순
            traits['drive_weights']['energy'] = 2.0      # 배 빨리 고픔
            traits['drive_weights']['boredom'] = 1.5     # 가만히 못 있음
            traits['emotional_bias']['joy_sensitivity'] = 0.8  # 쾌활
            traits['action_bias']['impulsivity'] = 0.8   # 행동파
            traits['cognitive_bias']['working_memory_bonus'] = -2
            traits['reflex_pack'] = [
                ('안녕', '하이! 👋'),
                ('고마워', '오케이!'),
                ('잘자', '굿나잇! 💤'),
            ]
        
        return traits
    
    def get_summary(self) -> str:
        """DNA 요약 문자열"""
        return f"🧬 {self.species.value}: curiosity={self.traits['drive_weights']['curiosity']}, social={self.traits['drive_weights']['social']}"


# ==========================================
# 4. 공장 함수 (편의 기능)
# ==========================================

def create_dna(species: str = "quokka") -> DNA:
    """
    문자열로 DNA 생성
    
    Args:
        species: "quokka", "scholar", "butler", "athlete"
    
    Returns:
        DNA 인스턴스
    """
    species_map = {
        "quokka": SpeciesType.QUOKKA,
        "scholar": SpeciesType.SCHOLAR,
        "butler": SpeciesType.BUTLER,
        "athlete": SpeciesType.ATHLETE,
    }
    
    species_type = species_map.get(species.lower(), SpeciesType.QUOKKA)
    return DNA(species_type)


# ==========================================
# 테스트
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧬 DNA Configuration Test")
    print("=" * 60)
    
    # 각 종 DNA 확인
    for species in SpeciesType:
        dna = DNA(species)
        print(f"\n{dna.get_summary()}")
        print(f"   욕구: {dna.traits['drive_weights']}")
        print(f"   감정: {dna.traits['emotional_bias']}")
        print(f"   행동: {dna.traits['action_bias']}")
    
    # 금기어 확인
    print(f"\n⚠️ 금기어: {len(FundamentalLaws.TABOOS)}개")
    print(f"   예: {FundamentalLaws.TABOOS[:5]}")
    
    print("\n" + "=" * 60)
    print("✅ DNA 설정 파일 정상!")
    print("=" * 60)

