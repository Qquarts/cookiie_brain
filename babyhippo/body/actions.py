"""
Actions: 운동 기관 (Motor Output)
=================================

🗣️ 입 (Mouth): TTS, 텍스트 출력
🦿 모터 (Motor): 로봇 제어

역할:
    뇌의 결정(Action) → 물리적 실행
    소뇌(Cerebellum)에서 다듬은 출력을 세상에 내보냄

흐름:
    [Cerebellum] → Action → SpeechOutput.speak() → [Speaker]
    [Cerebellum] → Action → TextOutput.write() → [Screen]
    [BasalGanglia] → Action → MotorOutput.move() → [Robot]

Author: GNJz (Qquarts)
Version: 1.0
"""

import time
from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


class ActionType(Enum):
    """행동 유형"""
    SPEAK = "speak"         # 말하기 (TTS)
    WRITE = "write"         # 텍스트 출력
    MOVE = "move"           # 모터 제어
    GESTURE = "gesture"     # 표정/제스처
    INTERNAL = "internal"   # 내부 행동 (학습 등)


@dataclass
class ActionCommand:
    """행동 명령"""
    action_type: ActionType
    content: Any
    priority: float = 0.5       # 0.0 ~ 1.0
    duration: float = None      # 실행 시간 (초)
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ActionResult:
    """행동 결과"""
    success: bool
    action_type: ActionType
    message: str
    duration: float
    metadata: Dict = None


class SpeechOutput:
    """
    🗣️ 말하기 (TTS)
    
    텍스트 → 음성 변환 및 출력
    """
    
    def __init__(self):
        self.tts_engine = None
        self.is_active = False
        
        # 음성 설정
        self.voice_settings = {
            'rate': 150,        # 말하기 속도
            'volume': 0.9,      # 볼륨
            'voice_id': None,   # 목소리 종류
        }
        
        # 통계
        self.stats = {
            'utterances': 0,
            'total_chars': 0,
        }
    
    def activate(self, engine: str = 'pyttsx3') -> bool:
        """TTS 엔진 활성화"""
        try:
            if engine == 'pyttsx3':
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.voice_settings['rate'])
                self.tts_engine.setProperty('volume', self.voice_settings['volume'])
                self.is_active = True
                return True
        except ImportError:
            print("⚠️ pyttsx3가 설치되지 않았습니다. TTS 비활성화.")
        except Exception as e:
            print(f"⚠️ TTS 활성화 실패: {e}")
        
        self.is_active = False
        return False
    
    def deactivate(self):
        """TTS 엔진 비활성화"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        self.tts_engine = None
        self.is_active = False
    
    def speak(self, text: str, blocking: bool = True) -> ActionResult:
        """
        말하기
        
        Args:
            text: 말할 내용
            blocking: True면 말이 끝날 때까지 대기
            
        Returns:
            ActionResult
        """
        start_time = time.time()
        
        if not self.is_active or self.tts_engine is None:
            # TTS 없으면 텍스트로 출력
            print(f"🗣️ {text}")
            return ActionResult(
                success=True,
                action_type=ActionType.SPEAK,
                message="[TTS 비활성화] 텍스트로 출력됨",
                duration=time.time() - start_time
            )
        
        try:
            self.tts_engine.say(text)
            
            if blocking:
                self.tts_engine.runAndWait()
            
            self.stats['utterances'] += 1
            self.stats['total_chars'] += len(text)
            
            return ActionResult(
                success=True,
                action_type=ActionType.SPEAK,
                message=text[:50] + "..." if len(text) > 50 else text,
                duration=time.time() - start_time
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=ActionType.SPEAK,
                message=f"TTS 오류: {e}",
                duration=time.time() - start_time
            )
    
    def set_voice(self, rate: int = None, volume: float = None, voice_id: str = None):
        """음성 설정"""
        if rate:
            self.voice_settings['rate'] = rate
            if self.tts_engine:
                self.tts_engine.setProperty('rate', rate)
        
        if volume:
            self.voice_settings['volume'] = volume
            if self.tts_engine:
                self.tts_engine.setProperty('volume', volume)
        
        if voice_id:
            self.voice_settings['voice_id'] = voice_id
            if self.tts_engine:
                self.tts_engine.setProperty('voice', voice_id)


class TextOutput:
    """
    📝 텍스트 출력
    
    화면 또는 파일로 텍스트 출력
    가장 기본적인 출력 방식
    """
    
    def __init__(self):
        self.output_handler: Optional[Callable[[str], None]] = None
        self.history: list = []
        self.max_history = 100
        
        # 통계
        self.stats = {
            'outputs': 0,
            'total_chars': 0,
        }
    
    def set_handler(self, handler: Callable[[str], None]):
        """
        출력 핸들러 설정
        
        예: GUI 텍스트 박스에 출력
        """
        self.output_handler = handler
    
    def write(self, text: str, prefix: str = "") -> ActionResult:
        """
        텍스트 출력
        
        Args:
            text: 출력할 텍스트
            prefix: 접두사 (예: "🤖")
            
        Returns:
            ActionResult
        """
        start_time = time.time()
        
        output_text = f"{prefix}{text}" if prefix else text
        
        # 핸들러가 있으면 사용, 없으면 print
        if self.output_handler:
            self.output_handler(output_text)
        else:
            print(output_text)
        
        # 기록
        self.history.append({
            'text': output_text,
            'timestamp': time.time()
        })
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # 통계
        self.stats['outputs'] += 1
        self.stats['total_chars'] += len(text)
        
        return ActionResult(
            success=True,
            action_type=ActionType.WRITE,
            message=text[:50] + "..." if len(text) > 50 else text,
            duration=time.time() - start_time
        )
    
    def write_to_file(self, text: str, file_path: str, mode: str = 'a') -> ActionResult:
        """파일에 출력"""
        start_time = time.time()
        
        try:
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(text + '\n')
            
            return ActionResult(
                success=True,
                action_type=ActionType.WRITE,
                message=f"파일에 저장: {file_path}",
                duration=time.time() - start_time
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=ActionType.WRITE,
                message=f"파일 저장 오류: {e}",
                duration=time.time() - start_time
            )
    
    def get_history(self, n: int = 10) -> list:
        """최근 출력 기록"""
        return self.history[-n:]


class MotorOutput:
    """
    🦿 모터 제어
    
    로봇 모터, 서보 등 물리적 움직임 제어
    라즈베리파이/아두이노 연동
    """
    
    def __init__(self):
        self.connection = None
        self.is_active = False
        
        # 모터 상태
        self.motor_state = {
            'left_wheel': 0,    # -100 ~ 100 (속도)
            'right_wheel': 0,
            'head_pan': 0,      # -90 ~ 90 (각도)
            'head_tilt': 0,
        }
        
        # 통계
        self.stats = {
            'commands_sent': 0,
            'total_distance': 0,
        }
    
    def connect(self, connection_type: str = 'serial', **kwargs) -> bool:
        """
        모터 컨트롤러 연결
        
        Args:
            connection_type: 'serial', 'gpio', 'socket'
            **kwargs: 연결 파라미터 (port, baudrate 등)
        """
        try:
            if connection_type == 'serial':
                import serial
                port = kwargs.get('port', '/dev/ttyUSB0')
                baudrate = kwargs.get('baudrate', 9600)
                self.connection = serial.Serial(port, baudrate)
                self.is_active = True
                return True
            elif connection_type == 'gpio':
                # 라즈베리파이 GPIO
                try:
                    import RPi.GPIO as GPIO
                    GPIO.setmode(GPIO.BCM)
                    self.connection = GPIO
                    self.is_active = True
                    return True
                except ImportError:
                    print("⚠️ RPi.GPIO가 설치되지 않았습니다.")
            elif connection_type == 'socket':
                # 네트워크 연결
                import socket
                host = kwargs.get('host', 'localhost')
                port = kwargs.get('port', 8888)
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((host, port))
                self.is_active = True
                return True
        except Exception as e:
            print(f"⚠️ 모터 연결 실패: {e}")
        
        self.is_active = False
        return False
    
    def disconnect(self):
        """연결 해제"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self.connection = None
        self.is_active = False
    
    def move(self, left: int = 0, right: int = 0, duration: float = 1.0) -> ActionResult:
        """
        바퀴 제어 (차동 구동)
        
        Args:
            left: 왼쪽 바퀴 속도 (-100 ~ 100)
            right: 오른쪽 바퀴 속도 (-100 ~ 100)
            duration: 동작 시간 (초)
        """
        start_time = time.time()
        
        # 속도 클램핑
        left = max(-100, min(100, left))
        right = max(-100, min(100, right))
        
        self.motor_state['left_wheel'] = left
        self.motor_state['right_wheel'] = right
        
        if not self.is_active:
            # 시뮬레이션 모드
            print(f"🦿 [시뮬레이션] 이동: L={left}, R={right}, {duration}초")
            time.sleep(min(duration, 0.1))  # 짧게 대기
            
            return ActionResult(
                success=True,
                action_type=ActionType.MOVE,
                message=f"[시뮬레이션] L={left}, R={right}",
                duration=time.time() - start_time
            )
        
        try:
            # 실제 명령 전송
            command = f"MOVE {left} {right} {duration}\n"
            
            if hasattr(self.connection, 'write'):
                self.connection.write(command.encode())
            elif hasattr(self.connection, 'send'):
                self.connection.send(command.encode())
            
            time.sleep(duration)
            
            # 정지
            self.motor_state['left_wheel'] = 0
            self.motor_state['right_wheel'] = 0
            
            self.stats['commands_sent'] += 1
            
            return ActionResult(
                success=True,
                action_type=ActionType.MOVE,
                message=f"이동 완료: L={left}, R={right}",
                duration=time.time() - start_time
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=ActionType.MOVE,
                message=f"모터 오류: {e}",
                duration=time.time() - start_time
            )
    
    def stop(self) -> ActionResult:
        """긴급 정지"""
        return self.move(0, 0, 0)
    
    def look(self, pan: int = 0, tilt: int = 0) -> ActionResult:
        """
        머리(카메라) 방향 제어
        
        Args:
            pan: 좌우 (-90 ~ 90)
            tilt: 상하 (-45 ~ 45)
        """
        start_time = time.time()
        
        pan = max(-90, min(90, pan))
        tilt = max(-45, min(45, tilt))
        
        self.motor_state['head_pan'] = pan
        self.motor_state['head_tilt'] = tilt
        
        if not self.is_active:
            print(f"🦿 [시뮬레이션] 바라보기: pan={pan}, tilt={tilt}")
            return ActionResult(
                success=True,
                action_type=ActionType.GESTURE,
                message=f"[시뮬레이션] pan={pan}, tilt={tilt}",
                duration=time.time() - start_time
            )
        
        try:
            command = f"LOOK {pan} {tilt}\n"
            
            if hasattr(self.connection, 'write'):
                self.connection.write(command.encode())
            elif hasattr(self.connection, 'send'):
                self.connection.send(command.encode())
            
            self.stats['commands_sent'] += 1
            
            return ActionResult(
                success=True,
                action_type=ActionType.GESTURE,
                message=f"바라보기: pan={pan}, tilt={tilt}",
                duration=time.time() - start_time
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=ActionType.GESTURE,
                message=f"서보 오류: {e}",
                duration=time.time() - start_time
            )


class Actions:
    """
    🎬 통합 행동 시스템
    
    모든 출력 기관을 통합 관리
    """
    
    def __init__(self):
        self.mouth = SpeechOutput()
        self.text = TextOutput()
        self.motor = MotorOutput()
        
        # 행동 큐 (우선순위 기반)
        self.action_queue: list = []
        
        # 통계
        self.stats = {
            'total_actions': 0,
            'successful_actions': 0,
        }
    
    def activate_all(self) -> Dict[str, bool]:
        """모든 출력 기관 활성화"""
        return {
            'mouth': self.mouth.activate(),
            'text': True,  # 텍스트는 항상 활성
            'motor': False,  # 모터는 명시적 연결 필요
        }
    
    def deactivate_all(self):
        """모든 출력 기관 비활성화"""
        self.mouth.deactivate()
        self.motor.disconnect()
    
    def execute(self, command: ActionCommand) -> ActionResult:
        """
        행동 실행 (통합 인터페이스)
        
        Args:
            command: ActionCommand
            
        Returns:
            ActionResult
        """
        self.stats['total_actions'] += 1
        
        if command.action_type == ActionType.SPEAK:
            result = self.mouth.speak(str(command.content))
        elif command.action_type == ActionType.WRITE:
            result = self.text.write(str(command.content))
        elif command.action_type == ActionType.MOVE:
            if isinstance(command.content, dict):
                result = self.motor.move(**command.content)
            else:
                result = self.motor.move()
        elif command.action_type == ActionType.GESTURE:
            if isinstance(command.content, dict):
                result = self.motor.look(**command.content)
            else:
                result = self.motor.look()
        else:
            result = ActionResult(
                success=False,
                action_type=command.action_type,
                message="알 수 없는 행동 유형",
                duration=0
            )
        
        if result.success:
            self.stats['successful_actions'] += 1
        
        return result
    
    def respond(self, text: str, speak: bool = False) -> ActionResult:
        """
        응답하기 (편의 메서드)
        
        Args:
            text: 응답 텍스트
            speak: True면 음성으로도 출력
        """
        # 텍스트 출력
        result = self.text.write(text, prefix="🤖 ")
        
        # 음성 출력 (옵션)
        if speak and self.mouth.is_active:
            self.mouth.speak(text)
        
        return result
    
    def get_stats(self) -> Dict:
        """통계"""
        return {
            'total_actions': self.stats['total_actions'],
            'successful_actions': self.stats['successful_actions'],
            'success_rate': (
                self.stats['successful_actions'] / self.stats['total_actions']
                if self.stats['total_actions'] > 0 else 0
            ),
            'mouth': self.mouth.stats,
            'text': self.text.stats,
            'motor': self.motor.stats,
        }

