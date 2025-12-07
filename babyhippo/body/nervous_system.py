"""
Nervous System: 뇌-몸 연결 (Central Coordinator)
=================================================

🔌 뇌(Brain)와 몸(Body)을 연결하는 신경망

역할:
    1. 감각(Senses) → 뇌(Thalamus)로 전달
    2. 뇌(Cerebellum) → 행동(Actions)으로 전달
    3. 내부 상태 모니터링 (배터리, 온도 등)
    4. 반사 회로 (위험 시 즉시 정지 등)

구조:
    [Senses] → NervousSystem → [Brain] → NervousSystem → [Actions]
                    ↑                           ↓
              [BodyState] ←←←←←←←←←←←←←←← [Feedback]

Author: GNJz (Qquarts)
Version: 1.0
"""

import time
import threading
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .senses import Senses, RawInput, SensorType
from .actions import Actions, ActionCommand, ActionResult, ActionType


class BodyMode(Enum):
    """몸 상태 모드"""
    IDLE = "idle"           # 대기
    ACTIVE = "active"       # 활동 중
    SLEEP = "sleep"         # 수면
    EMERGENCY = "emergency" # 비상


@dataclass
class BodyState:
    """몸 전체 상태"""
    mode: BodyMode = BodyMode.IDLE
    battery: float = 1.0            # 0.0 ~ 1.0
    temperature: float = 0.5        # 0.0=저체온, 0.5=정상, 1.0=과열
    uptime: float = 0.0             # 작동 시간 (초)
    last_input_time: float = 0.0
    last_output_time: float = 0.0
    
    # 센서 상태
    sensors_active: Dict[str, bool] = field(default_factory=dict)
    
    # 액추에이터 상태
    actuators_active: Dict[str, bool] = field(default_factory=dict)
    
    def is_healthy(self) -> bool:
        """건강 상태 확인"""
        return (
            self.battery > 0.1 and
            0.2 < self.temperature < 0.8 and
            self.mode != BodyMode.EMERGENCY
        )


class NervousSystem:
    """
    🔌 중추 신경계 (Central Nervous System)
    
    뇌와 몸의 통합 제어
    """
    
    def __init__(self, brain=None):
        """
        Args:
            brain: BabyBrain 인스턴스 (나중에 연결 가능)
        """
        self.brain = brain
        
        # 감각/행동 시스템
        self.senses = Senses()
        self.actions = Actions()
        
        # 몸 상태
        self.state = BodyState()
        self.start_time = time.time()
        
        # 콜백
        self.on_input: Optional[Callable[[RawInput], None]] = None
        self.on_output: Optional[Callable[[ActionResult], None]] = None
        self.on_emergency: Optional[Callable[[], None]] = None
        
        # 반사 회로 (뇌 우회)
        self.reflexes: Dict[str, Callable] = {}
        self._setup_default_reflexes()
        
        # 백그라운드 모니터링
        self._monitor_thread = None
        self._running = False
        
        # 통계
        self.stats = {
            'inputs_processed': 0,
            'outputs_executed': 0,
            'reflexes_triggered': 0,
            'emergencies': 0,
        }
    
    def connect_brain(self, brain):
        """뇌 연결"""
        self.brain = brain
        print(f"🔌 뇌 연결됨: {brain.name if hasattr(brain, 'name') else 'Unknown'}")
    
    def _setup_default_reflexes(self):
        """기본 반사 회로 설정"""
        # 위험 감지 → 정지
        def emergency_stop(input_data):
            if "위험" in str(input_data) or "stop" in str(input_data).lower():
                self.emergency_stop()
                return True
            return False
        
        # 배터리 부족 → 경고
        def low_battery_warning(input_data):
            if self.state.battery < 0.15:
                self.actions.text.write("⚠️ 배터리 부족! 충전이 필요합니다.")
                return True
            return False
        
        self.reflexes['emergency_stop'] = emergency_stop
        self.reflexes['low_battery'] = low_battery_warning
    
    def add_reflex(self, name: str, handler: Callable):
        """반사 회로 추가"""
        self.reflexes[name] = handler
    
    # =========================================================================
    # 🎭 입력 처리 (Sensory Pathway)
    # =========================================================================
    
    def receive_input(self, 
                      modality: SensorType = SensorType.TEXT,
                      data: Any = None) -> Optional[str]:
        """
        입력 수신 및 뇌로 전달
        
        Args:
            modality: 감각 유형
            data: 입력 데이터 (TEXT의 경우 문자열)
            
        Returns:
            뇌의 응답 (있으면)
        """
        # 1. 감각 수집
        raw_input = self.senses.sense(modality, data)
        
        if raw_input is None:
            return None
        
        self.state.last_input_time = time.time()
        self.stats['inputs_processed'] += 1
        
        # 2. 반사 체크 (뇌 우회)
        for name, handler in self.reflexes.items():
            try:
                if handler(raw_input.data):
                    self.stats['reflexes_triggered'] += 1
                    continue  # 반사 실행됨
            except:
                pass
        
        # 3. 콜백
        if self.on_input:
            self.on_input(raw_input)
        
        # 4. 뇌로 전달
        if self.brain is not None:
            try:
                # SensoryInput으로 변환
                sensory_input = self.senses.to_sensory_input(raw_input)
                
                # 뇌의 chat 메서드 호출
                if modality == SensorType.TEXT and data:
                    response = self.brain.chat(data)
                    return response
                
            except Exception as e:
                print(f"❌ 뇌 처리 오류: {e}")
        
        return None
    
    def receive_text(self, text: str) -> Optional[str]:
        """텍스트 입력 (편의 메서드)"""
        return self.receive_input(SensorType.TEXT, text)
    
    # =========================================================================
    # 🎬 출력 처리 (Motor Pathway)
    # =========================================================================
    
    def execute_action(self, 
                       action_type: ActionType,
                       content: Any,
                       **kwargs) -> ActionResult:
        """
        행동 실행
        
        Args:
            action_type: 행동 유형
            content: 내용
            **kwargs: 추가 옵션
        """
        command = ActionCommand(
            action_type=action_type,
            content=content,
            **kwargs
        )
        
        result = self.actions.execute(command)
        
        self.state.last_output_time = time.time()
        self.stats['outputs_executed'] += 1
        
        # 콜백
        if self.on_output:
            self.on_output(result)
        
        return result
    
    def respond(self, text: str, speak: bool = False) -> ActionResult:
        """응답 출력 (편의 메서드)"""
        return self.actions.respond(text, speak=speak)
    
    # =========================================================================
    # 🔄 통합 처리 루프
    # =========================================================================
    
    def process(self, text: str) -> str:
        """
        전체 처리 루프 (입력 → 뇌 → 출력)
        
        Args:
            text: 사용자 입력
            
        Returns:
            응답 텍스트
        """
        # 상태 체크
        if not self.state.is_healthy():
            return "⚠️ 몸 상태가 좋지 않습니다..."
        
        # 모드 업데이트
        self.state.mode = BodyMode.ACTIVE
        
        # 입력 → 뇌 처리
        response = self.receive_text(text)
        
        if response:
            # 출력
            self.respond(response)
            return response
        
        # 모드 복귀
        self.state.mode = BodyMode.IDLE
        
        return "..."
    
    # =========================================================================
    # 🚨 비상 시스템
    # =========================================================================
    
    def emergency_stop(self):
        """비상 정지"""
        self.state.mode = BodyMode.EMERGENCY
        self.stats['emergencies'] += 1
        
        # 모터 정지
        self.actions.motor.stop()
        
        # 경고 출력
        self.actions.text.write("🚨 비상 정지!")
        
        # 콜백
        if self.on_emergency:
            self.on_emergency()
        
        print("🚨 EMERGENCY STOP!")
    
    def recover(self):
        """비상 복구"""
        if self.state.mode == BodyMode.EMERGENCY:
            self.state.mode = BodyMode.IDLE
            print("✅ 비상 상태 해제")
    
    # =========================================================================
    # 📊 모니터링
    # =========================================================================
    
    def start_monitoring(self, interval: float = 1.0):
        """백그라운드 상태 모니터링 시작"""
        if self._running:
            return
        
        self._running = True
        
        def monitor_loop():
            while self._running:
                self._update_state()
                time.sleep(interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
    
    def _update_state(self):
        """상태 업데이트"""
        # 작동 시간
        self.state.uptime = time.time() - self.start_time
        
        # 배터리 감소 (시뮬레이션)
        if self.state.mode == BodyMode.ACTIVE:
            self.state.battery = max(0, self.state.battery - 0.0001)
        elif self.state.mode == BodyMode.SLEEP:
            self.state.battery = min(1.0, self.state.battery + 0.0005)
        
        # 배터리 경고
        if self.state.battery < 0.1:
            for name, handler in self.reflexes.items():
                if 'battery' in name:
                    handler(None)
    
    def get_state(self) -> Dict:
        """현재 상태"""
        return {
            'mode': self.state.mode.value,
            'battery': f"{self.state.battery:.0%}",
            'temperature': f"{self.state.temperature:.1f}",
            'uptime': f"{self.state.uptime:.0f}초",
            'healthy': self.state.is_healthy(),
            'stats': self.stats,
        }
    
    def get_full_status(self) -> str:
        """전체 상태 문자열"""
        state = self.get_state()
        
        return f"""
╔══════════════════════════════════════════╗
║  🤖 Body Status
╠══════════════════════════════════════════╣
║  모드: {state['mode']}
║  배터리: {state['battery']}
║  온도: {state['temperature']}
║  작동시간: {state['uptime']}
║  상태: {'✅ 정상' if state['healthy'] else '⚠️ 이상'}
╠══════════════════════════════════════════╣
║  📊 통계
║  - 입력 처리: {self.stats['inputs_processed']}회
║  - 출력 실행: {self.stats['outputs_executed']}회
║  - 반사 발동: {self.stats['reflexes_triggered']}회
╚══════════════════════════════════════════╝
"""
    
    # =========================================================================
    # 🔧 설정
    # =========================================================================
    
    def activate(self) -> Dict[str, bool]:
        """전체 활성화"""
        sensors = self.senses.activate_all()
        actuators = self.actions.activate_all()
        
        self.state.sensors_active = sensors
        self.state.actuators_active = actuators
        
        return {**sensors, **actuators}
    
    def deactivate(self):
        """전체 비활성화"""
        self.senses.deactivate_all()
        self.actions.deactivate_all()
        self.stop_monitoring()
    
    def sleep(self):
        """수면 모드"""
        self.state.mode = BodyMode.SLEEP
        # 센서 최소화
        self.senses.eyes.deactivate()
    
    def wake(self):
        """각성 모드"""
        self.state.mode = BodyMode.IDLE
        # 센서 재활성화
        self.senses.eyes.activate()

