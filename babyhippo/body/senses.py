"""
Senses: 감각 기관 (Peripheral Sensors)
======================================

👁️ 눈 (Eyes): 카메라, 이미지
👂 귀 (Ears): 마이크, 음성
⌨️ 텍스트: 키보드 입력

역할:
    외부 세계의 Raw Input → 시상(Thalamus)이 이해할 수 있는 SensoryInput으로 변환

흐름:
    [Microphone] → EarInput.listen() → SensoryInput(AUDITORY)
    [Camera] → EyeInput.see() → SensoryInput(VISUAL)
    [Keyboard] → TextInput.read() → SensoryInput(SEMANTIC)

Author: GNJz (Qquarts)
Version: 1.0
"""

import time
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


class SensorType(Enum):
    """감각 유형"""
    VISUAL = "visual"       # 시각 (카메라)
    AUDITORY = "auditory"   # 청각 (마이크)
    TACTILE = "tactile"     # 촉각 (센서)
    TEXT = "text"           # 텍스트 (키보드)
    INTERNAL = "internal"   # 내부 감각 (배터리 등)


@dataclass
class RawInput:
    """Raw 센서 입력"""
    sensor_type: SensorType
    data: Any
    timestamp: float
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EyeInput:
    """
    👁️ 눈 (시각 입력)
    
    카메라 또는 이미지 파일에서 시각 정보 수집
    """
    
    def __init__(self):
        self.camera = None
        self.last_frame = None
        self.is_active = False
        
        # 통계
        self.stats = {
            'frames_captured': 0,
            'objects_detected': 0,
        }
    
    def activate(self) -> bool:
        """카메라 활성화"""
        try:
            # OpenCV 사용 (설치되어 있으면)
            import cv2
            self.camera = cv2.VideoCapture(0)
            self.is_active = self.camera.isOpened()
            return self.is_active
        except ImportError:
            print("⚠️ OpenCV가 설치되지 않았습니다. 시각 입력 비활성화.")
            self.is_active = False
            return False
    
    def deactivate(self):
        """카메라 비활성화"""
        if self.camera:
            self.camera.release()
            self.camera = None
        self.is_active = False
    
    def see(self) -> Optional[RawInput]:
        """
        한 프레임 캡처
        
        Returns:
            RawInput(VISUAL) 또는 None
        """
        if not self.is_active or self.camera is None:
            return None
        
        try:
            import cv2
            ret, frame = self.camera.read()
            
            if ret:
                self.last_frame = frame
                self.stats['frames_captured'] += 1
                
                return RawInput(
                    sensor_type=SensorType.VISUAL,
                    data=frame,
                    timestamp=time.time(),
                    metadata={
                        'width': frame.shape[1],
                        'height': frame.shape[0],
                        'channels': frame.shape[2] if len(frame.shape) > 2 else 1,
                    }
                )
        except Exception as e:
            print(f"❌ 시각 입력 오류: {e}")
        
        return None
    
    def see_image(self, image_path: str) -> Optional[RawInput]:
        """이미지 파일에서 읽기"""
        try:
            import cv2
            frame = cv2.imread(image_path)
            
            if frame is not None:
                return RawInput(
                    sensor_type=SensorType.VISUAL,
                    data=frame,
                    timestamp=time.time(),
                    metadata={
                        'source': 'file',
                        'path': image_path,
                    }
                )
        except ImportError:
            # OpenCV 없으면 PIL 시도
            try:
                from PIL import Image
                import numpy as np
                img = Image.open(image_path)
                frame = np.array(img)
                
                return RawInput(
                    sensor_type=SensorType.VISUAL,
                    data=frame,
                    timestamp=time.time(),
                    metadata={'source': 'file', 'path': image_path}
                )
            except:
                pass
        
        return None


class EarInput:
    """
    👂 귀 (청각 입력)
    
    마이크에서 음성 수집 및 STT(Speech-to-Text)
    """
    
    def __init__(self):
        self.microphone = None
        self.recognizer = None
        self.is_active = False
        
        # STT 설정
        self.stt_engine = None  # 'google', 'whisper', 'local'
        
        # 통계
        self.stats = {
            'recordings': 0,
            'transcriptions': 0,
        }
    
    def activate(self, stt_engine: str = 'google') -> bool:
        """마이크 활성화"""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.stt_engine = stt_engine
            self.is_active = True
            
            # 노이즈 조정
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            return True
        except ImportError:
            print("⚠️ SpeechRecognition이 설치되지 않았습니다. 청각 입력 비활성화.")
            self.is_active = False
            return False
        except Exception as e:
            print(f"⚠️ 마이크 활성화 실패: {e}")
            self.is_active = False
            return False
    
    def deactivate(self):
        """마이크 비활성화"""
        self.microphone = None
        self.recognizer = None
        self.is_active = False
    
    def listen(self, timeout: float = 5.0) -> Optional[RawInput]:
        """
        음성 듣기 (STT 포함)
        
        Returns:
            RawInput(AUDITORY) - data에 텍스트 포함
        """
        if not self.is_active:
            return None
        
        try:
            import speech_recognition as sr
            
            with self.microphone as source:
                print("🎤 듣는 중...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            self.stats['recordings'] += 1
            
            # STT
            text = self._transcribe(audio)
            
            if text:
                self.stats['transcriptions'] += 1
                return RawInput(
                    sensor_type=SensorType.AUDITORY,
                    data=text,
                    timestamp=time.time(),
                    metadata={
                        'stt_engine': self.stt_engine,
                        'audio_duration': len(audio.frame_data) / audio.sample_rate,
                    }
                )
        except Exception as e:
            print(f"❌ 청각 입력 오류: {e}")
        
        return None
    
    def _transcribe(self, audio) -> Optional[str]:
        """음성 → 텍스트 변환"""
        try:
            if self.stt_engine == 'google':
                return self.recognizer.recognize_google(audio, language='ko-KR')
            elif self.stt_engine == 'whisper':
                return self.recognizer.recognize_whisper(audio, language='ko')
            else:
                return self.recognizer.recognize_google(audio, language='ko-KR')
        except Exception as e:
            print(f"⚠️ STT 실패: {e}")
            return None
    
    def listen_from_file(self, audio_path: str) -> Optional[RawInput]:
        """오디오 파일에서 읽기"""
        if not self.recognizer:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
            except ImportError:
                return None
        
        try:
            import speech_recognition as sr
            
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            text = self._transcribe(audio)
            
            if text:
                return RawInput(
                    sensor_type=SensorType.AUDITORY,
                    data=text,
                    timestamp=time.time(),
                    metadata={'source': 'file', 'path': audio_path}
                )
        except Exception as e:
            print(f"❌ 오디오 파일 처리 오류: {e}")
        
        return None


class TextInput:
    """
    ⌨️ 텍스트 입력
    
    키보드 또는 파일에서 텍스트 수집
    가장 기본적인 입력 방식
    """
    
    def __init__(self):
        self.buffer: List[str] = []
        
        # 통계
        self.stats = {
            'inputs_received': 0,
            'total_chars': 0,
        }
    
    def read(self, text: str) -> RawInput:
        """
        텍스트 입력 처리
        
        Args:
            text: 입력 텍스트
            
        Returns:
            RawInput(TEXT)
        """
        self.stats['inputs_received'] += 1
        self.stats['total_chars'] += len(text)
        self.buffer.append(text)
        
        return RawInput(
            sensor_type=SensorType.TEXT,
            data=text,
            timestamp=time.time(),
            metadata={
                'length': len(text),
                'words': len(text.split()),
            }
        )
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[RawInput]:
        """파일에서 텍스트 읽기"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            
            return self.read(text)
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
            return None
    
    def get_history(self, n: int = 10) -> List[str]:
        """최근 입력 기록"""
        return self.buffer[-n:]


class Senses:
    """
    🎭 통합 감각 시스템
    
    모든 감각 기관을 통합 관리
    """
    
    def __init__(self):
        self.eyes = EyeInput()
        self.ears = EarInput()
        self.text = TextInput()
        
        # 내부 센서 (배터리, 온도 등)
        self.internal_state = {
            'battery': 1.0,
            'temperature': 0.5,  # 정상 범위
        }
        
        # 통계
        self.stats = {
            'total_inputs': 0,
        }
    
    def activate_all(self) -> Dict[str, bool]:
        """모든 센서 활성화"""
        return {
            'eyes': self.eyes.activate(),
            'ears': self.ears.activate(),
            'text': True,  # 텍스트는 항상 활성
        }
    
    def deactivate_all(self):
        """모든 센서 비활성화"""
        self.eyes.deactivate()
        self.ears.deactivate()
    
    def sense(self, modality: SensorType, data: Any = None) -> Optional[RawInput]:
        """
        감각 수집 (통합 인터페이스)
        
        Args:
            modality: 감각 유형
            data: 텍스트의 경우 직접 데이터 전달
            
        Returns:
            RawInput 또는 None
        """
        self.stats['total_inputs'] += 1
        
        if modality == SensorType.VISUAL:
            return self.eyes.see()
        elif modality == SensorType.AUDITORY:
            return self.ears.listen()
        elif modality == SensorType.TEXT:
            if data:
                return self.text.read(data)
        elif modality == SensorType.INTERNAL:
            return RawInput(
                sensor_type=SensorType.INTERNAL,
                data=self.internal_state.copy(),
                timestamp=time.time()
            )
        
        return None
    
    def to_sensory_input(self, raw: RawInput):
        """
        RawInput → SensoryInput 변환 (시상용)
        
        brain/_1_thalamus.py의 SensoryInput 형식으로 변환
        """
        from ..brain import SensoryInput, ModalityType
        
        # SensorType → ModalityType 매핑
        modality_map = {
            SensorType.VISUAL: ModalityType.VISUAL,
            SensorType.AUDITORY: ModalityType.AUDITORY,
            SensorType.TEXT: ModalityType.SEMANTIC,
            SensorType.INTERNAL: ModalityType.SEMANTIC,
        }
        
        modality = modality_map.get(raw.sensor_type, ModalityType.SEMANTIC)
        
        # 데이터를 문자열로 변환 (시상이 처리할 수 있도록)
        if isinstance(raw.data, str):
            content = raw.data
        elif raw.sensor_type == SensorType.VISUAL:
            content = f"[이미지: {raw.metadata.get('width', '?')}x{raw.metadata.get('height', '?')}]"
        elif raw.sensor_type == SensorType.INTERNAL:
            content = f"[내부상태: 배터리={raw.data.get('battery', '?'):.0%}]"
        else:
            content = str(raw.data)
        
        return SensoryInput(
            modality=modality,
            content=content,
            intensity=0.7,  # 기본 강도
            timestamp=raw.timestamp
        )
    
    def get_stats(self) -> Dict:
        """통계"""
        return {
            'total_inputs': self.stats['total_inputs'],
            'eyes': self.eyes.stats,
            'ears': self.ears.stats,
            'text': self.text.stats,
        }

