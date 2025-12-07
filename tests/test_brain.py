"""
BabyHippo Brain Module Tests
============================

pytest tests/test_brain.py -v
"""

import pytest
import sys
sys.path.insert(0, '..')


class TestThalamus:
    """시상 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import Thalamus, SensoryInput, ModalityType
        assert Thalamus is not None
    
    def test_basic_relay(self):
        """기본 중계 테스트"""
        from babyhippo import Thalamus, SensoryInput, ModalityType
        
        thalamus = Thalamus()
        inputs = [
            SensoryInput(
                modality=ModalityType.TEXT,
                content="Hello",
                intensity=0.8
            )
        ]
        
        outputs = thalamus.relay(inputs)
        assert len(outputs) > 0
    
    def test_consciousness_gate(self):
        """의식 게이트 테스트"""
        from babyhippo import Thalamus, SensoryInput, ModalityType
        
        thalamus = Thalamus()
        thalamus.sleep_mode()  # 수면 모드
        
        inputs = [
            SensoryInput(
                modality=ModalityType.TEXT,
                content="Hello",
                intensity=0.8
            )
        ]
        
        outputs = thalamus.relay(inputs)
        assert len(outputs) == 0  # 수면 중에는 입력 차단


class TestAmygdala:
    """편도체 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import Amygdala
        assert Amygdala is not None
    
    def test_threat_detection(self):
        """위협 감지 테스트"""
        from babyhippo import Amygdala
        
        amygdala = Amygdala()
        
        # 위협 문장 테스트
        threat = amygdala.detect_threat("위험해! 도망쳐!")
        assert threat is not None
        assert threat.level > 0
    
    def test_no_threat(self):
        """위협 없는 문장 테스트"""
        from babyhippo import Amygdala
        
        amygdala = Amygdala()
        
        # 평범한 문장
        threat = amygdala.detect_threat("오늘 날씨가 좋네요")
        # 위협이 없거나 낮은 수준
        assert threat is None or threat.level < 0.3
    
    def test_emotion_processing(self):
        """감정 처리 테스트"""
        from babyhippo import Amygdala
        
        amygdala = Amygdala()
        
        emotion = amygdala.process_emotion("정말 기분 좋아!")
        assert emotion is not None
        assert hasattr(emotion, 'dominant')


class TestHypothalamus:
    """시상하부 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import Hypothalamus
        assert Hypothalamus is not None
    
    def test_tick(self):
        """틱 업데이트 테스트"""
        from babyhippo import Hypothalamus
        
        hypo = Hypothalamus()
        initial_energy = hypo.state.energy
        
        # 활동으로 에너지 소모
        hypo.tick(action_type='think')
        
        # 에너지가 약간 감소해야 함
        assert hypo.state.energy <= initial_energy
    
    def test_drives(self):
        """욕구 생성 테스트"""
        from babyhippo import Hypothalamus
        
        hypo = Hypothalamus()
        
        # 에너지를 낮춰서 수면 욕구 유발
        hypo.state.energy = 0.1
        
        drive = hypo.get_top_drive()
        assert drive is not None


class TestBasalGanglia:
    """기저핵 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import BasalGanglia
        assert BasalGanglia is not None
    
    def test_action_selection(self):
        """행동 선택 테스트"""
        from babyhippo import BasalGanglia
        
        bg = BasalGanglia()
        
        action = bg.select_action(
            context="greeting",
            available_actions=["respond", "ignore", "ask"]
        )
        
        assert action is not None
        assert action.name in ["respond", "ignore", "ask"]


class TestPrefrontalCortex:
    """전두엽 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import PrefrontalCortex
        assert PrefrontalCortex is not None
    
    def test_query_analysis(self):
        """쿼리 분석 테스트"""
        from babyhippo import PrefrontalCortex
        
        pfc = PrefrontalCortex()
        
        analysis = pfc.analyze_query("파이썬이 뭐야?")
        
        assert 'intents' in analysis
        assert 'keywords' in analysis


class TestCingulateCortex:
    """대상피질 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import CingulateCortex
        assert CingulateCortex is not None
    
    def test_error_detection(self):
        """오류 감지 테스트"""
        from babyhippo import CingulateCortex
        
        cingulate = CingulateCortex()
        
        # 빈 응답 = 오류
        error = cingulate.check_response_error("")
        assert error is not None


class TestCerebellum:
    """소뇌 모듈 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import Cerebellum
        assert Cerebellum is not None
    
    def test_reflex(self):
        """반사 테스트"""
        from babyhippo import Cerebellum
        
        cerebellum = Cerebellum()
        
        # 기본 반사 패턴 테스트
        reflex = cerebellum.check_reflex("안녕")
        # 반사가 있거나 없을 수 있음 (설정에 따라)


class TestDNA:
    """DNA 설정 테스트"""
    
    def test_import(self):
        """임포트 테스트"""
        from babyhippo import DNA, SpeciesType
        assert DNA is not None
        assert SpeciesType is not None
    
    def test_quokka(self):
        """쿼카 성격 테스트"""
        from babyhippo import DNA, SpeciesType
        
        dna = DNA(SpeciesType.QUOKKA)
        
        # 쿼카는 사회성이 높아야 함
        assert dna.traits['drive_weights']['social'] >= 1.5
    
    def test_scholar(self):
        """학자 성격 테스트"""
        from babyhippo import DNA, SpeciesType
        
        dna = DNA(SpeciesType.SCHOLAR)
        
        # 학자는 호기심이 높아야 함
        assert dna.traits['drive_weights']['curiosity'] >= 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

