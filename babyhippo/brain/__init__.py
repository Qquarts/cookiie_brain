"""
Brain Structures: 뇌 구조 모듈
==============================

🧠 처리 순서 (Processing Order):
  _1_thalamus.py      → 감각 입력 게이팅
  _2_amygdala.py      → 위협/감정 (Fast Path)
  _3_hypothalamus.py  → 욕구/동기
  _4_basal_ganglia.py → 습관/행동 선택
  _5_prefrontal.py    → 판단/계획
  _6_cingulate.py     → 오류 감지
  _7_cerebellum.py    → 미세 조정
  _8_brain_graph.py   → 전체 연결

Author: GNJz (Qquarts)
"""

# 순서대로 임포트
from ._1_thalamus import Thalamus, SensoryInput, FilteredOutput, ModalityType
from ._2_amygdala import Amygdala, EmotionState, ThreatSignal, FearMemory
from ._3_hypothalamus import Hypothalamus, DriveType, InternalState, DriveSignal
from ._4_basal_ganglia import BasalGanglia, Action, ActionResult, ActionType
from ._5_prefrontal import PrefrontalCortex
from ._6_cingulate import CingulateCortex, ErrorSignal, ConflictSignal, ControlSignal
from ._7_cerebellum import Cerebellum
from ._8_brain_graph import BrainGraph, create_brain

__all__ = [
    # 1. Thalamus (감각 게이팅)
    "Thalamus", "SensoryInput", "FilteredOutput", "ModalityType",
    # 2. Amygdala (위협/감정)
    "Amygdala", "EmotionState", "ThreatSignal", "FearMemory",
    # 3. Hypothalamus (욕구/동기)
    "Hypothalamus", "DriveType", "InternalState", "DriveSignal",
    # 4. Basal Ganglia (습관/행동)
    "BasalGanglia", "Action", "ActionResult", "ActionType",
    # 5. Prefrontal (판단/계획)
    "PrefrontalCortex",
    # 6. Cingulate (오류 감지)
    "CingulateCortex", "ErrorSignal", "ConflictSignal", "ControlSignal",
    # 7. Cerebellum (미세 조정)
    "Cerebellum",
    # 8. Brain Graph (전체 연결)
    "BrainGraph", "create_brain",
]
