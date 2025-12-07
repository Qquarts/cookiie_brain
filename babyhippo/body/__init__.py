"""
Body: 말초 신경계 (Peripheral Nervous System)
=============================================

🤖 뇌(Brain)를 담는 그릇 - 세상과의 인터페이스

구성:
    - senses.py: 감각 기관 (Input → SensoryInput)
    - actions.py: 운동 기관 (Action → 물리적 실행)
    - nervous_system.py: 뇌-몸 연결 (통신)

흐름:
    [World] → senses → [Brain] → actions → [World]

Author: GNJz (Qquarts)
Version: 1.0
"""

from .senses import (
    Senses,
    EyeInput,
    EarInput,
    TextInput,
    SensorType,
)

from .actions import (
    Actions,
    SpeechOutput,
    TextOutput,
    MotorOutput,
    ActionType,
)

from .nervous_system import (
    NervousSystem,
    BodyState,
)

__all__ = [
    # Senses
    "Senses", "EyeInput", "EarInput", "TextInput", "SensorType",
    # Actions
    "Actions", "SpeechOutput", "TextOutput", "MotorOutput", "ActionType",
    # Nervous System
    "NervousSystem", "BodyState",
]

